"""INTEGRATION ruler attainability (no engine runs). lo99 = 0.5% quantile of the pair bootstrap (assays.pair_ci,
2000 resamples) over 32 mirror pairs; each pair = mean of 2 twins x 12 trials. Model A: twins identical
(pair = Binomial(12,p)/12, the plant case: sign-symmetric program, shared physics streams). Model B: twins
independent (pair = Binomial(24,p)/24). Also E(q): accuracy of the exact majority over the votes that arrive,
each of 5 arriving independently w.p. q; and the async lat=delta ceiling a*E(q)+(1-a)/2."""
import numpy as np, json
import w2m_common as c
from math import comb
from prometheus.ananke import assays
BT = c.bayes_table()
def E(q): return sum(comb(5, m) * q**m * (1-q)**(5-m) * BT[m] for m in range(6))
def pass_rate(p, n_trials, R=400, seed=0):
    g = np.random.default_rng(seed); ok = 0; los = []
    for _ in range(R):
        pairs = g.binomial(n_trials, p, size=32) / n_trials
        _, lo, _ = assays.pair_ci(pairs, n_boot=2000, seed=0); los.append(lo); ok += lo > 0.70
    return ok / R, float(np.median(los))
out = {"E_q": {f"{q:.2f}": E(q) for q in np.arange(0.3, 1.0001, 0.05)}}
for model, n in (("A_twins_identical", 12), ("B_twins_independent", 24)):
    out[model] = {}
    for p in (0.72, 0.74, 0.75, 0.76, 0.77, 0.78, 0.80, 0.837):
        pr, mlo = pass_rate(p, n); out[model][f"{p:.3f}"] = {"P(lo99>.70)": pr, "median_lo99": mlo}
        print(model, p, "P(pass)=%.2f median lo99=%.3f" % (pr, mlo), flush=True)
# empirical: plant pairs at the three best SIGNAL cells -> pair SD, implied half-width
d = json.load(open(c.OUT / "score_signal.json"))
emp = {}
for o in d["rows"]:
    p = np.array(o["held"]["pairs"]); emp[o["cell"][:8]] = {"mean": float(p.mean()), "sd": float(p.std(ddof=1)), "mean_minus_lo99": float(p.mean() - o["held"]["lo99"])}
out["empirical_pairs"] = emp
hw = np.median([v["mean_minus_lo99"] for v in emp.values()])
out["median_mean_minus_lo99"] = float(hw)
# async lat == delta ceiling (ring100 r3 cells): sensor awake at t0 (p_wake), copy survives (1-loss), actuator awake at readout
for pw, loss in ((0.8, 0.3),):
    q = pw * (1 - loss); out["async_lat_eq_delta"] = {"p_wake": pw, "loss": loss, "q": q, "E(q)": E(q),
        "ceiling_any_program": pw * E(q) + (1 - pw) * 0.5, "single_sensor_ceiling": pw * (q * 0.7 + (1 - q) * 0.5) + (1 - pw) * 0.5}
# sample fanout 8 over 6 ports, loss .1 (4781b0a1 / 8743da7f): P(at least one copy to the actuator)
q2 = 1 - (1 - 0.9 / 6) ** 8
out["sample8_ring_r3_loss.1"] = {"q": q2, "E(q)": E(q2)}
c.save("attain.json", out)
print(json.dumps({k: out[k] for k in ("E_q", "median_mean_minus_lo99", "async_lat_eq_delta", "sample8_ring_r3_loss.1")}, indent=1))
