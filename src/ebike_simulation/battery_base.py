from abc import ABC, abstractmethod


class BatteryBase(ABC):

    @abstractmethod
    def __init__(self, capacity_nom_Ah: float, initial_soc: float = 1.0):
        pass

    @abstractmethod
    def reset_soc(self) -> float:
        pass

    @abstractmethod
    def apply_current(self, current: float, duration: float) -> float:
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        pass

    @abstractmethod
    def is_full(self) -> bool:
        pass

    @abstractmethod
    def voltage(self, current: float = 0.0) -> float:
        pass

    @abstractmethod
    def power(self, current: float = 0.0) -> float:
        pass