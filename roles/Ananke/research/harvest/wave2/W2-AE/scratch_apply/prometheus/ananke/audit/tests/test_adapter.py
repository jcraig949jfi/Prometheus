"""PTE adapter tests (W2-F test_pte_adapter.py, promoted): each explib primitive reproduces a real PTE historical
failure on the real engine or on real recorded data. CPU only."""
from __future__ import annotations

import csv
import gzip
import json
import pathlib

import numpy as np
import pytest

from prometheus.ananke import assays, c1b, envs, lens, plants
from prometheus.ananke.audit import adapter as A
from prometheus.ananke.audit import trace as HI
from prometheus.ananke.audit.tests._data import REPO
from prometheus.explib.authority import check_authority
from prometheus.explib.controls import FORCED, data_identity, identity_audit, mirror_identity
from prometheus.explib.outcomes import FAIL, PASS
from prometheus.explib.reach import ABSORBED, NOT_REACHED, REACHED, UNAPPLIED
from prometheus.explib.stats import replication_label
SEEDS = assays.world_seeds(0x7E57, 16)
M = len(SEEDS)
HOLD = envs.EnvSpec(family="HOLD", gap=8, cue_len=2, trials=12)
TK = c1b.ticks(HOLD)
K = 5


def latch_hooks():
    import torch
    ph = plants.c1b_echo_physics().replace(prog_len=12, payload_width=1)
    g = plants.plant("hold_latch", ph)
    ep = envs.build(ph, HOLD, SEEDS)
    ridx = ep.schedule.read_idx[:, 0]
    BI = torch.arange(M)

    def s1_readout(w):
        w.S[BI, ridx, 1] += 7

    def s0_elsewhere(w):
        m = torch.ones(M, w.N, dtype=torch.bool)
        m[BI, ridx] = False
        w.S[..., 0][m] += 7
    return ph, g, {"swap_S": lambda w: lens.swap(w, ["S"]), "s1_readout": s1_readout,
                   "s0_elsewhere": s0_elsewhere, "swap_w": lambda w: lens.swap(w, ["w"])}


def test_P1_reach_matches_HINST_and_applied_is_not_reached():
    """(1) on PTE: explib's certificate reproduces H-INST's four verdicts on hold_latch, and the
    lens.verify_reach failure (applied_ticks > 0, NOT_VERIFIED) is certified NOT_REACHED."""
    ph, g, H = latch_hooks()
    mid = TK["mid"][K]
    want = {"swap_S": REACHED, "s1_readout": ABSORBED, "s0_elsewhere": NOT_REACHED, "swap_w": UNAPPLIED}
    for name, h in H.items():
        r = A.reach(ph, g, HOLD, SEEDS, {mid: h}, K)
        hi = HI.reach_certificate(ph, g, HOLD, SEEDS, {mid: h}, K)["verdict"].replace("REACHED_OUTPUT", REACHED)
        assert r["verdict"] == want[name] == hi, (name, r["verdict"], hi)
        assert r["closure"] == PASS
    assert A.reach(ph, g, HOLD, SEEDS, {mid: H["swap_S"]}, K)["path"] == {"LOCAL": M}
    assert lens.applied_ticks(ph, g, HOLD, SEEDS, hooks={mid: H["s0_elsewhere"]}) > 0
    assert lens.verify_reach((ph, g, HOLD), None, SEEDS, hooks={mid: H["s0_elsewhere"]})["reach"] == "NOT_VERIFIED"


def test_P2_P3_closure_cone_and_authority_on_PTE():
    """(2)+(3) on PTE: echo twin closure PASS with an exact 2-hop cone and a single ENV leaf; route_relay's
    declared authority (w only from SENSE, S only from arrivals) holds and a wrong declaration fails."""
    ph = plants.c1b_echo_physics()
    dt, ep = HI.twin_trace(ph, plants.echo_hold(ph), HOLD, SEEDS, trial=K)
    rec = A.record_from_difftrace(dt)
    assert rec.closure()["outcome"] == PASS
    b = 0
    a = int(ep.schedule.read_idx[b, 0])
    rt = int(ep.ro_tick[b, K])
    mine, theirs = rec.cone(b, a, rt), dt.cone(b, a, rt)
    assert mine["edges"] == theirs["edges"] and len(mine["edges"]) == 4
    assert {l[0] for l in mine["leaves"]} == {"ENV"} and len(mine["leaves"]) == 1
    assert rec.path_class(rt, b, a) == "TRANSPORTED"
    phr = plants.c1b_route_physics()
    env = envs.EnvSpec(family="RELAY", d=2, delta=8, cue_len=4, trials=12)
    dtr, _ = HI.twin_trace(phr, plants.route_relay(phr)[None], env, SEEDS, trial=3)
    causes = A.record_from_difftrace(dtr).component_causes()
    assert causes["outcome"] == PASS
    ok = check_authority(causes["causes"], {"w": {"SENSED"}, "S": {"TRANSPORTED"}, "inbox": {"TRANSPORTED"},
                                            "E": {"SENSED", "TRANSPORTED", "CARRIED"}, "Kp": set(), "r": set()})
    assert ok.outcome == PASS, ok.detail
    bad = check_authority(causes["causes"], {"w": {"TRANSPORTED"}, "S": {"TRANSPORTED"}, "inbox": {"TRANSPORTED"},
                                             "E": {"SENSED", "TRANSPORTED", "CARRIED"}})
    assert bad.outcome == FAIL


