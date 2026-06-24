"""NDOM AccessMetadata — 访问元数据

v0.2 新增：用于审计、行为分析和异常检测。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid


@dataclass
class AccessMetadata:
    """访问元数据。
    
    追踪数据对象的访问、导出、下载、共享行为，
    支持安全审计、行为分析和异常检测。
    """

    object_id: str

    # 访问统计
    last_accessed: Optional[datetime] = None
    last_accessed_by: Optional[str] = None
    access_count: int = 0

    # 导出/下载统计
    export_count: int = 0
    download_count: int = 0
    last_exported: Optional[datetime] = None
    last_downloaded: Optional[datetime] = None
    total_bytes_exported: int = 0
    total_bytes_downloaded: int = 0

    # 共享状态
    sharing_status: str = "private"           # private, internal, shared, public
    shared_with: List[str] = field(default_factory=list)  # 共享对象/组织列表
    shared_at: Optional[datetime] = None
    share_expiry: Optional[datetime] = None  # 共享过期时间

    # 访问者画像
    unique_accessors: int = 0
    accessor_roles: List[str] = field(default_factory=list)
    accessor_organizations: List[str] = field(default_factory=list)

    # 异常检测标记
    anomaly_flags: List[str] = field(default_factory=list)
    # 例如："unusual_download_volume", "cross_border_access", "off_hours_access",
    # "multiple_failed_access_attempts", "bulk_export"

    # 访问控制
    access_log_id: Optional[str] = None
    data_sharing_agreement: Optional[str] = None  # DUA 编号

    # 扩展
    custom_metrics: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.object_id:
            self.object_id = str(uuid.uuid4())

    def record_access(self, actor_id: str, actor_role: str = "", timestamp: Optional[datetime] = None) -> None:
        """记录一次访问。"""
        self.access_count += 1
        self.last_accessed = timestamp or datetime.utcnow()
        self.last_accessed_by = actor_id
        if actor_role and actor_role not in self.accessor_roles:
            self.accessor_roles.append(actor_role)
        self.unique_accessors = len(set(self.accessor_roles))  # 简化计算

    def record_export(self, bytes_count: int = 0, timestamp: Optional[datetime] = None) -> None:
        """记录一次导出。"""
        self.export_count += 1
        self.last_exported = timestamp or datetime.utcnow()
        self.total_bytes_exported += bytes_count

    def record_download(self, bytes_count: int = 0, timestamp: Optional[datetime] = None) -> None:
        """记录一次下载。"""
        self.download_count += 1
        self.last_downloaded = timestamp or datetime.utcnow()
        self.total_bytes_downloaded += bytes_count

    def add_anomaly_flag(self, flag: str) -> None:
        """添加异常标记。"""
        if flag not in self.anomaly_flags:
            self.anomaly_flags.append(flag)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "object_id": self.object_id,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "last_accessed_by": self.last_accessed_by,
            "access_count": self.access_count,
            "export_count": self.export_count,
            "download_count": self.download_count,
            "last_exported": self.last_exported.isoformat() if self.last_exported else None,
            "last_downloaded": self.last_downloaded.isoformat() if self.last_downloaded else None,
            "total_bytes_exported": self.total_bytes_exported,
            "total_bytes_downloaded": self.total_bytes_downloaded,
            "sharing_status": self.sharing_status,
            "shared_with": self.shared_with,
            "shared_at": self.shared_at.isoformat() if self.shared_at else None,
            "share_expiry": self.share_expiry.isoformat() if self.share_expiry else None,
            "unique_accessors": self.unique_accessors,
            "accessor_roles": self.accessor_roles,
            "accessor_organizations": self.accessor_organizations,
            "anomaly_flags": self.anomaly_flags,
            "access_log_id": self.access_log_id,
            "data_sharing_agreement": self.data_sharing_agreement,
            "custom_metrics": self.custom_metrics,
        }
