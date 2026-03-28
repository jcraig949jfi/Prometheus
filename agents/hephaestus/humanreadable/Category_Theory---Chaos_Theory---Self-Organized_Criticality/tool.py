import zlib
import re
import math

class ReasoningTool:
    """
    Critical Functorial Reservoir (CFR) Approximation.
    
    Mechanism:
    1. Category Theory (Structural Functor): Parses prompt/candidate into structural tokens
       (negations, comparatives, conditionals, numbers). This acts as the 'functor' mapping
       raw text to a logical category, preserving relationships.
    2. Chaos Theory (Deterministic Perturbation): Applies a logistic map to the structural
       feature vector. This amplifies small differences in logical structure (sensitivity
       to initial conditions) without random noise, acting as a deterministic 'natural 
       transformation' to score consistency.
    3. Self-Organized Criticality (Avalanche Threshold): Monitors the 'gradient' (structural 
       mismatch). If mismatch exceeds a threshold, an 'avalanche' penalty is applied, 
       drastically reducing the score. This mimics SOC sandpile dynamics where large 
       deviations trigger system-wide reconfiguration (rejection).
       
    Scoring:
    - Primary: Structural consistency (logic, numbers, constraints).
    - Secondary: Chaotic amplification of structural features.
    - Tiebreaker: Normalized Compression Distance (NCD).
    """

    def __init__(self):
        # SOC Parameters
        self.critical_threshold = 0.6  # Threshold for avalanche
        self.avalanche_penalty = 0.9   # Penalty factor when criticality exceeded
        
        # Chaos Parameters
        self.r_chaos = 3.99  # Logistic map parameter (chaotic regime)
        self.chaos_iterations = 5
        
        # Structural keywords (Functor domain)
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'cannot', "n't"]
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<', 'higher', 'lower']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided', 'when']
        self.booleans = ['true', 'false', 'yes', 'no']

    def _normalize(self, text):
        return text.lower().strip()

    def _extract_structure(self, text):
        """Functor: Maps text to structural features (Category Theory)."""
        t = self._normalize(text)
        words = re.findall(r'\w+', t)
        
        features = {
            'neg_count': sum(1 for w in words if any(n in w for n in self.negations)),
            'comp_count': sum(1 for w in words if any(c in w for c in self.comparatives)),
            'cond_count': sum(1 for w in words if any(c in w for c in self.conditionals)),
            'has_number': bool(re.search(r'\d+\.?\d*', t)),
            'length': len(words),
            'bool_present': any(b in t for b in self.booleans)
        }
        
        # Extract numbers for numeric evaluation
        nums = re.findall(r'\d+\.?\d*', t)
        features['numbers'] = [float(n) for n in nums]
        
        return features

    def _chaotic_amplify(self, val):
        """Chaos: Applies logistic map to amplify small structural differences."""
        x = val
        for _ in range(self.chaos_iterations):
            x = self.r_chaos * x * (1 - x)
        return x

    def _compute_structural_score(self, prompt, candidate):
        """
        Computes consistency between prompt and candidate structures.
        Returns a base score (0-1) and a 'gradient' for SOC check.
        """
        p_feat = self._extract_structure(prompt)
        c_feat = self._extract_structure(candidate)
        
        score = 1.0
        gradient = 0.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has negation, candidate should reflect it or answer appropriately
        if p_feat['neg_count'] > 0:
            # Simple heuristic: if prompt negates, candidate shouldn't blindly affirm without context
            # Here we just check presence alignment as a proxy for logical flow
            if c_feat['neg_count'] == 0 and p_feat['neg_count'] > 1:
                gradient += 0.3
            score *= 0.9 if c_feat['neg_count'] == 0 else 1.0
            
        # 2. Numeric Evaluation
        if p_feat['has_number'] and c_feat['has_number']:
            # Check if candidate numbers are logically derived (simplified)
            # If prompt asks for comparison, candidate should have numbers
            if p_feat['comp_count'] > 0:
                if len(c_feat['numbers']) == 0:
                    gradient += 0.5
                    score *= 0.5
            # Direct numeric match bonus (heuristic for "what is 2+2?")
            if len(p_feat['numbers']) == len(c_feat['numbers']) and len(p_feat['numbers']) > 0:
                # Check magnitude similarity
                p_sum = sum(p_feat['numbers'])
                c_sum = sum(c_feat['numbers'])
                if p_sum > 0:
                    ratio = min(c_sum, p_sum) / max(c_sum, p_sum)
                    score = max(score, ratio) 
        elif p_feat['has_number'] and not c_feat['has_number']:
            # Prompt has numbers, candidate doesn't -> likely wrong unless yes/no
            if not c_feat['bool_present']:
                gradient += 0.4
                score *= 0.6

        # 3. Conditional/Logical Flow
        if p_feat['cond_count'] > 0:
            if c_feat['cond_count'] == 0 and p_feat['cond_count'] > 1:
                # Complex conditionals usually require complex answers
                gradient += 0.2
        
        # Normalize gradient to 0-1 range roughly
        gradient = min(1.0, gradient)
        
        # Apply Chaos Amplification to the structural match
        # We invert score to get 'error', amplify error, then invert back
        error = 1.0 - score
        chaotic_error = self._chaotic_amplify(error)
        chaotic_score = 1.0 - chaotic_error
        
        return max(0.0, chaotic_score), gradient

    def _ncd(self, s1, s2):
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_both - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_clean = self._normalize(prompt)
        
        # Pre-calculate prompt structure for efficiency
        p_struct = self._extract_structure(prompt)
        
        for cand in candidates:
            cand_clean = self._normalize(cand)
            
            # 1. Structural/Functorial Score
            struct_score, gradient = self._compute_structural_score(prompt, cand)
            
            # 2. SOC Avalanche Check
            # If gradient (logical inconsistency) exceeds critical threshold, trigger avalanche
            if gradient > self.critical_threshold:
                # Avalanche: drastic reduction in score
                final_score = struct_score * (1.0 - self.avalanche_penalty)
                reason = f"SOC Avalanche: Logical gradient ({gradient:.2f}) exceeded threshold. Structural reconfiguration required."
            else:
                final_score = struct_score
                reason = f"Structural consistency maintained. Gradient: {gradient:.2f}"
            
            # 3. NCD Tiebreaker (only if scores are very close or structural signal is weak)
            # We add a tiny NCD component to break ties, but keep structural primary
            ncd_val = self._ncd(prompt_clean, cand_clean)
            # NCD is distance (0=identical), we want similarity. 
            # Note: NCD is weak for reasoning, so weight is minimal (< 0.05)
            ncd_bonus = (1.0 - ncd_val) * 0.02 
            final_score += ncd_bonus
            
            # Clamp
            final_score = max(0.0, min(1.0, final_score))
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reason
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on structural alignment and SOC stability."""
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
        
        # The score already includes the SOC penalty and chaotic amplification
        score = res_list[0]['score']
        
        # Additional explicit SOC check for the wrapper
        # If the reasoning mentions "Avalanche", confidence is capped
        if "Avalanche" in res_list[0]['reasoning']:
            return min(score, 0.3) # Low confidence if system triggered critical reset
            
        return round(score, 4)