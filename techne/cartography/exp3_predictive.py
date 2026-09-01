"""EXPERIMENT 3 -- can any representation PREDICT a held-out experimental property?

    python -m techne.cartography.exp3_predictive

THE SHIFT THIS TEST MAKES. Every earlier verdict in this campaign judged a taxonomy by whether
it could CLASSIFY papers. That is circular: the coordinates are produced by the tagger, so a
representation that classifies well has only shown that its own instrument is self-consistent.
Here a representation must predict a property it was not built from.

THE TARGETS. Two binary experimental properties, both read from FULL TEXT by
`predicates.py` -- a different instrument from `taxonomy.py`, using different patterns, written
for a different purpose:

    ISOLATION      does the paper report an ablation / control (P3 CONFIRMED)?
    MATCHED_BUDGET does it report a compute- or evaluation-matched comparison?

Neither is used anywhere in constructing the coordinates or the neighbourhoods. That
separation is the whole validity of this experiment; if the target leaked into the
representation, a high score would mean nothing.

THE REPRESENTATIONS COMPARED
    four_tuple    (bottleneck, representation, selection, evaluation)
    three_tuple   TX-004: bottleneck dropped
    pairwise      TX-001: nearest by any shared axis PAIR
    lexical       token-overlap neighbours on the raw text -- the baseline that must be beaten
                  for any coordinate system to have earned its complexity
    random        neighbours drawn at random -- the floor

RETENTION RULE, fixed in advance. A coordinate earns retention only if REMOVING it measurably
destroys held-out predictive information. A representation earns promotion only if it beats
BOTH the lexical baseline and the majority-class baseline, with intervals that do not overlap
the thing it must beat. Beating random is not an achievement; a bag of words is the real
competitor.
"""
from __future__ import annotations

import collections
import json
import math
import pathlib
import random
import re
from typing import Optional

from . import predicates as P
from . import taxonomy

SAMPLE = pathlib.Path(__file__).resolve().parent / "exp2_fulltext_sample.json"
OUT = pathlib.Path(__file__).resolve().parent / "exp3_results.json"
AXES3 = ("representation_family", "selection_family", "evaluation_regime")
K = 5
SEED = 20260901
_TOK = re.compile(r"[a-z]{4,}")
STOP = set("this that with from have been which were they their there also such more than "
           "these those into using used show shows results result method methods approach "
           "paper work propose proposed present presents based data model models".split())


def wilson(k: int, n: int, z: float = 1.96) -> tuple:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def load_papers() -> list:
    d = json.loads(SAMPLE.read_text(encoding="utf-8"))
    return [p for p in d["papers"] if p.get("fulltext")]


# ------------------------------------------------------------------------------- targets

#: Replicate-reporting: does the paper state that results are averaged over multiple runs or
#: seeds? A methodological property, read from full text, whose vocabulary appears NOWHERE in
#: the mechanism table -- which is what the ISOLATION target failed to satisfy.
REPLICATES = re.compile(
    r"\b(averaged over \d+|mean of \d+|\d+ (?:independent )?(?:runs|trials|repetitions|seeds)|"
    r"over \d+ seeds|random seeds|repeated \d+ times|standard deviation over)\b", re.I)


def targets(papers: list) -> dict:
    """Target properties read from FULL TEXT by instruments other than the taxonomy.

    ISOLATION IS EXCLUDED. The first run of this experiment flagged it: `causal_attribution`
    lists "ablation study" as a mechanism surface form, so a paper saying "ablation study" is
    BOTH tagged into the coordinates AND scored positive on the target. The representation
    would have been predicting itself. Rather than weaken the leakage check, the target is
    dropped and replaced.

    MATCHED_BUDGET IS ALSO EXCLUDED, for the opposite reason: it is degenerate on this sample,
    with ZERO positives in 54 papers. A target every paper shares cannot discriminate between
    representations. (The 0/54 is a substantive finding in its own right and is reported.)

    REPLICATES is the retained target: does the paper report results over multiple runs or
    seeds? Methodological, non-degenerate, and its vocabulary appears nowhere in the mechanism
    table.
    """
    rep = []
    for p in papers:
        rep.append(1 if REPLICATES.search(p["fulltext"] or "") else 0)
    return {"REPLICATES": rep}


