"""Post-campaign adjudication of the special flags. RUNS AFTER THE CAMPAIGN, NEVER DURING.

WHY THIS IS A SEPARATE SCRIPT. The campaign froze its flag rules and thresholds before
launch. Two defects in those rules showed up while it ran (DEFECTS.md: the flags mix a
historical crossing event with a final-state measurement, and the reservoir flag never
checks that the reservoir contributed). Editing the scheduler to fix them mid-flight would
be a post-result threshold change, which the directive forbids and which would also make
the first half of the campaign incomparable with the second.

So the flags keep firing exactly as preregistered - they are a PRESERVATION trigger, and
they preserve correctly - and this script applies stricter rules afterwards, to the frozen
record. Its rules are declared here, in one place, and every verdict carries the numbers it
was computed from.

Nothing in the campaign imports this file.

VERDICTS
  ADMISSIBLE    the record supports the claim the flag names, at final state, with a margin
  WEAK          the flag fired on a real event, but the evidence does not separate it from
                its control, or the run is a seeded instrument
  INADMISSIBLE  the evidence contradicts the flag's name, or the run cannot bear on it at
                all (a seeded instrument under a spontaneity flag, an exogenous control
                under an endogenous-reproduction flag)
"""
from __future__ import annotations

import collections
import json
import pathlib
import sys

CROSS = 0.90          # the campaign's own crossing threshold, unchanged
MARGIN = 0.25         # minimum separation from the matched control, declared here


def load(p):
    p = pathlib.Path(p)
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="ascii").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def run_summary(root, run):
    """The FULL summary, read from the per-run record rather than from the index.

    The index carries a whitelist of headline keys, and that whitelist does not include
    replication_events or births_similar_no_write - the two fields that say whether a
    birth was backed by evidence that the organism placed the child's bytes. Reading the
    index here made every spontaneity verdict come back INADMISSIBLE for "no
    evidence-backed replication event" while the per-run record showed one at fidelity
    0.92. The index schema is deliberately NOT being changed: the campaign is running, and
    a mid-flight schema change would leave its two halves incomparable. The adjudicator
    reads the deeper file, which has always held the full record.
    """
    fam, rid = run.get("family"), run.get("run_id")
    if fam and rid:
        p = root / "runs" / fam / rid / "RESULT.json"
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="ascii")).get("summary", {})
            except (OSError, json.JSONDecodeError):
                pass
    return run.get("summary", {})


