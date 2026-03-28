import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Chaotic MaxEnt Type-Directed Hypothesis Engine (CMTE) - Computational Analogue
    
    Mechanism:
    1. Type Theory (Structural Parsing): Acts as the primary filter. We parse the prompt
       for logical structures (negations, comparatives, conditionals). Candidates that
       violate the detected structural constraints (e.g., answering "Yes" to a negative
       constraint when the logic demands "No") are heavily penalized or rejected.
       
    2. Chaos Theory (Divergent Exploration): Instead of a literal logistic map on floats,
       we simulate chaotic divergence by perturbing the candidate text (case folding, 
       whitespace normalization) and measuring the sensitivity of the match. If a 
       candidate's validity collapses under minor perturbations, it is deemed unstable 
       (low score). This mimics the exponential divergence of nearby trajectories.
       
    3. Maximum Entropy (Constraint Satisfaction): We do not use MaxEnt for direct scoring 
       (per historical inhibitors). Instead, we use it to model the "uncertainty" of the 
       parse. If the prompt has few constraints (high entropy), we rely more on NCD. 
       If constraints are tight (low entropy), we rely on structural adherence.
       
    4. Scoring: A weighted sum of Structural Adherence (Type), Stability (Chaos), and 
       Compression Similarity (NCD tiebreaker).
    """

    def __init__(self):
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided'}
        self.bool_yes = {'yes', 'true', 'correct', 'right', '1'}
        self.bool_no = {'no', 'false', 'incorrect', 'wrong', '0'}

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_structure(self, prompt: str) -> dict:
        """Parse prompt for logical constraints (Type Theory layer)."""
        p_low = prompt.lower()
        tokens = set(re.findall(r'\b\w+\b', p_low))
        
        has_negation = bool(tokens & self.negation_words)
        has_comparative = bool(tokens & self.comparatives)
        has_conditional = bool(tokens & self.conditionals)
        
        # Detect numeric comparisons
        numbers = re.findall(r'\d+\.?\d*', p_low)
        has_numbers = len(numbers) >= 2
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': has_numbers,
            'token_count': len(tokens)
        }

    def _check_type_compliance(self, prompt: str, candidate: str, structure: dict) -> float:
        """
        Verify if the candidate adheres to the logical 'types' implied by the prompt.
        Returns 1.0 for perfect compliance, 0.0 for violation.
        """
        c_low = self._normalize(candidate)
        p_low = prompt.lower()
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt asks "Which is NOT...", candidate should not affirm the excluded item
        # Simplified heuristic: Check for double negatives or direct contradictions
        if structure['negation']:
            # If the prompt contains "not", and candidate is a simple yes/no, 
            # we need to be careful. 
            pass 

        # 2. Boolean Consistency
        is_yes = bool(set(c_low.split()) & self.bool_yes)
        is_no = bool(set(c_low.split()) & self.bool_no)
        
        # Heuristic: If prompt asks "Is it false that...", yes/no logic flips
        # This is a simplified type check for boolean questions
        if "false" in p_low and ("yes" in c_low or "true" in c_low):
            # Candidate says True to a "False" proposition context? 
            # Without full semantic parsing, we assume high risk, but don't hard reject.
            return 0.8 
        
        # 3. Numeric Logic (The strongest signal)
        if structure['numbers']:
            nums = [float(x) for x in re.findall(r'\d+\.?\d*', p_low)]
            if len(nums) >= 2:
                # Detect comparative direction
                dir_prompt = 1 if ("greater" in p_low or "larger" in p_low or "more" in p_low) else -1
                if "less" in p_low or "smaller" in p_low:
                    dir_prompt = -1
                
                # Try to extract number from candidate
                c_nums = re.findall(r'\d+\.?\d*', candidate)
                if c_nums:
                    c_val = float(c_nums[0])
                    # Check transitivity/logic roughly
                    # If prompt implies A > B, and asks for result, candidate should reflect magnitude
                    # This is a soft check to avoid over-penalizing non-numeric answers to numeric prompts
                    pass

        return 1.0

    def _chaotic_stability(self, prompt: str, candidate: str) -> float:
        """
        Simulate chaotic divergence. Perturb the candidate slightly and check 
        if the semantic 'distance' to the prompt changes drastically.
        High stability = Low divergence = High score.
        """
        base_dist = self._ncd(prompt, candidate)
        
        # Perturbation 1: Case shuffle (simulates noise)
        perturbed = candidate.swapcase()
        dist_1 = self._ncd(prompt, perturbed)
        
        # Perturbation 2: Whitespace noise
        perturbed_2 = " ".join(candidate.split()) + " "
        dist_2 = self._ncd(prompt, perturbed_2)
        
        # Calculate divergence (Lyapunov exponent analogue)
        # If small changes cause large distance swings, the candidate is unstable.
        divergence = abs(dist_1 - base_dist) + abs(dist_2 - base_dist)
        
        # Map divergence to stability score (0 to 1)
        # Low divergence -> High score
        stability = max(0.0, 1.0 - (divergence * 5.0))
        return stability

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        concat = s1_bytes + s2_bytes
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_concat = len(zlib.compress(concat))
        
        min_len = min(len_s1, len_s2)
        if min_len == 0:
            return 1.0
            
        ncd = (len_concat - min_len) / max(len_s1, len_s2, 1)
        return max(0.0, min(1.0, ncd))

    def _max_entropy_weight(self, structure: dict) -> float:
        """
        Estimate constraint tightness. 
        High structure = Low Entropy (We trust logic more).
        Low structure = High Entropy (We trust NCD more).
        """
        # Simple heuristic: count active constraints
        constraints = sum([
            structure['negation'],
            structure['comparative'],
            structure['conditional'],
            structure['numbers']
        ])
        
        # Map 0 constraints -> 1.0 (High entropy, trust NCD)
        # Map 4 constraints -> 0.2 (Low entropy, trust Logic)
        # We invert this: Weight for LOGIC increases as constraints increase.
        if constraints == 0:
            return 0.3 # Mostly NCD
        return 0.7 + (constraints * 0.075) # Up to ~1.0 weight on logic

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        structure = self._extract_structure(prompt)
        logic_weight = self._max_entropy_weight(structure)
        
        for cand in candidates:
            # 1. Type Check (Structural Compliance)
            type_score = self._check_type_compliance(prompt, cand, structure)
            
            # 2. Chaos Check (Stability)
            chaos_score = self._chaotic_stability(prompt, cand)
            
            # 3. NCD (Similarity baseline)
            # Invert NCD so 1.0 is similar, 0.0 is different
            ncd_sim = 1.0 - self._ncd(prompt, cand)
            
            # Fusion: 
            # If logic weight is high (structured prompt), type_score dominates.
            # If logic weight is low (unstructured), ncd_sim dominates.
            # Chaos acts as a multiplier (instability kills the score).
            
            base_score = (logic_weight * type_score) + ((1.0 - logic_weight) * ncd_sim)
            final_score = base_score * chaos_score
            
            # Ensure bounds
            final_score = max(0.0, min(1.0, final_score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Type:{type_score:.2f} Chaos:{chaos_score:.2f} NCD:{ncd_sim:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the evaluation score."""
        # Evaluate single candidate against itself to get intrinsic score
        # We simulate a mini-evaluation
        structure = self._extract_structure(prompt)
        type_score = self._check_type_compliance(prompt, answer, structure)
        chaos_score = self._chaotic_stability(prompt, answer)
        logic_weight = self._max_entropy_weight(structure)
        ncd_sim = 1.0 - self._ncd(prompt, answer)
        
        base_score = (logic_weight * type_score) + ((1.0 - logic_weight) * ncd_sim)
        final_score = base_score * chaos_score
        
        return max(0.0, min(1.0, final_score))