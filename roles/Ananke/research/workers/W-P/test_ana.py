"""Classifier unit tests on synthetic truth tables (PLAN s4 must-fail items)."""
import numpy as np
import ana

N = 5


def table(fn):
    C = ana.cube(N)
    return np.array([fn(z) for z in C], dtype=np.int64)


def test_and():
    f = table(lambda z: int(z[0] and z[3]))
    assert ana.classify_fn(f, N)[:2] == ("AND", (0, 3))
    assert ana.min_decisive(f, N) == [(0, 3)]


def test_or():
    f = table(lambda z: int(z[1] or z[4]))
    assert ana.classify_fn(f, N)[:2] == ("OR", (1, 4))
    assert ana.min_decisive(f, N) == [(1, 4)]


def test_mux():
    f = table(lambda z: int(z[1] if z[2] == 0 else z[4]))
    c, R, m = ana.classify_fn(f, N)
    assert c == "MUX" and R == (1, 2, 4) and m == (2, 1, 4)
    assert ana.min_decisive(f, N) == [(1, 4)]


def test_xor3_is_higher_not_mux_not_joint():
    # f(0)=0, f(1)=1: XOR of 3 variables
    f = table(lambda z: z[0] ^ z[2] ^ z[3])
    c, R, _ = ana.classify_fn(f, N)
    assert c == "HIGHER" and R == (0, 2, 3)


def test_dictator():
    f = table(lambda z: int(z[2]))
    assert ana.classify_fn(f, N)[:2] == ("DICT", (2,))
    assert ana.min_decisive(f, N) == [(2,)]


def test_and_is_not_classified_as_mux_or_or():
    f = table(lambda z: int(z[0] and z[3]))
    assert ana.classify_fn(f, N)[0] not in ("MUX", "OR", "HIGHER")
