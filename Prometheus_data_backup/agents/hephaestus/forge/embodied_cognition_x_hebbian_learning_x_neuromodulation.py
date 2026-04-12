import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Neuromodulated Embodied Hebbian Predictive Coding (NEHPC) Approximation.
    
    Mechanism:
    1. Embodied Cognition (Structural Grounding): Parses the prompt for logical 
       structures (negations, comparatives, conditionals) to form a 'sensory' 
       representation of constraints.
    2. Hebbian Learning (Association): Strengthens candidates that share 
       structural tokens (keywords, logic operators) with the prompt. 
       "Neurons firing together" = shared logical tokens.
    3. Neuromodulation (Gating & Confidence):
       - Dopamine (Reward): Boosts score if candidate matches prompt structure.
       - Serotonin (Exploration): If confidence is low (high uncertainty), 
         penalize extreme scores slightly to allow alternative ranking.
       - Acetylcholine (Precision): Weighs specific logical operators higher 
         than generic words.
    
    This creates a self-evaluating loop where the "body" (parser) validates 
    the hypothesis (candidate) against sensory input (prompt structure).
    """

    def __init__(self):
        # Logical operators act as high-precision sensory inputs (Acetylcholine)
        self.logic_ops = {'not', 'no', 'never', 'if', 'then', 'else', 'unless', 
                          'greater', 'less', 'more', 'fewer', 'equal', 'true', 'false'}
        self.comparators = {'>', '<', '>=', '<=', '==', '!='}
        
    def _extract_structure(self, text: str) -> Tuple[set, float, bool]:
        """Extract logical tokens, numeric values, and negation state."""
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        # Identify logical operators (High precision weights)
        logic_tokens = words.intersection(self.logic_ops)
        
        # Detect negation scope (Simple heuristic: presence of negation words)
        has_negation = bool(words.intersection({'no', 'not', 'never', 'neither', 'nobody'}))
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r"-?\d+\.?\d*", lower_text)
        numeric_val = None
        if numbers:
            try:
                # Take the last number as the primary value for comparison contexts
                numeric_val = float(numbers[-1])
            except ValueError:
                pass
                
        return logic_tokens, numeric_val, has_negation

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        comp1 = len(zlib.compress(b1))
        comp2 = len(zlib.compress(b2))
        comp12 = len(zlib.compress(b1 + b2))
        
        # NCD formula
        ncd = (comp12 - min(comp1, comp2)) / max(comp1, comp2)
        return max(0.0, min(1.0, ncd))

    def _hebbian_update(self, prompt_tokens: set, cand_tokens: set, 
                        prompt_logic: set, has_negation: bool) -> float:
        """
        Simulates Hebbian learning: Strengthens connections between 
        co-occurring logical structures.
        """
        if not prompt_tokens:
            return 0.0
            
        # Base overlap (standard association)
        intersection = prompt_tokens.intersection(cand_tokens)
        base_score = len(intersection) / (len(prompt_tokens) + 1e-6)
        
        # Logic-gated reinforcement (Acetylcholine modulation)
        # If the prompt has logic ops, candidates sharing them get a massive boost
        logic_overlap = 0.0
        if prompt_logic:
            cand_logic = cand_tokens.intersection(self.logic_ops)
            if cand_logic:
                # Stronger weight for logical consistency
                logic_overlap = len(cand_logic) * 0.5
        
        # Negation consistency check
        # If prompt is negative, candidate should ideally reflect that or be evaluated carefully
        negation_bonus = 0.0
        if has_negation:
            cand_has_neg = bool(cand_tokens.intersection({'no', 'not', 'never', 'false'}))
            # In simple reasoning, if prompt negates, correct answer often acknowledges it
            if cand_has_neg:
                negation_bonus = 0.2
        
        return base_score + logic_overlap + negation_bonus

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_tokens = set(re.findall(r'\b\w+\b', prompt.lower()))
        p_logic, p_num, p_neg = self._extract_structure(prompt)
        
        scored_candidates = []
        
        for cand in candidates:
            cand_tokens = set(re.findall(r'\b\w+\b', cand.lower()))
            c_logic, c_num, c_neg = self._extract_structure(cand)
            
            # 1. Hebbian Strength (Structural similarity)
            hebbian_score = self._hebbian_update(prompt_tokens, cand_tokens, p_logic, p_neg)
            
            # 2. Numeric Evaluation (Constraint Propagation)
            numeric_bonus = 0.0
            if p_num is not None and c_num is not None:
                # Check for comparative consistency if prompt implies it
                # Simple heuristic: if numbers are close, higher score (approximation)
                if abs(p_num - c_num) < 1e-6:
                    numeric_bonus = 0.3
                elif p_num > c_num and ('less' in prompt.lower() or 'smaller' in prompt.lower()):
                    numeric_bonus = 0.2
                elif p_num < c_num and ('greater' in prompt.lower() or 'larger' in prompt.lower()):
                    numeric_bonus = 0.2
            
            # 3. Neuromodulatory Gating (Dopamine/Serotonin)
            # Dopamine: Reward for structural match
            raw_score = hebbian_score + numeric_bonus
            
            # Serotonin: Exploration bonus for short, distinct answers if confidence is low
            # This prevents getting stuck on long, verbose, but incorrect matches
            exploration_bonus = 0.0
            if raw_score < 0.1 and len(cand_tokens) < 5:
                exploration_bonus = 0.05 # Slight boost to explore short hypotheses
            
            final_score = min(1.0, raw_score + exploration_bonus)
            
            # Reasoning string generation
            reasoning = f"Structural match: {hebbian_score:.2f}"
            if numeric_bonus > 0:
                reasoning += f"; Numeric alignment detected"
            if p_logic and not c_logic:
                reasoning += "; Warning: Missing logical operators"
                
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Fallback to NCD if all structural scores are zero (Tiebreaker)
        if all(c["score"] == 0.0 for c in scored_candidates):
            for i, item in enumerate(scored_candidates):
                ncd = self._compute_ncd(prompt, item["candidate"])
                # Invert NCD so lower distance = higher score
                item["score"] = 1.0 - ncd
                item["reasoning"] = "Fallback to NCD (structural signal weak)"
            scored_candidates.sort(key=lambda x: x["score"], reverse=True)
            
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the evaluation score of the single answer.
        Uses the same NEHPC mechanism to self-evaluate the hypothesis.
        """
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        
        score = results[0]["score"]
        
        # Metacognitive thresholding
        # If the structural match is strong, confidence is high.
        # If it relied on NCD fallback, confidence is capped.
        if "NCD" in results[0]["reasoning"]:
            return max(0.0, min(0.4, score)) # Low confidence if structural parsing failed
        
        return max(0.0, min(1.0, score))