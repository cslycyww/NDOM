"""NDOMFile — NDOM 顶层容器对象

继承 NWBFile 的语义，并原生集成安全对象。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

from ndom.core import (
    NDOMSubject, NDOMDevice, NDOMDeviceModel,
    NDOMElectrodeGroup, NDOMElectrode,
    NDOMAcquisition, NDOMProcessingModule,
    NDOMTimeSeries, NDOMTimeIntervals,
)
from ndom.security import (
    SecurityPolicy, ConsentRecord, NeuralDataClass,
    RiskTags, AuditLog, AuditEntry, ActionType,
)


@dataclass
class NDOMFile:
    """NDOM 顶层文件对象。
    
    兼容 NWBFile 的核心字段，并扩展安全属性。
    """

    # 必需字段（继承 NWBFile）
    session_description: str
    identifier: str
    session_start_time: datetime

    # 可选元数据（继承 NWBFile）
    file_create_date: Optional[datetime] = None
    timestamps_reference_time: Optional[datetime] = None
    experimenter: Optional[str] = None
    experiment_description: Optional[str] = None
    session_id: Optional[str] = None
    institution: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    lab: Optional[str] = None
    data_collection: Optional[str] = None
    pharmacology: Optional[str] = None
    protocol: Optional[str] = None
    related_publications: List[str] = field(default_factory=list)
    surgery: Optional[str] = None
    virus: Optional[str] = None
    stimulus_notes: Optional[str] = None

    # 子对象容器（继承 NWBFile）
    subject: Optional[NDOMSubject] = None
    devices: List[NDOMDevice] = field(default_factory=list)
    electrode_groups: List[NDOMElectrodeGroup] = field(default_factory=list)
    electrodes: List[NDOMElectrode] = field(default_factory=list)
    acquisition: List[NDOMAcquisition] = field(default_factory=list)
    processing: List[NDOMProcessingModule] = field(default_factory=list)
    analysis: List[Any] = field(default_factory=list)
    stimulus: List[NDOMTimeSeries] = field(default_factory=list)
    intervals: List[NDOMTimeIntervals] = field(default_factory=list)

    # NDOM 新增安全属性（一等公民）
    security_policy: Optional[SecurityPolicy] = None
    consent_record: Optional[ConsentRecord] = None
    neural_data_class: Optional[NeuralDataClass] = None
    risk_tags: Optional[RiskTags] = None
    audit_log: AuditLog = field(default_factory=AuditLog)

    # 内部状态
    _objects: Dict[str, Any] = field(default_factory=dict, repr=False)

    def __post_init__(self):
        if self.file_create_date is None:
            self.file_create_date = datetime.utcnow()
        if self.timestamps_reference_time is None:
            self.timestamps_reference_time = self.session_start_time
        self.object_id = str(uuid.uuid4())

    # ------------------------------------------------------------------
    # 子对象管理（继承 NWBFile 语义）
    # ------------------------------------------------------------------

    def add_subject(self, subject: NDOMSubject) -> None:
        self.subject = subject
        self._register_object(subject)

    def add_device(self, device: NDOMDevice) -> None:
        self.devices.append(device)
        self._register_object(device)
        if device.model:
            self._register_object(device.model)

    def add_electrode_group(self, eg: NDOMElectrodeGroup) -> None:
        self.electrode_groups.append(eg)
        self._register_object(eg)

    def add_electrode(self, electrode: NDOMElectrode) -> None:
        self.electrodes.append(electrode)
        self._register_object(electrode)

    def add_acquisition(self, acq: NDOMAcquisition) -> None:
        self.acquisition.append(acq)
        self._register_object(acq)

    def add_processing(self, proc: NDOMProcessingModule) -> None:
        self.processing.append(proc)
        self._register_object(proc)

    def add_interval(self, interval: NDOMTimeIntervals) -> None:
        self.intervals.append(interval)
        self._register_object(interval)

    # ------------------------------------------------------------------
    # NDOM 安全方法
    # ------------------------------------------------------------------

    def set_security_policy(self, policy: SecurityPolicy) -> None:
        """设置安全策略。记录审计日志。"""
        old_policy = self.security_policy
        self.security_policy = policy
        self._audit(
            action=ActionType.UPDATE,
            actor_id="system",
            actor_role="admin",
            target_object=policy.policy_id,
            target_object_type="SecurityPolicy",
            reason=f"Security policy updated. Old: {old_policy.policy_id if old_policy else 'None'}"
        )

    def set_consent_record(self, record: ConsentRecord) -> None:
        """设置同意记录。"""
        self.consent_record = record
        self._audit(
            action=ActionType.CREATE,
            actor_id=record.recorded_by or "system",
            actor_role="data_curator",
            target_object=record.consent_id,
            target_object_type="ConsentRecord",
            reason="Consent record created/updated"
        )

    def set_neural_data_class(self, ndc: NeuralDataClass) -> None:
        """设置神经数据分类。"""
        self.neural_data_class = ndc
        # 自动验证安全策略
        if self.security_policy:
            violations = self.security_policy.validate_controls(ndc.sensitivity_level)
            if violations:
                print(f"[NDOM WARNING] Security policy violations for {ndc.sensitivity_level}: {violations}")

    def set_risk_tags(self, tags: RiskTags) -> None:
        """设置风险标签。"""
        self.risk_tags = tags

    def get_object_by_id(self, object_id: str) -> Optional[Any]:
        """通过 object_id 获取对象（继承 NWBFile.objects 语义）。"""
        return self._objects.get(object_id)

    def _register_object(self, obj: Any) -> None:
        if hasattr(obj, "object_id"):
            self._objects[obj.object_id] = obj

    def _audit(self, action: ActionType, actor_id: str, actor_role: str,
               target_object: str, target_object_type: str,
               access_granted: bool = True, reason: str = "",
               data_transformations: Optional[List[str]] = None) -> None:
        """内部审计方法。"""
        entry = AuditEntry(
            entry_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            action=action,
            actor_id=actor_id,
            actor_role=actor_role,
            target_object=target_object,
            target_object_type=target_object_type,
            access_granted=access_granted,
            reason=reason,
            data_transformations=data_transformations or []
        )
        self.audit_log.add_entry(entry)

    # ------------------------------------------------------------------
    # 安全策略验证
    # ------------------------------------------------------------------

    def validate_security(self) -> Dict[str, Any]:
        """全面验证安全策略合规性。
        
        Returns:
            验证结果字典，包含 violations 和 recommendations。
        """
        result = {
            "valid": True,
            "violations": [],
            "recommendations": [],
            "warnings": []
        }

        if self.security_policy is None:
            result["valid"] = False
            result["violations"].append("Missing security_policy")

        if self.consent_record is None:
            result["violations"].append("Missing consent_record")

        if self.neural_data_class is None:
            result["violations"].append("Missing neural_data_class")

        if self.neural_data_class and self.security_policy:
            violations = self.security_policy.validate_controls(self.neural_data_class.sensitivity_level)
            result["violations"].extend(violations)

        if self.consent_record and not self.consent_record.is_valid():
            result["violations"].append("Consent has been withdrawn")

        if self.risk_tags:
            nonstandard = self.risk_tags.validate_tags()
            if nonstandard:
                result["warnings"].append(f"Non-standard risk tags: {nonstandard}")

        if not self.audit_log.log_entries:
            result["recommendations"].append("Audit log is empty; consider enabling access logging")

        result["valid"] = len(result["violations"]) == 0
        return result

    # ------------------------------------------------------------------
    # 序列化
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典（不包含原始数据数组）。"""
        return {
            # 基本元数据
            "ndom_version": "0.1.0",
            "object_id": self.object_id,
            "session_description": self.session_description,
            "identifier": self.identifier,
            "session_start_time": self.session_start_time.isoformat(),
            "file_create_date": self.file_create_date.isoformat() if self.file_create_date else None,
            "timestamps_reference_time": self.timestamps_reference_time.isoformat() if self.timestamps_reference_time else None,
            "experimenter": self.experimenter,
            "experiment_description": self.experiment_description,
            "session_id": self.session_id,
            "institution": self.institution,
            "keywords": self.keywords,
            "notes": self.notes,
            "lab": self.lab,
            "data_collection": self.data_collection,
            "pharmacology": self.pharmacology,
            "protocol": self.protocol,
            "related_publications": self.related_publications,
            "surgery": self.surgery,
            "virus": self.virus,
            "stimulus_notes": self.stimulus_notes,

            # 子对象
            "subject": self.subject.to_dict() if self.subject else None,
            "devices": [d.to_dict() for d in self.devices],
            "electrode_groups": [eg.to_dict() for eg in self.electrode_groups],
            "electrodes": [e.to_dict() for e in self.electrodes],
            "acquisition": [a.to_dict() for a in self.acquisition],
            "processing": [p.to_dict() for p in self.processing],
            "intervals": [i.to_dict() for i in self.intervals],

            # 安全对象
            "security_policy": self.security_policy.to_dict() if self.security_policy else None,
            "consent_record": self.consent_record.to_dict() if self.consent_record else None,
            "neural_data_class": self.neural_data_class.to_dict() if self.neural_data_class else None,
            "risk_tags": self.risk_tags.to_dict() if self.risk_tags else None,
            "audit_log": self.audit_log.to_dict(),
        }
