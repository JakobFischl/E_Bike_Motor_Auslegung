class BatteryPack:
    """
    Simple model of a battery pack as a single cell.
    The battery is modeled as an ideal voltage source (open circuit voltage) in series with an internal resistance.
    The open circuit voltage is a linear function of the state of charge (SoC).
    The SoC is updated based on the applied current and duration.
    """

    def __init__(
        self,
        capacity_nom_Ah: float = 10,
        internal_resistance_mOhm: float = 80.0,
        initial_soc: float = 1.0,
        Vmin: float = 30,
        Vmax: float = 42,
    ):
        self.capacity_nom_As = capacity_nom_Ah * 3600
        self.internal_resistance_Ohm = internal_resistance_mOhm / 1000
        self.soc = max(0.0, min(1.0, initial_soc))
        self.Vmin = Vmin
        self.Vmax = Vmax

    def apply_current(self, current: float, duration: float) -> None:
        """Modify the SoC based on the applied current & duration"""
        
        delta_soc = (current * duration) / self.capacity_nom_As
        
        self.soc = max(0.0, min(1.0, self.soc - delta_soc))

        
    def is_empty(self) -> bool:
        if self.soc <= 0.0 + 1e-9:
            return True
        else:
            return False

    def is_full(self) -> bool:
        if self.soc >= 1.0 - 1e-9:
            return True
        else:
            return False

    def voltage(self, current: float = 0.0) -> float:
        """Return the current voltage of the battery at the SoC and the given current flow"""
        V_oc = self.Vmin + self.soc * (self.Vmax - self.Vmin)
        v_out = V_oc - self.internal_resistance_Ohm * current
        return v_out

    def __str__(self):
        return f"BatteryPack(SoC={self.soc * 100:.1f}%, V={self.voltage():.2f} V)"


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