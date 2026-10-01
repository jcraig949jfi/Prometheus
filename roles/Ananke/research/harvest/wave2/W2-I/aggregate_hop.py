"""Aggregate W2-I transplant outputs into hop_verdicts.csv / hop_verdicts.json.

Verdict rule (SIGNAL threshold is C1's lo99 > .55):
  native fails (native@d0 lo99 <= .55)          -> INDETERMINATE (no native law on fresh seeds)
  hop-matched = C1random@dh (RELAY/HOLD) or C1random@dh_inward (MAJ: sensors placed upstream)
  hop-matched lo99 > .55                         -> HOP-BOUND if C1random@d0 is not SIGNAL, else NO-COLLAPSE
  hop-matched lo99 <= .55 and hi99 < .60         -> TOPOLOGY-BOUND (fails with hops matched)
  otherwise                                      -> INDETERMINATE
'matched' also requires >= 80% of sensors at exactly d_h signal hops; else INDETERMINATE.
"""
import csv
import glob
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
O = HERE / "out"
cells = {}
for f in sorted(glob.glob(str(O / "*_*.json"))):
    name = pathlib.Path(f).stem
    mode, cid = name.split("_", 1)
    if mode not in ("main", "lite", "fact", "fact2", "hopscan", "clique", "ringlabels"):
        continue
    d = json.loads(pathlib.Path(f).read_text())
    c = cells.setdefault(cid, {k: d[k] for k in ("cell", "row_kind", "wave", "family", "topology", "radius",
                                                  "n_sites", "d0", "d_h", "dest_mode", "plastic_route",
                                                  "recorded_held", "recorded_held_lo99")})
    c.setdefault("conds", {}).update(d["conds"])
    c.setdefault("hops", {}).update(d["hops"])
    c.setdefault("cpu_s", 0.0)
    c["cpu_s"] += d["_compute"]["cpu_s"]


def frac_at(h, k):
    tot = sum(h.values())
    return h.get(str(k), 0) / tot if tot else 0.0


rows = []
for cid, c in cells.items():
    C = c["conds"]
    nat = C.get("native@d0")
    hm_name = "C1random@dh_inward" if c["family"] == "MAJ" else "C1random@dh"
    hm = C.get(hm_name)
    hm_hops = c["hops"].get(hm_name, {})
    target = 0 if c["family"] == "HOLD" else c["d_h"]
    matched = frac_at(hm_hops, target) >= 0.8 if hm else False
    r0 = C.get("C1random@d0")
    if nat is None or hm is None:
        v = "NOT_RUN"
    elif nat["lo99"] <= .55:
        v = "INDETERMINATE (no native signal)"
    elif not matched:
        v = "INDETERMINATE (hops not matched)"
    elif hm["lo99"] > .55:
        if c["family"] == "HOLD" or c["d0"] == c["d_h"] and c["topology"] != "global":
            v = "NO-COLLAPSE (task already 1-hop/no transport)"
        elif r0 is None:
            v = "HOP-BOUND (d0 transplant not run)"
        else:
            v = "NO-COLLAPSE" if r0["lo99"] > .55 else "HOP-BOUND"
    elif hm["hi99"] < .60:
        v = "TOPOLOGY-BOUND"
    else:
        v = "INDETERMINATE (wide CI)"
    # refinement for hop-matched failures (graph-variant decomposition, ring cells only)
    def lo(k):
        return C[k]["lo99"] if k in C else None
    dh_, d0_ = c["d_h"], c["d0"]
    refine = ""
    if v == "TOPOLOGY-BOUND":
        cl, sf, sr = lo("clique2x4_flatdist@d%d" % dh_), lo("schreier_flatdist@d%d" % dh_), lo("schreier_ringdist@d%d" % dh_)
        fd = lo("ring_flatdist@d%d" % d0_)
        if sr is not None and sr > .55 and fd is not None and (sf is None or sf < sr - .1):
            refine = "LATENCY-LABEL-BOUND (ring per-port delays; restored on a tree-like graph by ring labels)"
        elif cl is not None and cl > .55 and (sf is None or sf <= .55) and (sr is None or sr <= .55):
            refine = "CLUSTER-BOUND (fails on tree-like graphs at matched hops; passes on a clustered NON-lattice graph)"
        elif cl is not None:
            refine = "UNRESOLVED (no variant restores SIGNAL)"
    ret = None
    if nat and hm and nat["acc"] > .5:
        ret = round((hm["acc"] - .5) / (nat["acc"] - .5), 2)
    row = {"cell": cid, "kind": c["row_kind"], "wave": c["wave"], "family": c["family"], "topology": c["topology"],
           "r": c["radius"], "N": c["n_sites"], "d0": c["d0"], "d_h": c["d_h"], "dest_mode": c["dest_mode"],
           "recorded_held": None if c["recorded_held"] is None else round(c["recorded_held"], 3),
           "verdict": v, "refinement": refine, "hop_matched_cond": hm_name, "retention_hop_matched": ret}
    for k in ("native@d0", "C1random@d0", "C1random@dh", "C1random@dh_inward", "native@d4", "native@d6",
              "ring_relabel@d%d" % c["d0"], "ring_portshuffle@d%d" % c["d0"], "ring_flatdist@d%d" % c["d0"],
              "schreier_ringdist@d%d" % c["d_h"], "schreier_flatdist@d%d" % c["d_h"],
              "schreier_ringdist@d%d" % c["d0"], "clique2x4_flatdist@d%d" % c["d_h"],
              "clique2x4_flatdist@d%d" % c["d0"]):
        if k in C:
            kk = k.replace("@d%d" % c["d0"], "@d0").replace("@d%d" % c["d_h"], "@dh") if k not in (
                "native@d4", "native@d6", "native@d0") else k
            if k == "native@d0":
                kk = k
            row[kk] = "%.3f [%.3f]" % (C[k]["acc"], C[k]["lo99"])
            row[kk + "_hops"] = json.dumps(c["hops"].get(k, {}))
    rows.append(row)

order = {"RELAY": 0, "MAJ": 1, "HOLD": 2}
rows.sort(key=lambda r: (order.get(r["family"], 9), r["wave"] != "D", r["cell"]))
keys = []
for r in rows:
    for k in r:
        if k not in keys:
            keys.append(k)
with open(HERE / "hop_verdicts.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=keys)
    w.writeheader()
    w.writerows(rows)
tot_cpu = sum(c["cpu_s"] for c in cells.values())
(HERE / "hop_verdicts.json").write_text(json.dumps({"rows": rows, "transplant_cpu_s": round(tot_cpu, 1)}, indent=1))
import collections
print(collections.Counter(r["verdict"] for r in rows), "cpu_s", round(tot_cpu, 1))
for r in rows:
    print(r["cell"], r["wave"], r["family"], r["topology"], "d0", r["d0"], "dh", r["d_h"], "|",
          "nat", r.get("native@d0"), "| C1r@d0", r.get("C1random@d0"), "| C1r@dh", r.get("C1random@dh"),
          "| inward", r.get("C1random@dh_inward"), "|", r["verdict"], r["refinement"], "ret", r["retention_hop_matched"])
