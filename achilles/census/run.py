"""One census cycle (charter SCHEDULE steps 1-11). Entry point for the scheduled task.

    python -m achilles.census.run --publish-root <worktree> [--no-push] [--deep] [--state-dir DIR]

Code runs from a PINNED worktree (WORKING_CONTRACT s6); evidence is read from, and outputs are
committed in, a separate PUBLISH worktree that this cycle resets to origin/main (detached). The
canonical checkout is never touched (s1). Only Achilles's own paths are written:
    docs/fleet/{index.html, fleet_state.json, email_census.json, FLEET_CENSUS.md, run_status.json}
    roles/Achilles/census/runs/<YYYY-MM>.jsonl          (durable run receipts)

Failure never masquerades as success: on any error the snapshot and page are NOT replaced;
only run_status.json and the receipt are published, the page's own freshness check (computed in
the viewer's browser) turns the banner red, the mailer prints STALE, and one comms report is
posted at the start of a failure streak. Rule 10: after BOUND consecutive non-productive runs the
task parks itself (park record + schtasks /DISABLE + one comms message to the accountable seat).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import socket
import subprocess
import sys
import time
import traceback
from pathlib import Path

from . import build as B
from . import render as R
from . import sources as S
from . import util
from .util import iso, now_utc

OUT_DIR = "docs/fleet"
RUNS_DIR = "roles/Achilles/census/runs"
TASK_NAME = "PrometheusFleetCensus"
BOUND = 4                      # rule 10: consecutive non-productive runs before parking
ACCOUNTABLE = "Achilles"
AUTHOR = ["-c", "user.name=Achilles", "-c", "user.email=jcraig949jfi@users.noreply.github.com"]
CODE_ROOT = Path(__file__).resolve().parents[2]


def _assert_not_canonical(root: Path):
    """WORKING_CONTRACT s1: refuse to mutate a main worktree (git-dir == common-dir)."""
    g = util.Git(root)
    gd = Path(g.run("rev-parse", "--absolute-git-dir").strip()).resolve()
    cd = g.run("rev-parse", "--git-common-dir").strip()
    cdp = (root / cd).resolve() if not os.path.isabs(cd) else Path(cd).resolve()
    if gd == cdp:
        raise SystemExit("refusing to run: {} is the canonical checkout (main worktree)".format(root))


def _sync(git: util.Git):
    """Charter step 1: synchronise safely -- fetch, then hard-reset OUR publish worktree to origin/main."""
    git.run("fetch", "origin", "--prune", timeout=300)
    git.run("checkout", "-f", "--detach", "origin/main")
    git.run("clean", "-fdq", "--", OUT_DIR, RUNS_DIR)


def _write_outputs(root: Path, snap: dict, run_status: dict, receipt: dict, full: bool):
    out = root / OUT_DIR
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    if full:
        snap = json.loads(S.redact(json.dumps(snap, default=str)))
        util.write_json(out / "fleet_state.json", snap)
        (out / "index.html").write_text(R.render_html(snap), encoding="utf-8", newline="\n")
        util.write_json(out / "email_census.json", R.email_block(snap))
        (out / "FLEET_CENSUS.md").write_text(R.markdown_summary(snap), encoding="utf-8", newline="\n")
        paths += [OUT_DIR + "/" + n for n in ("fleet_state.json", "index.html", "email_census.json", "FLEET_CENSUS.md")]
    util.write_json(out / "run_status.json", run_status)
    paths.append(OUT_DIR + "/run_status.json")
    rdir = root / RUNS_DIR
    rdir.mkdir(parents=True, exist_ok=True)
    rfile = rdir / "{}.jsonl".format(receipt["started_utc"][:7])
    with open(rfile, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(receipt, default=str) + "\n")
    paths.append(RUNS_DIR + "/" + rfile.name)
    return paths


def _commit_push(git: util.Git, root: Path, paths: list, message: str, rewrite, attempts: int = 4) -> str:
    """Commit only our paths, push to main as a fast-forward; on rejection re-sync and re-apply."""
    for i in range(attempts):
        git.run("add", "--", *paths)
        msgf = root / ".git_census_msg"
        msgf.write_text(message, encoding="utf-8", newline="\n")
        try:
            git.run(*AUTHOR, "commit", "-q", "-F", str(msgf), "--", *paths)
        finally:
            msgf.unlink(missing_ok=True)
        sha = git.run("rev-parse", "HEAD").strip()
        r = subprocess.run(["git", "-C", str(root), "push", "origin", "HEAD:refs/heads/main"], capture_output=True,
                           text=True, timeout=300)
        if r.returncode == 0:
            git.run("fetch", "origin", timeout=300)
            if not git.ok("merge-base", "--is-ancestor", sha, "origin/main"):
                raise RuntimeError("pushed {} but it is not an ancestor of origin/main".format(sha))
            return sha
        if i == attempts - 1:
            raise RuntimeError("push rejected {} times: {}".format(attempts, r.stderr.strip()[:300]))
        time.sleep(5 + 10 * i)
        _sync(git)       # origin moved: start again from the new tip; our files are wholly ours
        paths = rewrite()
    raise RuntimeError("unreachable")


def _post_comms(repo_root: Path, subject: str, body: str, to: str = ACCOUNTABLE):
    """One comms report (failure-streak start or park). Best effort; the page and email are the loud path."""
    try:
        bf = Path(os.environ.get("TEMP", "/tmp")) / "achilles_census_msg.txt"
        bf.write_text(body, encoding="utf-8")
        subprocess.run([sys.executable, "-m", "comms", "post", "--from", "Achilles", "--to", to, "--kind", "report",
                        "--subject", subject, "--body-file", str(bf)], cwd=str(repo_root), timeout=120,
                       capture_output=True)
    except Exception:
        pass


def _park(state_dir: Path, state: dict, reason: str, repo_root: Path):
    rec = {"parked_at_utc": iso(now_utc()), "reason": reason, "consecutive_nonproductive": state.get("consecutive_nonproductive"),
           "task": TASK_NAME, "resume": "delete this park record after fixing the cause, then re-enable the task"}
    util.write_json(state_dir / "PARKED.json", rec)
    subprocess.run(["schtasks", "/Change", "/TN", TASK_NAME, "/DISABLE"], capture_output=True)
    _post_comms(repo_root, "Achilles fleet census PARKED after {} non-productive runs".format(BOUND), json.dumps(rec, indent=1))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--publish-root", required=True, type=Path)
    ap.add_argument("--state-dir", type=Path, default=None)
    ap.add_argument("--no-push", action="store_true", help="build and write outputs, do not commit or push")
    ap.add_argument("--no-sync", action="store_true", help="do not fetch/reset the publish worktree (tests)")
    ap.add_argument("--deep", action="store_true", help="force a full-history reconciliation")
    a = ap.parse_args(argv)
    root = a.publish_root.resolve()
    state_dir = (a.state_dir or (root.parent / "achilles-census-state")).resolve()
    state_dir.mkdir(parents=True, exist_ok=True)
    state = util.read_json(state_dir / "state.json", {}) or {}
    if (state_dir / "PARKED.json").exists():
        print("PARKED: {} -- not running (rule 10; clear the park record to resume)".format(state_dir / "PARKED.json"))
        return 3

    started = now_utc()
    run_id = started.strftime("%Y%m%dT%H%M%SZ")
    git = util.Git(root)
    code_git = util.Git(CODE_ROOT)
    receipt = {"run_id": run_id, "started_utc": iso(started), "host": socket.gethostname(),
               "code_root": str(CODE_ROOT), "code_sha": code_git.run("rev-parse", "HEAD", check=False).strip(),
               "publish_root": str(root), "status": "STARTED"}
    prev_run = util.read_json(root / OUT_DIR / "run_status.json", {}) or {}
    snap = None
    try:
        _assert_not_canonical(root)
        if not a.no_sync:
            _sync(git)
        receipt["base_sha"] = git.run("rev-parse", "origin/main").strip()
        prev = util.read_json(root / OUT_DIR / "fleet_state.json")
        conn, err = util.db_connect_readonly(root)
        run_info = {"run_id": run_id, "host": receipt["host"], "last_attempted_utc": iso(started),
                    "last_successful_utc": iso(started), "status": "SUCCESS", "error": None,
                    "code_sha": receipt["code_sha"], "schedule": "every 6 hours ({} on ELSA)".format(TASK_NAME)}
        snap = B.build(root, prev, conn, err, started, run_info, force_deep=a.deep)
        if conn is not None:
            conn.close()
        finished = now_utc()
        run_info["duration_s"] = round((finished - started).total_seconds(), 1)
        s = snap["summary"]
        productive = (prev is None) or ((prev or {}).get("base_sha") != snap["base_sha"]) or \
            (((prev or {}).get("cursors") or {}).get("comms_max_id") != snap["cursors"]["comms_max_id"])
        run_status = {"schema": "prometheus.fleet_census_run.v1", "last_attempted_utc": iso(started),
                      "last_successful_utc": iso(started), "last_status": "SUCCESS", "last_error": None,
                      "last_input_at": snap["base_sha"], "last_success_at": iso(finished),
                      "productive": productive, "mode": snap["stats"]["mode"], "seats": s["seats_total"],
                      "schedule": run_info["schedule"], "bound": BOUND, "accountable_seat": ACCOUNTABLE}
        receipt.update({"status": "SUCCESS", "finished_utc": iso(finished), "mode": snap["stats"]["mode"],
                        "commits_scanned": snap["stats"].get("commits_scanned"), "seats": s["seats_total"],
                        "entities": s["entities_total"], "counts": s["counts_by_state"], "anomalies": len(snap["anomalies"]),
                        "sources": snap["sources_status"], "productive": productive})
        def rewrite():
            return _write_outputs(root, snap, run_status, receipt, full=True)
        paths = rewrite()
        if not a.no_push:
            counts = ", ".join("{} {}".format(k, v) for k, v in sorted(s["counts_by_state"].items()))
            msg = ("Achilles[census]: fleet census {} -- {} seats ({}); {} anomalies; {} mode\n\n"
                   "Built from origin/main {} by {} (code {}). Snapshot docs/fleet/fleet_state.json; page "
                   "docs/fleet/index.html; email block docs/fleet/email_census.json; receipt {}.\n").format(
                iso(started), s["seats_total"], counts, len(snap["anomalies"]), snap["stats"]["mode"],
                receipt["base_sha"][:10], receipt["host"], receipt["code_sha"][:10], RUNS_DIR)
            receipt["publish_sha"] = _commit_push(git, root, paths, msg, rewrite)
        state.update({"last_success_at": iso(finished), "last_input_at": receipt["base_sha"], "last_error": None,
                      "failure_streak": 0,
                      "consecutive_nonproductive": 0 if productive else int(state.get("consecutive_nonproductive", 0)) + 1})
        util.write_json(state_dir / "state.json", state)
        print("census OK {} seats={} mode={} publish={}".format(run_id, s["seats_total"], snap["stats"]["mode"],
                                                              receipt.get("publish_sha", "(not pushed)")))
        if state["consecutive_nonproductive"] >= BOUND:
            _park(state_dir, state, "{} consecutive runs with no upstream change (origin/main and comms both still)".format(BOUND), root)
        return 0
    except Exception as e:
        err = "{}: {}".format(type(e).__name__, str(e)[:400])
        tb = traceback.format_exc()[-1500:]
        finished = now_utc()
        receipt.update({"status": "FAILED", "finished_utc": iso(finished), "error": err})
        run_status = {"schema": "prometheus.fleet_census_run.v1", "last_attempted_utc": iso(started),
                      "last_successful_utc": prev_run.get("last_successful_utc"), "last_status": "FAILED",
                      "last_error": err, "bound": BOUND, "accountable_seat": ACCOUNTABLE}
        streak = int(state.get("failure_streak", 0)) + 1
        state.update({"last_error": err, "last_failure_at": iso(finished), "failure_streak": streak,
                      "consecutive_nonproductive": int(state.get("consecutive_nonproductive", 0)) + 1})
        util.write_json(state_dir / "state.json", state)
        (state_dir / "last_failure.txt").write_text(tb, encoding="utf-8")
        print("census FAILED {}: {}".format(run_id, err), file=sys.stderr)
        if not a.no_push:
            try:
                if not a.no_sync:
                    _sync(git)
                paths = _write_outputs(root, None, run_status, receipt, full=False)
                _commit_push(git, root, paths, "Achilles[census]: census run FAILED {} -- {}\n".format(run_id, err[:200]),
                             lambda: _write_outputs(root, None, run_status, receipt, full=False))
            except Exception as e2:
                print("could not publish the failure record: {}".format(e2), file=sys.stderr)
        if streak == 1:
            _post_comms(root, "Achilles fleet census FAILED {}".format(run_id), "{}\n\n{}".format(err, tb))
        if state["consecutive_nonproductive"] >= BOUND:
            _park(state_dir, state, "{} consecutive non-productive runs; last error {}".format(BOUND, err), root)
        return 1


if __name__ == "__main__":
    sys.exit(main())
