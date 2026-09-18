"""One weekly pass of Aphrodite's bounded RSI news monitor (run by the scheduled task).

Runs from a PINNED worktree (WORKING_CONTRACT s6). Writes happen in a
separate service worktree reset to origin/main each pass; the model runs
in a scratch directory holding only a library snapshot and never touches
the repository. Commits explicit paths, pushes, verifies the ancestor.

    python run_news_pass.py            one pass
    python run_news_pass.py --dry-run  everything except the model call,
                                       the commit and the comms post
"""
from __future__ import annotations

import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import monitor as MON  # noqa: E402

REL = Path("roles/Aphrodite/monitors/news")
LIB = Path("roles/Aphrodite/library")
NOWIN = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW (M4 windowless rule)
IDENT = {"GIT_AUTHOR_NAME": "James Craig", "GIT_AUTHOR_EMAIL": "jcraig949jfi@users.noreply.github.com",
         "GIT_COMMITTER_NAME": "James Craig", "GIT_COMMITTER_EMAIL": "jcraig949jfi@users.noreply.github.com"}
ENV = dict(os.environ, EW_DB_HOST="192.168.1.202", **IDENT)
DRY = "--dry-run" in sys.argv


def sh(args, cwd=None, timeout=900, check=True):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=ENV,
                       creationflags=NOWIN)
    if check and r.returncode != 0:
        raise RuntimeError(f"{args[:3]} failed: {r.stderr[-800:]}")
    return r


def log(msg):
    d = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "PrometheusAphroditeNews"
    d.mkdir(parents=True, exist_ok=True)
    with open(d / "monitor.log", "a", encoding="utf-8") as fh:
        fh.write(f"{dt.datetime.now(dt.timezone.utc).isoformat()} {msg}\n")


def main():
    now = dt.datetime.now(dt.timezone.utc)
    today = now.date()
    common = Path(sh(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=HERE).stdout.strip())
    canonical = common.parent
    service = HERE.parents[3].parent / "aphrodite-news-service"  # sibling of the pinned worktree
    sh(["git", "fetch", "origin"], cwd=canonical)
    if not service.exists():
        sh(["git", "worktree", "add", "--detach", str(service), "origin/main"], cwd=canonical, timeout=3600)
    sh(["git", "fetch", "origin"], cwd=service)
    sh(["git", "switch", "--discard-changes", "-C", "aphrodite/news-pass", "origin/main"], cwd=service, timeout=3600)
    base_sha = sh(["git", "rev-parse", "HEAD"], cwd=service).stdout.strip()

    mdir, lib = service / REL, service / LIB
    state = MON.load_json(mdir / "state.json", {})
    changed = []

    if state.get("paused"):
        if not state.get("pause_reported") and not DRY:
            report_pause(service, mdir, state)
            state["pause_reported"] = True
            write_json(mdir / "state.json", state)
            changed.append(mdir / "state.json")
            commit(service, changed, f"Aphrodite news monitor: pause reported once (paused {state.get('paused_at')})")
        log("PAUSED; no pass run (resumes only on explicit clearance)")
        return

    # scratch pass directory with a read-only library snapshot
    pdir = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "PrometheusAphroditeNews" / today.isoformat()
    if pdir.exists():
        shutil.rmtree(pdir)
    pdir.mkdir(parents=True)
    for f in ("NEWS.md", "THEORIES.md", "QUESTIONS.md"):
        shutil.copy(lib / f, pdir / f)
    designs = []
    for p in sorted((lib / "designs").glob("*.md")):
        head = p.read_text(encoding="utf-8", errors="replace").split("## 1.")[0][:1500]
        designs.append(f"=== {p.name}\n{head}\n")
    (pdir / "DESIGNS.txt").write_text("\n".join(designs), encoding="utf-8")
    keys = MON.library_keys(lib)
    (pdir / "DEDUPE_KEYS.txt").write_text("\n".join(sorted(keys)), encoding="utf-8")
    since = state.get("last_pass_at", "")[:10] or (today - dt.timedelta(days=7)).isoformat()
    prompt = (mdir / "PROMPT.md").read_text(encoding="utf-8")
    for k, v in {"{DATE}": today.isoformat(), "{SINCE}": since, "{MAX_INSPECT}": str(MON.MAX_INSPECT),
                 "{MAX_ADMIT}": str(MON.MAX_ADMIT)}.items():
        prompt = prompt.replace(k, v)

    ok, err = True, ""
    if DRY:
        (pdir / "pass_output.json").write_text(json.dumps({"pass_date": today.isoformat(), "searches_ok": True,
                                                           "queries": [], "candidates": []}), encoding="utf-8")
    else:
        try:
            r = subprocess.run(["claude", "-p", prompt, "--allowedTools", "WebSearch", "WebFetch", "Read", "Write",
                                "--output-format", "json", "--no-session-persistence"],
                               cwd=pdir, capture_output=True, text=True, timeout=2700, creationflags=NOWIN)
            (pdir / "claude_stdout.json").write_text(r.stdout or "", encoding="utf-8")
            if r.returncode != 0:
                ok, err = False, f"claude exit {r.returncode}: {(r.stderr or '')[-300:]}"
        except Exception as e:  # noqa: BLE001 -- a failed pass is recorded, never hidden
            ok, err = False, f"claude failed: {e!r}"
    try:
        out = json.loads((pdir / "pass_output.json").read_text(encoding="utf-8"))
        ok = ok and bool(out.get("searches_ok", False))
    except Exception as e:  # noqa: BLE001
        out, ok, err = {"candidates": []}, False, (err or f"no valid pass_output.json: {e!r}")

    res = MON.validate(out, keys, MON.library_targets(lib))
    old = MON.load_json(mdir / "candidates.json", [])
    known = {c["dedupe_key"] for c in old}
    for c in res["candidates"]:
        if c["dedupe_key"] and c["dedupe_key"] not in known:
            c["first_seen"] = today.isoformat()
            old.append(c)
    cands, expired = MON.expire(old, today)
    state = MON.step_state(state, len(res["admitted"]), now.isoformat(), ok)

    record = {"pass_at": now.isoformat(), "base_sha": base_sha, "ok": ok, "error": err,
              "queries": out.get("queries", []), "inspected": len(out.get("candidates") or []),
              "admitted": [c["dedupe_key"] for c in res["admitted"]], "violations": res["violations"],
              "candidates_kept": len(cands), "expired": expired,
              "consecutive_empty": state["consecutive_empty"], "paused": state.get("paused", False)}
    if res["admitted"]:
        with open(lib / "NEWS.md", "a", encoding="utf-8", newline="\n") as fh:
            fh.write(MON.news_block(res["admitted"], today.isoformat()))
        changed.append(lib / "NEWS.md")
    write_json(mdir / "candidates.json", cands)
    with open(mdir / "passes.jsonl", "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")
    if state.get("paused") and not state.get("pause_reported") and not DRY:
        report_pause(service, mdir, state)
        state["pause_reported"] = True
        changed.append(mdir / "PARKED.md")
    write_json(mdir / "state.json", state)
    changed += [mdir / "candidates.json", mdir / "passes.jsonl", mdir / "state.json"]
    log(json.dumps(record))
    if DRY:
        print(json.dumps(record, indent=1))
        return
    commit(service, changed, f"Aphrodite news monitor pass {today}: {len(res['admitted'])} admitted, "
                             f"{record['inspected']} inspected, empty streak {state['consecutive_empty']}")


