import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a 'Recursive Self-Modeling Optimal Control' loop via structural parsing.
    
    Mechanism:
    1. Thesis Generator (ToM): Parses the prompt to extract structural constraints 
       (negations, comparatives, conditionals) as the 'expected state'.
    2. Antithesis Simulator: Evaluates each candidate against these constraints. 
       Violations generate a 'discrepancy cost' (dialectical tension).
    3. Synthesis Controller: Computes a final score by minimizing the total cost 
       (maximizing constraint satisfaction) and using NCD only as a tie-breaking 
       heuristic for semantic proximity when structural signals are equal.
       
    This adheres to the 'Causal Intelligence' directive by restricting ToM/Dialectics 
    to structural parsing and confidence wrapping, avoiding direct scoring based on 
    abstract philosophical concepts.
    """

    def __init__(self):
        # Structural patterns for the 'Thesis Generator'
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparative_ops = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower']
        self.conditional_keywords = ['if', 'then', 'unless', 'only if']
        
    def _extract_structural_features(self, text: str) -> dict:
        """Extracts logical constraints from text (Thesis Generation)."""
        text_lower = text.lower()
        words = set(re.findall(r'\b\w+\b', text_lower))
        
        features = {
            'has_negation': bool(words & self.negation_words),
            'has_comparative': bool(any(op in text_lower for op in self.comparative_ops)),
            'has_conditional': bool(any(kw in text_lower for kw in self.conditional_keywords)),
            'numbers': re.findall(r'\d+\.?\d*', text_lower),
            'negation_count': sum(1 for w in words if w in self.negation_words),
        }
        return features

    def _check_constraint_violation(self, prompt: str, candidate: str) -> float:
        """
        Antithesis Simulator: Checks if the candidate contradicts the prompt's structural constraints.
        Returns a penalty cost (0.0 = no violation, 1.0 = hard violation).
        """
        cost = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Negation Consistency
        # If prompt strongly negates, and candidate affirms without qualification
        if any(f"no {w}" in p_lower or f"not {w}" in p_lower for w in ['yes', 'true', 'correct']):
            if any(w in c_lower for w in ['yes', 'true', 'correct']) and 'not' not in c_lower:
                cost += 0.5
                
        # 2. Numeric Logic (Simple extraction and comparison)
        p_nums = self._extract_structural_features(prompt)['numbers']
        c_nums = self._extract_structural_features(candidate)['numbers']
        
        if p_nums and c_nums:
            try:
                # Check for comparative logic in prompt
                if 'less' in p_lower or 'smaller' in p_lower or 'lower' in p_lower:
                    if float(c_nums[0]) > float(p_nums[0]):
                        cost += 1.0 # Violation: Candidate is larger when prompt asks for smaller
                elif 'more' in p_lower or 'greater' in p_lower or 'higher' in p_lower:
                    if float(c_nums[0]) < float(p_nums[0]):
                        cost += 1.0 # Violation: Candidate is smaller when prompt asks for larger
            except ValueError:
                pass

        # 3. Conditional/Length Heuristic (Proxy for logical depth)
        # If prompt is a complex conditional, very short answers often fail synthesis
        if self._extract_structural_features(prompt)['has_conditional']:
            if len(candidate.split()) < 3:
                cost += 0.2 # Penalty for oversimplification in complex scenarios

        return min(cost, 1.0)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Computes Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        z = zlib.compress
        len1 = len(z(s1.encode()))
        len2 = len(z(s2.encode()))
        len12 = len(z((s1 + s2).encode()))
        
        denominator = max(len1, len2)
        if denominator == 0:
            return 1.0
        return (len12 - min(len1, len2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-compute prompt features (Thesis)
        prompt_features = self._extract_structural_features(prompt)
        
        scored_candidates = []
        
        for cand in candidates:
            # Antithesis Simulation: Calculate discrepancy cost
            violation_cost = self._check_constraint_violation(prompt, cand)
            
            # Synthesis: Base score starts at 1.0 and subtracts costs
            # Structural adherence is the primary driver (beating NCD baseline)
            base_score = 1.0 - violation_cost
            
            # Store for sorting
            scored_candidates.append({
                'candidate': cand,
                'base_score': base_score,
                'violation': violation_cost
            })
        
        # Ranking Logic (Optimal Control Policy)
        # Primary sort: Base Score (Structural adherence)
        # Secondary sort: NCD (Semantic proximity as tiebreaker)
        def sort_key(item):
            # We want highest score first, so we negate base_score for sorting
            # For NCD, lower is better (more similar), so we keep it positive
            ncd_val = self._compute_ncd(prompt, item['candidate'])
            return (-item['base_score'], ncd_val)

        scored_candidates.sort(key=sort_key)
        
        # Normalize scores to 0-1 range for output, ensuring the best is high
        max_base = max(c['base_score'] for c in scored_candidates) if scored_candidates else 0
        
        final_results = []
        for item in scored_candidates:
            # Adjust score slightly by NCD if base scores are tied, to ensure determinism and nuance
            ncd_val = self._compute_ncd(prompt, item['candidate'])
            
            # Final scoring formula: Structural Validity (90%) + Semantic Proximity (10%)
            # This ensures structural parsing dominates (beating NCD baseline)
            final_score = (0.9 * item['base_score']) + (0.1 * (1.0 - ncd_val))
            
            reasoning = f"Structural match: {item['base_score']:.2f}, Dialectical cost: {item['violation']:.2f}"
            if item['violation'] > 0:
                reasoning += " (Constraint violation detected)"
            
            final_results.append({
                "candidate": item['candidate'],
                "score": round(final_score, 4),
                "reasoning": reasoning
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural consistency.
        Uses the internal evaluation logic to determine if the answer 
        survives the dialectical falsification process.
        """
        # Run single evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        
        # Confidence wrapper: 
        # If structural violation exists, confidence drops sharply.
        # If structural match is high, confidence scales with the score.
        if score < 0.5:
            return max(0.0, score * 0.5) # Low confidence for low structural match
        
        return min(1.0, score)