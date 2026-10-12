"""RED evidence for the C-016-T041 behavioural pins (the rso/reach/repair_v101/run_red.py pattern on unittest). Each
edit in RED_EDITS.json is applied to the working copy -- Pallas's E-edits verbatim from challenge/edits.json -- and
its named test must fail; the whole suite is run as well and its failures recorded. The unmodified tree must pass.
Bytecode caches are purged and every subprocess runs with -B. The file is restored in a finally block and verified
(sha256 + git diff --quiet against the committed blob); a failed restore stops. Appends rows to red_rows.jsonl.

    python -B rso/ensorain/repair_v110/run_red.py
"""
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ROWS = HERE / "red_rows.jsonl"
SPEC = json.loads((HERE / "RED_EDITS.json").read_text(encoding="utf-8"))
CHALLENGE = {e["id"]: e for e in json.loads((HERE.parent / "challenge" / "edits.json").read_text(encoding="utf-8"))["edits"]}


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def purge_pyc():
    for d in list((ROOT / "rso" / "ensorain").rglob("__pycache__")):
        shutil.rmtree(d, ignore_errors=True)


def unittest_run(*targets):
    purge_pyc()
    t = time.time()
    p = subprocess.run([sys.executable, "-B", "-m", "unittest", *targets], cwd=str(ROOT), capture_output=True, text=True,
                       timeout=580)
    txt = p.stderr + p.stdout
    ran = re.search(r"Ran (\d+) tests?", txt)
    fails = re.findall(r"^(?:FAIL|ERROR): (\S+) \(([^)]+)\)", txt, re.M)
    return dict(rc=p.returncode, seconds=round(time.time() - t, 1), ran=int(ran.group(1)) if ran else None,
                failures=["%s.%s" % (c, m) for m, c in fails][:20],
                tail=[x for x in txt.splitlines() if x.strip()][-2:])


def row(**kw):
    kw["at_utc"] = now()
    with open(ROWS, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(kw, sort_keys=True) + "\n")
    print(json.dumps({k: kw.get(k) for k in ("edit", "outcome", "find_count")}), flush=True)


def main():
    base = unittest_run(*SPEC["suite"])
    row(edit="BASELINE_UNMODIFIED", outcome="GREEN" if base["rc"] == 0 else "NOT_GREEN", result=base)
    if base["rc"] != 0:
        return 1
    for e in SPEC["edits"]:
        src = dict(CHALLENGE[e["id"]], test=e["test"]) if e.get("from") == "challenge" else e
        path = ROOT / src["file"]
        orig = path.read_bytes()
        n = orig.count(src["find"].encode())
        if n != 1:
            raise SystemExit("find occurs %d times in %s" % (n, src["file"]))
        try:
            path.write_bytes(orig.replace(src["find"].encode(), src["replace"].encode()))
            named = unittest_run(src["test"])
            suite = unittest_run(*SPEC["suite"])
        finally:
            path.write_bytes(orig)
            ok = hashlib.sha256(path.read_bytes()).hexdigest() == hashlib.sha256(orig).hexdigest()
            clean = subprocess.run(["git", "diff", "--quiet", "--", src["file"]], cwd=str(ROOT)).returncode == 0
            if not ok or not clean:
                raise SystemExit("RESTORE FAILED: %s (sha_equal=%s git_clean=%s)" % (src["file"], ok, clean))
        purge_pyc()
        row(edit=e["id"], source="challenge/edits.json (verbatim)" if e.get("from") == "challenge" else "RED_EDITS.json",
            file=src["file"], find=src["find"], replace=src["replace"], test=src["test"], find_count=n,
            outcome="RED" if named["rc"] != 0 else "SURVIVES", named=named, suite=suite,
            restored_sha256=hashlib.sha256(orig).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
