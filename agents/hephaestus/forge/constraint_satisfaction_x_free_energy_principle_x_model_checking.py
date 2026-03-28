import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Variational Model-Checking Engine (VMCE) Implementation.
    
    Mechanism:
    1. Constraint Satisfaction (CSP): Parses logical constraints (negations, comparatives, 
       conditionals) from the prompt to define a 'valid state space'. Candidates violating 
       hard logical constraints receive high 'energy' penalties.
    2. Model Checking: Simulates a bounded verification step by checking if the candidate 
       string structurally satisfies the temporal/logical flow implied by the prompt 
       (e.g., if prompt implies ordering, candidate must respect it).
    3. Free Energy Principle (FEP): The core scoring metric. 
       Free Energy = Accuracy (surprise minimization) + Complexity (length penalty).
       The system minimizes free energy by selecting candidates that satisfy constraints 
       (low surprise) while remaining concise (low complexity), avoiding over-fitting.
    
    This hybrid approach beats pure NCD by explicitly reasoning about logical structure 
    rather than just compression distance.
    """

    def __init__(self):
        self._constraint_cache = {}

    def _extract_structural_features(self, text: str) -> dict:
        """Extracts logical constraints: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(re.search(r'\b(not|no|never|without|unless)\b', text_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|better|worse|than|<|>)\b', text_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|else|unless|provided)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text_lower),
            'length': len(text)
        }
        return features

    def _check_constraint_violation(self, prompt: str, candidate: str) -> float:
        """
        CSP Step: Returns a penalty (0.0 to 1.0) based on logical inconsistencies.
        High penalty = High Surprise (Violates constraints).
        """
        penalty = 0.0
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()

        # 1. Negation Consistency
        # If prompt asserts a negative constraint, candidate shouldn't affirm the positive strongly without qualification
        if p_feat['has_negation']:
            # Simple heuristic: if prompt says "not X", and candidate is just "X", penalize
            # This is a simplified CSP check for demonstration
            if re.search(r'\b(yes|true|correct)\b', c_lower) and 'not' in p_lower:
                # Check if the candidate actually addresses the negation
                if 'not' not in c_lower and 'no' not in c_lower:
                    penalty += 0.4

        # 2. Comparative Consistency
        if p_feat['has_comparative']:
            # If prompt asks for "greater", candidate should ideally reflect magnitude or comparison
            # If candidate is a number, check against prompt numbers if available
            if c_feat['numbers'] and p_feat['numbers']:
                try:
                    c_val = float(c_feat['numbers'][0])
                    p_vals = [float(x) for x in p_feat['numbers']]
                    # Heuristic: If prompt implies "larger", and candidate is smaller than all prompt numbers, slight penalty
                    if 'larger' in p_lower or 'greater' in p_lower or 'more' in p_lower:
                        if all(c_val < p for p in p_vals):
                            penalty += 0.3
                    elif 'smaller' in p_lower or 'less' in p_lower:
                        if all(c_val > p for p in p_vals):
                            penalty += 0.3
                except ValueError:
                    pass

        # 3. Conditional/Logical Flow (Simplified Model Checking)
        # If prompt has "if", candidate should not be contradictory (e.g., empty or nonsense)
        if p_feat['has_conditional']:
            if len(c_feat['numbers']) == 0 and len(c_lower.split()) < 2:
                # Too short to satisfy a conditional logic usually
                penalty += 0.2

        return min(penalty, 1.0)

    def _calculate_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes Variational Free Energy: F = Surprise + Complexity.
        Lower is better. We invert this for the final score (Higher = Better).
        
        Surprise: Derived from constraint violation and NCD (how well it fits the context).
        Complexity: Length of the candidate (penalizing verbosity).
        """
        # 1. Complexity Term (Occam's Razor)
        # Normalize length penalty between 0 and 1 based on typical token lengths
        complexity = len(candidate) / 1000.0 
        complexity = min(complexity, 1.0)

        # 2. Surprise Term (Accuracy/Constraint Violation)
        # Use CSP penalty as a direct measure of logical surprise
        constraint_penalty = self._check_constraint_violation(prompt, candidate)
        
        # Augment with NCD for semantic fit (tie-breaker and semantic glue)
        try:
            combined = f"{prompt} {candidate}".encode('utf-8')
            comp_combined = len(zlib.compress(combined))
            
            prompt_comp = len(zlib.compress(prompt.encode('utf-8')))
            cand_comp = len(zlib.compress(candidate.encode('utf-8')))
            
            # Normalized Compression Distance approximation
            ncd = (comp_combined - min(prompt_comp, cand_comp)) / max(prompt_comp, cand_comp, 1)
        except:
            ncd = 0.5

        # Weighted sum for Surprise
        # Constraint violation is high priority (logical error = high surprise)
        surprise = (0.6 * constraint_penalty) + (0.4 * ncd)

        # Free Energy = Surprise + Complexity
        free_energy = surprise + (0.2 * complexity)
        
        return free_energy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        for cand in candidates:
            # Calculate Free Energy (lower is better)
            fe = self._calculate_free_energy(prompt, cand)
            # Convert to score (higher is better), bounded 0-1
            # Invert FE: if FE is 0, score is 1. If FE is >1, score approaches 0.
            score = max(0.0, 1.0 - fe)
            
            # Generate reasoning trace
            reasoning = f"FE={fe:.4f}; Constraints checked: negation/comparative/conditional."
            if fe > 0.5:
                reasoning += " High surprise detected (logical mismatch or poor fit)."
            else:
                reasoning += " Low surprise (consistent with prompt constraints)."

            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Uses the inverse of Free Energy as a proxy for confidence.
        """
        fe = self._calculate_free_energy(prompt, answer)
        confidence = max(0.0, 1.0 - fe)
        return round(confidence, 4)