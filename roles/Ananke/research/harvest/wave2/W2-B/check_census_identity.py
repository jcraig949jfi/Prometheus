"""W2-B check S: census IDENTITY (site_acc + chan_acc = 1) is forced only when no mirror-different input
arrives after the swap; with cue_len 2 the swap after tick t0+o for o < cue_len-1 precedes the last cue tick.
relay_flood on ring24 RELAY d3: identity per offset. usage: python check_census_identity.py"""
import w2b_common as c
from w2b_common import np, envs, assays, Physics, plants
from prometheus.ananke import lens_swap

PH = Physics(topology="ring", n_sites=24, radius=1, dest_mode="all", lat_base=1, lat_hop=0, lat_jitter=0,
             loss=0.0, payload_width=2, channels=1, update_mode="sync", update_period=1, decay_shift=0,
             state_dim=4, prog_len=12).validate()
ENV = envs.EnvSpec(family="RELAY", d=3, delta=8, trials=12)


def main():
    ck = c.Clock()
    seeds = assays.world_seeds(c.NS + 7, 32)
    g = plants.plant("relay_flood", PH)
    res = lens_swap.mixture_scan(PH, g, ENV, seeds, offsets=[-1, 0, 1, 2, 4, 7], mode="single",
                                 trials=(2, 3, 4, 5), n_boot=100)
    out = {"normal": res["normal"]}
    for o, cc in res["offsets"].items():
        out[o] = {k: cc[k] for k in ("eligible", "identity", "fS", "fC", "fN", "site_acc", "chan_acc", "class")}
        print(o, out[o], flush=True)
    out["compute"] = ck.done()
    print(out["compute"])
    c.save("check_census_identity.json", out)


if __name__ == "__main__":
    main()
