from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import uuid


@dataclass
class NDOMDeviceModel:
    """设备模型，兼容 NWB DeviceModel。"""

    name: str
    manufacturer: str
    model_number: Optional[str] = None
    description: Optional[str] = None

    # NDOM 新增
    device_class: Optional[str] = None      # "invasive", "semi_invasive", "non_invasive", "consumer"
    neural_access_level: int = 1             # 1-5
    regulatory_status: Optional[str] = None  # "medical", "wellness", "research", "military"

    def __post_init__(self):
        self.object_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "manufacturer": self.manufacturer,
            "model_number": self.model_number,
            "description": self.description,
            "device_class": self.device_class,
            "neural_access_level": self.neural_access_level,
            "regulatory_status": self.regulatory_status,
            "object_id": self.object_id,
        }


@dataclass
class NDOMDevice:
    """设备实例，兼容 NWB Device 并扩展。"""

    name: str
    description: Optional[str] = None
    serial_number: Optional[str] = None
    model: Optional[NDOMDeviceModel] = None

    # NDOM 新增
    security_certification: Optional[str] = None
    firmware_version: Optional[str] = None
    data_integrity_hash: Optional[str] = None

    def __post_init__(self):
        self.object_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "serial_number": self.serial_number,
            "model": self.model.to_dict() if self.model else None,
            "security_certification": self.security_certification,
            "firmware_version": self.firmware_version,
            "data_integrity_hash": self.data_integrity_hash,
            "object_id": self.object_id,
        }
