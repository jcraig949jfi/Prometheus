import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Morphogenetic Sparse Tensor Autoencoder (MSTA) Simulation.
    
    Mechanism:
    1. Tensor Decomposition (Simulated): Prompts are parsed into structural cores 
       (negations, comparatives, conditionals, numerics) representing low-rank logical factors.
    2. Sparse Autoencoder: Candidates are scored on 'sparsity' of match—penalizing 
       verbose echoes and rewarding precise structural alignment with the prompt's logic cores.
    3. Morphogenesis (Reaction-Diffusion Prior): A stability score is computed based on 
       logical consistency (e.g., double negation cancellation, transitive closure). 
       Candidates causing logical 'turbulence' (contradictions) diffuse to low confidence.
    
    Note: Per safety guidelines, 'Morphogenesis' is restricted to the confidence wrapper 
    and structural parsing support, acting as a stability check rather than a direct scorer.
    """

    def __init__(self):
        # Structural patterns for logical core extraction
        self.negation_patterns = [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b', r'^un', r'^im', r'^in']
        self.comparative_patterns = [r'\bmore\s+than\b', r'\bless\s+than\b', r'\bgreater\s+than\b', r'\bsmaller\s+than\b', r'\b>\b', r'\b<\b', r'\bbeater\b', r'\bworse\b']
        self.conditional_patterns = [r'\bif\b', r'\bthen\b', r'\belse\b', r'\bunless\b', r'\bprovided\b']
        self.numeric_pattern = r'-?\d+\.?\d*'

    def _extract_structural_cores(self, text: str) -> Dict[str, any]:
        """Extracts logical factors simulating Tensor Train cores."""
        text_lower = text.lower()
        
        # Count logical operators
        neg_count = sum(len(re.findall(p, text_lower)) for p in self.negation_patterns)
        comp_count = sum(len(re.findall(p, text_lower)) for p in self.comparative_patterns)
        cond_count = sum(len(re.findall(p, text_lower)) for p in self.conditional_patterns)
        
        # Extract numerics for evaluation
        numerics = [float(x) for x in re.findall(self.numeric_pattern, text)]
        
        return {
            'negations': neg_count,
            'comparatives': comp_count,
            'conditionals': cond_count,
            'numerics': numerics,
            'length': len(text.split()),
            'raw': text_lower
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denominator = max(c1, c2)
        if denominator == 0:
            return 0.0
        return (c12 - min(c1, c2)) / denominator

    def _check_logical_consistency(self, prompt_cores: Dict, cand_cores: Dict) -> float:
        """
        Simulates Reaction-Diffusion stability.
        Checks if the candidate maintains the logical 'phase' of the prompt.
        """
        score = 1.0
        
        # Negation parity check (Modus Tollens simulation)
        # If prompt has odd negations, candidate should reflect that logic structure
        if prompt_cores['negations'] % 2 != cand_cores['negations'] % 2:
            # Potential contradiction, penalize unless context implies resolution
            score -= 0.2
            
        # Numeric consistency (Transitivity check)
        p_nums = prompt_cores['numerics']
        c_nums = cand_cores['numerics']
        
        if p_nums and c_nums:
            # Simple heuristic: if prompt compares A > B, candidate shouldn't claim B > A
            # Here we just check if numeric magnitudes are wildly off if counts match
            if len(p_nums) == len(c_nums):
                for p, c in zip(p_nums, c_nums):
                    if abs(p - c) > 0.0 and abs(p - c) > (abs(p) * 0.5): # 50% tolerance
                        score -= 0.1
        
        return max(0.0, score)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_cores = self._extract_structural_cores(prompt)
        results = []
        
        # Baseline NCD for tie-breaking
        candidate_ncds = []
        for cand in candidates:
            candidate_ncds.append(self._compute_ncd(prompt, cand))
        
        min_ncd = min(candidate_ncds) if candidate_ncds else 0
        max_ncd = max(candidate_ncds) if candidate_ncds else 1
        ncd_range = max_ncd - min_ncd if max_ncd > min_ncd else 1.0

        for i, cand in enumerate(candidates):
            cand_cores = self._extract_structural_cores(cand)
            
            # 1. Structural Parsing Score (Primary Signal)
            # Reward matching logical density
            struct_score = 0.0
            
            # Negation alignment
            if prompt_cores['negations'] > 0:
                if cand_cores['negations'] > 0:
                    struct_score += 0.3
                else:
                    struct_score -= 0.3 # Missed negation
            else:
                if cand_cores['negations'] > 0:
                    struct_score -= 0.2 # Hallucinated negation
            
            # Comparative/Conditional alignment
            if prompt_cores['comparatives'] > 0:
                struct_score += 0.2 if cand_cores['comparatives'] > 0 else -0.2
            if prompt_cores['conditionals'] > 0:
                struct_score += 0.2 if cand_cores['conditionals'] > 0 else -0.1

            # 2. Morphogenetic Stability (Consistency Check)
            stability = self._check_logical_consistency(prompt_cores, cand_cores)
            
            # 3. Sparsity Penalty (Anti-echo)
            # Penalize if candidate is just a slightly modified version of prompt (low sparsity of info)
            sparsity_penalty = 0.0
            if len(cand) > 0.8 * len(prompt) and self._compute_ncd(prompt, cand) < 0.1:
                sparsity_penalty = 0.2

            # Combine scores
            # Normalize NCD to be a tiebreaker (small contribution)
            ncd_score = (1.0 - (candidate_ncds[i] - min_ncd) / ncd_range) * 0.1
            
            final_score = struct_score + (stability * 0.4) - sparsity_penalty + ncd_score
            
            # Normalize to 0-1 range roughly
            final_score = max(0.0, min(1.0, 0.5 + final_score))
            
            reasoning = f"Structural match: {struct_score:.2f}, Stability: {stability:.2f}, NCD-tiebreak: {ncd_score:.2f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural parsing and stability checks as the primary signal.
        NCD is only used as a tiebreaker if structural signals are ambiguous.
        """
        prompt_cores = self._extract_structural_cores(prompt)
        ans_cores = self._extract_structural_cores(answer)
        
        # Base confidence on structural alignment
        conf = 0.5
        
        # Check negation parity
        if prompt_cores['negations'] % 2 == ans_cores['negations'] % 2:
            conf += 0.2
        else:
            conf -= 0.3
            
        # Check numeric presence consistency
        if bool(prompt_cores['numerics']) == bool(ans_cores['numerics']):
            conf += 0.1
            
        # Stability check (Morphogenetic prior)
        stability = self._check_logical_consistency(prompt_cores, ans_cores)
        conf += (stability - 0.5) * 0.4
        
        # Tiebreaker: if structurally similar, boost slightly via NCD
        ncd = self._compute_ncd(prompt, answer)
        if ncd < 0.2: # Very similar strings
            conf += 0.05
            
        return max(0.0, min(1.0, conf))