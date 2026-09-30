"""Deterministic, stratified first selection of historical triplicates.

Rule (preregistered in roles/Hecate/prereg/2026-09-29_first_selection/):

  Strata are filled in the order below. Within a stratum, candidates are
  shuffled with random.Random(SEED + stratum_index) over the corpus sorted
  by id, and taken in that order, skipping any triple that shares a
  concept with one already selected (so the 16 cover 48 distinct concepts
  and no over-sampled concept such as Free Energy Principle can appear
  twice).

    S1 cross_extreme   3  three different fields AND three different
                          mechanism classes (Nous dictionary)
    S2 forged          3  Hephaestus forged it at least once
    S3 nous_high       3  Nous composite in the top decile of scored
                          triples, never forged
    S4 nous_failure    3  Nous marked it unproductive, or its composite
                          is in the bottom decile
    S5 random          4  uniform over the whole corpus: no filter at all
                          (the charter's "bizarre/random" slots)

  The ordinary skew of the source is left in S5 on purpose: it is the
  control for the other strata's filters.

    python -m hecate.select            # prints the selection as JSON
"""

from __future__ import annotations

import json
import random
import sys

from hecate import corpus

SEED = 20260929
STRATA = (
    ("S1_cross_extreme", 3),
    ("S2_forged", 3),
    ("S3_nous_high", 3),
    ("S4_nous_failure", 3),
    ("S5_random", 4),
)


def _deciles(rows):
    comps = sorted(r["history"]["nous_composite_max"] for r in rows
                   if r["history"]["nous_composite_max"] is not None)
    lo = comps[len(comps) // 10]
    hi = comps[(len(comps) * 9) // 10]
    return lo, hi


def _predicates(rows):
    lo, hi = _deciles(rows)

    def cross_extreme(r):
        f = {c["field"] for c in r["concepts"]}
        m = {c["mechanism"] for c in r["concepts"]}
        return len(f) == 3 and len(m) == 3

    def forged(r):
        return r["history"]["forged"]

    def nous_high(r):
        c = r["history"]["nous_composite_max"]
        return c is not None and c >= hi and not r["history"]["forged"]

    def nous_failure(r):
        c = r["history"]["nous_composite_max"]
        return r["history"]["nous_unproductive_any"] or (c is not None and c <= lo)

    def anything(r):
        return True

    return {
        "S1_cross_extreme": cross_extreme, "S2_forged": forged,
        "S3_nous_high": nous_high, "S4_nous_failure": nous_failure,
        "S5_random": anything,
    }, {"composite_bottom_decile_max": lo, "composite_top_decile_min": hi}


def select(rows, seed=SEED):
    rows = sorted(rows, key=lambda r: r["id"])
    preds, cuts = _predicates(rows)
    used_concepts, used_ids, picks, eligible = set(), set(), [], {}
    for si, (name, k) in enumerate(STRATA):
        cand = [r for r in rows if preds[name](r)]
        eligible[name] = len(cand)
        random.Random(seed + si).shuffle(cand)
        taken = 0
        for r in cand:
            if taken == k:
                break
            names = {c["name"] for c in r["concepts"]}
            if r["id"] in used_ids or names & used_concepts:
                continue
            picks.append({"stratum": name, **r})
            used_ids.add(r["id"])
            used_concepts |= names
            taken += 1
        if taken < k:
            raise RuntimeError(f"stratum {name}: only {taken} of {k} eligible")
    return picks, {"seed": seed, "eligible_per_stratum": eligible, **cuts}


if __name__ == "__main__":
    picks, meta = select(corpus.load())
    json.dump({"meta": meta, "selection": picks}, sys.stdout, indent=2, sort_keys=True)
    print()
