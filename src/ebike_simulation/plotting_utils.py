import logging
import matplotlib.pyplot as plt

# Set up local logger
logger = logging.getLogger(__name__)

def plot_current_profile(current_profile: list[float], duration_profile: list[float]):
    """Plots the current over time profile starting from t=0s."""
    
    # Error Handling & Logging
    if len(current_profile) != len(duration_profile):
        logger.error(f"Plot failed: current_profile (len {len(current_profile)}) and duration_profile (len {len(duration_profile)}) mismatch.")
        raise ValueError("Current and duration profiles must have the same length.")

    logger.debug("Generating current profile plot...")
    
    t_plot, I_plot = [], []
    t_total = 0.0
    for I, d in zip(current_profile, duration_profile):
        t_plot += [t_total, t_total + d]
        I_plot += [I, I]
        t_total += d

    fig, ax = plt.subplots()
    ax.plot(t_plot, I_plot)
    ax.set_xlabel("Time $t$ / s")
    ax.set_ylabel("Current $I$ / A")
    ax.set_yticks(range(-2, 12, 1))
    ax.set_xticks(range(0, int(t_total) + 1, 60))
    ax.grid(True)
    fig.show()

    logger.info("Current profile plot generated successfully.")
    return fig

def plot_power_profile(power_profile: list[float], duration_profile: list[float]):
    """Plots the power over time profile starting from t=0s."""

    # Error Handling & Logging
    if len(power_profile) != len(duration_profile):
        logger.error("Plot failed: Power and duration profiles dimension mismatch.")
        raise ValueError("Power and duration profiles must have the same length.")

    logger.debug("Generating power profile plot...")

    t_plot, P_plot = [], []
    t_total = 0.0
    for P, d in zip(power_profile, duration_profile):
        t_plot += [t_total, t_total + d]
        P_plot += [P, P]
        t_total += d

    fig, ax = plt.subplots()
    ax.plot(t_plot, P_plot)
    ax.set_xlabel("Time $t$ / s")
    ax.set_ylabel("Power $P$ / W")
    ax.set_xticks(range(0, int(t_total) + 1, 60))
    ax.grid(True)
    fig.show()
    
    logger.info("Power profile plot generated successfully.")
    return fig


def plot_voltage_profile(voltage_profile: list[float], duration_profile: list[float]):
    """Plots the voltage over time profile starting from t=0s."""

    # Error Handling & Logging
    if len(voltage_profile) - 1 != len(duration_profile):
        logger.error("Plot failed: Voltage profile length must be exactly duration + 1 (for t=0).")
        raise ValueError("Voltage profile must be longer by 1 than duration profile.")

    logger.debug("Generating voltage profile plot...")

    t_plot, U_plot = [], []

    t_plot.append(0.0)
    U_plot.append(voltage_profile[0])

    t_total = 0.0
    for U, d in zip(voltage_profile[1:], duration_profile):
        t_plot += [t_total, t_total + d]
        U_plot += [U, U]
        t_total += d

    fig, ax = plt.subplots()
    ax.plot(t_plot, U_plot)
    ax.set_xlabel("Time $t$ / s")
    ax.set_ylabel("Voltage $U$ / V")
    ax.grid(True)
    fig.show()
    
    logger.info("Voltage profile plot generated successfully.")
    return fig

def plot_voltage_and_current_profile(voltage_profile: list[float], current_profile: list[float], duration_profile: list[float]):
    """Plots the voltage and current over time profiles starting from t=0s."""

    # Error Handling & Logging
    if not (len(voltage_profile) - 1 == len(current_profile) == len(duration_profile)):
        logger.error("Plot failed: Dimension mismatch among combined voltage, current, and duration profiles.")
        raise ValueError("Current and duration profiles must have the same length, and voltage profile must be longer by 1.")

    logger.debug("Generating combined voltage and current profile plot...")

    t_plot, U_plot, I_plot = [], [], []

    t_plot.append(0.0)
    U_plot.append(voltage_profile[0])

    t_total = 0.0
    for U, I, d in zip(voltage_profile[1:], current_profile, duration_profile):
        t_plot += [t_total, t_total + d]
        U_plot += [U, U]
        I_plot += [I, I]

        t_total += d

    fig, axV = plt.subplots(figsize=(9, 4.5))
    axI = axV.twinx()

    axV.plot(t_plot[0:], U_plot, "b-", label="Voltage U / V")
    axI.plot(t_plot[1:], I_plot, "r--", label="Current I / A")
    axV.set_xlabel("Time $t$ / s")
    axV.set_ylabel("Voltage $U$ / V", color="b")
    axI.set_ylabel("Current $I$ / A", color="r")
    axV.grid(True)
    
    fig.legend(loc="upper right", bbox_to_anchor=(0.85, 0.85))
    fig.show()
    
    logger.info("Combined voltage and current profile plot generated successfully.")
    return fig