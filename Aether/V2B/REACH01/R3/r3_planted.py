"""R3 planted COMBINE positive control (deliberately designed; NOT a discovery): relay rows from inputs A and B,
turning at column 17 and converging on a combiner at (9, 17) that writes into the output. Energy 24 everywhere.
Expected (op XOR): output = a XOR b; certifier COMPOSE (A-path cells only a-necessary, B-path cells only
b-necessary)."""
import numpy as np
N, E, S, W = 0, 1, 2, 3


def planted(e=24):
    p = np.zeros((5, 16, 16), np.uint8)
    p[0] = 9

    def put(y, x, d):
        p[:, y - 2, x - 2] = (1, d, 3, 0, e)
    for x in range(2, 18):
        put(6, x, E if x < 17 else S)
    for y in range(7, 9):
        put(y, 17, S)
    for x in range(2, 18):
        put(13, x, E if x < 17 else N)
    for y in range(10, 13):
        put(y, 17, N)
    put(9, 17, E)
    return p
