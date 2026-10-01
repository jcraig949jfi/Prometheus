"""Exact enumeration: expected same-cue / changed-cue accuracy of every per-branch signed single-source policy on a
scored FLIP trial (trial k-1 in the same block, so m_{k-1} = m_k = m; m, x_{k-1}, x_k independent fair coins)."""
import itertools
SRC = {"x_k": lambda m, xp, x: x, "x_prev": lambda m, xp, x: xp, "y_prev": lambda m, xp, x: m * xp}
def acc(src, sg, branch):
    n = c = 0
    for m, xp, x in itertools.product((1, -1), repeat=3):
        if (x == xp) != (branch == "same"): continue
        n += 1; c += (sg * SRC[src](m, xp, x) == m * x)
    return c / n
pure = {(s, g): (acc(s, g, "same"), acc(s, g, "chg")) for s in SRC for g in (1, -1)}
for k, v in pure.items(): print(f"{('+' if k[1] > 0 else '-')}{k[0]:7s} same {v[0]:.2f} chg {v[1]:.2f}")
best = []
for a in pure:
    for b in pure:
        B = (pure[a][0] + pure[b][1]) / 2
        best.append((B, f"same-branch {a}, changed-branch {b}"))
best.sort(reverse=True)
print("top gated policies by B:"); [print(f"  B={B:.3f}  {d}") for B, d in best[:4]]
assert best[0][0] == 1.0 and best[1][0] == 0.75 and "('y_prev', 1)" in best[0][1] and "('y_prev', -1)" in best[0][1].split("changed-branch")[1]
print("OK: B>.75 only for (same:+y_prev, changed:-y_prev) = m*x_k; every other pure gated policy has B<=.75")
