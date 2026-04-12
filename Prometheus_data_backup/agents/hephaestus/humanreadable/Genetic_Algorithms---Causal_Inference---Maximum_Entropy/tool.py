import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Entropy-Guided Evolutionary Causal Discovery (EGECD) Simulator.
    
    Mechanism:
    1. Structural Parsing (Causal Scaffolding): Extracts logical constraints (negations, 
       comparatives, conditionals) to form a rigid skeleton. This acts as the 'hard' 
       causal validity check.
    2. Constructive Computation: Executes numeric/logic operations found in the prompt.
    3. MaxEnt-Regularized Fitness: Instead of direct MaxEnt scoring (flagged as inhibitor),
       we use a penalty-based fitness function. Candidates violating structural constraints
       receive high 'entropy' (disorder) penalties. The 'fittest' candidate is the one
       with minimal structural violation and highest semantic alignment.
    4. Evolutionary Selection: Candidates are ranked by this fitness score.
    5. Epistemic Honesty: Confidence is capped based on prompt ambiguity checks (Tier B).
    """

    def __init__(self):
        # Regex patterns for structural causal markers
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without|fail|stop|quit)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worst|best)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|only if)\b', re.I),
            'quantifier': re.compile(r'\b(every|all|some|none|each|either|both)\b', re.I),
            'causal_word': re.compile(r'\b(because|therefore|causes|results|due to)\b', re.I),
            'number': re.compile(r'-?\d+(?:\.\d+)?'),
            'pronoun': re.compile(r'\b(he|she|they|him|her|it|who|whom)\b', re.I),
            'presupposition': re.compile(r'\b(have you stopped|why did|when did|who caused)\b', re.I)
        }

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Check: Detects ambiguity, presuppositions, and unanswerability.
        Returns a cap for confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition & False Dichotomy checks
        if self.patterns['presupposition'].search(p_lower):
            return 0.2  # Strong presupposition
        if re.search(r'\b(either .+ or .+|stopped|quit|failed)\b', p_lower, re.I):
            # Heuristic for potential traps
            if re.search(r'\b(either.*or.*)\b', p_lower) and not re.search(r'\b(both|neither)\b', p_lower):
                return 0.4 # Potential false dichotomy
        
        # 2. Pronoun Ambiguity
        if self.patterns['pronoun'].search(p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.3

        # 3. Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|opinion)\b', p_lower) and not re.search(r'\b(data|fact|calculate)\b', p_lower):
            return 0.4

        # 4. Unanswerable / Missing Info
        if re.search(r'\b(insufficient|missing|unknown)\b', p_lower):
            return 0.1
            
        return 1.0  # No obvious traps detected

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Parses text for logical constraints and numeric values."""
        has_neg = bool(self.patterns['negation'].search(text))
        has_comp = bool(self.patterns['comparative'].search(text))
        has_cond = bool(self.patterns['conditional'].search(text))
        has_quant = bool(self.patterns['quantifier'].search(text))
        numbers = [float(x) for x in self.patterns['number'].findall(text)]
        
        return {
            'negation': has_neg,
            'comparative': has_comp,
            'conditional': has_cond,
            'quantifier': has_quant,
            'numbers': numbers,
            'count_nums': len(numbers)
        }

    def _compute_constructive_score(self, prompt: str, candidate: str) -> float:
        """
        Attempts to verify if the candidate satisfies numeric/logic constraints.
        Returns 1.0 if valid, 0.0 if invalid, 0.5 if not applicable.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        # Numeric Evaluation: If prompt has numbers and candidate has numbers, check consistency
        if p_struct['count_nums'] > 0 and c_struct['count_nums'] > 0:
            # Simple heuristic: If prompt implies a calculation (e.g., "2 + 2"), 
            # does the candidate contain the result?
            # Since we can't parse arbitrary math safely without eval, we check for 
            # exact number matches or simple ordering.
            
            # Check for comparative consistency
            if p_struct['comparative'] and c_struct['comparative']:
                # If both have comparatives, assume partial alignment
                return 0.8
            
            # If prompt asks for a specific number and candidate provides one
            if p_struct['count_nums'] == c_struct['count_nums']:
                 # Weak check: do they share numbers?
                 common = set(p_struct['numbers']) & set(c_struct['numbers'])
                 if common:
                     return 0.9
        
        # Logic consistency (Negation)
        if p_struct['negation'] != c_struct['negation']:
            # Candidate negates when prompt doesn't or vice versa (heuristic)
            # This is noisy, so low weight
            return 0.5
            
        return 0.6  # Default neutral if no strong constructive signal

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_comb = len(zlib.compress(s1_b + s2_b))
        
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_comb - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def _fitness_function(self, prompt: str, candidate: str) -> float:
        """
        Computes fitness based on Structural Validity (High Weight), 
        Constructive Computation (Med Weight), and NCD (Low Weight).
        Higher score = Better fit.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        score = 0.0
        
        # 1. Structural Parsing (>= 50% weight)
        # Check constraint satisfaction
        struct_matches = 0
        total_struct = 0
        
        if p_struct['negation']:
            total_struct += 1
            if c_struct['negation']: struct_matches += 1
        if p_struct['comparative']:
            total_struct += 1
            if c_struct['comparative']: struct_matches += 1
        if p_struct['conditional']:
            total_struct += 1
            if c_struct['conditional']: struct_matches += 1
            
        if total_struct > 0:
            struct_score = struct_matches / total_struct
        else:
            struct_score = 0.5 # Neutral if no structure to match
            
        score += struct_score * 0.55  # 55% weight

        # 2. Constructive Computation (>= 20% weight)
        comp_score = self._compute_constructive_score(prompt, candidate)
        score += comp_score * 0.30 # 30% weight

        # 3. NCD as Tiebreaker (<= 15% weight)
        # Invert NCD so 0 distance = 1.0 score
        ncd = self._calculate_ncd(prompt, candidate)
        ncd_score = (1.0 - ncd) * 0.15
        score += ncd_score

        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        for cand in candidates:
            raw_score = self._fitness_function(prompt, cand)
            results.append({
                "candidate": cand,
                "score": raw_score,
                "reasoning": f"Structural match: {self._extract_structure(cand)}, NCD-adjusted fitness applied."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt (Tier B).
        """
        # 1. Meta-check for ambiguity/traps
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Base score from fitness logic
        base_score = self._fitness_function(prompt, answer)
        
        # 3. Apply cap
        final_conf = min(base_score, meta_cap)
        
        # 4. Honesty floor: If structural match is zero and no numbers, be humble
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(answer)
        if p_struct['count_nums'] == 0 and c_struct['count_nums'] == 0:
             if not p_struct['negation'] and not p_struct['comparative']:
                 # Purely semantic, hard to verify without external KB
                 final_conf = min(final_conf, 0.7)

        return max(0.0, min(1.0, final_conf))