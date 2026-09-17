"""C3-SFE-09 -- CA MECHANISM, NOT USEFULNESS (campaign 3, slot 9; parent C2-SFE-09).

    python -m archaeon.campaign3.c3_sfe09 [--seeds 1 2 3 4] [--delay 2] [--dry-run]

What local mechanism produces particle2's delayed-recall margin? Campaign 2 localized it
(k50 = 1). With a FROZEN ridge readout fit on the intact substrate, this harness runs
interventions that can tell local storage, routed information, transient synchronization
and readout coincidence apart, per seed (partition + reset root):

  site          single-site lesion drops -> the responsible site s* (largest drop)
  phase         lesion s* at ONE time step t only, for each t -> which phase carries the margin
  predecessors  lesion each radius-3 neighbour of s* (all t); lesion the neighbour set at t*-1
                only; lesion s* at t*-1 only
  storage vs    LOCAL STORAGE if clamping s* at t*-1 alone removes >= half of the full-lesion
  routing       drop while clamping its neighbours at t*-1 removes < half of that; ROUTED if the
                reverse; the site's own margin: readout from s*'s feature column alone (all t)
  coincidence   readout from s* alone with the reset lattice PERMUTED across streams (the
                site's correlation with the target through position-keyed reset alone)
  minimum       greedy smallest set of (site, t) clamps removing >= 90% of the margin
  redundancy    refit the readout after lesioning s* at all t: recovered accuracy

Rules are preregistered; the product is an executable hypothesis (site, phase, dependence)
that a later run can falsify, not a name.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from herakles.ca_stream import core as cs
from herakles.ca_stream import reset_v2 as rv
from herakles.evca import genomes as GEN
from archaeon.campaign3.c3base import CAMPAIGN_SEED, Experiment3

N_CELLS, HORIZON = 31, 8
RESET_DENSITY = 0.5
TASK = "delayed_recall"
GENOMES = ["particle2", "particle1", "GKL"]


class ClampedCA(rv.NonUniformResetCaSubstrate):
    """Clamp (site, t) pairs to 0 AFTER the step at time t (the state and the feature)."""

    def __init__(self, *a, clamps: Sequence[Tuple[int, int]] = (), **kw):
        self.clamps = {}
        for s, t in clamps:
            self.clamps.setdefault(int(t), set()).add(int(s))
        self.t = 0
        super().__init__(*a, **kw)

    def reset(self) -> None:
        super().reset(); self.t = 0

    def step(self, bit: int) -> np.ndarray:
        f = super().step(bit)
        sites = self.clamps.get(self.t, set()) | self.clamps.get(-1, set())
        if sites:
            idx = sorted(sites)
            self.state[0, idx] = 0; f[idx] = 0.0
        self.t += 1
        return f


def feats(rule: str, streams: np.ndarray, positions, reset_root: int, clamps=()) -> np.ndarray:
    sub = ClampedCA(rule, N_CELLS, (0,), reset_density=RESET_DENSITY, reset_root=reset_root, clamps=clamps)
    f, _ = rv.run_streams_v2(sub, streams, positions)
    return f


def score(f, y, mask, w) -> float:
    return float(cs.score_readout(f, y, mask, w)["accuracy"])


def run_genome(job: dict) -> dict:
    name, seed, d = job["name"], job["seed"], job["delay"]
    t0 = time.time()
    rule = GEN.rule_hex(name)
    streams = cs.all_streams(HORIZON)
    parts = cs.partitions(len(streams), 64, 64, seed=CAMPAIGN_SEED + seed)
    tr, cf = parts["train"], parts["confirmation"]
    positions = np.arange(len(streams))
    y = cs.build_targets(streams, TASK, d); mask = cs.warmup_mask(HORIZON, TASK, d)
    reset_root = CAMPAIGN_SEED + seed
    f0 = feats(rule, streams, positions, reset_root)
    w = cs.fit_readout(f0[tr], y[tr], mask)
    base = score(f0[cf], y[cf], mask, w)
    margin = base - 0.5
    row: Dict = {"arm": name, "seed": seed, "base_acc": round(base, 4), "margin": round(margin, 4)}
    if margin < 0.02:
        row.update({"informative": False, "wall_s": round(time.time() - t0, 1)})
        return row
    cfS, cfP = streams[cf], positions[cf]
    # 1. responsible site
    single = {}
    for s in range(N_CELLS):
        single[s] = base - score(feats(rule, cfS, cfP, reset_root, clamps=[(s, -1)]), y[cf], mask, w)
    s_star = max(single, key=single.get)
    full_drop = single[s_star]
    # 2. phase: clamp s* at one t
    phase = {t: round(base - score(feats(rule, cfS, cfP, reset_root, clamps=[(s_star, t)]), y[cf], mask, w), 4) for t in range(HORIZON)}
    t_star = max(phase, key=phase.get)
    # 3. predecessors (radius 3) and timing
    nbrs = [(s_star + k) % N_CELLS for k in (-3, -2, -1, 1, 2, 3)]
    nb_drop = {int(s): round(base - score(feats(rule, cfS, cfP, reset_root, clamps=[(s, -1)]), y[cf], mask, w), 4) for s in nbrs}
    nb_set_tm1 = base - score(feats(rule, cfS, cfP, reset_root, clamps=[(s, t_star - 1) for s in nbrs] if t_star > 0 else []), y[cf], mask, w) if t_star > 0 else 0.0
    self_tm1 = base - score(feats(rule, cfS, cfP, reset_root, clamps=[(s_star, t_star - 1)]), y[cf], mask, w) if t_star > 0 else 0.0
    self_t = phase[t_star]
    # site-alone readouts
    col = f0[:, :, [s_star]]
    w1 = cs.fit_readout(col[tr], y[tr], mask); alone = score(col[cf], y[cf], mask, w1)
    rng = np.random.default_rng(CAMPAIGN_SEED * 3 + seed)
    perm = rng.permutation(len(streams))
    f_perm = feats(rule, streams, positions[perm], reset_root)               # reset lattice of another position, same input
    colp = f_perm[:, :, [s_star]]
    wp = cs.fit_readout(colp[tr], y[tr], mask); alone_perm = score(colp[cf], y[cf], mask, wp)
    # 4. minimum causal lesion (greedy over (site, t) pairs among s* and its neighbours)
    cands = [(s, t) for s in [s_star] + nbrs for t in range(HORIZON)]
    chosen: List[Tuple[int, int]] = []; cur_drop = 0.0
    while cur_drop < 0.9 * full_drop and len(chosen) < 6:
        best = None
        for c in cands:
            if c in chosen:
                continue
            dr = base - score(feats(rule, cfS, cfP, reset_root, clamps=chosen + [c]), y[cf], mask, w)
            if best is None or dr > best[0]:
                best = (dr, c)
        if best is None or best[0] <= cur_drop + 1e-6:
            break
        cur_drop = best[0]; chosen.append(best[1])
    # 5. redundancy: refit after lesioning s* at all t
    fl_tr = feats(rule, streams[tr], positions[tr], reset_root, clamps=[(s_star, -1)]); fl_cf = feats(rule, cfS, cfP, reset_root, clamps=[(s_star, -1)])
    w2 = cs.fit_readout(fl_tr, y[tr], mask); recovered = score(fl_cf, y[cf], mask, w2)
    # rules
    local_storage = self_tm1 >= 0.5 * full_drop and nb_set_tm1 < 0.5 * self_tm1 if full_drop > 0 else False
    routed = nb_set_tm1 >= 0.5 * full_drop and self_tm1 < 0.5 * nb_set_tm1 if full_drop > 0 else False
    coincidence = alone_perm >= alone - 0.02 and alone > 0.52
    row.update({"informative": True, "site": int(s_star), "site_drop": round(full_drop, 4), "site_drop_share_of_margin": round(full_drop / margin, 4),
                "phase_drops": phase, "t_star": int(t_star), "phase_share": round(phase[t_star] / max(full_drop, 1e-9), 4),
                "neighbour_drops": nb_drop, "neighbour_set_tm1_drop": round(nb_set_tm1, 4), "self_tm1_drop": round(self_tm1, 4), "self_t_drop": round(self_t, 4),
                "alone_acc": round(alone, 4), "alone_permuted_reset_acc": round(alone_perm, 4), "min_lesion": chosen, "min_lesion_drop": round(cur_drop, 4),
                "recovered_after_refit": round(recovered, 4), "recovery_share": round((recovered - 0.5) / margin, 4),
                "flag_local_storage": bool(local_storage), "flag_routed": bool(routed), "flag_coincidence": bool(coincidence),
                "flag_redundant": bool(recovered - 0.5 >= 0.5 * margin), "wall_s": round(time.time() - t0, 1)})
    return row


class CAMechanism(Experiment3):
    ID = "C3-SFE-09"
    TITLE = "CA mechanism, not usefulness"
    PARENTS = ["C2-SFE-09", "SFE-04"]
    METRICS = ("base_acc", "site", "t_star", "self_tm1_drop", "neighbour_set_tm1_drop", "alone_acc", "alone_permuted_reset_acc", "recovery_share")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=[1, 2, 3, 4])
    ap.add_argument("--delay", type=int, default=2)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    X = CAMechanism(dry_run=a.dry_run, procs=a.procs)
    X.seal({
        "question": "Which site and time step of particle2 carry its delayed-recall (d=%d) margin, and does that site STORE the delayed bit (clamping it one step earlier "
                    "removes the margin) or EXPOSE information computed by its radius-3 predecessors (clamping them one step earlier removes it)? Same probes on particle1 and GKL." % a.delay,
        "parent_evidence": "C2-SFE-09 (n=4): particle2 0.54-0.61 vs random 0.50; not a reset artifact (reset-only < chance), not a dynamical bias (time shuffle removes it), "
                           "input-dependent; LOCALIZED with k50 = 1 in 11/12 rows.",
        "why_this_slot": "Usefulness has been measured twice; the campaign asks for one evolved computational effect reduced to a falsifiable local mechanism, and the "
                         "single-site localization makes this the cheapest such reduction available.",
        "assay_capability_requirement": "the frozen readout's margin on the confirmation set >= 0.02 for particle2 in >= 3 of %d seeds (rows below are marked uninformative)" % len(a.seeds),
        "positive_control": "the full single-site lesion drop reproduces campaign 2's localization (site_drop >= 0.5 x margin)",
        "reachability_estimate": {"note": "not a WSE cell; the reachability table does not apply"},
        "arms": GENOMES,
        "crn_policy": "per seed one partition and reset root shared by every genome; permutation for the coincidence probe drawn once per seed",
        "budget": {"seeds": a.seeds, "delay": a.delay, "n_cells": N_CELLS, "horizon": HORIZON, "reset_density": RESET_DENSITY, "min_lesion_max": 6},
        "primary_observable": "per genome x seed: site s*, phase t*, self_tm1_drop vs neighbour_set_tm1_drop (storage vs routing), site-alone readout with and without reset "
                              "permutation (coincidence), minimum causal lesion, recovery after refit; primary: particle2 - GKL on site_drop_share_of_margin (are the two "
                              "mechanisms equally localized?)",
        "claim_ceiling": "an executable hypothesis for particle2 at d=%d on this catalogue; n=%d seeds" % (a.delay, len(a.seeds)),
        "falsification_condition": "if neither flag_local_storage nor flag_routed holds in >= 3/4 seeds for particle2, the mechanism is not one of the two named classes "
                                   "(reported as such); flag_coincidence in >= 3/4 seeds kills the 'computation' reading",
        "kill_condition": "margin < 0.02 in > 1 seed for particle2 (assay uninformative)",
        "typed_failure_conditions": ["UNDERPOWERED", "INSTRUMENT_FAILURE"],
        "expected_machine_telemetry": ["single-site drops", "phase drops", "neighbour drops", "minimum lesion sets", "site-alone readouts", "recovery after refit"],
        "replacement_condition": "none",
        "ancestry": "original (queue slot 9)",
        "machine_changes_exercised": ["H (probes)", "I"],
        "decl": {"n_min": len(a.seeds), "primary": {"treatment": "particle2", "control": "GKL", "metric": "site_drop_share_of_margin", "min_effect": 0.1}},
    })
    X.decision("D3-012: storage vs routing decided by clamps ONE STEP BEFORE the critical phase (self at t*-1 vs radius-3 neighbours at t*-1), each against the full single-site drop; coincidence by the site-alone readout under a permuted reset lattice")
    X.open("cmp3-sfe09")
    wid = X.world("ca", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    jobs = [{"name": n, "seed": s, "delay": a.delay} for s in a.seeds for n in GENOMES]
    rows = X.pool_map(run_genome, jobs, "mechanism_s")
    t0 = time.time()
    for r in rows:
        X.record(wid, r, {"experiment": X.ID, "genome": r["arm"], "seed": r["seed"], "delay": a.delay, "prereg_digest": X.prereg["prereg_digest"]},
                 {k: v for k, v in r.items() if k not in ("phase_drops", "neighbour_drops")}, "SURVIVED" if r.get("informative") else "FALSIFIED", (r["arm"], r["seed"]))
    X.att.timing("records_s", t0)
    summ = {}
    for n in GENOMES:
        rs = [r for r in rows if r["arm"] == n and r.get("informative")]
        summ[n] = {"informative": len(rs), "sites": [r["site"] for r in rs], "t_star": [r["t_star"] for r in rs], "site_drop_share": [r["site_drop_share_of_margin"] for r in rs],
                   "self_tm1": [r["self_tm1_drop"] for r in rs], "nb_tm1": [r["neighbour_set_tm1_drop"] for r in rs], "alone": [r["alone_acc"] for r in rs],
                   "alone_perm": [r["alone_permuted_reset_acc"] for r in rs], "recovery": [r["recovery_share"] for r in rs],
                   "flags": {f: sum(1 for r in rs if r.get(f)) for f in ("flag_local_storage", "flag_routed", "flag_coincidence", "flag_redundant")},
                   "min_lesion": [r["min_lesion"] for r in rs]}
    X.receipt["summary"] = summ
    out = X.close(rows)
    print(json.dumps({"summary": summ, **out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
