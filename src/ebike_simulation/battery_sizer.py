from battery_simulator import BatterySimulator
from battery_pack import BatteryPack
import math
import numpy as np
import logging

# Set up local logger
logger = logging.getLogger(__name__)


def determine_capacity(
        battery_class: type[BatteryPack],
        current_profile: np.ndarray,
        duration_profile: np.ndarray,
        soc_reserve: float = 0.05,
        initial_test_capacity: float = 0.01,
        initial_soc: float = 1.0,
        capacity_resolution_Ah: float = 0.1,
        max_iterations: int = 100) -> float:
    """
    Find the smallest battery capacity (in Ah) that keeps the SoC at or above the reserve for the given profile.
    battery_class: BatteryPack subclass to use for each trial.
    current_profile: current per interval in amperes (positive = discharge).
    duration_profile: length of each interval in seconds, same length as current_profile.
    soc_reserve: minimum acceptable state of charge between zero and one.
    initial_test_capacity: starting capacity in Ah for the bracketing search.
    initial_soc: state of charge each trial battery starts from between zero and one.

    Returns the required capacity in Ah, rounded up to the next capacity_resolution_Ah step.
    """

    if not np.greater(current_profile, 0).any():
       raise ValueError("No positive current in the profile, therefore no battery is needed to complete the course.")
    if soc_reserve >= 1.0 or soc_reserve <= 0:
        raise ValueError("SoC Reserve has to be larger than 0 and less than 1.")
    if not issubclass(battery_class, BatteryPack):
        raise TypeError("The battery pack has to have the class type 'BatteryPack'")


    def get_min_soc(capacity):
        """Simulate the profile on a fresh battery of the given capacity (Ah) and return the lowest SoC reached."""
        logger.debug(f"Testing {capacity} Ah.")
        battery = battery_class(initial_soc=initial_soc, capacity_nom_Ah=capacity)
        bat_sim = BatterySimulator(battery)
        bat_sim.simulate(current_profile, duration_profile)  
        min_soc = min(bat_sim.soc_profile)
        logger.debug(f"Minimum state of charge is {min_soc}")
        return min_soc


    # Find a window with a low capacity that is insufficient and a high capacity that is sufficient.
    trial_capacity_Ah_high = initial_test_capacity
    trial_capacity_Ah_low = trial_capacity_Ah_high / 2
    min_soc_high = get_min_soc(trial_capacity_Ah_high)
    min_soc_low = get_min_soc(trial_capacity_Ah_low)

    # Shrink the low capacity until it is actually insufficient (below the reserve).
    while min_soc_low > soc_reserve:
        trial_capacity_Ah_low = trial_capacity_Ah_low / 2
        min_soc_low = get_min_soc(trial_capacity_Ah_low)

    # Grow the high capacity until it is sufficient (at or above the reserve).
    while min_soc_high < soc_reserve:
        trial_capacity_Ah_low = trial_capacity_Ah_high
        trial_capacity_Ah_high = trial_capacity_Ah_high * 2
        min_soc_high = get_min_soc(trial_capacity_Ah_high)

    low = trial_capacity_Ah_low
    high = trial_capacity_Ah_high

    iteration_count = 0

    # Narrow the window until it is smaller than 0.5 Ah.
    while True:
        iteration_count += 1
        mid = (low + high) / 2

        min_soc = get_min_soc(mid)

        if min_soc >= soc_reserve:
            # Once a sufficient capacity is found within a narrow window, round up to the next 0.1 Ah.
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
