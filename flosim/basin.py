from abc import ABCMeta, abstractmethod, ABC

import numpy as np

from flosim.func import gauss_seidel_solver, surr, zeroBoundAdjust, velAct


class ControlLayer(metaclass=ABCMeta):
    ZERO = np.float64(0)

    def __init__(self, x, y):
        self._x, self._y = x, y
        self._level = np.zeros((self._x, self._y), dtype=np.float64)

    def __getitem__(self, item):
        return self._level[item]

    def __call__(self,
                 WM: "np.ndarray",
                 BM: "np.ndarray",
                 SVX: "np.ndarray",
                 SVY: "np.ndarray",
                 tick: float) -> tuple["np.ndarray", "np.ndarray", "np.ndarray", "np.ndarray"]:
        return self._tick(WM, BM, SVX, SVY, tick)

    @abstractmethod
    def _tick(self, *args, **kwargs) -> tuple["np.ndarray", "np.ndarray", "np.ndarray", "np.ndarray"]:
        pass


class FillsLayer(ControlLayer, ABC):
    def setFill(self, x, y, fill):
        self._level[x, y] = fill

    def removeFill(self, x, y):
        self._level[x, y] = self.ZERO

    def __call__(self,
                 WM: "np.ndarray",
                 BM: "np.ndarray",
                 SVX: "np.ndarray",
                 SVY: "np.ndarray",
                 tick: float) -> tuple["np.ndarray", "np.ndarray", "np.ndarray", "np.ndarray"]:
        return self._tick(WM, BM, SVX, SVY, tick=tick)


class DrainLayer(ControlLayer, ABC):
    def setDrain(self, x, y, drain):
        self._level[x, y] = drain

    def removeDrain(self, x, y):
        self._level[x, y] = self.ZERO

    def __call__(self,
                 WM: "np.ndarray",
                 BM: "np.ndarray",
                 SVX: "np.ndarray",
                 SVY: "np.ndarray",
                 tick: float) -> tuple["np.ndarray", "np.ndarray", "np.ndarray", "np.ndarray"]:
        drain, db, dvx, dvy = self._tick(WM, BM, SVX, SVY, tick=tick)
        return np.where(WM > drain, -drain, -WM), db, dvx, dvy


class Basin:
    def __init__(self, x: int, y: int, eta: float = 0.5):
        self._x, self._y = x, y
        self._eta = eta
        self._layers: list["ControlLayer"] = []

        self._BM = np.zeros((self._x, self._y), dtype=np.float64)
        self._WM = np.zeros((self._x, self._y), dtype=np.float64)
        self._SVX = np.zeros((2, self._x, self._y), dtype=np.float64)
        self._SVY = np.zeros((2, self._x, self._y), dtype=np.float64)

        self._dB = np.zeros_like(self._BM)
        self._dW = np.zeros_like(self._WM)
        self._dSVX = np.zeros_like(self._SVX)
        self._dSVY = np.zeros_like(self._SVY)

    def __getitem__(self, item):
        return self._WM[item]

    def setElevation(self, x, y, elevation):
        self._BM[x, y] = elevation

    def setVelL(self, x, y, vel):
        self._SVX[0, x, y] = vel

    def setVelR(self, x, y, vel):
        self._SVX[1, x, y] = vel

    def setVelU(self, x, y, vel):
        self._SVY[0, x, y] = vel

    def setVelD(self, x, y, vel):
        self._SVY[1, x, y] = vel

    def addLayer(self, layer: ControlLayer):
        assert isinstance(layer, ControlLayer)
        self._layers.append(layer)

    def diffuse(self, dex, ndex, tick):
        return (dex + tick * surr(self._BM, ndex)) / (1 + tick)

    def tick(self, tick: float = 1):
        self._dW.fill(0)
        self._dB.fill(0)
        self._dSVX.fill(0)
        self._dSVY.fill(0)
        tick *= self._eta

        for layer in self._layers:
            dw, db, vx, vy = layer(self._WM, self._BM, self._SVX, self._SVY, tick)
            self._dW += dw
            self._dB += db
            self._dSVX += vx
            self._dSVY += vy
        self._BM += self._dB
        self._WM += self._dW
        self._SVX += self._dSVX
        self._SVY += self._dSVY

        zeroBoundAdjust(self._SVX, self._SVY)
        self._WM += velAct(self._BM, self._WM, self._SVX, self._SVY, tick)
        self._WM = gauss_seidel_solver(lambda dex, ndex: self.diffuse(dex, ndex, tick), self._WM)
