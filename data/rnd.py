from NPerlinNoise import Noise, perlinGenerator


def rnd(w, h, scale=128, seed=None):
    noise = Noise(seed=seed)
    asp = w / h
    return perlinGenerator(noise, (0, scale, w), (0, scale / asp, h))[0]
