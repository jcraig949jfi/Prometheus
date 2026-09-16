"""Prepare -- never launch -- the Vivarium consumer on M2 (2026-09-16).

The consumer follows the production ledger eng_8a37a5d3 to M2 (operator
ccb26df01; Daedalus ruling comms #270). This script does the D-23 mechanics
that can be done before the move and MEASURES the launch preconditions
(base rule 9) so the relaunch is one explicit act with a receipt behind it:

    1. pinned DETACHED worktree at a recorded SHA (WORKING_CONTRACT s6), or
       verification that the existing one is at that SHA and clean
    2. data directory outside any worktree, with var/
    3. the two launchers copied from deploy/ with the worktree path filled
       in, sha256 of each in the receipt
    4. secrets PRESENCE in the pinned worktree's config.local.json -- key
       names only; values are never read into this process's output
    5. preconditions, each measured now and recorded:
         store     viv.db.connect() proves the canonical cluster
         pew       GET <pew>/health answers
         engine    GET <sfe>/v2/version answers with the EXPECTED
                   engine_instance_id (a twin that answers is WRONG_ENGINE)
    6. (--register) Task Scheduler tasks: VivariumConsumerM2 on demand,
       VivariumDeadmanM2 every 5 min but DISABLED -- enabling it IS the
       launch decision, taken by a person after this receipt reads green

Exit 0 only when every precondition passed. It never starts the consumer.
Nothing here prints, copies or hashes a token.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent            # vivarium/deploy
VIVARIUM = HERE.parent
REPO = VIVARIUM.parent
EXPECTED_ENGINE = "eng_8a37a5d305969034d488c43e"


def _utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256(p: Path) -> str:
    return "sha256:" + hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _git(*args, cwd: Path, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                          text=True, timeout=timeout)


# ------------------------------------------------------------------ steps

def ensure_worktree(canonical: Path, path: Path, sha: str, out: dict) -> bool:
    rec = {"path": str(path), "requested_sha": sha}
    if not path.exists():
        r = _git("worktree", "add", "--detach", str(path), sha, cwd=canonical,
                 timeout=1800)                       # 43k files; never short
        rec["created"] = r.returncode == 0
        rec["stderr"] = (r.stderr or "")[-400:]
        if r.returncode != 0:
            out["worktree"] = dict(rec, ok=False)
            return False
    else:
        rec["created"] = False
    head = _git("rev-parse", "HEAD", cwd=path).stdout.strip()
    full = _git("rev-parse", sha, cwd=canonical).stdout.strip()
    branch = _git("rev-parse", "--abbrev-ref", "HEAD", cwd=path).stdout.strip()
    dirty = bool(_git("status", "--porcelain", "--untracked-files=no", cwd=path).stdout.strip())
    gd = _git("rev-parse", "--git-dir", cwd=path).stdout.strip()
    gcd = _git("rev-parse", "--git-common-dir", cwd=path).stdout.strip()
    rec.update({"head": head, "detached": branch == "HEAD", "dirty": dirty,
                "not_canonical": gd != gcd})
    ok = (head == full and rec["detached"] and not dirty and rec["not_canonical"])
    out["worktree"] = dict(rec, ok=ok)
    return ok


def write_launchers(worktree: Path, data_dir: Path, out: dict) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "var").mkdir(exist_ok=True)
    recs = {}
    for name in ("vivarium_consumer_m2.cmd", "vivarium_deadman_m2.cmd"):
        src = HERE / name
        text = src.read_text(encoding="utf-8").replace("__PINNED_WORKTREE__", str(worktree))
        dst = data_dir / name
        dst.write_text(text, encoding="utf-8", newline="\r\n")
        recs[name] = {"from": str(src), "to": str(dst), "template_sha256": _sha256(src),
                      "written_sha256": _sha256(dst)}
    out["launchers"] = recs


def secrets_presence(worktree: Path, out: dict) -> bool:
    p = worktree / "vivarium" / "config.local.json"
    rec = {"path": str(p), "exists": p.exists()}
    if p.exists():
        try:
            keys = sorted(json.loads(p.read_text(encoding="utf-8")).keys())
        except Exception as exc:                          # noqa: BLE001
            keys = ["<unreadable: %s>" % type(exc).__name__]
        rec["keys"] = keys                                # names only, never values
        rec["sfe_token_present"] = "sfe_token" in keys
        rec["pew_token_present"] = "pew_token" in keys
    else:
        rec["sfe_token_present"] = rec["pew_token_present"] = False
    ok = rec["sfe_token_present"] and rec["pew_token_present"]
    out["secrets"] = dict(rec, ok=ok,
                          note="the operator carries this file from M1 with a receipt; "
                               "no seat copies a token across hosts (Daedalus #270)")
    return ok


def check_store(out: dict) -> bool:
    if str(VIVARIUM) not in sys.path:
        sys.path.insert(0, str(VIVARIUM))
    try:
        from viv import db as _db                          # noqa: PLC0415
        conn = _db.connect()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM " + _db.schema() +
                            ".research_experiment_queue WHERE status = 'queued'")
                queued = cur.fetchone()[0]
        finally:
            conn.close()
        out["store"] = {"ok": True, "environment": _db.db_environment(), "queued": queued}
        return True
    except Exception as exc:                              # noqa: BLE001
        out["store"] = {"ok": False, "error": "%s: %s" % (type(exc).__name__, str(exc)[:300])}
        return False


def check_pew(url: str, out: dict) -> bool:
    try:
        with urllib.request.urlopen(url.rstrip("/") + "/health", timeout=10) as r:
            body = json.loads(r.read().decode("utf-8"))
        ok = body.get("status") == "ok"
        out["pew"] = {"ok": ok, "url": url, "service": body.get("service"),
                      "schema_version": body.get("schema_version"),
                      "uptime_s": body.get("uptime_s")}
        return ok
    except Exception as exc:                              # noqa: BLE001
        out["pew"] = {"ok": False, "url": url, "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
        return False


def check_engine(url: str, cacert: Path, expected: str, out: dict) -> bool:
    if str(VIVARIUM) not in sys.path:
        sys.path.insert(0, str(VIVARIUM))
    from viv import deadman as _dm                         # noqa: PLC0415
    v = _dm.probe_upstream(url.rstrip("/") + "/v2/version", str(cacert), expected)
    out["engine"] = dict(v, expected=expected)
    return bool(v.get("ok"))


def register_tasks(data_dir: Path, out: dict) -> bool:
    consumer = data_dir / "vivarium_consumer_m2.cmd"
    deadman = data_dir / "vivarium_deadman_m2.cmd"
    cmds = [
        ["schtasks", "/Create", "/F", "/TN", "VivariumConsumerM2", "/SC", "ONCE",
         "/SD", "01/01/2035", "/ST", "00:00", "/TR", 'conhost.exe "%s"' % consumer],
        ["schtasks", "/Create", "/F", "/TN", "VivariumDeadmanM2", "/SC", "MINUTE",
         "/MO", "5", "/TR", 'cmd.exe /c "%s"' % deadman],
        ["schtasks", "/Change", "/TN", "VivariumDeadmanM2", "/DISABLE"],
    ]
    recs = []
    ok = True
    for c in cmds:
        r = subprocess.run(c, capture_output=True, text=True, timeout=60)
        recs.append({"cmd": " ".join(c[:4]), "rc": r.returncode,
                     "out": (r.stdout or r.stderr or "").strip()[-200:]})
        ok = ok and r.returncode == 0
    out["tasks"] = {"ok": ok, "steps": recs,
                    "note": "VivariumDeadmanM2 is registered DISABLED; enabling it is the "
                            "launch decision and relaunches the consumer on its first tick "
                            "if the engine precondition holds"}
    return ok


# ------------------------------------------------------------------ main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sha", required=True, help="the SHA the consumer is pinned to")
    ap.add_argument("--canonical", default=r"D:\Prometheus")
    ap.add_argument("--worktree", default=r"D:\Prometheus-worktrees\vivarium-consumer")
    ap.add_argument("--data-dir", default=r"D:\Prometheus-data\vivarium")
    ap.add_argument("--sfe-url", default="https://192.168.1.191:8811")
    ap.add_argument("--pew-url", default="http://192.168.1.191:8377/api/v1")
    ap.add_argument("--expected-engine", default=EXPECTED_ENGINE)
    ap.add_argument("--register", action="store_true", help="register the two tasks")
    ap.add_argument("--receipt", default=None)
    a = ap.parse_args(argv)

    os.environ.setdefault("EW_DB_HOST", "192.168.1.202")
    os.environ.setdefault("VIV_DB_HOST", "192.168.1.202")
    out = {"schema": "vivarium_prepare_m2.v1", "at": _utc(),
           "host": os.environ.get("COMPUTERNAME"), "sha": a.sha, "launched": False}
    wt = Path(a.worktree); dd = Path(a.data_dir)
    results = {
        "worktree": ensure_worktree(Path(a.canonical), wt, a.sha, out),
    }
    if results["worktree"]:
        write_launchers(wt, dd, out)
    results["secrets"] = secrets_presence(wt, out)
    results["store"] = check_store(out)
    results["pew"] = check_pew(a.pew_url, out)
    results["engine"] = check_engine(a.sfe_url, wt / "SerendipityFoundry" /
                                     "SerendipityFoundryClient" / "config" / "m2.crt",
                                     a.expected_engine, out)
    if a.register and results["worktree"]:
        results["tasks"] = register_tasks(dd, out)
    out["preconditions"] = results
    out["ready_to_launch"] = all(results.values())
    out["next"] = ("schtasks /Change /TN VivariumDeadmanM2 /ENABLE  (then read "
                   "var/deadman-vivarium@m2.state.json)" if out["ready_to_launch"]
                   else "fix the failed precondition(s): %s"
                   % [k for k, v in results.items() if not v])
    receipt = Path(a.receipt) if a.receipt else dd / ("prepare_m2-%s.json" % _utc().replace(":", ""))
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(json.dumps(out, indent=2, default=str))
    print("receipt:", receipt)
    return 0 if out["ready_to_launch"] else 1


if __name__ == "__main__":
    sys.exit(main())
