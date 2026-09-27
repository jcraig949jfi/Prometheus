"""W-B Part 3 (PLAN Addendum A): non-bootstrap cells, Y1-Y5."""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import numpy as np
from probe import run, acc, paired, pin
from census import cells
from prometheus.ananke import c1b, envs, lens
from prometheus.ananke.physics import Physics

OUT = pathlib.Path(__file__).parent / "out"


def one(r):
    ph, env = Physics.from_dict(r["physics"]), envs.EnvSpec(**r["env"])
    g = np.asarray(r["result"]["champion"], dtype=np.int64)
    Pd = env.period()
    tk = c1b.ticks(env)
    mid = tk["mid"] if env.family == "HOLD" else [t0 + max(1, env.delta // 2) for t0 in tk["t0"]]
    base = run(ph, g, env, record_r=True)
    nrm = acc(base)
    B, N = base.r.shape[1:]
    o = {"family": env.family, "normal": lens.ci(nrm)}
    arms = {"Y1_r": lambda w: lens.swap(w, ["r"]),
            "Y2_site_no_r": lambda w: lens.swap(w, [a for a in lens.SITE_ARRAYS if a != "r"]),
            "Y2_inflight": lambda w: lens.swap(w, lens.FLIGHT_ARRAYS)}
    for an, fn in arms.items():
        tr = run(ph, g, env, hooks={t: fn for t in mid})
        pp = acc(tr)
        o[an] = {"acc": lens.ci(pp), "verdict": lens.swap_verdict(nrm, pp)}
    # Y3
    ep = base.ep
    ridx = ep.schedule.read_idx.cpu().numpy()[:, 0]
    sidx = ep.schedule.sense_idx.cpu().numpy()
    rro = np.stack([base.r[ep.ro_tick[b], b, ridx[b]] for b in range(B)])        # [B, trials]
    p = np.arange(B) ^ 1
    sc = ep.scored
    o["Y3_ro_r_partner_diff_share"] = float((rro != rro[p])[sc].mean())
    ys = ep.y[sc]; rs = rro[sc]
    hit = 0
    for k in np.unique(rs):
        m = rs == k
        hit += max((ys[m] == 1).sum(), (ys[m] == -1).sum())
    o["Y3_best_rule_to_sign_acc"] = float(hit / len(ys))
    o["Y3_ro_rule_hist"] = {int(k): int((rs == k).sum()) for k in np.unique(rs)}
    # Y4
    later = range(2, env.trials)
    nl = acc(base, later)
    ro = np.zeros((B, N), bool); ro[np.arange(B), ridx] = True
    ts = 2 * Pd - 1
    snap = {}

    def grab(w):
        snap["r"] = w.r.clone()
    for name, mask in (("Y4a_pin_readout_after_settle", ro), ("Y4b_pin_others_after_settle", ~ro)):
        def every(w, t, mask=mask):
            if t == ts:
                grab(w)
            if t >= ts:
                pin(mask, snap["r"])(w)
        o[name] = paired(acc(run(ph, g, env, every=every), later), nl)
    # Y5
    diff = base.r != base.r[:, p]                         # [T,B,N]
    tot = diff.sum()
    sense = np.zeros((B, N), bool)
    for b in range(B):
        sense[b, sidx[b]] = True
    o["Y5_partner_diff_site_ticks"] = int(tot)
    if tot:
        o["Y5_share_at_readout"] = float(diff[:, ro].sum() / tot)
        o["Y5_share_at_sense"] = float(diff[:, sense & ~ro].sum() / tot)
        o["Y5_share_elsewhere"] = float(diff[:, ~sense & ~ro].sum() / tot)
        o["Y5_share_after_trial1"] = float(diff[ts:].sum() / tot)
    return o


if __name__ == "__main__":
    want = set(sys.argv[1:])
    res = {}
    for r in cells():
        if r["cell_id"][:8] in want:
            res[r["cell_id"]] = one(r)
            print(r["cell_id"][:8], json.dumps(res[r["cell_id"]], default=float), flush=True)
            (OUT / "deepdive.json").write_text(json.dumps(res, indent=1, default=float))
