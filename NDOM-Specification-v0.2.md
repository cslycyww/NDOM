# NDOM v0.2 — Neural Data Object Model
## Specification Draft

> **定位升级**：从"神经科研数据模型" → **"神经数据安全对象模型"**  
> **核心目标**：让安全属性成为数据对象的一等公民，以 DataObject 为原子单元进行扫描、分类、风险评估。

---

## 1. 架构总览（v0.2 新结构）

```
NDOM (Neural Data Object Model)
│
├── Asset                               # 数据资产层（新增）
│   ├── asset_id
│   ├── owner
│   ├── department
│   ├── location
│   ├── storage_system
│   ├── repository
│   ├── backup_location
│   └── business_system
│
├── Dataset                             # 数据集层（原 NDOMFile 降级）
│   ├── dataset_id
│   ├── description
│   ├── created_at
│   ├── objects: List[DataObject]      # 核心：数据对象列表
│   └── metadata
│
├── DataObject (★ 核心原子单元)         # 每个都是独立安全对象
│   ├── object_id
│   ├── object_type                     # 类型：raw, processed, decoded, embedding
│   ├── parent_object                   # 父对象引用（数据血缘）
│   ├── schema                          # 数据结构描述
│   ├── security_policy                 # 安全策略（下放到对象级）
│   ├── risk_profile                    # 风险画像（新增）
│   ├── provenance                      # 数据血缘（新增）
│   ├── fingerprint                     # 数据指纹（新增）
│   ├── access_metadata                 # 访问元数据（新增）
│   ├── classification                  # 神经数据分类分级
│   ├── risk_tags                       # 风险标签
│   └── audit_log                       # 审计日志（对象级）
│
├── SecurityPolicy                      # 安全策略（可挂到 Dataset 或 DataObject）
├── ConsentRecord                       # 同意记录
├── RiskProfile                         # 风险画像（新增）
├── AuditLog                            # 审计日志
│
├── Classification
│   ├── NeuralDataSensitivity (L1-L5)
│   ├── NeuralModality (enum)
│   ├── DecodingStatus (enum)
│   └── DataObjectType (enum)
│
├── RiskTags                            # 扩展：推断风险标签
├── Provenance                          # 数据血缘链路
├── Fingerprint                         # 数据指纹
└── AccessMetadata                      # 访问元数据
```

### 核心设计变化（v0.1 → v0.2）

| 维度 | v0.1 | v0.2 |
|------|------|------|
| 顶层 | NDOMFile（科研文件） | Dataset（数据集）+ Asset（资产） |
| 安全粒度 | 仅 Dataset 级 | Dataset + DataObject 双级 |
| 核心单元 | NDOMFile | **DataObject** |
| 数据溯源 | 无 | Provenance（完整血缘链） |
| 数据指纹 | 无 | Fingerprint（多维哈希） |
| 风险画像 | 无 | RiskProfile（Neural Privacy Score） |
| 资产属性 | 无 | Asset（DSPM 核心） |
| 访问追踪 | 仅审计日志 | AccessMetadata + 审计日志 |
| 风险标签 | 10 个通用标签 | 10 通用 + 8 推断风险标签 |

---

## 2. Asset（数据资产层）

NDOM v0.2 将数据视为**资产**，增加资产管理属性。

```python
@dataclass
class Asset:
    asset_id: str                         # 资产唯一标识
    asset_name: str
    owner: str                            # 数据所有者（PI/负责人）
    department: str                       # 所属部门/实验室
    location: str                         # 物理存储位置
    storage_system: str                   # 存储系统：S3, DANDI, OneDrive, Local
    repository: Optional[str] = None      # 公共仓库：DANDI, OpenNeuro, Zenodo
    backup_location: Optional[str] = None  # 备份位置
    business_system: Optional[str] = None  # 业务系统：临床试验系统、BCI 平台
    asset_type: str = "neural_dataset"    # 资产类型：neural_dataset, derived_feature, model, decoder
    value_assessment: Optional[str] = None  # 价值评估：high, medium, low
    compliance_scope: List[str] = field(default_factory=list)  # 合规范围：["GDPR", "HIPAA", "CCPA", "DPDPA"]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
```

---

## 3. DataObject（核心原子单元）★

v0.2 最大的架构变化：引入 **DataObject** 作为安全对象的原子单元。

### 3.1 为什么需要 DataObject

