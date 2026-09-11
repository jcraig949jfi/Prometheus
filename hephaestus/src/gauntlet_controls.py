"""Instrument controls for the closure gauntlet on the BOOLEAN specs (HEPH-09 / HEPH-10; base role s2:
every instrument possesses a negative, a positive and a cheat control).

Expectations are fixed HERE, before the run, and the script grades itself. Nothing below touches a
spec's frozen result file; outputs go to hephaestus/closure_results/controls_<spec>.json.

  NEGATIVE  ("I do not hallucinate signal"): the route target is a seeded random boolean column over
            every search, verify and shift point. No typed program over the frozen ops, the generic
            basis or the generic language should reproduce it on the exhaustive domain.
            EXPECT: n_mechanism == 0 in arms A1, A2 and B. Coerced aliases on the search points are
            allowed (they are the alias column doing its job) and are reported.
  POSITIVE  ("I detect real signal"): the route target is a named expression the arm CAN build.
            EXPECT: n_mechanism >= 1, the named expression (or an equivalent shape) among the
            witnesses, and the minimal witness depth equal to the expression's depth.
  CHEAT     ("the channel can observe the thing I claim to measure"): the spec's REAL target kernel is
            injected under a decoy name as a typed op.
            CHEAT-A1: injected into the frozen op set. EXPECT: a depth-1 witness `decoy_kernel(...)`
                      is mechanism-bearing on the real route(s).
            CHEAT-A2: injected into the generic basis only (frozen set unchanged). EXPECT: the A1 arm
                      shows what it showed before and the A2 arm shows the decoy witness; i.e. the
                      gauntlet's margin moves to A2_ONLY / an A2 leak is visible.

Depth 3, budget 300,000 per arm, exactly the frozen protocol. Deterministic (seed 20260911).
"""
from __future__ import annotations

import importlib
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from hephaestus.src.closure_test import enumerate_arm  # noqa: E402
from hephaestus.src.closure_specs.generic_basis import A2_GENERIC, BASIS_VERSION, basis_hash  # noqa: E402

DEPTH, BUDGET, SEED = 3, 300_000, 20260911


class Shim:
    """A spec view with one route and a substituted target; everything else from the module."""

    def __init__(self, mod, route_fn, route="ctrl"):
        self.ROUTE_KEYS = [route]
        self.TARGET_TYPE = mod.TARGET_TYPE
        self.TERMINALS = mod.TERMINALS
        self.SEARCH_POINTS = mod.SEARCH_POINTS
        self.VERIFY_POINTS = mod.VERIFY_POINTS
        self.VERIFY_SHIFT_POINTS = getattr(mod, "VERIFY_SHIFT_POINTS", None)
        self._fn = route_fn

    def target(self, _k, pt):
        return self._fn(pt)


class RealRoutes:
    """The real spec with ops possibly augmented; routes as declared."""

    def __init__(self, mod):
        for a in ("ROUTE_KEYS", "TARGET_TYPE", "TERMINALS", "SEARCH_POINTS", "VERIFY_POINTS"):
            setattr(self, a, getattr(mod, a))
        self.VERIFY_SHIFT_POINTS = getattr(mod, "VERIFY_SHIFT_POINTS", None)
        self._mod = mod

    def target(self, k, pt):
        return self._mod.target(k, pt)


def _summ(r, route):
    pr = r["per_route"][route]
    return {"evaluated": r["evaluated"], "n_mechanism": pr["n_mechanism"], "n_robust": pr["n_robust"], "n_alias": pr["n_alias"],
            "min_witness_depth": min([h["depth"] for h in pr["mechanism_bearing"]], default=None),
            "witnesses": [h["expr"] for h in pr["mechanism_bearing"]], "aliases": [h["expr"] for h in pr["coerced_only_aliases"]]}


def random_target(mod):
    rng = random.Random(SEED)
    pts = list(mod.SEARCH_POINTS) + list(mod.VERIFY_POINTS) + list(getattr(mod, "VERIFY_SHIFT_POINTS", None) or [])
    table = {repr(p): rng.random() < 0.5 for p in pts}
    return lambda pt: table[repr(pt)]


# Positive-control expressions per spec: (arm, ops-builder, expression name, depth, python fn of pt)
def positive_cases(spec_name, mod):
    if spec_name == "vacuous_truth":
        return [("A1", mod.FROZEN_OPS, "pigeonhole_check(d, s)", 1, lambda pt: mod.FROZEN_OPS["pigeonhole_check"][2](pt[0], pt[1])),
                ("B", mod.B_OPS, "eq(d, s)", 1, lambda pt: pt[0] == pt[1])]
    if spec_name == "consistency_check":
        topo = mod.FROZEN_OPS["topological_sort"][2]
        return [("A2", {**mod.FROZEN_OPS, **A2_GENERIC}, "is_none(topological_sort(rels))", 2, lambda pt: topo([tuple(e) for e in pt]) is None),
                ("B", mod.B_OPS, "has_cycle_dfs(rels)", 1, lambda pt: mod.B_OPS["has_cycle_dfs"][2]([tuple(e) for e in pt]))]
    raise SystemExit(f"no positive cases defined for {spec_name}")


def decoy_op(spec_name, mod, route):
    """The real kernel for `route`, typed over the spec's terminals, under a decoy name."""
    if spec_name == "vacuous_truth":
        return {"decoy_kernel": (("int", "int"), "bool", lambda d, s: mod.target(route, (d, s)))}
    if spec_name == "consistency_check":
        return {"decoy_kernel": (("edges",), "bool", lambda e: mod.target(route, e))}
    raise SystemExit(spec_name)


