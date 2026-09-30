"""Fold probe round 3 (roles/Hecate/prereg/2026-09-30_pass3_v2/) into program
records, with the preregistered consequences and the repair-falsification
test (>= 3 of 8 unattainable / failed -> repair falsified).

    python -m hecate.probe_round3
"""

from __future__ import annotations

import collections
import json
import os

from hecate.probe_report import PROGS, VALID_READ, _norm_se, _rel
from hecate.schema import RESEARCH_AXES, validate_program

R3_PREREG = "roles/Hecate/prereg/2026-09-30_pass3_v2/PREREG.md"
GEN_SHA = "2adcfc8da07ee9adb9b04d2214889f0965758f7fcf0a60cde08eebb62bedd461"
IMPL_SHA = "a34a8c6143f49df2b33b75871e8f9cd12e60c10c37778ba595e12fedf1621685"
REVIVED = ("HT-37e311ce05", "HT-55162c0ac0", "HT-8a87057933", "HT-faa9277e02")


def _world_from_spec(tid, wid, sp, d):
    return {"id": wid, "triplicateId": tid, "passId": "P3v2",
            "mechanism_ids": sp.get("mechanism_ids") or [], "lens_ids": sp.get("lens_ids") or [],
            "hypothesis": sp.get("hypothesis"), "mechanism": sp.get("mechanism"),
            "intervention": sp.get("intervention"), "control": sp.get("control"),
            "positive_control": sp.get("positive_control"), "observable": sp.get("observable"),
            "success_criterion": json.dumps(sp.get("success_clauses")),
            "failure_criterion": json.dumps(sp.get("failure_clauses")),
            "alternative_explanation": sp.get("alternative_explanation"),
            "null_twin": sp.get("null_twin"), "substrate": sp.get("substrate"),
            "cost_estimate": sp.get("cost_estimate"),
            "stupid_explanations": sp.get("stupid_explanations"),
            "spec": _rel(os.path.join(d, "spec.json")),
            "attainability": _rel(os.path.join(d, "ATTAINABILITY.json"))}


def _pass(tid, pid, kind, prompt, sha, prior, unexplained, decision, support):
    return {"id": pid, "triplicateId": tid, "index": 3, "kind": kind,
            "added": ["new falsifier", "new observable"],
            "generator": {"model": "claude-opus-5-5", "search": False,
                          "prompt": prompt, "prompt_sha256": sha},
            "prereg": R3_PREREG, "inspected_prior": prior, "unexplained": unexplained,
            "decision": decision,
            "research_state": {a: "unknown" for a in RESEARCH_AXES} | {"empirical_support": support}}


