# NDOM — Neural Data Object Model

> **Neural Data Security Object Model for DSPM (Data Security Posture Management)**
>
> v0.2.0 | 从"神经科研数据模型"升级为"神经数据安全对象模型"

---

## 为什么需要 NDOM？

神经数据（EEG、fMRI、iEEG、BCI 等）是最高等级的个人数据。现有的数据模型（如 NWB、BIDS）专注于**科学可重复性**，但缺乏**安全与隐私的原生设计**。

NDOM v0.2 将安全内建于数据本身：每个数据对象（DataObject）独立携带安全策略、风险画像、数据指纹、血缘和审计日志。这是 DSPM 扫描器、数据安全平台、神经伦理治理系统的底层数据模型。

---

## 核心概念

```
NDOM
├── Asset（数据资产）— owner, department, storage_system, compliance_scope
├── Dataset（数据集）— 容器，默认安全策略，风险汇总
│   └── DataObject（原子对象）— 核心单元，独立携带：
│       ├── SecurityPolicy（安全策略）— 对象级，可继承
│       ├── RiskProfile（风险画像）— Neural Privacy Score（NPS）基础
│       ├── ThreatProfile（威胁画像）— NeuroATT&CK 映射
│       ├── Classification（神经数据分类）— L1-L5 敏感度
│       ├── RiskTags（风险标签）— 推断风险（identity_inference, intent_inference...）
│       ├── Fingerprint（数据指纹）— sha256, 感知哈希, 信号签名
│       ├── Provenance（数据血缘）— Raw → PSD → Embedding → Decoded 完整链路
│       ├── AccessMetadata（访问元数据）— 访问/导出/下载统计 + 异常标记
│       └── AuditLog（审计日志）— 对象级完整审计
├── BIDSMapper（BIDS + NDOM 扩展映射）
└── NDOMSerializer（JSON 序列化 + 侧车导出）
```

### DataObject 类型

| 类型 | 说明 | 典型敏感度 |
|------|------|-----------|
| `raw` | 原始采集信号 | L3 |
| `processed` | 预处理数据（滤波、降采样） | L3 |
| `feature` | 特征提取（PSD、功率谱） | L3 |
| `embedding` | 嵌入向量 | L4 |
| `decoded` | 解码输出（意图、情绪、语言） | L5 |
| `annotation` | 人工标注 | L2 |
| `model` | 模型/解码器 | L4 |
| `aggregated` | 聚合数据 | L2 |
| `synthetic` | 合成数据 | L1 |

---

## 快速开始

```python
from ndom import (
    NDOM, Asset, Dataset, DataObject,
    SecurityPolicy, RiskProfile, ThreatProfile, Fingerprint, Provenance,
    PrivacyLevel, NeuralDataSensitivity, DataObjectType, RiskLevel,
)

# 1. 创建资产
asset = Asset(
    asset_id="a1", asset_name="iEEG Dataset",
    owner="Dr. Zhang", department="Neuro Lab",
    location="Beijing", storage_system="S3",
)

# 2. 创建数据集
ds = Dataset(dataset_id="ds1", description="Memory Task")

# 3. 创建数据对象（每个都是独立安全单元）
obj = DataObject(
    object_id="obj-1",
    object_type=DataObjectType.RAW,
    name="raw_eeg",
)

# 4. 设置分类
obj.classification = NeuralDataClass(
    classification_id="c1",
    sensitivity_level=NeuralDataSensitivity.L3,
)

# 5. 设置风险画像（NPS 基础）
obj.risk_profile = RiskProfile(
    profile_id="rp-1",
    identity_risk=7.0, medical_risk=6.0,
    cognitive_risk=5.0, emotional_risk=3.0,
    memory_risk=4.0, reconstruction_risk=6.0,
)
# 自动计算 overall_score 和 risk_level
print(obj.risk_profile.overall_score)  # 42.47
print(obj.risk_profile.risk_level)      # RiskLevel.MEDIUM

# 6. 设置威胁画像（NeuroATT&CK）
obj.threat_profile = ThreatProfile(
    threat_profile_id="tp-1",
    attack_surface=["export", "cloud_storage"],
    threat_actors=["external_hacker", "insider_malicious"],
    attack_scenarios=["mental_decoding_exfiltration"],
    neuroattck_mapping="T0012.003",
)

# 7. 设置指纹
obj.fingerprint = Fingerprint(
    fingerprint_id="fp-1",
    sha256="a1b2c3...",
    channel_signature="32ch_2048Hz",
)

# 8. 设置血缘
obj.provenance = Provenance(
    provenance_id="p1", source_file="raw.edf",
)

# 9. 设置安全策略
obj.security_policy = SecurityPolicy(
    policy_id="sp-1",
    privacy_level=PrivacyLevel.RESTRICTED,
    encryption_at_rest=True,
    encryption_in_transit=True,
    pseudonymization=True,
)

# 10. 验证
result = obj.validate()
print(result["valid"])      # True
print(result["warnings"])   # []

# 11. 加入数据集
nds.add_object(obj)

# 12. 构建 NDOM
ndom = NDOM(asset=asset, dataset=ds)
ndom.validate()
```

### 完整工作流示例

```bash
python examples/example_v0.2.py
```

演示从 **Raw iEEG → PSD Feature → Embedding → Decoded Intent** 的完整数据血缘链，每个对象独立安全策略和威胁画像。

---

## 安装

NDOM 纯 Python 实现，无外部依赖，支持 Python 3.12+。

```bash
git clone https://github.com/<your-org>/NDOM.git
cd NDOM
python -m pytest ndom/tests/test_v0.2.py -v
```

---

## 测试

```bash
python -m ndom.tests.test_v0.2
```

