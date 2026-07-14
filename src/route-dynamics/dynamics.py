import numpy as np
import pandas as pd
import logging
from ebike_simulation.motor import Motor 

logger = logging.getLogger(__name__)

class EBikeDynamics:
    def __init__(self, daten: pd.DataFrame):
        logger.info("Starte EBikeDynamics.")
        try:
            self.daten = daten
        
            self.m_fahrer = 70.0
            self.m_fahrrad = 10.0
            self.m_ges = self.m_fahrer + self.m_fahrrad
            self.g = 9.81
            self.rho = 1.225      
            self.cw_A = 0.5625 
            self.radius_rad = (27 * 0.0254) / 2 
            self.motor = Motor(K_m=1.5)
            logger.debug("Konstanten und Motor starten.")

        except Exception as e:
            logger.error(f"Fehler beim starten der Klasse: {e}")
            raise

    def kraefte(self):
        logger.info("Berechnung der Kräfte.")
        try:
        
            # Luftwiderstand
            v = self.daten['geschwindigkeit_m_s']
            self.daten['F_luft'] = 0.5 * self.rho * self.cw_A * (v**2)
        
            # Hangabtriebskraft
            phi = self.daten['steigung_winkel_rad']
            self.daten['F_hang'] = self.m_ges * self.g * np.sin(phi)
        
            # Beschleunigungskraft
            a = self.daten['beschleunigung_m_s2']
            self.daten['F_beschleunigung'] = self.m_ges * a
        
            # F-Gesamt
            self.daten['F_gesamt'] = self.daten['F_luft'] + self.daten['F_hang'] + self.daten['F_beschleunigung']

        except KeyError as e:
            logger.error(f"Fehler: Fehlende Spalte Kinematik: {e}")
            raise
        except Exception as e:
            logger.error(f"Fehler bei Berechnung der Kräfte: {e}")
            raise
    
    def motor_werte(self):
        logger.info("Berechnung von Drehmoment, Strom und Leistung.")
        try:
        
            self.daten['drehmoment_Nm'] = self.daten['F_gesamt'] * self.radius_rad
            self.daten['motorstrom_A'] = self.motor.get_current_draw(self.daten['drehmoment_Nm'])
            self.daten['leistung_W'] = self.daten['F_gesamt'] * self.daten['geschwindigkeit_m_s']
        
            logger.debug("Motorwerte berechnet.")
            return self.daten
        
        except KeyError as e:
            logger.error(f"Fehler: Kräfte vor Motorwerte berechnen Fehlende Spalte: {e}")
            raise
        except Exception as e:
            logger.error(f"Fehler: Berechnung der Motorwerte: {e}")
            raise