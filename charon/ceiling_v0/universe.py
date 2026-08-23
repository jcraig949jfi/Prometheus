"""Alien Universe v0 — procedural hidden-law environment.

RESTORED 2026-08-22 after the working-tree loss (see RECOVERY.md). Reconstructed
from the session transcript and cross-checked against the surviving
__pycache__/universe.cpython-312.pyc. Fidelity is verified behaviourally: the
deterministic suite must reproduce P3c 0.364, P3b 0.483, P3d 0.647 over 20 seeds.

Ground truth lives here and is NEVER exposed through the reasoner-facing view.
Everything is deterministic given a seed. No LLM ever touches this module's
internals; it only ever sees `Session.run` results.
"""
from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

State = Tuple[int, ...]


class BudgetExhausted(RuntimeError):
    pass


class InteractionForbidden(RuntimeError):
    """Raised if anything tries to interact during a sealed evaluation."""


@dataclass(frozen=True)
class UniverseSpec:
    seed: int
    m: int = 3           # size of each hidden coordinate
    k: int = 3           # hidden dimensionality  -> |S| = 27
    n_actions: int = 4
    n_tags: int = 4
    n_symbols: int = 4
    family: str = "F_T"  # "F_T" translations (abelian, order 27)
                         # "F_P" permutation+translation (NON-abelian, order 162)
    max_word_len: int = 6

    def digest(self) -> str:
        raw = (f"{self.seed}|{self.m}|{self.k}|{self.n_actions}|{self.n_tags}"
               f"|{self.n_symbols}|{self.family}|{self.max_word_len}")
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


class Universe:
    """Hidden laws. Evaluator-only surface."""

    def __init__(self, spec: UniverseSpec):
        self.spec = spec
        rng = random.Random(spec.seed * 1_000_003 + 17)
        m, k = spec.m, spec.k

        # --- hidden action shifts, resampled until they generate the full group
        while True:
            shifts = [tuple(rng.randrange(m) for _ in range(k))
                      for _ in range(spec.n_actions)]
            if self._generates_all(shifts, m, k):
                break
        self._shifts: List[State] = shifts

        # --- hidden coordinate permutations, identity for the abelian family.
        # F_P makes the action monoid NON-COMMUTATIVE: word order now matters, so
        # every commutation rule that is true in F_T is false here. It is the
        # sharpest available test of whether a mechanism found in F_T is a
        # property of the substrate or of the abelian group it was tuned on.
        # F_M is the INTERMEDIATE family, added at iteration 21 to make an
        # out-of-sample test of the compressibility account possible: exactly one
        # action carries a permutation, so the monoid is "mostly abelian" and its
        # redundancy sits between F_T's and F_P's by construction.
        import itertools
        identity = tuple(range(k))
        if spec.family == "F_T":
            self._perms: List[Tuple[int, ...]] = [identity] * spec.n_actions
        elif spec.family in ("F_P", "F_M", "F_M2", "F_MT"):
            allp = [p for p in itertools.permutations(range(k)) if p != identity]
            # F_MT: the single permuting action is restricted to a TRANSPOSITION
            # (order 2) rather than any permutation (which may be an order-3
            # cycle). Less disruption per application, so the monoid should be
            # MORE compressible than F_M and sit between it and abelian F_T.
            # Added at iteration 25 to give the compressibility account a
            # discriminating out-of-sample test at the HIGH end of the curve,
            # where a predicted gap is large enough that its band excludes zero.
            def _is_transposition(p):
                return sum(1 for i, v in enumerate(p) if v != i) == 2
            perms = [p for p in allp if _is_transposition(p)]                 if spec.family == "F_MT" else allp
            n_perm = {"F_P": spec.n_actions, "F_M": 1,
                      "F_M2": 2, "F_MT": 1}[spec.family]
            self._perms = [tuple(rng.choice(perms)) if i < n_perm else identity
                           for i in range(spec.n_actions)]
        else:
            raise ValueError(f"unknown family {spec.family!r}")

        # --- hidden entry points
        self._tag_state: List[State] = [
            tuple(rng.randrange(m) for _ in range(k)) for _ in range(spec.n_tags)
        ]

        # --- lossy, near-balanced sensor
        order = list(self._all_states())
        rng.shuffle(order)
        self._sensor: Dict[State, int] = {
            s: i % spec.n_symbols for i, s in enumerate(order)}

        self.actions = [f"A{i}" for i in range(spec.n_actions)]
        self.tags = [f"K{i}" for i in range(spec.n_tags)]
        self.symbols = [f"q{i}" for i in range(spec.n_symbols)]
        self._a_index = {a: i for i, a in enumerate(self.actions)}
        self._t_index = {t: i for i, t in enumerate(self.tags)}

    # ---------------------------------------------------------------- internals
    def _all_states(self) -> List[State]:
        m, k = self.spec.m, self.spec.k
        out: List[State] = [()]
        for _ in range(k):
            out = [s + (v,) for s in out for v in range(m)]
        return out

    @staticmethod
    def _generates_all(shifts: Sequence[State], m: int, k: int) -> bool:
        seen = {tuple([0] * k)}
        frontier = [tuple([0] * k)]
        while frontier:
            cur = frontier.pop()
            for b in shifts:
                nxt = tuple((cur[i] + b[i]) % m for i in range(k))
                if nxt not in seen:
                    seen.add(nxt)
                    frontier.append(nxt)
        return len(seen) == m ** k

    def _step(self, x: State, a_idx: int) -> State:
        b = self._shifts[a_idx]
        p = self._perms[a_idx]
        m = self.spec.m
        return tuple((x[p[i]] + b[i]) % m for i in range(self.spec.k))

    # ------------------------------------------------------------ ground truth
    def true_trace(self, tag: str, word: Sequence[str]) -> List[int]:
        """Symbol indices at every position, length len(word)+1."""
        x = self._tag_state[self._t_index[tag]]
        out = [self._sensor[x]]
        for a in word:
            x = self._step(x, self._a_index[a])
            out.append(self._sensor[x])
        return out

    def true_final_symbol(self, tag: str, word: Sequence[str]) -> str:
        return self.symbols[self.true_trace(tag, word)[-1]]

    def true_word_element(self, word: Sequence[str]):
        """The hidden transformation a word denotes, as its action on EVERY state.

        Two words are interchangeable exactly when they induce the same map, so
        this is the correct equivalence for any family. Representing the element
        by its full image tuple rather than by a shift vector keeps the audits
        family-agnostic; for F_T it is equivalent to the old shift-vector
        representation because a translation is determined by its action.
        """
        states = self._all_states()
        idx = [self._a_index[a] for a in word]
        out = []
        for x in states:
            for ai in idx:
                x = self._step(x, ai)
            out.append(x)
        return tuple(out)

    def true_class_count(self) -> int:
        return self.spec.m ** self.spec.k


