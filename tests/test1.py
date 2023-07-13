import numpy as np

from flosim.func import gauss_seidel_solver, surr, velAct

if __name__ == '__main__':
    eta = 0.5
    tick = 1
    k = tick * eta

    e = np.array([[0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0]], dtype=np.float64)
    w = np.ones_like(e, dtype=np.float64)
    vx = np.array([[[0, 0, 0, 0],
                    [0, 0, 0, 0],
                    [0, 1, 1, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0]],
                   [[0, 0, 0, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0]]], dtype=np.float64)
    vy = np.array([[[0, 0, 0, 0],
                    [0, 0, 0, 0],
                    [0, 1, 1, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0]],
                   [[0, 0, 0, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0]]], dtype=np.float64)

    for _ in range(1000):
        w += velAct(e, w, vx, vy, k)
        w = gauss_seidel_solver(lambda ndex, dex: (dex + k * surr(e, ndex)) / (1 + k), w)
    print(w.sum())
