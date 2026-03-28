import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Renormalized Maximum-Entropy Variational Tool (RME-VT)
    
    Mechanism:
    This tool implements a computational analogy of the RME-VAE architecture for reasoning tasks.
    
    1. Micro-State Analysis (Statistical Mechanics): 
       Parses candidates into structural features (negations, comparatives, conditionals, numbers).
       These are the "spins" of the system.
       
    2. Maximum Entropy Constraints:
       Instead of assuming a uniform prior, we constrain the probability distribution of 
       candidate validity based on observed structural matches with the prompt (e.g., if prompt 
       has a negation, valid candidates often preserve or correctly invert it).
       
    3. Renormalization Group (RG) Flow:
       We perform iterative coarse-graining. 
       - Scale 0: Raw string similarity (NCD) - prone to noise.
       - Scale 1: Structural feature matching (logic gates).
       - Scale 2: Numeric consistency and constraint propagation.
       
       At each step, we compute a "Free Energy" score: F = E - T*S.
       - Energy (E): Penalty for structural mismatch (higher energy = bad fit).
       - Entropy (S): Penalty for over-specificity or contradiction (low entropy = rigid/wrong).
       
       The RG flow aggregates these scores. Candidates that maintain low free energy 
       (high consistency) across scales (from raw text to logical structure) are promoted.
       Candidates that fit fine-scale (text overlap) but fail coarse-scale (logic) are suppressed.
    """

    def __init__(self):
        # Structural keywords for parsing
        self.negations = ['no', 'not', 'never', 'none', 'cannot', "n't"]
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<', 'increased', 'decreased']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided', 'when']
        self.bool_words = ['true', 'false', 'yes', 'no', 'correct', 'incorrect']

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for numeric evaluation."""
        pattern = r"-?\d+\.?\d*"
        matches = re.findall(pattern, text.lower())
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                continue
        return nums

    def _structural_parse(self, text: str) -> Dict:
        """Parse text into structural 'spins' (micro-states)."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        has_neg = any(n in lower_text for n in self.negations)
        has_comp = any(c in lower_text for c in self.comparatives)
        has_cond = any(c in lower_text for c in self.conditionals)
        has_bool = any(b in words for b in self.bool_words)
        numbers = self._extract_numbers(text)
        
        return {
            'neg': has_neg,
            'comp': has_comp,
            'cond': has_cond,
            'bool': has_bool,
            'nums': numbers,
            'len': len(words)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _compute_energy(self, prompt_struct: Dict, cand_struct: Dict, prompt: str, candidate: str) -> float:
        """
        Compute Energy term: Penalty for structural mismatch.
        Lower energy = better structural alignment.
        """
        energy = 0.0
        
        # Negation consistency: If prompt has negation, candidate should reflect logic 
        # (simplified: if prompt has neg, candidate having neg is lower energy than random)
        # This is a heuristic proxy for logical consistency in absence of full NLI.
        if prompt_struct['neg'] != cand_struct['neg']:
            energy += 2.0  # Penalty for negation mismatch
            
        # Conditional presence
        if prompt_struct['cond'] and not cand_struct['cond']:
            energy += 1.0 # Penalty if prompt sets up conditionals but candidate ignores
            
        # Numeric consistency
        p_nums = prompt_struct['nums']
        c_nums = cand_struct['nums']
        
        if p_nums and c_nums:
            # Check if relative order is preserved (simple transitivity check)
            # If prompt implies A > B, candidate shouldn't imply B > A
            # Here we just penalize huge deviations in magnitude if counts match
            if len(p_nums) == len(c_nums):
                for pn, cn in zip(p_nums, c_nums):
                    if pn != 0 and abs(pn - cn) / abs(pn) > 0.5: # Allow some variance
                        energy += 0.5
            elif len(p_nums) != len(c_nums):
                 energy += 1.0 # Mismatch in number of entities
                 
        # Base energy from NCD (fine scale)
        ncd = self._compute_ncd(prompt, candidate)
        energy += ncd * 2.0
        
        return energy

    def _compute_entropy_term(self, candidate: str, prompt: str) -> float:
        """
        Compute Entropy term: Measure of disorder/uncertainty.
        In MaxEnt, we maximize entropy subject to constraints.
        Here, we use entropy as a complexity penalty. 
        Short, generic answers have high entropy (low info). 
        Overly long, rambling answers have high entropy.
        We want the "Goldilocks" zone constrained by the prompt.
        """
        if not candidate:
            return 10.0 # Max penalty
        
        # Length penalty relative to prompt
        len_ratio = len(candidate) / (len(prompt) + 1)
        if len_ratio < 0.01 or len_ratio > 5.0:
            return 2.0 # High entropy (disordered)
            
        # Vocabulary diversity (simple proxy)
        words = candidate.lower().split()
        if not words:
            return 1.0
        unique_ratio = len(set(words)) / len(words)
        
        # High unique ratio can mean disjointed (high energy), low means repetitive
        # We prefer moderate complexity
        return unique_ratio 

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._structural_parse(prompt)
        results = []
        
        # Pre-calculate prompt stats for RG flow
        T = 1.0 # Temperature parameter for the system
        
        for cand in candidates:
            cand_struct = self._structural_parse(cand)
            
            # Scale 1: Fine scale (NCD + basic overlap)
            ncd = self._compute_ncd(prompt, cand)
            
            # Scale 2: Coarse scale (Structural Energy)
            energy = self._compute_energy(prompt_struct, cand_struct, prompt, cand)
            
            # Scale 3: Entropy regularization
            entropy = self._compute_entropy_term(cand, prompt)
            
            # Free Energy: F = E - T*S
            # We want to MINIMIZE Free Energy. 
            # Score should be inversely related to Free Energy.
            free_energy = energy - T * (1.0/ (entropy + 0.1)) 
            
            # Invert for scoring (higher is better)
            # Normalize roughly to 0-1 range based on heuristics
            raw_score = 1.0 / (1.0 + free_energy)
            
            # Boost if structural features align perfectly (RG Fixed Point)
            if prompt_struct['neg'] == cand_struct['neg'] and prompt_struct['cond'] == cand_struct['cond']:
                raw_score += 0.1
                
            results.append({
                "candidate": cand,
                "score": round(raw_score, 4),
                "reasoning": f"Scale-invariant score: E={energy:.2f}, S={entropy:.2f}, NCD={ncd:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same Free Energy logic but normalized strictly.
        """
        # Reuse evaluation logic for single pair
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        base_score = res[0]['score']
        
        # Structural parsing support (as per constraints)
        # Check for direct contradictions in boolean words
        p_lower = prompt.lower()
        a_lower = answer.lower()
        
        if ('true' in p_lower or 'false' in p_lower):
            if ('true' in a_lower and 'false' in p_lower) or ('false' in a_lower and 'true' in p_lower):
                return 0.05 # Very low confidence due to direct contradiction
                
        # Map base_score (which can be > 1 or < 0 theoretically) to 0-1
        conf = max(0.0, min(1.0, base_score))
        return round(conf, 4)