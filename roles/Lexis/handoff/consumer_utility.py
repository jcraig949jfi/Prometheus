"""Consumer-utility evaluator: CORRECT / ABSTAIN / WRONG, under explicit loss functions.

Reach and ceiling (what the Lexis instruments measure) count answers, not errors. A
primitive that turns an abstention into a wrong answer raises reach and can lower utility.
This evaluator makes that visible and lets the CONSUMER own the loss function.

OUTCOME per task:
    CORRECT   selected_answer == correct
    ABSTAIN   selected_answer is "" or None   (the organism's abstain sentinel is "")
    WRONG     anything else

LOSS FUNCTIONS are (correct, abstain, wrong) payoffs. Built-ins:
    symmetric_1      ( 1, 0, -1)
    asymmetric_2     ( 1, 0, -2)
    fail_closed_5    ( 1, 0, -5)   a fail-closed scientific regime: an unsupported wrong
                                   answer costs five abstentions
    answer_rate      ( 1, 0,  0)   NOT an acceptance function -- included only so the
                                   consumer can see what "reach" silently assumes
Any (c, a, w) triple may be passed on the command line.

BREAK-EVEN. For payoffs (1, 0, -L), admitting a candidate changes utility by
    dU = dCORRECT - L * dWRONG          (dABSTAIN carries payoff 0)
so the candidate helps iff L < dCORRECT / dWRONG. That ratio is reported exactly.

This module chooses NO loss function. It reports all of them and the break-even.
Read-only on apollo/.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "instruments"))
sys.path.insert(0, str(ROOT / "apollo" / "src"))
sys.path.insert(0, str(ROOT / "apollo" / "scripts"))
sys.path.insert(0, str(ROOT / "agents" / "hephaestus" / "src"))

CORRECT, ABSTAIN, WRONG = "CORRECT", "ABSTAIN", "WRONG"
OUTCOMES = (CORRECT, ABSTAIN, WRONG)

LOSSES = {
    "symmetric_1":   (1, 0, -1),
    "asymmetric_2":  (1, 0, -2),
    "fail_closed_5": (1, 0, -5),
    "answer_rate":   (1, 0, 0),
}


def classify(selected, correct) -> str:
    if selected in ("", None):
        return ABSTAIN
    return CORRECT if selected == correct else WRONG


def run_program(ops, tasks):
    """-> list of {'outcome', 'selected'} in task order. Exceptions count as ABSTAIN
    (the organism produced no answer) and are flagged."""
    from blackboard import BlackboardState, run_pipeline   # noqa: E402
    out = []
    for t in tasks:
        s = BlackboardState(problem_text=t["prompt"], candidates=list(t["candidates"]))
        try:
            sel = run_pipeline(ops, s).selected_answer
            exc = None
        except Exception as e:                                # noqa: BLE001
            sel, exc = "", type(e).__name__
        out.append({"outcome": classify(sel, t["correct"]), "selected": sel,
                    "exception": exc})
    return out


def counts(outcomes) -> dict:
    c = Counter(o["outcome"] if isinstance(o, dict) else o for o in outcomes)
    return {k: c.get(k, 0) for k in OUTCOMES}


def utility(cnt: dict, loss) -> float:
    c, a, w = loss
    return c * cnt[CORRECT] + a * cnt[ABSTAIN] + w * cnt[WRONG]


def transitions(base, cand) -> dict:
    """from->to counts, e.g. 'ABSTAIN->WRONG': 2."""
    t = Counter()
    for b, c in zip(base, cand):
        bo = b["outcome"] if isinstance(b, dict) else b
        co = c["outcome"] if isinstance(c, dict) else c
        t["%s->%s" % (bo, co)] += 1
    return dict(sorted(t.items()))


def compare(base, cand, losses=None) -> dict:
    losses = losses or LOSSES
    cb, cc = counts(base), counts(cand)
    d = {k: cc[k] - cb[k] for k in OUTCOMES}
    per_loss = {}
    for name, l in losses.items():
        ub, uc = utility(cb, l), utility(cc, l)
        per_loss[name] = {"payoffs": list(l), "baseline": ub, "candidate": uc,
                          "delta": uc - ub, "helps": uc > ub}
    dc, dw = d[CORRECT], d[WRONG]
    if dw > 0:
        be = dc / dw
    elif dc > 0:
        be = float("inf")
    else:
        be = 0.0
    return {"n": len(base), "baseline": cb, "candidate": cc, "delta": d,
            "transitions": transitions(base, cand), "per_loss": per_loss,
            "break_even_wrong_penalty": be,
            "break_even_note": ("candidate helps iff wrong-answer penalty L < dCORRECT/dWRONG "
                                "= %s (payoffs (1, 0, -L))" % be)}


def fmt_report(label, cmp) -> str:
    lines = ["%s  (n=%d)" % (label, cmp["n"])]
    lines.append("  %-9s %8s %8s %8s" % ("", CORRECT, ABSTAIN, WRONG))
    lines.append("  %-9s %8d %8d %8d" % ("baseline", *[cmp["baseline"][k] for k in OUTCOMES]))
    lines.append("  %-9s %8d %8d %8d" % ("candidate", *[cmp["candidate"][k] for k in OUTCOMES]))
    lines.append("  %-9s %+8d %+8d %+8d" % ("delta", *[cmp["delta"][k] for k in OUTCOMES]))
    lines.append("  transitions: %s" % cmp["transitions"])
    for name, r in cmp["per_loss"].items():
        lines.append("  %-14s payoffs %-12s dU = %+6.1f   %s"
                     % (name, tuple(r["payoffs"]), r["delta"],
                        "HELPS" if r["helps"] else ("neutral" if r["delta"] == 0 else "HURTS")))
    lines.append("  break-even wrong penalty L* = %s" % cmp["break_even_wrong_penalty"])
    return "\n".join(lines)


def _parse_loss(s):
    c, a, w = (float(x) for x in s.split(","))
    return (c, a, w)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--battery", choices=["home", "charon", "both"], default="both")
    ap.add_argument("--loss", action="append", default=[],
                    help="extra loss as 'name=c,a,w', e.g. mine=1,0,-3")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    import blackboard_evolve as be                     # noqa: E402
    from o1_enumerate import build_battery, KNOWN_0833  # noqa: E402
    from g7_remeasure import load_charon               # noqa: E402
    import lexis_pair                                  # noqa: E402

    losses = dict(LOSSES)
    for spec in args.loss:
        name, trip = spec.split("=", 1)
        losses[name] = _parse_loss(trip)

    batteries = {}
    if args.battery in ("home", "both"):
        batteries["home"] = build_battery()[0]
    if args.battery in ("charon", "both"):
        batteries["charon"] = load_charon()[0]

    base_ops = [be.REGISTRY[n][0] for n in KNOWN_0833]
    arms = {
        "+parse_numbers only": lexis_pair.augmented_program("readout_last", False, False),
        "+parse_numbers +compute": lexis_pair.augmented_program("readout_last", True, False),
        "+parse_numbers +readout": lexis_pair.augmented_program("readout_last", False, True),
        "+bundle readout_last": lexis_pair.augmented_program("readout_last"),
        "+bundle readout_first": lexis_pair.augmented_program("readout_first"),
        "+bundle compute_first": lexis_pair.augmented_program("compute_first"),
    }
    result = {"losses": {k: list(v) for k, v in losses.items()}, "batteries": {}}
    for bname, tasks in batteries.items():
        base = run_program(base_ops, tasks)
        result["batteries"][bname] = {"baseline_counts": counts(base), "arms": {}}
        print("=" * 76)
        print("BATTERY %s -- baseline KNOWN_0833: %s" % (bname, counts(base)))
        print("=" * 76)
        for aname, (names, ops) in arms.items():
            cand = run_program(ops, tasks)
            cmp = compare(base, cand, losses)
            cmp["program"] = names
            cmp["per_task"] = [{"i": i, "base": b["outcome"], "cand": c["outcome"],
                                "selected": c["selected"]}
                               for i, (b, c) in enumerate(zip(base, cand))
                               if b["outcome"] != c["outcome"]]
            result["batteries"][bname]["arms"][aname] = cmp
            print(fmt_report(aname, cmp))
            print()
    if args.out:
        Path(args.out).write_text(json.dumps(result, indent=1), encoding="utf-8")
        print("wrote %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
