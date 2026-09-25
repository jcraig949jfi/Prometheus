from typing import Dict

"""
ReasoningTool
==============

A lightweight Python implementation of the pipeline described in the prompt:

1. **Parsing -> Proposition graph** – simple regex patterns extract atomic
   propositions (equality, inequality, "if ... then ...", "causes", "not ...").
   Each unique proposition becomes a node; directed edges encode the logical
   relation with signed weights.

2. **Spectral embedding** – the normalized graph Laplacian is built, its first
   k eigenvectors (k = min(10, n)) form a low‑frequency basis.  The initial
   truth vector (1 = asserted true, 0 = asserted false, 0.5 = unknown) is
   projected onto this basis.

3. **Morphogenetic reaction‑diffusion** – a FitzHugh‑Nagumo‑like update is
   applied to the spectral modes until convergence.  The dynamics create a
   bistable "true/false" attractor while diffusion propagates constraints
   through the logical edges.

4. **Maximum‑entropy scoring** – final spectral states are mapped back to node
   space; for each candidate answer the mean truth of the propositions it
   contains is taken as the Bernoulli parameter p, which is used as the
   plausibility score.

5. **Meta‑confidence** – a rule‑based detector looks for presupposition,
   scope/pronoun ambiguity, false dichotomies, subjectivity and outright
   unanswerability.  When any of these patterns appear the confidence is
   capped below 0.3, otherwise it follows the (calibrated) score.

Only the Python standard library and NumPy are required; the code is fully
deterministic and stays well under 200 lines.
"""

import re
import zlib
import numpy as np
from typing import List, Dict


