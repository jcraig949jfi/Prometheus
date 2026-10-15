"""B92 -- hand-control ladder: can a SIGNAL pay in an information-asymmetric group? (precondition for a communication run)

Finding 4: the shared signal word (C6 coupling, channel 3) was never used (ablation 0.0); nothing made it pay.
World: the B71 minimal ecology with LOCALITY OFF (any pool can be harvested from anywhere): 3 pools of different
richness that deplete (.489) and regenerate (.247). Observation [pool0, pool1, pool2, signal].
Concurrent 4-groups, with information asymmetry:
- agent 0 (SCOUT) sees the pool words;
- agents 1-3 see them ZEROED;
- everyone sees the shared signal.
Hand programs:
  SCOUT     harvest the richest visible pool i; write signal i+1
  SILENT    harvest the richest visible pool; never signal
  LISTENER  read the signal s; harvest pool s-1 if s > 0, else pool 0
  BLIND     always harvest pool 0
Measures (held-out world seeds s+1000..1003 x 16 episodes): per-agent and group-mean reward for
SCOUT+3 LISTENER, SILENT+3 LISTENER, SCOUT+3 BLIND.
PREDICTION (committed before running):
- the group mean of SCOUT+3L exceeds SILENT+3L by >= .02 (the signal pays the group);
- the SCOUT's own reward is LOWER in SCOUT+3L than SILENT's in SILENT+3L (signalling costs the scout -- the
  conflict that makes communication under INDIVIDUAL selection unlikely).
"""
import copy
import json
import sys
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from
from proteus.foundry.vm import Player

from archaeon.beta.b01_w2k2_existence import HALT, IN, JZ, LDC, MOV, OUT_, _prog
from archaeon.beta.b25_noclock_world import NoClock
from archaeon.campaign6.worlds.runtime import ComposedWorld

RES = Path(__file__).resolve().parent / "results"
ADD, SUB, LT = 7, 8, 17
R_ = 3


def world():
    c = json.loads((RES / "B71_world.json").read_text(encoding="utf-8")); p = copy.deepcopy(c["params"]); p["locality"] = {"on": False}
    return NoClock(ComposedWorld(p)), c["seed"]


def man(g):
    return {"schema_version": "proteus.player_manifest.v0", "n_regs": 10, "tape_words": 128, "genome": g,
            "code_writable": False, "persist": "none", "tick_budget": 64, "out_cap": 1}


def scout(signal=True):
    body = [(IN, 1, 0), (IN, 2, 0), (IN, 3, 0), (LDC, 4, 0), (MOV, 5, 1),
            (LT, 6, 5, 2), (JZ, 6, 3), (MOV, 5, 2), (LDC, 4, 1),
            (LT, 6, 5, 3), (JZ, 6, 3), (MOV, 5, 3), (LDC, 4, 2),
            (OUT_, 4, 0)]
    if signal:
        body += [(LDC, 7, 1), (ADD, 8, 4, 7), (LDC, 9, 3), (OUT_, 8, 9)]
    return _prog(body + [(HALT,)])


LISTENER = _prog([(IN, 1, 0)] * 4 + [(JZ, 1, 5), (LDC, 2, 1), (SUB, 3, 1, 2), (OUT_, 3, 0), (HALT,), (OUT_, 0, 0), (HALT,)])
BLIND = _prog([(OUT_, 0, 0), (HALT,)])


def group(ms, w, seed, E, n_scouts=1, rng_seed=7):
    """Concurrent group (B60 scheme, no locality): agents >= n_scouts see pool words zeroed. Returns per-agent rewards."""
    inner = w.w; players = [Player(m) for m in ms]; tot = [0.0] * len(ms); mx = [0.0] * len(ms)
    for ep in range(E):
        shared = {}
        sts = [inner.reset(seed, ep, shared) for _ in ms]; regen = sts[0]["regen"]
        for st in sts:
            st["regen"] = 0.0
        vms = [p.fresh_state() for p in players]
        rngs = [SplitMix64(seed_from("wse.vmrng", rng_seed, ep, i)) for i in range(len(ms))]
        t = 0
        while any(not w.done(st) for st in sts):
            order = list(range(len(ms))); order = order[t % len(ms):] + order[:t % len(ms)]
            for i in order:
                if w.done(sts[i]):
                    continue
                obs = w.observe(sts[i])
                if i >= n_scouts:
                    obs = [[0 if j < R_ else x for j, x in enumerate(ch)] for ch in obs]
                players[i].begin_tick(vms[i]); outs, status = players[i].run_tick(vms[i], obs, w.K, rngs[i])
                w.act(sts[i], outs)
                if status == "trap":
                    sts[i]["alive"] = False
            pools = sts[0]["pools"]
            for j, a in enumerate(pools):
                pools[j] = min(3.0, a + regen)
            t += 1
        for i, st in enumerate(sts):
            tot[i] += max(0.0, st["reward"]); mx[i] += st["max_reward"]
    return [min(1.0, a / max(1e-9, b)) for a, b in zip(tot, mx)]


def main():
    w, s = world()
    S, Q, L, B = man(scout(True)), man(scout(False)), man(LISTENER), man(BLIND)
    def avg(ms):
        v = [group(ms, w, s + 1000 + k, 16) for k in range(4)]
        return [round(sum(x[i] for x in v) / 4, 4) for i in range(len(ms))]
    rows = {"SCOUT+3L": avg([S, L, L, L]), "SILENT+3L": avg([Q, L, L, L]), "SCOUT+3B": avg([S, B, B, B]),
            "solo_SCOUT": avg([S]), "solo_BLIND": avg([B])}
    for k, v in rows.items():
        print(k, v, "mean", round(sum(v) / len(v), 4), flush=True)
    m = lambda k: sum(rows[k]) / len(rows[k])
    pred = {"group_signal_pays": m("SCOUT+3L") - m("SILENT+3L") >= .02, "signal_costs_scout": rows["SCOUT+3L"][0] < rows["SILENT+3L"][0]}
    print(json.dumps(pred))
    (RES / "B92_result.json").write_text(json.dumps({"probe": "B92", "rows": rows, "pred": pred}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
