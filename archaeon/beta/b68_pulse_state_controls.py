"""B68 -- hand-control ladder: can competition make STATE pay? (evaluation only; precondition for any evolution run)

B67: no competition->state bridge in P-boom, where regeneration keeps every pool > 0, so "sense my own pool" is
complete. PULSE variant of concurrent P-boom NoClock:
- a harvest EMPTIES the pool (deplete = 1);
- pools refill to their episode-start amounts every P ticks, with no regeneration in between.
An emptied pool therefore reads 0, the same as "my pool is not here"; only state can tell the two apart.
Hand programs (specialist on pool i; channel 0 = harvest index, channel 1 = move):
  REACT_i  harvest i if word i != 0, else move +1 (persist none)
  LATCH_i  as REACT_i, plus a write-once latch r5 := 1 when word i != 0; when word i == 0 and the latch is set, WAIT
           (persist regs)
Compositions, per-capita reward of the focal type: solo; 4-group of 2 x niche 1 + 2 x niche 2, all one type;
one LATCH among REACTs; one REACT among LATCHes. Worlds: P = None (standard P-boom regen, B60 evaluator), P = 4, 6, 8.
PREDICTION (before running):
- standard regen: LATCH - REACT ~ 0 (|d| < .02) solo and in group (consistent with B67);
- pulse worlds: LATCH - REACT > 0 solo;
- the bridge criterion: the advantage is LARGER in the 4-group than solo for >= 2/3 pulse settings.
"""
import copy
import json
import sys
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from
from proteus.foundry.vm import Player

from archaeon.beta.b01_w2k2_existence import HALT, IN, JNZ, JZ, LDC, OUT_, _prog
from archaeon.beta.b25_noclock_world import NoClock, load

OUT = Path(__file__).resolve().parent / "results"


def react(i):
    return _prog([(IN, 1, 0)] * (i + 1) + [(JZ, 1, 5), (LDC, 2, i), (LDC, 3, 0), (OUT_, 2, 3), (HALT,),
                                            (LDC, 2, 0), (LDC, 3, 1), (OUT_, 2, 3), (HALT,)])


def latch(i):
    return _prog([(IN, 1, 0)] * (i + 1) + [(JZ, 1, 6), (LDC, 5, 1), (LDC, 2, i), (LDC, 3, 0), (OUT_, 2, 3), (HALT,),
                                            (JNZ, 5, 5), (LDC, 2, 0), (LDC, 3, 1), (OUT_, 2, 3), (HALT,), (HALT,)])


def man(genome, persist):
    return {"schema_version": "proteus.player_manifest.v0", "n_regs": 8, "tape_words": 128, "genome": genome,
            "code_writable": False, "persist": persist, "tick_budget": 64, "out_cap": 1}


def group_pulse(ms, w, seed, E, P=None, rng_seed=7):
    """B60 concurrent evaluator; with P set: deplete = 1 and pools refill to start amounts every P ticks (no regen)."""
    players = [Player(m) for m in ms]; tot = [0.0] * len(ms); mx = [0.0] * len(ms)
    for ep in range(E):
        shared = {}
        sts = [w.reset(seed, ep, shared) for _ in ms]
        regen = sts[0]["regen"]; start = list(sts[0]["pools"])
        for st in sts:
            st["regen"] = 0.0
            if P:
                st["deplete"] = 1.0
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
            pools = sts[0]["pools"]
            if P:
                if (t + 1) % P == 0:
                    pools[:] = start
            else:
                for j, a in enumerate(pools):
                    pools[j] = min(3.0, a + regen)
            t += 1
        for i, st in enumerate(sts):
            tot[i] += max(0.0, st["reward"]); mx[i] += st["max_reward"]
    return [min(1.0, a / max(1e-9, b)) for a, b in zip(tot, mx)]


def ladder(w, s, P, E=16, seeds=4):
    R_ = {i: man(react(i), "none") for i in (1, 2)}; L_ = {i: man(latch(i), "regs") for i in (1, 2)}
    def avg(fn):
        v = [fn(s + 1000 + k) for k in range(seeds)]; return round(sum(v) / len(v), 4)
    row = {"P": P}
    row["solo_REACT"] = avg(lambda ss: sum(group_pulse([R_[i]], w, ss, E, P)[0] for i in (1, 2)) / 2)
    row["solo_LATCH"] = avg(lambda ss: sum(group_pulse([L_[i]], w, ss, E, P)[0] for i in (1, 2)) / 2)
    row["group_allREACT"] = avg(lambda ss: sum(group_pulse([R_[1], R_[2], R_[1], R_[2]], w, ss, E, P)) / 4)
    row["group_allLATCH"] = avg(lambda ss: sum(group_pulse([L_[1], L_[2], L_[1], L_[2]], w, ss, E, P)) / 4)
    row["LATCH_among_REACT"] = avg(lambda ss: group_pulse([L_[1], R_[2], R_[1], R_[2]], w, ss, E, P)[0])
    row["REACT_among_LATCH"] = avg(lambda ss: group_pulse([R_[1], L_[2], L_[1], L_[2]], w, ss, E, P)[0])
    row["adv_solo"] = round(row["solo_LATCH"] - row["solo_REACT"], 4)
    row["adv_group_pure"] = round(row["group_allLATCH"] - row["group_allREACT"], 4)
    row["adv_group_invade"] = round(row["LATCH_among_REACT"] - row["REACT_among_LATCH"], 4)
    return row


def main(argv):
    world, s, _ = load(); w = NoClock(world)
    # sanity: the P=None path must equal the B60 evaluator
    from archaeon.beta.b60_concurrent_niches import group_rewards
    m = man(react(1), "none")
    chk = {"b60": round(group_rewards([m], w, s, 8)[0], 6), "b68": round(group_pulse([m], w, s, 8, None)[0], 6)}
    print("equivalence", json.dumps(chk), flush=True)
    rows = []
    for P in (None, 4, 6, 8):
        rows.append(ladder(w, s, P)); print(json.dumps(rows[-1]), flush=True)
    (OUT / "B68_result.json").write_text(json.dumps({"probe": "B68", "equivalence": chk, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
