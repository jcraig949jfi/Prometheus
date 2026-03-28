import re
import zlib
import math

class ReasoningTool:
    """
    Thermodynamically-Regulated Adaptive Morphogenetic Bandit (TRAMB) Approximation.
    
    Mechanism:
    1. Morphogenesis (Hypothesis Space): Instead of a static list, we treat the 
       candidate set as a dynamic field. We generate 'structural perturbations' 
       (simulating reaction-diffusion peaks) by parsing logical constraints 
       (negations, comparatives, conditionals) from the prompt.
       
    2. Thermodynamics (Exploration Bonus): We compute an 'Entropy Production' score 
       based on the information density and structural complexity of the candidate 
       relative to the parsed constraints. High entropy production (high information 
       gain per unit of logical consistency) yields an exploration bonus.
       
    3. Bandit (Selection): Candidates are scored via a UCB-like formula:
       Score = (Logical Consistency Reward) + (Exploration Bonus * Entropy Factor).
       
    4. NCD Tiebreaker: Normalized Compression Distance is used only when structural 
       scores are indistinguishable, serving as a similarity metric to the prompt's 
       semantic center.
    """

    def __init__(self):
        self._pattern_cache = {}

    def _structural_parse(self, text: str) -> dict:
        """Extracts logical primitives: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse|than)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|when)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text_lower),
            'length': len(text)
        }
        # Normalize numbers to float for comparison logic if present
        features['numeric_vals'] = []
        for n in features['numbers']:
            try:
                features['numeric_vals'].append(float(n))
            except ValueError:
                pass
        return features

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Evaluates if the candidate respects the logical structure of the prompt.
        Returns a reward score (0.0 to 1.0).
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()
        
        reward = 0.5 # Base score
        
        # Constraint 1: Negation Handling
        # If prompt has negation, correct answer often needs to reflect it or contradict a false premise
        if p_feat['negations'] > 0:
            if c_feat['negations'] > 0 or any(x in c_lower for x in ['false', 'incorrect', 'no', 'not']):
                reward += 0.2
        
        # Constraint 2: Comparative Logic
        if p_feat['comparatives'] > 0:
            # Check if candidate contains comparative words or specific numbers found in prompt
            if c_feat['comparatives'] > 0 or len(c_feat['numbers']) > 0:
                reward += 0.15
                
        # Constraint 3: Numeric Evaluation (Simple transitivity check)
        if len(p_feat['numeric_vals']) >= 2:
            nums = sorted(p_feat['numeric_vals'])
            # If candidate mentions the largest number, it might be the answer to "which is largest"
            if c_feat['numbers']:
                c_nums = [float(x) for x in c_feat['numbers']]
                if max(nums) in c_nums or min(nums) in c_nums:
                    reward += 0.25

        # Constraint 4: Conditional Presence
        if p_feat['conditionals'] > 0:
            if c_feat['conditionals'] > 0 or len(c_lower) > 10: # Heuristic for elaborated conditional answer
                reward += 0.1

        return min(reward, 1.0)

    def _compute_entropy_production(self, prompt: str, candidate: str) -> float:
        """
        Computes a proxy for local entropy production.
        High entropy = High information density / unexpectedness relative to prompt.
        """
        if not candidate:
            return 0.0
        
        # Information density approximation via unique chars / length
        unique_chars = len(set(candidate))
        length = len(candidate)
        if length == 0:
            return 0.0
            
        density = unique_chars / length
        
        # Dissipation: Difference in structural complexity between prompt and candidate
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        complexity_diff = abs(p_feat['length'] - c_feat['length']) / (p_feat['length'] + 1)
        
        # Entropy production rate proxy
        entropy = (density * 0.5) + (complexity_diff * 0.5)
        return entropy

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len_s1 = len(zlib.compress(s1.encode('utf-8')))
        len_s2 = len(zlib.compress(s2.encode('utf-8')))
        len_combined = len(zlib.compress((s1 + s2).encode('utf-8')))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        
        if not candidates:
            return []

        # Pre-calculate prompt features
        prompt_features = self._structural_parse(prompt)
        
        scored_candidates = []
        
        for cand in candidates:
            if not isinstance(cand, str):
                cand = str(cand)
                
            # 1. Logical Consistency (Exploitation Reward)
            reward = self._check_logical_consistency(prompt, cand)
            
            # 2. Entropy Production (Exploration Bonus)
            entropy = self._compute_entropy_production(prompt, cand)
            
            # 3. Bandit Score: Reward + Bonus * Entropy
            # This mimics UCB where entropy drives exploration of complex answers
            bandit_score = reward + (entropy * 0.3)
            
            scored_candidates.append({
                "candidate": cand,
                "base_score": bandit_score,
                "entropy": entropy
            })

        # Normalize scores to avoid dominance by length alone
        max_base = max(c["base_score"] for c in scored_candidates) if scored_candidates else 0
        min_base = min(c["base_score"] for c in scored_candidates) if scored_candidates else 0
        range_base = max_base - min_base if (max_base - min_base) > 1e-6 else 1.0

        final_results = []
        for item in scored_candidates:
            # Normalize base score to 0.5-0.9 range to leave room for NCD tiebreaking
            norm_score = 0.5 + (0.4 * (item["base_score"] - min_base) / range_base)
            
            # Reasoning string generation
            reasoning = f"Logical consistency: {item['base_score']:.2f}. "
            if item['entropy'] > 0.4:
                reasoning += "High informational entropy detected (rich hypothesis)."
            elif prompt_features['negations'] > 0 and 'not' in item['candidate'].lower():
                reasoning += "Negation constraint satisfied."
            else:
                reasoning += "Standard structural match."

            final_results.append({
                "candidate": item["candidate"],
                "score": norm_score,
                "reasoning": reasoning,
                "_entropy": item["entropy"] # Internal use for sorting stability
            })

        # Sorting Strategy:
        # Primary: Score (Logical/Thermodynamic)
        # Secondary: NCD (Similarity to prompt as a tie-breaker for "relevance")
        # We sort descending by score. For ties, we prefer lower NCD (more similar to prompt context).
        
        def sort_key(x):
            # Small NCD bonus for ties in structural score
            ncd_val = self._ncd(prompt, x["candidate"])
            return (-x["score"], ncd_val)

        final_results.sort(key=sort_key)
        
        # Clean up internal fields and return
        return [{"candidate": r["candidate"], "score": r["score"], "reasoning": r["reasoning"]} for r in final_results]

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on thermodynamic stability of the answer 
        relative to the prompt's logical constraints.
        """
        if not answer:
            return 0.0
            
        consistency = self._check_logical_consistency(prompt, answer)
        entropy = self._compute_entropy_production(prompt, answer)
        
        # Confidence is high if consistency is high AND entropy is moderate (not noise)
        # Too high entropy might mean random noise, too low means trivial copy
        entropy_factor = 1.0 if 0.1 < entropy < 0.8 else 0.5
        
        conf_score = consistency * entropy_factor
        
        # Boost if numeric constraints are explicitly satisfied
        p_nums = self._structural_parse(prompt)['numeric_vals']
        a_nums = self._structural_parse(answer)['numeric_vals']
        
        if p_nums and a_nums:
            # If numbers match exactly, high confidence
            if any(abs(p - a) < 1e-6 for p in p_nums for a in a_nums):
                conf_score = min(conf_score + 0.3, 1.0)
                
        return float(min(max(conf_score, 0.0), 1.0))