**25/25 测试通过**，覆盖：
- 枚举标准化（Enums）
- 资产（Asset）
- 数据指纹（Fingerprint）
- 数据血缘（Provenance / ProcessingStep）
- 访问元数据（AccessMetadata）
- 风险画像（RiskProfile / Neural Privacy Score）
- 风险标签（RiskTags / 推断风险）
- 数据对象（DataObject / 安全策略继承）
- 数据集（Dataset / 风险汇总 / 血缘链）
- NDOM 顶层验证
- BIDS + NDOM 扩展映射
- JSON 序列化
- 安全策略控制矩阵（L1-L5）
- 同意撤回
- 威胁画像（ThreatProfile / NeuroATT&CK）

---

## 架构演进

| 版本 | 定位 | 核心变化 |
|------|------|---------|
| v0.1 | 神经科研数据模型 | NDOMFile 继承 NWBFile，安全属性外挂 |
| **v0.2** | **神经数据安全对象模型** | **SecurityPolicy 下放到 DataObject；新增 Asset、Fingerprint、Provenance、AccessMetadata、RiskProfile、ThreatProfile、DataObject 枚举、BIDS 扩展** |

---

## 文件结构

```
NDOM/
├── NDOM-Specification-v0.2.md    # v0.2 规范文档
├── examples/
│   └── example_v0.2.py           # 完整工作流示例
├── ndom/
│   ├── __init__.py               # 包入口
│   ├── enums.py                  # 完整枚举（PrivacyLevel, DataObjectType, NeuralModality...）
│   ├── asset.py                  # Asset（DSPM 资产模型）
│   ├── dataset.py                # Dataset（容器 + 风险汇总）
│   ├── dataobject.py             # DataObject（核心原子单元）
│   ├── fingerprint.py            # Fingerprint（数据指纹）
│   ├── provenance.py             # Provenance（数据血缘）
│   ├── access_metadata.py        # AccessMetadata（访问追踪）
│   ├── risk_profile.py           # RiskProfile（Neural Privacy Score）
│   ├── ndom.py                   # NDOM 顶层容器
│   ├── security/
│   │   ├── policy.py             # SecurityPolicy（安全策略）
│   │   ├── consent.py            # ConsentRecord（同意记录）
│   │   ├── classification.py     # NeuralDataClass（分类分级）
│   │   ├── risk_tags.py          # RiskTags（风险标签）
│   │   ├── audit.py              # AuditLog / AuditEntry（审计）
│   │   └── threat_profile.py     # ThreatProfile（攻击模型 / NeuroATT&CK）
│   ├── metadata/
│   │   └── bids_mapper.py        # BIDS + NDOM v0.2 扩展映射
│   ├── io/
│   │   └── serializer.py         # JSON 序列化
│   ├── core/                     # v0.1 兼容层（NWB 语义核心类）
│   └── tests/
│       └── test_v0.2.py          # 25 项测试套件
└── README.md                     # 本文档
```

---

## 安全控制矩阵（L1-L5）

| 敏感度 | 加密 | 假名化 | 差分隐私 | 审计频率 | 最小化 |
|--------|------|--------|----------|----------|--------|
| L1 | 可选 | 否 | 无需 | 无 | 否 |
| L2 | 建议 | 可选 | 无需 | 季度 | 建议 |
| L3 | 必须 | 建议 | 可选 | 月度 | 建议 |
| L4 | 必须 | 必须 | 建议 | 实时 | 必须 |
| L5 | 必须 | 必须 | 必须 | 实时 | 必须 |

---

## 风险维度（Neural Privacy Score）

| 维度 | 权重 | 说明 |
|------|------|------|
| identity_risk | 1.0 | 身份推断风险 |
| medical_risk | 1.2 | 医疗推断风险 |
| behavioral_risk | 0.8 | 行为推断风险 |
| cognitive_risk | 1.5 | 认知推断风险 |
| emotional_risk | 1.0 | 情绪推断风险 |
| linguistic_risk | 1.3 | 语言推断风险 |
| memory_risk | 1.4 | 记忆推断风险 |
| reconstruction_risk | 1.1 | 信号重建风险 |

综合评分 `overall_score = 加权平均 * 100`，等级划分：≥80 CRITICAL / ≥60 HIGH / ≥30 MEDIUM / 其余 LOW。

---

## 威胁画像（NeuroATT&CK）

| 攻击面 | 威胁参与者 | 攻击场景 |
|--------|-----------|---------|
| export | insider_malicious | mental_decoding_exfiltration |
| cloud_storage | external_hacker | model_inversion_attack |
| model_training | nation_state | membership_inference |
| inference_api | competitor | adversarial_decoding |

自动风险评分：攻击面×5 + 威胁参与者×8 + 攻击场景×15 − 缓解措施×3

---

## 路线图

- [x] v0.2 — 安全对象模型（DataObject + Asset + RiskProfile + ThreatProfile + Fingerprint + Provenance）
- [ ] v0.3 — 差分隐私集成（自动 ε 计算）
- [ ] v0.4 — 联邦学习安全契约
- [ ] v0.5 — 实时神经数据流安全网关
- [ ] v0.6 — NeuroATT&CK 完整技术映射库

---

## 许可证

Apache-2.0 License

---

## 引用

```bibtex
@software{ndom2025,
  title={NDOM: Neural Data Object Model},
  author={NDOM Contributors},
  year={2025},
  url={https://github.com/<your-org>/NDOM}
}
```

---

> **注意**：NDOM 是一个数据模型/规范项目，不是数据采集或分析工具。它不直接处理神经信号数据，而是为数据安全平台、DSPM 扫描器、合规审计系统提供标准化的数据描述框架。
