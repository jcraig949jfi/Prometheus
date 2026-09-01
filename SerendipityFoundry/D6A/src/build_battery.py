"""Battery construction. Designer-side only; nothing here is visible to any learner."""
import json, random, sys
from collections import Counter
sys.path.insert(0, 'F:/SerendipityA/src')
import substrate as S

FREQ_N = 500_000          # samples used to estimate blind-search rarity
SEED = 20260827


def blind_freq(seed=SEED, n=FREQ_N):
    rng = random.Random(seed)
    c = Counter()
    for _ in range(n):
        p = S.random_program(rng, 2, 12)
        c[S.behavior(p)[0]] += 1
    return c


def degenerate(tt):
    if tt == 0 or tt == S.FULL:
        return True
    for i in S.INPUT_TT:
        if tt == i or tt == (~i & S.FULL):
            return True
    pc = bin(tt).count('1')
    return not (16 <= pc <= 48)


def pick_modules(freq, rng, K=8, lo=1, hi=4, tries=400_000, avoid=()):
    """Modules = behaviors of short programs whose blind-hit count sits in [lo,hi]/FREQ_N."""
    mods = []
    seen = set(avoid)
    for _ in range(tries):
        p = S.random_program(rng, 3, 5)
        tt = S.behavior(p)[0]
        if tt in seen or degenerate(tt):
            continue
        if lo <= freq.get(tt, 0) <= hi:
            seen.add(tt)
            mods.append((p, tt, freq.get(tt, 0)))
            if len(mods) == K:
                break
    return mods


def main():
    rng = random.Random(SEED)
    freq = blind_freq()
    print("[calib] distinct behaviors in %d blind samples: %d" % (FREQ_N, len(freq)))
    print("[calib] top mass: %s" % ([c for _, c in freq.most_common(5)],))
    mods = pick_modules(freq, rng)
    print("[calib] modules: %d  blind counts: %s  lens: %s"
          % (len(mods), [m[2] for m in mods], [len(m[0]) for m in mods]))
    mods2 = pick_modules(freq, rng, K=8, avoid={m[1] for m in mods})
    print("[calib] neg modules: %d  counts: %s" % (len(mods2), [m[2] for m in mods2]))
    out = dict(seed=SEED, freq_n=FREQ_N, n_distinct=len(freq),
               modules=[[[list(i) for i in p], hex(tt), c] for p, tt, c in mods],
               neg_modules=[[[list(i) for i in p], hex(tt), c] for p, tt, c in mods2])
    with open('F:/SerendipityA/runs/modules.json', 'w') as f:
        json.dump(out, f, indent=1)
    print("[calib] wrote runs/modules.json")


if __name__ == '__main__':
    main()
