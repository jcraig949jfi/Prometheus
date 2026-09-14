"""H1/H0 phase-2 readout (F-18). Numbers only; Harmonia analyses.

Reads every phase-2 candidate set (the original, the re-issued slot-free
rows, and the artifact re-issue when it exists), reports per target task and
per cell the status / solved / vm_ops / oracle_calls, and runs the
DEGENERACY CHECK Harmonia made the second-seed replicate conditional on:
the S00-deg row (second seed_root) against its first-seed twin (target 0,
S00). Bit-identical result projection => the replicate measures nothing
and is not issued; different => the second-seed rows per cell are planned.

No contrast is computed. G_joint_treatment_S11_minus_S00 and I are
Harmonia's, on the solve-fraction scale, with the target task as the block.
"""
from __future__ import annotations

import argparse
import datetime
import json
from typing import Any, Dict, List, Sequence

SETS = ("cs-h1h0-1-p2", "cs-h1h0-1-p2-r1", "cs-h1h0-1-p2b")
CELLS = ("fresh", "random_pack", "S00", "S10", "S01", "S11", "S00-deg")
COMPARE_FIELDS = ("status", "solved", "solution", "solution_size", "candidates_tried", "candidates_invalid",
                  "verifications", "oracle_calls", "vm_ops", "constraints_seeded", "constraints_final",
                  "seed_probe_shortfall", "seeded_from", "witnesses", "witness_truncated")


def fetch(conn, sets: Sequence[str] = SETS) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(candidate_set_id, source_evidence->>'campaign_set'), arm_id, source_evidence->>'task_id', request_key, status, "
                "result_summary->'result'->'repeats'->0->'result', result_summary->'load_receipt'->>'allowance_mechanism', "
                "left(error, 200), sfe_experiment_id, spec_hash FROM viv.research_experiment_queue "
                "WHERE (candidate_set_id = ANY(%s) OR source_evidence->>'campaign_set' = ANY(%s)) "
                "ORDER BY source_evidence->>'task_id', arm_id, request_key", (list(sets), list(sets)))
    out = []
    for cs, arm, task, rk, status, res, allow, err, exp, spec_hash in cur.fetchall():
        out.append({"set": cs, "arm": arm, "task_id": task, "request_key": rk, "status": status,
                    "result": res or {}, "allowance_mechanism": allow, "error": err, "sfe_experiment_id": exp,
                    "spec_hash": spec_hash})
    return out


def dedup_by_spec_hash(live: Dict[tuple, Dict[str, Any]]) -> Dict[str, Any]:
    """Harmonia 57c259656 item 1b: dedup by spec hash BEFORE any statistic,
    with a mechanical refusal when one hash appears under two labels. Here
    the refusal is a flag on the readout (the readout computes no
    statistic); the analysis file must not treat the duplicated labels as
    independent arms."""
    by_hash: Dict[str, List[str]] = {}
    for (task, arm), r in live.items():
        h = r.get("spec_hash")
        if h:
            by_hash.setdefault(h, []).append(arm)
    dup: Dict[tuple, int] = {}
    for h, arms in by_hash.items():
        s = tuple(sorted(set(arms)))
        if len(s) > 1:
            dup[s] = dup.get(s, 0) + 1
    labels_sharing = sorted(dup, key=lambda k: -dup[k])
    return {"distinct_payloads": len(by_hash), "labels_sharing_a_hash": [list(k) for k in labels_sharing],
            "refusal": ("REFUSE_INDEPENDENT_ARMS: {} label groups share a spec hash; count each payload once".format(len(labels_sharing))
                        if labels_sharing else None)}


def _live(rows: List[Dict[str, Any]]) -> Dict[tuple, Dict[str, Any]]:
    """One row per (task, arm): the completed one if any, else the latest
    non-cancelled record. Cancelled rows are records, not results."""
    best: Dict[tuple, Dict[str, Any]] = {}
    for r in rows:
        k = (r["task_id"], r["arm"])
        if r["status"] == "cancelled":
            continue
        if k not in best or (r["status"] == "completed" and best[k]["status"] != "completed"):
            best[k] = r
    return best


