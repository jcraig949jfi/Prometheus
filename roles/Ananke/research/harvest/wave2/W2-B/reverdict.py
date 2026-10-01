"""Re-apply attain.certify's FINAL verdict precedence to the saved rows of out/certify_c1.json (the run used
an earlier precedence that named a forced-and-never-crossing ruler DEGENERATE instead of UNREACHABLE).
No engine compute. usage: python reverdict.py  -> out/certify_c1_final.json"""
import json
import pathlib

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
src = json.loads((HERE / "out/certify_c1.json").read_text())
final = {}
for name, cert in src["certificates"].items():
    rows = cert["rows"]
    vals = np.array([r["value"] for r in rows])
    passed = np.array([r["passed"] for r in rows])
    n_prog = len({r["program"] for r in rows})
    forced = cert["forced"] if n_prog >= 2 else False
    bad = [r for r in rows if r["role"] in ("null", "adversary") and r["passed"]]
    nulls = [r for r in rows if r["role"] == "null"]
    plants = [r for r in rows if r["role"] == "plant"]
    if forced and not passed.any():
        v = "UNREACHABLE"
    elif forced or (passed.all() and nulls):
        v = "DEGENERATE"
    elif bad:
        v = "CHEATABLE"
    elif not passed.any():
        v = "UNREACHABLE" if plants else "NO_PLANT"
    elif any(r["passed"] for r in plants):
        v = "SOUND"
    else:
        v = "NO_PLANT"
    final[name] = {"verdict_run": cert["verdict"], "verdict_final": v, "attainable": cert["attainable"],
                   "eligibility": cert["eligibility"], "cheapest": cert["cheapest"], "forced": forced}
    print(f"{name:34s} run={cert['verdict']:12s} final={v}")
(HERE / "out/certify_c1_final.json").write_text(json.dumps(final, indent=1))
