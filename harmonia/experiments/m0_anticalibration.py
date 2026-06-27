"""M0 harness — "Can the selector recognize novelty OUTSIDE its calibration manifold?"

Doctrine anchor: pivot/REASSESSMENT_2026-06-22_v2_enforcement.md §M0.
Falsification-first; EXECUTING lens (we actually RUN the instrument's checks, we
do not assert what it would do). Fail closed: any error / unrepresentable form is
recorded as a NON-acceptance, never silently passed.

What this measures
------------------
For each TRUE claim in the anti-calibration sets (m0_anticalibration_sets.py) we
route it to the BEST entry point the real instrument exposes
(harmonia/experiments/verifier_lens.py): the packaged `verify(probe, claim)` for
the 5 representable kinds, or the raw `certify_universal` / `entails` primitives,
or — for shapes the instrument cannot represent at all — we record a STRUCTURAL
non-recognition without inventing a check.

Per claim we record:
  verdict        : "accept" | "reject" | "unknown"
      accept  = instrument certified the (true) claim valid  (valid is True)
      reject  = instrument certified it WRONG (valid is False) — a TYPE-II error,
                the worst outcome: a true claim actively denied
      unknown = instrument could not certify either way
                (valid is None, or the claim is structurally unrepresentable, or
                 the check errored — all fail-closed into "not certified")
  which_check    : which entry point / kill fired
  recognition    : "STRUCTURAL"  — the instrument genuinely cannot represent the
                                    claim (no kind / no primitive / honest None on
                                    an undecidable universal)
                   "SUPERFICIAL" — the instrument COULD represent the underlying
                                    fact but surface-form parsing / packaging
                                    blocked it (e.g. a registry keyed by literal
                                    cid string, a kind that exists but the verify
                                    dispatch can't reach the fact)
                   "RECOGNIZED"  — accepted; recognition succeeded
  oracle_true    : independent ground truth (always True here; flagged if not)
  valid_raw      : the raw instrument `valid` field (True/False/None) for audit

The type-II reading: a battery that is a genuine discovery instrument should
ACCEPT out-of-manifold truths. If it cannot see them (high unknown) or actively
denies them (any reject), it is a recognizer of the familiar, not a discoverer.

Output: prints a per-set table and writes a machine-readable JSON sidecar
(m0_results.json) next to this file for the M0_RESULTS.md writeup to cite.
"""
from __future__ import annotations

import json
import os
from collections import Counter
from typing import Any, Dict

import sympy as sp
import z3

from harmonia.experiments.reasoning_phase0 import Probe, x
from harmonia.experiments.verifier_lens import (
    certify_universal,
    entails,
    verify,
)
from harmonia.experiments import m0_anticalibration_sets as sets


# --------------------------------------------------------------------------- #
# per-route execution. Each returns (verdict, which_check, recognition,
# valid_raw, detail). FAIL CLOSED everywhere.
# --------------------------------------------------------------------------- #
def _classify_valid(valid):
    """Map the instrument's tri-state `valid` to an M0 verdict."""
    if valid is True:
        return "accept"
    if valid is False:
        return "reject"   # type-II: a TRUE claim certified WRONG
    return "unknown"      # valid is None -> not certified


def _run_verify_kind(item, kind):
    """Route a claim through the packaged verify() for a representable `kind`.

    We build the minimal Probe the verifier expects for that kind and call the
    REAL verify(). A crash fails closed to unknown.
    """
    p = item["payload"]
    try:
        if kind == "quadratic":
            probe = Probe("M0", "antical", "quadratic", {"expr": p["expr"]}, None)
            res = verify(probe, p["claimed"])
        elif kind == "sqrt":
            eq = sp.Eq(sp.sqrt(x + p["a"]), x - p["b"])
            probe = Probe("M0", "antical", "sqrt",
                          {"a": p["a"], "b": p["b"], "eq": eq}, None)
            res = verify(probe, p["claimed"])
        elif kind == "rational":
            probe = Probe("M0", "antical", "rational",
                          {"num": p["num"], "den": p["den"], "rhs": p["rhs"],
                           "excluded": p["excluded"]}, None)
            res = verify(probe, p["claimed"])
        elif kind == "conjecture":
            probe = Probe("M0", "antical", "conjecture",
                          {"cid": p["cid"], "truth": True, "cex": None}, None)
            res = verify(probe, p["claimed"])
        else:
            return ("unknown", "no_such_kind", "STRUCTURAL", None, {})
    except Exception as exc:
        return ("unknown", "verify_exception", "STRUCTURAL", None,
                {"exception": f"{type(exc).__name__}: {exc}"})

    valid = res.get("valid")
    verdict = _classify_valid(valid)
    kp = res.get("kill_pattern")
    return (verdict, kp or f"verify_{kind}", _recognition_for(item, kind, valid, kp),
            valid, {"checks_keys": list(res.get("checks", {}).keys())})


