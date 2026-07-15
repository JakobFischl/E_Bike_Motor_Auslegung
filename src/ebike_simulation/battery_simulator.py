from ebike_simulation.battery_pack import BatteryPack
from ebike_simulation.lipo_battery import LiPoBatteryPack
from ebike_simulation.nmc_battery import NMCBatteryPack
import numpy as np
import matplotlib.pyplot as plt

from ebike_simulation.plotting_utils import (
    plot_current_profile,
    plot_voltage_profile,
    plot_voltage_and_current_profile,
    plot_soc_profile,
    plot_power_profile
)

from typing import NamedTuple

class SummaryResult(NamedTuple):
    """
    Summary of the results of a simulation run.
    final_soc: state of charge at the end of the profile.
    min_soc: lowest state of charge reached during the run.
    max_power: peak output power in watts.
    total_energy: discharged energy in joules (only positive power contributes).
    total_discharge: discharged charge in ampere-seconds (only positive current contributes).
    meets_soc_reserve: True if min_soc stayed at or above the requested state of charge reserve.
    """
    final_soc: float
    min_soc: float
    max_power: float
    total_energy: float
    total_discharge: float
    meets_soc_reserve: bool

import logging

# Set up local logger
logger = logging.getLogger(__name__)


class BatterySimulator:
    """Simple simulator for a battery pack. The simulator applies a current profile to the battery pack 
    and records voltage profile, state of charge over time and a power profile."""

    def __init__(self, battery_pack) -> None:
        """Wrap a battery pack and initialise empty result profiles."""
        self.battery_pack = battery_pack
        self.voltage_profile = []
        self.truncated_duration_profile = []
        self.truncated_current_profile = []
        self.soc_profile = []
        self.power_profile = []
        self.effective_current_profile = []
        self.has_run = False

    def simulate(self, current_profile: np.ndarray, duration_profile: np.ndarray) -> None:
        """
        Apply a current and duration profile to the battery pack and record the resulting profiles.
        current_profile: current per interval in amperes (positive = discharge, negative = charge).
        duration_profile: length of each interval in seconds, same length as current_profile.
        Stops early once the battery is empty.
        """

        if not isinstance(duration_profile, np.ndarray):
            raise TypeError("Duration profile has to be a numpy array.")
        if not isinstance(current_profile, np.ndarray):
            raise TypeError("Current profile has to be a numpy array.")
        if duration_profile.ndim != 1:
            raise ValueError("Expected duration profile must have one dimension.")
        if current_profile.ndim !=1:
            raise ValueError("Expected current profile must have one dimension.")
        if not np.isfinite(duration_profile).all():
            raise ValueError("Duration profile does not only contain numeric finite values.")
        if not np.isfinite(current_profile).all():
            raise ValueError("Current profile does not only contain numeric finite values.")
        if len(current_profile) != len(duration_profile):
            raise ValueError("Duration profile must have the same length as current profile.")
        if len(duration_profile) == 0:
            raise ValueError("Duration and current profiles cannot be empty.")
        if np.less(duration_profile, 0).any():
            raise ValueError("There can be no negative duration intervals.")
        if np.equal(duration_profile, 0).any():
            logger.warning("At least one duration between timestamps is zero seconds long.")


        # Start from a defined state and include the first value (initial SoC and initial voltage). Power profile starts empty.
        self.battery_pack.reset_soc()
        self.voltage_profile = [self.battery_pack.voltage()]
        self.soc_profile = [self.battery_pack.soc]
        self.power_profile = []
        self.effective_current_profile = []

        total_duration = 0.0

        for current, duration in zip(current_profile, duration_profile):

            if self.battery_pack.is_empty():
                logger.info(f"{self.battery_pack.name} Battery with {self.battery_pack.capacity_nom_As / 3600:.2f} Ah is empty after {total_duration / 60:.1f} minutes. Cannot discharge further.")
                break

            # A full battery cannot charge (negative current) further, so drop the effectively flowing current to zero.
            elif self.battery_pack.is_full() and current < 0:
                effective_current = 0.0
                logger.debug(f"Battery is full: Rejecting {current:.2f} A of regen.")
            else:
                effective_current = current

            v = self.battery_pack.voltage(effective_current)
            self.voltage_profile.append(v)
            soc = self.battery_pack.apply_current(effective_current, duration)
            self.soc_profile.append(soc)
            power = self.battery_pack.power(effective_current)
            self.power_profile.append(power)
            self.effective_current_profile.append(effective_current)
        
            total_duration += duration

        # If the loop broke early, trim the input profiles to the steps actually simulated.
        n = len(self.power_profile)
        self.truncated_duration_profile = duration_profile[:n]
        self.truncated_current_profile = self.effective_current_profile[:n]
        self.has_run = True

    def summary(
            self,
            current_profile: np.ndarray,
            duration_profile: np.ndarray,
            soc_reserve: float
    ) -> SummaryResult:
        """
        Run the simulation and return its results into a SummaryResult.
        soc_reserve: minimum acceptable state of charge between zero and one used for the reserve check.
        """

        if soc_reserve < 0 or soc_reserve > 1.0:
            raise ValueError("The state of charge reserve has to be between 0 and 1.")

        self.simulate(current_profile, duration_profile)
        final_soc = self.soc_profile[-1]
        min_soc = np.min(self.soc_profile)
        max_power = np.max(self.power_profile, initial=0.0)

        # Sum only positive power and current so charging intervals are excluded.
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
        if not meets_soc_reserve:
            logger.debug("Battery capacity is not sufficient.")

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
            current_profile: np.ndarray,
            duration_profile: np.ndarray,
            soc_reserve: float
    ) -> None:
        """Run the simulation and print a summary (SoC in %, energy in Wh, charge in Ah)."""
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


    def plot_profiles(self) -> list[tuple]:
        """
        Plot the recorded current, SoC, voltage and power profiles of the last run.
        Returns a list of (figure, caption) pairs, empty when there is nothing to plot.
        """

        # Empty profiles mean either the simulation never ran or it started with empty lists.
        if len(self.truncated_current_profile) == 0:
            if not self.has_run:
                raise RuntimeError("Lists are empty. Run simulation first.")
            logger.warning("Initial state of charge was 0%.")
            return []

        current_figure = plot_current_profile(
            current_profile=self.truncated_current_profile,
            duration_profile=self.truncated_duration_profile
        )
        soc_figure = plot_soc_profile(
            soc_profile=self.soc_profile,
            duration_profile=self.truncated_duration_profile
        )
        voltage_figure = plot_voltage_profile(
            voltage_profile=self.voltage_profile,
            duration_profile=self.truncated_duration_profile
        )
        voltage_and_current_figure = plot_voltage_and_current_profile(
            self.voltage_profile,
            self.truncated_current_profile,
            self.truncated_duration_profile
        )
        power_figure = plot_power_profile(
            power_profile=self.power_profile,
            duration_profile=self.truncated_duration_profile
        )

        return [
            (current_figure, "Current over time"),
            (soc_figure, "State of charge over time"),
            (voltage_figure, "Voltage over time"),
            (voltage_and_current_figure, "Voltage and current over time"),
            (power_figure, "Power over time")
        ]


if __name__ == "__main__":
    load_current = np.array([-1.5, 3.0, 11.0, 4.0, 1.0])
    load_durations = np.array([300.0, 240.0, 90.0, 150.0, 120.0])
    print(type(load_current))
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
        plt.show(block=False)
        input("Press Enter to continue...")