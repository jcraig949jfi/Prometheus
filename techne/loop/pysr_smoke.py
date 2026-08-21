"""PySR spike smoke test (loop cycle 003): can the pipeline run end-to-end and recover a
known planted law? Tiny budget on purpose — this validates the toolchain, not capability.
Planted: y = x0^2 + 2.5*cos(x1) - 0.5 (PySR README-style). Success = runs + finds a model
with cos and square terms scoring near-zero loss."""
import numpy as np

rng = np.random.default_rng(0)
X = rng.uniform(-3, 3, (200, 2))
y = X[:, 0] ** 2 + 2.5 * np.cos(X[:, 1]) - 0.5

from pysr import PySRRegressor

model = PySRRegressor(
    niterations=12,
    binary_operators=["+", "*", "-"],
    unary_operators=["cos"],
    population_size=30,
    progress=False,
    verbosity=0,
    temp_equation_file=True,
    parallelism="serial",
    deterministic=True,
    random_state=0,
)
model.fit(X, y)
best = model.get_best()
print("BEST:", best["equation"], "| loss:", best["loss"])
print("SMOKE:", "PASS" if best["loss"] < 1e-4 else "WEAK-PASS" if best["loss"] < 0.1 else "FAIL")
