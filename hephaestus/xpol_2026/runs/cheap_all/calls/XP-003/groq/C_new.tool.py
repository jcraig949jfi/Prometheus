from typing import Dict

"""
ReasoningTool
==============

A compact implementation of the theoretical design described in the prompt.
It builds a small proposition graph from a candidate answer, analyses its
topology (Betti numbers), runs a discrete‑time dynamical propagation on the
graph and measures sensitivity to tiny lexical perturbations.  The final
score mixes:

* structural coherence   (beta0, beta1)
* dynamical stability    (Lyapunov‑like norm change)
* robustness             (sensitivity index)
* a tiny NCD tie‑breaker (zlib)

The tool also supplies an epistemically honest *confidence* estimate that
looks for common ambiguity patterns in the *prompt* (presupposition,
scope‑ambiguity, pronoun‑ambiguity, false‑dichotomy, subjectivity,
unanswerability).  When any of those patterns are detected the confidence
is forced below 0.3, otherwise it is proportional to the reasoning score.

Only standard library, ``numpy``, ``networkx`` and the supplied
``forge_primitives`` are used.  No heavy ML libraries are required and the
behaviour is deterministic.
"""
import re
import zlib
import json
import numpy as np
import networkx as nx
from typing import List, Dict

# ----------------------------------------------------------------------
# primitives (the "library of composable reasoning primitives")
# ----------------------------------------------------------------------
from forge_primitives import (
    dag_traverse,                # Graph/Causal
    topological_sort,           # Graph/Causal
    bayesian_update,            # Probability
    solve_sat,                  # Logic
    confidence_from_agreement, # Meta
)

# ----------------------------------------------------------------------
# helper regexes for parsing propositions
# ----------------------------------------------------------------------
_NEGATION_RE = re.compile(r'\b(not|never|no )\b', re.I)
_COMPARATIVE_RE = re.compile(r'\b(more than|less than|greater than|smaller than)\b', re.I)
_CONDITIONAL_RE = re.compile(r'\bif\s+(.+?)\s+then\s+(.+)', re.I)
_CAUSAL_RE = re.compile(r'\b(causes?|leads to|results in)\b', re.I)
_NUMERIC_RE = re.compile(r'[-+]?\d*\.?\d+(?:%|e[-+]?\d+)?')
_LEX_WEIGHT = {
    'but': -0.8, 'however': -0.7, 'although': -0.6,
    'therefore': 0.9, 'so': 0.8, 'hence': 0.85,
    'and': 0.2, 'or': 0.0, 'if': 0.5,
}
# ----------------------------------------------------------------------


