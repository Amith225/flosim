import numpy as np
from PyQt5 import Qt
from matplotlib import pyplot as plt

from data.rnd import rnd
from flosim import Basin, RainLayer, GutterLayer, ReservoirLayer, EvaporationLayer


class GISMap(Qt.QWidget):
    BLUE = 0, 105, 148

    def __init__(self, width, height, sf):
        super().__init__()
        self._W = width
        self._H = height
        self._sf = sf
        self.setFixedSize(width * self._sf, height * self._sf)

        self._BM = np.zeros((height, width), dtype=np.uint8)
        self._WM = np.zeros((height, width), dtype=np.float64)

        self.road = np.zeros((height, width), dtype=bool)
        self.building = np.zeros((height, width), dtype=bool)

        self.clickListener = None
        self._pressed = 0

    def setBM(self, array):
        assert array.shape == (self._H, self._W)
        array = (array / array.max() * 255).astype(np.uint8)
        self._BM[:] = array

    def setSF(self, sf):
        self._sf = sf
        self.setFixedSize(self._W * self._sf, self._H * self._sf)

    def setWM(self, array):
        assert array.shape == (self._H, self._W)
        array = array / (array.max() + 1e-6)
        self._WM[:] = array

    def paintEvent(self, event):
        painter = Qt.QPainter(self)
        painter.setPen(Qt.Qt.NoPen)
        for j in range(self._H):
            for i in range(self._W):
                blue = self._WM[j, i]
                elev = self._BM[j, i]
                if self.building[j, i]:
                    col = 255, 255, 0
                elif self.road[j, i]:
                    col = 0, 0, 0
                elif blue > 0:
                    blue = np.minimum(1 - blue, 0.2) * 2 / 3
                    elev = elev / 3
                    col = int(self.BLUE[0] * blue + elev), int(self.BLUE[1] * blue + elev), int(self.BLUE[2] * blue + elev)
                else:
                    col = elev, elev, elev
                painter.setBrush(Qt.QColor(*col))
                painter.drawRect(i * self._sf, j * self._sf, self._sf, self._sf)
        painter.end()

    def mousePressEvent(self, event):
        self._pressed = 1 if event.button() == Qt.Qt.LeftButton else -1

    def mouseReleaseEvent(self, event):
        self._pressed = 0

    def mouseMoveEvent(self, event):
        if self._pressed:
            if self.clickListener is not None:
                x, y = event.x() // self._sf, event.y() // self._sf
                self.clickListener(x, y, self._pressed)


