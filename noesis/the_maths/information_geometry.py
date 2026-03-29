"""
Information Geometry — Fisher information metric, geodesics on statistical manifolds

Connects to: [differential_geometry, probability_theory, optimization, statistical_inference]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "information_geometry"
OPERATIONS = {}


def fisher_information_gaussian(x):
    """Fisher information matrix for Gaussian(mu, sigma) evaluated at parameters given by x.
    Input: array (x=[mu, sigma] or uses x as sigma values). Output: matrix.
    For a 1D Gaussian with parameters (mu, sigma), the Fisher information matrix is:
    [[1/sigma^2, 0], [0, 2/sigma^2]].
    If x has length 2, treats x as [mu, sigma]. Otherwise computes for each sigma in x.
    """
    if len(x) >= 2:
        sigma = np.abs(x[1]) + 1e-12
        fim = np.array([[1.0 / sigma**2, 0.0],
                        [0.0, 2.0 / sigma**2]])
        return fim
    sigma = np.abs(x[0]) + 1e-12
    return np.array([[1.0 / sigma**2, 0.0],
                     [0.0, 2.0 / sigma**2]])


OPERATIONS["fisher_information_gaussian"] = {
    "fn": fisher_information_gaussian,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Fisher information matrix for a 1D Gaussian parameterized by (mu, sigma)"
}


def fisher_metric_bernoulli(x):
    """Fisher information for Bernoulli(p) distribution.
    Input: array of probability values p. Output: array of Fisher information values 1/(p(1-p)).
    """
    p = np.clip(x, 1e-12, 1.0 - 1e-12)
    return 1.0 / (p * (1.0 - p))


OPERATIONS["fisher_metric_bernoulli"] = {
    "fn": fisher_metric_bernoulli,
    "input_type": "array",
    "output_type": "array",
    "description": "Fisher information for Bernoulli distribution at each probability p"
}


def geodesic_distance_normal(x):
    """Geodesic distance on the manifold of univariate normals between two distributions.
    Input: array [mu1, sigma1, mu2, sigma2]. Output: scalar.
    Uses the Fisher-Rao metric: d = sqrt((mu1-mu2)^2/sigma^2 + 2*(log(sigma1/sigma2))^2)
    approximated at the midpoint sigma = (sigma1+sigma2)/2.
    Exact formula: d = sqrt(2) * arccosh(1 + (mu1-mu2)^2/(2*sigma1*sigma2) + (sigma1^2+sigma2^2)/(2*sigma1*sigma2) - 1)
    Simplified: d = sqrt(2*log((sigma1^2+sigma2^2+(mu1-mu2)^2)/(2*sigma1*sigma2)))...
    We use the known closed-form for the Fisher-Rao distance on N(mu,sigma).
    """
    if len(x) < 4:
        return np.float64(0.0)
    mu1, s1, mu2, s2 = x[0], np.abs(x[1]) + 1e-12, x[2], np.abs(x[3]) + 1e-12
    # Fisher-Rao distance for univariate normals:
    # d = sqrt(2) * |log(s1/s2)| when mu1==mu2
    # General: d = sqrt(2) * arccosh(1 + (mu1-mu2)^2/(2*s1*s2) + (s1-s2)^2/(2*s1*s2))
    arg = 1.0 + ((mu1 - mu2)**2 + (s1 - s2)**2) / (2.0 * s1 * s2)
    arg = max(arg, 1.0)
    return np.float64(np.sqrt(2.0) * np.arccosh(arg))


OPERATIONS["geodesic_distance_normal"] = {
    "fn": geodesic_distance_normal,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Fisher-Rao geodesic distance between two univariate normal distributions"
}


def kl_divergence(x):
    """KL divergence D_KL(P||Q) between two discrete distributions.
    Input: array of length 2n, first half is P, second half is Q. Output: scalar.
    """
    n = len(x) // 2
    if n < 1:
        return np.float64(0.0)
    p = np.abs(x[:n]) + 1e-12
    q = np.abs(x[n:2*n]) + 1e-12
    p = p / p.sum()
    q = q / q.sum()
    return np.float64(np.sum(p * np.log(p / q)))


OPERATIONS["kl_divergence"] = {
    "fn": kl_divergence,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Kullback-Leibler divergence between two discrete distributions"
}


def jeffreys_divergence(x):
    """Jeffreys divergence (symmetric KL): D_KL(P||Q) + D_KL(Q||P).
    Input: array of length 2n, first half is P, second half is Q. Output: scalar.
    """
    n = len(x) // 2
    if n < 1:
        return np.float64(0.0)
    p = np.abs(x[:n]) + 1e-12
    q = np.abs(x[n:2*n]) + 1e-12
    p = p / p.sum()
    q = q / q.sum()
    kl_pq = np.sum(p * np.log(p / q))
    kl_qp = np.sum(q * np.log(q / p))
    return np.float64(kl_pq + kl_qp)


OPERATIONS["jeffreys_divergence"] = {
    "fn": jeffreys_divergence,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Jeffreys (symmetric KL) divergence between two discrete distributions"
}


def alpha_divergence(x):
    """Alpha-divergence D_alpha(P||Q) with alpha=0.5.
    Input: array of length 2n. Output: scalar.
    D_alpha = (4/(1-alpha^2)) * (1 - sum(p^((1+a)/2) * q^((1-a)/2)))
    For alpha=0.5: D_0.5 = (4/0.75)*(1 - sum(p^0.75 * q^0.25))
    """
    alpha = 0.5
    n = len(x) // 2
    if n < 1:
        return np.float64(0.0)
    p = np.abs(x[:n]) + 1e-12
    q = np.abs(x[n:2*n]) + 1e-12
    p = p / p.sum()
    q = q / q.sum()
    coeff = 4.0 / (1.0 - alpha**2)
    integral = np.sum(p**((1.0 + alpha) / 2.0) * q**((1.0 - alpha) / 2.0))
    return np.float64(coeff * (1.0 - integral))


OPERATIONS["alpha_divergence"] = {
    "fn": alpha_divergence,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Alpha-divergence (alpha=0.5) between two discrete distributions"
}


def natural_gradient(x):
    """Natural gradient: F^{-1} * grad, where F is Fisher information of a Bernoulli model.
    Input: array [p, grad_1, grad_2, ...]. Output: array.
    For Bernoulli(p), F = 1/(p(1-p)), so F^{-1} = p(1-p).
    Natural gradient = p(1-p) * euclidean_gradient.
    """
    p = np.clip(x[0], 1e-12, 1.0 - 1e-12)
    grad = x[1:]
    fisher_inv = p * (1.0 - p)
    return fisher_inv * grad


OPERATIONS["natural_gradient"] = {
    "fn": natural_gradient,
    "input_type": "array",
    "output_type": "array",
    "description": "Natural gradient descent step for a Bernoulli model"
}


def exponential_family_sufficient_stats(x):
    """Sufficient statistics for a Gaussian exponential family: T(x) = [x, x^2].
    Input: array of data points. Output: array [mean(x), mean(x^2)].
    """
    return np.array([np.mean(x), np.mean(x**2)])


OPERATIONS["exponential_family_sufficient_stats"] = {
    "fn": exponential_family_sufficient_stats,
    "input_type": "array",
    "output_type": "array",
    "description": "Sufficient statistics [E[x], E[x^2]] for Gaussian exponential family"
}


def amari_alpha_connection(x):
    """Amari alpha-connection Christoffel symbols for a 1D exponential family.
    For a Gaussian with natural parameter theta, the alpha-connection
    coefficients reduce to scalars. Returns a simplified 2x2 matrix of
    connection coefficients for the Gaussian manifold at sigma=x[0].
    Input: array. Output: matrix.
    For the Gaussian manifold parameterized by (mu, sigma), with alpha=0:
    The Levi-Civita connection Gamma^1_{12} = 0, Gamma^2_{11} = 1/sigma, etc.
    """
    sigma = np.abs(x[0]) + 1e-12
    alpha = 0.0  # Levi-Civita (alpha=0)
    # Christoffel symbols of the Fisher-Rao metric on the Gaussian manifold
    # In (mu, sigma) coordinates:
    gamma = np.zeros((2, 2, 2))
    gamma[1, 0, 0] = 1.0 / sigma       # Gamma^sigma_{mu,mu}
    gamma[0, 0, 1] = 0.0
    gamma[0, 1, 0] = 0.0
    gamma[1, 1, 1] = -1.0 / sigma      # Gamma^sigma_{sigma,sigma}
    # Return as a flattened 2x2 matrix (selecting Gamma^k_{ij} for display)
    result = np.array([[gamma[0, 0, 0], gamma[0, 0, 1]],
                       [gamma[1, 0, 0], gamma[1, 1, 1]]])
    return result


OPERATIONS["amari_alpha_connection"] = {
    "fn": amari_alpha_connection,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Christoffel symbols of the alpha-connection on the Gaussian manifold"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
