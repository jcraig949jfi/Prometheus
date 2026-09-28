import numpy as np, sys
d = np.load("out/obs_b59e6c3a.npz")
T, B, N = d["r"].shape
bi = np.arange(B); a = d["ridx"][:, 0]; s = d["sidx"][:, 0]
Pd = 19
r_a = d["r"][:, bi, a]; rp_a = d["r_pre"][:, bi, a]; S0a = d["S"][:, bi, a, 0]; S1a = d["S"][:, bi, a, 1]
c0a = d["cnt"][:, bi, a, 0]; c1a = d["cnt"][:, bi, a, 1]; aw = d["awake"][:, bi, a]
em_s = d["emit"][:, bi, s]
b = int(sys.argv[1]) if len(sys.argv) > 1 else 0
for k in range(3, 6):
    print("trial", k, "y", d["y"][b, k], "correct", d["per_trial"][b, k])
    for ph_ in range(Pd):
        t = k * Pd + ph_
        print(f"  ph{ph_:2d} sense_s={d['sense'][t,b,0]:5d} emit_s={int(em_s[t,b])} cnt0_a={c0a[t,b]} cnt1_a={c1a[t,b]} aw={int(aw[t,b])} r_pre={rp_a[t,b]} r={r_a[t,b]} S0={S0a[t,b]} S1={S1a[t,b]}")
# condition table: readout site, transitions r_pre -> r vs cnt0 seen (awake only)
print("r_pre,cnt0 -> r (awake, readout sites, all ticks)")
from collections import Counter
C = Counter()
for t in range(T):
    for bb in range(B):
        if aw[t, bb]:
            C[(int(rp_a[t, bb]), int(c0a[t, bb]), int(r_a[t, bb]))] += 1
for k_, v in sorted(C.items()): print(k_, v)