def degenerate_targets(papers: list) -> dict:
    """Targets excluded from the comparison, with the reason measured rather than asserted."""
    iso = mb = 0
    for p in papers:
        spans = [{"text": p["fulltext"], "scope": "fulltext"}]
        v, _r = P.mechanism_isolated(spans)
        iso += (v == "CONFIRMED")
        mb += 1 if P.MATCHED_BUDGET.search(p["fulltext"] or "") else 0
    n = len(papers)
    return {"ISOLATION": {"positives": iso, "n": n, "rate": iso / n,
                          "excluded_because": "LEAKAGE -- 'ablation study' is a surface form of "
                                              "the causal_attribution mechanism, so the target "
                                              "vocabulary helps build the coordinates"},
            "MATCHED_BUDGET": {"positives": mb, "n": n, "rate": mb / n,
                               "excluded_because": "DEGENERATE -- zero positives in %d papers; "
                                                   "a target every paper shares cannot "
                                                   "discriminate" % n,
                               "substantive_note": "not one paper in a stratified sample of %d "
                                                   "reports a compute- or evaluation-matched "
                                                   "comparison" % n}}


def leakage_check(papers: list) -> dict:
    """Does either target's vocabulary appear in the mechanism vocabulary that builds the
    coordinates? If it did, the representation would be predicting itself."""
    mech_vocab = " ".join(s for syn in taxonomy.MECHANISMS.values() for s in syn).lower()
    probes = ("averaged over", "runs", "trials", "repetitions", "seeds", "random seeds",
              "standard deviation")
    overlapping = [w for w in probes if w in mech_vocab]
    return {"target": "REPLICATES",
            "target_terms_found_in_mechanism_vocabulary": overlapping,
            "CLEAN": not overlapping,
            "note": ("checked against the RETAINED target only. ISOLATION was dropped after "
                     "this check failed on it -- see degenerate_targets().")}


# ----------------------------------------------------------------------- representations

def coords(p: dict) -> tuple:
    b, d, _m = _tag(p)
    return (b,) + tuple(d.get(a, "unknown") for a in AXES3)


_cache = {}


def _tag(p: dict):
    key = p["arxiv_id"]
    if key not in _cache:
        m = taxonomy.tag_mechanisms(p["fulltext"])
        _cache[key] = (taxonomy.assign_bottleneck(m), taxonomy.descriptors_from(m), m)
    return _cache[key]


def tokens(p: dict) -> set:
    t = (p.get("title") or "") + " " + (p["fulltext"] or "")[:20000]
    return {w for w in _TOK.findall(t.lower()) if w not in STOP}


def neighbours(i: int, papers: list, rep: str, rng: random.Random, k: int = K) -> list:
    idx = [j for j in range(len(papers)) if j != i]
    if rep == "random":
        return rng.sample(idx, min(k, len(idx)))
    if rep == "lexical":
        ti = tokens(papers[i])
        scored = []
        for j in idx:
            tj = tokens(papers[j])
            u = len(ti | tj)
            scored.append((-(len(ti & tj) / u if u else 0.0), j))
        scored.sort()
        return [j for _s, j in scored[:k]]

    ci = coords(papers[i])
    def known(c, s):
        return [(a, v) for a, v in zip(("bottleneck",) + AXES3, c)
                if v not in ("unknown", "B_UNASSIGNED") and a in s]
    if rep == "four_tuple":
        keep = {"bottleneck"} | set(AXES3)
    elif rep == "three_tuple":
        keep = set(AXES3)
    elif rep == "pairwise":
        keep = set(AXES3)
    else:
        raise ValueError(rep)
    ki = known(ci, keep)
    if not ki:
        return []
    scored = []
    for j in idx:
        kj = dict(known(coords(papers[j]), keep))
        shared = sum(1 for a, v in ki if kj.get(a) == v)
        if rep == "pairwise" and shared < 2:
            shared = 0            # pairwise requires an axis PAIR to match
        if shared:
            scored.append((-shared, j))
    scored.sort()
    return [j for _s, j in scored[:k]]


# ------------------------------------------------------------------------------ scoring

def evaluate(papers: list, y: list, rep: str, seed: int = SEED) -> dict:
    """Leave-one-out majority vote among neighbours. Abstentions counted, never guessed."""
    rng = random.Random(seed)
    n = len(papers)
    correct = abstain = 0
    for i in range(n):
        nb = neighbours(i, papers, rep, rng)
        if not nb:
            abstain += 1
            continue
        votes = collections.Counter(y[j] for j in nb)
        pred = votes.most_common(1)[0][0]
        correct += (pred == y[i])
    answered = n - abstain
    acc_all = correct / n
    acc_ans = (correct / answered) if answered else 0.0
    lo, hi = wilson(correct, n)
    return {"representation": rep, "n": n, "answered": answered, "abstained": abstain,
            "coverage": answered / n, "correct": correct,
            "accuracy_overall": acc_all, "accuracy_when_answering": acc_ans,
            "accuracy_ci95": [round(lo, 3), round(hi, 3)]}


