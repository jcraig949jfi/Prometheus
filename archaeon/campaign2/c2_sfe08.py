"""C2-SFE-08 -- ENCODING GEOMETRY: WHAT PREDICTS SEARCH EFFICIENCY (parent SFE-06).

    python -m archaeon.campaign2.c2_sfe08 [--tables 1 2 3 4] [--n-balanced 6 --n-scrambled 6] [--search-seeds 1 2 3] [--dry-run]

SFE-06 (campaign 1) falsified the simple idea that more accessible variation makes search
easier: the balanced encoding had ~50% more accessible variation than direct and searched
more slowly (L-023). Here the evaluator is fixed (the 256 elementary CA rules scored by
Herakles's block-output criterion; one score table per table seed) and MANY encodings of
the same 12-bit genotype space are laid over it: direct, n balanced (seeded genome
permutations) and n scrambled (seeded rule permutations over direct). For each encoding x
table the ENTIRE genotype space (4,096 genotypes x 12 single-bit neighbours) is enumerated
and six preregistered geometry statistics are computed:

  accessible_variation    mean distinct neighbour rules                      (the parent's proxy)
  useful_variation        mean distinct neighbour rules with a HIGHER score
  local_improvement_prob  mean fraction of neighbours with a higher score
  basin_share             fraction of genotypes whose best-improvement greedy path ends >= threshold
  greedy_path_len         mean greedy steps to threshold, over genotypes that reach it
  deceptive_share         fraction with an improving neighbour whose greedy path ends BELOW threshold
  mean_dist_to_threshold  mean Hamming distance to the nearest threshold genotype (BFS)

and search efficiency is measured by SFE-06's (1+lambda) hill climb (8 independent parents,
40 steps, lambda 4; 3 search seeds): evaluations to the first score >= 0.9, censored at the
budget. The preregistered PRIMARY is the parent's claim: accessible_variation predicts
efficiency (expected negative rank correlation with log evaluations, |rho| >= 0.5 over all
encoding x table rows). Every other statistic's rho is reported beside it; none is invented
into the metric.
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

from herakles.eca import core as E
from archaeon.producer import h5_decoders as H
from archaeon.wse import states as S
from archaeon.campaign2.c2base import Experiment
from archaeon.campaign2.runner import CAMPAIGN_SEED

N_CELLS, N_ICS, STEPS = 21, 64, 11
THRESHOLD = 0.9
STATS = ["accessible_variation", "useful_variation", "local_improvement_prob", "basin_share", "greedy_path_len", "deceptive_share", "mean_dist_to_threshold"]


def score_table(seed: int) -> List[float]:
    ics = E.make_ics(N_ICS, N_CELLS, seed, "bernoulli")
    return [E.block_output_score(r, ics, STEPS)["score"] for r in range(256)]


def geometry(dec, table: List[float]) -> dict:
    n = H.N_GENOMES; bits = H.GENOME_BITS
    rule = [dec(g) for g in range(n)]
    score = [table[r] for r in rule]
    acc = use = lip = 0.0
    best_nb = [None] * n
    for g in range(n):
        s = score[g]
        nbs = [g ^ (1 << b) for b in range(bits)]
        rules = {rule[h] for h in nbs}
        acc += len(rules)
        imp = [h for h in nbs if score[h] > s]
        lip += len(imp) / bits
        use += len({rule[h] for h in imp})
        best_nb[g] = max(imp, key=lambda h: score[h]) if imp else None
    # greedy paths (memoized): endpoint and length
    end = [None] * n; plen = [0] * n
    for g in range(n):
        path = []; h = g
        while end[h] is None and best_nb[h] is not None and h not in path:
            path.append(h); h = best_nb[h]
        if end[h] is None:                                   # local optimum (or cycle guard)
            end[h] = h; plen[h] = 0
        e, base = end[h], plen[h]
        for i, p in enumerate(reversed(path)):
            end[p] = e; plen[p] = base + i + 1
    reach = [score[end[g]] >= THRESHOLD for g in range(n)]
    basin = sum(reach) / n
    lens = [plen[g] for g in range(n) if reach[g]]
    decept = sum(1 for g in range(n) if best_nb[g] is not None and not reach[g]) / n
    # BFS distance to the threshold set
    dist = [-1] * n; q = deque()
    for g in range(n):
        if score[g] >= THRESHOLD:
            dist[g] = 0; q.append(g)
    while q:
        g = q.popleft()
        for b in range(bits):
            h = g ^ (1 << b)
            if dist[h] < 0:
                dist[h] = dist[g] + 1; q.append(h)
    return {"accessible_variation": round(acc / n, 4), "useful_variation": round(use / n, 4), "local_improvement_prob": round(lip / n, 4),
            "basin_share": round(basin, 4), "greedy_path_len": round(sum(lens) / len(lens), 4) if lens else None, "deceptive_share": round(decept, 4),
            "mean_dist_to_threshold": round(sum(d for d in dist if d >= 0) / n, 4) if any(d >= 0 for d in dist) else None,
            "threshold_share": round(sum(1 for g in range(n) if score[g] >= THRESHOLD) / n, 4)}


def hill_climb(dec, table: List[float], parents: List[int], steps: int, lam: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    evals = 0; best_overall = -1.0; first_hit = None
    for g0 in parents:
        g = g0; s = table[dec(g)]; evals += 1
        if s >= THRESHOLD and first_hit is None:
            first_hit = evals
        for _ in range(steps):
            cands = [g ^ (1 << int(b)) for b in rng.choice(H.GENOME_BITS, size=lam, replace=False)]
            scored = [(table[dec(c)], c) for c in cands]; evals += lam
            for sc, c in scored:
                if sc >= THRESHOLD and first_hit is None:
                    first_hit = evals
            sc, c = max(scored, key=lambda z: z[0])
            if sc >= s:
                g, s = c, sc
            best_overall = max(best_overall, s)
    return {"best": best_overall, "evals": evals, "first_hit_evals": first_hit}


def run_cell(job: dict) -> dict:
    name, kind, k, tseed = job["name"], job["kind"], job["k"], job["table_seed"]
    dec = H.direct if kind == "direct" else (H.make_balanced(k) if kind == "balanced" else H.make_scrambled(H.direct, k))
    table = score_table(tseed)
    t0 = time.time()
    geo = geometry(dec, table)
    hits = []; firsts = []; budget = None
    for ss in job["search_seeds"]:
        hc = hill_climb(dec, table, H.independent_parents(CAMPAIGN_SEED + 1000 * tseed + ss, job["parents"]), job["steps"], job["lam"], CAMPAIGN_SEED + 7 * ss + tseed)
        budget = hc["evals"]
        hits.append(1 if hc["first_hit_evals"] is not None else 0)
        firsts.append(hc["first_hit_evals"] if hc["first_hit_evals"] is not None else budget + 1)
    med = sorted(firsts)[len(firsts) // 2]
    return {"arm": kind, "encoding": name, "kind": kind, "k": k, "table_seed": tseed, "seed": tseed, **geo,
            "first_hits": firsts, "hits": sum(hits), "median_first_hit": med, "log_first_hit": round(math.log10(med), 4), "budget_evals": budget,
            "table_max": max(table), "wall_s": round(time.time() - t0, 1)}


class Geometry(Experiment):
    ID = "C2-SFE-08"
    TITLE = "encoding geometry: what predicts search efficiency"
    PARENTS = ["SFE-06"]
    ARM_FIELD = "encoding"
    METRICS = ("median_first_hit", "accessible_variation", "local_improvement_prob", "basin_share", "deceptive_share")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", nargs="*", type=int, default=[1, 2, 3, 4])
    ap.add_argument("--n-balanced", type=int, default=6)
    ap.add_argument("--n-scrambled", type=int, default=6)
    ap.add_argument("--search-seeds", nargs="*", type=int, default=[1, 2, 3])
    ap.add_argument("--parents", type=int, default=8)
    ap.add_argument("--steps", type=int, default=40)
    ap.add_argument("--lam", type=int, default=4)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    X = Geometry(dry_run=a.dry_run, procs=a.procs)
    encodings = [("direct", "direct", 0)] + [("balanced_%d" % k, "balanced", k) for k in range(1, a.n_balanced + 1)] + \
                [("scrambled_%d" % k, "scrambled", k) for k in range(1, a.n_scrambled + 1)]
    X.seal({
        "question": "Over %d encodings of one fixed evaluator (block-output score of the 256 elementary CA rules, %d score tables), which preregistered "
                    "neighbourhood statistic rank-correlates with evaluations-to-first-hit of a (1+%d) hill climb? PRIMARY: does accessible variation "
                    "(the parent's proxy) predict efficiency (expected NEGATIVE rho, |rho| >= 0.5)?" % (len(encodings), len(a.tables), a.lam),
        "parent_evidence": "SFE-06: direct first hit 13/53/53 evaluations, balanced 653/97/89 with ~50% more accessible variation, scrambled 971/-/190 (n=3); "
                           "accessible variation decoupled from navigability (L-023).",
        "assay_capability_requirement": "the direct encoding reaches the threshold in >= 2 of %d tables (else POSITIVE_CONTROL_FAILED: the evaluator has no "
                                        "reachable threshold region for the climb)" % len(a.tables),
        "positive_control": "direct encoding hill climb (hits >= 1 of %d search seeds) on each table" % len(a.search_seeds),
        "reachability_estimate": {"note": "not a WSE cell; the CA rule space is enumerated exhaustively (4096 genotypes per encoding); the reachability table does not apply"},
        "arms": [e[0] for e in encodings],
        "crn_policy": "one score table per table seed shared by every encoding; hill-climb parents and mutation streams keyed on (table seed, search seed) "
                      "so every encoding climbs from the same genotypes with the same flip sequence",
        "budget": {"tables": a.tables, "encodings": len(encodings), "search_seeds": a.search_seeds, "parents": a.parents, "steps": a.steps, "lam": a.lam,
                   "threshold": THRESHOLD, "n_cells": N_CELLS, "n_ics": N_ICS, "steps_ca": STEPS},
        "primary_observable": "log10(median evaluations to first hit, censored at budget+1) per encoding x table; rank correlation with each statistic over all rows",
        "claim_ceiling": "weak; one evaluator family, one climber; a capable negative for a statistic = it does not predict this climber's efficiency here",
        "falsification_condition": "rho(accessible_variation, log_first_hit) > -0.5 => the parent's proxy does not predict; every other statistic reported with its rho",
        "typed_failure_conditions": ["POSITIVE_CONTROL_FAILED (direct hits in < 2 tables)", "ENGINE_FAILURE / INSTRUMENT_FAILURE"],
        "expected_machine_telemetry": ["six geometry statistics + threshold_share per row (threshold_share must be identical across encodings: a decoder-totality check)",
                                       "first hits per search seed", "rho table for every statistic"],
        "machine_changes_exercised": ["B (rank_correlation primary in states)", "I"],
        "decl": {"positive_control": {"arm": "direct", "metric": "hits", "min": 1, "min_rows": 2},
                 "primary": {"type": "rank_correlation", "x": "accessible_variation", "y": "log_first_hit", "expected_sign": -1, "min_abs_rho": 0.5},
                 "statistics": STATS},
    })
    X.decision("D2-016: the primary is the PARENT'S proxy (accessible variation); the other six statistics are reported with their rho and none is promoted by the harness")
    X.open("cmp2-sfe08")
    wid = X.world("geometry", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    jobs = [{"name": nm, "kind": kd, "k": k, "table_seed": t, "search_seeds": a.search_seeds, "parents": a.parents, "steps": a.steps, "lam": a.lam}
            for t in a.tables for nm, kd, k in encodings]
    rows = X.pool_map(run_cell, jobs, "geometry_s")
    rhos = {st: S.spearman([r[st] for r in rows if r.get(st) is not None], [r["log_first_hit"] for r in rows if r.get(st) is not None]) for st in STATS}
    X.receipt["rho"] = {k: (None if v is None else round(v, 4)) for k, v in rhos.items()}
    X.receipt["threshold_share_by_table"] = {t: sorted({r["threshold_share"] for r in rows if r["table_seed"] == t}) for t in a.tables}
    X.receipt["per_kind"] = {kd: {"median_first_hit": [r["median_first_hit"] for r in rows if r["kind"] == kd], "hits": [r["hits"] for r in rows if r["kind"] == kd]}
                             for kd in ("direct", "balanced", "scrambled")}
    X.publish(wid, "geometry_table", "cmp2.encoding_geometry.v1", {"rows": [{k: v for k, v in r.items() if k != "first_hits"} for r in rows], "rho": X.receipt["rho"]},
              {"info_kind": "observation"})
    t0 = time.time()
    for r in rows:
        X.record(wid, r, {"experiment": X.ID, "encoding": r["encoding"], "table_seed": r["table_seed"], "threshold": THRESHOLD, "prereg_digest": X.prereg["prereg_digest"]},
                 {k: v for k, v in r.items()}, "SURVIVED" if r["hits"] > 0 else "FALSIFIED", (r["encoding"], r["table_seed"]))
    X.att.timing("records_s", t0)
    out = X.close(rows)
    print(json.dumps({"rho": X.receipt["rho"], "per_kind": X.receipt["per_kind"], "threshold_share_by_table": X.receipt["threshold_share_by_table"], **out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
