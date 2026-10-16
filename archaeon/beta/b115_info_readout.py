"""B115 -- CONSTANT-TWIN INFORMATION readout for self-group signalling (repairs the self-ablation readout).

DEFECT (found 17:40Z on B111 11106, before any B112-NL result): self-ablation (zero the listeners' signal word)
measures DEPENDENCE, not information. 11106 off-lattice: full .516, ablated .168 (drop .35), but full is BELOW the
no-signal baseline (MUTE_OP .746). Its listeners break without a signal word.
INFORMATION readout: info = self_full - max_v self_const(v), where self_const(v) replaces the listeners' signal word
with the constant v. v ranges over the values the scout writes on held-out episodes (plus 0). A constant carries no
information about this episode, so info > 0 only if the episode-specific signal beats every fixed word.
Communicating (info) = info > .05.
DECLARED BEFORE any B112-NL result: B112-NL is reported on BOTH readouts (the prereg drop > .05, and info > .05).
The prediction (<= 1/6) applies to both.
B115 RUN 1 (17:39Z): calibration MET (COMPLETE .233 / .210; MUTE_OP 0; 11106 jitter -.160). Constant set was the
first 12 sorted values (biased toward low values when a genome emits many); REPAIRED to <= 24 spread over the range
before any B112-NL scoring.
Calibration (prediction committed before running): hand COMPLETE info > .15 on both worlds (lattice / jittered);
MUTE_OP info = 0; 11106 jittered info <= 0.
"""
import json
import sys
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from
from proteus.foundry.vm import Player

R_, SIG = 3, 3


def run(m, w, s, const=None, collect=None, E=16):
    tot = 0.0; mx = 0.0
    for k in range(4):
        ss = s + 1000 + k
        for ep in range(E):
            sc = ep % 4; shared = {}; sts = [w.w.reset(ss, ep, shared) for _ in range(4)]
            players = [Player(m) for _ in range(4)]; vms = [p.fresh_state() for p in players]
            rngs = [SplitMix64(seed_from("wse.vmrng", 7, ep, i)) for i in range(4)]; t = 0
            while any(not w.done(st) for st in sts):
                order = list(range(4)); order = order[t % 4:] + order[:t % 4]
                for i in order:
                    if w.done(sts[i]):
                        continue
                    obs = w.observe(sts[i])
                    if i != sc:
                        obs = [[0 if j < R_ else (const if (const is not None and j == SIG) else x) for j, x in enumerate(ch)] for ch in obs]
                    players[i].begin_tick(vms[i]); outs, _ = players[i].run_tick(vms[i], obs, w.K, rngs[i])
                    if collect is not None and i == sc and len(outs) > SIG:
                        collect.update(outs[SIG])
                    w.act(sts[i], outs)
                t += 1
            for st in sts:
                tot += max(0.0, st["reward"]); mx += st["max_reward"]
    return tot / mx


def info(m, w, s):
    vals = set(); full = run(m, w, s, collect=vals); vals.add(0)
    sv = sorted(vals); pick = sv if len(sv) <= 24 else sorted({sv[round(i * (len(sv) - 1) / 23)] for i in range(24)} | {0})
    consts = {v: run(m, w, s, const=v) for v in pick}            # <= 24 constants spread over the emitted range
    best = max(consts.values())
    return {"full": round(full, 4), "best_const": round(best, 4), "info": round(full - best, 4), "n_vals": len(vals)}


def main(argv):
    import archaeon.beta.b92_signal_ladder as B92
    from archaeon.beta.b95_signal_restore import COMPLETE, MUTE_OP
    from archaeon.beta.b97_signal_headroom import sw
    from archaeon.beta.b114_nolattice import jw
    rows = {}
    progs = {"COMPLETE": B92.man(list(COMPLETE)), "MUTE_OP": B92.man(list(MUTE_OP))}
    for f in argv:
        progs[Path(f).stem] = json.loads(Path(f).read_text(encoding="utf-8"))
    for wn, (w, s) in (("lattice", sw()), ("jitter", jw())):
        for k, m in progs.items():
            rows[wn + ":" + k] = r = info(m, w, s); print(wn, k, json.dumps(r), flush=True)
    out = Path(__file__).resolve().parent / "results" / "B115_info"; out.mkdir(parents=True, exist_ok=True)
    (out / ("B115_%d.json" % len(argv))).write_text(json.dumps(rows, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
