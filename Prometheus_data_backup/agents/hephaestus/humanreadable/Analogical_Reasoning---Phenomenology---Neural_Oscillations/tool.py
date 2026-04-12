import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Oscillatory Phenomenal Analogical Reasoner (OPAR) - Computational Approximation
    
    Mechanism:
    1. Phenomenological Layer (PSV): Encodes prompt/candidate structure into a vector
       representing 'qualia' of logic (negations, comparatives, numbers, conditionals).
       Implements 'bracketing' by filtering noise to isolate structural intent.
    2. Neural Oscillations: Simulates Theta-Gamma coupling.
       - Theta: Organizes sequential logical blocks (sentences/clauses).
       - Gamma: Binds relational predicates within blocks via weighted feature binding.
    3. Analogical Mapping: Uses Bayesian-like scoring to map source (prompt) structure
       to target (candidate) structure, favoring relational consistency over lexical overlap.
    
    Strategy:
    - Primary Score: Structural alignment (logic, numbers, constraints).
    - Secondary Score: Oscillatory binding strength (coherence of logical features).
    - Tiebreaker: NCD (Compression distance).
    """

    def __init__(self):
        self.theta_freq = 6.0  # Simulated theta center
        self.gamma_freq = 40.0 # Simulated gamma center

    def _extract_structural_features(self, text: str) -> Dict[str, float]:
        """Extracts logical 'qualia' features (Phenomenological State Vector)."""
        if not text:
            return {k: 0.0 for k in ['neg_count', 'comp_count', 'cond_count', 'num_val', 'len_norm']}
        
        lower_text = text.lower()
        
        # Negation detection
        negations = ['not', 'no', 'never', 'neither', 'nobody', 'nothing', 'nowhere', 'cannot', "n't"]
        neg_count = sum(lower_text.count(n) for n in negations)
        
        # Comparative detection
        comps = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', 'better', 'worse', '>', '<', '>=', '<=']
        comp_count = sum(lower_text.count(c) for c in comps)
        
        # Conditional detection
        conds = ['if', 'then', 'else', 'unless', 'provided', 'when', 'implies']
        cond_count = sum(lower_text.count(c) for c in conds)
        
        # Numeric evaluation (simple extraction of first float/int for magnitude)
        nums = re.findall(r'-?\d+\.?\d*', text)
        num_val = float(nums[0]) if nums else 0.0
        
        # Length normalization (bracketing noise)
        len_norm = len(text) / 100.0
        
        return {
            'neg_count': float(neg_count),
            'comp_count': float(comp_count),
            'cond_count': float(cond_count),
            'num_val': num_val,
            'len_norm': len_norm
        }

    def _simulate_oscillatory_binding(self, prompt_features: Dict, candidate_features: Dict) -> float:
        """
        Simulates Theta-Gamma coupling to bind relational predicates.
        Theta organizes the sequence (feature presence), Gamma binds the intensity (feature match).
        Returns a coherence score (0.0 to 1.0).
        """
        keys = ['neg_count', 'comp_count', 'cond_count']
        theta_phase = 0.0
        gamma_bind = 0.0
        
        # Theta: Sequential organization of logical types
        for i, key in enumerate(keys):
            p_val = prompt_features.get(key, 0)
            c_val = candidate_features.get(key, 0)
            
            # Presence match (Theta rhythm sync)
            p_present = 1.0 if p_val > 0 else 0.0
            c_present = 1.0 if c_val > 0 else 0.0
            
            if p_present == c_present and p_present > 0:
                theta_phase += 1.0 / len(keys)
            
            # Gamma: Feature binding strength (magnitude similarity)
            if p_val > 0 and c_val > 0:
                diff = abs(p_val - c_val)
                similarity = 1.0 / (1.0 + diff) # Decay with difference
                gamma_bind += similarity * (1.0 / len(keys))
        
        # Numeric binding (special case for magnitude reasoning)
        p_num = prompt_features.get('num_val', 0)
        c_num = candidate_features.get('num_val', 0)
        if p_num != 0:
            # Check if candidate preserves numeric logic (simplified)
            num_coherence = 1.0 if abs(p_num - c_num) < 1.0 else 0.5
            gamma_bind += num_coherence * 0.5 # Weighted contribution
            
        return min(1.0, theta_phase * 0.4 + gamma_bind * 0.6)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        if not s1 or not s2:
            return 1.0
        try:
            c1 = len(zlib.compress(s1.encode()))
            c2 = len(zlib.compress(s2.encode()))
            c12 = len(zlib.compress((s1 + s2).encode()))
            max_len = max(c1, c2)
            if max_len == 0:
                return 0.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_features = self._extract_structural_features(prompt)
        results = []
        
        for cand in candidates:
            cand_features = self._extract_structural_features(cand)
            
            # 1. Structural Parsing Score (Primary Signal)
            # Checks for logical consistency in negation, comparison, and conditionals
            struct_score = 0.0
            
            # Negation alignment
            p_neg = 1 if prompt_features['neg_count'] > 0 else 0
            c_neg = 1 if cand_features['neg_count'] > 0 else 0
            # In many reasoning tasks, if prompt has negation, answer might need to address it
            # Simple heuristic: if prompt asks a negative question, valid answers often reflect that context
            if p_neg == c_neg:
                struct_score += 0.3
            
            # Comparative alignment
            if prompt_features['comp_count'] > 0:
                if cand_features['comp_count'] > 0 or cand_features['num_val'] > 0:
                    struct_score += 0.4 # Candidate respects comparative nature
            
            # Conditional alignment
            if prompt_features['cond_count'] > 0:
                if cand_features['cond_count'] > 0 or len(cand) < 50: # Short answers often resolve conditionals
                    struct_score += 0.3

            # 2. Oscillatory Binding Score (Analogical Coherence)
            osc_score = self._simulate_oscillatory_binding(prompt_features, cand_features)
            
            # 3. NCD Tiebreaker (Inverted: lower distance is better)
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.2 # Max 0.2 contribution
            
            # Final Score Composition
            # Heavier weight on structural and oscillatory binding
            final_score = (struct_score * 0.5) + (osc_score * 0.3) + ncd_score
            
            # Bonus for exact numeric match in simple eval tasks
            if prompt_features['num_val'] != 0 and cand_features['num_val'] != 0:
                if abs(prompt_features['num_val'] - cand_features['num_val']) < 1e-6:
                    final_score += 0.5

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Structural:{struct_score:.2f}, Oscillatory:{osc_score:.2f}, NCD:{ncd_score:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and oscillatory binding.
        """
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
        
        # Normalize the top score to 0-1 range based on theoretical max
        # Theoretical max approx 1.0 (0.5 struct + 0.3 osc + 0.2 ncd + bonuses)
        raw_score = res_list[0]['score']
        confidence = min(1.0, max(0.0, raw_score))
        
        return round(confidence, 4)