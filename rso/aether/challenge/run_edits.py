"""C-018-T040 semantic edits of the FROZEN surface (edits.json): each is applied to THIS worktree's working copy, the
frozen 33-test suite runs in a fresh `python -B` subprocess (caches purged), the witness runs, the file is restored byte
for byte (sha256 and `git diff --quiet` verified) and `freeze check` must print OK afterwards. An edit that SURVIVES the
suite while its witness moves shows a behaviour the frozen suite does not pin. No mutant is ever committed.

    python -B -m rso.aether.challenge.run_edits <scratch> <dup6_dir>

The E1 baseline witness is the B5 frozen run (<scratch>/B5_frozen.json, six real replays, run by cases.py before this),
not a second seven-minute run; under the E1 mutant no replay happens, so the mutant witness is quick.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

from rso.registry.registry import ROOT

HERE = os.path.dirname(os.path.abspath(__file__))
PY = [sys.executable, "-B"]
SUITE = PY + ["-m", "unittest", "rso.aether.tests.test_adapter"]
W2 = """
import json, os
from rso.aether import adapter as A, evaluate as E
m, a = A.load_unit(os.path.join(os.path.dirname(A.__file__), "qual", "records", "native_RX_0"))
t = m["tree"]; O, B = m["origin"], m["B"]
iO, iB = t["site"].index(O), t["site"].index(B)
t["parent"][iO], t["gen"][iO] = B, 1
t["parent"][iB], t["gen"][iB] = -1, 0
print(json.dumps(E.tree_check(m, a)))
"""


def purge():
    for d in ("rso/aether/__pycache__", "rso/aether/tests/__pycache__", "rso/aether/demand/__pycache__",
              "rso/aether/challenge/__pycache__", "rso/completeness/__pycache__"):
        shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)


def run(cmd, timeout=580):
    purge()
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout or ""), (p.stderr or "")


def suite():
    rc, out, err = run(SUITE)
    tail = (err or out).strip().splitlines()
    failing = sorted(set(l.split()[1] for l in tail if l.startswith(("FAIL:", "ERROR:"))))
    n = [l for l in tail if l.startswith("Ran ")]
    return rc, tail[-1] if tail else "", failing, n[0] if n else ""


def _e1_shape(r):
    return {"problems": r.get("problems"), "disposition_RX": r.get("laws", {}).get("RX", {}).get("disposition"),
            "completeness": r["completeness"]["status"], "rc": r["rc"], "replay_stubbed": r.get("replay_stubbed", False)}


def witness(eid, dup6, scratch, baseline=False):
    if eid == "E1":
        base = os.path.join(scratch, "B5_frozen.json")
        if baseline and os.path.exists(base):
            with open(base, encoding="utf-8") as f:
                return dict(_e1_shape(json.load(f)), source="B5_frozen.json")
        rc, out, err = run(PY + ["-m", "rso.aether.challenge.forge", "analyse", dup6])
        return dict(_e1_shape(json.loads(out)), source="run")
    if eid == "E2":
        rc, out, err = run(PY + ["-c", W2])
        return {"tree_check": json.loads(out)}
    if eid == "E3":
        rc, out, err = run(PY + ["-m", "rso.aether.challenge.forge", "e3", dup6])
        r = json.loads(out)
        return {"problems": r.get("problems"), "completeness": r["completeness"]["status"], "replay_stubbed": True}
    if eid == "E5":
        rc, out, err = run(PY + ["-m", "rso.aether.challenge.forge", "e5", dup6])
        r = json.loads(out)
        laws = r.get("laws")
        return {"rc": r["rc"], "completeness": r["completeness"]["status"], "laws_present": laws is not None,
                "RX_classes_printed": None if not laws else laws["RX"]["classes"],
                "RX_content_excess_all_printed": None if not laws else laws["RX"]["content_excess_all"],
                "disposition_RX": None if not laws else laws["RX"]["disposition"], "replay_stubbed": True}
    return None


def main(scratch, dup6):
    with open(os.path.join(HERE, "edits.json"), encoding="utf-8") as f:
        edits = json.load(f)
    rows = []
    rc, tail, failing, ran = suite()
    rows.append({"edit": "BASELINE", "suite_rc": rc, "tail": tail, "failing": failing, "ran": ran})
    if rc != 0:
        raise SystemExit("baseline not green: %s" % tail)
    base_w = {eid: witness(eid, dup6, scratch, baseline=True) for eid in edits if eid != "E4"}
    rows.append({"edit": "BASELINE_WITNESSES", "witnesses": base_w})
    for eid, e in edits.items():
        path = os.path.join(ROOT, "rso", "aether", e["file"])
        raw = open(path, "rb").read()
        sha = hashlib.sha256(raw).hexdigest()
        src = raw.decode("utf-8")
        if src.count(e["old"]) != 1:
            rows.append({"edit": eid, "result": "EDIT_NOT_UNIQUE", "count": src.count(e["old"])})
            continue
        try:
            open(path, "wb").write(src.replace(e["old"], e["new"]).encode("utf-8"))
            rc, tail, failing, ran = suite()
            w = witness(eid, dup6, scratch) if eid != "E4" else None
        finally:
            open(path, "wb").write(raw)
        restored = hashlib.sha256(open(path, "rb").read()).hexdigest() == sha
        gd = subprocess.run(["git", "diff", "--quiet", "--", path], cwd=ROOT).returncode == 0
        fz = run(PY + ["-m", "rso.aether.freeze", "check"])
        rows.append({"edit": eid, "file": e["file"], "prediction": e["prediction"], "suite_rc": rc, "tail": tail, "failing": failing,
                     "ran": ran, "result": "RED" if rc != 0 else "SURVIVES", "witness": w, "witness_baseline": base_w.get(eid),
                     "restored_sha256_ok": restored, "git_diff_quiet": gd, "freeze_check_after": fz[1].strip()})
        print(eid, rows[-1]["result"], failing, file=sys.stderr, flush=True)
    purge()
    with open(os.path.join(scratch, "edits_rows.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True, default=str) + "\n")
    return rows


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
