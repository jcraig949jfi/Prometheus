"""Frozen-test harness for the cartography campaign's outstanding taxonomy mutations.

WHY THIS FILE EXISTS. At cycle 032 the campaign recorded TRAJ-001: placed-paper growth had
stopped (6, 3, 1, 0 across cycle bands) while raw corpus growth continued, and the stated
recommendation was to stop spending cycles on acquisition and start spending them on the
FROZEN TESTS that TX-001 and TX-003 already owe. Cycles 033-037 kept acquiring. This module
is that redirection made executable.

WHAT IS FROZEN AND WHAT IS NOT. The protocols and pass conditions implemented here were
written down in `store/taxonomy_events.jsonl` at cycle 021 (TX-001) and cycle 028 (TX-003),
BEFORE any of this code existed and before any result was seen. This file may not restate
them more favourably; where the frozen text underdetermines an implementation choice, the
choice is recorded in DEVIATIONS below with its justification, and the alternative reading is
reported alongside rather than silently discarded.

ADJUDICATION RULE (campaign manifest). An LLM or a heuristic may PROPOSE; only a deterministic
predicate over stored evidence may write CONFIRMED. Everything below is deterministic given
(store contents, seed). Nothing here applies a mutation. A PASS licenses application as a
separate, later, reviewable act; a FAIL leaves the taxonomy exactly where it is.

DEVIATIONS FROM THE LITERAL FROZEN TEXT (declared before the numbers, not after):

  D1. "abstract-bearing genomes". The stored field `abstract_available` is None for all 135
      genomes discovered in cycles 0-18 -- the field post-dates them and was never backfilled
      -- while 123 of those 135 in fact carry an abstract evidence span. Selecting on the flag
      would run the test on 95 genomes instead of 218, and the 95 would be entirely
      post-cycle-20, i.e. a recency-biased sample of exactly the region where the instrument
      is known to degrade. This harness therefore derives abstract-bearing from the presence
      of an `abstract`-scoped evidence span, which is what the claim predicates already do.
      Filed as LIM-009.

  D2. "does the archive place it at all" for the PAIRWISE archive. The frozen text says a
      paper contributes to every axis and axis-pair it can be placed on, so pairwise placement
      requires at least one full axis-PAIR, i.e. >= 2 known coordinates. The weaker marginal
      reading (>= 1 known coordinate) is reported as a secondary line and is NOT the pass
      criterion, because a criterion that counts one known axis as placement would make the
      mutation pass by definition.

  D3. "nearest archive neighbours". Undefined in the frozen text. Implemented as the k=5
      training genomes with the largest number of shared KNOWN coordinates (ties broken by
      genome id, so the result is seed-independent given the split). Under the 4-tuple archive
      this reduces to same-cell occupants, which is the intended reading there.

  D4. Chance floor. The frozen text states a pass condition but no null. A cross-field
      neighbour rate is meaningless without one: if a large fraction of the corpus carries
      `tree_gp`, then randomly drawn neighbours share a mechanism tag often. Every
      neighbour-quality number below is therefore reported against a shuffled-neighbour null
      (neighbours drawn uniformly from the training set, same k, 200 resamples) with its 95th
      percentile published as the chance floor. A rate that does not clear its own floor is
      reported as NOT DISTINGUISHABLE FROM CHANCE regardless of how it compares to the other
      archive.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import random
import statistics

from . import store
from .schema import digest, now_iso
from .taxonomy import _COMPILED

AXES = ("bottleneck", "representation_family", "selection_family", "evaluation_regime")
UNKNOWN = {"bottleneck": "B_UNASSIGNED", "representation_family": "unknown",
           "selection_family": "unknown", "evaluation_regime": "unknown"}

#: The mechanism tags that make a paper a mechanistic-interpretability paper for TX-003.
#: Taken verbatim from the mechanisms TX-003 listed as detected on its 19 MI papers.
MI_MECHANISMS = {"circuit_discovery", "sparse_autoencoder", "circuit_representation",
                 "causal_attribution"}

#: The TX-003 mutation, exactly as proposed at cycle 028. Applied ONLY inside the test's
#: mutated arm; the live taxonomy is untouched.
TX003_SELECTION_ADD = {"circuit_discovery": "causal_intervention",
                       "causal_attribution": "causal_intervention",
                       "distillation": "causal_intervention"}
TX003_EVALUATION_ADD = {"circuit_discovery": "faithfulness_to_reference",
                        "causal_attribution": "faithfulness_to_reference",
                        "distillation": "faithfulness_to_reference",
                        "circuit_representation": "faithfulness_to_reference",
                        "sparse_autoencoder": "faithfulness_to_reference"}

NULL_RESAMPLES = 200
K_NEIGHBOURS = 5


# ---------------------------------------------------------------------------- corpus loading

def has_abstract(g: dict) -> bool:
    """D1: derived from evidence, not from the stale `abstract_available` flag."""
    return any(s.get("scope") == "abstract" for s in (g.get("evidence_spans") or []))


def load_corpus() -> list:
    cur = store.current("genomes")
    return sorted(cur.values(), key=lambda g: g["research_genome_id"])


def coords(g: dict, mutated: bool = False) -> dict:
    d = dict(g.get("descriptors") or {})
    c = {"bottleneck": g.get("bottleneck", "B_UNASSIGNED"),
         "representation_family": d.get("representation_family", "unknown"),
         "selection_family": d.get("selection_family", "unknown"),
         "evaluation_regime": d.get("evaluation_regime", "unknown")}
    if mutated:
        mechs = set(g.get("claimed_mechanism") or [])
        if c["selection_family"] == "unknown":
            for m, v in TX003_SELECTION_ADD.items():
                if m in mechs:
                    c["selection_family"] = v
                    break
        if c["evaluation_regime"] == "unknown":
            for m, v in TX003_EVALUATION_ADD.items():
                if m in mechs:
                    c["evaluation_regime"] = v
                    break
        # The mutation does not touch bottleneck assignment, and this harness does not either.
        # Silently repairing a second axis would make the two arms incomparable.
    return c


def known(c: dict) -> list:
    return [a for a in AXES if c[a] != UNKNOWN[a]]


# ------------------------------------------------------------------- neighbour-quality metric

def title_contains_mechanism(title: str, mech: str) -> bool:
    """Does the paper's TITLE lexically carry this mechanism's vocabulary?

    The frozen test asks for a shared tag the held-out paper's title does NOT contain, so a
    shared tag that is simply printed in both titles proves vocabulary overlap, not mechanism
    overlap, and must not count.
    """
    for pat in _COMPILED.get(mech, ()):
        if pat.search(title or ""):
            return True
    return False


def cross_field_hit(held: dict, neighbours: list) -> bool:
    """Frozen criterion: >= 1 neighbour shares a mechanism tag absent from held's title."""
    hm = set(held.get("claimed_mechanism") or [])
    if not hm:
        return False
    title = held.get("title") or ""
    for nb in neighbours:
        shared = hm & set(nb.get("claimed_mechanism") or [])
        for m in shared:
            if not title_contains_mechanism(title, m):
                return True
    return False


