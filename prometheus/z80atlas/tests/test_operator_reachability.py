"""Tests for geometry.scan_operators / scan_moves / sample_paths (BEL-RD-72): neighbourhood sizes, known routes, and the
BEL-48H fragment whose substitution and move neighbourhoods differ."""
from prometheus.z80atlas import geometry, vm


def _pad(b, L=64):
    return bytes(b[:L]) + bytes(max(0, L - len(b)))


def test_neighbourhood_sizes():
    t = _pad(vm.replicator(64))
    sizes = {op: sum(1 for _ in geometry.operator_neighbours(t, op, 64)) for op in ("SUB", "MOVE", "INS", "DEL")}
    assert sizes == {"SUB": 64 * 255, "MOVE": 50512, "INS": 64 * 256, "DEL": 64}
    assert sum(1 for _ in geometry.operator_neighbours(t, "DONOR", 64, donors=[t])) == 50512 + 64 * 16 - sum(range(16))


def test_known_routes_and_operator_relativity():
    rep = _pad(vm.replicator(64))
    is_rep = lambda u: u == rep
    broken = bytearray(rep); broken[6] = 0                             # LDIR knocked out
    assert geometry.scan_operators(bytes(broken), 64, is_rep, ops=("SUB",))["SUB"]["routes"] == 1
    shifted = bytes([0]) + rep[:63]                                     # replicator shifted right by one
    r = geometry.scan_operators(shifted, 64, is_rep, ops=("SUB", "DEL"))
    assert r["DEL"]["routes"] == 1 and r["SUB"]["routes"] == 0          # one deletion, not reachable by one substitution
    m = geometry.scan_moves(shifted, 64, is_rep)
    assert m["SUB"]["routes"] == 0 and m["MOVE"]["routes"] >= 1         # a segment move restores it


def test_donor_and_sampler_are_deterministic():
    rep = _pad(vm.replicator(64)); half = rep[:4] + bytes(60)
    r = geometry.scan_operators(half, 64, lambda u: u == rep, ops=("DONOR",), donors=[rep])
    assert r["DONOR"]["routes"] >= 1
    a = geometry.sample_paths(half, 64, lambda u: u[:8] == rep[:8], depth=2, n=300, seed=3)
    b = geometry.sample_paths(half, 64, lambda u: u[:8] == rep[:8], depth=2, n=300, seed=3)
    assert a == b and a["n"] == 300


def test_sampler_donor_step_uses_one_donor():
    import random
    from prometheus.z80atlas.geometry import _random_neighbour
    short, long_ = bytes([0xAA] * 4), bytes([0xBB] * 64)
    rng = random.Random(0)
    for _ in range(500):
        u = _random_neighbour(bytes(64), "DONOR", 64, rng, donors=[short, long_])
        assert len(u) == 64 and not ({0xAA, 0xBB} <= set(u))           # never a mix of two donors in one step
