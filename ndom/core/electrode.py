from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import uuid

from ndom.core.device import NDOMDevice


@dataclass
class NDOMElectrodeGroup:
    """电极组，兼容 NWB ElectrodeGroup。"""

    name: str
    description: str
    location: str
    device: Optional[NDOMDevice] = None
    position: Optional[List[float]] = None

    def __post_init__(self):
        self.object_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "location": self.location,
            "device": self.device.to_dict() if self.device else None,
            "position": self.position,
            "object_id": self.object_id,
        }


@dataclass
class NDOMElectrode:
    """电极，兼容 NWB Electrode。"""

    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None
    imp: Optional[float] = None
    location: Optional[str] = None
    filtering: Optional[str] = None
    group: Optional[NDOMElectrodeGroup] = None
    id: Optional[int] = None
    rel_x: Optional[float] = None
    rel_y: Optional[float] = None
    rel_z: Optional[float] = None
    reference: Optional[str] = None

    def __post_init__(self):
        self.object_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "x": self.x, "y": self.y, "z": self.z,
            "imp": self.imp, "location": self.location,
            "filtering": self.filtering,
            "group": self.group.to_dict() if self.group else None,
            "id": self.id,
            "rel_x": self.rel_x, "rel_y": self.rel_y, "rel_z": self.rel_z,
            "reference": self.reference,
            "object_id": self.object_id,
        }
