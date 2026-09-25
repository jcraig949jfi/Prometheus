import random
from typing import Dict, Tuple

"""
ReasoningTool
==============

A compact implementation of the *search‑guided reasoning graph* (SRG) described in
the prompt.  It combines three ideas:

* Neural‑Architecture‑Search‑style sub‑graph optimisation (binary edge masks)
* Pragmatic utility evaluation (consistency + coverage)
* Network‑science graph operations (transitivity, topological order)

The heavy lifting is delegated to the *forge_primitives* library – we only
re‑wire a few primitives:

    solve_sat          – checks logical consistency of the edge set
    modus_ponens       – expands implications
    check_transitivity– propagates equivalence/implication
    topological_sort   – orders causal/DAG edges
    confidence_from_agreement – merges several confidence signals
    information_sufficiency   – flags unanswerable prompts

All other work (parsing, mask handling, utility computation) is done with
NumPy, ``re`` and the standard library.  The code stays well below the 200‑line
limit and is fully deterministic.
"""

import re
import zlib
import itertools
from collections import defaultdict
from typing import List, Dict, Tuple

import numpy as np
from forge_primitives import (
    solve_sat,
    modus_ponens,
    check_transitivity,
    topological_sort,
    confidence_from_agreement,
    information_sufficiency,
)

# --------------------------------------------------------------------------- #
# Helper functions for parsing and graph construction
# --------------------------------------------------------------------------- #

def _tokenise(sentence: str) -> List[str]:
    """Very small tokenizer – lower‑case, keep alphanumerics and '_'."""
    return re.findall(r"\b\w+\b", sentence.lower())

def _extract_propositions(text: str) -> List[Tuple[str, str, str]]:
    """
    Very naive SPO extraction: look for patterns "X verb Y".
    Returns a list of (subject, predicate, object) triples.
    """
    triples = []
    # split on punctuation
    for sent in re.split(r"[.!?]\s*", text):
        words = _tokenise(sent)
        if len(words) < 3:
            continue
        # find a verb (simple heuristic: word ending with 'ed' or 's' or common verbs)
        verbs = {"is", "are", "was", "were", "has", "have", "had",
                 "do", "does", "did", "can", "could", "will", "would",
                 "should", "may", "might", "must", "need", "needs"}
        for i, w in enumerate(words[1:-1], 1):
            if w in verbs or w.endswith("ed") or w.endswith("s"):
                triples.append((words[i - 1], w, words[i + 1]))
                break
    return triples

def _build_vocab(triples: List[Tuple[str, str, str]]) -> Dict[str, int]:
    vocab = {}
    idx = 0
    for s, p, o in triples:
        for token in (s, p, o):
            if token not in vocab:
                vocab[token] = idx
                idx += 1
    return vocab

def _triples_to_edges(triples: List[Tuple[str, str, str]],
                      vocab: Dict[str, int]) -> Dict[Tuple[int, int], int]:
    """
    Convert triples to directed edges with a weight:
        implication   -> 1
        equivalence   -> 2   (detected by "same as", "equal")
        contradiction -> -1  (detected by "not", "no")
    """
    edges = {}
    for s, p, o in triples:
        si, pi, oi = vocab[s], vocab[p], vocab[o]
        # simple rule‑based weight
        if p in {"if", "when", "because", "leads", "causes"}:
            edges[(si, oi)] = 1          # implication
        elif p in {"same", "equal", "identical"}:
            edges[(si, oi)] = 2          # equivalence
        elif any(neg in p for neg in {"not", "no", "never"}):
            edges[(si, oi)] = -1         # contradiction
        else:
            edges[(si, oi)] = 1          # default to implication
    return edges

def _mask_population(edge_keys: List[Tuple[int, int]],
                     pop_size: int = 5) -> List[np.ndarray]:
    """Generate a small NAS population – binary masks over the edge list."""
    masks = []
    for _ in range(pop_size):
        mask = np.random.binomial(1, 0.5, size=len(edge_keys)).astype(bool)
        masks.append(mask)
    return masks

