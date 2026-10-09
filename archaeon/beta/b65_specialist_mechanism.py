"""B65 -- how does a B62 CONC specialist encode ITS pool? (evaluation only, 1 process)

For CONC P-boom populations 6001/6003/6005, take the 6 most frequent genomes per niche (the two largest niches).
Readouts, solo on held-out world seeds s+1000..1003, 16 episodes each:
(a) per-word ablation: reward drop when observation word j (NoClock channel 0) is zeroed;
(b) harvest-on-arrival: on ticks where ANY pool word is non-zero, the share of harvest outputs naming the organism's
    own pool vs the visible pool.
PREDICTION (before running): a specialist depends mainly on ITS OWN pool word (largest ablation drop at word = its
pool index) in >= 2/3 of genomes, i.e. it is "go to where my pool is, harvest it", not a constant harvest index
plus random walking.
"""
import json
import sys
from collections import Counter
from pathlib import Path

from archaeon.beta.b25_noclock_world import NoClock, load
from archaeon.beta.b26_word_ablation import Ablate
from archaeon.beta.b59_coupling_niches import dominant_index
from archaeon.campaign6.worlds.runtime import evaluate_world

OUT = Path(__file__).resolve().parent / "results"


def sc(m, w, s):
    return sum(evaluate_world(m, w, s + 1000 + k, 16, rng_seed=7)["reward"] for k in range(4)) / 4


def main():
    world, s, _ = load(); w = NoClock(world); R = world.R
    n_words = len(w.observe(w.reset(s, 0, None))[0])
    rows = []
    for sd in (6001, 6003, 6005):
        pop = json.loads((OUT / ("B62_pop_CONC_%d.json" % sd)).read_text(encoding="utf-8"))
        keyed = {}
        for m in pop:
            keyed.setdefault(json.dumps(m["genome"]), m)
        cnt = Counter(json.dumps(m["genome"]) for m in pop)
        dom = {g: dominant_index(keyed[g], w, s, R) for g in cnt}
        niches = Counter()
        for g, c in cnt.items():
            niches[dom[g]] += c
        top2 = [d for d, _ in niches.most_common() if d is not None][:2]
        for d in top2:
            gs = [g for g, _ in cnt.most_common() if dom[g] == d][:6]
            for g in gs:
                m = keyed[g]; base = sc(m, w, s)
                drops = [round(base - sc(m, Ablate(w, j), s), 4) for j in range(n_words)]
                top = max(range(n_words), key=lambda j: drops[j])
                rows.append({"seed": sd, "niche": d, "copies": cnt[g], "base": round(base, 4), "drops": drops, "top_word": top,
                             "own_word_is_top": top == d})
                print(json.dumps(rows[-1]), flush=True)
    summ = {"genomes": len(rows), "own_word_top": sum(r["own_word_is_top"] for r in rows),
            "top_word_counts": dict(Counter(r["top_word"] for r in rows))}
    print(json.dumps(summ))
    (OUT / "B65_result.json").write_text(json.dumps({"probe": "B65", "n_words": n_words, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
