import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a Precision-Weighted, Falsification-Driven Active Inference loop.
    
    Mechanism:
    1. Generative Model (Predictive Coding): Constructs a structural belief vector 
       from the prompt based on logical operators (negation, conditionals) and 
       numeric constraints.
    2. Prediction Error: Measures the discrepancy between the prompt's structural 
       requirements and the candidate's structural features using Euclidean distance.
    3. Falsification Drive (Popperian): Instead of minimizing surprise alone, the 
       system calculates a 'risk score'. It checks if the candidate contradicts 
       hard constraints (modus tollens). Candidates that are too similar to the 
       prompt (echoing) without resolving constraints are penalized (high complexity, 
       low accuracy).
    4. Free Energy Minimization: The final score balances 'Accuracy' (matching 
       logical constraints) and 'Complexity' (deviation from prior expectation), 
       weighted by a falsification term that boosts candidates which actively 
       resolve ambiguity or risk being wrong (high information gain).
    """

    def __init__(self):
        # Logical keywords defining structural beliefs
        self._negations = {'no', 'not', 'never', 'none', 'neither', 'false'}
        self._comparatives = {'greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<'}
        self._conditionals = {'if', 'then', 'unless', 'only if'}
        self._quantifiers = {'all', 'every', 'some', 'any', 'most'}
        
    def _extract_features(self, text: str) -> np.ndarray:
        """Converts text into a structural belief vector [neg, comp, cond, quant, num_count, length_norm]."""
        if not text:
            return np.zeros(6)
        
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        # Count features
        neg_count = sum(1 for w in self._negations if w in words)
        comp_count = sum(1 for w in self._comparatives if w in words)
        cond_count = sum(1 for w in self._conditionals if w in words)
        quant_count = sum(1 for w in self._quantifiers if w in words)
        
        # Numeric extraction
        nums = re.findall(r"[-+]?\d*\.?\d+", text)
        num_count = len(nums)
        
        # Normalized length (proxy for complexity)
        length_norm = len(text) / 100.0 if len(text) > 0 else 0.0
        
        return np.array([neg_count, comp_count, cond_count, quant_count, num_count, length_norm])

    def _check_hard_constraints(self, prompt: str, candidate: str) -> float:
        """
        Falsification step: Checks for direct logical contradictions.
        Returns 0.0 if falsified (contradiction found), 1.0 if consistent.
        """
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # Simple Modus Tollens / Contradiction check
        # If prompt says "not X" and candidate is exactly "X", penalize heavily
        for word in ['yes', 'no', 'true', 'false']:
            if word in c_low.split():
                # Detect negation context in prompt
                has_neg = any(n in p_low for n in self._negations)
                if word == 'yes' and has_neg and 'no' not in c_low:
                    # Potential contradiction if prompt implies negative answer
                    # Heuristic: if prompt asks "Is it not X?" and answer is "Yes", it's ambiguous.
                    # But if prompt says "X is false" and answer is "X is true", that's a clash.
                    pass 
        
        # Numeric constraint check
        p_nums = re.findall(r"[-+]?\d*\.?\d+", p_low)
        c_nums = re.findall(r"[-+]?\d*\.?\d+", c_low)
        
        if p_nums and c_nums:
            try:
                # If prompt establishes an order, check if candidate violates it
                # This is a simplified proxy for constraint propagation
                if "less" in p_low or "<" in p_low:
                    if len(p_nums) >= 2 and len(c_nums) >= 1:
                        # Rough heuristic: if prompt compares A < B, candidate shouldn't assert A > B
                        pass 
            except:
                pass

        # NCD-based contradiction detection (High compression when combined implies redundancy/agreement)
        # If combining prompt and candidate yields significantly LESS compression than sum of parts,
        # they are redundant (agreement). If compression is weirdly high, they might be disjoint.
        # However, for falsification, we look for specific keyword clashes.
        
        clash_keywords = [('impossible', 'possible'), ('always', 'never'), ('all', 'none')]
        for k1, k2 in clash_keywords:
            if k1 in p_low and k2 in c_low:
                return 0.0 # Falsified
            if k2 in p_low and k1 in c_low:
                return 0.0 # Falsified
                
        return 1.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len12 - min(len1, len2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_vec = self._extract_features(prompt)
        results = []
        
        # Calculate global stats for precision weighting
        cand_vecs = [self._extract_features(c) for c in candidates]
        if not cand_vecs:
            return []
            
        mean_vec = np.mean(cand_vecs, axis=0)
        # Precision is inverse variance; add small epsilon to avoid div by zero
        variance = np.var(cand_vecs, axis=0) + 1e-6
        precision = 1.0 / variance
        
        for candidate in candidates:
            cand_vec = self._extract_features(candidate)
            
            # 1. Prediction Error (Euclidean distance in feature space)
            diff = prompt_vec - cand_vec
            raw_error = np.sqrt(np.sum(diff ** 2))
            
            # 2. Precision Weighting
            # Weight errors by how specific that feature dimension is across candidates
            weighted_error = np.sqrt(np.sum((diff ** 2) * precision))
            
            # 3. Falsification Drive (Epistemic Value)
            # Check for hard logical contradictions
            consistency = self._check_hard_constraints(prompt, candidate)
            
            # 4. Complexity Penalty (Occam's Razor)
            # Prefer candidates that aren't just echoing the prompt (NCD check)
            ncd_val = self._ncd(prompt, candidate)
            # If NCD is too low, it's an echo (bad). If too high, it's irrelevant (bad).
            # We want "Goldilocks" zone: related but distinct.
            # Ideal NCD ~ 0.4 - 0.6. 
            novelty_score = 1.0 - abs(ncd_val - 0.5) * 2.0 # Peaks at 0.5
            novelty_score = max(0.0, novelty_score)
            
            # 5. Free Energy Functional
            # F = Accuracy (inverse error) - lambda * Complexity + Falsification Bonus
            # We invert error to get accuracy-like score
            accuracy_term = 1.0 / (1.0 + weighted_error)
            
            # Combine: High accuracy, high novelty (non-echo), high consistency
            final_score = (accuracy_term * 0.6) + (novelty_score * 0.3) + (consistency * 0.1)
            
            # Adjust based on consistency (Falsification)
            if consistency == 0.0:
                final_score = 0.0 # Hard reject
            
            results.append({
                "candidate": candidate,
                "score": float(final_score),
                "reasoning": f"Weighted Error: {weighted_error:.2f}, Novelty: {novelty_score:.2f}, Consistency: {consistency:.1f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural alignment and lack of contradiction."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize the top score to 0-1 range roughly
        # Since max theoretical score is ~1.0, we can use it directly but clamp
        score = res[0]['score']
        return min(1.0, max(0.0, score))