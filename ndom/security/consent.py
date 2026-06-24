"""NDOM ConsentRecord — 同意记录

v0.2 扩展：支持 ConsentScope 枚举和分层同意。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

from ndom.enums import ConsentType, ConsentScope


@dataclass
class ConsentRecord:
    """同意记录。

    记录数据主体的同意状态，支持：
    - 分层同意（不同用途不同同意）
    - 同意撤回
    - 数字签名
    - 特定用途限制
    """
    consent_id: str
    consent_type: ConsentType
    consent_scope: List[ConsentScope] = field(default_factory=list)
    consent_withdrawable: bool = True
    withdrawal_date: Optional[datetime] = None
    consent_document_version: Optional[str] = None
    data_use_limitations: List[str] = field(default_factory=list)
    recontact_allowed: bool = False
    specific_consent_for: List[str] = field(default_factory=list)
    recorded_by: Optional[str] = None
    recorded_at: Optional[datetime] = None
    digital_signature: Optional[str] = None
    consent_url: Optional[str] = None  # v0.2 新增：同意书链接

    def __post_init__(self):
        if not self.consent_id:
            self.consent_id = str(uuid.uuid4())

    def is_valid(self) -> bool:
        """检查同意是否仍然有效。"""
        return self.withdrawal_date is None

    def withdraw(self, withdrawn_by: str, reason: str = "") -> None:
        """撤回同意。"""
        self.withdrawal_date = datetime.utcnow()
        self.data_use_limitations.append(f"WITHDRAWN by {withdrawn_by} at {self.withdrawal_date.isoformat()}")
        if reason:
            self.data_use_limitations.append(f"Reason: {reason}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "consent_id": self.consent_id,
            "consent_type": self.consent_type.value,
            "consent_scope": [s.value for s in self.consent_scope],
            "consent_withdrawable": self.consent_withdrawable,
            "withdrawal_date": self.withdrawal_date.isoformat() if self.withdrawal_date else None,
            "consent_document_version": self.consent_document_version,
            "data_use_limitations": self.data_use_limitations,
            "recontact_allowed": self.recontact_allowed,
            "specific_consent_for": self.specific_consent_for,
            "recorded_by": self.recorded_by,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
            "digital_signature": self.digital_signature,
            "consent_url": self.consent_url,
        }