| 场景 | 问题 | v0.2 方案 |
|------|------|----------|
| 同一 Dataset 中既有 Raw EEG 又有 Decoded Language | 风险等级不同（L3 vs L5），无法统一控制 | 每个 DataObject 独立 SecurityPolicy |
| Embedding 数据被传播到多个下游 | 无法追踪血缘 | Provenance 记录 parent → child 链 |
| 数据泄露后无法溯源 | 无指纹 | Fingerprint 提供多维哈希 |
| 需要评估"某类数据的整体风险" | 无统一画像 | RiskProfile 生成 Neural Privacy Score |

### 3.2 DataObject 定义

```python
@dataclass
class DataObject:
    object_id: str
    object_type: DataObjectType          # 枚举：RAW, PROCESSED, FEATURE, EMBEDDING, DECODED, ANNOTATION, MODEL
    name: str
    description: Optional[str] = None
    parent_object: Optional[str] = None   # 父对象 object_id（支持数据血缘）
    child_objects: List[str] = field(default_factory=list)  # 子对象 object_ids
    
    # 数据内容
    schema: Optional[DataSchema] = None   # 数据结构描述（新增）
    data_reference: Optional[str] = None  # 数据引用路径（不直接存数据）
    
    # 安全层（每个对象独立）
    security_policy: Optional[SecurityPolicy] = None
    consent_record: Optional[ConsentRecord] = None
    classification: Optional[NeuralDataClass] = None
    risk_tags: Optional[RiskTags] = None
    risk_profile: Optional[RiskProfile] = None   # ★ 新增
    
    # 元数据层（新增）
    provenance: Optional[Provenance] = None
    fingerprint: Optional[Fingerprint] = None
    access_metadata: Optional[AccessMetadata] = None
    
    # 审计（对象级）
    audit_log: AuditLog = field(default_factory=AuditLog)
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    modified_at: datetime = field(default_factory=datetime.utcnow)
```

### 3.3 DataObject 类型枚举

```python
class DataObjectType(str, Enum):
    RAW = "raw"                        # 原始采集数据
    PROCESSED = "processed"            # 预处理数据（滤波、降采样等）
    FEATURE = "feature"                # 特征提取数据（PSD、功率谱等）
    EMBEDDING = "embedding"            # 嵌入向量（深度学习中间层）
    DECODED = "decoded"               # 解码输出（意图、情绪、语言等）
    ANNOTATION = "annotation"        # 人工标注
    MODEL = "model"                    # 模型/解码器
    AGGREGATED = "aggregated"        # 聚合数据
    SYNTHETIC = "synthetic"           # 合成数据
```

---

## 4. SecurityPolicy（策略下放到对象级）

v0.2 核心变化：SecurityPolicy **不再仅在 Dataset 顶层**，而是可以**绑定到每个 DataObject**。

```python
@dataclass
class SecurityPolicy:
    policy_id: str
    privacy_level: PrivacyLevel         # 枚举：PUBLIC, INTERNAL, SENSITIVE, RESTRICTED, NEURAL_SECRET
    data_retention_policy: DataRetentionPolicy
    encryption_at_rest: bool = False
    encryption_in_transit: bool = False
    pseudonymization: bool = False
    differential_privacy_epsilon: Optional[float] = None
    access_control_list: List[AccessRule] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    data_controller: Optional[str] = None
    data_protection_officer: Optional[str] = None
    legal_basis: Optional[str] = None
    cross_border_transfer: bool = False
    transfer_safeguards: List[str] = field(default_factory=list)
    
    # v0.2 新增：数据最小化策略
    data_minimization: bool = False     # 是否仅保留最小必要数据
    purpose_limitation: List[str] = field(default_factory=list)  # 允许的使用目的
    
    def validate_controls(self, sensitivity: NeuralDataSensitivity) -> List[str]:
        """验证控制是否符合敏感度级别的推荐配置。"""
        ...
    
    def validate_for_object(self, obj: DataObject) -> List[str]:
        """根据对象类型和分类自动验证策略。"""
        ...
```

### 4.1 隐私等级枚举（v0.2 扩展）

```python
class PrivacyLevel(str, Enum):
    PUBLIC = "PUBLIC"                   # 可公开共享
    INTERNAL = "INTERNAL"               # 机构内部
    SENSITIVE = "SENSITIVE"             # 敏感数据（v0.2 新增）
    RESTRICTED = "RESTRICTED"           # 受限，需审批
    NEURAL_SECRET = "NEURAL_SECRET"     # 神经机密，最高级别（v0.2 新增）
```

