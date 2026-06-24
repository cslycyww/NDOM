"""NDOM BIDS Mapper v0.2

支持 DataObject 级别的侧车文件生成。
扩展：指纹侧车、血缘侧车、风险画像侧车、资产侧车。
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from ndom.ndom import NDOM
from ndom.dataset import Dataset
from ndom.dataobject import DataObject
from ndom.enums import DataObjectType


class BIDSMapper:
    """BIDS 目录映射器（v0.2）。"""

    BIDS_MODALITIES = [
        "eeg", "ieeg", "meg", "func", "anat", "dwi", "fmap",
        "pet", "microscopy", "nirs", "motion", "mrs", "emg", "beh"
    ]

    def __init__(self, dataset_root: str, dataset_name: str):
        self.dataset_root = Path(dataset_root)
        self.dataset_name = dataset_name

    def generate_dataset_description(self, ndom: NDOM) -> Dict[str, Any]:
        """生成 dataset_description.json（BIDS 标准）。"""
        dataset = ndom.dataset
        return {
            "Name": self.dataset_name,
            "BIDSVersion": "1.11.0",
            "NDOMVersion": ndom.version,
            "DatasetType": "raw",
            "Authors": [dataset.subject.subject_id] if dataset and dataset.subject else [],
            "License": "CC-BY-4.0",
            "Keywords": dataset.keywords if dataset else [],
            "Funding": [],
            "EthicsApprovals": [],
        }

    def generate_dataset_asset(self, ndom: NDOM) -> Dict[str, Any]:
        """生成 dataset_asset.json（NDOM v0.2 新增）。"""
        if ndom.asset is None:
            return {}
        return ndom.asset.to_dict()

    def generate_dataset_risk_summary(self, ndom: NDOM) -> Dict[str, Any]:
        """生成 dataset_risk_summary.json（NDOM v0.2 新增）。"""
        summary = ndom.get_risk_summary()
        if summary is None:
            return {}
        return summary

    def generate_dataset_security(self, ndom: NDOM) -> Dict[str, Any]:
        """生成 dataset_security.json。"""
        dataset = ndom.dataset
        return {
            "ndom_version": ndom.version,
            "dataset_id": dataset.dataset_id if dataset else None,
            "global_security_policy": ndom.global_security_policy.to_dict() if ndom.global_security_policy else None,
            "default_security_policy": dataset.default_security_policy.to_dict() if dataset and dataset.default_security_policy else None,
            "compliance_framework": ndom.compliance_framework,
        }

    def generate_object_security_sidecar(self, obj: DataObject) -> Dict[str, Any]:
        """为单个 DataObject 生成安全侧车。"""
        policy = obj.security_policy
        classification = obj.classification
        risks = obj.risk_tags
        return {
            "ndom_version": "0.2.0",
            "object_id": obj.object_id,
            "object_type": obj.object_type.value,
            "privacy_level": policy.privacy_level.value if policy else None,
            "sensitivity_level": classification.sensitivity_level.value if classification else None,
            "risk_tags": risks.tags if risks else [],
            "security_controls": {
                "encryption_at_rest": policy.encryption_at_rest if policy else False,
                "encryption_in_transit": policy.encryption_in_transit if policy else False,
                "pseudonymization": policy.pseudonymization if policy else False,
                "differential_privacy_epsilon": policy.differential_privacy_epsilon if policy else None,
                "data_minimization": policy.data_minimization if policy else False,
            },
            "data_retention_policy": policy.data_retention_policy.to_dict() if policy else None,
            "audit_enabled": len(obj.audit_log.log_entries) > 0,
            "last_security_review": datetime.utcnow().isoformat(),
        }

    def generate_object_fingerprint_sidecar(self, obj: DataObject) -> Dict[str, Any]:
        """为 DataObject 生成指纹侧车（v0.2 新增）。"""
        fp = obj.fingerprint
        if fp is None:
            return {"object_id": obj.object_id, "fingerprint": None}
        return fp.to_dict()

    def generate_object_provenance_sidecar(self, obj: DataObject) -> Dict[str, Any]:
        """为 DataObject 生成血缘侧车（v0.2 新增）。"""
        prov = obj.provenance
        if prov is None:
            return {"object_id": obj.object_id, "provenance": None}
        return prov.to_dict()

    def generate_object_risk_profile_sidecar(self, obj: DataObject) -> Dict[str, Any]:
        """为 DataObject 生成风险画像侧车（v0.2 新增）。"""
        rp = obj.risk_profile
        if rp is None:
            return {"object_id": obj.object_id, "risk_profile": None}
        return rp.to_dict()

    def generate_object_consent_sidecar(self, obj: DataObject) -> Dict[str, Any]:
        """为 DataObject 生成同意侧车。"""
        cr = obj.consent_record
        if cr is None:
            return {}
        return cr.to_dict()

    def build_directory_structure(
        self,
        ndom: NDOM,
        subject_id: str,
        session_id: Optional[str] = None,
        modality: str = "eeg",
    ) -> Dict[str, Path]:
        """构建 BIDS + NDOM 扩展目录结构。"""
        paths = {}
        root = self.dataset_root

        # 数据集根级文件
        paths["dataset_description"] = root / "dataset_description.json"
        paths["dataset_asset"] = root / "dataset_asset.json"  # v0.2 新增
        paths["dataset_risk_summary"] = root / "dataset_risk_summary.json"  # v0.2 新增
        paths["dataset_security"] = root / "dataset_security.json"
        paths["participants"] = root / "participants.tsv"
        paths["readme"] = root / "README"

        # 受试者目录
        sub_dir = root / f"sub-{subject_id}"
        paths["sub_dir"] = sub_dir
        paths["sub_asset"] = sub_dir / f"sub-{subject_id}_asset.json"  # v0.2 新增
        paths["sub_security"] = sub_dir / f"sub-{subject_id}_security.json"

        if session_id:
            sub_dir = sub_dir / f"ses-{session_id}"

        # 模态目录
        modality_dir = sub_dir / modality
        modality_dir.mkdir(parents=True, exist_ok=True)
        paths["modality_dir"] = modality_dir

        # 衍生数据目录（v0.2 新增）
        derived_dir = sub_dir / "derived"
        derived_dir.mkdir(parents=True, exist_ok=True)
        paths["derived_dir"] = derived_dir

        return paths

    def write_bids_layout(
        self,
        ndom: NDOM,
        subject_id: str,
        session_id: Optional[str] = None,
        modality: str = "eeg",
        write_object_sidecars: bool = True,
    ) -> Dict[str, Path]:
        """写入完整的 BIDS + NDOM v0.2 扩展目录结构。

        注意：仅写入元数据文件，不写入原始数据。
        """
        paths = self.build_directory_structure(ndom, subject_id, session_id, modality)

        # 确保目录存在
        for p in paths.values():
            p.parent.mkdir(parents=True, exist_ok=True)

        # 写入 dataset_description.json
        with open(paths["dataset_description"], "w", encoding="utf-8") as f:
            json.dump(self.generate_dataset_description(ndom), f, indent=2, ensure_ascii=False)

        # 写入 dataset_asset.json（v0.2 新增）
        with open(paths["dataset_asset"], "w", encoding="utf-8") as f:
            json.dump(self.generate_dataset_asset(ndom), f, indent=2, ensure_ascii=False)

        # 写入 dataset_risk_summary.json（v0.2 新增）
        with open(paths["dataset_risk_summary"], "w", encoding="utf-8") as f:
            json.dump(self.generate_dataset_risk_summary(ndom), f, indent=2, ensure_ascii=False)

        # 写入 dataset_security.json
        with open(paths["dataset_security"], "w", encoding="utf-8") as f:
            json.dump(self.generate_dataset_security(ndom), f, indent=2, ensure_ascii=False)

        # 写入受试者级资产文件（v0.2 新增）
        if ndom.asset:
            with open(paths["sub_asset"], "w", encoding="utf-8") as f:
                json.dump(ndom.asset.to_dict(), f, indent=2, ensure_ascii=False)

        # 写入 participants.tsv
        if ndom.dataset and ndom.dataset.subject:
            subj = ndom.dataset.subject
            with open(paths["participants"], "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter="\t")
                writer.writerow(["participant_id", "age", "sex", "species", "pseudonym_id"])
                writer.writerow([
                    subj.subject_id, subj.age or "n/a", subj.sex or "n/a",
                    subj.species or "n/a", subj.pseudonym_id or "n/a"
                ])

        # 写入 DataObject 侧车文件
        if write_object_sidecars and ndom.dataset:
            for obj in ndom.dataset.objects:
                # 根据对象类型选择目录
                obj_dir = paths["modality_dir"] if obj.object_type == DataObjectType.RAW else paths["derived_dir"]
                base_name = f"sub-{subject_id}"
                if session_id:
                    base_name += f"_ses-{session_id}"
                base_name += f"_{obj.object_type.value}_{obj.name}"

                # 安全侧车
                sec_path = obj_dir / f"{base_name}_security.json"
                with open(sec_path, "w", encoding="utf-8") as f:
                    json.dump(self.generate_object_security_sidecar(obj), f, indent=2, ensure_ascii=False)

                # 指纹侧车（v0.2 新增）
                if obj.fingerprint:
                    fp_path = obj_dir / f"{base_name}_fingerprint.json"
                    with open(fp_path, "w", encoding="utf-8") as f:
                        json.dump(self.generate_object_fingerprint_sidecar(obj), f, indent=2, ensure_ascii=False)

                # 血缘侧车（v0.2 新增）
                if obj.provenance:
                    prov_path = obj_dir / f"{base_name}_provenance.json"
                    with open(prov_path, "w", encoding="utf-8") as f:
                        json.dump(self.generate_object_provenance_sidecar(obj), f, indent=2, ensure_ascii=False)

                # 风险画像侧车（v0.2 新增）
                if obj.risk_profile:
                    rp_path = obj_dir / f"{base_name}_risk_profile.json"
                    with open(rp_path, "w", encoding="utf-8") as f:
                        json.dump(self.generate_object_risk_profile_sidecar(obj), f, indent=2, ensure_ascii=False)

                # 同意侧车
                if obj.consent_record:
                    consent_path = obj_dir / f"{base_name}_consent.json"
                    with open(consent_path, "w", encoding="utf-8") as f:
                        json.dump(self.generate_object_consent_sidecar(obj), f, indent=2, ensure_ascii=False)

        # 写入 README
        if not paths["readme"].exists():
            with open(paths["readme"], "w", encoding="utf-8") as f:
                f.write(f"# {self.dataset_name}\n\n")
                if ndom.dataset:
                    f.write(f"Dataset: {ndom.dataset.dataset_id}\n")
                if ndom.asset:
                    f.write(f"Asset Owner: {ndom.asset.owner}\n")
                    f.write(f"Department: {ndom.asset.department}\n")
                f.write(f"\n## Security Notice\n")
                f.write(f"This dataset contains neural data managed under NDOM v0.2.\n")
                f.write(f"Each DataObject has independent security controls.\n")

        return paths
