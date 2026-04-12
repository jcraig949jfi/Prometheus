import re
import math
import numpy as np
from typing import List, Dict, Tuple, Any
from scipy.optimize import linear_sum_assignment

# --- Helper Functions for Parsing and Logic ---

def _extract_triples(text: str) -> List[Tuple[str, str, str, str]]:
    """
    Extracts elementary propositions (subject, predicate, object, relation_type).
    Handles negations, comparatives, conditionals, causals, and equivalence.
    """
    text = text.lower()
    triples = []
    words = text.split()
    
    # Simple tokenization for context
    full_text = " " + text + " "
    
    # Patterns
    patterns = [
        # Negation: "not X", "no X"
        (r'\b(not|no)\s+(\w+)\s+(\w+)', lambda m: (m.group(2), 'neg', m.group(3), 'NEG')),
        # Comparatives
        (r'\b(more|less|greater|smaller|higher|lower)\s+than\s+(\w+)', lambda m: (m.group(1), 'cmp', m.group(2), 'CMP')),
        (r'\b(\w+)\s+is\s+(more|less|greater|smaller)\s+than\s+(\w+)', lambda m: (m.group(1), 'cmp', m.group(3), 'CMP')),
        # Conditionals
        (r'\bif\s+(\w+).*?then\s+(\w+)', lambda m: (m.group(1), 'cond', m.group(2), 'COND')),
        # Causals
        (r'\b(\w+)\s+(leads to|causes|because)\s+(\w+)', lambda m: (m.group(1), 'cause', m.group(3), 'CAUS')),
        # Equivalence
        (r'\b(\w+)\s+is the same as\s+(\w+)', lambda m: (m.group(1), 'eq', m.group(2), 'EQ')),
        (r'\b(\w+)\s+=\s+(\w+)', lambda m: (m.group(1), 'eq', m.group(2), 'EQ')),
        # Generic Subject-Predicate-Object (heuristic: Noun-Verb-Noun)
        (r'\b(\w+)\s+(is|has|does|eats|loves|hates|kills|saves)\s+(\w+)', lambda m: (m.group(1), m.group(2), m.group(3), 'GEN')),
    ]
    
    found_relations = set()
    
    for pattern, extractor in patterns:
        for match in re.finditer(pattern, text):
            try:
                s, p, o, r_type = extractor(match)
                key = (s, p, o, r_type)
                if key not in found_relations:
                    triples.append(key)
                    found_relations.add(key)
            except:
                continue
                
    # Fallback for simple numeric comparisons if not caught
    num_match = re.search(r'(\d+\.?\d*)\s*([<>=!]+)\s*(\d+\.?\d*)', text)
    if num_match:
        v1, op, v2 = num_match.groups()
        triples.append((v1, op, v2, 'NUM_CMP'))

    return triples if triples else [(text, 'is', 'unknown', 'GEN')]

def _build_graph(triples: List[Tuple]) -> Tuple[List[str], np.ndarray, List[str]]:
    """Builds adjacency tensor and node list from triples."""
    nodes = list(set([t[0] for t in triples] + [t[2] for t in triples]))
    node_map = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    
    # Relation types mapping
    rel_types = ['NEG', 'CMP', 'COND', 'CAUS', 'EQ', 'GEN', 'NUM_CMP']
    r = len(rel_types)
    
    # Adjacency tensor A[i, j, k] = 1 if edge i->j has relation k
    A = np.zeros((n, n, r), dtype=np.float32)
    
    for s, p, o, r_type in triples:
        if s in node_map and o in node_map:
            i, j = node_map[s], node_map[o]
            try:
                k = rel_types.index(r_type)
                A[i, j, k] = 1.0
            except ValueError:
                A[i, j, rel_types.index('GEN')] = 1.0
                
    # Node features (one-hot for predicate types present on outgoing edges)
    # Simplified: count outgoing relation types
    X = np.zeros((n, r), dtype=np.float32)
    for i in range(n):
        # Sum over outgoing edges and relation types
        outgoing = A[i, :, :]
        if outgoing.sum() > 0:
            # Normalize to get feature vector
            X[i, :] = outgoing.sum(axis=0)
            if X[i, :].sum() > 0:
                X[i, :] /= X[i, :].sum()
                
    return nodes, A, X, rel_types

