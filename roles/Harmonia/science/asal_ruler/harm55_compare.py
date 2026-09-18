"""HARM-55: torch-port vs original-Flax observer comparison on the SAME 395 preserved rollouts.
Written and committed BEFORE any Flax score exists (operator review 2026-09-18 pt 2 + follow-up).

Input: a JSON/CSV from Techne mapping rollout key ("S0_212", ...) -> Flax open-endedness score, plus the
Flax path identity. Output: absolute error, crossing agreement at both thresholds, Spearman rank correlation,
identities/classes of the lowest scorers under each observer, and the PAIRWISE DISCORDANCE TABLE near both
decision boundaries (band preregistered here: +/- 0.01 around 0.8167 and around 0.7999, on the torch score).

    python harm55_compare.py --flax flax_scores.json [--band 0.01]
"""
import argparse, json, os, itertools
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "out", "run_2026-09-18", "search", "rows.jsonl")
THRESH = {"mean": 0.816686, "2sd": 0.816686 - 2 * 0.008363}
BAND = 0.01  # preregistered before any Flax score is read


def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--flax", required=True); ap.add_argument("--band", type=float, default=BAND); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    rows = {f"{r['stage']}_{r['idx']}": r for r in (json.loads(l) for l in open(ROWS)) if r.get("alive") and r.get("score") is not None}
    fx = json.load(open(a.flax))
    flax = fx["scores"] if "scores" in fx else fx
    keys = [k for k in rows if k in flax]
    missing = [k for k in rows if k not in flax]
    t = np.array([rows[k]["score"] for k in keys]); f = np.array([float(flax[k]) for k in keys])
    res = {"n_compared": len(keys), "n_missing_flax": len(missing), "flax_identity": fx.get("identity"), "band": a.band,
           "abs_error": {"max": float(np.abs(t - f).max()), "mean": float(np.abs(t - f).mean()), "p95": float(np.percentile(np.abs(t - f), 95))},
           "spearman": spearman(t, f), "crossing": {}, "lowest": {}, "discordance": {}}
    for name, th in THRESH.items():
        ct, cf = t < th, f < th
        res["crossing"][name] = {"threshold": th, "torch_crossers": int(ct.sum()), "flax_crossers": int(cf.sum()), "agree": int((ct == cf).sum()),
                                 "torch_only": [keys[i] for i in np.where(ct & ~cf)[0]], "flax_only": [keys[i] for i in np.where(~ct & cf)[0]],
                                 "min_torch": float(t.min()), "min_flax": float(f.min()), "flax_min_above_threshold": bool(f.min() >= th)}
    for obs, arr in (("torch", t), ("flax", f)):
        order = np.argsort(arr)[:10]
        res["lowest"][obs] = [{"key": keys[i], "score": float(arr[i]), "class": rows[keys[i]]["class"], "ic": rows[keys[i]]["ic"]} for i in order]
    res["best_crosser_identity_preserved"] = res["lowest"]["torch"][0]["key"] == res["lowest"]["flax"][0]["key"]
    res["best_crosser_class_preserved"] = res["lowest"]["torch"][0]["class"] == res["lowest"]["flax"][0]["class"]
    # pairwise discordance near each boundary: pairs with both torch scores within +/- band of the threshold
    for name, th in THRESH.items():
        idx = [i for i in range(len(keys)) if abs(t[i] - th) <= a.band]
        pairs = list(itertools.combinations(idx, 2))
        disc = [(i, j) for i, j in pairs if np.sign(t[i] - t[j]) != np.sign(f[i] - f[j]) and t[i] != t[j]]
        by_class = {}
        for i, j in disc:
            k = tuple(sorted((rows[keys[i]]["class"], rows[keys[j]]["class"]))); by_class["|".join(k)] = by_class.get("|".join(k), 0) + 1
        straddle = [(i, j) for i, j in disc if (t[i] < th) != (t[j] < th)]
        res["discordance"][name] = {"n_in_band": len(idx), "n_pairs": len(pairs), "n_discordant": len(disc),
                                    "discordance_rate": (len(disc) / len(pairs)) if pairs else None,
                                    "n_discordant_pairs_straddling_threshold": len(straddle), "by_class_pair": by_class,
                                    "by_distance_to_threshold": {f"<{d}": sum(1 for i, j in disc if max(abs(t[i] - th), abs(t[j] - th)) < d) for d in (0.0025, 0.005, 0.01)},
                                    "examples": [{"a": keys[i], "b": keys[j], "torch": [float(t[i]), float(t[j])], "flax": [float(f[i]), float(f[j])]} for i, j in disc[:10]]}
    out = a.out or os.path.join(HERE, "out", "run_2026-09-18", "harm55_comparison.json")
    json.dump(res, open(out, "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in res.items() if k not in ("lowest",)}, indent=1)); print("written", out)


if __name__ == "__main__":
    main()
