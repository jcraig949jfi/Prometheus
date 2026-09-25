"""X-RUNAWAY-TRANSPLANT (EXPLORE, TRANSPLANT; child of C-RUNAWAY). Declared before running.

C-RUNAWAY confirmed, for specimen 7ae3's cell, that the recombination splice prevents runaway
causal heredity. Does that hold for the OTHER RECOMBINATION-axis specimens of the H2 panel?

Matched design against FROZEN data: for every RECOMBINATION-axis panel specimen, run arm B
(implanted donor genome, one founder, tier M) with atlas_axis NONE on EXACTLY C9's seeds
(9_200_000 + s, s < 16). The splice-on control is C9's frozen arm-B result for the same seed:
same code (freeze still verifies), same cell, same seed, only the splice differs.
Sanity gate first: one frozen arm-B run is replayed and must reproduce its frozen depth.
Readout per specimen: runaways (P-11 depth >= 20) and depth >= 5, splice off vs frozen on.
Classification: SIGNAL (transplants) if runaways appear (off) in >= 2 specimens other than
7ae3 with 0 in the frozen arm; CLEAN_NULL if no specimen other than 7ae3 shows any runaway;
WEAK_SIGNAL otherwise.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))


def frozen_armB():
    import run_campaign as R
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    out = {}
    for b in man["bundles"]:
        if b["hypothesis_id"] != "H2":
            continue
        arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
        if arm["cell"]["atlas_axis"] != "RECOMBINATION":
            continue
        res = json.loads((C9 / "observatory" / "bundles" / (R.spec_of(b).bundle_id + ".json")).read_text())
        out[(b["specimen"], arm["seed"])] = {"arm": arm, "frozen_depth":
                                            res["results"]["B_reimplant_actual"]["max_causal_replication_depth"]}
    return out


def job(args):
    key, arm, off = args
    import world
    cell = dict(arm["cell"], atlas_axis="NONE") if off else dict(arm["cell"])
    s = world.Runner(cell, arm["seed"], tier=arm["tier"], implant="ACTUAL_GENOME",
                     implant_bytes=bytes.fromhex(arm["kwargs"]["implant_hex"])).run()
    return {"specimen": key[0], "seed": key[1], "off": off, "depth": s["max_causal_replication_depth"]}


def main():
    fr = frozen_armB()
    k0 = sorted(fr)[0]
    sanity = job((k0, fr[k0]["arm"], False))
    ok = sanity["depth"] == fr[k0]["frozen_depth"]
    print("sanity replay of frozen arm B:", k0, sanity["depth"], "frozen", fr[k0]["frozen_depth"], "OK" if ok else "MISMATCH")
    if not ok:
        (HERE / "SUMMARY.json").write_text(json.dumps({"classification": "INVALID", "sanity": sanity,
                                                       "frozen": fr[k0]["frozen_depth"]}))
        return 1
    todo = [(k, v["arm"], True) for k, v in sorted(fr.items())]
    with mp.Pool(10, maxtasksperchild=1) as pool:
        res = pool.map(job, todo)
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    per = {}
    for r in res:
        d = per.setdefault(r["specimen"], {"off_runaway": 0, "on_runaway": 0, "off_d5": 0, "on_d5": 0, "off_max": 0, "on_max": 0})
        fd = fr[(r["specimen"], r["seed"])]["frozen_depth"]
        d["off_runaway"] += r["depth"] >= 20
        d["on_runaway"] += fd >= 20
        d["off_d5"] += r["depth"] >= 5
        d["on_d5"] += fd >= 5
        d["off_max"] = max(d["off_max"], r["depth"])
        d["on_max"] = max(d["on_max"], fd)
    others = [s for s in per if not s.startswith("7ae3")]
    n_tr = sum(1 for s in others if per[s]["off_runaway"] > 0 and per[s]["on_runaway"] == 0)
    any_other = sum(1 for s in others if per[s]["off_runaway"] > 0)
    cls = "SIGNAL" if n_tr >= 2 else ("CLEAN_NULL" if any_other == 0 else "WEAK_SIGNAL")
    out = {"classification": cls, "sanity_replay": "OK", "specimens": len(per), "per_specimen": per}
    (HERE / "SUMMARY.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
