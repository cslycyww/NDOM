"""NDOM RiskProfile — 风险画像

v0.2 新增：Neural Privacy Score 的基础。
每个 DataObject 独立评估，量化各维度推断风险。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

from ndom.enums import RiskLevel


# 风险维度权重（用于计算综合评分）
RISK_WEIGHTS = {
    "identity_risk": 1.0,
    "medical_risk": 1.2,
    "behavioral_risk": 0.8,
    "cognitive_risk": 1.5,
    "emotional_risk": 1.0,
    "linguistic_risk": 1.3,
    "memory_risk": 1.4,
    "reconstruction_risk": 1.1,
}


@dataclass
class RiskProfile:
    """风险画像。
    
    为每个 DataObject 提供多维度的推断风险评分，
    并计算综合 Neural Privacy Score。
    
    Attributes:
        profile_id: 画像唯一标识
        assessed_at: 评估时间
        assessed_by: 评估者/工具
        identity_risk: 身份推断风险 (0-10)
        medical_risk: 医疗推断风险 (0-10)
        behavioral_risk: 行为推断风险 (0-10)
        cognitive_risk: 认知推断风险 (0-10)
        emotional_risk: 情绪推断风险 (0-10)
        linguistic_risk: 语言推断风险 (0-10)
        memory_risk: 记忆推断风险 (0-10)
        reconstruction_risk: 神经信号重建风险 (0-10)
        overall_score: 综合评分 (0-100)
        risk_level: 风险等级 (low, medium, high, critical)
        scoring_method: 评分方法
        scoring_version: 评分版本
        mitigation_recommendations: 降级建议
    """

    profile_id: str
    assessed_at: datetime = field(default_factory=datetime.utcnow)
    assessed_by: str = "ndom-auto"

    # 各维度风险评分（0-10，10 为最高）
    identity_risk: float = 0.0
    medical_risk: float = 0.0
    behavioral_risk: float = 0.0
    cognitive_risk: float = 0.0
    emotional_risk: float = 0.0
    linguistic_risk: float = 0.0
    memory_risk: float = 0.0
    reconstruction_risk: float = 0.0

    # 综合评分
    overall_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW

    # 评分元数据
    scoring_method: str = "weighted_sum"
    scoring_version: str = "v0.2"
    confidence: Optional[float] = None  # 评分置信度 (0-1)

    # 降级建议
    mitigation_recommendations: List[str] = field(default_factory=list)
    threat_model: Optional[str] = None  # 威胁模型引用

    # 扩展
    custom_dimensions: Dict[str, float] = field(default_factory=dict)
    notes: Optional[str] = None

    def __post_init__(self):
        if not self.profile_id:
            self.profile_id = str(uuid.uuid4())
        # 自动计算综合评分和等级
        self._compute_score()

    def _compute_score(self) -> None:
        """加权计算综合风险评分。"""
        total = 0.0
        max_total = 0.0
        for dim, weight in RISK_WEIGHTS.items():
            val = getattr(self, dim, 0.0)
            total += val * weight
            max_total += 10.0 * weight
        if max_total > 0:
            self.overall_score = round((total / max_total) * 100, 2)
        self._compute_level()

    def _compute_level(self) -> None:
        """根据综合评分计算风险等级。"""
        if self.overall_score >= 80:
            self.risk_level = RiskLevel.CRITICAL
        elif self.overall_score >= 60:
            self.risk_level = RiskLevel.HIGH
        elif self.overall_score >= 30:
            self.risk_level = RiskLevel.MEDIUM
        else:
            self.risk_level = RiskLevel.LOW

    def get_dimension_score(self, dimension: str) -> Optional[float]:
        """获取指定维度的风险评分。"""
        if hasattr(self, dimension):
            return getattr(self, dimension)
        return self.custom_dimensions.get(dimension)

    def is_critical(self) -> bool:
        return self.risk_level == RiskLevel.CRITICAL

    def needs_attention(self) -> bool:
        return self.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "assessed_at": self.assessed_at.isoformat(),
            "assessed_by": self.assessed_by,
            "identity_risk": self.identity_risk,
            "medical_risk": self.medical_risk,
            "behavioral_risk": self.behavioral_risk,
            "cognitive_risk": self.cognitive_risk,
            "emotional_risk": self.emotional_risk,
            "linguistic_risk": self.linguistic_risk,
            "memory_risk": self.memory_risk,
            "reconstruction_risk": self.reconstruction_risk,
            "overall_score": self.overall_score,
            "risk_level": self.risk_level.value,
            "scoring_method": self.scoring_method,
            "scoring_version": self.scoring_version,
            "confidence": self.confidence,
            "mitigation_recommendations": self.mitigation_recommendations,
            "threat_model": self.threat_model,
            "custom_dimensions": self.custom_dimensions,
            "notes": self.notes,
        }
