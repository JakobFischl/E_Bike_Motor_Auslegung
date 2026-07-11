import numpy as np
from battery_pack import BatteryPack

class NMCBatteryPack(BatteryPack):
    """
    Simple model of a 10-cell-series lithium polymer battery pack.
    Defines minimum/maximum voltage and internal resistance per cell,
    derives pack values for them and passes them on to BatteryPack.
    """
    
    cells_in_series = 10
    Vmin_per_cell = 3.2
    Vmax_per_cell = 4.2
    internal_resistance_mOhm_per_cell = 7
    name = "NMC"
    # Measured open circuit voltage at specific SoC's, interpolated with PCHIP in BatteryPack.
    soc_table = np.array([0.00, 0.04, 0.09, 0.13, 0.17, 0.21, 0.26, 0.30, 0.40, 0.52, 0.64, 0.76, 0.88, 1.00])
    voc_table = np.array([32.00, 32.61, 33.17, 33.85, 34.24, 34.66, 35.39, 35.65, 36.65, 37.64, 38.91, 40.14, 41.08, 42.00])

    def __init__(self, capacity_nom_Ah: float = 10.0, initial_soc: float = 1.0):
        """Derive voltage and resistance from the per-cell values and hand them to BatteryPack."""

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
