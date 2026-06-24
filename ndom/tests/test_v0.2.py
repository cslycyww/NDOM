"""NDOM v0.2 Test Suite

测试所有核心对象：Asset, DataObject, Dataset, Fingerprint, Provenance,
AccessMetadata, RiskProfile, SecurityPolicy（对象级）, 枚举, BIDS映射。
"""

import os, sys, io, json, tempfile
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ndom import (
    NDOM, Asset, Dataset, DataObject,
    SecurityPolicy, ConsentRecord, NeuralDataClass, RiskTags, RiskProfile, ThreatProfile,
    Fingerprint, Provenance, ProcessingStep, AccessMetadata,
    PrivacyLevel, NeuralDataSensitivity, ConsentType, ConsentScope, DataObjectType,
    DataRetentionPolicy, DataRetentionPolicyType, AccessRule, IdentifiabilityRisk,
    NeuralModality, DecodingStatus, SpatialResolution, TemporalResolution,
    RiskLevel, SharingStatus,
    STANDARD_RISK_TAGS, RISK_WEIGHTS,
    NDOMSubject,
    BIDSMapper, NDOMSerializer,
)


def test_enums():
    assert PrivacyLevel.RESTRICTED.value == "RESTRICTED"
    assert PrivacyLevel.NEURAL_SECRET.value == "NEURAL_SECRET"
    assert NeuralDataSensitivity.L5.value == "L5"
    assert DataObjectType.DECODED.value == "decoded"
    assert ConsentScope.AI_TRAINING.value == "ai_training"
    assert RiskLevel.CRITICAL.value == "critical"
    assert SharingStatus.PRIVATE.value == "private"
    return "PASS: test_enums"


def test_asset():
    a = Asset(
        asset_id="asset-test", asset_name="Test Asset", owner="Dr. Test",
        department="Test Lab", location="Building A", storage_system="S3",
        compliance_scope=["GDPR", "HIPAA"],
    )
    assert a.owner == "Dr. Test"
    assert "GDPR" in a.compliance_scope
    assert a.to_dict()["asset_type"] == "neural_dataset"
    return "PASS: test_asset"


def test_fingerprint():
    fp = Fingerprint(
        fingerprint_id="fp-test", sha256="abc123", perceptual_hash="ph123",
        channel_signature="32ch_2048Hz", signal_signature="mean=0.5uV",
    )
    assert fp.sha256 == "abc123"
    assert fp.to_dict()["channel_signature"] == "32ch_2048Hz"
    return "PASS: test_fingerprint"


def test_provenance():
    prov = Provenance(provenance_id="prov-test", source_file="test.edf")
    step = ProcessingStep(
        step_id="step-1",
        step_name="bandpass_filter", step_type="filter",
        input_objects=["obj-1"], output_object="obj-2",
        parameters={"low": 0.1, "high": 100},
    )
    prov.add_step(step)
    assert len(prov.preprocessing_steps) == 1
    assert prov.lineage_chain == ["obj-1"]
    return "PASS: test_provenance"


def test_access_metadata():
    am = AccessMetadata(object_id="obj-test")
    am.record_access("user1", "researcher")
    am.record_export(1024)
    am.record_download(2048)
    am.add_anomaly_flag("unusual_download_volume")
    assert am.access_count == 1
    assert am.export_count == 1
    assert am.download_count == 1
    assert "unusual_download_volume" in am.anomaly_flags
    assert am.total_bytes_exported == 1024
    return "PASS: test_access_metadata"


def test_risk_profile():
    rp = RiskProfile(
        profile_id="rp-test",
        identity_risk=9.0, medical_risk=9.0, behavioral_risk=9.0,
        cognitive_risk=9.0, emotional_risk=9.0, linguistic_risk=9.0,
        memory_risk=9.0, reconstruction_risk=9.0,
    )
    assert rp.overall_score > 0
    assert rp.risk_level == RiskLevel.CRITICAL
    assert rp.is_critical() is True
    assert rp.needs_attention() is True
    assert rp.get_dimension_score("cognitive_risk") == 9.0
    return "PASS: test_risk_profile"


def test_risk_profile_weights():
    assert "cognitive_risk" in RISK_WEIGHTS
    assert RISK_WEIGHTS["cognitive_risk"] == 1.5
    return "PASS: test_risk_profile_weights"


