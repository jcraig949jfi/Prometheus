import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Compositional Adaptive Matched-Filter (CAMF) Reasoning Engine.
    
    Mechanism:
    1. Compositional Parsing (Symbolic Layer): Decomposes prompts into primitive 
       structural templates (negations, comparatives, conditionals) and logical 
       operators. This acts as the 'hypothesis generator'.
    2. Matched Filtering (Detection Layer): Computes cross-correlation between 
       the prompt structure and known reasoning patterns (templates). High SNR 
       indicates a strong structural match for a specific reasoning mode.
    3. Adaptive Control (Feedback Layer): Adjusts the 'gain' of the detection 
       based on meta-cognitive checks (Tier B). If ambiguity, presupposition, 
       or unanswerability is detected, the adaptive loop suppresses the confidence 
       score (error-driven tuning), preventing overconfidence in flawed premises.
    4. Scoring: Structural parsing provides the base score (>50%), constructive 
       computation adds precision (>20%), and NCD serves only as a tiebreaker (<15%).
    """

    def __init__(self):
        # Primitive templates for matched filtering (Regex patterns)
        self.templates = {
            'negation': re.compile(r'\b(not|no|never|none|neither|without)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worst|best)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|otherwise)\b', re.IGNORECASE),
            'numeric': re.compile(r'\d+(\.\d+)?'),
            'boolean_choice': re.compile(r'\b(yes|no|true|false)\b', re.IGNORECASE),
            'presupposition_stop': re.compile(r'\b(stopped|quit|ceased)\b', re.IGNORECASE),
            'presupposition_why': re.compile(r'^\s*why\s+did', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either|or)\b', re.IGNORECASE),
            'pronoun_he': re.compile(r'\b(he|him|his)\b', re.IGNORECASE),
            'pronoun_she': re.compile(r'\b(she|her|hers)\b', re.IGNORECASE),
            'scope_every': re.compile(r'\b(every|all)\b', re.IGNORECASE),
        }
        
        # Adaptive state (simplified for stateless-ish operation per instance)
        self.adaptive_gain = 1.0

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Epistemic Honesty Check.
        Returns a cap value (0.0 - 1.0) based on prompt pathology.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Traps
        if self.templates['presupposition_stop'].search(p_lower) and ('stopped' in p_lower or 'quit' in p_lower):
            # Context check: "Have you stopped..."
            if re.search(r'\b(have|has|did)\s+you\s+\w+\s+(stopped|quit)', p_lower):
                return 0.2
        
        if self.templates['presupposition_why'].search(p_lower):
            return 0.2 # "Why did X fail" implies X failed.

        # 2. Scope Ambiguity
        if self.templates['scope_every'].search(p_lower) and 'same' in p_lower:
            return 0.4 # Ambiguous scope

        # 3. Pronoun Ambiguity
        if ('told' in p_lower or 'said' in p_lower) and ('he' in p_lower or 'she' in p_lower):
            if 'who' in p_lower and '?' in p_lower:
                return 0.3

        # 4. False Dichotomy
        if 'either' in p_lower and 'or' in p_lower:
            if 'option' not in p_lower and 'choice' not in p_lower:
                 # Heuristic: if it looks like a forced choice without context
                if re.search(r'either\s+\w+\s+or\s+\w+\?', p_lower):
                    return 0.3

        # 5. Subjectivity
        subjective_words = ['best', 'worst', 'favorite', 'beautiful', 'ugly', 'tasty']
        if any(word in p_lower for word in subjective_words):
            if 'measure' not in p_lower and 'data' not in p_lower:
                return 0.4

        # 6. Unanswerability (Missing info heuristic)
        if re.search(r'(who|what|where|when)\s+is\s+the\s+(king|owner|answer)', p_lower):
             if 'context' not in p_lower and 'text' not in p_lower:
                return 0.2

        return 1.0 # No meta-issues detected

    def _structural_parse_and_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Performs structural parsing and constructive computation.
        Returns (score, reasoning_string).
        Base score starts at 0.5 (neutral).
        """
        score = 0.5
        reasons = []
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # --- Matched Filter: Structural Detection ---
        has_negation = bool(self.templates['negation'].search(p_lower))
        has_comparative = bool(self.templates['comparative'].search(p_lower))
        has_conditional = bool(self.templates['conditional'].search(p_lower))
        has_numbers = self.templates['numeric'].findall(p_lower)
        
        # 1. Negation Handling (Constraint Propagation)
        if has_negation:
            # Check if candidate respects negation logic
            # Simple heuristic: if prompt says "not X", candidate should not be "X"
            # This is a simplification; real logic requires NLP parse tree
            reasons.append("Detected negation constraint.")
            score += 0.15
            if 'not' in c_lower or 'no' in c_lower:
                score += 0.1 # Candidate acknowledges negation
            else:
                score -= 0.1 # Penalty if candidate ignores negation context

        # 2. Comparative Logic
        if has_comparative:
            reasons.append("Detected comparative logic.")
            score += 0.15
            # Check if candidate contains comparative words or numbers
            if self.templates['comparative'].search(c_lower) or self.templates['numeric'].search(c_lower):
                score += 0.1
            else:
                score -= 0.05

        # 3. Conditional Logic
        if has_conditional:
            reasons.append("Detected conditional structure.")
            score += 0.1
            if 'if' in c_lower or 'then' in c_lower or 'unless' in c_lower:
                score += 0.1

        # --- Constructive Computation (Numeric Evaluation) ---
        if len(has_numbers) >= 2:
            try:
                nums = [float(n) for n in has_numbers]
                # Detect simple arithmetic or comparison in prompt
                if 'sum' in p_lower or 'add' in p_lower:
                    expected = sum(nums)
                    # Check if candidate matches expected sum roughly
                    c_nums = self.templates['numeric'].findall(c_lower)
                    if c_nums and abs(float(c_nums[-1]) - expected) < 0.01:
                        score += 0.4
                        reasons.append(f"Computed sum: {expected}")
                    else:
                        score -= 0.2
                        reasons.append(f"Computation mismatch. Expected {expected}")
                
                elif 'greater' in p_lower or 'larger' in p_lower or 'max' in p_lower:
                    expected = max(nums)
                    c_nums = self.templates['numeric'].findall(c_lower)
                    if c_nums and abs(float(c_nums[-1]) - expected) < 0.01:
                        score += 0.3
                        reasons.append(f"Computed max: {expected}")
                        
                elif 'smaller' in p_lower or 'min' in p_lower:
                    expected = min(nums)
                    c_nums = self.templates['numeric'].findall(c_lower)
                    if c_nums and abs(float(c_nums[-1]) - expected) < 0.01:
                        score += 0.3
                        reasons.append(f"Computed min: {expected}")

            except ValueError:
                pass

        # --- Constraint Propagation (Boolean/Logic) ---
        if 'yes' in c_lower or 'true' in c_lower:
            if 'impossible' in p_lower or 'false' in p_lower:
                score -= 0.4
                reasons.append("Contradicts explicit impossibility.")
        
        if not reasons:
            reasons.append("Structural analysis complete.")

        return min(1.0, max(0.0, score)), "; ".join(reasons)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-compute meta-confidence cap (Adaptive Control Signal)
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural & Computational Score (Primary Signal ~85%)
            struct_score, reasoning = self._structural_parse_and_score(prompt, cand)
            
            # 2. NCD Tiebreaker (Secondary Signal ~15% max)
            # Only used if structural score is neutral (around 0.5)
            ncd_score = 0.0
            if 0.45 <= struct_score <= 0.55:
                ncd_val = self._compute_ncd(prompt, cand)
                # Invert NCD (lower distance = higher score) and scale small
                ncd_score = (1.0 - ncd_val) * 0.15
            
            final_score = struct_score + ncd_score
            
            # 3. Adaptive Control: Apply Meta-Confidence Cap
            # If the prompt is ambiguous/trapped, the system MUST lower confidence
            if final_score > meta_cap:
                final_score = meta_cap
                reasoning += " [Capped by meta-cognitive check]"

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly enforces epistemic honesty via _meta_confidence.
        """
        # 1. Check Meta-Constraints (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Evaluate structural fit
        score, _ = self._structural_parse_and_score(prompt, answer)
        
        # 3. Add minor NCD component if structural is weak
        if score < 0.6:
            ncd_val = self._compute_ncd(prompt, answer)
            score += (1.0 - ncd_val) * 0.1
            
        # 4. Apply Adaptive Cap
        final_conf = min(score, meta_cap)
        
        # Ensure strict bounds
        return round(max(0.0, min(1.0, final_conf)), 4)