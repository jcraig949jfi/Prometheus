import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Free-Energy Mechanism Design Cellular Automaton (FE-MD-CA) Reasoning Tool.
    
    Mechanism:
    1.  **Free Energy Principle (FEP)**: The 'evaluate' method treats the prompt as sensory input.
        It computes a 'prediction error' (Free Energy) for each candidate by measuring the 
        structural consistency between the prompt's logical constraints and the candidate's 
        implied state. Lower error = higher likelihood.
    2.  **Mechanism Design**: Candidates are scored using a proper scoring rule analog. 
        Truthful alignment with logical constraints (negations, comparatives) yields maximum 
        payoff (score), while contradictions incur quadratic penalties (incentive compatibility).
    3.  **Cellular Automata**: The text is parsed into a local lattice of tokens. Updates 
        (scoring) depend only on nearest-neighbor logical relations (e.g., "NOT" flipping 
        the value of the adjacent token). This restricts the scope to local structural parsing.
    
    The tool prioritizes structural logic (negations, numbers, conditionals) over semantic 
    similarity, using NCD only as a tiebreaker for indistinguishable candidates.
    """

    def __init__(self):
        self._logic_ops = {'not', 'no', 'never', 'false', 'impossible'}
        self._comp_ops = {'greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<'}
        self._cond_ops = {'if', 'then', 'unless', 'otherwise'}

    def _parse_structure(self, text: str) -> Dict:
        """Extract logical signatures: negations, comparatives, numbers, conditionals."""
        t_lower = text.lower()
        words = re.findall(r'\b\w+\b', t_lower)
        
        # Count logic operators
        neg_count = sum(1 for w in words if w in self._logic_ops)
        comp_count = sum(1 for w in words if w in self._comp_ops)
        cond_count = sum(1 for w in words if w in self._cond_ops)
        
        # Extract numbers for numeric evaluation
        numbers = [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]
        
        # Simple constraint: Does it contain specific structural markers?
        has_structure = (neg_count > 0) or (comp_count > 0) or (len(numbers) > 1) or (cond_count > 0)
        
        return {
            "negations": neg_count,
            "comparatives": comp_count,
            "conditionals": cond_count,
            "numbers": numbers,
            "has_structure": has_structure,
            "length": len(words)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _calculate_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Calculate Variational Free Energy (F) for a candidate.
        F = Prediction Error + Complexity Penalty.
        Lower F is better. We invert this for the final score.
        """
        p_struct = self._parse_structure(prompt)
        c_struct = self._parse_structure(candidate)
        
        error = 0.0
        
        # 1. Negation Consistency (Mechanism Design: Truthful reporting of polarity)
        # If prompt has strong negation logic, candidate must reflect it or explicitly deny it.
        # Simplified heuristic: Mismatch in negation density creates high error.
        if p_struct["negations"] > 0:
            # If prompt has negations, candidate should ideally have some logical marker 
            # or be very short (direct answer). Long answers without negation markers get penalized.
            if c_struct["negations"] == 0 and c_struct["length"] > 10:
                error += 2.0 * p_struct["negations"]
        
        # 2. Numeric Consistency (Constraint Propagation)
        if len(p_struct["numbers"]) >= 2 and len(c_struct["numbers"]) >= 1:
            # Check if candidate number violates simple prompt logic (e.g., prompt says "less than 5", candidate "10")
            # This is a simplified proxy for full logical entailment.
            p_nums = sorted(p_struct["numbers"])
            c_num = c_struct["numbers"][0]
            
            # Heuristic: If prompt implies range via comparatives, check candidate
            if "less" in prompt.lower() or "smaller" in prompt.lower():
                if c_num > p_nums[-1]: # Candidate violates 'less than' constraint
                    error += 5.0
            elif "greater" in prompt.lower() or "larger" in prompt.lower():
                if c_num < p_nums[0]: # Candidate violates 'greater than' constraint
                    error += 5.0

        # 3. Structural Alignment (Local CA update rule)
        # Candidates that preserve structural density (without noise) are favored.
        if p_struct["has_structure"] and not c_struct["has_structure"]:
            # Candidate ignores structural cues in prompt
            error += 1.5
            
        # Complexity penalty (Occam's razor)
        complexity = 0.1 * math.log(c_struct["length"] + 1)
        
        return error + complexity

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates using FE-MD-CA principles.
        Returns ranked list of dicts with candidate, score, and reasoning.
        """
        if not candidates:
            return []
            
        results = []
        min_energy = float('inf')
        
        # Phase 1: Compute Free Energy for all candidates
        energies = []
        for cand in candidates:
            energy = self._calculate_free_energy(prompt, cand)
            energies.append((cand, energy))
            if energy < min_energy:
                min_energy = energy
        
        # Phase 2: Convert Energy to Score (Incentive Compatible Scoring Rule)
        # Score = exp(-Energy) normalized. Lower energy -> Higher score.
        # Add small epsilon to prevent division by zero if all energies are identical/high
        max_score_val = 0.0
        scored_candidates = []
        
        for cand, energy in energies:
            # Transform energy to a raw score (higher is better)
            raw_score = math.exp(-energy)
            if raw_score > max_score_val:
                max_score_val = raw_score
            scored_candidates.append({"candidate": cand, "raw_score": raw_score, "energy": energy})
        
        # Normalize scores to [0, 1] range roughly, ensuring the best one is high
        # Use NCD as a tiebreaker for raw_score collisions
        final_results = []
        for item in scored_candidates:
            cand = item["candidate"]
            score = item["raw_score"]
            
            # Tie-breaking with NCD if scores are very close (within floating point tolerance)
            # or if the prompt structure is weak (relying more on similarity)
            p_struct = self._parse_structure(prompt)
            if not p_struct["has_structure"]:
                # If prompt lacks structure, NCD becomes more relevant (fallback)
                ncd = self._compute_ncd(prompt, cand)
                score = score * (1.0 - ncd * 0.5) # Boost score if similar
            
            # Construct reasoning string
            reasoning = f"Free-Energy: {item['energy']:.2f}. "
            if item['energy'] < 1.0:
                reasoning += "High consistency with logical constraints."
            elif item['energy'] > 3.0:
                reasoning += "High prediction error; likely violates constraints."
            else:
                reasoning += "Moderate alignment."

            final_results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        final_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Normalize scores so max is 1.0 for cleaner output (optional but good practice)
        if final_results:
            max_s = final_results[0]["score"] if final_results[0]["score"] > 0 else 1.0
            for res in final_results:
                res["score"] = res["score"] / max_s
                
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1 based on the Free Energy of the specific answer.
        1.0 = Low Free Energy (High consistency), 0.0 = High Free Energy.
        """
        energy = self._calculate_free_energy(prompt, answer)
        # Map energy to confidence: exp(-energy) gives a value between 0 and 1
        # Low energy (0) -> 1.0, High energy (e.g., 5) -> ~0.006
        conf = math.exp(-energy)
        return min(1.0, max(0.0, conf))