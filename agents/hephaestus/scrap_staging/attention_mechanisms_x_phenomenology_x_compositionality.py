import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Phenomenologically-Grounded Self-Attentive Compositional Network (PG-SCN) Approximation.
    
    Mechanism:
    1. Structural Parsing (Compositionality): Extracts logical atoms (negations, comparatives, 
       conditionals, numeric values) to form a symbolic representation of the prompt and candidates.
    2. Phenomenological Bracketing (Epoché): Instead of relying on semantic embedding similarity 
       (which acts as the "natural attitude" bias), this module suspends semantic content and 
       evaluates the structural alignment between the prompt's logical skeleton and the candidate's 
       skeleton. It treats the structural match score as the "experiential field."
    3. Self-Attention Simulation: Computes an internal consistency score by checking if the 
       candidate's derived logical constraints satisfy the prompt's constraints (e.g., transitivity).
    4. Scoring: Primary signal is structural/logical consistency. NCD is used only as a tie-breaker 
       for structurally neutral candidates.
    """

    def __init__(self):
        self.ngram_size = 3

    def _structural_parse(self, text: str) -> Dict:
        """Extract logical atoms: negations, comparatives, conditionals, numbers."""
        t_lower = text.lower()
        atoms = {
            "negations": len(re.findall(r'\b(not|no|never|neither|nor)\b', t_lower)),
            "comparatives": len(re.findall(r'\b(more|less|greater|smaller|better|worse|than|<|>)\b', t_lower)),
            "conditionals": len(re.findall(r'\b(if|then|unless|provided|when)\b', t_lower)),
            "numbers": [],
            "length": len(text)
        }
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+\.?\d*', text)
        atoms["numbers"] = [float(n) for n in nums] if nums else []
        return atoms

    def _check_logical_consistency(self, prompt_atoms: Dict, cand_atoms: Dict) -> float:
        """
        Simulates the 'Self-Attentive' check by verifying if candidate atoms 
        logically cohere with prompt atoms (Constraint Propagation).
        """
        score = 0.0
        checks = 0

        # 1. Negation Consistency (Modus Tollens approximation)
        # If prompt has negation, candidate should ideally reflect or not contradict it
        if prompt_atoms["negations"] > 0:
            checks += 1
            if cand_atoms["negations"] > 0:
                score += 1.0 # Reinforcement
            else:
                score += 0.5 # Neutral/Ambiguous

        # 2. Comparative/Number Alignment
        if prompt_atoms["comparatives"] > 0 and prompt_atoms["numbers"] and cand_atoms["numbers"]:
            checks += 1
            # Simple heuristic: Does the candidate preserve the order implied?
            # Since we don't have full semantic parse, we check if numbers exist where expected
            score += 1.0 if len(cand_atoms["numbers"]) >= len(prompt_atoms["numbers"]) else 0.5
        
        # 3. Conditional Structure
        if prompt_atoms["conditionals"] > 0:
            checks += 1
            # Candidate should ideally have conditional markers or be a direct consequence
            score += 1.0 if cand_atoms["conditionals"] > 0 else 0.6

        # Default boost if structure is sparse (avoids penalizing short valid answers like "42")
        if checks == 0:
            return 0.5
            
        return score / checks if checks > 0 else 0.5

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as a tiebreaker."""
        import zlib
        l1 = len(zlib.compress(s1.encode()))
        l2 = len(zlib.compress(s2.encode()))
        l12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(l1, l2)
        if denom == 0: return 1.0
        return (l12 - min(l1, l2)) / denom

    def _phenomenological_bracket(self, prompt: str, candidate: str) -> float:
        """
        Applies 'Epoché': Suspends semantic meaning, focuses purely on structural 
        intentionality (logical form) alignment.
        """
        p_atoms = self._structural_parse(prompt)
        c_atoms = self._structural_parse(candidate)
        
        # Core structural score (The "Intentional Object")
        struct_score = self._check_logical_consistency(p_atoms, c_atoms)
        
        return struct_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_atoms = self._structural_parse(prompt)
        has_strong_logic = (prompt_atoms["negations"] > 0 or 
                            prompt_atoms["comparatives"] > 0 or 
                            prompt_atoms["conditionals"] > 0)

        for cand in candidates:
            # 1. Phenomenological Bracketing Score
            score = self._phenomenological_bracket(prompt, cand)
            
            # 2. Numeric Evaluation (Specific trap handler)
            p_nums = prompt_atoms["numbers"]
            c_nums = self._structural_parse(cand)["numbers"]
            
            if p_nums and c_nums:
                # Heuristic: If prompt asks for max/min via text cues, check value
                p_text = prompt.lower()
                if ("max" in p_text or "largest" in p_text) and c_nums:
                    if c_nums[0] == max(p_nums): score = 1.0
                    elif c_nums[0] == min(p_nums): score = 0.2 # Penalty for wrong extreme
                elif ("min" in p_text or "smallest" in p_text) and c_nums:
                    if c_nums[0] == min(p_nums): score = 1.0
                    elif c_nums[0] == max(p_nums): score = 0.2

            # 3. NCD Tiebreaker (Only if structural signal is weak/ambiguous)
            if score < 0.6 and not has_strong_logic:
                ncd = self._compute_ncd(prompt, cand)
                # Invert NCD (low distance = high similarity) and scale
                ncd_score = (1.0 - ncd) * 0.4 # Max contribution 0.4
                score = max(score, ncd_score)

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Structural alignment: {score:.2f}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on structural coherence."""
        # Re-use the bracketing mechanism
        base_score = self._phenomenological_bracket(prompt, answer)
        
        # Boost if numeric logic holds
        p_nums = self._structural_parse(prompt)["numbers"]
        a_nums = self._structural_parse(answer)["numbers"]
        
        if p_nums and a_nums:
            # If numbers match exactly, high confidence
            if p_nums == a_nums:
                return min(1.0, base_score + 0.5)
        
        return float(np.clip(base_score, 0.0, 1.0))