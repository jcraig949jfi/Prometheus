"""
Rank >= 2 Growth Law

Fit the rank-2+ fraction vs conductor to:
  1. log(N) model
  2. Power law model
  3. Logistic (saturation) model

Determine: is the growth decelerating?
"""
import numpy as np
import json
import psycopg2
from pathlib import Path
from scipy.optimize import curve_fit

print("RANK >= 2 GROWTH LAW")
print("=" * 60)

conn = psycopg2.connect(host="devmirror.lmfdb.xyz", port=5432, dbname="lmfdb",
                         user="lmfdb", password="lmfdb", connect_timeout=30)
cur = conn.cursor()

cur.execute("""
    SELECT conductor, rank FROM ec_curvedata
    WHERE rank IS NOT NULL AND conductor <= 500000
    ORDER BY conductor
""")
rows = cur.fetchall()
conn.close()

conductors = np.array([r[0] for r in rows])
ranks = np.array([r[1] for r in rows])
print(f"Total curves: {len(rows):,}")

# Compute rank-2+ fraction in fine conductor bins
n_bins = 40
cond_edges = np.logspace(np.log10(11), np.log10(500000), n_bins + 1)

bin_centers = []
bin_r2_frac = []
bin_r0_frac = []
bin_n = []

for i in range(n_bins):
    mask = (conductors >= cond_edges[i]) & (conductors < cond_edges[i + 1])
    if mask.sum() < 200:
        continue
    center = np.sqrt(cond_edges[i] * cond_edges[i + 1])
    r2_frac = np.mean(ranks[mask] >= 2)
    r0_frac = np.mean(ranks[mask] == 0)
    bin_centers.append(center)
    bin_r2_frac.append(r2_frac)
    bin_r0_frac.append(r0_frac)
    bin_n.append(int(mask.sum()))

x = np.array(bin_centers)
y = np.array(bin_r2_frac)
y0 = np.array(bin_r0_frac)
log_x = np.log10(x)

print(f"\n{'Conductor':>12} {'n':>10} {'% r>=2':>8} {'% r=0':>8}")
print("-" * 42)
for i in range(len(x)):
    print(f"{x[i]:12.0f} {bin_n[i]:10,} {y[i]*100:7.1f}% {y0[i]*100:7.1f}%")

# ---- Fit models ----
print("\n" + "-" * 40)
print("FITTING GROWTH MODELS")
print("-" * 40)

# Model 1: logarithmic: f(N) = a * log(N) + b
def log_model(x, a, b):
    return a * np.log10(x) + b

popt_log, _ = curve_fit(log_model, x, y)
y_pred_log = log_model(x, *popt_log)
ss_res_log = np.sum((y - y_pred_log)**2)
ss_tot = np.sum((y - np.mean(y))**2)
r2_log = 1 - ss_res_log / ss_tot
print(f"Logarithmic: f(N) = {popt_log[0]:.6f} * log10(N) + {popt_log[1]:.6f}")
print(f"  R2 = {r2_log:.4f}")

# Model 2: power law: f(N) = a * N^b
def power_model(x, a, b):
    return a * x**b

try:
    popt_pow, _ = curve_fit(power_model, x, y, p0=[0.001, 0.3], maxfev=5000)
    y_pred_pow = power_model(x, *popt_pow)
    r2_pow = 1 - np.sum((y - y_pred_pow)**2) / ss_tot
    print(f"Power law: f(N) = {popt_pow[0]:.6f} * N^{popt_pow[1]:.4f}")
    print(f"  R2 = {r2_pow:.4f}")
except:
    r2_pow = -1
    print("Power law: failed to converge")

# Model 3: logistic (saturation): f(N) = L / (1 + exp(-k*(log(N)-x0)))
def logistic_model(x, L, k, x0):
    return L / (1 + np.exp(-k * (np.log10(x) - x0)))

try:
    popt_logistic, _ = curve_fit(logistic_model, x, y, p0=[0.2, 2.0, 4.0], maxfev=5000)
    y_pred_logistic = logistic_model(x, *popt_logistic)
    r2_logistic = 1 - np.sum((y - y_pred_logistic)**2) / ss_tot
    print(f"Logistic: L={popt_logistic[0]:.4f}, k={popt_logistic[1]:.4f}, x0={popt_logistic[2]:.4f}")
    print(f"  Saturation level: {popt_logistic[0]*100:.1f}%")
    print(f"  Midpoint conductor: 10^{popt_logistic[2]:.2f} = {10**popt_logistic[2]:.0f}")
    print(f"  R2 = {r2_logistic:.4f}")