def _renormalize(A: np.ndarray, X: np.ndarray, steps: int = 5) -> np.ndarray:
    """
    Renormalization step: Coarse-graining via fixed-point iteration.
    X_{t+1} = ReLU(A_aggregated * X_t)
    """
    # Aggregate adjacency over relation types for smoothing
    A_agg = A.sum(axis=2)
    # Normalize rows to prevent explosion (simple row-normalization)
    row_sums = A_agg.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1.0
    A_norm = A_agg / row_sums
    
    X_curr = X.copy()
    for _ in range(steps):
        # Message passing: X_new = A * X
        X_next = np.dot(A_norm, X_curr)
        # Non-linearity
        X_next = np.maximum(0, X_next) # ReLU
        # Convergence check could go here, skipping for brevity/speed
        X_curr = X_next
        
    return X_curr

def _compute_cognitive_load(nodes_v: int, edges_v: int, matched_edges: int) -> Tuple[float, float, float]:
    """Calculates Intrinsic, Extraneous, and Germane load."""
    I = math.log2(max(1, nodes_v))
    G = matched_edges
    E = max(0, edges_v - matched_edges)
    return I, E, G

def _meta_confidence(prompt: str) -> float:
    """
    Tier B Reasoning: Detects ambiguity, presupposition, and unanswerability.
    Returns a cap on confidence (0.0 to 1.0).
    """
    p = prompt.lower()
    
    # 1. Presupposition traps
    presupp_patterns = [
        r"have you stopped", r"why did.*fail", r"why did.*stop", 
        r"when did.*stop", r"is it true that.*stopped"
    ]
    for pat in presupp_patterns:
        if re.search(pat, p):
            return 0.2

    # 2. Scope/Pronoun Ambiguity
    if re.search(r"every.*a.*y", p) and "same" not in p:
        # Heuristic for "Every X did a Y" ambiguity
        if "who" in p or "which" in p:
            return 0.3
            
    if re.search(r"\bhe\b.*\bshe\b", p) and "who" in p:
        return 0.3
        
    # 3. False Dichotomy
    if re.search(r"either.*or", p) and "only" not in p:
        # Check if options are exhaustive (hard to detect, assume ambiguous)
        if "choice" in p or "option" in p:
            return 0.4

    # 4. Subjectivity
    subj_words = ["best", "worst", "favorite", "beautiful", "ugly", "moral"]
    if any(w in p for w in subj_words):
        if "calculate" not in p and "math" not in p:
            return 0.4

    # 5. Unanswerable / Missing Info
    if "cannot be determined" in p or "not enough information" in p:
        return 0.9 # High confidence that it's unanswerable if prompt says so
        
    return 1.0

