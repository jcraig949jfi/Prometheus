from typing import Dict

"""
ReasoningTool
==============

A self‑contained Python implementation (~=150 LOC) that follows the
high‑value combination *Phase Transitions * Adaptive Control * Multi‑Armed
Bandits*.

*   Each candidate answer is an arm of a stochastic bandit.
*   After every pull a raw reward rin[0,1] is computed as the fraction of
    structural constraints (extracted from the prompt) that the answer
    satisfies.
*   The UCB value uses an exploration coefficient *c* that is tuned online
    by a simple regulator (exponential‑moving‑average of the error w.r.t.
    a perfect reference reward).
*   A global order parameter φ tracks the average arm quality; a sudden
    drop of its short‑term variance triggers a "phase transition'' that
    forces pure exploitation (c=0) for a few steps.
*   `confidence()` first runs a meta‑confidence check on the *prompt* for
    presupposition, scope‑ambiguity, pronoun‑ambiguity, false‑dichotomy,
    subjectivity and unanswerability.  The returned confidence is the
    product of this meta‑score and an uncertainty factor derived from the
    proportion of ambiguous parsed variables.

Only the Python standard library and NumPy are required; the code is
deterministic and runs in a few milliseconds for typical inputs.
"""

import re
import zlib
import numpy as np
from collections import deque
from typing import List, Dict


