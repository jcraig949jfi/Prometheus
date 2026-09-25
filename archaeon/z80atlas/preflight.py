"""Support / identifiability preflight for Atlas-style factor grammars (operator ruling 4, 2026-09-23).

Before an adaptive campaign's clock starts, prove mechanically that every intended causal comparison has support in what the
sampler will actually draw, and find structural coupling caused by constraints. The 72-hour Z80 x Atlas campaign would have failed
this: its sampler never drew a bare-niches world (topology not separable from migration/reservoir), and its reproduction matched
control silently dropped recombination and explicit_fitness (three factors changed at once).

Checks (grammar-generic; the grammar module supplies AXES, CONSTRAINTS, CONTEXT, NEUTRAL, spec_from_factors, factor_vector,
explore_step, matched_controls):
  1 STRUCTURAL ZEROS     every (axis=a, axis=b) level pair is tested for satisfiability (neutral completion + random completions).
                         A zero between two axes not linked in CONTEXT is UNDECLARED_COUPLING (FAIL): the sampler would condition
                         nothing on it.
  2 SAMPLER SUPPORT      the real exploration step is simulated DRAWS times from empty coverage and compared with the LEVEL-BALANCE
                         design (reference()); a level pair drawn at < STARVE_FRAC of its design rate is SAMPLER_STARVED.
  3 CONTRASTS            each declared contrast (two arm predicates + a hold predicate on the factor vector) needs MIN_SUPPORT
                         simulated draws per arm, and every level pair its arms rely on must not be starved.
  4 CONTROL AUDIT        for contrasts read through a constructed control, the constructor is applied to simulated treatments and
                         every factor it changes besides the contrast axis is counted: CONFOUNDED_CONTROL unless the clean subset
                         has MIN_SUPPORT, in which case RESTRICTED (the contrast may be read only on that subset).
Verdict PASS / PASS_WITH_RESTRICTIONS / FAIL. scheduler.start() refuses FAIL outright and PASS_WITH_RESTRICTIONS unless the
operator accepts the named restrictions (the family scorer does not restrict contrasts by itself).
"""
from __future__ import annotations

import itertools
import json
from collections import Counter
from typing import Callable, Dict, List

from proteus.foundry.prng import SplitMix64, seed_from

DRAWS = 20000
MIN_SUPPORT = 30
STARVE_FRAC = 0.25
COMPLETIONS = 300


def _is(axis, *levels):
    return lambda fv: str(fv[axis]) in {str(l) for l in levels}


def _has_pressure(p):
    return lambda fv: p in fv["pressure"].split("+")


def _all(*ps):
    return lambda fv: all(p(fv) for p in ps)


def _not(p):
    return lambda fv: not p(fv)


# The Z80 x Atlas campaign's intended causal readings (CAMPAIGN_CONTRACT / ATLAS_AXES), declared up front.
Z80ATLAS_CONTRASTS = [
    {"name": "topology_alone_niches_vs_well_mixed", "axis": "world.topology", "arms": [_is("world.topology", "niches"), _is("world.topology", "well_mixed")],
     "hold": _all(_is("world.migration", "none"), _is("world.reservoir", False), _is("world.env_dynamics", "fixed", "nonstationary", "env_mutate"))},
    {"name": "migration_within_niches", "axis": "world.migration", "arms": [_is("world.migration", "none"), _not(_is("world.migration", "none"))], "hold": _is("world.topology", "niches")},
    {"name": "reservoir_within_niches", "axis": "world.reservoir", "arms": [_is("world.reservoir", True), _is("world.reservoir", False)], "hold": _is("world.topology", "niches")},
    {"name": "recombination_within_EXTERNAL", "axis": "pressure", "arms": [_has_pressure("recombination"), _not(_has_pressure("recombination"))], "hold": _is("reproduction", "EXTERNAL")},
    {"name": "selection_explicit_vs_implicit_within_EXTERNAL", "axis": "pressure", "arms": [_has_pressure("explicit_fitness"), _has_pressure("implicit_survival")], "hold": _is("reproduction", "EXTERNAL")},
    {"name": "init_random_vs_seeded", "axis": "init", "arms": [_is("init", "random"), _is("init", "seeded_replicator")], "hold": lambda fv: True},
    {"name": "substrate_z80_vs_vmcopy", "axis": "representation.substrate", "arms": [_is("representation.substrate", "z80"), _is("representation.substrate", "vmcopy")], "hold": lambda fv: True},
    {"name": "length_32_vs_64", "axis": "representation.genome", "arms": [_is("representation.genome", 32), _is("representation.genome", 64)], "hold": lambda fv: True},
    {"name": "reproduction_physics_via_matched_control", "axis": "reproduction", "arms": [_is("reproduction", "EXTERNAL"), _not(_is("reproduction", "EXTERNAL"))],
     "hold": lambda fv: True, "control": "matched_control:reproduction"},
]


