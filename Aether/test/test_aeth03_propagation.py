"""The propagation assay's own controls: it must see nothing when there is
nothing, count hops exactly on a known relay, and catch a causal radius it
was not told about."""

import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_AETHER = os.path.dirname(_HERE)
for _p in (_AETHER, os.path.join(_HERE, "reference")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import gpu_aeth01 as K                                   # noqa: E402
from observatory import aeth03_propagation as P          # noqa: E402

QUIET = dict(seed=7, write_cost=1, maintenance_cost=0, replenish_numer=0,
             replenish_amount=0, mut_numer=0)


def blank(n, energy=200):
    f = [np.zeros((n, n), dtype=np.uint8) for _ in range(5)]
    f[0][:] = 7
    f[4][:] = energy
    return f


def test_null_twin_never_differs():
    rng = np.random.default_rng(1)
    n = 24
    f = [rng.integers(0, 256, size=(n, n), dtype=np.uint8) for _ in range(5)]
    f[0] = np.where(rng.random((n, n)) < 0.5, np.uint8(1), f[0]).astype(np.uint8)
    w = P.World("v1", f)
    par = dict(QUIET, mut_numer=int(0.1 * (1 << 32)), maintenance_cost=1,
               replenish_numer=int(0.125 * (1 << 32)), replenish_amount=8)
    rows, s = P.pair_run(w, (5, 5), 3, 2, par, 0, 60, P.manhattan_from(n, 5, 5),
                         null=True)
    assert s["class"] == "INERT" and s["died"] and s["new_differences"] == 0
    assert all(r["differing_sites"] == 0 for r in rows.values())


def test_relay_chain_counts_one_generation_per_hop():
    # 21 emitters in a row, each writing its payload into its east
    # neighbour's payload. A bit flipped in the head's payload must reach
    # hop k at tick k with generation exactly k.
    n, length = 64, 21
    f = blank(n)
    r = 10
    for c in range(2, 2 + length):
        f[0][r, c] = K.WRITE_OPCODE
        f[1][r, c] = K.EAST
        f[2][r, c] = K.PAYLOAD
        f[3][r, c] = 50
    w = P.World("v1", f)
    rows, s = P.pair_run(w, (r, 2), 3, 4, QUIET, 0, 40,
                         P.manhattan_from(n, r, 2))
    assert s["locality_violations"] == 0
    assert s["max_generation"] == length
    assert s["max_radius"] == length
    assert s["new_by_generation"][1] == 1 and s["new_by_generation"][2] == 1
    assert rows[10]["max_generation_now"] == 10


def test_assay_catches_an_undeclared_radius_two_effect():
    # mov: two emitters with EQUAL payloads contest one target, so the
    # target never differs; disabling one contender in world B changes
    # whether the OTHER wins, and therefore whether its payload is cleared.
    # That other emitter sits two sites from the flipped one. Under the
    # declared radius (2) this is a clean generation-1 edge; under a
    # radius-1 search it must be counted as a violation.
    n = 16
    f = blank(n)
    for (rr, cc, d) in ((5, 4, K.EAST), (5, 6, K.WEST)):
        f[0][rr, cc] = K.WRITE_OPCODE
        f[1][rr, cc] = d
        f[2][rr, cc] = K.ARG1
        f[3][rr, cc] = 40
    w = P.World("mov", f)
    # Find a tick at which (5, 6) wins in the unperturbed world, so that
    # disabling it changes (5, 4)'s outcome.
    tick = next(t for t in range(1, 200)
                if _winner_is_east(f, t))
    dist = P.manhattan_from(n, 5, 6)
    _rows, ok = P.pair_run(w, (5, 6), K.OPCODE, 0, QUIET, tick - 1, 1, dist)
    assert ok["locality_violations"] == 0 and ok["max_generation"] == 1
    saved = P.RADIUS.pop("mov")
    try:
        _rows, bad = P.pair_run(w, (5, 6), K.OPCODE, 0, QUIET, tick - 1, 1, dist)
    finally:
        P.RADIUS["mov"] = saved
    assert bad["locality_violations"] >= 1


def _winner_is_east(f, tick):
    from observatory import aeth03_variants as V
    out = V.step("mov", H=16, W=16, tick=tick, opcode=f[0], arg0=f[1],
                 arg1=f[2], payload=f[3], energy=f[4], **QUIET)
    return out[3][5, 6] == 0 and out[3][5, 4] == 40
