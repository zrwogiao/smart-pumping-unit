"""数据源抽象接口：模拟源 / 真实设备源可替换（答辩扩展点）。"""
from abc import ABC, abstractmethod
from typing import Dict


class DataSource(ABC):
    @abstractmethod
    def read_realtime(self, device: Dict) -> Dict:
        """读取一条实时监测数据。"""
        pass

    @abstractmethod
    def read_dynamo(self, device: Dict, condition: str = "normal"):
        """读取一张示功图 (位移, 载荷)。"""
        pass


class SimulatedDataSource(DataSource):
    def __init__(self):
        from app.services import simulator
        self._simulator = simulator

    def read_realtime(self, device: Dict) -> Dict:
        return self._simulator.generate_realtime(device)

    def read_dynamo(self, device: Dict, condition: str = "normal"):
        return self._simulator.generate_dynamo(condition)


# 全局数据源实例（未来替换为 MqttDataSource 即可接入真实设备）
data_source: DataSource = SimulatedDataSource()


def get_data_source() -> DataSource:
    return data_source
