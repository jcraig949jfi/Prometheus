"""Mutation runner for the C-016-T040 edits (edits.json). Applies ONE edit to the working copy of this worktree, runs
the frozen unittest suite (or a witness) in a fresh `python -B` subprocess after purging rso/ensorain's bytecode caches
(stale-pyc hazard, Pallas journal 2026-10-10), records whether the freeze hash guard fires with the mutant in place,
restores the file byte-for-byte and verifies (sha256, git diff --quiet), then requires `freeze check` to print OK.
Appends rows to mutation_rows.jsonl. The file is NEVER left mutated: the restore runs in a finally block and a failed
restore stops the run.

    python -B rso/ensorain/challenge/run_edits.py --edit E1_HOLM_BYPASS --phase suite|witness
    python -B rso/ensorain/challenge/run_edits.py --baseline
"""
import argparse
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
ROWS = HERE / "mutation_rows.jsonl"
SPEC = json.loads((HERE / "edits.json").read_text(encoding="utf-8"))


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def purge_pyc():
    for d in list((ROOT / "rso" / "ensorain").rglob("__pycache__")):
        shutil.rmtree(d, ignore_errors=True)


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
        ok = sha(self.path.read_bytes()) == sha(self.orig)
        clean = subprocess.run(["git", "diff", "--quiet", "--", self.edit["file"]], cwd=str(ROOT)).returncode == 0
        purge_pyc()
        if not (ok and clean):
            raise SystemExit("RESTORE FAILED for %s: sha_equal=%s git_clean=%s" % (self.edit["file"], ok, clean))
        return False


def suite_run():
    purge_pyc()
    t = time.perf_counter()
    r = subprocess.run([sys.executable, "-B", *SPEC["suite"][2:]], cwd=str(ROOT), capture_output=True, text=True, timeout=580)
    txt = r.stderr + r.stdout
    ran = re.search(r"Ran (\d+) tests", txt)
    fails = re.findall(r"^(FAIL|ERROR): (\S+) \(([^)]+)\)", txt, re.M)
    return dict(rc=r.returncode, seconds=round(time.perf_counter() - t, 1), ran=int(ran.group(1)) if ran else None,
                failures=[" ".join(x) for x in fails][:20], tail=[ln for ln in txt.splitlines() if ln.strip()][-2:])


def witness_run(w):
    purge_pyc()
    r = subprocess.run([sys.executable, "-B", str(HERE / "witnesses.py"), w], cwd=str(ROOT), capture_output=True, text=True, timeout=580)
    last = [ln for ln in r.stdout.splitlines() if ln.strip()]
    try:
        return json.loads(last[-1])
    except Exception:
        return dict(error=r.stderr[-2000:], stdout=r.stdout[-2000:])


def freeze_check():
    purge_pyc()
    r = subprocess.run([sys.executable, "-B", "-m", "rso.ensorain.freeze", "check"], cwd=str(ROOT), capture_output=True, text=True, timeout=300)
    return dict(ok=r.returncode == 0 and r.stdout.strip() == "OK", out=r.stdout.strip().splitlines()[:5])


def write(row):
    with open(ROWS, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(row, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: row.get(k) for k in ("edit", "phase", "outcome", "differs", "hash_guard_fires_on_mutant", "frozen_ok_after_restore")}), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edit")
    ap.add_argument("--phase", choices=["suite", "witness"])
    ap.add_argument("--baseline", action="store_true")
    a = ap.parse_args()
    if a.baseline:
        row = dict(edit="BASELINE_UNMODIFIED", phase="suite", started_at_utc=now(), result=suite_run(), freeze=freeze_check())
        row["outcome"] = "GREEN" if row["result"]["rc"] == 0 and row["freeze"]["ok"] else "NOT_GREEN"
        row["finished_at_utc"] = now()
        return write(row)
    edit = next(e for e in SPEC["edits"] if e["id"] == a.edit)
    row = dict(edit=a.edit, phase=a.phase, started_at_utc=now(), file=edit["file"], predicted=edit["predicted"],
               bytecode_hygiene="purge rso/ensorain __pycache__ + python -B for every subprocess")
    m = Mutant(edit)
    row["find_count"] = m.count
    if a.phase == "witness":
        if not edit["witness"]:
            raise SystemExit("no witness for this edit")
        row["original"] = witness_run(edit["witness"])
        with m:
            row["hash_guard_fires_on_mutant"] = not freeze_check()["ok"]
            row["mutant"] = witness_run(edit["witness"])
        row["differs"] = row["original"] != row["mutant"]
    else:
        with m:
            row["hash_guard_fires_on_mutant"] = not freeze_check()["ok"]
            row["result"] = suite_run()
        row["outcome"] = "KILLED" if row["result"]["rc"] != 0 else "SURVIVES"
    row["restored_sha256"] = sha(m.path.read_bytes())
    row["frozen_ok_after_restore"] = freeze_check()["ok"]
    row["finished_at_utc"] = now()
    write(row)


if __name__ == "__main__":
    main()