---

## 5. RiskProfile（风险画像）★

**Neural Privacy Score** 的基础。每个 DataObject 独立评估。

```python
@dataclass
class RiskProfile:
    profile_id: str
    assessed_at: datetime
    assessed_by: str
    
    # 各维度风险评分（0-10，10 为最高）
    identity_risk: float = 0.0          # 身份推断风险
    medical_risk: float = 0.0           # 医疗推断风险
    behavioral_risk: float = 0.0        # 行为推断风险
    cognitive_risk: float = 0.0         # 认知推断风险
    emotional_risk: float = 0.0         # 情绪推断风险（v0.2 新增）
    linguistic_risk: float = 0.0        # 语言推断风险（v0.2 新增）
    memory_risk: float = 0.0            # 记忆推断风险（v0.2 新增）
    reconstruction_risk: float = 0.0    # 神经信号重建风险
    
    # 综合评分
    overall_score: float = 0.0          # 综合风险评分（0-100）
    
    # 风险等级（自动计算）
    risk_level: str = "low"             # low, medium, high, critical
    
    # 评分说明
    scoring_method: str = "weighted_sum"  # 评分方法
    scoring_version: str = "v0.2"
    
    # 降级建议
    mitigation_recommendations: List[str] = field(default_factory=list)
```

### 5.1 风险评分计算（参考）

```python
def compute_overall_score(self) -> float:
    """加权计算综合风险评分。"""
    weights = {
        "identity_risk": 1.0,
        "medical_risk": 1.2,
        "behavioral_risk": 0.8,
        "cognitive_risk": 1.5,
        "emotional_risk": 1.0,
        "linguistic_risk": 1.3,
        "memory_risk": 1.4,
        "reconstruction_risk": 1.1,
    }
    total = sum(getattr(self, k) * w for k, w in weights.items())
    max_score = sum(10 * w for w in weights.values())
    score = (total / max_score) * 100
    return round(score, 2)
```

---

## 6. Fingerprint（数据指纹）★

用于数据溯源、重复识别、泄露追踪。

```python
@dataclass
class Fingerprint:
    fingerprint_id: str
    generated_at: datetime
    generated_by: str
    
    # 密码学哈希
    sha256: Optional[str] = None        # 文件级 SHA-256
    md5: Optional[str] = None           # 快速校验
    
    # 感知哈希（抗轻微修改）
    perceptual_hash: Optional[str] = None  # 适用于信号数据
    
    # 结构指纹
    schema_hash: Optional[str] = None   # 数据结构哈希
    
    # 信号特征指纹（神经数据专用）
    channel_signature: Optional[str] = None   # 通道特征签名
    signal_signature: Optional[str] = None     # 信号统计特征签名
    
    # 元数据指纹
    metadata_hash: Optional[str] = None       # 元数据哈希
    
    # 水印（如果已嵌入）
    watermark_id: Optional[str] = None
```

---

## 7. Provenance（数据血缘）★

记录数据的完整生命周期，支持从 Raw → Decoded 的完整追踪。

```python
@dataclass
class Provenance:
    provenance_id: str
    
    # 来源信息
    source_file: Optional[str] = None          # 原始文件路径
    source_dataset: Optional[str] = None         # 来源数据集
    parent_object: Optional[str] = None          # 父对象 object_id
    
    # 处理链
    preprocessing_steps: List[ProcessingStep] = field(default_factory=list)
    
    # 生成信息
    generated_by: Optional[str] = None           # 生成工具/脚本
    generated_by_version: Optional[str] = None    # 工具版本
    model_version: Optional[str] = None          # 模型版本（如果涉及 AI）
    
    # 运行环境
    execution_environment: Optional[str] = None   # 运行环境：Docker, conda, etc.
    compute_platform: Optional[str] = None      # 计算平台
    
    # 时间戳
    created_at: datetime = field(default_factory=datetime.utcnow)
    modified_at: datetime = field(default_factory=datetime.utcnow)
    
    # 完整链路（自动构建）
    lineage_chain: List[str] = field(default_factory=list)  # object_id 链

@dataclass
class ProcessingStep:
    step_id: str
    step_name: str                          # "bandpass_filter", "epoching", "decoding"
    step_type: str                          # "filter", "artifact_removal", "feature_extraction", "decoding", "aggregation"
    input_objects: List[str] = field(default_factory=list)   # 输入对象 object_ids
    output_object: Optional[str] = None      # 输出对象 object_id
    parameters: Dict[str, Any] = field(default_factory=dict) # 参数记录
    tool_name: Optional[str] = None          # 工具名称
    tool_version: Optional[str] = None       # 工具版本
    execution_time_ms: Optional[float] = None  # 执行时间
    timestamp: datetime = field(default_factory=datetime.utcnow)
```

