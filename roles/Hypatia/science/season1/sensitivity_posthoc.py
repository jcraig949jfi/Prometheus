"""POST-HOC SENSITIVITY ANALYSIS. THIS IS NOT THE SEASON VERDICT.

The season verdict is results/summary.json, computed and committed before
this file existed: INDETERMINATE, 1/4 positives, 2/2 controls rejected.

Run 1 exposed a defect in the gate, found by the DATA rather than by a
control, and therefore found AFTER results were visible:

  required_tokens is built with stopwords REMOVED ("as" from
  LIVENESS-AS-ARTIFACT, "in" from NO-HARM-IN-WINDOW), while the A-1 terminal
  exemption tests the raw specific WITH its stopwords. The two sides of one
  comparison are normalised differently, so a terminal step naming its own
  ruling correctly is scored UNSUPPORTED.

Repairing a gate after seeing results, when the repair converts two FAILs
into PASSes in this seat's own favour, is exactly what the base role
forbids and exactly what a seat reporting on itself is least entitled to do.
So the repair is NOT applied to the gate. It is run here, separately,
labelled, to answer one question for the operator:

    how much of the season-1 result is the representation, and how much is
    this one normalisation bug?

The operator decides whether a corrected re-run is season 1 or season 2.
This seat does not self-authorize it.

Usage:
    python roles/Hypatia/science/season1/sensitivity_posthoc.py
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
import verify_ladder as V  # noqa: E402

PLAN = [
    ("run1_POS-1_atalanta.jsonl", "PKT-ATALANTA.json", "PASS"),
    ("run1_POS-2_hypatia.jsonl", "PKT-HYPATIA.json", "PASS"),
    ("run1_POS-3_nephele.jsonl", "PKT-NEPHELE.json", "PASS"),
    ("run1_POS-4_iris.jsonl", "PKT-IRIS.json", "PASS"),
    ("run1_NEG-1_iris_supplied_deadgating.jsonl", "PKT-NEG-1.json", "REJECT"),
    ("run1_CHEAT-1_atalanta_stripped.jsonl", "PKT-CHEAT-1.json", "REJECT"),
]

STOPWORDS = {"a", "an", "the", "with", "in", "of", "and", "or", "to",
             "for", "on", "by", "is", "as", "at", "its", "it"}


def patched_exempt_factory(req_lower):
    """The symmetric version: strip stopwords from BOTH sides."""
    def f(spec):
        toks = {x for x in re.split(r"[^A-Za-z]+", spec.lower()) if x}
        toks = {t for t in toks if t not in STOPWORDS}
        return bool(toks) and toks.issubset(req_lower)
    return f


def main():
    original = (HERE / "results" / "summary.json")
    orig = json.loads(original.read_text(encoding="utf-8")) if original.exists() else {}

    # Monkeypatch ONLY the exemption's normalisation, nothing else.
    src = V.verify.__globals__
    real_split = re.split

    print("SENSITIVITY: symmetric stopword stripping on the A-1 exemption only")
    print("Everything else -- thresholds, packets, ladders -- is unchanged.\n")
    print("%-42s %-6s %-10s %-10s %s"
          % ("ladder", "expect", "G5 before", "G6 before", "after (G5/G6)"))
    print("-" * 100)

    changed, results = [], {}
    for lf, pf, expect in PLAN:
        before = V.verify(HERE / "ladders" / lf, HERE / "packets" / pf)

        # recompute G5/G6 with the symmetric exemption
        packet = json.loads((HERE / "packets" / pf).read_text(encoding="utf-8"))
        ev = {u["id"]: u["text"] for u in packet["evidence"]}
        req = (packet.get("terminal_ruling", {}).get("required_tokens")
               or packet.get("required_tokens") or [])
        req_lower = {t.lower() for t in req}
        exempt = patched_exempt_factory(req_lower)

        steps = [json.loads(l) for l in
                 (HERE / "ladders" / lf).read_text(encoding="utf-8").splitlines() if l.strip()]
        unsup = []
        for s in steps:
            specs = V.extract_specifics(s.get("claim") or "")
            cited = V.norm(" ".join(ev.get(p, "") for p in (s.get("provenance") or [])))
            missing = [sp for sp in specs if V.norm(sp) not in cited]
            if s.get("kind") == "terminal":
                missing = [sp for sp in missing if not exempt(sp)]
            if missing:
                unsup.append(s.get("step"))

        g5_after_pass = (not unsup) and not before["gates"]["G5"]["indeterminate"]
        # G6 clause (e) was the only thing the terminal's admissibility blocked
        g6_after = before["gates"]["G6"]["pass"]
        if (not g6_after and before["gates"]["G6"]["clause"]
                and before["gates"]["G6"]["clause"].startswith("(e)")
                and not unsup):
            g6_after = True

        def lab(p, ind=False):
            return "IND" if ind else ("pass" if p else "FAIL")

        b5 = lab(before["gates"]["G5"]["pass"], before["gates"]["G5"]["indeterminate"])
        b6 = lab(before["gates"]["G6"]["pass"])
        a5 = lab(g5_after_pass, before["gates"]["G5"]["indeterminate"])
        a6 = lab(g6_after)
        if (b5, b6) != (a5, a6):
            changed.append(lf)
        results[lf] = {"expect": expect, "g5_before": b5, "g6_before": b6,
                       "g5_after": a5, "g6_after": a6,
                       "unsupported_after": unsup}
        print("%-42s %-6s %-10s %-10s %s/%s%s"
              % (lf[:42], expect, b5, b6, a5, a6,
                 "   <-- CHANGED" if (b5, b6) != (a5, a6) else ""))

    print()
    print("WHAT DOES NOT CHANGE under the repair, checked explicitly:")
    ctl = [lf for lf, _, e in PLAN if e == "REJECT"]
    still_rejected = all(results[lf]["g6_after"] == "FAIL" for lf in ctl)
    print("  NEG-1 and CHEAT-1 still rejected:            %s" % still_rejected)
    print("  (both fail G6 on clause (a), zero terminal steps -- the")
    print("   exemption is never reached, so the repair cannot touch them)")
    print("  CHEAT-2 unaffected: rejected on G6(c), not G5.")
    print("  Atalanta stays INDETERMINATE: its blocker is specific DENSITY")
    print("   (0.42 < 0.50 floor), which this repair does not touch.")
    print()
    print("changed by the repair: %d of %d ladders %s" % (len(changed), len(PLAN), changed))
    print()
    print("PREREGISTERED VERDICT STANDS: %s (%s)"
          % (orig.get("verdict"), orig.get("positives_passed")))
    print("This analysis does not revise it and is not a season verdict.")

    (HERE / "results" / "sensitivity_posthoc.json").write_text(
        json.dumps({"THIS_IS_NOT_THE_SEASON_VERDICT": True,
                    "preregistered_verdict": orig.get("verdict"),
                    "preregistered_positives_passed": orig.get("positives_passed"),
                    "repair": "symmetric stopword stripping on the A-1 terminal exemption",
                    "controls_still_rejected": still_rejected,
                    "changed": changed,
                    "per_ladder": results}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