def is_mi(g: dict) -> bool:
    return bool(MI_MECHANISMS & set(g.get("claimed_mechanism") or []))


def neighbours_of(held: dict, train: list, mutated: bool, require_non_mi: bool = False,
                  k: int = K_NEIGHBOURS) -> list:
    """D3: k training genomes sharing the most KNOWN coordinates. Deterministic."""
    hc = coords(held, mutated)
    hk = known(hc)
    if not hk:
        return []
    scored = []
    for t in train:
        if require_non_mi and is_mi(t):
            continue
        if t["research_genome_id"] == held["research_genome_id"]:
            continue
        tc = coords(t, mutated)
        s = sum(1 for a in hk if tc[a] == hc[a])
        if s:
            scored.append((-s, t["research_genome_id"], t))
    scored.sort(key=lambda x: (x[0], x[1]))
    return [t for _, _, t in scored[:k]]


def null_floor(held_set: list, train: list, rng: random.Random,
               require_non_mi: bool = False, k: int = K_NEIGHBOURS) -> dict:
    """D4: chance floor for the cross-field rate under uniformly random neighbours."""
    pool = [t for t in train if not (require_non_mi and is_mi(t))]
    if not pool or not held_set:
        return {"mean": None, "p95": None, "max": None, "resamples": 0}
    rates = []
    for _ in range(NULL_RESAMPLES):
        hits = 0
        for h in held_set:
            nb = rng.sample(pool, min(k, len(pool)))
            if cross_field_hit(h, nb):
                hits += 1
        rates.append(hits / len(held_set))
    rates.sort()
    return {"mean": round(statistics.fmean(rates), 4),
            "p95": round(rates[int(0.95 * (len(rates) - 1))], 4),
            "max": round(rates[-1], 4),
            "resamples": NULL_RESAMPLES}


# ------------------------------------------------------------------------------------ TX-001

