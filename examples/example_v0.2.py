"""NDOM v0.2 使用示例 — 完整工作流

演示从 Raw EEG → PSD Feature → Decoded Intent 的完整数据血缘链，
每个 DataObject 都有独立的安全策略、风险画像、指纹和血缘。
"""

from datetime import datetime
from ndom import (
    NDOM, Asset, Dataset, DataObject,
    SecurityPolicy, ConsentRecord, NeuralDataClass, RiskTags, RiskProfile, ThreatProfile,
    Fingerprint, Provenance, ProcessingStep, AccessMetadata,
    PrivacyLevel, NeuralDataSensitivity, ConsentType, ConsentScope, DataObjectType,
    DataRetentionPolicy, DataRetentionPolicyType, AccessRule, IdentifiabilityRisk,
    NeuralModality, DecodingStatus, SpatialResolution, TemporalResolution,
    NeuralDataType,
    NDOMSubject, NDOMDevice, NDOMDeviceModel,
    BIDSMapper, NDOMSerializer,
)


def create_example_v02():
    """创建 NDOM v0.2 示例：iEEG 记忆任务，包含完整数据血缘链。"""

    print("=" * 60)
    print("NDOM v0.2 Example — iEEG Memory Task with Full Provenance")
    print("=" * 60)

    # ============================================================
    # 1. 创建 Asset（数据资产）
    # ============================================================
    asset = Asset(
        asset_id="asset-ieeg-memory-2025",
        asset_name="iEEG Verbal Memory Task Dataset",
        owner="Dr. Zhang Wei",
        department="Beijing Brain Institute / Cognitive Neuroscience Lab",
        location="Beijing, CN-BJDC-01",
        storage_system="S3 (cn-north-1)",
        repository="DANDI:000001",
        backup_location="S3 Glacier (cn-north-1)",
        business_system="ClinicalTrialSystem-CT-2025-004",
        asset_type="neural_dataset",
        value_assessment="high",
        compliance_scope=["GDPR", "HIPAA", "China-Personal-Information-Protection-Law"],
    )
    print("[1] Asset created:", asset.asset_name)

    # ============================================================
    # 2. 创建 Dataset（数据集）
    # ============================================================
    dataset = Dataset(
        dataset_id="ds-ieeg-memory-001",
        description="Intracranial EEG recording during verbal memory task",
    )

    # 设置默认安全策略（L3：个体非侵入功能）
    default_policy = SecurityPolicy(
        policy_id="sp-default-001",
        privacy_level=PrivacyLevel.RESTRICTED,
        data_retention_policy=DataRetentionPolicy(
            policy_type=DataRetentionPolicyType.PROJECT_DURATION,
            retention_end_date=datetime(2027, 12, 31),
            destruction_method="cryptographic_erasure",
        ),
        encryption_at_rest=True,
        encryption_in_transit=True,
        pseudonymization=True,
        access_control_list=[
            AccessRule(role="principal_investigator", permission="admin"),
            AccessRule(role="researcher", permission="read", conditions=["DUA_signed"]),
        ],
        data_controller="Beijing Brain Institute",
        data_protection_officer="dpo@bbinstitute.cn",
        legal_basis="research_ethics",
    )
    dataset.default_security_policy = default_policy

    # 设置默认同意记录
    default_consent = ConsentRecord(
        consent_id="consent-2025-001",
        consent_type=ConsentType.EXPLICIT_INFORMED,
        consent_scope=[ConsentScope.PRIMARY_RESEARCH, ConsentScope.SECONDARY_ANALYSIS],
        consent_withdrawable=True,
        data_use_limitations=["non-commercial", "academic-only", "no-military-use"],
        recontact_allowed=False,
        recorded_by="Dr. Zhang Wei",
        recorded_at=datetime(2025, 6, 10, 10, 0, 0),
    )
    dataset.default_consent_record = default_consent

    # 受试者
    subject = NDOMSubject(
        subject_id="sub-01",
        age="P25Y",
        sex="M",
        species="Homo sapiens",
        pseudonym_id="pseudo-abc-123",
        vulnerability_tags=["cognitive_impairment", "medical_patient"],
    )
    dataset.subject = subject

    # 设备
    device_model = NDOMDeviceModel(
        name="Nihon Kohden EEG-1200",
        manufacturer="Nihon Kohden",
        model_number="EEG-1200A",
        device_class="semi_invasive",
        neural_access_level=3,
        regulatory_status="medical",
    )
    device = NDOMDevice(
        name="ieeg-amplifier-01",
        description="iEEG recording amplifier",
        serial_number="NK-2024-8847",
        model=device_model,
        security_certification="CE-MDR",
        firmware_version="v2.1.3",
    )
    dataset.subject = subject
    dataset.device = device  # v0.2 简化：单设备直接赋值

    print("[2] Dataset created with default security policy (L3)")

    # ============================================================
    # 3. 创建 DataObject 1: Raw iEEG
    # ============================================================
    raw_ieeg = DataObject(
        object_id="obj-raw-ieeg-001",
        object_type=DataObjectType.RAW,
        name="raw_ieeg_lh_grid",
        description="Raw iEEG signal from left hippocampal depth electrode",
        data_format="edf",
        size_bytes=2147483648,  # 2GB
        data_reference="s3://bucket/ds-ieeg-memory-001/raw/sub-01_ses-01_ieeg.edf",
    )

    # 分类：L3（个体非侵入功能）
    raw_class = NeuralDataClass(
        classification_id="ndc-raw-001",
        sensitivity_level=NeuralDataSensitivity.L3,
        data_type=NeuralDataType.FUNCTIONAL_INVASIVE,
        modality=NeuralModality.iEEG,
        spatial_resolution=SpatialResolution.REGIONAL,
        temporal_resolution=TemporalResolution.FAST,
        decoding_status=DecodingStatus.RAW,
        identifiability_risk=IdentifiabilityRisk.HIGH,
        mental_content_disclosure_risk=IdentifiabilityRisk.MEDIUM,
    )
    raw_ieeg.classification = raw_class

    # 风险标签
    raw_ieeg.risk_tags = RiskTags(
        tags=["reidentification", "cross_domain_inference", "identity_inference"],
        risk_assessment_date=datetime(2025, 6, 1),
        assessed_by="Ethics Committee BBI-EC-2025-004",
    )

    # 风险画像
    raw_ieeg.risk_profile = RiskProfile(
        profile_id="rp-raw-001",
        identity_risk=7.0,
        medical_risk=6.0,
        cognitive_risk=5.0,
        emotional_risk=3.0,
        linguistic_risk=2.0,
        memory_risk=4.0,
        reconstruction_risk=6.0,
    )

    # 指纹
    raw_ieeg.fingerprint = Fingerprint(
        fingerprint_id="fp-raw-001",
        sha256="a1b2c3d4e5f6...",
        channel_signature="32ch_2048Hz_lh_hippocampus",
        signal_signature="mean=0.5uV_std=12.3uV_psd_alpha_dominant",
    )

    # 血缘（根对象，无父对象）
    raw_ieeg.provenance = Provenance(
        provenance_id="prov-raw-001",
        source_file="sub-01_ses-01_ieeg.edf",
        source_dataset="ds-ieeg-memory-001",
    )

    # 访问元数据
    raw_ieeg.access_metadata = AccessMetadata(
        object_id=raw_ieeg.object_id,
        sharing_status="private",
    )

    dataset.add_object(raw_ieeg)
    print("[3] DataObject 1 (Raw iEEG) created — L3, risk_score:", raw_ieeg.risk_profile.overall_score)

    # ============================================================
    # 4. 创建 DataObject 2: PSD Feature
    # ============================================================
    psd = DataObject(
        object_id="obj-psd-001",
        object_type=DataObjectType.FEATURE,
        name="psd_alpha_band",
        description="Power spectral density in alpha band (8-12 Hz)",
        data_format="npy",
        size_bytes=10485760,  # 10MB
        parent_object=raw_ieeg.object_id,
        data_reference="s3://bucket/ds-ieeg-memory-001/derived/sub-01_ses-01_psd_alpha.npy",
    )

    psd.classification = NeuralDataClass(
        classification_id="ndc-psd-001",
        sensitivity_level=NeuralDataSensitivity.L3,
        data_type=NeuralDataType.FUNCTIONAL_INVASIVE,
        modality=NeuralModality.iEEG,
        decoding_status=DecodingStatus.FEATURE_EXTRACTED,
        identifiability_risk=IdentifiabilityRisk.MEDIUM,
        mental_content_disclosure_risk=IdentifiabilityRisk.LOW,
    )

    psd.risk_tags = RiskTags(
        tags=["reidentification", "cross_domain_inference"],
    )

    psd.risk_profile = RiskProfile(
        profile_id="rp-psd-001",
        identity_risk=5.0,
        medical_risk=4.0,
        cognitive_risk=4.0,
        emotional_risk=2.0,
        linguistic_risk=1.0,
        memory_risk=3.0,
        reconstruction_risk=4.0,
    )

    # 血缘：从 Raw EEG 生成
    psd_provenance = Provenance(
        provenance_id="prov-psd-001",
        parent_object=raw_ieeg.object_id,
        generated_by="MNE-Python",
        generated_by_version="1.6.0",
    )
    psd_step = ProcessingStep(
        step_id="step-psd-001",
        step_name="power_spectral_density",
        step_type="feature_extraction",
        input_objects=[raw_ieeg.object_id],
        output_object=psd.object_id,
        parameters={"fmin": 8, "fmax": 12, "method": "welch"},
        tool_name="MNE-Python",
        tool_version="1.6.0",
    )
    psd_provenance.add_step(psd_step)
    psd.provenance = psd_provenance

    psd.fingerprint = Fingerprint(
        fingerprint_id="fp-psd-001",
        sha256="b2c3d4e5f6g7...",
        schema_hash="npy_2d_float32_32ch_100freqs",
    )

    raw_ieeg.add_child(psd.object_id)
    dataset.add_object(psd)
    print("[4] DataObject 2 (PSD Feature) created — parent:", raw_ieeg.object_id)

    # ============================================================
    # 5. 创建 DataObject 3: Embedding
    # ============================================================
    embedding = DataObject(
        object_id="obj-embedding-001",
        object_type=DataObjectType.EMBEDDING,
        name="neural_embedding_v2",
        description="Neural embedding vector from encoder model",
        data_format="npy",
        size_bytes=5242880,  # 5MB
        parent_object=psd.object_id,
        data_reference="s3://bucket/ds-ieeg-memory-001/derived/sub-01_ses-01_embedding.npy",
    )

    embedding.classification = NeuralDataClass(
        classification_id="ndc-emb-001",
        sensitivity_level=NeuralDataSensitivity.L4,
        data_type=NeuralDataType.DECODED,
        modality=NeuralModality.iEEG,
        decoding_status=DecodingStatus.FEATURE_EXTRACTED,
        identifiability_risk=IdentifiabilityRisk.HIGH,
        mental_content_disclosure_risk=IdentifiabilityRisk.MEDIUM,
    )

    embedding.risk_tags = RiskTags(
        tags=["reidentification", "mental_decoding", "identity_inference", "intent_inference"],
    )

    embedding.risk_profile = RiskProfile(
        profile_id="rp-emb-001",
        identity_risk=8.0,
        medical_risk=5.0,
        cognitive_risk=7.0,
        emotional_risk=6.0,
        linguistic_risk=4.0,
        memory_risk=6.0,
        reconstruction_risk=7.0,
    )

    emb_provenance = Provenance(
        provenance_id="prov-emb-001",
        parent_object=psd.object_id,
        generated_by="NeuralEncoder",
        model_name="Encoder-v2.1",
        model_version="v2.1.0",
    )
    emb_step = ProcessingStep(
        step_id="step-emb-001",
        step_name="neural_encoding",
        step_type="feature_extraction",
        input_objects=[psd.object_id],
        output_object=embedding.object_id,
        parameters={"latent_dim": 256, "encoder_type": "CNN-LSTM"},
        tool_name="NeuralEncoder",
        tool_version="v2.1.0",
    )
    emb_provenance.add_step(emb_step)
    embedding.provenance = emb_provenance

    embedding.fingerprint = Fingerprint(
        fingerprint_id="fp-emb-001",
        sha256="c3d4e5f6g7h8...",
        schema_hash="npy_2d_float32_256dim",
    )

    # L4 需要更强的安全控制
    embedding.security_policy = SecurityPolicy(
        policy_id="sp-emb-001",
        privacy_level=PrivacyLevel.RESTRICTED,
        data_retention_policy=DataRetentionPolicy(
            policy_type=DataRetentionPolicyType.PROJECT_DURATION,
        ),
        encryption_at_rest=True,
        encryption_in_transit=True,
        pseudonymization=True,
        differential_privacy_epsilon=1.0,
        access_control_list=[
            AccessRule(role="principal_investigator", permission="admin"),
            AccessRule(role="ml_engineer", permission="read", conditions=["model_training_only"]),
        ],
    )

    psd.add_child(embedding.object_id)
    dataset.add_object(embedding)
    print("[5] DataObject 3 (Embedding) created — L4, risk_score:", embedding.risk_profile.overall_score)

    # ============================================================
    # 6. 创建 DataObject 4: Decoded Intent (L5) ★
    # ============================================================
    decoded = DataObject(
        object_id="obj-decoded-001",
        object_type=DataObjectType.DECODED,
        name="decoded_intent",
        description="Decoded user intent from neural embedding",
        data_format="json",
        size_bytes=10240,
        parent_object=embedding.object_id,
        data_reference="s3://bucket/ds-ieeg-memory-001/derived/sub-01_ses-01_decoded_intent.json",
    )

    decoded.classification = NeuralDataClass(
        classification_id="ndc-decoded-001",
        sensitivity_level=NeuralDataSensitivity.L5,
        data_type=NeuralDataType.DECODED,
        modality=NeuralModality.BCI,
        decoding_status=DecodingStatus.DECODED_INTENT,
        identifiability_risk=IdentifiabilityRisk.CERTAIN,
        mental_content_disclosure_risk=IdentifiabilityRisk.HIGH,
    )

    decoded.risk_tags = RiskTags(
        tags=[
            "reidentification", "mental_decoding", "identity_inference",
            "intent_inference", "language_inference", "cognitive_manipulation",
            "neurodiscrimination", "dual_use",
        ],
        inference_confidence=0.92,
    )

    decoded.risk_profile = RiskProfile(
        profile_id="rp-decoded-001",
        identity_risk=9.0,
        medical_risk=7.0,
        cognitive_risk=9.0,
        emotional_risk=8.0,
        linguistic_risk=8.0,
        memory_risk=7.0,
        reconstruction_risk=9.0,
        mitigation_recommendations=[
            "Apply differential privacy before sharing",
            "Use federated learning for model training",
            "Implement real-time access monitoring",
            "Consider on-device processing only",
        ],
    )

    decoded_provenance = Provenance(
        provenance_id="prov-decoded-001",
        parent_object=embedding.object_id,
        generated_by="IntentDecoder",
        model_name="IntentDecoder-v3.0",
        model_version="v3.0.1",
        model_checkpoint="checkpoint-epoch-250",
    )
    decoded_step = ProcessingStep(
        step_id="step-decoded-001",
        step_name="intent_decoding",
        step_type="decoding",
        input_objects=[embedding.object_id],
        output_object=decoded.object_id,
        parameters={"decoder_type": "Transformer", "confidence_threshold": 0.85},
        tool_name="IntentDecoder",
        tool_version="v3.0.1",
    )
    decoded_provenance.add_step(decoded_step)
    decoded.provenance = decoded_provenance

    decoded.fingerprint = Fingerprint(
        fingerprint_id="fp-decoded-001",
        sha256="d4e5f6g7h8i9...",
        schema_hash="json_1d_string_intent_labels",
    )

    # L5 最高级别安全控制
    decoded.security_policy = SecurityPolicy(
        policy_id="sp-decoded-001",
        privacy_level=PrivacyLevel.NEURAL_SECRET,
        data_retention_policy=DataRetentionPolicy(
            policy_type=DataRetentionPolicyType.SESSION_ONLY,
        ),
        encryption_at_rest=True,
        encryption_in_transit=True,
        pseudonymization=True,
        differential_privacy_epsilon=0.1,
        data_minimization=True,
        purpose_limitation=["primary_research_only", "no_commercial_use"],
        access_control_list=[
            AccessRule(role="principal_investigator", permission="admin"),
            AccessRule(role="decoder_reviewer", permission="read", conditions=["two_eyes_review"]),
        ],
    )

    decoded.threat_profile = ThreatProfile(
        threat_profile_id="tp-decoded-001",
        attack_surface=["export", "inference_api", "model_training", "cloud_storage"],
        threat_actors=["external_hacker", "insider_malicious", "nation_state", "competitor"],
        attack_scenarios=[
            "mental_decoding_exfiltration",
            "model_inversion_attack",
            "adversarial_decoding",
            "cross_dataset_linkage",
        ],
        mitigations=[
            "encryption_at_rest",
            "differential_privacy_epsilon_0.1",
            "two_eyes_review",
            "session_only_retention",
            "real_time_access_monitoring",
        ],
        neuroattck_mapping="T0012.003",
        neuroattck_techniques=["T0012", "T0015", "T0021"],
        notes="Highest threat level: decoded neural intent is the most sensitive attack surface",
    )

    embedding.add_child(decoded.object_id)
    dataset.add_object(decoded)
    print("[6] DataObject 4 (Decoded Intent) created — L5, risk_score:", decoded.risk_profile.overall_score, "CRITICAL")
    print("    Threat level:", decoded.threat_profile.risk_level.value, "| NeuroATT&CK:", decoded.threat_profile.neuroattck_mapping)

    # ============================================================
    # 7. 构建 NDOM 顶层
    # ============================================================
    ndom = NDOM(
        version="0.2.0",
        asset=asset,
        dataset=dataset,
        compliance_framework=["GDPR", "HIPAA", "China-Personal-Information-Protection-Law"],
    )

    print("[7] NDOM v0.2 top-level created")

    # ============================================================
    # 8. 验证
    # ============================================================
    print()
    print("=" * 60)
    print("Validation")
    print("=" * 60)
    validation = ndom.validate()
    print(f"Valid: {validation['valid']}")
    print(f"Errors: {validation['errors']}")
    print(f"Warnings: {validation['warnings']}")
    print(f"Recommendations: {validation['recommendations']}")

    # ============================================================
    # 9. 风险汇总
    # ============================================================
    print()
    print("=" * 60)
    print("Risk Summary")
    print("=" * 60)
    risk_summary = ndom.get_risk_summary()
    print(json.dumps(risk_summary, indent=2, ensure_ascii=False))

    # ============================================================
    # 10. 血缘链展示
    # ============================================================
    print()
    print("=" * 60)
    print("Lineage Chain (Decoded Intent)")
    print("=" * 60)
    lineage = dataset.get_lineage(decoded.object_id)
    for obj_id in lineage:
        obj = dataset.get_object_by_id(obj_id)
        if obj:
            print(f"  {obj.object_type.value}: {obj.name} ({obj_id})")

    # ============================================================
    # 11. 高亮安全策略差异
    # ============================================================
    print()
    print("=" * 60)
    print("Security Policy Comparison (per DataObject)")
    print("=" * 60)
    for obj in dataset.objects:
        policy = obj.security_policy or dataset.default_security_policy
        print(f"  {obj.name:20s} | {obj.object_type.value:10s} | {obj.classification.sensitivity_level.value if obj.classification else 'N/A':3s} | {policy.privacy_level.value if policy else 'N/A'}")

    # ============================================================
    # 12. 序列化
    # ============================================================
    print()
    print("=" * 60)
    print("Serialization")
    print("=" * 60)
    json_str = NDOMSerializer.to_json(ndom, filepath="example_ndom_v02.json")
    print(f"Serialized to example_ndom_v02.json ({len(json_str)} chars)")

    # ============================================================
    # 13. BIDS + NDOM 扩展导出
    # ============================================================
    print()
    print("=" * 60)
    print("BIDS + NDOM v0.2 Export")
    print("=" * 60)
    mapper = BIDSMapper(dataset_root="./example_bids_v02", dataset_name="iEEG Memory Task v0.2")
    paths = mapper.write_bids_layout(
        ndom=ndom,
        subject_id="01",
        session_id="01",
        modality="ieeg",
    )
    for key, path in paths.items():
        print(f"  {key}: {path}")

    print()
    print("=" * 60)
    print("NDOM v0.2 Example Complete")
    print("=" * 60)
    return ndom


import json

if __name__ == "__main__":
    create_example_v02()
