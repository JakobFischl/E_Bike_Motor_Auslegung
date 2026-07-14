from route_dynamics.route import RouteAnalysis
from route_dynamics.dynamics import EBikeDynamics
from route_dynamics.route_plotting import (
    plot_hoehenprofil,
    plot_geschwindigkeit,
    plot_motorleistung
)
from route_dynamics.ride_metrics import compute_ride_metrics, print_ride_metrics
from ebike_simulation.battery_simulator import BatterySimulator
from ebike_simulation.battery_sizer import determine_capacity
from ebike_simulation.lipo_battery import LiPoBatteryPack
from ebike_simulation.nmc_battery import NMCBatteryPack
import numpy as np
import matplotlib.pyplot as plt
import logging

# Set up local logger
logger = logging.getLogger(__name__)


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    dateipfad = "simulation_data/final_project_input_data.csv"
    soc_reserve = 0.05

    route = RouteAnalysis(dateipfad)
    route.geschwindigkeit()
    route.beschleunigung()
    route.steigung()

    dynamics = EBikeDynamics(route.daten)
    dynamics.kraefte()
    duration_profile, current_profile = dynamics.motor_werte()

    daten = dynamics.daten
