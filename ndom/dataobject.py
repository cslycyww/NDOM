"""NDOM DataObject — v0.2 核心原子单元

DataObject 是 NDOM v0.2 最重要的概念：每个数据对象都是独立的安全单元，
拥有自己的安全策略、风险画像、血缘、指纹和访问元数据。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

from ndom.enums import DataObjectType
from ndom.fingerprint import Fingerprint
from ndom.provenance import Provenance
from ndom.access_metadata import AccessMetadata
from ndom.risk_profile import RiskProfile
from ndom.security.policy import SecurityPolicy
from ndom.security.consent import ConsentRecord
from ndom.security.classification import NeuralDataClass
from ndom.security.risk_tags import RiskTags
from ndom.security.audit import AuditLog, AuditEntry, ActionType
from ndom.security.threat_profile import ThreatProfile


@dataclass
class DataObject:
    """数据对象 — NDOM v0.2 的核心原子单元。
    
    每个 DataObject 代表一个独立的数据实体，可以是：
    - Raw EEG / fMRI / iEEG 原始信号
    - 预处理后的数据（滤波、降采样等）
    - 特征提取数据（PSD、功率谱等）
    - 嵌入向量（深度学习中间层）
    - 解码输出（意图、情绪、语言等）
    - 人工标注、模型、聚合数据等
    
    每个对象都独立携带：
    - security_policy: 安全策略
    - risk_profile: 风险画像
    - provenance: 数据血缘
    - fingerprint: 数据指纹
    - access_metadata: 访问元数据
    - classification: 神经数据分类
    - risk_tags: 风险标签
    - audit_log: 审计日志
    """

    # 基本标识
    object_id: str
    object_type: DataObjectType
    name: str
    description: Optional[str] = None
    data_format: Optional[str] = None  # edf, nifti, hdf5, json, npy, etc.
    size_bytes: Optional[int] = None
    schema_version: Optional[str] = None

    # 血缘关系
    parent_object: Optional[str] = None           # 父对象 object_id
    child_objects: List[str] = field(default_factory=list)  # 子对象 object_ids
    sibling_objects: List[str] = field(default_factory=list)  # 同级对象

    # 数据引用（不直接存储数据）
    data_reference: Optional[str] = None          # 数据引用路径/URI
    data_checksum: Optional[str] = None          # 数据校验和

    # 安全层（每个对象独立）
    security_policy: Optional[SecurityPolicy] = None
    consent_record: Optional[ConsentRecord] = None
    classification: Optional[NeuralDataClass] = None
    risk_tags: Optional[RiskTags] = None
    risk_profile: Optional[RiskProfile] = None
    threat_profile: Optional[ThreatProfile] = None  # v0.2 新增：攻击模型/威胁画像

    # 元数据层（v0.2 新增）
    provenance: Optional[Provenance] = None
    fingerprint: Optional[Fingerprint] = None
    access_metadata: Optional[AccessMetadata] = None

    # 审计（对象级）
    audit_log: AuditLog = field(default_factory=AuditLog)

    # 时间戳
    created_at: datetime = field(default_factory=datetime.utcnow)
    modified_at: datetime = field(default_factory=datetime.utcnow)

    # 扩展
    tags: List[str] = field(default_factory=list)
    custom_properties: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.object_id:
            self.object_id = str(uuid.uuid4())
        # 如果 access_metadata 存在但缺少 object_id，自动补全
        if self.access_metadata and not self.access_metadata.object_id:
            self.access_metadata.object_id = self.object_id

    # ------------------------------------------------------------------
    # 血缘管理
    # ------------------------------------------------------------------
    def add_child(self, child_object_id: str) -> None:
        """添加子对象引用。"""
        if child_object_id not in self.child_objects:
            self.child_objects.append(child_object_id)
            self._audit(ActionType.CREATE, "system", "data_object", child_object_id, "DataObject",
                        f"Added child object {child_object_id}")

    def set_parent(self, parent_object_id: str) -> None:
        """设置父对象。"""
        self.parent_object = parent_object_id

    # ------------------------------------------------------------------
    # 安全策略
    # ------------------------------------------------------------------
    def set_security_policy(self, policy: SecurityPolicy) -> None:
        """设置安全策略。"""
        self.security_policy = policy
        self._audit(ActionType.UPDATE, "system", "admin", self.object_id, "DataObject",
                    f"Security policy set: {policy.policy_id}")

    def inherit_security_policy(self, parent_policy: SecurityPolicy) -> None:
        """从父对象继承安全策略（如果自身未设置）。"""
        if self.security_policy is None:
            # 深拷贝父策略，但保留自身 object_id
            import copy
            self.security_policy = copy.copy(parent_policy)
            self.security_policy.policy_id = f"{parent_policy.policy_id}-child-{self.object_id[:8]}"

    # ------------------------------------------------------------------
    # 风险画像
    # ------------------------------------------------------------------
    def set_risk_profile(self, profile: RiskProfile) -> None:
        """设置风险画像。"""
        self.risk_profile = profile
        if profile.needs_attention():
            self._audit(ActionType.UPDATE, "system", "risk_engine", self.object_id, "DataObject",
                        f"High-risk profile assigned: score={profile.overall_score}")

    # ------------------------------------------------------------------
    # 威胁画像（v0.2 新增）
    # ------------------------------------------------------------------
    def set_threat_profile(self, profile: ThreatProfile) -> None:
        """设置威胁画像。"""
        self.threat_profile = profile
        if profile.needs_attention():
            self._audit(ActionType.UPDATE, "system", "threat_engine", self.object_id, "DataObject",
                        f"High-threat profile assigned: {profile.risk_level.value}")

    # ------------------------------------------------------------------
    # 访问追踪
    # ------------------------------------------------------------------
    def record_access(self, actor_id: str, actor_role: str = "") -> None:
        """记录一次访问。"""
        if self.access_metadata is None:
            self.access_metadata = AccessMetadata(object_id=self.object_id)
        self.access_metadata.record_access(actor_id, actor_role)
        self._audit(ActionType.ACCESS, actor_id, actor_role, self.object_id, "DataObject",
                    f"Object accessed by {actor_id}")

    # ------------------------------------------------------------------
    # 审计
    # ------------------------------------------------------------------
    def _audit(self, action: ActionType, actor_id: str, actor_role: str,
               target_object: str, target_object_type: str, reason: str = "",
               access_granted: bool = True, data_transformations: Optional[List[str]] = None) -> None:
        entry = AuditEntry(
            entry_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            action=action, actor_id=actor_id, actor_role=actor_role,
            target_object=target_object, target_object_type=target_object_type,
            access_granted=access_granted, reason=reason,
            data_transformations=data_transformations or []
        )
        self.audit_log.add_entry(entry)

    # ------------------------------------------------------------------
    # 验证
    # ------------------------------------------------------------------
    def validate(self) -> Dict[str, Any]:
        """验证数据对象的完整性。"""
        result = {"valid": True, "errors": [], "warnings": [], "recommendations": []}

        if self.security_policy is None:
            result["warnings"].append("No security policy assigned")
        if self.fingerprint is None:
            result["warnings"].append("No fingerprint generated")
        if self.provenance is None:
            result["warnings"].append("No provenance recorded")
        if self.risk_profile is None:
            result["recommendations"].append("No risk profile; consider generating one")
        if self.classification is None:
            result["warnings"].append("No neural data classification")
        if self.consent_record is None:
            result["warnings"].append("No consent record")

        # 检查风险画像与分类是否一致
        if self.risk_profile and self.classification:
            sens_map = {
                "L1": 10, "L2": 30, "L3": 50, "L4": 70, "L5": 90
            }
            expected_min = sens_map.get(self.classification.sensitivity_level.value, 0)
            if self.risk_profile.overall_score < expected_min - 20:
                result["warnings"].append(
                    f"Risk score ({self.risk_profile.overall_score}) seems low for "
                    f"sensitivity level {self.classification.sensitivity_level.value}"
                )

        if self.threat_profile is None:
            result["recommendations"].append("No threat profile; consider attack modeling")

        result["valid"] = len(result["errors"]) == 0
        return result

    # ------------------------------------------------------------------
    # 序列化
    # ------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        return {
            "object_id": self.object_id,
            "object_type": self.object_type.value,
            "name": self.name,
            "description": self.description,
            "data_format": self.data_format,
            "size_bytes": self.size_bytes,
            "schema_version": self.schema_version,
            "parent_object": self.parent_object,
            "child_objects": self.child_objects,
            "sibling_objects": self.sibling_objects,
            "data_reference": self.data_reference,
            "data_checksum": self.data_checksum,
            "security_policy": self.security_policy.to_dict() if self.security_policy else None,
            "consent_record": self.consent_record.to_dict() if self.consent_record else None,
            "classification": self.classification.to_dict() if self.classification else None,
            "risk_tags": self.risk_tags.to_dict() if self.risk_tags else None,
            "risk_profile": self.risk_profile.to_dict() if self.risk_profile else None,
            "threat_profile": self.threat_profile.to_dict() if self.threat_profile else None,
            "provenance": self.provenance.to_dict() if self.provenance else None,
            "fingerprint": self.fingerprint.to_dict() if self.fingerprint else None,
            "access_metadata": self.access_metadata.to_dict() if self.access_metadata else None,
            "audit_log": self.audit_log.to_dict(),
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "tags": self.tags,
            "custom_properties": self.custom_properties,
        }
