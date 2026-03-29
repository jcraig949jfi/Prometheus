"""
Fractional QM — Fractional Schrodinger equation with Levy paths

Connects to: [unparticle_physics, rg_flow_qft, pseudo_riemannian]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "fractional_qm"
OPERATIONS = {}


def fractional_schrodinger_step(x):
    """One time step of the fractional Schrodinger equation.
    i*hbar * d psi/dt = D_alpha * (-hbar^2 Delta)^{alpha/2} * psi + V * psi
    Input: array (real part of wavefunction psi on a grid).
    Output: array (psi after one step, alpha=1.5, dt=0.001).
    Uses spectral method: fractional Laplacian in Fourier space = |k|^alpha."""
    alpha = 1.5  # Levy index
    dt = 0.001
    D_alpha = 1.0
    psi = x.astype(complex)
    n = len(psi)
    # Normalize
    norm = np.sqrt(np.sum(np.abs(psi) ** 2))
    if norm > 1e-15:
        psi /= norm
    # Fourier transform
    psi_k = np.fft.fft(psi)
    k = np.fft.fftfreq(n, d=1.0 / n) * 2 * np.pi / n
    # Fractional Laplacian: |k|^alpha
    frac_lap = np.abs(k) ** alpha
    # Time evolution: exp(-i * D_alpha * |k|^alpha * dt)
    psi_k *= np.exp(-1j * D_alpha * frac_lap * dt)
    psi_new = np.fft.ifft(psi_k)
    return np.real(psi_new)


OPERATIONS["fractional_schrodinger_step"] = {
    "fn": fractional_schrodinger_step,
    "input_type": "array",
    "output_type": "array",
    "description": "One time step of fractional Schrodinger equation (alpha=1.5)"
}


def levy_path_weight(x):
    """Compute Levy stable distribution weight for path integral.
    Input: array of path displacements. Output: array of weights.
    Levy alpha-stable PDF approximation: P(x) ~ 1/(|x|^{1+alpha}) for |x| >> 1."""
    alpha = 1.5
    displacements = x
    # Levy stable characteristic function: exp(-|k|^alpha)
    # Approximate PDF via inverse FFT or analytic tail
    weights = np.zeros_like(displacements)
    for i, dx in enumerate(displacements):
        if abs(dx) < 0.1:
            # Near zero: approximate as Gaussian-like peak
            weights[i] = np.exp(-abs(dx) ** alpha)
        else:
            # Power law tail
            weights[i] = 1.0 / (abs(dx) ** (1.0 + alpha))
    # Normalize
    total = np.sum(weights)
    if total > 1e-15:
        weights /= total
    return weights


OPERATIONS["levy_path_weight"] = {
    "fn": levy_path_weight,
    "input_type": "array",
    "output_type": "array",
    "description": "Levy stable distribution weights for path integral displacements"
}


def fractional_energy_levels(x):
    """Energy levels of fractional quantum harmonic oscillator.
    Input: array where x[0]=alpha (Levy index), x[1]=n_max.
    Output: array of energy levels E_n.
    E_n ~ (n + 1/2)^{2*alpha/(alpha+1)} for fractional oscillator (Laskin)."""
    alpha = x[0] if len(x) > 0 and 1.0 < x[0] <= 2.0 else 1.5
    n_max = int(x[1]) if len(x) > 1 and x[1] > 0 else 5
    n_max = min(n_max, 50)
    exponent = 2.0 * alpha / (alpha + 1.0)
    n_vals = np.arange(n_max)
    E_n = (n_vals + 0.5) ** exponent
    return E_n


OPERATIONS["fractional_energy_levels"] = {
    "fn": fractional_energy_levels,
    "input_type": "array",
    "output_type": "array",
    "description": "Energy levels of fractional quantum oscillator E_n ~ (n+1/2)^{2a/(a+1)}"
}


def fractional_tunneling_probability(x):
    """Tunneling probability through a barrier for fractional Schrodinger equation.
    Input: array where x[0]=alpha, x[1]=barrier_height, x[2]=barrier_width, x[3]=energy.
    Output: scalar transmission coefficient.
    T ~ exp(-C * (V-E)^{1/alpha} * L) where C depends on alpha."""
    alpha = x[0] if len(x) > 0 and 1.0 < x[0] <= 2.0 else 1.5
    V = abs(x[1]) if len(x) > 1 else 2.0
    L = abs(x[2]) if len(x) > 2 else 1.0
    E = abs(x[3]) if len(x) > 3 else 1.0
    if E >= V:
        return np.float64(1.0)
    # Fractional WKB: kappa = (V - E)^{1/alpha}
    kappa = (V - E) ** (1.0 / alpha)
    T = np.exp(-2.0 * kappa * L)
    return np.float64(min(T, 1.0))


OPERATIONS["fractional_tunneling_probability"] = {
    "fn": fractional_tunneling_probability,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Tunneling probability with fractional WKB approximation"
}


def fractional_wavepacket_spread(x):
    """Spreading rate of a wavepacket under fractional Schrodinger evolution.
    Input: array where x[0]=alpha, x[1]=initial_width, x[2]=time.
    Output: scalar (width at time t).
    sigma(t) ~ sigma_0 * (1 + (t/t_0)^2)^{1/alpha} for fractional spreading."""
    alpha = x[0] if len(x) > 0 and 1.0 < x[0] <= 2.0 else 1.5
    sigma_0 = abs(x[1]) if len(x) > 1 else 1.0
    t = abs(x[2]) if len(x) > 2 else 1.0
    if sigma_0 < 1e-15:
        sigma_0 = 1.0
    t_0 = sigma_0 ** alpha  # characteristic time
    sigma_t = sigma_0 * (1.0 + (t / t_0) ** 2) ** (1.0 / alpha)
    return np.float64(sigma_t)


OPERATIONS["fractional_wavepacket_spread"] = {
    "fn": fractional_wavepacket_spread,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Wavepacket width sigma(t) under fractional Schrodinger evolution"
}


def levy_vs_brownian_compare(x):
    """Compare Levy (alpha<2) vs Brownian (alpha=2) path statistics.
    Input: array of step sizes. Output: array [mean_step, std_step, kurtosis, levy_alpha_estimate].
    High kurtosis indicates Levy-like heavy tails."""
    steps = x
    n = len(steps)
    mean_step = np.mean(np.abs(steps))
    std_step = np.std(steps)
    # Kurtosis: excess kurtosis (Gaussian = 0, Levy > 0)
    if std_step > 1e-15:
        kurt = np.mean((steps - np.mean(steps)) ** 4) / std_step ** 4 - 3.0
    else:
        kurt = 0.0
    # Estimate alpha from tail behavior: alpha ~ 2 * log(n) / log(max/median)
    sorted_abs = np.sort(np.abs(steps))
    median_abs = np.median(np.abs(steps))
    max_abs = np.max(np.abs(steps))
    if median_abs > 1e-15 and max_abs > median_abs:
        alpha_est = 2.0 * np.log(n) / np.log(max_abs / median_abs)
        alpha_est = np.clip(alpha_est, 0.5, 2.0)
    else:
        alpha_est = 2.0  # Gaussian-like
    return np.array([mean_step, std_step, kurt, alpha_est])


OPERATIONS["levy_vs_brownian_compare"] = {
    "fn": levy_vs_brownian_compare,
    "input_type": "array",
    "output_type": "array",
    "description": "Compare Levy vs Brownian statistics: [mean, std, kurtosis, alpha_estimate]"
}


def fractional_momentum_operator(x):
    """Apply fractional momentum operator |p|^alpha to a wavefunction.
    Input: array (wavefunction values on grid). Output: array (result of |p|^alpha psi).
    Computed in Fourier space: F[|p|^alpha psi] = |k|^alpha * F[psi]."""
    alpha = 1.5
    psi = x.astype(complex)
    n = len(psi)
    psi_k = np.fft.fft(psi)
    k = np.fft.fftfreq(n, d=1.0 / n) * 2 * np.pi / n
    result_k = (np.abs(k) ** alpha) * psi_k
    result = np.fft.ifft(result_k)
    return np.real(result)


OPERATIONS["fractional_momentum_operator"] = {
    "fn": fractional_momentum_operator,
    "input_type": "array",
    "output_type": "array",
    "description": "Apply |p|^alpha to wavefunction via Fourier transform"
}


def riesz_potential_1d(x):
    """Compute 1D Riesz potential I_alpha[f](x) = integral |x-y|^{alpha-1} f(y) dy.
    Input: array of function values on uniform grid. Output: array of Riesz potential values.
    Uses discrete convolution with |x|^{alpha-1} kernel."""
    alpha = 1.5
    n = len(x)
    # Kernel: |i - j|^{alpha - 1}
    indices = np.arange(n)
    kernel = np.zeros(2 * n - 1)
    for i in range(2 * n - 1):
        d = abs(i - (n - 1))
        if d == 0:
            kernel[i] = 1.0  # regularize at origin
        else:
            kernel[i] = d ** (alpha - 1.0)
    # Convolution via FFT
    from numpy.fft import fft, ifft
    fx = np.zeros(2 * n - 1)
    fx[:n] = x
    result = np.real(ifft(fft(fx) * fft(kernel)))[:n]
    # Normalize by grid spacing
    dx = 1.0 / n
    result *= dx
    return result


OPERATIONS["riesz_potential_1d"] = {
    "fn": riesz_potential_1d,
    "input_type": "array",
    "output_type": "array",
    "description": "1D Riesz potential via convolution with |x|^{alpha-1} kernel"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