def degeneracy_check(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    live = _live(rows)
    tasks = sorted({t for t, _ in live})
    t0 = tasks[0] if tasks else None
    a = live.get((t0, "S00")); b = live.get((t0, "S00-deg"))
    if not a or not b or a["status"] != "completed" or b["status"] != "completed":
        return {"verdict": "INDETERMINATE", "reason": "twin or degeneracy row not completed", "task": t0}
    diffs = [f for f in COMPARE_FIELDS if a["result"].get(f) != b["result"].get(f)]
    identical = not diffs
    return {"verdict": "BIT_IDENTICAL" if identical else "DIFFERS", "task": t0, "differing_fields": diffs,
            "first_seed": {f: a["result"].get(f) for f in ("status", "solved", "vm_ops", "oracle_calls", "candidates_tried")},
            "second_seed": {f: b["result"].get(f) for f in ("status", "solved", "vm_ops", "oracle_calls", "candidates_tried")},
            "consequence": ("the second-seed replicate is bit-identical and measures nothing; NOT issued (Harmonia item 4)"
                            if identical else "the second-seed replicate rows per cell are eligible; plan them")}


def readout(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    live = _live(rows)
    tasks = sorted({t for t, _ in live})
    table = []
    for t in tasks:
        rec = {"task_id": t}
        for c in CELLS:
            r = live.get((t, c))
            if r is None:
                rec[c] = None; continue
            res = r["result"]
            rec[c] = {"status": r["status"], "kind_status": res.get("status"), "solved": res.get("solved"),
                      "vm_ops": res.get("vm_ops"), "oracle_calls": res.get("oracle_calls"),
                      "allowance": r["allowance_mechanism"], "set": r["set"],
                      "error": (r["error"] if r["status"] == "failed" else None)}
        table.append(rec)
    counts: Dict[str, Dict[str, int]] = {}
    for (t, c), r in live.items():
        d = counts.setdefault(c, {"completed": 0, "failed": 0, "queued": 0, "running": 0, "solved": 0})
        d[r["status"]] = d.get(r["status"], 0) + 1
        if r["status"] == "completed" and r["result"].get("solved"):
            d["solved"] += 1
    by_set: Dict[str, Dict[str, int]] = {}
    for r in rows:
        by_set.setdefault(r["set"], {}).setdefault(r["status"], 0)
        by_set[r["set"]][r["status"]] += 1
    artifact_cells_done = all(counts.get(c, {}).get("completed", 0) == len(tasks) for c in ("random_pack", "S10", "S01", "S11")) if tasks else False
    slot_free_done = all(counts.get(c, {}).get("completed", 0) == len(tasks) for c in ("fresh", "S00")) if tasks else False
    return {"schema": "archaeon.h1h0.phase2_readout.v0",
            "written": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "sets": list(SETS), "by_set": by_set, "n_targets": len(tasks),
            "complete": bool(tasks) and slot_free_done and artifact_cells_done,
            "slot_free_complete": slot_free_done, "artifact_cells_complete": artifact_cells_done,
            "counts_per_cell": counts, "table": table, "degeneracy_check": degeneracy_check(rows),
            "spec_hash_dedup": dedup_by_spec_hash(live),
            "contrasts": "none computed here; G_joint_treatment_S11_minus_S00 and I are Harmonia's (block = target task, n = 12)",
            "h1_contrast_label": "transport_only (fresh vs random_pack); relevance inert at this scope (Harmonia 745d9c698)"}


def to_markdown(r: Dict[str, Any]) -> str:
    L = ["# H1/H0 phase-2 readout -- {}".format("COMPLETE" if r["complete"] else "PARTIAL"), "",
         "Written {}. Sets: {}. Numbers only; Harmonia analyses (block = target task, n = {}).".format(r["written"], ", ".join(r["sets"]), r["n_targets"]),
         "", "## Degeneracy check (second seed_root vs first, target 0, S00)", "",
         "- " + json.dumps(r["degeneracy_check"]), "", "## Spec-hash dedup (Harmonia 1b)", "",
         "- " + json.dumps(r["spec_hash_dedup"]), "", "## Counts per cell", ""]
    for c in CELLS:
        if c in r["counts_per_cell"]:
            L.append("- {}: {}".format(c, json.dumps(r["counts_per_cell"][c])))
    L += ["", "## Per task, per cell (kind status / solved / vm_ops)", ""]
    for rec in r["table"]:
        cells = []
        for c in CELLS:
            x = rec.get(c)
            if x is None:
                cells.append("{}: -".format(c))
            elif x["status"] != "completed":
                cells.append("{}: {}".format(c, x["status"].upper()))
            else:
                cells.append("{}: {}/{}/{}".format(c, x["kind_status"], "S" if x["solved"] else "-", x["vm_ops"]))
        L.append("- {}: {}".format(rec["task_id"], "; ".join(cells)))
    L += ["", "By set: {}".format(json.dumps(r["by_set"])), "", "H1 contrast label: {}".format(r["h1_contrast_label"]), ""]
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="archaeon.producer.h1h0_readout")
    ap.add_argument("--out", default="archaeon/docs/h0h5/H1H0_PHASE2_READOUT")
    a = ap.parse_args(argv)
    from evidence_wiki.ew import db as ewdb
    conn = ewdb.connect()
    try:
        rows = fetch(conn)
    finally:
        conn.close()
    r = readout(rows)
    with open(a.out + ".json", "w", encoding="utf-8") as f:
        json.dump(r, f, indent=1, sort_keys=True, default=str)
    with open(a.out + ".md", "w", encoding="utf-8") as f:
        f.write(to_markdown(r))
    print(json.dumps({"complete": r["complete"], "slot_free_complete": r["slot_free_complete"],
                      "degeneracy": r["degeneracy_check"].get("verdict"), "counts": r["counts_per_cell"]}, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
