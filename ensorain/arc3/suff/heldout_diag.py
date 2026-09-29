"""T25 diagnosis of the held-out unifilar family (answer-keyed machine properties vs learner excess).

Per world (the known machine):
- S_min: minimal state count by Moore refinement (label = emission P(1) rounded to 1e-9, plus successor classes);
- H6: mean entropy (bits) of the MINIMAL-machine state given only the last 6 symbols (forward filter from stationary on
  a 6-symbol window; 3000 windows sampled from a long stream). This is the residual state uncertainty at the CSSR window;
- gap: the smallest |P(1)| difference between distinct minimal states;
- pmin: the smallest stationary probability of a minimal state.
Also runs CSSR_EM and MIX_FS at T = 16000 on the 4 worst worlds (by MIX_FS excess at T = 4000). Writes
results/heldout_diag.json."""
import json, pathlib, sys, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from ensorain.arc3.suff.worlds_unifilar import random_unifilar
from ensorain.arc3.suff.heldout_eval import learners, lp

def minimal(w):
    S = w.S
    p1 = [w.Tm[1][i].sum() for i in range(S)]
    succ = [[int(np.argmax(w.Tm[x][i])) if w.Tm[x][i].sum() > 0 else -1 for x in (0, 1)] for i in range(S)]
    cls = [round(p, 9) for p in p1]
    while True:
        key = [(cls[i], tuple(cls[s] if s >= 0 else None for s in succ[i])) for i in range(S)]
        ids = {k: j for j, k in enumerate(sorted(set(key), key=repr))}
        new = [ids[k] for k in key]
        if len(set(new)) == len(set(cls)):
            return new, p1
        cls = new

def diag(w, rng):
    cls, p1 = minimal(w); m = max(cls) + 1
    st = np.zeros(m)
    for i, c in enumerate(cls): st[c] += w.stat[i]
    pm = [np.mean([p1[i] for i in range(w.S) if cls[i] == c]) for c in range(m)]
    gap = min((abs(a - b) for i, a in enumerate(pm) for b in pm[i + 1:]), default=1.0)
    x = w.sample(60000, rng); H = []
    for t in rng.integers(6, len(x), 3000):
        b = w.stat.copy()
        for s in x[t - 6:t]:
            b = b @ w.Tm[s]; b = b / b.sum()
        q = np.zeros(m)
        for i, c in enumerate(cls): q[c] += b[i]
        q = q[q > 1e-12]; H.append(float(-(q * np.log2(q)).sum()))
    return dict(S_min=m, H6=float(np.mean(H)), gap=float(gap), pmin=float(st.min()))

if __name__ == "__main__":
    ev = json.loads((pathlib.Path(__file__).parent / "results" / "heldout_eval.json").read_text())["family"]
    out = {}
    for S in (3, 4, 5):
        for ws in range(1, 9):
            w = random_unifilar(S, ws)
            d = diag(w, np.random.default_rng(10_000 + ws)); d.update(ev[w.name]); out[w.name] = d
            print(w.name, {k: round(v, 4) if isinstance(v, float) else v for k, v in d.items() if k in
                           ("S_min", "H6", "gap", "pmin", "em", "mix_fs")}, flush=True)
    from scipy.stats import spearmanr
    for f in ("H6", "gap", "pmin", "S_min"):
        r = spearmanr([o[f] for o in out.values()], [o["mix_fs"] for o in out.values()])
        print(f"spearman({f}, mix_fs) = {r.correlation:.3f} p={r.pvalue:.4f}")
    worst = sorted(out, key=lambda n: -out[n]["mix_fs"])[:4]
    for n in worst:
        S, ws = int(n[1]), int(n.split("_s")[1]); w = random_unifilar(S, ws)
        x = w.sample(16000, np.random.default_rng(ws + 100)); B = lp(w.bayes(x), x)
        r = {k: float((lp(P, x) - B)[8000:].mean()) for k, P in learners(x).items() if k in ("em", "mix_fs", "stat6")}
        out[n]["T16000"] = r
        print(n, "T=16000", {k: round(v, 4) for k, v in r.items()}, "| T=4000 mix_fs", round(out[n]["mix_fs"], 4), flush=True)
    (pathlib.Path(__file__).parent / "results" / "heldout_diag.json").write_text(json.dumps(out, indent=1) + "\n")
