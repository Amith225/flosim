from flosim import Basin, RainLayer, GutterLayer


if __name__ == '__main__':
    # basin initial conditions
    x, y = 5, 5
    basin = Basin(x, y)
    basin.setElevation([0, 1, 2], [2, 1, 0], 10)
    basin.setVelR(2, 2, 1)
    basin.setVelD(2, 2, 1)

    # add environmental layers
    basin.addLayer(rl1 := RainLayer(x, y))
    basin.addLayer(gl1 := GutterLayer(x, y))

    # dynamic environmental levels
    rl1.setFill(2, 2, 1)
    gl1.setDrain(4, 4, 1)

    # run simulation
    for _ in range(50):
        WL = basin[:]
        basin.tick()

    # dynamic environmental levels
    rl1.removeFill(2, 2)

    # run simulation
    for _ in range(50):
        WL = basin[:]
        basin.tick()
