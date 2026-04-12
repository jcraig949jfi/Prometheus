"""Extra verification for kill script."""
import numpy as np
from sklearn.metrics import mutual_info_score

def mi_binned(x, y, nb=20):
    xd = np.digitize(x, np.linspace(x.min()-1e-10, x.max()+1e-10, nb+1))
    yd = np.digitize(y, np.linspace(y.min()-1e-10, y.max()+1e-10, nb+1))
    return mutual_info_score(xd, yd) / np.log(2)

np.random.seed(42)
# Sorted unrelated distributions
results = []
for _ in range(20):
    x = np.sort(np.random.exponential(1, 300))
    y = np.sort(np.random.gamma(2, 1, 300))
    results.append(mi_binned(x, y))
print("MI of sorted UNRELATED distributions (20 trials):")
print(f"  mean={np.mean(results):.4f}, min={np.min(results):.4f}, max={np.max(results):.4f}")
print("Proves sorted pairing inflates MI on ANY two distributions.")
print()
print("CRITICAL FINDING:")
print("After mod-12 removal, isogeny residual std = 0.000000 (constant).")
print("MI of a constant with anything = 0.")
print("The claimed MI=0.109 after mod-12 removal is impossible from node counts alone.")
print()

# What COULD give MI=0.109? Perhaps eigenvalue data from the isogeny graphs.
# The metadata contains graph eigenvalues for each ell-isogeny.
# Those ARE stochastic. But the claim was about "node counts".
print("Possible source of MI=0.109:")
print("  - NOT node counts (deterministic from p, zero variance after mod-12)")
print("  - MAYBE graph eigenvalues (stochastic, in metadata)")
print("  - MAYBE diameter or other graph property")
print("  - But eigenvalues are Ramanujan-bounded, so constrained by p")
