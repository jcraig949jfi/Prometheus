import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Self-Monitoring Belief-Measure Dynamics (SBMD) Engine.
    
    Mechanism:
    Instead of heavy Bayesian inference, we simulate the 'phase transition' detection
    by analyzing the structural stability of candidates against the prompt's logical constraints.
    
    1. Measure Theory Analog: We treat the set of extracted logical constraints as a 
       discrete measure space. A candidate's 'belief measure' is the fraction of 
       constraints it satisfies.
    2. Phase Transition Analog: We look for abrupt drops in satisfaction (Wasserstein-like 
       distance) when a candidate violates a critical negation or comparative.
    3. Phenomenology Analog: An 'intentionality layer' that checks if the candidate 
       aligns with the prompt's inferred goal (e.g., finding the smallest/largest number,
       or adhering to a negation).
       
    This avoids the 'Measure Theory' and 'Phenomenology' traps by using them as 
    structural parsing metaphors rather than direct scoring metrics, focusing on 
    logical consistency (negations, comparatives) as the primary signal.
    """

    def __init__(self):
        # Keywords indicating logical structures
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['larger', 'smaller', 'greater', 'less', 'more', 'fewer', 'better', 'worse']
        self.conditionals = ['if', 'then', 'unless', 'otherwise']
        self.numeric_pattern = re.compile(r'-?\d+\.?\d*')

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract all floating point numbers from text."""
        return [float(x) for x in self.numeric_pattern.findall(text)]

    def _parse_structure(self, prompt: str) -> dict:
        """
        Extract logical structure: negations, comparatives, conditionals, and numbers.
        This forms the 'measure space' for evaluation.
        """
        p_lower = prompt.lower()
        has_negation = any(n in p_lower for n in self.negations)
        has_comparative = any(c in p_lower for c in self.comparatives)
        has_conditional = any(c in p_lower for c in self.conditionals)
        numbers = self._extract_numbers(prompt)
        
        # Determine intent direction based on comparatives
        intent_dir = 0 # 0: none, 1: max, -1: min
        if 'largest' in p_lower or 'greatest' in p_lower or 'max' in p_lower:
            intent_dir = 1
        elif 'smallest' in p_lower or 'least' in p_lower or 'min' in p_lower:
            intent_dir = -1
        elif 'larger' in p_lower or 'greater' in p_lower:
            intent_dir = 1
        elif 'smaller' in p_lower or 'less' in p_lower:
            intent_dir = -1

        return {
            'has_negation': has_negation,
            'has_comparative': has_comparative,
            'has_conditional': has_conditional,
            'numbers': numbers,
            'intent_dir': intent_dir,
            'prompt_len': len(prompt)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denominator

    def _evaluate_candidate_logic(self, prompt: str, candidate: str, structure: dict) -> float:
        """
        Evaluate candidate against the logical structure of the prompt.
        Returns a score based on logical consistency (0.0 to 1.0).
        """
        score = 1.0
        c_lower = candidate.lower()
        c_nums = self._extract_numbers(candidate)
        
        # 1. Negation Check (Critical Failure Mode)
        # If prompt has negation, candidate should not blindly affirm without nuance
        if structure['has_negation']:
            # Simple heuristic: if prompt says "not X" and candidate is exactly "X", penalize
            # This is a proxy for measure-theoretic support dropping to zero
            prompt_words = set(re.findall(r'\w+', prompt.lower()))
            candidate_words = set(re.findall(r'\w+', c_lower))
            
            # Check for direct contradiction of negated concepts if possible
            # Simplified: If prompt has 'not' and candidate is a simple 'yes' or repeats a number blindly
            if 'yes' in c_lower and 'no' in prompt_words:
                score -= 0.5
            if 'no' in c_lower and 'yes' in prompt_words: # Weak heuristic
                pass 

        # 2. Comparative/Numeric Consistency (Phase Transition Check)
        # If the prompt asks for the smallest/largest, check if the candidate matches that number
        if structure['intent_dir'] != 0 and structure['numbers'] and c_nums:
            target = None
            if structure['intent_dir'] == 1: # Max
                target = max(structure['numbers'])
            elif structure['intent_dir'] == -1: # Min
                target = min(structure['numbers'])
            
            if target is not None:
                # Check if candidate contains the target number
                found_target = any(abs(n - target) < 1e-6 for n in c_nums)
                if not found_target:
                    # Major penalty for missing the explicit numeric goal
                    score -= 0.6
                else:
                    # Bonus for hitting the target
                    score += 0.2

        # 3. Structural Overlap (Phenomenological Alignment)
        # Does the candidate share key structural tokens without being identical?
        # This simulates the 'intentionality layer' aligning with the 'lifeworld' of the prompt
        prompt_tokens = set(re.findall(r'\w+', prompt.lower()))
        candidate_tokens = set(re.findall(r'\w+', c_lower))
        
        # Remove stopwords for better overlap
        stopwords = {'the', 'is', 'a', 'an', 'of', 'to', 'in', 'it', 'for', 'on', 'that', 'this'}
        p_sig = prompt_tokens - stopwords
        c_sig = candidate_tokens - stopwords
        
        if p_sig:
            overlap = len(p_sig & c_sig) / len(p_sig)
            # Adjust score slightly based on semantic alignment, but don't override logic
            score += (overlap - 0.5) * 0.2 

        return max(0.0, min(1.0, score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Rank candidates based on logical consistency (SBMD logic) and use NCD as tiebreaker.
        """
        structure = self._parse_structure(prompt)
        scored_candidates = []

        for cand in candidates:
            # Primary Score: Logical/Structural Consistency
            logic_score = self._evaluate_candidate_logic(prompt, cand, structure)
            
            # Tiebreaker: NCD (Lower is better, so we invert it for addition if needed, 
            # but here we use it to break ties in logic_score)
            # We store raw logic score and use NCD for sorting stability
            ncd_val = self._compute_ncd(prompt, cand)
            
            scored_candidates.append({
                'candidate': cand,
                'logic_score': logic_score,
                'ncd': ncd_val,
                'reasoning': f"Logic: {logic_score:.2f}, NCD: {ncd_val:.2f}"
            })

        # Sort: Higher logic_score first. If tie, lower NCD (more similar/compressed) is often safer 
        # but per instructions NCD is tiebreaker. 
        # Actually, for reasoning, if logic scores are equal, we might prefer the one that 
        # is structurally distinct? No, usually NCD implies relevance in these baselines.
        # Let's sort by logic_score desc, then ncd asc.
        scored_candidates.sort(key=lambda x: (-x['logic_score'], x['ncd']))

        # Normalize scores to 0-1 range roughly based on rank and logic
        final_results = []
        max_logic = max(c['logic_score'] for c in scored_candidates) if scored_candidates else 0
        
        for i, item in enumerate(scored_candidates):
            # Final score combines logic dominance with a small NCD factor
            # Ensure the top logic item gets the highest score
            base_score = item['logic_score']
            # Add small epsilon based on rank to ensure strict ordering if logic is identical
            rank_bonus = (len(candidates) - i) * 0.001 
            final_score = base_score + rank_bonus
            
            final_results.append({
                'candidate': item['candidate'],
                'score': final_score,
                'reasoning': item['reasoning']
            })

        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Uses the same logical evaluation as evaluate().
        """
        structure = self._parse_structure(prompt)
        logic_score = self._evaluate_candidate_logic(prompt, answer, structure)
        
        # Calibrate: Logic score is the main driver. 
        # If logic is high, confidence is high.
        # Add a small check for length sanity (avoid empty answers)
        if not answer.strip():
            return 0.0
            
        return min(1.0, max(0.0, logic_score))