"""Holm correction + classification per PLAN.md (no thresholds changed)."""
import glob, json, pathlib, sys
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[4]))
from prometheus.ananke import lens

def holm(ps, alpha=0.01):
    keys = sorted(ps, key=lambda k: ps[k]); m = len(keys); out = {}; ok = True
    for i, k in enumerate(keys):
        adj = min(1.0, max((m - ii) * ps[keys[ii]] for ii in range(i + 1)))
        out[k] = adj
    return out

rows = [json.load(open(f)) for f in sorted(glob.glob(str(HERE / "out/D_*.json"))) + sorted(glob.glob(str(HERE / "out/M2_*.json")))]
ps = {(r["name"], j): r["decoder_single"][str(j)]["p"] for r in rows for j in range(7)}
pp = {(r["name"], j): r["decoder_paired"][str(j)]["p"] for r in rows for j in range(7)}
hs, hp = holm(ps), holm(pp)
summ = []
for r in rows:
    n = r["name"]
    rr = [j for j in range(2, 7) if hs[(n, j)] < 0.01]
    rrp = [j for j in range(2, 7) if hp[(n, j)] < 0.01]
    dec_any = [j for j in range(1, 7) if hs[(n, j)] < 0.01]
    intj = [j for j in range(1, 7) if r["effective"][str(j)]["ci"][1] > 0]
    fb = r["frac_merged_by_end_of_trial_k_plus"]
    forgets = fb["1"] == 1.0
    diverges = r["frac_ever_merged"] < 0.5
    if rr: lab = "RETAINS-RECOVERABLE"
    elif intj: lab = "INTERFERES"
    elif forgets: lab = "FORGETS"
    elif diverges and not dec_any: lab = "DIVERGES-UNRECOVERABLE"
    else: lab = "MIXED"
    persist = sorted(c for c, d in r["carrier_pairs_differing"].items() if d["6"] > 0)
    summ.append({"name": n, "class": r["class"], "family": r["family"], "label": lab,
                 "RR_single_lags": rr, "RR_paired_lags": rrp, "INT_lags": intj,
                 "eff_frac": {j: r["effective"][str(j)]["frac"] for j in range(1, 7)},
                 "eff_lo99": {j: round(r["effective"][str(j)]["ci"][1], 3) for j in range(1, 7)},
                 "merged_by_k+1": fb["1"], "merged_by_k+6": fb["6"], "ever": r["frac_ever_merged"],
                 "persisting_carriers_j6": persist,
                 "paired_feature_j2..6": [r["decoder_paired"][str(j)]["feature"] for j in range(2, 7)],
                 "paired_acc_j2..6": [round(r["decoder_paired"][str(j)]["acc"], 3) for j in range(2, 7)],
                 "single_acc_j2..6": [round(r["decoder_single"][str(j)]["acc"], 3) for j in range(2, 7)],
                 "min_holm_single_j>=2": min(hs[(n, j)] for j in range(2, 7)),
                 "min_holm_paired_j>=2": min(hp[(n, j)] for j in range(2, 7)),
                 "normal_here": r["normal_here"][0]})
dec = any(s["label"] == "RETAINS-RECOVERABLE" for s in summ)
out = {"decision_nontrivial_retention_regime": dec, "rows": summ}
(HERE / "out/summary.json").write_text(json.dumps(out, indent=1))
for s in summ:
    print(f'{s["name"]:12s} {s["class"]:18s} {s["family"]:5s} {s["label"]:24s} m1={s["merged_by_k+1"]:.2f} m6={s["merged_by_k+6"]:.2f} ever={s["ever"]:.2f} '
          f'Hs={s["min_holm_single_j>=2"]:.3g} Hp={s["min_holm_paired_j>=2"]:.3g} RRp={s["RR_paired_lags"]} INT={s["INT_lags"]} pers={s["persisting_carriers_j6"]} pf={s["paired_feature_j2..6"][0]} pa={s["paired_acc_j2..6"]} sa={s["single_acc_j2..6"]}')
print("DECISION nontrivial retention regime (primary):", dec)
