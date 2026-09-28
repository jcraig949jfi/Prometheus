"""FR-101 (reduced): does particle2 beat generic rule tables under the same encoding?

Follows roles/Artemis/challenge/experiments/FR-101/PREREG.md (commit 591209b9e).
Run ONLY from a `git archive` copy with GIT_* unset, e.g.

    env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE \
        OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
        PYTHONPATH=<copy of herakles @ 5a0458fd6> \
        python3 run_fr101.py --c3rows <C3-SFE-09/rows.json @ cb9135104> \
                             --c2rows <C2-SFE-09/rows.json> --out <dir>

Inputs used: herakles/ca_stream/core.py, reset_v2.py, herakles/evca (@ 5a0458fd6;
the step-relevant files are byte-identical at cb9135104 and fe3c1647c).
ClampedCA / feats are COPIED from archaeon/campaign3/c3_sfe09.py:45-71 @ fe3c1647c
(not imported: importing c3_sfe09 pulls proteus and the SFE client).
"""
from __future__ import annotations

import argparse
import json
import os
import time
from typing import Sequence, Tuple

import numpy as np

from herakles import evca
from herakles.ca_stream import core as cs
from herakles.ca_stream import reset_v2 as rv
from herakles.evca import genomes as GEN

# --- constants from archaeon/campaign3/c3_sfe09.py @ fe3c1647c and c3base.py:18
N_CELLS, HORIZON = 31, 8
RESET_DENSITY = 0.5
TASK = "delayed_recall"
DELAY = 2
CAMPAIGN_SEED = 20260920          # archaeon/campaign3/c3base.py:18 (CAMPAIGN_3["seed"])
C2_CAMPAIGN_SEED = 20260918       # archaeon/campaign2/runner.py:47 (diagnostic only)
SEEDS = list(range(1, 9))
RANDOM_RULE_SEED = 20260928
N_RANDOM = 64


# ---- copied verbatim from archaeon/campaign3/c3_sfe09.py:45-71 @ fe3c1647c ----
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
# ---- end copy ----


def table_from_fn(fn) -> str:
    """Rule hex from out = fn(neigh) where neigh[j] = cell[i-3+j] (j=0 is MSB, evca convention)."""
    t = np.zeros(128, dtype=np.uint8)
    for k in range(128):
        neigh = [(k >> (6 - j)) & 1 for j in range(7)]
        t[k] = fn(neigh)
    return evca.encode_table(t)


def build_rules():
    rules = []  # (name, family, hex)
    for n in GEN.NAMES:                              # maj exp par particle1 particle2 GKL
        rules.append((n, "named", GEN.rule_hex(n)))
    rules.append(("identity", "transport", table_from_fn(lambda nb: nb[3])))
    # shift_k: new[i] = old[i-k]; content moves toward higher index (port 0 -> site k per step)
    for k in (1, 2, 3):
        rules.append(("shift%d" % k, "transport", table_from_fn(lambda nb, k=k: nb[3 - k])))
    # supplementary (not in the prereg's transport set): opposite direction, new[i] = old[i+k]
    for k in (1, 2, 3):
        rules.append(("shiftL%d" % k, "supplementary", table_from_fn(lambda nb, k=k: nb[3 + k])))
    rng = np.random.default_rng(RANDOM_RULE_SEED)
    tabs = rng.integers(0, 2, size=(N_RANDOM, 128), dtype=np.uint8)   # uniform over 2^128 tables
    for i in range(N_RANDOM):
        rules.append(("rand%02d" % i, "random", evca.encode_table(tabs[i])))
    return rules


def base_acc(rule_hex: str, seed: int) -> float:
    """Exactly c3_sfe09.run_genome's base_acc (lines 82-91 @ fe3c1647c)."""
    streams = cs.all_streams(HORIZON)
    parts = cs.partitions(len(streams), 64, 64, seed=CAMPAIGN_SEED + seed)
    tr, cf = parts["train"], parts["confirmation"]
    positions = np.arange(len(streams))
    y = cs.build_targets(streams, TASK, DELAY); mask = cs.warmup_mask(HORIZON, TASK, DELAY)
    reset_root = CAMPAIGN_SEED + seed
    f0 = feats(rule_hex, streams, positions, reset_root)
    w = cs.fit_readout(f0[tr], y[tr], mask)
    return float(cs.score_readout(f0[cf], y[cf], mask, w)["accuracy"])


def reset_only_feats(rule_hex, reset_root, positions, n):
    """Identical to reset_v2.reset_leakage_probe lines 233-242 (no injection)."""
    table = evca.decode_table(rule_hex)
    F = np.empty((n, HORIZON, N_CELLS), dtype=np.float64)
    for i in range(n):
        rng = np.random.default_rng(rv.reset_seed(reset_root, int(positions[i])))
        state = (rng.random((1, N_CELLS)) < RESET_DENSITY).astype(np.uint8)
        for t in range(HORIZON):
            state = evca.step(state, table)
            F[i, t] = state[0].astype(np.float64)
    return F


