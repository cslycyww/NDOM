"""NDOM 使用示例 — 完整工作流

演示如何创建一个 NDOM 数据集对象，设置安全策略，并导出为 BIDS + NDOM 扩展格式。
"""

from datetime import datetime, timedelta
from ndom.core import (
    NDOMFile, NDOMSubject, NDOMDevice, NDOMDeviceModel,
    NDOMElectrodeGroup, NDOMElectrode,
    NDOMAcquisition, NDOMProcessingModule,
    NDOMTimeSeries, NDOMTimeIntervals,
)
from ndom.security import (
    SecurityPolicy, ConsentRecord, NeuralDataClass, RiskTags,
    PrivacyLevel, NeuralDataSensitivity, ConsentType,
    DataRetentionPolicy, DataRetentionPolicyType, AccessRule,
)
from ndom.metadata import BIDSMapper
from ndom.io import NDOMSerializer


def create_example_ndom_dataset():
    """创建一个示例 NDOM 数据集（高精度侵入性 EEG，L4 级别）。"""

    # 1. 创建顶层文件
    ndom = NDOMFile(
        session_description="Intracranial EEG recording during verbal memory task",
        identifier="ndom-ieeg-001",
        session_start_time=datetime(2025, 6, 15, 9, 0, 0),
        experimenter="Dr. Zhang Wei",
        institution="Beijing Brain Institute",
        experiment_description="Verbal memory encoding and retrieval task",
        keywords=["iEEG", "memory", "epilepsy", "language"],
    )

    # 2. 创建受试者
    subject = NDOMSubject(
        subject_id="sub-01",
        age="P25Y",
        sex="M",
        species="Homo sapiens",
        description="Patient with drug-resistant epilepsy, left temporal lobe",
        pseudonym_id="pseudo-abc-123",
        vulnerability_tags=["cognitive_impairment", "medical_patient"],
    )
    ndom.add_subject(subject)

    # 3. 创建设备
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
    ndom.add_device(device)

    # 4. 创建电极组
    eg = NDOMElectrodeGroup(
        name="LH-grid",
        description="Left hippocampal depth electrode grid",
        location="left hippocampus",
        device=device,
    )
    ndom.add_electrode_group(eg)

    # 5. 创建电极
    electrode = NDOMElectrode(
        x=10.5, y=20.3, z=-5.2,
        location="left hippocampus CA1",
        filtering="bandpass 0.1-300 Hz",
        group=eg,
        id=1,
        reference="bipolar adjacent",
    )
    ndom.add_electrode(electrode)

    # 6. 创建采集时间序列
    ts = NDOMTimeSeries(
        name="ieeg_LH-grid",
        unit="microvolts",
        rate=2048.0,
        description="iEEG signal from left hippocampal grid",
    )
    acq = NDOMAcquisition(name="ieeg_acquisition")
    acq.add_timeseries(ts)
    ndom.add_acquisition(acq)

    # 7. 创建处理模块（例如频谱分析）
    proc = NDOMProcessingModule(
        name="spectral_analysis",
        description="Power spectral density analysis",
    )
    ndom.add_processing(proc)

    # 8. 创建安全策略（L4 级别：侵入性数据，高风险）
    retention = DataRetentionPolicy(
        policy_type=DataRetentionPolicyType.PROJECT_DURATION,
        retention_end_date=datetime(2027, 12, 31),
        destruction_method="cryptographic_erasure",
    )
    policy = SecurityPolicy(
        policy_id="sp-ieeg-001",
        privacy_level=PrivacyLevel.CONFIDENTIAL,
        data_retention_policy=retention,
        encryption_at_rest=True,
        encryption_in_transit=True,
        pseudonymization=True,
        access_control_list=[
            AccessRule(role="principal_investigator", permission="admin"),
            AccessRule(role="researcher", permission="read", conditions=["DUA_signed"]),
            AccessRule(role="data_curator", permission="read"),
        ],
        data_controller="Beijing Brain Institute",
        data_protection_officer="dpo@bbinstitute.cn",
        legal_basis="research_ethics",
        cross_border_transfer=False,
    )
    ndom.set_security_policy(policy)

    # 9. 创建同意记录
    consent = ConsentRecord(
        consent_id="consent-2025-001-sub01",
        consent_type=ConsentType.EXPLICIT_INFORMED,
        consent_scope=["primary_research", "secondary_analysis"],
        consent_withdrawable=True,
        data_use_limitations=["non-commercial", "academic-only", "no-military-use"],
        recontact_allowed=False,
        consent_document_version="v3.1",
        recorded_by="Dr. Zhang Wei",
        recorded_at=datetime(2025, 6, 10, 10, 0, 0),
    )
    ndom.set_consent_record(consent)

    # 10. 创建神经数据分类
    ndc = NeuralDataClass(
        classification_id="ndc-ieeg-001",
        sensitivity_level=NeuralDataSensitivity.L4,
        data_type="functional_invasive",
        modality="iEEG",
        spatial_resolution="regional",
        temporal_resolution="fast",
        decoding_status="raw",
        identifiability_risk="high",
        mental_content_disclosure_risk="medium",
    )
    ndom.set_neural_data_class(ndc)

    # 11. 设置风险标签
    risks = RiskTags(
        tags=["reidentification", "mental_decoding", "cross_domain_inference"],
        risk_assessment_date=datetime(2025, 6, 1),
        assessed_by="Ethics Committee BBI-EC-2025-004",
        reassessment_interval_days=180,
        custom_risk_notes="Patient data from clinical epilepsy monitoring. Raw signals may be re-identified via cross-hospital matching.",
    )
    ndom.set_risk_tags(risks)

    # 12. 验证安全策略
    print("=" * 60)
    print("NDOM Security Validation")
    print("=" * 60)
    validation = ndom.validate_security()
    print(f"Valid: {validation['valid']}")
    print(f"Violations: {validation['violations']}")
    print(f"Recommendations: {validation['recommendations']}")
    print(f"Warnings: {validation['warnings']}")
    print()

    # 13. 验证安全控制矩阵
    print("Security Control Matrix Check:")
    violations = policy.validate_controls(NeuralDataSensitivity.L4)
    if violations:
        print(f"  ⚠ Policy violations for L4: {violations}")
    else:
        print("  ✓ All required controls for L4 are satisfied")
    print()

    # 14. 序列化为 JSON
    print("=" * 60)
    print("Serialization")
    print("=" * 60)
    json_str = NDOMSerializer.to_json(ndom, filepath="example_ndom.json")
    print(f"Serialized to example_ndom.json ({len(json_str)} chars)")
    print()

    # 15. 导出 BIDS + NDOM 扩展目录
    print("=" * 60)
    print("BIDS + NDOM Export")
    print("=" * 60)
    mapper = BIDSMapper(dataset_root="./example_bids_dataset", dataset_name="iEEG Memory Task")
    paths = mapper.write_bids_layout(
        ndom_file=ndom,
        subject_id="01",
        session_id="01",
        modality="ieeg",
        task_name="verbalmemory",
        run_id=1,
    )
    for key, path in paths.items():
        print(f"  {key}: {path}")
    print()

    # 16. 显示审计日志
    print("=" * 60)
    print("Audit Log")
    print("=" * 60)
    for entry in ndom.audit_log.log_entries:
        print(f"  [{entry.timestamp}] {entry.action.value} by {entry.actor_id} on {entry.target_object_type}")
    print()

    print("✓ Example dataset created successfully.")
    return ndom


if __name__ == "__main__":
    create_example_ndom_dataset()
