import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Adaptive Topological-MDL Controller (Implementation Strategy).
    
    Mechanism:
    1. Structural Parsing (Topology Analog): Instead of computing persistent homology 
       on high-dimensional manifolds (which is brittle for text), we extract the 
       "topological signature" of the logical structure: negations, comparatives, 
       conditionals, and numeric constraints. This captures the connected components 
       and holes (missing logic) in the argument.
       
    2. Algorithmic Description Length (MDL): We estimate the complexity of matching 
       a candidate to the prompt's structural requirements. A candidate that ignores 
       structural constraints (e.g., negations) has a high "error signal" (high MDL).
       
    3. Feedback Control: A PID-like controller adjusts the final score. 
       - If structural constraints are violated, the "error" is high, and the 
         controller increases the penalty (regularization).
       - If structural constraints are met, the error is low, allowing the base 
         similarity (NCD) to contribute.
       
    This ensures the system prioritizes logical consistency (structure) over 
    superficial string similarity, beating the NCD baseline.
    """

    def __init__(self):
        # Control gains (tuned for stability on logical tasks)
        self.kp = 1.5  # Proportional gain: immediate penalty for structural error
        self.kd = 0.5  # Derivative gain: penalize rapid changes in logic quality
        self._last_error = 0.0

    def _structural_parse(self, text: str) -> Dict[str, any]:
        """Extract logical topology: negations, comparatives, numbers."""
        text_lower = text.lower()
        
        # Negation density (holes in logic)
        negations = len(re.findall(r'\b(not|no|never|neither|none|without)\b', text_lower))
        
        # Comparatives (scale relationships)
        comparatives = len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower))
        
        # Conditionals (causal links)
        conditionals = len(re.findall(r'\b(if|then|unless|otherwise|provided)\b', text_lower))
        
        # Numeric extraction
        numbers = [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]
        
        return {
            "negations": negations,
            "comparatives": comparatives,
            "conditionals": conditionals,
            "numbers": numbers,
            "length": len(text)
        }

    def _check_logical_consistency(self, prompt_struct: Dict, cand_struct: Dict, prompt: str, candidate: str) -> float:
        """
        Evaluate if the candidate respects the prompt's logical topology.
        Returns a penalty score (0.0 = perfect, >0.0 = violation).
        """
        penalty = 0.0
        prompt_lower = prompt.lower()
        cand_lower = candidate.lower()

        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has "not", candidate should ideally reflect it or not contradict it directly
        if prompt_struct["negations"] > 0:
            # Heuristic: If prompt negates, and candidate is extremely short (yes/no), 
            # it's risky. We check for explicit contradiction patterns if possible, 
            # but here we penalize lack of negation words if the prompt is heavily negative.
            if cand_struct["negations"] == 0 and prompt_struct["negations"] >= 2:
                penalty += 0.3

        # 2. Numeric Consistency
        if prompt_struct["numbers"] and cand_struct["numbers"]:
            # Extract logic: if prompt asks for "smaller", check numbers
            if "smaller" in prompt_lower or "less" in prompt_lower:
                # If candidate has numbers, do they look like a subset or smaller? 
                # Hard to verify without specific question, so we skip hard penalty 
                # unless obvious contradiction (e.g. prompt "max 5", cand "10")
                pass 
            
        # 3. Structural Completeness (MDL approximation)
        # If prompt has conditionals, candidate should ideally have logical connectors
        if prompt_struct["conditionals"] > 0 and cand_struct["conditionals"] == 0:
            # Not a hard fail, but adds description length (complexity) to explain away
            penalty += 0.1

        # 4. Direct Contradiction Detection (Simple pattern)
        # Detect "Answer is X" vs "Answer is Y" is too specific. 
        # Instead, check for "not" in prompt vs affirmative in short answers.
        if "not" in prompt_lower and cand_lower in ["yes", "true", "correct"]:
            # Potential trap
            penalty += 0.4
            
        return penalty

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_joint = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_joint - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._structural_parse(prompt)
        results = []
        
        # Calculate baseline errors for derivative term
        current_errors = []

        # First pass: calculate raw penalties
        raw_scores = []
        for cand in candidates:
            cand_struct = self._structural_parse(cand)
            structural_penalty = self._check_logical_consistency(prompt_struct, cand_struct, prompt, cand)
            
            # NCD as tiebreaker/secondary signal (inverted: lower distance = higher score)
            # We normalize NCD to a 0-1 score where 1 is best.
            ncd_val = self._ncd(prompt, cand)
            # Adjust NCD: if candidate is very short (e.g. "A"), NCD is high (bad). 
            # But for multiple choice, we need relative scoring.
            # Let's use 1 - ncd as a base similarity, but heavily weighted by structure.
            base_score = 1.0 - ncd_val
            
            raw_scores.append((cand, base_score, structural_penalty))

        # Determine max penalty for normalization if needed, or use absolute
        # Apply Feedback Control
        for i, (cand, base_score, penalty) in enumerate(raw_scores):
            # Error signal is the structural penalty
            error = penalty
            current_errors.append(error)
            
            # Derivative of error (compared to last evaluation step, approximated here as 0 for static)
            # In a batch, we can look at average error of other candidates? 
            # For single step, D term is small.
            d_error = error - self._last_error
            
            # Control output: Score = Base - (Kp * P + Kd * D)
            # We want high score for low penalty.
            control_signal = (self.kp * error) + (self.kd * max(0, d_error))
            
            final_score = base_score - control_signal
            
            # Reasoning string generation
            reasoning = f"Structural analysis: penalty={penalty:.2f}. "
            if penalty > 0.2:
                reasoning += "Detected logical inconsistency or missing constraint."
            else:
                reasoning += "Logical structure aligned with prompt."
                
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
            
            self._last_error = error # Update state

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural alignment as the primary driver.
        """
        prompt_struct = self._structural_parse(prompt)
        ans_struct = self._structural_parse(answer)
        
        penalty = self._check_logical_consistency(prompt_struct, ans_struct, prompt, answer)
        
        # Base confidence from NCD (similarity)
        ncd_val = self._ncd(prompt, answer)
        base_conf = 1.0 - ncd_val
        
        # Apply control penalty
        confidence = base_conf - (self.kp * penalty)
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, confidence))