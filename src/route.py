import pandas as pd
import numpy as np 

class RouteAnalysis:
    
    def __init__(self, dateipfad):
        self.daten = pd.read_csv(dateipfad, sep=';')
        self.daten['time'] = pd.to_datetime(self.daten['time'])
        
    def geschwindigkeit(self):
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
        
    def beschleunigung(self):
        delta_v = self.daten['geschwindigkeit_m_s'].diff()
        self.daten['beschleunigung_m_s2'] = delta_v / self.daten['delta_t_sekunden']
        
    def steigung(self):
        delta_h = self.daten['ele'].diff()
        
        strecke = self.daten['delta_s_meter'].replace(0, np.nan)
        
        self.daten['steigung_prozent'] = (delta_h / strecke) * 100
        self.daten['steigung_winkel_rad'] = np.arctan(delta_h / strecke)



meine_fahrt = RouteAnalysis('simulation_data/final_project_input_data.csv')

meine_fahrt.geschwindigkeit()
meine_fahrt.beschleunigung()
meine_fahrt.steigung()


print(meine_fahrt.daten[['time', 'geschwindigkeit_km_h', 'beschleunigung_m_s2', 'steigung_prozent']].head())