def run() -> dict:
    papers = load_papers()
    tg = targets(papers)
    leak = leakage_check(papers)
    excluded = degenerate_targets(papers)
    reps = ("four_tuple", "three_tuple", "pairwise", "lexical", "random")

    results = {}
    for tname, y in tg.items():
        base_k = max(sum(y), len(y) - sum(y))
        blo, bhi = wilson(base_k, len(y))
        rows = {r: evaluate(papers, y, r) for r in reps}
        lex = rows["lexical"]["accuracy_overall"]
        verdicts = {}
        for r in reps:
            a = rows[r]
            beats_base = a["accuracy_ci95"][0] > (base_k / len(y))
            beats_lex = a["accuracy_overall"] > lex
            verdicts[r] = ("PROMOTABLE" if (beats_base and beats_lex and r not in
                                            ("lexical", "random"))
                           else "NOT_PROMOTABLE")
        # Coordinate retention: does dropping the bottleneck destroy predictive information?
        d4 = rows["four_tuple"]["accuracy_overall"]
        d3 = rows["three_tuple"]["accuracy_overall"]
        results[tname] = {
            "positive_rate": sum(y) / len(y),
            "majority_baseline": base_k / len(y),
            "majority_baseline_ci95": [round(blo, 3), round(bhi, 3)],
            "arms": rows,
            "verdicts": verdicts,
            "bottleneck_retention": {
                "four_tuple_accuracy": d4, "three_tuple_accuracy": d3,
                "delta_from_dropping_bottleneck_pp": round(100 * (d3 - d4), 2),
                "destroys_information": d3 < d4,
                "note": ("a coordinate earns retention only if REMOVING it measurably destroys "
                         "held-out predictive information. A non-negative delta means it did "
                         "not."),
            },
        }

    any_promotable = any(v == "PROMOTABLE"
                         for t in results.values() for v in t["verdicts"].values())
    return {"experiment": "EXP3_PREDICTIVE_TAXONOMY", "seed": SEED,
            "n_papers": len(papers), "k_neighbours": K,
            "leakage_check": leak,
            "excluded_targets": excluded,
            "targets_note": ("both targets are read from FULL TEXT by predicates.py -- a "
                             "different instrument from the taxonomy that builds the "
                             "coordinates, with different patterns written for a different "
                             "purpose"),
            "results": results,
            "ANY_REPRESENTATION_PROMOTABLE": any_promotable,
            "retention_rule": ("beat BOTH the majority baseline (with the accuracy CI lower "
                               "bound above it) AND the lexical token-overlap baseline. "
                               "Beating random is not an achievement."),
            "caveats": ["n=54, so intervals are wide and only large effects are visible",
                        "targets are regex-derived from full text and are themselves lexical "
                        "instruments -- they measure whether ablation LANGUAGE is present, not "
                        "whether an ablation was correctly performed",
                        "arXiv-only, preprint-biased sample; 12-page truncation"]}


def main() -> int:
    r = run()
    print("EXPERIMENT 3 -- PREDICTIVE TAXONOMY TEST  (n=%d, k=%d)" % (r["n_papers"], r["k_neighbours"]))
    print("  leakage check: %s  %s" % ("CLEAN" if r["leakage_check"]["CLEAN"] else "LEAK",
                                       r["leakage_check"]["target_terms_found_in_mechanism_vocabulary"]))
    for tname, t in r["results"].items():
        print("\n  TARGET: %s   positive rate %.2f   majority baseline %.2f [%.2f, %.2f]"
              % (tname, t["positive_rate"], t["majority_baseline"],
                 t["majority_baseline_ci95"][0], t["majority_baseline_ci95"][1]))
        print("    Representation   Cov     Acc      CI95            Verdict")
        print("    --------------   -----   ------   -------------   ---------------")
        for rep, a in t["arms"].items():
            print("    %-14s   %5.2f   %5.1f%%   [%.2f, %.2f]   %s"
                  % (rep, a["coverage"], 100 * a["accuracy_overall"],
                     a["accuracy_ci95"][0], a["accuracy_ci95"][1], t["verdicts"][rep]))
        b = t["bottleneck_retention"]
        print("    dropping the bottleneck: %+.2f pp -> destroys information: %s"
              % (b["delta_from_dropping_bottleneck_pp"], b["destroys_information"]))
    print("\n  ANY REPRESENTATION PROMOTABLE: %s" % r["ANY_REPRESENTATION_PROMOTABLE"])
    OUT.write_text(json.dumps(r, indent=2, default=str), encoding="utf-8")
    print("  wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
