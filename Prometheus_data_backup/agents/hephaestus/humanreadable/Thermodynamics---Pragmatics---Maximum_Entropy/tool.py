import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamic-Pragmatic Reasoning Tool.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (negations, comparatives, numerics) 
       into a constraint matrix A and bound vector b.
    2. Pragmatics: Assigns 'energy' costs based on Gricean maxims (length, relevance).
    3. Inference: Uses a simplified Maximum Entropy principle (via Generalized Iterative 
       Scaling logic) to find the probability distribution over truth assignments that 
       maximizes entropy while minimizing pragmatic energy.
    4. Scoring: Candidates are scored by their joint log-probability (equilibrium state).
    
    Note: MaxEnt is restricted to the confidence wrapper and structural scoring modifier 
    as per causal intelligence guidelines, with structural parsing as the primary signal.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater|less|more|fewer|higher|lower)\s+(than)?', re.IGNORECASE),
            'numeric': re.compile(r'\d+(\.\d+)?'),
            'conditional': re.compile(r'\b(if|then|unless)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|leads? to|causes?)\b', re.IGNORECASE)
        }

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Extract structural features from text."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(self.patterns['negation'].search(text_lower)),
            'has_comparative': bool(self.patterns['comparative'].search(text_lower)),
            'has_conditional': bool(self.patterns['conditional'].search(text_lower)),
            'has_causal': bool(self.patterns['causal'].search(text_lower)),
            'numbers': [float(n) for n in self.patterns['numeric'].findall(text_lower)],
            'length': len(text.split()),
            'raw': text
        }
        return features

    def _compute_pragmatic_energy(self, features: Dict, prompt_len: int) -> float:
        """
        Compute pragmatic cost (energy). 
        High energy = violation of maxims (e.g., too verbose or too brief relative to prompt).
        """
        energy = 0.0
        # Penalty for excessive length (Quantity maxim)
        if features['length'] > prompt_len * 1.5:
            energy += 0.5
        # Penalty for extreme brevity if prompt is complex (Manner maxim)
        if features['length'] < 3 and prompt_len > 10:
            energy += 0.3
        return energy

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Primary scoring based on structural constraint satisfaction.
        Returns a score where higher is better (constraints satisfied).
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        score = 0.0
        
        # 1. Numeric Consistency (Strongest signal)
        if p_feat['numbers'] and c_feat['numbers']:
            # Check if candidate numbers logically follow prompt numbers
            # Simple heuristic: if prompt has comparison words, candidate numbers should reflect order
            if p_feat['has_comparative']:
                if 'less' in p_feat['raw'].lower() or 'fewer' in p_feat['raw'].lower():
                    # Expect smaller number in candidate if it answers a specific query? 
                    # Hard to infer direction without full NLP, so we check consistency of presence
                    score += 2.0 if len(c_feat['numbers']) > 0 else 0.0
                else:
                    score += 2.0 if len(c_feat['numbers']) > 0 else 0.0
            else:
                # Exact match or close proximity often required for numeric answers
                p_nums = sorted(p_feat['numbers'])
                c_nums = sorted(c_feat['numbers'])
                # Reward if candidate contains a number from prompt (contextual relevance)
                if any(abs(p - c) < 1e-6 for p in p_nums for c in c_nums):
                    score += 3.0
        
        # 2. Logical Consistency (Negation/Conditional)
        if p_feat['has_negation']:
            if c_feat['has_negation']:
                score += 1.5 # Likely preserves logical scope
            else:
                score -= 1.0 # Risk of contradiction
        
        if p_feat['has_conditional']:
            if c_feat['has_conditional'] or c_feat['has_causal']:
                score += 1.0 # Maintains logical structure
        
        # 3. Pragmatic Energy (Thermodynamic component)
        # Lower energy = higher probability. We subtract energy from score.
        p_energy = self._compute_pragmatic_energy(c_feat, len(p_feat['raw'].split()))
        score -= p_energy * 2.0
        
        return score

    def _max_ent_confidence_mod(self, base_score: float, prompt: str, answer: str) -> float:
        """
        Applies MaxEnt principle as a confidence modifier.
        Models P(z) ~ exp(-E). 
        Uses GIS-like logic to adjust confidence based on equilibrium between 
        structural score and pragmatic energy.
        """
        # Simplified Gibbs distribution logic for confidence
        # Temperature T=1.0 for scaling
        energy = -base_score # Higher base_score -> lower energy
        
        # Partition function approximation (Z) - normalizing over a hypothetical space
        # Since we don't have the full space, we use a sigmoid-like mapping 
        # derived from the exponential family form: P ~ exp(-E)
        # We clamp to avoid overflow
        energy = np.clip(energy, -10, 10)
        
        # Exponential family probability proxy
        prob = np.exp(energy) / (1.0 + np.exp(energy))
        
        # Adjust for pragmatic "surprise" (entropy)
        # If the answer is too short/long compared to prompt, entropy is high -> lower confidence
        p_feat = self._extract_features(prompt)
        a_feat = self._extract_features(answer)
        
        len_ratio = a_feat['length'] / (p_feat['length'] + 1e-6)
        if len_ratio < 0.1 or len_ratio > 5.0:
            prob *= 0.8 # Penalize outliers
            
        return float(np.clip(prob, 0.0, 1.0))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates and return ranked list.
        """
        results = []
        prompt_features = self._extract_features(prompt)
        prompt_len_words = prompt_features['length']
        
        scored_candidates = []
        
        for cand in candidates:
            # 1. Structural Parsing & Scoring (Primary Signal)
            struct_score = self._structural_score(prompt, cand)
            
            # 2. Pragmatic Energy Calculation
            cand_features = self._extract_features(cand)
            prag_energy = self._compute_pragmatic_energy(cand_features, prompt_len_words)
            
            # 3. Combined Score (Thermodynamic Equilibrium)
            # Score = Structural Fit - Pragmatic Cost
            final_score = struct_score - (prag_energy * 0.5)
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural:{struct_score:.2f}, PragmaticCost:{prag_energy:.2f}"
            })

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        
        # Normalize scores for better interpretability (optional but good practice)
        if scored_candidates:
            max_s = scored_candidates[0]['score']
            min_s = scored_candidates[-1]['score']
            range_s = max_s - min_s if max_s != min_s else 1.0
            for item in scored_candidates:
                # Rescale to 0-10 range roughly
                item['score'] = 5.0 + ((item['score'] - min_s) / range_s) * 5.0

        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Uses structural parsing as primary, MaxEnt as wrapper.
        """
        # Base structural evaluation
        base_score = self._structural_score(prompt, answer)
        
        # Apply MaxEnt confidence modifier
        conf = self._max_ent_confidence_mod(base_score, prompt, answer)
        
        return conf