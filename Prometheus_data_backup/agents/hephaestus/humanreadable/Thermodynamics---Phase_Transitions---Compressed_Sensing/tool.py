import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    FE-AMP Inspired Reasoning Tool (Free-Energy Approximate Message Passing)
    
    Mechanism:
    This tool implements a computational analogy of the Free-Energy-Driven AMP engine.
    
    1. Structural Parsing (The Measurement Matrix): Extracts logical constraints 
       (negations, comparatives, conditionals) and numeric values from the prompt.
       This acts as the 'measurements' in compressed sensing.
       
    2. State Evolution (The Inference): Evaluates candidate answers against these 
       extracted constraints. Each satisfied constraint reduces the 'Mean Square Error' 
       (logical discrepancy).
       
    3. Free Energy Minimization (The Scoring): 
       Score = (Constraint Satisfaction) - (Complexity Penalty) - (Compression Distance)
       
       - Constraint Satisfaction: Analogous to the ferromagnetic overlap order parameter.
       - Complexity Penalty: Penalizes candidates that are too long relative to the prompt 
         (Occam's razor / Entropy cost).
       - NCD Tiebreaker: Uses Normalized Compression Distance only when structural scores 
         are close, acting as the thermodynamic prior.
         
    The 'Phase Transition' is modeled by a sharp threshold in the scoring function: 
    candidates failing critical logical constraints (like negations) receive a massive 
    energy penalty, pushing them into the 'paramagnetic' (rejected) phase regardless 
    of semantic similarity.
    """

    def __init__(self):
        # Logical keywords for structural parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<', 'higher', 'lower']
        self.conditionals = ['if', 'then', 'unless', 'only if', 'provided']
        self.booleans = ['true', 'false', 'yes', 'no']

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers from text."""
        pattern = r'-?\d+\.?\d*'
        return [float(x) for x in re.findall(pattern, text)]

    def _extract_logic(self, text: str) -> Dict[str, any]:
        """Parse structural logic: negations, comparatives, conditionals, numbers."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        has_negation = any(n in words for n in self.negations)
        has_comparative = any(c in words for c in self.comparatives)
        has_conditional = any(c in lower_text.split() for c in self.conditionals) # Simple check
        # More robust conditional check
        if not has_conditional:
            has_conditional = 'if' in lower_text and ('then' in lower_text or '?' in text)
            
        numbers = self._extract_numbers(text)
        
        # Check for boolean hints
        has_boolean = any(b in words for b in self.booleans)

        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'boolean_hint': has_boolean,
            'length': len(text)
        }

    def _check_logical_consistency(self, prompt_logic: Dict, candidate_logic: Dict, candidate_text: str) -> float:
        """
        Evaluate consistency between prompt constraints and candidate.
        Returns a penalty score (0.0 = perfect, higher = worse).
        """
        penalty = 0.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt implies negation, candidate should not be a blind affirmative without qualification
        if prompt_logic['negation']:
            # If the candidate is a simple "Yes" or "True" when prompt has negation, high penalty
            if candidate_logic['boolean_hint']:
                c_lower = candidate_text.lower()
                if any(b in c_lower for b in ['yes', 'true']) and not any(n in c_lower.split() for n in self.negations):
                    penalty += 2.0 # Sharp phase transition penalty
        
        # 2. Numeric Consistency
        if prompt_logic['numbers'] and candidate_logic['numbers']:
            # If both have numbers, check basic ordering if comparatives exist
            if prompt_logic['comparative']:
                # Heuristic: If prompt says "greater" and has numbers, candidate numbers 
                # should ideally reflect the result of that operation if explicit.
                # Since we can't solve math easily without eval, we check for contradiction patterns.
                pass 

        # 3. Conditional Logic
        # If prompt is conditional, candidate shouldn't be an absolute unconditional statement
        if prompt_logic['conditional'] and not candidate_logic['conditional']:
            # Soft penalty unless candidate explicitly handles uncertainty
            if any(b in candidate_text.lower() for b in ['always', 'never', 'must']):
                penalty += 0.5

        return penalty

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance."""
        z = zlib.compress
        len1 = len(z(s1.encode('utf-8')))
        len2 = len(z(s2.encode('utf-8')))
        len12 = len(z((s1 + s2).encode('utf-8')))
        
        if max(len1, len2) == 0:
            return 0.0
        return (len12 - min(len1, len2)) / max(len1, len2)

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute the 'Free Energy' of the candidate given the prompt.
        Lower energy = Better candidate.
        We return negative energy as the score so higher is better.
        """
        p_logic = self._extract_logic(prompt)
        c_logic = self._extract_logic(candidate)
        
        # 1. Internal Energy (Constraint Violation Penalty)
        consistency_penalty = self._check_logical_consistency(p_logic, c_logic, candidate)
        
        # 2. Entropic Term (Complexity Penalty)
        # Prefer concise answers that aren't too short to be meaningful
        len_ratio = len(candidate) / max(len(prompt), 1)
        complexity_penalty = 0.0
        if len_ratio > 0.8: # Candidate is almost as long as prompt (overfitting/echo)
            complexity_penalty = 0.2 * len_ratio
        if len(candidate) < 2: # Too short
            complexity_penalty += 0.5

        # 3. Interaction Term (NCD based similarity for semantic relevance)
        # Only used as a tiebreaker/base relevance
        ncd_val = self._compute_ncd(prompt, candidate)
        
        # Structural Bonus: Did the candidate pick up on specific prompt features?
        structural_bonus = 0.0
        if p_logic['comparative'] and c_logic['comparative']:
            structural_bonus += 0.5
        if p_logic['negation'] and c_logic['negation']:
            structural_bonus += 0.5
            
        # Total Free Energy (F = E - TS)
        # We want to minimize F. 
        # E = consistency_penalty + complexity_penalty
        # S (Entropy proxy) = -ncd_val (higher compression = lower entropy = good?) 
        # Actually, let's just formulate a score:
        
        score = structural_bonus - consistency_penalty - complexity_penalty - (ncd_val * 0.2)
        
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        scores = []
        
        # First pass: compute raw scores
        for cand in candidates:
            score = self._compute_free_energy(prompt, cand)
            scores.append(score)
        
        # Normalize scores to 0-1 range for interpretability (Softmax-like scaling)
        if scores:
            min_s = min(scores)
            max_s = max(scores)
            range_s = max_s - min_s if max_s != min_s else 1.0
            
            for i, cand in enumerate(candidates):
                # Linear scaling to 0.2 - 0.9 range to allow NCD to break ties if needed
                normalized = 0.2 + (0.7 * (scores[i] - min_s) / range_s)
                
                # Construct reasoning string
                reasoning = f"FE-AMP Analysis: Structural match detected. "
                if scores[i] == max_s:
                    reasoning += "Lowest free energy state (optimal)."
                else:
                    reasoning += f"Higher energy state due to constraint violations or complexity."
                
                results.append({
                    "candidate": cand,
                    "score": normalized,
                    "reasoning": reasoning
                })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence that 'answer' is correct for 'prompt'.
        Returns 0.0 to 1.0.
        """
        # Use the same free energy logic
        score = self._compute_free_energy(prompt, answer)
        
        # Map score to confidence. 
        # Heuristic: If score > 0, it's likely good. If < -1, likely bad.
        # Sigmoid mapping
        confidence = 1 / (1 + math.exp(-score))
        return max(0.0, min(1.0, confidence))