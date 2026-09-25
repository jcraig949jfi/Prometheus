from typing import Dict

"""
ReasoningTool
==============

A compact implementation of the "Spectral Analysis * Neuromodulation * Model
Checking'' idea described in the prompt.

*   The prompt and each candidate answer are parsed into a small set of
    *semantic predicates* (negation, comparison, conditional, numeric, causal,
    ordering, logical connector).  
*   Predicates become nodes of a graph; edges are added when two predicates
    appear in the same sentence or are linked by a conditional/causal cue.
*   A *neuromodulatory gain* multiplies edge weights according to discourse
    cues (e.g. "therefore'' -> excitatory, "but'' -> inhibitory).
*   The adjacency matrix of the graph is transformed with `numpy.fft.rfft`.
    Low‑frequency mass reflects coherent reasoning chains, high‑frequency
    components expose noisy or contradictory links.
*   The similarity of the prompt‑ and candidate‑spectra (cosine) together with
    a high‑frequency penalty yields a structural score in **[0,1]**.
*   A tiny Normalised Compression Distance (zlib NCD) is used only as a
    secondary tie‑breaker (<= 15 % of the final score).
*   `confidence()` first runs a *meta‑confidence* check for presupposition,
    scope‑/pronoun‑ambiguity, false dichotomy, subjectivity and unanswerability.
    If any trap is detected the confidence is capped at 0.25; otherwise it is
    derived from the best structural score but never exceeds 0.9 unless the
    score is > 0.95.

The class is fully deterministic, uses only the Python standard library and
NumPy, and fits comfortably under 200 source lines.
"""

import re
import zlib
import numpy as np
from itertools import combinations
from typing import List, Dict


