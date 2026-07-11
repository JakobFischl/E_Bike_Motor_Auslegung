from battery_simulator import BatterySimulator
from battery_pack import BatteryPack
import math
import numpy as np
import logging

# Set up local logger
logger = logging.getLogger(__name__)


def determine_capacity(battery_class: type[BatteryPack], current_profile: np.ndarray, duration_profile: np.ndarray, soc_reserve: float, initial_test_capacity: float = 0.01, initial_soc: float = 1.0) -> float:

    if not np.greater(current_profile, 0).any():
       raise ValueError("No positive current in the profile, therefore no battery is needed to complete the course.")
    if soc_reserve >= 1.0 or soc_reserve <= 0:
        raise ValueError("SoC Reserve has to be larger than 0 and less than 1.")
    if not issubclass(battery_class, BatteryPack):
        raise TypeError("The battery pack has to have the class type 'BatteryPack'")


    def get_min_soc(capacity):
        logger.debug(f"Testing {capacity} Ah.")
        battery = battery_class(initial_soc=initial_soc, capacity_nom_Ah=capacity)
        bat_sim = BatterySimulator(battery)
        bat_sim.simulate(current_profile, duration_profile)  
        min_soc = min(bat_sim.soc_profile)
        logger.debug(f"Minimum state of charge is {min_soc}")
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

    iteration_count = 0

    while True:
        iteration_count += 1
        mid = (low + high) / 2

        min_soc = get_min_soc(mid)

        if min_soc >= soc_reserve:
            if (high - low) <= 0.5:
                final_capacity = math.ceil(mid*10) / 10
                logger.debug(f"Battery sufficient with {final_capacity} Ah. Found after {iteration_count} iterations.")
                return final_capacity
            else:
                high = mid
        else:
            low = mid

if __name__ == "__main__":
    
    load_current = np.array([15.5, 12.0, 13.0, 14.0, 10.0])
    load_durations = np.array([800.0, 240.0, 90.0, 150.0, 120.0])

    sufficient_capacity = determine_capacity(BatteryPack, current_profile=load_current, duration_profile=load_durations, soc_reserve=0.05)
    print(f"Battery has to have at least {sufficient_capacity} Ah.")
