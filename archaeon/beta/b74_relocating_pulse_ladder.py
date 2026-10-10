"""B74 -- hand ladder: a world where UPDATE-ON-CONDITION memory is decisive? (evaluation only; attack on the memory law)

Finding 3: write-once state is reachable, update-on-condition state is not. B68/B69: in the pulse world a write-once
gating LATCH is decisive and IS reached. RELOCATING PULSE world:
- pulse as in B68 (deplete 1; refill every P=4 ticks);
- every Q ticks, every pool moves +L/2 nodes on the ring.
A write-once LATCH then waits forever at a dead node. The RESET latch counts consecutive empty ticks while latched and,
after P of them, UNLATCHES and searches again. That is update-on-condition state (a counter that is reset by the
condition, and a latch that is cleared).
Hand programs (specialist on pool i): REACT_i, LATCH_i (B68), RESET_i (latch + empty counter + unlatch).
Worlds: Q = None (no relocation), 8, 12. Solo and 4-group (2 x niche 1 + 2 x niche 2), held-out seeds.
PREDICTION (committed before running):
- Q = None: |RESET - LATCH| < .01 solo;
- Q = 8 and Q = 12: RESET - LATCH >= .02 solo, and LATCH no better than REACT + .01 at Q = 8.
If it holds, the relocating pulse world is a test bed where the memory law's unreached class is decisive.
v1 (mode "half", +L/2 shift) FAILED BY DESIGN FLAW (mine): two half-ring shifts per episode at Q=8 return every pool
home, so a stuck LATCH recovers. v2 (mode "random"): each pool jumps to a random other node. SAME prediction,
committed before the v2 run.
"""
import json
import sys
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from
from proteus.foundry.vm import Player

from archaeon.beta.b01_w2k2_existence import HALT, IN, JNZ, JZ, LDC, OUT_, _prog
from archaeon.beta.b25_noclock_world import NoClock, load
from archaeon.beta.b68_pulse_state_controls import latch, man, react

OUT = Path(__file__).resolve().parent / "results"
ADD, EQ, JMP = 7, 16, 18


def reset(i, P=4):
    return _prog([(IN, 1, 0)] * (i + 1) + [
        (JZ, 1, 7), (LDC, 5, 1), (LDC, 6, 0), (LDC, 2, i), (LDC, 3, 0), (OUT_, 2, 3), (HALT,),       # p..p+6 food: latch, reset counter, harvest
        (JNZ, 5, 5), (LDC, 2, 0), (LDC, 3, 1), (OUT_, 2, 3), (HALT,),                              # p+7..p+11 not latched: move
        (LDC, 7, 1), (ADD, 6, 6, 7), (LDC, 9, P), (EQ, 8, 6, 9), (JNZ, 8, 2), (HALT,),              # p+12..p+17 latched + empty: count, wait
        (LDC, 5, 0), (LDC, 6, 0), (JMP, 0, (1 << 32) - 12)])                                         # p+18..p+20 unlatch, go move


def group_reloc(ms, w, seed, E, P=4, Q=None, rng_seed=7, mode="half", log=None):
    players = [Player(m) for m in ms]; tot = [0.0] * len(ms); mx = [0.0] * len(ms); L = w.w.L
    for ep in range(E):
        shared = {}
        sts = [w.reset(seed, ep, shared) for _ in ms]; start = list(sts[0]["pools"])
        for st in sts:
            st["regen"] = 0.0; st["deplete"] = 1.0
        vms = [p.fresh_state() for p in players]
        rngs = [SplitMix64(seed_from("wse.vmrng", rng_seed, ep, i)) for i in range(len(ms))]
        t = 0
        while any(not w.done(st) for st in sts):
            order = list(range(len(ms))); order = order[t % len(ms):] + order[:t % len(ms)]
            for i in order:
                if w.done(sts[i]):
                    continue
                players[i].begin_tick(vms[i])
                outs, status = players[i].run_tick(vms[i], w.observe(sts[i]), w.K, rngs[i])
                w.act(sts[i], outs)
                if status == "trap":
                    sts[i]["alive"] = False
            if (t + 1) % P == 0:
                sts[0]["pools"][:] = start
            if Q and (t + 1) % Q == 0:
                if mode == "half":
                    new = [(n + L // 2) % L for n in sts[0]["pool_node"]]
                else:                                   # v2: each pool jumps to a random OTHER node (never returns by construction)
                    rr = SplitMix64(seed_from("b74.reloc", seed, ep, t))
                    new = [(n + 1 + rr.randbelow(L - 1)) % L for n in sts[0]["pool_node"]]
                for st in sts:
                    st["pool_node"] = list(new)
            t += 1
        for i, st in enumerate(sts):
            tot[i] += max(0.0, st["reward"]); mx[i] += st["max_reward"]
    return [min(1.0, a / max(1e-9, b)) for a, b in zip(tot, mx)]


def main(argv=()):
    mode = argv[0] if argv else "half"
    world, s, _ = load(); w = NoClock(world)
    progs = {"REACT": lambda i: man(react(i), "none"), "LATCH": lambda i: man(latch(i), "regs"), "RESET": lambda i: man(reset(i), "regs")}
    avg = lambda f: round(sum(f(s + 1000 + k) for k in range(4)) / 4, 4)
    rows = []
    for Q in (None, 8, 12):
        row = {"Q": Q}
        for name, mk in progs.items():
            row["solo_" + name] = avg(lambda ss: sum(group_reloc([mk(i)], w, ss, 16, Q=Q, mode=mode)[0] for i in (1, 2)) / 2)
            row["group_" + name] = avg(lambda ss: sum(group_reloc([mk(1), mk(2), mk(1), mk(2)], w, ss, 16, Q=Q, mode=mode)) / 4)
        row["RESET_minus_LATCH_solo"] = round(row["solo_RESET"] - row["solo_LATCH"], 4)
        rows.append(row); print(json.dumps(row), flush=True)
    p0 = abs(rows[0]["RESET_minus_LATCH_solo"]) < .01
    p1 = all(r["RESET_minus_LATCH_solo"] >= .02 for r in rows[1:])
    p2 = rows[1]["solo_LATCH"] <= rows[1]["solo_REACT"] + .01
    print(json.dumps({"pred_noreloc_equal": p0, "pred_reloc_reset_wins": p1, "pred_latch_useless_Q8": p2}))
    (OUT / ("B74_result%s.json" % ("" if mode == "half" else "_" + mode))).write_text(json.dumps({"probe": "B74", "rows": rows, "pred": [p0, p1, p2]}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
