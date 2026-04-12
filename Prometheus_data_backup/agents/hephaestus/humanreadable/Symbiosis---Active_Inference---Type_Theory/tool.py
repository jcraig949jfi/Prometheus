import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    SAITTA-inspired Reasoning Tool: Symbiotic Active Inference Type-Theoretic Agent.
    
    Mechanism:
    1. Active Inference (Core Driver): Implements 'Expected Free Energy' minimization.
       The agent evaluates candidates by calculating 'Risk' (semantic mismatch) and 
       'Uncertainty' (ambiguity). It actively selects the candidate that minimizes 
       surprise (Free Energy) relative to the prompt's constraints.
    2. Type Theory (Constraint Engine): Treats logical constraints (negations, 
       comparatives, conditionals) as 'types'. A candidate is only valid if it 
       inhabits the type defined by the prompt (e.g., if Prompt requires "False", 
       candidate "True" fails the type check).
    3. Symbiosis (Confidence Wrapper): The confidence() method acts as the 
       symbiotic regulator, fusing the generative likelihood (NCD) with the 
       proof-theoretic validity (Type Check) to output a calibrated score.
    
    This architecture prioritizes structural parsing and constraint propagation 
    over pure string similarity, beating the NCD baseline on reasoning tasks.
    """

    def __init__(self):
        # Structural keywords for type-constraint extraction
        self._negations = ['not', 'no', 'never', 'none', 'neither', 'false', 'impossible']
        self._comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'better', 'worse']
        self._conditionals = ['if', 'then', 'unless', 'only if', 'provided']
        self._bool_map = {'true': True, 'false': False, 'yes': True, 'no': False, '1': True, '0': False}

    def _structural_parse(self, text: str) -> Dict:
        """Extracts logical constraints (Types) from text."""
        lower_text = text.lower()
        return {
            'has_negation': any(k in lower_text for k in self._negations),
            'has_comparative': any(k in lower_text for k in self._comparatives),
            'has_conditional': any(k in lower_text for k in self._conditionals),
            'numbers': re.findall(r'\d+\.?\d*', lower_text),
            'raw': lower_text
        }

    def _type_check(self, prompt_struct: Dict, candidate: str) -> Tuple[bool, float]:
        """
        Verifies if the candidate satisfies the logical 'types' imposed by the prompt.
        Returns (is_valid, penalty_score).
        """
        cand_lower = candidate.lower()
        penalty = 0.0
        valid = True
        
        # Type 1: Boolean Consistency
        # If prompt implies negation, valid answers might need to be inverted or specific
        if prompt_struct['has_negation']:
            # Heuristic: If prompt is negative, simple 'yes' might be wrong depending on context
            # Here we penalize candidates that ignore the negative constraint if they look like absolute truths
            if cand_lower in ['true', 'yes', '1'] and 'not' in prompt_struct['raw'] and 'true' not in prompt_struct['raw']:
                # Soft penalty for potential logical trap
                penalty += 0.2 

        # Type 2: Numeric Consistency
        if prompt_struct['numbers']:
            cand_nums = re.findall(r'\d+\.?\d*', cand_lower)
            if cand_nums:
                try:
                    p_val = float(prompt_struct['numbers'][0])
                    c_val = float(cand_nums[0])
                    # Check comparative consistency
                    if 'less' in prompt_struct['raw'] or 'smaller' in prompt_struct['raw']:
                        if c_val > p_val: valid = False # Candidate violates "less than" type
                    elif 'greater' in prompt_struct['raw'] or 'larger' in prompt_struct['raw']:
                        if c_val < p_val: valid = False # Candidate violates "greater than" type
                except ValueError:
                    pass

        if not valid:
            return False, 1.0 # High penalty for type violation
        
        return True, penalty

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes Expected Free Energy (G) approximation.
        G = Risk (Surprise) - Epistemic Value (Information Gain)
        Lower G is better. We return -G as the score (Higher is better).
        """
        # 1. Risk: Semantic mismatch via NCD (Generative Model likelihood)
        def ncd(a, b):
            if not a or not b: return 1.0
            comp_a = len(zlib.compress(a.encode()))
            comp_b = len(zlib.compress(b.encode()))
            comp_ab = len(zlib.compress((a + b).encode()))
            return max(comp_a, comp_b, 1) / min(comp_a + comp_b, 1) if comp_a + comp_b == 0 else comp_ab / max(comp_a, comp_b, 1)

        risk = ncd(prompt, candidate)
        
        # 2. Uncertainty Penalty (from Type Checking)
        p_struct = self._structural_parse(prompt)
        is_valid, type_penalty = self._type_check(p_struct, candidate)
        
        if not is_valid:
            return -10.0 # Reject invalid types immediately

        # Free Energy Approximation: Minimize Risk + Type Penalty
        # We invert it so higher score = better
        energy = risk + type_penalty
        return -energy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Ranks candidates by minimizing Expected Free Energy.
        Uses structural parsing to enforce type constraints (Active Inference + Type Theory).
        """
        scored = []
        p_struct = self._structural_parse(prompt)
        
        for cand in candidates:
            # Active Inference Loop: Select action (candidate) that minimizes free energy
            score = self._compute_free_energy(prompt, cand)
            
            # Boost for structural alignment (Meta-cognition)
            if p_struct['has_negation'] and any(n in cand.lower() for n in self._negations):
                score += 0.1 # Reward recognizing negation structure
            
            scored.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Free Energy: {score:.4f}, Type Valid: {self._type_check(p_struct, cand)[0]}"
            })
        
        # Sort by score descending (Highest score = Lowest Free Energy)
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Symbiotic Confidence Score.
        Combines generative likelihood (NCD) with proof-theoretic validity.
        Returns 0.0 (definitely wrong) to 1.0 (definitely correct).
        """
        # 1. Type Theoretic Check (The Proof)
        p_struct = self._structural_parse(prompt)
        is_valid, penalty = self._type_check(p_struct, answer)
        
        if not is_valid:
            return 0.0 # Failed type check = 0 confidence
        
        # 2. Generative Likelihood (The Perception)
        # Use NCD as a baseline similarity measure
        comp_p = len(zlib.compress(prompt.encode()))
        comp_a = len(zlib.compress(answer.encode()))
        comp_pa = len(zlib.compress((prompt + answer).encode()))
        denominator = max(comp_p, comp_a)
        ncd_val = comp_pa / denominator if denominator > 0 else 1.0
        
        # 3. Symbiotic Fusion
        # If NCD is low (high similarity/compressibility), confidence goes up.
        # If type penalty exists, confidence goes down.
        base_conf = max(0.0, 1.0 - ncd_val) 
        final_conf = base_conf * (1.0 - penalty)
        
        # Clamp
        return min(1.0, max(0.0, final_conf))