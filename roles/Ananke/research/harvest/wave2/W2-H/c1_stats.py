"""(3) multiplicity, (5) selection / winner's curse, (6) seed reuse, on the recorded C1 rows (read-only).
Output out/c1_stats.json. numpy + scipy; prometheus.ananke.campaign/assays imported unchanged (torch import only)."""
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import collections
import gzip
import json
import math
import pathlib
import sys

import numpy as np
from scipy import stats as st

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
import w2h_stats as W  # noqa: E402
from prometheus.ananke import campaign as C, search, assays  # noqa: E402
from prometheus.ananke.rng import H_int  # noqa: E402

RUN = ROOT / "roles/Ananke/pte/c1_rows"
R = [json.loads(l) for l in gzip.open(RUN / "cells.jsonl.gz", "rt")]
cfg = C.CampaignConfig()
out = {}

# ------------------------------------------------------------------ (3a) SIGNAL multiplicity
held_rows = [r for r in R if r["kind"] in ("evolve", "transfer")]
Mh = collections.Counter(r["search"]["M_held"] for r in held_rows)
P = 32
q995 = 2.5758  # percentile bootstrap ~ normal
tq = st.t.ppf(0.995, P - 1)


def pvals(r, mu0):
    h = r["result"]["held"]
    m, lo, hi = h["acc"], h["lo99"], h["hi99"]
    se = (hi - lo) / (2 * q995)
    if se <= 1e-12:
        # all 32 pairs equal to m: P(all pairs >= m | mean <= mu0) <= (mu0/m)^32 (Markov per pair)
        return 1.0 if m <= mu0 else min(1.0, (mu0 / m) ** P), se
    return float(st.t.sf((m - mu0) / se, P - 1)), se


rows = []
for r in held_rows:
    p55, se = pvals(r, 0.55)
    p50, _ = pvals(r, 0.50)
    h = r["result"]["held"]
    rows.append({"cell": r["cell_id"], "wave": r["wave"], "kind": r["kind"], "fam": r["env"]["family"],
                 "acc": h["acc"], "lo99": h["lo99"], "se": se, "p55": p55, "p50": p50,
                 "SIGNAL": h["lo99"] > 0.55,
                 "t_lo99": h["acc"] - tq * se,              # t-interval lower bound at the same SE
                 })
n = len(rows)
sig = [x for x in rows if x["SIGNAL"]]
p55 = np.array([x["p55"] for x in rows])
p50 = np.array([x["p50"] for x in rows])
out["signal"] = {
    "n_tests": n, "M_held": dict(Mh), "n_SIGNAL": len(sig),
    "SIGNAL_by_wave": dict(collections.Counter(x["wave"] for x in sig)),
    "BH_q05_mu55": int(W.bh(p55, 0.05).sum()), "BH_q01_mu55": int(W.bh(p55, 0.01).sum()),
    "Holm_a01_mu55": int(W.holm(p55, 0.01).sum()), "Holm_a05_mu55": int(W.holm(p55, 0.05).sum()),
    "BH_q01_mu50": int(W.bh(p50, 0.01).sum()), "Holm_a01_mu50": int(W.holm(p50, 0.01).sum()),
    "SIGNAL_and_not_Holm01_mu55": [x["cell"] for x, k in zip(rows, W.holm(p55, 0.01)) if x["SIGNAL"] and not k],
    "SIGNAL_and_not_BH01_mu55": [x["cell"] for x, k in zip(rows, W.bh(p55, 0.01)) if x["SIGNAL"] and not k],
    "SIGNAL_lost_under_t_interval": [x["cell"] for x in sig if not x["t_lo99"] > 0.55],
    "expected_false_SIGNAL_if_all_at_boundary_mu55_alpha_005": n * 0.005,
    "nonSIGNAL_cells_with_acc_le_055": int(sum(x["acc"] <= 0.55 for x in rows)),
}
# A1 only (the census the report states per family)
a1 = [x for x in rows if x["wave"] == "A"]
pa = np.array([x["p55"] for x in a1])
out["signal"]["A1"] = {"n": len(a1), "SIGNAL": int(sum(x["SIGNAL"] for x in a1)),
                       "Holm01": int(W.holm(pa, 0.01).sum()), "BH01": int(W.bh(pa, 0.01).sum()),
                       "BH05": int(W.bh(pa, 0.05).sum())}
