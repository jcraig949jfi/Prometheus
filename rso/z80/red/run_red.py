"""C-017-T030 RED rows: every decision-rule line has a behavioural test that turns RED on its mutant (C-016-T041 lesson 3:
a hash guard is not a behavioural pin). Each edit in RED_EDITS.json is applied IN PLACE, the suite runs in a fresh `python -B`
subprocess (caches purged), the source is restored byte for byte and its sha256 re-checked. Baseline first, unedited.

    python -m rso.z80.red.run_red rso/z80/red/red_rows.jsonl
    python -m rso.z80.red.run_red OUT i/k        v1.1.0: mutants with index % k == i (each shard runs the baseline; a headless
                                                 foreground call is <= 600 s); then `merge OUT k` writes OUT from the shards
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

from rso.registry.registry import ROOT

HERE = os.path.dirname(os.path.abspath(__file__))
SUITE = [sys.executable, "-B", "-m", "unittest", "rso.z80.tests.test_attribution"]


def purge():
    for d in ("rso/z80/__pycache__", "rso/z80/tests/__pycache__"):
        shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)


def suite():
    purge()
    p = subprocess.run(SUITE, cwd=ROOT, capture_output=True, text=True, timeout=600)
    failing = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+)", p.stderr, re.M)))
    ran = re.search(r"Ran (\d+) test", p.stderr)
    return p.returncode, failing, int(ran.group(1)) if ran else 0


def main(out, shard=(0, 1)):
    edits = [e for k, e in enumerate(json.load(open(os.path.join(HERE, "RED_EDITS.json"), encoding="utf-8"))) if k % shard[1] == shard[0]]
    rc, failing, ran = suite()
    rows = [dict(id="BASELINE", rc=rc, ran=ran, failing=failing, green=rc == 0)]
    print(rows[-1], flush=True)
    for e in edits:
        path = os.path.join(ROOT, e["file"])
        orig = open(path, "rb").read(); h = hashlib.sha256(orig).hexdigest()
        text = orig.decode("utf-8")
        assert text.count(e["find"]) == 1, e["id"]
        try:
            open(path, "wb").write(text.replace(e["find"], e["replace"]).encode("utf-8"))
            rc, failing, ran = suite()
        finally:
            open(path, "wb").write(orig)
        assert hashlib.sha256(open(path, "rb").read()).hexdigest() == h, e["id"]
        rows.append(dict(id=e["id"], file=e["file"], what=e["what"], expect=e["expect"], rc=rc, ran=ran, failing=failing,
                         red=rc != 0, expected_red=e["expect"] in failing))
        print(rows[-1]["id"], "RED" if rows[-1]["red"] else "SURVIVED", "expected-test-red" if rows[-1]["expected_red"] else "EXPECTED TEST GREEN",
              failing, flush=True)
    purge()
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    ok = rows[0]["green"] and all(r["red"] and r["expected_red"] for r in rows[1:])
    print("ALL_RED" if ok else "NOT_ALL_RED", len(rows) - 1, "mutants")
    return 0 if ok else 1


def merge(out, k):
    shards = [[json.loads(x) for x in open("%s.%d-%d" % (out, i, k), encoding="utf-8")] for i in range(k)]
    order = [e["id"] for e in json.load(open(os.path.join(HERE, "RED_EDITS.json"), encoding="utf-8"))]
    byid = {r["id"]: r for sh in shards for r in sh[1:]}
    rows = [shards[0][0]] + [byid[i] for i in order]
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    ok = all(sh[0]["green"] for sh in shards) and all(r["red"] and r["expected_red"] for r in rows[1:])
    print("ALL_RED" if ok else "NOT_ALL_RED", len(rows) - 1, "mutants")
    return 0 if ok else 1


if __name__ == "__main__":
    if sys.argv[1] == "merge":
        sys.exit(merge(sys.argv[2], int(sys.argv[3])))
    if len(sys.argv) > 2:
        i, k = (int(x) for x in sys.argv[2].split("/"))
        sys.exit(main("%s.%d-%d" % (sys.argv[1], i, k), (i, k)))
    sys.exit(main(sys.argv[1]))