def test_P4_identity_audit_flags_zero_comm_on_PTE_mirror_pairs():
    """(4) HISTORICAL, real engine: zero_comm on relay_flood (RELAY, actuator != sensor) gives readouts that are
    identical within every mirror pair while targets are negated -> pair accuracy exactly .5 whatever the
    program does: A3 mirror identity FAILS. hold_latch on HOLD (actuator = sensor) under zero_comm keeps
    following the cue: no identity."""
    from prometheus.ananke.engine import Controls
    ph = plants.c1b_da_physics()
    relay = envs.EnvSpec(family="RELAY", d=1, delta=4, cue_len=2, trials=12, iti=50)
    g = plants.plant("relay_flood", ph)
    zc = A.pair_table(ph, g, relay, SEEDS, ctrl=Controls(zero_comm=True))
    nm = A.pair_table(ph, g, relay, SEEDS)
    assert A.table_accuracy(nm) > 0.9 and A.table_accuracy(zc) == 0.5
    assert mirror_identity(zc["outputs"], zc["targets"]).outcome == FAIL
    phl = plants.c1b_echo_physics().replace(prog_len=12, payload_width=1)
    zl = A.pair_table(phl, plants.plant("hold_latch", phl), HOLD, SEEDS, ctrl=Controls(zero_comm=True))
    assert A.table_accuracy(zl) == 1.0 and mirror_identity(zl["outputs"], zl["targets"]).outcome == PASS


ROWS = REPO / "roles/Ananke/pte/c1_rows/cells.jsonl.gz"


@pytest.mark.skipif(not ROWS.exists(), reason="C1 rows not present")
def test_P4_identity_audit_on_real_C1_rows():
    """(4) HISTORICAL, real rows: zero_comm is exactly .500 in 213/213 RELAY, 174/174 MAJ, 95/95 XOR rows while
    held accuracy reaches .91 / .79: FORCED (A2). In HOLD rows it spans .49-1.0: not constant."""
    rows = [json.loads(l) for l in gzip.open(ROWS, "rt")]
    n = {}
    for fam in ("RELAY", "MAJ", "XOR", "HOLD"):
        c, t = A.zero_comm_panel(rows, fam)
        n[fam] = (len(c), sum(v == 0.5 for v in c.values()))
        r = identity_audit(control_stats=c, treatment_stats=t if fam != "XOR" else None)
        a2 = {x["name"]: x["outcome"] for x in r["checks"]}["A2_not_constant"]
        assert (a2 == FAIL and r["verdict"] == FORCED) if fam != "HOLD" else a2 == PASS, (fam, r)
    assert n["RELAY"] == (213, 213) and n["MAJ"] == (174, 174) and n["XOR"] == (95, 95)


WZ = REPO / "roles/Ananke/research/workers/W-Z/out"


@pytest.mark.skipif(not (WZ / "pairs").exists(), reason="W-Z pair arrays not present")
def test_P4_site_plus_channel_identity_in_real_W_Z_pairs_and_P9_margins_with_swap_rel():
    """(4) W-M's forced relation in REAL data. For RELAY and MAJ groups swapped at offset >= 1 (after the cue,
    so mirror partners receive identical inputs from the swap tick on: H-CHK C3), the site_all and channel_all
    swap scores sum to the maximum at EVERY (pair, trial) in all 93 groups: a design identity, so their
    agreement is not evidence. At offset <= 0 (cue still arriving) it fails in all 13 groups.
    (9) the promoted swap_rel H2 intervals reproduce all 301 W-Z certificates, and the predictive replication
    rule at inflation 2 flags all 20 certified rows that flipped against W-U."""
    groups = {r["gid"]: r for r in csv.DictReader(open(WZ / "group_table.csv"))}
    after, during = {}, {}
    for f in sorted((WZ / "pairs").glob("*.npz")):
        d = np.load(f)
        g = groups.get(f.stem)
        if g and g["family"] in ("RELAY", "MAJ") and "s__site_all" in d.files and "s__channel_all" in d.files:
            arr = (d["s__site_all"].astype(int), d["s__channel_all"].astype(int))
            (after if int(g["offset"]) >= 1 else during)[f.stem] = arr
    di = data_identity(after, lambda a, b: (a + b) == 4)
    assert di["specimens"] == 93 and di["flag"] == "IDENTITY_SUSPECTED"
    dd = data_identity(during, lambda a, b: (a + b) == 4)
    assert dd["specimens"] == 13 and dd["elementwise_hold_fraction"] == 0.0
    rs = list(csv.DictReader(open(WZ / "row_table.csv")))
    det = [r for r in rs if r["WU_status"] == "DETERMINED" and r["new_certificate"]]
    mism = flagged = flips = 0
    for r in det:
        d = np.load(WZ / "pairs" / (r["gid"] + ".npz"))
        a = d["a__" + r["arm"]].astype(float).mean(1) / 4
        s = d["s__" + r["arm"]].astype(float).mean(1) / 4
        ci, v = A.swap_rel_ci(a, s, d["a__" + r["arm"]].shape[1], r["new_certificate"])
        mism += v != r["new_certificate"]
        if r["WU_rel3"] != r["new_certificate"] and v != "INDETERMINATE":
            flips += 1
            flagged += replication_label(ci, [0], 1, p_min=0.95, inflation=2.0) == "MARGINAL"
    assert mism == 0 and flips == 20 and flagged == 20