def fold():
    with open(os.path.join(PROGS, "PROBE_ROUND3_SELECTION.jsonl"), encoding="utf-8") as fh:
        sel = [json.loads(l) for l in fh if l.strip()]
    res = []
    for s in sel:
        tid, wid = s["triplicateId"], s["probe_world"]
        wdir = os.path.join(PROGS, tid, "worlds", wid)
        with open(os.path.join(wdir, "probe", "OUTCOME.json"), encoding="utf-8") as fh:
            oc = json.load(fh)
        ppath = os.path.join(PROGS, tid, "program.json")
        with open(ppath, encoding="utf-8") as fh:
            p = json.load(fh)
        prior_valid = [w["id"] for w in p["experiments"] if w.get("outcome") in VALID_READ]
        out = oc["outcome"]
        ses = [_norm_se(x) for x in oc.get("stupid_explanations_status") or []]
        rows = _rel(os.path.join(wdir, "probe", "rows.jsonl"))
        for w2 in ("W5", "W6"):
            d2 = os.path.join(PROGS, tid, "worlds", w2)
            with open(os.path.join(d2, "spec.json"), encoding="utf-8") as fh:
                sp = json.load(fh)
            if not any(x["id"] == w2 for x in p["experiments"]):
                p["experiments"].append(_world_from_spec(tid, w2, sp, d2))
        if not any(ps["id"] == "P3v2" for ps in p["passes"]):
            p["passes"].append(_pass(tid, "P3v2", "minimal_worlds_v2",
                                     "hecate/programs/_prompts/pass3_v2.md", GEN_SHA,
                                     prior_valid, [], "FALSIFY", "none"))
        if not any(ps["id"] == "P3-probe3" for ps in p["passes"]):
            p["passes"].append(_pass(
                tid, "P3-probe3", "cheap_probe", "hecate/programs/_prompts/probe_impl_v3.md",
                IMPL_SHA, [wid], [x["text"] for x in ses if not x.get("addressed_by_this_run")],
                "FALSIFY" if out == "SIGNAL" else "PARK", "low" if out == "SIGNAL" else "none"))
        w = next(x for x in p["experiments"] if x["id"] == wid)
        w.update(outcome=out, round=3, rows=rows,
                 outcome_file=_rel(os.path.join(wdir, "probe", "OUTCOME.json")),
                 statistics=oc.get("statistics"),
                 anomalies=[{"id": f"A{i+1}", "text": str(a)} for i, a in enumerate(oc.get("anomalies") or [])],
                 rejected_explanations=[x["text"] for x in ses
                                        if x.get("addressed_by_this_run") and out in ("NULL", "SIGNAL")])
        oid = f"O-{wid}-r3"
        p["hypotheses"] = [h for h in p["hypotheses"] if h["id"] != oid]
        p["hypotheses"].append({
            "id": oid, "triplicateId": tid, "passId": "P3-probe3", "kind": "observation",
            "layer": "experimental_observation", "evidence_rows": [rows],
            "statement": f"{wid} probe round 3: {out}. {oc.get('notes', '')}"[:1200],
            "derived_from": w.get("mechanism_ids") or []})
        if out in VALID_READ or out == "SIGNAL":
            for h in p["hypotheses"]:
                if h["id"] in (w.get("mechanism_ids") or []) and h["layer"] == "speculation":
                    h["layer"] = "implemented_candidate"
        if out == "SIGNAL":
            verdict, reason = "PROBING", "round-3 SIGNAL; Pass 4 next"
        elif out in VALID_READ and tid in REVIVED:
            verdict, reason = "PARK", "revived by the generator repair and read NULL (two reasons)"
        elif out in VALID_READ and prior_valid:
            verdict, reason = "PARK", f"two valid NULL readings ({prior_valid[0]}, {wid})"
        elif out in VALID_READ:
            verdict, reason = "SPECULATIVE", "one valid NULL reading"
        else:
            verdict, reason = p["currentVerdict"], f"{out}: no valid reading"
        p["currentVerdict"] = verdict
        p["evidenceSummary"] = {"layer": "experimental_observation", "rows": rows,
                                "note": f"round 3 {wid} {out}: {reason}"}
        errs = validate_program(p)
        if errs:
            raise SystemExit(f"{tid}: {errs[:3]}")
        with open(ppath, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(p, indent=2, ensure_ascii=True) + "\n")
        res.append({"triplicateId": tid, "world": wid, "outcome": out, "verdict": verdict,
                    "reason": reason, "core_minutes": oc.get("core_minutes")})
    bad = sum(r["outcome"] in ("INSTRUMENT_FAIL", "NOT_BUILT", "SPEC_UNATTAINABLE") for r in res)
    bad += sum(1 for s in sel if s["status"] != "SELECTED")
    rep = {"prereg": R3_PREREG, "counts": dict(collections.Counter(r["outcome"] for r in res)),
           "verdicts": dict(collections.Counter(r["verdict"] for r in res)),
           "unattainable_or_failed": bad, "repair_falsified": bad >= 3, "worlds": res}
    with open(os.path.join(PROGS, "PROBE_ROUND3_REPORT.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(rep, indent=2, ensure_ascii=True) + "\n")
    return rep


if __name__ == "__main__":
    r = fold()
    print(r["counts"], r["verdicts"], "repair_falsified", r["repair_falsified"], r["unattainable_or_failed"])
    for w in r["worlds"]:
        print(w["triplicateId"], w["world"], w["outcome"], w["verdict"], "|", w["reason"])
