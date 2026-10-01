"""W2-B check B: legacy REACH_BEYOND_HOP for programs with NO multi-hop transport.
silent sense_copy: fires iff some perturbed sensor lies > hop from sensor 0;
one-hop emitter (adversaries.maj_sum: sensors emit once, receivers never relay): fires whenever >= 2
sensors are perturbed, because sensor j's one-hop packet lands up to d + radius > radius from sensor 0.
usage: python check_beyond_hop.py"""
import w2b_common as c
from w2b_common import np, envs, assays, Physics, plants
import adversaries as adv

X0 = Physics(topology="torus", n_sites=64, radius=3, dest_mode="all", loss=0.0, lat_base=1, lat_hop=0,
             lat_jitter=0, decay_shift=0, update_mode="sync", update_period=1, state_dim=4, payload_width=2,
             channels=1, prog_len=18).validate()


def main():
    ck = c.Clock()
    seeds = assays.world_seeds(c.NS + 6, 16)
    out = {}
    for fam, d in (("XOR", 3), ("XOR", 2), ("MAJ", 2), ("RELAY", 3)):
        env = envs.EnvSpec(family=fam, d=d, delta=8, trials=12)
        for name, g in (("sense_copy(silent)", plants.plant("sense_copy", X0)),
                        ("one_hop_emitter(maj_sum)", adv.maj_sum(X0))):
            tw = assays.twin_assay(X0, g[None], env, seeds, device="cpu")
            k = f"X0 r3 {fam} d{d} | {name}"
            out[k] = {kk: float(tw[kk][0]) for kk in ("reach", "beyond_hop", "reach_nearest", "beyond_hop_nearest")}
            print(k, out[k], flush=True)
    out["compute"] = ck.done()
    print(out["compute"])
    c.save("check_beyond_hop.json", out)


if __name__ == "__main__":
    main()
