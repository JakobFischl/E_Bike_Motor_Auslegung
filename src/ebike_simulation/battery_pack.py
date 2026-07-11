from battery_base import BatteryBase
from scipy.interpolate import PchipInterpolator
import logging

# Set up local logger
logger = logging.getLogger(__name__)

class BatteryPack(BatteryBase):
    """
    Simple model of a battery pack as a single cell.
    The battery is modeled as an ideal voltage source (open circuit voltage) in series with an internal resistance.
    The SoC is updated based on the applied current and duration.
    """
    name = "Standard battery pack"
    soc_table = None
    voc_table = None

    def __init__(
        self,
        capacity_nom_Ah: float = 10,
        internal_resistance_mOhm: float = 80.0,
        initial_soc: float = 1.0,
        Vmin: float = 30,
        Vmax: float = 42,
    ):
        
        if capacity_nom_Ah <= 0:
            raise ValueError("Capacity must be positive.")
        self.capacity_nom_As = capacity_nom_Ah * 3600

        if internal_resistance_mOhm <= 0:
            raise ValueError("Internal resistance must be positive.")
        self.R_int = internal_resistance_mOhm / 1000
        
        if initial_soc < 0 or initial_soc > 1.0:
            raise ValueError("The initial state of charge has to be between 0 and 1.")
        self.starting_soc = initial_soc
        self.soc = self.starting_soc

        if Vmin >= Vmax:
            raise ValueError("The minimum voltage of the battery must be lower than the maximum voltage.")
        self.Vmin = Vmin
        self.Vmax = Vmax
        self.pchip = None
        if self.soc_table is not None and self.voc_table is not None:
            if len(self.soc_table) != len(self.voc_table):
                raise ValueError("The open circuit voltage must be defined by the same amount of values as the soc_table.")
            elif not all(x < y for x, y in zip(self.soc_table, self.soc_table[1:])):
                raise ValueError("The values in soc_table must be strictly monotonically increasing.")
            self.pchip = PchipInterpolator(self.soc_table, self.voc_table)

        logger.debug(f"Constructed {self.name} with {capacity_nom_Ah} Ah and {initial_soc * 100:.2f} initial state of charge.")

    def reset_soc(self) -> float:
        self.soc = self.starting_soc
        return self.soc

    def apply_current(self, current: float = 0.0, duration: float = 0.0) -> float:
        """Modify the SoC based on the applied current & duration and return it."""

        delta_soc = (current * duration) / self.capacity_nom_As
        unclamped_soc = self.soc - delta_soc
        if unclamped_soc > 1:
            logger.info(f"The state of charge would reach {unclamped_soc * 100:.2f}%, clamped to 100%.")
            self.soc = 1.0
        elif unclamped_soc < 0:
            logger.warning(f"The state of charge would reach {unclamped_soc * 100:.2f}%, clamped to 0%.")
            self.soc = 0.0
        else:
            self.soc = unclamped_soc

        return self.soc
        
    def is_empty(self) -> bool:
        return self.soc <= 0.0 + 1e-9

    def is_full(self) -> bool:
        return self.soc >= 1.0 - 1e-9

    def voltage(self, current: float = 0.0) -> float:
        """Return the current voltage of the battery at the SoC and the given current flow"""
        if self.pchip is None:
            open_circuit_voltage = self.Vmin + self.soc * (self.Vmax - self.Vmin)
        else:
            open_circuit_voltage = float(self.pchip(self.soc))

        v_out = open_circuit_voltage - self.R_int * current
        return v_out

    def __str__(self):
        return f"Battery: {self.name}; SoC = {self.soc * 100:.1f}%"

    def power(self, current: float = 0.0) -> float:
        """Return the current power draw from the battery at the given current flow and SoC."""
        power_out = self.voltage(current) * current
        return power_out




if __name__ == "__main__":

    battery = BatteryPack(capacity_nom_Ah=10, initial_soc=0.7, Vmin=32.0, Vmax=42.0)
    print(battery)

    battery.apply_current(current=5.0, duration=300.0)
    print(battery)
    print(f"{battery.voltage(current = 482.25):.2f} V")
    battery.apply_current(current=10.0, duration=240.0)
    print(battery)
    battery.apply_current(current=-5.0, duration=150.0)
    print(battery)
    print(f"{battery.power(current = 5.0):.2f} W")