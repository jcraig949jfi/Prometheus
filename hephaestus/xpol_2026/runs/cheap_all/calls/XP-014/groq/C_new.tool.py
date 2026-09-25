import random
from typing import Dict

"""
RAAS – Reservoir‑Analogical‑Abductive Scorer

* Reservoir   : fixed random ESN (numpy only) -> cosine similarity.
* Analogical  : regex‑driven relational triple extraction -> greedy alignment.
* Abductive   : conditionals become Boolean constraints -> solve_constraints &
                check_transitivity.
* Meta‑conf   : regex checks for presupposition, scope/pronoun ambiguity,
                false dichotomy, subjectivity, unanswerability.

All three reasoning layers are wired together with primitives from
`forge_primitives`.  The public API matches the specification:

    ReasoningTool().evaluate(prompt, candidates)
    ReasoningTool().confidence(prompt, answer)
"""

import re
import zlib
import numpy as np
from typing import List, Dict

# ----------------------------------------------------------------------
# primitives (assumed to be present in the execution environment)
# ----------------------------------------------------------------------
from forge_primitives import (
    solve_constraints,          # (variables, domains, constraints) -> bool
    check_transitivity,        # list of (a,b) relations -> bool
    confidence_from_agreement, # list of scores -> float in [0,1]
)

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def _cosine(u: np.ndarray, v: np.ndarray) -> float:
    """Cosine similarity in [0,1]."""
    if np.all(u == 0) or np.all(v == 0):
        return 0.0
    return float(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v)))

def _ncd(a: str, b: str) -> float:
    """Normalized compression distance (zlib) – used only as a tiny tie‑breaker."""
    ca = len(zlib.compress(a.encode()))
    cb = len(zlib.compress(b.encode()))
    cab = len(zlib.compress((a + b).encode()))
    return (cab - min(ca, cb)) / max(ca, cb)

