"""C-018-T030 RED rows: every decision line of the evaluator / completeness wrapper / non-ancestor rule has a behavioural test
that turns RED on its mutant (C-016-T041 lesson 3: a hash guard is not a behavioural pin; the suite has no freeze-hash test,
so every kill below is behavioural). Each edit is applied IN PLACE, the suite runs in a fresh `python -B` subprocess (caches
purged), the source is restored byte for byte and its sha256 re-checked. Baseline first, unedited.

    python -m rso.aether.red.run_red rso/aether/red/red_rows.jsonl
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

from rso.registry.registry import ROOT

SUITE = [sys.executable, "-B", "-m", "unittest", "rso.aether.tests.test_adapter"]
EDITS = [
    ("evaluate.py", "REMOVED_MIN, NONANC_MAX, TARGETS_MIN = 0.8, 0.2, 3", "REMOVED_MIN, NONANC_MAX, TARGETS_MIN = 0.7, 0.2, 3"),
    ("evaluate.py", "REMOVED_MIN, NONANC_MAX, TARGETS_MIN = 0.8, 0.2, 3", "REMOVED_MIN, NONANC_MAX, TARGETS_MIN = 0.8, 0.3, 3"),
    ("evaluate.py", "REMOVED_MIN, NONANC_MAX, TARGETS_MIN = 0.8, 0.2, 3", "REMOVED_MIN, NONANC_MAX, TARGETS_MIN = 0.8, 0.2, 2"),
    ("evaluate.py", "MARGIN, NULL_MAX = 0.05, 0.03", "MARGIN, NULL_MAX = 0.07, 0.03"),
    ("evaluate.py", "    if t0_sites(a) != [O]:\n", "    if len(t0_sites(a)) > 7:\n"),
    ("evaluate.py", "vac = N is None or imp[N] < 0", "vac = N is None"),
    ("evaluate.py", "tg = [s for s in targets if imp[s] >= 0]", "tg = list(targets)"),
    ("evaluate.py", "return bool((d <= ft[idx]).all())", "return bool((d <= ft[idx] + 10).all())"),
    ("evaluate.py", "    if set(tree[\"site\"]) != obs:\n", "    if False:\n"),
    ("evaluate.py", "    if B != meta[\"B\"]:\n", "    if False:\n"),
    ("evaluate.py", "return B, A.choose_nonancestor(tree, B, meta[\"origin\"], meta[\"n\"]), sorted(TR.descendants(tree, B))",
     "return B, meta[\"N\"], sorted(TR.descendants(tree, B))"),
    ("evaluate.py", "return [] if meta.get(\"arrays_sha256\") == A.arrays_sha256(a) else", "return [] if True else"),
    ("evaluate.py", "p2 = L[\"confirmed_r2\"] >= max(3, math.ceil(0.1 * L[\"n_units\"]))", "p2 = L[\"confirmed_r2\"] >= 3"),
    ("evaluate.py", "if L[\"null_excess\"] is None or abs(L[\"null_excess\"]) >= NULL_MAX:", "if L[\"null_excess\"] is None:"),
    ("evaluate.py", "need = max(3, math.ceil(0.1 * len(rows)))", "need = max(2, math.ceil(0.1 * len(rows)))"),
    ("evaluate.py", "[:, 1:min(band, 6)] - 0.125)", "[:, 1:6] - 0.125)"),
    ("confirm.py", "(pinned_design_sha256 is not None and design[\"manifest_sha256\"] != pinned_design_sha256)", "False"),
    ("confirm.py", "presented, sources=sources, native_digest=M.digest)", "presented, sources=sources, native_digest=None)"),
    ("adapter.py", "if g >= 1 and s != B", "if g >= -1 and s != B"),
    ("adapter.py", "return min(cands)[2] if cands else None", "return max(cands)[2] if cands else None"),
    ("adapter.py", "                    nx[f][y, x] = nc[f][y, x]\n", "                    pass\n"),
]


def purge():
    for d in ("rso/aether/__pycache__", "rso/aether/tests/__pycache__", "rso/aether/demand/__pycache__"):
        shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)


def suite():
    purge()
    p = subprocess.run(SUITE, cwd=ROOT, capture_output=True, text=True, timeout=600)
    tail = (p.stderr or p.stdout).strip().splitlines()
    return p.returncode, tail[-1] if tail else ""


def main(out):
    rows = []
    rc, tail = suite()
    rows.append({"edit": "BASELINE (unedited)", "returncode": rc, "result": "GREEN" if rc == 0 else "BROKEN", "tail": tail})
    if rc != 0:
        raise SystemExit("baseline not green: %s" % tail)
    for i, (f, old, new) in enumerate(EDITS):
        path = os.path.join(ROOT, "rso", "aether", f)
        raw = open(path, "rb").read()
        sha = hashlib.sha256(raw).hexdigest()
        src = raw.decode("utf-8")
        if src.count(old) != 1:
            rows.append({"edit": i, "file": f, "result": "EDIT_NOT_UNIQUE", "count": src.count(old)})
            continue
        try:
            open(path, "wb").write(src.replace(old, new).encode("utf-8"))
            rc, tail = suite()
        finally:
            open(path, "wb").write(raw)
        assert hashlib.sha256(open(path, "rb").read()).hexdigest() == sha
        rows.append({"edit": i, "file": f, "old": old.strip(), "new": new.strip(), "returncode": rc,
                     "result": "KILLED" if rc != 0 else "SURVIVED", "tail": tail})
        print(i, f, rows[-1]["result"], tail, file=sys.stderr, flush=True)
    purge()
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    killed = sum(1 for r in rows if r.get("result") == "KILLED")
    print("killed %d / %d" % (killed, len(EDITS)))
    return 0 if killed == len(EDITS) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
