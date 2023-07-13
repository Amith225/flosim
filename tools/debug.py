import numpy as np
from PyQt5 import Qt

from data.rnd import rnd
from flosim import Basin


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
                if blue > 0:
                    col = self.BLUE
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

        x, y = 64, 32
        self.basin = Basin(x, y)
        self.basin.setElevation(slice(0, x), slice(0, y), rnd(x, y, seed=777) * 10)

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

    def tick(self):
        for _ in range(10):
            self.basin.tick(0.1)
            self._map.setBM(self.basin.BM)
            self._map.setWM(self.basin[:])
            self._map.update()
            Qt.QTest.qWait(1)

    def elevMode(self, px, py, k):
        px = max(min(px, self._map._W - 1), 0)
        py = max(min(py, self._map._H - 1), 0)
        self.basin.addElevation(
            *np.meshgrid([max(px - 1, 0), px, min(px + 1, self._map._W - 1)],
                         [max(py - 1, 0), py, min(py + 1, self._map._H - 1)]), 0.05 * k
        )
        self._map.setBM(self.basin.BM)
        self._map.update()

    def menu(self):
        menu = Qt.QFrame()
        layout = Qt.QVBoxLayout()
        menu.setLayout(layout)

        # tick = Qt.QPushButton("Tick")
        # tick.clicked.connect(lambda: self.tick())
        # layout.addWidget(tick, alignment=Qt.Qt.AlignTop)

        mode = Qt.QComboBox()
        mode.addItems(["None", "Elevation", "Building", "Rain", "Gutter"])
        mode.currentIndexChanged.connect(lambda i: setattr(self._map, "clickListener", self.elevMode))
        layout.addWidget(mode, alignment=Qt.Qt.AlignTop)

        return menu
