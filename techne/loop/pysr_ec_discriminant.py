"""PySR on a REAL invariant table (loop cycle 005).

Data: elliptic-curve short-Weierstrass discriminants computed by PARI (cypari2) — real
mathematical data from an authoritative engine, not synthetic noise. Known ground truth:
Delta = -16*(4*a^3 + 27*b^2). Two-arm adjudication per battery discipline:

  ARM 1 (recovery): fit (a,b) -> Delta/(-16). Success = exact law 4a^3 + 27b^2 at ~0 loss.
  ARM 2 (generator null): fit the same X against a SHUFFLED target
  (feedback_corpus_signal_needs_unbiased_generator_null): any "law" found here is the
  instrument's noise floor; ARM 1 must beat it by orders of magnitude or the recovery is
  not evidence.
"""
import pathlib
import subprocess
import sys

import numpy as np

# PARI (cypari) and PySR (juliacall) segfault when loaded into ONE process — two native
# runtimes fighting over signal handlers. Discovered live this cycle; the fix is process
# isolation: PARI generates the table in a child process, PySR consumes the file.
TABLE = pathlib.Path(__file__).with_name("ec_disc_table.csv")
GEN = r"""
import numpy as np, cypari
pari = cypari.pari
rng = np.random.default_rng(20260821)
rows = []
while len(rows) < 300:
    a, b = int(rng.integers(-20, 21)), int(rng.integers(-20, 21))
    if 4*a**3 + 27*b**2 == 0:
        continue
    e = pari.ellinit([a, b])
    rows.append((a, b, int(e[11])))
np.savetxt(r"%s", np.array(rows, dtype=float), delimiter=",")
""" % TABLE
subprocess.run([sys.executable, "-c", GEN], check=True)
data = np.loadtxt(TABLE, delimiter=",")
rng = np.random.default_rng(20260821)
X, disc = data[:, :2], data[:, 2]
y = disc / -16.0
assert np.allclose(y, 4 * X[:, 0] ** 3 + 27 * X[:, 1] ** 2), "PARI disagrees with the known law?!"
print(f"table: {len(data)} real curves from PARI; target = Delta/-16")

from pysr import PySRRegressor

def fit(target, tag):
    m = PySRRegressor(
        niterations=20, binary_operators=["+", "*"], unary_operators=[],
        maxsize=25, population_size=40, progress=False, verbosity=0,
        temp_equation_file=True, parallelism="serial", deterministic=True, random_state=0,
    )
    m.fit(X, target, variable_names=["a", "b"])
    best = m.get_best()
    print(f"{tag}: {best['equation']}  | loss {best['loss']:.4g}")
    return float(best["loss"])

loss_real = fit(y, "ARM1 real  ")
loss_null = fit(rng.permutation(y), "ARM2 null  ")
ratio = loss_null / max(loss_real, 1e-30)
print(f"null/real loss ratio: {ratio:.3g}")
print("VERDICT:", "RECOVERED-BEATS-NULL" if loss_real < 1e-6 and ratio > 1e6 else
      "WEAK" if loss_real < 1e-2 * loss_null else "FAIL")
