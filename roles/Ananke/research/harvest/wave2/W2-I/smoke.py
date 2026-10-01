"""Smoke: timing + identity patch exactness + reproduce W2-G random_d3=.5 on bbef66a1."""
import time, dataclasses
from w2i_common import *
t0=time.time(); c0=time.process_time()
r, ph, env, g = load("bbef66a1"); G=g[None]
S = seeds_for(1)
a = score(ph, G, env, S); print("native", a, time.process_time()-c0)
_, nb, ds, M, _ = variant(ph, "ring_native_patched", 0)
with patched(nb, ds, M): b = score(ph, G, env, S)
print("patched", b, a == b)
c = score(c1_random(ph), G, env, S); print("C1random d3", c)
print("hops native", signal_hops(ph, env, S[:16]), "random", signal_hops(c1_random(ph), env, S[:16]))
# batching speed test: 4 copies
c1=time.process_time(); score(ph, np.repeat(G,4,0), env, S); print("4x batch cpu", time.process_time()-c1)
print("wall", time.time()-t0, "cpu", time.process_time()-c0)
