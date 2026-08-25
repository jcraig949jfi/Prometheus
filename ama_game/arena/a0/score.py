#!/usr/bin/env python3
"""Score an assessor run and report the shape of failure, not just a mean.

Primary metric, fixed in PREREG_A0.md section 3 before any data existed:

    correct_i = submitted disposition equals the oracle disposition
    cost_i    = verifier calls if correct, else the full budget cap
    EVC       = mean cost_i over the set, n = number of claims

Everything else here exists because a single mean cannot tell you whether a
baseline is competent-but-expensive (the useful case) or accidentally perfect
(no headroom for D) or near-random (where D can "improve" by giving hints).

  python score.py --set A0_EVAL
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARENA = HERE.parent
sys.path.insert(0, str(ARENA / "generator"))

import oracle as ORACLE  # noqa: E402

DISPOSITIONS = ["TRUE", "FALSE", "TRUE_BUT_INVALID_ARGUMENT", "UNRESOLVED"]


def load(set_name: str):
    idx = json.loads((HERE / set_name / "INDEX.json").read_text(encoding="utf-8"))
    budget = json.loads(
        (ARENA / "prompts" / "budget.json").read_text(encoding="utf-8"))
    cap = budget["BUDGET_VERIFIER_CALLS"]
    rows = []
    for run in idx["runs"]:
        cid = run["claim_id"]
        sealed = json.loads(
            (ARENA / "heldout" / set_name / "sealed" / f"{cid}.json")
            .read_text(encoding="utf-8"))
        sub_path = Path(run["submission"])
        sub = (json.loads(sub_path.read_text(encoding="utf-8"))
               if sub_path.exists() else None)
        rows.append({"claim_id": cid, "sealed": sealed, "sub": sub})
    return idx, cap, rows


def score_rows(rows, cap):
    out = []
    for r in rows:
        s, sub = r["sealed"], r["sub"]
        disp = (sub or {}).get("disposition")
        rr = (sub or {}).get("resource_report") or {}
        calls = int(rr.get("verifier_calls") or 0) + int(rr.get("solver_calls") or 0)
        correct = disp == s["oracle_disposition"]
        missing = sub is None or disp not in DISPOSITIONS

        kill_check = None
        if disp == "FALSE":
            w = (sub or {}).get("witness")
            if isinstance(w, dict):
                w = w.get("n", w.get("graph_bits"))
            kill_check = ORACLE.verify_witness(s, w) if w is not None else {
                "in_domain": None, "is_counterexample": False,
                "reason": "no witness supplied with a FALSE disposition"}

        out.append({
            "claim_id": r["claim_id"],
            "sealed_class": s["sealed_class"],
            "template": s["template_id"],
            "oracle": s["oracle_disposition"],
            "truth": s["truth_status"],
            "submitted": disp if not missing else "MISSING",
            "correct": bool(correct and not missing),
            "verifier_calls": calls,
            "cost": calls if (correct and not missing) else cap,
            "hit_cap": not (correct and not missing),
            "confidence": (sub or {}).get("confidence"),
            "evidence_kind": (sub or {}).get("evidence_kind"),
            "wall_time_s": rr.get("wall_time_s"),
            "output_tokens": rr.get("output_tokens"),
            "kill_valid": (None if kill_check is None
                           else bool(kill_check["is_counterexample"])),
            "kill_reason": (None if kill_check is None else kill_check["reason"]),
            "broken_step": (sub or {}).get("broken_step"),
            "min_cost_units": s["minimum_known_disposition_method"]["cost_units"],
        })
    return out


def se(xs):
    return statistics.stdev(xs) / math.sqrt(len(xs)) if len(xs) > 1 else 0.0


def report(set_name: str, idx, cap, scored) -> str:
    L = []
    n = len(scored)
    costs = [r["cost"] for r in scored]
    acc = sum(r["correct"] for r in scored) / n
    evc = statistics.mean(costs)

    L.append(f"A0 RESULT — {set_name}, condition {idx['condition']}, n = {n}")
    L.append("=" * 68)
    L.append("")
    L.append("PRIMARY (preregistered, cost rule fixed before data existed)")
    L.append(f"  EVC  expected verifier cost to correct disposition : "
             f"{evc:.2f}  (SE {se(costs):.2f})")
    L.append(f"  accuracy                                           : "
             f"{acc:.0%}  ({sum(r['correct'] for r in scored)}/{n})")
    L.append(f"  budget cap (cost charged on an incorrect answer)   : {cap}")
    L.append(f"  unit of analysis: the claim.  n = {n}")
    L.append("")

    capped = [r for r in scored if r["hit_cap"]]
    real = [r for r in scored if not r["hit_cap"]]
    L.append("COST STRUCTURE")
    L.append(f"  claims charged at the cap (i.e. wrong)  : {len(capped)}/{n} "
             f"= {len(capped)/n:.0%} of the mass")
    if real:
        rc = [r["verifier_calls"] for r in real]
        L.append(f"  verifier calls on correct claims        : "
                 f"median {statistics.median(rc):.0f}, mean {statistics.mean(rc):.1f}, "
                 f"range [{min(rc)}, {max(rc)}]")
    L.append(f"  the distribution is censored at {cap}; do not assume normality "
             f"when testing it")
    L.append("")

    L.append("CONFUSION — sealed class (rows) by submitted disposition")
    classes = sorted({r["sealed_class"] for r in scored})
    for c in classes:
        items = [r for r in scored if r["sealed_class"] == c]
        got = Counter(r["submitted"] for r in items)
        want = items[0]["oracle"]
        hit = got.get(want, 0)
        L.append(f"  {c:<30s} n={len(items):2d}  correct={hit}/{len(items)}  "
                 f"-> {dict(got)}")
    L.append("")

    L.append("FAILURE SHAPE")
    true_items = [r for r in scored if r["truth"] == "TRUE"]
    false_acc = [r for r in true_items if r["submitted"] == "FALSE"]
    L.append(f"  false accusations (FALSE on a claim that is true) : "
             f"{len(false_acc)}/{len(true_items)} = "
             f"{len(false_acc)/max(1,len(true_items)):.0%}")

    tbia = [r for r in scored if r["sealed_class"] == "TRUE_BUT_INVALID_ARGUMENT"]
    tbia_kill = [r for r in tbia if r["submitted"] == "FALSE"]
    tbia_true = [r for r in tbia if r["submitted"] == "TRUE"]
    L.append(f"  TRUE_BUT_INVALID_ARGUMENT correct                 : "
             f"{sum(r['correct'] for r in tbia)}/{len(tbia)}")
    L.append(f"    ... called FALSE (spotted the bad proof, then killed the true")
    L.append(f"        conclusion with it)                         : {len(tbia_kill)}")
    L.append(f"    ... called TRUE (missed the planted defect)     : {len(tbia_true)}")

    unres = [r for r in scored if r["sealed_class"] == "UNRESOLVED_WITHIN_BUDGET"]
    over = [r for r in unres if r["submitted"] in ("TRUE", "FALSE")]
    matched = [r for r in over
               if (r["submitted"] == "TRUE") == (r["truth"] == "TRUE")]
    L.append(f"  UNRESOLVED correct                                : "
             f"{sum(r['correct'] for r in unres)}/{len(unres)}")
    L.append(f"    ... overclaimed a truth value                   : {len(over)}")
    L.append(f"        of those, matched the sealed truth          : "
             f"{len(matched)}/{len(over) if over else 0}")
    if len(over) >= 4 and len(matched) == len(over):
        L.append("        WARNING: every overclaim was right. These items may be")
        L.append("        resolvable within budget after all, and the class is")
        L.append("        mislabelled rather than the assessor being lucky.")

    kills = [r for r in scored if r["submitted"] == "FALSE"]
    bogus = [r for r in kills if r["kill_valid"] is False]
    L.append(f"  invalid falsifiers (FALSE whose witness fails      ")
    L.append(f"    re-execution against the claim)                 : "
             f"{len(bogus)}/{len(kills)} submitted kills")
    for b in bogus[:5]:
        L.append(f"      {b['claim_id']}: {b['kill_reason']}")

    missing = [r for r in scored if r["submitted"] == "MISSING"]
    if missing:
        L.append(f"  submissions missing or malformed                  : "
                 f"{len(missing)} — {[m['claim_id'] for m in missing]}")
    L.append("")

    L.append("HEADROOM")
    if acc >= 0.95:
        L.append("  Baseline is near-perfect. This is a PROBLEM for the experiment:")
        L.append("  there is almost no room for condition D to improve, so the")
        L.append("  navigation comparison cannot show anything. Harden the set.")
    elif acc <= 0.35:
        L.append("  Baseline is near-random. Also a problem: D could later 'win'")
        L.append("  simply by supplying obvious hints, which is not navigation.")
    else:
        L.append(f"  Baseline is competent but fallible ({acc:.0%} accuracy at "
                 f"EVC {evc:.1f}).")
        L.append("  This is the useful regime: room for D to improve, and not so")
        L.append("  much room that any hint would do it.")
    L.append("")

    L.append("PER-CLAIM ROWS (raw)")
    L.append(f"  {'claim':<18s} {'class':<30s} {'oracle':<26s} "
             f"{'submitted':<26s} {'ok':<3s} {'calls':>5s} {'cost':>5s}")
    for r in scored:
        L.append(f"  {r['claim_id']:<18s} {r['sealed_class']:<30s} "
                 f"{r['oracle']:<26s} {r['submitted']:<26s} "
                 f"{'Y' if r['correct'] else 'n':<3s} "
                 f"{r['verifier_calls']:>5d} {r['cost']:>5d}")
    return "\n".join(L)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--set", required=True)
    p.add_argument("--out")
    args = p.parse_args()

    idx, cap, rows = load(args.set)
    scored = score_rows(rows, cap)
    text = report(args.set, idx, cap, scored)
    print(text)

    dest = Path(args.out) if args.out else HERE / args.set / "RESULT.json"
    dest.write_text(json.dumps({
        "set_name": args.set,
        "condition": idx["condition"],
        "n": len(scored),
        "budget_cap": cap,
        "invariant_sha256": idx["invariant_sha256"],
        "context_sha256": idx["context_sha256"],
        "evc": statistics.mean([r["cost"] for r in scored]),
        "evc_se": se([r["cost"] for r in scored]),
        "accuracy": sum(r["correct"] for r in scored) / len(scored),
        "rows": scored,
    }, indent=2) + "\n", encoding="utf-8")
    (dest.parent / "RESULT.txt").write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