def adjudicate(root):
    root = pathlib.Path(root)
    rows = {r["run_id"]: r for r in load(root / "INDEX.jsonl")}
    specials = load(root / "SPECIALS.jsonl")
    verdicts = []

    for s in specials:
        run = rows.get(s["run_id"]) or {}
        summ = run_summary(root, run)
        der = run.get("derived", {})
        ev = s.get("evidence") or {}
        flag = s["flag"]
        v, why, numbers = "WEAK", "", {}

        if flag == "REACHED_ONLY_UNDER_ENDOGENOUS_REPRODUCTION":
            endo = ev.get("endogenous_held")
            ext = ev.get("external_held")
            margin = (endo or 0) - (ext or 0)
            numbers = {"endogenous_held": endo, "external_held": ext, "margin": round(margin, 4),
                       "endogenous_is_endogenous": der.get("endogenous")}
            if not der.get("endogenous"):
                v, why = "INADMISSIBLE", "the flagged run is not an endogenous treatment"
            elif margin < 0:
                v, why = "INADMISSIBLE", "the exogenous control finished better than the flagged run"
            elif (endo or 0) < CROSS:
                v, why = "WEAK", "the flagged run is below the crossing threshold at final state (D01)"
            elif margin < MARGIN:
                v, why = "WEAK", "margin below %.2f: the control is not separated" % MARGIN
            else:
                v, why = "ADMISSIBLE", "at threshold at final state, control below it, margin >= %.2f" % MARGIN

        elif flag == "SPONTANEOUS_REPLICATOR_FROM_RANDOM_BYTES":
            numbers = {"seeded_instrument": s.get("seeded_instrument"),
                       "spontaneity_test": der.get("spontaneity_test"),
                       "fidelity": (ev or {}).get("fidelity"),
                       "replication_events": summ.get("replication_events"),
                       "births_similar_no_write": summ.get("births_similar_no_write")}
            if s.get("seeded_instrument") or not der.get("spontaneity_test"):
                v, why = "INADMISSIBLE", "seeded population: cannot bear on spontaneous origin"
            elif not summ.get("replication_events"):
                v, why = "INADMISSIBLE", "no evidence-backed replication event in the run"
            elif (ev.get("fidelity") or 0) < CROSS:
                v, why = "WEAK", "first replicator fidelity below %.2f" % CROSS
            else:
                v, why = "ADMISSIBLE", "random initial population, evidence-backed copy, fidelity >= %.2f" % CROSS

        elif flag == "RESERVOIR_CROSSED_A_MOAT":
            occ = ev.get("niche_occupancy") or []
            held = ev.get("held")
            numbers = {"held": held, "niche_occupancy": occ, "seeded_instrument": s.get("seeded_instrument"),
                       "endogenous": der.get("endogenous")}
            if s.get("seeded_instrument"):
                v, why = "INADMISSIBLE", "seeded instrument population"
            elif not der.get("endogenous"):
                v, why = "INADMISSIBLE", "exogenous control, not a reservoir result"
            elif (held or 0) < CROSS:
                v, why = "WEAK", "below the crossing threshold at final state (D01)"
            else:
                v, why = "WEAK", ("at threshold, but the flag cannot show the easy niche supplied the "
                                  "crossing lineage; that needs the lineage records (D02)")

        elif flag == "REACHED_ONLY_IN_INCREMENTAL_REPRESENTATION":
            inc = ev.get("incremental_held")
            at = ev.get("atomic_held")
            margin = (inc or 0) - (at or 0)
            numbers = {"incremental_held": inc, "atomic_held": at, "margin": round(margin, 4)}
            if margin < MARGIN:
                v, why = "WEAK", "margin below %.2f" % MARGIN
            elif (inc or 0) < CROSS:
                v, why = "WEAK", "below the crossing threshold at final state (D01)"
            else:
                v, why = "ADMISSIBLE", "incremental at threshold, atomic separated by >= %.2f" % MARGIN

        elif flag == "REPRODUCTIVE_ARCHITECTURE_CHANGED_UNDER_TASK_DEMAND":
            numbers = {"span_mean_final": ev.get("span_mean_final"), "pressure": ev.get("pressure"),
                       "replication_events": summ.get("replication_events")}
            if not summ.get("replication_events"):
                v, why = "INADMISSIBLE", "no evidence-backed replication in the run"
            else:
                v, why = "WEAK", ("compression is measured against the representation length, not against "
                                  "a matched no-task control; needs the paired table")

        verdicts.append({"run_id": s["run_id"], "family": s.get("family"), "flag": flag,
                         "verdict": v, "why": why, "numbers": numbers,
                         "cell": s.get("cell"), "ts": s.get("ts")})

    by = collections.Counter((x["flag"], x["verdict"]) for x in verdicts)
    summary = {}
    for flag in sorted({x["flag"] for x in verdicts}):
        summary[flag] = {v: by[(flag, v)] for v in ("ADMISSIBLE", "WEAK", "INADMISSIBLE") if by[(flag, v)]}

    out = {"root": str(root), "n_specials": len(specials), "rules": {"CROSS": CROSS, "MARGIN": MARGIN},
           "summary": summary, "verdicts": verdicts}
    (root / "ADJUDICATION.json").write_text(json.dumps(out, indent=1, ensure_ascii=True, default=str),
                                            encoding="ascii")

    L = ["# Special-flag adjudication", "",
         "Applied AFTER the campaign to the frozen record. The flags fired as preregistered;",
         "these stricter rules are declared in adjudicate.py and were never used to steer the run.",
         "", "| flag | admissible | weak | inadmissible |", "|---|---|---|---|"]
    for flag, d in summary.items():
        L.append("| %s | %d | %d | %d |" % (flag, d.get("ADMISSIBLE", 0), d.get("WEAK", 0),
                                            d.get("INADMISSIBLE", 0)))
    L += ["", "## Admissible instances", ""]
    adm = [v for v in verdicts if v["verdict"] == "ADMISSIBLE"]
    if not adm:
        L.append("None.")
    for v in adm[:60]:
        L.append("- **%s** %s: %s" % (v["flag"], v["run_id"], json.dumps(v["numbers"], default=str)[:220]))
    (root / "ADJUDICATION.md").write_text("\n".join(L), encoding="ascii")
    return out


if __name__ == "__main__":
    o = adjudicate(sys.argv[1] if len(sys.argv) > 1 else "observatory")
    print(json.dumps({"n_specials": o["n_specials"], "summary": o["summary"]}, indent=1))
