"""
Synthesis-space census (D7 section 7).  ORACLE-lane instrument characterization.

Goal: make sure the intended wormhole structure is NOT essentially spelled by the
grammar. We measure behavioral richness, target-capable density, minimal crossing
size, single-template dominance, and topology reachability, then emit KILL flags.

Efficient: all family pairs share the same start S, so ONE Gz-closure per sample
covers every family target.
"""

from __future__ import annotations
import random
from collections import Counter

from substrate import Grammar, z_size, run_z, MicroFault
from synthlang import random_program, all_quoted
from evalz import evaluate


def _sig(ast, world, hoard, probe):
    out = []
    for v in probe:
        try:
            nv, _ = run_z(ast, v, world, hoard)
        except MicroFault:
            nv = v
        out.append(nv)
    return tuple(out)


def census(world, S, T, hoard, g: Grammar, n=15000, seed=7, family=None):
    rng = random.Random(seed)
    ids = sorted(hoard.keys())
    probe = list(world.states())[: min(24, world.p ** world.nreg)]
    family = family or [(S, T)]
    fam_targets = [T] + [ft for (fs, ft) in family if fs == S and ft != T]

    classes = set()
    n_cross = 0
    cross_sizes = []
    cross_uses = Counter()
    uses_ifz = uses_rep = 0
    sizes = []
    fam_cross = Counter()
    seen_asts = {}

    for _ in range(n):
        ast = random_program(rng, ids, g)
        sizes.append(z_size(ast))
        flat = str(ast)
        if "ifz" in flat:
            uses_ifz += 1
        if "rep" in flat:
            uses_rep += 1
        res = evaluate(ast, world, S, fam_targets, hoard)
        classes.add(_sig(ast, world, hoard, probe))
        if res["reached"][T]:
            n_cross += 1
            cross_sizes.append(z_size(ast))
            for a in set(all_quoted(ast)):
                cross_uses[a] += 1
        for t in fam_targets:
            if res["reached"][t]:
                fam_cross[t] += 1

    min_cross = min(cross_sizes) if cross_sizes else None
    dominance = None
    if n_cross:
        top_aid, top_n = cross_uses.most_common(1)[0]
        dominance = {"aid": top_aid, "frac_of_crossers": round(top_n / n_cross, 3)}

    report = {
        "samples": n,
        "distinct_behavior_classes": len(classes),
        "mean_size": round(sum(sizes) / len(sizes), 2),
        "primary_crossing_density": round(n_cross / n, 5),
        "min_crossing_size_seen": min_cross,
        "topology_ifz_frac": round(uses_ifz / n, 3),
        "topology_rep_frac": round(uses_rep / n, 3),
        "crosser_artifact_usage_top": dict(cross_uses.most_common(8)),
        "single_template_dominance": dominance,
        "family_crossing_density": {str(t): round(v / n, 5) for t, v in fam_cross.items()},
    }
    flags = []
    if report["primary_crossing_density"] > 0.05:
        flags.append("HIGH_CROSSING_DENSITY")
    if dominance and dominance["frac_of_crossers"] > 0.98 and (min_cross or 99) <= 2:
        flags.append("SINGLE_OPENER_DOMINATES")
    if report["distinct_behavior_classes"] < 50:
        flags.append("LOW_BEHAVIORAL_RICHNESS")
    report["KILL_FLAGS"] = flags
    return report
