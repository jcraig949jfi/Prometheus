"""Reconcile a set of queue rows across every surface they touched.

    python tools/reconcile_rows.py --se experiment=<prereg id> [--se treatment=..]
                                   [--request-key-prefix rk-fc-] [--ids a,b,c]
                                   [--sfe-db D:/Prometheus-data/sfe/engine.db]
                                   [--json out.json]

For each selected row (viv.research_experiment_queue) it reads, from the
SURFACE THAT OWNS THE FACT and never from the consumer's log:

    queue      status, created/claimed/started/finished, claimed_by, the
               event sequence and the number of 'claimed' events
    set        candidate_set_id, membership count, alternatives recorded
    SFE        world / experiment / observation / work item for the row's
               sfe_experiment_id, the experiment count in that world, the
               engine identity + conformance state stamped on the row
               (sqlite, mode=ro, on the ledger path given)
    PEW        the encounter row behind pew_reference (ew.fossil_encounters)
               and whether its producer.queue.experiment_id points back
    outcome    result_summary.outcome, or the typed failure class + error

and then the integrity questions the operator asked (2026-09-12): missing
(rows selected but not terminal), duplicates (same spec_hash executed more
than once inside the set), retries (SFE work attempts > 1), parks (records
in the worker's var dir), refusals (none can appear here by design -- a
refused append leaves no row), contamination (rows in the execution window
that are NOT in the set), and the engine-build boundary (distinct
engine_source_hash values across the set, in execution order).

This tool DECIDES nothing. It prints what happened to the rows it was
given and which of them it could not tie together.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sqlite3
import sys
from pathlib import Path

VIVARIUM = Path(__file__).resolve().parent.parent
if str(VIVARIUM) not in sys.path:
    sys.path.insert(0, str(VIVARIUM))

from viv import db as _db                                          # noqa: E402
from viv import daemon as _daemon                                  # noqa: E402
from viv import vardir as _vardir                                  # noqa: E402

Q = "viv.research_experiment_queue"
E = "viv.research_experiment_events"


def _select(cur, args):
    where, params = [], []
    for kv in args.se or ():
        k, _, v = kv.partition("=")
        where.append("source_evidence->>%s = %s"); params += [k, v]
    if args.request_key_prefix:
        where.append("request_key LIKE %s"); params.append(args.request_key_prefix + "%")
    if args.ids:
        where.append("experiment_id = ANY(%s::uuid[])"); params.append(args.ids.split(","))
    if not where:
        raise SystemExit("select rows with --se key=value, --request-key-prefix or --ids")
    cur.execute("SELECT experiment_id, status, created_by, source_reason, candidate_set_id, request_key, "
                "family_id, arm_id, created_at, claimed_at, started_at, finished_at, claimed_by, "
                "sfe_experiment_id, pew_reference, spec_hash, priority, error, result_summary, "
                "source_evidence, experiment_spec->'work'->>'kind' FROM " + Q +
                " WHERE " + " AND ".join(where) + " ORDER BY created_at", params)
    cols = ["experiment_id", "status", "created_by", "source_reason", "candidate_set_id", "request_key",
            "family_id", "arm_id", "created_at", "claimed_at", "started_at", "finished_at", "claimed_by",
            "sfe_experiment_id", "pew_reference", "spec_hash", "priority", "error", "result_summary",
            "source_evidence", "kind"]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def _events(cur, eid):
    cur.execute("SELECT event_type, occurred_at, actor FROM " + E + " WHERE experiment_id=%s ORDER BY event_id", (eid,))
    return [(t, o.isoformat(), a) for t, o, a in cur.fetchall()]


def _members(cur, csid):
    if not csid:
        return None
    cur.execute("SELECT count(*) FROM " + Q + " WHERE candidate_set_id=%s", (csid,))
    return cur.fetchone()[0]


def _pew(cur, ref):
    if not ref:
        return None
    enc = ref.split("/", 1)[1].split(":")[0] if "/" in ref else None
    cur.execute("SELECT encounter_id, outcome, namespace, sfe_world_id, run_id, sfe_event_id, created_at, "
                "producer->'queue'->>'experiment_id' FROM ew.fossil_encounters WHERE encounter_id=%s", (enc,))
    r = cur.fetchone()
    if not r:
        return {"encounter_id": enc, "found": False}
    return {"encounter_id": r[0], "found": True, "outcome": r[1], "namespace": r[2], "sfe_world_id": r[3],
            "run_id": r[4], "sfe_event_id": r[5], "created_at": r[6].isoformat(), "points_back_to": r[7]}


def _sfe(scur, exp_id):
    if not exp_id or scur is None:
        return None
    scur.execute("SELECT exp_id, world_id, state, spec_hash, work_id FROM experiments WHERE exp_id=?", (exp_id,))
    e = scur.fetchone()
    if not e:
        return {"exp_id": exp_id, "found": False}
    wid = e[1]
    scur.execute("SELECT name, state, client_id FROM worlds WHERE world_id=?", (wid,)); w = scur.fetchone()
    scur.execute("SELECT count(*), sum(state='OBSERVED') FROM experiments WHERE world_id=?", (wid,)); n = scur.fetchone()
    scur.execute("SELECT obs_id, outcome, evidence_role FROM observations WHERE exp_id=? ORDER BY created_ts", (exp_id,)); obs = scur.fetchall()
    scur.execute("SELECT status, attempts, claimed_by FROM work_items WHERE work_id=?", (e[4],)); wk = scur.fetchone()
    return {"exp_id": e[0], "found": True, "world_id": wid, "world_name": w[0] if w else None,
            "world_state": w[1] if w else None, "world_client": w[2] if w else None,
            "exp_state": e[2], "spec_hash": e[3],
            "experiments_in_world": n[0], "observed_in_world": n[1],
            "observations": [{"obs_id": o[0], "outcome": o[1], "role": o[2]} for o in obs],
            "work": {"work_id": e[4], "status": wk[0] if wk else None, "attempts": wk[1] if wk else None,
                     "claimed_by": wk[2] if wk else None}}


def reconcile(args):
    conn = _db.connect(); cur = conn.cursor()
    scur = None
    sfe_db = args.sfe_db or os.environ.get("VIV_SFE_DB")
    if sfe_db and Path(sfe_db).exists():
        scur = sqlite3.connect("file:%s?mode=ro" % str(sfe_db).replace("\\", "/"), uri=True).cursor()
    rows = _select(cur, args)
    out = {"schema": "viv.reconcile.v1", "at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
           "selection": {"se": args.se, "request_key_prefix": args.request_key_prefix, "ids": args.ids},
           "sfe_db": sfe_db if scur else None, "rows": []}
    for r in rows:
        rs = r["result_summary"] or {}
        sel = rs.get("selection") or {}
        ev = _events(cur, r["experiment_id"])
        rec = {
            "experiment_id": str(r["experiment_id"]), "status": r["status"], "kind": r["kind"],
            "created_by": r["created_by"], "source_reason": r["source_reason"],
            "request_key": r["request_key"], "family_id": r["family_id"], "arm_id": r["arm_id"],
            "treatment": (r["source_evidence"] or {}).get("treatment"),
            "pair": (r["source_evidence"] or {}).get("pair"),
            "experiment": (r["source_evidence"] or {}).get("experiment"),
            "spec_hash": r["spec_hash"], "priority": r["priority"],
            "transitions": {k: (r[k].isoformat() if r[k] else None)
                            for k in ("created_at", "claimed_at", "started_at", "finished_at")},
            "claimed_by": r["claimed_by"],
            "events": ev, "claim_events": sum(1 for t, _, _ in ev if t == "claimed"),
            "candidate_set_id": r["candidate_set_id"], "set_members": _members(cur, r["candidate_set_id"]),
            "alternatives_recorded": (len(sel.get("alternatives", [])) if isinstance(sel.get("alternatives"), list)
                                      else sel.get("alternatives_recorded")),
            "selection_bound": sel.get("bound"), "selection_family": sel.get("family_id"),
            "sfe_experiment_id": r["sfe_experiment_id"],
            "sfe": _sfe(scur, r["sfe_experiment_id"]),
            "engine": rs.get("engine"), "conformance_state": (rs.get("conformance") or {}).get("state"),
            "pew_reference": r["pew_reference"], "pew": _pew(cur, r["pew_reference"]),
            "outcome": rs.get("outcome"),
            "failure": ({"class": (r["error"] or "").split(":", 1)[0], "error": (r["error"] or "")[:300]}
                        if r["status"] == "failed" else None),
        }
        rec["ties"] = {
            "spec_hash_matches_engine": bool(rec["sfe"] and rec["sfe"].get("found") and rec["sfe"]["spec_hash"] == r["spec_hash"]),
            "pew_points_back": bool(rec["pew"] and rec["pew"].get("found") and rec["pew"]["points_back_to"] == str(r["experiment_id"])),
            "one_experiment_in_world": bool(rec["sfe"] and rec["sfe"].get("found") and rec["sfe"]["experiments_in_world"] == 1),
        }
        out["rows"].append(rec)

    # ---- integrity over the set
    order = sorted(out["rows"], key=lambda x: x["transitions"]["claimed_at"] or "9")
    hashes = [x["spec_hash"] for x in out["rows"]]
    engine_hashes = []
    for x in order:
        h = (x["engine"] or {}).get("engine_source_hash")
        if h and (not engine_hashes or engine_hashes[-1] != h):
            engine_hashes.append(h)
    window = [x["transitions"]["claimed_at"] for x in out["rows"] if x["transitions"]["claimed_at"]]
    contamination = []
    if window:
        lo, hi = min(window), max(window)
        ids = [x["experiment_id"] for x in out["rows"]]
        cur.execute("SELECT experiment_id, created_by, request_key, status, claimed_at FROM " + Q +
                    " WHERE claimed_at BETWEEN %s AND %s AND NOT (experiment_id = ANY(%s::uuid[])) ORDER BY claimed_at",
                    (lo, hi, ids))
        contamination = [{"experiment_id": str(a), "created_by": b, "request_key": c, "status": d,
                          "claimed_at": e.isoformat()} for a, b, c, d, e in cur.fetchall()]
    parks = []
    try:
        var = _vardir.resolve(_db.load_config(), create=False)
        parks = sorted(p.name for p in var.glob("park-*"))
    except Exception:                                               # noqa: BLE001
        pass
    out["integrity"] = {
        "selected": len(out["rows"]),
        "terminal": sum(1 for x in out["rows"] if x["status"] in ("completed", "failed", "cancelled")),
        "missing_not_terminal": [x["experiment_id"] for x in out["rows"] if x["status"] not in ("completed", "failed", "cancelled")],
        "duplicates_spec_hash_executed_twice": sorted({h for h in hashes if hashes.count(h) > 1
                                                       and sum(1 for x in out["rows"] if x["spec_hash"] == h and x["status"] == "completed") > 1}),
        "retries_attempts_gt_1": [x["experiment_id"] for x in out["rows"] if x["sfe"] and x["sfe"].get("found") and (x["sfe"]["work"]["attempts"] or 0) > 1],
        "multi_claim": [x["experiment_id"] for x in out["rows"] if x["claim_events"] > 1],
        "alternatives_nonzero": [x["experiment_id"] for x in out["rows"] if (x["alternatives_recorded"] or 0) > 0],
        "parks_in_var_dir": parks,
        "refusals": "not observable here by design: a refused candidate_set append leaves no row; the writer holds the typed exception",
        "contamination_rows_claimed_inside_window_not_in_set": contamination,
        "execution_order": [x["experiment_id"] for x in order],
        "engine_hashes_in_execution_order": engine_hashes,
        "build_boundary_crossed": len(engine_hashes) > 1,
        "ties_failed": [x["experiment_id"] for x in out["rows"] if not all(x["ties"].values())],
    }
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--se", action="append", help="source_evidence key=value (repeatable)")
    ap.add_argument("--request-key-prefix")
    ap.add_argument("--ids", help="comma-separated experiment_ids")
    ap.add_argument("--sfe-db", help="engine ledger path (read-only); or VIV_SFE_DB")
    ap.add_argument("--json", help="write the full record here")
    args = ap.parse_args(argv)
    out = reconcile(args)
    if args.json:
        Path(args.json).write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    for x in out["rows"]:
        print("%s %-9s %-7s %-22s cs=%s members=%s alts=%s sfe=%s exp_in_world=%s pew=%s outcome=%s fail=%s ties=%s"
              % (x["experiment_id"][:8], x["status"], x["created_by"], (x["request_key"] or "")[:22],
                 (x["candidate_set_id"] or "-")[:14], x["set_members"], x["alternatives_recorded"],
                 (x["sfe"] or {}).get("exp_state"), (x["sfe"] or {}).get("experiments_in_world"),
                 (x["pew"] or {}).get("found"), x["outcome"], (x["failure"] or {}).get("class"),
                 "ok" if all(x["ties"].values()) else x["ties"]))
    print(json.dumps(out["integrity"], indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
