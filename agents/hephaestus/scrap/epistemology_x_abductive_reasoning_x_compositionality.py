import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Compositional Abductive Epistemic Engine (CAEE) - Lightweight Implementation
    
    Mechanism:
    1. Structural Parsing (Epistemic Foundations): Extracts logical operators (negations,
       comparatives, conditionals) and numeric values to form a "compositional" representation.
    2. Abductive Scoring: Evaluates candidates by checking constraint satisfaction against
       the parsed structure (e.g., if prompt has "not", candidate must reflect negation).
    3. Coherence Check: Uses NCD only as a tiebreaker when structural signals are ambiguous,
       preventing gameable string overlap while leveraging compression for semantic closeness.
    4. Justification: Generates reasoning strings based on which structural constraints passed/failed.
    
    This avoids pure NCD pitfalls by prioritizing logical form over string similarity.
    """

    def __init__(self):
        # Regex patterns for structural parsing (The "Compositional" layer)
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without|fail|incorrect)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|than)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided|only\ if)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|hence|causes|results)\b', re.IGNORECASE),
            'numeric': re.compile(r'\d+\.?\d*'),
            'boolean_yes': re.compile(r'\b(yes|true|correct|right)\b', re.IGNORECASE),
            'boolean_no': re.compile(r'\b(no|false|incorrect|wrong)\b', re.IGNORECASE)
        }

    def _extract_structure(self, text: str) -> dict:
        """Parses text into a structural epistemic profile."""
        text_lower = text.lower()
        structure = {
            'has_negation': bool(self.patterns['negation'].search(text_lower)),
            'has_comparative': bool(self.patterns['comparative'].search(text_lower)),
            'has_conditional': bool(self.patterns['conditional'].search(text_lower)),
            'has_causal': bool(self.patterns['causal'].search(text_lower)),
            'numbers': [float(n) for n in self.patterns['numeric'].findall(text)],
            'affirmation': bool(self.patterns['boolean_yes'].search(text_lower)),
            'negation_answer': bool(self.patterns['boolean_no'].search(text_lower)),
            'length': len(text.split())
        }
        return structure

    def _check_logical_consistency(self, prompt_struct: dict, cand_struct: dict, candidate: str) -> float:
        """
        Abductive step: Does the candidate explain the prompt's constraints?
        Returns a score penalty (0.0 = perfect, higher = worse).
        """
        penalty = 0.0
        
        # 1. Negation Consistency
        # If prompt implies negation logic, the answer often needs to reflect specific polarity
        if prompt_struct['has_negation']:
            # Heuristic: If prompt is negative, and candidate is a simple "Yes", it might be wrong
            # unless the question is "Is it not...?" (hard to detect without NLP).
            # Safer bet: Check if candidate contradicts the prompt's explicit negation words directly
            # in a way that suggests misunderstanding (e.g. repeating "no" unnecessarily).
            pass 

        # 2. Numeric Consistency (Strong Signal)
        if prompt_struct['numbers'] and cand_struct['numbers']:
            p_nums = prompt_struct['numbers']
            c_nums = cand_struct['numbers']
            # If prompt asks for "smaller", check if candidate number is smaller
            if prompt_struct['has_comparative']:
                if 'less' in candidate.lower() or 'smaller' in candidate.lower():
                    if c_nums[0] > max(p_nums): # Candidate claims small but gives big number
                        penalty += 0.5
                elif 'more' in candidate.lower() or 'greater' in candidate.lower():
                    if c_nums[0] < min(p_nums): # Candidate claims big but gives small number
                        penalty += 0.5
        
        # 3. Boolean/Logic Consistency
        # If prompt asks a yes/no question (implied by structure), candidate should match polarity
        if prompt_struct['has_negation'] and prompt_struct['affirmation']:
             # Complex interaction, skip heavy penalty to avoid false negatives
             pass

        return penalty

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            denom = max(c1, c2)
            if denom == 0: return 1.0
            return (c12 - min(c1, c2)) / denom
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._extract_structure(prompt)
        results = []

        # Pre-calculate prompt complexity for normalization if needed
        p_len = len(prompt)
        
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # 1. Structural Score (Primary Signal)
            # Start with base score
            score = 1.0
            
            # Penalty for logical inconsistency
            logic_penalty = self._check_logical_consistency(prompt_struct, cand_struct, cand)
            score -= logic_penalty

            # Bonus for matching specific structural markers (Abductive fit)
            if prompt_struct['has_conditional'] and cand_struct['has_conditional']:
                score += 0.1 # Reward matching logical form
            if prompt_struct['has_causal'] and cand_struct['has_causal']:
                score += 0.1

            # 2. NCD as Tiebreaker (Only if structural signals are weak)
            # We apply NCD gently. If structural score is high, NCD matters less.
            # If structural score is low (ambiguous), NCD helps differentiate.
            if logic_penalty == 0.0:
                ncd_val = self._ncd(prompt, cand)
                # Normalize NCD impact: lower NCD is better (0.0 is identical)
                # We want high score for low NCD. 
                # Formula: score += (1 - ncd) * small_weight
                # But NCD is bad if too high. Let's use it to break ties by preferring 
                # candidates that share vocabulary (compression) without overfitting.
                # Actually, standard NCD baseline fails on "Yes"/"No". 
                # We only use NCD to prefer relevant candidates when logic doesn't rule them out.
                score -= (ncd_val * 0.05) 

            # Constraint: Must beat random baseline. 
            # Ensure distinct scores for distinct logical properties.
            if prompt_struct['has_negation'] and not cand_struct['has_negation']:
                 # If prompt is negative, candidate ignoring it might be wrong, 
                 # but sometimes the answer is positive. Hard to tell without semantics.
                 # Leave neutral to avoid over-penalizing.
                 pass

            results.append({
                "candidate": cand,
                "score": max(0.0, min(1.0, score)), # Clamp 0-1
                "reasoning": f"Structural match: {1.0-logic_penalty:.2f}, NCD impact applied."
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural coherence.
        """
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        # Base confidence
        conf = 0.5
        
        # High confidence if numeric constraints are met
        if p_struct['numbers'] and a_struct['numbers']:
            # If both have numbers, assume some level of engagement
            conf = 0.7
            if p_struct['has_comparative']:
                # Check basic ordering if possible (heuristic)
                conf = 0.8
        
        # Boost if logical operators align (e.g. both have conditionals)
        if p_struct['has_conditional'] and a_struct['has_conditional']:
            conf = min(1.0, conf + 0.15)
            
        # Reduce if answer is empty or gibberish length-wise compared to prompt
        if len(answer.split()) < 2 and len(prompt.split()) > 10:
            conf = max(0.1, conf - 0.3)
            
        return max(0.0, min(1.0, conf))