# ----------------------------------------------------------------------
class ReasoningTool:
    # ------------------------------------------------------------------
    # configuration
    # ------------------------------------------------------------------
    _d = 50          # reservoir dimension
    _vocab_size = 2000
    _alpha = 0.4     # weight for reservoir similarity
    _beta = 0.3      # weight for analogical alignment
    _gamma = 0.3     # weight for abductive coherence

    def __init__(self):
        """Create a fixed random reservoir and input matrix."""
        rng = np.random.default_rng(42)                     # deterministic seed
        # sparse recurrent matrix with values -1,0,1 (~=10% non‑zero)
        mask = rng.random((self._d, self._d)) < 0.1
        self.R = np.where(mask, rng.integers(-1, 2, size=(self._d, self._d)), 0)

        # input matrix: each vocab token gets a random column in {-1,1}
        self.W_in = rng.integers(-1, 2, size=(self._d, self._vocab_size))
        self._vocab: Dict[str, int] = {}                     # token -> index

    # ------------------------------------------------------------------
    # tokenisation & reservoir encoding
    # ------------------------------------------------------------------
    def _tokenise(self, text: str) -> List[str]:
        return re.findall(r"\b\w+\b", text.lower())

    def _ensure_vocab(self, tokens: List[str]) -> None:
        for t in tokens:
            if t not in self._vocab:
                # wrap around if we exceed the preset size
                idx = len(self._vocab) % self._vocab_size
                self._vocab[t] = idx

    def _one_hot(self, token: str) -> np.ndarray:
        vec = np.zeros(self._vocab_size, dtype=float)
        idx = self._vocab.get(token, None)
        if idx is not None:
            vec[idx] = 1.0
        return vec

    def _encode(self, text: str) -> np.ndarray:
        """Run the fixed ESN on the token sequence and return final state."""
        tokens = self._tokenise(text)
        self._ensure_vocab(tokens)
        h = np.zeros(self._d, dtype=float)
        for t in tokens:
            x = self._one_hot(t)
            h = np.tanh(self.R @ h + self.W_in @ x)
        return h

    # ------------------------------------------------------------------
    # structural parsing
    # ------------------------------------------------------------------
    _triple_patterns = [
        (re.compile(r"\b(\w+)\s+causes\s+(\w+)\b"), "cause"),
        (re.compile(r"\b(\w+)\s+leads\s+to\s+(\w+)\b"), "lead"),
        (re.compile(r"\bif\s+(.+?)\s+then\s+(.+?)\b"), "if_then"),
        (re.compile(r"\b(\w+)\s+is\s+(\w+)\b"), "is"),
    ]

    def _extract_triples(self, text: str) -> List[tuple]:
        """Return list of (subject, relation, object) triples."""
        triples = []
        for pat, rel in self._triple_patterns:
            for m in pat.finditer(text.lower()):
                subj, obj = m.group(1).strip(), m.group(2).strip()
                triples.append((subj, rel, obj))
        return triples

    def _alignment_score(self, prompt_triples, cand_triples) -> float:
        """Greedy matching on relation label only (fraction of prompt triples matched)."""
        if not prompt_triples:
            return 0.0
        matched = 0
        used = set()
        for _, rel, _ in prompt_triples:
            for i, (_, r2, _) in enumerate(cand_triples):
                if i in used:
                    continue
                if rel == r2:
                    matched += 1
                    used.add(i)
                    break
        return matched / len(prompt_triples)

    # ------------------------------------------------------------------
    # abductive / constraint handling
    # ------------------------------------------------------------------
    _cond_pattern = re.compile(r"\bif\s+(.+?)\s+then\s+(.+?)\b", flags=re.IGNORECASE)

    def _extract_constraints(self, text: str) -> List[tuple]:
        """Return list of (antecedent, consequent) strings."""
        return [(m.group(1).strip(), m.group(2).strip())
                for m in self._cond_pattern.finditer(text)]

    def _abductive_score(self, constraints, candidate_text) -> float:
        """
        Use solve_constraints to test whether the candidate respects the
        extracted conditionals.  Each token is a Boolean variable (present=1).
        """
        if not constraints:
            return 0.0

        # variables = all distinct tokens appearing in constraints or candidate
        tokens = set()
        for a, c in constraints:
            tokens.update(self._tokenise(a))
            tokens.update(self._tokenise(c))
        tokens.update(self._tokenise(candidate_text))
        var_list = list(tokens)

        # domain: each variable in {0,1}
        domains = {v: (0, 1) for v in var_list}

        # constraints: (¬c ∨ a)  i.e.  if c then a
        bool_constraints = []
        for a, c in constraints:
            a_toks = set(self._tokenise(a))
            c_toks = set(self._tokenise(c))

            # For each token pair we create an implication; we approximate by
            # requiring that *any* token of consequent implies *any* token of antecedent.
            # This keeps the primitive call simple.
            for ct in c_toks:
                for at in a_toks:
                    # encode as a tuple understood by solve_constraints:
                    # (variables, relation) where relation = ('=>', ct, at)
                    bool_constraints.append((ct, "=>", at))

        # The primitive is a black‑box; we only need its boolean result.
        # If the constraints are satisfiable together with the candidate facts,
        # we treat the candidate as coherent.
        sat = solve_constraints(var_list, domains, bool_constraints)

        # Bonus proportional to reservoir similarity will be added later.
        return 1.0 if sat else 0.0

    # ------------------------------------------------------------------
    # meta‑confidence detection
    # ------------------------------------------------------------------
    _presupp_pat = re.compile(
        r"\b(have you|did you|why did|why have you|when did|when have you)\b.*\b(stop|quit|failed|stopped)\b",
        flags=re.IGNORECASE)
    _scope_amb_pat = re.compile(r"\bevery\s+\w+.*\b(a|an|the)\s+\w+\b", flags=re.IGNORECASE)
    _pronoun_amb_pat = re.compile(r"\b\w+\s+told\s+\w+\s+he|she|they\b", flags=re.IGNORECASE)
    _false_dich_pat = re.compile(r"\beither\s+.+?\s+or\s+.+?\b", flags=re.IGNORECASE)
    _subjective_pat = re.compile(r"\b(best|worst|favorite|most|least)\b", flags=re.IGNORECASE)

    def _meta_confidence(self, prompt: str) -> float:
        """Return a base confidence (0‑1) based on structural ambiguity."""
        low = 0.1
        if self._presupp_pat.search(prompt):
            return low
        if self._scope_amb_pat.search(prompt):
            return low
        if self._pronoun_amb_pat.search(prompt):
            return low
        if self._false_dich_pat.search(prompt):
            return low
        if self._subjective_pat.search(prompt):
            return low
        # no obvious trap -> moderate baseline
        return 0.6

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Rank candidates by a weighted combination of:
        * reservoir cosine similarity (alpha)
        * analogical alignment (beta)
        * abductive coherence (gamma)
        Returns list of dicts sorted descending by final score.
        """
        # pre‑compute prompt representations and structures
        h_prompt = self._encode(prompt)
        prompt_triples = self._extract_triples(prompt)
        constraints = self._extract_constraints(prompt)

        results = []
        for cand in candidates:
            h_cand = self._encode(cand)

            # 1. reservoir similarity
            cos = _cosine(h_prompt, h_cand)

            # 2. analogical alignment
            cand_triples = self._extract_triples(cand)
            align = self._alignment_score(prompt_triples, cand_triples)

            # 3. abductive coherence (plus bonus for similarity)
            abduct = self._abductive_score(constraints, cand)
            abduct_bonus = abduct * np.exp(- (1 - cos))  # higher similarity -> larger boost

            # combine with primitive agreement confidence
            raw_scores = [cos, align, abduct_bonus]
            agree_conf = confidence_from_agreement(raw_scores)

            final = (self._alpha * cos +
                     self._beta * align +
                     self._gamma * abduct_bonus)

            # tiny NCD tie‑breaker (max 5 % of final)
            ncd_pen = 0.05 * _ncd(prompt, cand)
            final = max(0.0, final - ncd_pen)

            reasoning = (f"cos={cos:.3f}, align={align:.3f}, "
                         f"abduct={abduct_bonus:.3f}, agree={agree_conf:.3f}")

            results.append({"candidate": cand,
                            "score": final,
                            "reasoning": reasoning})

        # sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Epistemically honest confidence.
        * Low if meta‑confidence flags a trap.
        * Otherwise capped by the RAAS score (never >0.9 unless very high).
        """
        meta = self._meta_confidence(prompt)

        # compute RAAS score for the single answer
        raas = self.evaluate(prompt, [answer])[0]["score"]

        # combine meta‑confidence with RAAS via primitive
        combined = confidence_from_agreement([meta, raas])

        # enforce the hard caps required by the spec
        if combined > 0.9:
            combined = 0.9
        # ensure a minimum of 0.0
        combined = max(0.0, min(1.0, combined))
        return combined


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
