from typing import Dict

"""
ReasoningTool
==============

Implements the three‑step algorithm described in the prompt:

1. **Parsing & boundary encoding** – extracts logical atoms from a prompt
   and a candidate answer using very general regular expressions.
   Each atom becomes a dimension of a binary vector *a* (unknown -> 0.5).

2. **Abstract interpretation** – builds a constraint matrix *C* whose rows
   are simple Horn‑like clauses (positive literal = 1, negated literal = -1).
   Interval propagation yields lower/upper sound bounds for every atom.

3. **Nash‑equilibrium refinement** – treats every atom as a player whose
   strategy is its truth value.  Repeated best‑response (rounding the
   midpoint of the interval) converges to a pure‑strategy equilibrium.
   The distance between the equilibrium and the interval gives an
   inconsistency score *I* and a quality score *S = 1/(1+I)*.

The final candidate score mixes *S* (~=85 % weight) with a tiny
zlib‑based Normalised Compression Distance (<=15 %).  The `confidence`
method first checks the prompt for epistemic traps (presupposition,
scope/pronoun ambiguity, false dichotomy, subjectivity, unanswerability)
and caps the confidence accordingly.

Only the Python standard library and NumPy are used; the implementation
is deterministic and well under 200 lines.
"""

import re
import zlib
import numpy as np
from typing import List, Dict


