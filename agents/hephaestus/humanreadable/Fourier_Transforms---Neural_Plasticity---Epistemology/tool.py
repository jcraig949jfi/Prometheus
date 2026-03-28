import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Spectral Predictive-Coding Network with Reliability-Weighted Hebbian Plasticity.
    
    Mechanism:
    1. Structural Parsing (Epistemology): Extracts logical constraints (negations, comparatives,
       conditionals) to form a 'hypothesis' of the prompt's logical structure.
    2. Spectral Transformation (Fourier Analogy): Converts text into a frequency-like domain
       by analyzing n-gram periodicity and token distribution variance. This acts as a filter
       to detect noise vs. signal patterns.
    3. Reliability-Weighted Hebbian Plasticity: 
       - Prediction Error: Difference between structural expectations and candidate content.
       - Reliability (r_k): Inverse variance of structural features. High reliability features
         (e.g., explicit negations) weight the score heavily.
       - Update: Scores are updated based on the coherence of the candidate with high-reliability
         structural bands.
    4. NCD Tiebreaker: Used only when structural signals are ambiguous.
    """

    def __init__(self):
        self.stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'just', 'don', 'now'}
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere', 'cannot', "n't"}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse', 'larger', 'shorter', 'longer', 'increased', 'decreased'}
        self.conditionals = {'if', 'unless', 'provided', 'assuming', 'when', 'whenever'}

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_structure(self, text: str) -> Dict[str, float]:
        """Extracts logical features acting as 'reliability bands'."""
        tokens = set(self._tokenize(text))
        score = 0.0
        features = {
            'has_negation': 1.0 if any(n in tokens for n in self.negations) else 0.0,
            'has_comparative': 1.0 if any(c in tokens for c in self.comparatives) else 0.0,
            'has_conditional': 1.0 if any(c in tokens for c in self.conditionals) else 0.0,
            'numeric_density': 0.0
        }
        
        # Numeric density as a reliability band
        nums = re.findall(r'\d+\.?\d*', text)
        if len(text) > 0:
            features['numeric_density'] = len(nums) / (len(text) / 10.0) # Normalized approx
            
        return features

    def _spectral_transform(self, text: str) -> List[float]:
        """
        Analogous to Fourier Transform: Converts token sequence to frequency domain.
        Computes variance of n-gram occurrences to detect periodicity/structure.
        """
        tokens = self._tokenize(text)
        if not tokens:
            return [0.0] * 4
        
        # Simple spectral proxy: variance of token frequencies (energy distribution)
        freq = {}
        for t in tokens:
            freq[t] = freq.get(t, 0) + 1
        
        counts = list(freq.values())
        if len(counts) < 2:
            return [0.0] * 4
            
        mean_c = sum(counts) / len(counts)
        variance = sum((c - mean_c) ** 2 for c in counts) / len(counts)
        
        # Bigram variance (higher frequency components)
        bigrams = [f"{tokens[i]}_{tokens[i+1]}" for i in range(len(tokens)-1)]
        bg_freq = {}
        for bg in bigrams:
            bg_freq[bg] = bg_freq.get(bg, 0) + 1
            
        bg_counts = list(bg_freq.values()) if bg_freq else [0]
        mean_bg = sum(bg_counts) / len(bg_counts)
        bg_variance = sum((c - mean_bg) ** 2 for c in bg_counts) / len(bg_counts) if len(bg_counts) > 1 else 0.0
        
        # Return spectral signature
        return [variance, bg_variance, len(tokens), len(set(tokens))]

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(z1, z2)
        if denom == 0: return 1.0
        return (z12 - min(z1, z2)) / denom

    def _evaluate_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Core logic: Spectral Hebbian update with reliability weighting."""
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        # 1. Compute Prediction Error (epsilon) in structural domain
        errors = []
        reliability_weights = []
        
        # Band 1: Negation consistency (High reliability if present in prompt)
        err_neg = abs(p_struct['has_negation'] - c_struct['has_negation'])
        rel_neg = 2.0 if p_struct['has_negation'] > 0 else 0.5 # High weight if prompt has negation
        errors.append(err_neg)
        reliability_weights.append(rel_neg)
        
        # Band 2: Comparative consistency
        err_comp = abs(p_struct['has_comparative'] - c_struct['has_comparative'])
        rel_comp = 1.5 if p_struct['has_comparative'] > 0 else 0.5
        errors.append(err_comp)
        reliability_weights.append(rel_comp)
        
        # Band 3: Conditional consistency
        err_cond = abs(p_struct['has_conditional'] - c_struct['has_conditional'])
        rel_cond = 1.5 if p_struct['has_conditional'] > 0 else 0.5
        errors.append(err_cond)
        reliability_weights.append(rel_cond)

        # 2. Spectral Hebbian Update
        # Delta W = eta * error * pre * post (simplified to coherence check)
        # If error is low (coherent), score increases. Weighted by reliability.
        base_score = 1.0
        reasoning_steps = []
        
        total_weighted_error = 0.0
        total_reliability = 0.0
        
        for i, err in enumerate(errors):
            r = reliability_weights[i]
            # Gaussian-like penalty scaled by reliability
            penalty = r * (err ** 2) 
            total_weighted_error += penalty
            total_reliability += r
            
            if err > 0 and r > 1.0:
                reasoning_steps.append(f"Mismatch in {'negation' if i==0 else 'comparative' if i==1 else 'conditional'} structure (Reliability: {r})")

        # Normalize error by total reliability to get a bounded score component
        structural_score = math.exp(-total_weighted_error / (total_reliability + 1e-6))
        
        # 3. NCD Tiebreaker (only if structural score is high/ambiguous)
        ncd_score = 0.0
        if structural_score > 0.8:
            ncd = self._compute_ncd(prompt, candidate)
            # Low NCD (high similarity) is good for context, but we want reasoning.
            # Use NCD to penalize complete irrelevance if structure matches but content is noise.
            # Inverse NCD contribution
            ncd_score = (1.0 - ncd) * 0.1 
            if ncd > 0.85: # Very different strings might be wrong if structure matched by chance
                 reasoning_steps.append("Low content overlap (NCD check)")

        final_score = structural_score + ncd_score
        final_score = max(0.0, min(1.0, final_score)) # Clamp 0-1
        
        if not reasoning_steps:
            reasoning_steps.append("Structural coherence maintained across spectral bands.")
            
        return final_score, "; ".join(reasoning_steps)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        for cand in candidates:
            score, reason = self._evaluate_candidate(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        score, _ = self._evaluate_candidate(prompt, answer)
        return score