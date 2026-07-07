class Motor:
    def __init__(self, K_m: float):
        self.K_m = K_m

    def get_current_draw(self, torque: float) -> float:
        current = torque / self.K_m
        return current