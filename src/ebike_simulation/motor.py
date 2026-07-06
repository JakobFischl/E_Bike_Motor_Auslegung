class Motor:
    def __init__(self, efficiency: float):
        self.efficiency = efficiency

    def get_current_draw(self, power: float, voltage: float) -> float:
        current = power / (voltage * self.efficiency)
        return current