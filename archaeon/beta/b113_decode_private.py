"""B113 -- DECODE the B111 private codes (cheap, single process, descriptive only).
Per held-out episode, in a clonal 4-group with rotating scout: richest pool (from the scout's first observation),
the scout's first channel-3 write, and the listeners' first channel-0 action. A code = a mapping richest -> signal;
it is 'used' if the listeners' action depends on it.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from
from proteus.foundry.vm import Player

from archaeon.beta.b97_signal_headroom import sw


def decode(m, w, s, E=16):
    sig = defaultdict(Counter); act = defaultdict(Counter)
    for k in range(4):
        ss = s + 1000 + k
        for ep in range(E):
            sc = ep % 4; shared = {}; sts = [w.w.reset(ss, ep, shared) for _ in range(4)]
            players = [Player(m) for _ in range(4)]; vms = [p.fresh_state() for p in players]
            rngs = [SplitMix64(seed_from("wse.vmrng", 7, ep, i)) for i in range(4)]; t = 0
            rich = None; first_sig = None; first_act = {}
            while any(not w.done(st) for st in sts) and t < 50:
                order = list(range(4)); order = order[t % 4:] + order[:t % 4]
                for i in order:
                    if w.done(sts[i]):
                        continue
                    obs = w.observe(sts[i])
                    if i == sc and rich is None:
                        p = obs[0][:3]; rich = max(range(3), key=lambda j: p[j])
                    if i != sc:
                        obs = [[0 if j < 3 else x for j, x in enumerate(ch)] for ch in obs]
                    players[i].begin_tick(vms[i]); outs, _ = players[i].run_tick(vms[i], obs, w.K, rngs[i])
                    if i == sc and first_sig is None and len(outs) > 3 and outs[3]:
                        first_sig = outs[3][0]                        # outs[ch] = values written on channel ch
                    if i != sc and i not in first_act and outs[0]:
                        first_act[i] = outs[0][0]
                    w.act(sts[i], outs)
                t += 1
            sig[rich][first_sig] += 1
            for v in first_act.values():
                act[(rich, first_sig)][v] += 1
    return {"signal_by_richest": {str(r): dict(c) for r, c in sig.items()},
            "listener_action_by_(richest,signal)": {str(k): dict(c) for k, c in act.items()}}


if __name__ == "__main__":
    w, s = sw()
    for f in sys.argv[1:]:
        print(f, json.dumps(decode(json.loads(Path(f).read_text(encoding="utf-8")), w, s)), flush=True)
