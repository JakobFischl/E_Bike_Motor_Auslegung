import logging
import matplotlib.pyplot as plt
import numpy as np

# Set up local logger
logger = logging.getLogger(__name__)

def plot_current_profile(current_profile: list[float], duration_profile: list[float]):
    """Plots the current over time profile starting from t=0s."""
    
    # Error Handling & Logging
    if len(current_profile) != len(duration_profile):
        raise ValueError("Current and duration profiles must have the same length.")
    elif len(duration_profile) == 0:
        raise ValueError("The duration profile must have at least one value.")
    elif any(x == 0 for x in duration_profile):
        logger.warning("At least one duration between timestamps is zero seconds long.")
    
    logger.debug("Generating current profile plot...")
    
    edges = np.concatenate(([0.0], np.cumsum(duration_profile)))

    fig, ax = plt.subplots()
    ax.stairs(current_profile, edges, linewidth=1.5, zorder=2.5)
    ax.set_xlabel("Time $t$ / s")
    ax.set_ylabel("Current $I$ / A")
    ax.grid(True)
    fig.show()

    logger.debug("Current profile plot generated successfully.")
    return fig

def plot_power_profile(power_profile: list[float], duration_profile: list[float]):
    """Plots the power over time profile starting from t=0s."""

    # Error Handling & Logging
    if len(power_profile) != len(duration_profile):
        raise ValueError("Power and duration profiles must have the same length.")
    elif len(duration_profile) == 0:
        raise ValueError("The duration profile must have at least one value.")
    elif any(x == 0 for x in duration_profile):
        logger.warning("At least one duration between timestamps is zero seconds long.")
    
    logger.debug("Generating power profile plot...")

    edges = np.concatenate(([0.0], np.cumsum(duration_profile)))

    fig, ax = plt.subplots()
    ax.stairs(power_profile, edges, linewidth=1.5, zorder=2.5)
    ax.set_xlabel("Time $t$ / s")
    ax.set_ylabel("Power $P$ / W")
    ax.grid(True)
    fig.show()
    
    logger.debug("Power profile plot generated successfully.")
    return fig


def plot_voltage_profile(voltage_profile: list[float], duration_profile: list[float]):
    """Plots the voltage over time profile starting from t=0s."""

    # Error Handling & Logging
    if len(voltage_profile) - 1 != len(duration_profile):
        raise ValueError("Voltage profile must be longer by 1 than duration profile.")
    elif len(duration_profile) == 0:
        raise ValueError("The duration profile must have at least one value.")
    elif any(x == 0 for x in duration_profile):
        logger.warning("At least one duration between timestamps is zero seconds long.")
    
    logger.debug("Generating voltage profile plot...")

    edges = np.concatenate(([0.0], np.cumsum(duration_profile)))

    fig, ax = plt.subplots()
    ax.stairs(voltage_profile[1:], edges, linewidth=1.5, zorder=2.5, baseline=None)
    ax.set_xlabel("Time $t$ / s")
    ax.set_ylabel("Voltage $U$ / V")
    ax.grid(True)
    fig.show()
    
    logger.debug("Voltage profile plot generated successfully.")
    return fig

def plot_voltage_and_current_profile(voltage_profile: list[float], current_profile: list[float], duration_profile: list[float]):
    """Plots the voltage and current over time profiles starting from t=0s."""

    # Error Handling & Logging
    if not (len(voltage_profile) - 1 == len(current_profile) == len(duration_profile)):
        raise ValueError("Current and duration profiles must have the same length, and voltage profile must be longer by 1.")
    elif len(duration_profile) == 0:
        raise ValueError("The duration profile must have at least one value.")
    elif any(x == 0 for x in duration_profile):
        logger.warning("At least one duration between timestamps is zero seconds long.")
    
    logger.debug("Generating combined voltage and current profile plot...")

    edges = np.concatenate(([0.0], np.cumsum(duration_profile)))

    fig, axV = plt.subplots(figsize=(9, 4.5))
    axI = axV.twinx()

    axV.stairs(voltage_profile[1:], edges, baseline=None, linewidth=1.5, zorder=2.5, color="b", linestyle="-", label="Voltage U / V")
    axI.stairs(current_profile, edges, baseline=None, linewidth=1.5, zorder=2.5, color="r", linestyle="--", label="Current I / A")
    axV.set_xlabel("Time $t$ / s")
    axV.set_ylabel("Voltage $U$ / V", color="b")
    axI.set_ylabel("Current $I$ / A", color="r")
    axV.grid(True)
    
    fig.legend(loc="upper right", bbox_to_anchor=(0.85, 0.85))
    fig.show()
    
    logger.debug("Combined voltage and current profile plot generated successfully.")
    return fig


def plot_soc_profile(soc_profile: list[float], duration_profile: list[float]):
    """Plots the State of Charge over time starting at t = 0s"""
    
    if len(soc_profile) - 1 != len(duration_profile):
        raise ValueError("SoC profile must be longer by 1 than duration profile.")
    elif len(duration_profile) == 0:
        raise ValueError("The duration profile must have at least one value.")
    elif any(x == 0 for x in duration_profile):
        logger.warning("At least one duration between timestamps is zero seconds long.")

    logger.debug("Generating SoC profile plot...")
    
    edges = np.concatenate(([0.0], np.cumsum(duration_profile)))
        
    fig, ax = plt.subplots()
    ax.plot(edges, soc_profile)
    ax.set_xlabel("Time $t$ / s")
    ax.set_ylabel("State of Charge $SoC$ / -")
    ax.set_yticks(np.arange(0.0, 1.05, 0.1))
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True)
    fig.show()

    logger.debug("SoC profile plot generated successfully.")
    return fig