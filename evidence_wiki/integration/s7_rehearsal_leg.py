"""S7 -- PEW's leg of the Campaign 4 rehearsal (archaeon/campaign4/REHEARSAL_PLAN.md;
closure order 2026-09-17, Prompt 4 / Mnemosyne). One command, one receipt.

    python integration/s7_rehearsal_leg.py [--commit <sha>] [--precheck]

Steps (each a gate in the receipt):
    I1  ingest --campaign 4 at <commit>: the reader accepts the directory and
        lands every campaign-4 row it finds (shared tables included)
    I2  ingest again: 0 new, 0 conflicts (replay / idempotence)
    I3  campaign-4 rows exist (source_path under archaeon/campaign4/) --
        SKIPPED in --precheck (no artifacts yet), FAIL otherwise
    R1  rebuild-check reach_level v1, reach_level v0, corridor_edge v1: equal,
        and unchanged from the frozen point-release digests
    C1  campaign_release_check: all gates pass on the deployed service
    F1  the frozen surface test passes (the pinned identities still equal
        the code that just ran)
    X1  reconcile with Vivarium: ingestion checkpoint for vivarium@m2 /
        viv.execution.v1 (last_seq, gaps, duplicate_seqs, rows) -- reported,
        not gated (advisory backlog per the launch policy)

Receipt: integration/s7_rehearsal_results.json (pass/fail per gate,
counts, digests, commit, reader/builder versions). Archaeon's P4 may point
at this file: `present` := the file exists and all gates that are not
SKIP pass. Run from a task worktree; never from the pinned one.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
R = []
FROZEN_DIGESTS = {"reach_level/v1": "e7625bfb967f7015151ddd73943b8f63ee6d1f6a1f15fbb0a5ea1db12946a1b9",
                  "reach_level/v0": "7037fbc41aff4f7d89b681b1d695b71b4b2cc820075eeb30b2a10657bc1cb0c2",
                  "corridor_edge/v1": "719fa5a1ec6f4045a1d8c6b17082e7dad79e7aa0d08afdea6c53a5579dda4ca7"}


def gate(name, ok, detail, skipped=False):
    R.append({"gate": name, "pass": bool(ok), "skipped": skipped, "detail": detail})
    print(f"[{'SKIP' if skipped else ('PASS' if ok else 'FAIL')}] {name}: {detail}")
    return bool(ok)


def run(cmd, timeout=1800):
    env = dict(os.environ)
    env.setdefault("EW_DB_HOST", "192.168.1.202")
    env.setdefault("PROMETHEUS_MACHINE", "M2")
    return subprocess.run(cmd, cwd=str(HERE), capture_output=True, text=True, timeout=timeout, env=env)


def ingest(commit, tag):
    rcpt = HERE / "derived" / f"s7_ingest_{tag}.json"
    rcpt.parent.mkdir(exist_ok=True)
    r = run([sys.executable, "-m", "ew.campaign_ingest", "--campaign", "4", "--commit", commit, "--receipt", str(rcpt)])
    if r.returncode != 0 or not rcpt.exists():
        return None, (r.stderr or r.stdout)[-400:]
    return json.loads(rcpt.read_text(encoding="utf-8")), None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", default=None)
    ap.add_argument("--precheck", action="store_true", help="no campaign-4 artifacts expected yet")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8377)
    a = ap.parse_args()
    t0 = time.time()
    commit = a.commit or run(["git", "rev-parse", "origin/main"]).stdout.strip()

    j1, err = ingest(commit, "run1")
    gate("I1_ingest_campaign4", j1 is not None,
         f"commit {commit[:9]} reader {j1['reader_version'] if j1 else '?'} seen {j1['result']['seen'] if j1 else '?'} "
         f"new {j1['result']['new'] if j1 else '?'} conflicts {j1['result']['conflicts'] if j1 else '?'} {err or ''}")
    j2, err2 = ingest(commit, "run2")
    gate("I2_second_ingest_idempotent", j2 is not None and j2["result"]["new"] == 0 and j2["result"]["conflicts"] == 0,
         f"seen {j2['result']['seen'] if j2 else '?'} new {j2['result']['new'] if j2 else '?'} conflicts {j2['result']['conflicts'] if j2 else '?'} {err2 or ''}")

    from ew import db as ewdb
    conn = ewdb.connect(); cur = conn.cursor()
    cur.execute("SELECT count(*), count(DISTINCT harness_id), count(DISTINCT attempt_id) FROM ew.campaign_observations "
                "WHERE campaign_id='cmp4' AND source_path LIKE 'archaeon/campaign4/%%'")
    n4, h4, a4 = cur.fetchone()
    cur.execute("SELECT kind, count(*) FROM ew.campaign_observations WHERE campaign_id='cmp4' AND source_path LIKE 'archaeon/campaign4/%%' GROUP BY 1 ORDER BY 1")
    kinds4 = dict(cur.fetchall())
    if a.precheck:
        gate("I3_campaign4_rows_present", True, f"precheck: {n4} campaign-4 rows (none expected yet); reader accepts the directory", skipped=True)
    else:
        gate("I3_campaign4_rows_present", n4 > 0, f"{n4} rows from archaeon/campaign4/ ({h4} harnesses, {a4} attempts) kinds={kinds4}")

    digests = {}
    ok_all = True
    for name, ver in (("reach_level", "v1"), ("reach_level", "v0"), ("corridor_edge", "v1")):
        r = run([sys.executable, "-m", "ew.projections", "rebuild-check", name, ver])
        try:
            j = json.loads(r.stdout[r.stdout.index("{"):])
        except Exception:
            j = {"rebuild_equal": False, "rebuild_digest": None}
        digests[f"{name}/{ver}"] = j.get("rebuild_digest")
        ok_all = ok_all and j.get("rebuild_equal") and j.get("rebuild_digest") == FROZEN_DIGESTS[f"{name}/{ver}"]
    gate("R1_rebuild_equal_and_unchanged_from_frozen", ok_all,
         json.dumps({k: (v[:12] if v else None) for k, v in digests.items()}))

    r = run([sys.executable, "integration/campaign_release_check.py", "--machine", "M2", "--host", a.host, "--port", str(a.port)])
    try:
        rel = json.loads((HERE / "integration" / "campaign_release_results.json").read_text(encoding="utf-8"))
        gate("C1_release_check", rel["all_pass"] and r.returncode == 0,
             f"{sum(1 for g in rel['gates'] if g['pass'])}/{len(rel['gates'])} failed={[g['gate'] for g in rel['gates'] if not g['pass']]}")
    except Exception as e:
        gate("C1_release_check", False, f"no results: {e}")

    r = run([sys.executable, "-m", "pytest", "tests/test_frozen_surface.py", "-q"])
    gate("F1_frozen_surface_holds", r.returncode == 0, (r.stdout.strip().splitlines() or ["?"])[-1])

    cur.execute("SELECT last_seq, rows_seen, rows_new, gaps, duplicate_seqs, updated_at FROM ew.ingestion_checkpoints "
                "WHERE producer='vivarium@m2' AND stream='viv.execution.v1'")
    cp = cur.fetchone()
    cur.execute("SELECT count(*) FROM ew.producer_events WHERE producer='vivarium@m2' AND stream='viv.execution.v1'")
    nev = cur.fetchone()[0]
    outbox = {"checkpoint": None if cp is None else {"last_seq": cp[0], "rows_seen": cp[1], "rows_new": cp[2], "gaps": cp[3],
                                                     "duplicate_seqs": cp[4], "updated_at": str(cp[5])}, "events_stored": nev}
    gate("X1_vivarium_outbox_reconciliation", True, json.dumps(outbox), skipped=(cp is None))
    conn.close()

    ok = all(g["pass"] for g in R if not g["skipped"])
    out = {"stage": "S7", "all_pass": ok, "precheck": a.precheck, "commit": commit,
           "reader_version": j1["reader_version"] if j1 else None,
           "ingest_run1": j1["result"] if j1 else None, "ingest_run2": j2["result"] if j2 else None,
           "campaign4_rows": {"n": n4, "harnesses": h4, "attempts": a4, "kinds": kinds4},
           "rebuild_digests": digests, "frozen_digests": FROZEN_DIGESTS, "vivarium_outbox": outbox,
           "ran_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "seconds": round(time.time() - t0, 1), "gates": R}
    (HERE / "integration" / "s7_rehearsal_results.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(json.dumps({"all_pass": ok, "precheck": a.precheck, "campaign4_rows": n4, "seconds": out["seconds"]}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
