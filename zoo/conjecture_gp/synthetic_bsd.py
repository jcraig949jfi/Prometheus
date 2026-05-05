"""Synthetic rank-0 EC-like dataset where BSD identity holds by construction.

For Tink 2: we need a dataset where the BSD identity
    log L = log Ω + log ∏c_p + log |Sha| − 2 log |Tor|
holds exactly across all rows, plus atoms NOT in the basis (log j,
log |Δ|), plus a synthetic target T that depends on the off-basis
atoms.

This setup lets us:
- demonstrate that F043-shape candidates (correlations among BSD
  ingredients) have very high |z| and very high basis_projection_score
- demonstrate that genuinely-novel candidates (using log j or
  log |Δ|) have lower |z| but higher novelty + affordance_gain
- observe the predicted disagreement between aggregate scalar and
  Pareto-front
"""

import numpy as np


def generate(n: int = 1000, seed: int = 42) -> dict[str, np.ndarray]:
    """Generate n synthetic rank-0 EC-like objects.

    Returns a dict of named atoms (each a length-n vector).
    """
    rng = np.random.default_rng(seed)

    # BSD-ingredient atoms (in identity basis)
    log_omega = rng.normal(-2.0, 1.0, n)
    log_prod_cp = rng.gamma(shape=2.0, scale=0.5, size=n)  # positive, integer-ish
    # log |Sha|: heavy bias toward 0, some 1, rare 2 (Sha = 1, 4, 9 in practice)
    log_sha_choices = np.array([0.0, np.log(4.0), np.log(9.0)])
    log_sha = rng.choice(log_sha_choices, size=n, p=[0.85, 0.10, 0.05])
    # log |Tor|: Mazur-ish distribution
    log_tor_choices = np.log(np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12]))
    log_tor_probs = np.array([0.55, 0.20, 0.10, 0.06, 0.03, 0.025, 0.01, 0.01, 0.005, 0.005, 0.005])
    log_tor_probs = log_tor_probs / log_tor_probs.sum()
    log_tor = rng.choice(log_tor_choices, size=n, p=log_tor_probs)

    # BSD identity at rank 0 (Reg = 1):
    # log L = log Ω + log ∏c_p + log |Sha| − 2 log |Tor|
    log_L = log_omega + log_prod_cp + log_sha - 2.0 * log_tor

    # Atoms NOT in the BSD basis
    log_j = rng.normal(0.0, 5.0, n)
    log_disc = rng.normal(2.0, 2.0, n)
    log_N = rng.normal(5.0, 0.3, n)  # decade 5 conductor

    # Synthetic affordance target: depends on off-basis atoms only
    # T captures structure that genuine candidates can detect
    # but F043-family candidates cannot (no information in BSD ingredients)
    T = 2.0 * log_j + 1.0 * log_disc + rng.normal(0.0, 1.0, n)

    return {
        # in-basis atoms
        "log_omega": log_omega,
        "log_prod_cp": log_prod_cp,
        "log_sha": log_sha,
        "log_tor": log_tor,
        "log_L": log_L,
        # out-of-basis atoms
        "log_j": log_j,
        "log_disc": log_disc,
        "log_N": log_N,
        # affordance target
        "T": T,
    }


def materialize_basis(data: dict[str, np.ndarray]) -> np.ndarray:
    """Materialize the identity basis as a (n, k) matrix.

    Each column is one identity basis element evaluated on the dataset.
    The basis is what Layer B regression projects candidates against.
    """
    bsd_residual = (
        data["log_L"]
        - data["log_omega"]
        - data["log_prod_cp"]
        - data["log_sha"]
        + 2.0 * data["log_tor"]
    )
    return np.column_stack(
        [
            data["log_omega"],
            data["log_prod_cp"],
            data["log_sha"],
            data["log_tor"],
            data["log_L"],
            bsd_residual,  # always near 0; included for completeness
        ]
    )


if __name__ == "__main__":
    data = generate(n=1000, seed=42)
    print(f"Generated {len(data['log_L'])} synthetic objects.")
    print()
    print("BSD identity check (should be ~0 for all rows):")
    residual = (
        data["log_L"]
        - data["log_omega"]
        - data["log_prod_cp"]
        - data["log_sha"]
        + 2.0 * data["log_tor"]
    )
    print(f"  max |residual| = {np.abs(residual).max():.2e}")
    print(f"  mean |residual| = {np.abs(residual).mean():.2e}")
    print()
    print("Atom statistics:")
    for k, v in data.items():
        print(f"  {k:15s}  mean={v.mean():+.3f}  std={v.std():.3f}  "
              f"min={v.min():+.3f}  max={v.max():+.3f}")
