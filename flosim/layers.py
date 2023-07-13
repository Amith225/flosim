from .basin import FillsLayer as _FL, DrainLayer as _DL

import numpy as _np


class RainLayer(_FL):
    def _tick(self, *_, tick: float, **__) -> tuple["_np.ndarray", "_np.ndarray", "_np.ndarray", "_np.ndarray"]:
        return self._level * tick, self.ZERO, self.ZERO, self.ZERO


class GutterLayer(_DL):
    def _tick(self, *_, tick: float, **__) -> tuple["_np.ndarray", "_np.ndarray", "_np.ndarray", "_np.ndarray"]:
        return self._level * tick, self.ZERO, self.ZERO, self.ZERO


class EvaporationLayer(_DL):
    def __init__(self, x, y, rate):
        super().__init__(x, y)
        self._level += 0.01
        self._rate = rate

    def _tick(self, *_, tick: float, **__) -> tuple["_np.ndarray", "_np.ndarray", "_np.ndarray", "_np.ndarray"]:
        return self._level * self._rate * tick, self.ZERO, self.ZERO, self.ZERO


class ReservoirLayer(_FL):
    def __init__(self, x, y, height):
        super().__init__(x, y)
        self._level = self._level.astype(bool)
        self._height = height

    def setMask(self, x, y, mask: bool = True):
        self._level[y, x] = mask

    def _tick(self,
              WM: "_np.ndarray", *_,
              tick: float, **__) -> tuple["_np.ndarray", "_np.ndarray", "_np.ndarray", "_np.ndarray"]:
        return _np.where(self._level * (WM - self._height) < 0, self._height * tick, self.ZERO),\
            self.ZERO, self.ZERO, self.ZERO