# per-cell margin of the SIGNAL call in SE units, for the replication gate
marg = np.array([(x["lo99"] - 0.55) / x["se"] if x["se"] > 0 else np.inf for x in sig])
out["signal"]["margin_SE_quantiles_SIGNAL"] = np.quantile(marg[np.isfinite(marg)], [0, .05, .1, .25, .5]).tolist()
out["signal"]["n_SIGNAL_margin_lt_1SE"] = int(np.sum(marg < 1))
out["signal"]["n_SIGNAL_margin_lt_2SE"] = int(np.sum(marg < 2))
keep = W.keep_prob(np.where(np.isfinite(marg), marg, 50), 0.0)
out["signal"]["expected_SIGNAL_lost_on_rerun_predictive"] = float(np.sum(1 - keep))

# ------------------------------------------------------------------ (3b) transect boundary null
B = [r for r in R if r["wave"] == "B"]
B2 = [r for r in R if r["wave"] == "B2"]


def n_tests(rows_, metric):
    g = {}
    for r in rows_:
        e = r["extra"]
        if metric == "acc" and r["kind"] != "evolve":
            continue
        if metric in ("sens", "emit") and "gen0" not in r["result"]:
            continue
        g.setdefault((r["env"]["family"], e["transect"], e["base"], e.get("track", "evo")), set()).add(e["level_index"])
    return sum(max(0, len(v) - 1) for v in g.values() if len(v) >= 3), len(g)


rng = np.random.default_rng(7)
tb = {}
for metric in ("acc", "plant", "sens", "emit"):
    get = C.METRICS[metric]
    usable = [r for r in B if not (metric == "acc" and r["kind"] != "evolve")
              and not (metric in ("sens", "emit") and "gen0" not in r["result"])]
    obs = C.detect_boundaries(cfg, usable, metric)
    nt, ng = n_tests(usable, metric)
    # permutation null: shuffle values across levels within each transect group (H0: no level effect)
    groups = collections.defaultdict(list)
    for r in usable:
        e = r["extra"]
        groups[(r["env"]["family"], e["transect"], e["base"], e.get("track", "evo"))].append(r)
    null_counts = []
    for it in range(200):
        fake = []
        for k, rs in groups.items():
            vals = [get(r) for r in rs]
            perm = rng.permutation(len(vals))
            for r, j in zip(rs, perm):
                rr = {"env": r["env"], "kind": r["kind"], "extra": r["extra"],
                      "result": {"held": {"acc": vals[j]}, "plant": {"acc": vals[j]},
                                 "gen0": {"frac_sensitive_any": vals[j], "frac_emitting": vals[j]}}}
                fake.append(rr)
        null_counts.append(len(C.detect_boundaries(cfg, fake, metric)))
    tb[metric] = {"tests": nt, "groups": ng, "observed_candidates": len(obs),
                  "perm_null_mean": float(np.mean(null_counts)), "perm_null_q95": float(np.quantile(null_counts, .95))}
out["transect"] = tb

# ------------------------------------------------------------------ (5) selection / winner's curse
ev = [r for r in R if r["kind"] == "evolve"]
gap = np.array([r["result"]["champ_train_final"] - r["result"]["held"]["acc"] for r in ev])
tr = np.array([r["result"]["champ_train_final"] for r in ev])
he = np.array([r["result"]["held"]["acc"] for r in ev])
out["selection"] = {"n": len(ev), "gap_mean": float(gap.mean()), "gap_median": float(np.median(gap)),
                    "gap_q": np.quantile(gap, [.05, .25, .5, .75, .95]).tolist(),
                    "gap_mean_when_held_gt_055": float(gap[he > .55].mean()),
                    "gap_mean_when_held_le_055": float(gap[he <= .55].mean()),
                    "frac_train_gt_held": float(np.mean(gap > 0))}
