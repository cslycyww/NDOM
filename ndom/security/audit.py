"""NDOM Audit — 审计日志

v0.2 扩展：支持更多操作类型和对象级审计。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

from ndom.enums import ActionType


@dataclass
class AuditEntry:
    """审计日志条目。"""
    entry_id: str
    timestamp: datetime
    action: ActionType
    actor_id: str
    actor_role: str
    target_object: str
    target_object_type: str
    access_granted: bool = True
    reason: Optional[str] = None
    ip_address: Optional[str] = None
    data_transformations: List[str] = field(default_factory=list)

    # v0.2 新增
    session_id: Optional[str] = None
    user_agent: Optional[str] = None
    geolocation: Optional[str] = None
    mfa_used: Optional[bool] = None

    def __post_init__(self):
        if not self.entry_id:
            self.entry_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action.value,
            "actor_id": self.actor_id,
            "actor_role": self.actor_role,
            "target_object": self.target_object,
            "target_object_type": self.target_object_type,
            "access_granted": self.access_granted,
            "reason": self.reason,
            "ip_address": self.ip_address,
            "data_transformations": self.data_transformations,
            "session_id": self.session_id,
            "user_agent": self.user_agent,
            "geolocation": self.geolocation,
            "mfa_used": self.mfa_used,
        }


@dataclass
class AuditLog:
    """审计日志。"""
    log_entries: List[AuditEntry] = field(default_factory=list)

    def add_entry(self, entry: AuditEntry) -> None:
        self.log_entries.append(entry)

    def filter_by_actor(self, actor_id: str) -> List[AuditEntry]:
        return [e for e in self.log_entries if e.actor_id == actor_id]

    def filter_by_object(self, object_id: str) -> List[AuditEntry]:
        return [e for e in self.log_entries if e.target_object == object_id]

    def filter_by_action(self, action: ActionType) -> List[AuditEntry]:
        return [e for e in self.log_entries if e.action == action]

    def filter_by_time_range(self, start: datetime, end: datetime) -> List[AuditEntry]:
        return [e for e in self.log_entries if start <= e.timestamp <= end]

    def get_recent(self, n: int = 10) -> List[AuditEntry]:
        """获取最近的 n 条记录。"""
        sorted_entries = sorted(self.log_entries, key=lambda x: x.timestamp, reverse=True)
        return sorted_entries[:n]

    def to_dict(self) -> Dict[str, Any]:
        return {"log_entries": [e.to_dict() for e in self.log_entries]}
