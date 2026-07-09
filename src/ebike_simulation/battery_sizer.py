from battery_simulator import BatterySimulator
from nmc_battery import NMCBatteryPack
from lipo_battery import LiPoBatteryPack
import math


def determine_capacity(battery_class, current_profile: list[float], duration_profile: list[float], soc_reserve: float, initial_soc: float = 1.0) -> float:

    trial_capacity_Ah = 0.1
    battery = battery_class(initial_soc=initial_soc, capacity_nom_Ah=trial_capacity_Ah)
    bat_sim = BatterySimulator(battery)
    bat_sim.simulate(current_profile, duration_profile)  
    min_soc = min(bat_sim.soc_profile)

    if min_soc >= soc_reserve:
        c_sufficient = True
    else:
        c_sufficient = False

    while c_sufficient is not True:
        trial_capacity_Ah = trial_capacity_Ah * 2
        battery = battery_class(initial_soc=initial_soc, capacity_nom_Ah=trial_capacity_Ah)
        bat_sim = BatterySimulator(battery)
        bat_sim.simulate(current_profile, duration_profile)  
        min_soc = min(bat_sim.soc_profile)
        if min_soc >= soc_reserve:
            c_sufficient = True
        else:
            c_sufficient = False
    else:
        low = trial_capacity_Ah / 2
        high = trial_capacity_Ah
        while low <= high:
            mid = (low + high) / 2

            battery = battery_class(initial_soc=initial_soc, capacity_nom_Ah=mid)
            bat_sim = BatterySimulator(battery)
            bat_sim.simulate(current_profile, duration_profile)  
            min_soc = min(bat_sim.soc_profile)
        
            if min_soc >= soc_reserve and (high - low) <= 0.5:
                sufficient_capacity = math.ceil(mid)
                return sufficient_capacity
            elif min_soc >= soc_reserve and (high - low) > 0.5:
                high = mid
            else:
                low = mid



load_current = [15.5, 12.0, 13.0, 14.0, 10.0]
load_durations = [800.0, 240.0, 90.0, 150.0, 120.0]

sufficient_capacity = determine_capacity(NMCBatteryPack, current_profile=load_current, duration_profile=load_durations, soc_reserve=0.05)
print(f"Battery has to have at least {sufficient_capacity} Ah")