class ReasoningTool:
    def __init__(self):
        self.alpha = 0.5
        self.beta = 0.3
        self.gamma = 0.2

    def _parse_and_graph(self, text: str):
        triples = _extract_triples(text)
        nodes, A, X, rel_types = _build_graph(triples)
        return nodes, A, X, len(triples), rel_types

    def _functorial_align(self, A_pred: np.ndarray, A_gold: np.ndarray) -> Tuple[int, float]:
        """
        Aligns graphs using Hungarian algorithm on relation preservation.
        Returns matched edge count and structural similarity.
        """
        n_pred = A_pred.shape[0]
        n_gold = A_gold.shape[0]
        
        if n_pred == 0 or n_gold == 0:
            return 0, 0.0
            
        # Flatten adjacency to compare structures
        # We need a cost matrix C[i, j] = cost of mapping node i (pred) to node j (gold)
        # Cost = negative similarity of their connection profiles
        
        # Flatten A to (N, R*N) for comparison? Too big.
        # Simplified: Compare degree profiles and relation counts
        pred_profile = A_pred.sum(axis=(0, 1)) # Total per relation type
        gold_profile = A_gold.sum(axis=(0, 1))
        
        # Since Hungarian needs square matrix, we pad
        n = max(n_pred, n_gold)
        cost = np.zeros((n, n))
        
        # Heuristic cost: Difference in total relation counts if we map i->j
        # This is a simplification of the full tensor alignment
        for i in range(n_pred):
            for j in range(n_gold):
                # Compare row i of pred with row j of gold (padded)
                row_p = A_pred[i, :, :].flatten()
                row_g = A_gold[j, :, :].flatten()
                
                # Pad to max length
                len_p, len_g = len(row_p), len(row_g)
                if len_p < len_g:
                    row_p = np.pad(row_p, (0, len_g - len_p))
                elif len_g < len_p:
                    row_g = np.pad(row_g, (0, len_p - len_g))
                    
                # Cosine distance as cost
                norm_p = np.linalg.norm(row_p)
                norm_g = np.linalg.norm(row_g)
                if norm_p == 0 or norm_g == 0:
                    cost[i, j] = 1.0
                else:
                    sim = np.dot(row_p, row_g) / (norm_p * norm_g)
                    cost[i, j] = 1.0 - sim
        
        # Pad remaining rows/cols with high cost (or 0 if dummy)
        # For simplicity in this constrained env, we assume small graphs or use min(n_pred, n_gold)
        size = min(n_pred, n_gold)
        if size == 0: return 0, 0.0
        
        sub_cost = cost[:size, :size]
        row_ind, col_ind = linear_sum_assignment(sub_cost)
        
        # Calculate matched edges based on assignment
        matched = 0
        total_possible = 0
        
        for i, j in zip(row_ind, col_ind):
            # Check how many relations match exactly between node i and j
            # Simplified: count non-zero overlaps in adjacency slices
            slice_p = A_pred[i, :, :]
            slice_g = A_gold[j, :, :]
            # Intersect
            inter = np.minimum(slice_p, slice_g).sum()
            matched += int(inter > 0)
            total_possible += 1
            
        return matched, (matched / max(1, total_possible))

    def _compute_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        # 1. Parse Prompt and Candidate
        nodes_p, A_p, X_p, edges_p, _ = self._parse_and_graph(prompt)
        nodes_c, A_c, X_c, edges_c, _ = self._parse_and_graph(candidate)
        
        if len(nodes_p) == 0:
            return 0.0, "No structure parsed."

        # 2. Functorial Alignment
        matched_count, struct_sim = self._functorial_align(A_p, A_c)
        
        # 3. Renormalization (Fixed Point)
        X_p_star = _renormalize(A_p, X_p)
        X_c_star = _renormalize(A_c, X_c)
        
        # Similarity of fixed points (mean cosine)
        if X_p_star.shape[0] > 0 and X_c_star.shape[0] > 0:
            # Flatten and compare
            vec_p = X_p_star.flatten()
            vec_c = X_c_star.flatten()
            # Pad to match
            if len(vec_p) < len(vec_c):
                vec_p = np.pad(vec_p, (0, len(vec_c) - len(vec_p)))
            elif len(vec_c) < len(vec_p):
                vec_c = np.pad(vec_c, (0, len(vec_p) - len(vec_c)))
            
            norm_p = np.linalg.norm(vec_p)
            norm_c = np.linalg.norm(vec_c)
            if norm_p > 0 and norm_c > 0:
                S = np.dot(vec_p, vec_c) / (norm_p * norm_c)
            else:
                S = 0.0
        else:
            S = 0.0

        # 4. Cognitive Load
        I, E, G = _compute_cognitive_load(len(nodes_c), edges_c, matched_count)
        total_load = I + E + G
        if total_load == 0: total_load = 1
        
        germane_ratio = G / total_load
        extraneous_ratio = E / (I + E) if (I+E) > 0 else 0
        
        # Final Score Formula
        score = self.alpha * S + self.beta * germane_ratio - self.gamma * extraneous_ratio
        
        # Normalize to [-1, 1] roughly
        score = max(-1.0, min(1.0, score))
        
        reason = f"Structural Sim: {struct_sim:.2f}, FixedPoint Sim: {S:.2f}, Load Penalty: {extraneous_ratio:.2f}"
        return score, reason

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        meta_cap = _meta_confidence(prompt)
        
        for cand in candidates:
            score, reason = self._compute_score(prompt, cand)
            
            # Apply meta-confidence cap
            if meta_cap < 0.5:
                score = score * meta_cap # Dampen score if ambiguous
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reason
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt (Tier B).
        """
        meta_cap = _meta_confidence(prompt)
        
        # If meta-analysis says ambiguous, return low confidence immediately
        if meta_cap < 0.5:
            return meta_cap
            
        # Otherwise, compute structural alignment score
        score, _ = self._compute_score(prompt, answer)
        
        # Map score [-1, 1] to [0, 1]
        conf = (score + 1.0) / 2.0
        
        # Hard cap by meta-confidence
        final_conf = min(conf, meta_cap)
        
        # Never overconfident unless computation was perfect
        if score < 0.9:
            final_conf = min(final_conf, 0.85)
            
        return float(np.clip(final_conf, 0.0, 1.0))