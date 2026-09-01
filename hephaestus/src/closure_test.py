"""Semantic-injection closure gauntlet (Addendum 3; tooling per Addendum 4, 2026-09-01).

The standard Forge test. Freeze and bypass the first arrow of
    text -> semantic state -> computation -> answer
and ask whether the second arrow is already inside the frozen primitives' reach.

Arms (increasingly permissive), each answering a DIFFERENT question -- never collapsed:
  A0  frozen primitives, no routing                     G(C)
  A1  frozen primitives + operational routing           G(C | R)   one expression per route key
  A2  A1 + the FROZEN global basis A2-GENERIC-v1        G(C | R, A2)
  B   small generic boolean/comparison/count language   the "any small program" control
CLOSURE_MARGIN = the first arm at which every route has a mechanism-bearing witness:
  A0 / A1 / A2_ONLY / NONE.  (Addendum 4, Q3: the margin is information about the substrate.)

Membership, per expression (Addendum 4, Q1 -- extensional, not nominal):
  coerced            Python truthiness matches the target on the SEARCH points
  typed              static return type == TARGET_TYPE (no coercion)
  verify_exhaustive  matches on VERIFY_POINTS (exhaustive at small size, disjoint from search)
  verify_shift       matches on VERIFY_SHIFT_POINTS (structurally shifted regime), if the spec has one
  mechanism_bearing  typed AND verify_exhaustive
  robust             mechanism_bearing AND verify_shift
Only mechanism-bearing witnesses carry a classification; robust ones are reported as such.

Equivalence classes (Addendum 4): value-vector -> up to MAX_EQUIV structurally distinct expressions
(distinct operator tree shape), so that "closure existence" and "closure explanation" are both
recorded. Only the first expression of a class enters the search pool (search cost unchanged).

Usage:  PYTHONPATH=. python -m hephaestus.src.closure_test <spec_name> [budget]
"""
from __future__ import annotations

import importlib
import itertools
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hephaestus.src.closure_specs.generic_basis import A2_GENERIC, BASIS_VERSION, basis_hash  # noqa: E402

MAX_EQUIV = 5


def _vec(fn, points):
    out = []
    for pt in points:
        try:
            out.append(fn(pt))
        except Exception:  # noqa: BLE001
            out.append(("__ERR__",))
    return tuple(out)


def _hashable(v):
    try:
        hash(v); return v
    except TypeError:
        return repr(v)


def _shape(expr: str) -> str:
    """Operator tree shape: terminals replaced by '_'. Two expressions with the same shape are
    the same mechanism up to argument choice; different shapes are structurally distinct."""
    return re.sub(r"\b(?!(?:[a-z_]+\())([A-Za-z_][A-Za-z0-9_]*|\d+)\b(?!\()", "_", expr)


def _bools(vec):
    return tuple(None if x == ("__ERR__",) else bool(x) for x in vec)


