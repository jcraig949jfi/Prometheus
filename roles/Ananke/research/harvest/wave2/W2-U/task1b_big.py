"""TASK 1b: position-sampling-stable ceilings (1024 worlds = 512 position pairs) and exact held-set ceilings
for ALL four families' evolve rows (RELAY/MAJ via W2-P's task2_timing.ceilings, read-only; XOR/FLIP via w2u_ceil).
python task1b_big.py -> out/task1b_big.json"""
from w2u_ceil import *            # noqa
from w2p_common import Clock, held_seeds
import attain as A
NS = 0x57325542   # "W2UB"
ck = Clock()
E = [r for r in hc.rows() if r["kind"] == "evolve" and r["env"]["family"] in ("RELAY", "MAJ", "XOR", "FLIP")]
out, thr = [], {}
for i, r in enumerate(E):
    ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    seeds = assays.world_seeds(H_int(NS, int(r["cell_id"][:8], 16)), 1024)
    f = T2.ceilings if env.family == "MAJ" else ceilings
    c, ch = f(ph, env, seeds), f(ph, env, held_seeds(r))
    K = ch["n_trials"] // (r["search"]["M_held"] // 2)
    P = r["search"]["M_held"] // 2
    if (P, K) not in thr:
        thr[(P, K)] = A.min_true_to_cross(0.55, P, K, "lo_gt", 0.5)
    out.append({"cell": r["cell_id"], "family": env.family, "wave": r["wave"], "topology": ph.topology,
                "update_mode": ph.update_mode, "SIGNAL": bool(r["labels"]["SIGNAL"]),
                "held_acc": r["result"]["held"]["acc"], "held_lo99": r["result"]["held"]["lo99"],
                "K": K, "thr": thr[(P, K)], "big": c, "held": ch})
    if i % 80 == 0:
        print(i, len(E), ck.done(), flush=True)
save("task1b_big.json", {"rows": out, "compute": ck.done()})
print(ck.done())
