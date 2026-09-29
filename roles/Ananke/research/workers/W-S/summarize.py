"""W-S summary: per (spec, offset, phase) census + predictor accuracies (PLAN s4) -> out/summary.{json,txt}."""
import json, pathlib, sys
from collections import Counter
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[4]))
sys.path.insert(0, str(HERE))
import numpy as np
import analyze as A

OUT = HERE / "out"
UNITS = {("c_2dccdaa5", 5, 0): "U1", ("c_c16d5231", 4, 0): "U2", ("c_c16d5231", 5, 0): "U3", ("c_8c37f32e", 5, 0): "U4"}
PREDS = ["P3_cone", "P1_first", "P2_dflight", "P4_last", "P5_dleaf", "P6_share", "P7_stale", "H3_loo"]


def fmt(r):
    if not r or r.get("acc") is None:
        return "n0"
    lo, hi = r["ci99"]
    return f"{r['acc']:.2f} [{lo:.2f},{hi:.2f}] n{r['n']}"


def block(rows):
    pat = np.array([r["pat"] for r in rows])
    pair = np.array([r["pair"] for r in rows])
    preds = {k: np.array([r[k] for r in rows]) for k in PREDS[:6]}
    preds["P7_stale"] = np.array(["S" if r["y_same_prev"] else "C" for r in rows])
    preds["H3_loo"] = A.loo_pair_majority(pat, pair)
    out = {"n": len(rows), "census": dict(Counter(pat.tolist())),
           "census_tgt": dict(Counter(r.get("pat_tgt") for r in rows))}
    sc = np.isin(pat, ("S", "C"))
    out["majority_rate"] = float(max(np.mean(pat[sc] == "S"), np.mean(pat[sc] == "C"))) if sc.any() else None
    for k, pr in preds.items():
        strict = A.accuracy(pr, pat, pair)
        dec = np.isin(pr, ("S", "C"))
        decisive = A.accuracy(pr[dec], pat[dec], pair[dec])
        cov = float(np.mean(dec[sc])) if sc.any() else None
        sh = A.accuracy(A.shuffled(pr, pat, 0), pat, pair)
        shd = A.accuracy(A.shuffled(pr[dec], pat[dec], 0), pat[dec], pair[dec])
        out[k] = {"strict": strict, "decisive": decisive, "coverage": cov, "shuffled_strict": sh,
                  "shuffled_decisive": shd,
                  "xtab": {f"{a}>{b}": c for (a, b), c in sorted(Counter(zip(pat.tolist(), pr.tolist())).items())}}
    m = preds["P3_cone"] == "M"
    out["P7b_stale_on_M"] = A.accuracy(preds["P7_stale"][m], pat[m], pair[m])
    out["P7b_shuffled"] = A.accuracy(A.shuffled(preds["P7_stale"][m], pat[m], 0), pat[m], pair[m])
    # H2 / jitter descriptives on S/C pair-trials
    d = {}
    for key in ("first_from_source", "first_dist", "first_jit", "first_jit_cross", "first_sib_split", "first_arr_rel",
                "first_te_rel", "y_same_prev"):
        d[key] = {f"{r['pat']}|{r.get(key)}": 0 for r in rows}
        d[key] = dict(sorted(Counter(f"{r['pat']}|{r.get(key)}" for r in rows if r["pat"] in ("S", "C")).items()))
    out["descr"] = d
    out["n_direct_mean"] = {p: float(np.mean([r["n_direct"] for r in rows if r["pat"] == p])) for p in ("S", "C") if (pat == p).any()}
    out["n_direct_flight_mean"] = {p: float(np.mean([r["n_direct_flight"] for r in rows if r["pat"] == p])) for p in ("S", "C") if (pat == p).any()}
    out["n_direct_held_mean"] = {p: float(np.mean([r["n_direct_held"] for r in rows if r["pat"] == p])) for p in ("S", "C") if (pat == p).any()}
    if rows and "fa_eq_chan" in rows[0]:
        out["causal"] = {p: {"fa_eq_chan": float(np.mean([r["fa_eq_chan"] for r in rows if r["pat"] == p])),
                             "sa_eq_site": float(np.mean([r["sa_eq_site"] for r in rows if r["pat"] == p]))}
                         for p in ("S", "C", "N") if (pat == p).any()}
    return out


def main(tags):
    res, lines = {}, []
    for tag in tags:
        d = json.loads((OUT / f"rows_{tag}.json").read_text())
        res[tag] = {"KA_L": d["KA_L"], "KA_L_mustfail": d["KA_L_mustfail_te_plus1"], "normal_acc": d["normal_acc"],
                    "wall_s": d["wall_s"], "blocks": {}}
        lines.append(f"== {tag} normal {d['normal_acc']:.3f} KA_L {d['KA_L']} mustfail {d['KA_L_mustfail_te_plus1']} wall {d['wall_s']:.0f}s")
        for o in d["offsets"]:
            for q in (0, 1):
                rows = [r for r in d["rows"] if r["o"] == o and r["q"] == q]
                if not rows:
                    continue
                b = block(rows)
                unit = UNITS.get(("c_" + tag.split("_")[-1], o, q), "")
                res[tag]["blocks"][f"o{o}q{q}"] = b
                lines.append(f"-- o{o} q{q} {unit} n{b['n']} census {b['census']} tgt {b['census_tgt']} maj {b['majority_rate']}")
                for k in PREDS:
                    x = b[k]
                    lines.append(f"   {k:10s} strict {fmt(x['strict'])} | decisive {fmt(x['decisive'])} cov {x['coverage'] if x['coverage'] is None else round(x['coverage'], 2)}"
                                 f" | shuf {fmt(x['shuffled_strict'])} / {fmt(x['shuffled_decisive'])} | {x['xtab']}")
                lines.append(f"   P7b(M only) {fmt(b['P7b_stale_on_M'])} shuf {fmt(b['P7b_shuffled'])}")
                lines.append(f"   n_direct {b['n_direct_mean']} flight {b['n_direct_flight_mean']} held {b['n_direct_held_mean']}")
                if "causal" in b:
                    lines.append(f"   causal {b['causal']}")
                for key, v in b["descr"].items():
                    lines.append(f"   {key}: {v}")
    name = "summary" if len(sys.argv) < 2 else "summary_" + "_".join(t.split("_")[0] for t in tags[:1])
    (OUT / f"{name}.json").write_text(json.dumps(res, indent=1))
    (OUT / f"{name}.txt").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1:])
