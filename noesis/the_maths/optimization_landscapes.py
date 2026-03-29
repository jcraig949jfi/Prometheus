"""
Optimization Landscapes — Energy/objective functions that enable chains that optimize

Connects to: [dynamical_systems, noise_perturbation, constraint_feasibility, compression_metrics]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "optimization_landscapes"
OPERATIONS = {}


def quadratic_form_energy(x):
    """Energy x^T A x where A is positive-definite from array structure. Input: array. Output: scalar."""
    n = len(x)
    # Build a simple PD matrix: identity + rank-1
    A = np.eye(n) + 0.1 * np.ones((n, n))
    return float(x @ A @ x)


OPERATIONS["quadratic_form_energy"] = {
    "fn": quadratic_form_energy,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Quadratic form energy x^T A x with positive-definite A"
}


def ising_energy_1d(x):
    """1D Ising model energy: -sum(s_i * s_{i+1}). Input: array (treated as spins). Output: scalar."""
    spins = np.sign(x)
    spins[spins == 0] = 1
    return float(-np.sum(spins[:-1] * spins[1:]))


OPERATIONS["ising_energy_1d"] = {
    "fn": ising_energy_1d,
    "input_type": "array",
    "output_type": "scalar",
    "description": "1D Ising model energy from spin array"
}


def cross_entropy_loss(x):
    """Cross-entropy loss treating first half as logits, second half as labels. Input: array. Output: scalar."""
    n = len(x)
    h = n // 2
    if h < 1:
        return 0.0
    logits = x[:h]
    # Softmax
    logits_shifted = logits - np.max(logits)
    probs = np.exp(logits_shifted) / np.sum(np.exp(logits_shifted))
    # Labels: use second half values to pick class index
    label_idx = int(np.abs(x[h]) % h)
    return float(-np.log(np.clip(probs[label_idx], 1e-12, 1.0)))


OPERATIONS["cross_entropy_loss"] = {
    "fn": cross_entropy_loss,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Cross-entropy loss from logits and label"
}


def l2_loss(x):
    """L2 loss (mean squared error) from zero. Input: array. Output: scalar."""
    return float(np.mean(x ** 2))


OPERATIONS["l2_loss"] = {
    "fn": l2_loss,
    "input_type": "array",
    "output_type": "scalar",
    "description": "L2 loss (mean squared error from zero)"
}


def huber_loss(x, delta=1.0):
    """Huber loss from zero, combining L1 and L2. Input: array. Output: scalar."""
    abs_x = np.abs(x)
    quadratic = np.minimum(abs_x, delta)
    linear = abs_x - quadratic
    return float(np.mean(0.5 * quadratic ** 2 + delta * linear))


OPERATIONS["huber_loss"] = {
    "fn": huber_loss,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Huber loss (L1/L2 hybrid) from zero"
}


def rastrigin_function(x):
    """Rastrigin function: A*n + sum(x_i^2 - A*cos(2*pi*x_i)). Input: array. Output: scalar."""
    A = 10.0
    n = len(x)
    return float(A * n + np.sum(x ** 2 - A * np.cos(2 * np.pi * x)))


OPERATIONS["rastrigin_function"] = {
    "fn": rastrigin_function,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Rastrigin multimodal test function"
}


def rosenbrock_function(x):
    """Rosenbrock function: sum(100*(x_{i+1}-x_i^2)^2 + (1-x_i)^2). Input: array. Output: scalar."""
    return float(np.sum(100.0 * (x[1:] - x[:-1] ** 2) ** 2 + (1 - x[:-1]) ** 2))


OPERATIONS["rosenbrock_function"] = {
    "fn": rosenbrock_function,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Rosenbrock valley test function"
}


def ackley_function(x):
    """Ackley function. Input: array. Output: scalar."""
    n = len(x)
    sum_sq = np.sum(x ** 2) / n
    sum_cos = np.sum(np.cos(2 * np.pi * x)) / n
    return float(-20.0 * np.exp(-0.2 * np.sqrt(sum_sq)) - np.exp(sum_cos) + 20.0 + np.e)


OPERATIONS["ackley_function"] = {
    "fn": ackley_function,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Ackley multimodal test function"
}


def schwefel_function(x):
    """Schwefel function: 418.9829*n - sum(x_i * sin(sqrt(|x_i|))). Input: array. Output: scalar."""
    n = len(x)
    return float(418.9829 * n - np.sum(x * np.sin(np.sqrt(np.abs(x)))))


OPERATIONS["schwefel_function"] = {
    "fn": schwefel_function,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Schwefel deceptive test function"
}


def constraint_penalty_sum(x, bounds_low=-5.0, bounds_high=5.0):
    """Sum of constraint violations for box constraints. Input: array. Output: scalar."""
    lower_viol = np.maximum(bounds_low - x, 0)
    upper_viol = np.maximum(x - bounds_high, 0)
    return float(np.sum(lower_viol ** 2 + upper_viol ** 2))


OPERATIONS["constraint_penalty_sum"] = {
    "fn": constraint_penalty_sum,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Sum of squared box constraint violations"
}


def gradient_finite_difference(x, func=None, eps=1e-5):
    """Finite difference gradient of L2 loss. Input: array. Output: array."""
    if func is None:
        func = lambda v: np.sum(v ** 2)
    grad = np.zeros_like(x)
    f0 = func(x)
    for i in range(len(x)):
        x_plus = x.copy()
        x_plus[i] += eps
        grad[i] = (func(x_plus) - f0) / eps
    return grad


OPERATIONS["gradient_finite_difference"] = {
    "fn": gradient_finite_difference,
    "input_type": "array",
    "output_type": "array",
    "description": "Finite difference gradient of L2 objective"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
