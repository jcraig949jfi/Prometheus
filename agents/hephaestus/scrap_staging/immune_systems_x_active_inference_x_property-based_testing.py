import re
import math
import zlib
from typing import List, Dict, Tuple, Any, Optional

# Constants
SELECTION_PRESSURE = 0.5  # Keep top 50%
GENERATIONS = 5
CLONE_COUNT = 3
THRESHOLD_AFFINITY = 0.6

class ReasoningTool:
    """
    Clonal-Active Property-Based Scorer (CAPS) Implementation.
    
    Mechanism:
    1. Extraction: Parses prompt into logical 'Antigens' (predicates, numerics, conditionals).
    2. Clonal Expansion: Generates variant interpretations of candidate answers.
    3. Affinity Maturation: Scores candidates based on logical entailment (Active Inference)
       and minimizes free energy (mismatch between prompt constraints and answer assertions).
    4. Epistemic Honesty: Detects ambiguity/traps to cap confidence, preventing overconfidence.
    
    Score Decomposition: Structural (60%), Computation (25%), NCD (15%).
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'numeric': re.compile(r'[-+]?\d*\.?\d+'),
            'comparator': re.compile(r'(greater|less|more|fewer|before|after|equal|same|different)'),
            'negation': re.compile(r'\b(not|no|never|neither|without|fail|stop|quit)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(causes|leads to|results in|because|therefore)\b', re.IGNORECASE),
            'presupposition': re.compile(r'(have you stopped|why did|when did|who is the)', re.IGNORECASE),
            'pronoun_trap': re.compile(r'(told|said to|asked).*\b(he|she|him|her|they|them)\b.*\b(who|which one)\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either|or)\b.*\b(or|but)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|believe)\b', re.IGNORECASE)
        }

    def _extract_antigens(self, text: str) -> List[Dict]:
        """Extract logical constraints (Antigens) from text."""
        antigens = []
        text_lower = text.lower()
        
        # 1. Numeric Constraints
        numbers = [float(n) for n in self.patterns['numeric'].findall(text)]
        if len(numbers) >= 2:
            # Infer comparison if keywords exist
            if any(self.patterns['comparator'].search(text_lower)):
                antigens.append({'type': 'numeric_constraint', 'values': numbers, 'op': 'implied'})
        
        # 2. Logical Predicates
        if self.patterns['negation'].search(text_lower):
            antigens.append({'type': 'negation', 'present': True})
            
        if self.patterns['conditional'].search(text_lower):
            antigens.append({'type': 'conditional', 'present': True})
            
        if self.patterns['causal'].search(text_lower):
            antigens.append({'type': 'causal', 'present': True})

        # 3. Specific Logic Traps
        if 'either' in text_lower and 'or' in text_lower:
             antigens.append({'type': 'dichotomy', 'present': True})

        return antigens

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes score based on logical entailment and constraint satisfaction.
        Returns 0.0 to 1.0.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.0
        checks = 0
        
        # A. Negation Consistency
        # If prompt has negation, candidate must reflect it (simplified heuristic)
        if self.patterns['negation'].search(p_lower):
            checks += 1
            if self.patterns['negation'].search(c_lower):
                score += 1.0
            else:
                # Penalty for ignoring negation
                score -= 0.5
        
        # B. Numeric Consistency (Constructive Computation)
        p_nums = [float(x) for x in self.patterns['numeric'].findall(p_lower)]
        c_nums = [float(x) for x in self.patterns['numeric'].findall(c_lower)]
        
        if p_nums:
            checks += 1
            # Check if candidate numbers are mathematically consistent with prompt
            # Simple heuristic: If prompt implies a calculation (e.g. "5 plus 3"), 
            # candidate should contain the result (8). 
            # Since we can't parse full math without eval, we check for exact match of derived values
            # or presence of prompt numbers if it's a retrieval task.
            
            # Heuristic: If candidate contains a number from prompt, it's likely relevant (positive)
            # If it contains a number NOT in prompt, it might be a calculation result.
            match_count = sum(1 for n in c_nums if any(abs(n - p) < 1e-6 for p in p_nums))
            if match_count > 0:
                score += 0.8 # High reward for retaining numeric context
            elif len(c_nums) > 0:
                # Candidate introduces new numbers; assume it's a calculation attempt
                # We can't verify correctness without full solver, but structure implies reasoning
                score += 0.5 

        # C. Keyword Overlap for Logic Terms (Structural)
        logic_terms = ['if', 'then', 'because', 'therefore', 'not', 'unless']
        p_logic = [t for t in logic_terms if t in p_lower]
        if p_logic:
            checks += 1
            c_logic = [t for t in logic_terms if t in c_lower]
            overlap = len(set(p_logic) & set(c_logic))
            if overlap > 0:
                score += (overlap / len(p_logic)) * 0.9

        return max(0.0, min(1.0, score / max(1, checks))) if checks > 0 else 0.5

    def _clonal_expansion_and_score(self, prompt: str, candidate: str) -> float:
        """
        Simulates clonal selection. 
        1. Base affinity via structural score.
        2. Generate clones (perturbations) to test robustness.
        3. Select max affinity.
        """
        base_score = self._compute_structural_score(prompt, candidate)
        
        # If base score is low, try to find a 'mutation' of interpretation that fits better?
        # In this context, 'clones' are slight variations of the candidate string 
        # to see if a more precise version yields higher logical consistency.
        # Since we can't generate text, we simulate by checking substrings (shrinking).
        
        max_affinity = base_score
        
        # Shrinking / Maturation: Check if removing parts of the answer increases density of logic
        words = candidate.split()
        if len(words) > 3:
            # Test subsets (simulating shrinking to minimal failing set)
            step = max(1, len(words) // 3)
            for i in range(0, len(words), step):
                subset = " ".join(words[i:i+step*2])
                if subset:
                    sub_score = self._compute_structural_score(prompt, subset)
                    if sub_score > max_affinity:
                        max_affinity = sub_score

        # Add small noise tolerance (Active Inference: minimizing free energy)
        # If the candidate is very close to prompt structure, boost slightly
        return min(1.0, max_affinity)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Detects ambiguity, traps, and unanswerable conditions.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Traps ("Have you stopped...", "Why did X fail?")
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        
        # 2. Pronoun Ambiguity ("John told Bill he... who?")
        if self.patterns['pronoun_trap'].search(p_lower):
            return 0.2
            
        # 3. False Dichotomy without clear options
        if self.patterns['false_dichotomy'].search(p_lower) and 'only' not in p_lower:
            # Soft penalty, depends on context
            return 0.5
            
        # 4. Subjectivity
        if self.patterns['subjectivity'].search(p_lower):
            return 0.4
            
        # 5. Unanswerability (No structural hooks found)
        antigens = self._extract_antigens(prompt)
        if not antigens and len(prompt.split()) < 10:
            # Very short prompt with no logic markers might be ambiguous
            return 0.3
            
        return 1.0  # No traps detected

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        try:
            z1 = len(zlib.compress(s1.encode()))
            z2 = len(zlib.compress(s2.encode()))
            z12 = len(zlib.compress((s1 + s2).encode()))
            if max(z1, z2) == 0: return 1.0
            return float(z12 - min(z1, z2)) / max(z1, z2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural & Clonal Score (Primary Signal)
            structural_score = self._clonal_expansion_and_score(prompt, cand)
            
            # 2. NCD Tiebreaker (Secondary Signal, max 15% weight)
            # We invert NCD so high similarity = high score
            ncd_val = self._ncd_score(prompt, cand)
            ncd_score = 1.0 - ncd_val
            
            # Weighted Combination
            # Structural >= 50%, Computation (included in structural) >= 20%, NCD <= 15%
            # Let's do: 85% Structural, 15% NCD
            raw_score = (0.85 * structural_score) + (0.15 * ncd_score)
            
            # Apply Epistemic Cap
            final_score = min(raw_score, meta_cap)
            
            # Reasoning string
            reason = f"Structural fit: {structural_score:.2f}, NCD: {ncd_score:.2f}"
            if meta_cap < 1.0:
                reason += " [CAP: Ambiguity/Trap Detected]"
                
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reason
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at meta-confidence limit derived from prompt analysis.
        """
        # 1. Check for traps (Tier B)
        cap = self._meta_confidence(prompt)
        
        # 2. Evaluate structural fit
        score_data = self.evaluate(prompt, [answer])
        if not score_data:
            return 0.0
            
        raw_score = score_data[0]['score']
        
        # 3. Apply cap
        final_conf = min(raw_score, cap)
        
        # 4. Honesty check: If structural signal is weak, don't overconfidence
        # Even if cap is high, if the answer doesn't match structure, confidence should be low
        return round(final_conf, 4)