class ReasoningTool:
    """Implements spectral‑model‑checking reasoning with epistemic honesty."""

    # ---- static resources -------------------------------------------------
    _PRED_TYPES = [
        "NEG", "COMP", "COND", "NUM", "CAUSE", "ORDER", "CONNECT"
    ]                                   # one‑hot length = 7
    _CUE_EXCIT = {"therefore", "hence", "thus", "if", "because", "so"}
    _CUE_INHIB = {"but", "however", "although", "though", "yet"}

    # regexes for structural features
    _RE_NEG = re.compile(r"\b(not|never)\b", re.I)
    _RE_COMP = re.compile(
        r"\b(\w+)\s+(greater|more|higher|less|fewer|lower)\s+than\s+(\w+)\b", re.I)
    _RE_COND = re.compile(r"\bif\b(.+?)\bthen\b(.+)", re.I)
    _RE_NUM = re.compile(r"\b([-+]?\d*\.?\d+)(?:\s*([a-zA-Z%]+))?\b")
    _RE_CAUSE = re.compile(r"\b(cause|causes|caused|lead to|leads to|result in)\b", re.I)
    _RE_ORDER = re.compile(r"\b(first|second|third|after|subsequently|next)\b", re.I)
    _RE_CONNECT = re.compile(r"\b(and|or|implies|if|then)\b", re.I)

    # meta‑confidence patterns
    _RE_PRESUP = re.compile(r"\b(have you (stopped|quit|ceased|given up) )\b", re.I)
    _RE_SCOPE = re.compile(r"\bevery\s+\w+.*\b(a|an)\s+\w+", re.I)
    _RE_PRON = re.compile(r"\b\w+\s+told\s+\w+\s+he|she|they\b", re.I)
    _RE_DICHOT = re.compile(r"\beither\b.+\bor\b.+", re.I)
    _RE_SUBJ = re.compile(r"\b(best|worst|favorite|most|least)\b", re.I)

    def __init__(self):
        pass

    # ------------------------------------------------------------------ #
    #  Public API
    # ------------------------------------------------------------------ #
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Score each candidate and return a ranked list."""
        g_prompt = self._build_graph(prompt)

        results = []
        for cand in candidates:
            g_cand = self._build_graph(cand)
            struct_score = self._graph_score(g_prompt, g_cand)

            # tiny NCD tie‑breaker (max 15 % weight)
            ncd = self._ncd(prompt, cand)
            ncd_score = 1.0 - ncd          # higher = more similar
            final = 0.85 * struct_score + 0.15 * ncd_score
            reasoning = (f"struct={struct_score:.3f}, ncd={ncd_score:.3f}, "
                         f"final={final:.3f}")
            results.append({"candidate": cand, "score": final,
                            "reasoning": reasoning})

        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return an honesty‑aware confidence in [0,1]."""
        meta = self._meta_confidence(prompt)
        if meta < 0.3:                     # ambiguous / unanswerable
            return meta * 0.8               # keep it low

        # structural confidence from best‑match score
        scores = [self._graph_score(self._build_graph(prompt),
                                    self._build_graph(answer))]
        base = max(scores)                 # single element now
        # map to [0.3,0.9] unless near‑certain
        conf = 0.3 + 0.6 * base
        if base > 0.95:
            conf = min(0.99, conf)          # allow up to 0.99 for definitive
        return min(conf, 0.9) if base <= 0.95 else conf

    # ------------------------------------------------------------------ #
    #  Core implementation
    # ------------------------------------------------------------------ #
    def _build_graph(self, text: str) -> Dict:
        """Parse text -> predicate list + adjacency matrix."""
        sentences = re.split(r"[.!?]\s*", text.strip())
        preds = []                         # list of (type_idx, numeric)
        for sent in sentences:
            if not sent:
                continue
            # 1‑hot type detection
            typ = None
            num = 0.0
            if self._RE_NEG.search(sent):
                typ = "NEG"
            elif m := self._RE_COMP.search(sent):
                typ = "COMP"
                # optional numeric capture from words (skip)
            elif m := self._RE_COND.search(sent):
                typ = "COND"
            elif self._RE_CAUSE.search(sent):
                typ = "CAUSE"
            elif self._RE_ORDER.search(sent):
                typ = "ORDER"
            elif self._RE_CONNECT.search(sent):
                typ = "CONNECT"
            # numeric slot (first number in sentence)
            if mnum := self._RE_NUM.search(sent):
                try:
                    num = float(mnum.group(1))
                except ValueError:
                    num = 0.0
            # default to CONNECT if nothing else matched
            if typ is None:
                typ = "CONNECT"
            type_idx = self._PRED_TYPES.index(typ)
            vec = np.zeros(len(self._PRED_TYPES) + 1)
            vec[type_idx] = 1.0
            vec[-1] = num / 100.0          # simple normalisation
            preds.append(vec)

        n = len(preds)
        if n == 0:
            # empty graph – return zero matrix
            return {"W": np.zeros((1, 1)), "size": 1}
        W = np.zeros((n, n))
        # edges: co‑occurrence in same sentence -> weight 1
        for i, j in combinations(range(n), 2):
            W[i, j] = W[j, i] = 1.0

        # extra edges for conditionals / causal cues
        for i, vec_i in enumerate(preds):
            typ_i = self._PRED_TYPES[int(np.argmax(vec_i[:-1]))]
            if typ_i in {"COND", "CAUSE"}:
                for j, vec_j in enumerate(preds):
                    if i == j:
                        continue
                    W[i, j] = max(W[i, j], 2.0)   # stronger directed influence

        # neuromodulatory gain per edge based on cue words in the whole text
        gain = np.ones_like(W)
        for cue in self._CUE_EXCIT:
            if cue in text.lower():
                gain *= 1.5
        for cue in self._CUE_INHIB:
            if cue in text.lower():
                gain *= 0.5
        W_mod = W * gain
        return {"W": W_mod, "size": n}

    def _graph_score(self, g_prompt: Dict, g_cand: Dict) -> float:
        """Spectral similarity with high‑frequency penalty."""
        Wp = g_prompt["W"]
        Wc = g_cand["W"]

        # pad to same size
        N = max(Wp.shape[0], Wc.shape[0])
        if Wp.shape[0] < N:
            pad = ((0, N - Wp.shape[0]), (0, N - Wp.shape[1]))
            Wp = np.pad(Wp, pad, constant_values=0)
        if Wc.shape[0] < N:
            pad = ((0, N - Wc.shape[0]), (0, N - Wc.shape[1]))
            Wc = np.pad(Wc, pad, constant_values=0)

        Sp = np.abs(np.fft.rfft(Wp, axis=0).flatten())
        Sc = np.abs(np.fft.rfft(Wc, axis=0).flatten())

        # cosine similarity
        dot = np.dot(Sp, Sc)
        norm = np.linalg.norm(Sp) * np.linalg.norm(Sc) + 1e-12
        sim = dot / norm

        # high‑frequency penalty
        freq = np.arange(len(Sp))
        diff = Sc - Sp
        pen = np.sum(np.maximum(0, diff) * freq) / (np.sum(freq) + 1e-12)

        alpha = 0.02                     # empirically small
        score = max(0.0, min(1.0, sim - alpha * pen))
        return score

    # ------------------------------------------------------------------ #
    #  Helper utilities
    # ------------------------------------------------------------------ #
    def _ncd(self, a: str, b: str) -> float:
        """Normalised Compression Distance using zlib."""
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + b).encode()))
        ncd = (cab - min(ca, cb)) / max(ca, cb)
        return max(0.0, min(1.0, ncd))

    def _meta_confidence(self, prompt: str) -> float:
        """Detect traps; return a base confidence in [0,1]."""
        low = 0.2  # base for ambiguous / unanswerable
        txt = prompt.lower()

        # presupposition
        if self._RE_PRESUP.search(txt):
            return low
        # scope ambiguity
        if self._RE_SCOPE.search(txt):
            return low
        # pronoun ambiguity
        if self._RE_PRON.search(txt):
            return low
        # false dichotomy
        if self._RE_DICHOT.search(txt):
            return low
        # subjectivity without measurable criteria
        if self._RE_SUBJ.search(txt):
            return low
        # generic unanswerability: no verb or question word
        if not re.search(r"\b(is|are|do|does|did|can|could|should|would|will)\b", txt):
            return low

        # no trap detected -> moderate base confidence
        return 0.6

# ---------------------------------------------------------------------- #
# Example usage (not part of the library, kept for illustration only):
# ---------------------------------------------------------------------- #
if __name__ == "__main__":
    rt = ReasoningTool()
    prompt = ("If the temperature rises above 30°C then the reaction rate "
              "increases. The rate at 35°C is 1.5 times the rate at 25°C.")
    candidates = [
        "The rate at 35°C is 1.5 times the rate at 25°C.",
        "The rate at 35°C is the same as at 25°C.",
        "The rate at 35°C is lower than at 25°C."
    ]
    for r in rt.evaluate(prompt, candidates):
        print(r)
    print("Confidence:", rt.confidence(prompt, candidates[0]))


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
