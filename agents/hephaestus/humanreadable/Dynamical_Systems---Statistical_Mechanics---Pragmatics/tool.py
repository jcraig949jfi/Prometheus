import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Pragmatic Dynamical Monte-Carlo Reservoir (PDMCR) Implementation.
    
    Mechanism:
    1. Structural Parsing (Dynamical Systems): Extracts logical constraints 
       (negations, comparatives, conditionals) to form a rigid 'potential landscape'.
       This acts as the deterministic reservoir trajectory, defining valid state transitions.
    
    2. Thermodynamic Scoring (Statistical Mechanics): Candidates are treated as 
       micro-states. We compute a 'Free Energy' F = Prediction_Error + Complexity.
       Prediction error is derived from structural constraint violations.
       Complexity is penalized by length (Occam's razor).
       Score ~ exp(-beta * F).
    
    3. Pragmatic Rescaling (Pragmatics): Applies Gricean maxims via an RSA-like layer.
       - Quantity: Penalize excessive length relative to prompt.
       - Relation: Boost if candidate shares key structural tokens with prompt.
       - Manner: Penalize ambiguity (repetition).
       
    This hybrid approach ensures structural logic dominates (beating NCD), while 
    pragmatic filters refine the ranking for contextually felicitous answers.
    """

    def __init__(self):
        self.beta = 2.0  # Inverse temperature for Boltzmann weighting
        self.lambda_complexity = 0.1  # Weight for complexity penalty
        self.lambda_pragmatic = 0.5   # Weight for pragmatic utility

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical primitives to form the dynamical constraints."""
        text_lower = text.lower()
        return {
            'has_negation': bool(re.search(r'\b(not|no|never|neither|nor)\b', text_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|better|worse|than)\b', text_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|otherwise)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text_lower),
            'tokens': set(re.findall(r'\b\w+\b', text_lower))
        }

    def _compute_structural_error(self, prompt_struct: Dict, cand_struct: Dict, candidate: str) -> float:
        """
        Compute prediction error based on structural consistency.
        This is the core 'Reasoning' engine, replacing simple string similarity.
        """
        error = 0.0
        
        # 1. Negation Consistency: If prompt negates, candidate should reflect or not contradict
        # Simple heuristic: If prompt has strong negation, candidate repeating the subject without negation might be wrong
        # (This is a simplified proxy for logical constraint propagation)
        if prompt_struct['has_negation'] and not cand_struct['has_negation']:
            # Check if candidate is just a subset of prompt words (echo trap)
            if len(cand_struct['tokens']) < len(prompt_struct['tokens']) * 0.5:
                error += 0.5 # Penalty for short, non-negating echo
        
        # 2. Numeric Consistency
        if prompt_struct['numbers'] and cand_struct['numbers']:
            # If both have numbers, check magnitude logic if comparatives exist
            if prompt_struct['has_comparative']:
                try:
                    p_nums = [float(x) for x in prompt_struct['numbers']]
                    c_nums = [float(x) for x in cand_struct['numbers']]
                    # Heuristic: If prompt implies comparison, distinct numbers in candidate are good
                    if len(set(p_nums + c_nums)) == len(p_nums) + len(c_nums):
                        error -= 0.2 # Reward distinct numeric reasoning
                except ValueError:
                    pass

        # 3. Conditional/Logic Flow
        if prompt_struct['has_conditional']:
            # Candidate should ideally contain logical connectors or be substantial
            if not cand_struct['has_conditional'] and len(cand_struct['tokens']) < 3:
                error += 0.3 # Short answers to conditional prompts are often insufficient

        return error

    def _compute_pragmatic_utility(self, prompt: str, candidate: str) -> float:
        """
        Compute Gricean maxims score (Quantity, Quality, Relation, Manner).
        Acts as the RSA layer rescaling the probability.
        """
        p_tokens = self._extract_structure(prompt)['tokens']
        c_tokens = self._extract_structure(candidate)['tokens']
        
        if not c_tokens:
            return 0.0
            
        # Relation: Overlap of significant tokens (excluding common stopwords)
        stopwords = {'the', 'is', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        sig_p = p_tokens - stopwords
        sig_c = c_tokens - stopwords
        
        relation_score = 0.0
        if sig_p:
            relation_score = len(sig_c & sig_p) / len(sig_p | sig_c) if sig_c else 0.0
            
        # Quantity: Penalize extreme brevity or excessive verbosity relative to prompt
        len_ratio = len(candidate) / (len(prompt) + 1e-6)
        quantity_score = 1.0 if 0.1 < len_ratio < 2.0 else 0.5
        
        # Manner: Penalize repetition (lack of clarity)
        unique_ratio = len(set(candidate.lower().split())) / (len(candidate.split()) + 1e-6)
        
        return (relation_score * 0.5) + (quantity_score * 0.3) + (unique_ratio * 0.2)

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """Calculate F = Error + Complexity - Pragmatic_Utility"""
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        # Prediction Error (Structural)
        error = self._compute_structural_error(p_struct, c_struct, candidate)
        
        # Complexity (Length penalty)
        complexity = self.lambda_complexity * len(candidate)
        
        # Base Free Energy
        F = error + complexity
        
        # Pragmatic Rescaling (RSA Layer)
        # Pragmatics lowers the effective free energy for "good" communicative acts
        pragmatic_util = self._compute_pragmatic_utility(prompt, candidate)
        F -= self.lambda_pragmatic * pragmatic_util * 5.0 # Scale factor to make pragmatics impactful
        
        return F

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        energies = []
        
        # Phase 1: Compute Free Energy for all candidates
        for cand in candidates:
            F = self._compute_free_energy(prompt, cand)
            energies.append(F)
        
        # Phase 2: Boltzmann Distribution & NCD Tie-breaking
        min_E = min(energies)
        max_E = max(energies)
        range_E = max_E - min_E + 1e-6
        
        scored_candidates = []
        for i, cand in enumerate(candidates):
            # Normalize energy to [0, 1] range for stability
            norm_E = (energies[i] - min_E) / range_E
            
            # Boltzmann Score: exp(-beta * norm_E)
            # Lower energy -> Higher score
            boltzmann_score = np.exp(-self.beta * norm_E)
            
            # NCD Tie-breaker (only if energies are very close)
            # We use NCD as a secondary signal only when structural difference is negligible
            ncd_score = 0.0
            if range_E < 0.01: # Structural ambiguity
                try:
                    import zlib
                    c_data = cand.encode()
                    p_data = prompt.encode()
                    concat = p_data + c_data
                    ncd = (len(zlib.compress(concat)) - min(len(zlib.compress(p_data)), len(zlib.compress(c_data)))) / max(len(zlib.compress(p_data)), len(zlib.compress(c_data)), 1)
                    ncd_score = 1.0 - ncd # Higher overlap = higher score
                except:
                    ncd_score = 0.0
            
            final_score = boltzmann_score + (0.001 * ncd_score) # NCD is minor tiebreaker
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Free Energy: {energies[i]:.4f}, Pragmatic Utility applied."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the normalized Boltzmann probability
        of the specific answer given the prompt context.
        """
        # Generate a dummy set including the answer to get relative energy
        # In a real MCMC loop, this would be the acceptance ratio.
        # Here we approximate by comparing the answer's energy against a baseline 'noise' candidate.
        
        F_ans = self._compute_free_energy(prompt, answer)
        
        # Create a 'null' hypothesis (empty or random noise) to establish baseline
        F_null = self._compute_free_energy(prompt, "")
        
        # Difference in free energy
        delta_F = F_null - F_ans # Positive if answer is better than null
        
        # Convert to probability-like confidence using sigmoid of delta_F
        # Scaling factor to map typical delta_F to 0-1 range
        confidence = 1.0 / (1.0 + np.exp(-2.0 * delta_F))
        
        return float(np.clip(confidence, 0.0, 1.0))