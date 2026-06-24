"""NDOM Asset — 数据资产层

v0.2 新增：将神经数据视为企业/机构资产，支持 DSPM 数据安全态势管理。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid


@dataclass
class Asset:
    """数据资产信息。
    
    NDOM v0.2 将数据从"科研文件"升级为"数据资产"，支持资产管理、
    合规审计、安全态势管理（DSPM）等场景。
    """

    asset_id: str
    asset_name: str
    owner: str                              # 数据所有者（PI/负责人/团队）
    department: str                         # 所属部门/实验室/机构
    location: str                           # 物理存储位置（数据中心、云区域等）
    storage_system: str                     # 存储系统：S3, DANDI, OneDrive, Local, NAS

    # 可选
    repository: Optional[str] = None          # 公共仓库：DANDI, OpenNeuro, Zenodo, Figshare
    backup_location: Optional[str] = None   # 备份位置
    business_system: Optional[str] = None   # 业务系统：临床试验系统、BCI 平台、教学系统
    asset_type: str = "neural_dataset"      # 资产类型
    value_assessment: Optional[str] = None    # 价值评估：high, medium, low
    compliance_scope: List[str] = field(default_factory=list)  # ["GDPR", "HIPAA", "CCPA", "DPDPA"]

    # 时间戳
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # 扩展
    tags: List[str] = field(default_factory=list)
    custom_properties: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.asset_id:
            self.asset_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "asset_name": self.asset_name,
            "owner": self.owner,
            "department": self.department,
            "location": self.location,
            "storage_system": self.storage_system,
            "repository": self.repository,
            "backup_location": self.backup_location,
            "business_system": self.business_system,
            "asset_type": self.asset_type,
            "value_assessment": self.value_assessment,
            "compliance_scope": self.compliance_scope,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags,
            "custom_properties": self.custom_properties,
        }
