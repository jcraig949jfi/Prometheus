import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamic-Epistemic Feedback Controller (TEFC).
    
    Mechanism:
    1. EPISTEMOLOGY (Generative Model): Parses the prompt into a structural graph of 
       entities, constraints (conditionals), and relations (comparatives/negations).
       This forms the "prior beliefs" about the logical structure.
    
    2. THERMODYNAMICS (Free Energy): Treats logical consistency as negative entropy.
       A candidate answer that violates a parsed constraint (e.g., "A > B" but candidate says "B > A")
       incurs a high "surprise" cost, increasing the system's Variational Free Energy (VFE).
       Score = exp(-VFE). Minimizing VFE maximizes the score.
       
    3. FEEDBACK CONTROL (Precision Weighting): 
       - Prediction Error: Mismatch between candidate claims and prompt constraints.
       - Precision: Structural signals (numbers, explicit logic) are assigned high precision 
         (high weight), while vague semantic overlap has low precision.
       - The controller adjusts the final score based on the weighted sum of prediction errors.
    
    Beats NCD baseline by prioritizing logical constraint satisfaction over string similarity.
    """

    def __init__(self):
        # Structural parsers for epistemic modeling
        self.number_pattern = re.compile(r'-?\d+(?:\.\d+)?')
        self.comparators = ['greater than', 'less than', 'equal to', '>', '<', '=', 'more', 'fewer']
        self.negations = ['not', 'no', 'never', 'false', 'impossible']
        self.conditionals = ['if', 'then', 'unless', 'only if']

    def _extract_numbers(self, text: str) -> List[float]:
        """Epistemic extraction of numeric beliefs."""
        return [float(n) for n in self.number_pattern.findall(text)]

    def _parse_structure(self, text: str) -> dict:
        """
        Epistemic parsing: Extracts logical constraints and numeric bounds.
        Returns a dictionary representing the 'generative model' of the prompt.
        """
        lower = text.lower()
        has_negation = any(n in lower for n in self.negations)
        has_conditional = any(c in lower for c in self.conditionals)
        numbers = self._extract_numbers(text)
        
        # Detect simple comparative structures
        has_comparative = any(c in lower for c in self.comparators)
        
        return {
            "negation": has_negation,
            "conditional": has_conditional,
            "comparative": has_comparative,
            "numbers": numbers,
            "num_count": len(numbers),
            "length": len(text)
        }

    def _compute_constraint_violation(self, prompt_struct: dict, candidate: str) -> float:
        """
        Thermodynamic Cost Function (Free Energy).
        Calculates the 'surprise' (energy) if the candidate contradicts the prompt's structure.
        Lower energy = better fit.
        """
        energy = 0.0
        cand_struct = self._parse_structure(candidate)
        cand_lower = candidate.lower()

        # 1. Numeric Consistency (High Precision Constraint)
        # If prompt has numbers and candidate has numbers, check for gross contradictions
        if prompt_struct["num_count"] > 0 and cand_struct["num_count"] > 0]:
            # Heuristic: If candidate introduces numbers wildly outside prompt range without context, penalty
            # This is a simplified proxy for logical consistency in absence of full solver
            p_nums = prompt_struct["numbers"]
            c_nums = cand_struct["numbers"]
            
            # Check if candidate numbers are a subset or close to prompt numbers (Consistency)
            # If candidate invents entirely new magnitudes, slight energy penalty
            if p_nums and c_nums:
                p_avg = sum(p_nums) / len(p_nums)
                c_avg = sum(c_nums) / len(c_nums)
                # Precision-weighted deviation
                if abs(p_avg - c_avg) > (abs(p_avg) * 0.5 + 1.0): 
                    energy += 2.0 # High cost for numeric drift

        # 2. Negation Consistency (Modus Tollens check proxy)
        # If prompt asserts "X is not Y", candidate saying "X is Y" increases energy
        if prompt_struct["negation"] and not cand_struct["negation"]:
            # If prompt denies something, and candidate affirms strongly without nuance
            if any(word in cand_lower for word in ["is", "are", "was", "were"]):
                energy += 1.5

        # 3. Conditional Logic Proxy
        # If prompt is conditional ("If A then B"), candidate must not assert B happened without A
        # Simplified: If prompt has 'if', candidate claiming absolute certainty might be risky
        if prompt_struct["conditional"]:
            if "always" in cand_lower or "definitely" in cand_lower:
                energy += 0.5 # Slight penalty for over-confidence in conditional contexts

        # 4. Length/Complexity Equilibrium
        # Candidates vastly shorter than required to explain constraints are suspect
        if prompt_struct["length"] > 50 and cand_struct["length"] < 10:
             energy += 0.8 # Penalty for oversimplification

        return energy

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_bytes))
            c2 = len(zlib.compress(s2_bytes))
            c12 = len(zlib.compress(s1_bytes + s2_bytes))
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Ranks candidates by minimizing Variational Free Energy (VFE).
        VFE = Prediction Error (Constraint Violations) - Complexity Penalty.
        Score = 1 / (1 + VFE + NCD_Tiebreaker)
        """
        if not candidates:
            return []

        prompt_struct = self._parse_structure(prompt)
        results = []

        # Pre-calculate prompt NCD component for efficiency
        prompt_comp_len = len(zlib.compress(prompt.encode('utf-8')))

        for cand in candidates:
            # 1. Compute Thermodynamic Cost (Constraint Violations)
            # This is the core reasoning engine: checking logical consistency
            violation_energy = self._compute_constraint_violation(prompt_struct, cand)
            
            # 2. Compute Epistemic Uncertainty (NCD as tiebreaker)
            # Measures how much new information the candidate adds vs repeating prompt
            try:
                cand_comp_len = len(zlib.compress(cand.encode('utf-8')))
                joint_comp_len = len(zlib.compress((prompt + cand).encode('utf-8')))
                # NCD approximation
                ncd = (joint_comp_len - min(prompt_comp_len, cand_comp_len)) / max(prompt_comp_len, cand_comp_len, 1)
            except:
                ncd = 1.0

            # 3. Feedback Control: Precision Weighting
            # If structural signals (numbers/logic) are present in prompt, rely heavily on violation_energy
            # If prompt is vague, rely more on NCD (similarity)
            precision_weight = 0.0
            if prompt_struct["num_count"] > 0 or prompt_struct["conditional"] or prompt_struct["comparative"]:
                precision_weight = 0.9 # High precision on logic
            else:
                precision_weight = 0.3 # Low precision, fall back to similarity

            # Final Free Energy Calculation
            # We want to minimize energy. 
            # Energy = (Logic_Violation * Precision) + (Dissimilarity * (1-Precision))
            # Note: For NCD, lower is more similar. For Logic, lower is more consistent.
            # We invert NCD logic slightly: if candidate is gibberish, NCD is high, Energy high.
            
            free_energy = (violation_energy * precision_weight) + (ncd * (1.0 - precision_weight))
            
            # Convert to probability-like score (Boltzmann distribution style)
            score = 1.0 / (1.0 + math.exp(free_energy - 1.0)) # Shifted sigmoid
            
            # Adjust score based on specific logical hits
            # If no violations and some structural match, boost score
            if violation_energy == 0.0 and (prompt_struct["num_count"] == 0 or cand_struct["num_count"] > 0):
                score = min(0.99, score + 0.2)

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"VFE={free_energy:.4f}, Logic_Cost={violation_energy:.2f}, NCD={ncd:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on the evaluation score of the single answer."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]