"""
Landscape: tensor-parameterized function R^d -> R.

Designed as a GA gene with TYPE-PRESERVED sub-genes so mutation operators can
preserve landscape class (quadratic-dominant / ridge-dominant / GMM-dominant)
while perturbing within a class.

Gene layout (for d dimensions):
    quad        : (d, d) symmetric matrix A       -> (1/2) x^T A x
                  stored as upper triangle (d*(d+1)/2 floats).
                  Optional near-singular penalty: scale one eigenvalue toward 0.
    ridge       : k_ridge anisotropic ridge terms
                  each: direction u (unit vec, d floats) + amplitude a + width w
                  contributes  a * (1 + exp(-(u . x)^2 / w^2)) ** -1   (logistic ridge)
    gmm         : k_gmm Gaussian components
                  each: center c (d), log-diag Sigma (d), signed weight w_i
                  contributes  Sum  w_i * exp(-0.5 * (x-c) Sigma^-1 (x-c))

f(x) = x^T A x / 2 + sum ridges(x) + sum gmm(x)

Signed GMM weights allow HILLS as well as BASINS, which gives plateaus / deceptive
valleys / ridge-embedded minima rather than one dominant basin.

The sub-genes are stored separately so evolve.py can mutate each independently or
crossover at the sub-gene boundary, preserving structural character.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np


# ---------- sub-genes --------------------------------------------------------

@dataclass
class QuadGene:
    """Symmetric (d,d) matrix stored by upper triangle."""
    d: int
    upper: np.ndarray  # length d*(d+1)//2

    def matrix(self) -> np.ndarray:
        A = np.zeros((self.d, self.d))
        i, j = np.triu_indices(self.d)
        A[i, j] = self.upper
        A[j, i] = self.upper
        return A

    def evaluate(self, x: np.ndarray) -> np.ndarray:
        A = self.matrix()
        # broadcast: x may be (N,d)
        if x.ndim == 1:
            return 0.5 * x @ A @ x
        return 0.5 * np.einsum('ni,ij,nj->n', x, A, x)


@dataclass
class RidgeGene:
    """Anisotropic ridge with switchable shape.

    shape='lorentzian' (PRIMARY, sharp barrier):
        a / (1 + ((u . x - b) / w)^2)
        -> narrow high-curvature barrier, strong separability
    shape='logistic' (SECONDARY, smooth deformation):
        a / (1 + exp(-(u . x - b)^2 / w^2))
    """
    direction: np.ndarray   # (d,), unit
    amplitude: float
    bias: float
    width: float
    shape: str = "lorentzian"

    def evaluate(self, x: np.ndarray) -> np.ndarray:
        u = self.direction / (np.linalg.norm(self.direction) + 1e-12)
        proj = (x @ u) if x.ndim > 1 else float(x @ u)
        z = (proj - self.bias) / max(self.width, 1e-6)
        if self.shape == "lorentzian":
            return self.amplitude / (1.0 + z * z)
        # logistic fallback
        return self.amplitude / (1.0 + np.exp(-z * z))


@dataclass
class GaussGene:
    """Axis-aligned Gaussian component (diagonal covariance).

    Contribution:   w * exp(-0.5 * sum_k (x_k - c_k)^2 / sigma_k^2)
    w may be negative (hill) or positive (basin — subtracted from f).
    We follow the 'pit' convention: POSITIVE w lowers f (creates a basin).
    """
    center: np.ndarray      # (d,)
    log_sigma: np.ndarray   # (d,) log-scale of per-dim std
    weight: float           # signed

    def evaluate(self, x: np.ndarray) -> np.ndarray:
        sigma = np.exp(self.log_sigma)
        if x.ndim == 1:
            diff = (x - self.center) / sigma
            return -self.weight * math.exp(-0.5 * float(diff @ diff))
        diff = (x - self.center) / sigma
        return -self.weight * np.exp(-0.5 * np.einsum('ni,ni->n', diff, diff))


@dataclass
class FourierGene:
    """Sinusoidal mode: a * sin(omega . x + phi).

    omega is a frequency vector in R^d; |omega| controls oscillation rate.
    Multiple FourierGenes superpose to make rough / multi-frequency landscapes
    that gradient methods often fail to navigate.
    """
    omega: np.ndarray       # (d,) frequency vector
    phase: float
    amplitude: float

    def evaluate(self, x: np.ndarray) -> np.ndarray:
        if x.ndim == 1:
            return self.amplitude * math.sin(float(self.omega @ x) + self.phase)
        return self.amplitude * np.sin(x @ self.omega + self.phase)


# ---------- landscape --------------------------------------------------------

@dataclass
class Landscape:
    d: int
    quad: QuadGene
    ridges: List[RidgeGene] = field(default_factory=list)
    gmm: List[GaussGene] = field(default_factory=list)
    fourier: List[FourierGene] = field(default_factory=list)

    # bookkeeping (NOT used as descriptor — mode is exploration-only)
    mode: str = "mixed"         # basin|ridge|plateau|deceptive|oscillatory|mixed
    genome_id: str = ""
    parent_ids: tuple = ()

    # ---- evaluation ----
    def evaluate(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        y = self.quad.evaluate(x)
        for r in self.ridges:
            y = y + r.evaluate(x)
        for g in self.gmm:
            y = y + g.evaluate(x)
        for f in self.fourier:
            y = y + f.evaluate(x)
        return y

    def __call__(self, x):
        return self.evaluate(x)

    # ---- cheap derivatives via finite differences ----
    def grad(self, x: np.ndarray, h: float = 1e-4) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        g = np.zeros(self.d)
        for i in range(self.d):
            xp = x.copy(); xp[i] += h
            xm = x.copy(); xm[i] -= h
            g[i] = (float(self.evaluate(xp)) - float(self.evaluate(xm))) / (2 * h)
        return g

    def hessian(self, x: np.ndarray, h: float = 1e-3) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        H = np.zeros((self.d, self.d))
        f0 = float(self.evaluate(x))
        for i in range(self.d):
            for j in range(i, self.d):
                xpp = x.copy(); xpp[i] += h; xpp[j] += h
                xpm = x.copy(); xpm[i] += h; xpm[j] -= h
                xmp = x.copy(); xmp[i] -= h; xmp[j] += h
                xmm = x.copy(); xmm[i] -= h; xmm[j] -= h
                val = (float(self.evaluate(xpp)) - float(self.evaluate(xpm))
                       - float(self.evaluate(xmp)) + float(self.evaluate(xmm))) / (4 * h * h)
                H[i, j] = H[j, i] = val
        return H

    # ---- genome flatten (for mutation utilities) ----
    def genome_blocks(self):
        """Return list of (name, ndarray) sub-genes for selective mutation."""
        blocks = [("quad_upper", self.quad.upper.copy())]
        for i, r in enumerate(self.ridges):
            blocks.append((f"ridge{i}_dir", r.direction.copy()))
            blocks.append((f"ridge{i}_ampl", np.array([r.amplitude])))
            blocks.append((f"ridge{i}_bias", np.array([r.bias])))
            blocks.append((f"ridge{i}_width", np.array([r.width])))
        for i, g in enumerate(self.gmm):
            blocks.append((f"gmm{i}_center", g.center.copy()))
            blocks.append((f"gmm{i}_logsig", g.log_sigma.copy()))
            blocks.append((f"gmm{i}_weight", np.array([g.weight])))
        return blocks


# ---------- samplers ---------------------------------------------------------

def _sample_quad(d, eig_lo, eig_hi, near_singular_prob, scale, rng):
    U = np.linalg.qr(rng.standard_normal((d, d)))[0]
    eigvals = rng.uniform(eig_lo, eig_hi, size=d)
    if rng.random() < near_singular_prob:
        idx = int(rng.integers(d))
        eigvals[idx] = 10 ** rng.uniform(-3, -1)
    A = scale * (U * eigvals) @ U.T
    i, j = np.triu_indices(d)
    return QuadGene(d=d, upper=A[i, j])


def _sample_ridge(d, amp_lo, amp_hi, width_lo, width_hi, shape, rng):
    u = rng.standard_normal(d); u = u / (np.linalg.norm(u) + 1e-12)
    return RidgeGene(
        direction=u,
        amplitude=rng.uniform(amp_lo, amp_hi),
        bias=rng.uniform(-2.0, 2.0),
        width=rng.uniform(width_lo, width_hi),
        shape=shape,
    )


def _sample_gauss(d, center_box, sigma_lo, sigma_hi, w_lo, w_hi, negative_prob, rng):
    center = rng.uniform(-center_box, center_box, size=d)
    log_sigma = rng.uniform(math.log(sigma_lo), math.log(sigma_hi), size=d)
    w = rng.uniform(w_lo, w_hi)
    if rng.random() < negative_prob:
        w = -w
    return GaussGene(center=center, log_sigma=log_sigma, weight=w)


def _sample_fourier(d, omega_lo, omega_hi, amp_lo, amp_hi, rng):
    """Sample a Fourier mode with isotropic random direction and frequency
    magnitude sampled log-uniformly in [omega_lo, omega_hi]."""
    direction = rng.standard_normal(d)
    direction = direction / (np.linalg.norm(direction) + 1e-12)
    omega_mag = math.exp(rng.uniform(math.log(omega_lo), math.log(omega_hi)))
    return FourierGene(
        omega=direction * omega_mag,
        phase=rng.uniform(0.0, 2 * math.pi),
        amplitude=rng.uniform(amp_lo, amp_hi) * (1 if rng.random() > 0.5 else -1),
    )


# ---- explicit generator modes ----------------------------------------------

def _maybe_small_fourier(d, rng, prob=0.3):
    """Optional small high-frequency perturbation for non-oscillatory modes.
    Returns a (possibly empty) list of FourierGenes with low amplitude."""
    if rng.random() > prob:
        return []
    n = int(rng.integers(1, 3))
    return [_sample_fourier(d, omega_lo=2.0, omega_hi=4.0, amp_lo=0.05, amp_hi=0.20, rng=rng)
            for _ in range(n)]


def sample_basin_mode(d=2, rng=None):
    """GMM-dominant. Several basins of varied depth, weak quadratic bowl."""
    rng = rng or np.random.default_rng()
    quad = _sample_quad(d, 0.1, 0.8, 0.0, 0.2, rng)
    ridges = []
    gmm = [_sample_gauss(d, 3.0, 0.35, 1.2, 0.8, 2.0, 0.15, rng) for _ in range(4)]
    fourier = _maybe_small_fourier(d, rng)
    return Landscape(d=d, quad=quad, ridges=ridges, gmm=gmm, fourier=fourier,
                     mode="basin", genome_id=f"basin_{rng.integers(1<<31)}")


def sample_ridge_mode(d=2, rng=None):
    """Ridge-dominant. 2-3 Lorentzian barriers, moderate quad, few GMM pits."""
    rng = rng or np.random.default_rng()
    quad = _sample_quad(d, 0.3, 1.0, 0.05, 0.3, rng)
    n_r = int(rng.integers(2, 4))
    ridges = [_sample_ridge(d, 0.8, 3.5, 0.2, 0.6, "lorentzian", rng)
              for _ in range(n_r)]
    gmm = [_sample_gauss(d, 3.0, 0.4, 1.0, 0.5, 1.0, 0.0, rng) for _ in range(2)]
    fourier = _maybe_small_fourier(d, rng)
    return Landscape(d=d, quad=quad, ridges=ridges, gmm=gmm, fourier=fourier,
                     mode="ridge", genome_id=f"ridge_{rng.integers(1<<31)}")


def sample_plateau_mode(d=2, rng=None):
    """Plateau. Very small quadratic (flat base), 1-2 soft logistic ridges
    as weak boundary, a couple of small GMMs."""
    rng = rng or np.random.default_rng()
    quad = _sample_quad(d, 0.01, 0.1, 0.6, 0.05, rng)
    ridges = [_sample_ridge(d, 0.3, 1.0, 0.8, 1.8, "logistic", rng)
              for _ in range(int(rng.integers(1, 3)))]
    gmm = [_sample_gauss(d, 3.0, 0.5, 1.4, 0.3, 0.8, 0.1, rng)
           for _ in range(int(rng.integers(0, 3)))]
    fourier = _maybe_small_fourier(d, rng, prob=0.2)
    return Landscape(d=d, quad=quad, ridges=ridges, gmm=gmm, fourier=fourier,
                     mode="plateau", genome_id=f"plateau_{rng.integers(1<<31)}")


def sample_deceptive_mode(d=2, rng=None):
    """Deceptive. Strong quadratic bowl hiding negative-weight Gaussians
    (hills/saddles) near its minimum -> gradient methods funnel toward the bowl
    but the true minima are off-center pits behind hills."""
    rng = rng or np.random.default_rng()
    quad = _sample_quad(d, 0.8, 1.5, 0.0, 0.5, rng)
    ridges = [_sample_ridge(d, 0.5, 1.5, 0.4, 0.8, "lorentzian", rng)
              for _ in range(int(rng.integers(0, 2)))]
    gmm = []
    for _ in range(2):
        gmm.append(_sample_gauss(d, 1.2, 0.4, 0.9, 1.0, 2.5, 1.0, rng))
        gmm.append(_sample_gauss(d, 3.0, 0.35, 0.9, 1.2, 2.5, 0.0, rng))
    fourier = _maybe_small_fourier(d, rng)
    return Landscape(d=d, quad=quad, ridges=ridges, gmm=gmm, fourier=fourier,
                     mode="deceptive", genome_id=f"decept_{rng.integers(1<<31)}")


def sample_oscillatory_mode(d=2, rng=None):
    """Fourier-dominant. Weak quadratic, no GMM, multiple sinusoidal modes
    spanning low to mid frequencies. Designed to be gradient-trap rich and
    test whether descriptors capture frequency content."""
    rng = rng or np.random.default_rng()
    quad = _sample_quad(d, 0.05, 0.4, 0.0, 0.15, rng)  # gentle bowl
    ridges = [_sample_ridge(d, 0.3, 1.0, 0.4, 1.0, "lorentzian", rng)
              for _ in range(int(rng.integers(0, 2)))]
    gmm = []
    n_f = int(rng.integers(3, 7))
    fourier = [_sample_fourier(d, omega_lo=0.8, omega_hi=4.0,
                                amp_lo=0.4, amp_hi=1.5, rng=rng)
               for _ in range(n_f)]
    return Landscape(d=d, quad=quad, ridges=ridges, gmm=gmm, fourier=fourier,
                     mode="oscillatory", genome_id=f"osc_{rng.integers(1<<31)}")


MODE_SAMPLERS = {
    "basin":       sample_basin_mode,
    "ridge":       sample_ridge_mode,
    "plateau":     sample_plateau_mode,
    "deceptive":   sample_deceptive_mode,
    "oscillatory": sample_oscillatory_mode,
}


def sample_mixed_landscape(d=2, rng=None, weights=None):
    """Pick a mode uniformly by default, sample from it."""
    rng = rng or np.random.default_rng()
    modes = list(MODE_SAMPLERS.keys())
    if weights is None:
        w = np.ones(len(modes)) / len(modes)
    else:
        w = np.array([weights.get(m, 0.0) for m in modes])
        w = w / w.sum()
    mode = str(rng.choice(modes, p=w))
    return MODE_SAMPLERS[mode](d=d, rng=rng)


# Legacy single-sampler (kept for backward-compat with preview.py first run)
def random_landscape(
    d: int = 2,
    n_ridges: int = 1,
    n_gmm: int = 4,
    rng: Optional[np.random.Generator] = None,
    **_
) -> Landscape:
    """Backward-compatible sampler: uniform over 4 modes."""
    return sample_mixed_landscape(d=d, rng=rng)
