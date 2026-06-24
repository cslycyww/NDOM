"""NDOM 测试 — 验证核心对象和安全层
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from ndom.core import (
    NDOMFile, NDOMSubject, NDOMDevice, NDOMDeviceModel,
    NDOMElectrodeGroup, NDOMElectrode,
    NDOMAcquisition, NDOMProcessingModule,
    NDOMTimeSeries, NDOMTimeIntervals,
)
from ndom.security import (
    SecurityPolicy, ConsentRecord, NeuralDataClass, RiskTags, AuditLog,
    PrivacyLevel, NeuralDataSensitivity, ConsentType,
    DataRetentionPolicy, DataRetentionPolicyType, AccessRule, ActionType,
    STANDARD_RISK_TAGS, SECURITY_CONTROL_MATRIX,
)
from ndom.metadata import BIDSMapper
from ndom.io import NDOMSerializer


def test_subject():
    """测试受试者对象。"""
    s = NDOMSubject(
        subject_id="sub-01",
        age="P25Y",
        sex="M",
        species="Homo sapiens",
        pseudonym_id="pseudo-123",
        vulnerability_tags=["cognitive_impairment"],
    )
    assert s.subject_id == "sub-01"
    assert s.pseudonym_id == "pseudo-123"
    assert "cognitive_impairment" in s.vulnerability_tags
    assert hasattr(s, "object_id")
    print("[PASS] test_subject passed")


def test_device():
    """测试设备对象。"""
    model = NDOMDeviceModel(
        name="Neuropixels 1.0",
        manufacturer="Imec",
        neural_access_level=4,
        device_class="invasive",
    )
    device = NDOMDevice(
        name="probe-01",
        model=model,
        firmware_version="v1.2.0",
    )
    assert device.model.neural_access_level == 4
    assert device.model.device_class == "invasive"
    assert device.firmware_version == "v1.2.0"
    print("[PASS] test_device passed")


def test_electrode():
    """测试电极对象。"""
    eg = NDOMElectrodeGroup(
        name="M1-array",
        description="Motor cortex array",
        location="primary motor cortex",
    )
    elec = NDOMElectrode(
        x=1.0, y=2.0, z=3.0,
        location="M1 layer 5",
        group=eg,
        id=1,
    )
    assert elec.group.name == "M1-array"
    assert elec.x == 1.0
    print("[PASS] test_electrode passed")


def test_ndom_file():
    """测试 NDOMFile 对象。"""
    ndom = NDOMFile(
        session_description="Test session",
        identifier="test-001",
        session_start_time=datetime(2025, 1, 1, 10, 0, 0),
    )
    assert ndom.session_description == "Test session"
    assert ndom.object_id is not None
    assert ndom.file_create_date is not None
    print("[PASS] test_ndom_file passed")


def test_security_policy():
    """测试安全策略。"""
    retention = DataRetentionPolicy(
        policy_type=DataRetentionPolicyType.PROJECT_DURATION,
    )
    policy = SecurityPolicy(
        policy_id="sp-001",
        privacy_level=PrivacyLevel.RESTRICTED,
        data_retention_policy=retention,
        encryption_at_rest=True,
        encryption_in_transit=True,
        pseudonymization=True,
    )
    # L3 需要加密、假名化、访问日志
    violations = policy.validate_controls(NeuralDataSensitivity.L3)
    assert "access_control_list required" in violations
    print("[PASS] test_security_policy passed")


def test_consent_record():
    """测试同意记录。"""
    cr = ConsentRecord(
        consent_id="consent-001",
        consent_type=ConsentType.EXPLICIT_INFORMED,
        consent_scope=["primary_research"],
        consent_withdrawable=True,
    )
    assert cr.is_valid() is True
    assert cr.consent_type == ConsentType.EXPLICIT_INFORMED
    print("[PASS] test_consent_record passed")


def test_neural_data_class():
    """测试神经数据分类。"""
    ndc = NeuralDataClass(
        classification_id="ndc-001",
        sensitivity_level=NeuralDataSensitivity.L5,
        data_type="decoded",
        modality="BCI",
        decoding_status="decoded_intent",
        identifiability_risk="certain",
        mental_content_disclosure_risk="high",
    )
    assert ndc.sensitivity_level == NeuralDataSensitivity.L5
    assert ndc.identifiability_risk == "certain"
    print("[PASS] test_neural_data_class passed")


def test_risk_tags():
    """测试风险标签。"""
    rt = RiskTags(
        tags=["reidentification", "mental_decoding"],
    )
    assert "reidentification" in rt.tags
    nonstandard = rt.validate_tags()
    assert len(nonstandard) == 0  # 都是标准标签
    print("[PASS] test_risk_tags passed")


def test_audit_log():
    """测试审计日志。"""
    log = AuditLog()
    entry = log.add_entry  # 方法存在
    assert log.log_entries == []
    print("[PASS] test_audit_log passed")


def test_security_matrix():
    """测试安全控制矩阵。"""
    assert NeuralDataSensitivity.L5 in SECURITY_CONTROL_MATRIX
    assert SECURITY_CONTROL_MATRIX[NeuralDataSensitivity.L5]["encryption_at_rest"] is True
    assert SECURITY_CONTROL_MATRIX[NeuralDataSensitivity.L1]["encryption_at_rest"] is False
    print("[PASS] test_security_matrix passed")


def test_standard_risk_tags():
    """测试标准风险标签。"""
    assert "reidentification" in STANDARD_RISK_TAGS
    assert "mental_decoding" in STANDARD_RISK_TAGS
    assert "neurodiscrimination" in STANDARD_RISK_TAGS
    print("[PASS] test_standard_risk_tags passed")


def test_ndom_full_workflow():
    """测试完整工作流。"""
    ndom = NDOMFile(
        session_description="Full test session",
        identifier="full-test-001",
        session_start_time=datetime(2025, 6, 1, 9, 0, 0),
    )

    subject = NDOMSubject(subject_id="sub-01", age="P30Y", sex="F")
    ndom.add_subject(subject)

    policy = SecurityPolicy(
        policy_id="sp-001",
        privacy_level=PrivacyLevel.RESTRICTED,
        data_retention_policy=DataRetentionPolicy(
            policy_type=DataRetentionPolicyType.PROJECT_DURATION,
        ),
        encryption_at_rest=True,
        encryption_in_transit=True,
        pseudonymization=True,
        access_control_list=[AccessRule(role="researcher", permission="read")],
    )
    ndom.set_security_policy(policy)

    consent = ConsentRecord(
        consent_id="consent-001",
        consent_type=ConsentType.EXPLICIT_INFORMED,
    )
    ndom.set_consent_record(consent)

    ndc = NeuralDataClass(
        classification_id="ndc-001",
        sensitivity_level=NeuralDataSensitivity.L3,
        modality="EEG",
    )
    ndom.set_neural_data_class(ndc)

    # 验证
    validation = ndom.validate_security()
    assert validation["valid"] is True, f"Violations: {validation['violations']}"

    # 序列化
    data = ndom.to_dict()
    assert data["ndom_version"] == "0.1.0"
    assert data["subject"]["subject_id"] == "sub-01"
    assert data["security_policy"]["privacy_level"] == "RESTRICTED"

    print("[PASS] test_ndom_full_workflow passed")


def test_bids_mapper():
    """测试 BIDS 映射器。"""
    import tempfile
    ndom = NDOMFile(
        session_description="BIDS test",
        identifier="bids-test-001",
        session_start_time=datetime(2025, 6, 1, 9, 0, 0),
    )
    
    policy = SecurityPolicy(
        policy_id="sp-001",
        privacy_level=PrivacyLevel.RESTRICTED,
        data_retention_policy=DataRetentionPolicy(
            policy_type=DataRetentionPolicyType.PROJECT_DURATION,
        ),
    )
    ndom.set_security_policy(policy)

    with tempfile.TemporaryDirectory() as tmpdir:
        mapper = BIDSMapper(dataset_root=tmpdir, dataset_name="Test Dataset")
        desc = mapper.generate_dataset_description(ndom)
        assert desc["Name"] == "Test Dataset"
        assert desc["BIDSVersion"] == "1.11.0"
        assert desc["NDOMVersion"] == "0.1.0"

        sec = mapper.generate_dataset_security(ndom)
        assert sec["dataset_id"] == "bids-test-001"
        assert sec["security_policy"]["privacy_level"] == "RESTRICTED"

        paths = mapper.write_bids_layout(ndom, subject_id="01", session_id="01", modality="eeg", task_name="test", run_id=1)
        assert paths["dataset_description"].exists()
        assert paths["dataset_security"].exists()

    print("[PASS] test_bids_mapper passed")


def test_serializer():
    """测试序列化器。"""
    import tempfile
    ndom = NDOMFile(
        session_description="Serializer test",
        identifier="ser-test-001",
        session_start_time=datetime(2025, 6, 1, 9, 0, 0),
    )
    json_str = NDOMSerializer.to_json(ndom)
    assert "ndom_version" in json_str
    assert "ser-test-001" in json_str

    with tempfile.TemporaryDirectory() as tmpdir:
        fp = os.path.join(tmpdir, "test_output.json")
        NDOMSerializer.to_json(ndom, filepath=fp)
        assert os.path.exists(fp)

    print("[PASS] test_serializer passed")


def run_all_tests():
    """运行所有测试。"""
    print("=" * 60)
    print("NDOM Test Suite")
    print("=" * 60)
    
    tests = [
        test_subject,
        test_device,
        test_electrode,
        test_ndom_file,
        test_security_policy,
        test_consent_record,
        test_neural_data_class,
        test_risk_tags,
        test_audit_log,
        test_security_matrix,
        test_standard_risk_tags,
        test_ndom_full_workflow,
        test_bids_mapper,
        test_serializer,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1

    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
