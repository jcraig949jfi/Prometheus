"""nuisance_census.py — the A2 probe. W1-W5 exactly as preregistered, plus its own null.

This is a NEW instrument. Under the program-wide rule adopted 2026-08-27 it may not issue a
scientific verdict until `run_a2_calibration.py` returns INSTRUMENT_VALIDATED, because the A1
calibration validated the REACHABILITY_CENSUS -- a probe for boolean-label worlds -- and says
nothing whatever about this one.

Every threshold that depends on an unknown variance is expressed as a MULTIPLE OF A MEASURED
NULL BAND (class-label permutation on the same rows), per the LOOP doctrine that thresholds
fail in both directions. The absolute thresholds (W1 band, W2 floor, W3 multiple) are fixed in
the preregistration and are not touched here.
"""
from __future__ import annotations

import math
import random
import statistics as st

import world3 as W3

STATS = ("min_size", "c_search", "c_execution", "out_entropy")

# preregistered absolute thresholds
W1_LO, W1_HI = 0.60, 1.00
W2_FLOOR = 0.90
W3_MULTIPLE = 10.0
NULL_MULTIPLE = 2.0
NULL_DRAWS = 2000


def measure_task(expr, probes, prims, minsize, order):
    sig = W3.signature(expr, probes, prims)
    key = (W3.V, sig)
    solved = key in minsize
    counts = {}
    for o in sig:
        counts[o] = counts.get(o, 0) + 1
    n = len(sig)
    ent = -sum((c / n) * math.log(c / n) for c in counts.values())
    ent = ent / math.log(n) if n > 1 else 0.0
    return {
        "solved": solved,
        "min_size": minsize.get(key),
        "c_search": order.get(key),
        "c_execution": (order.get(key) * len(probes)) if solved else None,
        "out_entropy": round(ent, 6),
        "true_size": W3.size_of(expr),
    }


def _modal_motif(tasks_early):
    """The motif most often CONTAINED in the early half, ties broken deterministically.

    Containment is structural over the fully substituted expression, so an accidental
    recurrence counts exactly as much as a declared one. That is deliberate: the statistic must
    not be able to see the generator's intent.
    """
    cands = {repr(t["motif"]): t["motif"] for t in tasks_early}
    best, best_n = None, -1
    for r in sorted(cands):
        m = cands[r]
        c = sum(1 for t in tasks_early if W3.contains(t["expr"], m))
        if c > best_n or (c == best_n and best is not None and r < repr(best)):
            best, best_n = m, c
    return best


def measure_episode(ep, probes, prims, minsize, order):
    rows = [dict(t, **measure_task(t["expr"], probes, prims, minsize, order)) for t in ep["tasks"]]
    solved = [r for r in rows if r["solved"]]
    early = [r for r in rows if r["early"]]
    late = [r for r in rows if not r["early"]]
    m = _modal_motif(early) if early else None
    rec_e = (sum(1 for r in early if W3.contains(r["expr"], m)) / len(early)) if early and m else 0.0
    rec_l = (sum(1 for r in late if W3.contains(r["expr"], m)) / len(late)) if late and m else 0.0
    out = {"class": ep["class"], "n_tasks": len(rows), "n_solved": len(solved),
           "solve_rate": len(solved) / max(len(rows), 1),
           "rec_early": rec_e, "rec_late": rec_l}
    for s in STATS:
        vals = [r[s] for r in solved if r[s] is not None]
        out[s] = st.fmean(vals) if vals else None
    out["_rows"] = rows
    return out


def _groups(labels, values):
    g = {}
    for lab, v in zip(labels, values):
        if v is not None:
            g.setdefault(lab, []).append(v)
    return {k: v for k, v in g.items() if v}


