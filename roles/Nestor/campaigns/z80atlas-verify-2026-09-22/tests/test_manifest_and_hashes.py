"""T-MAN and T-HASH: manifest validation and hash reproducibility (pre-freeze gates).

T-MAN   the generated manifest validates (every arm a valid cell, every bundle honest
        about its cardinality), H4 is absent, H1/H2/H3 have the ruled sizes, every H2
        arm B carries embedded implant bytes, and every H3 arm B keeps RESERVOIR.
T-HASH  every proposed hash is recomputed in THREE fresh processes with different
        PYTHONHASHSEED values and must agree; PROPOSED_HASHES.json must equal the
        recomputation (a stale file is caught).

Run:  python tests/test_manifest_and_hashes.py    Exit 0 all pass, 1 otherwise.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import manifest as M     # noqa: E402

PROBE = ("import json,sys; sys.path.insert(0, %r); import proposed_hashes as P; "
         "b,p,m,bad,pan=P.compute(); print(json.dumps(dict(b, proposed_protocol_hash=p)))")


def main():
    ok = True

    def rec(name, good, detail):
        nonlocal ok
        ok &= bool(good)
        print("%-6s %-44s %s" % ("PASS" if good else "FAIL", name, detail))

    m = M.build()
    by = m["by_hypothesis"]
    runs = {h: sum(b["expected_cardinality"] for b in m["bundles"] if b["hypothesis_id"] == h)
            for h in ("H1", "H2", "H3", "H4")}
    rec("T-MAN validate()", not M.validate(m), "%d problems" % len(M.validate(m)))
    rec("T-MAN H4 withheld", by["H4"] == 0 and runs["H4"] == 0, "H4 bundles %d" % by["H4"])
    rec("T-MAN ruled sizes", runs == {"H1": 240, "H2": 768, "H3": 192, "H4": 0}, str(runs))
    h2b = [a for b in m["bundles"] if b["hypothesis_id"] == "H2" for a in b["arms"]
           if a["arm"] == "B_reimplant_actual"]
    rec("T-MAN H2 arm B bytes embedded", h2b and all(a["kwargs"].get("implant_hex") for a in h2b),
        "%d arm-B runs" % len(h2b))
    h3b = [a for b in m["bundles"] if b["hypothesis_id"] == "H3" for a in b["arms"]
           if a["arm"] == "B_homogeneous_same_migration"]
    rec("T-MAN H3 arm B identical migration", h3b and all(
        a["cell"]["structure"] == "RESERVOIR" and a["kwargs"].get("easy_niche_disabled") for a in h3b),
        "%d arm-B runs" % len(h3b))
    rec("T-MAN total", m["n_runs"] == 1200, "n_runs %d" % m["n_runs"])

    outs = []
    for seed in ("0", "1", "12345"):
        env = dict(os.environ, PYTHONHASHSEED=seed)
        p = subprocess.run([sys.executable, "-c", PROBE % str(ROOT)], capture_output=True,
                           text=True, env=env, cwd=ROOT)
        outs.append(json.loads(p.stdout.strip().splitlines()[-1]) if p.returncode == 0 else None)
    same = all(o is not None and o == outs[0] for o in outs)
    rec("T-HASH 3 processes, 3 hash seeds agree", same,
        "protocol %s.." % ((outs[0] or {}).get("proposed_protocol_hash", "?")[:16]))
    f = json.loads((ROOT / "PROPOSED_HASHES.json").read_text())
    stale = [k for k in ("proposed_protocol_hash", "manifest_hash", "specimen_panel_hash",
                         "grammar_hash", "constants_sha256")
             if outs[0] and f.get(k) != outs[0].get(k)]
    rec("T-HASH PROPOSED_HASHES.json is current", outs[0] and not stale, "stale: %s" % (stale or "none"))
    print("T-MAN/T-HASH:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
