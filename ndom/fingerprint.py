"""NDOM Fingerprint — 数据指纹

v0.2 新增：用于数据溯源、重复识别、泄露追踪。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import uuid


@dataclass
class Fingerprint:
    """数据指纹。
    
    提供多维度的数据指纹，支持：
    - 密码学哈希（完整性校验）
    - 感知哈希（抗轻微修改，重复检测）
    - 结构指纹（schema 一致性）
    - 信号特征指纹（神经数据专用）
    - 水印（主动追踪）
    """

    fingerprint_id: str
    generated_at: datetime = field(default_factory=datetime.utcnow)
    generated_by: str = "ndom"

    # 密码学哈希
    sha256: Optional[str] = None            # 文件级 SHA-256
    md5: Optional[str] = None               # 快速校验
    blake3: Optional[str] = None             # 高性能哈希

    # 感知哈希（抗轻微修改）
    perceptual_hash: Optional[str] = None   # 适用于信号数据的感知哈希

    # 结构指纹
    schema_hash: Optional[str] = None       # 数据结构/Schema 哈希
    metadata_hash: Optional[str] = None     # 元数据哈希

    # 信号特征指纹（神经数据专用）
    channel_signature: Optional[str] = None   # 通道特征签名（通道数、采样率、电极位置等）
    signal_signature: Optional[str] = None     # 信号统计特征签名（均值、方差、功率谱特征等）
    temporal_signature: Optional[str] = None   # 时间特征签名（时长、事件数等）

    # 水印
    watermark_id: Optional[str] = None
    watermark_type: Optional[str] = None      # "robust", "fragile", "reversible"

    # 扩展
    custom_hashes: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if not self.fingerprint_id:
            self.fingerprint_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fingerprint_id": self.fingerprint_id,
            "generated_at": self.generated_at.isoformat(),
            "generated_by": self.generated_by,
            "sha256": self.sha256,
            "md5": self.md5,
            "blake3": self.blake3,
            "perceptual_hash": self.perceptual_hash,
            "schema_hash": self.schema_hash,
            "metadata_hash": self.metadata_hash,
            "channel_signature": self.channel_signature,
            "signal_signature": self.signal_signature,
            "temporal_signature": self.temporal_signature,
            "watermark_id": self.watermark_id,
            "watermark_type": self.watermark_type,
            "custom_hashes": self.custom_hashes,
        }
