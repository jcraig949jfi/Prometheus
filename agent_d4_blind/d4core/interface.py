"""D-4 abstract substrate interface, meter, and RNG discipline.

Everything downstream (metrics, navigators, gates) sees ONLY this interface.
Synthetic geometry controls and real substrates implement the same contract,
so the instrument is validated on known geometry and applied unchanged.

Anti-cheat invariants enforced by construction:
- operators are opaque indices; no names/semantics cross the interface
- navigators receive no substrate ID, no oracle output, no graph
- every evaluate() is metered against the component that caused it
- caching (if any) is inside the substrate, identical for all consumers,
  and cache hits still charge the meter (no cache asymmetry)
"""
from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod

import numpy as np


class Meter:
    """Counts logical evaluations (and auxiliary ops) per pipeline component."""

    COMPONENTS = (
        "census", "operator_census", "reversibility", "target_generation",
        "navigation", "counterfactual", "oracle_validation", "expressivity",
    )

    def __init__(self) -> None:
        self.component = "census"
        self.evals: dict[str, int] = {}
        self.mutations: dict[str, int] = {}
        self.distance_ops: dict[str, int] = {}

    def set_component(self, name: str) -> None:
        self.component = name

    def charge_eval(self, n: int = 1) -> None:
        self.evals[self.component] = self.evals.get(self.component, 0) + n

    def charge_mutation(self, n: int = 1) -> None:
        self.mutations[self.component] = self.mutations.get(self.component, 0) + n

    def charge_distance(self, n: int = 1) -> None:
        self.distance_ops[self.component] = self.distance_ops.get(self.component, 0) + n

    def snapshot(self) -> dict:
        return {
            "evals": dict(self.evals),
            "mutations": dict(self.mutations),
            "distance_ops": dict(self.distance_ops),
            "evals_total": int(sum(self.evals.values())),
        }


class Substrate(ABC):
    """Abstract computational-physics substrate.

    Genomes are opaque to consumers. Fingerprints are opaque except through
    d1 / d_aux / viable / pkey / fp_bytes / disp_features.
    """

    name: str = "abstract"
    n_ops: int = 5  # single-parent primitive mutation mechanisms

    def __init__(self) -> None:
        self.meter: Meter | None = None

    def bind_meter(self, meter: Meter) -> None:
        self.meter = meter

    # --- physics -----------------------------------------------------------
    @abstractmethod
    def random_genome(self, rng: np.random.Generator):
        ...

    @abstractmethod
    def mutate(self, genome, op_index: int, rng: np.random.Generator):
        ...

    def crossover(self, g1, g2, rng: np.random.Generator):
        """Two-parent recombination. Registered mechanism, censused separately;
        reachable only through the recombining navigator."""
        raise NotImplementedError

    def sample_op(self, rng: np.random.Generator) -> int:
        """Operator-menu distribution is PHYSICS, not navigator choice.
        Base physics: uniform. Counterfactual wrappers override this."""
        return int(rng.integers(0, self.n_ops))

    # --- behavior ----------------------------------------------------------
    @abstractmethod
    def _evaluate_raw(self, genome):
        """Substrate-internal: genome -> fingerprint (deterministic)."""
        ...

    def evaluate(self, genome):
        if self.meter is not None:
            self.meter.charge_eval()
        return self._evaluate_raw(genome)

    @abstractmethod
    def viable(self, fp) -> bool:
        ...

    @abstractmethod
    def pkey(self, fp):
        """Phenotype equivalence-class key (exact fingerprint identity)."""
        ...

    @abstractmethod
    def fp_bytes(self, fp) -> bytes:
        """Canonical bytes of the fingerprint (deterministic tie-breaks)."""
        ...

    @abstractmethod
    def d1(self, f1, f2) -> float:
        """Primary behavioral distance in [0,1] (output disagreement)."""
        ...

    def d1m(self, f1, f2) -> float:
        if self.meter is not None:
            self.meter.charge_distance()
        return self.d1(f1, f2)

    def d_aux(self, f1, f2) -> dict:
        return {}

    @abstractmethod
    def disp_features(self, f_parent, f_child) -> np.ndarray:
        """Behavioral displacement feature vector for the identifiability
        assay. Must be a function of the two fingerprints only."""
        ...

    def fp_hash(self, fp) -> str:
        return hashlib.sha256(self.fp_bytes(fp)).hexdigest()[:16]


class MenuWrapper(Substrate):
    """Counterfactual physics wrapper: restrict or reweight the operator menu.

    Presents the SAME interface; navigators cannot tell they are running
    under counterfactual physics.
    """

    def __init__(self, base: Substrate, allowed_ops=None, weights=None,
                 use_crossover: bool = True) -> None:
        super().__init__()
        self.base = base
        self.allowed = list(allowed_ops) if allowed_ops is not None else list(range(base.n_ops))
        self.n_ops = len(self.allowed)
        if weights is not None:
            w = np.asarray([weights[i] for i in self.allowed], dtype=float)
            self.weights = w / w.sum()
        else:
            self.weights = np.full(self.n_ops, 1.0 / self.n_ops)
        self.use_crossover = use_crossover
        self.name = base.name

    def bind_meter(self, meter: Meter) -> None:
        self.meter = meter
        self.base.bind_meter(meter)

    def random_genome(self, rng):
        return self.base.random_genome(rng)

    def mutate(self, genome, op_index, rng):
        return self.base.mutate(genome, self.allowed[op_index], rng)

    def crossover(self, g1, g2, rng):
        if not self.use_crossover:
            # crossover removed: degrade to a menu mutation of g1
            return self.base.mutate(g1, self.allowed[int(rng.integers(0, self.n_ops))], rng)
        return self.base.crossover(g1, g2, rng)

    def sample_op(self, rng):
        return int(rng.choice(self.n_ops, p=self.weights))

    def _evaluate_raw(self, genome):
        return self.base._evaluate_raw(genome)

    def evaluate(self, genome):
        if self.meter is not None:
            self.meter.charge_eval()
        return self.base._evaluate_raw(genome)

    def viable(self, fp):
        return self.base.viable(fp)

    def pkey(self, fp):
        return self.base.pkey(fp)

    def fp_bytes(self, fp):
        return self.base.fp_bytes(fp)

    def d1(self, f1, f2):
        return self.base.d1(f1, f2)

    def d_aux(self, f1, f2):
        return self.base.d_aux(f1, f2)

    def disp_features(self, f_parent, f_child):
        return self.base.disp_features(f_parent, f_child)
