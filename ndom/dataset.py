"""NDOM Dataset — 数据集层

v0.2：Dataset 是 DataObject 的容器，本身也有默认安全属性。
Dataset 从 NDOMFile v0.1 的"科研文件"角色升级为"数据对象容器"。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

from ndom.asset import Asset
from ndom.dataobject import DataObject
from ndom.security.policy import SecurityPolicy
from ndom.security.consent import ConsentRecord
from ndom.security.audit import AuditLog, AuditEntry, ActionType
from ndom.core.subject import NDOMSubject
from ndom.core.device import NDOMDevice
from ndom.core.electrode import NDOMElectrodeGroup, NDOMElectrode


@dataclass
class Dataset:
    """数据集 — DataObject 的容器。"""

    dataset_id: str
    description: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    modified_at: datetime = field(default_factory=datetime.utcnow)

    # 关联资产
    asset: Optional[Asset] = None

    # 核心：数据对象列表
    objects: List[DataObject] = field(default_factory=list)
    _object_index: Dict[str, DataObject] = field(default_factory=dict, repr=False)

    # 默认安全策略（对象未设置时继承）
    default_security_policy: Optional[SecurityPolicy] = None
    default_consent_record: Optional[ConsentRecord] = None

    # 传统神经科学元数据（保留）
    subject: Optional[NDOMSubject] = None
    devices: List[NDOMDevice] = field(default_factory=list)
    electrode_groups: List[NDOMElectrodeGroup] = field(default_factory=list)
    electrodes: List[NDOMElectrode] = field(default_factory=list)

    # 审计（数据集级）
    audit_log: AuditLog = field(default_factory=AuditLog)

    # 扩展
    keywords: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    custom_properties: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.dataset_id:
            self.dataset_id = str(uuid.uuid4())
        # 重建索引
        for obj in self.objects:
            self._object_index[obj.object_id] = obj

    # ------------------------------------------------------------------
    # 对象管理
    # ------------------------------------------------------------------
    def add_object(self, obj: DataObject) -> None:
        """添加数据对象，自动继承默认策略（如果对象未设置）。"""
        if obj.security_policy is None and self.default_security_policy is not None:
            obj.inherit_security_policy(self.default_security_policy)
        if obj.consent_record is None and self.default_consent_record is not None:
            import copy
            obj.consent_record = copy.copy(self.default_consent_record)
            obj.consent_record.consent_id = f"{self.default_consent_record.consent_id}-obj-{obj.object_id[:8]}"

        self.objects.append(obj)
        self._object_index[obj.object_id] = obj
        self._audit(ActionType.CREATE, "system", "data_curator", obj.object_id, "DataObject",
                    f"DataObject added to dataset: {obj.name}")

    def get_object_by_id(self, object_id: str) -> Optional[DataObject]:
        return self._object_index.get(object_id)

    def get_objects_by_type(self, obj_type: str) -> List[DataObject]:
        from ndom.enums import DataObjectType
        return [obj for obj in self.objects if obj.object_type == DataObjectType(obj_type)]

    def get_objects_by_tag(self, tag: str) -> List[DataObject]:
        return [obj for obj in self.objects if tag in obj.tags]

    def get_high_risk_objects(self) -> List[DataObject]:
        """获取高风险对象。"""
        return [obj for obj in self.objects
                if obj.risk_profile and obj.risk_profile.needs_attention()]

    def get_lineage(self, object_id: str) -> List[str]:
        """获取指定对象的完整血缘链。"""
        chain = []
        current = object_id
        visited = set()
        while current and current not in visited:
            visited.add(current)
            chain.append(current)
            obj = self.get_object_by_id(current)
            if obj and obj.parent_object:
                current = obj.parent_object
            else:
                break
        return list(reversed(chain))

    # ------------------------------------------------------------------
    # 风险汇总
    # ------------------------------------------------------------------
    def get_risk_summary(self) -> Dict[str, Any]:
        """生成数据集风险汇总。"""
        from ndom.enums import RiskLevel
        summary = {
            "total_objects": len(self.objects),
            "objects_by_type": {},
            "objects_by_sensitivity": {},
            "risk_distribution": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "max_sensitivity": None,
            "objects_needing_attention": [],
            "total_neural_privacy_score": 0.0,
        }

        for obj in self.objects:
            # 按类型统计
            t = obj.object_type.value
            summary["objects_by_type"][t] = summary["objects_by_type"].get(t, 0) + 1

            # 按敏感度统计
            if obj.classification:
                s = obj.classification.sensitivity_level.value
                summary["objects_by_sensitivity"][s] = summary["objects_by_sensitivity"].get(s, 0) + 1
                if summary["max_sensitivity"] is None:
                    summary["max_sensitivity"] = s
                elif s > summary["max_sensitivity"]:
                    summary["max_sensitivity"] = s

            # 风险分布
            if obj.risk_profile:
                summary["risk_distribution"][obj.risk_profile.risk_level.value] += 1
                summary["total_neural_privacy_score"] += obj.risk_profile.overall_score

                # 需要关注的对象
                if obj.risk_profile.needs_attention():
                    summary["objects_needing_attention"].append({
                        "object_id": obj.object_id,
                        "name": obj.name,
                        "type": obj.object_type.value,
                        "score": obj.risk_profile.overall_score,
                        "level": obj.risk_profile.risk_level.value,
                    })

        if summary["total_objects"] > 0:
            summary["average_neural_privacy_score"] = round(
                summary["total_neural_privacy_score"] / summary["total_objects"], 2
            )
        else:
            summary["average_neural_privacy_score"] = 0.0

        return summary

    # ------------------------------------------------------------------
    # 审计
    # ------------------------------------------------------------------
    def _audit(self, action: ActionType, actor_id: str, actor_role: str,
               target_object: str, target_object_type: str, reason: str = "") -> None:
        entry = AuditEntry(
            entry_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            action=action, actor_id=actor_id, actor_role=actor_role,
            target_object=target_object, target_object_type=target_object_type,
            access_granted=True, reason=reason
        )
        self.audit_log.add_entry(entry)

    # ------------------------------------------------------------------
    # 序列化
    # ------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "asset": self.asset.to_dict() if self.asset else None,
            "objects": [obj.to_dict() for obj in self.objects],
            "default_security_policy": self.default_security_policy.to_dict() if self.default_security_policy else None,
            "default_consent_record": self.default_consent_record.to_dict() if self.default_consent_record else None,
            "subject": self.subject.to_dict() if self.subject else None,
            "devices": [d.to_dict() for d in self.devices],
            "electrode_groups": [eg.to_dict() for eg in self.electrode_groups],
            "electrodes": [e.to_dict() for e in self.electrodes],
            "audit_log": self.audit_log.to_dict(),
            "keywords": self.keywords,
            "tags": self.tags,
            "custom_properties": self.custom_properties,
        }