def structural_zeros(G) -> Dict[str, list]:
    axes = list(G.AXES); zeros = {}; r = SplitMix64(seed_from("preflight.completions", 0))
    for A, B in itertools.combinations(axes, 2):
        for a in G.AXES[A]:
            for b in G.AXES[B]:
                ok = False
                for t in range(COMPLETIONS + 1):
                    fv = dict(G.NEUTRAL) if t == 0 else {ax: G.AXES[ax][r.randbelow(len(G.AXES[ax]))] for ax in axes}
                    fv[A] = a; fv[B] = b
                    if G.spec_from_factors(fv) is not None:
                        ok = True; break
                if not ok:
                    zeros.setdefault("%s|%s" % (A, B), []).append([a, b])
    return zeros


def simulate(G, draws: int = DRAWS, seed: int = 0, step: Callable = None) -> List[dict]:
    rng = SplitMix64(seed_from("preflight.simulate", seed)); cov: Dict[str, int] = {}; pairs: Dict[str, int] = {}; out = []
    step = step or G.explore_step
    for _ in range(draws):
        s = step(rng, "early", cov, pairs)
        if s is not None: out.append(G.factor_vector(s))
    return out


def reference(G, draws: int = DRAWS, seed: int = 1) -> List[dict]:
    """The DESIGN the sparse-coverage sampler is meant to approximate: level balance. Independent axes uniform over their levels;
    a dependent axis (CONTEXT) uniform over the levels the constraints admit given its parent; 1-2 distinct pressures. (Uniform over
    valid FULL specs is the wrong reference: niches admits 60 world combinations and every other topology 3, so it puts ~84% of
    the mass on niches.) A reference draw that still violates a constraint means CONTEXT misses a coupling: counted and reported."""
    r = SplitMix64(seed_from("preflight.reference", seed)); out = []; rejected = 0
    parents = sorted({p for p in G.CONTEXT.values()}); order = parents + [a for a in G.AXES if a not in parents]
    while len(out) < draws:
        fv = {}
        for ax in order:
            if ax == "pressure": continue
            lv = G.AXES[ax] if ax not in G.CONTEXT else [l for l in G.AXES[ax] if G.eligible(ax, l, {G.CONTEXT[ax]: fv[G.CONTEXT[ax]]})]
            fv[ax] = lv[r.randbelow(len(lv))]
        lv = [l for l in G.AXES["pressure"] if G.eligible("pressure", l, {"reproduction": fv["reproduction"]})]; ps = []; n = 1 + r.randbelow(2)
        while len(ps) < min(n, len(lv)):
            p = lv[r.randbelow(len(lv))]
            if p not in ps: ps.append(p)
        fv["pressure"] = "+".join(sorted(ps))
        if G.spec_from_factors(fv) is not None: out.append(fv)
        else: rejected += 1
    reference.rejected = rejected
    return out


def _cells(fvs, A, B):
    cnt = Counter()
    for fv in fvs:
        for a in (fv[A].split("+") if A == "pressure" else [str(fv[A])]):
            for b in (fv[B].split("+") if B == "pressure" else [str(fv[B])]):
                cnt[(a, b)] += 1
    return cnt


def sampler_support(G, fvs: List[dict], ref: List[dict]) -> dict:
    """A level pair is SAMPLER_STARVED when the sampler draws it at < STARVE_FRAC of its rate under the level-balance design."""
    starved = {}
    for A, B in itertools.combinations(list(G.AXES), 2):
        cs, cr = _cells(fvs, A, B), _cells(ref, A, B)
        for c, nr in cr.items():
            exp = nr * len(fvs) / len(ref)
            if exp >= 10 and cs[c] < STARVE_FRAC * exp:
                starved.setdefault("%s|%s" % (A, B), []).append({"cell": list(c), "count": cs[c], "expected_under_design": round(exp, 1)})
    return starved