def enumerate_arm(spec, ops: dict, max_depth: int, budget: int, generic: dict | None = None):
    t0 = time.time()
    allops = dict(ops); allops.update(generic or {})
    S = spec.SEARCH_POINTS; V = spec.VERIFY_POINTS; W = getattr(spec, "VERIFY_SHIFT_POINTS", None)
    targets = {k: tuple(bool(spec.target(k, p)) for p in S) for k in spec.ROUTE_KEYS}
    vtargets = {k: tuple(bool(spec.target(k, p)) for p in V) for k in spec.ROUTE_KEYS}
    wtargets = {k: tuple(bool(spec.target(k, p)) for p in W) for k in spec.ROUTE_KEYS} if W else None
    classes: dict[tuple, dict] = {}          # (type, value-vector) -> {"exprs": [(expr, fn)], "shapes": set()}
    layers: list[list[tuple[str, str, object]]] = []
    evaluated = 0

    def consider(expr, typ, fn, depth):
        nonlocal evaluated
        vec = _vec(fn, S); evaluated += 1
        key = (typ, tuple(_hashable(x) for x in vec))
        cls = classes.get(key)
        if cls is None:
            classes[key] = {"exprs": [(expr, fn, depth)], "shapes": {_shape(expr)}, "bools": _bools(vec)}
            return (expr, typ, fn)
        sh = _shape(expr)
        if len(cls["exprs"]) < MAX_EQUIV and sh not in cls["shapes"]:
            cls["exprs"].append((expr, fn, depth)); cls["shapes"].add(sh)
        return None

    cur = []
    for name, (typ, fn) in spec.TERMINALS.items():
        r = consider(name, typ, fn, 0)
        if r: cur.append(r)
    layers.append(cur)
    for depth in range(1, max_depth + 1):
        nxt = []
        pool = [e for L in layers for e in L]
        for opname, (argtypes, rettype, op) in allops.items():
            cands = [[e for e in pool if e[1] == at] for at in argtypes]
            if any(not c for c in cands):
                continue
            for args in itertools.product(*cands):
                if evaluated >= budget:
                    break
                if not any(a in layers[-1] for a in args):
                    continue
                fs = [a[2] for a in args]
                def f(pt, op=op, fs=fs):
                    return op(*[g(pt) for g in fs])
                r = consider(f"{opname}({', '.join(a[0] for a in args)})", rettype, f, depth)
                if r: nxt.append(r)
            if evaluated >= budget:
                break
        layers.append(nxt)
        if evaluated >= budget:
            break

    # Hits: every class whose coerced vector matches a route target; each equivalent verified separately.
    per_route = {}
    for k in spec.ROUTE_KEYS:
        hits = []
        for (typ, _), cls in classes.items():
            if cls["bools"] != targets[k]:
                continue
            for expr, fn, depth in cls["exprs"]:
                h = {"expr": expr, "depth": depth, "static_type": typ, "typed": typ == spec.TARGET_TYPE}
                h["verify_exhaustive"] = (_bools(_vec(fn, V)) == vtargets[k])
                h["verify_shift"] = (_bools(_vec(fn, W)) == wtargets[k]) if W else None
                h["mechanism_bearing"] = bool(h["typed"] and h["verify_exhaustive"])
                h["robust"] = bool(h["mechanism_bearing"] and (h["verify_shift"] if W else True))
                hits.append(h)
        mech = sorted([h for h in hits if h["mechanism_bearing"]], key=lambda h: (h["depth"], len(h["expr"])))
        alias = sorted([h for h in hits if not h["mechanism_bearing"]], key=lambda h: (h["depth"], len(h["expr"])))
        per_route[k] = {"mechanism_bearing": mech[:MAX_EQUIV], "coerced_only_aliases": alias[:MAX_EQUIV],
                        "n_mechanism": len(mech), "n_robust": sum(h["robust"] for h in mech), "n_alias": len(alias)}
    return {"evaluated": evaluated, "distinct_classes": len(classes), "depth": len(layers) - 1,
            "seconds": round(time.time() - t0, 2), "budget": budget, "per_route": per_route,
            "all_routes_mechanism_bearing": all(v["n_mechanism"] > 0 for v in per_route.values()),
            "all_routes_robust": all(v["n_robust"] > 0 for v in per_route.values()),
            "all_routes_coerced": all((v["n_mechanism"] + v["n_alias"]) > 0 for v in per_route.values())}


