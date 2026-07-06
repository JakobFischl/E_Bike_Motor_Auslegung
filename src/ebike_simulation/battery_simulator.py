from battery_pack import BatteryPack

from plotting_utils import (
    plot_current_profile,
    plot_voltage_profile,
    plot_voltage_and_current_profile,
)


class BatterySimulator:
    """Simple simulator for a battery pack. The simulator applies a current profile to the battery pack and records the voltage profile."""

    def __init__(self, battery_pack: BatteryPack) -> None:
        self.battery_pack = battery_pack
        self.voltage_profile = []

    def simulate(self, current_profile: list[float], duration_profile: list[float]) -> None:
        
        self.voltage_profile = [self.battery_pack.voltage()]

        for current, duration in zip(current_profile, duration_profile):
            
            if self.battery_pack.is_empty() == True and current > 0:
                print("Battery is empty: cannot discharge further!")
                break
            elif self.battery_pack.is_full() == True and current < 0:
                print("Battery is full: energy must be dissipated!")
                continue
            else:
                self.battery_pack.apply_current(current, duration)
                v = self.battery_pack.voltage(current)
                self.voltage_profile.append(v)


if __name__ == "__main__":
    load_current = [3.0, 11.0, 4.0, -1.5, 1.0]
    load_durations = [300.0, 240.0, 90.0, 150.0, 120.0]

    plot_current_profile(current_profile=load_current, duration_profile=load_durations)

    battery = BatteryPack(capacity_nom_Ah=10, initial_soc=0.01, Vmin=32.0, Vmax=42.0)
    bat_sim = BatterySimulator(battery)
    bat_sim.simulate(load_current, load_durations)
    print(battery)

    plot_voltage_profile(voltage_profile=bat_sim.voltage_profile, duration_profile=load_durations)
    plot_voltage_and_current_profile(bat_sim.voltage_profile, load_current, load_durations)

    input("Press Enter to continue...")