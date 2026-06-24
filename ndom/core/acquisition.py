from dataclasses import dataclass, field
from typing import Dict, Any, List
import uuid

from ndom.core.base import NDOMDataInterface
from ndom.core.timeseries import NDOMTimeSeries


@dataclass
class NDOMAcquisition(NDOMDataInterface):
    """采集数据容器。"""
    timeseries: List[NDOMTimeSeries] = field(default_factory=list)

    def add_timeseries(self, ts: NDOMTimeSeries):
        self.timeseries.append(ts)

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["timeseries"] = [ts.to_dict() for ts in self.timeseries]
        return d


@dataclass
class NDOMProcessingModule:
    """处理模块，兼容 NWB ProcessingModule。"""

    name: str
    description: str
    data_interfaces: List[NDOMDataInterface] = field(default_factory=list)

    def __post_init__(self):
        self.object_id = str(uuid.uuid4())

    def add_data_interface(self, interface: NDOMDataInterface):
        self.data_interfaces.append(interface)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "data_interfaces": [di.to_dict() for di in self.data_interfaces],
            "object_id": self.object_id,
        }