def test_risk_tags():
    rt = RiskTags(
        tags=["reidentification", "intent_inference", "language_inference"],
    )
    assert len(rt.validate_tags()) == 0
    assert rt.is_inference_tag("intent_inference") is True
    assert rt.is_inference_tag("reidentification") is False
    inference_tags = rt.get_inference_tags()
    assert "intent_inference" in inference_tags
    assert "language_inference" in inference_tags
    return "PASS: test_risk_tags"


def test_standard_risk_tags():
    assert "identity_inference" in STANDARD_RISK_TAGS
    assert "medical_inference" in STANDARD_RISK_TAGS
    assert "emotion_inference" in STANDARD_RISK_TAGS
    assert "intent_inference" in STANDARD_RISK_TAGS
    assert "language_inference" in STANDARD_RISK_TAGS
    assert "memory_inference" in STANDARD_RISK_TAGS
    assert "location_inference" in STANDARD_RISK_TAGS
    assert "biometric_linkage" in STANDARD_RISK_TAGS
    return "PASS: test_standard_risk_tags"


def test_dataobject():
    obj = DataObject(
        object_id="obj-test", object_type=DataObjectType.RAW,
        name="test_eeg", data_format="edf",
    )
    assert obj.object_type == DataObjectType.RAW
    assert obj.security_policy is None

    # 设置安全策略
    policy = SecurityPolicy(
        policy_id="sp-test", privacy_level=PrivacyLevel.RESTRICTED,
        data_retention_policy=DataRetentionPolicy(policy_type=DataRetentionPolicyType.PROJECT_DURATION),
    )
    obj.set_security_policy(policy)
    assert obj.security_policy is not None

    # 验证
    result = obj.validate()
    assert "valid" in result
    return "PASS: test_dataobject"


def test_dataobject_inheritance():
    parent_policy = SecurityPolicy(
        policy_id="sp-parent", privacy_level=PrivacyLevel.RESTRICTED,
        data_retention_policy=DataRetentionPolicy(policy_type=DataRetentionPolicyType.PROJECT_DURATION),
    )
    obj = DataObject(
        object_id="obj-inherit", object_type=DataObjectType.RAW, name="inherit_test",
    )
    obj.inherit_security_policy(parent_policy)
    assert obj.security_policy is not None
    assert obj.security_policy.policy_id.startswith("sp-parent-child")
    return "PASS: test_dataobject_inheritance"


def test_dataobject_lineage():
    parent = DataObject(object_id="obj-parent", object_type=DataObjectType.RAW, name="parent")
    child = DataObject(object_id="obj-child", object_type=DataObjectType.PROCESSED, name="child", parent_object=parent.object_id)
    parent.add_child(child.object_id)
    assert child.parent_object == parent.object_id
    assert child.object_id in parent.child_objects
    return "PASS: test_dataobject_lineage"


def test_dataset():
    ds = Dataset(dataset_id="ds-test", description="Test dataset")
    obj = DataObject(object_id="obj-1", object_type=DataObjectType.RAW, name="raw")
    ds.add_object(obj)
    assert len(ds.objects) == 1
    assert ds.get_object_by_id("obj-1") == obj
    return "PASS: test_dataset"


def test_dataset_risk_summary():
    ds = Dataset(dataset_id="ds-risk", description="Risk test")
    obj1 = DataObject(
        object_id="obj-1", object_type=DataObjectType.RAW, name="raw",
    )
    obj1.risk_profile = RiskProfile(profile_id="rp-1",
                                     identity_risk=2.0, medical_risk=2.0, cognitive_risk=2.0,
                                     emotional_risk=2.0, linguistic_risk=2.0, memory_risk=2.0,
                                     reconstruction_risk=2.0)
    obj2 = DataObject(
        object_id="obj-2", object_type=DataObjectType.DECODED, name="decoded",
    )
    obj2.risk_profile = RiskProfile(profile_id="rp-2",
                                     identity_risk=9.0, medical_risk=9.0, behavioral_risk=9.0,
                                     cognitive_risk=9.0, emotional_risk=9.0, linguistic_risk=9.0,
                                     memory_risk=9.0, reconstruction_risk=9.0)
    ds.add_object(obj1)
    ds.add_object(obj2)
    summary = ds.get_risk_summary()
    assert summary["total_objects"] == 2
    assert summary["risk_distribution"]["low"] == 1
    assert summary["risk_distribution"]["critical"] == 1
    assert len(summary["objects_needing_attention"]) == 1
    return "PASS: test_dataset_risk_summary"


