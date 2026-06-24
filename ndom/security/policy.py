"""NDOM Security Policy — 安全策略

v0.2 核心变化：SecurityPolicy 可以绑定到 Dataset 或每个 DataObject。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

from ndom.enums import (
    PrivacyLevel, NeuralDataSensitivity, DataRetentionPolicyType,
)


# 安全控制矩阵（推荐配置）
SECURITY_CONTROL_MATRIX = {
    NeuralDataSensitivity.L1: {
        "encryption_at_rest": False, "encryption_in_transit": False,
        "pseudonymization": False, "differential_privacy": False,
        "access_logging": False, "audit_frequency_days": 365,
    },
    NeuralDataSensitivity.L2: {
        "encryption_at_rest": False, "encryption_in_transit": True,
        "pseudonymization": True, "differential_privacy": False,
        "access_logging": True, "audit_frequency_days": 180,
    },
    NeuralDataSensitivity.L3: {
        "encryption_at_rest": True, "encryption_in_transit": True,
        "pseudonymization": True, "differential_privacy": False,
        "access_logging": True, "audit_frequency_days": 90,
    },
    NeuralDataSensitivity.L4: {
        "encryption_at_rest": True, "encryption_in_transit": True,
        "pseudonymization": True, "differential_privacy": True,
        "access_logging": True, "audit_frequency_days": 30,
    },
    NeuralDataSensitivity.L5: {
        "encryption_at_rest": True, "encryption_in_transit": True,
        "pseudonymization": True, "differential_privacy": True,
        "access_logging": True, "audit_frequency_days": 1,
    },
}


@dataclass
class AccessRule:
    """访问控制规则。"""
    role: str
    permission: str  # read, write, admin, none
    conditions: List[str] = field(default_factory=list)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role, "permission": self.permission,
            "conditions": self.conditions,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
        }


@dataclass
class DataRetentionPolicy:
    """数据保留策略。"""
    policy_type: DataRetentionPolicyType
    retention_end_date: Optional[datetime] = None
    destruction_method: Optional[str] = None  # cryptographic_erasure, physical_destruction, standard_deletion

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_type": self.policy_type.value,
            "retention_end_date": self.retention_end_date.isoformat() if self.retention_end_date else None,
            "destruction_method": self.destruction_method,
        }


@dataclass
class SecurityPolicy:
    """安全策略。

    v0.2 新增：
    - data_minimization: 数据最小化策略
    - purpose_limitation: 目的限制
    - 支持绑定到 DataObject 级别
    """
    policy_id: str
    privacy_level: PrivacyLevel
    data_retention_policy: DataRetentionPolicy

    encryption_at_rest: bool = False
    encryption_in_transit: bool = False
    pseudonymization: bool = False
    differential_privacy_epsilon: Optional[float] = None
    access_control_list: List[AccessRule] = field(default_factory=list)

    # v0.2 新增
    data_minimization: bool = False
    purpose_limitation: List[str] = field(default_factory=list)

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    data_controller: Optional[str] = None
    data_protection_officer: Optional[str] = None
    legal_basis: Optional[str] = None  # GDPR_Art9, HIPAA, research_ethics, etc.
    cross_border_transfer: bool = False
    transfer_safeguards: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.policy_id:
            self.policy_id = str(uuid.uuid4())

    def validate_controls(self, sensitivity: NeuralDataSensitivity) -> List[str]:
        """验证当前安全控制是否符合敏感度级别的推荐配置。"""
        recommended = SECURITY_CONTROL_MATRIX.get(sensitivity, {})
        violations = []
        if recommended.get("encryption_at_rest") and not self.encryption_at_rest:
            violations.append("encryption_at_rest required")
        if recommended.get("encryption_in_transit") and not self.encryption_in_transit:
            violations.append("encryption_in_transit required")
        if recommended.get("pseudonymization") and not self.pseudonymization:
            violations.append("pseudonymization required")
        if recommended.get("differential_privacy") and self.differential_privacy_epsilon is None:
            violations.append("differential_privacy required")
        if recommended.get("access_logging") and not any(self.access_control_list):
            violations.append("access_control_list required")
        return violations

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "privacy_level": self.privacy_level.value,
            "data_retention_policy": self.data_retention_policy.to_dict(),
            "encryption_at_rest": self.encryption_at_rest,
            "encryption_in_transit": self.encryption_in_transit,
            "pseudonymization": self.pseudonymization,
            "differential_privacy_epsilon": self.differential_privacy_epsilon,
            "access_control_list": [r.to_dict() for r in self.access_control_list],
            "data_minimization": self.data_minimization,
            "purpose_limitation": self.purpose_limitation,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "data_controller": self.data_controller,
            "data_protection_officer": self.data_protection_officer,
            "legal_basis": self.legal_basis,
            "cross_border_transfer": self.cross_border_transfer,
            "transfer_safeguards": self.transfer_safeguards,
        }
