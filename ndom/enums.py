"""NDOM Enums — v0.2 完整枚举定义

所有关键类型标准化，避免实现时的不一致。
"""

from enum import Enum


class PrivacyLevel(str, Enum):
    """隐私等级（v0.2 扩展为5级）。"""
    PUBLIC = "PUBLIC"                   # 可公开共享
    INTERNAL = "INTERNAL"               # 机构内部
    SENSITIVE = "SENSITIVE"             # 敏感数据
    RESTRICTED = "RESTRICTED"           # 受限，需审批
    NEURAL_SECRET = "NEURAL_SECRET"     # 神经机密，最高级别


class NeuralDataSensitivity(str, Enum):
    """神经数据敏感度分级。"""
    L1 = "L1"   # 结构基础
    L2 = "L2"   # 非侵入功能（群体）
    L3 = "L3"   # 个体非侵入功能
    L4 = "L4"   # 侵入性神经信号
    L5 = "L5"   # 解码神经内容


class NeuralModality(str, Enum):
    """神经数据模态（v0.2 扩展）。"""
    EEG = "EEG"
    fMRI = "fMRI"
    iEEG = "iEEG"
    ECoG = "ECoG"
    MEG = "MEG"
    fNIRS = "fNIRS"
    BCI = "BCI"
    NEUROMODULATION = "neuromodulation"
    SPIKE = "spike"
    LFP = "LFP"
    MULTIUNIT = "multiunit"
    MRI = "MRI"
    CT = "CT"
    PET = "PET"


class DecodingStatus(str, Enum):
    """解码状态（v0.2 扩展）。"""
    RAW = "raw"
    PREPROCESSED = "preprocessed"
    FEATURE_EXTRACTED = "feature_extracted"
    DECODED_INTENT = "decoded_intent"
    DECODED_EMOTION = "decoded_emotion"
    DECODED_COGNITIVE_STATE = "decoded_cognitive_state"
    DECODED_LANGUAGE = "decoded_language"       # v0.2 新增
    DECODED_MEMORY = "decoded_memory"           # v0.2 新增
    SYNTHETIC = "synthetic"


class NeuralDataType(str, Enum):
    """神经数据类型。"""
    STRUCTURAL = "structural"
    FUNCTIONAL_NON_INVASIVE = "functional_non_invasive"
    FUNCTIONAL_INVASIVE = "functional_invasive"
    DECODED = "decoded"
    MODULATED = "modulated"
    SYNTHETIC = "synthetic"


class DataObjectType(str, Enum):
    """数据对象类型（v0.2 核心枚举）。"""
    RAW = "raw"                           # 原始采集数据
    PROCESSED = "processed"              # 预处理数据（滤波、降采样等）
    FEATURE = "feature"                  # 特征提取数据（PSD、功率谱等）
    EMBEDDING = "embedding"               # 嵌入向量（深度学习中间层）
    DECODED = "decoded"                  # 解码输出（意图、情绪、语言等）
    ANNOTATION = "annotation"            # 人工标注
    MODEL = "model"                      # 模型/解码器
    AGGREGATED = "aggregated"           # 聚合数据
    SYNTHETIC = "synthetic"             # 合成数据
    METADATA = "metadata"               # 纯元数据


class DeviceClass(str, Enum):
    """设备分类。"""
    NON_INVASIVE = "non_invasive"
    SEMI_INVASIVE = "semi_invasive"
    INVASIVE = "invasive"
    CONSUMER = "consumer"
    MEDICAL = "medical"
    RESEARCH = "research"
    MILITARY = "military"


class RegulatoryStatus(str, Enum):
    """监管状态。"""
    MEDICAL = "medical"
    WELLNESS = "wellness"
    RESEARCH = "research"
    CONSUMER = "consumer"
    MILITARY = "military"
    UNREGULATED = "unregulated"


class ConsentType(str, Enum):
    """同意类型。"""
    EXPLICIT_INFORMED = "explicit_informed"
    BROAD_CONSENT = "broad_consent"
    IMPLIED = "implied"
    MANDATED = "mandated"


class ConsentScope(str, Enum):
    """同意范围（v0.2 新增）。"""
    PRIMARY_RESEARCH = "primary_research"
    SECONDARY_ANALYSIS = "secondary_analysis"
    DATA_SHARING = "data_sharing"
    COMMERCIAL_USE = "commercial_use"
    AI_TRAINING = "ai_training"
    PUBLIC_RELEASE = "public_release"
    CROSS_BORDER = "cross_border"


class DataRetentionPolicyType(str, Enum):
    """数据保留策略类型。"""
    SESSION_ONLY = "session_only"
    PROJECT_DURATION = "project_duration"
    LEGAL_REQUIREMENT = "legal_requirement"
    INDEFINITE = "indefinite"


class ActionType(str, Enum):
    """审计操作类型。"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    SHARE = "share"
    ANONYMIZE = "anonymize"
    PSEUDONYMIZE = "pseudonymize"
    ACCESS = "access"
    DOWNLOAD = "download"
    DECODE = "decode"


class SpatialResolution(str, Enum):
    """空间分辨率。"""
    WHOLE_BRAIN = "whole_brain"
    REGIONAL = "regional"
    LAMINAR = "laminar"
    SINGLE_UNIT = "single_unit"


class TemporalResolution(str, Enum):
    """时间分辨率。"""
    STATIC = "static"
    SLOW = "slow"
    FAST = "fast"
    REAL_TIME = "real_time"


class IdentifiabilityRisk(str, Enum):
    """可识别风险。"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CERTAIN = "certain"


class RiskLevel(str, Enum):
    """风险等级。"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SharingStatus(str, Enum):
    """共享状态。"""
    PRIVATE = "private"
    INTERNAL = "internal"
    SHARED = "shared"
    PUBLIC = "public"