# fresh-world re-evaluation of champions selected on HELD lo99: wave C same-family transfer (no variant)
src = {r["cell_id"]: r for r in R}
ct = [r for r in R if r["wave"] == "C" and r["kind"] == "transfer" and not r["extra"].get("variant")
      and r["env"]["family"] == r["extra"]["source_family"]]
pairs_c = [(src[r["extra"]["source_cell"]]["result"]["held"]["acc"], r["result"]["held"]["acc"],
            src[r["extra"]["source_cell"]]["result"]["held"]["lo99"] > .55, r["result"]["held"]["lo99"] > .55,
            r["extra"]["source_cell"]) for r in ct]
out["selection"]["C_same_family_refresh"] = {
    "n": len(pairs_c), "mean_source_held": float(np.mean([a for a, *_ in pairs_c])),
    "mean_fresh_held": float(np.mean([b for _, b, *_ in pairs_c])),
    "mean_drop": float(np.mean([a - b for a, b, *_ in pairs_c])),
    "SIGNAL_kept": f"{sum(1 for _, _, s, f, _ in pairs_c if s and f)}/{sum(1 for _, _, s, *_ in pairs_c if s)}",
    "rows": [(c, round(a, 4), round(b, 4)) for a, b, _, _, c in pairs_c]}
# held-world / train-world seed disjointness per evolve cell (lead seeds only carry randomness)
coll = 0
cross = collections.Counter()
for r in ev:
    sp = search.SearchSpec(**r["search"])
    s = r["search_seed"]
    tr_ = set()
    for g in range(sp.gens):
        tr_ |= set(assays.world_seeds(H_int(s, search.TRAIN_NS, g), sp.M)[0::2])
    fi = set(assays.world_seeds(H_int(s, search.FINAL_NS), sp.M_final)[0::2])
    ho = set(assays.world_seeds(H_int(s, search.HELD_NS), sp.M_held)[0::2])
    coll += len(ho & (tr_ | fi))
    for x in ho:
        cross[x] += 1
out["selection"]["held_train_seed_overlap_total"] = coll
out["seeds"] = {"held_lead_seeds_shared_between_cells": sum(1 for v in cross.values() if v > 1)}
# search_seed reuse across rows
ss = collections.defaultdict(list)
for r in R:
    ss[r["search_seed"]].append(r)
dup = {k: v for k, v in ss.items() if len(v) > 1}
desc = collections.Counter()
ex = []
for k, v in dup.items():
    key = tuple(sorted({(x["wave"], x["kind"]) for x in v}))
    fams = sorted({x["env"]["family"] for x in v})
    desc[(key, len(fams) > 1)] += 1
    if len(ex) < 6:
        ex.append({"seed": k, "rows": [(x["wave"], x["kind"], x["env"]["family"], x["extra"].get("transect"),
                                        x["extra"].get("track"), x["extra"].get("base"),
                                        x["extra"].get("level_index"), x["extra"].get("rep"),
                                        x["physics"]["n_sites"]) for x in v]})
out["seeds"]["search_seed_dup_groups"] = len(dup)
out["seeds"]["dup_rows"] = sum(len(v) for v in dup.values())
out["seeds"]["dup_kinds"] = {str(k): v for k, v in desc.items()}
out["seeds"]["examples"] = ex
# do duplicated-seed B2 evolve rows across families have correlated held errors? (same held worlds)
pairs_dup = []
for k, v in dup.items():
    evs = [x for x in v if x["kind"] == "evolve"]
    for i in range(len(evs)):
        for j in range(i + 1, len(evs)):
            pairs_dup.append((evs[i]["result"]["held"]["acc"], evs[j]["result"]["held"]["acc"]))
out["seeds"]["dup_evolve_pairs"] = len(pairs_dup)
json.dump(out, open(HERE / "out" / "c1_stats.json", "w"), indent=1, default=str)
print(json.dumps({k: (v if k != "selection" else {kk: vv for kk, vv in v.items() if kk != "C_same_family_refresh"})
                  for k, v in out.items()}, indent=1, default=str)[:6000])
print(json.dumps(out["selection"]["C_same_family_refresh"], default=str)[:1500])