class DebugWindow(Qt.QWidget):
    WIDTH, HEIGHT = 1200, 600

    def __init__(self):
        super().__init__()
        self.setMinimumSize(self.WIDTH, self.HEIGHT)
        self.setWindowTitle("Debug Window")
        self._layout = Qt.QHBoxLayout()
        self.setLayout(self._layout)

        x, y = 128, 64
        self.basin = Basin(x, y)
        self._initElev = rnd(x, y, seed=777) * 10
        self.basin.setElevation(slice(0, x), slice(0, y), self._initElev)
        self.rain = RainLayer(x, y)
        self.basin.addLayer(self.rain)
        self.gutter = GutterLayer(x, y)
        self.basin.addLayer(self.gutter)
        self.reservoir = ReservoirLayer(x, y, 0.07)
        self.basin.addLayer(self.reservoir)
        self.evaporation = EvaporationLayer(x, y, 0.9)

        self.hydrograph = []

        self._map = GISMap(x, y, 1)
        self._map.setBM(self.basin.BM)
        self._map.setWM(self.basin[:])
        scroll = Qt.QScrollArea()
        scroll.setAlignment(Qt.Qt.AlignCenter)
        scroll.setVerticalScrollBarPolicy(Qt.Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.Qt.ScrollBarAlwaysOn)
        scroll.setWidget(self._map)
        scroll.resizeEvent = lambda _: self._map.setSF(scroll.height() // y)
        self._layout.addWidget(scroll, stretch=3)

        self._menu = self.menu()
        self._layout.addWidget(self._menu, stretch=1)

    def __reinit__(self):
        self.basin.setElevation(slice(0, self._map._W), slice(0, self._map._H), rnd(self._map._W, self._map._H, seed=777) * 10)
        self.rain._level *= 0
        self.gutter._level *= 0
        self.basin._WM *= 0
        self._map.building *= False
        self._map.road *= False
        self.reservoir._level *= False
        self._map.setBM(self.basin.BM)
        self._map.setWM(self.basin[:])
        self._map.update()
        plt.plot(self.hydrograph)
        plt.show()
        self.hydrograph = []

    def tick(self):
        for _ in range(1000):
            self.basin.tick(0.2)
            self._map.setBM(self.basin.BM)
            self._map.setWM(self.basin[:])
            self._map.update()
            self.hydrograph.append(self.basin[:].sum())
            Qt.QTest.qWait(1)

    def elevMode(self, px, py, k):
        px = max(min(px, self._map._W - 1), 0)
        py = max(min(py, self._map._H - 1), 0)
        self.basin.addElevation(
            *np.meshgrid([max(px - 1, 0), px, min(px + 1, self._map._W - 1)],
                         [max(py - 1, 0), py, min(py + 1, self._map._H - 1)]), self.value.value() * k
        )
        self._map.setBM(self.basin.BM)
        self._map.update()

    def rainMode(self, px, py, k):
        px = max(min(px, self._map._W - 1), 0)
        py = max(min(py, self._map._H - 1), 0)
        p = np.meshgrid([max(px - 1, 0), px, min(px + 1, self._map._W - 1)],
                        [max(py - 1, 0), py, min(py + 1, self._map._H - 1)])
        if k > 0:
            self.rain.setFill(*p, 0.001)
        else:
            self.rain.setFill(*p, py, 0)

    def gutterMode(self, px, py, k):
        px = max(min(px, self._map._W - 1), 0)
        py = max(min(py, self._map._H - 1), 0)
        p = np.meshgrid([max(px - 1, 0), px, min(px + 1, self._map._W - 1)],
                        [max(py - 1, 0), py, min(py + 1, self._map._H - 1)])
        if k > 0:
            self.gutter.setDrain(*p, 0.05)
        else:
            self.gutter.setDrain(*p, py, 0)

    def buildingMode(self, px, py, k):
        px = max(min(px, self._map._W - 1), 0)
        py = max(min(py, self._map._H - 1), 0)
        if k > 0:
            self._map.building[py, px] = 1
            self.basin.setElevation(px, py, 10)
        else:
            self._map.building[py, px] = 0
            self.basin.setElevation(px, py, self._initElev[py, px])
        self._map.setBM(self.basin.BM)
        self._map.update()

    def roadMode(self, px, py, k):
        px = max(min(px, self._map._W - 1), 0)
        py = max(min(py, self._map._H - 1), 0)
        px = [max(px - 1, 0), px, min(px + 1, self._map._W - 1)]
        py = [max(py - 1, 0), py, min(py + 1, self._map._H - 1)]
        if k > 0:
            self._map.road[py, px] = 1
        else:
            self._map.road[py, px] = 0
        self._map.update()

    def riverMode(self, px, py, k):
        px = max(min(px, self._map._W - 1), 0)
        py = max(min(py, self._map._H - 1), 0)
        if k > 0:
            self.reservoir.setMask(px, py, True)
        else:
            self.reservoir.setFill(px, py, False)

    def modeSwitch(self, i):
        match i:
            case 0:
                self._map.clickListener = None
            case 1:
                self._map.clickListener = self.elevMode
            case 2:
                self._map.clickListener = self.rainMode
            case 3:
                self._map.clickListener = self.gutterMode
            case 4:
                self._map.clickListener = self.buildingMode
            case 5:
                self._map.clickListener = self.roadMode
            case 6:
                self._map.clickListener = self.riverMode

    def menu(self):
        menu = Qt.QFrame()
        layout = Qt.QVBoxLayout()
        menu.setLayout(layout)

        tick = Qt.QPushButton("Tick")
        tick.clicked.connect(lambda: self.tick())
        layout.addWidget(tick, alignment=Qt.Qt.AlignTop)

        modeLabel = Qt.QLabel("Mode:")
        layout.addWidget(modeLabel, alignment=Qt.Qt.AlignTop)
        mode = Qt.QComboBox()
        mode.addItems(["None", "Elevation", "Rain", "Gutter", "Building", "Road", "River"])
        mode.currentIndexChanged.connect(self.modeSwitch)
        layout.addWidget(mode, alignment=Qt.Qt.AlignTop)

        self.value = Qt.QDoubleSpinBox()
        self.value.setRange(0, 1)
        self.value.setSingleStep(0.01)
        self.value.setValue(0.1)
        layout.addWidget(self.value, alignment=Qt.Qt.AlignTop)

        reset = Qt.QPushButton("Reset")
        reset.clicked.connect(lambda: self.__reinit__())
        layout.addWidget(reset, alignment=Qt.Qt.AlignTop)

        layout.addStretch(1)

        return menu
