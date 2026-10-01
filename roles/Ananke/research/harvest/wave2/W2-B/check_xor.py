"""W2-B check X: XOR non-parity ceiling (.75) and the per-sensor pivotality ruler that separates parity
from one-flag readouts. usage: python check_xor.py [M]"""
import sys

import w2b_common as c
from w2b_common import np, envs, assays, Physics
import adversaries as adv
from rulers_extra import per_sensor_pivotality

X0 = Physics(topology="torus", n_sites=64, radius=3, dest_mode="all", loss=0.0, lat_base=1,
             lat_hop=0, lat_jitter=0, dup=0.0, noise=0, cap=0, collision="none", decay_shift=0,
             update_mode="sync", update_period=1, state_dim=4, payload_width=2, channels=1,
             rules=1, prog_len=18).validate()          # H-PLANT X0 with prog_len 16 -> 18 (2 readout lines)
ENV0 = envs.EnvSpec(family="XOR", d=3, delta=8, trials=12)


def main():
    M = int(sys.argv[1]) if len(sys.argv) > 1 else 128
    ck = c.Clock()
    seeds = assays.world_seeds(c.NS + 2, M)
    Pd = ENV0.period()
    progs = {"P_XOR(parity)": adv.p_xor(X0, Pd)}
    for r in adv.XOR_RULES:
        progs["oneflag:" + r] = adv.xor_oneflag(X0, Pd, r)
    out = {"physics": X0.to_dict(), "env": ENV0.to_dict(), "M": M, "results": {}}
    for n, g in progs.items():
        pairs, pt, ep, tr = c.run(X0, g, ENV0, seeds)
        piv, _ = per_sensor_pivotality(X0, g, ENV0, seeds[:32], trials=(2, 5, 8))
        out["results"][n] = {"acc": c.ci(pairs), "pivotality": piv, "SIGNAL": c.ci(pairs)["lo99"] > 0.55}
        print(n, out["results"][n], flush=True)
    out["compute"] = ck.done()
    print(out["compute"])
    c.save("check_xor.json", out)


if __name__ == "__main__":
    main()