# ---------------------------------------------------------------------------
#  Reasoner-facing views
# ---------------------------------------------------------------------------


@dataclass
class Interaction:
    idx: int
    tag: str
    word: List[str]
    readout: List[str]
    source: str  # 'llm' | 'ruletest' | 'policy' | 'baseline' | 'c4check'


@dataclass
class Session:
    """Budget-metered interaction channel. This is ALL the reasoner ever sees."""

    universe: Universe
    budget: int
    log: List[Interaction] = field(default_factory=list)
    used: int = 0

    @property
    def remaining(self) -> int:
        return self.budget - self.used

    def run(self, tag: str, word: Sequence[str], source: str = "llm") -> List[str]:
        if self.used >= self.budget:
            raise BudgetExhausted(f"budget {self.budget} exhausted")
        tag = tag.strip()
        word = [w.strip() for w in word if w.strip()]
        if tag not in self.universe.tags:
            raise ValueError(f"unknown tag {tag!r}")
        if not word or len(word) > self.universe.spec.max_word_len:
            raise ValueError(
                f"sequence length {len(word)} outside "
                f"1..{self.universe.spec.max_word_len}")
        for a in word:
            if a not in self.universe.actions:
                raise ValueError(f"unknown item {a!r}")
        self.used += 1
        readout = [self.universe.symbols[i]
                   for i in self.universe.true_trace(tag, word)]
        self.log.append(Interaction(self.used, tag, list(word), readout, source))
        return readout

    def try_run(self, tag: str, word: Sequence[str], source: str = "llm"):
        """Non-raising variant; returns (ok, readout_or_error)."""
        try:
            return True, self.run(tag, word, source)
        except (BudgetExhausted, ValueError) as exc:
            return False, str(exc)


class SealedSession:
    """Evaluation-time view. Any interaction attempt is a hard failure."""

    remaining = 0
    used = 0

    def run(self, *_a, **_kw):
        raise InteractionForbidden("interaction is forbidden during evaluation")

    try_run = run


# ---------------------------------------------------------------------------
#  Held-out evaluation set
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EvalQuery:
    qid: int
    tag: str
    word: Tuple[str, ...]


class EvalSet:
    """Fixed held-out query pool. Word lengths strictly exceed max_word_len,
    so no query can ever have been executed by any arm."""

    def __init__(self, universe: Universe, n_queries: int = 40,
                 len_lo: int = 8, len_hi: int = 12, salt: int = 77_777):
        assert len_lo > universe.spec.max_word_len
        rng = random.Random(universe.spec.seed * 7_919 + salt)
        self.universe = universe
        self.len_lo, self.len_hi = len_lo, len_hi
        self.queries: List[EvalQuery] = []
        for i in range(n_queries):
            tag = rng.choice(universe.tags)
            L = rng.randint(len_lo, len_hi)
            word = tuple(rng.choice(universe.actions) for _ in range(L))
            self.queries.append(EvalQuery(i, tag, word))
        self.answers: List[str] = [
            universe.true_final_symbol(q.tag, q.word) for q in self.queries
        ]

    def __len__(self) -> int:
        return len(self.queries)

    def score(self, predictions: Sequence[str]) -> Tuple[float, List[bool]]:
        n = len(self.queries)
        preds = list(predictions)[:n] + ["?"] * max(0, n - len(predictions))
        hits = [preds[i] == self.answers[i] for i in range(n)]
        return sum(hits) / n, hits

    def majority_baseline(self) -> Tuple[str, float]:
        counts: Dict[str, int] = {}
        for a in self.answers:
            counts[a] = counts.get(a, 0) + 1
        best = max(counts, key=lambda s: counts[s])
        return best, counts[best] / len(self.answers)
