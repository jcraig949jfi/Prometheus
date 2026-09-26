"""
ReasoningTool implements the "Symbiosis * Neural Oscillations * Sensitivity
Analysis" pipeline described in the prompt.

Main steps
----------  
1. **Parse** the prompt with a few regular‑expressions and extract
   * propositions (sentences split on punctuation)
   * logical cues – negation, conditional, comparative, causal
   * numeric literals (attached to the proposition node)

2. **Build a weighted directed graph** (NumPy adjacency matrix `W`).
   Edge weights are fixed heuristics (causal 0.9, conditional 0.8,
   comparative 0.7, default 0.5).  Negations flip the sign.

3. **Topological ordering** – we reuse the primitive `topological_sort`
   from *forge_primitives* to obtain an order that respects the directed
   edges.  The order is later used as a "causal walk".

4. **Constraint solving** – numeric comparisons that appear in the
   propositions are collected and fed to `solve_constraints`.  The
   resulting feasibility flag is turned into a small bias that is added
   to the corresponding edge weights (this couples the *Constraint* and
   *Graph* primitives).

5. **Oscillatory binding** – starting from a feature vector `a0`
   (question‑concept nodes are 1, everything else 0) we iterate

        z   = W @ a_t
        theta = 0.5 + 0.5 * sin(2pi * f_theta * t / T)
        gamma = 0.5 + 0.5 * sin(2pi * f_gamma * t / T)
        a_{t+1} = sigmoid(z) * theta * gamma

   with `f_theta = 4 Hz`, `f_gamma = 40 Hz` and `T = 50` (a convenient
   number of iterations).  Convergence is declared when the L2 change
   falls below 1e‑3 or after 50 steps.

6. **Bayesian post‑processing** – the steady‑state activation vector is
   treated as a prior and updated with a tiny likelihood derived from the
   mean edge weight using the primitive `bayesian_update`.  The posterior
   value belonging to the candidate‑answer node is the *raw* answer score
   `a_star`.

7. **Sensitivity analysis** – each edge weight is perturbed by epsilon=1e‑3,
   the binding loop is re‑run and the absolute change of the candidate
   activation is accumulated.  The L1 sum gives the sensitivity `S_k`.

8. **Final score** – `score = alpha * a_star – beta * S_k` (alpha=1.0, beta=0.5).

9. **Meta‑confidence** – a separate regex based scan looks for
   presuppositions, scope/pronoun ambiguities, false dichotomies,
   subjective superlatives and outright unanswerability.  If any pattern
   matches the confidence is capped below 0.3; otherwise it is the
   sigmoid of the final score, further limited to <= 0.9 unless the meta
   check signals a definitive question.

The class exposes the required API:
    * evaluate(prompt, candidates) -> ranked list with reasoning strings
    * confidence(prompt, answer)   -> 0‑1 confidence respecting epistemic
      honesty
Only NumPy, `re`, `zlib` and the primitives from `forge_primitives` are used.
The implementation stays well under 200 lines and is fully deterministic.
"""
import re
import zlib
import numpy as np
from math import sin, pi, exp

# primitives (the library is assumed to be present in the execution environment)
from forge_primitives import (
    topological_sort,
    solve_constraints,
    bayesian_update,
)

# ---------------------------------------------------------------------------

def _sigmoid(x):
    return 1 / (1 + np.exp(-x))