except Exception as e:
    r2_logistic = -1
    popt_logistic = [0, 0, 0]
    print(f"Logistic: failed ({e})")

# Model 4: linear in log(N)
coeffs_lin = np.polyfit(log_x, y, 1)
y_pred_lin = np.polyval(coeffs_lin, log_x)
r2_lin = 1 - np.sum((y - y_pred_lin)**2) / ss_tot
print(f"Linear in log(N): slope = {coeffs_lin[0]:.6f}")
print(f"  R2 = {r2_lin:.4f}")

# ---- Best model ----
print(f"\nModel comparison:")
print(f"  Logarithmic: R2 = {r2_log:.4f}")
print(f"  Power law:   R2 = {r2_pow:.4f}")
print(f"  Logistic:    R2 = {r2_logistic:.4f}")
print(f"  Linear(log): R2 = {r2_lin:.4f}")

best_r2 = max(r2_log, r2_pow, r2_logistic, r2_lin)
if best_r2 == r2_logistic and r2_logistic > 0:
    best_model = "LOGISTIC (saturation)"
    print(f"\nBest fit: {best_model}")
    print(f"  Predicts saturation at {popt_logistic[0]*100:.1f}% rank>=2")
    print(f"  Goldfeld-compatible: {'YES' if popt_logistic[0] < 0.5 else 'NO'}")
elif best_r2 == r2_log:
    best_model = "LOGARITHMIC (unbounded)"
    print(f"\nBest fit: {best_model}")
    print(f"  No saturation detected — growth continues")
else:
    best_model = "POWER LAW" if best_r2 == r2_pow else "LINEAR"
    print(f"\nBest fit: {best_model}")

# ---- Extrapolation ----
print("\n" + "-" * 40)
print("EXTRAPOLATION")
print("-" * 40)

extrap_N = [1e6, 1e7, 1e8, 1e9, 1e12]
print(f"{'Conductor':>12} {'Log model':>10} {'Logistic':>10}")
for N in extrap_N:
    pred_log = log_model(N, *popt_log) * 100
    pred_logistic = logistic_model(N, *popt_logistic) * 100 if r2_logistic > 0 else 0
    print(f"{N:12.0e} {pred_log:9.1f}% {pred_logistic:9.1f}%")

# ---- Rank-0 trend (Goldfeld's real prediction) ----
print("\n" + "-" * 40)
print("RANK-0 FRACTION TREND")
print("-" * 40)

coeffs_r0 = np.polyfit(log_x, y0, 1)
print(f"Rank-0 fraction: slope = {coeffs_r0[0]:.6f} per decade of conductor")
print(f"Current (N~400K): {y0[-1]*100:.1f}%")
print(f"Extrapolation to N=10^6: {np.polyval(coeffs_r0, 6)*100:.1f}%")
print(f"Extrapolation to N=10^9: {np.polyval(coeffs_r0, 9)*100:.1f}%")
print(f"Goldfeld prediction: 50.0%")

# When does rank-0 hit 50%?
if coeffs_r0[0] < 0:
    crossover = (0.50 - coeffs_r0[1]) / coeffs_r0[0]
    print(f"Rank-0 hits 50% at conductor 10^{crossover:.1f}" if crossover > 0 else "Never reaches 50% (wrong direction)")
    if crossover < 0:
        print("RANK-0 FRACTION IS DECREASING — MOVING AWAY FROM GOLDFELD")

results = {
    "n_bins": len(x),
    "models": {
        "logarithmic": {"r2": float(r2_log), "a": float(popt_log[0]), "b": float(popt_log[1])},
        "power_law": {"r2": float(r2_pow)},
        "logistic": {
            "r2": float(r2_logistic),
            "saturation": float(popt_logistic[0]) if r2_logistic > 0 else None,
            "midpoint_log10": float(popt_logistic[2]) if r2_logistic > 0 else None,
        },
    },
    "best_model": best_model,
    "rank0_slope": float(coeffs_r0[0]),
}

out = Path("harmonia/results/rank2_growth_law.json")
with open(out, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out}")
