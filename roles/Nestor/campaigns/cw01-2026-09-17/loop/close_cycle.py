"""Close a priority-loop cycle: collect RESULT.json of the frozen ten, summarise evidence and
state changes, write CYCLE_REPORT_<tag>.md, and update CAMPAIGN_STATE.json (loop section;
totals derived from the ledger and gated)."""
from __future__ import annotations

import collections
import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
CAMPAIGN = HERE.parent
sys.path.insert(0, str(CAMPAIGN / "lib"))
import recordsafety as RS      # noqa: E402


def main(tag, expdir="cw01-loop1"):
    pr = json.loads((HERE / ("PRIORITY_%s.json" % tag)).read_text(encoding="utf-8"))
    ten = pr["frozen_top_ten"]
    exp = CAMPAIGN / "experiments" / expdir
    rows = []
    for c in ten:
        d = exp / c["id"]
        if not (d / "RESULT.json").exists():            # a tranche may span experiment directories
            for alt in (CAMPAIGN / "experiments").glob("cw01-*/" + c["id"]):
                if (alt / "RESULT.json").exists():
                    d = alt
                    break
        rp = d / "RESULT.json"
        res = json.loads(rp.read_text(encoding="utf-8")) if rp.exists() else None
        rows.append({"rank": c["rank"], "id": c["id"], "parent": c["parent"], "type": c["type"],
                     "ran": res is not None,
                     "disposition": ((res or {}).get("disposition") or (res or {}).get("reading")
                                     or ("material=%s" % res.get("material") if res and "material" in res else None)
                                     or ("RAN (see RESULT.json)" if res else "NOT RUN")),
                     "elapsed_s": (res or {}).get("elapsed_s"), "prereg_sha256": (res or {}).get("prereg_sha256")})
    ev = [json.loads(l) for l in (HERE / "EVIDENCE.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    st_events = [json.loads(l) for l in (HERE / "STATE.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    state_now = {}
    for e in st_events:
        state_now[e["trajectory_id"]] = e
    material = [e for e in ev if e.get("material_change")]
    n_stasis = sum(1 for v in state_now.values() if v["state"].startswith("TEMPORAL_STASIS"))   # scoped labels count (D078)

    md = ["# CW01 priority loop - cycle report %s" % tag, "",
          "Ten frozen perturbations executed under their own preregistrations (PREREG.json hashed before each run).",
          "", "| rank | id | parent | type | disposition / reading | s |", "|---|---|---|---|---|---|"]
    for r in rows:
        md.append("| %d | %s | %s | %s | %s | %s |" % (r["rank"], r["id"], r["parent"], r["type"], r["disposition"], r["elapsed_s"]))
    md += ["", "## Evidence appended this cycle (%d events, %d material)" % (len(ev), len(material)), ""]
    for e in ev:
        md.append("- **%s** <- %s (%s): %s" % (e["trajectory_id"], e["perturbation_id"], "MATERIAL" if e.get("material_change") else "not material", e["summary"]))
    md += ["", "## State after the cycle (%d trajectories, %d in TEMPORAL_STASIS)" % (len(state_now), n_stasis), ""]
    for tid, v in sorted(state_now.items()):
        md.append("- %s: %s - %s" % (tid, v["state"], v.get("reason", "")))
    md += ["", "Rank is temporary. Every trajectory outside the ten waits with its record intact. The next cycle begins with global re-evaluation of the whole pool."]
    out = HERE / ("CYCLE_REPORT_%s.md" % tag)
    out.write_text("\n".join(md), encoding="utf-8")
    RS.require_ascii_safe(out)

    # ---- campaign state: loop section + derived totals
    state = json.loads((CAMPAIGN / "CAMPAIGN_STATE.json").read_text(encoding="utf-8"))
    state["campaign_order"] = ("PRIORITY LOOP (operator directive 2026-09-18): revisit / perturb / stasis / reactivate over the whole history; "
                               "nothing scientific is killed; see loop/LOOP_RULES.md")
    state.setdefault("loop", {})
    state["loop"][tag] = {"pool": sum(1 for _ in (HERE / "TRAJECTORIES.jsonl").read_text(encoding="utf-8").splitlines() if _.strip()),
                          "candidates": pr["n_candidates"], "frozen_ten": [r["id"] for r in rows],
                          "dispositions": {r["id"]: r["disposition"] for r in rows},
                          "evidence_events": len(ev), "material": len(material), "in_stasis": n_stasis,
                          "report": "loop/CYCLE_REPORT_%s.md" % tag}
    state["active"] = {"mode": "priority_loop", "cycle": tag, "phase": "APPENDED",
                       "next": "next cycle: RECONCILE the whole pool with this cycle's evidence, re-score, re-diversify, freeze a new ten"}
    state["updated_local"] = time.strftime("%Y-%m-%d %H:%M:%S")
    entries = [json.loads(l) for l in (CAMPAIGN / "DEFECTS.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    per = collections.Counter(d.get("experiment_id") for d in entries)
    state["campaign_totals"]["defects_logged"] = len(entries)
    state["campaign_totals"]["defects_per_experiment"] = {str(k).replace("cw01-", ""): v for k, v in sorted(per.items())}
    (CAMPAIGN / "CAMPAIGN_STATE.json").write_text(json.dumps(state, indent=1, ensure_ascii=True), encoding="utf-8")
    RS.require_ascii_safe(CAMPAIGN / "CAMPAIGN_STATE.json")
    v = RS.require_tally_consistent(CAMPAIGN / "CAMPAIGN_STATE.json", CAMPAIGN / "DEFECTS.jsonl")
    print("cycle %s closed: %d/10 ran, %d evidence events (%d material), %d in stasis | tally %s" % (
        tag, sum(r["ran"] for r in rows), len(ev), len(material), n_stasis, v["outcome"]))
    for r in rows:
        print("  %2d %-6s %-7s %s" % (r["rank"], r["id"], r["parent"], r["disposition"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else time.strftime("%Y-%m-%d"),
                  sys.argv[2] if len(sys.argv) > 2 else "cw01-loop1"))
