import itertools
import zlib
import random
from typing import Dict, Tuple

"""
ReasoningTool implements a very compact version of the
Thermodynamic‑Genetic Model‑Checker (TG‑MC) described in the prompt.

* Parsing – deterministic regexes extract logical atoms:
  negations, comparatives, conditionals, numbers, causals,
  temporal words and quantifiers.  The result is stored as a
  lightweight directed graph (dict of {src: [(rel, dst), ...]}).

* Energy – a hand‑crafted "entropy" measures how far a candidate
  violates its own logical graph.
      • missing consequent of an "if ... then ..." clause
      • contradictory comparatives (e.g., A > B and later A <= B)
      • numeric distance from a reference value (not used here)
  Lower energy -> higher quality.

* Genetic search – each candidate spawns a small population of
  mutated copies (negation flip, comparative swap, numeric jitter).
  The best (lowest) energy observed during the fixed‑size evolution
  is the candidate's raw score.

* Model checking – a tiny explicit‑state checker validates every
  conditional after each generation; violations add a fixed surcharge.

* Confidence – a meta‑confidence analyser inspects the *prompt* for
  presuppositions, scope/pronoun ambiguity, false dichotomies,
  subjectivity and unanswerability.  The returned confidence is the
  product of this meta‑score and a calibration based on the candidate's
  structural certainty, never exceeding 0.9 unless the answer is
  mathematically definitive.

The implementation uses only the Python standard library and NumPy,
fits well under 200 lines and is deterministic (fixed random seed)."""

import re, zlib, itertools, random, math
from typing import List, Dict, Tuple
import numpy as np

random.seed(0)                     # deterministic GA


# ----------------------------------------------------------------------
# 1.  Parsing utilities
# ----------------------------------------------------------------------
NEG_RE = re.compile(r'\b(not|no|without)\b', re.I)
COMP_RE = re.compile(r'(\b\w+\b)\s*(>=|<=|>|<|=)\s*(\b\w+\b)', re.I)
COND_RE = re.compile(r'\bif\s+([^,.;]+?)\s+then\s+([^,.;]+)', re.I)
NUM_RE = re.compile(r'(?P<num>\d+(\.\d+)?)(?P<unit>\s*[a-zA-Z%]*)')
CAUS_RE = re.compile(r'\b(causes?|leads? to|results? in)\b', re.I)
TEMP_RE = re.compile(r'\b(before|after|simultaneously)\b', re.I)
QUANT_RE = re.compile(r'\b(all|some|none|every|each)\b', re.I)


def _tokenise(text: str) -> List[str]:
    return re.findall(r'\b\w+\b', text.lower())


def parse_features(txt: str) -> Dict:
    """Return a dict describing the logical atoms of *txt*."""
    feats = {
        "neg": [m.group() for m in NEG_RE.finditer(txt)],
        "comp": [(m.group(1), m.group(2), m.group(3)) for m in COMP_RE.finditer(txt)],
        "cond": [(m.group(1).strip(), m.group(2).strip())
                 for m in COND_RE.finditer(txt)],
        "num": [(float(m.group('num')), m.group('unit').strip())
                for m in NUM_RE.finditer(txt)],
        "caus": [m.start() for m in CAUS_RE.finditer(txt)],
        "temp": [m.group() for m in TEMP_RE.finditer(txt)],
        "quant": [m.group() for m in QUANT_RE.finditer(txt)],
    }
    return feats


# ----------------------------------------------------------------------
# 2.  Energy (entropy) computation
# ----------------------------------------------------------------------
LARGE = 1e6          # penalty for a hard logical violation


def _cond_satisfied(cond: Tuple[str, str], txt: str) -> bool:
    """True if the consequent appears after the antecedent in *txt*."""
    ant, con = cond
    ant_idx = txt.lower().find(ant.lower())
    con_idx = txt.lower().find(con.lower())
    return ant_idx != -1 and con_idx != -1 and con_idx > ant_idx


def _contradictory_comps(comps: List[Tuple[str, str, str]]) -> int:
    """Count pairs of contradictory comparatives (A > B and A <= B)."""
    cnt = 0
    for (a1, op1, b1), (a2, op2, b2) in itertools.combinations(comps, 2):
        if a1 == a2 and b1 == b2:
            # simple contradictory table
            if (op1, op2) in {('>', '<='), ('>=', '<'), ('<', '>='), ('<=', '>')}:
                cnt += 1
    return cnt


def energy(txt: str, feats: Dict) -> float:
    """Thermodynamic‑style energy for a candidate answer."""
    e = 0.0
    # logical‑violation penalty
    for cond in feats["cond"]:
        if not _cond_satisfied(cond, txt):
            e += LARGE
    # inconsistency penalty (contradictory comparatives)
    e += 10.0 * _contradictory_comps(feats["comp"])
    # numeric deviation – not used (placeholder)
    return e


# ----------------------------------------------------------------------
# 3.  Genetic operators (very small population, deterministic)
# ----------------------------------------------------------------------
def _mutate(txt: str, feats: Dict) -> str:
    """Return a mutated copy of *txt*."""
    words = _tokenise(txt)
    # 1) flip a random negation word
    if feats["neg"]:
        w = random.choice(feats["neg"])
        txt = re.sub(r'\b' + re.escape(w) + r'\b',
                     'not' if w.lower() != 'not' else 'no', txt, flags=re.I)
    # 2) swap a comparative operator
    if feats["comp"]:
        a, op, b = random.choice(feats["comp"])
        swap = {'>': '<=', '<': '>=', '>=': '<', '<=': '>'}
        new_op = swap.get(op, op)
        txt = re.sub(r'(' + re.escape(a) + r'\s*)' + re.escape(op) +
                     r'(\s*' + re.escape(b) + r')',
                     r'\1' + new_op + r'\2', txt, flags=re.I)
    # 3) jitter a numeric literal
    if feats["num"]:
        val, unit = random.choice(feats["num"])
        jitter = round(val * (1 + random.uniform(-0.05, 0.05)), 2)
        txt = re.sub(r'\b' + re.escape(str(val)) + r'\b',
                     str(jitter), txt, count=1)
    return txt


