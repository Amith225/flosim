import numpy as np

from flosim.basin import ElevationLayer, Basin, RainLayer


def main():
    x, y = 16, 16
    basin = Basin(x, y)
    basin.addLayer(eleLayer := ElevationLayer(np.random.rand(x, y)))
    basin.addLayer(rainLayer := RainLayer(x, y))
    rainLayer.addRain(0, 0, 1)
    basin.tick()


if __name__ == '__main__':
    main()
