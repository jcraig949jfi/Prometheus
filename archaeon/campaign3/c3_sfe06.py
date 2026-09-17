"""C3-SFE-06 -- BASIN SHARE OUT-OF-FAMILY TEST (campaign 3, slot 6; parent C2-SFE-08).

    python -m archaeon.campaign3.c3_sfe06 [--n-perms 10] [--dry-run]

Does basin share predict search efficiency outside the evaluator/climber pair that produced
the campaign-2 observation (CA block-output evaluator; best-of-lambda hill climb)? Second
evaluator family: a WSE event-stream cell (W0 4-bit, one fixed 16-episode battery). Genotype
space: the OPCODE FIELDS of a minimal 4-instruction W0 solver skeleton (operand words and
manifest fixed; two skeletons = two score tables), 25^4 = 390,625 genotypes each, scored
exhaustively. Encodings: orderings of the 25 opcodes (identity, affordance-class-grouped,
n seeded permutations); the neighbourhood under an encoding moves ONE position's opcode by
+-1 or +-2 in that ordering (16 neighbours), the geometry campaign 2's A_words neighbourhood
has on the opcode word. Two climbers, both different from campaign 2's: (a) a first-improvement
stochastic climber with restarts, (b) a (mu+lambda) population search (N=50, elitism 4,
tournament 4, one move per child). Efficiency = evaluations to the first genotype at or above
the threshold (reward >= 0.875 on the battery), censored at the budget.

PRIMARY (preregistered): Spearman rho between basin_share and log10(evaluations to threshold)
over all encoding x table x climber rows, expected NEGATIVE, |rho| >= 0.5. Every other
statistic is reported with its rho and none is promoted.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from collections import deque
from typing import Dict, List

import numpy as np

from proteus.foundry.affordances import CATEGORY, N_OPCODES
from proteus.foundry.vm import SCHEMA

from archaeon.wse import states as S
from archaeon.wse.evolve import evaluate
from archaeon.wse.worlds import WorldSpec, episodes_for
from archaeon.campaign3.c3base import CAMPAIGN_SEED, Experiment3

W0 = WorldSpec("W0", value_bits=4)
THRESHOLD = 0.875
K = 4                       # free opcode positions
NG = N_OPCODES ** K
STATS = ["accessible_variation", "useful_variation", "local_improvement_prob", "basin_share", "greedy_path_len", "deceptive_share", "mean_dist_to_threshold"]
# the two minimal W0 solvers found by reconnaissance (evolved, then minimized by knockout): operands fixed, opcodes free
SKELETONS = {
    "skelA": {"n_regs": 2, "persist": "all", "tick_budget": 64, "tape_words": 32, "out_cap": 1, "code_writable": False, "operands": None, "ops": [21, 21, 23, 6]},
    "skelB": {"n_regs": 4, "persist": "all", "tick_budget": 64, "tape_words": 32, "out_cap": 1, "code_writable": False, "operands": None, "ops": [23, 12, 21, 19]},
}


def load_skeletons(path: str):
    """Operand words come from the reconnaissance file (scratchpad w0_solvers.json) when present."""
    try:
        sol = json.load(open(path, encoding="utf-8"))
    except Exception:                                                # noqa: BLE001
        sol = []
    for s in sol:
        key = "skelA" if s["seed"] == 2 else "skelB" if s["seed"] == 6 else None
        if key and s["instr"] == K:
            SKELETONS[key]["operands"] = [s["genome"][4 * i + 1:4 * i + 4] for i in range(K)]
            for f in ("n_regs", "persist", "tick_budget", "tape_words", "out_cap", "code_writable"):
                SKELETONS[key][f] = s[f]
    return SKELETONS


def decode(idx: int) -> List[int]:
    ops = []
    for _ in range(K):
        ops.append(idx % N_OPCODES); idx //= N_OPCODES
    return ops


def encode(ops: List[int]) -> int:
    idx = 0
    for o in reversed(ops):
        idx = idx * N_OPCODES + o
    return idx


def manifest_for(sk: dict, ops: List[int]) -> dict:
    g = []
    for i, o in enumerate(ops):
        opr = sk["operands"][i] if sk["operands"] else [0, 0, 0]
        g.extend([o] + list(opr))
    return {"schema_version": SCHEMA, "n_regs": sk["n_regs"], "tape_words": sk["tape_words"], "genome": g, "code_writable": sk["code_writable"],
            "persist": sk["persist"], "tick_budget": sk["tick_budget"], "out_cap": sk["out_cap"]}


def score_table(sk: dict, eps) -> np.ndarray:
    tab = np.zeros(NG, dtype=np.float32)
    for idx in range(NG):
        try:
            tab[idx] = evaluate(manifest_for(sk, decode(idx)), eps, rng_seed=1)["reward"]
        except Exception:                                            # noqa: BLE001
            tab[idx] = 0.0
    return tab


def orderings(n_perms: int) -> Dict[str, List[int]]:
    out = {"identity": list(range(N_OPCODES))}
    cls = sorted(range(N_OPCODES), key=lambda o: (CATEGORY[o], o))
    out["class_grouped"] = cls
    rng = np.random.default_rng(CAMPAIGN_SEED + 6)
    for i in range(n_perms):
        out["perm_%d" % (i + 1)] = rng.permutation(N_OPCODES).tolist()
    return out


def neighbours_table(order: List[int]) -> np.ndarray:
    """For each opcode, its 4 neighbours (+-1, +-2 in the ordering)."""
    pos = {o: i for i, o in enumerate(order)}
    nb = np.zeros((N_OPCODES, 4), dtype=np.int64)
    for o in range(N_OPCODES):
        i = pos[o]
        nb[o] = [order[(i + d) % N_OPCODES] for d in (1, -1, 2, -2)]
    return nb


def all_neighbours(nb: np.ndarray) -> np.ndarray:
    """(NG, 16) neighbour indices under the encoding."""
    idx = np.arange(NG)
    digits = [(idx // (N_OPCODES ** p)) % N_OPCODES for p in range(K)]
    out = np.zeros((NG, 4 * K), dtype=np.int64)
    col = 0
    for p in range(K):
        base = idx - digits[p] * (N_OPCODES ** p)
        for d in range(4):
            out[:, col] = base + nb[digits[p], d] * (N_OPCODES ** p); col += 1
    return out


def geometry(tab: np.ndarray, NB: np.ndarray) -> dict:
    s = tab
    ns = s[NB]                                                       # (NG, 16) neighbour scores
    acc = np.array([len(set(row)) for row in np.round(ns, 4)])       # distinct neighbour scores (behaviours)
    better = ns > s[:, None] + 1e-9
    lip = better.mean(axis=1)
    useful = np.array([len(set(np.round(row[m], 4))) if m.any() else 0 for row, m in zip(ns, better)])
    best_nb = np.where(better.any(axis=1), NB[np.arange(NG), ns.argmax(axis=1)], -1)
    # greedy endpoints (memoized)
    end = np.full(NG, -1, dtype=np.int64); plen = np.zeros(NG, dtype=np.int64)
    for g in range(NG):
        if end[g] >= 0:
            continue
        path = []; h = g
        while end[h] < 0 and best_nb[h] >= 0 and h not in path:
            path.append(h); h = int(best_nb[h])
        if end[h] < 0:
            end[h] = h; plen[h] = 0
        e, base = end[h], plen[h]
        for i, p in enumerate(reversed(path)):
            end[p] = e; plen[p] = base + i + 1
    reach = s[end] >= THRESHOLD
    basin = reach.mean()
    lens = plen[reach]
    decept = ((best_nb >= 0) & ~reach).mean()
    dist = np.full(NG, -1, dtype=np.int64); q = deque()
    for g in np.where(s >= THRESHOLD)[0]:
        dist[g] = 0; q.append(int(g))
    while q:
        g = q.popleft()
        for h in NB[g]:
            if dist[h] < 0:
                dist[h] = dist[g] + 1; q.append(int(h))
    return {"accessible_variation": round(float(acc.mean()), 4), "useful_variation": round(float(useful.mean()), 4), "local_improvement_prob": round(float(lip.mean()), 4),
            "basin_share": round(float(basin), 4), "greedy_path_len": round(float(lens.mean()), 4) if len(lens) else None, "deceptive_share": round(float(decept), 4),
            "mean_dist_to_threshold": round(float(dist[dist >= 0].mean()), 4) if (dist >= 0).any() else None, "threshold_share": round(float((s >= THRESHOLD).mean()), 6)}


def climb_first_improvement(tab: np.ndarray, NB: np.ndarray, seed: int, restarts: int = 8, steps: int = 400) -> dict:
    rng = np.random.default_rng(seed)
    evals = 0; first = None
    for r in range(restarts):
        g = int(rng.integers(NG)); sc = tab[g]; evals += 1
        if sc >= THRESHOLD and first is None:
            first = evals
        for _ in range(steps):
            h = int(NB[g, rng.integers(NB.shape[1])]); evals += 1
            if tab[h] >= THRESHOLD and first is None:
                first = evals
            if tab[h] > sc:
                g, sc = h, tab[h]
        if first is not None:
            break
    return {"first_hit": first, "evals": evals}


def climb_population(tab: np.ndarray, NB: np.ndarray, seed: int, N: int = 50, G: int = 40, elitism: int = 4, k: int = 4) -> dict:
    rng = np.random.default_rng(seed)
    pop = rng.integers(NG, size=N); evals = 0; first = None
    for g in range(G):
        sc = tab[pop]; evals += N
        if first is None and (sc >= THRESHOLD).any():
            first = evals - N + int(np.argmax(sc >= THRESHOLD)) + 1
            break
        order = np.argsort(-sc)
        new = list(pop[order[:elitism]])
        while len(new) < N:
            a = pop[order[np.min(rng.integers(N, size=k))]]
            new.append(int(NB[a, rng.integers(NB.shape[1])]))
        pop = np.array(new)
    return {"first_hit": first, "evals": evals}


def run_cell(job: dict) -> dict:
    enc, order, table_name, tab, climber, seeds = job["encoding"], job["order"], job["table"], job["tab"], job["climber"], job["seeds"]
    t0 = time.time()
    NB = all_neighbours(neighbours_table(order))
    geo = job.get("geo") or geometry(tab, NB)
    firsts = []; budget = None
    for s in seeds:
        hc = (climb_first_improvement if climber == "first_improvement" else climb_population)(tab, NB, CAMPAIGN_SEED + 100 * s + hash(enc) % 1000)
        budget = 8 * 401 if climber == "first_improvement" else 50 * 40
        firsts.append(hc["first_hit"] if hc["first_hit"] is not None else budget + 1)
    med = sorted(firsts)[len(firsts) // 2]
    return {"arm": enc, "encoding": enc, "table": table_name, "climber": climber, "seed": "%s/%s" % (table_name, climber), **geo, "first_hits": firsts,
            "hits": sum(1 for f in firsts if f <= budget), "median_first_hit": med, "log_first_hit": round(math.log10(med), 4), "budget_evals": budget, "wall_s": round(time.time() - t0, 1)}


class BasinOOF(Experiment3):
    ID = "C3-SFE-06"
    TITLE = "basin share out-of-family test"
    PARENTS = ["C2-SFE-08"]
    ARM_FIELD = "encoding"
    METRICS = ("median_first_hit", "basin_share", "deceptive_share", "accessible_variation", "local_improvement_prob")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-perms", type=int, default=10)
    ap.add_argument("--search-seeds", nargs="*", type=int, default=[1, 2, 3])
    ap.add_argument("--skeletons", default=r"C:\Users\James\AppData\Local\Temp\claude\D--prometheus\411504ab-b880-47d2-8796-03ceeaf87c96\scratchpad\w0_solvers.json")
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    X = BasinOOF(dry_run=a.dry_run, procs=a.procs)
    sk = load_skeletons(a.skeletons)
    eps = episodes_for(W0, CAMPAIGN_SEED, "train", 777, 16)
    encs = orderings(a.n_perms if not a.dry_run else 2)
    X.seal({
        "question": "Over %d opcode orderings (encodings) of two exhaustive 25^4 opcode spaces on a WSE cell (W0 4-bit, fixed battery) and two climbers unlike campaign 2's, "
                    "does basin share rank-correlate with evaluations-to-threshold (expected negative, |rho| >= 0.5)?" % len(encs),
        "parent_evidence": "C2-SFE-08 (CA block-output evaluator, best-of-lambda climb, 52 rows): basin_share rho -0.59, deceptive_share +0.57, accessible variation -0.23.",
        "why_this_slot": "A geometry that predicts search only on the evaluator/climber pair that produced it is a description of one landscape; the campaign needs to know "
                         "whether basin share is a general instrument before C3-SFE-07 spends compute on manipulating it.",
        "assay_capability_requirement": "each score table contains threshold genotypes (threshold_share > 0) and the identity encoding's climbers hit the threshold in >= 1 of "
                                        "%d seeds on each table (POSITIVE_CONTROL_FAILED otherwise); threshold_share must be identical across encodings of one table" % len(a.search_seeds),
        "positive_control": "identity ordering, both climbers, both tables",
        "reachability_estimate": {"note": "exhaustive space; the reachability table does not apply; skeleton solvers found by reconnaissance (seeds 2 and 6, minimized to 4 instructions)"},
        "arms": sorted(encs),
        "crn_policy": "one score table per skeleton shared by every encoding; climber seeds keyed on (search seed, encoding); neighbourhood moves keyed on the encoding",
        "budget": {"n_encodings": len(encs), "tables": list(sk), "genotypes_per_table": NG, "neighbours": 4 * K, "search_seeds": a.search_seeds, "threshold": THRESHOLD,
                   "climber_a": "first-improvement, 8 restarts x 400 steps", "climber_b": "(mu+lambda) N=50 G=40 elitism 4 tournament 4"},
        "primary_observable": "log10(median evaluations to threshold, censored) per encoding x table x climber; Spearman rho of basin_share with it",
        "claim_ceiling": "weak: two skeleton spaces, one cell, two climbers; a negative kills basin share as a general predictor for this substrate",
        "falsification_condition": "rho(basin_share, log_first_hit) > -0.5 over all rows => basin share does not generalize; per-climber rho reported",
        "kill_condition": "positive control fails on either table; or every encoding has identical geometry (the neighbourhood definition would then be inert)",
        "typed_failure_conditions": ["POSITIVE_CONTROL_FAILED", "INSTRUMENT_FAILURE (threshold_share differs across encodings of one table)"],
        "expected_machine_telemetry": ["seven geometry statistics per encoding x table", "first hits per seed per climber", "rho table (all rows; per climber)"],
        "replacement_condition": "none",
        "ancestry": "original (queue slot 6)",
        "machine_changes_exercised": ["B rank_correlation primary", "I"],
        "decl": {"positive_control": {"arm": "identity", "metric": "hits", "min": 1, "min_rows": 2},
                 "primary": {"type": "rank_correlation", "x": "basin_share", "y": "log_first_hit", "expected_sign": -1, "min_abs_rho": 0.5}, "statistics": STATS},
    })
    X.decision("D3-011: basin share is the preregistered PRIMARY; the neighbourhood is +-1/+-2 in the encoding's opcode ordering (campaign 2's A_words geometry on the opcode word); two climbers unlike campaign 2's")
    X.open("cmp3-sfe06")
    wid = X.world("basin", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    t0 = time.time()
    tables = {}
    for name, s in sk.items():
        if s["operands"] is None:
            continue
        tables[name] = score_table(s, eps) if not a.dry_run else np.random.default_rng(1).random(NG).astype(np.float32)
    X.att.timing("tables_s", t0)
    X.receipt["tables"] = {n: {"threshold_share": float((t >= THRESHOLD).mean()), "max": float(t.max()), "n_solvers": int((t >= THRESHOLD).sum())} for n, t in tables.items()}
    X.att.save()
    t0 = time.time()
    geos = {}
    for tn, tab in tables.items():
        for en, order in encs.items():
            geos[(tn, en)] = geometry(tab, all_neighbours(neighbours_table(order)))
    X.att.timing("geometry_s", t0)
    rows = []
    for tn, tab in tables.items():
        for en, order in encs.items():
            for cl in ("first_improvement", "population"):
                rows.append(run_cell({"encoding": en, "order": order, "table": tn, "tab": tab, "climber": cl, "seeds": a.search_seeds, "geo": geos[(tn, en)]}))
    X.att.timing("climbs_s", t0)
    rhos = {st: S.spearman([r[st] for r in rows if r.get(st) is not None], [r["log_first_hit"] for r in rows if r.get(st) is not None]) for st in STATS}
    per_cl = {cl: {st: S.spearman([r[st] for r in rows if r["climber"] == cl and r.get(st) is not None], [r["log_first_hit"] for r in rows if r["climber"] == cl and r.get(st) is not None]) for st in STATS} for cl in ("first_improvement", "population")}
    X.receipt["rho"] = {k: (None if v is None else round(v, 4)) for k, v in rhos.items()}
    X.receipt["rho_per_climber"] = {cl: {k: (None if v is None else round(v, 4)) for k, v in d.items()} for cl, d in per_cl.items()}
    X.receipt["threshold_share_by_table"] = {tn: sorted({r["threshold_share"] for r in rows if r["table"] == tn}) for tn in tables}
    X.publish(wid, "geometry_table", "cmp3.encoding_geometry.v1", {"rows": [{k: v for k, v in r.items() if k != "first_hits"} for r in rows], "rho": X.receipt["rho"]}, {"info_kind": "observation"})
    t0 = time.time()
    for r in rows:
        X.record(wid, r, {"experiment": X.ID, "encoding": r["encoding"], "table": r["table"], "climber": r["climber"], "prereg_digest": X.prereg["prereg_digest"]},
                 {k: v for k, v in r.items()}, "SURVIVED" if r["hits"] > 0 else "FALSIFIED", (r["encoding"], r["table"], r["climber"]))
    X.att.timing("records_s", t0)
    harness_errors = [] if all(len(v) == 1 for v in X.receipt["threshold_share_by_table"].values()) else [{"step": "geometry", "error": "threshold_share differs across encodings"}]
    out = X.close(rows, meas_extra={"harness_errors": harness_errors})
    print(json.dumps({"rho": X.receipt["rho"], "rho_per_climber": X.receipt["rho_per_climber"], "tables": X.receipt["tables"], **out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
