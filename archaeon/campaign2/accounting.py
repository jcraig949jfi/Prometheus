"""AUTOMATIC ACCOUNTING (directive Phase A group I): records, ledger candidates and the
campaign funnel are generated from receipts, rows, preregistrations and typed states.
Agents interpret the science in a clearly marked addendum; they never transcribe numbers
that already exist in machine-readable form.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from archaeon.wse import states as S
from archaeon.campaign2 import prereg as P

C2 = Path(__file__).resolve().parent
LEDGER = C2 / "LEDGER.jsonl"


# ------------------------------------------------------------------ tables
def _fmt(v: Any) -> str:
    if v is None:
        return "-"
    if isinstance(v, float):
        return "%.3f" % v
    return str(v)


def arm_table(rows: List[dict], arm_field: str, metrics: Sequence[str], seed_field: str = "seed") -> str:
    arms = sorted({r.get(arm_field) for r in rows}, key=str)
    seeds = sorted({r.get(seed_field) for r in rows}, key=str)
    out = []
    for m in metrics:
        out.append("    %-22s %s  %s" % ("arm / %s" % m, " ".join("%7s" % ("s%s" % s) for s in seeds), "  mean    n"))
        for a in arms:
            by = {r.get(seed_field): r.get(m) for r in rows if r.get(arm_field) == a}
            vals = [by.get(s) for s in seeds]
            nums = [v for v in vals if isinstance(v, (int, float))]
            mean = sum(nums) / len(nums) if nums else None
            out.append("    %-22s %s  %s  %3d" % (str(a)[:22], " ".join("%7s" % _fmt(v) for v in vals), "%6s" % _fmt(mean), len(nums)))
        out.append("")
    return "\n".join(out)


def first_solved_table(rows: List[dict], arm_field: str) -> str:
    arms = sorted({r.get(arm_field) for r in rows}, key=str)
    lines = ["    %-22s %-10s %s" % ("arm", "footholds", "first_solved_gen per row")]
    for a in arms:
        rs = [r for r in rows if r.get(arm_field) == a]
        fs = [r.get("first_solved_gen") for r in rs]
        lines.append("    %-22s %-10s %s" % (str(a)[:22], "%d/%d" % (sum(1 for f in fs if f is not None), len(rs)), ",".join(_fmt(f) for f in fs)))
    return "\n".join(lines)


# ------------------------------------------------------------------ record
def render_record(prereg: dict, receipt: dict, rows: List[dict], attempts_index: dict, *,
                  arm_field: str = "arm", metrics: Sequence[str] = ("competence_heldout",),
                  states: Optional[List[dict]] = None, disposition: Optional[dict] = None,
                  addendum: Optional[Dict[str, str]] = None, decisions: Sequence[str] = ()) -> str:
    addendum = addendum or {}
    states = states if states is not None else receipt.get("typed_states", [])
    disposition = disposition or receipt.get("disposition_candidate") or {}
    att = attempts_index.get("attempts", {})
    n_att = len(att)
    of_record = attempts_index.get("of_record")
    t = receipt.get("timings", {})
    lines = ["# %s -- %s" % (prereg["experiment"], prereg.get("title", "")), "", P.render(prereg)]
    # B
    lines += ["## B. EXECUTION (generated from receipts)", ""]
    lines.append("- attempts: %d (of record: a%02d); resumed_from: %s; replayed steps on the attempt of record: %d" % (
        n_att, of_record or 0, receipt.get("resumed_from"), len(receipt.get("replayed", []))))
    for k in sorted(att, key=int):
        a = att[k]
        lines.append("    a%02d  errors=%d replayed=%d engine=%s purpose=%s disposition_candidate=%s" % (
            int(k), a.get("errors", 0), a.get("replayed_steps", 0), a.get("engine_path"), a.get("purpose", ""), a.get("disposition_candidate")))
    lines.append("- engine: %s; worlds %d; artifacts %d; imports %d; records %d; errors %d" % (
        "live" if receipt.get("engine_path") else "dry-run", len(receipt.get("worlds", {})), len(receipt.get("artifacts", {})),
        len(receipt.get("imports", {})), len(receipt.get("records", {})), len(receipt.get("errors", []))))
    imps = receipt.get("imports", {})
    if imps:
        lines.append("- import hash checks: %d/%d ok" % (sum(1 for v in imps.values() if v.get("hash_ok")), len(imps)))
    lines.append("- timings (s): " + ", ".join("%s=%s" % (k, v) for k, v in sorted(t.items())))
    if receipt.get("errors"):
        lines.append("- errors on the attempt of record:")
        for e in receipt["errors"]:
            lines.append("    " + json.dumps(e, sort_keys=True)[:200])
    if decisions:
        lines.append("- decisions: " + ", ".join(decisions))
    lines.append("- warnings from the loop: %s" % sorted({w for r in rows for w in (r.get("warnings") or [])}))
    lines.append("")
    # C
    lines += ["## C. SCIENCE (numbers generated from rows; interpretation in the addendum)", ""]
    if rows:
        lines.append("- primary table:")
        lines.append(arm_table(rows, arm_field, metrics))
        if any("first_solved_gen" in r for r in rows):
            lines.append("- footholds:")
            lines.append(first_solved_table(rows, arm_field))
            lines.append("")
    lines.append("- typed states fired: %s" % ([s["state"] for s in states] or "none"))
    for s in states:
        lines.append("    %s  %s" % (s["state"], json.dumps(s.get("evidence"), sort_keys=True)[:220]))
    lines.append("- disposition candidate (machine): %s -- %s" % (disposition.get("disposition"), disposition.get("reason")))
    if disposition.get("evidence"):
        lines.append("    evidence: " + json.dumps(disposition["evidence"], sort_keys=True))
    if disposition.get("battery"):
        lines.append("    battery: " + json.dumps(disposition["battery"], sort_keys=True))
    lines.append("- claim ceiling (machine): %s; preregistered ceiling: %s" % (disposition.get("claim_ceiling"), prereg.get("claim_ceiling")))
    lines.append("")
    lines.append("### C-addendum (agent interpretation; quotes the candidate, may argue with it)")
    lines.append("")
    lines.append(addendum.get("science", "(none)"))
    lines.append("")
    # D
    lines += ["## D. TEARDOWN (generated)", ""]
    td = receipt.get("teardown", {})
    lines.append("- worlds: %s" % (json.dumps(td, sort_keys=True) if td else "none (dry run)"))
    lines.append("- all TERMINATED: %s" % (all(v == "TERMINATED" for v in td.values()) if td else "n/a"))
    lines.append("")
    # E
    lines += ["## E. BENCH IMPROVEMENT", "", "- ledger candidates (generated): see LEDGER.jsonl entries tagged %s" % prereg["experiment"], "",
              addendum.get("bench", "(none)"), ""]
    # F
    lines += ["## F. LANDSCAPE / GRADIENT NOTES", "", addendum.get("landscape", "(none)"), ""]
    lines.append("DISPOSITION: %s (machine candidate %s). %s" % (addendum.get("disposition", disposition.get("disposition")),
                                                                  disposition.get("disposition"), addendum.get("disposition_note", "")))
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------ ledger
def next_ledger_id(path: Path = LEDGER) -> str:
    n = 0
    if path.exists():
        for l in path.read_text(encoding="utf-8").splitlines():
            if l.strip():
                n = max(n, int(json.loads(l)["id"].split("-")[1]))
    return "L2-%03d" % (n + 1)


def ledger_candidates(experiment: str, receipt: dict, states: List[dict], attempts_index: dict) -> List[dict]:
    """Candidate entries from the receipt: engine/harness errors (BUG), typed states that
    fired (ASSAY_STATE, informational), attempts > 1 (RECOVERY: resumed or re-created)."""
    out = []
    for e in receipt.get("errors", []):
        out.append({"experiment": experiment, "category": "BUG", "severity": "major", "auto": True,
                    "symptom": "step %s failed: %s" % (e.get("step"), str(e.get("error", ""))[:160]),
                    "evidence": "attempt %s receipt errors" % receipt.get("attempt"), "workaround": "", "proposed_fix": "",
                    "proposed_telemetry": "", "blocks_future_runs": False, "safe_to_defer": False})
    for s in states:
        if s["state"] in S.ASSAY_STATES:
            out.append({"experiment": experiment, "category": "ASSAY_STATE", "severity": "note", "auto": True,
                        "symptom": "typed state %s fired automatically" % s["state"], "evidence": json.dumps(s.get("evidence"), sort_keys=True)[:200],
                        "workaround": "", "proposed_fix": "", "proposed_telemetry": "", "blocks_future_runs": False, "safe_to_defer": True})
    n_att = len(attempts_index.get("attempts", {}))
    if n_att > 1:
        replayed = len(receipt.get("replayed", []))
        out.append({"experiment": experiment, "category": "RECOVERY", "severity": "note", "auto": True,
                    "symptom": "%d attempts; attempt of record replayed %d steps from the previous attempt (%s)" % (
                        n_att, replayed, "resume" if replayed else "full re-creation"),
                    "evidence": "ATTEMPTS.json", "workaround": "", "proposed_fix": "", "proposed_telemetry": "",
                    "blocks_future_runs": False, "safe_to_defer": True})
    return out


def append_ledger(entries: List[dict], path: Path = LEDGER) -> List[str]:
    ids = []
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as f:
        for e in entries:
            e = dict(e)
            e.setdefault("id", next_ledger_id(path))
            e.setdefault("recurrence", 0); e.setdefault("recurred_in", []); e.setdefault("mitigation_helped", None)
            e.setdefault("links", []); e.setdefault("recorded_at", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
            f.write(json.dumps(e, sort_keys=True) + "\n"); f.flush()
            ids.append(e["id"])
    return ids


def recur(ledger_id: str, experiment: str, path: Path = LEDGER, mitigation_helped: Optional[bool] = None) -> None:
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    for r in rows:
        if r["id"] == ledger_id:
            r["recurrence"] += 1; r["recurred_in"].append(experiment)
            if mitigation_helped is not None:
                r["mitigation_helped"] = mitigation_helped
    path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8", newline="\n")


# ------------------------------------------------------------------ funnel
def funnel_row(experiment: str, prereg: dict, receipt: dict, states: List[dict], disposition: dict, attempts_index: dict,
               *, machine_defect: str = "", machine_repair: str = "", telemetry_added: str = "", decisions: Sequence[str] = ()) -> dict:
    names = [s["state"] for s in states]
    decl = prereg.get("decl", {})
    return {
        "experiment": experiment,
        "attempted": True,
        "engine_executed": bool(receipt.get("engine_path")) and not any(e.get("kind") == "engine" for e in receipt.get("errors", [])),
        "assay_capable": not any(s in names for s in S.ASSAY_STATES),
        "positive_control_passed": (None if not decl.get("positive_control") else "POSITIVE_CONTROL_FAILED" not in names),
        "target_reached": (None if not decl.get("target") else "TARGET_UNREACHABLE" not in names),
        "intervention_applied": (None if not decl.get("interventions") else "INTERVENTION_NOT_APPLIED" not in names),
        "adequate_sample": "UNDERPOWERED" not in names,
        "scientific_disposition": disposition.get("disposition"),
        "claim_ceiling": disposition.get("claim_ceiling"),
        "attempts": len(attempts_index.get("attempts", {})),
        "resumed": any(a.get("replayed_steps", 0) > 0 for a in attempts_index.get("attempts", {}).values()),
        "machine_defect": machine_defect, "machine_repair": machine_repair, "telemetry_added": telemetry_added,
        "decisions": list(decisions), "typed_states": names,
    }
