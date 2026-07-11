from battery_simulator import BatterySimulator
from battery_pack import BatteryPack
import math
import numpy as np


def determine_capacity(battery_class: type[BatteryPack], current_profile: np.ndarray, duration_profile: np.ndarray, soc_reserve: float, initial_test_capacity: float = 0.01, initial_soc: float = 1.0) -> float:

    def get_min_soc(capacity):
        battery = battery_class(initial_soc=initial_soc, capacity_nom_Ah=capacity)
        bat_sim = BatterySimulator(battery)
        bat_sim.simulate(current_profile, duration_profile)  
        min_soc = min(bat_sim.soc_profile)
        return min_soc


    trial_capacity_Ah_high = initial_test_capacity
    trial_capacity_Ah_low = trial_capacity_Ah_high / 2
    min_soc_high = get_min_soc(trial_capacity_Ah_high)
    min_soc_low = get_min_soc(trial_capacity_Ah_low)

    while min_soc_low > soc_reserve:
        trial_capacity_Ah_low = trial_capacity_Ah_low / 2
        min_soc_low = get_min_soc(trial_capacity_Ah_low)

    while min_soc_high < soc_reserve:
        trial_capacity_Ah_high = trial_capacity_Ah_high * 2
        min_soc_high = get_min_soc(trial_capacity_Ah_high)
    
    low = trial_capacity_Ah_low
    high = trial_capacity_Ah_high
    while True:
        mid = (low + high) / 2

        min_soc = get_min_soc(mid)

        if min_soc >= soc_reserve:
            if (high - low) <= 0.5:
                return math.ceil(mid*10) / 10
            else:
                high = mid
        else:
            low = mid

if __name__ == "__main__":
    
    load_current = np.array([15.5, 12.0, 13.0, 14.0, 10.0])
    load_durations = np.array([800.0, 240.0, 90.0, 150.0, 120.0])

    sufficient_capacity = determine_capacity(BatteryPack, current_profile=load_current, duration_profile=load_durations, soc_reserve=0.05)
    print(f"Battery has to have at least {sufficient_capacity} Ah.")
