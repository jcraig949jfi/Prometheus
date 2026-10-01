"""W2-B: run the attainability certifier on C1 rulers and the proposed replacements.
usage: python certify_c1.py [M]   (CPU, 2 threads; ~5-10 min at M=32)"""
import sys

import w2b_common as c
from w2b_common import np, envs, assays, Physics, plants
import adversaries as adv
import attain as A
import rulers_c1 as R
from prometheus.ananke.search import random_genomes

RING = dict(topology="ring", n_sites=24, radius=1, dest_mode="all", lat_base=1, lat_hop=0, lat_jitter=0,
            loss=0.0, payload_width=2, channels=1, update_mode="sync", update_period=1, decay_shift=0,
            state_dim=4, prog_len=28)
PH = Physics(**RING).validate()
PHG = Physics(**{**RING, "topology": "global", "dest_mode": "sample", "fanout": 2, "n_sites": 24}).validate()
X0 = Physics(topology="torus", n_sites=64, radius=3, dest_mode="all", loss=0.0, lat_base=1, lat_hop=0,
             lat_jitter=0, decay_shift=0, update_mode="sync", update_period=1, state_dim=4, payload_width=2,
             channels=1, prog_len=18).validate()
ECHO = plants.c1b_echo_physics()

RELAY = envs.EnvSpec(family="RELAY", d=3, delta=8, trials=12)
MAJ = envs.EnvSpec(family="MAJ", d=2, delta=8, trials=12)
XOR = envs.EnvSpec(family="XOR", d=3, delta=8, trials=12)
FLIP = envs.EnvSpec(family="FLIP", d=3, delta=8, block=4, trials=16)
HOLD = envs.EnvSpec(family="HOLD", gap=8, cue_len=2, trials=12)


def one_sensor(ep):            # MAJ world edit: only sensor 0 carries the cue (single-sensor world)
    ep.schedule.sense_val[:, :, 1:] = 0


def prog(name, role, f, lacks="", only=()):
    return A.Program(name, role, f, lacks, only)


def fam_is(*fams):
    return lambda env: env.family in fams


def base_programs(rng):
    G = {}

    def rnd(i):
        def f(ph, env):
            if i not in G.setdefault(ph.digest(), {}):
                G[ph.digest()][i] = random_genomes(np.random.default_rng(1000 + i), 1, ph)[0]
            return G[ph.digest()][i]
        return f
    return [
        prog("null", "null", lambda ph, env: plants.plant("null", ph)),
        prog("const+", "null", lambda ph, env: plants.plant("null", ph) if False else
             np.broadcast_to(plants.assemble(ph, [("CONST", "S0", 0, 7, 2)]), (ph.rules, ph.prog_len, 5)).copy()),
        prog("sense_copy(silent)", "adversary", lambda ph, env: plants.plant("sense_copy", ph), "any transport"),
        prog("random0", "probe", rnd(0)),
        prog("random1", "probe", rnd(1)),
    ]


