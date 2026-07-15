from dataclasses import dataclass
import sys
import logging

from pathlib import Path

# Set up local logger
logger = logging.getLogger(__name__)


@dataclass
class RideParameters:
    """
    Class to keep track of all input parameters
    to make interaction with the user easier.
    """
    rider_mass_kg: float | int = 70
    bike_mass_kg: float | int = 10
    cwA_m2: float = 0.5625 # c_w * A
    wheel_diameter_inch: int = 27
    motor_constant_Nm_A: float | int = 1.5 # N * m / A
    soc_reserve: float = 0.05
    initial_soc: float | int = 1
    data_file_path: str = "simulation_data/final_project_input_data.csv"
    gravity_acceleration_m_s2: float = 9.81 # m / s^2
    min_dt_sekunden: float | int = 1
    capacity_resolution_Ah: float = 0.1
    initial_test_capacity: float = 0.01
    earth_radius_m: int = 6371000
