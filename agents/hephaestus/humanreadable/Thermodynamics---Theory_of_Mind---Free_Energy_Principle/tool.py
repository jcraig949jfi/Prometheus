import re
import numpy as np
import math
import zlib
from collections import defaultdict

class ReasoningTool:
    """
    A reasoning tool implementing a Factor-Graph Free Energy Scorer.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (predicates, comparatives, negations, conditionals)
       using regex to form nodes in a factor graph.
    2. Thermodynamics: Assigns 'energy' to states based on logical consistency (Modus Ponens, 
       transitivity, negation) and priors. Lower energy = higher probability.
    3. Theory of Mind (Restricted): Used only in confidence() to estimate surprisal/entropy,
       not for direct scoring logic to avoid adversarial failure modes.
    4. Free Energy Principle: The core evaluator. Calculates F = <E> - H. 
       Candidates that minimize free energy (high consistency, low surprisal) are ranked higher.
    """

    def __init__(self):
        # Simple priors for common sense (frequency-based approximation)
        self.priors = defaultdict(lambda: 0.5)
        self.priors["true"] = 0.9
        self.priors["false"] = 0.1
        
        # Regex patterns for structural parsing
        self.patterns = {
            'comparative': re.compile(r'(\w+)\s*(>|<|=|>=|<=)\s*(\w+)'),
            'conditional': re.compile(r'if\s+(.+?)\s+(?:then)?\s+(.+?)', re.IGNORECASE),
            'causal': re.compile(r'(.+?)\s*->\s*(.+?)'),
            'negation': re.compile(r'(?:not|no|never)\s+(\w+)', re.IGNORECASE),
            'number': re.compile(r'-?\d+\.?\d*'),
            'predicate': re.compile(r'(\w+)\(([^)]+)\)')
        }

    def _extract_propositions(self, text):
        """Extracts atomic propositions and logical structures from text."""
        props = []
        text_lower = text.lower()
        
        # Extract numbers for numeric evaluation
        numbers = [float(n) for n in self.patterns['number'].findall(text)]
        
        # Extract comparatives
        for m in self.patterns['comparative'].findall(text):
            props.append(('comp', m[0].strip(), m[1].strip(), m[2].strip()))
            
        # Extract conditionals
        for m in self.patterns['conditional'].findall(text_lower):
            props.append(('cond', m[0].strip(), m[1].strip()))
            
        # Extract causal
        for m in self.patterns['causal'].findall(text):
            props.append(('causal', m[0].strip(), m[1].strip()))
            
        # Extract negations
        for m in self.patterns['negation'].findall(text_lower):
            props.append(('neg', m.strip()))
            
        # Extract predicates
        for m in self.patterns['predicate'].findall(text):
            props.append(('pred', m[0], m[1]))

        return props, numbers

    def _compute_energy(self, prompt_props, answer_props, prompt_nums, answer_nums):
        """
        Computes the 'Energy' E(x) of the combined state.
        Lower energy indicates higher logical consistency and thermodynamic plausibility.
        """
        energy = 0.0
        
        # 1. Numeric Consistency (Thermodynamic constraint)
        # If prompt has numbers and answer has numbers, check ordering consistency
        if prompt_nums and answer_nums:
            # Simple heuristic: if prompt implies a direction, does answer follow?
            # This is a shallow check but captures basic numeric reasoning
            p_diff = max(prompt_nums) - min(prompt_nums) if len(prompt_nums) > 1 else 0
            a_diff = max(answer_nums) - min(answer_nums) if len(answer_nums) > 1 else 0
            
            # Penalty if magnitudes are wildly inconsistent (heuristic)
            if abs(p_diff) > 0 and abs(a_diff) == 0:
                energy += 2.0 # Moderate penalty for losing numeric resolution

        # 2. Logical Consistency (Factor Graph Potentials)
        # Check for direct contradictions between prompt constraints and answer assertions
        
        prompt_negs = {p[1] for p in prompt_props if p[0] == 'neg'}
        answer_negs = {p[1] for p in answer_props if p[0] == 'neg'}
        
        prompt_asserts = {p[1] for p in prompt_props if p[0] == 'pred'}
        answer_asserts = {p[1] for p in answer_props if p[0] == 'pred'}

        # Modus Ponens / Contradiction Check
        # If prompt says "not X" and answer asserts "X", high energy penalty
        for item in prompt_negs:
            if item in answer_asserts:
                energy += 10.0 # Strong penalty
        
        # If answer says "not X" but prompt asserts "X"
        for item in answer_negs:
            if item in prompt_asserts:
                energy += 10.0

        # Conditional Consistency
        # If prompt: "if A then B". Answer asserts A but not B (or not B).
        for p_type, antecedent, consequent in [p for p in prompt_props if p[0] == 'cond']:
            ant_present = antecedent in " ".join([str(x) for x in answer_props]).lower()
            cons_present = consequent in " ".join([str(x) for x in answer_props]).lower()
            
            # If antecedent is true in answer context, consequent should be too
            if ant_present and not cons_present:
                # Check if consequent is explicitly negated
                if any(consequent in str(n) for n in answer_negs):
                    energy += 8.0
                elif not any(consequent in str(a) for a in answer_asserts):
                    energy += 4.0 # Soft penalty for missing inference

        return energy

    def _ncd_distance(self, s1, s2):
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        try:
            z1 = len(zlib.compress(s1.encode()))
            z2 = len(zlib.compress(s2.encode()))
            z12 = len(zlib.compress((s1 + s2).encode()))
            max_len = max(z1, z2)
            if max_len == 0: return 1.0
            return (z12 - min(z1, z2)) / max_len
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """
        Evaluates candidates based on Free Energy minimization.
        Score = -F(h) = -(Energy - Entropy). 
        Since we approximate Entropy as constant-ish for short answers, 
        we primarily minimize Energy (logical consistency).
        """
        results = []
        prompt_props, prompt_nums = self._extract_propositions(prompt)
        
        # Base entropy estimate (simulated) based on prompt complexity
        base_entropy = math.log(len(prompt_props) + 2) 

        for cand in candidates:
            cand_props, cand_nums = self._extract_propositions(cand)
            
            # 1. Compute Energy (Thermodynamic/Logical cost)
            energy = self._compute_energy(prompt_props, cand_props, prompt_nums, cand_nums)
            
            # 2. Estimate Entropy (Surprisal)
            # Heuristic: Longer, more complex answers that match prompt structure have lower surprisal
            # if they are consistent. Here we use a simple length-based proxy adjusted by match.
            match_ratio = 0.0
            if prompt_props:
                common = 0
                for cp in cand_props:
                    if cp in prompt_props: common += 1
                match_ratio = common / (len(prompt_props) + 1)
            
            # Entropy approximation: Higher if the answer introduces new but consistent concepts
            # Low entropy (bad) if it's random noise or completely unrelated.
            # We model Q(x) such that consistent answers have higher probability -> lower -logQ
            entropy_term = base_entropy * (0.5 + 0.5 * match_ratio)
            
            # 3. Free Energy Calculation: F = E - H
            # We want to minimize F. 
            free_energy = energy - entropy_term
            
            # NCD Tiebreaker (small weight)
            ncd = self._ncd_distance(prompt, cand)
            final_score = -free_energy - (ncd * 0.1)

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Energy: {energy:.2f}, Entropy: {entropy_term:.2f}, NCD: {ncd:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses Theory of Mind layer to estimate if the answer is 'expected' given the prompt.
        Restricted to structural validation to avoid adversarial traps.
        """
        props_p, nums_p = self._extract_propositions(prompt)
        props_a, nums_a = self._extract_propositions(answer)
        
        if not props_p and not nums_p:
            # If no structure, rely on NCD similarity as a baseline
            return 1.0 - self._ncd_distance(prompt, answer)
        
        energy = self._compute_energy(props_p, props_a, nums_p, nums_a)
        
        # Convert energy to probability-like confidence using Boltzmann distribution concept
        # P ~ exp(-E). Normalize roughly to 0-1.
        # Energy 0 -> ~0.99, Energy 10 -> ~0.0
        confidence = 1.0 / (1.0 + math.exp(energy - 2.0))
        
        return float(np.clip(confidence, 0.0, 1.0))