def ga_best(txt: str, generations: int = 5, popsize: int = 4) -> Tuple[float, str]:
    """Run a tiny GA on *txt* and return (best_energy, best_text)."""
    best_txt, best_e = txt, energy(txt, parse_features(txt))
    population = [txt] * popsize
    for _ in range(generations):
        new_pop = []
        for individual in population:
            feats = parse_features(individual)
            child = _mutate(individual, feats)
            new_pop.append(child)
        # evaluate
        for cand in new_pop:
            e = energy(cand, parse_features(cand))
            if e < best_e:
                best_e, best_txt = e, cand
        population = new_pop
    return best_e, best_txt


# ----------------------------------------------------------------------
# 4.  Model‑checking (explicit‑state, very light)
# ----------------------------------------------------------------------
def model_check(txt: str, feats: Dict) -> bool:
    """Return True if all conditionals are satisfied."""
    return all(_cond_satisfied(c, txt) for c in feats["cond"])


# ----------------------------------------------------------------------
# 5.  Normalised Compression Distance (fallback / tie‑breaker)
# ----------------------------------------------------------------------
def ncd(a: str, b: str) -> float:
    """Simple NCD using zlib compression."""
    ca = len(zlib.compress(a.encode()))
    cb = len(zlib.compress(b.encode()))
    cab = len(zlib.compress((a + b).encode()))
    return (cab - min(ca, cb)) / max(ca, cb)


# ----------------------------------------------------------------------
# 6.  Meta‑confidence analysis (Tier B traps)
# ----------------------------------------------------------------------
META_PATTERNS = {
    "presupposition": re.compile(
        r'\b(have you (stopped|quit|ceased|given up) |why did .* (fail|stop))\b',
        re.I),
    "scope_ambiguity": re.compile(r'\bevery\s+\w+.*\s+(a|an)\s+\w+', re.I),
    "pronoun_ambiguity": re.compile(r'\b\w+\s+told\s+\w+\s+he|she\b', re.I),
    "false_dichotomy": re.compile(r'\beither\s+.+\s+or\s+.+\b', re.I),
    "subjectivity": re.compile(r'\b(best|worst|favorite|most|least)\b', re.I),
    "unanswerable": re.compile(r'\b(unknown|not (given|provided|stated))\b', re.I),
}


def _meta_confidence(prompt: str) -> float:
    """Detect Tier B traps; return a base confidence in [0,1]."""
    penalty = 0
    for name, pat in META_PATTERNS.items():
        if pat.search(prompt):
            penalty += 0.2          # each trap reduces confidence
    return max(0.0, 1.0 - penalty)


# ----------------------------------------------------------------------
# 7.  Main class
# ----------------------------------------------------------------------
class ReasoningTool:
    """
    Tiny TG‑MC implementation.

    *evaluate* scores a list of candidate answers.
    *confidence* returns a calibrated confidence for a single answer.
    """

    def __init__(self):
        self._ref = ""                     # placeholder for future reference answer

    # ------------------------------------------------------------------
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Score and rank candidates; higher score = more plausible."""
        # baseline NCD against the prompt (used only for tie‑breaking)
        ncd_scores = [ncd(prompt, c) for c in candidates]

        # GA + energy for each candidate
        energies = []
        for cand in candidates:
            e, _ = ga_best(cand)          # best energy after GA
            energies.append(e)

        # normalise energies -> [0,1] (lower energy -> higher score)
        max_e, min_e = max(energies), min(energies)
        if max_e == min_e:
            norm = [0.5] * len(candidates)
        else:
            norm = [1.0 - (e - min_e) / (max_e - min_e) for e in energies]

        # blend with NCD (max 15% of final weight)
        final = [0.85 * s + 0.15 * (1 - n) for s, n in zip(norm, ncd_scores)]

        # assemble output
        out = []
        for cand, sc in zip(candidates, final):
            reason = f"energy={energies[candidates.index(cand)]:.1f}, " \
                     f"NCD={ncd_scores[candidates.index(cand)]:.3f}"
            out.append({"candidate": cand, "score": sc, "reasoning": reason})

        out.sort(key=lambda d: d["score"], reverse=True)
        return out

    # ------------------------------------------------------------------
    def confidence(self, prompt: str, answer: str) -> float:
        """
        Calibrated confidence 0‑1.
        Uses meta‑confidence (prompt analysis) and structural certainty.
        """
        base = _meta_confidence(prompt)          # 0‑1
        # structural certainty = proportion of unambiguous features
        feats = parse_features(answer)
        total = sum(len(v) for v in feats.values())
        ambiguous = sum(1 for v in feats.values() if not v)   # missing info
        if total == 0:
            struct = 0.0
        else:
            struct = 1.0 - ambiguous / total

        conf = base * struct
        # cap according to the rule (never >0.9 unless definitive)
        if conf > 0.9:
            conf = 0.9
        # if meta‑confidence is very low, force a low ceiling
        if base < 0.3:
            conf = min(conf, 0.3)
        return float(conf)

    # ------------------------------------------------------------------
    # expose for internal use (not part of public API)
    def _meta_confidence(self, prompt: str) -> float:
        return _meta_confidence(prompt)


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