### 7.1 血缘链路示例

```yaml
Raw EEG (obj-001, L3)
  → Provenance:
      preprocessing_steps:
        - step_name: "bandpass_filter"
          step_type: "filter"
          parameters: {low: 0.1, high: 100, order: 4}
          tool_name: "MNE-Python"
          tool_version: "1.6.0"
          output_object: obj-002
    → Filtered EEG (obj-002, L3)
      → Provenance:
          preprocessing_steps:
            - step_name: "power_spectral_density"
              step_type: "feature_extraction"
              parameters: {fmin: 8, fmax: 12, method: "welch"}
              output_object: obj-003
        → PSD Feature (obj-003, L3)
          → Provenance:
              preprocessing_steps:
                - step_name: "intent_decoder"
                  step_type: "decoding"
                  model_version: "intent-v2.1"
                  output_object: obj-004
            → Decoded Intent (obj-004, L5)  ← 最高风险
```

---

## 8. AccessMetadata（访问元数据）★

用于审计、行为分析和异常检测。

```python
@dataclass
class AccessMetadata:
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
    
    # 共享状态
    sharing_status: str = "private"       # private, internal, shared, public
    shared_with: List[str] = field(default_factory=list)  # 共享对象列表
    shared_at: Optional[datetime] = None
    
    # 访问者画像
    unique_accessors: int = 0
    accessor_roles: List[str] = field(default_factory=list)
    
    # 异常检测标记
    anomaly_flags: List[str] = field(default_factory=list)  # "unusual_download_volume", "cross_border_access"
```

---

## 9. RiskTags（扩展推断风险）★

v0.2 扩充风险标签，从通用风险扩展到**推断风险**。

### 9.1 标准风险标签（v0.2 完整版）

| 标签 | 类别 | 描述 |
|------|------|------|
| `reidentification` | 通用 | 重新识别风险 |
| `mental_decoding` | 通用 | 精神状态解码风险 |
| `neurodiscrimination` | 通用 | 神经歧视风险 |
| `cognitive_manipulation` | 通用 | 认知操控风险 |
| `dual_use` | 通用 | 双重用途风险 |
| `cross_domain_inference` | 通用 | 跨域推断风险 |
| `group_level_inference` | 通用 | 群体推断风险 |
| `real_time_monitoring` | 通用 | 实时监控风险 |
| `data_aggregation` | 通用 | 数据聚合风险 |
| `third_party_sharing` | 通用 | 第三方共享风险 |
| `identity_inference` | **推断** | 身份推断（从神经信号推断个人身份） |
| `medical_inference` | **推断** | 医疗推断（疾病、健康状况） |
| `emotion_inference` | **推断** | 情绪推断（情绪状态、情感） |
| `intent_inference` | **推断** | 意图推断（意图、决策） |
| `language_inference` | **推断** | 语言推断（内心言语、语言内容） |
| `memory_inference` | **推断** | 记忆推断（记忆内容、遗忘症） |
| `location_inference` | **推断** | 位置推断（空间导航、位置信息） |
| `biometric_linkage` | **推断** | 生物特征关联（神经指纹与其他生物特征关联） |

---

## 10. Classification（扩展枚举）

v0.2 引入完整枚举体系，所有关键类型标准化。

