"""Epistemic objective — the proposed SEVENTH coordinate (ChatGPT round 3, restated).

Their claim, and it lands hard on this project: coordinates 1-6 all assume the OBJECTIVE is
supplied. Band G (open-ended research: generate, test, repair, accumulate under
falsification) confronts "what should I try to learn next?" — and two actions with identical
immediate progress can differ enormously in expected uncertainty reduction ΔU(a | H). No
amount of state topology, rule synthesis, constraint memory or fresh-symbol generation picks
between them unless the architecture REPRESENTS informational value.

Their prediction: operator plasticity is the Band-S ceiling; epistemic objective is the
Band-G ceiling — and the second is the more dangerous one for Prometheus-like research
behavior. Recorded, and made executable here.

The separation used: hypothesis identification over a finite space H. Every action is one
legal experiment costing one unit — so "immediate progress" is IDENTICAL by construction and
accuracy-style scoring cannot distinguish the selectors. Only expected-information-gain
selection turns |H| into log|H|.

Directly relevant to Prometheus: this is the formal shape of the substrate's own open
question — a battery that measures whether kills happened, but not whether the kills chosen
were the INFORMATIVE ones.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, FrozenSet, List, Optional, Sequence, Tuple

Hypothesis = int
#: An experiment maps a hypothesis to the outcome that hypothesis predicts.
Experiment = Callable[[Hypothesis], bool]


def entropy(hypotheses: Sequence[Hypothesis]) -> float:
    """Uniform-prior entropy in bits — the uncertainty an experiment can reduce."""
    n = len(hypotheses)
    return math.log2(n) if n > 0 else 0.0


def expected_posterior_entropy(hypotheses: Sequence[Hypothesis], exp: Experiment) -> float:
    """E_outcome[H(posterior)] under a uniform prior: the quantity a ΔU-selector minimises."""
    n = len(hypotheses)
    if n == 0:
        return 0.0
    yes = [h for h in hypotheses if exp(h)]
    no = [h for h in hypotheses if not exp(h)]
    out = 0.0
    for branch in (yes, no):
        if branch:
            out += (len(branch) / n) * entropy(branch)
    return out


def information_gain(hypotheses: Sequence[Hypothesis], exp: Experiment) -> float:
    """ΔU(a | H): prior entropy minus expected posterior entropy, in bits."""
    return entropy(hypotheses) - expected_posterior_entropy(hypotheses, exp)


@dataclass
class Investigation:
    """One identification run: shrink H to a singleton using unit-cost experiments."""

    hypotheses: List[Hypothesis]
    truth: Hypothesis
    history: List[Tuple[str, int]] = field(default_factory=list)

    def ask(self, name: str, exp: Experiment) -> bool:
        """Run one experiment against the truth and condition H on the outcome."""
        outcome = exp(self.truth)
        self.hypotheses = [h for h in self.hypotheses if exp(h) == outcome]
        self.history.append((name, len(self.hypotheses)))
        return outcome

    @property
    def solved(self) -> bool:
        return len(self.hypotheses) == 1


def singleton_experiments(space: Sequence[Hypothesis]) -> Dict[str, Experiment]:
    """The 'test one already-likely hypothesis' family: each experiment asks 'is it h?'.
    Every one is a legal, unit-cost, genuinely progressing experiment."""
    return {f"is_{h}": (lambda x, h=h: x == h) for h in space}


def bisection_experiments(space: Sequence[Hypothesis]) -> Dict[str, Experiment]:
    """The discriminating family: each experiment splits the space by a bit of the index."""
    bits = max(1, math.ceil(math.log2(max(len(space), 2))))
    return {f"bit_{k}": (lambda x, k=k: bool(x >> k & 1)) for k in range(bits)}


def all_experiments(space: Sequence[Hypothesis]) -> Dict[str, Experiment]:
    """Both families offered together: the selector's choice is the ONLY difference."""
    return {**singleton_experiments(space), **bisection_experiments(space)}


# ---- selectors ------------------------------------------------------------------------------

def progress_greedy(inv: Investigation, experiments: Dict[str, Experiment]) -> Optional[str]:
    """MYOPIC objective: maximise P(the answer is settled THIS step) — "test an
    already-likely hypothesis". A singleton probe resolves outright on `yes` (probability
    1/|H|); a balanced split never resolves immediately (probability 0). Both are legal,
    unit-cost, genuinely-progressing experiments; only the objective differs.

    (First draft ranked by 'could eliminate something' and accidentally picked the bit-splits,
    making both selectors identical — the separation was hidden by a sloppy baseline. Recorded:
    a comparison is only as sharp as the honesty of its weaker arm.)"""
    live = list(inv.hypotheses)
    n = len(live)
    if n <= 1:
        return None
    best, best_p = None, -1.0
    for name in sorted(experiments):
        exp = experiments[name]
        yes = [h for h in live if exp(h)]
        no = [h for h in live if not exp(h)]
        if not yes or not no:
            continue  # uninformative under any objective
        p_now = (len(yes) / n if len(yes) == 1 else 0.0) + (len(no) / n if len(no) == 1 else 0.0)
        if p_now > best_p + 1e-12:
            best, best_p = name, p_now
    return best


def info_greedy(inv: Investigation, experiments: Dict[str, Experiment]) -> Optional[str]:
    """Maximises ΔU(a | H): the architecture that REPRESENTS expected uncertainty reduction."""
    best, best_gain = None, -1.0
    for name in sorted(experiments):
        gain = information_gain(inv.hypotheses, experiments[name])
        if gain > best_gain + 1e-12:
            best, best_gain = name, gain
    return best if best_gain > 1e-12 else None


def investigate(space: Sequence[Hypothesis], truth: Hypothesis, selector, max_steps: int = 1000):
    """Run an investigation to a singleton; returns (steps_used, solved)."""
    inv = Investigation(hypotheses=list(space), truth=truth)
    experiments = all_experiments(space)
    for _ in range(max_steps):
        if inv.solved:
            return len(inv.history), True
        name = selector(inv, experiments)
        if name is None:
            return len(inv.history), inv.solved
        inv.ask(name, experiments[name])
    return len(inv.history), inv.solved
