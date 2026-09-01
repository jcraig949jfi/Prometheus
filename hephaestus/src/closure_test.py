"""Semantic-injection closure gauntlet (Addendum 3, 2026-09-01).

The standard Forge test. Freeze and bypass the first arrow of
    text -> semantic state -> computation -> answer
and ask whether the second arrow is already inside the frozen primitives' reach.

Arms (increasingly permissive), each answering a DIFFERENT question -- never collapsed:
  A0  frozen primitives, no routing            G(C)
  A1  frozen primitives + operational routing  G(C | R): one expression per route key
      (the dispatch Apollo's guarded ops actually provide; R is an explicit resource)
  A2  A1 + bounded generic composition         G(C | R, gen): is_none / len / not / pair / first
  B   small generic boolean/comparison/count language (the "any small program" control)
  C   candidate primitive, only if A0-A2 and B disagree in the diagnostic way

Two kinds of membership are reported for every hit (operator ruling on Q1):
  coerced      the expression's Python truthiness matches the target on the SEARCH points
  mechanism    the expression's STATIC return type is the target type (no truthiness coercion)
               AND it matches on the VERIFY points -- a larger / exhaustive domain disjoint
               from the search points (counterfactual verification, Q8 requirement)
Only mechanism-bearing membership carries a classification.

Classification (three destinations; only the third goes to a Master Smith):
  SEARCH_ROUTING   target is mechanism-bearing in G(C|R) (A0/A1/A2) but the system does not
                   find / route to it
  REPRESENTATION   target is computable once semantic state exists; the system cannot build
                   that state (the parser / world side) -- asserted by the spec, measured elsewhere
  OPERATOR         target remains outside mechanism-bearing G(C|R,gen) while B reaches it
  INCONCLUSIVE     neither A nor B within depth/budget

Usage:  PYTHONPATH=. python -m hephaestus.src.closure_test <spec_name> [budget]
Specs live in hephaestus/src/closure_specs/<spec_name>.py and define:
  ROUTE_KEYS, SEARCH_POINTS, VERIFY_POINTS, TERMINALS (name -> (type, fn(point))),
  target(route_key, point) -> value, TARGET_TYPE, FROZEN_OPS (name -> (arg types, ret type, fn)),
  GENERIC_OPS (A2), B_OPS, notes
"""
from __future__ import annotations

import importlib
import itertools
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


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


def enumerate_arm(spec, ops: dict, max_depth: int, budget: int, generic: dict | None = None):
    """Typed bottom-up enumeration. Records EVERY expression that matches a target on the search
    points (coerced), then verifies each on VERIFY_POINTS and checks static return type."""
    t0 = time.time()
    allops = dict(ops); allops.update(generic or {})
    S, V = spec.SEARCH_POINTS, spec.VERIFY_POINTS
    targets = {k: tuple(spec.target(k, p) for p in S) for k in spec.ROUTE_KEYS}
    vtargets = {k: tuple(spec.target(k, p) for p in V) for k in spec.ROUTE_KEYS}
    seen: set = set()
    layers: list[list[tuple[str, str, object]]] = []   # (expr, type, fn)
    evaluated = 0
    hits: dict[str, list[dict]] = {k: [] for k in spec.ROUTE_KEYS}

    def consider(expr, typ, fn, depth):
        nonlocal evaluated
        vec = _vec(fn, S); evaluated += 1
        key = (typ, tuple(_hashable(x) for x in vec))
        if key in seen:
            return None
        seen.add(key)
        coerced = tuple(bool(x) if x != ("__ERR__",) else None for x in vec)
        for k in spec.ROUTE_KEYS:
            tgt = targets[k]
            if coerced == tuple(bool(t) for t in tgt):
                h = {"expr": expr, "depth": depth, "static_type": typ, "coerced_match_search": True}
                h["typed"] = (typ == spec.TARGET_TYPE)
                vv = _vec(fn, V)
                h["verify_match"] = (tuple(bool(x) if x != ("__ERR__",) else None for x in vv) == tuple(bool(t) for t in vtargets[k]))
                h["mechanism_bearing"] = bool(h["typed"] and h["verify_match"])
                hits[k].append(h)
        return (expr, typ, fn)

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
    summary = {}
    for k in spec.ROUTE_KEYS:
        mech = sorted([h for h in hits[k] if h["mechanism_bearing"]], key=lambda h: (h["depth"], len(h["expr"])))
        co = sorted([h for h in hits[k] if not h["mechanism_bearing"]], key=lambda h: (h["depth"], len(h["expr"])))
        summary[k] = {"mechanism_bearing": mech[:3], "coerced_only_aliases": co[:3],
                      "n_mechanism": len(mech), "n_alias": len(co)}
    return {"evaluated": evaluated, "distinct": len(seen), "depth": len(layers) - 1, "seconds": round(time.time() - t0, 2),
            "budget": budget, "per_route": summary,
            "all_routes_mechanism_bearing": all(summary[k]["n_mechanism"] > 0 for k in spec.ROUTE_KEYS),
            "all_routes_coerced": all((summary[k]["n_mechanism"] + summary[k]["n_alias"]) > 0 for k in spec.ROUTE_KEYS)}


