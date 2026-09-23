"""Substrate contract tests: replay, controls, declared coordinates, unit invariance."""
import numpy as np
import pytest

from prometheus.cosmos.contract import COORDS, MECHANISMS
from prometheus.cosmos.substrates import visible
from prometheus.cosmos.world import evaluate

FAMS = visible()
BASE = {
    "regs": dict(V=8, H=16, K=4, R=1.0, bitcost=4e-3, q=0.003),
    "ring": dict(V=8, H=12, K=4, R=1.0, s=1, n=64, ehop=1.6e-2, lam=0.006),
    "ca": dict(V=8, H=20, K=4, R=2.0, r=1, Lc=510, ccell=1e-2, p=0.0015),
}
COST_KNOB = {"regs": "bitcost", "ring": "ehop", "ca": "ccell"}
NOISE_KNOB = {"regs": "q", "ring": "lam", "ca": "p"}


@pytest.mark.parametrize("name", sorted(FAMS))
def test_replay_is_bit_identical(name):
    a, b = evaluate(FAMS[name], BASE[name]), evaluate(FAMS[name], BASE[name])
    assert a["obs_digest"] == b["obs_digest"]
    c = evaluate(FAMS[name], BASE[name], replicate=1)
    assert c["obs_digest"] != a["obs_digest"], "replicates must draw fresh episodes"


@pytest.mark.parametrize("name", sorted(FAMS))
def test_sham_control_never_pays(name):
    fam = FAMS[name]
    for cost in fam.space()[COST_KNOB[name]][:3]:
        p = dict(BASE[name], **{COST_KNOB[name]: cost, NOISE_KNOB[name]: 0.0})
        r = evaluate(fam, fam.sham(p))
        assert r["verdict"] == "QUIET", (p, r["margin"])
        assert abs(r["acc"]["SEL"] - 1 / p["V"]) < 0.08


@pytest.mark.parametrize("name", sorted(FAMS))
def test_positive_control_clean_twin_remembers(name):
    fam = FAMS[name]
    p = dict(BASE[name], **{COST_KNOB[name]: fam.space()[COST_KNOB[name]][0], NOISE_KNOB[name]: 0.0})
    r = evaluate(fam, p)
    assert r["acc"]["SEL"] >= 0.99
    assert r["acc"]["LAST"] < 0.25


@pytest.mark.parametrize("name", sorted(FAMS))
def test_zero_cost_logger_ties_and_high_cost_memory_loses(name):
    fam = FAMS[name]
    p0 = dict(BASE[name], **{COST_KNOB[name]: 0.0, NOISE_KNOB[name]: 0.0})
    r0 = evaluate(fam, p0)
    assert abs(r0["fitness"]["SEL"] - r0["fitness"]["LOG"]) < 1e-9 or r0["acc"]["LOG"] < r0["acc"]["SEL"]
    hi = dict(BASE[name], **{COST_KNOB[name]: fam.space()[COST_KNOB[name]][-1] * 4})
    assert evaluate(fam, hi)["verdict"] == "QUIET"


@pytest.mark.parametrize("name", sorted(FAMS))
def test_coords_are_declared_from_spec_only(name):
    fam = FAMS[name]
    c = fam.coords(BASE[name])
    assert set(c) == set(COORDS)
    assert all(np.isfinite(v) and v >= 0 for v in c.values())


@pytest.mark.parametrize("name", sorted(FAMS))
def test_currency_rescaling_is_exactly_invariant(name):
    """Multiplying the reward unit and the cost rate by the same factor must not change normalized fitness."""
    fam = FAMS[name]
    p = BASE[name]
    q = dict(p, R=p["R"] * 7.0, **{COST_KNOB[name]: p[COST_KNOB[name]] * 7.0})
    for m in MECHANISMS:
        a, b = fam.run(p, m, 123, 200), fam.run(q, m, 123, 200)
        fa = (a["reward"] - a["cost"]) / p["R"]
        fb = (b["reward"] - b["cost"]) / q["R"]
        assert np.allclose(fa, fb)
    assert fam.coords(p) == pytest.approx(fam.coords(q))


@pytest.mark.parametrize("name", sorted(FAMS))
def test_coord_preserving_variants_really_preserve_declared_coords(name):
    fam = FAMS[name]
    c0 = fam.coords(BASE[name])
    vs = fam.coord_preserving(BASE[name], np.random.default_rng(0))
    assert vs
    for v in vs:
        assert fam.coords(v) == pytest.approx(c0, rel=1e-9, abs=1e-12)
        assert v != BASE[name]


def test_ca_redundancy_repairs():
    """r=3 with majority repair must beat r=1 at the same per-cell flip rate (physics sanity)."""
    fam = FAMS["ca"]
    p1 = dict(BASE["ca"], p=0.015, r=1, ccell=0.0)
    p3 = dict(p1, r=3)
    assert evaluate(fam, p3)["acc"]["SEL"] > evaluate(fam, p1)["acc"]["SEL"] + 0.2


def test_ring_capacity_evicts_the_logger_cue():
    fam = FAMS["ring"]
    p = dict(BASE["ring"], n=3, K=5, lam=0.0, ehop=0.0)
    r = evaluate(fam, p)
    assert r["acc"]["SEL"] > 0.99 and r["acc"]["LOG"] < 0.3


def test_v3_capacity_coordinate():
    from prometheus.cosmos.contract import coords_of
    assert coords_of(FAMS["regs"], BASE["regs"], "v3")["Q"] == 1.0            # unbounded registers
    assert coords_of(FAMS["ring"], dict(BASE["ring"], n=3, K=5), "v3")["Q"] == 0.5
    assert coords_of(FAMS["ring"], dict(BASE["ring"], n=64), "v3")["Q"] == 1.0
    ca = dict(BASE["ca"], V=16, r=3, Lc=24, K=4)                                  # 12 cells/symbol -> 2 slots
    assert coords_of(FAMS["ca"], ca, "v3")["Q"] == 2 / 5
    assert coords_of(FAMS["ca"], ca, "v3")["N"] == FAMS["ca"].coords(ca, "v2")["N"]


@pytest.mark.parametrize("name", sorted(FAMS))
def test_matched_pair_on_common_random_numbers_is_exactly_monotone_in_cost(name):
    fam = FAMS[name]
    p = BASE[name]
    q = dict(p, **{COST_KNOB[name]: p[COST_KNOB[name]] * 2})
    a = evaluate(fam, p)
    b = evaluate(fam, q, seed_key=a["world_id"])
    assert b["acc"]["SEL"] == a["acc"]["SEL"]               # same random numbers: cost does not touch dynamics
    assert b["fitness"]["SEL"] < a["fitness"]["SEL"]


def test_v4_expected_cost_matches_the_ring_meter():
    """v4 declares the ring's expected SEL cost exactly: compare with the metered cost of SEL."""
    from prometheus.cosmos.contract import coords_of
    fam = FAMS["ring"]
    p = dict(BASE["ring"], lam=0.05, s=3, H=12, ehop=0.01, R=1.0)
    c4 = coords_of(fam, p, "v4")["C"]
    metered = fam.run(p, "SEL", 7, 20000)["cost"].mean() / p["R"]
    assert abs(c4 - metered) / metered < 0.02
    assert coords_of(fam, p, "v3")["C"] > c4 * 1.5
    assert coords_of(FAMS["regs"], BASE["regs"], "v4") == coords_of(FAMS["regs"], BASE["regs"], "v3")
