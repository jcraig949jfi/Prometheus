import numpy as np, time, warnings
import cvxpy as cp
warnings.filterwarnings("ignore")
m, eps = 30, 1e-6

def build(m, spread, seed):
    rng = np.random.default_rng(seed)
    d = np.logspace(0, spread, m)
    Q = np.linalg.qr(rng.standard_normal((m, m)))[0]
    return Q @ np.diag(d) @ Q.T

def analytic(C):
    lam = np.linalg.eigvalsh(C)
    return eps*np.trace(C) + (1 - m*eps)*lam.min(), lam

def run(C, s, scaled):
    lam = np.linalg.eigvalsh(C); k = lam.max() if scaled else 1.0
    X = cp.Variable((m, m), symmetric=True)
    p = cp.Problem(cp.Minimize(cp.trace((C/k) @ X)), [X >> np.eye(m)*eps, cp.trace(X) == 1])
    try:
        v = p.solve(solver=s)
        return p.status, (None if not np.isfinite(v) else v*k), X.value
    except Exception as e:
        return f"EXC:{type(e).__name__}", None, None

# --- A. does the 1e4 case have the same hidden story? ---
print("=== C_illcond_1e4 vs ANALYTIC OPTIMUM (fixture called CLARABEL a pass, SCS a fail) ===")
C4 = build(m, 4.0, 7); p4, _ = analytic(C4)
print(f"  analytic p*            = {p4:.10f}")
print(f"  fixture CLARABEL value = 1.0367178925367533   rel_err = {abs(1.0367178925367533-p4)/p4:.3e}")
print(f"  fixture SCS      value = 1.0505293645246603   rel_err = {abs(1.0505293645246603-p4)/p4:.3e}")
print(f"  fixture 'feasible point attains' = 1224.93 -> {1224.9298653638475/p4:.0f}x the optimum")

# --- B. verify the rescaled CLARABEL solution independently ---
print("\n=== INDEPENDENT VERIFICATION OF THE RESCALED CLARABEL SOLUTION (1e10) ===")
C10 = build(m, 10.0, 7); p10, lam10 = analytic(C10)
st, val, Xv = run(C10, "CLARABEL", scaled=True)
print(f"  status {st}, reported (rescaled) {val:.4f}, analytic {p10:.4f}")
print(f"  recomputed trace(C X) from returned X = {np.trace(C10 @ Xv):.4f}")
print(f"  constraint check: trace(X) = {np.trace(Xv):.12f}   min eig(X - eps I) = {np.linalg.eigvalsh(Xv - eps*np.eye(m)).min():.3e}")

# --- C. FAMILY: is the failure seed-specific, and does rescaling rescue every member? ---
print("\n=== FAMILY SWEEP: 10 seeds at spread 1e10 ===")
hdr = f"  {'seed':>4} {'CLA as-posed':<24} {'SCS as-posed':<24} {'CLA scaled rel_err':>20} {'SCS scaled rel_err':>20}"
print(hdr)
rows = []
for seed in range(10):
    C = build(m, 10.0, seed); ps, _ = analytic(C)
    s1, v1, _ = run(C, "CLARABEL", False); s2, v2, _ = run(C, "SCS", False)
    s3, v3, _ = run(C, "CLARABEL", True); s4, v4, _ = run(C, "SCS", True)
    e3 = abs(v3-ps)/ps if v3 is not None else float('nan')
    e4 = abs(v4-ps)/ps if v4 is not None else float('nan')
    rows.append((seed, s1, s2, s3, e3, s4, e4))
    print(f"  {seed:>4} {s1:<24} {s2:<24} {s3+' '+format(e3,'.2e'):>20} {s4+' '+format(e4,'.2e'):>20}")

# --- D. where is the cliff in spread, as posed vs rescaled? ---
print("\n=== SPREAD CLIFF (seed 7): as-posed vs rescaled ===")
print(f"  {'spread':>8} {'CLA posed':<24} {'SCS posed':<22} {'CLA scaled':<10} {'relerr':>10} {'SCS scaled':<10} {'relerr':>10}")
for sp in (4.0, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0, 14.0):
    C = build(m, sp, 7); ps, _ = analytic(C)
    s1, v1, _ = run(C, "CLARABEL", False); s2, v2, _ = run(C, "SCS", False)
    s3, v3, _ = run(C, "CLARABEL", True); s4, v4, _ = run(C, "SCS", True)
    e3 = abs(v3-ps)/ps if v3 is not None else float('nan')
    e4 = abs(v4-ps)/ps if v4 is not None else float('nan')
    print(f"  1e{sp:<6.0f} {s1:<24} {s2:<22} {s3:<10} {e3:>10.2e} {s4:<10} {e4:>10.2e}")