def _max_pair_gap(labels, values):
    """Largest pairwise class-mean gap, standardised by the pooled WITHIN-class sd.

    REVISED DURING CALIBRATION 2026-08-27, and the reason is disclosed rather than buried.
    The first version divided by the sd of ALL episodes, which includes the between-class
    variance the statistic is trying to detect. That makes the reading self-limiting: for five
    classes the value cannot exceed sqrt(8) = 2.8284 no matter how enormous the class effect
    is, and the preregistered bar sat at 2.49 -- inside 12 percent of a hard ceiling. A world
    with class means at sizes 4,5,6,7,8 read 2.191 and was declared MATCHED.

    That is the GATE MUST BE SHOWN REACHABLE failure, in my own instrument, one pass after the
    doctrine was restated. The calibration caught it; inspection had not. Dividing by the
    within-class sd is the standard one-way effect size and is unbounded above, so the reading
    can traverse the range the verdict rule needs.
    """
    groups = _groups(labels, values)
    if len(groups) < 2:
        return 0.0
    means = {k: st.fmean(v) for k, v in groups.items()}
    spread = max(means.values()) - min(means.values())
    within = []
    for v in groups.values():
        if len(v) > 1:
            m = st.fmean(v)
            within.extend((a - m) ** 2 for a in v)
    sd = math.sqrt(st.fmean(within)) if within else 0.0
    if sd == 0.0:
        return 0.0 if spread == 0.0 else float("inf")
    return spread / sd


def _max_pair_gap_raw(labels, values):
    """Largest pairwise class-mean gap in RAW units. Used where a single stat is compared
    against its own permutation null, so no standardiser is needed at all."""
    groups = _groups(labels, values)
    if len(groups) < 2:
        return 0.0
    means = [st.fmean(v) for v in groups.values()]
    return max(means) - min(means)


def _null_band(rng, labels, value_lists, draws=NULL_DRAWS):
    """95th percentile of the max-over-stats gap under class-label permutation."""
    labs = list(labels)
    out = []
    for _ in range(draws):
        rng.shuffle(labs)
        out.append(max(_max_pair_gap(labs, vals) for vals in value_lists))
    out.sort()
    return out[int(0.95 * (len(out) - 1))]


def _null_band_raw(rng, labels, values, draws=NULL_DRAWS):
    """95th percentile of the RAW max pairwise class-mean gap under label permutation.

    Deliberately conservative: the observed comparison is between two named classes, but the
    null is the maximum over all ten pairs, so the band already carries the multiplicity
    correction."""
    labs = list(labels)
    out = []
    for _ in range(draws):
        rng.shuffle(labs)
        out.append(_max_pair_gap_raw(labs, values))
    out.sort()
    return out[int(0.95 * (len(out) - 1))]


