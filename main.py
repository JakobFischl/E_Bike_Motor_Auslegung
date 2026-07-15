from route_dynamics.route import RouteAnalysis
from route_dynamics.dynamics import EBikeDynamics
from route_dynamics.ride_metrics import compute_ride_metrics, print_ride_metrics
from route_dynamics.route_plotting import (
    plot_hoehenprofil,
    plot_geschwindigkeit,
    plot_motorleistung
)
from ebike_simulation.battery_simulator import BatterySimulator
from ebike_simulation.battery_sizer import determine_capacity
from ebike_simulation.lipo_battery import LiPoBatteryPack
from ebike_simulation.nmc_battery import NMCBatteryPack
import numpy as np
import matplotlib.pyplot as plt
import logging

from pathlib import Path

# Set up local logger
logger = logging.getLogger(__name__)


if __name__ == "__main__":

    output_folder = Path("output")
    output_folder.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(name)s:%(message)s",
        filename=output_folder / "simulation.log",
        filemode="w"
    )

    file_path = "simulation_data/final_project_input_data.csv"
    soc_reserve = 0.05

    route = RouteAnalysis(file_path)
    route.geschwindigkeit()
    route.beschleunigung()
    route.steigung()

    dynamics = EBikeDynamics(route.daten)
    dynamics.kraefte()
    duration_profile, current_profile = dynamics.motor_werte()

    data = dynamics.daten

    metrics = compute_ride_metrics(
        data['delta_s_meter'].to_numpy(),
        data['delta_t_sekunden'].to_numpy(),
        data['ele'].to_numpy(),
        data['leistung_W'].to_numpy()
    )
    print_ride_metrics(metrics)

    distance_km = np.cumsum(data['delta_s_meter'].to_numpy()) / 1000
    time_min = np.cumsum(data['delta_t_sekunden'].to_numpy()) / 60

    plot_hoehenprofil(distance_km, data['ele'].to_numpy())
    plot_geschwindigkeit(time_min, data['geschwindigkeit_km_h'].to_numpy())
    plot_motorleistung(time_min, data['leistung_W'].to_numpy())

    for battery_class in (LiPoBatteryPack, NMCBatteryPack):
        capacity_Ah = determine_capacity(
            battery_class,
            current_profile=current_profile,
            duration_profile=duration_profile,
            soc_reserve=soc_reserve
        )
        battery = battery_class(capacity_nom_Ah=capacity_Ah, initial_soc=1.0)
        print(f"{battery.name} pack needs at least {capacity_Ah:.1f} Ah:")
        simulator = BatterySimulator(battery)
        simulator.print_summary(current_profile, duration_profile, soc_reserve)
        simulator.plot_profiles()
        plt.show()
