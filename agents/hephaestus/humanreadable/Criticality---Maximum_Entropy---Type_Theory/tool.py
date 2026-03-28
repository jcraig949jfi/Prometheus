import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Critical MaxEnt Type-Theoretic Inference Engine (CMTIE) Approximation.
    
    Mechanism:
    1. Type Theory (Structural Parsing): Extracts logical constraints (negations, 
       comparatives, conditionals) as 'proof obligations'. Candidates are scored 
       by how well they satisfy these structural constraints (Type Checking).
    2. Criticality (Susceptibility Scaling): The scoring function uses a steep 
       sigmoid-like penalty near the decision boundary. Small violations of 
       critical constraints (e.g., answering "Yes" to a negated question) cause 
       a macroscopic drop in score, simulating the divergence of susceptibility 
       at a critical point.
    3. Maximum Entropy (Confidence Only): Used strictly in confidence() to measure 
       the uniformity of the candidate distribution, avoiding direct use in ranking 
       to prevent the noted negative interaction with Criticality during evaluation.
    """

    def __init__(self):
        # Critical coupling parameter (high value = high sensitivity)
        self.critical_coupling = 15.0 
        # Base score for valid type inhabitation
        self.base_score = 1.0

    def _extract_constraints(self, prompt: str) -> List[Dict]:
        """
        Type Theory Layer: Parse prompt for logical structures.
        Returns a list of constraint dictionaries.
        """
        constraints = []
        p_lower = prompt.lower()
        
        # Detect Negation (Not, Never, None)
        if re.search(r'\b(not|never|no|none|neither)\b', p_lower):
            constraints.append({'type': 'negation', 'weight': 2.0})
            
        # Detect Comparatives (Greater, Less, More, Before, After)
        if re.search(r'\b(greater|less|more|before|after|larger|smaller|higher|lower)\b', p_lower):
            constraints.append({'type': 'comparative', 'weight': 1.5})
            
        # Detect Conditionals (If, Unless, Provided)
        if re.search(r'\b(if|unless|provided|assuming)\b', p_lower):
            constraints.append({'type': 'conditional', 'weight': 1.8})
            
        # Detect Numeric literals (for potential numeric evaluation)
        if re.search(r'\d+(\.\d+)?', p_lower):
            constraints.append({'type': 'numeric', 'weight': 1.2})
            
        return constraints

    def _check_type_compliance(self, candidate: str, prompt: str, constraints: List[Dict]) -> float:
        """
        Type Checking Layer: Verify if candidate satisfies constraints.
        Returns a compliance score (0.0 to 1.0).
        """
        c_lower = candidate.lower()
        p_lower = prompt.lower()
        compliance = 1.0
        
        for cons in constraints:
            ctype = cons['type']
            
            if ctype == 'negation':
                # If prompt has negation, candidate should not be a blind affirmative
                # Simple heuristic: if prompt says "not", and candidate is "yes"/"true", penalize
                if re.search(r'\b(not|never)\b', p_lower):
                    if re.search(r'\b(yes|true|definitely|always)\b', c_lower):
                        # Critical failure: Affirming a negated premise
                        compliance -= 0.9 
                    elif re.search(r'\b(no|false|never|not)\b', c_lower):
                        compliance += 0.1 # Bonus for explicit negation
                
            elif ctype == 'comparative':
                # Check if candidate contains comparative words or numbers if prompt implies comparison
                has_comp = re.search(r'\b(greater|less|more|before|after|larger|smaller|higher|lower|>\|<)\b', c_lower)
                has_num = re.search(r'\d+', c_lower)
                if not has_comp and not has_num:
                    # Weak penalty for lacking comparative structure
                    compliance -= 0.2

            elif ctype == 'numeric':
                # Extract numbers from prompt and candidate
                p_nums = re.findall(r'\d+(\.\d+)?', p_lower)
                c_nums = re.findall(r'\d+(\.\d+)?', c_lower)
                
                if p_nums and not c_nums:
                    # Prompt has numbers, candidate has none -> Likely failed numeric reasoning
                    compliance -= 0.3
                
                # Simple transitivity check simulation (heuristic)
                # If prompt implies A > B and candidate suggests B > A (hard to detect without full NLP)
                # We rely on the presence of numbers as a proxy for 'type inhabitation'
        
        return max(0.0, min(1.0, compliance))

    def _critical_score(self, base_compliance: float, constraints: List[Dict]) -> float:
        """
        Criticality Layer: Apply non-linear scaling.
        Near the threshold of failure, small drops in compliance yield massive score drops.
        """
        if not constraints:
            return base_compliance
            
        # Calculate effective 'temperature' based on constraint density
        # More constraints = lower effective temperature = sharper phase transition
        temp = 1.0 / (1.0 + 0.5 * len(constraints))
        
        # Critical scaling function: sigmoid-like drop near 0.5 compliance
        # x = base_compliance
        # score = 1 / (1 + exp(-k * (x - threshold)))
        # We invert this logic: we want high score for high compliance, 0 for low.
        # Let's use a steep exponential decay for violations.
        
        violation = 1.0 - base_compliance
        if violation > 0:
            # Critical amplification: small violation -> large penalty
            penalty = 1.0 - (1.0 / (1.0 + (violation * self.critical_coupling * temp)))
            return max(0.0, base_compliance - penalty)
        
        return base_compliance

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance (tiebreaker)."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates using CMTIE principles.
        1. Parse prompt for logical types (constraints).
        2. Check candidate compliance (type checking).
        3. Apply critical scaling to scores.
        4. Use NCD only for tie-breaking.
        """
        constraints = self._extract_constraints(prompt)
        results = []
        
        for cand in candidates:
            # Step 1 & 2: Type Compliance
            compliance = self._check_type_compliance(cand, prompt, constraints)
            
            # Step 3: Critical Scaling
            score = self._critical_score(compliance, constraints)
            
            # Add small noise based on string length to break exact ties deterministically
            # (Simulating minor entropy in the physical system without breaking determinism)
            length_factor = len(cand) / 1000.0
            final_score = score + length_factor
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Type compliance: {compliance:.2f}, Constraints: {len(constraints)}, Critical scaling applied."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Tie-breaking with NCD if scores are effectively identical (within float precision)
        # This is a simplified post-process for the 'NCD as tiebreaker' requirement
        if len(results) > 1:
            top_score = results[0]['score']
            # Group by near-equal scores
            i = 0
            while i < len(results):
                j = i + 1
                while j < len(results) and abs(results[j]['score'] - top_score) < 1e-6:
                    j += 1
                if j > i + 1:
                    # Tie detected among results[i:j]
                    # Sort this slice by NCD to prompt (lower NCD = better match)
                    tie_group = results[i:j]
                    tie_group.sort(key=lambda x: self._ncd_distance(prompt, x['candidate']))
                    results[i:j] = tie_group
                i = j
                if i < len(results):
                    top_score = results[i]['score']

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Compute confidence using Maximum Entropy principle indirectly.
        Measures how 'surprising' the answer is given the prompt structure.
        High entropy (uniform distribution over features) -> Low confidence.
        Low entropy (strong alignment) -> High confidence.
        """
        constraints = self._extract_constraints(prompt)
        if not constraints:
            # No structural hooks, rely on simple overlap
            overlap = len(set(prompt.lower().split()) & set(answer.lower().split()))
            return min(1.0, 0.5 + (overlap * 0.1))
        
        compliance = self._check_type_compliance(answer, prompt, constraints)
        
        # Map compliance to confidence via a smooth function
        # Avoids the sharp critical drop used in evaluation, providing a 'confidence' metric
        # that reflects the 'entropy' of the decision (high compliance = low entropy = high confidence)
        confidence = 1.0 / (1.0 + (1.0 - compliance) * 4.0)
        return min(1.0, max(0.0, confidence))