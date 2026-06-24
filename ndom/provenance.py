"""NDOM Provenance — 数据血缘

v0.2 新增：记录数据从 Raw → Decoded 的完整生命周期。
基于 W3C PROV 模型简化。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid


@dataclass
class ProcessingStep:
    """数据处理步骤。"""

    step_id: str
    step_name: str                          # "bandpass_filter", "epoching", "decoding"
    step_type: str                          # "filter", "artifact_removal", "feature_extraction", "decoding", "aggregation"
    input_objects: List[str] = field(default_factory=list)   # 输入对象 object_ids
    output_object: Optional[str] = None      # 输出对象 object_id
    parameters: Dict[str, Any] = field(default_factory=dict)   # 参数记录
    tool_name: Optional[str] = None          # 工具名称（MNE-Python, MATLAB, custom）
    tool_version: Optional[str] = None       # 工具版本
    execution_time_ms: Optional[float] = None  # 执行时间
    timestamp: datetime = field(default_factory=datetime.utcnow)
    operator: Optional[str] = None           # 操作者
    notes: Optional[str] = None

    def __post_init__(self):
        if not self.step_id:
            self.step_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "step_name": self.step_name,
            "step_type": self.step_type,
            "input_objects": self.input_objects,
            "output_object": self.output_object,
            "parameters": self.parameters,
            "tool_name": self.tool_name,
            "tool_version": self.tool_version,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "operator": self.operator,
            "notes": self.notes,
        }


@dataclass
class Provenance:
    """数据血缘。
    
    记录数据的完整来源、处理链和生成信息。
    """

    provenance_id: str

    # 来源信息
    source_file: Optional[str] = None          # 原始文件路径
    source_dataset: Optional[str] = None       # 来源数据集标识
    source_object: Optional[str] = None         # 来源对象 object_id
    parent_object: Optional[str] = None         # 直接父对象 object_id

    # 处理链（核心）
    preprocessing_steps: List[ProcessingStep] = field(default_factory=list)

    # 生成信息
    generated_by: Optional[str] = None           # 生成工具/脚本名称
    generated_by_version: Optional[str] = None    # 工具版本
    model_name: Optional[str] = None             # 模型名称（如果涉及 AI）
    model_version: Optional[str] = None          # 模型版本
    model_checkpoint: Optional[str] = None       # 模型检查点

    # 运行环境
    execution_environment: Optional[str] = None   # Docker, conda, venv, etc.
    compute_platform: Optional[str] = None          # 计算平台：AWS, Azure, HPC, local
    container_id: Optional[str] = None             # 容器 ID

    # 时间戳
    created_at: datetime = field(default_factory=datetime.utcnow)
    modified_at: datetime = field(default_factory=datetime.utcnow)

    # 完整血缘链（自动构建）
    lineage_chain: List[str] = field(default_factory=list)  # object_id 链，从根到当前

    def add_step(self, step: ProcessingStep) -> None:
        """添加处理步骤。"""
        self.preprocessing_steps.append(step)
        # 自动更新 lineage_chain
        if step.input_objects and step.input_objects[-1] not in self.lineage_chain:
            self.lineage_chain.append(step.input_objects[-1])

    def get_lineage(self) -> List[str]:
        """获取完整血缘链。"""
        return self.lineage_chain

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provenance_id": self.provenance_id,
            "source_file": self.source_file,
            "source_dataset": self.source_dataset,
            "source_object": self.source_object,
            "parent_object": self.parent_object,
            "preprocessing_steps": [s.to_dict() for s in self.preprocessing_steps],
            "generated_by": self.generated_by,
            "generated_by_version": self.generated_by_version,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "model_checkpoint": self.model_checkpoint,
            "execution_environment": self.execution_environment,
            "compute_platform": self.compute_platform,
            "container_id": self.container_id,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "lineage_chain": self.lineage_chain,
        }