def run(spec_name: str, budget: int = 300_000, max_depth: int = 3) -> dict:
    spec = importlib.import_module(f"hephaestus.src.closure_specs.{spec_name}")
    if hasattr(spec, "GENERIC_OPS"):
        raise SystemExit(f"spec {spec_name} defines GENERIC_OPS; per-spec generic ops are forbidden (Addendum 4). Use the frozen basis.")
    res = {"spec": spec_name, "notes": getattr(spec, "NOTES", ""), "route_keys": spec.ROUTE_KEYS,
           "n_search_points": len(spec.SEARCH_POINTS), "n_verify_points": len(spec.VERIFY_POINTS),
           "n_verify_shift_points": len(getattr(spec, "VERIFY_SHIFT_POINTS", []) or []),
           "verify_shift_description": getattr(spec, "VERIFY_SHIFT_DESCRIPTION", None),
           "target_type": spec.TARGET_TYPE, "basis": {"version": BASIS_VERSION, "hash": basis_hash()},
           "max_depth": max_depth, "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    multi = len(spec.ROUTE_KEYS) > 1
    if multi:
        cols = [tuple(bool(spec.target(k, p)) for p in spec.SEARCH_POINTS) for k in spec.ROUTE_KEYS]
        res["A0_frozen_no_routing"] = {"possible": len(set(cols)) == 1,
                                       "note": "route columns identical -> routing unnecessary" if len(set(cols)) == 1 else
                                       "route columns differ -> no routing-free expression can fit; routing R is a required resource"}
    else:
        res["A0_frozen_no_routing"] = enumerate_arm(spec, spec.FROZEN_OPS, max_depth, budget)
    res["A1_frozen_with_routing"] = enumerate_arm(spec, spec.FROZEN_OPS, max_depth, budget)
    res["A2_frozen_routing_generic"] = enumerate_arm(spec, spec.FROZEN_OPS, max_depth, budget, generic=A2_GENERIC)
    res["B_generic_language"] = enumerate_arm(spec, spec.B_OPS, max_depth, budget)
    a0m = (not multi) and res["A0_frozen_no_routing"]["all_routes_mechanism_bearing"]
    a1m = res["A1_frozen_with_routing"]["all_routes_mechanism_bearing"]
    a2m = res["A2_frozen_routing_generic"]["all_routes_mechanism_bearing"]
    a_co = res["A1_frozen_with_routing"]["all_routes_coerced"] or res["A2_frozen_routing_generic"]["all_routes_coerced"]
    bm = res["B_generic_language"]["all_routes_mechanism_bearing"]
    margin = "A0" if a0m else "A1" if a1m else "A2_ONLY" if a2m else "NONE"
    if a1m or a2m:
        cls = "SEARCH_ROUTING"; why = f"target is mechanism-bearing inside G(C|R{',A2' if margin == 'A2_ONLY' else ''}); the frozen set computes it and the system does not route to it"
    elif bm and not a_co:
        cls = "OPERATOR"; why = "outside G(C|R,A2) even coerced while a small generic language reaches it: a missing operator family"
    elif bm and a_co:
        cls = "SEARCH_ROUTING (alias only)"; why = "only coerced aliases inside G(C|R,A2); reachable but no typed mechanism; a typed primitive is warranted"
    else:
        cls = "INCONCLUSIVE"; why = "neither arm reached the target at this depth/budget"
    res["classification"] = {"class": cls, "CLOSURE_MARGIN": margin, "why": why,
                             "robust_at_margin": (res["A0_frozen_no_routing"] if margin == "A0" else
                                                  res["A1_frozen_with_routing"] if margin == "A1" else
                                                  res["A2_frozen_routing_generic"]).get("all_routes_robust") if margin != "NONE" else None,
                             "representation_debt": getattr(spec, "REPRESENTATION_DEBT", "not assessed by this test")}
    out = ROOT / "hephaestus" / "closure_results" / f"{spec_name}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2, default=str), encoding="utf-8")
    return res


def _slim(r):
    s = {k: r[k] for k in ("spec", "n_search_points", "n_verify_points", "n_verify_shift_points", "basis", "classification")}
    s["A0"] = r["A0_frozen_no_routing"] if "possible" in r["A0_frozen_no_routing"] else {"evaluated": r["A0_frozen_no_routing"]["evaluated"], "all_mech": r["A0_frozen_no_routing"]["all_routes_mechanism_bearing"]}
    for arm in ("A1_frozen_with_routing", "A2_frozen_routing_generic", "B_generic_language"):
        a = r[arm]
        s[arm] = {"evaluated": a["evaluated"], "depth": a["depth"], "all_mech": a["all_routes_mechanism_bearing"], "all_robust": a["all_routes_robust"],
                  "per_route": {k: {"mech": [f"{h['expr']} (d{h['depth']}{'' if h['robust'] else ', not robust'})" for h in v["mechanism_bearing"]],
                                    "alias": [f"{h['expr']} (d{h['depth']})" for h in v["coerced_only_aliases"]]}
                                for k, v in a["per_route"].items()}}
    return s


if __name__ == "__main__":
    r = run(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 300_000)
    print(json.dumps(_slim(r), indent=1, default=str))
