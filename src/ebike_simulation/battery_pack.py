from battery_base import BatteryBase
from scipy.interpolate import PchipInterpolator

class BatteryPack(BatteryBase):
    """
    Simple model of a battery pack as a single cell.
    The battery is modeled as an ideal voltage source (open circuit voltage) in series with an internal resistance.
    The open circuit voltage is a linear function of the state of charge (SoC).
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
        self.capacity_nom_As = capacity_nom_Ah * 3600
        self.R_int = internal_resistance_mOhm / 1000
        self.starting_soc = max(0.0, min(1.0, initial_soc))
        self.soc = self.starting_soc
        self.Vmin = Vmin
        self.Vmax = Vmax
        if self.soc_table is not None:
            self.pchip = PchipInterpolator(self.soc_table, self.voc_table)

    def reset_soc(self) -> float:
        self.soc = self.starting_soc
        return self.soc

    def apply_current(self, current: float = 0.0, duration: float = 0.0) -> float:
        """Modify the SoC based on the applied current & duration and return it."""
        
        delta_soc = (current * duration) / self.capacity_nom_As
        
        self.soc = max(0.0, min(1.0, self.soc - delta_soc))
        return self.soc
        
    def is_empty(self) -> bool:
        return self.soc <= 0.0 + 1e-9

    def is_full(self) -> bool:
        return self.soc >= 1.0 - 1e-9

    def voltage(self, current: float = 0.0) -> float:
        """Return the current voltage of the battery at the SoC and the given current flow"""
        if self.soc_table is None:
            open_circuit_voltage = self.Vmin + self.soc * (self.Vmax - self.Vmin)
        else:
            open_circuit_voltage = self.pchip(self.soc)

        v_out = open_circuit_voltage - self.R_int * current
        return v_out

    def __str__(self):
        return f"BatteryPack: {self.name}; SoC = {self.soc * 100:.1f}%"

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