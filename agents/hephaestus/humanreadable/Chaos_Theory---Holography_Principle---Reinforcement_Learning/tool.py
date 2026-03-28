import zlib
import re
import math

class ReasoningTool:
    """
    Holographic-Chaotic RL Controller (Computational Analogy).
    
    Mechanism:
    1. Holographic Boundary (Compression): Uses zlib NCD to establish a baseline 
       similarity metric between prompt and candidate, representing the 'boundary' 
       information density.
    2. Chaotic Perturbation (Sensitivity): Instead of random noise, we apply 
       structural perturbations by extracting logical operators (negations, comparatives).
       We measure the 'Lyapunov divergence' by checking if the candidate preserves 
       the logical structure of the prompt. A high divergence (mismatch in logic) 
       penalizes the score.
    3. RL Reward Shaping: The final score is a weighted sum where structural 
       consistency (logic matching) acts as the extrinsic reward, and NCD acts as 
       the intrinsic exploration bonus/tiebreaker.
    
    This implements the 'active inference' by prioritizing candidates that maintain 
    logical coherence (low chaotic divergence) while compressing well (holographic bound).
    """

    def __init__(self):
        # Logical operators act as the 'chaotic map' sensitive points
        self.negations = ['not', 'no', 'never', 'none', 'cannot', 'dont', "don't", 'wont', "won't"]
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', '>', '<', '>=', '<=']
        self.conditionals = ['if', 'then', 'else', 'unless', 'provided']
        
    def _normalize(self, text):
        """Lowercase and remove non-alphanumeric for basic cleaning."""
        return re.sub(r'[^a-z0-9\s]', '', text.lower())

    def _extract_logic_signature(self, text):
        """Extract a vector of logical presence (Holographic Boundary Data)."""
        clean = self._normalize(text)
        words = clean.split()
        
        has_neg = any(n in words for n in self.negations) or any(n in clean for n in ['!', '!='])
        has_comp = any(c in words for c in self.comparatives) or any(c in clean for c in ['>', '<'])
        has_cond = any(c in words for c in self.conditionals)
        
        # Numeric detection
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", clean)
        has_num = len(numbers) > 0
        
        return (has_neg, has_comp, has_cond, has_num)

    def _compute_ncd(self, s1, s2):
        """Compute Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        
        max_len = max(z1, z2)
        if max_len == 0:
            return 0.0
        return (z12 - min(z1, z2)) / max_len

    def _numeric_consistency(self, prompt, candidate):
        """Check if numeric constraints are preserved (Constraint Propagation)."""
        p_nums = re.findall(r"[-+]?\d*\.\d+|\d+", prompt)
        c_nums = re.findall(r"[-+]?\d*\.\d+|\d+", candidate)
        
        if not p_nums:
            return 1.0 # No numbers to check
        
        # Simple heuristic: If prompt has numbers, candidate should likely reference magnitude or count
        # This is a rough proxy for 'understanding' the numeric constraint
        if not c_nums:
            # If prompt has numbers and candidate has none, it might be abstract, 
            # but if prompt asks for calculation, this fails. 
            # We give partial credit unless explicit comparison fails.
            return 0.8 
            
        return 1.0

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_sig = self._extract_logic_signature(prompt)
        
        for cand in candidates:
            cand_sig = self._extract_logic_signature(cand)
            
            # 1. Structural Parsing Score (The 'Lyapunov' stability check)
            # Mismatch in logical operators implies high divergence (bad)
            logic_match = sum(a == b for a, b in zip(prompt_sig, cand_sig)) / 4.0
            
            # 2. Numeric Evaluation
            num_score = self._numeric_consistency(prompt, cand)
            
            # 3. Holographic Compression (NCD) as tiebreaker/base
            # Lower NCD is better (more similar/compressible together)
            ncd = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd  # Convert distance to similarity
            
            # Combined Score: 
            # Heavily weighted towards logical consistency (Reasoning)
            # NCD acts as the 'boundary entropy' regulator
            score = (0.6 * logic_match) + (0.3 * num_score) + (0.1 * ncd_score)
            
            # Reasoning string generation
            reasoning = f"Logic match: {logic_match:.2f}, Num consistency: {num_score:.2f}, NCD: {ncd:.2f}"
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment.
        """
        evaluated = self.evaluate(prompt, [answer])
        if not evaluated:
            return 0.0
        # Normalize the score from evaluate to a confidence metric
        # Since max theoretical score in evaluate is 1.0, we can use it directly
        # but tighten the threshold for 'high confidence'
        raw_score = evaluated[0]['score']
        
        # Calibration: Map raw score to confidence
        # If logic matches perfectly, confidence is high. 
        # If NCD is high (dissimilar) but logic matches, confidence is moderate.
        return min(1.0, max(0.0, raw_score))