"""B75 -- does search reach UPDATE-ON-CONDITION memory where it is the best strategy? (direct attack on the memory law)

B74/B74b hand ladder, relocating pulse world: ticks 48; refill every P=4; every Q=16 ticks each pool jumps to a
random other node. Solo rewards: REACT .021, write-once LATCH .038, update-on-condition RESET (unlatch after P
empties, re-search) .064 = 1.66x LATCH.
Arm SOLO (k=1), CMP3 N=200, E=8, G=300, seeds 7501-7512, via the B62 cell with this world and evaluator.
Readout on the top 10 genomes per population, solo, held-out world seeds s+1000..1003 x 16 eps:
- reward;
- full state dependence (code locked AND persist none);
- RE-FIND rate = among relocation events after which the organism had harvested its own pool, the share in which it
  harvests that pool again before the episode ends (hand RESET vs LATCH as references).
A genome is RESET-LIKE if: state dependence >= .02, re-find rate >= the midpoint between hand LATCH and hand RESET
re-find rates, and reward > hand LATCH.
PREDICTION (committed before running), written as the MEMORY LAW's defender: RESET-like genomes appear in <= 2/12
populations, and no population's best reward exceeds the hand RESET (.064).
"""
import copy
import functools
import json
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from
from proteus.foundry.vm import Player

import archaeon.beta.b60_concurrent_niches as B60
import archaeon.beta.b62_niche_attack as B62
from archaeon.beta.b25_noclock_world import NoClock, load as _load
from archaeon.beta.b68_pulse_state_controls import latch, man
from archaeon.beta.b74_relocating_pulse_ladder import group_reloc, reset

OUT = Path(__file__).resolve().parent / "results" / "B75_reset"
T_, P_, Q_ = 48, 4, 16


def load():
    world, s, x = _load(); world.ticks = T_; return world, s, x


def _patch():
    g = functools.partial(group_reloc, P=P_, Q=Q_, mode="random")
    B60.group_rewards = g; B62.group_rewards = g; B62.load = load; B62.OUT = OUT


def refind(m, w, s, R, E=16):
    """Share of relocation events (after the organism had harvested its own pool) followed by a harvest of it."""
    p = Player(m); ev = 0; hit = 0
    for k in range(4):
        for ep in range(E // 4):
            ss = s + 1000 + k; st = w.reset(ss, ep, None); start = list(st["pools"]); st["regen"] = 0.0; st["deplete"] = 1.0
            vm = p.fresh_state(); rng = SplitMix64(seed_from("wse.vmrng", 7, ep, 0)); harv = Counter(); pending = False; t = 0
            while not w.done(st):
                p.begin_tick(vm); outs, _ = p.run_tick(vm, w.observe(st), w.K, rng)
                h = outs[0][0] % R if outs and outs[0] else None
                if h is not None and st["pool_node"][h] == st["pos"] and st["pools"][h] > 0:
                    harv[h] += 1
                    if pending and h == harv.most_common(1)[0][0]:
                        hit += 1; pending = False
                w.act(st, outs)
                if (t + 1) % P_ == 0:
                    st["pools"][:] = start
                if (t + 1) % Q_ == 0:
                    rr = SplitMix64(seed_from("b74.reloc", ss, ep, t)); L = w.w.L
                    st["pool_node"] = [(n + 1 + rr.randbelow(L - 1)) % L for n in st["pool_node"]]
                    if harv:
                        if pending:
                            pass
                        ev += 1; pending = True
                t += 1
    return round(hit / ev, 3) if ev else None


def census_pop(pop, w, s, R, refs):
    sc = lambda m: sum(group_reloc([m], w, s + 1000 + k, 16, P=P_, Q=Q_, mode="random")[0] for k in range(4)) / 4
    cnt = Counter(json.dumps(m["genome"]) for m in pop); keyed = {json.dumps(m["genome"]): m for m in pop}
    mid = (refs["LATCH_refind"] + refs["RESET_refind"]) / 2; n = 0; best = 0.0
    for g, _ in cnt.most_common(10):
        m = keyed[g]; r = sc(m); lk = copy.deepcopy(m); lk["code_writable"] = False; lk["persist"] = "none"
        dep = r - sc(lk); rf = refind(m, w, s, R); best = max(best, r)
        n += bool(dep >= .02 and rf is not None and rf >= mid and r > refs["LATCH"])
    return n, round(best, 4)


def refs_():
    world, s, _ = load(); w = NoClock(world); R = world.R
    sc = lambda m: sum(group_reloc([m], w, s + 1000 + k, 16, P=P_, Q=Q_, mode="random")[0] for k in range(4)) / 4
    L1 = man(latch(1), "regs"); R1 = man(reset(1), "regs")
    return {"LATCH": round(sc(L1), 4), "RESET": round(sc(R1), 4), "LATCH_refind": refind(L1, w, s, R), "RESET_refind": refind(R1, w, s, R)}


def cell(job):
    _patch(); r = B62.cell(job)
    world, s, _ = load(); w = NoClock(world)
    pop = json.loads((OUT / ("B62_pop_%s_%d.json" % (job["arm"], job["seed"]))).read_text(encoding="utf-8"))
    r["reset_like_top10"], r["best_reward"] = census_pop(pop, w, s, world.R, job["refs"])
    return r


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    refs = refs_(); print("refs", json.dumps(refs), flush=True)
    if argv and argv[0] == "refs":
        return 0
    G_ = int(argv[0]) if argv else 300
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"arm": "SOLO", "seed": 7501 + i, "G": G_, "refs": refs}): i for i in range(12)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                r = {"arm": "SOLO", "seed": 7501 + futs[f], "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B75_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {"pops_with_reset_like": sum(r.get("reset_like_top10", 0) > 0 for r in rows), "beat_hand_reset": sum(r.get("best_reward", 0) > refs["RESET"] for r in rows)}
    print(json.dumps(summ))
    (OUT / "B75_result.json").write_text(json.dumps({"probe": "B75", "refs": refs, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
