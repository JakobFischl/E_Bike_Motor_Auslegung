import numpy as np
import logging

from typing import NamedTuple

# Set up local logger
logger = logging.getLogger(__name__)


class RideMetrics(NamedTuple):
    """
    Aggregate figures describing a whole ride.
    total_distance_m: total distance travelled in meters.
    total_time_s: total elapsed time in seconds.
    average_speed_m_s: average speed over the ride (total distance divided by total time) in meters per second.
    elevation_gain_m: sum of all uphill elevation changes in meters.
    elevation_loss_m: sum of all downhill elevation changes as a positive value in meters.
    max_power_W: peak mechanical power in watts.
    """
    total_distance_m: float
    total_time_s: float
    average_speed_m_s: float
    elevation_gain_m: float
    elevation_loss_m: float
    max_power_W: float


def compute_ride_metrics(
        distance_profile: np.ndarray,
        duration_profile: np.ndarray,
        elevation_profile: np.ndarray,
        power_profile: np.ndarray) -> RideMetrics:
    """
    Compute the aggregate metrics for a whole ride and return them in a RideMetrics.
    distance_profile: distance travelled per interval in meters.
    duration_profile: length of each interval in seconds, same length as distance_profile.
    elevation_profile: altitude above sea level at each timestamp in meters.
    power_profile: mechanical power at each timestamp in watts.
    """

    profiles = (distance_profile, duration_profile, elevation_profile, power_profile)
    if not all(isinstance(profile, np.ndarray) for profile in profiles):
        raise TypeError("All profiles have to be numpy arrays.")
    if not all(profile.ndim == 1 for profile in profiles):
        raise ValueError("All profiles must have one dimension.")
    if not all(np.isfinite(profile).all() for profile in profiles):
        raise ValueError("The profiles must only contain numeric finite values.")
    if len({len(profile) for profile in profiles}) != 1:
        raise ValueError("All profiles must have the same length.")
    if len(distance_profile) == 0:
        raise ValueError("The profiles cannot be empty.")

    total_distance_m = float(np.sum(distance_profile))
    total_time_s = float(np.sum(duration_profile))

    if total_time_s <= 0:
        raise ValueError("The total time has to be positive to determine an average speed.")
    average_speed_m_s = total_distance_m / total_time_s

    # Split the elevation changes between consecutive points into climbs and descents.
    delta_elevation = np.diff(elevation_profile)
    elevation_gain_m = float(np.sum(delta_elevation[delta_elevation > 0]))
    elevation_loss_m = float(-np.sum(delta_elevation[delta_elevation < 0]))

    max_power_W = float(np.max(power_profile))

    logger.debug(f"Computed ride metrics over {total_distance_m / 1000:.2f} km.")

    return RideMetrics(
        total_distance_m=total_distance_m,
        total_time_s=total_time_s,
        average_speed_m_s=average_speed_m_s,
        elevation_gain_m=elevation_gain_m,
        elevation_loss_m=elevation_loss_m,
        max_power_W=max_power_W
    )


def print_ride_metrics(metrics: RideMetrics) -> None:
    """Print the ride metrics (distance in km, time in minutes, speed in km/h)."""
    print(f"Total distance travelled was {metrics.total_distance_m / 1000:.2f} km.")
    print(f"Total time needed was {metrics.total_time_s / 60:.1f} minutes.")
    print(f"The average speed was {metrics.average_speed_m_s * 3.6:.2f} km/h.")
    print(f"Total elevation gain was {metrics.elevation_gain_m:.1f} m.")
    print(f"Total elevation loss was {metrics.elevation_loss_m:.1f} m.")
    print(f"The peak mechanical power was {metrics.max_power_W:.2f} W.")


if __name__ == "__main__":

    distance_profile = np.array([0.0, 12.5, 20.0, 18.0, 9.5])
    duration_profile = np.array([0.0, 2.5, 2.0, 2.0, 1.5])
    elevation_profile = np.array([494.0, 496.0, 495.0, 500.0, 498.0])
    power_profile = np.array([0.0, 220.0, 540.0, 130.0, 80.0])

    metrics = compute_ride_metrics(
        distance_profile,
        duration_profile,
        elevation_profile,
        power_profile
    )
    print_ride_metrics(metrics)