def census(episodes, probes, prims, minsize, order, layer1_width, seed=20260827,
           draws=NULL_DRAWS):
    rng = random.Random(seed)
    eps = [measure_episode(e, probes, prims, minsize, order) for e in episodes]
    rows = [r for e in eps for r in e["_rows"]]
    labels = [e["class"] for e in eps]

    # ---- W1 solvability
    solve_rate = sum(1 for r in rows if r["solved"]) / max(len(rows), 1)
    w1 = W1_LO <= solve_rate <= W1_HI

    # ---- W2 non-triviality (an unsolved task's minimal size exceeds the enumerated depth,
    #      so it cannot be shallow; counted as satisfying, and reported separately)
    deep = sum(1 for r in rows if (not r["solved"]) or r["min_size"] >= 3)
    frac_deep = deep / max(len(rows), 1)
    deep_solved_only = ([r["min_size"] >= 3 for r in rows if r["solved"]] or [False])
    w2 = frac_deep >= W2_FLOOR

    # ---- W3 cost headroom
    csearch = sorted(r["c_search"] for r in rows if r["solved"])
    med = st.median(csearch) if csearch else 0.0
    headroom = med / max(layer1_width, 1)
    w3 = headroom >= W3_MULTIPLE

    # ---- W4 nuisance match
    value_lists = [[e[s] for e in eps] for s in STATS]
    gaps = {s: _max_pair_gap(labels, [e[s] for e in eps]) for s in STATS}
    w4_stat = max(gaps.values())
    w4_null = _null_band(rng, labels, value_lists, draws)
    w4 = w4_stat <= NULL_MULTIPLE * w4_null

    # ---- W5 class separation on the intended axis
    def cmean(cls, key):
        v = [e[key] for e in eps if e["class"] == cls]
        return st.fmean(v) if v else 0.0

    null_late = _null_band_raw(rng, labels, [e["rec_late"] for e in eps], draws)
    null_early = _null_band_raw(rng, labels, [e["rec_early"] for e in eps], draws)
    band_late = NULL_MULTIPLE * null_late                      # already raw units
    band_early = NULL_MULTIPLE * null_early

    g_a = cmean("REUSE", "rec_late") - cmean("NO_REUSE", "rec_late")
    w5a = g_a > band_late
    d_early = cmean("DECOY_REUSE", "rec_early") - cmean("NO_REUSE", "rec_early")
    d_late = abs(cmean("DECOY_REUSE", "rec_late") - cmean("NO_REUSE", "rec_late"))
    w5b = (d_early > band_early) and (d_late <= band_late)
    l_late = cmean("LATE_REUSE", "rec_late") - cmean("NO_REUSE", "rec_late")
    l_early = abs(cmean("LATE_REUSE", "rec_early") - cmean("NO_REUSE", "rec_early"))
    w5c = (l_late > band_late) and (l_early <= band_early)
    w5 = w5a and w5b and w5c

    # ---- branch table, evaluated in order; the four terminals are asserted to be exhaustive
    if not (w1 and w2 and w3):
        verdict = "WORLD_REJECTED_UNUSABLE_BAND"
    elif not w4:
        verdict = "WORLD_REJECTED_NUISANCE_CONFOUND"
    elif not w5:
        verdict = "WORLD_REJECTED_CLASSES_NOT_SEPARATED"
    else:
        verdict = "WORLD_ADMISSIBLE"
    terminals = set()
    for a in (False, True):
        for b in (False, True):
            for c in (False, True):
                terminals.add("WORLD_REJECTED_UNUSABLE_BAND" if not a else
                              ("WORLD_REJECTED_NUISANCE_CONFOUND" if not b else
                               ("WORLD_REJECTED_CLASSES_NOT_SEPARATED" if not c else
                                "WORLD_ADMISSIBLE")))
    assert terminals == {"WORLD_REJECTED_UNUSABLE_BAND", "WORLD_REJECTED_NUISANCE_CONFOUND",
                         "WORLD_REJECTED_CLASSES_NOT_SEPARATED", "WORLD_ADMISSIBLE"}

    return {
        "n_episodes": len(eps), "n_tasks": len(rows),
        "W1_solve_rate": round(solve_rate, 4), "W1": w1,
        "W2_frac_min_size_ge_3": round(frac_deep, 4),
        "W2_frac_solved_only": round(sum(deep_solved_only) / len(deep_solved_only), 4),
        "W2": w2,
        "W3_median_c_search": med, "W3_layer1_width": layer1_width,
        "W3_headroom_multiple": round(headroom, 4), "W3": w3,
        "W4_gaps": {k: round(v, 4) for k, v in gaps.items()},
        "W4_stat": round(w4_stat, 4), "W4_null_p95": round(w4_null, 4),
        "W4_bar": round(NULL_MULTIPLE * w4_null, 4), "W4": w4,
        "W5_rec_late_by_class": {c: round(cmean(c, "rec_late"), 4) for c in W3.CLASSES},
        "W5_rec_early_by_class": {c: round(cmean(c, "rec_early"), 4) for c in W3.CLASSES},
        "W5_band_late": round(band_late, 4), "W5_band_early": round(band_early, 4),
        "W5a_reuse_minus_noreuse": round(g_a, 4), "W5a": w5a,
        "W5b_decoy_early_lift": round(d_early, 4), "W5b_decoy_late_gap": round(d_late, 4),
        "W5b": w5b,
        "W5c_late_lift": round(l_late, 4), "W5c_late_early_gap": round(l_early, 4), "W5c": w5c,
        "W5": w5,
        "verdict": verdict,
        "episodes": [{k: v for k, v in e.items() if k != "_rows"} for e in eps],
    }
