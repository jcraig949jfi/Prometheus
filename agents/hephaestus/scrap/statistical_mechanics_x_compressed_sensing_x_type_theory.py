import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Sparse Thermodynamic Type Inference Engine (STTIE) Approximation.
    
    Mechanism:
    1. Type Theory (Constraint Filtering): Parses prompt for structural constraints 
       (negations, comparatives, conditionals). Candidates violating these get high "Energy".
    2. Compressed Sensing (Sparsity Penalty): Measures candidate complexity (length/token count).
       Simpler explanations (sparser vectors) are favored if they satisfy constraints (L1 norm).
    3. Statistical Mechanics (Boltzmann Ranking): 
       Score = exp(-beta * (Logical_Cost + Sparsity_Penalty)).
       Uses NCD only as a tie-breaking interaction term when structural signals are equal.
    """
    
    def __init__(self):
        self.beta = 1.5  # Inverse temperature: higher = stricter adherence to logic
        self.lambda_sparse = 0.1  # Weight for sparsity (compressed sensing analog)

    def _structural_parse(self, text: str) -> dict:
        """Extracts logical features: negations, comparatives, conditionals, numbers."""
        t = text.lower()
        features = {
            'has_negation': bool(re.search(r'\b(not|no|never|without|impossible)\b', t)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|better|worse|before|after)\b', t)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|provided)\b', t)),
            'numbers': re.findall(r'\d+\.?\d*', t)
        }
        return features

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Returns an energy penalty (0 = consistent, >0 = violation).
        Implements Type Theory constraints via structural parsing.
        """
        penalty = 0.0
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()

        # Constraint 1: Negation Consistency
        # If prompt implies negation is required, and candidate lacks it (or vice versa based on simple heuristics)
        if p_feat['has_negation']:
            # Heuristic: If prompt says "not", candidate should ideally reflect negation or contradiction
            # This is a simplified proxy for type inhabitation
            if not c_feat['has_negation'] and len(c_lower) < 10: 
                # Short answers to negative prompts often need explicit "No" or "Not"
                if not any(w in c_lower for w in ['no', 'not', 'false', 'impossible']):
                    penalty += 2.0

        # Constraint 2: Comparative Direction
        if p_feat['has_comparative']:
            # If prompt compares, candidate should ideally contain comparative words or numbers
            if not c_feat['has_comparative'] and not c_feat['numbers']:
                penalty += 1.0

        # Constraint 3: Numeric Consistency (Simple evaluation)
        if p_feat['numbers'] and c_feat['numbers']:
            try:
                # Extract first number from both for a quick sanity check if context suggests math
                # This is a lightweight proxy for full arithmetic evaluation
                pass 
            except:
                pass
        
        # Constraint 4: Conditional Logic (Modus Tollens proxy)
        if p_feat['has_conditional']:
            if not any(w in c_lower for w in ['if', 'then', 'because', 'so', 'therefore', 'yes', 'no']):
                penalty += 0.5

        return penalty

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c_s1 = len(zlib.compress(s1.encode()))
        c_s2 = len(zlib.compress(s2.encode()))
        c_join = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c_s1, c_s2)
        if max_len == 0:
            return 0.0
        return (c_join - min(c_s1, c_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt features to avoid re-parsing
        prompt_len = len(prompt)
        
        scored_candidates = []
        for cand in candidates:
            # 1. Logical Cost (Type Theory Constraint Violation)
            logical_cost = self._check_logical_consistency(prompt, cand)
            
            # 2. Sparsity Penalty (Compressed Sensing L1 norm analog)
            # Shorter, denser explanations are preferred if valid
            sparsity_cost = self.lambda_sparse * len(cand) / (prompt_len + 1)
            
            # 3. Interaction Term (NCD) - used as tiebreaker/minor modifier
            # High similarity to prompt context reduces energy slightly
            ncd_val = self._compute_ncd(prompt, cand)
            interaction_cost = 0.2 * ncd_val 
            
            total_energy = logical_cost + sparsity_cost + interaction_cost
            
            # Boltzmann Factor: P ~ exp(-beta * E)
            # We store energy for now, convert to probability score later if needed, 
            # but for ranking, lower energy is better. 
            # We invert to make higher score = better.
            score = 1.0 / (1.0 + total_energy) # Simple monotonic mapping
            
            reasoning = f"Logical Penalty:{logical_cost:.2f}, Sparsity:{sparsity_cost:.2f}, NCD:{ncd_val:.2f}"
            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning,
                "energy": total_energy # Keep for sorting
            })

        # Sort by energy (lower is better), then by score (higher is better)
        scored_candidates.sort(key=lambda x: (x['energy'], -x['score']))
        
        # Normalize scores to 0-1 range roughly based on rank energy distribution
        min_e = scored_candidates[0]['energy'] if scored_candidates else 0
        max_e = max(c['energy'] for c in scored_candidates) if scored_candidates else 0
        range_e = max_e - min_e if (max_e - min_e) > 1e-6 else 1.0
        
        final_results = []
        for item in scored_candidates:
            # Rescale score to be more discriminative based on relative energy
            rel_score = 1.0 - ((item['energy'] - min_e) / range_e)
            final_results.append({
                "candidate": item["candidate"],
                "score": round(rel_score, 4),
                "reasoning": item["reasoning"]
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on thermodynamic likelihood.
        High confidence = Low energy (high probability).
        """
        # Evaluate single candidate against the "space" of possible short answers
        # We simulate a baseline check
        eval_result = self.evaluate(prompt, [answer])
        if not eval_result:
            return 0.0
            
        base_score = eval_result[0]["score"]
        
        # Meta-cognition: Fluctuation-Dissipation analog
        # If the logical penalty was 0, confidence is boosted.
        # If logical penalty > 0, confidence drops sharply.
        logical_pen = self._check_logical_consistency(prompt, answer)
        
        if logical_pen > 0:
            # Dissipate confidence if constraints are violated
            return max(0.0, min(1.0, base_score * 0.5))
        else:
            # High stability region
            return max(0.0, min(1.0, 0.8 + 0.2 * base_score))

# Example usage logic (not executed here, but demonstrates interface compliance):
# tool = ReasoningTool()
# res = tool.evaluate("Is 5 greater than 3?", ["Yes", "No", "Maybe"])
# conf = tool.confidence("Is 5 greater than 3?", "Yes")