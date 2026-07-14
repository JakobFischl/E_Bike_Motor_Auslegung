import numpy as np
import pandas as pd
from ebike_simulation.motor import Motor 

class EBikeDynamics:
    def __init__(self, daten: pd.DataFrame):
        self.daten = daten
        
        self.m_fahrer = 70.0
        self.m_fahrrad = 10.0
        self.m_ges = self.m_fahrer + self.m_fahrrad
        self.g = 9.81
        self.rho = 1.225      
        self.cw_A = 0.5625 
        self.radius_rad = (27 * 0.0254) / 2 
        self.motor = Motor(K_m=1.5)

    def kraefte(self):
        print("Berechne physikalische Kräfte...")
        
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

    def motor_werte(self):
        print("Berechne Drehmoment, Motorstrom und Leistung...")
        
        self.daten['drehmoment_Nm'] = self.daten['F_gesamt'] * self.radius_rad
    
        self.daten['motorstrom_A'] = self.motor.get_current_draw(self.daten['drehmoment_Nm'])
        
        self.daten['leistung_W'] = self.daten['F_gesamt'] * self.daten['geschwindigkeit_m_s']
        
        return self.daten