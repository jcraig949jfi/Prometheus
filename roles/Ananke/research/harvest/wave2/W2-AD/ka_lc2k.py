"""KA: lc2k (K-bit generalisation) reproduces W2-J lc2.json f_both / f_s1 / f_s2 exactly on 3 XOR rows
(same seeds WJ_NS+7, M=32, R=4, rng seed 0, same draw order)."""
from w2ad_common import *
torch.set_num_threads(1)
import w2ad_ceil as WC
from prometheus.ananke import topology
ref = {o["cell"]: o for o in json.load(open(W2 / "W2-J/out/lc2.json"))["rows"]}
WJ_NS = 0x57324A53
out = []
for cid in list(ref)[:3]:
    r = hc.row(cid); ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    seeds = assays.world_seeds(WJ_NS + 7, 32); ep = envs.build(ph, env, seeds)
    sidx = ep.schedule.sense_idx.numpy(); ridx = ep.schedule.read_idx.numpy()[:, 0]
    nbr, dist = topology.build(ph); rng = np.random.default_rng(0)
    mode = list(ref[cid]["modes"])[0]
    both, s1, s2 = [], [], []
    for b in range(0, 32, 2):
        for k in range(env.trials):
            if not ep.scored[b, k]: continue
            for _ in range(4):
                inf = WC.reach_trial_k(ph, env, [int(x) for x in sidx[b][:2]], int(ridx[b]), k * env.period(), rng, nbr, dist, mode)
                both.append(inf.all()); s1.append(inf[0]); s2.append(inf[1])
    mine = (float(np.mean(both)), float(np.mean(s1)), float(np.mean(s2)))
    rr = ref[cid]["modes"][mode]; theirs = (rr["f_both"], rr["f_s1"], rr["f_s2"])
    out.append((cid[:8], mine, theirs, mine == theirs)); print(out[-1], flush=True)
jdump(OUT / "ka_lc2k.json", out)
