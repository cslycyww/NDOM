# NDOM — Neural Data Object Model
## 规范草案 v0.1.0

> **核心定位**：PyNWB 对象模型 + BIDS 元数据规范 + 神经数据安全标签层

---

## 1. 背景与动机

### 1.1 现有标准的局限

| 标准 | 贡献 | 缺失 |
|------|------|------|
| **BIDS** | 目录结构、文件命名、元数据、采集参数 | ❌ 安全属性、❌ 风险标签、❌ 隐私等级、❌ 神经数据分类分级 |
| **PyNWB/NWB** | Subject、Device、Electrode、Session、Acquisition、Processing 对象模型 | ❌ 安全标签、❌ 隐私控制、❌ 神经数据分类 |
| **GDPR / CCPA** | 个人数据保护框架 | ❌ 神经数据特异性分类、❌ 技术元数据绑定 |

### 1.2 为什么需要 NDOM

神经数据具有**不可替代的敏感性**：
- **不可匿名化**：EEG/fMRI 神经信号可被重新识别（Schwarz et al., 2019）
- **不可控性**：数据采集过程不受主体意识控制
- **可推断性**：AI 可从神经信号解码意图、情绪、认知状态
- **双重用途**：消费级 BCI 数据可能具有军事/监控用途
- **神经歧视风险**：基于神经特征（如认知衰退早期标志）的歧视

NDOM 在现有科学数据标准之上，增加**原生安全层**，使安全属性成为数据对象的一等公民（first-class citizen），而非外部附件。

---

## 2. NDOM 架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                        NDOM 三层架构                            │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3: 安全标签层 (Security Tag Layer)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ PrivacyLevel │  │ NeuralData   │  │ RiskTags     │          │
│  │ 隐私等级     │  │ Classification│  │ 风险标签     │          │
│  └──────────────┘  │ 神经数据分类 │  └──────────────┘          │
│                    └──────────────┘                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ ConsentStatus  │  │ Security     │  │ AuditLog     │          │
│  │ 同意状态     │  │ Controls     │  │ 审计日志     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2: BIDS 元数据层 (Metadata Layer)                         │
│  ├── dataset_description.json                                    │
│  ├── participants.tsv + participants.json                        │
│  ├── *_sidecar.json (TSV/JSON 元数据)                          │
│  ├── Events (events.tsv)                                         │
│  └── NDOM 新增: *_security.json, *_consent.json                 │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1: 对象模型层 (Object Model Layer)                        │
│  ├── NDOMFile (继承 NWBFile 语义)                              │
│  ├── Subject, Device, DeviceModel                              │
│  ├── ElectrodeGroup, Electrode                                 │
│  ├── Acquisition, ProcessingModule                             │
│  ├── TimeSeries, TimeIntervals, Units                          │
│  └── NDOM 新增: SecurityPolicy, ConsentRecord, NeuralDataClass │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Layer 1: 对象模型层

### 3.1 核心对象

基于 PyNWB/NWB 的成熟对象模型，NDOM 保留全部语义，并扩展安全对象。

#### 3.1.1 NDOMFile

NDOM 的顶层容器，对应一个数据集或一次会话。

```yaml
NDOMFile:
  # 继承自 NWBFile
  session_description: str           # 会话描述
  identifier: str                   # 唯一标识符
  session_start_time: datetime      # 会话开始时间
  file_create_date: datetime        # 文件创建时间
  experimenter: str | list[str]     # 实验者
  institution: str                  # 机构
  experiment_description: str        # 实验描述
  keywords: list[str]               # 关键词
  
  # 子对象容器
  subject: Subject                   # 受试者信息
  devices: list[Device]             # 设备
  electrode_groups: list[ElectrodeGroup]
  electrodes: ElectrodesTable        # 电极表
  acquisition: list[NDOMDataInterface]   # 原始采集数据
  processing: list[ProcessingModule]    # 处理模块
  analysis: list[NDOMContainer]         # 分析结果
  stimulus: list[TimeSeries]        # 刺激
  intervals: list[TimeIntervals]    # 时间区间
  units: Units                       # 单元记录
  
  # NDOM 新增安全属性
  security_policy: SecurityPolicy   # 安全策略（全局）
  consent_record: ConsentRecord    # 同意记录（全局）
  neural_data_class: NeuralDataClass  # 神经数据分类（全局）
  audit_log: AuditLog               # 审计日志
```

