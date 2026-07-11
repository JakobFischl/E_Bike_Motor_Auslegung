from abc import ABC, abstractmethod


class BatteryBase(ABC):
    """
    Abstract interface for a battery pack model.
    Subclasses track a state of charge (SoC) between zero and one and calculate the pack
    voltage and power under a given current (positive = discharge).
    """

    @abstractmethod
    def __init__(self, capacity_nom_Ah: float, initial_soc: float = 1.0):
        """Construct a pack of the given nominal capacity and initial SoC between zero and one."""
        pass

    @abstractmethod
    def reset_soc(self) -> float:
        """Reset the SoC to its initial value and return it."""
        pass

    @abstractmethod
    def apply_current(self, current: float, duration: float) -> float:
        """Update the SoC for a current applied over a duration and return the new SoC."""
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        """Return True if the pack is fully discharged."""
        pass

    @abstractmethod
    def is_full(self) -> bool:
        """Return True if the pack is fully charged."""
        pass

    @abstractmethod
    def voltage(self, current: float = 0.0) -> float:
        """Return the output voltage at the present SoC under the given current."""
        pass

    @abstractmethod
    def power(self, current: float = 0.0) -> float:
        """Return the output power at the present SoC under the given current."""
        pass