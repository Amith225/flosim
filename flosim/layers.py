import numpy as np

from .basin import FillsLayer, DrainLayer


class RainLayer(FillsLayer):
    def _tick(self, *_, tick: float, **__) -> tuple["np.ndarray", "np.ndarray", "np.ndarray", "np.ndarray"]:
        return self._level * tick, self.ZERO, self.ZERO, self.ZERO


class GutterLayer(DrainLayer):
    def _tick(self, *_, tick: float, **__) -> tuple["np.ndarray", "np.ndarray", "np.ndarray", "np.ndarray"]:
        return self._level * tick, self.ZERO, self.ZERO, self.ZERO
