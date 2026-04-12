import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Pragmatic Predictive-Coding Network (PPCN) Implementation.
    
    Mechanism:
    1. Free Energy Principle (Core): Evaluates candidates by minimizing 'surprise' 
       (prediction error) derived from structural constraint satisfaction. 
       It parses the prompt for logical operators (negations, comparatives, conditionals)
       and numeric constraints. The 'energy' is the count of violated constraints.
       
    2. Hebbian Learning (Synergy): Implements associative strengthening between 
       prompt tokens and candidate tokens. If a candidate contains words strongly 
       co-occurring with the prompt's structural keys (e.g., "not" -> antonyms, 
       "greater" -> numbers), the synaptic weight increases, lowering the energy.
       
    3. Pragmatism (Utility Modulation): Acts as a confidence wrapper and tie-breaker.
       It does not drive the core logic (to avoid historical failure modes) but 
       modulates the final score based on the 'usefulness' of the answer format 
       (e.g., specific numeric precision or direct boolean alignment) and the 
       magnitude of the free-energy gap between top candidates.
       
    The system minimizes variational free energy (logical inconsistency) while 
    reinforcing pathways (Hebbian) that align with structural truths, judged by 
    pragmatic utility.
    """

    def __init__(self):
        # Structural keywords for parsing (Free Energy Gradients)
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'greater', 'less', 'more', 'fewer', 'higher', 'lower', 'larger', 'smaller'}
        self.conditionals = {'if', 'then', 'unless', 'only', 'provided'}
        self.booleans = {'true', 'false', 'yes', 'no'}
        
        # Hebbian Weights (Simplified static matrix for token association)
        # In a full system, these would update dynamically. Here they represent 
        # pre-trained semantic links that reinforce structural logic.
        self.hebbian_associations = {
            'greater': {'less', 'smaller', 'lower'},
            'less': {'greater', 'larger', 'higher'},
            'true': {'false', 'no'},
            'false': {'true', 'yes'},
            'increase': {'decrease', 'drop', 'fall'},
            'decrease': {'increase', 'rise', 'grow'}
        }

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        # Extracts floats/integers for numeric evaluation
        matches = re.findall(r'-?\d+\.?\d*', text)
        return [float(m) for m in matches]

    def _check_structural_constraints(self, prompt: str, candidate: str) -> float:
        """
        Calculates Free Energy (Error) based on logical constraints.
        Lower energy = better fit. We invert this for scoring.
        """
        p_tokens = set(self._tokenize(prompt))
        c_tokens = set(self._tokenize(candidate))
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        energy = 0.0
        
        # 1. Negation Consistency
        has_negation = bool(p_tokens & self.negations)
        candidate_has_negation = bool(c_tokens & self.negations)
        
        # If prompt implies negation logic, check if candidate respects it roughly
        # This is a heuristic proxy for logical consistency
        if has_negation:
            # Simple heuristic: if prompt has 'no' and candidate is just 'yes', high energy
            if 'no' in p_tokens and 'yes' in c_tokens and len(c_tokens) < 3:
                energy += 2.0
            if 'not' in p_tokens and 'yes' in c_tokens and len(c_tokens) < 3:
                energy += 2.0

        # 2. Comparative Logic (Numeric)
        # If prompt asks for "greater" and provides numbers, check candidate numbers
        if p_tokens & self.comparatives and len(p_nums) >= 2 and len(c_nums) >= 1:
            n1, n2 = p_nums[0], p_nums[1]
            c_val = c_nums[0]
            
            if 'greater' in p_tokens or 'larger' in p_tokens or 'more' in p_tokens:
                if c_val != max(n1, n2): energy += 1.5
            elif 'less' in p_tokens or 'smaller' in p_tokens or 'fewer' in p_tokens:
                if c_val != min(n1, n2): energy += 1.5

        # 3. Conditional Presence
        if p_tokens & self.conditionals:
            # If conditional exists, candidate should ideally not be a bare number 
            # unless the logic is purely mathematical. 
            # Heuristic: Penalize candidates that ignore conditional keywords entirely
            # if the prompt is complex.
            if len(c_tokens) < 2 and len(p_tokens) > 10:
                energy += 0.5

        return energy

    def _compute_hebbian_strength(self, prompt: str, candidate: str) -> float:
        """
        Computes Hebbian reinforcement: strength of association between 
        prompt context and candidate content.
        """
        p_tokens = self._tokenize(prompt)
        c_tokens = self._tokenize(candidate)
        
        strength = 0.0
        p_set = set(p_tokens)
        
        # Strengthen if candidate contains words associated with prompt keys
        for token in p_set:
            if token in self.hebbian_associations:
                # Check if candidate contains any associated concept
                associated_concepts = self.hebbian_associations[token]
                matches = c_tokens & associated_concepts
                strength += len(matches) * 0.2
                
        # Bonus for exact keyword overlap (strong co-activation)
        overlap = len(p_set & c_tokens)
        strength += overlap * 0.1
        
        return strength

    def _pragmatic_utility(self, prompt: str, candidate: str) -> float:
        """
        Pragmatic filter: Rewards answers that look like valid solutions 
        (specific formats, directness) without driving the logic.
        """
        utility = 0.0
        c_lower = candidate.lower().strip()
        p_lower = prompt.lower()
        
        # Reward direct answers to yes/no questions
        if any(q in p_lower for q in ['is it', 'does it', 'can it', 'true or false']):
            if c_lower in ['yes', 'no', 'true', 'false']:
                utility += 0.5
        
        # Reward numeric precision if numbers are in prompt
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if len(p_nums) > 0 and len(c_nums) > 0:
            utility += 0.3
            
        # Penalty for empty or whitespace only
        if len(c_lower) == 0:
            utility -= 1.0
            
        return utility

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as a tiebreaker."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0: return 1.0
        return (len_combined - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt features to avoid re-parsing
        p_tokens = set(self._tokenize(prompt))
        
        for cand in candidates:
            # 1. Free Energy (Structural Logic) - Primary Driver
            # We want to MINIMIZE energy, so we negate it for the score
            energy = self._check_structural_constraints(prompt, cand)
            fe_score = -energy 
            
            # 2. Hebbian Strength - Synergistic Reinforcement
            # Adds positive weight to logically consistent paths
            hebb_score = self._compute_hebbian_strength(prompt, cand)
            
            # 3. Pragmatic Utility - Modulation
            prag_score = self._pragmatic_utility(prompt, cand)
            
            # Combined Score: FE is dominant, Hebbian reinforces, Pragmatic adjusts
            # Weights tuned to prioritize logical consistency (FE)
            total_score = (fe_score * 1.0) + (hebb_score * 0.5) + (prag_score * 0.3)
            
            # NCD Tiebreaker (only if scores are very close or zero)
            # We store NCD separately to apply only if needed, but for sorting 
            # we can add a tiny epsilon based on NCD if scores are equal.
            # However, to strictly follow "NCD as tiebreaker", we rely on the 
            # stability of float comparison or add a micro-penalty for high NCD.
            # Here we just keep it pure. If scores equal, stable sort preserves order.
            # To actively use it:
            ncd = self._ncd_distance(prompt, cand)
            if abs(total_score) < 1e-6: # If logic yields no signal
                total_score -= ncd * 0.001 # Prefer lower NCD (more similar structure)

            results.append({
                "candidate": cand,
                "score": total_score,
                "reasoning": f"FE:{-energy:.2f} Hebb:{hebb_score:.2f} Prag:{prag_score:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the pragmatic success of the answer
        combined with low free energy (logical consistency).
        """
        # Evaluate single candidate against itself to get internal metrics
        # We simulate the evaluation step
        energy = self._check_structural_constraints(prompt, answer)
        hebb = self._compute_hebbian_strength(prompt, answer)
        prag = self._pragmatic_utility(prompt, answer)
        
        # Base confidence from pragmatic utility (format validity)
        # If the answer looks nonsense structurally, confidence drops
        base_conf = max(0.0, min(1.0, 0.5 + prag * 0.2))
        
        # Adjust by Free Energy (Logical Consistency)
        # High energy (errors) reduces confidence significantly
        logic_factor = 1.0 / (1.0 + energy) # Maps 0->1, 2->0.33, etc.
        
        # Adjust by Hebbian (Association strength)
        hebb_factor = min(1.0, hebb * 0.5)
        
        # Weighted combination
        # Logic is most important for "truth", Pragmatics for "usefulness"
        final_conf = (logic_factor * 0.6) + (base_conf * 0.3) + (hebb_factor * 0.1)
        
        return float(np.clip(final_conf, 0.0, 1.0))