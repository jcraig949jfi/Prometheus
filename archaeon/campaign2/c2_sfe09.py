"""C2-SFE-09 -- CA SUBSTRATE: DISTRIBUTED vs REDUNDANT vs ARTIFACT (parent SFE-04).

    python -m archaeon.campaign2.c2_sfe09 [--seeds 1 2 3 4] [--delay 2] [--dry-run]

SFE-04 (campaign 1) read delayed recall at 0.608 (chance 0.5) from a radius-3 CA with
non-uniform reset, found a flat single-window lesion map, and called the computation
"distributed"; the reset-leakage probe was never wired (L-019). Four explanations are put
against each other with four measurements, all preregistered with their decision rules:

  readout artifact        reset-only readout (NO input injected) >= base - 0.02
  frozen dynamical bias   readout on TIME-SHUFFLED features (per stream) >= base - 0.02
  input-independent       readout on the CA driven by SHUFFLED input bits (targets kept) >= base - 0.02
  redundant-local vs      cumulative lesion curves: sites ordered by single-site drop (greedy)
  distributed             vs random orders; localization index LI = area between the curves
                          normalised by the base margin; LI >= 0.10 -> localized/redundant,
                          else distributed; k50 = greedy lesions to halve the margin

Rows: one per (substrate, partition seed): the six evolved CA genomes plus ShiftRegister
(perfect memory: the readout-capability control), DirectInput (no memory) and FrozenRandom
(readout-only control). Seeds vary the train/confirmation partition and the reset root.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Dict, List

import numpy as np

from herakles.ca_stream import core as cs
from herakles.ca_stream import reset_v2 as rv
from herakles.evca import genomes as GEN
from archaeon.campaign2.c2base import Experiment
from archaeon.campaign2.runner import CAMPAIGN_SEED

N_CELLS, HORIZON = 31, 8
RESET_DENSITY = 0.5
TASK = "delayed_recall"
EPS = 0.02
LI_MIN = 0.10
CONTROLS = ["shift", "direct", "random"]


class LesionedCA(rv.NonUniformResetCaSubstrate):
    def __init__(self, *a, lesion=(), **kw):
        self.lesion = tuple(int(i) for i in lesion)
        super().__init__(*a, **kw)

    def step(self, bit: int) -> np.ndarray:
        f = super().step(bit)
        if self.lesion:
            self.state[0, list(self.lesion)] = 0
            f[list(self.lesion)] = 0.0
        return f


def feats_ca(rule_hex: str, streams: np.ndarray, positions, reset_root: int, lesion=()) -> np.ndarray:
    sub = LesionedCA(rule_hex, N_CELLS, (0,), reset_density=RESET_DENSITY, reset_root=reset_root, lesion=lesion)
    f, _ = rv.run_streams_v2(sub, streams, positions)
    return f


def feats_plain(sub, streams: np.ndarray) -> np.ndarray:
    f, _ = cs.run_streams(sub, streams)
    return f


def acc(ftr, ytr, fcf, ycf, mask) -> float:
    w = cs.fit_readout(ftr, ytr, mask)
    return float(cs.score_readout(fcf, ycf, mask, w)["accuracy"])


def time_shuffle(f: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    out = f.copy()
    for i in range(f.shape[0]):
        out[i] = f[i][rng.permutation(f.shape[1])]
    return out


def run_substrate(job: dict) -> dict:
    name, seed, d = job["name"], job["seed"], job["delay"]
    t0 = time.time()
    streams = cs.all_streams(HORIZON)
    parts = cs.partitions(len(streams), 64, 64, seed=CAMPAIGN_SEED + seed)
    tr, cf = parts["train"], parts["confirmation"]
    positions = np.arange(len(streams))
    y = cs.build_targets(streams, TASK, d); mask = cs.warmup_mask(HORIZON, TASK, d)
    reset_root = CAMPAIGN_SEED + seed
    rng = np.random.default_rng(CAMPAIGN_SEED * 7 + seed)
    row: Dict = {"arm": name, "seed": seed, "kind": "ca" if name.startswith("ca:") else "control"}
    if name.startswith("ca:"):
        rule = GEN.rule_hex(name[3:])
        f = feats_ca(rule, streams, positions, reset_root)
        row["base_acc"] = acc(f[tr], y[tr], f[cf], y[cf], mask)
        # readout artifact: the reset lattice alone
        try:
            probe = rv.reset_leakage_probe(rule, N_CELLS, RESET_DENSITY, reset_root, streams, positions, TASK, d)
            row["reset_only_acc"] = float(probe.get("accuracy", probe.get("acc", float("nan")))) if isinstance(probe, dict) else float(probe)
            row["reset_probe_keys"] = sorted(probe.keys()) if isinstance(probe, dict) else None
        except Exception as e:                                       # noqa: BLE001
            row["reset_only_acc"] = None; row["reset_probe_error"] = repr(e)[:160]
        # frozen dynamical bias: time order destroyed per stream
        fs = time_shuffle(f, rng)
        row["time_shuffled_acc"] = acc(fs[tr], y[tr], fs[cf], y[cf], mask)
        # input-independent: the CA driven by shuffled input bits, targets kept
        sh = streams.copy()
        for i in range(sh.shape[0]):
            sh[i] = sh[i][rng.permutation(sh.shape[1])]
        fi = feats_ca(rule, sh, positions, reset_root)
        row["input_shuffled_acc"] = acc(fi[tr], y[tr], fi[cf], y[cf], mask)
        # lesion curves with a FROZEN readout
        w = cs.fit_readout(f[tr], y[tr], mask)
        base_cf = float(cs.score_readout(f[cf], y[cf], mask, w)["accuracy"])
        single = {}
        for i in range(N_CELLS):
            fl = feats_ca(rule, streams[cf], positions[cf], reset_root, lesion=[i])
            single[i] = base_cf - float(cs.score_readout(fl, y[cf], mask, w)["accuracy"])
        order = sorted(range(N_CELLS), key=lambda i: -single[i])
        greedy = []
        for k in range(1, N_CELLS + 1):
            fl = feats_ca(rule, streams[cf], positions[cf], reset_root, lesion=order[:k])
            greedy.append(float(cs.score_readout(fl, y[cf], mask, w)["accuracy"]))
        rand_curves = []
        for rep in range(4):
            perm = rng.permutation(N_CELLS).tolist(); cur = []
            for k in range(1, N_CELLS + 1):
                fl = feats_ca(rule, streams[cf], positions[cf], reset_root, lesion=perm[:k])
                cur.append(float(cs.score_readout(fl, y[cf], mask, w)["accuracy"]))
            rand_curves.append(cur)
        rand_mean = [sum(c[k] for c in rand_curves) / len(rand_curves) for k in range(N_CELLS)]
        margin = base_cf - 0.5
        # LI is undefined when the frozen readout has no margin over chance on the confirmation set
        li = (sum(rand_mean[k] - greedy[k] for k in range(N_CELLS)) / (N_CELLS * margin)) if margin >= EPS else None
        half = 0.5 + margin / 2
        k50 = next((k + 1 for k in range(N_CELLS) if greedy[k] < half), None) if margin >= EPS else None
        top = order[:6]; inter = []
        for a_ in range(len(top)):
            for b_ in range(a_ + 1, len(top)):
                fl = feats_ca(rule, streams[cf], positions[cf], reset_root, lesion=[top[a_], top[b_]])
                dij = base_cf - float(cs.score_readout(fl, y[cf], mask, w)["accuracy"])
                inter.append(dij - single[top[a_]] - single[top[b_]])
        row.update({"base_cf_frozen": base_cf, "single_drop_max": max(single.values()), "single_drop_mean": sum(single.values()) / N_CELLS,
                    "greedy_curve": [round(x, 4) for x in greedy], "random_curve": [round(x, 4) for x in rand_mean], "localization_index": (None if li is None else round(li, 4)), "margin_cf": round(margin, 4),
                    "k50": k50, "pair_interaction_mean": round(sum(inter) / len(inter), 4) if inter else None,
                    "flag_readout_artifact": (row["reset_only_acc"] is not None and row["reset_only_acc"] >= row["base_acc"] - EPS),
                    "flag_dynamical_bias": row["time_shuffled_acc"] >= row["base_acc"] - EPS,
                    "flag_input_independent": row["input_shuffled_acc"] >= row["base_acc"] - EPS,
                    "flag_localized": (None if li is None else li >= LI_MIN)})
    else:
        sub = {"shift": cs.ShiftRegister(N_CELLS), "direct": cs.DirectInput(N_CELLS) if "n_cells" in cs.DirectInput.__init__.__code__.co_varnames else cs.DirectInput(),
               "random": cs.FrozenRandom(N_CELLS, seed=reset_root)}[name]
        f = feats_plain(sub, streams)
        row["base_acc"] = acc(f[tr], y[tr], f[cf], y[cf], mask)
        fs = time_shuffle(f, rng)
        row["time_shuffled_acc"] = acc(fs[tr], y[tr], fs[cf], y[cf], mask)
        sh = streams.copy()
        for i in range(sh.shape[0]):
            sh[i] = sh[i][rng.permutation(sh.shape[1])]
        sub.reset() if hasattr(sub, "reset") else None
        fi = feats_plain(sub, sh)
        row["input_shuffled_acc"] = acc(fi[tr], y[tr], fi[cf], y[cf], mask)
    row["wall_s"] = round(time.time() - t0, 1)
    return row


class CASubstrate(Experiment):
    ID = "C2-SFE-09"
    TITLE = "CA substrate: distributed vs redundant vs artifact"
    PARENTS = ["SFE-04"]
    METRICS = ("base_acc", "reset_only_acc", "time_shuffled_acc", "input_shuffled_acc", "localization_index", "k50")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=[1, 2, 3, 4])
    ap.add_argument("--delay", type=int, default=2)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    X = CASubstrate(dry_run=a.dry_run, procs=a.procs)
    names = ["ca:" + n for n in GEN.NAMES] + CONTROLS
    X.seal({
        "question": "Which explanation of SFE-04's delayed-recall readout (0.608 vs 0.5 chance, flat single-window lesion map) survives: genuinely distributed "
                    "computation, redundant/local computation invisible to single lesions, a readout artifact of the reset lattice, or a frozen dynamical bias?",
        "parent_evidence": "SFE-04: particle2 0.608 on delayed recall d=2; lesion map flat within the matched-random band; frozen whole-substrate reuse positive; "
                           "reset_leakage_probe unwired (L-019).",
        "assay_capability_requirement": "the ShiftRegister (perfect memory) reads >= 0.8 under the ridge readout (READOUT_CANNOT_EXPRESS otherwise); "
                                        "the best CA must exceed FrozenRandom by the preregistered margin for the explanations to be about anything",
        "positive_control": "ShiftRegister base accuracy (readout capability); DirectInput and FrozenRandom as floors",
        "reachability_estimate": {"note": "not a WSE cell; the CA genomes are the six recovered Herakles genomes; the reachability table does not apply"},
        "arms": names,
        "crn_policy": "per seed: one train/confirmation partition and one reset root shared by every substrate; shuffles drawn from one generator per row",
        "budget": {"seeds": a.seeds, "delay": a.delay, "n_cells": N_CELLS, "horizon": HORIZON, "reset_density": RESET_DENSITY, "eps": EPS, "li_min": LI_MIN,
                   "random_orders": 4, "pair_sites": 6},
        "primary_observable": "base_acc per substrate x seed (particle2 vs random, the parent's pair); the four preregistered flags per CA row",
        "claim_ceiling": "weak; one CA family, one task; the flags are measurements with fixed rules, not a verdict",
        "falsification_condition": "particle2 - random < 0.05 base accuracy => the parent's usefulness does not replicate; flag rules: reset_only >= base - %.2f => "
                                   "readout artifact; time_shuffled >= base - %.2f => dynamical bias; input_shuffled >= base - %.2f => input-independent; LI >= %.2f => "
                                   "localized (else distributed)" % (EPS, EPS, EPS, LI_MIN),
        "typed_failure_conditions": ["READOUT_CANNOT_EXPRESS (shift < 0.8)", "UNDERPOWERED", "INSTRUMENT_FAILURE (probe signature)"],
        "expected_machine_telemetry": ["reset-only accuracy (the L-019 probe, wired)", "time-shuffled and input-shuffled accuracies", "greedy and random cumulative "
                                       "lesion curves", "localization index and k50", "pairwise interaction of the top-6 sites"],
        "machine_changes_exercised": ["H (the missing telemetry L-019)", "B (readout_control state)", "I"],
        "decl": {"readout_control": {"arm": "shift", "metric": "base_acc", "chance": 0.5, "min_above": 0.30}, "n_min": len(a.seeds),
                 "primary": {"treatment": "ca:particle2", "control": "random", "metric": "base_acc", "min_effect": 0.05}},
    })
    X.decision("D2-017: the four explanations are decided by preregistered rules on four measurements per CA genome; no explanation is assigned by reading rows")
    X.open("cmp2-sfe09")
    wid = X.world("ca", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    jobs = [{"name": n, "seed": s, "delay": a.delay} for s in a.seeds for n in names]
    rows = X.pool_map(run_substrate, jobs, "substrates_s")
    X.publish(wid, "lesion_curves", "cmp2.ca_lesion_curves.v1", {"%s_s%d" % (r["arm"], r["seed"]): {"greedy": r.get("greedy_curve"), "random": r.get("random_curve")}
                                                                 for r in rows if r["kind"] == "ca"}, {"info_kind": "observation"})
    t0 = time.time()
    for r in rows:
        X.record(wid, r, {"experiment": X.ID, "substrate": r["arm"], "seed": r["seed"], "delay": a.delay, "prereg_digest": X.prereg["prereg_digest"]},
                 {k: v for k, v in r.items() if k not in ("greedy_curve", "random_curve")}, "SURVIVED" if r["base_acc"] >= 0.55 else "FALSIFIED", (r["arm"], r["seed"]))
    X.att.timing("records_s", t0)
    summ = {}
    for n in names:
        rs = [r for r in rows if r["arm"] == n]
        summ[n] = {"base": [round(r["base_acc"], 3) for r in rs], "reset_only": [None if r.get("reset_only_acc") is None else round(r["reset_only_acc"], 3) for r in rs],
                   "time_shuffled": [round(r["time_shuffled_acc"], 3) for r in rs], "input_shuffled": [round(r["input_shuffled_acc"], 3) for r in rs],
                   "LI": [r.get("localization_index") for r in rs], "k50": [r.get("k50") for r in rs],
                   "flags": {f: sum(1 for r in rs if r.get(f)) for f in ("flag_readout_artifact", "flag_dynamical_bias", "flag_input_independent", "flag_localized")} if n.startswith("ca:") else None}
    X.receipt["summary"] = summ
    out = X.close(rows)
    print(json.dumps({"summary": summ, **out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
