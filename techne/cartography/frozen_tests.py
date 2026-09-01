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
        hits_by_arm = {}
        for arm, min_known in (("four_tuple", 4), ("pairwise", 2), ("marginal", 1)):
            placed = [h for h in hold if len(known(coords(h))) >= min_known]
            # neighbours are drawn only from training genomes the same archive would place
            tr = [t for t in train if len(known(coords(t))) >= min_known]
            hits = {h["research_genome_id"]: cross_field_hit(
                h, neighbours_of(h, tr, mutated=False)) for h in placed}
            hits_by_arm[arm] = hits
            cf = sum(1 for v in hits.values() if v)
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
        res["non_degradation_paired"] = _paired(hits_by_arm["four_tuple"],
                                                hits_by_arm["pairwise"])
        per_seed.append(res)
    out = {"test_id": "TX-001-partial-cells", "arms": per_seed}
    out["non_degradation_loo"] = _tx001_loo(pool)
    out["ceiling"] = satisfiability_ceiling(pool, pool)
    return out


def _paired(four: dict, pair: dict) -> dict:
    """The frozen non-degradation clause, read as it is written.

    "not degrade the cross-field neighbour quality of THOSE IT ALREADY PLACED" is a PAIRED
    comparison on the papers the 4-tuple archive places, not a comparison of two marginal
    rates over two different paper sets. The first pass of this harness computed the marginal
    version, which is a different and easier question. This is the paired one.
    """
    shared = sorted(set(four) & set(pair))
    lost = [i for i in shared if four[i] and not pair[i]]
    gained = [i for i in shared if pair[i] and not four[i]]
    return {"n_comparable": len(shared),
            "degraded": len(lost), "improved": len(gained),
            "verdict": ("NO_DEGRADATION" if shared and not lost
                        else "DEGRADED" if lost
                        else "UNDERPOWERED_n0"),
            "power_note": ("n_comparable is the number of papers the 4-tuple archive places "
                           "at all. Below roughly 10 this clause cannot distinguish "
                           "no-degradation from no-information.")}


def _tx001_loo(pool: list) -> dict:
    """SUPPLEMENT, not the frozen test: leave-one-out to recover power on the paired clause.

    The frozen protocol holds out 25%, which leaves the 4-tuple arm with a single-digit
    comparable set and therefore no ability to detect degradation either way. Leave-one-out
    uses the same predicate and the same neighbour rule over the whole abstract-bearing pool,
    so every paper the 4-tuple archive can place enters the paired comparison. It is reported
    as a power-recovery supplement and makes NO pass claim of its own; the frozen 25% result
    above remains the adjudicated one.
    """
    res = {}
    hits_by_arm = {}
    for arm, min_known in (("four_tuple", 4), ("pairwise", 2)):
        hits = {}
        for h in pool:
            if len(known(coords(h))) < min_known:
                continue
            tr = [t for t in pool
                  if t["research_genome_id"] != h["research_genome_id"]
                  and len(known(coords(t))) >= min_known]
            hits[h["research_genome_id"]] = cross_field_hit(
                h, neighbours_of(h, tr, mutated=False))
        hits_by_arm[arm] = hits
        res[arm] = {"placed": len(hits),
                    "placement_rate": round(len(hits) / len(pool), 4) if pool else None,
                    "cross_field_hits": sum(1 for v in hits.values() if v),
                    "cross_field_rate": (round(sum(1 for v in hits.values() if v) / len(hits), 4)
                                         if hits else None)}
    res["paired"] = _paired(hits_by_arm["four_tuple"], hits_by_arm["pairwise"])
    return res


# ------------------------------------------------------------------------------------ TX-003

def satisfiability_ceiling(held: list, pool: list) -> dict:
    """How many held-out papers COULD pass the cross-field criterion, under any archive?

    A metric needs a ceiling as much as it needs a floor. The frozen criterion requires a
    shared mechanism tag that is absent from the held-out paper's own title -- but the tagger
    is lexical, so a paper whose every tag came from its title has no eligible tag at all, and
    a paper whose only eligible tags appear on no retrievable paper has no eligible partner.
    Neither case is reachable by improving the archive, the axes, or the mutation. If the
    ceiling sits below the pass threshold the test cannot be passed, and its failure is a fact
    about the test rather than about the papers.

    This is the LIM-003 error class -- a kill made structurally impossible reads as a
    confirmed absence -- and the campaign has already been bitten by it once.
    """
    tag_pop = {}
    for g in pool:
        for m in set(g.get("claimed_mechanism") or []):
            tag_pop[m] = tag_pop.get(m, 0) + 1
    detail, n_eligible_tag, n_usable = [], 0, 0
    for g in held:
        title = g.get("title") or ""
        abs_only = [m for m in (g.get("claimed_mechanism") or [])
                    if not title_contains_mechanism(title, m)]
        usable = [m for m in abs_only if tag_pop.get(m, 0) > 0]
        n_eligible_tag += 1 if abs_only else 0
        n_usable += 1 if usable else 0
        detail.append({"id": g["research_genome_id"], "title": title[:80],
                       "tags": g.get("claimed_mechanism") or [],
                       "abstract_only_tags": abs_only, "usable_tags": usable,
                       "can_ever_pass": bool(usable)})
    return {"n_held": len(held),
            "with_any_abstract_only_tag": n_eligible_tag,
            "SATISFIABILITY_CEILING": n_usable,
            "ceiling_rate": round(n_usable / len(held), 4) if held else None,
            "detail": detail}


def run_tx003(seed: int = 20260901) -> dict:
    corpus = load_corpus()
    mi = [g for g in corpus if is_mi(g)]
    non_mi = [g for g in corpus if not is_mi(g)]
    out = {"test_id": "TX-003-coordinates-cannot-express-MI",
           "n_mi": len(mi), "n_non_mi": len(non_mi), "seed": seed,
           "ceiling": satisfiability_ceiling(mi, non_mi),
           "pass_threshold_papers": len(mi) // 2 + 1,
           "arms": {}}
    # The last two arms are a DIAGNOSTIC, not part of the frozen test and making no pass
    # claim. They exist because the frozen arms cannot separate two very different failures:
    # "MI is inexpressible in these coordinates" (TX-003's thesis) and "the 4-tuple archive
    # has almost no occupants to retrieve, so nothing can be retrieved from it" (TX-001's
    # thesis). Re-running the same predicate under the pairwise geometry answers that.
    for arm, mutated, min_known in (("current_axes", False, 4), ("mutated_axes", True, 4),
                                    ("DIAG_current_pairwise", False, 2),
                                    ("DIAG_mutated_pairwise", True, 2)):
        placed = [h for h in mi if len(known(coords(h, mutated))) >= min_known]
        # cross-field: neighbours must be NON-MI papers -- that is what "cross-field" means here
        tr = [t for t in non_mi if len(known(coords(t, mutated))) >= min_known]
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
            "is_frozen_test_arm": not arm.startswith("DIAG_"),
            "min_known_coords": min_known,
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
