"""Step 1: the 128 panel copiers (ROWS with P11 certified on exactly one side, DENSE: 111 side-0 + 17 side-1),
CVT-R re-scored on both sides at the record seed (sid = hex; must reproduce ROWS exactly) and K = 8 reseeds
(sid = hex + ":reseed%d", j = 0..7; j = 0..3 coincide with W2-16 s3's RESEED). World-order RAND victims.
For every (genome, side, seed): original CVT-R accept and the repaired rule R* (see _cvtx.analyse)."""
import json, pathlib, sys, time
from _cvtx import A, ROWS, run_one

K = 8
OUT = pathlib.Path(__file__).with_suffix(".json")
LOG = pathlib.Path(__file__).with_suffix(".log")
KEEP = ("CVTR_accept", "CVTR_n", "CVTR_classes", "base_fid_floor_ok", "cr_variant_in_sig", "cr_inherited",
        "cr_variant_fid_ok", "RSTAR_accept", "RSTAR_n", "RSTAR_classes", "inherit_rate_variant_by_gen",
        "inherit_rate_base_by_gen")


def main():
    panel = [r for r in ROWS if r["vm"] == "DENSE" and r["P11"]["certified"] and len(r["P11"]["certified_sides"]) == 1]
    assert len(panel) == 128, len(panel)
    out, t0 = [], time.time()
    mism = 0
    for r in panel:
        G = bytes.fromhex(r["hex"])
        P = A.params(r["vm"], r["cell"]); _, _, z = A.env(r["vm"], r["cell"])
        rec = {"key": r["key"], "cell": r["cell"], "p11_side": r["P11"]["certified_sides"][0],
               "record_CVTR_accept_either": r["CVTR_accept"],
               "record_CVTR_by_side": {s: r["CVT"][s]["CVTR"]["accept"] for s in ("0", "1")}, "sides": {}}
        for side in (0, 1):
            seeds = [r["hex"]] + [r["hex"] + ":reseed%d" % j for j in range(K)]
            per = []
            for sid in seeds:
                o = run_one(G, r["vm"], r["cell"], side, sid, "RAND", P, z)
                per.append({k: o[k] for k in KEEP})
                if sid == r["hex"]:
                    if o["score"] != r["CVT"][str(side)]:
                        mism += 1
                    per[-1]["record_reproduced"] = o["score"] == r["CVT"][str(side)]
            rec["sides"][str(side)] = per
        out.append(rec)
        with open(LOG, "a") as fh:
            fh.write("%s %.0fs\n" % (r["key"], time.time() - t0))
    OUT.write_text(json.dumps({"K": K, "n": len(out), "record_mismatches": mism,
                               "cpu_seconds": round(time.time() - t0, 1), "rows": out}, indent=0))
    print("done", len(out), "mismatches", mism, round(time.time() - t0))


if __name__ == "__main__":
    main()