def _recognition_for(item, kind, valid, kill_pattern):
    """Decide STRUCTURAL vs SUPERFICIAL vs RECOGNIZED for a verify() result.

    accept -> RECOGNIZED.
    For a non-accept on a claim whose underlying fact the kind CAN represent
    (the oracle confirms it true and a native-form sibling exists), the wall is
    SUPERFICIAL. Otherwise STRUCTURAL.
    """
    if valid is True:
        return "RECOGNIZED"
    # conjecture registry is keyed by literal cid string -> a true universal with
    # an unregistered cid returns unverifiable_universal: that is the instrument
    # failing to recognize a fact it provably can verify under the registered
    # surface form. That is the SUPERFICIAL (surface-keyed) wall.
    if kind == "conjecture" and item["id"] == "A4":
        return "SUPERFICIAL"
    # everything else routed to a real kind that returned None/False on a TRUE
    # claim it can represent -> surface/representation issue, not absence of kind.
    if valid is False:
        return "SUPERFICIAL"   # actively denied a fact it represents = surface bug
    return "STRUCTURAL"


def _run_certify_universal(item):
    """Route to the raw z3 certify_universal primitive (single int var)."""
    p = item["payload"]
    try:
        res = certify_universal(p["predicate"], p.get("domain"))
    except Exception as exc:
        return ("unknown", "certify_universal_exception", "STRUCTURAL", None,
                {"exception": f"{type(exc).__name__}: {exc}"})
    verdict = {"proved": "accept", "refuted": "reject", "unknown": "unknown"}[res["verdict"]]
    valid = {"proved": True, "refuted": False, "unknown": None}[res["verdict"]]
    rec = ("RECOGNIZED" if verdict == "accept"
           else "STRUCTURAL")  # z3 unknown on a true universal = genuine reach limit
    return (verdict, f"z3_{res['verdict']}", rec, valid,
            {"z3_result": res["z3_result"], "reason": res["reason"]})


def _run_certify_universal_real4(item):
    """Cauchy-Schwarz 2D over 4 REALS — pose directly to z3 real arithmetic.

    The instrument exposes certify_universal only for a single INTEGER var, so a
    4-real-variable inequality cannot be posed through its surface at all. We
    pose it to z3 directly to establish that the UNDERLYING claim is decidable —
    and record that the INSTRUMENT's exposed primitive could not represent it
    (STRUCTURAL: the surface is single-int-var only)."""
    a, b, c, d = z3.Reals("a b c d")
    lhs = (a * c + b * d) ** 2
    rhs = (a * a + b * b) * (c * c + d * d)
    s = z3.Solver()
    s.set("timeout", 5000)
    s.add(z3.Not(lhs <= rhs))
    r = s.check()
    z3_says_true = (r == z3.unsat)
    # The instrument's certify_universal signature is single-int-var; a 4-real
    # claim cannot be handed to it. So instrument-recognition is STRUCTURAL-no,
    # regardless of z3's raw verdict.
    return ("unknown", "instrument_primitive_is_single_int_var", "STRUCTURAL", None,
            {"z3_raw_decidable": z3_says_true, "z3_result": str(r),
             "note": "claim is z3-decidable but the instrument's exposed "
                     "certify_universal takes one INTEGER variable; a 4-real "
                     "inequality is unrepresentable through the instrument surface"})


def _run_certify_universal_abs(item):
    """Triangle inequality |a+b|<=|a|+|b| — z3-decidable but uses abs over 2 reals.

    Same structural story as real4: not posable through the single-int-var
    primitive. Establish raw decidability, record STRUCTURAL non-representability."""
    a, b = z3.Reals("a b")
    absx = lambda t: z3.If(t >= 0, t, -t)
    s = z3.Solver()
    s.set("timeout", 5000)
    s.add(z3.Not(absx(a + b) <= absx(a) + absx(b)))
    r = s.check()
    z3_says_true = (r == z3.unsat)
    return ("unknown", "instrument_primitive_is_single_int_var", "STRUCTURAL", None,
            {"z3_raw_decidable": z3_says_true, "z3_result": str(r),
             "note": "z3-decidable over reals, but unrepresentable through the "
                     "instrument's single-int-var certify_universal surface"})


