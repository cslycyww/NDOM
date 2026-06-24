# ndom/core/__init__.py
# 从子模块导入核心类，保持统一命名空间

from ndom.core.base import NDOMContainer, NDOMDataInterface
from ndom.core.subject import NDOMSubject
from ndom.core.device import NDOMDevice, NDOMDeviceModel
from ndom.core.electrode import NDOMElectrodeGroup, NDOMElectrode
from ndom.core.timeseries import NDOMTimeSeries, NDOMTimeIntervals
from ndom.core.acquisition import NDOMAcquisition, NDOMProcessingModule
from ndom.core.ndom_file import NDOMFile

__all__ = [
    "NDOMContainer",
    "NDOMDataInterface",
    "NDOMSubject",
    "NDOMDevice",
    "NDOMDeviceModel",
    "NDOMElectrodeGroup",
    "NDOMElectrode",
    "NDOMTimeSeries",
    "NDOMTimeIntervals",
    "NDOMAcquisition",
    "NDOMProcessingModule",
    "NDOMFile",
]