def run(spec_name):
    t0 = time.time()
    mod = importlib.import_module(f"hephaestus.src.closure_specs.{spec_name}")
    out = {"spec": spec_name, "depth": DEPTH, "budget": BUDGET, "seed": SEED, "basis": {"version": BASIS_VERSION, "hash": basis_hash()},
           "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "controls": []}

    # NEGATIVE
    neg = Shim(mod, random_target(mod))
    arms = {"A1": mod.FROZEN_OPS, "A2": {**mod.FROZEN_OPS, **A2_GENERIC}, "B": mod.B_OPS}
    obs = {a: _summ(enumerate_arm(neg, ops, DEPTH, BUDGET), "ctrl") for a, ops in arms.items()}
    out["controls"].append({"control": "NEGATIVE", "expect": "n_mechanism == 0 in A1, A2, B (aliases allowed, reported)",
                            "observed": obs, "PASS": all(o["n_mechanism"] == 0 for o in obs.values())})

    # POSITIVE
    for arm, ops, expr, depth, fn in positive_cases(spec_name, mod):
        pos = Shim(mod, fn)
        o = _summ(enumerate_arm(pos, ops, DEPTH, BUDGET), "ctrl")
        ok = o["n_mechanism"] >= 1 and o["min_witness_depth"] == depth
        out["controls"].append({"control": f"POSITIVE-{arm}", "expect": f"n_mechanism >= 1 and minimal witness depth == {depth} for target {expr}",
                                "observed": o, "named_expression_present": expr in o["witnesses"], "PASS": ok})

    # CHEAT-A1 and CHEAT-A2 on the real routes
    real = RealRoutes(mod)
    base_a1 = enumerate_arm(real, mod.FROZEN_OPS, DEPTH, BUDGET)
    cheat = {}
    for route in mod.ROUTE_KEYS:
        d = decoy_op(spec_name, mod, route)
        a1 = enumerate_arm(real, {**mod.FROZEN_OPS, **d}, DEPTH, BUDGET)
        a2 = enumerate_arm(real, mod.FROZEN_OPS, DEPTH, BUDGET, generic={**A2_GENERIC, **d})
        ba, sa1, sa2 = _summ(base_a1, route), _summ(a1, route), _summ(a2, route)
        decoy_a1 = any(w.startswith("decoy_kernel(") for w in sa1["witnesses"]) and sa1["min_witness_depth"] == 1
        decoy_a2 = any(w.startswith("decoy_kernel(") for w in sa2["witnesses"])
        cheat[route] = {"baseline_A1": ba, "A1_plus_decoy": sa1, "A2only_decoy": sa2,
                        "PASS_A1": decoy_a1, "PASS_A2": decoy_a2,
                        "note": "A2-only injection: the frozen arm is unchanged by construction; the leak is visible when the A2 arm carries the decoy witness"}
    out["controls"].append({"control": "CHEAT", "expect": "decoy witness at depth 1 in A1+decoy on every route; decoy witness present in A2-only injection",
                            "observed": cheat, "PASS": all(v["PASS_A1"] and v["PASS_A2"] for v in cheat.values())})
    out["ALL_PASS"] = all(c["PASS"] for c in out["controls"])
    out["seconds"] = round(time.time() - t0, 1)
    try:
        from hephaestus.workspace_guard import receipt
        out["workspace"] = receipt()
    except Exception as e:  # noqa: BLE001
        out["workspace"] = {"error": repr(e)}
    path = ROOT / "hephaestus" / "closure_results" / f"controls_{spec_name}.json"
    path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    try:
        from hephaestus.state import record
        record(f"gauntlet_controls:{spec_name}", [ROOT / "hephaestus" / "src" / "closure_specs" / f"{spec_name}.py"], len(out["controls"]),
               "ALL_PASS" if out["ALL_PASS"] else "CONTROL FAILED: " + ", ".join(c["control"] for c in out["controls"] if not c["PASS"]))
    except Exception as e:  # noqa: BLE001
        print("state record failed:", repr(e))
    return out


if __name__ == "__main__":
    from hephaestus.workspace_guard import refuse_canonical  # D-23
    refuse_canonical("gauntlet controls")
    for name in (sys.argv[1:] or ["vacuous_truth", "consistency_check"]):
        r = run(name)
        print(f"== {name}: ALL_PASS={r['ALL_PASS']} ({r['seconds']}s)")
        for c in r["controls"]:
            print(f"   {c['control']:<12} PASS={c['PASS']}  expect: {c['expect']}")
            if c["control"] == "NEGATIVE":
                for a, o in c["observed"].items():
                    print(f"      {a}: mech {o['n_mechanism']} alias {o['n_alias']} evaluated {o['evaluated']}")
            elif c["control"].startswith("POSITIVE"):
                o = c["observed"]; print(f"      mech {o['n_mechanism']} min depth {o['min_witness_depth']} named present {c['named_expression_present']} first {o['witnesses'][:2]}")
            else:
                for k, v in c["observed"].items():
                    print(f"      {k}: baseline A1 mech {v['baseline_A1']['n_mechanism']} (min d {v['baseline_A1']['min_witness_depth']}); "
                          f"A1+decoy mech {v['A1_plus_decoy']['n_mechanism']} (min d {v['A1_plus_decoy']['min_witness_depth']}) PASS {v['PASS_A1']}; "
                          f"A2-only decoy present {v['PASS_A2']}")