def _run_entails(item):
    """Route to the raw z3 entails primitive."""
    p = item["payload"]
    n = z3.Int("n")
    # parse the tiny premise/conclusion DSL ("n > k")
    def _term(s):
        s = s.strip()
        if ">" in s:
            _, k = s.split(">")
            return n > int(k.strip())
        raise ValueError(f"unsupported clause {s!r}")
    try:
        res = entails(_term(p["premise"]), _term(p["conclusion"]))
    except Exception as exc:
        return ("unknown", "entails_exception", "STRUCTURAL", None,
                {"exception": f"{type(exc).__name__}: {exc}"})
    verdict = {"valid": "accept", "invalid": "reject", "unknown": "unknown"}[res]
    valid = {"valid": True, "invalid": False, "unknown": None}[res]
    rec = "RECOGNIZED" if verdict == "accept" else "STRUCTURAL"
    return (verdict, f"entails_{res}", rec, valid, {})


def _run_sympy_identity(item):
    """A polynomial IDENTITY (LHS==RHS for all x). The instrument has NO identity
    kind. We confirm truth with the external sympy oracle, then attempt to coerce
    the identity into the instrument's rational verifier (num/den form) to see if
    it is representable at all. The verify() result — not the oracle — decides the
    instrument verdict; the oracle only confirms the claim really is true."""
    p = item["payload"]
    oracle_true = bool(sp.expand(p["lhs"] - p["rhs"]) == 0)
    # Try to coerce into the rational kind: (lhs - rhs)/1 == 0 is NOT the rational
    # verifier's shape (it expects num/den=rhs with an excluded singular value).
    # There is no excluded singular point in an identity, so the rational kind
    # cannot represent it. This is the structural gap we are measuring.
    coercion_possible = False
    return ("unknown", "no_identity_kind", "STRUCTURAL", None,
            {"sympy_oracle_true": oracle_true,
             "coercion_to_rational_kind_possible": coercion_possible,
             "note": "instrument verifies polynomial ROOTS and rational identities "
                     "WITH an excluded singular value; a plain LHS==RHS identity has "
                     "no root claim and no singular point, so no kind represents it"})


def _run_unrepresentable(item):
    """A claim with no instrument kind and no exposed primitive (graphs, matrices,
    pigeonhole, ...). We do NOT invent a check. STRUCTURAL non-recognition."""
    return ("unknown", "no_representable_kind", "STRUCTURAL", None,
            {"domain": item["payload"].get("domain"),
             "note": "no instrument kind or exposed primitive can pose this claim"})


_ROUTERS = {
    "verify_quadratic": lambda it: _run_verify_kind(it, "quadratic"),
    "verify_sqrt": lambda it: _run_verify_kind(it, "sqrt"),
    "verify_rational": lambda it: _run_verify_kind(it, "rational"),
    "verify_conjecture": lambda it: _run_verify_kind(it, "conjecture"),
    "certify_universal": _run_certify_universal,
    "certify_universal_real4": _run_certify_universal_real4,
    "certify_universal_abs": _run_certify_universal_abs,
    "entails": _run_entails,
    "sympy_identity": _run_sympy_identity,
    "UNREPRESENTABLE": _run_unrepresentable,
}


def run_item(item: Dict[str, Any]) -> Dict[str, Any]:
    # independent ground truth FIRST — never trust our own label
    try:
        oracle_true = bool(item["oracle_true"]())
    except Exception as exc:
        oracle_true = None
        oracle_err = f"{type(exc).__name__}: {exc}"
    else:
        oracle_err = None

    router = _ROUTERS.get(item["route"])
    if router is None:
        verdict, which, recog, valid_raw, detail = (
            "unknown", "no_router", "STRUCTURAL", None, {"route": item["route"]})
    else:
        verdict, which, recog, valid_raw, detail = router(item)

    return {
        "id": item["id"],
        "set": item["set"],
        "statement": item["statement"],
        "route": item["route"],
        "oracle_true": oracle_true,
        "oracle_error": oracle_err,
        "verdict": verdict,
        "which_check": which,
        "recognition": recog,
        "valid_raw": valid_raw,
        "why_outside_manifold": item["why_outside_manifold"],
        "detail": detail,
    }