def run_tx001(seeds=(20260901,), holdout_frac: float = 0.25) -> dict:
    corpus = load_corpus()
    pool = [g for g in corpus if has_abstract(g)]
    per_seed = []
    for seed in seeds:
        rng = random.Random(seed)
        idx = list(range(len(pool)))
        rng.shuffle(idx)
        n_hold = int(round(holdout_frac * len(pool)))
        hold = [pool[i] for i in idx[:n_hold]]
        train = [pool[i] for i in idx[n_hold:]]

        res = {"seed": seed, "n_pool": len(pool), "n_train": len(train), "n_held": len(hold)}
        for arm, min_known in (("four_tuple", 4), ("pairwise", 2), ("marginal", 1)):
            placed = [h for h in hold if len(known(coords(h))) >= min_known]
            # neighbours are drawn only from training genomes the same archive would place
            tr = [t for t in train if len(known(coords(t))) >= min_known]
            cf = sum(1 for h in placed
                     if cross_field_hit(h, neighbours_of(h, tr, mutated=False)))
            floor = null_floor(placed, tr, random.Random(seed + 7))
            res[arm] = {
                "placed": len(placed),
                "placement_rate": round(len(placed) / len(hold), 4) if hold else None,
                "cross_field_hits": cf,
                "cross_field_rate": round(cf / len(placed), 4) if placed else None,
                "chance_floor_p95": floor["p95"],
                "chance_floor_mean": floor["mean"],
                "beats_chance": (None if not placed or floor["p95"] is None
                                 else (cf / len(placed)) > floor["p95"]),
                "train_archive_size": len(tr),
            }
        per_seed.append(res)
    return {"test_id": "TX-001-partial-cells", "arms": per_seed}


# ------------------------------------------------------------------------------------ TX-003

def run_tx003(seed: int = 20260901) -> dict:
    corpus = load_corpus()
    mi = [g for g in corpus if is_mi(g)]
    non_mi = [g for g in corpus if not is_mi(g)]
    out = {"test_id": "TX-003-coordinates-cannot-express-MI",
           "n_mi": len(mi), "n_non_mi": len(non_mi), "seed": seed, "arms": {}}
    for arm, mutated in (("current_axes", False), ("mutated_axes", True)):
        placed = [h for h in mi if len(known(coords(h, mutated))) >= 4]
        # cross-field: neighbours must be NON-MI papers -- that is what "cross-field" means here
        tr = [t for t in non_mi if len(known(coords(t, mutated))) >= 4]
        cf = 0
        detail = []
        for h in mi:
            nb = neighbours_of(h, tr, mutated=mutated, require_non_mi=True)
            hit = cross_field_hit(h, nb)
            cf += 1 if hit else 0
            detail.append({"id": h["research_genome_id"], "title": (h.get("title") or "")[:90],
                           "cell": coords(h, mutated), "n_neighbours": len(nb),
                           "cross_field_hit": hit,
                           "neighbours": [(n.get("title") or "")[:60] for n in nb[:3]]})
        floor = null_floor(mi, tr, random.Random(seed + 11), require_non_mi=True)
        out["arms"][arm] = {
            "placed_on_4_tuple": len(placed),
            "placement_rate": round(len(placed) / len(mi), 4) if mi else None,
            "cross_field_hits": cf,
            "cross_field_rate": round(cf / len(mi), 4) if mi else None,
            "chance_floor_p95": floor["p95"],
            "chance_floor_mean": floor["mean"],
            "majority_pass": (cf / len(mi) > 0.5) if mi else None,
            "beats_chance": (None if not mi or floor["p95"] is None
                             else (cf / len(mi)) > floor["p95"]),
            "non_mi_archive_size": len(tr),
            "detail": detail,
        }
    return out


# --------------------------------------------------------------------------------------- CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="run the campaign's frozen taxonomy-mutation tests")
    ap.add_argument("--test", choices=["tx001", "tx003", "both"], default="both")
    ap.add_argument("--seeds", default="20260901,20260902,20260903")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    seeds = [int(s) for s in a.seeds.split(",") if s.strip()]
    corpus = load_corpus()
    result = {"ran_at": now_iso(), "seeds": seeds,
              "corpus_size": len(corpus),
              "abstract_bearing_by_evidence": sum(1 for g in corpus if has_abstract(g)),
              "abstract_bearing_by_flag": sum(1 for g in corpus if g.get("abstract_available")),
              "k_neighbours": K_NEIGHBOURS, "null_resamples": NULL_RESAMPLES}
    if a.test in ("tx001", "both"):
        result["tx001"] = run_tx001(seeds=seeds)
    if a.test in ("tx003", "both"):
        result["tx003"] = run_tx003(seed=seeds[0])
    result["_digest"] = digest(result)
    text = json.dumps(result, indent=2, ensure_ascii=False, default=str)
    if a.out:
        pathlib.Path(a.out).write_text(text, encoding="utf-8")
        print("wrote " + a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
