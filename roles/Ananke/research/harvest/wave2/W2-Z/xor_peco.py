"""P-ECONOMY bound for XOR rows whose emission cost exceeds the per-trial income.
(1) DP: maximum number of trials in which ONE sensor can emit during its cue window, over ALL emission policies,
    for a k-line rule (k >= 1: EMIT is zeroed every tick, so an emitter needs >= 1 non-NOP line), m = 0 (optimistic),
    sync wake (deterministic). (2) W2-J LC2 reach on the row's OWN held worlds (64 = 32 pairs, R=4).
Bound: acc <= .5 + .5 * (e_max/trials) * f_LC2  (deterministic emission schedule independent of loss/latency draws;
LC2 assumes emission at every awake tick, so it bounds delivery given emission)."""
import sys, json; sys.path.insert(0, '.')
import wz_common as wz
np = wz.np
sys.path.insert(0, str(wz.HERE.parent / "W2-J"))
import lc2 as L2
from prometheus.ananke import topology


def dp_max(ph, env, k):
    """max #trials with >=1 emission; sync only. State: E in [0, e_max]. Choice at each awake cue-window tick."""
    assert ph.update_mode == "sync"
    Pd, T = env.period(), env.T(); cE = ph.c_emit * ph.copies()
    NEG = -10 ** 9
    best = np.full(ph.e_max + 1, NEG); best[ph.e_max] = 0   # best[E] = max trials-with-emission so far
    flag = np.zeros(ph.e_max + 1, bool)                       # (approx-free) we track per (E, emitted_this_trial)
    st = {(ph.e_max, False): 0}
    for t in range(T):
        ph_t = t % Pd
        if ph_t == 0:
            st2 = {}
            for (E, f), v in st.items():
                st2[(E, False)] = max(st2.get((E, False), NEG), v)
            st = st2
        aw = (t % ph.update_period == 0)
        st2 = {}
        for (E, f), v in st.items():
            if not aw:
                key = (min(ph.e_max, E + ph.e_income), f); st2[key] = max(st2.get(key, NEG), v); continue
            # no emission
            key = (max(0, min(ph.e_max, E + ph.e_income - ph.c_op * k)), f); st2[key] = max(st2.get(key, NEG), v)
            if ph_t < env.cue_len and E >= cE:
                key = (max(0, min(ph.e_max, E + ph.e_income - cE - ph.c_op * k)), True)
                st2[key] = max(st2.get(key, NEG), v + (0 if f else 1))
        st = st2
    return max(st.values())


out = {}
for c in sys.argv[1].split(","):
    r = wz.row(c); ph, env = wz.cell(r)
    dps = {k: dp_max(ph, env, k) for k in (1, 2, 3)}
    seeds = wz.held(r, 64)
    ep = wz.envs.build(ph, env, seeds)
    sidx = ep.schedule.sense_idx.numpy(); ridx = ep.schedule.read_idx.numpy()[:, 0]
    nbr, dist = topology.build(ph)
    rng = np.random.default_rng(7)
    mode = "all" if (ph.dest_mode == "all" and ph.topology != "global") else "sample"
    both = []
    for b in range(0, 64, 2):
        for kk in range(env.trials):
            for _ in range(4):
                i1, i2 = L2.reach_trial(ph, env, sidx[b][:2], int(ridx[b]), kk * env.period(), rng, nbr, dist, mode)
                both.append(i1 and i2)
    both = np.array(both, float)
    pw = both.reshape(32, -1).mean(1)
    m, lo, hi = wz.assays.pair_ci(pw)
    e1 = dps[1] / env.trials
    o = {"dp_max_trials": dps, "trials": env.trials, "e_frac_k1": e1, "f_LC2_held": float(both.mean()), "f_ci99": [float(lo), float(hi)],
         "acc_bound_point": 0.5 + 0.5 * e1 * float(both.mean()), "acc_bound_hi": 0.5 + 0.5 * e1 * float(hi),
         "acc_bound_no_reach": 0.5 + 0.5 * e1}
    out[r["cell_id"]] = o
    print(c, o, flush=True)
wz.save("xor_peco.json", out)