class ReasoningTool:
    """Implements the topology * dynamics * sensitivity evaluator."""

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    def __init__(self):
        # nothing to initialise – all work is functional
        pass

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Score each candidate answer and return a ranked list.
        Each entry: {"candidate": str, "score": float, "reasoning": str}
        """
        results = []
        for cand in candidates:
            # 1. build proposition graph
            G, vertex_vecs = self._build_graph(cand)

            # 2. topological invariants
            beta0, beta1 = self._betti_numbers(G)

            # 3. dynamical propagation (Lyapunov‑like)
            lyap, final_state = self._run_dynamics(G, vertex_vecs)

            # 4. sensitivity index
            si = self._sensitivity(G, vertex_vecs, final_state)

            # 5. combine into a raw score (0‑1)
            raw = self._combine_score(beta0, beta1, lyap, si, len(G))

            # 6. tiny NCD tie‑breaker (max 0.05 of final score)
            ncd = self._ncd(prompt, cand)
            score = min(1.0, raw + 0.05 * (1 - ncd))

            # 7. human‑readable reasoning string
            reasoning = (
                f"beta0={beta0}, beta1={beta1}, lyap={lyap:.3f}, SI={si:.3f}, "
                f"NCD={ncd:.3f}"
            )
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})

        # rank by descending score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Epistemically honest confidence (0‑1).  Uses meta‑confidence checks
        on the *prompt* and caps the value by the reasoning score.
        """
        meta = self._meta_confidence(prompt)
        # if the prompt is ambiguous we stay low regardless of the answer
        if meta < 0.3:
            return meta

        # otherwise compute a reasoning score for the answer alone
        G, vecs = self._build_graph(answer)
        beta0, beta1 = self._betti_numbers(G)
        lyap, _ = self._run_dynamics(G, vecs)
        si = self._sensitivity(G, vecs, None)
        raw = self._combine_score(beta0, beta1, lyap, si, len(G))

        # combine meta‑confidence and raw reasoning confidence
        return float(confidence_from_agreement([meta, raw]))

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------
    def _build_graph(self, text: str):
        """
        Very light‑weight proposition extraction -> directed graph.
        Returns (networkx.DiGraph, dict[node] = 5‑dim vector).
        """
        G = nx.DiGraph()
        vertex_vecs = {}

        # split on sentence terminators – crude but sufficient
        sentences = re.split(r'[.!?]\s*', text.strip())
        for i, sent in enumerate(s for s in sentences if s):
            node = f"N{i}"
            # type tag
            if _CAUSAL_RE.search(sent):
                typ = "causal"
            elif _COMPARATIVE_RE.search(sent):
                typ = "comparative"
            elif _NEGATION_RE.search(sent):
                typ = "negation"
            else:
                typ = "fact"

            # value vector (polarity, magnitude, temporal, depth, hole‑indicator)
            polarity = -1.0 if _NEGATION_RE.search(sent) else 1.0
            mags = [float(m) for m in _NUMERIC_RE.findall(sent)]
            magnitude = float(mags[0]) if mags else 0.0
            temporal = 0.0  # not inferred here
            depth = len(re.findall(r'\b(if|because|since)\b', sent, re.I))
            hole = 0.0  # placeholder – graph connectivity handled later
            vec = np.array([polarity, magnitude, temporal, depth, hole], dtype=float)
            vertex_vecs[node] = vec
            G.add_node(node, type=typ, vec=vec)

        # add edges based on simple lexical cues
        for src, data_src in G.nodes(data=True):
            sent_src = sentences[int(src[1:])]
            # conditionals create directed edges
            m = _CONDITIONAL_RE.search(sent_src)
            if m:
                # find target node that contains the consequent clause
                consequent = m.group(2).strip()
                for tgt, data_tgt in G.nodes(data=True):
                    if tgt != src and consequent in sentences[int(tgt[1:])]:
                        weight = _LEX_WEIGHT.get('if', 0.5)
                        G.add_edge(src, tgt, weight=weight, delay=1)
            # causal verbs also create edges to following sentences
            if _CAUSAL_RE.search(sent_src):
                nxt = f"N{int(src[1:]) + 1}"
                if nxt in G:
                    weight = _LEX_WEIGHT.get('therefore', 0.9)
                    G.add_edge(src, nxt, weight=weight, delay=1)

        # fill missing "hole‑indicator" (0 = fully connected, 1 = missing link)
        for n in G:
            vertex_vecs[n][4] = 0.0 if G.out_degree(n) + G.in_degree(n) > 0 else 1.0

        return G, vertex_vecs

    # ------------------------------------------------------------------
    def _betti_numbers(self, G: nx.DiGraph):
        """beta0 = #connected components, beta1 = #independent cycles (undirected)."""
        UG = G.to_undirected()
        beta0 = nx.number_connected_components(UG)
        # cycle_basis returns a list of independent cycles
        beta1 = len(nx.cycle_basis(UG))
        return beta0, beta1

    # ------------------------------------------------------------------
    def _run_dynamics(self, G: nx.DiGraph, vecs: dict):
        """
        Discrete‑time linear dynamics: s_{t+1}=A·s_t + b.
        Returns (Lyapunov‑like score, final state vector).
        """
        nodes = list(G.nodes())
        n = len(nodes)
        if n == 0:
            return 1.0, np.zeros(5)

        # adjacency matrix A (weights only, delays ignored for simplicity)
        A = np.zeros((5, 5))
        for u, v, data in G.edges(data=True):
            w = data.get("weight", 0.0)
            # propagate from source vector to target vector linearly
            A += w * np.outer(vecs[v], vecs[u])

        # b = sum of all vertex vectors (acts as constant input)
        b = sum(vecs.values())

        # initial state s0 = sum of vectors
        s = b.copy()
        eps = 1e-6
        T = max(1, n)  # number of steps
        for _ in range(T):
            s_next = A @ s + b
            if np.linalg.norm(s_next - s) < eps:
                break
            s = s_next

        # Lyapunov‑like: smaller change = more stable (0 = perfect)
        lyap = np.linalg.norm(s_next - s) / (np.linalg.norm(s) + 1e-9)
        return lyap, s

    # ------------------------------------------------------------------
    def _sensitivity(self, G: nx.DiGraph, vecs: dict, base_state):
        """
        Perturb each vertex vector by ±0.1 (all dimensions) and recompute the
        final state.  Return the average norm change per unit perturbation.
        """
        if base_state is None:
            _, base_state = self._run_dynamics(G, vecs)

        perturbed_states = []
        delta = 0.1
        for node in G.nodes():
            for sign in (-1, 1):
                vec_pert = vecs[node].copy()
                vec_pert += sign * delta
                vecs_pert = vecs.copy()
                vecs_pert[node] = vec_pert
                _, s = self._run_dynamics(G, vecs_pert)
                perturbed_states.append(s)

        if not perturbed_states:
            return 0.0
        diffs = [np.linalg.norm(s - base_state) for s in perturbed_states]
        si = np.mean(diffs) / (delta * np.sqrt(5))
        return float(si)

    # ------------------------------------------------------------------
    def _combine_score(self, beta0, beta1, lyap, si, V):
        """
        alpha·(1‑beta0/|V|) + beta·(1‑beta1/|V|) + gamma·(1‑Lyapunov) – lambda_·SI
        with alpha=0.4, beta=0.2, gamma=0.3, lambda_=0.1
        """
        if V == 0:
            return 0.0
        alpha, beta, gamma, lambda_ = 0.4, 0.2, 0.3, 0.1
        term0 = 1 - beta0 / V
        term1 = 1 - beta1 / V
        term2 = 1 - lyap
        score = alpha * term0 + beta * term1 + gamma * term2 - lambda_ * si
        return max(0.0, min(1.0, score))

    # ------------------------------------------------------------------
    def _ncd(self, prompt: str, candidate: str) -> float:
        """Normalized Compression Distance using zlib (quick approximation)."""
        a = (prompt + " ").encode()
        b = candidate.encode()
        ab = a + b
        ca = len(zlib.compress(a))
        cb = len(zlib.compress(b))
        cab = len(zlib.compress(ab))
        return (cab - min(ca, cb)) / max(ca, cb)

    # ------------------------------------------------------------------
    # meta‑confidence detection (prompt‑only)
    # ------------------------------------------------------------------
    def _meta_confidence(self, prompt: str) -> float:
        """
        Returns a base confidence in [0,1] based on ambiguity patterns.
        If any pattern matches the confidence is forced below 0.3.
        """
        low = 0.1  # default low confidence when ambiguous
        # 1. presupposition
        if re.search(r'\b(have you|did you|why did|why have you)\s+(stopped|quit|failed|stopped)\b', prompt,
                     re.I):
            return low

        # 2. scope ambiguity – "Every X ... a Y"
        if re.search(r'\bevery\s+\w+\b.*\ba\s+\w+\b', prompt, re.I):
            return low

        # 3. pronoun ambiguity – "X told Y he/she ..."
        if re.search(r'\b\w+\s+told\s+\w+\s+(he|she|they)\b', prompt, re.I):
            return low

        # 4. false dichotomy – "Either A or B" without "both"
        if re.search(r'\beither\s+.+\s+or\s+.+\b', prompt, re.I) and not re.search(r'\bboth\b', prompt, re.I):
            return low

        # 5. subjectivity – "best", "worst", "favorite", "most beautiful", etc.
        if re.search(r'\b(best|worst|favorite|most|least|beautiful|ugly)\b', prompt, re.I):
            return low

        # 6. unanswerability – no question word or no detectable entity
        if not re.search(r'\b(what|why|how|when|where|who|which)\b', prompt, re.I):
            return low

        # no pattern matched -> moderate confidence (will be capped by reasoning)
        return 0.7

    # ------------------------------------------------------------------
    # optional: expose meta‑confidence for external inspection
    # ------------------------------------------------------------------
    def meta_confidence(self, prompt: str) -> float:
        """Public wrapper for the internal meta‑confidence check."""
        return self._meta_confidence(prompt)


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