def write_json(p: Path, obj):
    p.write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def report_pause(service: Path, mdir: Path, state):
    body = mdir / "PARKED.md"
    body.write_text(
        "# Aphrodite news monitor PARKED\n\n"
        f"Paused at {state.get('paused_at')} after {MON.BOUND_EMPTY} consecutive empty runs "
        "(base rule 10; operator limits of 2026-09-18). It resumes only on explicit clearance: "
        "set paused=false in state.json in a committed change that names who cleared it.\n",
        encoding="utf-8", newline="\n")
    sh(["python", "-m", "comms", "post", "--from", "Aphrodite", "--to", "Aphrodite", "--kind", "report",
        "--subject", "Aphrodite news monitor PARKED after 4 consecutive empty runs (reported once)",
        "--body-file", str(body)], cwd=service, check=False)


def commit(service: Path, paths, subject):
    msg = service / ".git_news_msg.txt"
    msg.write_text(subject + "\n\nAutomated pass of the bounded RSI news monitor (APHRODITE-12).\n",
                   encoding="utf-8")
    sh(["git", "add", "--"] + [str(p) for p in paths], cwd=service)
    if not sh(["git", "diff", "--cached", "--quiet"], cwd=service, check=False).returncode:
        msg.unlink()
        return
    sh(["git", "commit", "-q", "-F", str(msg)], cwd=service)
    msg.unlink()
    for _ in range(3):
        sh(["git", "fetch", "origin"], cwd=service)
        sh(["git", "merge", "-q", "--no-edit", "origin/main"], cwd=service, timeout=3600)
        if sh(["git", "push", "-q", "origin", "HEAD:main"], cwd=service, check=False).returncode == 0:
            break
    sh(["git", "fetch", "origin"], cwd=service)
    head = sh(["git", "rev-parse", "HEAD"], cwd=service).stdout.strip()
    ok = sh(["git", "merge-base", "--is-ancestor", head, "origin/main"], cwd=service, check=False).returncode == 0
    log(f"commit {head[:9]} ancestor_of_origin_main={ok}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # noqa: BLE001
        log(f"PASS FAILED: {e!r}")
        raise
