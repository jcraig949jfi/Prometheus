import random, collections, backoff
def gen(*a, **k):
    g = backoff.expo(*a, **k); next(g)   # backoff's wait generators are primed with a first next()
    return g
g = gen(base=2, factor=1, max_value=60)
print("expo schedule:", [next(g) for _ in range(8)])
random.seed(1)
g = gen()
print("full_jitter sample:", [round(backoff.full_jitter(next(g)), 3) for _ in range(8)])
def waits(jit):
    random.seed(7); out = []
    for c in range(1000):
        g = gen(); v = None
        for _ in range(6):
            v = next(g)
        out.append(round(backoff.full_jitter(v), 2) if jit else v)
    return out
for jit in (False, True):
    c = collections.Counter(waits(jit))
    print("jitter=%s distinct_wait_values=%d max_share=%.3f" % (jit, len(c), max(c.values()) / 1000.0))
