import re
import math
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Implements a reasoning engine combining Information Theory, Neural Oscillations (via 
    cross-frequency coupling of logical features), and Multi-Armed Bandits (UCB selection).
    
    Mechanism:
    1. Structural Parsing: Extracts logical propositions (negations, comparatives, conditionals).
    2. Constraint Graph: Builds a directed graph of implications and checks consistency.
    3. Feature Banding: Computes 'Low-freq' (global coherence) and 'High-freq' (local detail) 
       scores. Their product mimics neural phase-amplitude coupling.
    4. Information Scoring: Estimates Mutual Information between answer propositions and 
       prompt constraints.
    5. Bandit Selection: Uses UCB to rank candidates, favoring high information gain with 
       exploration bonus for robustness.
    """

    def __init__(self):
        self.alpha = 1.5  # Exploration constant for UCB
        self.total_evals = 0
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|cannot)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads? to|causes?)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(before|after|first|last|next|previous)\b', re.IGNORECASE),
            'number': re.compile(r'-?\d+\.?\d*')
        }

    def _extract_props(self, text: str) -> List[Tuple[str, Any, Any, bool]]:
        """Extracts atomic propositions as (type, arg1, arg2, polarity)."""
        props = []
        text_lower = text.lower()
        
        # Extract numbers for comparison logic
        nums = [float(n) for n in self.patterns['number'].findall(text)]
        if len(nums) >= 2:
            # Simple heuristic: assume order implies relation if comparatives present
            if any(self.patterns['comparative'].findall(text)):
                props.append(('comparative', nums[0], nums[1], True))
        
        # Extract logical markers
        if self.patterns['negation'].search(text_lower):
            props.append(('negation', 'global', None, False))
        if self.patterns['conditional'].search(text_lower):
            props.append(('conditional', 'global', None, True))
        if self.patterns['causal'].search(text_lower):
            props.append(('causal', 'global', None, True))
        if self.patterns['ordering'].search(text_lower):
            props.append(('ordering', 'global', None, True))
            
        return props

    def _build_graph_and_propagate(self, prompt_props: List, answer_props: List) -> Tuple[int, int, bool]:
        """
        Simulates constraint propagation.
        Returns: (num_nodes, num_edges, has_cycle)
        """
        # Simplified graph model: Nodes are proposition types, edges imply logical flow
        # In a full engine, this would be symbolic. Here we use counts as proxies for graph density.
        all_props = prompt_props + answer_props
        nodes = set(p[0] for p in all_props)
        num_nodes = len(nodes) if nodes else 1
        
        # Estimate edges based on co-occurrence (transitivity proxy)
        num_edges = len(all_props) * (len(all_props) - 1) // 2 if len(all_props) > 1 else 0
        
        # Cycle detection heuristic: Contradictory negations
        has_cycle = False
        negations = [p for p in all_props if p[0] == 'negation']
        if len(negations) > 1:
            # If multiple global negations exist without clear scope, assume potential conflict
            has_cycle = True
            
        return num_nodes, num_edges, has_cycle

    def _compute_features(self, prompt: str, candidate: str) -> Tuple[float, float, float]:
        """Computes Low-freq (global) and High-freq (local) features and their coupling."""
        p_props = self._extract_props(prompt)
        c_props = self._extract_props(candidate)
        
        # Graph metrics
        n_nodes, n_edges, has_cycle = self._build_graph_and_propagate(p_props, c_props)
        
        # Low-frequency: Global structural coherence (normalized)
        # Penalize cycles, reward connectivity
        low_score = (n_edges + 1) / (n_nodes + 10) 
        if has_cycle:
            low_score *= 0.5
        low_score = min(1.0, low_score)
        
        # High-frequency: Local lexical density
        # Density of specific logical markers in the candidate relative to prompt
        h_count = sum(1 for p in c_props if p[0] in ['comparative', 'number', 'causal'])
        high_score = min(1.0, h_count / 5.0) # Normalize by expected max density
        
        # Cross-frequency coupling (Phase-Amplitude analogue)
        coupling = low_score * high_score
        
        return low_score, high_score, coupling

    def _compute_mutual_information(self, prompt: str, candidate: str) -> float:
        """
        Estimates I(Candidate; Prompt Constraints).
        Approximated by the overlap of structural features and consistency.
        """
        p_props = self._extract_props(prompt)
        c_props = self._extract_props(candidate)
        
        if not p_props or not c_props:
            return 0.0
            
        # Joint probability approximation based on feature matching
        # Count how many prompt constraints are satisfied/mirrored in candidate
        matches = 0
        total_prompt_features = len(p_props)
        
        for pp in p_props:
            for cp in c_props:
                # Check type match and polarity consistency
                if pp[0] == cp[0]:
                    if pp[0] == 'negation':
                        # Negation in prompt should ideally be handled, not necessarily repeated
                        matches += 0.5 
                    else:
                        matches += 1.0
                # Numeric consistency check
                if pp[0] == 'comparative' and cp[0] == 'comparative':
                    if pp[2] == cp[2]: # Compare values if available
                        matches += 1.0

        # Normalize to probability space
        p_c = (matches + 1) / (total_prompt_features * len(c_props) + 2)
        p_p = 0.5 # Prior assumption
        p_joint = p_c 
        
        # MI = sum p(x,y) log (p(x,y) / p(x)p(y))
        if p_joint > 0 and p_p > 0 and p_c > 0:
            mi = p_joint * math.log2(p_joint / (p_p * p_c + 1e-9) + 1e-9)
            return max(0.0, mi)
        return 0.0

    def _ucb_score(self, mi: float, n_i: int, N: int) -> float:
        """Calculates Upper Confidence Bound."""
        if n_i == 0:
            return float('inf')
        exploration = self.alpha * math.sqrt(math.log(N + 1) / n_i)
        return mi + exploration

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []
            
        self.total_evals += 1
        N = self.total_evals
        results = []
        
        # Storage for bandit updates
        candidate_stats = {} 

        for i, cand in enumerate(candidates):
            # 1. Feature Banding
            f_low, f_high, coupling = self._compute_features(prompt, cand)
            
            # 2. Information Theoretic Score
            mi = self._compute_mutual_information(prompt, cand)
            
            # Weight MI by coupling (neural oscillation analogy)
            # High MI only counts if structural coherence (coupling) is present
            weighted_mi = mi * (0.5 + 0.5 * coupling)
            
            # 3. Bandit Update
            n_i = 1 # Treat each evaluation in this batch as first for simplicity in single-shot
            ucb = self._ucb_score(weighted_mi, n_i, N)
            
            # Fallback to NCD if structural signal is too weak (Tiebreaker logic)
            structural_signal = f_low + f_high + weighted_mi
            if structural_signal < 0.01:
                # Minimal NCD implementation for tie-breaking
                try:
                    import zlib
                    data = (prompt + cand).encode('utf-8')
                    comp = len(zlib.compress(data))
                    norm = comp / (len(data) + 1)
                    weighted_mi = max(weighted_mi, 0.01 * (1.0 - norm))
                except:
                    pass

            results.append({
                "candidate": cand,
                "score": ucb,
                "reasoning": f"Low-freq:{f_low:.2f}, High-freq:{f_high:.2f}, Coupling:{coupling:.2f}, MI:{weighted_mi:.4f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural consistency and MI."""
        f_low, f_high, coupling = self._compute_features(prompt, answer)
        mi = self._compute_mutual_information(prompt, answer)
        
        # Base confidence on coupling and MI
        raw_conf = (f_low * 0.4 + f_high * 0.3 + mi * 0.3)
        
        # Clamp to [0, 1]
        return min(1.0, max(0.0, raw_conf))