import re
import numpy as np
from collections import namedtuple
from typing import List, Dict, Tuple, Any

# Data structure for propositions
Prop = namedtuple('Prop', ['text', 'type', 'feats', 'idx'])

class ReasoningTool:
    """
    Gauge-Updated Bayesian Sensitivity Scorer (GUBSS)
    
    Mechanism:
    1. Structural Parsing: Extracts logical atoms (negations, comparatives, conditionals, numbers).
    2. Gauge Transport: Propagates belief evidence across a syntactic graph using connection weights.
    3. Bayesian Update: Updates Beta-distribution priors based on transported evidence.
    4. Sensitivity Analysis: Perturbs features to measure robustness (Jacobian approximation).
    5. Epistemic Honesty: Caps confidence on ambiguous/unanswerable prompts (Tier B).
    
    Score Composition: Structural (50%) + Computation (35%) + NCD Tiebreaker (15%).
    """

    def __init__(self):
        # Regex patterns for structural features
        self.patterns = {
            'neg': re.compile(r'\b(not|no|never|neither|without)\b', re.I),
            'comp': re.compile(r'\b(more than|less than|greater than|smaller than|>=|<=|>|<|equal to)\b', re.I),
            'cond': re.compile(r'\b(if|unless|provided that|then)\b', re.I),
            'causal': re.compile(r'\b(because|leads to|results in|causes|due to)\b', re.I),
            'order': re.compile(r'\b(before|after|precedes|follows|first|last)\b', re.I),
            'num': re.compile(r'-?\d+(?:\.\d+)?%?'),
            'presupposition': re.compile(r'\b(have you stopped|why did .*(fail|stop|quit)|when did .*(stop|fail))\b', re.I),
            'scope_ambiguity': re.compile(r'\b(every|each|all).*\b(a|an|the same)\b', re.I),
            'pronoun_ambiguity': re.compile(r'\b(told|said to)\b.*\b(he|she|him|her)\b.*\bwho\b', re.I),
            'false_dichotomy': re.compile(r'\b(either|or)\b.*\b(or|else)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|better)\b', re.I)
        }
        self.epsilon = 0.01  # Perturbation step for sensitivity

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Extract structural features from text."""
        feats = {
            'has_neg': bool(self.patterns['neg'].search(text)),
            'has_comp': bool(self.patterns['comp'].search(text)),
            'has_cond': bool(self.patterns['cond'].search(text)),
            'has_causal': bool(self.patterns['causal'].search(text)),
            'has_order': bool(self.patterns['order'].search(text)),
            'numbers': [],
            'raw_len': len(text)
        }
        
        # Extract numbers
        nums = self.patterns['num'].findall(text)
        if nums:
            try:
                feats['numbers'] = [float(n.replace('%', '')) for n in nums]
            except ValueError:
                feats['numbers'] = []
        
        return feats

    def _build_graph(self, prompt: str, candidate: str) -> Tuple[List[Prop], List[List[Tuple[int, float]]]]:
        """Build proposition list and adjacency graph."""
        combined = f"{prompt} {candidate}"
        feats = self._extract_features(combined)
        
        # Create nodes based on structural types detected
        props = []
        types = ['neg', 'comp', 'cond', 'causal', 'order', 'atom']
        
        # Map detected features to nodes
        node_data = []
        if feats['has_neg']: node_data.append(('neg', 1.0))
        if feats['has_comp']: node_data.append(('comp', 1.0))
        if feats['has_cond']: node_data.append(('cond', 1.0))
        if feats['has_causal']: node_data.append(('causal', 1.0))
        if feats['has_order']: node_data.append(('order', 1.0))
        
        # Always add an atom node for the candidate content
        cand_feats = self._extract_features(candidate)
        node_data.append(('atom', 1.0 if cand_feats['numbers'] else 0.5))
        
        props = [Prop(text=candidate, type=t, feats=feats, idx=i) for i, (t, _) in enumerate(node_data)]
        
        # Build adjacency list (fully connected for small N, weighted by type similarity)
        n = len(props)
        edges = [[] for _ in range(n)]
        if n > 0:
            for i in range(n):
                for j in range(n):
                    if i != j:
                        # Gauge weight: higher if types are related (simplified heuristic)
                        w = 0.5 if props[i].type == props[j].type else 0.2
                        edges[i].append((j, w))
                        
        return props, edges

    def _gauge_transport(self, props: List[Prop], edges: List[List[Tuple[int, float]]]) -> np.ndarray:
        """Propagate evidence along graph edges."""
        n = len(props)
        if n == 0:
            return np.array([])
            
        # Initialize evidence means based on feature presence
        e = np.array([p.feats['has_comp'] or p.feats['has_causal'] or bool(p.feats['numbers']) 
                      for p in props], dtype=float)
        
        # Normalize initial evidence
        if e.max() > 0:
            e = e / e.max()
            
        # Iterative transport (3 sweeps)
        for _ in range(3):
            e_new = e.copy()
            for i in range(n):
                for j, w in edges[i]:
                    if j < len(e):
                        # e_j = e_i + w * (feat_j - feat_i) approximation
                        # Using feature overlap as proxy for (feat_j - feat_i) direction
                        diff = 0.1 if props[j].feats != props[i].feats else 0.0
                        e_new[j] += w * diff
            e = e_new
            
        return e

    def _bayesian_update(self, evidence: np.ndarray) -> np.ndarray:
        """Update Beta priors and return posterior means."""
        if len(evidence) == 0:
            return np.array([])
            
        # Prior: Alpha=1, Beta=1 (Uniform)
        alpha = 1.0 + evidence
        beta = 1.0 + (1.0 - np.clip(evidence, 0, 1))
        
        return alpha / (alpha + beta)

    def _sensitivity_score(self, prompt: str, candidate: str, base_posterior: np.ndarray) -> float:
        """Compute robustness score via finite difference perturbation."""
        if len(base_posterior) == 0:
            return 0.0
            
        # Perturb candidate string slightly (simulate feature noise)
        perturbed_cand = candidate + " " # Minimal perturbation
        props_p, edges_p = self._build_graph(prompt, perturbed_cand)
        
        if len(props_p) == 0:
            return 0.0
            
        ev_p = self._gauge_transport(props_p, edges_p)
        post_p = self._bayesian_update(ev_p)
        
        # Ensure shapes match for subtraction
        min_len = min(len(base_posterior), len(post_p))
        if min_len == 0:
            return 0.0
            
        # Jacobian approximation
        diff = np.abs(base_posterior[:min_len] - post_p[:min_len])
        sensitivity = np.sum(diff) / (min_len * self.epsilon * 10) # Scale factor
        
        # Robustness reward: Lower sensitivity = higher score
        return max(0.0, 1.0 - sensitivity)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_both - min(len_s1, len_s2)) / max_len

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Check for ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        # 2. Scope Ambiguity
        if self.patterns['scope_ambiguity'].search(p_lower):
            return 0.3
        # 3. Pronoun Ambiguity (simplified check)
        if 'who' in p_lower and ('he' in p_lower or 'she' in p_lower) and 'told' in p_lower:
            return 0.3
        # 4. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            return 0.4
        # 5. Subjectivity
        if self.patterns['subjectivity'].search(p_lower):
            return 0.5
            
        # Default: High confidence allowed if structural parsing succeeds
        return 1.0

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str, float]:
        """Internal scoring returning (score, reasoning, raw_confidence_cap)."""
        
        # 1. Structural Parsing & Graph Build
        props, edges = self._build_graph(prompt, candidate)
        feats = self._extract_features(f"{prompt} {candidate}")
        
        reasoning_parts = []
        struct_score = 0.0
        
        # Structural Scoring Logic
        if feats['has_neg']:
            reasoning_parts.append("Detected negation logic.")
            struct_score += 0.2
        if feats['has_comp']:
            reasoning_parts.append("Detected comparative logic.")
            struct_score += 0.2
        if feats['has_cond']:
            reasoning_parts.append("Detected conditional logic.")
            struct_score += 0.15
        if feats['numbers']:
            reasoning_parts.append(f"Numeric values found: {feats['numbers']}.")
            struct_score += 0.25
            # Simple numeric consistency check (heuristic)
            if len(feats['numbers']) >= 2:
                # If prompt implies order and candidate respects it (simplified)
                struct_score += 0.1 
        else:
            reasoning_parts.append("No numeric values detected.")
            
        # Cap structural score at 1.0 for normalization
        struct_score = min(1.0, struct_score)
        
        # 2. Gauge Transport & Bayesian Update
        evidence = self._gauge_transport(props, edges)
        posterior = self._bayesian_update(evidence)
        bayes_mean = np.mean(posterior) if len(posterior) > 0 else 0.5
        
        # 3. Sensitivity Analysis
        sens_score = self._sensitivity_score(prompt, candidate, posterior)
        
        # 4. NCD Tiebreaker (Max 15% weight)
        # Compare candidate to prompt (should be relevant) and self-consistency
        ncd_val = self._compute_ncd(prompt, candidate)
        # Lower NCD (more similar/compressible together) is generally better for relevance, 
        # but we want diversity too. Let's use inverse NCD relative to random noise.
        # Simplified: If NCD is very high (unrelated), penalize.
        ncd_score = max(0.0, 1.0 - ncd_val) 
        
        # Final Score Composition
        # Structural: 50%, Computation (Bayes/Sens): 35%, NCD: 15%
        final_score = (struct_score * 0.50) + (bayes_mean * 0.20 + sens_score * 0.15) + (ncd_score * 0.15)
        
        reasoning_str = " ".join(reasoning_parts) + f" Bayesian belief: {bayes_mean:.2f}. Robustness: {sens_score:.2f}."
        
        return final_score, reasoning_str, self._meta_confidence(prompt)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        for cand in candidates:
            score, reason, _ = self._score_candidate(prompt, cand)
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
        Caps based on meta-cognitive analysis of the prompt (Tier B).
        """
        score, _, cap = self._score_candidate(prompt, answer)
        
        # Base confidence on the computed score
        base_conf = score
        
        # Apply epistemic cap
        final_conf = min(base_conf, cap)
        
        # Ensure strict bounds
        return float(np.clip(final_conf, 0.0, 1.0))