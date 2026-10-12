"""C-018-T040 POST-HOC edits E1h / E3h (labelled; predictions added to expected.json and committed before this runs).
The first run's E1 / E3 witnesses could not move because the forged design pins confirm.py's own hash: a mutated
analyser is refused with SOURCE_MISMATCH (a property in the builder's favour). B6 shows the design pin is rewritable at
analysis time, so here the design's sources are re-sealed under the mutant (forge.reseal_sources) and the witnesses
re-run. Same apply / restore discipline as run_edits.py.

    python -B -m rso.aether.challenge.edits_posthoc <scratch> <dup6_dir>
"""
import hashlib
import json
import os
import subprocess
import sys

from rso.aether.challenge.run_edits import HERE, PY, ROOT, purge, run, suite


def witness(eid, dup6):
    if eid == "E1":
        rc, out, err = run(PY + ["-m", "rso.aether.challenge.forge", "analyse", dup6, "--reseal-sources"])
        r = json.loads(out)
        return {"problems": r.get("problems"), "disposition_RX": r.get("laws", {}).get("RX", {}).get("disposition"),
                "completeness": r["completeness"]["status"], "rc": r["rc"], "replay_stubbed": r.get("replay_stubbed", False),
                "design_resealed": r.get("design_resealed")}
    rc, out, err = run(PY + ["-m", "rso.aether.challenge.forge", "e3", dup6, "--reseal-sources"])
    r = json.loads(out)
    return {"problems": r.get("problems"), "completeness": r["completeness"]["status"], "replay_stubbed": True,
            "design_resealed": r.get("design_resealed")}


def main(scratch, dup6):
    with open(os.path.join(HERE, "edits.json"), encoding="utf-8") as f:
        edits = json.load(f)
    rows = []
    base_w = {eid: witness(eid, dup6) for eid in ("E1", "E3")}
    rows.append({"edit": "BASELINE_WITNESSES_RESEALED", "witnesses": base_w})
    for eid in ("E1", "E3"):
        e = edits[eid]
        path = os.path.join(ROOT, "rso", "aether", e["file"])
        raw = open(path, "rb").read()
        sha = hashlib.sha256(raw).hexdigest()
        src = raw.decode("utf-8")
        assert src.count(e["old"]) == 1
        try:
            open(path, "wb").write(src.replace(e["old"], e["new"]).encode("utf-8"))
            rc, tail, failing, ran = suite()
            w = witness(eid, dup6)
        finally:
            open(path, "wb").write(raw)
        restored = hashlib.sha256(open(path, "rb").read()).hexdigest() == sha
        gd = subprocess.run(["git", "diff", "--quiet", "--", path], cwd=ROOT).returncode == 0
        fz = run(PY + ["-m", "rso.aether.freeze", "check"])
        rows.append({"edit": eid + "h", "file": e["file"], "posthoc": True, "suite_rc": rc, "failing": failing, "ran": ran,
                     "result": "RED" if rc != 0 else "SURVIVES", "witness": w, "witness_baseline": base_w[eid],
                     "restored_sha256_ok": restored, "git_diff_quiet": gd, "freeze_check_after": fz[1].strip()})
        print(eid + "h", rows[-1]["result"], json.dumps(w), file=sys.stderr, flush=True)
    purge()
    with open(os.path.join(scratch, "edits_posthoc.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True, default=str) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
