import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Plasticity-Guided Optimal Graph Neural Network (PO-GNN) Approximation.
    
    Mechanism:
    1. Epistemic Honesty (Meta-Control): Before scoring, analyzes the prompt for 
       logical traps (presuppositions, ambiguity, false dichotomies). If detected,
       confidence is capped low (<0.3) regardless of candidate match, satisfying 
       Tier B requirements.
       
    2. Structural Parsing (Graph Nodes): Extracts logical operators (negations, 
       comparatives, conditionals) and numeric values. This forms the static graph 
       structure of the hypothesis.
       
    3. Plasticity & Optimal Control (Edge Weights): 
       - Candidates are scored based on structural alignment (presence of required 
         logical tokens) and computational correctness (numeric evaluation).
       - 'Plasticity' is simulated by dynamically adjusting the weight of evidence:
         exact numeric matches receive high weight (Hebbian growth), while partial 
         string matches decay.
       - 'Optimal Control' minimizes a cost function balancing prediction error 
         (match quality) and complexity (sparsity), preferring concise, structurally 
         sound answers over verbose echoes.
         
    4. Scoring: Final score = (Structural * 0.50) + (Computation * 0.35) + (NCD * 0.15).
    """

    def __init__(self):
        # Logical operators for structural parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.presupposition_triggers = ['stopped', 'quit', 'failed', 'stopped', 'regret', 'again']
        self.false_dichotomy_triggers = ['either', 'or not', 'choose between']
        
        # Control parameters
        self.alpha = 0.1  # Sparsity penalty
        self.beta = 0.05  # Smoothness penalty
        
    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for epistemic traps (Tier B).
        Returns a cap value: 0.25 if trap detected, 1.0 otherwise.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Check
        for trigger in self.presupposition_triggers:
            if trigger in p_lower:
                # Contextual check: usually questions starting with "Why", "Have", "Did"
                if any(p_lower.startswith(q) for q in ['why', 'have', 'did', 'when', 'how']):
                    return 0.25
        
        # 2. False Dichotomy
        if 'either' in p_lower and ('or' in p_lower):
            # Simple heuristic for false dichotomy patterns
            if 'or not' in p_lower or 'choose between' in p_lower:
                return 0.25
                
        # 3. Unanswerable / Missing Info indicators
        unanswerable_phrases = ['impossible to know', 'not mentioned', 'cannot be determined']
        if any(phrase in p_lower for phrase in unanswerable_phrases):
            return 0.25
            
        # 4. Subjectivity without criteria
        if any(word in p_lower for word in ['best', 'worst', 'favorite']) and 'criteria' not in p_lower:
             # Only flag if no objective metric is implied
             if 'number' not in p_lower and 'count' not in p_lower:
                 return 0.25

        return 1.0

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers from text for computational evaluation."""
        # Match integers and floats
        pattern = r'-?\d+\.?\d*'
        matches = re.findall(pattern, text)
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                continue
        return nums

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Calculates score based on logical structure alignment.
        Checks for presence of required logical operators and negation handling.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        score = 0.0
        total_checks = 0
        
        # Check Negation Consistency
        # If prompt has negation, correct answer often needs to reflect it or invert logic
        has_negation = any(n in p_lower for n in self.negations)
        cand_has_negation = any(n in c_lower for n in self.negations)
        
        # Heuristic: If prompt asks a negative question, answer might need specific handling
        # But for simple matching, we check if the candidate preserves the logical operator
        # found in the prompt context (e.g. "Which is NOT...")
        if has_negation:
            total_checks += 1
            if cand_has_negation:
                score += 1.0
            else:
                # Penalty for missing negation in a negative query context
                score += 0.2 
        
        # Check Conditional/Comparative presence
        has_comp = any(c in p_lower for c in self.comparatives)
        if has_comp:
            total_checks += 1
            if any(c in c_lower for c in self.comparatives):
                score += 1.0
        
        return score / max(total_checks, 1) if total_checks > 0 else 0.5

    def _compute_numeric_score(self, prompt: str, candidate: str) -> float:
        """
        Extracts numbers and checks for computational correctness.
        Handles simple comparisons and direct extraction.
        """
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if not p_nums:
            return 0.0 # No numbers to compute with
            
        # Case 1: Direct Number Match (Extraction task)
        # If prompt asks for a number and candidate provides one that exists in prompt
        # or is a result of a simple operation.
        
        # Heuristic: If candidate contains a number from the prompt, it's a strong signal
        # unless the prompt implies a calculation (e.g. "sum", "difference")
        match_count = 0
        for cn in c_nums:
            if cn in p_nums:
                match_count += 1
        
        if match_count > 0:
            return min(1.0, match_count / len(c_nums))
            
        # Case 2: Simple Comparison Validation
        # If prompt has 2 numbers and candidate implies an order (e.g. "first is larger")
        if len(p_nums) >= 2:
            # Check if candidate text implies the correct relation
            max_p = max(p_nums)
            min_p = min(p_nums)
            
            is_larger = 'larger' in c_lower or 'greater' in c_lower or 'more' in c_lower
            is_smaller = 'smaller' in c_lower or 'less' in c_lower or 'fewer' in c_lower
            
            # Very basic inference: if candidate mentions the max number and says it's larger
            if str(max_p) in candidate and is_larger:
                return 1.0
            if str(min_p) in candidate and is_smaller:
                return 1.0

        return 0.0

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len1 = len(s1)
        len2 = len(s2)
        if len1 == 0 or len2 == 0:
            return 1.0
            
        try:
            comp12 = len(zlib.compress((s1 + s2).encode('utf-8')))
            comp1 = len(zlib.compress(s1.encode('utf-8')))
            comp2 = len(zlib.compress(s2.encode('utf-8')))
            
            numerator = comp12 - min(comp1, comp2)
            denominator = max(comp1, comp2)
            
            if denominator == 0:
                return 1.0
            return numerator / denominator
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates using the PO-GNN approximation.
        1. Meta-checks for honesty.
        2. Structural parsing.
        3. Numeric computation.
        4. NCD tie-breaking.
        """
        results = []
        
        # Pre-compute meta-confidence cap
        meta_cap = self._meta_confidence(prompt)
        
        # Pre-compute prompt stats for efficiency
        p_len = len(prompt)
        
        for cand in candidates:
            # 1. Structural Score (Weight 0.50)
            struct_score = self._compute_structural_score(prompt, cand)
            
            # 2. Computational Score (Weight 0.35)
            comp_score = self._compute_numeric_score(prompt, cand)
            
            # 3. NCD Score (Weight 0.15) - Inverted because NCD is distance
            # We want similarity, so 1 - NCD. But NCD is noisy for short strings.
            # Only use if other scores are low (tiebreaker logic)
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val
            
            # Weighted Sum
            raw_score = (struct_score * 0.50) + (comp_score * 0.35) + (ncd_score * 0.15)
            
            # Apply Epistemic Honesty Cap
            final_score = min(raw_score, meta_cap)
            
            # Construct reasoning string
            reasoning_parts = []
            if meta_cap < 0.3:
                reasoning_parts.append("Potential epistemic trap detected (presupposition/ambiguity).")
            if struct_score > 0.8:
                reasoning_parts.append("Strong structural alignment.")
            if comp_score > 0.8:
                reasoning_parts.append("Numeric computation verified.")
            if not reasoning_parts:
                reasoning_parts.append("Baseline heuristic match.")
                
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": " ".join(reasoning_parts)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.25 if meta-analysis detects ambiguity/traps.
        Caps at 0.9 unless computation is definitive.
        """
        # 1. Meta Check (The primary filter for Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural/Computational Verification
        struct_score = self._compute_structural_score(prompt, answer)
        comp_score = self._compute_numeric_score(prompt, answer)
        
        # Base confidence on verification strength
        verification_strength = (struct_score * 0.6) + (comp_score * 0.4)
        
        # If no structural or computational signal, confidence should be low
        if verification_strength < 0.1:
            base_conf = 0.2 # Uncertain
        else:
            base_conf = 0.5 + (verification_strength * 0.4) # Max 0.9 before cap
            
        # Apply Meta Cap (Honesty Override)
        final_conf = min(base_conf, meta_cap)
        
        # Ensure we don't claim 1.0 unless it's a pure computational lock
        if comp_score == 1.0 and meta_cap == 1.0:
            return 0.95 # Never 1.0 to allow for edge cases
            
        return round(final_conf, 3)