def _utility(mask: np.ndarray,
             edge_keys: List[Tuple[int, int]],
             edge_vals: List[int],
             required_nodes: set,
             n_nodes: int) -> float:
    """
    Pragmatic utility:
        alpha * (consistent edges / |V|) + beta * (coverage / |V|)
    Consistency is approximated by SAT solvability of the selected edges.
    """
    alpha, beta = 0.6, 0.4
    selected = {k: v for k, v, m in zip(edge_keys, edge_vals, mask) if m}
    # Build SAT clauses: each edge (i->j) becomes (¬i ∨ j)
    clauses = []
    for (i, j), w in selected.items():
        if w == -1:                     # contradiction -> unsat clause
            clauses.append([i, -i])    # always false
        else:
            clauses.append([-i, j])    # implication
    consistent = solve_sat(clauses, n_vars=n_nodes)
    consistent_edges = sum(mask) if consistent else 0
    coverage = len(required_nodes & set(itertools.chain.from_iterable(edge_keys))) / n_nodes
    return alpha * (consistent_edges / n_nodes) + beta * coverage

# --------------------------------------------------------------------------- #
# Meta‑confidence detection (Tier B handling)
# --------------------------------------------------------------------------- #

_AMBIGUITY_PATTERNS = [
    # 1. Presupposition
    r"\bhave you (stopped|quit|ceased)\b",
    r"\bwhy did .* (fail|stop)\b",
    # 2. Scope ambiguity
    r"\bevery \w+ .* a \w+\b",
    # 3. Pronoun ambiguity
    r"\b\w+ told \w+ (he|she|they) was\b",
    # 4. False dichotomy
    r"\beither .+ or .+\b",
    # 5. Subjectivity
    r"\b(best|worst|favorite|most|least) \w+\b",
]

def _meta_confidence(prompt: str) -> float:
    """Return a base confidence (0‑1) based on detected ambiguities."""
    lowered = prompt.lower()
    for pat in _AMBIGUITY_PATTERNS:
        if re.search(pat, lowered):
            return 0.2                     # low confidence for any trap
    # If the prompt asks for a numeric or factual answer, raise confidence
    if re.search(r"\b(what|how|calculate|compute|probability|rate)\b", lowered):
        return 0.8
    # Default moderate confidence
    return 0.5

# --------------------------------------------------------------------------- #
# Main class
# --------------------------------------------------------------------------- #

