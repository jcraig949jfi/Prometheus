"""CANON R6 — counterexample / falsification. (Canon v2.0 §3; see RUNG_LABEL_CORRECTION.md.)

Canon: *"Kill: mixed true and false conjectures — phantom-failure rate is scored. Math:
n²+n+41 is prime for n<40, fails at 40; find it. Artifact: counterexample ledger with
boundary cases."* And: **"This rung is the battery's own discipline, miniaturized."**

Which is why it matters most here: a circuit at this rung is a model of Prometheus's own
falsification battery, so its failure modes are the battery's failure modes at small scale.

Three circuits:
- BoundedSearcher: searches n in [0, horizon]; reports a counterexample only when it HAS one,
  abstains otherwise. Phantom rate 0 by construction; recall bounded by the horizon — the
  honest instrument, whose limitation is legible.
- EagerFalsifier: declares "false" whenever it cannot verify quickly. Perfect recall on false
  conjectures, and a phantom failure on every true one — the killer-of-everything pathology
  Prometheus would call a battery that kills real findings.
- CredulousAsserter: never falsifies. Zero phantoms, zero recall — the opposite failure, and
  the reason recall must be scored alongside phantoms rather than instead of them.

The artifact is a LEDGER with the boundary recorded (first failing n), not a verdict.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import sympy as sp

#: A conjecture: a name, a predicate over n, and the truth of "holds for all n >= 0".
Conjecture = Tuple[str, Callable[[int], bool], bool]


def euler_prime_conjecture() -> Conjecture:
    """n² + n + 41 is prime — true for n = 0..39, FALSE at n = 40 (41² divides it).
    The canon's named probe, and a long misleading streak by construction."""
    return ("euler_n2_n_41", lambda n: sp.isprime(n * n + n + 41), False)


def true_conjecture_sum() -> Conjecture:
    """0+1+...+n = n(n+1)/2 — genuinely true for every n."""
    return ("gauss_sum", lambda n: sum(range(n + 1)) == n * (n + 1) // 2, True)


def true_conjecture_square() -> Conjecture:
    """n² >= 0 — trivially true; included so the battery has easy trues as well as hard ones."""
    return ("square_nonneg", lambda n: n * n >= 0, True)


def late_failure_conjecture(k: int) -> Conjecture:
    """A tunable misleading streak: holds for all n < k, fails at exactly k. Lets the battery
    place the boundary beyond a circuit's horizon on purpose."""
    return (f"holds_below_{k}", lambda n, k=k: n != k, False)


@dataclass
class Finding:
    """One ledger row: what was claimed, and the boundary if a counterexample was found."""

    conjecture: str
    claimed_false: bool
    counterexample: Optional[int] = None

    @property
    def is_supported(self) -> bool:
        """A falsity claim is SUPPORTED only if it carries a witness."""
        return (not self.claimed_false) or (self.counterexample is not None)


@dataclass
class BoundedSearcher:
    """Honest instrument: bounded search, witness-carrying claims, abstention past the horizon."""

    horizon: int
    ledger: List[Finding] = field(default_factory=list)

    def judge(self, conj: Conjecture) -> Finding:
        name, pred, _truth = conj
        for n in range(self.horizon + 1):
            if not pred(n):
                f = Finding(name, claimed_false=True, counterexample=n)
                self.ledger.append(f)
                return f
        f = Finding(name, claimed_false=False)   # no counterexample WITHIN the horizon
        self.ledger.append(f)
        return f


@dataclass
class EagerFalsifier:
    """Declares falsity on suspicion: any conjecture it cannot confirm within `patience`
    steps is called false — WITHOUT a witness. Perfect recall, phantom failures everywhere."""

    patience: int = 3
    ledger: List[Finding] = field(default_factory=list)

    def judge(self, conj: Conjecture) -> Finding:
        name, pred, _truth = conj
        for n in range(self.patience + 1):
            if not pred(n):
                f = Finding(name, claimed_false=True, counterexample=n)
                self.ledger.append(f)
                return f
        f = Finding(name, claimed_false=True, counterexample=None)  # unwitnessed falsity claim
        self.ledger.append(f)
        return f


@dataclass
class CredulousAsserter:
    """Never falsifies anything. Zero phantoms, zero recall."""

    ledger: List[Finding] = field(default_factory=list)

    def judge(self, conj: Conjecture) -> Finding:
        f = Finding(conj[0], claimed_false=False)
        self.ledger.append(f)
        return f


def verdict_only_score(findings: Sequence[Finding], truths: Dict[str, bool]) -> Dict[str, float]:
    """The NAIVE battery: scores the verdict alone, ignoring whether a witness was produced.
    This is what most batteries actually do, and it is the weaker of the two defences."""
    false_conj = [f for f in findings if not truths[f.conjecture]]
    true_conj = [f for f in findings if truths[f.conjecture]]
    return {
        "recall": (sum(1 for f in false_conj if f.claimed_false) / len(false_conj))
        if false_conj else 0.0,
        "phantom_rate": (sum(1 for f in true_conj if f.claimed_false) / len(true_conj))
        if true_conj else 0.0,
    }


def score(findings: Sequence[Finding], truths: Dict[str, bool]) -> Dict[str, float]:
    """Canon's scoring: recall on false conjectures AND phantom-failure rate on true ones.

    WITNESS-REQUIRED: a false conjecture counts as caught only if the claim carries its
    counterexample. Measured this cycle, this single requirement is a SECOND and independent
    defence — it collapses the eager falsifier's apparent recall to zero even on a battery
    with no true conjectures at all, where phantom-rate scoring is vacuous.
    """
    false_conj = [f for f in findings if not truths[f.conjecture]]
    true_conj = [f for f in findings if truths[f.conjecture]]
    caught = sum(1 for f in false_conj if f.claimed_false and f.counterexample is not None)
    phantoms = sum(1 for f in true_conj if f.claimed_false)
    return {
        "recall": caught / len(false_conj) if false_conj else 0.0,
        "phantom_rate": phantoms / len(true_conj) if true_conj else 0.0,
        "unwitnessed": sum(1 for f in findings if not f.is_supported),
    }
