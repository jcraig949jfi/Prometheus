import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Chaotic Pragmatic Model Checker (CPMC) Implementation.
    
    Mechanism:
    1. Pragmatics (Gricean Maxims): Parses the prompt for structural constraints 
       (negations, comparatives, conditionals) to form a "Relevance Vector".
    2. Chaos Theory (Logistic Map): Uses a deterministic chaotic map (r=3.9) 
       initialized with a seed derived from the prompt/candidate hash. This generates 
       divergent perturbation weights to explore the "state space" of the candidate's 
       features, simulating sensitivity to initial conditions.
    3. Model Checking: Validates if the candidate satisfies the extracted structural 
       constraints (the specification). 
       
    Scoring:
    - Base score derived from structural satisfaction (Model Checking).
    - Multiplied by a chaotic divergence factor (Chaos) that rewards candidates 
      containing specific contextual keywords identified by the pragmatic layer.
    - NCD used strictly as a tie-breaker for low-scoring candidates.
    """

    def __init__(self):
        self.r = 3.9  # Logistic map parameter for chaos
        self.max_iter = 100

    def _logistic_map(self, seed: float, iterations: int) -> List[float]:
        """Generates a chaotic sequence using the logistic map."""
        x = seed
        sequence = []
        for _ in range(iterations):
            x = self.r * x * (1 - x)
            sequence.append(x)
        return sequence

    def _extract_pragmatic_features(self, text: str) -> Dict[str, any]:
        """Extracts structural and pragmatic features (Gricean Maxims)."""
        lower = text.lower()
        features = {
            'has_negation': bool(re.search(r'\b(no|not|never|none|neither)\b', lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|better|worse|than|\>|\<)\b', lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|otherwise)\b', lower)),
            'has_numeric': bool(re.search(r'\d+', lower)),
            'word_count': len(text.split()),
            'keywords': set(re.findall(r'\b\w+\b', lower))
        }
        return features

    def _check_model_compliance(self, prompt: str, candidate: str) -> float:
        """
        Model Checking step: Verifies if the candidate satisfies 
        logical constraints implied by the prompt structure.
        """
        p_feat = self._extract_pragmatic_features(prompt)
        c_feat = self._extract_pragmatic_features(candidate)
        score = 1.0
        
        # Constraint 1: Negation consistency
        # If prompt asks a negative question or contains strong negation, 
        # valid answers often mirror or explicitly address it.
        if p_feat['has_negation']:
            # Simple heuristic: if prompt has negation, candidate should ideally 
            # contain logical markers or be substantial enough to explain.
            if not c_feat['has_negation'] and c_feat['word_count'] < 3:
                score *= 0.8 # Penalty for overly simple response to complex negative prompt

        # Constraint 2: Comparative logic
        if p_feat['has_comparative']:
            if not c_feat['has_comparative'] and not c_feat['has_numeric']:
                # If prompt compares, good answers often compare or quantify
                score *= 0.9
        
        # Constraint 3: Conditional logic
        if p_feat['has_conditional']:
            if not c_feat['has_conditional'] and c_feat['word_count'] < 5:
                score *= 0.95

        return score

    def _compute_chaos_score(self, prompt: str, candidate: str) -> float:
        """
        Chaos step: Uses logistic map to generate a sensitivity score.
        Seed depends on the interaction between prompt and candidate hashes.
        """
        # Create a deterministic seed from 0.1 to 0.9 based on string content
        combined = f"{prompt}:{candidate}"
        seed_val = (hash(combined) % 1000) / 1000.0
        if seed_val == 0: seed_val = 0.5 # Avoid fixed points
        
        # Generate chaotic trajectory
        trajectory = self._logistic_map(seed_val, self.max_iter)
        
        # Pragmatic Guidance: Bias towards regions where candidate contains 
        # keywords found in prompt (Relevance Maxim)
        p_words = self._extract_pragmatic_features(prompt)['keywords']
        c_words = self._extract_pragmatic_features(candidate)['keywords']
        overlap = len(p_words.intersection(c_words)) + 1 # Avoid div by zero
        
        # The chaotic sum acts as a unique fingerprint for this pair
        chaos_sum = sum(trajectory)
        
        # Normalize and bias by overlap (Pragmatics guiding Chaos)
        # High overlap + chaotic stability in specific regions = higher score
        base_chaos = (chaos_sum / self.max_iter) 
        return base_chaos * (1.0 + (overlap / 10.0))

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 1.0
            
        return (len_combined - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt features for pragmatic context
        p_feat = self._extract_pragmatic_features(prompt)
        
        for cand in candidates:
            # 1. Model Checking (Structural Validation)
            mc_score = self._check_model_compliance(prompt, cand)
            
            # 2. Chaos + Pragmatics (Exploration & Relevance)
            chaos_score = self._compute_chaos_score(prompt, cand)
            
            # 3. NCD (Tie-breaker only)
            # Invert NCD so higher is better (similarity), but weight it low
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.05 # Max 0.05 contribution
            
            # Final Score Composition
            # Logic: Structural compliance is primary (0-1), 
            # Chaos adds differentiation (0-0.2 range typically), NCD is noise floor
            final_score = (mc_score * 0.6) + (chaos_score * 0.35) + ncd_score
            
            # Reasoning trace
            reason_parts = []
            if p_feat['has_negation'] and self._extract_pragmatic_features(cand)['has_negation']:
                reason_parts.append("Maintains negation consistency")
            if p_feat['has_comparative'] and self._extract_pragmatic_features(cand)['has_comparative']:
                reason_parts.append("Matches comparative structure")
            if chaos_score > 0.5:
                reason_parts.append("High chaotic relevance")
                
            reasoning = "; ".join(reason_parts) if reason_parts else "Standard structural match"

            results.append({
                "candidate": cand,
                "score": round(final_score, 6),
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the evaluation score."""
        # Evaluate single candidate against itself to get relative score
        # We simulate a small candidate pool of [answer, ""] to normalize
        res = self.evaluate(prompt, [answer, "No"])
        if res and res[0]['candidate'] == answer:
            # Normalize the score to 0-1 range based on expected max possible
            # Max theoretical approx 1.0 (1.0*0.6 + ~0.4*0.35 + small)
            conf = min(1.0, max(0.0, res[0]['score']))
            return round(conf, 4)
        return 0.0