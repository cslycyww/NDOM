from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import uuid

from ndom.core.base import NDOMDataInterface


@dataclass
class NDOMTimeSeries(NDOMDataInterface):
    """时间序列数据，兼容 NWB TimeSeries。"""

    data: Any = None
    unit: str = ""
    timestamps: Optional[Any] = None
    rate: Optional[float] = None
    description: Optional[str] = None
    starting_time: Optional[float] = None

    def __post_init__(self):
        self.object_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "unit": self.unit,
            "rate": self.rate,
            "description": self.description,
            "starting_time": self.starting_time,
            "has_data": self.data is not None,
            "has_timestamps": self.timestamps is not None,
        })
        return d


@dataclass
class NDOMTimeIntervals:
    """时间区间表，兼容 NWB TimeIntervals。"""

    name: str
    description: str = ""
    columns: Dict[str, List[Any]] = field(default_factory=dict)
    colnames: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.object_id = str(uuid.uuid4())

    def add_interval(self, start_time: float, stop_time: float, **kwargs):
        """添加一个时间区间。"""
        if "start_time" not in self.columns:
            self.columns["start_time"] = []
            self.columns["stop_time"] = []
            self.colnames = ["start_time", "stop_time"] + self.colnames
        self.columns["start_time"].append(start_time)
        self.columns["stop_time"].append(stop_time)
        for k, v in kwargs.items():
            if k not in self.columns:
                self.columns[k] = [None] * (len(self.columns["start_time"]) - 1)
                self.colnames.append(k)
            self.columns[k].append(v)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "columns": {k: v for k, v in self.columns.items()},
            "colnames": self.colnames,
            "object_id": self.object_id,
        }