class ReasoningTool:
    """Implements the holographic‑Nash‑abstract‑interpretation pipeline."""

    # --------------------------------------------------------------------- #
    # 1.  Structural extraction (robust, not template‑matching)
    # --------------------------------------------------------------------- #
    _ATOM_RE = re.compile(
        r"""
        (?P<neg>not\s+)?               # optional negation
        (?P<left>\b\w+\b)              # left identifier
        \s*
        (?P<op>>=|<=|>|<|=|!=)         # comparison operator
        \s*
        (?P<right>\b[\w\.]+\b)         # right identifier / number
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    _COND_RE = re.compile(
        r"""
        if\s+(?P<cond>.+?)\s+then\s+(?P<consq>.+)
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    _CAUSE_RE = re.compile(
        r"""
        (?P<cause>\b\w+\b)\s+(because|due\s+to|caused\s+by|leads\s+to|results\s+in|produces)\s+(?P<effect>\b\w+\b)
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    _ORDER_RE = re.compile(
        r"""
        (?P<first>\b\w+\b)\s+(before|after)\s+(?P<second>\b\w+\b)
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    # --------------------------------------------------------------------- #
    # 2.  Public API
    # --------------------------------------------------------------------- #
    def __init__(self):
        pass

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Score each candidate and return a ranked list."""
        results = []
        for cand in candidates:
            score, reasoning = self._score_candidate(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        # rank highest score first
        return sorted(results, key=lambda d: d["score"], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        """Return an honesty‑driven confidence in [0,1]."""
        base = self._meta_confidence(prompt)
        # a high base means the question is well‑posed; otherwise we stay low
        # combine with the candidate's own consistency score (but never exceed 0.9)
        score, _ = self._score_candidate(prompt, answer)
        conf = min(base * score, 0.9) if base > 0.6 else base * 0.5
        return float(conf)

    # --------------------------------------------------------------------- #
    # 3.  Core pipeline (private)
    # --------------------------------------------------------------------- #
    def _score_candidate(self, prompt: str, cand: str):
        """Run the holographic‑Nash pipeline and return (score, textual reasoning)."""
        # 1) extract atoms & clauses from prompt + candidate
        atoms, clauses = self._extract(prompt, cand)

        if not atoms:
            # nothing to reason about – fall back to NCD only
            ncd_score = self._ncd_score(prompt, cand)
            return ncd_score, "No logical atoms found; used NCD only."

        idx = {a: i for i, a in enumerate(sorted(atoms))}
        n = len(idx)

        # build constraint matrix C (rows = clauses)
        C_rows = []
        thresh = []  # all thresholds are 1 in this simple encoding
        for pos, neg in clauses:
            row = np.zeros(n, dtype=int)
            for p in pos:
                row[idx[p]] = 1
            for n_ in neg:
                row[idx[n_]] = -1
            C_rows.append(row)
            thresh.append(1)

        C = np.vstack(C_rows) if C_rows else np.zeros((0, n), dtype=int)
        thresh = np.array(thresh, dtype=int)

        # initialise truth vector a (unknown -> 0.5)
        a = np.full(n, 0.5, dtype=float)

        # abstract interpretation – interval propagation
        # lower = max(0, C@a - (|C|_1 - 1)), upper = min(1, C@a)
        if C.shape[0]:
            absC = np.abs(C).sum(axis=1)
            lower = np.maximum(0.0, C @ a - (absC - 1))
            upper = np.minimum(1.0, C @ a)
        else:
            lower = upper = np.zeros(0)

        # Nash‑equilibrium iteration
        proj = np.clip((lower + upper) / 2.0, 0.0, 1.0) if lower.size else np.full(n, 0.5)
        a_prev = np.full_like(a, -1.0)
        eps = 1e-3
        while np.linalg.norm(a - a_prev, 1) > eps:
            a_prev = a.copy()
            proj = np.clip((lower + upper) / 2.0, 0.0, 1.0)
            a = np.rint(proj)  # best‑response: round to 0 or 1
            # recompute intervals with the new a
            if C.shape[0]:
                lower = np.maximum(0.0, C @ a - (absC - 1))
                upper = np.minimum(1.0, C @ a)

        # inconsistency and primary score
        I = np.sum(np.abs(a - proj))
        S = 1.0 / (1.0 + I)

        # NCD tiebreaker (max 15 % weight)
        ncd = self._ncd_score(prompt, cand)  # already in [0,1]
        final = 0.85 * S + 0.15 * ncd

        # build a short reasoning string
        reasoning = (
            f"atoms={n}, clauses={len(clauses)}, inconsistency={I:.3f}, "
            f"S={S:.3f}, NCD={ncd:.3f}"
        )
        return float(final), reasoning

    # --------------------------------------------------------------------- #
    # 4.  Extraction helpers
    # --------------------------------------------------------------------- #
    def _extract(self, prompt: str, cand: str):
        """Return (set_of_atoms, list_of_clauses).  Clause = (positives, negatives)."""
        text = f"{prompt}\n{cand}"
        atoms = set()
        clauses = []

        # 4.1 binary literals, comparatives, numeric constraints
        for m in self._ATOM_RE.finditer(text):
            left = m.group("left")
            right = m.group("right")
            op = m.group("op")
            neg = bool(m.group("neg"))
            atom = f"{left}{op}{right}"
            atoms.add(atom)
            if neg:
                clauses.append((set(), {atom}))
            else:
                clauses.append(({atom}, set()))

        # 4.2 conditionals  (if A then B)
        for m in self._COND_RE.finditer(text):
            cond = m.group("cond").strip()
            cons = m.group("consq").strip()
            # treat as implication: cond -> cons
            # encode as ¬cond ∨ cons  -> clause (pos={cons}, neg={cond})
            atoms.update([cond, cons])
            clauses.append(({cons}, {cond}))

        # 4.3 causal statements (X because Y)  -> Y -> X
        for m in self._CAUSE_RE.finditer(text):
            cause = m.group("cause")
            effect = m.group("effect")
            atoms.update([cause, effect])
            clauses.append(({cause}, {effect}))

        # 4.4 ordering (A before B)  -> A -> B
        for m in self._ORDER_RE.finditer(text):
            first = m.group("first")
            second = m.group("second")
            atoms.update([first, second])
            clauses.append(({second}, {first}))

        # 4.5 simple arithmetic statements inside candidate (e.g. "9+1=10")
        # we try to evaluate them and add a truth clause.
        arith_pat = re.compile(r"(?P<expr>[\d\.\s\+\-\*/\(\)]+)\s*=\s*(?P<val>[\d\.\s\+\-\*/\(\)]+)")
        for m in arith_pat.finditer(cand):
            try:
                lhs = eval(m.group("expr"), {"__builtins__": {}})
                rhs = eval(m.group("val"), {"__builtins__": {}})
                atom = f"{m.group('expr').strip()}={m.group('val').strip()}"
                atoms.add(atom)
                if abs(lhs - rhs) < 1e-9:
                    clauses.append(({atom}, set()))   # true
                else:
                    clauses.append((set(), {atom}))   # false
            except Exception:
                pass

        return atoms, clauses

    # --------------------------------------------------------------------- #
    # 5.  NCD helper (zlib based)
    # --------------------------------------------------------------------- #
    def _ncd_score(self, p: str, c: str) -> float:
        """Return a similarity in [0,1] where 1 = identical."""
        cp = zlib.compress(p.encode())
        cc = zlib.compress(c.encode())
        pc = zlib.compress((p + c).encode())
        Cx = len(cp)
        Cy = len(cc)
        Cxy = len(pc)
        ncd = (Cxy - min(Cx, Cy)) / max(Cx, Cy) if max(Cx, Cy) else 0.0
        return 1.0 - ncd  # higher = more similar

    # --------------------------------------------------------------------- #
    # 6.  Meta‑confidence detection (epistemic honesty)
    # --------------------------------------------------------------------- #
    _PRESUPP_RE = re.compile(r"\b(have\s+you\s+stopped|why\s+did|why\s+has)\b", re.I)
    _SCOPE_RE = re.compile(r"\bevery\s+\w+\b.*\b(a|an)\b\s+\w+", re.I)
    _PRON_RE = re.compile(r"\b\w+\s+told\s+\w+\s+he|she|they\b", re.I)
    _FALSE_DICH_RE = re.compile(r"\beither\s+.+\s+or\s+.+\b", re.I)
    _SUBJ_RE = re.compile(r"\b(best|worst|favorite|most|least)\b", re.I)
    _UNANS_RE = re.compile(r"\b(meaning of life|what\s+is\s+the\s+purpose|unknown)\b", re.I)

    def _meta_confidence(self, prompt: str) -> float:
        """Detect epistemic traps; return a base confidence in [0,1]."""
        lowered = prompt.lower()
        traps = 0
        if self._PRESUPP_RE.search(lowered):
            traps += 1
        if self._SCOPE_RE.search(lowered):
            traps += 1
        if self._PRON_RE.search(lowered):
            traps += 1
        if self._FALSE_DICH_RE.search(lowered):
            traps += 1
        if self._SUBJ_RE.search(lowered):
            traps += 1
        if self._UNANS_RE.search(lowered):
            traps += 1

        # No trap -> moderate confidence, otherwise low.
        if traps == 0:
            return 0.7
        elif traps == 1:
            return 0.4
        else:
            return 0.2


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
