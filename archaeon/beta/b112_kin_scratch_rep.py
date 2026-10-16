"""B112 -- PREREGISTERED replication: does communication evolve FROM SCRATCH under the kin route? (follow-up to B111)

B111 (random gen 0, clonal groups, normal load, world 1, G=300). The hand-listener SIGNALS readout was 0/6 -- the
evolved codes are not 'richest + 1', so the hand listener is misled. An EXPLORATORY readout defined after seeing the
results is SELF-ABLATION: the best genome's reward in its own clonal group, minus the same with the listeners' signal
word zeroed. Hand COMPLETE drops .241, MUTE_OP 0. On it, 11104 (.071) and 11105 (.088) communicate in private codes;
11102/11103 do not.
Here the self-ablation readout is FIXED IN ADVANCE: communicating = drop > .05 (held-out world seeds s+1000..1003 x 16).
Same design as B111, NEW seeds 11201-11206.
PREDICTION (committed before running): communicating >= 2/6.
Control in the same readout: hand MUTE_OP (drop 0) and hand COMPLETE (.241) are re-scored with every run as instrument
checks.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from
from proteus.foundry.vm import Player

import archaeon.beta.b111_kin_scratch as B111
from archaeon.beta.b97_signal_headroom import sw

OUT = Path(__file__).resolve().parent / "results" / "B112_kin_scratch_rep"
R_, SIG = 3, 3


def self_group(m, w, s, ablate_signal, E=16):
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
                        obs = [[0 if (j < R_ or (ablate_signal and j == SIG)) else x for j, x in enumerate(ch)] for ch in obs]
                    players[i].begin_tick(vms[i]); outs, _ = players[i].run_tick(vms[i], obs, w.K, rngs[i]); w.act(sts[i], outs)
                t += 1
            for st in sts:
                tot += max(0.0, st["reward"]); mx += st["max_reward"]
    return tot / mx


def cell(job):
    B111.OUT = OUT; r = B111.cell(job)
    w, s = sw(); m = json.loads((OUT / ("best_%d.json" % job["seed"])).read_text(encoding="utf-8"))
    a, b = self_group(m, w, s, False), self_group(m, w, s, True)
    r.update({"self_full": round(a, 4), "self_ablated": round(b, 4), "ablation_drop": round(a - b, 4), "communicating": a - b > .05})
    return r


def controls():
    import archaeon.beta.b92_signal_ladder as B92
    from archaeon.beta.b95_signal_restore import COMPLETE, MUTE_OP
    w, s = sw(); out = {}
    for k, g in (("COMPLETE", COMPLETE), ("MUTE_OP", MUTE_OP)):
        m = B92.man(list(g)); out[k] = round(self_group(m, w, s, False) - self_group(m, w, s, True), 4)
    return out


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    if argv and argv[0] == "ablate":
        w, s = sw()
        for f in argv[1:]:
            m = json.loads(Path(f).read_text(encoding="utf-8")); a, b = self_group(m, w, s, False), self_group(m, w, s, True)
            print(json.dumps({"file": f, "self_full": round(a, 4), "self_ablated": round(b, 4), "ablation_drop": round(a - b, 4)}), flush=True)
        return 0
    ctl = controls(); print("controls", json.dumps(ctl), flush=True)
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 6) as ex:
        futs = {ex.submit(cell, {"seed": 11201 + i, "G": int(argv[0]) if argv else 300}): i for i in range(6)}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception as e:                    # noqa: BLE001
                r = {"seed": 11201 + futs[fu], "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B112_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    k = sum(r.get("communicating", False) for r in rows); summ = {"communicating": k, "n": len(rows), "pred": k >= 2, "controls": ctl}
    print(json.dumps(summ))
    (OUT / "B112_result.json").write_text(json.dumps({"probe": "B112", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
