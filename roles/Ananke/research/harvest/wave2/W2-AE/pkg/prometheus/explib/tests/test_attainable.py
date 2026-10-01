"""(6) Attainable-range certification of a gate (null, adversary, ceiling/eligibility, attainable labels).
Core only: no PTE import (the light-cone census is read as plain JSON data)."""
from __future__ import annotations

import json
import math
import pathlib

import numpy as np
import pytest

from prometheus.explib.attainable import attainable_labels, certify_gate, eligibility
from prometheus.explib.outcomes import FAIL, PASS

from prometheus.explib.tests._paths import REPO  # noqa: E402
LC = REPO / "roles/Ananke/research/harvest/H-PLANT/out/lc_census.json"
P, K = 128, 12


def xor_mirror(rng):
    """Mirror pairs negate x1 only; target = XNOR(flag1, flag2) as +-1 (the partner's target is negated)."""
    x1 = rng.choice([-1, 1], size=(P, K))
    x2 = rng.choice([-1, 1], size=(P, K))
    X1 = np.stack([x1, -x1], 1).reshape(2 * P, K)
    X2 = np.stack([x2, x2], 1).reshape(2 * P, K)
    return X1, X2, X1 * X2


def stat(out, y):
    pm = ((np.sign(out) == y).mean(-1)).reshape(P, 2).mean(-1)
    m, sd = pm.mean(), pm.std(ddof=1)
    return {"acc": float(m), "lo99": float(m - 2.576 * sd / math.sqrt(P))}


GATE_C1 = lambda s: s["lo99"] > 0.55                     # C1 SIGNAL rule
GATE_TWIN = lambda s: s["lo99"] > 0.80                   # beats every 2-input non-XOR boolean rule (max .75)


def null_sampler(rng):
    X1, X2, y = xor_mirror(rng)
    return stat(rng.choice([-1, 1], size=y.shape), y)


def adversaries():
    rng = np.random.default_rng(7)
    X1, X2, y = xor_mirror(rng)
    nor = np.where((X1 < 0) & (X2 < 0), 1, -1)           # "+ iff no + cue" (H-PLANT's one-flag readout)
    return {"nor_one_flag": stat(nor, y), "x2_only": stat(X2, y), "constant": stat(np.ones_like(y), y)}


def plants():
    rng = np.random.default_rng(8)
    X1, X2, y = xor_mirror(rng)
    return {"xor_exact": stat(X1 * X2, y)}


def test_one_flag_readout_games_the_C1_XOR_gate():
    """HISTORICAL (H-PLANT disagreement 4): a one-flag readout scores ~.76 on XOR at X0 and passes C1's
    SIGNAL rule (lo99 > .55) without computing XOR. The certifier flags the gate (G2 adversary) while its
    null pass rate is fine; the twin gate that must beat every non-XOR rule is certified."""
    adv = adversaries()
    assert 0.70 < adv["nor_one_flag"]["acc"] < 0.80
    r = certify_gate(GATE_C1, null_sampler=null_sampler, adversaries=adv, ceilings={"X0": 1.0}, threshold=0.55,
                     n_null=300)
    by = {c["name"]: c for c in r["checks"]}
    assert by["G1_null"]["outcome"] == PASS
    assert by["G2_adversary"]["outcome"] == FAIL and by["G2_adversary"]["detail"]["passers"] == ["nor_one_flag"]
    assert r["verdict"] == "FLAGGED"
    twin = certify_gate(GATE_TWIN, null_sampler=null_sampler, adversaries=adv, plants=plants(),
                        ceilings={"X0": 1.0}, threshold=0.80, n_null=300)
    assert twin["verdict"] == "CERTIFIED", twin["checks"]
    # fail-closed: no adversary set (or no plant) -> NOT_VERIFIED, never CERTIFIED
    assert certify_gate(GATE_TWIN, null_sampler=null_sampler, plants=plants(), ceilings={"X0": 1.0},
                        threshold=0.8, n_null=300)["verdict"] == "NOT_VERIFIED"
    assert certify_gate(GATE_TWIN, null_sampler=null_sampler, adversaries=adv, ceilings={"X0": 1.0},
                        threshold=0.8, n_null=300)["verdict"] == "NOT_VERIFIED"
    # MUST-FAIL: a gate no plant can pass (lo99 > 1) is FLAGGED by G3, not certified
    imp = certify_gate(lambda s: s["lo99"] > 1.0, null_sampler=null_sampler, adversaries=adv, plants=plants(),
                       ceilings={"X0": 1.0}, threshold=1.0, n_null=300)
    assert {c["name"]: c["outcome"] for c in imp["checks"]}["G3_positive"] == FAIL


@pytest.mark.skipif(not LC.exists(), reason="H-PLANT light-cone census not present")
def test_P3_zero_XOR_signal_is_ineligible_on_rings():
    """HISTORICAL (P-1a, H-PLANT A7): P3 "zero XOR SIGNAL" was confirmed over rows where no program can reach
    the gate. Using the committed light-cone bounds as per-cell ceilings: rings have 2 of 19 eligible cells
    (bound > .55), global 81 of 81. With a minimum of 10 eligible cells for a zero-count claim, the ring
    stratum's NULL is uninformative by design."""
    rows = [r for r in json.loads(LC.read_text())["rows"] if r["family"] == "XOR"]
    ring = {r["cell"]: r["bound"] for r in rows if r["topology"] == "ring"}
    glob = {r["cell"]: r["bound"] for r in rows if r["topology"] == "global"}
    er = eligibility(ring, 0.55, min_eligible=10)
    eg = eligibility(glob, 0.55, min_eligible=10)
    assert er.outcome == FAIL and er.detail["cells"] == 19 and er.detail["eligible"] == 2
    assert eg.outcome == PASS and eg.detail["eligible"] == 81


def test_attainable_labels_harmonia_RA_compatible():
    """R-A semantics (Tyche v0 H1 with 3 valid worlds: PASS unreachable); the 4-valid twin reaches PASS."""
    def h1(valid):
        return lambda x: "PASS" if valid >= 4 and x["solved"] >= 4 else ("FAIL" if x["solved"] <= 1 else "INDETERMINATE")
    space = [{"solved": s} for s in range(7)]
    assert attainable_labels(h1(3), space, ["PASS"])["unreachable_gated"] == ["PASS"]
    assert attainable_labels(h1(4), space, ["PASS"])["flag"] is False


MF = REPO / "roles/Ananke/research/harvest/H-PLANT/out/xor_mf.json"


@pytest.mark.skipif(not MF.exists(), reason="H-PLANT xor_mf.json not present")
def test_real_one_flag_readout_number_games_C1_XOR_SIGNAL():
    """Same failure with the REAL measurement: H-PLANT's '+ iff P' readout scored .237 [.221, .252] at X0
    (M = 256, no ties), so its negation '+ iff no P' scores .763 with lo99 = 1 - .252 = .748 > .55."""
    d = json.loads(MF.read_text())["mf_xor_b_q_readout"]
    neg = {"acc": 1 - d["acc"], "lo99": 1 - d["hi99"]}
    r = certify_gate(GATE_C1, null_sampler=null_sampler, adversaries={"h_plant_not_P": neg}, ceilings={"X0": 1.0},
                     threshold=0.55, n_null=300)
    g2 = {c["name"]: c for c in r["checks"]}["G2_adversary"]
    assert g2["outcome"] == FAIL and g2["detail"]["passers"] == ["h_plant_not_P"] and r["verdict"] == "FLAGGED"
    assert not GATE_TWIN(neg)
