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
        
        self.voltage_profile = [self.battery_pack.voltage()]
        self.soc_profile = [self.battery_pack.soc]
        self.power_profile = []

        for i, (current, duration) in enumerate(zip(current_profile, duration_profile)):
            
            if self.battery_pack.is_empty():
                print("Battery is empty: cannot discharge further!")
                self.truncated_duration_profile = duration_profile[:i]
                self.truncated_current_profile = current_profile[:i]
                break
                
            elif self.battery_pack.is_full() and current < 0:
                v = self.battery_pack.voltage()
                soc = self.battery_pack.soc
                # print(f"Battery is full: {power:.2f} W must be dissipated!") supposed to be logging later
            else:
                v = self.battery_pack.voltage(current)
                soc = self.battery_pack.apply_current(current, duration)

            self.voltage_profile.append(v)
 
            self.soc_profile.append(soc)

            power = self.battery_pack.power(current)
            self.power_profile.append(power)
        else:    
            self.truncated_duration_profile = duration_profile
            self.truncated_current_profile = current_profile

    def summary(self, current_profile: list[float], duration_profile: list[float], soc_reserve: float) -> tuple:
        self.simulate(current_profile, duration_profile)
        final_soc = self.soc_profile[-1]
        min_soc = min(self.soc_profile)
        if len(self.power_profile) == 0:
            #print("Battery is empty at start.") supposed to be logging
            max_power = 0.0
        else:
            max_power = max(self.power_profile)
            #print(f"max power = {max_power:.2f} W")
        total_energy = 0.0
        for p, d in zip(self.power_profile, self.truncated_duration_profile):
            if p < 0:
                continue
            else:
                delta_energy = p * d
                total_energy = total_energy + delta_energy
        #print(f"Total energy usage = {total_energy:.2f} Ws")
        total_discharge = 0.0
        for i, d in zip(self.truncated_current_profile, self.truncated_duration_profile):
            if i < 0:
                continue
            else:
                delta_discharge = i * d
                total_discharge = total_discharge + delta_discharge
        #print(f"Total current discharge = {total_discharge:.2f} As")
        if min_soc >= soc_reserve:
            c_sufficient = True
            #print(f"Battery capacity was sufficient. The lowest SoC was {min_soc:.2f}. The final SoC was {final_soc:.2f}.")
        else:
            c_sufficient = False
            #print("Battery capacity was not sufficient.")

        return final_soc, min_soc, max_power, total_energy, total_discharge, c_sufficient

    def print_summary(self, current_profile: list[float], duration_profile: list[float], soc_reserve) -> None:
        final_soc, min_soc, max_power, total_energy, total_discharge, c_sufficient = self.summary(current_profile, duration_profile, soc_reserve)
        print(f"The final SoC was {final_soc * 100:.2f} %.")
        print(f"The lowest SoC was {min_soc * 100:.2f} %.")
        print(f"The peak power draw was {max_power:.2f} W")
        print(f"Total energy usage was {total_energy / 3600:.2f} Wh")
        print(f"Total current discharge was {total_discharge / 3600:.2f} Ah")
        if c_sufficient == True:
            print(f"The battery capacity was sufficient.")
        else:
            print(f"The battery capacity was not sufficient.")



        



if __name__ == "__main__":
    load_current = [-1.5, 3.0, 11.0, 4.0, 1.0]
    load_durations = [300.0, 240.0, 90.0, 150.0, 120.0]

    battery = BatteryPack(capacity_nom_Ah=10, initial_soc=1, Vmin=32.0, Vmax=42.0)
    print(battery)
    bat_sim = BatterySimulator(battery)
    bat_sim.summary(load_current, load_durations, 0.05)
    bat_sim.print_summary(load_current, load_durations, 0.05)
    bat_sim.simulate(load_current, load_durations)
    print(battery)

    plot_current_profile(current_profile=bat_sim.truncated_current_profile, duration_profile=bat_sim.truncated_duration_profile)
    plot_soc_profile(soc_profile=bat_sim.soc_profile, duration_profile=bat_sim.truncated_duration_profile)
    plot_voltage_profile(voltage_profile=bat_sim.voltage_profile, duration_profile=bat_sim.truncated_duration_profile)
    plot_voltage_and_current_profile(bat_sim.voltage_profile, bat_sim.truncated_current_profile, bat_sim.truncated_duration_profile)
    plot_power_profile(power_profile=bat_sim.power_profile, duration_profile=bat_sim.truncated_duration_profile)

    input("Press Enter to continue...")

    battery = LiPoBatteryPack(capacity_nom_Ah=10, initial_soc=1)
    print(battery)
    bat_sim = BatterySimulator(battery)
    bat_sim.summary(load_current, load_durations, 0.05)
    bat_sim.simulate(load_current, load_durations)
    print(battery)

    plot_current_profile(current_profile=bat_sim.truncated_current_profile, duration_profile=bat_sim.truncated_duration_profile)
    plot_soc_profile(soc_profile=bat_sim.soc_profile, duration_profile=bat_sim.truncated_duration_profile)
    plot_voltage_profile(voltage_profile=bat_sim.voltage_profile, duration_profile=bat_sim.truncated_duration_profile)
    plot_voltage_and_current_profile(bat_sim.voltage_profile, bat_sim.truncated_current_profile, bat_sim.truncated_duration_profile)
    plot_power_profile(power_profile=bat_sim.power_profile, duration_profile=bat_sim.truncated_duration_profile)

    input("Press Enter to continue...")

    battery = NMCBatteryPack(capacity_nom_Ah=10, initial_soc=1)
    print(battery)
    bat_sim = BatterySimulator(battery)
    bat_sim.summary(load_current, load_durations, 0.05)
    bat_sim.simulate(load_current, load_durations)
    print(battery)

    plot_current_profile(current_profile=bat_sim.truncated_current_profile, duration_profile=bat_sim.truncated_duration_profile)
    plot_soc_profile(soc_profile=bat_sim.soc_profile, duration_profile=bat_sim.truncated_duration_profile)
    plot_voltage_profile(voltage_profile=bat_sim.voltage_profile, duration_profile=bat_sim.truncated_duration_profile)
    plot_voltage_and_current_profile(bat_sim.voltage_profile, bat_sim.truncated_current_profile, bat_sim.truncated_duration_profile)
    plot_power_profile(power_profile=bat_sim.power_profile, duration_profile=bat_sim.truncated_duration_profile)

    input("Press Enter to continue...")