#### 3.1.2 Subject

继承 PyNWB 的 `Subject`，字段完全兼容。

```yaml
Subject:
  subject_id: str           # 唯一受试者标识
  age: str                  # 年龄，ISO 8601 Duration，如 "P25Y"
  sex: str                  # "F", "M", "U", "O"
  species: str              # 拉丁双名，如 "Homo sapiens"
  genotype: str             # 基因型（如适用）
  strain: str              # 品系（如适用）
  weight: str              # 体重，含单位
  date_of_birth: datetime   # 出生日期
  description: str          # 描述
  
  # NDOM 新增
  pseudonym_id: str         # 假名标识（用于去标识化）
  vulnerability_tags: list[str]  # 脆弱性标签：["cognitive_impairment", "minor", "military_personnel"]
```

#### 3.1.3 Device & DeviceModel

继承 PyNWB，兼容 NWB 2.0+ 的 `DeviceModel` 分离设计。

```yaml
Device:
  name: str
  description: str
  serial_number: str
  model: DeviceModel          # 关联模型
  
  # NDOM 新增
  security_certification: str  # 安全认证（如 FDA, CE, ISO 27001）
  firmware_version: str         # 固件版本
  data_integrity_hash: str    # 固件/配置完整性哈希

DeviceModel:
  name: str
  manufacturer: str
  model_number: str
  description: str
  
  # NDOM 新增
  device_class: str            # 设备分类："invasive", "semi_invasive", "non_invasive", "consumer"
  neural_access_level: int     # 神经访问级别：1-5
  regulatory_status: str        # 监管状态："medical", "wellness", "research", "military"
```

### 3.2 NDOM 新增安全对象

#### 3.2.1 SecurityPolicy

定义数据集级别的安全策略。

```yaml
SecurityPolicy:
  policy_id: str                    # 策略唯一标识
  privacy_level: PrivacyLevel       # 隐私等级（枚举）
  data_retention_policy: DataRetentionPolicy  # 保留策略
  encryption_at_rest: bool           # 静态加密
  encryption_in_transit: bool        # 传输加密
  pseudonymization: bool            # 假名化
  differential_privacy_epsilon: float | null  # 差分隐私参数
  access_control_list: list[AccessRule]     # 访问控制规则
  created_at: datetime              # 策略创建时间
  updated_at: datetime              # 策略更新时间
  data_controller: str             # 数据控制者
  legal_basis: str                  # 法律依据（如 "GDPR_Art9", "HIPAA", "research_ethics"）
  cross_border_transfer: bool       # 是否跨境传输
  transfer_safeguards: list[str]    # 传输保障措施（如 "SCC", "BCR", "adequacy_decision"）
```

#### 3.2.2 ConsentRecord

记录同意状态，支持分层同意。

```yaml
ConsentRecord:
  consent_id: str                   # 同意记录标识
  consent_type: str                 # 类型："explicit_informed", "broad_consent", "implied", "mandated"
  consent_scope: list[str]          # 同意范围：["primary_research", "secondary_analysis", "data_sharing", "commercial_use"]
  consent_withdrawable: bool        # 是否可撤回
  withdrawal_date: datetime | null   # 撤回日期
  consent_document_version: str     # 同意书版本
  data_use_limitations: list[str]   # 数据使用限制
  recontact_allowed: bool           # 是否允许重新联系
  specific_consent_for: list[str]   # 特定同意事项
  recorded_by: str                 # 记录者
  recorded_at: datetime            # 记录时间
  digital_signature: str | null     # 数字签名
```

#### 3.2.3 NeuralDataClass

神经数据分类分级对象。

```yaml
NeuralDataClass:
  classification_id: str
  sensitivity_level: NeuralDataSensitivity  # 敏感度级别：L1-L5
  data_type: str                     # 数据类型："structural", "functional_non_invasive", "functional_invasive", "decoded", "modulated"
  modality: str                       # 模态："EEG", "fMRI", "iEEG", "ECoG", "MEG", "fNIRS", "BCI", "neuromodulation"
  spatial_resolution: str           # 空间分辨率："whole_brain", "regional", "laminar", "single_unit"
  temporal_resolution: str          # 时间分辨率："static", "slow", "fast", "real_time"
  decoding_status: str               # 解码状态："raw", "feature_extracted", "decoded_intent", "decoded_emotion", "decoded_cognitive_state"
  identifiability_risk: str         # 可识别风险："none", "low", "medium", "high", "certain"
  mental_content_disclosure_risk: str  # 精神内容披露风险："none", "low", "medium", "high", "certain"
```