def test_dataset_lineage():
    ds = Dataset(dataset_id="ds-lineage", description="Lineage test")
    obj1 = DataObject(object_id="obj-a", object_type=DataObjectType.RAW, name="raw")
    obj2 = DataObject(object_id="obj-b", object_type=DataObjectType.PROCESSED, name="proc", parent_object="obj-a")
    obj3 = DataObject(object_id="obj-c", object_type=DataObjectType.DECODED, name="decoded", parent_object="obj-b")
    ds.add_object(obj1)
    ds.add_object(obj2)
    ds.add_object(obj3)
    chain = ds.get_lineage("obj-c")
    assert chain == ["obj-a", "obj-b", "obj-c"]
    return "PASS: test_dataset_lineage"


def test_ndom_top():
    ndom = NDOM(version="0.2.0")
    assert ndom.version == "0.2.0"
    assert ndom.dataset is None
    return "PASS: test_ndom_top"


def test_ndom_validation():
    ndom = NDOM(version="0.2.0")
    result = ndom.validate()
    assert result["valid"] is False  # 缺少 Dataset
    assert "Dataset is required" in result["errors"]
    return "PASS: test_ndom_validation"


def test_ndom_full_workflow():
    asset = Asset(asset_id="a1", asset_name="Test", owner="Test", department="Test", location="Test", storage_system="Test")
    ds = Dataset(dataset_id="ds1", description="Test")
    ds.default_security_policy = SecurityPolicy(
        policy_id="sp1", privacy_level=PrivacyLevel.INTERNAL,
        data_retention_policy=DataRetentionPolicy(policy_type=DataRetentionPolicyType.PROJECT_DURATION),
    )
    obj = DataObject(object_id="obj1", object_type=DataObjectType.RAW, name="test")
    ds.add_object(obj)

    ndom = NDOM(asset=asset, dataset=ds)
    result = ndom.validate()
    assert result["valid"] is True
    assert ndom.get_risk_summary() is not None
    return "PASS: test_ndom_full_workflow"


def test_bids_mapper():
    asset = Asset(asset_id="a1", asset_name="Test", owner="Test", department="Test", location="Test", storage_system="Test")
    ds = Dataset(dataset_id="ds1", description="Test")
    ds.default_security_policy = SecurityPolicy(
        policy_id="sp1", privacy_level=PrivacyLevel.INTERNAL,
        data_retention_policy=DataRetentionPolicy(policy_type=DataRetentionPolicyType.PROJECT_DURATION),
    )
    obj = DataObject(object_id="obj1", object_type=DataObjectType.RAW, name="test")
    obj.classification = NeuralDataClass(
        classification_id="nc1", sensitivity_level=NeuralDataSensitivity.L3,
        modality=NeuralModality.EEG,
    )
    obj.risk_profile = RiskProfile(profile_id="rp-bids-1",
                                    identity_risk=5.0, medical_risk=5.0, behavioral_risk=5.0,
                                    cognitive_risk=5.0, emotional_risk=5.0, linguistic_risk=5.0,
                                    memory_risk=5.0, reconstruction_risk=5.0)
    obj.fingerprint = Fingerprint(fingerprint_id="fp1", sha256="abc")
    obj.provenance = Provenance(provenance_id="p1", source_file="test.edf")
    ds.add_object(obj)

    ndom = NDOM(asset=asset, dataset=ds)

    with tempfile.TemporaryDirectory() as tmpdir:
        mapper = BIDSMapper(dataset_root=tmpdir, dataset_name="Test")
        paths = mapper.write_bids_layout(ndom, subject_id="01", modality="eeg")
        assert paths["dataset_description"].exists()
        assert paths["dataset_asset"].exists()
        assert paths["dataset_risk_summary"].exists()
        assert paths["dataset_security"].exists()

    return "PASS: test_bids_mapper"


def test_serializer():
    asset = Asset(asset_id="a1", asset_name="Test", owner="Test", department="Test", location="Test", storage_system="Test")
    ds = Dataset(dataset_id="ds1", description="Test")
    obj = DataObject(object_id="obj1", object_type=DataObjectType.RAW, name="test")
    ds.add_object(obj)
    ndom = NDOM(asset=asset, dataset=ds)

    json_str = NDOMSerializer.to_json(ndom)
    assert "version" in json_str
    assert "asset" in json_str
    assert "dataset" in json_str

    with tempfile.TemporaryDirectory() as tmpdir:
        fp = os.path.join(tmpdir, "test.json")
        NDOMSerializer.to_json(ndom, filepath=fp)
        assert os.path.exists(fp)

    return "PASS: test_serializer"


