import pandas as pd
import numpy as np  # Neu: Für die mathematischen Berechnungen (Sinus, Cosinus etc.)

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
        print("Beschleunigung:")
        
        delta_v = self.daten['geschwindigkeit_m_s'].diff()
        
        # Beschleunigung 
        self.daten['beschleunigung_m_s2'] = delta_v / self.daten['delta_t_sekunden']
        



meine_fahrt = RouteAnalysis('simulation_data/final_project_input_data.csv')

meine_fahrt.geschwindigkeit()

print(meine_fahrt.daten[['time', 'delta_t_sekunden', 'delta_s_meter', 'geschwindigkeit_km_h']].head())


meine_fahrt = RouteAnalysis('simulation_data/final_project_input_data.csv')

# Geschwindigkeit
meine_fahrt.geschwindigkeit()

# Beschleunigung 
meine_fahrt.beschleunigung()


print(meine_fahrt.daten[['time', 'geschwindigkeit_km_h', 'beschleunigung_m_s2']].head())