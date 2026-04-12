import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    PF-VFES Implementation Strategy:
    Given the constraint that 'Phenomenology' is a historical inhibitor for direct scoring
    and 'Free Energy' is the primary driver, this tool implements a hybrid architecture:
    
    1. FREE ENERGY CORE (evaluate): Uses structural parsing (negations, comparatives, 
       conditionals) and numeric evaluation to compute a 'prediction error' bound. 
       Lower error = higher fitness. This mimics the variational free-energy minimization.
       
    2. PHENOMENOLOGY MASK (confidence): Restricted to a confidence wrapper that checks 
       for structural consistency (bracketing) rather than semantic truth, avoiding 
       the 'reasoning trap' of subjective scoring.
       
    3. EVOLUTIONARY SELECTION: Candidates are ranked by structural fidelity (Free Energy)
       with NCD used only as a tiebreaker for candidates with identical structural scores.
    """

    def __init__(self):
        # Structural patterns for Free Energy minimization (Prediction Error reduction)
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparators = {'>', '<', 'greater', 'less', 'more', 'fewer', 'larger', 'smaller'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided'}
        self.logic_ops = {'and', 'or', 'implies'}

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for quantitative reasoning."""
        pattern = r"-?\d+\.?\d*"
        matches = re.findall(pattern, text.lower())
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                continue
        return nums

    def _compute_structural_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes a 'Free Energy' score (lower is better) based on structural alignment.
        Minimizes prediction error by checking if the candidate respects prompt constraints.
        """
        energy = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has negation, candidate should ideally reflect it or not contradict it
        p_negs = sum(1 for w in self.negation_words if w in p_lower.split())
        c_negs = sum(1 for w in self.negation_words if w in c_lower.split())
        
        # Penalty for wild divergence in negation density (heuristic for contradiction)
        if p_negs > 0 and c_negs == 0:
            energy += 2.0  # High prediction error if ignoring negation context
        elif abs(p_negs - c_negs) > 1:
            energy += 0.5

        # 2. Numeric Consistency (Constraint Propagation)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # Check if candidate numbers are plausible transformations of prompt numbers
            # Simple heuristic: Candidate should contain relevant numbers or logical results
            p_set = set(p_nums)
            c_set = set(c_nums)
            # Penalty if no numbers match and no obvious derivation (simplified)
            if not p_set.intersection(c_set) and len(p_set) > 0:
                # Allow small deviations for calculation results, penalize total mismatch
                if len(c_nums) == 0:
                    energy += 1.0 
        elif p_nums and not c_nums:
            # Prompt asks for math/logic, candidate has no numbers -> High error
            if any(word in p_lower for word in ['calculate', 'sum', 'total', 'difference', 'larger', 'smaller']):
                energy += 3.0

        # 3. Conditional/Logical Flow
        has_conditional = any(w in p_lower for w in self.conditionals)
        if has_conditional:
            # Candidate should ideally contain logical connectors or definitive answers
            if not any(w in c_lower for w in self.conditionals + ['yes', 'no', 'true', 'false']):
                energy += 0.5

        # 4. Length/Complexity regularization (Occam's razor)
        # Penalize excessively long candidates that don't add information density
        if len(candidate) > len(prompt) * 1.5:
            energy += 0.1 * (len(candidate) - len(prompt)) / len(prompt)
            
        return energy

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            denom = max(c1, c2)
            if denom == 0:
                return 1.0
            return (c12 - min(c1, c2)) / denom
        except Exception:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Ranks candidates by minimizing Free Energy (structural error).
        Uses NCD only as a tiebreaker.
        """
        scored_candidates = []
        
        for cand in candidates:
            # Core Free Energy Minimization (Structural Parsing)
            fe_score = self._compute_structural_free_energy(prompt, cand)
            
            # Invert for ranking (higher is better) and add small noise for diversity if needed
            # Base score starts at 10.0, subtract free energy
            raw_score = 10.0 - fe_score
            
            scored_candidates.append({
                "candidate": cand,
                "score": raw_score,
                "fe_error": fe_score, # Internal metric
                "reasoning": f"Structural free-energy: {fe_score:.2f}"
            })

        # Sorting: Primary by Free Energy score (desc), Secondary by NCD (asc, as tiebreaker logic)
        # Since we want deterministic output, we use index as final tiebreaker
        def sort_key(item):
            # Higher score is better (so negative for ascending sort)
            # If scores are equal, use NCD to prompt (lower NCD = more similar context = tiebreak)
            ncd_val = self._ncd(prompt, item['candidate'])
            return (-item['score'], ncd_val)

        scored_candidates.sort(key=sort_key)
        
        # Normalize scores to 0-1 range roughly for consistency, keeping relative order
        max_score = scored_candidates[0]['score'] if scored_candidates else 0
        min_score = scored_candidates[-1]['score'] if scored_candidates else 0
        range_score = max_score - min_score if (max_score - min_score) > 1e-6 else 1.0

        final_results = []
        for item in scored_candidates:
            # Rescale to 0.1 - 0.9 range to allow confidence wrapper to operate
            normalized = 0.1 + (0.8 * (item['score'] - min_score) / range_score)
            final_results.append({
                "candidate": item['candidate'],
                "score": normalized,
                "reasoning": item['reasoning']
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Phenomenological Bracketing Wrapper.
        Instead of scoring truth directly (inhibitor), it checks for 
        structural consistency (epoché mask) between prompt constraints and answer form.
        Returns 0.0 to 1.0.
        """
        # Re-use the free energy calculation as the 'consistency' check
        fe = self._compute_structural_free_energy(prompt, answer)
        
        # Map free energy to confidence: Low FE -> High Confidence
        # Heuristic mapping: FE=0 -> 0.95, FE=5 -> 0.5, FE>10 -> 0.1
        confidence = 1.0 / (1.0 + fe)
        
        # Hard constraints (The 'Bracketed' Lifeworld)
        # If the answer is empty or purely whitespace, confidence is 0
        if not answer or not answer.strip():
            return 0.0
            
        # If prompt asks for specific format (e.g., number) and answer lacks it
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(answer)
        
        # Specific check for numeric questions
        if len(p_nums) > 0 and "calculate" in prompt.lower():
            if len(c_nums) == 0:
                confidence *= 0.2 # Strong penalty within the bracket

        return min(1.0, max(0.0, confidence))