#### 3.2.4 RiskTags

风险标签系统，支持多标签。

```yaml
RiskTags:
  tags: list[str]                    # 风险标签列表
  risk_assessment_date: datetime     # 评估日期
  assessed_by: str                   # 评估者
  reassessment_interval_days: int    # 重新评估间隔（天）
  custom_risk_notes: str            # 自定义风险说明
```

标准风险标签：
- `reidentification` — 重新识别风险
- `mental_decoding` — 精神状态解码风险
- `neurodiscrimination` — 神经歧视风险
- `cognitive_manipulation` — 认知操控风险
- `dual_use` — 双重用途风险
- `cross_domain_inference` — 跨域推断风险（与社交媒体、基因数据等结合）
- `group_level_inference` — 群体推断风险
- `real_time_monitoring` — 实时监控风险
- `data_aggregation` — 数据聚合风险
- `third_party_sharing` — 第三方共享风险

#### 3.2.5 AuditLog

审计日志，记录数据访问和变更。

```yaml
AuditLog:
  log_entries: list[AuditEntry]

AuditEntry:
  entry_id: str
  timestamp: datetime
  action: str                        # "create", "read", "update", "delete", "export", "share", "anonymize"
  actor_id: str                     # 操作者标识
  actor_role: str                   # 角色："researcher", "data_curator", "system", "admin", "subject"
  target_object: str                # 目标对象（object_id）
  target_object_type: str            # 对象类型
  access_granted: bool               # 是否授权访问
  reason: str                       # 操作理由
  ip_address: str | null            # IP地址（如适用）
  data_transformations: list[str]    # 数据转换：["pseudonymized", "aggregated", "differentially_private"]
```

---

## 4. Layer 2: BIDS 元数据层

### 4.1 继承的 BIDS 结构

NDOM 完全兼容 BIDS 目录结构，并在 BIDS 命名实体基础上扩展 NDOM 安全实体。

#### 4.1.1 标准 BIDS 实体

| 实体 | 键 | 说明 |
|------|-----|------|
| 受试者 | sub | 受试者标识 |
| 会话 | ses | 会话标识 |
| 任务 | task | 任务名称 |
| 采集 | acq | 采集参数标签 |
| 运行 | run | 运行编号 |
| 模态 | modality | eeg, ieeg, func, anat, meg, fNIRS 等 |

#### 4.1.2 标准 BIDS 文件

```
dataset/
├── dataset_description.json
├── participants.tsv
├── participants.json
├── README
├── CHANGES
├── code/
├── stimuli/
├── sub-01/
│   ├── ses-01/
│   │   ├── eeg/
│   │   │   ├── sub-01_ses-01_task-rest_run-01_eeg.edf
│   │   │   ├── sub-01_ses-01_task-rest_run-01_eeg.json      # BIDS 侧车
│   │   │   ├── sub-01_ses-01_task-rest_run-01_events.tsv    # BIDS 事件
│   │   │   ├── sub-01_ses-01_task-rest_run-01_channels.tsv # BIDS 通道
│   │   │   └── ...
│   │   └── anat/
│   └── ses-02/
└── sub-02/
```

### 4.2 NDOM 扩展元数据

#### 4.2.1 安全侧车文件: `*_security.json`

每个数据文件可附带安全侧车，描述该文件的安全属性。

```json
{
  "ndom_version": "0.1.0",
  "privacy_level": "RESTRICTED",
  "sensitivity_level": "L4",
  "risk_tags": ["reidentification", "mental_decoding"],
  "security_controls": {
    "encryption_at_rest": true,
    "encryption_in_transit": true,
    "pseudonymization": true,
    "differential_privacy_epsilon": null
  },
  "data_retention_policy": {
    "policy_type": "project_duration",
    "retention_end_date": "2027-12-31",
    "destruction_method": "cryptographic_erasure"
  },
  "audit_enabled": true,
  "last_security_review": "2025-06-01T00:00:00Z",
  "next_security_review": "2026-06-01T00:00:00Z"
}
```

#### 4.2.2 同意侧车文件: `*_consent.json`

