"""NDOM Classification — 神经数据分类分级

v0.2 扩展：使用完整枚举体系。
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import uuid

from ndom.enums import (
    NeuralDataSensitivity, NeuralDataType, NeuralModality,
    SpatialResolution, TemporalResolution, IdentifiabilityRisk,
    DecodingStatus,
)


@dataclass
class NeuralDataClass:
    """神经数据分类分级。

    为每个 DataObject 提供完整的分类信息，
    支持自动化的安全策略推荐和风险评估。
    """
    classification_id: str
    sensitivity_level: NeuralDataSensitivity

    data_type: Optional[NeuralDataType] = None
    modality: Optional[NeuralModality] = None
    spatial_resolution: Optional[SpatialResolution] = None
    temporal_resolution: Optional[TemporalResolution] = None
    decoding_status: Optional[DecodingStatus] = None
    identifiability_risk: Optional[IdentifiabilityRisk] = None
    mental_content_disclosure_risk: Optional[IdentifiabilityRisk] = None

    # v0.2 新增
    data_quality: Optional[str] = None  # high, medium, low
    artifact_level: Optional[str] = None  # none, mild, moderate, severe
    preprocessing_applied: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.classification_id:
            self.classification_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "classification_id": self.classification_id,
            "sensitivity_level": self.sensitivity_level.value,
            "data_type": self.data_type.value if self.data_type else None,
            "modality": self.modality.value if self.modality else None,
            "spatial_resolution": self.spatial_resolution.value if self.spatial_resolution else None,
            "temporal_resolution": self.temporal_resolution.value if self.temporal_resolution else None,
            "decoding_status": self.decoding_status.value if self.decoding_status else None,
            "identifiability_risk": self.identifiability_risk.value if self.identifiability_risk else None,
            "mental_content_disclosure_risk": self.mental_content_disclosure_risk.value if self.mental_content_disclosure_risk else None,
            "data_quality": self.data_quality,
            "artifact_level": self.artifact_level,
            "preprocessing_applied": self.preprocessing_applied,
        }
