"""P-FLIP and P-MULTIHOP runs at d9cc and its lossless variant.
usage: python run_flip_mh.py flip|mh dev|score"""
import sys

import hp_common as hc
from hp_common import Clock, save, evaluate, decompile, row
import hp_plants as hp
from prometheus.ananke import assays, envs
from prometheus.ananke.physics import Physics

FLIP_CELL = "6f82f9c7d51bcef1"     # C1 wave C, FLIP at d9cc, held .479 (NULL)
MH_CELL = "fac4aaa23a0bdcb2"       # C1 wave C, RELAY d5 at d9cc, held .5 (NULL)


def phys(cell):
    r = row(cell)
    ph = Physics.from_dict(r["physics"]).validate()
    assert ph.digest().startswith("d9cc"), ph.digest()
    lossless = ph.replace(loss=0.0, lat_jitter=0, cap=0, collision="none").validate()
    return r, ph, lossless


def main():
    task, mode = sys.argv[1], sys.argv[2]
    ck = Clock()
    seeds = assays.world_seeds(hc.DEV_NS if mode == "dev" else hc.SCORE_NS, 32 if mode == "dev" else 256)
    out = {"task": task, "mode": mode, "results": {}}
    if task == "flip":
        r, ph, ll = phys(FLIP_CELL)
        env = envs.EnvSpec(**r["env"])
        out["program"] = decompile(ph, hp.p_flip(ph)[0])
        for name, p in (("d9cc_C1", ph), ("d9cc_lossless", ll)):
            res = {"physics": p.to_dict(), "env": env.to_dict(),
                   "normal": evaluate(p, hp.p_flip(p), env, seeds),
                   "mf_flip_a_teacher_zeroed": evaluate(p, hp.p_flip(p, "mf_teacher"), env, seeds),
                   "mf_flip_b_readout_no_m": evaluate(p, hp.p_flip(p, "mf_readout_no_m"), env, seeds)}
            out["results"][name] = res
    else:
        r, ph, ll = phys(MH_CELL)
        env5 = envs.EnvSpec(**r["env"])
        assert env5.family == "RELAY" and env5.d == 5
        env6 = envs.EnvSpec(**{**r["env"], "d": 6})
        out["program"] = decompile(ph, hp.p_multihop(ph)[0])
        out["program_mf"] = decompile(ph, hp.p_multihop(ph, "mf_no_relay")[0])
        for name, p in (("d9cc_C1", ph), ("d9cc_lossless", ll)):
            for en, env in (("d5", env5), ("d6", env6)):
                res = {"physics": p.to_dict(), "env": env.to_dict(),
                       "normal": evaluate(p, hp.p_multihop(p), env, seeds),
                       "mf_mh_no_relay": evaluate(p, hp.p_multihop(p, "mf_no_relay"), env, seeds)}
                out["results"][f"{name}_{en}"] = res
    out["compute"] = ck.done()
    for k, v in out["results"].items():
        for kk, vv in v.items():
            if isinstance(vv, dict) and "acc" in vv:
                print(k, kk, round(vv["acc"], 4), round(vv["lo99"], 4), round(vv["hi99"], 4))
    print(out["compute"])
    save(f"{task}_{mode}.json", out)


if __name__ == "__main__":
    main()
