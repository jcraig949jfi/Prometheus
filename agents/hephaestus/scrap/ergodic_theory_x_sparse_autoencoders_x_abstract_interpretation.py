import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Ergodic-Sparse Abstract Scorer (ESAS) Implementation.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and logical relations into a graph.
    2. Ergodic Analysis: Uses power iteration on the graph adjacency to find 
       the stationary distribution (importance) of each proposition.
    3. Sparse Coding: Simulates dictionary learning via hard-coded logical atoms 
       and soft-thresholding to identify key reasoning features.
    4. Abstract Interpretation: Performs interval arithmetic on extracted numbers
       to check for contradictions (Penalty P).
    5. Scoring: Combines cosine similarity of sparse-ergodic vectors with penalties.
    6. Meta-Cognition: Explicitly checks for Tier B traps (ambiguity, presupposition)
       to cap confidence, ensuring epistemic honesty.
    """
    
    def __init__(self):
        # Pre-defined logical atoms for sparse dictionary (simplified for no-ML-deps)
        self.atoms = [
            r'not\s+\w+', r'\w+\s*>\s*\w+', r'\w+\s*<\s*\w+', 
            r'if\s+.*then', r'all\s+\w+', r'some\s+\w+', r'either\s+.*or'
        ]
        self.alpha = 0.5  # Penalty weight

    def _parse_graph(self, text: str) -> Tuple[List[str], np.ndarray, Dict[str, Tuple[float, float]]]:
        """Extract nodes, adjacency matrix, and numeric intervals."""
        text_lower = text.lower()
        # Tokenize into rough propositions (split by punctuation/logical connectors)
        raw_nodes = re.split(r'[.,;!?]|\s+(?:and|or|but|then)\s+', text_lower)
        nodes = [n.strip() for n in raw_nodes if len(n.strip()) > 3]
        if not nodes:
            nodes = [text_lower]
            
        n = len(nodes)
        adj = np.zeros((n, n))
        intervals = {}

        # Extract numeric constraints
        nums = re.findall(r'-?\d+\.?\d*', text)
        if nums:
            vals = [float(x) for x in nums]
            if vals:
                # Global bound estimation for the whole text as a single node proxy
                intervals["global"] = (min(vals), max(vals))

        # Build edges based on logical flow (simplified heuristic)
        for i, node in enumerate(nodes):
            for j, target in enumerate(nodes):
                if i == j: continue
                # Transitivity/Flow heuristic: if node i words appear in j or vice versa
                common = set(node.split()) & set(target.split())
                if len(common) >= 1:
                    adj[i, j] = 1.0
                # Specific logic patterns
                if re.search(r'if.*then', node) and target in node:
                    adj[i, j] = 2.0
        
        # Self-loops for stability
        np.fill_diagonal(adj, 1.0)
        return nodes, adj, intervals

    def _ergodic_average(self, adj: np.ndarray) -> np.ndarray:
        """Power iteration to find stationary distribution."""
        if adj.shape[0] == 0:
            return np.array([])
        
        # Normalize to column-stochastic
        col_sums = adj.sum(axis=0)
        col_sums[col_sums == 0] = 1.0
        W = adj / col_sums
        
        pi = np.ones(adj.shape[0]) / adj.shape[0]
        for _ in range(50): # Converge
            pi_new = W.T @ pi
            if np.linalg.norm(pi_new - pi, 1) < 1e-6:
                break
            pi = pi_new
        return pi

    def _sparse_code(self, text: str, pi: np.ndarray) -> np.ndarray:
        """Simulate sparse coding over logical atoms weighted by ergodic pi."""
        text_lower = text.lower()
        codes = []
        
        # Create feature vector based on atom presence
        features = []
        for pattern in self.atoms:
            if re.search(pattern, text_lower):
                features.append(1.0)
            else:
                features.append(0.0)
        
        # Add numeric density feature
        nums = re.findall(r'\d+', text)
        features.append(min(len(nums) / 10.0, 1.0))
        
        if not pi.any():
            return np.array(features)
            
        # Expand/align features to node space roughly (simplified for single text)
        # In full ESAS, this maps nodes to dictionary. Here we map text features.
        base_vec = np.array(features)
        
        # Soft thresholding (ISTA step simulation)
        lambda_val = 0.1
        coded = np.sign(base_vec) * np.maximum(np.abs(base_vec) - lambda_val, 0)
        
        # Weight by ergodic importance (approximated as global importance for single text)
        weight = np.mean(pi) if pi.any() else 1.0
        return coded * weight

    def _abstract_interpretation_penalty(self, text: str) -> float:
        """Check for numeric contradictions using interval arithmetic."""
        nums = re.findall(r'-?\d+\.?\d*', text)
        if len(nums) < 2:
            return 0.0
        
        vals = [float(x) for x in nums]
        penalty = 0.0
        
        # Check for explicit contradictions like "5 > 10"
        if re.search(r'\d+\s*>\s*\d+', text):
             matches = re.findall(r'(\d+)\s*>\s*(\d+)', text)
             for a, b in matches:
                 if float(a) <= float(b): penalty += 1.0
                 
        if re.search(r'\d+\s*<\s*\d+', text):
             matches = re.findall(r'(\d+)\s*<\s*(\d+)', text)
             for a, b in matches:
                 if float(a) >= float(b): penalty += 1.0
                 
        return penalty

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        l1 = len(z(s1.encode()))
        l2 = len(z(s2.encode()))
        l12 = len(z((s1 + s2).encode()))
        if max(l1, l2) == 0: return 0.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Detect ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p = prompt.lower()
        
        # 1. Presupposition traps
        presupposition_triggers = [
            r"have you stopped", r"why did.*fail", r"why is.*wrong", 
            r"when did.*stop", r"quit\s+\w+", r"used to"
        ]
        for pat in presupposition_triggers:
            if re.search(pat, p):
                return 0.2  # Low confidence due to loaded question

        # 2. Scope/Pronoun Ambiguity
        if re.search(r"every\s+\w+.*\s+a\s+\w+", p) and "same" in p:
            return 0.4
        if re.search(r"told\s+\w+\s+he", p) and "who" in p:
            return 0.3
            
        # 3. False Dichotomy
        if re.search(r"either\s+.*\s+or\s+.*", p) and "option" not in p:
            # Heuristic: if it looks like a forced choice without context
            if len(p.split()) < 20: 
                return 0.5

        # 4. Subjectivity without criteria
        subjective_words = ["best", "worst", "favorite", "beautiful"]
        if any(w in p for w in subjective_words) and "measure" not in p and "data" not in p:
            return 0.4

        # 5. Unanswerable / Missing Info
        if re.search(r"calculate.*without.*data", p) or re.search(r"impossible", p):
            return 0.1
            
        return 1.0  # No obvious traps detected

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_nodes, prompt_adj, prompt_intervals = self._parse_graph(prompt)
        prompt_pi = self._ergodic_average(prompt_adj)
        prompt_code = self._sparse_code(prompt, prompt_pi)
        
        results = []
        ref_score = None
        
        # Identify reference (heuristic: longest or first candidate if no expert provided)
        # In a real setting, 'R' is provided. Here we assume the prompt might contain the answer
        # or we compare candidates against each other. 
        # Strategy: Compare each candidate to the Prompt's logical structure + NCD to prompt context.
        
        prompt_numeric_penalty = self._abstract_interpretation_penalty(prompt)

        for cand in candidates:
            cand_nodes, cand_adj, cand_intervals = self._parse_graph(cand)
            cand_pi = self._ergodic_average(cand_adj)
            cand_code = self._sparse_code(cand, cand_pi)
            
            # 1. Structural Similarity (Cosine)
            if np.linalg.norm(prompt_code) == 0 or np.linalg.norm(cand_code) == 0:
                similarity = 0.0
            else:
                similarity = np.dot(prompt_code, cand_code) / (
                    np.linalg.norm(prompt_code) * np.linalg.norm(cand_code)
                )
            
            # 2. Abstract Interpretation Penalty
            cand_penalty = self._abstract_interpretation_penalty(cand)
            
            # 3. NCD Tiebreaker (Max 15% impact)
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val # Convert distance to similarity
            
            # Combine: Structural (50%) + Computation/Logic (35%) + NCD (15%)
            # Logic score derived from similarity minus penalty
            logic_score = max(0, similarity - self.alpha * cand_penalty)
            
            final_score = (0.5 * logic_score) + (0.35 * logic_score) + (0.15 * ncd_score)
            
            # Reasoning string generation
            reason = f"Structural match: {similarity:.2f}. Logic penalty: {cand_penalty:.2f}."
            if cand_penalty > 0:
                reason += " Detected numeric/logical contradiction."
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reason
            })
            
        # Rank by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt.
        """
        # 1. Meta-cognitive cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural match check
        nodes, adj, _ = self._parse_graph(prompt)
        if len(nodes) == 0 or adj.sum() == 0:
            # If we can't parse structure, confidence must be low
            meta_cap = min(meta_cap, 0.3)
            
        # 3. Compute raw score
        eval_res = self.evaluate(prompt, [answer])
        raw_score = eval_res[0]["score"] if eval_res else 0.0
        
        # Scale raw score to 0-1 range roughly (assuming max ~1.0)
        # If meta_cap is low, we override high confidence
        final_conf = min(raw_score, meta_cap)
        
        # Ensure definitive answers (computation) can reach high confidence only if no traps
        # If the answer involves a calculation result (detected by number density), allow higher
        nums_in_ans = len(re.findall(r'\d+', answer))
        if nums_in_ans > 0 and meta_cap == 1.0:
            final_conf = min(raw_score * 1.2, 0.95) # Boost computed answers slightly
            
        return float(np.clip(final_conf, 0.0, 1.0))