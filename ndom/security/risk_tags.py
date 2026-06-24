"""NDOM RiskTags — 风险标签

v0.2 扩充：增加推断风险标签（identity_inference, medical_inference 等）。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any


# 标准风险标签（v0.2 完整版）
STANDARD_RISK_TAGS = [
    # 通用风险
    "reidentification",
    "mental_decoding",
    "neurodiscrimination",
    "cognitive_manipulation",
    "dual_use",
    "cross_domain_inference",
    "group_level_inference",
    "real_time_monitoring",
    "data_aggregation",
    "third_party_sharing",
    # 推断风险（v0.2 新增）
    "identity_inference",
    "medical_inference",
    "emotion_inference",
    "intent_inference",
    "language_inference",
    "memory_inference",
    "location_inference",
    "biometric_linkage",
]


@dataclass
class RiskTags:
    """风险标签。

    为 DataObject 附加标准化的风险标签，
    支持多标签组合和自定义风险说明。
    """
    tags: List[str] = field(default_factory=list)
    risk_assessment_date: Optional[datetime] = None
    assessed_by: Optional[str] = None
    reassessment_interval_days: int = 180  # v0.2 从 365 改为 180
    custom_risk_notes: Optional[str] = None

    # v0.2 新增：推断风险专门标记
    inference_risks: List[str] = field(default_factory=list)  # 推断风险子集
    inference_confidence: Optional[float] = None  # 推断风险置信度

    def validate_tags(self) -> List[str]:
        """返回非标准标签（警告）。"""
        return [t for t in self.tags if t not in STANDARD_RISK_TAGS]

    def add_tag(self, tag: str) -> None:
        """添加标签。"""
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        """移除标签。"""
        if tag in self.tags:
            self.tags.remove(tag)

    def is_inference_tag(self, tag: str) -> bool:
        """检查是否为推断风险标签。"""
        inference_tags = [
            "identity_inference", "medical_inference", "emotion_inference",
            "intent_inference", "language_inference", "memory_inference",
            "location_inference", "biometric_linkage",
        ]
        return tag in inference_tags

    def get_inference_tags(self) -> List[str]:
        """获取所有推断风险标签。"""
        return [t for t in self.tags if self.is_inference_tag(t)]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tags": self.tags,
            "risk_assessment_date": self.risk_assessment_date.isoformat() if self.risk_assessment_date else None,
            "assessed_by": self.assessed_by,
            "reassessment_interval_days": self.reassessment_interval_days,
            "custom_risk_notes": self.custom_risk_notes,
            "inference_risks": self.inference_risks,
            "inference_confidence": self.inference_confidence,
        }