```json
{
  "consent_id": "consent-2025-001-sub-01",
  "consent_type": "explicit_informed",
  "consent_scope": ["primary_research", "secondary_analysis"],
  "consent_withdrawable": true,
  "withdrawal_date": null,
  "data_use_limitations": ["non-commercial", "academic-only"],
  "recontact_allowed": false,
  "consent_document_version": "v2.3",
  "recorded_at": "2025-01-15T09:00:00Z",
  "digital_signature": "sha256:a1b2c3d4..."
}
```

#### 4.2.3 数据集级安全文件: `dataset_security.json`

位于数据集根目录，定义全局安全策略。

```json
{
  "ndom_version": "0.1.0",
  "dataset_id": "ds-ndom-001",
  "security_policy": {
    "policy_id": "sp-001",
    "privacy_level": "RESTRICTED",
    "legal_basis": "GDPR_Art9",
    "data_controller": "ETH Zurich Neuroethics Lab",
    "data_protection_officer": "dpo@ethz.ch",
    "cross_border_transfer": false,
    "transfer_safeguards": []
  },
  "neural_data_class": {
    "sensitivity_level": "L3",
    "data_type": "functional_non_invasive",
    "modality": "EEG",
    "decoding_status": "raw",
    "identifiability_risk": "high",
    "mental_content_disclosure_risk": "medium"
  },
  "default_risk_tags": ["reidentification", "cross_domain_inference"],
  "consent_framework": "broad_consent",
  "minimum_security_controls": {
    "encryption_at_rest": true,
    "encryption_in_transit": true,
    "pseudonymization": true
  }
}
```

---

## 5. Layer 3: 安全标签层

### 5.1 隐私等级 (PrivacyLevel)

| 等级 | 标识符 | 描述 | 访问控制 | 典型场景 |
|------|--------|------|----------|----------|
| **公开** | PUBLIC | 完全去标识化，可公开共享 | 无限制 | 群体水平统计图、聚合特征 |
| **内部** | INTERNAL | 机构内部使用，需认证 | 机构账号 | 实验室内部分析 |
| **受限** | RESTRICTED | 需审批和协议 | 数据使用协议 (DUA) | 多中心合作研究 |
| **机密** | CONFIDENTIAL | 严格最小化访问 | 角色基础 + 最小权限 | 临床侵入性数据 |
| **关键** | CRITICAL | 最高级别，持续监控 | 双人控制 + 实时审计 | 植入式 BCI 原始信号、军事数据 |

### 5.2 神经数据敏感度分级 (NeuralDataSensitivity)

| 级别 | 名称 | 数据类型 | 风险特征 | 示例 |
|------|------|----------|----------|------|
| **L1** | 结构基础 | 脑结构静态数据 | 低；传统医学影像级别 | T1/T2 结构 MRI、CT |
| **L2** | 非侵入功能（群体） | 群体水平非侵入功能数据 | 中低；个体身份可模糊化 | 群体 fMRI 对比图、平均 EEG 功率谱 |
| **L3** | 个体非侵入功能 | 个体水平非侵入神经信号 | 中高；个体可识别、情绪可推断 | 个体 EEG 时间序列、个体 fMRI BOLD |
| **L4** | 侵入性神经信号 | 高精度侵入性记录 | 高；可直接关联到个体神经活动 | iEEG、ECoG、Neuropixels 单单元记录、LFP |
| **L5** | 解码神经内容 | 已解码的神经信息 | 极高；直接暴露精神内容 | 解码的意图、情绪、认知状态、内心言语 |

### 5.3 设备神经访问级别 (NeuralAccessLevel)

| 级别 | 描述 | 设备示例 |
|------|------|----------|
| 1 | 间接/远程 | 消费级 EEG 头带、智能手表 |
| 2 | 表面非侵入 | 医疗级 EEG 帽、fNIRS |
| 3 | 近侵入 | 颅内 EEG (sEEG)、ECoG |
| 4 | 侵入记录 | 皮层内电极阵列、Neuropixels |
| 5 | 双向读写 | 闭环神经假体、深部脑刺激 + 记录 |

### 5.4 安全控制矩阵

