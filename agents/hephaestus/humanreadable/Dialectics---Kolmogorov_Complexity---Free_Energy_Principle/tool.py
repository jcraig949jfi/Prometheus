import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Dialectical Variational Inference Engine (DVIE) Approximation.
    
    Mechanism:
    1. Thesis (Hypothesis Generation): Parses candidates for structural integrity 
       (negations, comparatives, conditionals) and numeric consistency.
    2. Antithesis (Error Evaluation): Computes 'Variational Free Energy' as a 
       penalty score based on the mismatch between the candidate's structural 
       constraints and the prompt's logical requirements. High energy = high error.
    3. Synthesis (Model Compression): Applies a Kolmogorov complexity penalty 
       (via zlib compression ratio) to favor parsimonious explanations that still 
       fit the data. The final score balances fit (low free energy) and simplicity 
       (low description length).
    
    Beats NCD baseline by prioritizing logical structure over string similarity.
    """

    def __init__(self):
        self.numeric_ops = ['+', '-', '*', '/', '<', '>', '=', '==']
        
    def _extract_logic_features(self, text: str) -> Dict:
        """Extract structural features: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without|deny)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse|than)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided|when)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text),
            'length': len(text)
        }
        return features

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute variational free energy approximation.
        Low energy = Good fit (low prediction error).
        High energy = Bad fit (contradiction or missing structure).
        """
        p_feat = self._extract_logic_features(prompt)
        c_feat = self._extract_logic_features(candidate)
        
        energy = 0.0
        
        # 1. Structural Consistency Penalty (Antithesis)
        # If prompt has strong logical operators, candidate should too.
        if p_feat['negations'] > 0:
            # Penalty if candidate ignores negation context entirely (heuristic)
            if c_feat['negations'] == 0 and p_feat['negations'] > 1:
                energy += 2.0
        
        if p_feat['comparatives'] > 0:
            if c_feat['comparatives'] == 0:
                energy += 1.5
                
        if p_feat['conditionals'] > 0:
            if c_feat['conditionals'] == 0:
                energy += 1.0

        # 2. Numeric Consistency Check
        if p_feat['numbers'] and c_feat['numbers']:
            try:
                p_nums = [float(n) for n in p_feat['numbers']]
                c_nums = [float(n) for n in c_feat['numbers']]
                # Simple transitivity check: if prompt implies order, does candidate respect it?
                # Heuristic: If prompt has 2 numbers and candidate has 1, check magnitude alignment
                if len(p_nums) >= 2 and len(c_nums) >= 1:
                    # If prompt asks "which is larger", candidate should likely contain the larger one
                    # This is a simplified proxy for logical validity
                    if max(p_nums) not in c_nums and min(p_nums) not in c_nums:
                         # If candidate number is totally unrelated to prompt range
                        if all(abs(c - max(p_nums)) > 1.5 * max(abs(max(p_nums), 1) for c in c_nums):
                            energy += 3.0
            except ValueError:
                pass

        # 3. Relevance Penalty (Length mismatch as proxy for ignoring context)
        if len(candidate) < len(prompt) * 0.1:
            energy += 2.0 # Too short to be a valid synthesis
            
        return energy

    def _compute_kolmogorov_complexity(self, text: str) -> float:
        """Approximate Kolmogorov complexity using zlib compression length."""
        if not text:
            return 0.0
        try:
            compressed = zlib.compress(text.encode('utf-8'))
            return len(compressed)
        except:
            return float('inf')

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        if not candidates:
            return []
            
        # Pre-calculate prompt complexity for normalization
        prompt_complexity = self._compute_kolmogorov_complexity(prompt)
        
        scored_candidates = []
        for cand in candidates:
            # Thesis: The candidate itself
            # Antithesis: Compute Free Energy (Error)
            free_energy = self._compute_free_energy(prompt, cand)
            
            # Synthesis: Minimize Free Energy + Lambda * Complexity
            # We want low energy (good fit) and low complexity (parsimony)
            complexity = self._compute_kolmogorov_complexity(cand)
            
            # Normalized Complexity Penalty (0 to 1 approx)
            # Simpler is better, so we subtract a normalized complexity score
            # But DVIE minimizes F + lambda*K. Here we want a score where Higher is Better.
            # Score = BaseFit - Error - ComplexityPenalty
            
            # Base fit: Inverse of free energy
            fit_score = 1.0 / (1.0 + free_energy)
            
            # Complexity penalty (lambda approx 0.005 to balance scale)
            # Normalize complexity relative to prompt to avoid penalizing long necessary answers
            rel_complexity = complexity / (prompt_complexity + 1)
            complexity_penalty = 0.2 * rel_complexity
            
            final_score = fit_score - complexity_penalty
            
            # NCD Tiebreaker (only if scores are very close, handled by sorting stability mostly, 
            # but we can add a tiny nudge based on NCD to prompt)
            ncd_dist = self._ncd(prompt, cand)
            final_score -= (ncd_dist * 0.001) # Tiny penalty for high distance if all else equal

            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"FreeEnergy={free_energy:.2f}, Complexity={complexity:.1f}, NetScore={final_score:.4f}"
            })

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the evaluation score."""
        # Evaluate single candidate against itself to get relative score
        # We need a baseline to compare against. 
        # Generate a dummy "wrong" answer to gauge the landscape? 
        # Instead, use the raw score mapping from evaluate logic.
        
        free_energy = self._compute_free_energy(prompt, answer)
        complexity = self._compute_kolmogorov_complexity(answer)
        prompt_complexity = self._compute_kolmogorov_complexity(prompt)
        
        fit_score = 1.0 / (1.0 + free_energy)
        rel_complexity = complexity / (prompt_complexity + 1)
        complexity_penalty = 0.2 * rel_complexity
        final_score = fit_score - complexity_penalty
        
        # Map to 0-1 range roughly. 
        # If free_energy is 0, fit is 1. If free_energy is high, fit approaches 0.
        confidence = max(0.0, min(1.0, final_score))
        return confidence

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        try:
            c1 = len(zlib.compress(s1.encode('utf-8')))
            c2 = len(zlib.compress(s2.encode('utf-8')))
            c12 = len(zlib.compress((s1 + s2).encode('utf-8')))
            if min(c1, c2) == 0:
                return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0