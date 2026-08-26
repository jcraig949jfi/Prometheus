#!/usr/bin/env python3
"""Score a metered navigation run under the amended objective.

`PREREG_A0.md` Amendment 1: two co-primary outcomes, reported together —
disposition correctness, and verifier cost conditional on a correct
disposition — with capped EVC demoted to a secondary risk summary.

Cost comes from the harness ledger, not from the seat. The ledger is a hash
chain and its integrity is checked here; a broken chain is reported as a failed
run rather than scored, because a cost number from a tampered ledger is worse
than no number.

The headline this run exists to produce: how far above the achievable floor did
the seats actually land? The floor is known per claim, because
`nav_strategy_sim.py` proved it walkable.

  python score_nav.py --run NAV_PILOT_RUN --set ../heldout/NAV_PILOT
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
sys.path.insert(0, str(ARENA / "verifier"))

from meter_cli import verify_chain  # noqa: E402

SESSIONS = HERE / "_meter_sessions"


def se(xs):
    return statistics.stdev(xs) / math.sqrt(len(xs)) if len(xs) > 1 else 0.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="NAV_PILOT_RUN")
    ap.add_argument("--set", default=str(ARENA / "heldout" / "NAV_PILOT"))
    args = ap.parse_args()

    idx = json.loads((HERE / args.run / "INDEX.json").read_text(encoding="utf-8"))
    sealed_dir = Path(args.set) / "sealed"
    budget = idx["budget"]

    rows = []
    for r in idx["runs"]:
        cid = r["claim_id"]
        s = json.loads((sealed_dir / f"{cid}.json").read_text(encoding="utf-8"))
        sub_p = Path(r["submission"])
        sub = (json.loads(sub_p.read_text(encoding="utf-8"))
               if sub_p.exists() else None)
        sess_p = SESSIONS / f"{r['session']}.json"
        sess = (json.loads(sess_p.read_text(encoding="utf-8"))
                if sess_p.exists() else None)

        chain_ok, chain_why = (verify_chain(sess) if sess else (False, "no session"))

        # Concurrent-session contamination. When the launcher hit its agent
        # limit and relaunched, some claims received two seats sharing one
        # session, so the ledger accumulated both. The meter detected it and two
        # seats reported it unprompted. A repeated (op, point) pair is the
        # signature: a single seat has no reason to buy the same observation
        # twice, and a restart replays its opening samples.
        dup = False
        if sess:
            seen = set()
            for e in sess["ledger"]:
                key = (e["op"], e.get("point"), e.get("lo"), e.get("hi"))
                if key in seen:
                    dup = True
                    break
                seen.add(key)
        spent = sess["spent"] if sess else None
        disp = (sub or {}).get("disposition", "MISSING")
        oracle = s["oracle_disposition"]
        correct = disp == oracle

        witness_ok = None
        if disp == "FALSE":
            w = (sub or {}).get("witness")
            if isinstance(w, dict):
                w = w.get("n")
            witness_ok = (s.get("witness") or {}).get("n") == w

        rows.append({
            "claim_id": cid, "sealed_class": s["sealed_class"],
            "oracle": oracle, "submitted": disp, "correct": correct,
            "spent": spent, "floor": s["achievable_floor"],
            "enumerate_cost": s["route_menu"]["enumerate"],
            "enumerate_within_budget": s["enumerate_within_budget"],
            "chain_ok": chain_ok, "chain_detail": chain_why,
            "witness_correct": witness_ok,
            "refusals": (sess or {}).get("refusals"),
            "contaminated": dup,
            "route_taken": (sub or {}).get("route_taken", ""),
        })

    n = len(rows)
    tampered = [r for r in rows if not r["chain_ok"]]
    scored = [r for r in rows if r["chain_ok"] and r["spent"] is not None]
    clean = [r for r in scored if not r["contaminated"]]
    acc = sum(r["correct"] for r in scored) / max(1, len(scored))
    corr = [r for r in clean if r["correct"]]

    L = []
    L.append(f"A0 v0.2 — METERED NAVIGATION, {idx['set_name']}, "
             f"condition {idx['condition']}, n = {n}")
    L.append("=" * 70)
    L.append(f"budget {budget} credits per claim · cost measured by the harness")
    L.append("")

    if tampered:
        L.append(f"LEDGER INTEGRITY: {len(tampered)} run(s) failed verification "
                 "and are excluded")
        for t in tampered[:5]:
            L.append(f"  {t['claim_id']}: {t['chain_detail']}")
    else:
        L.append(f"LEDGER INTEGRITY: all {len(scored)} hash chains intact")
    L.append("")

    L.append("CO-PRIMARY 1 — disposition correctness")
    L.append(f"  accuracy: {acc:.0%} ({sum(r['correct'] for r in scored)}"
             f"/{len(scored)})")
    for cls in sorted({r["sealed_class"] for r in scored}):
        items = [r for r in scored if r["sealed_class"] == cls]
        got = Counter(r["submitted"] for r in items)
        L.append(f"    {cls:<16s} {sum(i['correct'] for i in items)}/{len(items)}"
                 f"  -> {dict(got)}")
    fa = [r for r in scored if r["oracle"] == "TRUE" and r["submitted"] == "FALSE"]
    tn = [r for r in scored if r["oracle"] == "TRUE"]
    L.append(f"  false accusations (FALSE on a true claim): "
             f"{len(fa)}/{len(tn)}")
    bad_w = [r for r in scored if r["witness_correct"] is False]
    L.append(f"  FALSE dispositions with a wrong witness: {len(bad_w)}")
    L.append("")

    contaminated = [r for r in scored if r["contaminated"]]
    L.append(f"SESSION CONTAMINATION: {len(contaminated)}/{len(scored)} sessions "
             "were charged by two seats")
    L.append("  Cause: the launcher hit its concurrency limit and relaunched "
             "claims whose")
    L.append("  first seat was still running, so two seats shared one session. "
             "Correctness")
    L.append("  is unaffected — each seat reached its own conclusion — but the "
             "COST is not")
    L.append("  attributable, so these are excluded from co-primary 2 and "
             "reported here.")
    if contaminated:
        L.append("  affected: " + ", ".join(r["claim_id"] for r in contaminated))
    L.append("")

    L.append("CO-PRIMARY 2 — verifier cost among correct dispositions "
             f"(uncontaminated only, n={len(clean)})")
    if corr:
        c = [r["spent"] for r in corr]
        fl = [r["floor"] for r in corr]
        over = [r["spent"] / max(1, r["floor"]) for r in corr]
        L.append(f"  n = {len(corr)}   mean {statistics.mean(c):.1f} "
                 f"(SE {se(c):.1f})   median {statistics.median(c):.0f}")
        L.append(f"  achievable floor on those claims: mean "
                 f"{statistics.mean(fl):.1f}")
        L.append(f"  OVERSPEND RATIO (spent / floor): mean {statistics.mean(over):.1f}x"
                 f"   median {statistics.median(over):.1f}x")
        L.append("  This is the headroom figure. A seat that found the structural")
        L.append("  route sits near 1.0x; one that enumerated sits far above it.")
    else:
        L.append("  no correct dispositions to price")
    L.append("")

    L.append("SECONDARY — capped EVC (risk summary, not a success criterion)")
    evc = [r["spent"] if r["correct"] else budget for r in scored]
    L.append(f"  EVC {statistics.mean(evc):.1f} (SE {se(evc):.1f})")
    L.append("")

    L.append("ROUTE BEHAVIOUR")
    near_floor = [r for r in corr if r["spent"] <= r["floor"] * 2]
    L.append(f"  correct at <= 2x the floor (found the cheap route): "
             f"{len(near_floor)}/{len(corr) if corr else 0}")
    hard = [r for r in scored if not r["enumerate_within_budget"]]
    hard_ok = [r for r in hard if r["correct"]]
    L.append(f"  claims enumeration could NOT solve within budget: "
             f"{len(hard_ok)}/{len(hard)} answered correctly")
    L.append("  That second line is the sharpest signal: those claims are")
    L.append("  unreachable without the structural route.")
    L.append("")

    L.append("PER-CLAIM ROWS")
    L.append(f"  {'claim':<10s} {'class':<16s} {'oracle':<10s} {'submitted':<11s} "
             f"{'ok':<3s} {'spent':>6s} {'floor':>6s} {'x':>6s}")
    for r in rows:
        ratio = (f"{r['spent']/max(1,r['floor']):.1f}"
                 if r["spent"] is not None else "-")
        L.append(f"  {r['claim_id']:<10s} {r['sealed_class']:<16s} "
                 f"{r['oracle']:<10s} {r['submitted']:<11s} "
                 f"{'Y' if r['correct'] else 'n':<3s} "
                 f"{str(r['spent']):>6s} {r['floor']:>6d} {ratio:>6s}")

    text = "\n".join(L)
    print(text)
    (HERE / args.run / "RESULT.txt").write_text(text + "\n", encoding="utf-8",
                                                newline="\n")
    (HERE / args.run / "RESULT.json").write_text(
        json.dumps({"set": idx["set_name"], "budget": budget, "n": n,
                    "accuracy": acc, "rows": rows}, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
