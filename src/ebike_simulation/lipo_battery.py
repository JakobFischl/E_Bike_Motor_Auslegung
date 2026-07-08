import numpy as np
from battery_pack import BatteryPack

class LiPoBatteryPack(BatteryPack):

    cells_in_series = 10
    Vmin_per_cell = 3.2
    Vmax_per_cell = 4.2
    internal_resistance_mOhm_per_cell = 8
    name = "LiPo"
    soc_table = np.array([0.00, 0.04, 0.09, 0.13, 0.17, 0.21, 0.26, 0.30, 0.40, 0.52, 0.64, 0.76, 0.88, 1.00])
    voc_table = np.array([32.00, 35.87, 36.85, 37.56, 37.87, 38.28, 38.81, 39.05, 39.55, 40.27, 40.70, 41.16, 41.65, 42.00])

    def __init__(self, capacity_nom_Ah = 10, initial_soc = 1):
        
        Vmin = self.Vmin_per_cell * self.cells_in_series
        Vmax = self.Vmax_per_cell * self.cells_in_series
        R_int_mOhm = self.internal_resistance_mOhm_per_cell * self.cells_in_series

        super().__init__(
            capacity_nom_Ah,
            initial_soc=initial_soc,
            Vmin=Vmin,
            Vmax=Vmax,
            internal_resistance_mOhm=R_int_mOhm
        )
