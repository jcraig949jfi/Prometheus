"""Mutation runner for the C-013-T011 edits (edits.json). Applies ONE edit to the working copy of this worktree, runs the
named tests in a subprocess, restores the file byte-for-byte and verifies (sha256, git diff --quiet), then checks the
frozen manifest. Appends rows to mutation_rows.jsonl.

    <venv python> rso/reach/challenge/D1/run_edits.py --edit E1_... --phase targeted|rest|witness [--python <venv>]

Phases: targeted = the edit's own test file; rest = the other frozen test files (run only for survivors);
witness = witnesses.py <W> under the original, then under the mutant. The file is NEVER left mutated: every phase
restores in a finally block and refuses to proceed if the restore does not verify.
"""
import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ROWS = HERE / "mutation_rows.jsonl"
SPEC = json.loads((HERE / "edits.json").read_text(encoding="utf-8"))


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha(b):
    return hashlib.sha256(b).hexdigest()


class Mutant:
    def __init__(self, edit):
        self.edit = edit
        self.path = ROOT / edit["file"]
        self.orig = self.path.read_bytes()
        f, r = edit["find"].encode(), edit["replace"].encode()
        self.count = self.orig.count(f)
        if self.count != 1:
            raise SystemExit("find string occurs %d times in %s (need exactly 1)" % (self.count, edit["file"]))
        self.mut = self.orig.replace(f, r)

    def __enter__(self):
        self.path.write_bytes(self.mut)
        return self

    def __exit__(self, *a):
        self.path.write_bytes(self.orig)
        back = self.path.read_bytes()
        ok = sha(back) == sha(self.orig)
        clean = subprocess.run(["git", "diff", "--quiet", "--", self.edit["file"]], cwd=str(ROOT)).returncode == 0
        if not (ok and clean):
            raise SystemExit("RESTORE FAILED for %s: sha_equal=%s git_clean=%s" % (self.edit["file"], ok, clean))
        return False


def purge_pyc():
    """Bytecode hygiene (tooling repair after the first E3 witness, disclosed in REPORT.md): a mutation and its restore
    that land in the same second with equal file size leave a .pyc compiled from the MUTANT that Python considers valid
    for the restored original. Every subprocess now runs with -B and after a purge of rso/reach's caches."""
    for d in list((ROOT / "rso" / "reach").rglob("__pycache__")):
        shutil.rmtree(d, ignore_errors=True)


def pytest_run(python, tests):
    purge_pyc()
    t = time.perf_counter()
    r = subprocess.run([python, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", *tests], cwd=str(ROOT),
                       capture_output=True, text=True)
    tail = [ln for ln in r.stdout.splitlines() if ln.strip()][-3:]
    return dict(rc=r.returncode, seconds=round(time.perf_counter() - t, 1), tail=tail,
                failed_lines=[ln for ln in r.stdout.splitlines() if ln.startswith("FAILED")][:20])


def witness_run(python, w):
    purge_pyc()
    r = subprocess.run([python, "-B", str(HERE / "witnesses.py"), w], cwd=str(ROOT), capture_output=True, text=True)
    last = [ln for ln in r.stdout.splitlines() if ln.strip()]
    try:
        return json.loads(last[-1])
    except Exception:
        return dict(error=r.stderr[-2000:], stdout=r.stdout[-2000:])


def check_frozen(python):
    purge_pyc()
    r = subprocess.run([python, "-B", "-c", "from rso.reach import run_d1; run_d1.check_frozen(); print('FROZEN_OK')"],
                       cwd=str(ROOT), capture_output=True, text=True)
    return "FROZEN_OK" in r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edit", required=True)
    ap.add_argument("--phase", required=True, choices=["targeted", "rest", "witness"])
    ap.add_argument("--python", default=sys.executable)
    a = ap.parse_args()
    edit = next(e for e in SPEC["edits"] if e["id"] == a.edit)
    row = dict(edit=a.edit, phase=a.phase, started_at_utc=now(), file=edit["file"], predicted=edit["predicted"],
               bytecode_hygiene="purge+-B (rerun after the stale-pyc finding)")
    m = Mutant(edit)
    row["find_count"] = m.count
    if a.phase == "witness":
        if not edit["witness"]:
            raise SystemExit("no witness for this edit")
        row["original"] = witness_run(a.python, edit["witness"])
        with m:
            row["mutant"] = witness_run(a.python, edit["witness"])
        row["differs"] = row["original"] != row["mutant"]
    else:
        tests = edit["targeted_tests"] if a.phase == "targeted" else \
            [t for t in SPEC["all_tests"] if t not in edit["targeted_tests"]]
        row["tests"] = tests
        with m:
            row["result"] = pytest_run(a.python, tests)
        row["outcome"] = "KILLED" if row["result"]["rc"] != 0 else "SURVIVES"
    row["restored_sha256"] = sha(m.path.read_bytes())
    row["frozen_ok_after_restore"] = check_frozen(a.python)
    row["finished_at_utc"] = now()
    with open(ROWS, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(row, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: row.get(k) for k in ("edit", "phase", "outcome", "differs", "frozen_ok_after_restore")}))


if __name__ == "__main__":
    main()
