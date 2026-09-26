"""Reduce `aeth02_closure.py` outputs to the H2/H3 closure tables.

Reads every `closure_n*_s*.json` in a directory and prints one JSON
document with the pooled numbers the closure section quotes. Pure
reduction: no lattice is stepped here, so any figure in the report can be
regenerated from the committed evidence alone.
"""

import argparse
import glob
import json
import math
import os

FIELDS = ("opcode", "arg0", "arg1", "payload", "energy")


def wilson(k, n, z=1.96):
    if not n:
        return None
    p = k / float(n)
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [p, c - h, c + h]


def reduce_h3(runs):
    out = {"per_run": [], "pooled": {}}
    tot = {"real": 0, "nullA": 0.0, "nullB": 0, "samples": 0}
    by_field = {k: [0.0] * 5 for k in ("real", "nullA", "nullB", "sources")}
    sc_all = {f: [0, 0] for f in FIELDS}
    sc_cyc = {f: [0, 0] for f in FIELDS}
    lengths = {}
    persist = {"on_cycle": {}, "off_cycle": {}}
    relax = {}
    for r in runs:
        real = [s["cycle_nodes"] for s in r["h3_samples"]]
        na = [sum(s["nullA_cycle_nodes"]) / len(s["nullA_cycle_nodes"])
              for s in r["h3_samples"]]
        nb = [s["nullB_cycle_nodes"] for s in r["h3_samples"]]
        out["per_run"].append({
            "n": r["n"], "seed_index": r["seed_index"],
            "samples": len(real),
            "real_mean": sum(real) / len(real),
            "nullA_mean": sum(na) / len(na),
            "nullB_mean": sum(nb) / len(nb),
            "real_over_nullA": sum(real) / sum(na),
            "real_over_nullB": sum(real) / float(sum(nb)),
            "mapped_nodes_mean": sum(s["mapped_nodes"] for s in r["h3_samples"])
            / len(real)})
        tot["real"] += sum(real)
        tot["nullA"] += sum(na)
        tot["nullB"] += sum(nb)
        tot["samples"] += len(real)
        for s in r["h3_samples"]:
            k = len(s["nullA_by_field"])
            for f in range(5):
                by_field["real"][f] += s["cycle_edges_by_field"][f]
                by_field["nullA"][f] += sum(x[f] for x in s["nullA_by_field"]) / k
                by_field["nullB"][f] += s["nullB_by_field"][f]
                by_field["sources"][f] += s["sources_by_field"][f]
            for f in FIELDS:
                for acc, key in ((sc_all, "state_changing_all"),
                                 (sc_cyc, "state_changing_cycle")):
                    acc[f][0] += s[key][f][0]
                    acc[f][1] += s[key][f][1]
            for L, c in s["cycle_lengths"].items():
                lengths[L] = lengths.get(L, 0) + c
        for lab in ("on_cycle", "off_cycle"):
            for key, (k, n) in r["h3_one_tick_persistence"][lab].items():
                a = persist[lab].setdefault(key, [0, 0])
                a[0] += k
                a[1] += n
        for rl in r["h3_relaxation"]:
            for pt in rl["series"]:
                a = relax.setdefault(pt["t"], {"cycle_nodes": 0, "per_field": [0] * 5,
                                               "k": 0})
                a["cycle_nodes"] += pt["cycle_nodes"]
                a["per_field"] = [x + y for x, y in zip(a["per_field"], pt["per_field"])]
                a["k"] += 1
            a = relax.setdefault("realized_at_fork", {"cycle_nodes": 0, "k": 0})
            a["cycle_nodes"] += rl["realized_cycle_nodes"]
            a["k"] += 1
    out["pooled"] = {
        "samples": tot["samples"],
        "real_cycle_nodes_total": tot["real"],
        "real_over_nullA": tot["real"] / tot["nullA"],
        "real_over_nullB": tot["real"] / float(tot["nullB"]),
        "cycle_edges_by_field": {
            FIELDS[f]: {"real": by_field["real"][f], "nullA": by_field["nullA"][f],
                        "nullB": by_field["nullB"][f],
                        "real_over_nullA": (by_field["real"][f] / by_field["nullA"][f]
                                            if by_field["nullA"][f] else None),
                        "real_over_nullB": (by_field["real"][f] / by_field["nullB"][f]
                                            if by_field["nullB"][f] else None),
                        "share_of_sources": by_field["sources"][f]
                        / sum(by_field["sources"])}
            for f in range(5)},
        "state_changing": {
            f: {"all": wilson(*sc_all[f]), "on_cycle": wilson(*sc_cyc[f]),
                "edges_all": sc_all[f][1], "edges_on_cycle": sc_cyc[f][1]}
            for f in FIELDS},
        "state_changing_pooled": {
            "all": wilson(sum(v[0] for v in sc_all.values()),
                          sum(v[1] for v in sc_all.values())),
            "on_cycle": wilson(sum(v[0] for v in sc_cyc.values()),
                               sum(v[1] for v in sc_cyc.values()))},
        "cycle_lengths": dict(sorted(lengths.items(), key=lambda kv: int(kv[0]))),
        "one_tick_persistence": {
            lab: {key: wilson(*v) + [v[1]] if v[1] else None
                  for key, v in d.items()} for lab, d in persist.items()},
        "relaxation_mean_cycle_nodes": {
            str(t): v["cycle_nodes"] / v["k"] for t, v in relax.items()},
        "relaxation_per_field_t1_t10_t60": {
            str(t): [x / relax[t]["k"] for x in relax[t]["per_field"]]
            for t in (1, 10, 60) if t in relax},
    }
    return out


def reduce_h2(runs):
    out = {}
    for r in runs:
        key = "n%d_s%d_w%d" % (r["n"], r["seed_index"], r["warmup"])
        out[key] = {f: {k: v[k] for k in (
            "edges_at_risk", "observed_ge64", "hazard_total", "hazard_by_cause",
            "naive_pred_ge64", "naive_ratio",
            "conditioned_memoryless_pred_ge64", "conditioned_memoryless_ratio",
            "conditioned_energy_pred_ge64", "conditioned_energy_ratio",
            "life_table_selfcheck_ge64", "energy_persistence_at")}
            for f, v in r["h2"].items()}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--n", type=int, default=None, help="only this lattice size")
    a = ap.parse_args(argv)
    runs = []
    for d in a.dirs:
        for p in sorted(glob.glob(os.path.join(d, "closure_n*_s*.json"))):
            with open(p, encoding="utf-8") as fh:
                r = json.load(fh)
            if a.n is None or r["n"] == a.n:
                runs.append(r)
    print(json.dumps({"runs": [(r["n"], r["seed_index"], r["warmup"]) for r in runs],
                      "h2": reduce_h2(runs), "h3": reduce_h3(runs)},
                     indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
