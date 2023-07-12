import numpy as np


def zeroBoundAdjust(SVX: "np.ndarray", SVY: "np.ndarray"):
    pass


def gauss_seidel_solver(foo, dex: "np.ndarray", n=32) -> "np.ndarray":
    ndex = dex.copy()
    for _ in range(n):
        ndex = foo(dex, ndex)
    return ndex


def surr(e: "np.ndarray", w: "np.ndarray") -> "np.ndarray":
    h = np.pad(e + w, ((1, 1), (1, 1)), 'constant', constant_values=float("inf"))
    lr = h[:, :-1] - h[:, 1:]
    ud = h[:-1, :] - h[1:, :]
    l = lr[1:-1, :-1] <= 0
    r = lr[1:-1, 1:] >= 0
    u = ud[:-1, 1:-1] <= 0
    d = ud[1:, 1:-1] >= 0

    s = np.pad((w * l)[:, 1:], ((0, 0), (0, 1))) / 4 + \
        np.pad((w * r)[:, :-1], ((0, 0), (1, 0))) / 4 + \
        np.pad((w * u)[1:, :], ((0, 1), (0, 0))) / 4 + \
        np.pad((w * d)[:-1, :], ((1, 0), (0, 0))) / 4
    agr = 4 - (l.astype(np.int8) + r.astype(np.int8) + u.astype(np.int8) + d.astype(np.int8))
    return s + agr * w / 4


def velAct(e: "np.ndarray", w: "np.ndarray", vx: "np.ndarray", vy: "np.ndarray", k: float) -> "np.ndarray":
    fx = w * vx * k
    fy = w * vy * k
    l = np.pad(fx[0, :, 1:], ((0, 0), (0, 1)))
    r = np.pad(fx[1, :, :-1], ((0, 0), (1, 0)))
    u = np.pad(fy[0, 1:], ((0, 1), (0, 0)))
    d = np.pad(fy[1, :-1], ((1, 0), (0, 0)))
    return l + r + u + d - fx.sum(axis=0) - fy.sum(axis=0)
