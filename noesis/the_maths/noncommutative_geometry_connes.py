"""
Noncommutative Geometry (Connes) — Spectral triples and Connes distance (toy cases)

Connects to: [pseudo_riemannian, spin_foam, octonion_qm, rg_flow_qft]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "noncommutative_geometry_connes"
OPERATIONS = {}


def spectral_action_toy(x):
    """Spectral action Tr(f(D/Lambda)) for toy Dirac operator D.
    Input: array (eigenvalues of toy Dirac operator). Output: scalar action.
    f is a smooth cutoff: f(x) = exp(-x^2). Lambda = max eigenvalue."""
    eigvals = x
    Lambda = np.max(np.abs(eigvals))
    if Lambda < 1e-15:
        Lambda = 1.0
    # Spectral action = sum_i f(lambda_i / Lambda) = sum exp(-(lambda_i/Lambda)^2)
    action = np.sum(np.exp(-(eigvals / Lambda) ** 2))
    return np.float64(action)


OPERATIONS["spectral_action_toy"] = {
    "fn": spectral_action_toy,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Spectral action Tr(exp(-(D/Lambda)^2)) for toy Dirac operator"
}


def connes_distance(x):
    """Connes spectral distance between two pure states on a finite geometry.
    Input: array where first half = state p, second half = state q (as vectors).
    Output: scalar d(p,q) = sup{|p(a) - q(a)| : ||[D,a]|| <= 1}.
    For finite geometry with diagonal Dirac, this reduces to l1 distance / max gap."""
    n = len(x) // 2
    if n < 1:
        return np.float64(0.0)
    p = x[:n]
    q = x[n:2*n]
    # Normalize as probability distributions
    p_norm = np.abs(p) / np.sum(np.abs(p)) if np.sum(np.abs(p)) > 1e-15 else np.ones(n) / n
    q_norm = np.abs(q) / np.sum(np.abs(q)) if np.sum(np.abs(q)) > 1e-15 else np.ones(n) / n
    # For a finite spectral triple with Dirac operator D = diag(d_1, ..., d_n),
    # the Connes distance is the Wasserstein-1 distance
    # Approximate: max |p_i - q_i| / min nonzero |d_i - d_j|
    diff = np.max(np.abs(p_norm - q_norm))
    # Use input values as proxy for Dirac spectrum gap
    gaps = []
    for i in range(n):
        for j in range(i + 1, n):
            g = abs(p[i] - p[j])
            if g > 1e-15:
                gaps.append(g)
    min_gap = min(gaps) if gaps else 1.0
    distance = diff / min_gap
    return np.float64(distance)


OPERATIONS["connes_distance"] = {
    "fn": connes_distance,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Connes spectral distance between two states on finite geometry"
}


def dirac_operator_spectrum(x):
    """Spectrum of a toy Dirac operator built from input data.
    Input: array (used to construct a Hermitian matrix as D). Output: array of eigenvalues.
    D = antisymmetric part of matrix + diagonal, mimicking Dirac structure."""
    n = int(np.sqrt(len(x)))
    if n < 2:
        n = len(x)
        D = np.diag(x)
    else:
        mat = x[:n*n].reshape(n, n)
        # Dirac operator is self-adjoint: D = (mat - mat.T)/2 + diag
        D = (mat - mat.T) / 2.0
        D += np.diag(np.diag(mat))
        # Make Hermitian
        D = (D + D.T) / 2.0
    eigvals = np.linalg.eigvalsh(D)
    return eigvals


OPERATIONS["dirac_operator_spectrum"] = {
    "fn": dirac_operator_spectrum,
    "input_type": "array",
    "output_type": "array",
    "description": "Eigenvalue spectrum of toy Dirac operator from input matrix"
}


def heat_kernel_coefficient(x):
    """Heat kernel expansion coefficient a_n for Dirac operator.
    Input: array of Dirac eigenvalues. Output: array of first few Seeley-DeWitt coefficients.
    Tr(exp(-t*D^2)) = sum_n a_n * t^{(n-d)/2}. a_n ~ sum lambda_i^{-n}."""
    eigvals = x
    eigvals_sq = eigvals ** 2
    # Avoid division by zero
    eigvals_sq = np.where(eigvals_sq > 1e-15, eigvals_sq, 1e-15)
    # Heat kernel coefficients: a_0 = count, a_2 = sum 1/lambda^2, a_4 = sum 1/lambda^4
    a0 = float(len(eigvals))
    a2 = np.sum(1.0 / eigvals_sq)
    a4 = np.sum(1.0 / eigvals_sq ** 2)
    return np.array([a0, a2, a4])


OPERATIONS["heat_kernel_coefficient"] = {
    "fn": heat_kernel_coefficient,
    "input_type": "array",
    "output_type": "array",
    "description": "Seeley-DeWitt heat kernel coefficients a_0, a_2, a_4"
}


def spectral_dimension(x):
    """Spectral dimension from Dirac operator eigenvalues.
    Input: array of eigenvalues. Output: scalar d_s.
    d_s = -2 * d(log Tr(exp(-t*D^2)))/d(log t) evaluated at optimal t."""
    eigvals = x
    eigvals_sq = eigvals ** 2
    # Evaluate at multiple t values and estimate slope
    t_vals = np.logspace(-2, 2, 50)
    log_t = np.log(t_vals)
    log_trace = np.zeros_like(t_vals)
    for i, t in enumerate(t_vals):
        trace = np.sum(np.exp(-t * eigvals_sq))
        log_trace[i] = np.log(max(trace, 1e-300))
    # d_s = -2 * d(log_trace)/d(log_t) at the plateau
    d_log = np.diff(log_trace) / np.diff(log_t)
    d_s = -2.0 * np.median(d_log)
    return np.float64(max(d_s, 0.0))


OPERATIONS["spectral_dimension"] = {
    "fn": spectral_dimension,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Spectral dimension from return probability on Dirac spectrum"
}


def dixmier_trace_approx(x):
    """Approximate Dixmier trace: Tr_omega(T) = lim_{N->inf} (1/log N) sum_{n=1}^{N} mu_n.
    Input: array of singular values (eigenvalues of |T|). Output: scalar.
    For operators where mu_n ~ 1/n, this converges."""
    mu = np.sort(np.abs(x))[::-1]  # descending order
    n = len(mu)
    if n < 2:
        return np.float64(mu[0] if n > 0 else 0.0)
    partial_sums = np.cumsum(mu)
    log_n = np.log(np.arange(1, n + 1) + 1)
    # Cesaro mean of partial_sums / log(N)
    ratios = partial_sums / log_n
    # Dixmier trace is the limit (use last few values as estimate)
    trace = np.mean(ratios[-max(n // 4, 1):])
    return np.float64(trace)


OPERATIONS["dixmier_trace_approx"] = {
    "fn": dixmier_trace_approx,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Approximate Dixmier trace from singular values"
}


def fredholm_index(x):
    """Fredholm index of a toy operator: index(D) = dim(ker D) - dim(coker D).
    Input: array (eigenvalues of operator). Output: scalar index.
    Count zero eigenvalues with sign from chirality (positive vs negative indices)."""
    eigvals = x
    # Near-zero eigenvalues (within tolerance)
    tol = 0.1 * np.min(np.abs(eigvals[np.abs(eigvals) > 1e-10])) if np.any(np.abs(eigvals) > 1e-10) else 0.1
    near_zero = np.abs(eigvals) < tol
    # Chirality: count based on position (proxy for gamma_5 grading)
    n = len(eigvals)
    n_pos = np.sum(near_zero[:n // 2])
    n_neg = np.sum(near_zero[n // 2:])
    index = int(n_pos) - int(n_neg)
    return np.float64(index)


OPERATIONS["fredholm_index"] = {
    "fn": fredholm_index,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Fredholm index from operator eigenvalues"
}


def k_theory_class(x):
    """K-theory class indicator for a projection matrix.
    Input: array (flattened projection matrix). Output: scalar (trace = K-theory rank).
    For a projection P, the K-theory class [P] has rank = Tr(P)."""
    n = int(np.sqrt(len(x)))
    if n * n > len(x):
        n -= 1
    if n < 1:
        return np.float64(0.0)
    mat = np.zeros((n, n))
    mat.flat[:min(len(x), n*n)] = x[:n*n]
    # Project to nearest projection: P = V V^T where V = eigenvectors with eigenvalue ~ 1
    mat = (mat + mat.T) / 2.0
    eigvals, eigvecs = np.linalg.eigh(mat)
    # K-theory rank = number of eigenvalues close to 1
    rank = np.sum(eigvals > 0.5)
    return np.float64(rank)


OPERATIONS["k_theory_class"] = {
    "fn": k_theory_class,
    "input_type": "array",
    "output_type": "scalar",
    "description": "K-theory class rank from projection matrix trace"
}


def noncommutative_torus_spectrum(x):
    """Spectrum of Dirac operator on noncommutative torus T^2_theta.
    Input: array where x[0]=theta (irrationality parameter), rest ignored.
    Output: array of eigenvalues.
    Eigenvalues: lambda_{m,n} = 2*pi*(m + n*theta) for m,n in range."""
    theta = x[0] if len(x) > 0 else (1 + np.sqrt(5)) / 2 - 1  # golden ratio
    N = min(int(x[1]) if len(x) > 1 else 5, 10)
    eigenvalues = []
    for m in range(-N, N + 1):
        for n in range(-N, N + 1):
            lam = 2 * np.pi * (m + n * theta)
            eigenvalues.append(lam)
    eigenvalues = np.sort(np.array(eigenvalues))
    return eigenvalues


OPERATIONS["noncommutative_torus_spectrum"] = {
    "fn": noncommutative_torus_spectrum,
    "input_type": "array",
    "output_type": "array",
    "description": "Dirac spectrum on noncommutative torus T^2_theta"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
