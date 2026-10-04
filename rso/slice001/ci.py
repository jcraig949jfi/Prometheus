"""Deterministic CI command for slice001: `python -B -m rso.slice001.ci`.

Runs unittest discovery over rso/slice001/tests, shape-checks contract/contract.json
when present, prints one JSON run record on stdout, exits 0 only if nothing failed or
errored and the contract is not INVALID. Presence and types only; no semantics.
Python >= 3.8, standard library only.
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
import time
import unittest

PKG_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(PKG_DIR))
DEFAULT_TESTS = os.path.join(PKG_DIR, "tests")
DEFAULT_CONTRACT = os.path.join(PKG_DIR, "contract", "contract.json")

REQUIRED_KEYS = ("version", "frozen", "claim", "world", "reset_model", "receipt", "render",
                 "authority_stages", "custody", "gates", "cases", "challenge", "caps", "files")
# Only the types the packet fixes; every other key must merely be present and not null.
KEY_TYPES = {"version": (str, int, float), "frozen": (bool,)}


def validate_contract(path):
    """Return {"state": ABSENT|OK|INVALID, "problems": [...]}."""
    if not os.path.isfile(path):
        return {"state": "ABSENT", "problems": []}
    try:
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)
    except (OSError, ValueError) as e:
        return {"state": "INVALID", "problems": ["unreadable or not JSON: %s" % e]}
    if not isinstance(obj, dict):
        return {"state": "INVALID", "problems": ["top level is not an object"]}
    problems = []
    for k in REQUIRED_KEYS:
        if k not in obj:
            problems.append("missing key: %s" % k)
        elif obj[k] is None:
            problems.append("null value: %s" % k)
        elif k in KEY_TYPES:
            ok = isinstance(obj[k], KEY_TYPES[k])
            if k == "version" and isinstance(obj[k], bool):
                ok = False
            if not ok:
                problems.append("wrong type: %s is %s" % (k, type(obj[k]).__name__))
    return {"state": "INVALID" if problems else "OK", "problems": problems}


def _git(*args):
    try:
        r = subprocess.run(("git",) + args, cwd=REPO_ROOT, stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL, universal_newlines=True, timeout=60)
        return r.stdout.strip() if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_tests(tests_dir):
    # Discover by start dir; top-level is the repo root when tests live in the package so
    # that `rso.slice001.tests.*` imports resolve, else the start dir itself.
    in_repo = os.path.abspath(tests_dir).startswith(REPO_ROOT + os.sep)
    top_level = REPO_ROOT if in_repo else os.path.abspath(tests_dir)
    suite = unittest.defaultTestLoader.discover(os.path.abspath(tests_dir), top_level_dir=top_level)
    with open(os.devnull, "w") as sink:
        result = unittest.TextTestRunner(stream=sink, verbosity=0).run(suite)
    failed, errored = len(result.failures), len(result.errors)
    skipped = len(result.skipped)
    return {"tests_run": result.testsRun, "failed": failed, "errored": errored,
            "skipped": skipped, "passed": result.testsRun - failed - errored - skipped}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -B -m rso.slice001.ci")
    ap.add_argument("--tests-dir", default=DEFAULT_TESTS)
    ap.add_argument("--contract", default=DEFAULT_CONTRACT)
    ap.add_argument("--ledger", help="attempted-run inventory store (JSONL); makes this launch a charged, "
                                     "inventoried TOP_LEVEL attempt (C-004-T019). Off by default so that "
                                     "development runs never spend the slice caps.")
    ap.add_argument("--node-id", help="node_id this launch validates (V7); required with --ledger")
    ap.add_argument("--run-id", help="run_id for the inventory row (default: UTC time and pid)")
    args = ap.parse_args(argv)
    if args.ledger and not args.node_id:
        ap.error("--ledger requires --node-id")
    if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)
    sys.dont_write_bytecode = True
    attempt = led = None
    if args.ledger:
        from rso.slice001 import ledger as ledger_mod
        run_id = args.run_id or "ci-%s-%d" % (_utc_now(), os.getpid())
        try:
            led = ledger_mod.Ledger.from_contract(args.ledger, args.contract)
            attempt = led.begin(run_id, args.node_id, supplied_by="rso.slice001.ci")
        except (ledger_mod.CapExhausted, ledger_mod.LedgerError) as e:
            sys.stderr.write("REFUSED: %s\n" % e)
            return 2
    start_utc, w0, c0 = _utc_now(), time.perf_counter(), time.process_time()
    try:
        counts = run_tests(args.tests_dir)
        contract = validate_contract(args.contract)
    except BaseException:
        if attempt:
            attempt.finish("FAILED", cpu_s=time.process_time() - c0)
        raise
    ok = counts["failed"] == 0 and counts["errored"] == 0 and contract["state"] != "INVALID"
    record = dict(counts)
    record.update({
        "status": "PASSED" if ok else "FAILED",
        "contract": contract,
        "start_utc": start_utc,
        "end_utc": _utc_now(),
        "git_sha": _git("rev-parse", "HEAD"),
        "dirty": bool(_git("status", "--porcelain", "--untracked-files=no")),
        "wall_s": round(time.perf_counter() - w0, 3),
        "cpu_s": round(time.process_time() - c0, 3),
    })
    if attempt:
        attempt.finish("COMPLETED" if ok else "FAILED", cpu_s=record["cpu_s"])
        record["ledger"] = {"store": args.ledger, "run_id": run_id, "node_id": args.node_id,
                            "usage": led.usage()}
    print(json.dumps(record, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
