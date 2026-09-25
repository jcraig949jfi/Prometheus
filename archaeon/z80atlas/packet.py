"""Campaign packet (code-generated, ASCII, small): the map of which structural combinations produced which mechanical
signals, positive-control verdicts, exploits, the verification table, pointers. No interpretation is written here.
"""
from __future__ import annotations

import json
import time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def build(c) -> Path:
    from archaeon.z80atlas import grammar as GR
    F = GR.FROZEN; root = HERE / "campaign"; runs = [r for r in c.runs.values() if r["status"] == "DONE"]; fams = c.family_table()
    keys = ["spontaneous_replication", "moat_crossed", "moat_advantage", "compression", "new_arch_events", "coexistence", "longevity", "transport", "env_lineage", "ruler_gain", "persistence_over_control", "exploit"]
    # per axis-level: runs and flag counts
    axis = defaultdict(lambda: defaultdict(lambda: {"runs": 0, **{k: 0 for k in keys}}))
    for r in runs:
        fl = r.get("flags") or {}
        for a, v in r["factor_vector"].items():
            cell = axis[a][str(v)]; cell["runs"] += 1
            for k in fl: cell[k] = cell.get(k, 0) + 1
    # verification table: family -> reason -> signals summary
    verif = defaultdict(dict)
    for r in runs:
        if r["scheduler_reason"].startswith("verify:"):
            fam = r["scheduler_reason"].split(":")[1]; kind = ":".join(r["scheduler_reason"].split(":")[2:]); s = r["signals"]
            verif[fam][kind + "@s%d" % r["seed"]] = {"pop": s.get("final_pop_frac"), "endo": s.get("births_endo"), "best": s.get("best_ever"), "cross": bool(s.get("first_crossing")), "arch": s.get("archs"), "flags": sorted(r.get("flags") or {})}
    top = sorted(fams.items(), key=lambda x: -x[1]["best"])[:30]
    pk = {"schema": "archaeon.z80atlas.packet.v1", "built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "grammar": c.state["grammar"], "started": c.state["started"], "frozen_at": c.state.get("frozen_at"),
          "runs_done": len(runs), "errors": c.state.get("errors", 0), "families": len(fams), "retired": len(c.state["retired"]), "promotions": c.state["promotions"],
          "positive_controls": c.state["controls"], "uncalibrated": c.state["uncalibrated"], "high_value": c.state["high_value"][:100],
          "flag_totals": {k: sum(1 for r in runs if k in (r.get("flags") or {})) for k in keys},
          "axis_map": {a: dict(v) for a, v in axis.items()}, "top_families": [{"family": fam, "score": f["best"], "flags": sorted(f["flags"]), "runs": len(f["runs"]), "best_run": f.get("best_run"), "factors": c.runs[f["best_run"]]["factor_vector"] if f.get("best_run") else None} for fam, f in top],
          "verification": {k: v for k, v in verif.items()}, "exploit_runs": [r["run_id"] for r in runs if r["signals"].get("exploits")][:100],
          "spontaneous_runs": [r["run_id"] for r in runs if r["signals"].get("spontaneous_replication")][:100],
          "blocked": GR.BLOCKED, "pointers": {"runs": "archaeon/z80atlas/campaign/runs/<family>/<run_id>/{SPEC,RECEIPT,TELEMETRY.json.gz,SNAPSHOTS.json.gz,FORENSICS,EXPLOITS}",
                                               "atlas_index": "archaeon/z80atlas/campaign/ATLAS_INDEX.jsonl", "runs_log": "archaeon/z80atlas/campaign/RUNS.jsonl", "grammar": "archaeon/z80atlas/campaign/GRAMMAR_FROZEN.json", "log": "archaeon/z80atlas/campaign/scheduler.log"}}
    (root / "PACKET.json").write_text(json.dumps(pk, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    L = []
    L.append("+" + "=" * 78 + "+"); L.append("| Z80 x ATLAS COMBINATORIAL CAMPAIGN -- PACKET (code-generated; no interpretation)".ljust(79) + "|")
    L.append(("| Archaeon (M2) build of the NESTOR directive; grammar %s; started %s" % (pk["grammar"], pk["started"])).ljust(79) + "|")
    L.append(("| frozen %s; runs %d; errors %d; families %d; retired %d" % (pk["frozen_at"], pk["runs_done"], pk["errors"], pk["families"], pk["retired"])).ljust(79) + "|")
    L.append("+" + "=" * 78 + "+"); L.append("")
    L.append("0. POSITIVE CONTROLS"); L.append("-" * 40)
    for k, v in pk["positive_controls"].items(): L.append("  %-8s %-36s %s" % (v["verdict"], v["reason"].split(":")[1], v["substrate"]))
    L.append("  uncalibrated substrates: %s" % (json.dumps(pk["uncalibrated"]) if pk["uncalibrated"] else "none")); L.append("")
    L.append("1. FLAG TOTALS (mechanical triggers; promotion = more compute, not a claim)"); L.append("-" * 40)
    for k, v in pk["flag_totals"].items(): L.append("  %-26s %d" % (k, v))
    L.append("")
    L.append("2. AXIS MAP  (level: runs | spont moat moat_adv compr arch coex long transp env ruler persist exploit)"); L.append("-" * 40)
    for a, lv in pk["axis_map"].items():
        L.append("  " + a)
        for l, cell in sorted(lv.items()):
            L.append("    %-22s %5d | " % (l[:22], cell["runs"]) + " ".join("%3d" % cell.get(k, 0) for k in keys))
    L.append("")
    L.append("3. TOP FAMILIES (by best mechanical score)"); L.append("-" * 40)
    for f in pk["top_families"]:
        fv = f["factors"] or {}
        L.append("  %s score %d runs %d flags %s" % (f["family"], f["score"], f["runs"], ",".join(f["flags"])))
        L.append("      %s %s %s task=%s press=%s init=%s topo=%s mig=%s env=%s" % (fv.get("reproduction"), fv.get("representation.substrate"), fv.get("representation.layout"), fv.get("task"), fv.get("pressure"), fv.get("init"), fv.get("world.topology"), fv.get("world.migration"), fv.get("world.env_dynamics")))
    L.append("")
    L.append("4. VERIFICATION (late stage: fresh seeds, matched controls, transplants: same / physics_swap / world_swap / environment_swap)"); L.append("-" * 40)
    for fam, tab in list(pk["verification"].items())[:20]:
        L.append("  " + fam)
        for k, v in sorted(tab.items()): L.append("    %-44s pop %.2f endo %6d best %.2f cross %-5s arch %3d %s" % (k[:44], v["pop"] or 0, v["endo"] or 0, v["best"] or 0, v["cross"], v["arch"] or 0, ",".join(v["flags"])))
    L.append("")
    L.append("5. SPECIAL RESULTS"); L.append("-" * 40)
    L.append("  spontaneous replication runs: %d  (%s)" % (len(pk["spontaneous_runs"]), ", ".join(pk["spontaneous_runs"][:8])))
    L.append("  exploit runs (specimens frozen): %d  (%s)" % (len(pk["exploit_runs"]), ", ".join(pk["exploit_runs"][:8])))
    L.append("  moat_advantage families: %d" % sum(1 for f in pk["top_families"] if "moat_advantage" in f["flags"]))
    L.append("  blocked factor levels: %s" % json.dumps(pk["blocked"]))
    L.append("")
    L.append("6. POINTERS"); L.append("-" * 40)
    for k, v in pk["pointers"].items(): L.append("  %-12s %s" % (k, v))
    L.append(""); L.append("END. Scientific promotion is post-campaign adjudication. 'Not worth continuing' remains a first-class answer.")
    txt = "\n".join(L) + "\n"
    txt = txt.encode("ascii", "replace").decode("ascii")
    p = root / "CAMPAIGN_PACKET.md"; p.write_text(txt[:60000], encoding="utf-8", newline="\n")
    return p
