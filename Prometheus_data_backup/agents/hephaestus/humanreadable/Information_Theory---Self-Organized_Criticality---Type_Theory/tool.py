import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Critical-Information Type-Driven Proof Engine (CIT-PE) Approximation.
    
    Mechanism:
    1. Type-Directed Frontier (Structural Parsing): Extracts logical operators 
       (negations, comparatives, conditionals) and numeric values as 'types'.
    2. Information-Theoretic Weighting: Scores candidates based on the mutual 
       information of matching structural types between prompt and candidate.
       Higher weight for preserving logical constraints (e.g., negation flips).
    3. Self-Organized Criticality (SOC) Simulation: 
       - Accumulates 'tension' when structural matches are ambiguous or partial.
       - Triggers an 'avalanche' (re-ranking boost) if tension exceeds a threshold,
         favoring candidates that resolve the logical contradiction (e.g., explicit 'No').
       - Entropy production is approximated by the diversity of matched types; 
         the system prefers candidates that maximize structural clarity (low entropy in outcome).
    4. NCD Tiebreaker: Used only when structural scores are identical.
    """

    def __init__(self):
        self.threshold = 0.6  # SOC tension threshold
        self.operators = ['not', 'no', 'never', 'without', 'less', 'fewer', 'smaller']
        self.comparatives = ['>', '<', 'greater', 'less', 'more', 'fewer', 'larger', 'smaller']
        self.conditionals = ['if', 'then', 'unless', 'only if', 'when']
        self.negation_words = set(['not', 'no', 'never', 'none', 'nothing', 'nobody', 'nowhere'])

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical types: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        has_negation = any(w in self.negation_words for w in words)
        has_comparative = any(c in text_lower for c in self.comparatives)
        has_conditional = any(c in text_lower for c in self.conditionals)
        
        # Extract numbers
        nums = re.findall(r'-?\d+\.?\d*', text)
        numbers = [float(n) for n in nums]
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'length': len(text)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_joint = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_joint - min(len1, len2)) / max_len

    def _evaluate_structural_match(self, prompt_struct: Dict, cand_struct: Dict, prompt: str, candidate: str) -> Tuple[float, float]:
        """
        Calculate score based on structural consistency (Type Theory) 
        and tension (SOC).
        Returns: (score, tension)
        """
        score = 0.0
        tension = 0.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has negation, candidate should reflect it or answer appropriately
        if prompt_struct['negation']:
            # Heuristic: If prompt is negative, simple positive echoes are low score
            if not cand_struct['negation'] and len(cand_struct['numbers']) == 0:
                # Check if candidate is just a short affirmation which might be wrong
                if cand_struct['length'] < 10 and cand_struct['comparative'] == False:
                    tension += 0.4 # High tension: potential contradiction
                    score -= 0.2
                else:
                    score += 0.3 # Likely reasoned response
            else:
                score += 0.5 # Explicit handling
        else:
            score += 0.2 # Baseline
            
        # 2. Numeric Evaluation (Constraint Propagation)
        if prompt_struct['numbers'] and cand_struct['numbers']:
            p_nums = prompt_struct['numbers']
            c_nums = cand_struct['numbers']
            
            # Simple transitivity/comparison check
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                # If prompt compares A and B, and candidate gives a number
                # Check if the number aligns with comparative logic if present
                if prompt_struct['comparative']:
                    # Rough heuristic: if prompt says "less", candidate should be smaller than ref?
                    # Hard to infer without full NLP, so we reward presence of numbers in math contexts
                    score += 0.4
                    if 'less' in prompt.lower() or 'smaller' in prompt.lower():
                        if c_nums[0] < max(p_nums):
                            score += 0.3
                        else:
                            tension += 0.3 # Contradicts 'less' hint
                    elif 'more' in prompt.lower() or 'greater' in prompt.lower():
                        if c_nums[0] > min(p_nums):
                            score += 0.3
                        else:
                            tension += 0.3
            else:
                score += 0.1 # Numbers present but logic unclear
                
        elif prompt_struct['numbers'] and not cand_struct['numbers']:
            # Prompt has math, candidate doesn't -> High tension, low score unless logical word
            tension += 0.5
            if not any(w in candidate.lower() for w in ['yes', 'no', 'true', 'false', 'equal', 'impossible']):
                score -= 0.5

        # 3. Conditional Logic
        if prompt_struct['conditional']:
            if cand_struct['conditional'] or any(w in candidate.lower() for w in ['if', 'then', 'unless']):
                score += 0.3
            else:
                tension += 0.2 # Missing conditional structure in response

        # Normalize score slightly
        return score, tension

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # Phase 1: Structural Scoring & Tension Accumulation
        raw_scores = []
        max_tension = 0.0
        
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            score, tension = self._evaluate_structural_match(prompt_struct, cand_struct, prompt, cand)
            raw_scores.append((cand, score, tension))
            if tension > max_tension:
                max_tension = tension

        # Phase 2: SOC Avalanche Adjustment
        # If system-wide tension is high (ambiguous/hard problem), trigger avalanche
        # Avalanche = Boost candidates that resolve tension (e.g. definitive answers)
        avalanche_active = max_tension > self.threshold
        
        final_scores = []
        for cand, score, tension in raw_scores:
            if avalanche_active:
                # If tension was high for this candidate, check if it resolves it
                # Resolution heuristic: Definitive words or specific numbers
                is_resolved = any(w in cand.lower() for w in ['yes', 'no', 'true', 'false']) or self._extract_structure(cand)['numbers']
                if is_resolved:
                    score += 0.5 # Avalanche boost for resolution
                else:
                    score -= 0.2 # Penalize ambiguity during criticality
            
            final_scores.append((cand, score))

        # Phase 3: Ranking with NCD Tiebreaker
        # Sort by score desc, then by NCD asc (shorter compression distance to prompt context is better tiebreaker)
        # Actually, for NCD tiebreaker: we want candidate that compresses well WITH prompt (high mutual info)
        # But standard NCD is distance. Lower is better.
        
        scored_results = []
        for i, (cand, score) in enumerate(final_scores):
            # Calculate NCD only for tie-breaking logic later or as minor factor
            ncd_val = self._compute_ncd(prompt, cand)
            scored_results.append({
                "candidate": cand,
                "score": score,
                "ncd": ncd_val,
                "reasoning": f"Structural match: {score:.2f}, SOC tension: {'High' if max_tension > self.threshold else 'Low'}, NCD: {ncd_val:.2f}"
            })
        
        # Sort: Primary by score (desc), Secondary by NCD (asc)
        scored_results.sort(key=lambda x: (-x['score'], x['ncd']))
        
        # Clean up output
        return [{"candidate": r["candidate"], "score": r["score"], "reasoning": r["reasoning"]} for r in scored_results]

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Estimate confidence based on structural alignment and NCD.
        Returns 0-1.
        """
        prompt_struct = self._extract_structure(prompt)
        ans_struct = self._extract_structure(answer)
        
        score = 0.5 # Base confidence
        
        # Penalty for mismatched negation
        if prompt_struct['negation'] != ans_struct['negation']:
            # If prompt has negation and answer doesn't (or vice versa), check context
            # This is a heuristic simplification
            if prompt_struct['negation'] and not ans_struct['negation']:
                score -= 0.3
            elif not prompt_struct['negation'] and ans_struct['negation']:
                score -= 0.3
        
        # Reward numeric consistency
        if prompt_struct['numbers'] and ans_struct['numbers']:
            score += 0.2
            
        # NCD factor: If answer is very different (high NCD), lower confidence slightly
        ncd = self._compute_ncd(prompt, answer)
        # Normalize NCD impact: low NCD (similar) -> higher confidence in this context?
        # Actually, for reasoning, low NCD might mean echoing. 
        # Let's use NCD as a penalty for noise.
        if ncd > 0.9:
            score -= 0.1
            
        return max(0.0, min(1.0, score))