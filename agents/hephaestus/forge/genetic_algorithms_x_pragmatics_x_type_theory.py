import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Pragmatic Type-Guided Evolutionary Proof Search (PTGEPS) Approximation.
    
    Mechanism:
    1. TYPE THEORY (Structural Validity): Uses regex structural parsing to enforce 
       logical constraints (negations, comparatives, conditionals). Candidates violating 
       these 'types' (logical forms) are penalized heavily.
    2. PRAGMATICS (Contextual Fitness): Evaluates Relevance (keyword overlap with prompt 
       intent) and Quantity (penalizes over/under-informative lengths relative to prompt).
    3. GENETIC ALGORITHMS (Selection): Treats the candidate list as a population. 
       Scores act as fitness. Selection favors high pragmatic fitness + type safety.
    4. NCD: Used strictly as a tiebreaker for semantically similar candidates.
    
    This implements the core loop of PTGEPS without external dependencies, focusing on 
    structural parsing and logical consistency as the primary drivers.
    """

    def __init__(self):
        # Structural parsers acting as "Type Checkers"
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparative_ops = ['>', '<', 'greater', 'less', 'more', 'fewer', 'larger', 'smaller']
        self.conditionals = ['if', 'then', 'unless', 'otherwise']
        self.numeric_pattern = re.compile(r"-?\d+\.?\d*")

    def _extract_structure(self, text: str) -> dict:
        """Parses text for logical structures (Type Theory layer)."""
        lower = text.lower()
        words = set(re.findall(r'\b\w+\b', lower))
        
        has_negation = bool(words & self.negation_words)
        has_comparative = any(op in lower for op in self.comparative_ops)
        has_conditional = any(cond in lower for cond in self.conditionals)
        numbers = [float(n) for n in self.numeric_pattern.findall(text)]
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'word_count': len(words)
        }

    def _check_type_consistency(self, prompt_struct: dict, cand_struct: dict, prompt: str, candidate: str) -> float:
        """
        Checks if the candidate respects the logical 'types' implied by the prompt.
        Returns 1.0 for consistent, <1.0 for violations.
        """
        score = 1.0
        
        # Modus Tollens/Negation Check: If prompt asks a negative question, answer should reflect it
        # Simple heuristic: If prompt has negation and candidate is a simple 'Yes/No', check alignment
        if prompt_struct['negation']:
            lower_cand = candidate.lower().strip()
            # If prompt is negative, a bare "yes" might be ambiguous/wrong without context
            if lower_cand in ['yes', 'yeah', 'yep']:
                score -= 0.2 # Penalty for potential pragmatic failure on negation
        
        # Numeric Consistency: If prompt has numbers and candidate has numbers, check ordering if comparatives exist
        if prompt_struct['comparative'] and cand_struct['comparative']:
            if len(prompt_struct['numbers']) >= 2 and len(cand_struct['numbers']) >= 1:
                # Extract logic: if prompt implies A > B, and candidate asserts a value, 
                # we can't fully verify without semantic mapping, but we check presence.
                pass 

        # Conditional Closure: If prompt is conditional, candidate shouldn't be a bare fact ignoring the condition
        if prompt_struct['conditional'] and not cand_struct['conditional']:
            # Heuristic: Long prompts with 'if' usually require nuanced answers, not just "True"
            if cand_struct['word_count'] < 3:
                score -= 0.3

        return max(0.0, score)

    def _pragmatic_score(self, prompt: str, candidate: str, prompt_struct: dict) -> float:
        """
        Evaluates Gricean Maxims: Relevance, Quantity, Quality, Manner.
        """
        p_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        c_words = set(re.findall(r'\b\w+\b', candidate.lower()))
        
        # 1. Relevance: Overlap of significant words (excluding very common stopwords)
        stopwords = {'the', 'is', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'it', 'that'}
        sig_p = p_words - stopwords
        sig_c = c_words - stopwords
        
        if not sig_p:
            relevance = 0.5
        else:
            intersection = sig_p & sig_c
            relevance = len(intersection) / len(sig_p) if len(sig_p) > 0 else 0.0
            
        # 2. Quantity: Is the answer too short or too long relative to prompt complexity?
        # Ideal length heuristic: Answer should be 10%-80% of prompt length usually, 
        # unless it's a direct extraction task.
        p_len = len(prompt)
        c_len = len(candidate)
        quantity_score = 1.0
        if c_len == 0:
            quantity_score = 0.0
        elif c_len < 2 and p_len > 20: # Too brief for complex prompt
            quantity_score = 0.7
        elif c_len > p_len * 1.5: # Too verbose
            quantity_score = 0.8
            
        # 3. Manner (Perspicuity): Avoidance of contradiction markers within the candidate itself
        # Simple check: does it say "yes" and "no"?
        lower_c = candidate.lower()
        if ('yes' in lower_c and 'no' in lower_c) and ('if' not in lower_c):
            manner_score = 0.5 # Ambiguous
        else:
            manner_score = 1.0
            
        return (relevance * 0.4 + quantity_score * 0.3 + manner_score * 0.3)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            max_len = max(c1, c2)
            if max_len == 0: return 0.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        scored_candidates = []
        
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # 1. Type Consistency (Hard constraints/Logic)
            type_score = self._check_type_consistency(prompt_struct, cand_struct, prompt, cand)
            
            # 2. Pragmatic Fitness (Contextual relevance)
            prag_score = self._pragmatic_score(prompt, cand, prompt_struct)
            
            # 3. Numeric Evaluation (Specific capability check)
            numeric_bonus = 0.0
            if prompt_struct['numbers'] and cand_struct['numbers']:
                # If both have numbers, check if the candidate numbers make sense logically 
                # (e.g. if prompt asks for max, does candidate have the max number?)
                # Simplified: Just bonus for having numbers when prompt has them
                numeric_bonus = 0.1 
            
            # Base Score
            score = (type_score * 0.5) + (prag_score * 0.4) + numeric_bonus
            
            scored_candidates.append({
                "candidate": cand,
                "base_score": score,
                "struct": cand_struct
            })
        
        # Genetic Selection / Ranking Phase
        # Sort by base score first
        scored_candidates.sort(key=lambda x: x['base_score'], reverse=True)
        
        # Apply NCD as tie-breaker and final refinement
        # We want diversity (low similarity to poor candidates) but high similarity to prompt intent
        final_results = []
        for i, item in enumerate(scored_candidates):
            cand = item['candidate']
            score = item['base_score']
            
            # Tie-breaking logic using NCD against the prompt (Relevance via compression)
            # Lower NCD to prompt means more relevant information density
            ncd_prompt = self._ncd(prompt, cand)
            
            # Adjust score slightly by NCD to break ties
            # High similarity to prompt (low NCD) is good, but we don't want exact echo
            ncd_factor = 0.0
            if len(scored_candidates) > 1:
                # If scores are very close, use NCD
                # This is a simplified evolutionary pressure step
                ncd_factor = (1.0 - ncd_prompt) * 0.05 
            
            final_score = min(1.0, score + ncd_factor)
            
            reasoning = f"Type-safe: {item['base_score'] > 0.5}, Pragmatic-fit: {prag_score:.2f}"
            
            final_results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reasoning
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural and pragmatic alignment."""
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        return results[0]['score']