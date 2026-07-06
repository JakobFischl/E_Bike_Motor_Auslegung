import numpy as np
from scipy.interpolate import PchipInterpolator
from battery_pack import BatteryPack

class NMCBatteryPack(BatteryPack):

    cells_in_series = 10
    Vmin_per_cell = 3.2
    Vmax_per_cell = 4.2
    internal_resistance_mOhm_per_cell = 7

    def __init__(self, capacity_nom_Ah = 10, initial_soc = 1):
        super().__init__(capacity_nom_Ah, initial_soc)

        self.Vmin = self.Vmin_per_cell * self.cells_in_series
        self.Vmax = self.Vmax_per_cell * self.cells_in_series
        self.R_int = self.internal_resistance_mOhm_per_cell * self.cells_in_series / 1000
        
    def voltage(self, current = 0.0):
        soc = np.array([0.00, 0.04, 0.09, 0.13, 0.17, 0.21, 0.26, 0.30, 0.40, 0.52, 0.64, 0.76, 0.88, 1.00])
        voc = np.array([32.00, 32.61, 33.17, 33.85, 34.24, 34.66, 35.39, 35.65, 36.65, 37.64, 38.91, 40.14, 41.08, 42.00])
        pchip = PchipInterpolator(soc, voc)

        open_circuit_voltage = pchip(self.soc)
        v_out = open_circuit_voltage - self.R_int * current

        return v_out