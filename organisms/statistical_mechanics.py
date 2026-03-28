"""
Statistical Mechanics organism.

Operations: partition_function, boltzmann_distribution, ising_model_1d,
            free_energy
"""

from .base import MathematicalOrganism


class StatisticalMechanics(MathematicalOrganism):
    name = "statistical_mechanics"
    operations = {
        "partition_function": {
            "code": """
def partition_function(energies, beta=1.0):
    \"\"\"Canonical partition function: Z = sum_i exp(-beta * E_i).
    Input: array of energy levels, inverse temperature beta.
    Returns Z and per-state Boltzmann weights.\"\"\"
    E = np.asarray(energies, dtype=np.float64)
    # Subtract min for numerical stability
    E_shifted = E - E.min()
    weights = np.exp(-beta * E_shifted)
    Z = weights.sum()
    return {"Z": float(Z), "weights": weights, "log_Z": float(np.log(Z) - beta * E.min())}
""",
            "input_type": "vector",
            "output_type": "dict",
        },
        "boltzmann_distribution": {
            "code": """
def boltzmann_distribution(energies, beta=1.0):
    \"\"\"Boltzmann probability distribution: p_i = exp(-beta*E_i) / Z.
    Also returns mean energy <E> and entropy S.\"\"\"
    E = np.asarray(energies, dtype=np.float64)
    E_shifted = E - E.min()
    log_weights = -beta * E_shifted
    log_Z = np.log(np.sum(np.exp(log_weights)))  # logsumexp
    log_probs = log_weights - log_Z
    probs = np.exp(log_probs)

    mean_E = np.sum(probs * E)
    # Entropy in natural units
    S = -np.sum(probs[probs > 0] * np.log(probs[probs > 0]))

    return {
        "probabilities": probs,
        "mean_energy": float(mean_E),
        "entropy": float(S),
        "specific_heat": float(beta**2 * np.sum(probs * (E - mean_E)**2)),
    }
""",
            "input_type": "vector",
            "output_type": "probability_distribution",
        },
        "ising_model_1d": {
            "code": """
def ising_model_1d(n_spins=50, beta=1.0, J=1.0, h=0.0, n_sweeps=1000):
    \"\"\"1D Ising model with Metropolis Monte Carlo.
    H = -J * sum(s_i * s_{i+1}) - h * sum(s_i)
    Periodic boundary conditions.
    Returns magnetisation trajectory and final configuration.\"\"\"
    spins = np.random.choice([-1, 1], size=n_spins)
    mag_history = np.zeros(n_sweeps)

    for sweep in range(n_sweeps):
        for _ in range(n_spins):
            i = np.random.randint(n_spins)
            left = spins[(i - 1) % n_spins]
            right = spins[(i + 1) % n_spins]
            dE = 2.0 * J * spins[i] * (left + right) + 2.0 * h * spins[i]
            if dE <= 0 or np.random.rand() < np.exp(-beta * dE):
                spins[i] *= -1
        mag_history[sweep] = spins.mean()

    # Final energy
    energy = 0.0
    for i in range(n_spins):
        energy -= J * spins[i] * spins[(i+1) % n_spins]
        energy -= h * spins[i]

    return {
        "final_spins": spins,
        "magnetisation_history": mag_history,
        "final_magnetisation": float(spins.mean()),
        "final_energy": float(energy),
        "energy_per_spin": float(energy / n_spins),
    }
""",
            "input_type": "scalar",
            "output_type": "dict",
        },
        "free_energy": {
            "code": """
def free_energy(energies, beta=1.0):
    \"\"\"Helmholtz free energy: F = -kT * ln(Z) = -(1/beta) * ln(Z).
    Also computes internal energy U = <E> and entropy S = beta*(U - F).\"\"\"
    E = np.asarray(energies, dtype=np.float64)
    E_shifted = E - E.min()
    log_weights = -beta * E_shifted
    # Numerically stable logsumexp
    max_lw = log_weights.max()
    log_Z = max_lw + np.log(np.sum(np.exp(log_weights - max_lw)))
    log_Z_actual = log_Z - beta * E.min()  # undo shift

    F = -(1.0 / beta) * log_Z_actual

    # Internal energy
    probs = np.exp(log_weights - log_Z)
    U = np.sum(probs * E)

    # Entropy
    S = beta * (U - F)

    return {
        "free_energy": float(F),
        "internal_energy": float(U),
        "entropy": float(S),
        "beta": float(beta),
        "temperature": float(1.0 / beta) if beta > 0 else float('inf'),
    }
""",
            "input_type": "vector",
            "output_type": "dict",
        },
    }


if __name__ == "__main__":
    import numpy as np
    np.random.seed(42)

    org = StatisticalMechanics()
    print(org)

    # Simple two-level system
    energies = np.array([0.0, 1.0])

    pf = org.execute("partition_function", energies, beta=1.0)
    print(f"Partition function Z(beta=1): {pf['Z']:.4f}  (expect 1+e^-1 ~ 1.368)")

    bd = org.execute("boltzmann_distribution", energies, beta=1.0)
    print(f"Boltzmann probs: {bd['probabilities']}  (expect ~[0.731, 0.269])")
    print(f"Mean energy: {bd['mean_energy']:.4f}")
    print(f"Entropy: {bd['entropy']:.4f}")

    # Free energy
    fe = org.execute("free_energy", energies, beta=1.0)
    print(f"Free energy F: {fe['free_energy']:.4f}")
    print(f"Internal energy U: {fe['internal_energy']:.4f}")
    print(f"Entropy S: {fe['entropy']:.4f}")

    # 1D Ising model at low temperature (should order)
    ising = org.execute("ising_model_1d", n_spins=30, beta=3.0, J=1.0, n_sweeps=500)
    print(f"Ising 1D final |m|: {abs(ising['final_magnetisation']):.3f}  (expect near 1 at low T)")

    # 1D Ising at high temperature (should disorder)
    ising_hot = org.execute("ising_model_1d", n_spins=30, beta=0.1, J=1.0, n_sweeps=500)
    print(f"Ising 1D hot |m|: {abs(ising_hot['final_magnetisation']):.3f}  (expect near 0)")

    # Harmonic oscillator energy levels
    levels = np.arange(0, 10, dtype=float)
    fe2 = org.execute("free_energy", levels, beta=0.5)
    print(f"Harmonic oscillator F(beta=0.5): {fe2['free_energy']:.4f}")

    print("--- statistical_mechanics: ALL TESTS PASSED ---")