def main():
    M = int(sys.argv[1]) if len(sys.argv) > 1 else 32
    seeds = assays.world_seeds(c.NS + 4, M)
    ck = c.Clock()
    base = base_programs(None)
    relay_flood = lambda ph, env: plants.plant("relay_flood", ph) if ph.prog_len >= 12 else None
    hold_latch = lambda ph, env: plants.plant("hold_latch", ph.replace(prog_len=ph.prog_len)) if ph.prog_len >= 9 else None
    jobs = []
    # 1 zero_comm and SIGNAL / COMM_DEPENDENT on comm families
    comm_cells = [A.Cell(PH, RELAY, "ring24/RELAY"), A.Cell(PH, MAJ, "ring24/MAJ"), A.Cell(X0, XOR, "X0/XOR")]
    comm_progs = base + [prog("relay_flood", "plant", relay_flood),
                         prog("P_XOR", "plant", lambda ph, env: adv.p_xor(ph, env.period()) if env.family == "XOR" else None)]
    jobs += [("zero_comm", R.ZERO_COMM, comm_cells, comm_progs),
             ("SIGNAL_comm", R.SIGNAL, comm_cells, comm_progs),
             ("COMM_DEPENDENT", R.COMM_DEPENDENT, comm_cells, comm_progs)]
    # 2 XOR: SIGNAL (claim: XOR computed) vs proposed pivotality ruler
    xor_cells = [A.Cell(X0, XOR, "X0/XOR")]
    xor_progs = [p for p in base if p.role != "probe"] + [
        prog("P_XOR(parity)", "plant", lambda ph, env: adv.p_xor(ph, env.period())),
        prog("oneflag:not_P", "adversary", lambda ph, env: adv.xor_oneflag(ph, env.period(), "not_P"), "parity"),
        prog("oneflag:P", "adversary", lambda ph, env: adv.xor_oneflag(ph, env.period(), "P"), "parity")]
    jobs += [("XOR_SIGNAL_as_XOR_ruler", R.SIGNAL, xor_cells, xor_progs),
             ("XOR_PIVOT", R.XOR_PIVOT, xor_cells, xor_progs)]
    # 3 MAJ INTEGRATION: single-sensor worlds are the adversary family
    # one family of worlds: X0 (all sensors one hop from the actuator), full worlds and one-live-sensor worlds;
    # the plant maj_sum is the SAME program in both, so only the world decides plant vs adversary
    MAJX = envs.EnvSpec(family="MAJ", d=2, delta=8, trials=12)
    jobs += [("INTEGRATION_MAJ", R.INTEGRATION_MAJ,
              [A.Cell(X0, MAJX, "X0/MAJ"), A.Cell(X0, MAJX, "X0/MAJ(one live sensor)", one_sensor)],
              [prog("maj_sum", "plant", lambda ph, env: adv.maj_sum(ph), only=("X0/MAJ",))] + [p for p in base if p.role == "null"]
              + [prog("maj_sum@1sensor", "adversary", lambda ph, env: adv.maj_sum(ph), "more than one sensor",
                     only=("X0/MAJ(one live sensor)",))])]
    # 4 REACH_BEYOND_HOP legacy vs nearest, plus global topology
    rbh_cells = [A.Cell(PH, MAJ, "ring24/MAJ"), A.Cell(X0, XOR, "X0/XOR"), A.Cell(PH, RELAY, "ring24/RELAY")]
    rbh_progs = [p for p in base if p.role != "probe"] + [prog("relay_flood", "plant", relay_flood)]
    jobs += [("REACH_BEYOND_HOP", R.REACH_BEYOND_HOP, rbh_cells, rbh_progs),
             ("REACH_BEYOND_HOP_NEAREST", R.REACH_BEYOND_HOP_NEAREST, rbh_cells, rbh_progs),
             ("REACH_BEYOND_HOP_global", R.REACH_BEYOND_HOP, [A.Cell(PHG, RELAY, "global24/RELAY"),
                                                             A.Cell(PHG, MAJ, "global24/MAJ")], rbh_progs + base[3:])]
    # 5 FLIP: SIGNAL (claim: adapts from feedback) vs proposed feedback-ablation ruler
    flip_cells = [A.Cell(PH, FLIP, "ring24/FLIP")]
    flip_progs = [p for p in base if p.role != "probe"] + [
        prog("P_FLIP", "plant", lambda ph, env: adv.p_flip(ph)),
        prog("FLIP_CLOCK", "adversary", lambda ph, env: adv.flip_clock(ph, env.period(), env.block),
             "feedback after trial 0")]
    jobs += [("FLIP_SIGNAL_as_feedback_ruler", R.SIGNAL, flip_cells, flip_progs),
             ("FLIP_FEEDBACK", R.FLIP_FEEDBACK, flip_cells, flip_progs)]
    # 6 env_permutation clause: can anything fail it?
    perm_cells = [A.Cell(PH, RELAY, "ring24/RELAY"), A.Cell(ECHO, HOLD, "echo/HOLD")]
    perm_progs = base + [prog("relay_flood", "plant", relay_flood), prog("hold_latch", "plant", hold_latch),
                         prog("echo_hold", "plant", lambda ph, env: np.broadcast_to(plants.echo_hold(ph), (ph.rules, ph.prog_len, 5)).copy()
                              if ph.prog_len >= 28 else None)]
    jobs += [("env_permutation_clause", R.ENV_PERM_OK, perm_cells, perm_progs)]
    out = {"M": M, "certificates": {}}
    certs = {}
    for name, ruler, cells, progs in jobs:
        cert = A.certify(ruler, cells, progs, seeds)
        certs[name] = cert
        s = cert.summary()
        s["rows"] = [{k: (v if k != "pairs" else None) for k, v in r.items()} for r in cert.rows]
        out["certificates"][name] = s
        print(f"{name:34s} {cert.verdict:12s} range={tuple(round(x, 3) for x in cert.attainable)} "
              f"elig={cert.eligibility} cheapest={cert.cheapest} notes={cert.notes}", flush=True)
    al = A.alias(certs["SIGNAL_comm"], certs["COMM_DEPENDENT"])
    out["alias_SIGNAL_vs_COMM_DEPENDENT"] = al
    print("alias SIGNAL~COMM_DEPENDENT:", al)
    out["compute"] = ck.done()
    print(out["compute"])
    c.save("certify_c1.json", out)


if __name__ == "__main__":
    main()