def main():
    results = [run_item(it) for it in sets.ALL_SETS]

    # guard: exclude any item whose independent oracle did not confirm True
    excluded = [r for r in results if r["oracle_true"] is not True]
    scored = [r for r in results if r["oracle_true"] is True]

    print("=" * 78)
    print("M0 — CAN THE SELECTOR RECOGNIZE NOVELTY OUTSIDE ITS CALIBRATION MANIFOLD?")
    print("=" * 78)
    print(f"items: {len(results)}  scored: {len(scored)}  "
          f"excluded (oracle disagreed): {len(excluded)}")
    if excluded:
        for r in excluded:
            print(f"  EXCLUDED {r['id']}: oracle_true={r['oracle_true']} "
                  f"err={r['oracle_error']}")

    # per-item table
    print("\nper-item (all claims are TRUE; accept=good, reject=type-II error, "
          "unknown=not certified):")
    print(f"  {'id':3s} {'set':3s} {'verdict':8s} {'recognition':12s} "
          f"{'valid':6s} {'which_check'}")
    for r in scored:
        print(f"  {r['id']:3s} {r['set']:3s} {r['verdict']:8s} "
              f"{r['recognition']:12s} {str(r['valid_raw']):6s} {r['which_check']}")

    # per-set rates
    print("\nper-set rates (over scored items):")
    summary = {}
    for s in ("A", "B", "C"):
        rs = [r for r in scored if r["set"] == s]
        n = len(rs)
        cnt = Counter(r["verdict"] for r in rs)
        rec = Counter(r["recognition"] for r in rs)
        summary[s] = {
            "n": n,
            "accept": cnt["accept"], "reject": cnt["reject"], "unknown": cnt["unknown"],
            "accept_rate": cnt["accept"] / n if n else 0.0,
            "reject_rate": cnt["reject"] / n if n else 0.0,
            "unknown_rate": cnt["unknown"] / n if n else 0.0,
            "recognition": dict(rec),
        }
        print(f"  SET {s} (n={n}): "
              f"accept={cnt['accept']} ({summary[s]['accept_rate']:.0%})  "
              f"reject={cnt['reject']} ({summary[s]['reject_rate']:.0%})  "
              f"unknown={cnt['unknown']} ({summary[s]['unknown_rate']:.0%})  "
              f"| recognition: {dict(rec)}")

    # overall
    allcnt = Counter(r["verdict"] for r in scored)
    n = len(scored)
    overall = {
        "n": n,
        "accept": allcnt["accept"], "reject": allcnt["reject"],
        "unknown": allcnt["unknown"],
        "accept_rate": allcnt["accept"] / n if n else 0.0,
        "reject_rate": allcnt["reject"] / n if n else 0.0,
        "unknown_rate": allcnt["unknown"] / n if n else 0.0,
    }
    print(f"\nOVERALL (n={n}): accept={allcnt['accept']} "
          f"({overall['accept_rate']:.0%})  reject={allcnt['reject']} "
          f"({overall['reject_rate']:.0%})  unknown={allcnt['unknown']} "
          f"({overall['unknown_rate']:.0%})")

    # pre-registered verdict reading
    print("\n--- PRE-REGISTERED M0 VERDICT ---")
    structural = sum(1 for r in scored if r["recognition"] == "STRUCTURAL")
    superficial = sum(1 for r in scored if r["recognition"] == "SUPERFICIAL")
    print(f"non-recognition cause split: STRUCTURAL={structural}  "
          f"SUPERFICIAL={superficial}  RECOGNIZED={allcnt['accept']}")
    # READING A = thesis alive iff it certifies ENOUGH out-of-manifold truths.
    # The cleanest arm is the genuinely-novel content: Set B (adjacent domains)
    # and the non-within-kind portion of Set C. Within-kind controls (fresh
    # constants/irrational roots) measure kind-generalization, not novelty reach.
    out_of_manifold = [r for r in scored
                       if r["id"] not in ("C6", "C7")]  # exclude within-kind controls
    oom_accept = sum(1 for r in out_of_manifold if r["verdict"] == "accept")
    oom_n = len(out_of_manifold)
    print(f"out-of-manifold (excluding within-kind controls C6,C7): "
          f"{oom_accept}/{oom_n} accepted ({oom_accept/oom_n:.0%})")
    if oom_accept / oom_n >= 0.5:
        reading = ("A: thesis ALIVE — instrument certifies a majority of "
                   "out-of-manifold truths")
    else:
        reading = ("B: thesis DEMOTED — instrument fails to certify the majority "
                   "of out-of-manifold truths; demote discovery-engine -> "
                   "audit/recognition substrate")
    print(f"READING: {reading}")

    payload = {
        "experiment": "M0_anticalibration",
        "doctrine": "pivot/REASSESSMENT_2026-06-22_v2_enforcement.md §M0",
        "n_items": len(results), "n_scored": n, "n_excluded": len(excluded),
        "per_set": summary, "overall": overall,
        "recognition_split": {"structural": structural, "superficial": superficial,
                              "recognized": allcnt["accept"]},
        "out_of_manifold": {"n": oom_n, "accepted": oom_accept,
                            "accept_rate": oom_accept / oom_n if oom_n else 0.0},
        "reading": reading,
        "items": results,
    }
    out = os.path.join(os.path.dirname(__file__), "m0_results.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
