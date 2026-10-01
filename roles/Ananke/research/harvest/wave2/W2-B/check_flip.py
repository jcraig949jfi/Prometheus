"""W2-B check F: FLIP SIGNAL is passed by a mechanism that ignores every teacher after trial 0.
usage: python check_flip.py [M]   (CPU, 2 threads)"""
import sys

import w2b_common as c
from w2b_common import np, envs, assays, Physics, plants
import adversaries as adv

PH = Physics(topology="ring", n_sites=24, radius=1, dest_mode="all", lat_base=1, lat_hop=0, lat_jitter=0,
             loss=0.0, payload_width=2, channels=1, update_mode="sync", update_period=1, decay_shift=0,
             state_dim=4, prog_len=28).validate()


def teacher_after(k0, Pd):
    def f(ep):
        ep.schedule.sense_val[k0 * Pd:, :, 1] = 0       # FLIP column 1 = teacher at the actuator
    return f


def teacher_all(ep):
    ep.schedule.sense_val[:, :, 1] = 0


def main():
    M = int(sys.argv[1]) if len(sys.argv) > 1 else 64
    ck = c.Clock()
    seeds = assays.world_seeds(c.NS + 1, M)
    out = {"physics": PH.to_dict(), "M": M, "results": {}}
    for block in (4, 2):
        env = envs.EnvSpec(family="FLIP", d=3, delta=8, block=block, trials=16)
        Pd = env.period()
        progs = {"P_FLIP(H-PLANT)": adv.p_flip(PH), "FLIP_CLOCK(adversary)": adv.flip_clock(PH, Pd, block),
                 "relay_flood": plants.plant("relay_flood", PH)}
        arms = {"normal": None, "teacher_zeroed_after_trial0": teacher_after(1, Pd), "teacher_zeroed_all": teacher_all}
        res = {}
        for pn, g in progs.items():
            for an, fn in arms.items():
                pairs, pt, ep, tr = c.run(PH, g, env, seeds, sched_fn=fn)
                res[f"{pn}|{an}"] = c.ci(pairs)
                print(block, pn, an, res[f"{pn}|{an}"], flush=True)
        out["results"][f"block{block}"] = {"env": env.to_dict(), "arms": res}
    out["compute"] = ck.done()
    print(out["compute"])
    c.save("check_flip.json", out)


if __name__ == "__main__":
    main()
