"""NDOM — 顶层入口

v0.2 核心重构：
- 引入 Asset 资产层
- 引入 Dataset 数据集层
- 引入 DataObject 核心原子单元
- SecurityPolicy 下放到 DataObject 级别
- 新增 Fingerprint, Provenance, AccessMetadata, RiskProfile
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from ndom.asset import Asset
from ndom.dataset import Dataset
from ndom.dataobject import DataObject
from ndom.security.policy import SecurityPolicy
from ndom.security.audit import AuditLog


@dataclass
class NDOM:
    """NDOM v0.2 顶层入口。

    完整架构：
    NDOM
    ├── Asset          # 数据资产（DSPM 核心）
    ├── Dataset        # 数据集（DataObject 容器）
    └── 全局安全设置
    """

    version: str = "0.2.0"
    schema_version: str = "0.2.0"

    # 资产
    asset: Optional[Asset] = None

    # 数据集
    dataset: Optional[Dataset] = None

    # 全局安全设置（兜底策略）
    global_security_policy: Optional[SecurityPolicy] = None

    # 合规框架
    compliance_framework: List[str] = field(default_factory=list)

    # 审计（全局）
    audit_log: AuditLog = field(default_factory=AuditLog)

    # 扩展
    custom_metadata: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # 便捷方法
    # ------------------------------------------------------------------
    def set_asset(self, asset: Asset) -> None:
        self.asset = asset

    def set_dataset(self, dataset: Dataset) -> None:
        self.dataset = dataset
        # 如果数据集有对象但未设置安全策略，继承全局策略
        if self.global_security_policy and dataset.default_security_policy is None:
            dataset.default_security_policy = self.global_security_policy

    def add_object(self, obj: DataObject) -> None:
        """向数据集添加数据对象。"""
        if self.dataset is None:
            raise ValueError("Dataset must be set before adding objects")
        self.dataset.add_object(obj)

    def get_object(self, object_id: str) -> Optional[DataObject]:
        if self.dataset is None:
            return None
        return self.dataset.get_object_by_id(object_id)

    # ------------------------------------------------------------------
    # 验证
    # ------------------------------------------------------------------
    def validate(self) -> Dict[str, Any]:
        """全面验证 NDOM 实例。

        Returns:
            验证结果字典，包含 errors, warnings, recommendations。
        """
        result = {"valid": True, "errors": [], "warnings": [], "recommendations": []}

        if self.asset is None:
            result["warnings"].append("Asset not defined; consider adding asset metadata for DSPM compliance")

        if self.dataset is None:
            result["errors"].append("Dataset is required")
            result["valid"] = False
        else:
            # 验证每个数据对象
            for obj in self.dataset.objects:
                obj_result = obj.validate()
                result["warnings"].extend(
                    [f"Object {obj.object_id}: {w}" for w in obj_result.get("warnings", [])]
                )
                result["recommendations"].extend(
                    [f"Object {obj.object_id}: {r}" for r in obj_result.get("recommendations", [])]
                )
                result["errors"].extend(
                    [f"Object {obj.object_id}: {e}" for e in obj_result.get("errors", [])]
                )

            # 检查是否有高风险对象未设置安全策略
            for obj in self.dataset.get_high_risk_objects():
                if obj.security_policy is None:
                    result["warnings"].append(
                        f"High-risk object {obj.object_id} ({obj.name}) has no security policy"
                    )

        if len(result["errors"]) > 0:
            result["valid"] = False

        return result

    # ------------------------------------------------------------------
    # 风险汇总
    # ------------------------------------------------------------------
    def get_risk_summary(self) -> Optional[Dict[str, Any]]:
        """获取数据集风险汇总。"""
        if self.dataset is None:
            return None
        return self.dataset.get_risk_summary()

    # ------------------------------------------------------------------
    # 序列化
    # ------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "schema_version": self.schema_version,
            "asset": self.asset.to_dict() if self.asset else None,
            "dataset": self.dataset.to_dict() if self.dataset else None,
            "global_security_policy": self.global_security_policy.to_dict() if self.global_security_policy else None,
            "compliance_framework": self.compliance_framework,
            "audit_log": self.audit_log.to_dict(),
            "custom_metadata": self.custom_metadata,
        }
