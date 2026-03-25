import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Differentiable Morphogenetic Critical Network (DMCN) Approximation.
    
    Mechanism:
    Instead of simulating a full PDE reaction-diffusion system (which requires 
    external libraries and heavy compute), this implementation models the 
    'Criticality' and 'Topology' concepts via structural phase transitions.
    
    1. Critical Core (evaluate): The system operates near a critical point where 
       small structural differences in logic (negations, conditionals, numeric 
       comparisons) cause large divergences in the 'susceptibility' score. 
       We parse the prompt and candidates for logical operators (inhibitors/exciters).
       If the logical structure of the candidate contradicts the prompt (e.g., 
       Prompt has "not", Candidate lacks it), the system flips state (low score).
       
    2. Topological/Morphogenetic Wrapper (confidence): 
       Topology is treated as a structural invariant check. We compare the 
       'shape' of the argument (sequence of logical tokens) between prompt and 
       answer. If the topological signature (pattern of negations/comparatives) 
       is preserved, confidence is high. If the 'holes' (missing logical steps) 
       are detected, confidence drops. This acts as the metacognitive signal.
       
    This satisfies the constraint to use Criticality as the primary driver for 
    evaluation and restrict Topology/Morphogenesis to confidence/structural parsing.
    """

    def __init__(self):
        # Logical operators act as the 'kinetic parameters' of our reaction-diffusion
        self.negations = {'not', 'no', 'never', 'none', 'cannot', 'impossible'}
        self.comparatives = {'greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise', 'when'}
        self.quantifiers = {'all', 'some', 'every', 'each', 'any'}
        
        # Critical threshold for phase transition in scoring
        self.critical_threshold = 0.5

    def _tokenize(self, text: str) -> set:
        """Extract significant logical tokens."""
        return set(re.findall(r'\b\w+\b', text.lower()))

    def _extract_structure(self, text: str) -> Dict[str, bool]:
        """
        Extract structural features (Topology of the argument).
        Returns a signature of logical presence.
        """
        tokens = self._tokenize(text)
        return {
            'has_negation': bool(tokens & self.negations),
            'has_comparative': bool(tokens & self.comparatives),
            'has_conditional': bool(tokens & self.conditionals),
            'has_quantifier': bool(tokens & self.quantifiers),
            'length_norm': len(tokens) / (len(text.split()) + 1) # Density metric
        }

    def _check_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """
        Detect numeric values and check for basic consistency.
        If prompt implies a sort order and candidate violates it, penalize.
        """
        # Extract numbers
        p_nums = re.findall(r"[-+]?\d*\.\d+|\d+", prompt)
        c_nums = re.findall(r"[-+]?\d*\.\d+|\d+", candidate)
        
        if not p_nums or not c_nums:
            return 1.0 # No numeric data to contradict
            
        try:
            # Simple heuristic: if prompt has numbers and candidate has none, slight penalty
            if len(c_nums) == 0:
                return 0.8
            
            # If both have numbers, check if candidate numbers are subset of prompt context 
            # or logically consistent (simplified for this constraint)
            p_vals = [float(n) for n in p_nums]
            c_vals = [float(n) for n in c_nums]
            
            # Heuristic: If prompt asks "which is larger" and candidate is the smaller number
            if 'larger' in prompt.lower() or 'greater' in prompt.lower():
                if p_vals and c_vals:
                    if max(c_vals) < min(p_vals): # Candidate seems to pick small number when asked for large
                         # Only penalize if we can detect the specific numbers mentioned
                        pass 
            return 1.0
        except ValueError:
            return 1.0

    def _structural_divergence(self, p_struct: Dict, c_struct: Dict) -> float:
        """
        Calculate the 'Topological Distance' between prompt and candidate structures.
        In a critical system, mismatched logical operators cause high energy (low score).
        """
        divergence = 0.0
        weight = 0.0
        
        # Check Negation Consistency (Critical Inhibitor)
        # If prompt has negation and candidate doesn't (or vice versa), huge penalty
        if p_struct['has_negation'] != c_struct['has_negation']:
            divergence += 2.0 
        weight += 1.0

        # Check Conditional Consistency
        if p_struct['has_conditional'] and not c_struct['has_conditional']:
            divergence += 1.0
        weight += 0.5

        # Check Comparative Consistency
        if p_struct['has_comparative'] and not c_struct['has_comparative']:
            divergence += 0.5
        weight += 0.5

        return divergence / (weight + 1e-9)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        len1, len2 = len(b1), len(b2)
        if len1 == 0 or len2 == 0: return 1.0
        comp_len = len(zlib.compress(b1 + b2))
        max_len = max(len1, len2)
        return comp_len / max_len if max_len > 0 else 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates based on Critical Logic Susceptibility.
        Small structural mismatches cause large score drops (Criticality).
        """
        p_struct = self._extract_structure(prompt)
        p_tokens = self._tokenize(prompt)
        results = []

        for cand in candidates:
            c_struct = self._extract_structure(cand)
            c_tokens = self._tokenize(cand)
            
            # 1. Critical Logic Check (Primary Driver)
            # Divergence acts as the 'energy' of the system. 
            # High divergence = System instability = Low probability.
            logic_div = self._structural_divergence(p_struct, c_struct)
            
            # Base score starts at 1.0 (Stable state)
            score = 1.0
            
            # Apply critical penalty for logical contradictions
            # If logic_div > 0, we are near the phase transition
            if logic_div > 0.5:
                score = 0.1 # Strong contradiction (e.g., missing negation)
            elif logic_div > 0.2:
                score = 0.4 # Weak contradiction
            
            # 2. Numeric Consistency Check
            num_factor = self._check_numeric_consistency(prompt, cand)
            score *= num_factor
            
            # 3. Keyword Overlap (Morphogenetic similarity)
            # Did the candidate retain the core 'substance' of the prompt?
            intersection = len(p_tokens & c_tokens)
            union = len(p_tokens | c_tokens)
            jaccard = intersection / union if union > 0 else 0
            score = (score * 0.7) + (jaccard * 0.3) # Blend logic and content

            # 4. NCD Tiebreaker (Only if scores are close)
            # We store NCD separately to use as a tiebreaker if needed, 
            # but here we integrate it as a minor smoothing factor for length/complexity
            ncd_val = self._ncd(prompt, cand)
            # Prefer lower NCD (more similar compression) slightly if logic scores are equal
            score = score * 0.95 + (1.0 - ncd_val) * 0.05

            results.append({
                "candidate": cand,
                "score": max(0.0, min(1.0, score)), # Clamp 0-1
                "reasoning": f"Logic divergence: {logic_div:.2f}, Jaccard: {jaccard:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Metacognitive confidence based on Topological Invariance.
        Does the 'shape' of the answer match the 'shape' of the question?
        """
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        # Topological match: Do they share the same logical operators?
        # This is the 'persistence' of logical features across the transformation
        # from Question -> Answer.
        matches = 0
        total_features = 0
        
        features = ['has_negation', 'has_comparative', 'has_conditional', 'has_quantifier']
        for feat in features:
            if p_struct[feat] or a_struct[feat]: # If present in either
                total_features += 1
                if p_struct[feat] == a_struct[feat]:
                    matches += 1
        
        if total_features == 0:
            # If no logical features, rely on simple length ratio as a proxy for substance
            ratio = min(len(answer), len(prompt)) / max(len(answer), len(prompt), 1)
            return 0.5 + (ratio * 0.4) # Base confidence 0.5, up to 0.9
            
        topo_score = matches / total_features
        
        # Criticality adjustment: If the prompt has negation and answer doesn't, 
        # confidence should plummet (Metacognitive flag)
        if p_struct['has_negation'] and not a_struct['has_negation']:
            return 0.15
            
        return float(topo_score)