```python
class NeuralModality(str, Enum):
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

class DecodingStatus(str, Enum):
    RAW = "raw"                              # 原始信号
    PREPROCESSED = "preprocessed"           # 已预处理
    FEATURE_EXTRACTED = "feature_extracted" # 特征提取
    DECODED_INTENT = "decoded_intent"       # 解码意图
    DECODED_EMOTION = "decoded_emotion"     # 解码情绪
    DECODED_COGNITIVE_STATE = "decoded_cognitive_state"  # 解码认知状态
    DECODED_LANGUAGE = "decoded_language"   # 解码语言（v0.2 新增）
    DECODED_MEMORY = "decoded_memory"       # 解码记忆（v0.2 新增）
    SYNTHETIC = "synthetic"                 # 合成数据

class NeuralDataType(str, Enum):
    STRUCTURAL = "structural"               # 结构数据
    FUNCTIONAL_NON_INVASIVE = "functional_non_invasive"  # 非侵入功能
    FUNCTIONAL_INVASIVE = "functional_invasive"           # 侵入功能
    DECODED = "decoded"                     # 解码数据
    MODULATED = "modulated"                 # 调制数据
    SYNTHETIC = "synthetic"                 # 合成数据

class DeviceClass(str, Enum):
    NON_INVASIVE = "non_invasive"           # 非侵入
    SEMI_INVASIVE = "semi_invasive"         # 半侵入
    INVASIVE = "invasive"                   # 侵入
    CONSUMER = "consumer"                   # 消费级
    MEDICAL = "medical"                     # 医疗级
    RESEARCH = "research"                   # 研究级
    MILITARY = "military"                   # 军事级

class RegulatoryStatus(str, Enum):
    MEDICAL = "medical"                     # 医疗器械
    WELLNESS = "wellness"                   #  wellness 设备
    RESEARCH = "research"                   # 研究设备
    CONSUMER = "consumer"                   # 消费设备
    MILITARY = "military"                   # 军事设备
    UNREGULATED = "unregulated"             # 未监管

class ConsentScope(str, Enum):
    PRIMARY_RESEARCH = "primary_research"
    SECONDARY_ANALYSIS = "secondary_analysis"
    DATA_SHARING = "data_sharing"
    COMMERCIAL_USE = "commercial_use"
    AI_TRAINING = "ai_training"
    PUBLIC_RELEASE = "public_release"
    CROSS_BORDER = "cross_border"
```

---

## 11. Dataset（数据集层）

Dataset 是 DataObject 的容器，本身也有安全属性（默认策略）。

```python
@dataclass
class Dataset:
    dataset_id: str
    description: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # 关联资产
    asset: Optional[Asset] = None
    
    # 数据对象列表（核心）
    objects: List[DataObject] = field(default_factory=list)
    
    # 默认安全策略（对象未设置时继承）
    default_security_policy: Optional[SecurityPolicy] = None
    default_consent_record: Optional[ConsentRecord] = None
    
    # 元数据
    subject: Optional[NDOMSubject] = None
    devices: List[NDOMDevice] = field(default_factory=list)
    electrode_groups: List[NDOMElectrodeGroup] = field(default_factory=list)
    electrodes: List[NDOMElectrode] = field(default_factory=list)
    
    # 审计（数据集级）
    audit_log: AuditLog = field(default_factory=AuditLog)
    
    def add_object(self, obj: DataObject):
        """添加数据对象，自动继承默认策略（如果对象未设置）。"""
        if obj.security_policy is None and self.default_security_policy is not None:
            obj.security_policy = self.default_security_policy
        self.objects.append(obj)
    
    def get_object_by_id(self, object_id: str) -> Optional[DataObject]:
        for obj in self.objects:
            if obj.object_id == object_id:
                return obj
        return None
    
    def get_objects_by_type(self, obj_type: DataObjectType) -> List[DataObject]:
        return [obj for obj in self.objects if obj.object_type == obj_type]
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """生成数据集风险汇总。"""
        summary = {
            "total_objects": len(self.objects),
            "objects_by_type": {},
            "risk_distribution": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "max_sensitivity": None,
            "objects_needing_attention": [],
        }
        for obj in self.objects:
            # 按类型统计
            t = obj.object_type.value
            summary["objects_by_type"][t] = summary["objects_by_type"].get(t, 0) + 1
            
            # 风险分布
            if obj.risk_profile:
                summary["risk_distribution"][obj.risk_profile.risk_level] += 1
            
            # 最高敏感度
            if obj.classification:
                sens = obj.classification.sensitivity_level
                if summary["max_sensitivity"] is None or sens.value > summary["max_sensitivity"]:
                    summary["max_sensitivity"] = sens.value
            
            # 需要关注的对象（高/严重风险）
            if obj.risk_profile and obj.risk_profile.risk_level in ("high", "critical"):
                summary["objects_needing_attention"].append(obj.object_id)
        
        return summary
```

---

