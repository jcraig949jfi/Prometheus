#!/usr/bin/env python3
"""Reconcile one dispatch batch against Fabric (CWO 2026-09-30 ARTEMIS CURRENT).

usage: python3 roles/Artemis/dispatch/reconcile_batch.py BATCH [--fetch DIR]

Reads dispatch/BATCH/TASKS.json, asks Fabric for each Task's actual state, and writes
dispatch/BATCH/RECEIPTS.json: state, attempts (worker, host, exit, wall minutes), artifact
names/sizes/sha256, and whether the expected deliverables (out/REPORT.md, out/claims.json) came
back (Fabric names out/ files by basename). With --fetch, every artifact is downloaded to DIR/<alias>/ and its sha256 re-checked
against Fabric's record. Fabric is the source of truth; nothing here is inferred from STATE files.
"""
import hashlib, json, os, subprocess, sys
from datetime import UTC, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
EXPECTED = ("REPORT.md", "claims.json")  # Fabric stores out/ files by basename


def fabric(*args):
    r = subprocess.run([sys.executable, "-m", "fabric", *args], capture_output=True, text=True, timeout=120)
    if r.returncode:
        raise SystemExit(f"fabric {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def ts(s):
    return datetime.fromisoformat(s) if s else None


def main():
    batch = sys.argv[1]
    fetch = sys.argv[sys.argv.index("--fetch") + 1] if "--fetch" in sys.argv else None
    tasks = json.load(open(os.path.join(HERE, batch, "TASKS.json")))
    rows = []
    for alias, tid in tasks.items():
        t = json.loads(fabric("show", tid))
        atts = [{
            "attempt_id": a["attempt_id"], "agent": a["agent"], "host": a["host"], "model": a["model"],
            "status": a["status"], "exit_code": a["exit_code"], "error": a["error"],
            "base_sha": a["base_sha"], "started_at": a["started_at"], "ended_at": a["ended_at"],
            "wall_min": round((ts(a["ended_at"]) - ts(a["started_at"])).total_seconds() / 60, 1)
            if a["ended_at"] and a["started_at"] else None,
        } for a in t["attempts"]]
        arts = [{k: a[k] for k in ("artifact_id", "attempt_id", "name", "kind", "sha256", "size_bytes")}
                for a in t["artifacts"]]
        names = {a["name"] for a in arts}
        row = {
            "alias": alias, "task_id": tid, "thread_id": t["thread_id"], "state": t["state"],
            "attempts_made": t["attempts_made"], "base_sha": t["base_sha"],
            "terminal_at": t["terminal_at"], "error_summary": t["error_summary"],
            "deliverables": {e: e in names for e in EXPECTED},
            "attempts": atts, "artifacts": arts,
        }
        if fetch:
            d = os.path.join(fetch, alias)
            os.makedirs(d, exist_ok=True)
            bad = []
            for a in arts:
                out = os.path.join(d, a["name"].replace("/", "__"))
                fabric("get", a["artifact_id"], "--out", out)
                if hashlib.sha256(open(out, "rb").read()).hexdigest() != a["sha256"]:
                    bad.append(a["name"])
            row["fetch"] = {"dir": d, "sha256_mismatch": bad}
        rows.append(row)
    states = {}
    for r in rows:
        states[r["state"]] = states.get(r["state"], 0) + 1
    rec = {
        "schema": "artemis.dispatch_receipts.v1", "batch": batch,
        "reconciled_at_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%MZ"),
        "source": "python3 -m fabric show <task> (Fabric is authoritative)",
        "summary": {"n": len(rows), "states": states,
                    "all_deliverables": sum(all(r["deliverables"].values()) for r in rows)},
        "tasks": rows,
    }
    with open(os.path.join(HERE, batch, "RECEIPTS.json"), "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(json.dumps(rec["summary"]))


if __name__ == "__main__":
    main()