def contrast_support(G, fvs: List[dict], contrasts: list, ref: List[dict] = None) -> dict:
    out = {}
    for c in contrasts:
        held = [fv for fv in fvs if c["hold"](fv)]
        n = [sum(1 for fv in held if arm(fv)) for arm in c["arms"]]
        res = {"arm_support": n, "supported": min(n) >= MIN_SUPPORT}
        if ref:
            e = [sum(1 for fv in ref if c["hold"](fv) and arm(fv)) * len(fvs) / len(ref) for arm in c["arms"]]
            res["arm_expected_under_design"] = [round(x, 1) for x in e]
            res["arm_starved"] = [x > 0 and k < STARVE_FRAC * x for k, x in zip(n, e)]
            res["supported"] = res["supported"] and not any(res["arm_starved"])
        if c.get("control"):
            extra = Counter(); clean = 0; treated = 0
            for fv in held:
                if not c["arms"][0](fv): continue
                s = G.spec_from_factors(fv)
                if s is None: continue
                cs = [x for x in G.matched_controls(s, "early") if x["scheduler_reason"] == c["control"]]
                if not cs: extra["NO_CONTROL_CONSTRUCTIBLE"] += 1; continue
                cf = G.factor_vector(cs[0]); treated += 1
                diff = sorted(k for k in fv if k != c["axis"] and str(fv[k]) != str(cf[k]))
                for k in diff: extra[k] += 1
                clean += not diff
            res.update({"treatments_checked": treated, "control_changes_other_factors": dict(extra), "clean_subset_support": clean})
            res["status"] = "OK" if not extra else ("RESTRICTED" if clean >= MIN_SUPPORT else "CONFOUNDED_CONTROL")
            if not res["supported"]: res["status"] = "UNSUPPORTED"
        else:
            res["status"] = "OK" if res["supported"] else "UNSUPPORTED"
        out[c["name"]] = res
    return out


def run(G, contrasts=None, draws: int = DRAWS, step: Callable = None) -> dict:
    contrasts = contrasts if contrasts is not None else Z80ATLAS_CONTRASTS
    zeros = structural_zeros(G)
    linked = {frozenset((a, p)) for a, p in G.CONTEXT.items()}
    undeclared = sorted(k for k in zeros if frozenset(k.split("|")) not in linked)
    fvs = simulate(G, draws, step=step); ref = reference(G, draws)
    starved = sampler_support(G, fvs, ref)
    cs = contrast_support(G, fvs, contrasts, ref)
    fail = bool(undeclared) or bool(getattr(reference, "rejected", 0)) or any(v["status"] in ("UNSUPPORTED", "CONFOUNDED_CONTROL") for v in cs.values())
    return {"schema": "archaeon.preflight.v1", "draws_simulated": len(fvs), "min_support": MIN_SUPPORT, "starve_frac": STARVE_FRAC, "reference_rejections": getattr(reference, "rejected", None),
            "structural_zeros": zeros, "undeclared_coupling": undeclared, "sampler_starved": starved,
            "contrasts": cs, "restricted_contrasts": [k for k, v in cs.items() if v["status"] == "RESTRICTED"],
            "verdict": "FAIL" if fail else ("PASS_WITH_RESTRICTIONS" if any(v["status"] == "RESTRICTED" for v in cs.values()) else "PASS")}


def campaign_sampler_step(commit: str = "c7610ea19") -> Callable:
    """The exploration step exactly as the 72-hour campaign ran it (grammar.random_spec at `commit`, plain coverage, plain pair cost
    over all axes), for demonstrating what the preflight would have said before that launch."""
    import importlib.util, subprocess, sys, tempfile
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    src = subprocess.run(["git", "show", "%s:archaeon/z80atlas/grammar.py" % commit], cwd=root, capture_output=True, check=True).stdout
    f = Path(tempfile.mkdtemp()) / "grammar_campaign.py"; f.write_bytes(src)
    sp = importlib.util.spec_from_file_location("z80atlas_grammar_campaign", f); old = importlib.util.module_from_spec(sp); sys.modules[sp.name] = old; sp.loader.exec_module(old)

    def step(rng, stage, cov, pairs):
        cands = [c for c in (old.random_spec(rng, stage, cov, "exploration") for _ in range(4)) if c]
        if not cands: return None
        def keys(fv):
            ks = sorted(fv); return ["%s=%s|%s=%s" % (ks[i], fv[ks[i]], ks[j], fv[ks[j]]) for i in range(len(ks)) for j in range(i + 1, len(ks))]
        best = min(cands, key=lambda c: sum(pairs.get(k, 0) for k in keys(old.factor_vector(c))))
        fv = old.factor_vector(best)
        for k, v in fv.items(): cov["%s=%s" % (k, v)] = cov.get("%s=%s" % (k, v), 0) + 1
        for k in keys(fv): pairs[k] = pairs.get(k, 0) + 1
        return best
    return step


def summary(p: dict) -> dict:
    return {"verdict": p["verdict"], "undeclared_coupling": p["undeclared_coupling"], "starved_cells": sum(len(v) for v in p["sampler_starved"].values()),
            "contrasts": {k: {"status": v["status"], "support": v["arm_support"], "expected": v.get("arm_expected_under_design")} for k, v in p["contrasts"].items()}}


if __name__ == "__main__":
    import sys
    from archaeon.z80atlas import grammar as GR
    step = campaign_sampler_step() if "--campaign-sampler" in sys.argv else None
    p = run(GR, step=step)
    print(json.dumps(p if "--full" in sys.argv else summary(p), indent=1, default=str))