## 12. NDOM（顶层入口）

```python
@dataclass
class NDOM:
    """NDOM v0.2 顶层入口。"""
    
    version: str = "0.2.0"
    
    # 资产
    asset: Optional[Asset] = None
    
    # 数据集
    dataset: Optional[Dataset] = None
    
    # 全局安全设置
    global_security_policy: Optional[SecurityPolicy] = None
    
    # 元数据
    schema_version: str = "0.2.0"
    compliance_framework: List[str] = field(default_factory=list)  # ["GDPR", "HIPAA"]
    
    def validate(self) -> Dict[str, Any]:
        """全面验证 NDOM 实例。"""
        result = {"valid": True, "errors": [], "warnings": [], "recommendations": []}
        
        if self.asset is None:
            result["warnings"].append("Asset not defined; consider adding asset metadata for DSPM compliance")
        
        if self.dataset is None:
            result["errors"].append("Dataset is required")
            result["valid"] = False
        else:
            # 验证每个对象
            for obj in self.dataset.objects:
                if obj.security_policy is None:
                    result["warnings"].append(f"Object {obj.object_id} has no security policy")
                if obj.fingerprint is None:
                    result["warnings"].append(f"Object {obj.object_id} has no fingerprint")
                if obj.provenance is None:
                    result["warnings"].append(f"Object {obj.object_id} has no provenance")
                if obj.risk_profile is None:
                    result["recommendations"].append(f"Object {obj.object_id} has no risk profile")
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "schema_version": self.schema_version,
            "asset": self.asset.to_dict() if self.asset else None,
            "dataset": self.dataset.to_dict() if self.dataset else None,
            "compliance_framework": self.compliance_framework,
        }
```

---

## 13. BIDS + NDOM 扩展（v0.2）

v0.2 的 BIDS 映射需要支持 DataObject 级别的侧车文件。

```
dataset/
├── dataset_description.json              # BIDS 标准
├── dataset_security.json                 # NDOM 全局安全策略
├── dataset_asset.json                     # NDOM 资产信息（v0.2 新增）
├── dataset_risk_summary.json             # NDOM 风险汇总（v0.2 新增）
├── participants.tsv
├── sub-01/
│   ├── sub-01_asset.json                 # 受试者级资产信息（v0.2 新增）
│   ├── sub-01_security.json
│   ├── ses-01/
│   │   ├── eeg/
│   │   │   ├── sub-01_ses-01_task-rest_run-01_eeg.edf
│   │   │   ├── sub-01_ses-01_task-rest_run-01_eeg.json      # BIDS 侧车
│   │   │   ├── sub-01_ses-01_task-rest_run-01_eeg_security.json    # 安全侧车
│   │   │   ├── sub-01_ses-01_task-rest_run-01_eeg_fingerprint.json   # 指纹侧车（v0.2 新增）
│   │   │   ├── sub-01_ses-01_task-rest_run-01_eeg_provenance.json   # 血缘侧车（v0.2 新增）
│   │   │   └── sub-01_ses-01_task-rest_run-01_eeg_risk_profile.json  # 风险画像侧车（v0.2 新增）
│   │   └── derived/                     # 衍生数据（v0.2 新增）
│   │       ├── sub-01_ses-01_task-rest_run-01_psd.json
│   │       ├── sub-01_ses-01_task-rest_run-01_psd_fingerprint.json
│   │       ├── sub-01_ses-01_task-rest_run-01_psd_provenance.json
│   │       └── sub-01_ses-01_task-rest_run-01_psd_risk_profile.json
│   └── ...
└── derivatives/ndom-security/
    ├── audit_logs/
    └── risk_assessments/
```

---

## 14. 参考标准

1. **BIDS** — Gorgolewski, K.J. et al. (2016). *Scientific Data*.
2. **PyNWB / NWB** — Ruebel, O. et al. (2022). *eLife*.
3. **Ienca et al.** (2021). Towards a Governance Framework for Brain Data. *arXiv:2109.11960*.
4. **GDPR** — Regulation (EU) 2016/679.
5. **CCPA / CPA** — 加州/科罗拉多隐私法（神经数据列为敏感数据）。
6. **W3C PROV** — 数据血缘标准。
7. **DSPM** — Data Security Posture Management 框架。

---

*NDOM v0.2 是一个开放草案，欢迎神经科学、数据安全、DSPM、伦理治理社区共同完善。*
