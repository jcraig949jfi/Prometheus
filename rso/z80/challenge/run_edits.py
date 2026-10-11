"""C-017-T040 semantic edits (Pallas). Each edit in edits.json is applied IN PLACE to the working copy of THIS worktree, the
frozen 42-test suite runs in a fresh `python -B` subprocess (caches purged), the edit's witness runs under the mutant, the
file is restored byte for byte and verified (sha256; `git diff --quiet` on the file), and `freeze check` must print OK
afterwards. The witnesses run once under the frozen source first (baseline). Rows -> red_rows.jsonl. Two processes at most
(this one waits on its child).

    python -B -m rso.z80.challenge.run_edits
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

from rso.registry.registry import ROOT

HERE = os.path.dirname(os.path.abspath(__file__))
SUITE = [sys.executable, "-B", "-m", "unittest", "rso.z80.tests.test_attribution"]


def purge():
    for d, _, _ in os.walk(os.path.join(ROOT, "rso", "z80")):
        if d.endswith("__pycache__"):
            shutil.rmtree(d, ignore_errors=True)


def suite():
    purge(); t = time.time()
    p = subprocess.run(SUITE, cwd=ROOT, capture_output=True, text=True, timeout=580)
    failing = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+)", p.stderr, re.M)))
    ran = re.search(r"Ran (\d+) test", p.stderr)
    return dict(rc=p.returncode, ran=int(ran.group(1)) if ran else 0, failing=failing, seconds=round(time.time() - t, 1))


def witness(w):
    purge()
    p = subprocess.run([sys.executable, "-B", "-m", "rso.z80.challenge.witnesses", w], cwd=ROOT, capture_output=True, text=True, timeout=580)
    last = [x for x in p.stdout.splitlines() if x.strip()]
    try:
        return json.loads(last[-1])
    except Exception:
        return dict(error=p.stderr[-1500:])


def freeze_check():
    p = subprocess.run([sys.executable, "-B", "-m", "rso.z80.freeze", "check"], cwd=ROOT, capture_output=True, text=True, timeout=120)
    return p.stdout.strip()


def main():
    edits = json.load(open(os.path.join(HERE, "edits.json"), encoding="utf-8"))["edits"]
    rows = []
    base = suite(); rows.append(dict(id="BASELINE", **base, green=base["rc"] == 0, freeze=freeze_check()))
    print(rows[-1], flush=True)
    for w in sorted({e["witness"] for e in edits if e.get("witness")}):
        rows.append(dict(id="BASELINE:" + w, witness=witness(w))); print(rows[-1], flush=True)
    for e in edits:
        path = os.path.join(ROOT, e["file"]); orig = open(path, "rb").read(); h = hashlib.sha256(orig).hexdigest()
        text = orig.decode("utf-8"); n = text.count(e["find"])
        row = dict(id=e["id"], file=e["file"], what=e["what"], expect=e["expect"], find_count=n)
        if n != 1:
            row.update(applied=False); rows.append(row); print(row, flush=True); continue
        try:
            open(path, "wb").write(text.replace(e["find"], e["replace"]).encode("utf-8"))
            s = suite(); row.update(applied=True, **s, red=s["rc"] != 0, expected_test_red=(e["expect"] in s["failing"]) if e["expect"] else None,
                                   freeze_with_mutant=freeze_check())
            if e.get("witness"):
                row["witness"] = witness(e["witness"])
        finally:
            open(path, "wb").write(orig)
        restored = hashlib.sha256(open(path, "rb").read()).hexdigest() == h
        gd = subprocess.run(["git", "diff", "--quiet", "--", e["file"]], cwd=ROOT).returncode == 0
        row.update(restored=restored, git_clean=gd, freeze_after=freeze_check())
        assert restored and gd and row["freeze_after"] == "OK", row
        rows.append(row)
        print(e["id"], "RED" if row["red"] else "SURVIVES", row["failing"], row.get("witness"), flush=True)
    purge()
    with open(os.path.join(HERE, "red_rows.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
