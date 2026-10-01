"""W2-33 bit-exact replay of one recorded splice-on (BASE) run in a FRESH process.

usage: python -B replay.py <label> <seed> <harness: runner|run_cell> <expected_depth> [expected_p11]
Runs C9 arm-B physics for 7ae3 (cell as frozen, tier M) exactly as the named harness does, and
writes replay_<label>.json with depth, p11_events, recombinations, wall time and match flags.
"""
import json, pathlib, sys, time
HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parents[1] / "campaigns" / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
import world
SPEC = "7ae3f9c1437c8000-s54765-tL-a0"
label, seed, harness, exp_d = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
exp_p = int(sys.argv[5]) if len(sys.argv) > 5 else None
man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
genome = bytes.fromhex(arm["kwargs"]["implant_hex"])
t0 = time.time()
if harness == "runner":
    r = world.Runner(dict(arm["cell"]), seed, tier=arm["tier"], implant="ACTUAL_GENOME", implant_bytes=genome)
    out = r.run(); ct = r.ct
else:
    out = world.run_cell(dict(arm["cell"]), seed, tier=arm["tier"], implant="ACTUAL_GENOME",
                         implant_bytes=genome)["summary"]; ct = {}
rec = {"label": label, "seed": seed, "harness": harness, "depth": out["max_causal_replication_depth"],
       "p11_events": out["p11_events"], "epochs_run": out.get("epochs_run"),
       "recombinations": ct.get("recombinations"), "expected_depth": exp_d, "expected_p11": exp_p,
       "match_depth": out["max_causal_replication_depth"] == exp_d,
       "match_p11": None if exp_p is None else out["p11_events"] == exp_p,
       "wall_s": round(time.time() - t0, 1)}
(HERE / ("replay_%s.json" % label)).write_text(json.dumps(rec, indent=1))
print(json.dumps(rec))