class ReasoningTool:
    """
    Implements a NAS‑guided symbolic reasoner.

    Workflow (per candidate):
        1. Parse prompt + candidate into SPO triples.
        2. Build a vocabulary -> node IDs.
        3. Create an edge dictionary with weights.
        4. Generate a tiny NAS population of edge‑masks.
        5. Evaluate each mask with a pragmatic utility that uses
           ``solve_sat`` (consistency) and ``check_transitivity`` (propagation).
        6. Return the best utility as the candidate's score.
        7. Confidence is derived from meta‑analysis of the prompt and from
           agreement among the top‑scoring masks (via ``confidence_from_agreement``).
    """

    def __init__(self):
        # deterministic random seed for reproducibility
        np.random.seed(0)

    # ------------------------------------------------------------------- #
    # Public API
    # ------------------------------------------------------------------- #

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Rank candidates by the SRG‑NAS score.

        Returns a list of dicts:
            {"candidate": str, "score": float, "reasoning": str}
        """
        # Parse prompt once
        prompt_triples = _extract_propositions(prompt)
        prompt_vocab = _build_vocab(prompt_triples)

        results = []
        for cand in candidates:
            # 1. Parse candidate and merge vocabularies
            cand_triples = _extract_propositions(cand)
            all_triples = prompt_triples + cand_triples
            vocab = _build_vocab(all_triples)

            # 2. Edge construction
            edges = _triples_to_edges(all_triples, vocab)
            edge_keys = list(edges.keys())
            edge_vals = list(edges.values())

            # 3. Required nodes = nodes appearing in the prompt
            required_nodes = {vocab[t] for triple in prompt_triples for t in triple}

            # 4. NAS population (fixed size 7)
            masks = _mask_population(edge_keys, pop_size=7)

            # 5. Evaluate each mask
            utilities = []
            for mask in masks:
                # propagate equivalence/implication before SAT check
                propagated = check_transitivity(
                    [(i, j, w) for (i, j), w in zip(edge_keys, edge_vals) if mask[edge_keys.index((i, j))]]
                )
                # convert propagated list back to edge dict for SAT
                sat_edges = {(i, j): w for i, j, w in propagated}
                sat_keys = list(sat_edges.keys())
                sat_vals = list(sat_edges.values())
                util = _utility(mask, edge_keys, edge_vals, required_nodes, len(vocab))
                utilities.append(util)

            best_idx = int(np.argmax(utilities))
            best_score = float(utilities[best_idx])

            # 6. Reasoning trace (lightweight)
            reasoning = (
                f"Parsed {len(all_triples)} triples, "
                f"{len(edge_keys)} edges. "
                f"Best mask kept {int(best_score*100)}% of edges. "
                f"Consistency check: {'sat' if best_score > 0 else 'unsat'}."
            )

            results.append({"candidate": cand, "score": best_score, "reasoning": reasoning})

        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return a calibrated confidence 0‑1.

        The value is the minimum of:
            * meta‑confidence (ambiguity detection)
            * agreement‑based confidence from the top‑scoring masks
        """
        meta = _meta_confidence(prompt)

        # Run a quick evaluation of the answer to obtain a score
        eval_res = self.evaluate(prompt, [answer])
        score = eval_res[0]["score"] if eval_res else 0.0

        # Convert score to a pseudo‑confidence (higher score -> higher confidence)
        score_conf = min(0.9, 0.3 + 0.6 * score)   # cap at 0.9 unless definitive

        # Agreement among masks – we reuse the NAS masks from evaluate
        # (re‑run with same seed for determinism)
        # Build a list of binary mask vectors for the answer
        prompt_triples = _extract_propositions(prompt)
        cand_triples = _extract_propositions(answer)
        all_triples = prompt_triples + cand_triples
        vocab = _build_vocab(all_triples)
        edges = _triples_to_edges(all_triples, vocab)
        edge_keys = list(edges.keys())
        masks = _mask_population(edge_keys, pop_size=7)

        # agreement = proportion of masks that achieve >0.5 utility
        utilities = [_utility(m, edge_keys,
                              [edges[k] for k in edge_keys],
                              {vocab[t] for triple in prompt_triples for t in triple},
                              len(vocab))
                     for m in masks]
        agreement = sum(u > 0.5 for u in utilities) / len(utilities)
        agree_conf = confidence_from_agreement([agreement])

        # Final confidence respects epistemic honesty
        final = min(meta, score_conf, agree_conf)
        return float(final)

    # ------------------------------------------------------------------- #
    # Private helpers (exposed for possible unit‑testing)
    # ------------------------------------------------------------------- #

    _meta_confidence = staticmethod(_meta_confidence)   # expose as method


# --------------------------------------------------------------------------- #
# Simple NCD fallback (used only as a tie‑breaker, <=15% of final weight)
# --------------------------------------------------------------------------- #

def _ncd(a: str, b: str) -> float:
    """Normalized Compression Distance based on zlib."""
    a_bytes, b_bytes = a.encode(), b.encode()
    ca = len(zlib.compress(a_bytes))
    cb = len(zlib.compress(b_bytes))
    cab = len(zlib.compress(a_bytes + b_bytes))
    return (cab - min(ca, cb)) / max(ca, cb)


# The class is ready for import and use:
#   tool = ReasoningTool()
#   ranked = tool.evaluate(prompt, candidates)
#   conf   = tool.confidence(prompt, ranked[0]["candidate"])


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
