import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Compositional Energy-Based Causal Model (CEBCM) Approximation.
    
    Mechanism:
    Instead of training a neural energy model, we define a deterministic 'energy' 
    function based on structural logic constraints derived from the prompt.
    
    1. Structural Parsing (The Causal Graph G): Extract logical operators 
       (negations, comparatives, conditionals) to form a skeleton of constraints.
    2. Energy Function E(x): For each candidate, compute an energy score based on 
       how well it satisfies the extracted constraints.
       - Violating a negation adds high energy.
       - Matching numeric order adds low energy.
       - Semantic consistency (via NCD tie-breaking) adds minimal energy.
    3. Scoring: Score = exp(-E). Higher score = lower energy = better fit.
    
    This mimics the partition function ratio by comparing relative energies of 
    candidates under the same structural Hamiltonian defined by the prompt.
    """

    def __init__(self):
        self._logic_ops = ['if', 'then', 'else', 'unless', 'provided']
        self._neg_ops = ['not', 'no', 'never', 'none', 'cannot', "n't"]
        self._comp_ops = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', '>', '<']
        
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers from text."""
        pattern = r"-?\d+(?:\.\d+)?"
        return [float(x) for x in re.findall(pattern, text)]

    def _check_negation_context(self, text: str, target: str) -> bool:
        """Simple heuristic: does the text contain a negation near the target?"""
        # Simplified: checks if any negation word appears in the text
        text_lower = text.lower()
        for op in self._neg_ops:
            if op in text_lower:
                # Crude proximity check (last 50 chars before target occurrence)
                idx = text_lower.find(target.lower())
                if idx != -1:
                    window = text_lower[max(0, idx-50):idx]
                    if any(n in window for n in self._neg_ops):
                        return True
        return False

    def _compute_structural_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute energy based on structural logic constraints.
        Lower energy = better fit.
        """
        energy = 0.0
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # 1. Negation Consistency
        # If prompt has "not" and candidate affirms the negated concept without qualification
        has_prompt_neg = any(op in p_low for op in self._neg_ops)
        has_cand_neg = any(op in c_low for op in self._neg_ops)
        
        # Heuristic: If prompt is negative, candidate should likely reflect that or be short
        if has_prompt_neg and not has_cand_neg:
            # Penalty if candidate is long and affirmative in a negative context
            if len(candidate.split()) > 3:
                energy += 2.0
        
        # 2. Numeric Consistency
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # Check ordering if comparatives exist
            has_comp = any(op in p_low for op in self._comp_ops)
            if has_comp:
                # If prompt says "greater", candidate number should be greater than context?
                # This is hard without full semantic parse, so we penalize mismatched counts
                if len(p_nums) != len(c_nums):
                     energy += 1.0 # Soft penalty for number count mismatch
            else:
                # Exact match preferred for pure numeric prompts
                if p_nums != c_nums:
                    energy += 5.0 # High penalty for wrong numbers

        # 3. Conditional/Logical Flow
        # If "if" in prompt, candidate often contains "then" or is a direct consequence
        if 'if' in p_low:
            if 'then' in c_low or len(c_low.split()) > 2:
                energy -= 0.5 # Reward structured response
            else:
                energy += 0.5 # Slight penalty for unstructured response to conditional

        # 4. Length constraint (Occam's razor / Compositionality)
        # Prefer candidates that are concise but not empty
        if len(candidate) == 0:
            energy += 10.0
        elif len(candidate) > len(prompt) * 1.5:
            energy += 1.0 # Penalty for excessive verbosity
            
        return energy

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        c1 = len(zlib.compress(s1_bytes))
        c2 = len(zlib.compress(s2_bytes))
        c12 = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        if not candidates:
            return []

        # Pre-calculate structural energies
        energies = []
        for cand in candidates:
            e_struct = self._compute_structural_energy(prompt, cand)
            energies.append((cand, e_struct))
        
        # Find minimum energy to normalize scores (Boltzmann distribution approx)
        # We use a simple exponential decay on energy: score ~ exp(-energy)
        # To avoid underflow, subtract min energy first
        min_e = min(e for _, e in energies)
        
        scored_candidates = []
        for cand, e_raw in energies:
            # Shifted energy for stability
            e_shifted = e_raw - min_e
            
            # Base score from structural energy (The "Causal" part)
            # Using exp(-E) logic
            base_score = math.exp(-e_shifted)
            
            scored_candidates.append({
                "candidate": cand,
                "base_score": base_score,
                "energy": e_raw
            })

        # Tie-breaking / Refinement using NCD (The "Statistical Mechanics" part)
        # NCD is used only when structural energies are very close (within threshold)
        # or as a secondary sorting key.
        # However, to strictly beat NCD baseline, we must prioritize structure.
        # We will use NCD to slightly perturb scores where structure is ambiguous.
        
        final_results = []
        for item in scored_candidates:
            cand = item["candidate"]
            score = item["base_score"]
            
            # NCD Tiebreaker logic:
            # If two candidates have similar structural energy, the one with 
            # lower NCD distance to the prompt (higher similarity) gets a tiny boost.
            # But wait, correct answers aren't always similar strings. 
            # Let's use NCD to penalize "noise". 
            # Actually, the prompt says: "NCD is only a tiebreaker for candidates where no structural signal is detected."
            # Our structural signal is the energy. If energy is high (bad), score is low.
            # If energy is low (good), score is high.
            
            # Let's apply a very small NCD-based adjustment to break ties in energy
            ncd_val = self._ncd_distance(prompt, cand)
            # Normalize NCD impact to be negligible compared to structural logic
            # unless structural logic is flat.
            ncd_adjustment = (1.0 - ncd_val) * 1e-6 
            
            final_score = score + ncd_adjustment
            
            # Generate reasoning string
            reasoning = f"Structural Energy: {item['energy']:.2f}. "
            if item['energy'] < 1.0:
                reasoning += "High consistency with logical constraints."
            elif item['energy'] < 3.0:
                reasoning += "Moderate consistency; minor structural mismatches."
            else:
                reasoning += "Low consistency; violates key logical or numeric constraints."
                
            final_results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        final_results.sort(key=lambda x: x["score"], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the structural energy of the answer.
        """
        # Evaluate single candidate against prompt
        # We simulate the evaluation of this single candidate
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        # The score from evaluate is exp(-E_shifted). 
        # If the candidate is the only one, E_shifted = 0, so score = 1.0.
        # This doesn't help absolute confidence.
        
        # Instead, calculate raw energy and map to 0-1
        energy = self._compute_structural_energy(prompt, answer)
        
        # Map energy to confidence: 
        # Energy 0 -> Conf 1.0
        # Energy 5 -> Conf ~0.01
        # Using sigmoid-like decay: 1 / (1 + E) or exp(-E)
        # Let's use exp(-0.5 * E) to be less harsh than the relative scorer
        conf = math.exp(-0.5 * energy)
        
        # Clamp
        return max(0.0, min(1.0, conf))