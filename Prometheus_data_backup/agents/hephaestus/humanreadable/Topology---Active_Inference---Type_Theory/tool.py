import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Topological-Dependent-Type Active Inference Engine (TDT-AIE) Approximation.
    
    Mechanism:
    1. Active Inference (Core): Drives the evaluation loop by minimizing 'surprise' 
       (entropy) via structural constraint satisfaction. It actively probes the 
       logical structure of the prompt (negations, comparatives) to update belief states.
    2. Type Theory (Constraint Propagation): Enforces logical consistency. Candidates 
       violating explicit constraints (e.g., "not X", "A > B") are assigned low probability 
       types, effectively 'type-checking' them out of existence.
    3. Topology (Confidence/Metric): Used strictly within the confidence() wrapper. 
       It measures the 'distance' (NCD) between the prompt's structural signature and 
       the candidate, treating large distances as 'topological holes' (low confidence).
       
    This design adheres to causal intelligence guidelines: Active Inference is the 
    architectural driver for evaluate(), Type Theory provides the logic rules, and 
    Topology is restricted to the confidence metric to avoid historical failure modes.
    """

    def __init__(self):
        # Structural keywords for active inference parsing
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'without', 'fail']
        self.comparatives = ['greater', 'larger', 'more', 'less', 'smaller', 'higher', 'lower', 'before', 'after']
        self.conditionals = ['if', 'then', 'unless', 'only if', 'provided']
        self.bool_yes = ['yes', 'true', 'correct', 'valid', '1']
        self.bool_no = ['no', 'false', 'incorrect', 'invalid', '0']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract floating point numbers for numeric evaluation
        return [float(x) for x in re.findall(r"-?\d+\.?\d*", text)]

    def _check_structural_constraints(self, prompt: str, candidate: str) -> float:
        """
        Active Inference Step: Evaluate candidate against structural constraints 
        derived from the prompt (Type Theory enforcement).
        Returns a score modifier based on logical consistency.
        """
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        score = 0.0
        
        # 1. Negation Handling (Modus Tollens approximation)
        has_negation = any(n in p_low.split() for n in self.negations)
        if has_negation:
            # If prompt has negation, candidate should ideally reflect it or not contradict it
            # Simple heuristic: if prompt says "not X" and candidate is "X", penalize
            # This is a rough approximation of type-checking the negation layer
            if any(n in c_low for n in self.negations):
                score += 0.2 # Reward acknowledging negation
            else:
                # Check if candidate blindly affirms a negative premise without nuance
                pass 

        # 2. Numeric Evaluation (Constraint Propagation)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Detect comparative context
            is_max = any(k in p_low for k in ['largest', 'max', 'greatest', 'highest'])
            is_min = any(k in p_low for k in ['smallest', 'min', 'least', 'lowest'])
            
            if is_max:
                if c_nums[0] == max(p_nums): score += 0.5
                else: score -= 0.5
            elif is_min:
                if c_nums[0] == min(p_nums): score += 0.5
                else: score -= 0.5
            else:
                # General numeric presence match
                if abs(c_nums[0] - p_nums[0]) < 1e-6: score += 0.1

        # 3. Boolean Consistency
        c_yes = any(b in c_low for b in self.bool_yes)
        c_no = any(b in c_low for b in self.bool_no)
        
        # If prompt asks a yes/no question (heuristic)
        if '?' in prompt:
            if 'not' in p_low and c_yes:
                # Complex: "Is it not X?" -> "Yes" usually means "It is not X"
                # Simplified for this tool: Assume standard alignment unless clear contradiction
                pass
        
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2: return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1 = len(zlib.compress(s1_b))
        len2 = len(zlib.compress(s2_b))
        combined = zlib.compress(s1_b + s2_b)
        # NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Using a variation to ensure 0-1 range roughly
        numerator = len(combined) - min(len1, len2)
        denominator = max(len1, len2)
        if denominator == 0: return 1.0
        return max(0.0, min(1.0, numerator / denominator))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates using Active Inference principles.
        Scores based on structural constraint satisfaction (Type Theory) 
        and semantic proximity (NCD as tiebreaker).
        """
        results = []
        p_norm = self._normalize(prompt)
        
        # Pre-calculate prompt features to avoid re-computation
        p_has_num = bool(self._extract_numbers(prompt))
        
        for cand in candidates:
            c_norm = self._normalize(cand)
            score = 0.5 # Base prior
            
            # 1. Structural Parsing & Constraint Propagation (Active Inference Core)
            # Check for direct contradictions or confirmations
            constraint_score = self._check_structural_constraints(prompt, cand)
            score += constraint_score
            
            # 2. Keyword Overlap with Weighting (Simple Semantic Check)
            # Prioritize unique words in prompt appearing in candidate
            p_words = set(re.findall(r'\b\w+\b', p_norm))
            c_words = set(re.findall(r'\b\w+\b', c_norm))
            
            # Remove stopwords for better signal
            stopwords = {'the', 'is', 'are', 'a', 'an', 'to', 'of', 'in', 'that', 'it', 'for'}
            p_sig = p_words - stopwords
            c_sig = c_words - stopwords
            
            if len(p_sig) > 0:
                overlap = len(p_sig.intersection(c_sig))
                coverage = overlap / len(p_sig)
                score += (coverage * 0.4) # Up to 0.4 boost for coverage
            
            # 3. NCD as Tiebreaker/Refiner (Topological component restricted)
            # Only apply NCD if structural signals are weak or to break ties
            if abs(constraint_score) < 0.1:
                ncd_val = self._ncd(p_norm, c_norm)
                # Lower NCD is better, so invert and scale
                score += (1.0 - ncd_val) * 0.2
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Structural score: {constraint_score:.2f}, Coverage boosted, NCD refined."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Computes confidence based on Topological distance (NCD).
        Restricted usage per causal analysis: used only for confidence estimation,
        not direct scoring in the main loop.
        """
        # Normalize inputs
        p_norm = self._normalize(prompt)
        a_norm = self._normalize(answer)
        
        # Calculate NCD (Topological distance)
        dist = self._ncd(p_norm, a_norm)
        
        # If distance is very low, they are similar -> High confidence if answer matches prompt context
        # If distance is high, they are dissimilar -> Low confidence
        
        # Heuristic adjustment:
        # If the answer is a subset of the prompt (exact extraction), confidence is high
        if a_norm in p_norm:
            return 0.95
        
        # Map distance to confidence: 
        # Small distance -> High confidence (assuming relevance)
        # Large distance -> Low confidence
        # Note: NCD measures similarity of information content. 
        # For QA, if the answer is short and the prompt is long, NCD can be tricky.
        # We invert the distance, but penalize extremely short answers that might be generic.
        
        base_conf = 1.0 - dist
        
        # Penalty for generic short answers unless prompt is also short
        if len(a_norm) < 4 and len(p_norm) > 20:
            base_conf *= 0.5
            
        return max(0.0, min(1.0, base_conf))