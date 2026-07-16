from route_dynamics.route import RouteAnalysis
from route_dynamics.dynamics import EBikeDynamics
from route_dynamics.ride_metrics import compute_ride_metrics
from route_dynamics.route_plotting import (
    plot_hoehenprofil,
    plot_geschwindigkeit,
    plot_motorleistung
)
from ebike_simulation.battery_simulator import BatterySimulator
from ebike_simulation.battery_sizer import determine_capacity
from ebike_simulation.lipo_battery import LiPoBatteryPack
from ebike_simulation.nmc_battery import NMCBatteryPack
from ebike_app.parameters import prompt_parameters
from ebike_app.report import build_report
import numpy as np
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

    parameters = prompt_parameters()

    route = RouteAnalysis(parameters.data_file_path)
    route.geschwindigkeit()
    route.beschleunigung()
    route.steigung()

    dynamics = EBikeDynamics(
        route.daten,
        m_fahrer=parameters.rider_mass_kg,
        m_fahrrad=parameters.bike_mass_kg,
        cw_A=parameters.cwA_m2,
        rad_durchmesser_zoll=parameters.wheel_diameter_inch,
        motor_konstante=parameters.motor_constant_Nm_A
    )
    dynamics.kraefte()
    duration_profile, current_profile = dynamics.motor_werte()

    data = dynamics.daten

    metrics = compute_ride_metrics(
        data['delta_s_meter'].to_numpy(),
        data['delta_t_sekunden'].to_numpy(),
        data['ele'].to_numpy(),
        data['leistung_W'].to_numpy()
    )

    distance_km = np.cumsum(data['delta_s_meter'].to_numpy()) / 1000
    time_min = np.cumsum(data['delta_t_sekunden'].to_numpy()) / 60

    figures = [
        (plot_hoehenprofil(distance_km, data['ele'].to_numpy()), "Elevation profile"),
        (plot_geschwindigkeit(time_min, data['geschwindigkeit_km_h'].to_numpy()), "Speed over time"),
        (plot_motorleistung(time_min, data['leistung_W'].to_numpy()), "Motor power over time")
    ]

    battery_results = []

    for battery_class in (LiPoBatteryPack, NMCBatteryPack):
        capacity_Ah = determine_capacity(
            battery_class,
            current_profile=current_profile,
            duration_profile=duration_profile,
            soc_reserve=parameters.soc_reserve,
            initial_soc=parameters.initial_soc,
            capacity_resolution_Ah=parameters.capacity_resolution_Ah,
            initial_test_capacity=parameters.initial_test_capacity
        )
        battery = battery_class(capacity_nom_Ah=capacity_Ah, initial_soc=parameters.initial_soc)
        simulator = BatterySimulator(battery)
        result = simulator.summary(current_profile, duration_profile, parameters.soc_reserve)
        battery_results.append((battery.name, capacity_Ah, result))

        for figure, caption in simulator.plot_profiles():
            figures.append((figure, f"{battery.name}: {caption}"))

    report_path = build_report(parameters, metrics, battery_results, figures, output_folder)
    print(f"The result is visible in a pdf report that was written to '{report_path}'.")
