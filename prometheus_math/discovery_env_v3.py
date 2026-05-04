"""prometheus_math.discovery_env_v3 — root-space reciprocal-polynomial RL env.

Sibling to ``discovery_env.py`` (V1, coefficient enumeration) and
``discovery_env_v2.py`` (V2, GA mutation in coefficient space).  Where V1
and V2 both search **coefficient space**, V3 searches **root space**: the
agent (or a random sampler) picks angles and magnitudes for a set of
complex root pairs, then reconstructs the polynomial coefficients via
Vieta's formulas.

Why a different generator?
--------------------------
V1 hit the enumeration sparsity wall (0/216K).  V2 hit the elitist-trap
attractor (population collapses to cyclotomic).  Both failures share an
underlying suspicion: **coefficient space is the wrong coordinate system
for sub-Lehmer search**.  Salem polynomials live in a structured corner
of root-space (one root pair off the unit circle, the rest exactly on it
in conjugate pairs); coefficient space hides this structure behind
heavy combinatorial dependence.

V3 inverts the search: parameterize by the root structure, generate the
coefficients deterministically.  By construction every output is
reciprocal (root + 1/root pairs); by construction the generic Salem
shape (k-1 unit-circle pairs + 1 off-unit pair) is the *default
distribution*, not a needle in a coefficient haystack.

Action / sample space
---------------------
For a degree-2k reciprocal polynomial we sample k root pairs.  Each
root pair is (r, theta) with r > 0 magnitude and theta in (0, pi)
angle.  The full root set is {r * exp(±i*theta), 1/r * exp(±i*theta)}
for that pair (4 roots total — this is what makes the resulting poly
reciprocal of degree 4k... no wait).  We use the cleaner Salem
parameterization:

  * For ``k_unit`` pairs: r = 1 (so roots are ``exp(±i*theta)``, a
    plain conjugate pair on the unit circle, contributing degree 2 to
    the polynomial via ``x^2 - 2*cos(theta)*x + 1``).
  * For ``k_salem`` pairs: r > 1 (roots are ``r*exp(±i*theta)`` and
    ``(1/r)*exp(±i*theta)``, contributing degree 4: a Salem-style
    block ``(x^2 - 2r*cos(theta)*x + r^2) * (x^2 - 2*cos(theta)/r*x +
    1/r^2)``).
  * Optionally a real root pair ``(rho, 1/rho)`` for ``rho > 0``,
    contributing degree 2: ``(x - rho)*(x - 1/rho) = x^2 - (rho +
    1/rho)*x + 1``.

For the standard Salem-shape sampler we use:

  * ``k = degree // 2`` — total root pairs.
  * Exactly one Salem pair (r > 1).
  * ``k - 1`` unit-circle pairs (r = 1).
  * No real-root pair (set ``include_real_pair=False``).

This is the canonical Salem polynomial structure.

Discrete action bins
--------------------
Continuous (theta, r) is hard for tabular RL; we expose discrete bins:

  * ``n_theta_bins`` angles uniformly spaced in (0, pi) (default 16).
  * ``n_r_bins`` magnitudes log-spaced in (1.0001, 1.5) for the Salem
    pair (default 8).  Magnitudes for unit-circle pairs are pinned to
    1.

Coefficient extraction
----------------------
Given the root multiset, ``numpy.poly`` produces the polynomial
coefficients.  We then *round to integers* (with a tolerance check).
For most root configurations this round will not produce an integer
poly (Vieta's expansion of Salem-style angles produces irrational
coefficients in general); we keep only those configurations whose
rounded poly is within tolerance of the true Vieta expansion AND has
M close to the original Salem-style configuration.

Pilot
-----
Sample N configurations, expand each to coefficients, route any that
round to integer coefficients with M < 1.18 through the standard
``DiscoveryPipeline``.  Compare PROMOTE rate / catalog hits / M
distribution against V2 elitist on the same degree.

Honest framing: V3 is one specific inductive-bias choice — *not* a
solution to the coefficient-space failure of V1/V2.  Positive result
strengthens H2 (richer generators help); negative result strengthens
H1 (sub-Lehmer territory genuinely sparse, regardless of generator).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from sigma_kernel.sigma_kernel import SigmaKernel
from sigma_kernel.bind_eval import (
    BindEvalExtension,
    BudgetExceeded,
    CostModel,
)


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------


DEFAULT_N_THETA_BINS: int = 16
DEFAULT_N_R_BINS: int = 8
DEFAULT_R_MIN: float = 1.0001
DEFAULT_R_MAX: float = 1.5
DEFAULT_INTEGER_TOL: float = 1e-6


# ---------------------------------------------------------------------------
# Root-config dataclass
# ---------------------------------------------------------------------------


@dataclass
class RootConfig:
    """A root-space sample.

    ``unit_thetas`` is a list of angles in (0, pi) for the unit-circle
    conjugate pairs (each contributes ``x^2 - 2 cos(theta) x + 1``).
    ``salem_pair`` is an optional ``(r, theta)`` with r > 1; if present
    it contributes the degree-4 Salem block.  ``real_pair_rho`` is an
    optional ``rho > 0``; if present it contributes ``(x - rho)(x -
    1/rho)``.  The total polynomial degree is
    ``2*len(unit_thetas) + 4*(salem_pair is not None) + 2*(real_pair_rho is not None)``.
    """

    unit_thetas: Tuple[float, ...]
    salem_pair: Optional[Tuple[float, float]] = None  # (r, theta)
    real_pair_rho: Optional[float] = None

    def degree(self) -> int:
        d = 2 * len(self.unit_thetas)
        if self.salem_pair is not None:
            d += 4
        if self.real_pair_rho is not None:
            d += 2
        return d


# ---------------------------------------------------------------------------
# Vieta's expansion (root multiset -> coefficient vector)
# ---------------------------------------------------------------------------


def _expand_roots_to_real_coeffs(roots: Sequence[complex]) -> np.ndarray:
    """Expand a root multiset into a real coefficient vector via numpy.poly.

    Returns the coefficients in *descending* power order (numpy
    convention).  The result is real-valued only if the root multiset
    is closed under complex conjugation (which all our configurations
    are by construction).
    """
    poly = np.poly(np.asarray(list(roots), dtype=np.complex128))
    # If conjugation-closure was honored, the imag parts should be ~0.
    if np.max(np.abs(poly.imag)) > 1e-7:
        # Defensive — symmetric roots should always give real polys.
        # Surface the imag mass so callers can debug.
        raise ValueError(
            f"non-real coefficients from root expansion: max imag = "
            f"{np.max(np.abs(poly.imag)):.3e}"
        )
    return poly.real


def _config_to_root_multiset(cfg: RootConfig) -> List[complex]:
    """Turn a RootConfig into the explicit root multiset (closed under
    conjugation and reciprocation)."""
    roots: List[complex] = []
    for theta in cfg.unit_thetas:
        roots.append(complex(math.cos(theta), math.sin(theta)))
        roots.append(complex(math.cos(theta), -math.sin(theta)))
    if cfg.salem_pair is not None:
        r, theta = cfg.salem_pair
        # Salem block: r * e^{±i theta} and (1/r) * e^{±i theta}.
        roots.append(complex(r * math.cos(theta), r * math.sin(theta)))
        roots.append(complex(r * math.cos(theta), -r * math.sin(theta)))
        roots.append(complex((1.0 / r) * math.cos(theta), (1.0 / r) * math.sin(theta)))
        roots.append(complex((1.0 / r) * math.cos(theta), -(1.0 / r) * math.sin(theta)))
    if cfg.real_pair_rho is not None:
        rho = cfg.real_pair_rho
        roots.append(complex(rho, 0.0))
        roots.append(complex(1.0 / rho, 0.0))
    return roots


def _config_to_coeffs_real(cfg: RootConfig) -> np.ndarray:
    """RootConfig -> real coefficient vector (ascending power order, to
    match the V1/V2 convention used elsewhere in prometheus_math)."""
    roots = _config_to_root_multiset(cfg)
    desc = _expand_roots_to_real_coeffs(roots)
    return np.asarray(list(desc[::-1]), dtype=np.float64)


def _round_to_integer_coeffs(
    coeffs_real: np.ndarray, tol: float = DEFAULT_INTEGER_TOL
) -> Tuple[Optional[List[int]], float]:
    """Round a real coefficient vector to integers if the rounding
    error is within tol.  Returns ``(int_coeffs, max_error)``;
    ``int_coeffs`` is None if the rounding error exceeds tol.

    The leading coefficient is forced to +1 (monic) by construction
    (``numpy.poly`` produces monic).  Reciprocity (palindromic) is
    automatic by Vieta's of a root-and-reciprocal-closed multiset.
    """
    rounded = np.rint(coeffs_real)
    err = float(np.max(np.abs(coeffs_real - rounded)))
    if err > tol:
        return None, err
    return [int(c) for c in rounded], err


# ---------------------------------------------------------------------------
# Sampler
# ---------------------------------------------------------------------------


def _sample_root_config(
    degree: int,
    rng: np.random.Generator,
    n_theta_bins: int = DEFAULT_N_THETA_BINS,
    n_r_bins: int = DEFAULT_N_R_BINS,
    r_min: float = DEFAULT_R_MIN,
    r_max: float = DEFAULT_R_MAX,
    include_real_pair: bool = False,
    salem_pair_required: bool = True,
) -> RootConfig:
    """Sample one root configuration of total degree ``degree``.

    Default Salem-shape:
      * 1 Salem pair (degree 4)
      * ``(degree - 4 - 2*include_real_pair) // 2`` unit-circle pairs
      * 0 or 1 real root pair (degree 2 each)

    Angles are quantized to ``n_theta_bins`` bins in (0, pi); the Salem
    magnitude to ``n_r_bins`` log-spaced bins in (r_min, r_max).
    """
    if degree < 2 or degree % 2 != 0:
        raise ValueError(
            f"V3 requires even degree >= 2; got {degree}"
        )
    if salem_pair_required and degree < 4:
        raise ValueError(
            f"degree must be >= 4 when salem_pair_required; got {degree}"
        )

    theta_grid = np.linspace(
        math.pi / (n_theta_bins + 1),
        math.pi - math.pi / (n_theta_bins + 1),
        n_theta_bins,
    )
    r_grid = np.exp(np.linspace(math.log(r_min), math.log(r_max), n_r_bins))

    used_degree = 0
    salem: Optional[Tuple[float, float]] = None
    if salem_pair_required:
        r = float(r_grid[int(rng.integers(0, n_r_bins))])
        theta = float(theta_grid[int(rng.integers(0, n_theta_bins))])
        salem = (r, theta)
        used_degree += 4

    real_pair_rho: Optional[float] = None
    if include_real_pair:
        rho = float(r_grid[int(rng.integers(0, n_r_bins))])
        real_pair_rho = rho
        used_degree += 2

    remaining = degree - used_degree
    if remaining < 0:
        raise ValueError(
            f"degree {degree} too small for the requested config "
            f"(salem={salem_pair_required}, real={include_real_pair})"
        )
    n_unit = remaining // 2
    unit_thetas = tuple(
        float(theta_grid[int(rng.integers(0, n_theta_bins))])
        for _ in range(n_unit)
    )
    return RootConfig(
        unit_thetas=unit_thetas,
        salem_pair=salem,
        real_pair_rho=real_pair_rho,
    )


# ---------------------------------------------------------------------------
# Episode record
# ---------------------------------------------------------------------------


@dataclass
class EpisodeRecordV3:
    """One V3 episode = one root-config sample + Vieta expansion + (if
    integer-coeff) pipeline routing."""

    cfg: RootConfig
    coeffs_real: List[float]
    coeffs_int: Optional[List[int]]
    integer_round_error: float
    mahler_measure: float
    is_sub_lehmer: bool
    pipeline_terminal_state: Optional[str] = None
    pipeline_kill_pattern: Optional[str] = None
    is_signal_class: bool = False


# ---------------------------------------------------------------------------
# Reciprocity check (mirror V2)
# ---------------------------------------------------------------------------


def _is_reciprocal(coeffs: List[int]) -> bool:
    n = len(coeffs)
    return all(coeffs[i] == coeffs[n - 1 - i] for i in range(n // 2))


# ---------------------------------------------------------------------------
# The env
# ---------------------------------------------------------------------------


class DiscoveryEnvV3:
    """Root-space reciprocal-polynomial discovery env.

    Action space:
        ``Discrete(n_theta_bins * n_r_bins)`` per step in the
        agent-driven mode, but in the typical pilot use we sample
        configurations directly via ``sample_one()``.

    Observation space:
        ``Box(shape=(6,))`` —
            [step, last_M, best_M_overall, n_integer_coeffs_so_far,
             integer_round_error, episode_done_flag]

    Episode:
        One root-config sample per step; episode terminates after
        ``n_samples_per_episode`` samples.  Each sample's Vieta
        expansion is checked for integer-coefficient roundability;
        integer-coefficient configurations with M in (1.001, 1.18) are
        routed through DiscoveryPipeline.

    Use ``run_pilot(n_episodes, n_samples_per_episode)`` for the
    headline pilot.  Use ``sample_one()`` for ad-hoc single-config
    inspection.
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        degree: int = 14,
        n_theta_bins: int = DEFAULT_N_THETA_BINS,
        n_r_bins: int = DEFAULT_N_R_BINS,
        r_min: float = DEFAULT_R_MIN,
        r_max: float = DEFAULT_R_MAX,
        include_real_pair: bool = False,
        salem_pair_required: bool = True,
        integer_tol: float = DEFAULT_INTEGER_TOL,
        n_samples_per_episode: int = 1,
        kernel_db_path: str = ":memory:",
        cost_seconds: float = 0.5,
        seed: Optional[int] = None,
        enable_pipeline: bool = True,
    ):
        if degree < 2:
            raise ValueError(f"degree must be >= 2; got {degree}")
        if degree % 2 != 0:
            raise ValueError(
                f"V3 root-space requires even degree; got {degree}"
            )
        if n_theta_bins < 1:
            raise ValueError(f"n_theta_bins must be >= 1; got {n_theta_bins}")
        if n_r_bins < 1:
            raise ValueError(f"n_r_bins must be >= 1; got {n_r_bins}")
        if r_min <= 1.0:
            raise ValueError(
                f"r_min must be > 1.0 for Salem-style search; got {r_min}"
            )
        if r_max <= r_min:
            raise ValueError(
                f"r_max must be > r_min; got r_max={r_max}, r_min={r_min}"
            )
        if integer_tol <= 0:
            raise ValueError(f"integer_tol must be > 0; got {integer_tol}")
        if n_samples_per_episode < 1:
            raise ValueError(
                f"n_samples_per_episode must be >= 1; got {n_samples_per_episode}"
            )

        self.degree = int(degree)
        self.n_theta_bins = int(n_theta_bins)
        self.n_r_bins = int(n_r_bins)
        self.r_min = float(r_min)
        self.r_max = float(r_max)
        self.include_real_pair = bool(include_real_pair)
        self.salem_pair_required = bool(salem_pair_required)
        self.integer_tol = float(integer_tol)
        self.n_samples_per_episode = int(n_samples_per_episode)
        self.kernel_db_path = str(kernel_db_path)
        self.cost_seconds = float(cost_seconds)
        self.seed = seed
        self._enable_pipeline = bool(enable_pipeline)

        # Substrate handles (lazy-init).
        self._kernel: Optional[SigmaKernel] = None
        self._ext: Optional[BindEvalExtension] = None
        self._mm_binding_name: Optional[str] = None
        self._mm_binding_version: Optional[int] = None
        self._pipeline = None
        self._pipeline_records: List[Any] = []

        # State.
        self._rng: Optional[np.random.Generator] = None
        self._step_count: int = 0
        self._samples_this_episode: int = 0
        self._best_m_overall: float = float("inf")
        self._last_m: float = float("inf")
        self._last_round_err: float = float("inf")
        self._n_integer_coeffs: int = 0
        self._discoveries: List[EpisodeRecordV3] = []
        self._sub_lehmer_candidates: List[EpisodeRecordV3] = []
        self._n_evals: int = 0

        # Spaces (Gymnasium if available, stubs otherwise).
        self.n_actions = self.n_theta_bins * self.n_r_bins
        try:
            import gymnasium as gym  # noqa: F401
            from gymnasium import spaces

            self.observation_space = spaces.Box(
                low=-1e9,
                high=1e9,
                shape=(6,),
                dtype=np.float64,
            )
            self.action_space = spaces.Discrete(self.n_actions)
            self._gym_spaces = spaces
        except ImportError:
            from .sigma_env import _BoxStub, _DiscreteStub  # local fallback

            self.observation_space = _BoxStub((6,))
            self.action_space = _DiscreteStub(self.n_actions)
            self._gym_spaces = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        if seed is not None:
            self.seed = int(seed)
        self._rng = np.random.default_rng(self.seed)

        if self._kernel is None:
            self._kernel = SigmaKernel(self.kernel_db_path)
            self._ext = BindEvalExtension(self._kernel)
            cap = self._kernel.mint_capability("BindCap")
            binding = self._ext.BIND(
                callable_ref="techne.lib.mahler_measure:mahler_measure",
                cost_model=CostModel(max_seconds=self.cost_seconds),
                postconditions=["M(P) >= 1 for any non-zero integer poly"],
                authority_refs=["Mossinghoff Mahler tables", "Lehmer 1933"],
                cap=cap,
            )
            self._mm_binding_name = binding.symbol.name
            self._mm_binding_version = binding.symbol.version

        self._step_count = 0
        self._samples_this_episode = 0
        self._last_m = float("inf")
        self._last_round_err = float("inf")
        info = {
            "degree": self.degree,
            "n_theta_bins": self.n_theta_bins,
            "n_r_bins": self.n_r_bins,
            "n_samples_per_episode": self.n_samples_per_episode,
        }
        return self._obs(), info

    def step(
        self, action: int
    ) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        if self._kernel is None or self._rng is None:
            raise RuntimeError("env.step() called before env.reset()")
        if action < 0 or action >= self.n_actions:
            raise ValueError(f"action {action} out of [0, {self.n_actions})")

        self._step_count += 1
        self._samples_this_episode += 1

        # Decode action: (theta_bin, r_bin) — used to seed the Salem
        # block.  The remaining unit-circle pair angles are drawn
        # randomly (unsupervised exploration over the unit-circle
        # subspace; the agent only controls the Salem corner).
        theta_bin = action // self.n_r_bins
        r_bin = action % self.n_r_bins
        theta_grid = np.linspace(
            math.pi / (self.n_theta_bins + 1),
            math.pi - math.pi / (self.n_theta_bins + 1),
            self.n_theta_bins,
        )
        r_grid = np.exp(
            np.linspace(math.log(self.r_min), math.log(self.r_max), self.n_r_bins)
        )
        salem_theta = float(theta_grid[theta_bin])
        salem_r = float(r_grid[r_bin])

        n_unit = (self.degree - 4) // 2
        unit_thetas = tuple(
            float(theta_grid[int(self._rng.integers(0, self.n_theta_bins))])
            for _ in range(n_unit)
        )
        cfg = RootConfig(
            unit_thetas=unit_thetas,
            salem_pair=(salem_r, salem_theta),
            real_pair_rho=None,
        )
        rec = self._evaluate_config(cfg)

        terminated = self._samples_this_episode >= self.n_samples_per_episode
        reward = self._compute_reward(rec)

        info: Dict[str, Any] = {
            "step": self._step_count,
            "cfg": cfg,
            "mahler_measure": rec.mahler_measure,
            "is_sub_lehmer": rec.is_sub_lehmer,
            "is_signal_class": rec.is_signal_class,
            "integer_round_error": rec.integer_round_error,
            "coeffs_int": rec.coeffs_int,
            "pipeline_terminal_state": rec.pipeline_terminal_state,
            "pipeline_kill_pattern": rec.pipeline_kill_pattern,
        }
        return self._obs(), float(reward), bool(terminated), False, info

    # ------------------------------------------------------------------
    # Direct sampling API (for pilots that don't need an agent)
    # ------------------------------------------------------------------

    def sample_one(self) -> EpisodeRecordV3:
        """Sample one root-config + evaluate.  Skips action decoding."""
        if self._rng is None:
            self.reset()
        cfg = _sample_root_config(
            self.degree,
            self._rng,
            n_theta_bins=self.n_theta_bins,
            n_r_bins=self.n_r_bins,
            r_min=self.r_min,
            r_max=self.r_max,
            include_real_pair=self.include_real_pair,
            salem_pair_required=self.salem_pair_required,
        )
        return self._evaluate_config(cfg)

    def run_pilot(
        self, n_samples: int, log_every: int = 1000
    ) -> Dict[str, Any]:
        """Run a pilot of ``n_samples`` direct samples.  Returns a
        summary dict suitable for the results doc."""
        if self._rng is None:
            self.reset()
        n_integer = 0
        n_sub_lehmer = 0
        n_signal = 0
        m_values: List[float] = []
        for i in range(n_samples):
            rec = self.sample_one()
            if rec.coeffs_int is not None:
                n_integer += 1
                if math.isfinite(rec.mahler_measure):
                    m_values.append(rec.mahler_measure)
            if rec.is_sub_lehmer:
                n_sub_lehmer += 1
            if rec.is_signal_class:
                n_signal += 1
        return {
            "n_samples": n_samples,
            "n_integer_coeffs": n_integer,
            "n_sub_lehmer": n_sub_lehmer,
            "n_signal_class": n_signal,
            "fraction_integer": n_integer / max(1, n_samples),
            "best_m_overall": self._best_m_overall,
            "m_distribution_summary": (
                {
                    "min": float(min(m_values)) if m_values else None,
                    "median": float(np.median(m_values)) if m_values else None,
                    "max": float(max(m_values)) if m_values else None,
                }
            ),
        }

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def _evaluate_config(self, cfg: RootConfig) -> EpisodeRecordV3:
        """Vieta-expand a config, attempt integer-rounding, EVAL M
        through the substrate, optionally route through pipeline."""
        try:
            coeffs_real = _config_to_coeffs_real(cfg)
        except Exception:
            rec = EpisodeRecordV3(
                cfg=cfg,
                coeffs_real=[],
                coeffs_int=None,
                integer_round_error=float("inf"),
                mahler_measure=float("inf"),
                is_sub_lehmer=False,
            )
            self._discoveries.append(rec)
            return rec
        coeffs_int, err = _round_to_integer_coeffs(
            coeffs_real, tol=self.integer_tol
        )
        self._last_round_err = err
        if coeffs_int is None:
            rec = EpisodeRecordV3(
                cfg=cfg,
                coeffs_real=[float(c) for c in coeffs_real],
                coeffs_int=None,
                integer_round_error=err,
                mahler_measure=float("inf"),
                is_sub_lehmer=False,
            )
            self._discoveries.append(rec)
            return rec
        # Reciprocity check (defensive — should always pass by construction).
        if not _is_reciprocal(coeffs_int):
            rec = EpisodeRecordV3(
                cfg=cfg,
                coeffs_real=[float(c) for c in coeffs_real],
                coeffs_int=coeffs_int,
                integer_round_error=err,
                mahler_measure=float("inf"),
                is_sub_lehmer=False,
            )
            self._discoveries.append(rec)
            return rec
        # M-EVAL through substrate.
        m_value = self._evaluate_m(coeffs_int)
        self._last_m = m_value
        self._n_integer_coeffs += 1
        if math.isfinite(m_value) and m_value < self._best_m_overall:
            self._best_m_overall = m_value
        is_sub_lehmer = (
            math.isfinite(m_value)
            and 1.001 < m_value < 1.18
            and not all(c == 0 for c in coeffs_int)
        )
        is_signal = False
        terminal: Optional[str] = None
        kill: Optional[str] = None
        if is_sub_lehmer and self._enable_pipeline:
            try:
                from .discovery_pipeline import DiscoveryPipeline

                if self._pipeline is None:
                    self._pipeline = DiscoveryPipeline(
                        kernel=self._kernel, ext=self._ext
                    )
                pipe_rec = self._pipeline.process_candidate(coeffs_int, m_value)
                self._pipeline_records.append(pipe_rec)
                terminal = pipe_rec.terminal_state
                kill = pipe_rec.kill_pattern
                is_signal = pipe_rec.is_signal_class
            except Exception as e:
                terminal = f"pipeline_error:{type(e).__name__}"

        rec = EpisodeRecordV3(
            cfg=cfg,
            coeffs_real=[float(c) for c in coeffs_real],
            coeffs_int=coeffs_int,
            integer_round_error=err,
            mahler_measure=m_value,
            is_sub_lehmer=is_sub_lehmer,
            pipeline_terminal_state=terminal,
            pipeline_kill_pattern=kill,
            is_signal_class=is_signal,
        )
        self._discoveries.append(rec)
        if is_sub_lehmer:
            self._sub_lehmer_candidates.append(rec)
        return rec

    def _evaluate_m(self, coeffs_int: List[int]) -> float:
        if self._kernel is None or self._ext is None:
            raise RuntimeError("env not reset; cannot eval")
        if all(c == 0 for c in coeffs_int):
            return float("inf")
        cap = self._kernel.mint_capability("EvalCap")
        try:
            ev = self._ext.EVAL(
                binding_name=self._mm_binding_name,
                binding_version=self._mm_binding_version,
                args=[coeffs_int],
                cap=cap,
                eval_version=self._n_evals + 1,
            )
            self._n_evals += 1
        except BudgetExceeded:
            return float("inf")
        if not ev.success:
            return float("inf")
        try:
            return float(ev.output_repr)
        except (TypeError, ValueError):
            return float("inf")

    def _compute_reward(self, rec: EpisodeRecordV3) -> float:
        """Simple non-negative reward shape, mirroring V2 conventions."""
        if not math.isfinite(rec.mahler_measure) or rec.mahler_measure < 1.0 - 1e-9:
            return 0.0
        base = max(0.0, 5.0 - rec.mahler_measure)
        band = 50.0 if rec.is_sub_lehmer else 0.0
        signal = 20.0 if rec.is_signal_class else 0.0
        return base + band + signal

    # ------------------------------------------------------------------
    # Observation
    # ------------------------------------------------------------------

    def _obs(self) -> np.ndarray:
        last_m = self._last_m if math.isfinite(self._last_m) else -1.0
        best = (
            self._best_m_overall if math.isfinite(self._best_m_overall) else -1.0
        )
        err = (
            self._last_round_err if math.isfinite(self._last_round_err) else -1.0
        )
        done = (
            1.0
            if self._samples_this_episode >= self.n_samples_per_episode
            else 0.0
        )
        return np.array(
            [
                float(self._step_count),
                float(last_m),
                float(best),
                float(self._n_integer_coeffs),
                float(err),
                float(done),
            ],
            dtype=np.float64,
        )

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def discoveries(self) -> List[EpisodeRecordV3]:
        return list(self._discoveries)

    def sub_lehmer_candidates(self) -> List[EpisodeRecordV3]:
        return list(self._sub_lehmer_candidates)

    def pipeline_records(self) -> List[Any]:
        return list(self._pipeline_records)

    def best_m_overall(self) -> float:
        return float(self._best_m_overall)

    def kernel(self) -> SigmaKernel:
        if self._kernel is None:
            raise RuntimeError("env not reset yet")
        return self._kernel

    def close(self) -> None:
        if self._kernel is not None:
            try:
                self._kernel.conn.close()
            except Exception:
                pass
        self._kernel = None
        self._ext = None


__all__ = [
    "DiscoveryEnvV3",
    "EpisodeRecordV3",
    "RootConfig",
    "DEFAULT_N_THETA_BINS",
    "DEFAULT_N_R_BINS",
    "DEFAULT_R_MIN",
    "DEFAULT_R_MAX",
    "DEFAULT_INTEGER_TOL",
    "_expand_roots_to_real_coeffs",
    "_config_to_root_multiset",
    "_config_to_coeffs_real",
    "_round_to_integer_coeffs",
    "_sample_root_config",
    "_is_reciprocal",
]
