import numpy as np
import re
from typing import List, Dict, Any

class ReasoningTool:
    """
    Thermodynamic-NAS Pragmatic Reasoner.
    
    Mechanism:
    1. Parses logical predicates (Negation, Comparatives, Causality) from text.
    2. Represents interpretations as states with energy fields (Truth, Info, Rel, Manner).
    3. Uses a greedy NAS-inspired search to minimize 'Energy' (maximize pragmatic satisfaction).
    4. Scores candidates based on equilibrium energy (-E), using NCD only as a tiebreaker.
    """
    
    def __init__(self):
        self.weights = {'truth': 0.4, 'info': 0.3, 'rel': 0.2, 'mann': 0.1}
        self.ops = ['neg_flip', 'comp_tighten', 'causal_chain', 'qty_share']

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Extract structural logical features from text."""
        t_lower = text.lower()
        features = {
            'has_neg': bool(re.search(r'\b(not|no|never|none|without)\b', t_lower)),
            'has_comp': bool(re.search(r'\b(more|less|greater|smaller|before|after)\b', t_lower)),
            'has_cause': bool(re.search(r'\b(because|therefore|leads to|if.*then|causes)\b', t_lower)),
            'numbers': [float(n) for n in re.findall(r'-?\d+\.?\d*', t_lower)]
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as a fallback metric."""
        import zlib
        s1_b, s2_b = s1.encode(), s2.encode()
        c1, c2 = len(zlib.compress(s1_b)), len(zlib.compress(s2_b))
        c12 = len(zlib.compress(s1_b + s2_b))
        if max(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def _init_state(self, prompt_feats: Dict, cand_feats: Dict) -> np.ndarray:
        """Initialize state array [E_truth, E_info, E_rel, E_mann]."""
        # Heuristic initialization based on feature overlap
        t_match = 0.5
        if prompt_feats['has_neg'] == cand_feats['has_neg']: t_match = 0.8
        elif prompt_feats['has_neg'] != cand_feats['has_neg']: t_match = 0.2
        
        # Info: proportion of numeric constraints matched
        i_score = 0.5
        if prompt_feats['numbers'] and cand_feats['numbers']:
            # Simple check if candidate numbers satisfy prompt logic (simplified)
            i_score = 0.9 if len(cand_feats['numbers']) >= len(prompt_feats['numbers']) else 0.4
            
        return np.array([t_match, i_score, 0.7, 0.2]) # Start with low manner penalty

    def _energy(self, state: np.ndarray) -> float:
        """Calculate thermodynamic energy. Lower is better."""
        w = self.weights
        # E = w_truth*(1-E_truth) + w_info*(1-E_info) + w_rel*(1-E_rel) + w_mann*E_mann
        return (w['truth'] * (1 - state[0]) +
                w['info'] * (1 - state[1]) +
                w['rel'] * (1 - state[2]) +
                w['mann'] * state[3])

    def _search_equilibrium(self, prompt: str, candidate: str) -> float:
        """Run greedy descent to find minimum energy state."""
        p_feats = self._extract_features(prompt)
        c_feats = self._extract_features(candidate)
        
        state = self._init_state(p_feats, c_feats)
        best_energy = self._energy(state)
        
        # NAS-inspired operator search loop
        improved = True
        iterations = 0
        while improved and iterations < 5:
            improved = False
            iterations += 1
            
            # Generate neighbors via operators
            neighbors = []
            
            # 1. Negation Flip Operator
            n1 = state.copy()
            if p_feats['has_neg'] != c_feats['has_neg']:
                # If negation mismatch, flipping truth might help if logic is tricky
                n1[0] = 1.0 - n1[0] 
            neighbors.append(n1)
            
            # 2. Comparative Tightening Operator
            n2 = state.copy()
            if p_feats['has_comp'] and c_feats['has_comp']:
                if len(p_feats['numbers']) > 0 and len(c_feats['numbers']) > 0:
                    # Check logical consistency of numbers (simplified)
                    # If prompt says "more than 5" and candidate has "6", boost info
                    if c_feats['numbers'][0] > p_feats['numbers'][0]: 
                        n2[1] = min(1.0, n2[1] + 0.3)
            neighbors.append(n2)
            
            # 3. Causal Chaining Operator
            n3 = state.copy()
            if p_feats['has_cause'] and c_feats['has_cause']:
                n3[0] = min(1.0, n3[0] + 0.4) # Boost truth if causal structure matches
                n3[2] = min(1.0, n3[2] + 0.2) # Boost relevance
            neighbors.append(n3)
            
            # 4. Quantity Sharing (Weight sharing analogy)
            n4 = state.copy()
            if len(p_feats['numbers']) == len(c_feats['numbers']) and len(p_feats['numbers']) > 0:
                n4[1] = min(1.0, n4[1] + 0.2)
            neighbors.append(n4)

            # Evaluate neighbors
            for n in neighbors:
                e = self._energy(n)
                if e < best_energy:
                    best_energy = e
                    state = n
                    improved = True
                    
        return -best_energy # Score is negative energy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        scores = []
        
        # Phase 1: Structural Scoring
        for cand in candidates:
            score = self._search_equilibrium(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": "thermo-nas"})
            scores.append(score)
        
        # Phase 2: Tie-breaking with NCD if scores are too close (within epsilon)
        final_results = []
        epsilon = 0.05
        
        # Sort initially by structural score
        sorted_indices = np.argsort(scores)[::-1]
        
        for idx in sorted_indices:
            cand = candidates[idx]
            base_score = scores[idx]
            
            # Check for ties among top candidates to apply NCD
            # (Simplified: just adding small NCD penalty if structural score is ambiguous)
            ncd_val = self._compute_ncd(prompt, cand)
            # NCD is distance (0=identical), we want similarity. 
            # But NCD on prompt/answer isn't always "correctness". 
            # We use it only as a tiny modifier for exact string matches or very close paraphrases.
            final_score = base_score - (ncd_val * 0.001) 
            
            final_results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Energy minimized via operators; NCD tiebreak applied."
            })
            
        # Re-sort after tie-breaking
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on equilibrium energy."""
        score = self._search_equilibrium(prompt, answer)
        # Map score (likely negative) to 0-1 range. 
        # Assuming max energy violation is around -0.5 and perfect is > -0.1
        # Sigmoid-like mapping not strictly needed, just normalization.
        conf = (score + 1.0) / 2.0 # Shift and scale roughly
        return float(np.clip(conf, 0.0, 1.0))