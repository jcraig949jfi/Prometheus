"""Verify the Lexis handoff without model judgment. Exit 0 = everything reproduces.

Checks, in order:
  1. the frozen pair's file hash matches the manifest (and the git blob, if git is present)
  2. the G7 instrument re-runs and reproduces the committed rows (controls, arms, dE/dS,
     recognition) -- notes/g7_charon_result.json
  3. build_handoff.py re-runs into a scratch dir and the three artifacts are byte-identical
     to the committed ones
  4. the frozen numbers this handoff is allowed to state are read back from the artifacts
     and asserted

Usage:  python roles/Lexis/handoff/verify_handoff.py
"""
from __future__ import annotations

import filecmp
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NOTES = HERE.parent / "notes"
INSTR = HERE.parent / "instruments"
PY = sys.executable
ENV = dict(os.environ, PYTHONHASHSEED="0")   # the home synth subset is hash-seed dependent


def fail(msg):
    print("FAIL  " + msg)
    return 1


def main():
    rc = 0
    manifest = json.loads((HERE / "interface_pair_manifest.json").read_text(encoding="utf-8"))

    # 1 ── hash pin
    sha = hashlib.sha256((INSTR / "candidate_primitives.py").read_bytes()
                         .replace(b"\r\n", b"\n")).hexdigest()
    if sha != manifest["source"]["sha256"]:
        rc |= fail("candidate_primitives.py sha256 %s != manifest %s" % (sha, manifest["source"]["sha256"]))
    else:
        print("ok    frozen pair sha256 %s" % sha)
    try:
        blob = subprocess.check_output(
            ["git", "rev-parse", "HEAD:roles/Lexis/instruments/candidate_primitives.py"],
            cwd=str(ROOT), text=True).strip()
        if manifest["source"]["git_blob"] and blob != manifest["source"]["git_blob"]:
            rc |= fail("git blob %s != manifest %s" % (blob, manifest["source"]["git_blob"]))
        else:
            print("ok    git blob %s" % blob)
    except Exception as e:                              # noqa: BLE001
        print("skip  git blob check (%s)" % type(e).__name__)

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        # 2 ── G7 instrument reproduces
        out = td / "g7.json"
        r = subprocess.run([PY, str(INSTR / "g7_remeasure.py"), "--out", str(out)],
                           capture_output=True, text=True, env=ENV)
        if r.returncode != 0:
            rc |= fail("g7_remeasure.py exit %d\n%s" % (r.returncode, r.stdout[-2000:]))
        else:
            new = json.loads(out.read_text(encoding="utf-8"))
            old = json.loads((NOTES / "g7_charon_result.json").read_text(encoding="utf-8"))
            keys = ["P1_home_known_organism_acc", "P2_charon_known_organism", "arms",
                    "solved", "dS_bound", "dE_bound", "per_category", "unrecognised",
                    "number_only", "transformers_never_firing", "all_but_n_pair_trace"]
            bad = [k for k in keys if new.get(k) != old.get(k)]
            if bad:
                rc |= fail("g7_remeasure.py rows differ from committed on: %s" % bad)
            else:
                print("ok    g7_remeasure.py reproduces the committed rows (%d keys)" % len(keys))

        # 3 ── build reproduces byte-identically
        r = subprocess.run([PY, str(HERE / "build_handoff.py"), "--out-dir", str(td)],
                           capture_output=True, text=True, env=ENV)
        if r.returncode != 0:
            rc |= fail("build_handoff.py exit %d\n%s" % (r.returncode, r.stderr[-2000:]))
        else:
            for name in ("interface_pair_manifest.json", "state_injection_fixture.json",
                         "consumer_utility_result.json"):
                if filecmp.cmp(td / name, HERE / name, shallow=False):
                    print("ok    %s byte-identical" % name)
                else:
                    rc |= fail("%s differs from committed" % name)

    # 4 ── frozen numbers
    fx = json.loads((HERE / "state_injection_fixture.json").read_text(encoding="utf-8"))
    s = fx["summary"]
    g7 = json.loads((NOTES / "g7_charon_result.json").read_text(encoding="utf-8"))
    home = json.loads((NOTES / "product_ceiling_clean.json").read_text(encoding="utf-8"))
    cu = json.loads((HERE / "consumer_utility_result.json").read_text(encoding="utf-8"))
    pair = g7["arms"]["C + compute + readout"]
    checks = [
        ("home ceiling 100/120", home["best_correct"] == 100 and home["n_tasks"] == 120),
        ("charon ceiling 2/42", g7["arms"]["baseline C"]["ceiling"] == 2 and g7["n_tasks"] == 42),
        ("charon dS = 0", len(g7["dS_bound"]) == 0),
        ("charon dE = 40/42", len(g7["dE_bound"]) == 40),
        ("15/42 unrecognised", s["unrecognised"] == 15),
        ("19/42 number-extraction only", s["number_extraction_only"] == 19),
        ("34/42 fail before the capability layer", s["fail_before_capability_layer"] == 34),
        ("compute alone +0", g7["arms"]["C + compute"]["dE"] == 0),
        ("readout alone +0", g7["arms"]["C + readout"]["dE"] == 0),
        ("pair +4 / +4 / +4 on charon", (pair["dE"], pair["dS"], pair["dROBUST"]) == (4, 4, 4)),
        ("pair: 4 correct, 2 wrong on all_but_n",
         sum(r["ok"] for r in g7["all_but_n_pair_trace"]) == 4
         and sum(r["wrong_guess"] for r in g7["all_but_n_pair_trace"]) == 2),
        ("bundle on charon (organism-level): ABSTAIN->CORRECT 4, ABSTAIN->WRONG 3",
         cu["batteries"]["charon"]["arms"]["+bundle readout_last"]["transitions"]
         .get("ABSTAIN->CORRECT") == 4
         and cu["batteries"]["charon"]["arms"]["+bundle readout_last"]["transitions"]
         .get("ABSTAIN->WRONG") == 3),
        ("compute alone regresses 9 home tasks CORRECT->WRONG (max_value write-write hazard)",
         cu["batteries"]["home"]["arms"]["+parse_numbers +compute"]["transitions"]
         .get("CORRECT->WRONG") == 9),
        ("compute_first placement: +5 CORRECT, 0 WRONG on the seed-0 home draw",
         cu["batteries"]["home"]["arms"]["+bundle compute_first"]["delta"]
         == {"CORRECT": 5, "ABSTAIN": -5, "WRONG": 0}),
        ("hash-seed sweep present (5 draws of the home synth subset)",
         len(cu.get("home_hashseed_sweep", {}).get("seeds", {})) == 5),
        ("charon break-even wrong penalty L* = 4/3",
         abs(cu["batteries"]["charon"]["arms"]["+bundle readout_last"]
             ["break_even_wrong_penalty"] - 4 / 3) < 1e-9),
    ]
    for label, ok in checks:
        if ok:
            print("ok    " + label)
        else:
            rc |= fail(label)
    print("\nVERIFY_HANDOFF: %s" % ("PASS" if rc == 0 else "FAIL"))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
