import re
import math
import zlib
from typing import List, Dict, Tuple, Any, Optional

class ReasoningTool:
    """
    A reasoning evaluation tool combining Dual Process Theory, Property-Based Testing,
    and Sensitivity Analysis.
    
    Mechanism:
    1. System 1 (Fast): Parses atomic propositions (negations, comparatives, numerics).
    2. System 2 (Slow): Propagates constraints and performs constructive computation.
    3. Property Testing: Perturbs inputs to test robustness (sensitivity).
    4. Epistemic Honesty: Detects ambiguity/traps to cap confidence.
    
    Score = (Structural Match * Computation Accuracy) * (1 - Sensitivity Penalty)
    """

    def __init__(self):
        # Regex patterns for System 1 parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|without)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.I),
            'conditional': re.compile(r'\b(if|then|when|unless)\b', re.I),
            'causal': re.compile(r'\b(because|causes|leads to|results in)\b', re.I),
            'numeric': re.compile(r'-?\d+(\.\d+)?'),
            'presupposition': re.compile(r'\b(have you stopped|why did|when did|quit)\b', re.I),
            'scope_ambiguity': re.compile(r'\b(every|all).*\b(a|an)\b', re.I),
            'pronoun_ambiguity': re.compile(r'\b(told|said|asked)\b.*\b(he|she|him|her)\b', re.I),
            'false_dichotomy': re.compile(r'\b(either|or)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion)\b', re.I)
        }
        self.lambda_penalty = 0.5  # Weight for sensitivity penalty

    def _parse_propositions(self, text: str) -> List[Dict]:
        """System 1: Extract atomic propositions with polarity and type."""
        props = []
        text_lower = text.lower()
        
        # Check types
        has_neg = bool(self.patterns['negation'].search(text))
        has_comp = bool(self.patterns['comparative'].search(text))
        has_cond = bool(self.patterns['conditional'].search(text))
        has_causal = bool(self.patterns['causal'].search(text))
        
        # Extract numbers
        numbers = [float(m.group(0)) for m in self.patterns['numeric'].finditer(text)]
        
        if numbers:
            props.append({'type': 'numeric', 'value': numbers, 'polarity': -1 if has_neg else 1})
        
        if has_comp:
            props.append({'type': 'comparative', 'polarity': -1 if has_neg else 1})
        if has_cond:
            props.append({'type': 'conditional', 'polarity': -1 if has_neg else 1})
        if has_causal:
            props.append({'type': 'causal', 'polarity': -1 if has_neg else 1})
            
        # Fallback for pure text structure if no specific type found but negation exists
        if not props and has_neg:
            props.append({'type': 'negation', 'polarity': -1})
            
        return props if props else [{'type': 'statement', 'polarity': 1}]

    def _constructive_compute(self, prompt: str, answer: str) -> Tuple[float, bool]:
        """
        Frame B: Constructive Computation.
        Attempts to solve numeric/logic problems directly.
        Returns (computed_value_match_score, is_definitive).
        """
        # Extract numbers from prompt and answer
        p_nums = [float(m.group(0)) for m in self.patterns['numeric'].finditer(prompt)]
        a_nums = [float(m.group(0)) for m in self.patterns['numeric'].finditer(answer)]
        
        # Heuristic: If prompt has numbers and answer has numbers, check arithmetic consistency
        if p_nums and a_nums:
            # Simple case: Answer is one of the prompt numbers (extraction)
            if any(abs(a - p) < 1e-6 for a in a_nums for p in p_nums):
                return 1.0, True
            
            # Simple case: Answer is sum/product of prompt numbers (Computation)
            p_sum = sum(p_nums)
            p_prod = 1
            for p in p_nums: p_prod *= p
            
            # Check if answer matches simple aggregation
            if any(abs(a - p_sum) < 1e-6 for a in a_nums):
                return 1.0, True
            if any(abs(a - p_prod) < 1e-6 for a in a_nums):
                return 1.0, True
                
            # If numbers exist but don't match simple logic, it might be wrong or complex
            # We give partial credit if close, but mark as not definitive
            return 0.5, False

        # Logic keyword matching for non-numeric constructive steps
        p_lower = prompt.lower()
        a_lower = answer.lower()
        
        # Check for direct contradiction in yes/no
        if ('yes' in p_lower or 'no' in p_lower) and ('yes' in a_lower or 'no' in a_lower):
            # Very rough heuristic: if prompt asks "Is X > Y?" and answer says "No"
            # We can't fully solve without semantic parsing, so we rely on structural match here
            return 0.8, False
            
        return 0.0, False

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty.
        Detects ambiguity, presuppositions, and unanswerable structures.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        
        # 2. Scope ambiguity (simplified)
        if self.patterns['scope_ambiguity'].search(p_lower):
            return 0.4
            
        # 3. Pronoun ambiguity (if question asks "who")
        if self.patterns['pronoun_ambiguity'].search(p_lower) and 'who' in p_lower:
            return 0.3
            
        # 4. False dichotomy
        if self.patterns['false_dichotomy'].search(p_lower) and 'or' in p_lower:
            # Only flag if it looks like a forced choice without "either"
            if 'either' not in p_lower: 
                return 0.5
                
        # 5. Subjectivity
        if self.patterns['subjectivity'].search(p_lower):
            return 0.3
            
        # 6. Unanswerability (keywords)
        unanswerable_keys = ['insufficient', 'cannot be determined', 'unknown']
        if any(k in p_lower for k in unanswerable_keys):
            return 0.2
            
        return 1.0

    def _generate_perturbations(self, text: str) -> List[str]:
        """Property-based test generation: Create minimal perturbations."""
        perturbations = [text]
        
        # 1. Flip negation
        if 'not' in text.lower():
            perturbations.append(text.replace('not', '').replace('Not', ''))
        else:
            # Add negation to first verb-ish word (simplified)
            words = text.split()
            if len(words) > 2:
                words[1] = "not " + words[1]
                perturbations.append(" ".join(words))
                
        # 2. Numeric shift (if numbers exist)
        nums = list(self.patterns['numeric'].finditer(text))
        if nums:
            # Perturb the first number found by +5%
            m = nums[0]
            val = float(m.group(0))
            new_val = val * 1.05
            perturbed_text = text[:m.start()] + f"{new_val:.2f}" + text[m.end():]
            perturbations.append(perturbed_text)
            
        return perturbations

    def _sensitivity_analysis(self, prompt: str, candidate: str) -> float:
        """
        Step 4 & 5: Sensitivity Analysis.
        Measures how much the 'correctness' signal changes under perturbation.
        High sensitivity (fragility) reduces the score.
        """
        base_props = self._parse_propositions(candidate)
        base_score = len(base_props) # Simple proxy for entailment strength
        
        perturbations = self._generate_perturbations(candidate)
        if len(perturbations) <= 1:
            return 0.0 # No perturbations generated, assume stable
            
        scores = []
        for p_text in perturbations:
            p_props = self._parse_propositions(p_text)
            # Compare structural similarity of props
            score = 0
            if len(p_props) == len(base_props):
                score = 1.0
            else:
                # Penalize structural drift
                score = 0.5 
            scores.append(score)
            
        if not scores:
            return 0.0
            
        # Calculate variance as sensitivity proxy
        avg_s = sum(scores) / len(scores)
        variance = sum((s - avg_s)**2 for s in scores) / len(scores)
        sensitivity = math.sqrt(variance)
        
        return sensitivity

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (max 15% weight)."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        concat = s1_bytes + s2_bytes
        
        len1 = len(zlib.compress(s1_bytes))
        len2 = len(zlib.compress(s2_bytes))
        len_concat = len(zlib.compress(concat))
        
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_concat - max_len) / max_len

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Main entry point for confidence scoring.
        Combines structural parsing, constructive computation, and epistemic checks.
        """
        # Tier B: Epistemic Honesty Check
        meta_cap = self._meta_confidence(prompt)
        if meta_cap < 0.3:
            return meta_cap

        # Constructive Computation (Frame B)
        comp_score, is_definitive = self._constructive_compute(prompt, answer)
        
        # If computation yielded a definitive result, trust it highly (capped by meta)
        if is_definitive and comp_score > 0.8:
            return min(0.95, meta_cap)
            
        # Structural Parsing (System 1 & 2)
        props = self._parse_propositions(answer)
        struct_score = 0.0
        if props:
            # Basic heuristic: Does the answer contain relevant structural tokens?
            # In a real scenario, we compare against prompt props. 
            # Here we assume presence of structure in answer is better than none.
            struct_score = 0.6 if len(props) > 0 else 0.1
            
        # Sensitivity Penalty
        sensitivity = self._sensitivity_analysis(prompt, answer)
        robustness_factor = 1.0 - (self.lambda_penalty * sensitivity)
        
        # NCD Tiebreaker (Max 15%)
        ncd_val = self._ncd_score(prompt, answer)
        ncd_score = 1.0 - ncd_val # Convert distance to similarity
        
        # Final Aggregation
        # Weights: Computation 40%, Structural 30%, NCD 15%, Robustness modifier
        base_score = (comp_score * 0.4) + (struct_score * 0.3) + (ncd_score * 0.15)
        final_score = base_score * robustness_factor
        
        # Cap by meta confidence
        return min(final_score, meta_cap)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates and ranks candidate answers.
        Returns a list of dicts sorted by score descending.
        """
        results = []
        for cand in candidates:
            score = self.confidence(prompt, cand)
            # Generate reasoning string
            reasoning_parts = []
            if self._meta_confidence(prompt) < 0.5:
                reasoning_parts.append("Potential ambiguity or trap detected.")
            if self._constructive_compute(prompt, cand)[1]:
                reasoning_parts.append("Constructive computation verified.")
            else:
                reasoning_parts.append("Structural and heuristic analysis applied.")
                
            results.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": " ".join(reasoning_parts)
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results