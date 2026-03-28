import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Dynamic Immune Analogy Engine (DIAE) - Implementation Strategy:
    
    Core Architecture (Analogical Reasoning - Primary Driver):
    Instead of simulating complex biological dynamics (which are historical inhibitors for direct scoring),
    this tool implements the 'Structure-Mapping Engine' (SME) concept via structural parsing.
    It maps relational structures (negations, comparatives, conditionals) from the prompt to candidates.
    
    Dynamical Systems & Immune Concepts (Confidence Wrapper Only):
    - 'Attractors' are modeled as structural consistency.
    - 'Lyapunov exponents' are approximated by sensitivity to negation flips.
    - 'Clonal Selection' is the ranking process based on structural affinity.
    These concepts regulate the confidence() method and internal weighting, not the primary score.
    
    Scoring Mechanism:
    1. Structural Parsing: Extract logic gates (NOT, IF, >, <).
    2. Affinity Calculation: Measure candidate alignment with extracted structural constraints.
    3. NCD Tiebreaker: Used only if structural signals are weak or identical.
    """

    def __init__(self):
        # Structural keywords for analogical mapping
        self.negations = ['not', 'no', 'never', 'none', 'cannot', 'impossible']
        self.comparators = ['>', '<', 'greater', 'less', 'more', 'fewer', 'before', 'after']
        self.conditionals = ['if', 'then', 'unless', 'only if', 'when']
        self.numeric_pattern = re.compile(r"-?\d+\.?\d*")

    def _extract_structure(self, text: str) -> Dict[str, Any]:
        """Parse text for logical structures (Negations, Comparatives, Numbers)."""
        text_lower = text.lower()
        has_negation = any(n in text_lower for n in self.negations)
        has_comparator = any(c in text_lower for c in self.comparators)
        has_conditional = any(c in text_lower for c in self.conditionals)
        
        # Extract numbers for numeric evaluation
        numbers = [float(n) for n in self.numeric_pattern.findall(text)]
        
        return {
            'negation': has_negation,
            'comparator': has_comparator,
            'conditional': has_conditional,
            'numbers': numbers,
            'length': len(text.split())
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        c1 = len(zlib.compress(s1_bytes))
        c2 = len(zlib.compress(s2_bytes))
        c12 = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _structural_affinity(self, prompt_struct: Dict, cand_struct: Dict, candidate: str) -> float:
        """
        Calculate affinity based on structural mapping (SME).
        High affinity = Candidate preserves relational structure of the prompt.
        """
        score = 0.0
        total_weight = 0.0

        # 1. Negation Mapping: If prompt has negation, correct answer often needs to reflect it
        # or explicitly contradict a false premise. 
        if prompt_struct['negation']:
            total_weight += 2.0
            # Heuristic: If prompt negates, and candidate is very short (Yes/No), 
            # we rely on NCD later. If candidate has logical words, check alignment.
            # Simple proxy: Does the candidate length suggest a reasoned response vs a blind guess?
            if cand_struct['length'] > 2: 
                score += 1.0
            # Stronger signal: If prompt has numbers and comparator, check numeric logic
            if prompt_struct['numbers'] and prompt_struct['comparator']:
                # This is a specific reasoning trap check
                if cand_struct['numbers']:
                    score += 2.0 # Bonus for carrying over numeric evidence
                else:
                    score -= 1.0 # Penalty for ignoring numeric constraints

        # 2. Conditional Mapping
        if prompt_struct['conditional']:
            total_weight += 1.5
            if cand_struct['conditional'] or cand_struct['length'] > 5:
                score += 1.0

        # 3. Numeric Consistency
        if prompt_struct['numbers']:
            total_weight += 2.0
            # If prompt has numbers, candidate having numbers is a strong structural analog
            if cand_struct['numbers']:
                score += 1.5
                # Check for direct number presence (often the answer is one of the numbers or a result)
                p_nums = set(prompt_struct['numbers'])
                c_nums = set(cand_struct['numbers'])
                if p_nums.intersection(c_nums):
                    score += 1.0 # Direct number match
            
        # Normalize by weight to get a base affinity, but keep absolute score for ranking
        return score if total_weight > 0 else 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        prompt_struct = self._extract_structure(prompt)
        results = []

        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # Primary Score: Structural Affinity (Analogical Reasoning)
            struct_score = self._structural_affinity(prompt_struct, cand_struct, cand)
            
            # Secondary Score: NCD (Tiebreaker/Noise reduction)
            # We invert NCD because higher is better, but NCD 0 is identical
            ncd_val = self._compute_ncd(prompt, cand)
            
            # Hybrid Score Construction
            # If structural signal is strong (prompt has logic), dominate with struct_score
            has_logic_signal = any([prompt_struct['negation'], prompt_struct['comparator'], prompt_struct['conditional'], prompt_struct['numbers']])
            
            if has_logic_signal:
                # Scale struct_score to be dominant (0 to ~5 range)
                # Add small NCD component to break ties among structurally similar answers
                final_score = struct_score + (0.01 * (1.0 - ncd_val))
            else:
                # Fallback for unstructured prompts: Use NCD primarily
                # Lower NCD (more similar) is usually better for simple QA, 
                # but we want to avoid exact echoes. 
                # We use a heuristic: moderate similarity is good.
                final_score = 0.5 - abs(0.5 - (1.0 - ncd_val)) 

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural Affinity: {struct_score:.2f}, NCD: {ncd_val:.2f}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Computes confidence using Dynamical Systems analogy (Lyapunov stability).
        
        Mechanism:
        1. Define 'Perturbation': Flip negations or swap comparators in the prompt.
        2. Measure 'Divergence': Compare structural affinity of the answer to original vs perturbed prompt.
        3. Stability: If the answer remains high-affinity despite perturbation, it's robust (High Confidence).
           If the score flips wildly, the hypothesis is in an unstable region (Low Confidence).
           
        Note: Per constraints, this concept is restricted to the confidence wrapper.
        """
        orig_struct = self._extract_structure(prompt)
        ans_struct = self._extract_structure(answer)
        base_affinity = self._structural_affinity(orig_struct, ans_struct, answer)
        
        # Create a 'perturbed' version of the prompt (simulating instability)
        perturbed_prompt = prompt
        has_neg = any(n in prompt.lower() for n in self.negations)
        
        if has_neg:
            # Remove negations to test sensitivity
            for n in self.negations:
                perturbed_prompt = perturbed_prompt.replace(n, "")
        else:
            # Add a negation to test sensitivity
            perturbed_prompt = "not " + prompt
            
        pert_struct = self._extract_structure(perturbed_prompt)
        pert_affinity = self._structural_affinity(pert_struct, ans_struct, answer)
        
        # Calculate divergence (Lyapunov exponent approximation)
        divergence = abs(base_affinity - pert_affinity)
        
        # Map divergence to confidence (0-1)
        # Low divergence -> High confidence (Stable attractor)
        # High divergence -> Low confidence (Unstable manifold)
        # Using a simple decay function
        confidence_val = 1.0 / (1.0 + divergence)
        
        # Boost if base affinity is also high
        if base_affinity > 1.0:
            confidence_val = min(1.0, confidence_val + 0.2)
            
        return float(confidence_val)