import matplotlib.pyplot as plt
import numpy as np
import logging


logger = logging.getLogger(__name__)

def plot_hoehenprofil(distanz_km: np.ndarray, elevation: np.ndarray):
    """
    Zeichnet das Höhenprofil der Strecke.
    Gibt die erstellte Figur zurück.
    """
    logger.debug("Generiert Höhenprofil.")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(distanz_km, elevation, color='forestgreen', linewidth=2)
    ax.set_title('Höhenprofil der Strecke')
    ax.set_xlabel('Zurückgelegte Distanz (km)')
    ax.set_ylabel('Höhe über Meeresspiegel (m)')
    ax.grid(True, linestyle='--', alpha=0.7)
    
    ax.fill_between(distanz_km, elevation, np.min(elevation) - 10, color='forestgreen', alpha=0.2)
    
    fig.show()
    logger.debug("Höhenprofil generiert.")
    return fig

def plot_geschwindigkeit(zeit: np.ndarray, geschwindigkeit_kmh: np.ndarray):
    """
    Zeichnet die Geschwindigkeit über die Zeit.
    """
    logger.debug("Generiert Geschwindigkeits Plot")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(zeit, geschwindigkeit_kmh, color='royalblue', linewidth=1.5)
    ax.set_title('Geschwindigkeit über die Zeit')
    ax.set_xlabel('Zeit')
    ax.set_ylabel('Geschwindigkeit (km/h)')
    ax.grid(True, linestyle='--', alpha=0.7)
    
    fig.show()
    logger.debug("Geschwindigkeits Plot generiert.")
    return fig

def plot_motorleistung(zeit: np.ndarray, leistung_w: np.ndarray):
    """
    Zeichnet die benötigte Motorleistung über die Zeit.
    """
    logger.debug("Generiert Leistungs Plot")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(zeit, leistung_w, color='crimson', linewidth=1.5)
    ax.set_title('Benötigte Motorleistung über die Zeit')
    ax.set_xlabel('Zeit')
    ax.set_ylabel('Leistung (W)')
    ax.grid(True, linestyle='--', alpha=0.7)
    
    fig.show()
    logger.debug("Leistungs Plot generiert.")
    return fig
