import numpy as np
from PyQt5 import Qt

from data.rnd import rnd


class GISMap(Qt.QWidget):
    def __init__(self, width, height, wsf, hsf):
        super().__init__()
        self._width = width
        self._height = height
        self._wsf = wsf
        self._hsf = hsf

        self._pixmap = Qt.QPixmap(width * wsf, height * hsf)
        self._map = np.zeros((width, height), dtype=np.uint8)

    def setArray(self, array):
        assert array.shape == (self._width, self._height)
        assert np.all(array >= 0) and np.all(array <= 1)
        array = (array * 255).astype(np.uint8)
        self._map[:] = array

    def paintEvent(self, event):
        painter = Qt.QPainter(self)
        painter.drawPixmap(0, 0, self._pixmap)
        painter.setPen(Qt.Qt.NoPen)
        for j in range(self._height):
            for i in range(self._width):
                painter.setBrush(Qt.QColor(self._map[i, j], self._map[i, j], self._map[i, j]))
                painter.drawRect(i * self._wsf, j * self._hsf, self._wsf, self._hsf)
        painter.end()


class DebugWindow(Qt.QWidget):
    WIDTH, HEIGHT = 800, 600

    def __init__(self):
        super().__init__()
        self.setMinimumSize(self.WIDTH, self.HEIGHT)
        self.setWindowTitle("Debug Window")
        self._layout = Qt.QVBoxLayout()
        self.setLayout(self._layout)

        self._map = GISMap(128, 64, 8, 8)
        self._map.setArray(rnd(128, 64, seed=0))
        self._layout.addWidget(self._map)
