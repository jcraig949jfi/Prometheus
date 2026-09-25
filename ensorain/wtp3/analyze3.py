"""WTP-03 report numbers: gate funnel per stratum, per-world and per-founder fractions, carrier-bias
check, crossover collapse on cap/cells vs cap/DL (PREREG_WTP03 s8). Writes runs/wtp03/analysis.json."""
import collections
import json
import os

import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "runs", "wtp03")


def _load(name):
    p = os.path.join(OUT, name)
    return json.load(open(p)) if os.path.exists(p) else None


def main():
    A, B, C, D = _load("waveA.json"), _load("waveB.json") or [], _load("waveC.json") or [], _load("waveD.json") or []
    out = dict(candidates=A["candidates"], gates=A["gates"], admitted=len(A["admitted"]))
    adm = A["admitted"]
    out["admission_rate"] = len(adm) / max(1, A["candidates"])
    out["lineages"] = len({a["root"] for a in adm})
    out["strata_admitted"] = dict(collections.Counter(a["stratum"] for a in adm))
    out["carriers"] = dict(collections.Counter(a["g"]["memory"].get("carrier") for a in adm))
    out["generators"] = dict(collections.Counter(a["g"]["substrate"]["gen"] for a in adm))
    out["learning_pays_in_life"] = sum(bool(a["pre"].get("learning_pays")) for a in adm)
    out["kappa"] = dict(collections.Counter(a["g"]["resource"].get("kappa") for a in adm))
    # per-world / per-founder detector fractions
    fr = {}
    for d in ("X1", "X6", "X3", "X4"):
        w = [r for r in B if any(f["det"] == d for f in r["flags"])]
        fr[d] = dict(worlds=len(w), lineages=len({r["root"] for r in w}))
    out["wave_b_flags"] = fr
    sd = [c for c in C if c["flag"]["det"] in ("X1", "X6") and c["status"] == "STRUCTURE-DEPENDENT"]
    out["sd_specimen_lineages"] = len({c["root"] for c in sd})
    out["sd_lineage_fraction"] = out["sd_specimen_lineages"] / max(1, out["lineages"])
    # carrier-bias check: does the winning structured substrate equal the carrier kind more often than chance?
    same = tot = 0
    for r in B:
        u = r["unit"]
        if u.get("status") != "OK":
            continue
        subs = {k: v for k, v in u["real"]["subs"].items() if v.get("status") == "OK" and v.get("n_floats", 0) >= 8
                and k in ("lowrank", "cp", "tt", "dct", "hybrid_al") and v["XC"]["interp"] is not None}
        if not subs:
            continue
        win = max(subs, key=lambda k: subs[k]["XC"]["interp"])
        tot += 1
        same += (win == r["carrier"])
    out["carrier_bias"] = dict(winner_equals_carrier=same, worlds=tot)
    # crossover collapse: CV of the boundary location across worlds, in cap/cells vs cap/DL
    locs = collections.defaultdict(list)
    for d in D:
        if d["kind"] != "crossover" or not d.get("boundary"):
            continue
        rows = d["sweeps"]["budget"]
        b = d["boundary"][0]["between"]
        mid = float(np.mean(b))
        DLs = [r["res"].get("DL") for r in rows]
        locs[tuple(d["flag"]["pair"])].append(dict(cap_over_cells=mid))
    out["crossover_boundaries"] = {str(k): v for k, v in locs.items()}
    json.dump(out, open(os.path.join(OUT, "analysis.json"), "w"), indent=1, default=str)
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
