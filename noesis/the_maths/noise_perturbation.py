"""
Noise Perturbation — Feed sensitivity scoring better inputs

Connects to: [dynamical_systems, optimization_landscapes, multiscale_operators, compression_metrics]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "noise_perturbation"
OPERATIONS = {}


def gaussian_noise(x, sigma=0.1, seed=42):
    """Add Gaussian noise to array. Input: array. Output: array."""
    rng = np.random.RandomState(seed)
    return x + sigma * rng.randn(len(x))


OPERATIONS["gaussian_noise"] = {
    "fn": gaussian_noise,
    "input_type": "array",
    "output_type": "array",
    "description": "Add i.i.d. Gaussian noise to signal"
}


def correlated_noise_ar1(x, phi=0.9, sigma=0.1, seed=42):
    """Add AR(1) correlated noise. Input: array. Output: array."""
    rng = np.random.RandomState(seed)
    n = len(x)
    noise = np.zeros(n)
    noise[0] = rng.randn() * sigma
    for i in range(1, n):
        noise[i] = phi * noise[i - 1] + sigma * np.sqrt(1 - phi ** 2) * rng.randn()
    return x + noise


OPERATIONS["correlated_noise_ar1"] = {
    "fn": correlated_noise_ar1,
    "input_type": "array",
    "output_type": "array",
    "description": "Add AR(1) temporally correlated noise"
}


def pink_noise_spectrum(x, seed=42):
    """Add 1/f (pink) noise. Input: array. Output: array."""
    rng = np.random.RandomState(seed)
    n = len(x)
    white = rng.randn(n)
    freqs = np.fft.rfftfreq(n)
    freqs[0] = 1  # avoid div by zero
    spectrum = np.fft.rfft(white)
    pink = spectrum / np.sqrt(freqs)
    noise = np.fft.irfft(pink, n=n)
    noise = noise / (np.std(noise) + 1e-10) * 0.1
    return x + noise


OPERATIONS["pink_noise_spectrum"] = {
    "fn": pink_noise_spectrum,
    "input_type": "array",
    "output_type": "array",
    "description": "Add 1/f (pink) noise via spectral shaping"
}


def adversarial_perturbation_fgsm(x, target_fn=None, eps=0.1):
    """FGSM-style adversarial perturbation along gradient of L2 loss. Input: array. Output: array."""
    if target_fn is None:
        target_fn = lambda v: np.sum(v ** 2)
    grad = np.zeros_like(x)
    f0 = target_fn(x)
    delta = 1e-5
    for i in range(len(x)):
        x_p = x.copy()
        x_p[i] += delta
        grad[i] = (target_fn(x_p) - f0) / delta
    perturbation = eps * np.sign(grad)
    return x + perturbation


OPERATIONS["adversarial_perturbation_fgsm"] = {
    "fn": adversarial_perturbation_fgsm,
    "input_type": "array",
    "output_type": "array",
    "description": "FGSM adversarial perturbation along gradient sign"
}


def random_projection(x, target_dim=None, seed=42):
    """Random Gaussian projection to lower dimension. Input: array. Output: array."""
    rng = np.random.RandomState(seed)
    n = len(x)
    if target_dim is None:
        target_dim = max(2, n // 2)
    projection_matrix = rng.randn(target_dim, n) / np.sqrt(target_dim)
    return projection_matrix @ x


OPERATIONS["random_projection"] = {
    "fn": random_projection,
    "input_type": "array",
    "output_type": "array",
    "description": "Random Gaussian projection to lower dimension"
}


def dropout_mask(x, drop_rate=0.3, seed=42):
    """Apply dropout (zero out random elements, scale survivors). Input: array. Output: array."""
    rng = np.random.RandomState(seed)
    mask = rng.random(len(x)) > drop_rate
    return x * mask / (1 - drop_rate)


OPERATIONS["dropout_mask"] = {
    "fn": dropout_mask,
    "input_type": "array",
    "output_type": "array",
    "description": "Apply inverted dropout mask to array"
}


def salt_pepper_noise(x, fraction=0.2, seed=42):
    """Add salt-and-pepper noise. Input: array. Output: array."""
    rng = np.random.RandomState(seed)
    result = x.copy()
    n = len(x)
    n_noisy = int(fraction * n)
    indices = rng.choice(n, n_noisy, replace=False)
    lo, hi = x.min(), x.max()
    for idx in indices:
        result[idx] = hi if rng.random() > 0.5 else lo
    return result


OPERATIONS["salt_pepper_noise"] = {
    "fn": salt_pepper_noise,
    "input_type": "array",
    "output_type": "array",
    "description": "Add salt-and-pepper impulse noise"
}


def structured_perturbation_svd(x, rank=1, scale=0.1, seed=42):
    """Low-rank structured perturbation via SVD. Input: array. Output: array."""
    rng = np.random.RandomState(seed)
    n = len(x)
    rows = int(np.ceil(np.sqrt(n)))
    cols = int(np.ceil(n / rows))
    padded = np.zeros(rows * cols)
    padded[:n] = x
    mat = padded.reshape(rows, cols)
    U, S, Vt = np.linalg.svd(mat, full_matrices=False)
    # Perturb top-rank singular values
    r = min(rank, len(S))
    S[:r] += scale * rng.randn(r)
    perturbed = (U * S) @ Vt
    return perturbed.flatten()[:n]


OPERATIONS["structured_perturbation_svd"] = {
    "fn": structured_perturbation_svd,
    "input_type": "array",
    "output_type": "array",
    "description": "Low-rank structured perturbation via SVD"
}


def jitter_perturbation(x, amount=0.05, seed=42):
    """Add uniform jitter. Input: array. Output: array."""
    rng = np.random.RandomState(seed)
    scale = (x.max() - x.min()) * amount if x.max() != x.min() else amount
    return x + rng.uniform(-scale, scale, len(x))


OPERATIONS["jitter_perturbation"] = {
    "fn": jitter_perturbation,
    "input_type": "array",
    "output_type": "array",
    "description": "Add uniform jitter noise scaled to data range"
}


def noise_robustness_score(x, n_trials=20, sigma=0.1, seed=42):
    """Measure how stable a function of x is under noise. Input: array. Output: scalar."""
    rng = np.random.RandomState(seed)
    base_metric = np.sum(x ** 2)
    deviations = []
    for _ in range(n_trials):
        noisy = x + sigma * rng.randn(len(x))
        noisy_metric = np.sum(noisy ** 2)
        deviations.append(abs(noisy_metric - base_metric))
    return float(1.0 / (1.0 + np.mean(deviations)))


OPERATIONS["noise_robustness_score"] = {
    "fn": noise_robustness_score,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Robustness score measuring stability under Gaussian noise"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
