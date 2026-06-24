from typing import Dict, Any
import uuid


class NDOMContainer:
    """所有 NDOM 对象的基类。"""

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.object_id: str = str(uuid.uuid4())
        self._annotations: Dict[str, Any] = {}
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "object_id": self.object_id,
            "neurodata_type": self.__class__.__name__,
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.name}' id={self.object_id[:8]}>"


class NDOMDataInterface(NDOMContainer):
    """数据接口基类，对应 NWB 的 DataInterface。"""
    pass