def run(spec_name: str, budget: int = 300_000, max_depth: int = 3) -> dict:
    spec = importlib.import_module(f"hephaestus.src.closure_specs.{spec_name}")
    res = {"spec": spec_name, "notes": getattr(spec, "NOTES", ""), "route_keys": spec.ROUTE_KEYS,
           "n_search_points": len(spec.SEARCH_POINTS), "n_verify_points": len(spec.VERIFY_POINTS),
           "target_type": spec.TARGET_TYPE, "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    # A0: no routing -> a single expression must match the target for ALL route keys at once.
    if len(spec.ROUTE_KEYS) > 1:
        # Emulate by concatenating route columns: only possible if one expression fits all; report by arity.
        cols = [tuple(bool(spec.target(k, p)) for p in spec.SEARCH_POINTS) for k in spec.ROUTE_KEYS]
        res["A0_frozen_no_routing"] = {"possible": len(set(cols)) == 1,
                                       "note": "route columns identical -> routing unnecessary" if len(set(cols)) == 1 else
                                       "route columns differ -> no routing-free expression can fit; routing R is a required resource"}
    else:
        res["A0_frozen_no_routing"] = enumerate_arm(spec, spec.FROZEN_OPS, max_depth, budget)
    res["A1_frozen_with_routing"] = enumerate_arm(spec, spec.FROZEN_OPS, max_depth, budget)
    res["A2_frozen_routing_generic"] = enumerate_arm(spec, spec.FROZEN_OPS, max_depth, budget, generic=spec.GENERIC_OPS)
    res["B_generic_language"] = enumerate_arm(spec, spec.B_OPS, max_depth, budget)
    a_mech = res["A1_frozen_with_routing"]["all_routes_mechanism_bearing"] or res["A2_frozen_routing_generic"]["all_routes_mechanism_bearing"]
    a_co = res["A1_frozen_with_routing"]["all_routes_coerced"] or res["A2_frozen_routing_generic"]["all_routes_coerced"]
    b_mech = res["B_generic_language"]["all_routes_mechanism_bearing"]
    if a_mech:
        cls = "SEARCH_ROUTING"
        why = "target is mechanism-bearing inside G(C|R" + (",gen" if not res["A1_frozen_with_routing"]["all_routes_mechanism_bearing"] else "") + "): the frozen set computes it; the system does not route to it"
    elif b_mech and not a_co:
        cls = "OPERATOR"; why = "outside G(C|R,gen) even coerced, while a small generic language reaches it: a missing operator family"
    elif b_mech and a_co:
        cls = "SEARCH_ROUTING (alias only)"; why = "only coerced aliases inside G(C|R); treat as operator-adjacent; a typed primitive is warranted but the function is reachable"
    else:
        cls = "INCONCLUSIVE"; why = "neither arm reached the target at this depth/budget"
    res["classification"] = {"class": cls, "why": why,
                             "representation_debt": getattr(spec, "REPRESENTATION_DEBT", "not assessed by this test")}
    out = ROOT / "hephaestus" / "closure_results" / f"{spec_name}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2, default=str), encoding="utf-8")
    return res


if __name__ == "__main__":
    r = run(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 300_000)
    slim = {k: v for k, v in r.items()}
    for arm in ("A1_frozen_with_routing", "A2_frozen_routing_generic", "B_generic_language"):
        slim[arm] = {"evaluated": r[arm]["evaluated"], "depth": r[arm]["depth"], "all_mech": r[arm]["all_routes_mechanism_bearing"],
                     "per_route": {k: {"mech": [h["expr"] + f" (d{h['depth']})" for h in v["mechanism_bearing"]],
                                       "alias": [h["expr"] + f" (d{h['depth']})" for h in v["coerced_only_aliases"]]}
                                   for k, v in r[arm]["per_route"].items()}}
    print(json.dumps(slim, indent=1, default=str))