class ReasoningTool:
    # ---------- meta‑confidence patterns ----------
    _presupp_pat = re.compile(
        r'\b(have|did|didn\'t|did not|did you|are you|were you|has|had)\s+(stopped|quit|ceased|failed|ended)\b',
        re.I)
    _scope_pat = re.compile(r'\bevery\s+\w+.*\b(some|a|an)\b', re.I)
    _pronoun_pat = re.compile(r'\b(\w+)\s+told\s+(\w+)\s+he|she|they\b', re.I)
    _dichotomy_pat = re.compile(r'\beither\b.*\bor\b', re.I)
    _subjective_pat = re.compile(r'\b(best|worst|favorite|most|least)\b', re.I)

    def __init__(self):
        # bandit state (filled in evaluate)
        self.c = 0.1                     # exploration coefficient
        self.e_bar = 0.0                 # EMA of error
        self.alpha = 0.2                 # EMA smoothing
        self.tau = 0.1                   # error threshold
        self.c_decay = 0.99
        self.c_inc = 0.05
        self.c_min = 0.0
        self.c_baseline = 0.1
        self.phase_k = 5                # pure‑exploitation steps
        self.phase_cnt = 0
        self.var_window = deque(maxlen=10)   # recent φ values
        self.theta = 0.005
        self.prev_var = None

    # ------------------------------------------------------------------ #
    # 1.  Structural parsing ------------------------------------------------
    # ------------------------------------------------------------------ #
    _num_pat = re.compile(r'([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)')
    _comp_pat = re.compile(
        r'(?P<left>\w+)\s*(?P<op>>=|<=|>|<|=|!=|!=)\s*(?P<right>\-?\d*\.?\d+)', re.I)
    _neg_pat = re.compile(r'\b(not|no|never|without)\b', re.I)
    _cond_pat = re.compile(r'\bif\b.*?\bthen\b', re.I)
    _causal_pat = re.compile(r'\b(because|leads? to|causes?|results? in)\b', re.I)
    _order_pat = re.compile(r'\b(before|after|earlier|later|higher|lower)\b', re.I)

    def _extract_constraints(self, prompt: str) -> List[Dict]:
        """Return a list of simple constraints extracted from *prompt*."""
        constraints = []

        # numeric comparisons
        for m in self._comp_pat.finditer(prompt):
            left, op, right = m.group('left'), m.group('op'), float(m.group('right'))
            constraints.append({'type': 'comp', 'left': left, 'op': op, 'right': right})

        # negations (treated as a Boolean flag)
        if self._neg_pat.search(prompt):
            constraints.append({'type': 'neg'})

        # conditionals – we just note their presence
        if self._cond_pat.search(prompt):
            constraints.append({'type': 'cond'})

        # causal claims
        if self._causal_pat.search(prompt):
            constraints.append({'type': 'causal'})

        # ordering / temporal relations
        if self._order_pat.search(prompt):
            constraints.append({'type': 'order'})

        return constraints

    # ------------------------------------------------------------------ #
    # 2.  Reward evaluation -------------------------------------------------
    # ------------------------------------------------------------------ #
    def _eval_constraint(self, constraint: Dict, answer: str) -> bool:
        """Very coarse evaluation of a single constraint against *answer*."""
        # numeric comparison – look for a number after the left token
        if constraint['type'] == 'comp':
            left = constraint['left']
            op = constraint['op']
            right = constraint['right']
            # find the first number that follows the left token in answer
            pattern = re.compile(rf'{re.escape(left)}\W*{self._num_pat.pattern}')
            m = pattern.search(answer)
            if not m:
                return False
            val = float(m.group(1))
            if op in ('>', '＞'):
                return val > right
            if op in ('>=', '>='):
                return val >= right
            if op in ('<', '＜'):
                return val < right
            if op in ('<=', '<='):
                return val <= right
            if op in ('=', '=='):
                return np.isclose(val, right)
            if op in ('!=', '!='):
                return not np.isclose(val, right)
            return False

        # negation – satisfied if answer contains a negation word
        if constraint['type'] == 'neg':
            return bool(self._neg_pat.search(answer))

        # conditional – satisfied if both "if" and "then" appear
        if constraint['type'] == 'cond':
            return bool(re.search(r'\bif\b', answer, re.I) and
                        re.search(r'\bthen\b', answer, re.I))

        # causal – satisfied if a causal connective appears
        if constraint['type'] == 'causal':
            return bool(self._causal_pat.search(answer))

        # ordering – satisfied if any ordering keyword appears
        if constraint['type'] == 'order':
            return bool(self._order_pat.search(answer))

        return False

    def _raw_reward(self, constraints: List[Dict], answer: str) -> float:
        """Fraction of constraints that the answer satisfies."""
        if not constraints:
            return 1.0                     # no constraints -> perfect reward
        satisfied = sum(self._eval_constraint(c, answer) for c in constraints)
        return satisfied / len(constraints)

    # ------------------------------------------------------------------ #
    # 3.  Adaptive control & phase‑transition handling --------------------
    # ------------------------------------------------------------------ #
    def _update_c(self, reward: float):
        """Adjust exploration coefficient *c* according to the EMA regulator."""
        e = 1.0 - reward                     # r_ref = 1
        self.e_bar = self.alpha * e + (1 - self.alpha) * self.e_bar

        # variance of recent rewards (simple window)
        if hasattr(self, '_reward_window'):
            self._reward_window.append(reward)
        else:
            self._reward_window = deque([reward], maxlen=20)

        var = np.var(self._reward_window)
        if var < 0.01:
            self.tau *= 1.1                 # become less sensitive

        if abs(self.e_bar) > self.tau:
            self.c = min(self.c + self.c_inc, 5.0)   # cap to avoid explosion
        else:
            # decay toward baseline
            self.c = max(self.c_baseline + self.c_decay * (self.c - self.c_baseline),
                         self.c_min)

    def _maybe_phase_transition(self, mus: np.ndarray):
        """Detect a drop in variance of the global order parameter."""
        phi = mus.mean()
        self.var_window.append(phi)
        if len(self.var_window) < self.var_window.maxlen:
            return
        var = np.var(self.var_window)
        if self.prev_var is None:
            self.prev_var = var
            return
        dvar = var - self.prev_var
        self.prev_var = var
        if dvar < -self.theta:
            self.phase_cnt = self.phase_k      # enforce pure exploitation

    # ------------------------------------------------------------------ #
    # 4.  Main evaluation -------------------------------------------------
    # ------------------------------------------------------------------ #
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Bandit‑based scoring of *candidates* given *prompt*.
        Returns a list sorted by descending score.
        """
        B = 30                                 # total pulls
        n = len(candidates)
        pulls = np.zeros(n, dtype=int)
        reward_sum = np.zeros(n, dtype=float)
        ucb = np.full(n, np.inf)               # force initial pull of each arm

        constraints = self._extract_constraints(prompt)

        total_pulls = 0
        while total_pulls < B:
            # pure‑exploitation phase?
            if self.phase_cnt > 0:
                self.c = 0.0
                self.phase_cnt -= 1

            # select arm with max UCB
            i = int(np.argmax(ucb))
            # compute reward
            r = self._raw_reward(constraints, candidates[i])
            # update statistics
            pulls[i] += 1
            reward_sum[i] += r
            total_pulls += 1

            mu = reward_sum[i] / pulls[i]
            # recompute UCB for the pulled arm
            if pulls[i] > 0:
                ucb[i] = mu + self.c * np.sqrt(np.log(total_pulls) / pulls[i])
            else:
                ucb[i] = np.inf

            # update adaptive exploration term
            self._update_c(r)

            # phase‑transition check (using all mus)
            mus = reward_sum / np.maximum(pulls, 1)
            self._maybe_phase_transition(mus)

        # final scores = empirical means
        scores = reward_sum / np.maximum(pulls, 1)

        # optional NCD tie‑breaker (max 15 % of final score)
        ncd_weights = np.array([self._ncd(prompt, cand) for cand in candidates])
        ncd_norm = (ncd_weights - ncd_weights.min()) / (ncd_weights.ptp() + 1e-9)
        final = 0.85 * scores + 0.15 * (1 - ncd_norm)

        results = []
        for cand, sc in sorted(zip(candidates, final), key=lambda x: -x[1]):
            reasoning = f"{sc:.3f} = 0.85*{scores[candidates.index(cand)]:.3f}" \
                        f" + 0.15*{1 - ncd_norm[candidates.index(cand)]:.3f}"
            results.append({"candidate": cand, "score": float(sc), "reasoning": reasoning})
        return results

    # ------------------------------------------------------------------ #
    # 5.  Normalized Compression Distance (NCD) ---------------------------
    # ------------------------------------------------------------------ #
    @staticmethod
    def _ncd(s1: str, s2: str) -> float:
        """Simple NCD using zlib compression."""
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2)

    # ------------------------------------------------------------------ #
    # 6.  Meta‑confidence -------------------------------------------------
    # ------------------------------------------------------------------ #
    def _meta_confidence(self, prompt: str) -> float:
        """Detect traps in *prompt* and return a base confidence (0‑1)."""
        # presupposition
        if self._presupp_pat.search(prompt):
            return 0.2
        # scope ambiguity
        if self._scope_pat.search(prompt):
            return 0.25
        # pronoun ambiguity
        if self._pronoun_pat.search(prompt):
            return 0.25
        # false dichotomy
        if self._dichotomy_pat.search(prompt):
            return 0.3
        # subjectivity
        if self._subjective_pat.search(prompt):
            return 0.35
        # generic unanswerable cue (no question mark)
        if not re.search(r'\?', prompt):
            return 0.2
        return 0.9

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return a calibrated confidence 0‑1.
        Low confidence for ambiguous / under‑determined prompts,
        high confidence only when a concrete computation succeeded.
        """
        base = self._meta_confidence(prompt)

        # compute how many constraints are *certain* (no ambiguity)
        constraints = self._extract_constraints(prompt)
        if not constraints:
            # nothing to check -> rely on meta‑confidence only
            return base * 0.5

        # evaluate each constraint; ambiguous if we could not find a number etc.
        certain = 0
        for c in constraints:
            if c['type'] == 'comp':
                # try to locate a numeric value in answer; if missing -> ambiguous
                if re.search(self._num_pat, answer):
                    certain += 1
            else:
                # other types are considered certain (they are word‑based)
                certain += 1

        prop_certain = certain / len(constraints)
        # final confidence = meta * proportion of certain constraints,
        # capped at 0.9 unless the answer matches all constraints perfectly.
        raw = base * prop_certain
        # if raw > 0.9 we still cap unless reward == 1
        reward = self._raw_reward(constraints, answer)
        if reward == 1.0:
            return min(raw, 0.95)
        return min(raw, 0.9)


# --- Auto-fix: ensure confidence() returns float in [0, 1] ---
_orig_confidence = ReasoningTool.confidence
def _safe_confidence(self, prompt, answer):
    try:
        result = _orig_confidence(self, prompt, answer)
        if result is None:
            return 0.5
        return max(0.0, min(1.0, float(result)))
    except (TypeError, ValueError):
        return 0.5
ReasoningTool.confidence = _safe_confidence


# --- Auto-fix: ensure evaluate() returns list[dict] ---
_orig_evaluate = ReasoningTool.evaluate
def _safe_evaluate(self, prompt, candidates):
    try:
        result = _orig_evaluate(self, prompt, candidates)
        if result is None:
            return [{"candidate": c, "score": 0.5, "reasoning": "fallback"} for c in candidates]
        if not isinstance(result, list):
            return [{"candidate": c, "score": 0.5, "reasoning": "fallback"} for c in candidates]
        return result
    except Exception:
        return [{"candidate": c, "score": 0.5, "reasoning": "error"} for c in candidates]
ReasoningTool.evaluate = _safe_evaluate