| 控制项 | L1 | L2 | L3 | L4 | L5 |
|--------|-----|-----|-----|-----|-----|
| 静态加密 | 可选 | 建议 | 必须 | 必须 | 必须 |
| 传输加密 | 可选 | 建议 | 必须 | 必须 | 必须 |
| 假名化 | 建议 | 建议 | 必须 | 必须 | 必须 |
| 差分隐私 | 可选 | 建议 | 建议 | 必须 | 必须 |
| 访问日志 | 可选 | 建议 | 必须 | 必须 | 必须（实时） |
| 审计频率 | 年度 | 半年 | 季度 | 月度 | 实时 |
| 存储隔离 | 共享 | 共享 | 逻辑隔离 | 物理隔离 | 物理隔离 + 加密 |
| 同意类型 | 简单 | 知情 | 明确知情 | 明确知情 | 明确知情 + 持续 |

---

## 6. 目录结构扩展

NDOM 在 BIDS 基础上增加安全目录。

```
dataset/
├── dataset_description.json          # BIDS 标准
├── dataset_security.json             # NDOM 新增：全局安全策略
├── dataset_consent.json              # NDOM 新增：全局同意框架
├── participants.tsv
├── participants.json
├── README
├── CHANGES
├── code/
├── stimuli/
├── derivatives/                      # 衍生数据（BIDS 标准）
│   └── ndom-security/                # NDOM 安全衍生层
│       ├── audit_logs/
│       │   └── audit_log_2025.tsv
│       └── risk_assessments/
│           └── risk_assessment_2025.json
├── sub-01/
│   ├── sub-01_security.json          # NDOM 新增：受试者级安全标签
│   ├── sub-01_consent.json           # NDOM 新增：受试者级同意记录
│   ├── ses-01/
│   │   ├── ses-01_security.json      # NDOM 新增：会话级安全标签
│   │   ├── eeg/
│   │   │   ├── sub-01_ses-01_task-rest_run-01_eeg.edf
│   │   │   ├── sub-01_ses-01_task-rest_run-01_eeg.json
│   │   │   ├── sub-01_ses-01_task-rest_run-01_eeg_security.json    # NDOM 新增
│   │   │   ├── sub-01_ses-01_task-rest_run-01_eeg_consent.json     # NDOM 新增
│   │   │   ├── sub-01_ses-01_task-rest_run-01_events.tsv
│   │   │   └── sub-01_ses-01_task-rest_run-01_channels.tsv
│   │   └── anat/
│   │       ├── sub-01_ses-01_T1w.nii.gz
│   │       ├── sub-01_ses-01_T1w.json
│   │       └── sub-01_ses-01_T1w_security.json    # NDOM 新增
│   └── ses-02/
│       └── ...
└── sub-02/
    └── ...
```

**继承原则（BIDS Inheritance Principle）**：低层级的 `_security.json` 覆盖高层级的定义。即：
- 文件级 > 会话级 > 受试者级 > 数据集级

---

## 7. JSON Schema 定义（摘要）

### 7.1 NDOMFile Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "NDOMFile",
  "type": "object",
  "required": ["identifier", "session_start_time", "session_description"],
  "properties": {
    "identifier": {"type": "string"},
    "session_start_time": {"type": "string", "format": "date-time"},
    "session_description": {"type": "string"},
    "security_policy": {"$ref": "#/definitions/SecurityPolicy"},
    "consent_record": {"$ref": "#/definitions/ConsentRecord"},
    "neural_data_class": {"$ref": "#/definitions/NeuralDataClass"}
  }
}
```

（完整 Schema 见 `ndom-schema.json`）

---

## 8. Python 实现

见 `ndom/` 目录下的参考实现。核心设计原则：
- 与 PyNWB 的 `NWBFile` 语义兼容，可双向转换
- 安全对象可序列化为 JSON sidecars
- 支持 BIDS 目录验证与生成
- 支持安全策略验证（Policy Enforcement）

---

## 9. 参考标准与文献

1. **BIDS** — Gorgolewski, K.J. et al. (2016). The brain imaging data structure. *Scientific Data*.
2. **PyNWB / NWB** — Ruebel, O. et al. (2022). The Neurodata Without Borders ecosystem for neurophysiological data science. *eLife*.
3. **Ienca et al.** (2021). Towards a Governance Framework for Brain Data. *arXiv:2109.11960*.
4. **GDPR** — Regulation (EU) 2016/679.
5. **CCPA / CPA** — California Consumer Privacy Act; Colorado Privacy Act (神经数据列为敏感数据).
6. **Schwarz et al.** (2019). Identification of Anonymous MRI Research Participants with Face-Recognition Software. *NEJM*.

---

*NDOM 是一个开放草案，欢迎神经科学、数据安全、伦理治理社区共同完善。*
