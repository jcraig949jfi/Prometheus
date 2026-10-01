"""Analytic epidemic bound for GLOBAL-topology FLIP rows (plant-independent; no simulation).
Engine fact (engine._emit): global topology sends each copy to a uniform random other site (no routing control),
F = fanout copies per emitting awake site per tick, delay >= max(1, lat_base + lat_hop) (+jitter >= 0).
Upper bound in expectation on the number of sites holding trial-k cue information by the readout tick:
  I(tau) <= I(tau-1) + F * w(tau - dmin) * I(tau - dmin),   w = awake prob at the emission tick
  (sync period p: 1 at awake ticks else 0, phase maximised over trials; async: update_p; recipients assumed
  to process immediately = optimistic). Sensor counts as informed at its first awake tick in [0, cue_len).
The actuator is exchangeable with every other site, so q = P(actuator informed) <= (I(delta)-1)/(N-1), and with
no cue information the best FLIP answer is a coin (x_k independent): acc <= 1/2 + q/2."""
import json, gzip, pathlib
O = pathlib.Path(__file__).parent / "out"
ROOT = pathlib.Path(__file__).resolve().parents[6]
rows = {json.loads(l)["cell_id"]: json.loads(l) for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt")}
und = open(O / "undecided.txt").read().split(",")
def bound(p, e):
    N, F = p["n_sites"], p["fanout"]; dmin = max(1, p["lat_base"] + p["lat_hop"])
    best = 0.0
    phases = range(p["update_period"]) if p["update_mode"] == "sync" else [0]
    for ph0 in phases:
        def w(tau):
            if p["update_mode"] == "sync": return 1.0 if (ph0 + tau) % p["update_period"] == 0 else 0.0
            return p["update_p"]
        ts = [t for t in range(e["cue_len"]) if w(t) > 0]
        if not ts: continue
        I = [0.0] * (e["delta"] + 1)
        for tau in range(e["delta"] + 1):
            prev = I[tau - 1] if tau > 0 else 0.0
            if tau == ts[0]: prev = max(prev, 1.0)
            src = tau - dmin
            new = F * w(src) * I[src] if src >= 0 else 0.0
            I[tau] = min(N, prev + new)
        q = min(1.0, max(0.0, (I[-1] - 1) / (N - 1)))
        best = max(best, q)
    return best
out = []
for cid in und:
    r = rows[cid]; p, e = r["physics"], r["env"]
    if p["topology"] != "global": continue
    q = bound(p, e)
    out.append({"cell": cid, "N": p["n_sites"], "fanout": p["fanout"], "lat": [p["lat_base"], p["lat_hop"]], "update": [p["update_mode"], p["update_period"], p["update_p"]],
                "delta": e["delta"], "q_max": round(q, 4), "acc_bound": round(0.5 + q / 2, 4)})
    print(cid[:8], out[-1])
json.dump(out, open(O / "epidemic_bound.json", "w"), indent=1)
