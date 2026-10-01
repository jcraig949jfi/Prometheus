"""W2-4 sufficiency: necessity per position does not show sufficiency of the set. Keep a candidate core set S, refill
every other position, and re-measure the five readouts against the wild type.

    python -B w4_suff.py   (after w4_run.py)  -> w4_suff.json

Sets per genome (from w4_results.json, initial position calls):
  S_conv  = CONV_NEC positions
  S_convp = CONV_NEC + CONV_PARTIAL
  S_est   = S_convp + EST_ONLY positions confirmed on re-assay (same value, fresh seeds)
  S_exec  = S_est + every byte of every instruction executed before the main copy (traced draw)
Refill: RANDOM (uniform random bytes, 4 draws per set; primary) and NOP (00; one draw; can be inflated by zero-painting,
FOR Q3, so it is secondary). Readouts are the w4_common.full readouts at the per-position N, ratio to the wild type.
"""
from __future__ import annotations

import json
import random
import time

import w4_common as W

OUT = W.HERE / "w4_suff.json"
NZ, NKID, NI, NCAR = 60, 5, 8, 60
ND = 4
t0 = time.process_time()


def sets(r):
    pos = r["pos"]
    conv = {x["p"] for x in pos if x["cls"] == "CONV_NEC"}
    convp = conv | {x["p"] for x in pos if x["cls"] == "CONV_PARTIAL"}
    est = convp | {x["p"] for x in pos if x["cls"] == "EST_ONLY" and x.get("re_same", {}).get("cls") == "EST_ONLY"}
    ex = set(est)
    if r.get("trace"):
        for p0, ln in r["trace"]["instr_before_copy"]:
            ex |= set(range(p0, min(64, p0 + ln)))
    return {"S_conv": sorted(conv), "S_convp": sorted(convp), "S_est": sorted(est), "S_exec": sorted(ex)}


def main():
    R = json.loads((W.HERE / "w4_results.json").read_text())["genomes"]
    out = []
    for r in R:
        if r["status"] != "OK":
            continue
        g = bytes.fromhex(r["hex"])
        cell = r["cell"]
        wt = r["wt"]
        S = sets(r)
        rec = {"id": r["id"], "grp": r["grp"], "sets": S, "res": {}}
        seen = {}
        for nm, s in S.items():
            key = tuple(s)
            if key in seen:
                rec["res"][nm] = seen[key]
                continue
            rows = []
            for d in range(ND + 1):
                rng = random.Random(repr(("SUFF", r["id"], nm, d)))
                if d < ND:
                    m = bytes(g[j] if j in s else rng.randrange(256) for j in range(64))
                    fill = "RANDOM"
                else:
                    m = bytes(g[j] if j in s else 0 for j in range(64))
                    fill = "NOP"
                x = W.full(m, cell, ("SUFF", nm, d), NZ, NKID, NI, NCAR)
                rows.append({"fill": fill, "Z": round(x["Z"], 4), "R": round(x["R"], 4), "K": x["K"],
                             "C": round(x["C"], 4), "P2": round(x["P2"], 4)})
            rnd = [x for x in rows if x["fill"] == "RANDOM"]

            def mean(k, rows=rnd):
                v = [x[k] for x in rows if x[k] is not None]
                return round(sum(v) / len(v), 4) if v else None
            summ = {"n": len(s), "rows": rows, "Z": mean("Z"), "C": mean("C"), "K": mean("K"), "R": mean("R"),
                    "P2": mean("P2"),
                    "Z_ratio": round(mean("Z") / wt["Z"], 3) if wt["Z"] else None,
                    "C_ratio": round(mean("C") / wt["C"], 3) if wt["C"] and wt["C"] >= 0.1 else None,
                    "K_ratio": round(mean("K") / wt["K"], 3) if (wt["K"] and wt["K"] >= 0.1 and mean("K") is not None) else None,
                    "P2_ratio": round(mean("P2") / wt["P2"], 3) if wt["P2"] and wt["P2"] >= 0.2 else None,
                    "draws_Z_ge_half": sum(1 for x in rnd if x["Z"] >= 0.5 * wt["Z"]),
                    "NOP": rows[-1]}
            seen[key] = summ
            rec["res"][nm] = summ
        out.append(rec)
        print(r["id"], {k: (v["n"], v["Z_ratio"], v["C_ratio"], v["K_ratio"], v["P2_ratio"]) for k, v in rec["res"].items()},
              round(time.process_time() - t0, 1), flush=True)
        OUT.write_text(json.dumps({"ND": ND, "genomes": out}, indent=0))
    print("cpu", round(time.process_time() - t0, 1))


if __name__ == "__main__":
    main()
