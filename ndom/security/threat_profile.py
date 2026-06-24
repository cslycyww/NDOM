"""NDOM ThreatProfile — 攻击模型/威胁画像

v0.2 新增：为每个 DataObject 提供攻击面分析、威胁参与者评估、
攻击场景和缓解措施，支撑 NeuroATT&CK 框架映射。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

from ndom.enums import RiskLevel


# 标准攻击面（NeuroATT&CK 参考）
STANDARD_ATTACK_SURFACES = [
    "export",
    "sharing",
    "cloud_storage",
    "model_training",
    "inference_api",
    "data_ingestion",
    "third_party_integration",
    "backup",
    "replication",
    "analytics_pipeline",
]

# 标准威胁参与者
STANDARD_THREAT_ACTORS = [
    "insider_malicious",
    "insider_negligent",
    "external_hacker",
    "competitor",
    "nation_state",
    "criminal_organization",
    "researcher_misuse",
    "third_party_vendor",
    "ai_system",
]

# 标准攻击场景（神经数据特有）
STANDARD_ATTACK_SCENARIOS = [
    "mental_decoding_exfiltration",
    "reidentification_via_neural_signature",
    "model_inversion_attack",
    "membership_inference",
    "attribute_inference",
    "synthetic_data_reconstruction",
    "cross_dataset_linkage",
    "consent_bypass",
    "privilege_escalation",
    "data_aggregation_attack",
    "side_channel_inference",
    "adversarial_decoding",
]


@dataclass
class ThreatProfile:
    """威胁画像。

    为 DataObject 提供攻击模型评估，识别攻击面、威胁参与者、
    攻击场景和缓解措施，支撑 NeuroATT&CK 框架映射。

    Attributes:
        threat_profile_id: 画像唯一标识
        attack_surface: 攻击面列表
        threat_actors: 威胁参与者列表
        attack_scenarios: 攻击场景列表
        mitigations: 缓解措施列表
        risk_level: 综合威胁风险等级
        assessment_date: 评估时间
        assessed_by: 评估者/工具
        neuroattck_mapping: NeuroATT&CK 技术映射 ID
        notes: 备注
    """

    threat_profile_id: str
    attack_surface: List[str] = field(default_factory=list)
    threat_actors: List[str] = field(default_factory=list)
    attack_scenarios: List[str] = field(default_factory=list)
    mitigations: List[str] = field(default_factory=list)

    risk_level: RiskLevel = RiskLevel.LOW
    assessment_date: datetime = field(default_factory=datetime.utcnow)
    assessed_by: str = "ndom-threat-engine"

    # NeuroATT&CK 框架映射
    neuroattck_mapping: Optional[str] = None  # 例如 "T0012.003"
    neuroattck_techniques: List[str] = field(default_factory=list)

    notes: Optional[str] = None

    def __post_init__(self):
        if not self.threat_profile_id:
            self.threat_profile_id = str(uuid.uuid4())
        self._compute_risk_level()

    def _compute_risk_level(self) -> None:
        """根据攻击面、威胁参与者和攻击场景数量计算风险等级。"""
        score = 0
        score += len(self.attack_surface) * 5
        score += len(self.threat_actors) * 8
        score += len(self.attack_scenarios) * 15  # 攻击场景权重最高（神经数据特有）
        score -= len(self.mitigations) * 3

        if score >= 80:
            self.risk_level = RiskLevel.CRITICAL
        elif score >= 45:
            self.risk_level = RiskLevel.HIGH
        elif score >= 20:
            self.risk_level = RiskLevel.MEDIUM
        else:
            self.risk_level = RiskLevel.LOW

    def add_attack_surface(self, surface: str) -> None:
        """添加攻击面。"""
        if surface not in self.attack_surface:
            self.attack_surface.append(surface)
            self._compute_risk_level()

    def add_threat_actor(self, actor: str) -> None:
        """添加威胁参与者。"""
        if actor not in self.threat_actors:
            self.threat_actors.append(actor)
            self._compute_risk_level()

    def add_attack_scenario(self, scenario: str) -> None:
        """添加攻击场景。"""
        if scenario not in self.attack_scenarios:
            self.attack_scenarios.append(scenario)
            self._compute_risk_level()

    def add_mitigation(self, mitigation: str) -> None:
        """添加缓解措施。"""
        if mitigation not in self.mitigations:
            self.mitigations.append(mitigation)
            self._compute_risk_level()

    def validate_surfaces(self) -> List[str]:
        """返回非标准攻击面（警告）。"""
        return [s for s in self.attack_surface if s not in STANDARD_ATTACK_SURFACES]

    def validate_actors(self) -> List[str]:
        """返回非标准威胁参与者（警告）。"""
        return [a for a in self.threat_actors if a not in STANDARD_THREAT_ACTORS]

    def validate_scenarios(self) -> List[str]:
        """返回非标准攻击场景（警告）。"""
        return [s for s in self.attack_scenarios if s not in STANDARD_ATTACK_SCENARIOS]

    def is_critical(self) -> bool:
        return self.risk_level == RiskLevel.CRITICAL

    def needs_attention(self) -> bool:
        return self.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "threat_profile_id": self.threat_profile_id,
            "attack_surface": self.attack_surface,
            "threat_actors": self.threat_actors,
            "attack_scenarios": self.attack_scenarios,
            "mitigations": self.mitigations,
            "risk_level": self.risk_level.value,
            "assessment_date": self.assessment_date.isoformat(),
            "assessed_by": self.assessed_by,
            "neuroattck_mapping": self.neuroattck_mapping,
            "neuroattck_techniques": self.neuroattck_techniques,
            "notes": self.notes,
        }
