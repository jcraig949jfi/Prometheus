"""C-016-T042 mutation re-run (Pallas). Every edit of repair_v110/RED_EDITS.json (Pallas's E1 E2 E3 E4 E6 verbatim
from challenge/edits.json, Argus's R1-R6) plus the E5 control is applied to the working copy of THIS worktree; the
named test and the full two-module suite run in fresh `python -B` subprocesses after a cache purge; the freeze hash
guard is recorded with the mutant in place; the file is restored byte-for-byte and verified (sha256, git diff
--quiet) and `freeze check` must print OK afterwards. Witness phase: witnesses_r2.py under original and mutant.
Appends rows to red_rows_r2.jsonl. The file is never left mutated (finally block; a failed restore stops the run).

    python -B rso/ensorain/challenge/R2/run_edits_r2.py --baseline
    python -B rso/ensorain/challenge/R2/run_edits_r2.py --edit E1_HOLM_BYPASS [--phase suite|witness]
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
ROOT = HERE.parents[3]
ROWS = HERE / "red_rows_r2.jsonl"
RED = json.loads((ROOT / "rso/ensorain/repair_v110/RED_EDITS.json").read_text(encoding="utf-8"))
CHALLENGE = {e["id"]: e for e in json.loads((ROOT / "rso/ensorain/challenge/edits.json").read_text(encoding="utf-8"))["edits"]}
SUITE = ["rso.ensorain.tests.test_assay", "rso.ensorain.tests.test_repair_v110"]
WITNESS = {"E1_HOLM_BYPASS": "W1", "E2_GPRE_ARM": "W2", "E3_LATE_WINDOW": "W3", "E4_SWAP_CONTROLS": "W4", "E6_GATE_MAJORITY": "W5"}


def edits():
    out = {}
    for e in RED["edits"]:
        if e.get("from") == "challenge":
            src = dict(CHALLENGE[e["id"]], test=e["test"], source="challenge/edits.json (verbatim)")
        else:
            src = dict(e, source="repair_v110/RED_EDITS.json")
        out[e["id"]] = src
    out["E5_FROZEN_IS_PLASTIC"] = dict(CHALLENGE["E5_FROZEN_IS_PLASTIC"], test=None, source="challenge/edits.json (control)")
    return out


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def purge_pyc():
    for d in list((ROOT / "rso" / "ensorain").rglob("__pycache__")):
        shutil.rmtree(d, ignore_errors=True)


def unittest_run(*targets):
    purge_pyc()
    t = time.perf_counter()
    p = subprocess.run([sys.executable, "-B", "-m", "unittest", *targets], cwd=str(ROOT), capture_output=True, text=True, timeout=580)
    txt = p.stderr + p.stdout
    ran = re.search(r"Ran (\d+) tests?", txt)
    fails = re.findall(r"^(?:FAIL|ERROR): (\S+) \(([^)]+)\)", txt, re.M)
    return dict(rc=p.returncode, seconds=round(time.perf_counter() - t, 1), ran=int(ran.group(1)) if ran else None,
                failures=sorted({c for m, c in fails})[:20], tail=[x for x in txt.splitlines() if x.strip()][-2:])


def witness_run(w):
    purge_pyc()
    r = subprocess.run([sys.executable, "-B", str(HERE / "witnesses_r2.py"), w], cwd=str(ROOT), capture_output=True, text=True, timeout=580)
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


class Mutant:
    def __init__(self, e):
        self.e, self.path = e, ROOT / e["file"]
        self.orig = self.path.read_bytes()
        f, r = e["find"].encode(), e["replace"].encode()
        self.count = self.orig.count(f)
        if self.count != 1:
            raise SystemExit("find string occurs %d times in %s" % (self.count, e["file"]))
        self.mut = self.orig.replace(f, r)

    def __enter__(self):
        self.path.write_bytes(self.mut)
        return self

    def __exit__(self, *a):
        self.path.write_bytes(self.orig)
        ok = sha(self.path.read_bytes()) == sha(self.orig)
        clean = subprocess.run(["git", "diff", "--quiet", "--", self.e["file"]], cwd=str(ROOT)).returncode == 0
        purge_pyc()
        if not (ok and clean):
            raise SystemExit("RESTORE FAILED for %s: sha_equal=%s git_clean=%s" % (self.e["file"], ok, clean))
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edit")
    ap.add_argument("--phase", choices=["suite", "witness"], default="suite")
    ap.add_argument("--baseline", action="store_true")
    a = ap.parse_args()
    if a.baseline:
        row = dict(edit="BASELINE_UNMODIFIED", phase="suite", started_at_utc=now(), result=unittest_run(*SUITE), freeze=freeze_check())
        row["outcome"] = "GREEN" if row["result"]["rc"] == 0 and row["freeze"]["ok"] else "NOT_GREEN"
        row["finished_at_utc"] = now()
        return write(row)
    e = edits()[a.edit]
    row = dict(edit=a.edit, phase=a.phase, started_at_utc=now(), file=e["file"], source=e["source"], test=e["test"],
               find=e["find"], replace=e["replace"], bytecode_hygiene="purge rso/ensorain __pycache__ + python -B for every subprocess")
    m = Mutant(e)
    row["find_count"] = m.count
    if a.phase == "witness":
        w = WITNESS[a.edit]
        row["witness"] = w
        row["original"] = witness_run(w)
        with m:
            row["hash_guard_fires_on_mutant"] = not freeze_check()["ok"]
            row["mutant"] = witness_run(w)
        row["differs"] = row["original"] != row["mutant"]
    else:
        with m:
            row["hash_guard_fires_on_mutant"] = not freeze_check()["ok"]
            row["named"] = unittest_run(e["test"]) if e["test"] else None
            row["suite"] = unittest_run(*SUITE)
        named_red = row["named"] is not None and row["named"]["rc"] != 0
        row["outcome"] = "RED" if named_red else ("KILLED" if row["suite"]["rc"] != 0 else "SURVIVES")
    row["restored_sha256"] = sha(m.path.read_bytes())
    row["frozen_ok_after_restore"] = freeze_check()["ok"]
    row["finished_at_utc"] = now()
    write(row)


if __name__ == "__main__":
    main()
