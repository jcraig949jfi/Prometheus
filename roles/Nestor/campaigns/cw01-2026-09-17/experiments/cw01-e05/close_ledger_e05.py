"""Flip the six e05 QUALIFY defects from OPEN to FIXED, with evidence.

Bookkeeping only. Each fix is already in the code and is demonstrated by a named
fixture or consistency-gate check; this records that rather than asserting it.
D042 was already FIXED and is left alone.
"""
from __future__ import annotations

import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE.parents[1]                      # campaign root, matching the other scripts
LEDGER = BASE / "DEFECTS.jsonl"
assert LEDGER.exists(), "ledger not found at %s" % LEDGER

EVIDENCE = {
 "CW01-D037": "world_e05.make_items draws items PER EPISODE from the attempt-stable pool; "
              "variance restored and measurable - fixtures F2/F6 build a non-degenerate null "
              "band [-6.64, +7.11] on BEST, which was impossible under the zero-variance world.",
 "CW01-D038a": "world_e05.solo_values accepts and applies **kw, so an intervention reaches every "
               "baseline; lib/learnability.require_controlled added as a standing guard. Fixture F4 "
               "MEASURES propagation (solo baselines move between composition laws) rather than "
               "trusting the guard, which is tautological at the nsa call site.",
 "CW01-D038b": "superadditivity and ablation defined on INFORMATION (world_e05.mean_info), carry "
               "cost reported separately. Consistency gate A8 now checks the basis across "
               "VERDICT_CONTRACT, QUALIFY and all five WORLD.measurements keys: PASS.",
 "CW01-D039": "carry BUDGET B=3 replaces the unbindable carry price, present in WORLD arms, "
              "QUALIFY and the frozen contract (gate A4), derived by one canonical rule across all "
              "three artifacts (gate A7), and enforced at load time (gate A13: load_cfg refuses a "
              "WORLD whose max_components disagrees with budget_B).",
 "CW01-D040": "raw cross-law superadditivity is no longer a verdict quantity; the statistic is a "
              "difference-in-differences on NORMALISED superadditivity (gate A9, all four artifacts "
              "agree). Fixture F3 exhibits the trap directly: BEST under disjunction reads -22.63% "
              "from coverage overlap, and is never read as a verdict.",
 "CW01-D041": "the invented gap_conj > abs(gap_disj) magnitude threshold is gone; eligibility is "
              "infometrics.effect_clears_null against a measured null of >=8 blocks (gate A10). "
              "Fixture F6 shows an effect inside its own band refused and one outside admitted.",
}


def main():
    lines = [l for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]
    out, flipped = [], []
    for l in lines:
        d = json.loads(l)
        if d.get("id") in EVIDENCE and d.get("status") == "OPEN":
            d["status"] = "FIXED"
            d["fix_evidence"] = EVIDENCE[d["id"]]
            d["fixed_phase"] = "QUALIFY (pre-EXECUTE), freeze boundary"
            flipped.append(d["id"])
        out.append(json.dumps(d, ensure_ascii=True))     # CW01-D050: ASCII-safe records
    LEDGER.write_text("\n".join(out) + "\n", encoding="utf-8")

    after = [json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]
    still_open = [d["id"] for d in after if d.get("id") in EVIDENCE and d.get("status") == "OPEN"]
    print("ledger entries: %d" % len(after))
    print("flipped OPEN->FIXED: %s" % flipped)
    print("e05 defects still OPEN: %s" % (still_open or "none"))
    print("total OPEN across campaign: %d" % sum(1 for d in after if d.get("status") == "OPEN"))
    return 0 if not still_open else 1


if __name__ == "__main__":
    raise SystemExit(main())
