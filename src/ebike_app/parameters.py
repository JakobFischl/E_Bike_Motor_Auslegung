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


def ask_float(
        prompt: str,
        default: float,
        minimum: float | None = None,
        maximum: float | None = None) -> float:
    """
    Ask the user for a number and return it.
    prompt: question shown to the user, the default value is appended in brackets.
    default: value returned when the user presses enter without typing anything.
    minimum, maximum: inclusive bounds the answer has to lie within.
    Repeats the question until the answer is a number within the bounds.
    """

    while True:
        try:
            answer = input(f"{prompt} [{default}]: ").strip()
        except EOFError:
            # Nothing left to read, e.g. when the input is redirected from an empty file.
            print()
            logger.info(f"No input available, using the default value {default}.")
            return default

        if not answer:
            return default

        try:
            value = float(answer)
        except ValueError:
            print(f"'{answer}' is not a number, please try again.")
            continue

        if minimum is not None and value < minimum:
            print(f"The value has to be at least {minimum}, please try again.")
            continue
        if maximum is not None and value > maximum:
            print(f"The value has to be at most {maximum}, please try again.")
            continue

        return value


def ask_file_path(prompt: str, default: str) -> str:
    """
    Ask the user for the path to the data file and return it.
    Repeats the question until the path points to an existing file.
    """

    while True:
        try:
            answer = input(f"{prompt} [{default}]: ").strip()
        except EOFError:
            # Nothing left to read, e.g. when the input is redirected from an empty file.
            print()
            logger.info(f"No input available, using the default path '{default}'.")
            return default

        path = answer if answer else default
        if Path(path).is_file():
            return path
        print(f"'{path}' is not an existing file, please try again.")


def prompt_parameters() -> RideParameters:
    """
    Ask the user for the ride parameters and return them in a RideParameters.
    Returns the default parameters without asking when no interactive terminal is available.
    """

    defaults = RideParameters()

    # Prompts would block forever when the input is piped in or redirected.
    if not sys.stdin.isatty():
        logger.info("No interactive terminal available, using the default parameters.")
        return defaults

    print("Press enter to accept the default value in brackets.\n")

    parameters = RideParameters(
        data_file_path=ask_file_path("Path to the GPS data file", defaults.data_file_path),
        rider_mass_kg=ask_float("Mass of the rider in kg", defaults.rider_mass_kg, minimum=1),
        bike_mass_kg=ask_float("Mass of the bike in kg", defaults.bike_mass_kg, minimum=1),
        cwA_m2=ask_float("Drag coefficient times frontal area in m^2", defaults.cwA_m2, minimum=0.01),
        wheel_diameter_inch=ask_float("Wheel diameter in inch", defaults.wheel_diameter_inch, minimum=1),
        motor_constant_Nm_A=ask_float("Motor constant in Nm/A", defaults.motor_constant_Nm_A, minimum=0.01),
        soc_reserve=ask_float("State of charge reserve", defaults.soc_reserve, minimum=0.01, maximum=0.99)
    )

    print()
    logger.info(f"The user chose {parameters}.")
    return parameters


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    print(prompt_parameters())
