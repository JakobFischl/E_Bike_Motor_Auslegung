from battery_pack import BatteryPack
from lipo_battery import LiPoBatteryPack
from nmc_battery import NMCBatteryPack

from plotting_utils import (
    plot_current_profile,
    plot_voltage_profile,
    plot_voltage_and_current_profile,
    plot_soc_profile,
    plot_power_profile
)

from typing import NamedTuple

class SummaryResult(NamedTuple):
    final_soc: float
    min_soc: float
    max_power: float
    total_energy: float
    total_discharge: float
    meets_soc_reserve: bool


class BatterySimulator:
    """Simple simulator for a battery pack. The simulator applies a current profile to the battery pack 
    and records voltage profile, state of charge over time and a power profile."""

    def __init__(self, battery_pack) -> None:
        self.battery_pack = battery_pack
        self.voltage_profile = []
        self.truncated_duration_profile = []
        self.truncated_current_profile = []
        self.soc_profile = []
        self.power_profile = []

    def simulate(self, current_profile: list[float], duration_profile: list[float]) -> None:
        
        self.battery_pack.reset_soc()
        self.voltage_profile = [self.battery_pack.voltage()]
        self.soc_profile = [self.battery_pack.soc]
        self.power_profile = []

        for current, duration in zip(current_profile, duration_profile):
            
            if self.battery_pack.is_empty():
                print("Battery is empty: cannot discharge further!")
                break
                
            elif self.battery_pack.is_full() and current < 0:
                effective_current = 0.0
                # print(f"Battery is full: {power:.2f} W must be dissipated!") supposed to be logging later
            else:
                effective_current = current

            v = self.battery_pack.voltage(effective_current)
            self.voltage_profile.append(v)
            soc = self.battery_pack.apply_current(effective_current, duration)
            self.soc_profile.append(soc)
            power = self.battery_pack.power(effective_current)
            self.power_profile.append(power)
        
        n = len(self.power_profile)
        self.truncated_duration_profile = duration_profile[:n]
        self.truncated_current_profile = current_profile[:n]

    def summary(
            self,
            current_profile: list[float],
            duration_profile: list[float],
            soc_reserve: float
    ) -> SummaryResult:
        self.simulate(current_profile, duration_profile)
        final_soc = self.soc_profile[-1]
        min_soc = min(self.soc_profile)
        max_power = max(self.power_profile, default=0.0)
        
        total_energy = sum(
            power * duration
            for power, duration in zip(self.power_profile, self.truncated_duration_profile)
            if power > 0
        )
        total_discharge = sum(
            current * duration
            for current, duration in zip(self.truncated_current_profile, self.truncated_duration_profile)
            if current > 0
        )

        meets_soc_reserve = min_soc >= soc_reserve

        return SummaryResult(
            final_soc=final_soc,
            min_soc=min_soc,
            max_power=max_power,
            total_energy=total_energy,
            total_discharge=total_discharge,
            meets_soc_reserve=meets_soc_reserve
        )

    def print_summary(
            self,
            current_profile: list[float],
            duration_profile: list[float],
            soc_reserve: float
    ) -> None:
        result = self.summary(current_profile, duration_profile, soc_reserve)
        print(f"The final SoC was {result.final_soc * 100:.2f} %.")
        print(f"The lowest SoC was {result.min_soc * 100:.2f} %.")
        print(f"The peak power draw was {result.max_power:.2f} W")
        print(f"Total energy usage was {result.total_energy / 3600:.2f} Wh")
        print(f"Total current discharge was {result.total_discharge / 3600:.2f} Ah")
        if result.meets_soc_reserve:
            print("The battery capacity was sufficient.")
        else:
            print("The battery capacity was not sufficient.")


    def plot_profiles(self):
        plot_current_profile(
            current_profile=self.truncated_current_profile,
            duration_profile=self.truncated_duration_profile
        )
        plot_soc_profile(
            soc_profile=self.soc_profile,
            duration_profile=self.truncated_duration_profile
        )
        plot_voltage_profile(
            voltage_profile=self.voltage_profile,
            duration_profile=self.truncated_duration_profile
        )
        plot_voltage_and_current_profile(
            self.voltage_profile,
            self.truncated_current_profile,
            self.truncated_duration_profile
        )
        plot_power_profile(
            power_profile=self.power_profile,
            duration_profile=self.truncated_duration_profile
        )


if __name__ == "__main__":
    load_current = [-1.5, 3.0, 11.0, 4.0, 1.0]
    load_durations = [300.0, 240.0, 90.0, 150.0, 120.0]
    batteries = [
        BatteryPack(capacity_nom_Ah=10, initial_soc=1, Vmin=32.0, Vmax=42.0),
        LiPoBatteryPack(capacity_nom_Ah=10, initial_soc=1),
        NMCBatteryPack(capacity_nom_Ah=10, initial_soc=1)
    ]

    for battery in batteries:
        print(battery)
        bat_sim = BatterySimulator(battery)
        bat_sim.print_summary(load_current, load_durations, 0.05)
        bat_sim.plot_profiles()
        input("Press Enter to continue...")