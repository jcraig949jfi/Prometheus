"""W2-AC: does B2's family-free search-seed key (campaign.py:648) create spurious cross-family agreement?

B2 seed = H_int(cfg.seed, 0xB2, hash_str(transect), base, level_index, rep): no family, no track. So rows of
different families (and tracks) at the same transect/base/level/rep share: the census random-genome RNG stream,
the census world seeds (0xCE), the plant-viability world seeds (0x9147) and, for evolve rows, the train/final/held
world seeds. Physics differ across families (family-specific bases), so the coupling runs only through shared
engine-noise draws keyed (ws, stream, t, site) and through a shared random-genome stream prefix.

Test: residual r = value - mean(value | family, transect, base, track, level) across the 3 reps. Correlate the
residuals of family pairs at MATCHED rep (same seeds) vs MISMATCHED rep (different seeds; null). Also check
genome-stream identity directly (numpy only) and list cross-family boundary agreements whose B2 reproductions
share seeds. CPU, numpy only.
"""
from __future__ import annotations

import collections
import gzip
import itertools
import json
import os
import pathlib

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
R = [json.loads(l) for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt")]
V = json.load(open(ROOT / "roles/Ananke/pte/c1_rows/boundaries_verdicts.json"))
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)

MET = {
    "plant": lambda r: r["result"]["plant"]["acc"],
    "sens": lambda r: r["result"]["gen0"]["frac_sensitive_any"] if "gen0" in r["result"] else None,
    "emit": lambda r: r["result"]["gen0"]["frac_emitting"] if "gen0" in r["result"] else None,
    "acc_mean_random": lambda r: r["result"]["gen0"]["acc_mean"] if "gen0" in r["result"] else None,
    "held_acc": lambda r: r["result"]["held"]["acc"] if "held" in r["result"] else None,
}
B2 = [r for r in R if r["wave"] == "B2"]
cell = collections.defaultdict(dict)  # (fam, transect, base, track, level) -> rep -> row
for r in B2:
    e = r["extra"]
    cell[(r["env"]["family"], e["transect"], e["base"], e["track"], e["level_index"])][e["rep"]] = r

res = {"seed_groups": {}}
seedg = collections.defaultdict(list)
for r in B2:
    seedg[r["search_seed"]].append(r)
res["seed_groups"]["n_seeds"] = len(seedg)
res["seed_groups"]["multi_family"] = sum(1 for v in seedg.values() if len({x["env"]["family"] for x in v}) > 1)
res["seed_groups"]["same_family_cross_track"] = sum(
    1 for v in seedg.values() if len({(x["env"]["family"], x["extra"]["track"]) for x in v}) > len({x["env"]["family"] for x in v}))