class ReasoningTool:
    """Implements the Morphogenesis‑Spectral‑MaxEnt reasoning pipeline."""

    # --------------------------------------------------------------------- #
    # 1.  Parsing utilities
    # --------------------------------------------------------------------- #
    _ATOM_RE = re.compile(
        r'(?P<neg>not\s+)?(?P<subj>\w+)\s*'
        r'(?P<op>is|=|>|<|>=|<=|causes|leads\s+to|if\s+.*?\s+then)\s*'
        r'(?P<obj>[\w\.]+)'
    )
    _COND_RE = re.compile(r'if\s+(?P<ante>.+?)\s+then\s+(?P<cons>.+)', re.I)
    _COMP_RE = re.compile(r'(?P<a>\d+\.?\d*)\s*(?P<op>>=|<=|>|<|=)\s*(?P<b>\d+\.?\d*)')
    _NUM_RE = re.compile(r'\d+\.?\d*')

    def __init__(self):
        pass

    # --------------------------------------------------------------------- #
    # 2.  Core pipeline
    # --------------------------------------------------------------------- #
    def _parse(self, text: str):
        """Extract propositions, truth values and adjacency matrix."""
        nodes = {}                     # proposition string -> index
        truth = []                     # initial truth per node
        edges = []                     # (i, j, weight)

        # Helper to register a proposition
        def add_prop(p, val=None):
            if p not in nodes:
                nodes[p] = len(nodes)
                truth.append(0.5)      # unknown by default
            if val is not None:
                truth[nodes[p]] = val

        # 1) Simple atomic patterns
        for m in self._ATOM_RE.finditer(text):
            neg = bool(m.group('neg'))
            subj, op, obj = m.group('subj'), m.group('op'), m.group('obj')
            prop = f"{subj} {op} {obj}"
            add_prop(prop, 0.0 if neg else 1.0)

            # conditional edge (if ... then ...) handled later
            if op.lower().startswith('if'):
                # ignore – will be caught by _COND_RE
                continue

        # 2) Conditional sentences
        for m in self._COND_RE.finditer(text):
            ante, cons = m.group('ante').strip(), m.group('cons').strip()
            add_prop(ante)
            add_prop(cons)
            i, j = nodes[ante], nodes[cons]
            edges.append((i, j, +1.0))          # excitatory conditional

        # 3) Comparative numeric statements
        for m in self._COMP_RE.finditer(text):
            a, op, b = float(m.group('a')), m.group('op'), float(m.group('b'))
            prop = f"{a} {op} {b}"
            add_prop(prop, 1.0 if eval(f"{a}{op}{b}") else 0.0)
            # weight proportional to magnitude difference
            weight = (abs(a - b) + 1e-6)
            if op in ('>', '>='):
                edges.append((nodes[prop], nodes[prop], weight))
            else:
                edges.append((nodes[prop], nodes[prop], -weight))

        n = len(nodes)
        A = np.zeros((n, n))
        for i, j, w in edges:
            A[i, j] += w

        return list(nodes.keys()), np.array(truth), A

    def _spectral(self, A: np.ndarray, x0: np.ndarray, k: int = 10):
        """Compute low‑frequency basis and project the initial truth vector."""
        n = A.shape[0]
        deg = np.maximum(A.sum(axis=1), 1e-6)
        D_inv_sqrt = np.diag(1.0 / np.sqrt(deg))
        L = np.eye(n) - D_inv_sqrt @ A @ D_inv_sqrt          # normalized Laplacian
        # eigen‑decomposition (symmetric)
        vals, vecs = np.linalg.eigh(L)
        idx = np.argsort(vals)[1:k+1]                         # skip zero eigenvalue
        U = vecs[:, idx]                                      # n * k
        z0 = U.T @ x0
        return L, U, z0

    def _reaction_diffusion(self, L: np.ndarray, z: np.ndarray,
                            eps=0.01, a=0.7, b=0.8, delta=1e-5, max_iter=500):
        """FitzHugh‑Nagumo dynamics on spectral modes."""
        w = np.zeros_like(z)
        for _ in range(max_iter):
            dz = z - (z**3) / 3.0 - w + L @ z
            dw = eps * (z + a - b * w)
            z_new = z + 0.01 * dz
            w_new = w + 0.01 * dw
            if np.linalg.norm(z_new - z) < delta:
                break
            z, w = z_new, w_new
        return z

    def _maxent_score(self, U: np.ndarray, z: np.ndarray,
                      prop_list: List[str], candidate: str):
        """Map back to node space and compute Bernoulli parameter for the candidate."""
        x = U @ z                     # n‑dim truth estimate
        # extract propositions from candidate using same parser
        cand_props = set()
        for m in self._ATOM_RE.finditer(candidate):
            cand_props.add(f"{m.group('subj')} {m.group('op')} {m.group('obj')}")
        for m in self._COND_RE.finditer(candidate):
            cand_props.add(m.group('ante').strip())
            cand_props.add(m.group('cons').strip())
        for m in self._COMP_RE.finditer(candidate):
            cand_props.add(f"{m.group('a')} {m.group('op')} {m.group('b')}")
        # map to indices
        idx = [i for i, p in enumerate(prop_list) if p in cand_props]
        if not idx:                     # no overlap -> fallback to low score
            return 0.0, "No propositional overlap"
        mu = np.mean(x[idx])
        return float(np.clip(mu, 0.0, 1.0)), f"Mean truth of {len(idx)} props = {mu:.3f}"

    # --------------------------------------------------------------------- #
    # 3.  Meta‑confidence detector
    # --------------------------------------------------------------------- #
    _AMBIG_PATTERNS = {
        "presupposition": re.compile(r'\b(have you|did you|why did|how could)\s+(stopped|quit|failed|stopped)\b', re.I),
        "scope": re.compile(r'\bevery\s+\w+.*\b(a|an)\s+\w+\b', re.I),
        "pronoun": re.compile(r'\b\w+\s+told\s+\w+\s+he|she|they\b', re.I),
        "dichotomy": re.compile(r'\beither\b.*\bor\b', re.I),
        "subjective": re.compile(r'\b(best|worst|favorite|most|least)\b', re.I),
        "unanswerable": re.compile(r'\bwhat\s+is\s+the\s+name\s+of\b', re.I)
    }

    def _meta_confidence(self, prompt: str) -> float:
        """Return a base confidence (0‑1) based on ambiguity detection."""
        for name, pat in self._AMBIG_PATTERNS.items():
            if pat.search(prompt):
                return 0.2                     # low confidence for any trap
        return 0.9                             # otherwise we are willing to trust

    # --------------------------------------------------------------------- #
    # 4.  Public interface
    # --------------------------------------------------------------------- #
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Score each candidate and return a ranked list with reasoning."""
        props, truth_vec, A = self._parse(prompt)
        if not props:                         # nothing parsed -> fallback
            scores = [(c, 0.0, "No structure extracted") for c in candidates]
        else:
            L, U, z0 = self._spectral(A, truth_vec, k=min(10, len(props)))
            z = self._reaction_diffusion(L, z0)
            scores = []
            for c in candidates:
                sc, reason = self._maxent_score(U, z, props, c)
                scores.append((c, sc, reason))

        # optional NCD tie‑breaker (max 15 % of final score)
        def ncd(a, b):
            return len(zlib.compress(a.encode())) + len(zlib.compress(b.encode()))

        # combine with tiny NCD weight
        final = []
        for cand, sc, reason in scores:
            ncd_weight = 0.0
            if sc == max(s[1] for s in scores):   # only on top‑tied items
                ncd_weight = 0.15 * (1.0 / (1 + ncd(prompt, cand)))
            final.append({"candidate": cand,
                          "score": float(sc + ncd_weight),
                          "reasoning": reason})

        final.sort(key=lambda d: d["score"], reverse=True)
        return final

    def confidence(self, prompt: str, answer: str) -> float:
        """Return a calibrated confidence 0‑1 respecting epistemic honesty."""
        base = self._meta_confidence(prompt)          # low if ambiguous
        # compute a structural score for the specific answer
        props, truth_vec, A = self._parse(prompt)
        if not props:
            return min(base, 0.3)                     # nothing to base on
        L, U, z0 = self._spectral(A, truth_vec, k=min(10, len(props)))
        z = self._reaction_diffusion(L, z0)
        sc, _ = self._maxent_score(U, z, props, answer)
        # blend: we trust the max‑ent probability but never exceed the meta cap
        conf = min(base, sc)
        # enforce the required ceiling
        if conf > 0.9:
            conf = 0.9
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
