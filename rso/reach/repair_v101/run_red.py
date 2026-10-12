"""RED evidence for the C-013-T013 behavioural pins: each edit in RED_EDITS.json, applied verbatim, must make its test
fail; the unmodified tree must pass all four. Appends rows to red_rows.jsonl.

    <venv python> rso/reach/repair_v101/run_red.py

The mutated file is restored in a finally block and verified (sha256 + git diff --quiet); a failed restore stops.
"""
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ROWS = HERE / "red_rows.jsonl"
SPEC = json.loads((HERE / "RED_EDITS.json").read_text(encoding="utf-8"))


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def purge_pyc():
    for d in (ROOT / "rso" / "reach").rglob("__pycache__"):
        shutil.rmtree(d, ignore_errors=True)


def pytest(node):
    purge_pyc()
    t = time.time()
    p = subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", node], cwd=str(ROOT),
                       capture_output=True, text=True, timeout=580)
    tail = [x for x in p.stdout.splitlines() if x.strip()][-3:]
    reason = [x.strip() for x in p.stdout.splitlines() if x.startswith("E ")][:2]
    return dict(rc=p.returncode, seconds=round(time.time() - t, 1), tail=tail, reason=reason)


def row(**kw):
    kw["at_utc"] = now()
    with open(ROWS, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(kw, sort_keys=True) + "\n")
    print(json.dumps(kw, sort_keys=True), flush=True)


def main():
    base = pytest("rso/reach/tests/test_repair_v101.py")
    row(edit="BASELINE_UNMODIFIED", outcome="GREEN" if base["rc"] == 0 else "NOT_GREEN", result=base)
    for e in SPEC["edits"]:
        path = ROOT / e["file"]
        orig = path.read_bytes()
        n = orig.count(e["find"].encode())
        if n != 1:
            raise SystemExit("find occurs %d times in %s" % (n, e["file"]))
        try:
            path.write_bytes(orig.replace(e["find"].encode(), e["replace"].encode()))
            res = pytest(e["test"])
        finally:
            path.write_bytes(orig)
            ok = hashlib.sha256(path.read_bytes()).hexdigest() == hashlib.sha256(orig).hexdigest()
            clean = subprocess.run(["git", "diff", "--quiet", "--", e["file"]], cwd=str(ROOT)).returncode == 0
            if not (ok and clean):
                raise SystemExit("RESTORE FAILED: %s" % e["file"])
        purge_pyc()
        row(edit=e["id"], file=e["file"], test=e["test"], find_count=n, outcome="RED" if res["rc"] != 0 else "SURVIVES",
            restored_sha256=hashlib.sha256(orig).hexdigest(), result=res)
    return 0


if __name__ == "__main__":
    sys.exit(main())
