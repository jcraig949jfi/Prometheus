"""W-R POST-HOC (LOG A13): exact trial-split permutation test. For each offset, dN/dS/dC of the
true phase split vs ALL C(11,5)=462 splits of trials 1..11 into 5+6 (point estimates, no bootstrap).
Tells whether the phase split is extreme among arbitrary trial splits (trial-level heterogeneity
is not in the pair bootstrap). python posthoc_split.py <spec> [...] -> out/split_<spec>.json"""
import itertools, json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np
import fork
from prometheus.ananke import lens_swap as LS
from posthoc import load_raw


def fr(tab):
    ok = tab["ok"]
    pat = tab["pat"]
    return {x: (pat == x) & ok for x in "SCN"}, ok


def run(name):
    d, normal, ns0, scored, site, chan, s0s, s0c = load_raw(name)
    trials = d["trials"]
    out = {}
    for o in d["offsets"]:
        tab = LS.pair_trial_table(normal, site[o], chan[o], s0s[o], s0c[o], trials)
        m, ok = fr(tab)
        cnt = {x: m[x].sum(0) for x in "SCN"}           # per trial counts
        n = ok.sum(0)
        st = fork.strata(trials, o, d["Pd"], d["strat_period"])
        if not st[0] or not st[1] or len(st[0]) + len(st[1]) != len(trials):
            continue
        def diff(t1):
            t0 = [k for k in trials if k not in t1]
            if n[t0].sum() == 0 or n[list(t1)].sum() == 0:
                return None
            return {x: cnt[x][list(t1)].sum() / n[list(t1)].sum() - cnt[x][t0].sum() / n[t0].sum() for x in "SCN"}
        true = diff(st[1])
        if true is None:
            continue
        stat = lambda dd: max(abs(v) for v in dd.values())
        allv = [stat(dd) for c in itertools.combinations(trials, len(st[1])) if (dd := diff(c)) is not None]
        rank_p = float(np.mean([v >= stat(true) - 1e-12 for v in allv]))
        out[str(o)] = {"true_maxabs_d": stat(true), "true_d": true, "perm_p": rank_p, "n_splits": len(allv),
                       "per_trial_fN": {str(k): (float(cnt["N"][k] / n[k]) if n[k] else None) for k in trials}}
    (HERE / f"out/split_{name}.json").write_text(json.dumps(out, indent=1, default=float))
    print(name, " ".join(f"o{o}:{v['true_maxabs_d']:.2f}/p{v['perm_p']:.3f}" for o, v in out.items()), flush=True)


if __name__ == "__main__":
    for n in sys.argv[1:]:
        run(n)