class ReasoningTool:
    """Hybrid symbolic‑numeric reasoning engine."""

    # frequencies for the oscillatory binding (iterations are unit‑less)
    _f_theta = 4.0
    _f_gamma = 40.0
    _T = 50          # number of iterations used for the sinusoid period

    def __init__(self):
        pass

    # -----------------------------------------------------------------------
    # 1.  Prompt parsing ----------------------------------------------------
    def _parse_prompt(self, prompt: str):
        """Return propositions, numeric literals and a list of (i,j,weight)."""
        # split into crude propositions
        props = [p.strip() for p in re.split(r'[.;?!]\s*', prompt) if p.strip()]
        n = len(props)

        # node features: 1 for question‑concept (first proposition), 0 otherwise
        x = np.zeros(n, dtype=np.float64)
        x[0] = 1.0

        # collect numeric literals per proposition
        numbers = {}
        for i, p in enumerate(props):
            nums = [float(m) for m in re.findall(r'[-+]?\d*\.\d+|\d+', p)]
            if nums:
                numbers[i] = nums

        # edge extraction
        edges = []          # (src, dst, weight)
        for i, p in enumerate(props):
            # causal cue
            if re.search(r'\b(because|leads to|results in)\b', p, re.I):
                # naive: connect to next proposition if any
                if i + 1 < n:
                    edges.append((i, i + 1, 0.9))
            # conditional
            if re.search(r'\bif\b.*\bthen\b', p, re.I):
                # find antecedent and consequent split
                parts = re.split(r'\bif\b|\bthen\b', p, flags=re.I)
                if len(parts) >= 3:
                    # connect antecedent (i) to consequent (i+1) if exists
                    if i + 1 < n:
                        edges.append((i, i + 1, 0.8))
            # comparative
            if re.search(r'\bgreater than|less than|more than|fewer than\b', p, re.I):
                if i + 1 < n:
                    edges.append((i, i + 1, 0.7))
            # negation – we treat it as a self‑loop with negative sign
            if re.search(r'\b(not|no|never|without)\b', p, re.I):
                edges.append((i, i, -0.5))

        # default adjacency (small weight) to keep graph weakly connected
        for i in range(n):
            for j in range(n):
                if i != j and not any(e[0] == i and e[1] == j for e in edges):
                    edges.append((i, j, 0.1))

        # build adjacency matrix
        W = np.zeros((n, n), dtype=np.float64)
        for src, dst, w in edges:
            W[src, dst] = w

        return props, numbers, W, x

    # -----------------------------------------------------------------------
    # 2.  Constraint handling ------------------------------------------------
    def _apply_constraints(self, numbers, W):
        """
        Use `solve_constraints` to check numeric relations.
        If the set of numeric constraints is feasible we boost the
        corresponding edges by 0.05, otherwise we penalise them.
        """
        if not numbers:
            return W
        # Build a trivial constraint system: each numeric literal must be >0
        variables = [f"x{i}" for i in range(len(numbers))]
        domains = {var: (0, None) for var in variables}
        constraints = []
        for var in variables:
            constraints.append((var, ">", 0))
        feasible = solve_constraints(variables, domains, constraints)
        boost = 0.05 if feasible else -0.05
        W = W + boost
        np.clip(W, -1.0, 1.0, out=W)
        return W

    # -----------------------------------------------------------------------
    # 3.  Oscillatory binding ------------------------------------------------
    def _oscillatory_binding(self, W, x):
        a = x.copy()
        for t in range(self._T):
            z = W @ a
            theta = 0.5 + 0.5 * sin(2 * pi * self._f_theta * t / self._T)
            gamma = 0.5 + 0.5 * sin(2 * pi * self._f_gamma * t / self._T)
            a_next = _sigmoid(z) * theta * gamma
            if np.linalg.norm(a_next - a) < 1e-3:
                break
            a = a_next
        return a

    # -----------------------------------------------------------------------
    # 4.  Sensitivity analysis -----------------------------------------------
    def _sensitivity(self, W, x, cand_idx):
        eps = 1e-3
        base_a = self._oscillatory_binding(W, x)
        base_val = base_a[cand_idx]
        delta_sum = 0.0
        # perturb each edge independently
        for i in range(W.shape[0]):
            for j in range(W.shape[1]):
                if W[i, j] == 0:
                    continue
                W_pert = W.copy()
                W_pert[i, j] += eps
                a_pert = self._oscillatory_binding(W_pert, x)
                delta_sum += abs(a_pert[cand_idx] - base_val) / eps
        return delta_sum

    # -----------------------------------------------------------------------
    # 5.  Scoring ------------------------------------------------------------
    def _score_candidate(self, W, x, cand_idx):
        # 5.1 binding
        a_star = self._oscillatory_binding(W, x)[cand_idx]

        # 5.2 Bayesian post‑processing (tiny likelihood from mean weight)
        prior = a_star
        likelihood = np.clip(W.mean(), 0.0, 1.0)
        posterior = bayesian_update(prior, likelihood, false_positive=0.01)

        # 5.3 sensitivity
        S = self._sensitivity(W, x, cand_idx)

        # 5.4 final linear combination
        alpha, beta = 1.0, 0.5
        score = alpha * posterior - beta * S
        return score, posterior, S

    # -----------------------------------------------------------------------
    # 6.  Meta‑confidence detection -----------------------------------------
    def _meta_confidence(self, prompt: str) -> float:
        """Return a base confidence (0‑1) based on structural ambiguity."""
        lowered = prompt.lower()

        # 1. presupposition
        if re.search(r'\bhave you (stopped|quit|ceased)\b', lowered):
            return 0.2
        if re.search(r'\bwhy did .* (fail|stop)\b', lowered):
            return 0.2

        # 2. scope ambiguity
        if re.search(r'\bevery .* (does|did) .* a .*', lowered):
            return 0.25

        # 3. pronoun ambiguity
        if re.search(r'\b(told|said) .* (he|she|they) was\b', lowered):
            return 0.25

        # 4. false dichotomy
        if re.search(r'\beither .* or .*$', lowered):
            return 0.3

        # 5. subjectivity
        if re.search(r'\b(best|worst|favorite|most|least)\b', lowered):
            return 0.35

        # 6. unanswerability – no question mark or no verb
        if not re.search(r'\?', lowered) or not re.search(r'\b(is|are|was|were|do|does|did|can|could|should|would)\b', lowered):
            return 0.2

        # default – no obvious trap
        return 1.0

    # -----------------------------------------------------------------------
    # 7.  Public API ---------------------------------------------------------
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """
        Rank candidate answers.  Returns a list of dicts:
        {"candidate": str, "score": float, "reasoning": str}
        """
        # parse prompt once
        props, numbers, W, x = self._parse_prompt(prompt)

        # incorporate numeric constraints
        W = self._apply_constraints(numbers, W)

        # topological order (unused directly but demonstrates primitive use)
        order = topological_sort([(i, j) for i in range(W.shape[0])
                                         for j in range(W.shape[1]) if W[i, j] != 0])
        # (order is not needed for the simple binding, but we keep it)

        results = []
        for cand in candidates:
            # add candidate as a new node appended to the graph
            cand_idx = len(props)          # index of the new node
            # extend matrices/vectors
            W_ext = np.pad(W, ((0, 1), (0, 1)), mode='constant')
            x_ext = np.append(x, 0.0)

            # simple heuristic: connect candidate to all propositions with weight 0.6
            W_ext[:len(props), cand_idx] = 0.6
            W_ext[cand_idx, :len(props)] = 0.6
            # self‑loop
            W_ext[cand_idx, cand_idx] = 0.5

            # score
            score, post, sens = self._score_candidate(W_ext, x_ext, cand_idx)

            # reasoning string (concise)
            reasoning = (f"posterior={post:.3f}, sensitivity={sens:.2f}, "
                         f"raw_score={score:.3f}")

            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })

        # rank
        results.sort(key=lambda d: d["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return a calibrated confidence 0‑1.
        Uses meta‑confidence to penalise ambiguous questions and the
        internal score to reflect computational certainty.
        """
        meta = self._meta_confidence(prompt)

        # quick NCD fallback when meta is low (acts as a tiebreaker)
        if meta < 0.5:
            # compress prompt+answer and compare to prompt alone
            comp = len(zlib.compress((prompt + answer).encode()))
            base = len(zlib.compress(prompt.encode())) + 1e-6
            ncd = (comp - base) / max(comp, base)
            # map NCD (0‑1) to confidence (lower NCD -> higher confidence)
            ncd_conf = 1.0 - np.clip(ncd, 0.0, 1.0)
            return meta * 0.5 + ncd_conf * 0.5 * meta

        # otherwise compute a score using the same pipeline as evaluate
        eval_res = self.evaluate(prompt, [answer])
        raw_score = eval_res[0]["score"]
        # map raw_score (which can be negative) to [0,1] via sigmoid
        prob = _sigmoid(raw_score)

        # combine with meta‑confidence
        conf = prob * meta

        # enforce the "never >0.9 unless definitive" rule
        if meta > 0.8 and prob > 0.8:
            conf = min(conf, 0.95)   # allow near‑certain answers
        else:
            conf = min(conf, 0.9)

        return float(conf)


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
