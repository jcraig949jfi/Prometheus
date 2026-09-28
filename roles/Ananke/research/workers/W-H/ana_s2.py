import numpy as np, sys
from collections import Counter
cid = sys.argv[1]; Pd = int(sys.argv[2]); b = int(sys.argv[3]); ks = [int(x) for x in sys.argv[4].split(",")]
d = np.load(f"out/obs_{cid}.npz")
T, B, N = d["r"].shape
bi = np.arange(B); a = d["ridx"][:, 0]; s = d["sidx"][:, 0]
r_a = d["r"][:, bi, a]; rp_a = d["r_pre"][:, bi, a]; S = d["S"][:, bi, a]; aw = d["awake"][:, bi, a]
cnt = d["cnt"][:, bi, a]; ins = d["insum"][:, bi, a]; E = d["E"][:, bi, a]; em = d["emit"][:, bi, a]
for k in ks:
    print("trial", k, "y", d["y"][b, k], "correct", d["per_trial"][b, k], "ro", d["ro_tick"][b, k] - k * Pd)
    for p in range(Pd):
        t = k * Pd + p
        print(f"  ph{p:2d} sense={d['sense'][t,b,0]:5d} aw={int(aw[t,b])} cnt={cnt[t,b].tolist()} in={ins[t,b].tolist()} r_pre={rp_a[t,b]} r={r_a[t,b]} S={S[t,b].tolist()} E={E[t,b]} emit={int(em[t,b])}")
