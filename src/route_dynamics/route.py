import pandas as pd
import numpy as np 
import logging

logger = logging.getLogger(__name__)

class RouteAnalysis:
    """
    Klasse zur  Analyse der GPS-Route. 
    Liest die daten der csv Datei ein und berechnet Strecke, Geschwindigkeit, Beschleunigung und Steigung.
    """
    
    def __init__(self, dateipfad):
        try:
            logger.info(f"Daten von '{dateipfad}'laden.")
            self.daten = pd.read_csv(dateipfad, sep=';')
            self.daten['time'] = pd.to_datetime(self.daten['time'])
            logger.info("Daten geladen")

        except FileNotFoundError:
            logger.error(f"Datei unter '{dateipfad}' konnte nicht gefunden werden!")
            raise
        
        except Exception as e:
            logger.error(f"Fehler beim Laden der Daten: {e}")
            raise

    def geschwindigkeit(self):
        """
        Berechnet die zurückgelegte Strecke mitttels der Haversine-Formel 
        sowie Geschwindigkeit in m/s und km/h.
        """
        logger.info("Berechnung der Geschwindigkeit.")
        try:
            self.daten['delta_t_sekunden'] = self.daten['time'].diff().dt.total_seconds()
        
            lat_vorher = self.daten['lat'].shift(1)
            lon_vorher = self.daten['lon'].shift(1)
            lat_jetzt = self.daten['lat']
            lon_jetzt = self.daten['lon']
        
            # Erdradius in Metern
            R = 6371000  
        
         # Gradzahlen in Bogenmaß
            phi1 = np.radians(lat_vorher)
            phi2 = np.radians(lat_jetzt)
            delta_phi = np.radians(lat_jetzt - lat_vorher)
            delta_lambda = np.radians(lon_jetzt - lon_vorher)
        
            #Haversine Formel
            a = np.sin(delta_phi/2.0)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda/2.0)**2
            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        
            self.daten['delta_s_meter'] = R * c
        
            # Geschwindigkeit
            self.daten['geschwindigkeit_m_s'] = self.daten['delta_s_meter'] / self.daten['delta_t_sekunden']

            # Umrechnung in km/h
            self.daten['geschwindigkeit_km_h'] = self.daten['geschwindigkeit_m_s'] * 3.6
            self.daten['delta_t_sekunden'] = self.daten['delta_t_sekunden'].fillna(0)
            self.daten['delta_s_meter'] = self.daten['delta_s_meter'].fillna(0)
            self.daten['geschwindigkeit_m_s'] = self.daten['geschwindigkeit_m_s'].fillna(0)
            self.daten['geschwindigkeit_km_h'] = self.daten['geschwindigkeit_km_h'].fillna(0)
            logger.debug("Geschwindigkeit im Datensatz.")
            
        except KeyError as e:
            logger.error(f"Fehler Geschwindigkeitsberechnung: {e}")
            raise

    def beschleunigung(self):
        """
        Berechnet die Beschleunigung in m/s^2 mithilfe der Geschwindigkeitsdifferenz.
        """
        logger.info("Berechnung der Beschleunigung.")
        try:
            delta_v = self.daten['geschwindigkeit_m_s'].diff()
            self.daten['beschleunigung_m_s2'] = delta_v / self.daten['delta_t_sekunden']
            self.daten['beschleunigung_m_s2'] = self.daten['beschleunigung_m_s2'].fillna(0)
            logger.debug("Beschleunigung erfolgreich berechnet.")
        except KeyError:
            logger.error("Fehler: Geschwindigkeit vor Beschleunigung berechnen!")
            raise
        except Exception as e:
            logger.error(f"Fehler beim Berechnen der Beschleunigung: {e}")
            raise

    def steigung(self):
        """
        Berechnung der Steigung in Prozent sowie dem Steigungswinkel im Bogenmaß.
        """
        logger.info("Berechnung der Steigung.")
        try:
            delta_h = self.daten['ele'].diff()
            strecke = self.daten['delta_s_meter'].replace(0, np.nan)
        
            self.daten['steigung_prozent'] = (delta_h / strecke) * 100
            self.daten['steigung_winkel_rad'] = np.arctan(delta_h / strecke)
            self.daten['steigung_prozent'] = self.daten['steigung_prozent'].fillna(0)
            self.daten['steigung_winkel_rad'] = self.daten['steigung_winkel_rad'].fillna(0)
            logger.debug("Steigung berechnet")
            
        except KeyError as e:
            logger.error(f"Fehler Steigungsberechnung: {e}")
            raise


if __name__ == "__main__":
    meine_fahrt = RouteAnalysis('simulation_data/final_project_input_data.csv')
    meine_fahrt.geschwindigkeit()
    meine_fahrt.beschleunigung()
    meine_fahrt.steigung()
    print(meine_fahrt.daten[['time', 'geschwindigkeit_km_h', 'beschleunigung_m_s2', 'steigung_prozent']].head())