out = {}
for m, get in MET.items():
    resid = {}
    for k, reps in cell.items():
        vals = {rep: get(r) for rep, r in reps.items()}
        if any(v is None for v in vals.values()) or len(vals) < 3:
            continue
        mu = np.mean(list(vals.values()))
        for rep, v in vals.items():
            resid[k + (rep,)] = v - mu
    # family pairs at the same (transect, base, level); matched rep vs mismatched rep
    byloc = collections.defaultdict(dict)
    for (f, t, b, tr, lv, rep), x in resid.items():
        byloc[(t, b, lv)].setdefault((f, tr), {})[rep] = x
    mat, mis = [], []
    for loc, d in byloc.items():
        for (a, b) in itertools.combinations(sorted(d), 2):
            if a[0] == b[0]:
                continue
            for i in range(3):
                for j in range(3):
                    if i in d[a] and j in d[b]:
                        (mat if i == j else mis).append((d[a][i], d[b][j]))
    def corr(p):
        if len(p) < 4:
            return None
        x = np.array(p)
        if x[:, 0].std() == 0 or x[:, 1].std() == 0:
            return "zero-variance"
        return round(float(np.corrcoef(x.T)[0, 1]), 3)
    # permutation p for matched corr (shuffle rep labels within location)
    out[m] = {"matched_pairs": len(mat), "matched_r": corr(mat), "mismatched_pairs": len(mis), "mismatched_r": corr(mis)}
    if len(mat) >= 4 and isinstance(corr(mat), float):
        # NOTE: residuals are zero-sum over the 3 reps of a cell, so the mismatched sum is algebraically
        # -1x the matched sum; it is NOT a null. Null = random permutation of family-b rep labels per location pair.
        rng = np.random.default_rng(1)
        obs = corr(mat)
        pairs_loc = []
        for loc, d in byloc.items():
            for (a, b) in itertools.combinations(sorted(d), 2):
                if a[0] != b[0] and all(i in d[a] and i in d[b] for i in range(3)):
                    pairs_loc.append((np.array([d[a][i] for i in range(3)]), np.array([d[b][i] for i in range(3)])))
        perms = [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]
        null = []
        for _ in range(4000):
            xs, ys = [], []
            for xa, xb in pairs_loc:
                p = perms[rng.integers(6)]
                xs.append(xa); ys.append(xb[list(p)])
            X, Y = np.concatenate(xs), np.concatenate(ys)
            if X.std() > 0 and Y.std() > 0:
                null.append(np.corrcoef(X, Y)[0, 1])
        null = np.array(null)
        out[m]["perm_p_two_sided"] = round(float(np.mean(np.abs(null) >= abs(obs) - 1e-12)), 4)
        out[m]["perm_null_sd"] = round(float(null.std()), 3)
        out[m]["location_pairs"] = len(pairs_loc)
res["residual_corr"] = out

# genome-stream identity: census rows of different families sharing a seed
ident = []
for s, v in seedg.items():
    cen = [x for x in v if x["kind"] == "census"]
    for a, b in itertools.combinations(cen, 2):
        if a["env"]["family"] == b["env"]["family"]:
            continue
        pa, pb = a["physics"], b["physics"]
        ga = np.random.default_rng(s).integers(0, 256, size=(64, pa["rules"], pa["prog_len"], 5))
        gb = np.random.default_rng(s).integers(0, 256, size=(64, pb["rules"], pb["prog_len"], 5))
        same_shape = ga.shape == gb.shape
        ident.append({"seed": s, "fams": (a["env"]["family"], b["env"]["family"]), "transect": a["extra"]["transect"],
                      "same_genome_shape": same_shape,
                      "identical_genomes": bool(same_shape and (ga == gb).all()),
                      "same_topology": pa["topology"] == pb["topology"], "same_n_sites": pa["n_sites"] == pb["n_sites"]})
res["genome_identity"] = {"pairs": len(ident), "identical_genomes": sum(x["identical_genomes"] for x in ident),
                          "by_transect": {f"{k[0]}|{k[1]}": v for k, v in collections.Counter((x["transect"], x["identical_genomes"]) for x in ident).items()}}

# cross-family boundary agreements and whether their B2 reproductions share seeds
agree = collections.defaultdict(list)
for v in V:
    agree[(v["dial"], v["metric"], v["track"])].append((v["family"], v["base"], v["label"][15:], v["fresh_seed_reproduced"]))
cf = {}
for k, lst in agree.items():
    fams = {x[0] for x in lst}
    if len(fams) > 1:
        # B2 seeds of these transects
        seeds = collections.defaultdict(set)
        for r in B2:
            e = r["extra"]
            if e["transect"] == k[0] and e["track"] == k[2] and r["env"]["family"] in fams:
                seeds[r["env"]["family"]].add(r["search_seed"])
        shared = set.intersection(*seeds.values()) if len(seeds) > 1 else set()
        cf[str(k)] = {"verdicts": lst, "families_with_B2": sorted(seeds), "shared_B2_seeds": len(shared),
                      "B2_seeds_per_family": {f: len(s) for f, s in seeds.items()}}
res["cross_family_agreements"] = cf
json.dump(res, open(OUT / "b2_shared.json", "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