def leakage_diagnostic(rule_hex, campaign_seed, seed):
    streams = cs.all_streams(HORIZON); n = len(streams)
    positions = np.arange(n)
    reset_root = campaign_seed + seed
    F = reset_only_feats(rule_hex, reset_root, positions, n)
    y = cs.build_targets(streams, TASK, DELAY); mask = cs.warmup_mask(HORIZON, TASK, DELAY)

    def fs(tr, te):
        w = cs.fit_readout(F[tr], y[tr], mask)
        return float(cs.score_readout(F[te], y[te], mask, w)["accuracy"])
    half = n // 2
    idx = np.arange(n)
    out = {"index_order": fs(idx[:half], idx[half:])}          # as committed (reproduction)
    p = np.random.default_rng(RANDOM_RULE_SEED + seed).permutation(n)
    out["random_half"] = fs(np.sort(p[:half]), np.sort(p[half:]))
    parts = cs.partitions(n, 64, 64, seed=campaign_seed + seed)
    out["base_partition"] = fs(parts["train"], parts["confirmation"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--c3rows", required=True)
    ap.add_argument("--c2rows", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cpu-cap-s", type=float, default=3600.0)
    a = ap.parse_args()
    t_start = time.process_time(); w_start = time.time()
    c3 = json.load(open(a.c3rows))
    ref = {r["seed"]: r["base_acc"] for r in c3 if r["arm"] == "particle2"}

    # ---- GATE
    p2 = GEN.rule_hex("particle2")
    gate = []
    for s in SEEDS:
        acc = base_acc(p2, s)
        gate.append({"seed": s, "recomputed": acc, "committed": ref[s], "abs_diff": abs(acc - ref[s])})
    n_ok = sum(1 for g in gate if g["abs_diff"] <= 0.01)
    gate_pass = n_ok >= 7
    print("GATE", n_ok, "/ 8", "PASS" if gate_pass else "FAIL", flush=True)
    result = {"prereg": "FR-101 @ 591209b9e", "gate": {"rows": gate, "n_within_0.01": n_ok, "pass": gate_pass}}
    if not gate_pass:
        result["decision"] = "STOP"
        json.dump(result, open(os.path.join(a.out, "rows.json"), "w"), indent=1)
        return

    # ---- rule set
    rules = build_rules()
    rows = []; partial = False
    for name, fam, hx in rules:
        if time.process_time() - t_start > a.cpu_cap_s:
            partial = True; break
        accs = [gate[s - 1]["recomputed"] if name == "particle2" else base_acc(hx, s) for s in SEEDS]
        rows.append({"rule": name, "family": fam, "hex": hx, "acc": accs,
                     "mean": float(np.mean(accs)), "sd": float(np.std(accs, ddof=1))})
        print("%-10s %-13s mean %.4f sd %.4f" % (name, fam, rows[-1]["mean"], rows[-1]["sd"]), flush=True)
    result["rules"] = rows; result["partial"] = partial

    # ---- decision (verbatim from prereg)
    M = {r["rule"]: r["mean"] for r in rows}
    rnd = np.array([r["mean"] for r in rows if r["family"] == "random"])
    p95 = float(np.percentile(rnd, 95))                 # numpy default (linear interpolation)
    tmax_name = max(["identity", "shift1", "shift2", "shift3"], key=lambda k: M[k])
    tmax = M[tmax_name]
    mp2 = M["particle2"]
    if mp2 <= p95:
        dec = "CLOSE"
    elif mp2 > tmax:
        dec = "REOPEN"
    else:
        dec = "CLOSE-with-note"
    pct = float((rnd < mp2).mean() * 100)
    result["decision"] = {"label": dec, "M_particle2": mp2, "random_p95": p95, "random_p95_method": "numpy.percentile linear",
                          "random_p95_nearest_rank": float(np.sort(rnd)[int(np.ceil(0.95 * len(rnd))) - 1]),
                          "transport_max": tmax, "transport_max_rule": tmax_name,
                          "particle2_percentile_among_random": pct,
                          "random_mean_of_means": float(rnd.mean()), "random_min": float(rnd.min()), "random_max": float(rnd.max()),
                          "n_random_above_0.52": int((rnd > 0.52).sum())}
    print(json.dumps(result["decision"], indent=1), flush=True)

    # ---- diagnostic: C2 reset-leakage probe, index-order vs random split
    c2 = json.load(open(a.c2rows))
    c2ref = {(r["arm"], r["seed"]): r.get("reset_only_acc") for r in c2}
    diag = []
    for s in (1, 2, 3, 4):
        for n in GEN.NAMES:
            d = leakage_diagnostic(GEN.rule_hex(n), C2_CAMPAIGN_SEED, s)
            d.update({"rule": n, "seed": s, "committed_c2_reset_only_acc": c2ref.get(("ca:" + n, s))})
            diag.append(d)
            print("diag", n, s, {k: round(v, 4) for k, v in d.items() if isinstance(v, float)}, flush=True)
    result["diagnostic_c2_reset_leakage"] = diag
    result["runtime"] = {"cpu_s": time.process_time() - t_start, "wall_s": time.time() - w_start}
    json.dump(result, open(os.path.join(a.out, "rows.json"), "w"), indent=1)
    print("runtime", result["runtime"])


if __name__ == "__main__":
    main()