def test_security_policy_v02():
    policy = SecurityPolicy(
        policy_id="sp-v02", privacy_level=PrivacyLevel.NEURAL_SECRET,
        data_retention_policy=DataRetentionPolicy(policy_type=DataRetentionPolicyType.SESSION_ONLY),
        data_minimization=True,
        purpose_limitation=["research_only"],
        encryption_at_rest=True,
        encryption_in_transit=True,
        pseudonymization=True,
        differential_privacy_epsilon=0.1,
        access_control_list=[AccessRule(role="pi", permission="admin")],
    )
    assert policy.data_minimization is True
    assert "research_only" in policy.purpose_limitation
    violations = policy.validate_controls(NeuralDataSensitivity.L5)
    assert len(violations) == 0, f"Violations: {violations}"
    return "PASS: test_security_policy_v02"


def test_threat_profile():
    tp = ThreatProfile(
        threat_profile_id="tp-test",
        attack_surface=["export", "cloud_storage", "model_training"],
        threat_actors=["external_hacker", "insider_malicious"],
        attack_scenarios=["mental_decoding_exfiltration", "model_inversion_attack"],
        mitigations=["encryption_at_rest", "access_control"],
        neuroattck_mapping="T0012.003",
    )
    assert tp.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
    assert tp.needs_attention() is True
    assert len(tp.validate_surfaces()) == 0
    assert len(tp.validate_actors()) == 0
    assert len(tp.validate_scenarios()) == 0
    assert tp.neuroattck_mapping == "T0012.003"
    assert "mental_decoding_exfiltration" in tp.attack_scenarios
    return "PASS: test_threat_profile"


def test_threat_profile_mitigation():
    tp = ThreatProfile(
        threat_profile_id="tp-mit",
        attack_surface=["export"],
        threat_actors=["external_hacker"],
        attack_scenarios=["membership_inference"],
        mitigations=["differential_privacy", "access_control", "encryption_at_rest", "audit_logging"],
    )
    # 缓解措施足够多，风险等级应降低
    assert tp.risk_level in (RiskLevel.LOW, RiskLevel.MEDIUM)
    assert tp.needs_attention() is False
    return "PASS: test_threat_profile_mitigation"


def test_threat_profile_on_dataobject():
    obj = DataObject(
        object_id="obj-tp", object_type=DataObjectType.DECODED, name="decoded_intent",
    )
    tp = ThreatProfile(
        threat_profile_id="tp-obj",
        attack_surface=["inference_api", "export"],
        threat_actors=["external_hacker", "competitor"],
        attack_scenarios=["mental_decoding_exfiltration", "adversarial_decoding"],
    )
    obj.set_threat_profile(tp)
    assert obj.threat_profile is not None
    assert obj.threat_profile.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
    return "PASS: test_threat_profile_on_dataobject"


def test_consent_withdrawal():
    cr = ConsentRecord(consent_id="c1", consent_type=ConsentType.EXPLICIT_INFORMED)
    assert cr.is_valid() is True
    cr.withdraw("subject_001", "changed_mind")
    assert cr.is_valid() is False
    assert cr.withdrawal_date is not None
    return "PASS: test_consent_withdrawal"


def run_all_tests():
    tests = [
        test_enums, test_asset, test_fingerprint, test_provenance,
        test_access_metadata, test_risk_profile, test_risk_profile_weights,
        test_risk_tags, test_standard_risk_tags,
        test_dataobject, test_dataobject_inheritance, test_dataobject_lineage,
        test_dataset, test_dataset_risk_summary, test_dataset_lineage,
        test_ndom_top, test_ndom_validation, test_ndom_full_workflow,
        test_bids_mapper, test_serializer, test_security_policy_v02,
        test_threat_profile, test_threat_profile_mitigation, test_threat_profile_on_dataobject,
        test_consent_withdrawal,
    ]
    results = []
    passed = 0
    failed = 0
    for t in tests:
        try:
            results.append(t())
            passed += 1
        except Exception as e:
            results.append(f"FAIL: {t.__name__}: {e}")
            failed += 1
    return {"results": results, "passed": passed, "failed": failed, "success": failed == 0}


if __name__ == "__main__":
    result = run_all_tests()
    print("=" * 60)
    print("NDOM v0.2 Test Results")
    print("=" * 60)
    for r in result["results"]:
        print(r)
    print(f"\nPassed: {result['passed']}, Failed: {result['failed']}")
    sys.exit(0 if result["success"] else 1)
