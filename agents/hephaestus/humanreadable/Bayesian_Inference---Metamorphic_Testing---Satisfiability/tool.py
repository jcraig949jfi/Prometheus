from typing import Dict, Set, Tuple

"""
Bayesian-Metamorphic Constraint Scorer (BMCS)

Combines SAT-based constraint extraction, Bayesian belief updating, and 
metamorphic testing to score candidate answers. Emphasizes epistemic honesty
by detecting ambiguity, presuppositions, and unanswerable questions.
"""

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    def __init__(self):
        self.prior_default = 0.5
        self.mr_likelihood_both = 1.0
        self.mr_likelihood_one = 0.01
        self.mr_likelihood_none = 0.0001
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by Bayesian-metamorphic score."""
        results = []
        meta_conf = self._meta_confidence(prompt)
        
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            conf = min(meta_conf, self._compute_confidence(prompt, cand, score))
            reasoning = self._explain_score(prompt, cand, score, meta_conf)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-confidence."""
        meta_conf = self._meta_confidence(prompt)
        score = self._score_candidate(prompt, answer)
        base_conf = self._compute_confidence(prompt, answer, score)
        return min(meta_conf, base_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Evaluate PROMPT for ambiguity/presupposition patterns."""
        p_lower = prompt.lower()
        
        # Presupposition patterns
        presup_patterns = [
            r'\b(have you|did you|has .+) (stop|quit|cease)',
            r'\bwhy (did|does|is) .+ (fail|stop|wrong)',
            r'\bwhen (did|will) .+ (stop|start|begin)',
        ]
        for pat in presup_patterns:
            if re.search(pat, p_lower):
                return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery .+ (has|did|does|made) a\b', p_lower):
            if '?' in prompt and 'same' in p_lower:
                return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p_lower):
            if re.search(r'\b(who|which one|whom)\b', p_lower):
                return 0.25
        
        # False dichotomy: "either A or B"
        if re.search(r'\beither .+ or .+[?\.]', p_lower):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|better|worse)\b', p_lower):
            if not re.search(r'\b(most|least|more|less|higher|lower)\b', p_lower):
                return 0.3
        
        # Unanswerability cues
        if re.search(r'\b(impossible to know|cannot determine|insufficient information)\b', p_lower):
            return 0.2
        
        # Multiple questions
        if prompt.count('?') > 1:
            return 0.4
        
        return 1.0  # No meta-issues detected
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        """Compute Bayesian-metamorphic score."""
        # Parse prompt and candidate
        p_props = self._parse_propositions(prompt)
        c_props = self._parse_propositions(candidate)
        
        # Numeric comparison check
        num_score = self._numeric_eval(prompt, candidate)
        if num_score is not None:
            return num_score
        
        # Structural consistency
        struct_score = self._structural_consistency(p_props, c_props, prompt, candidate)
        
        # Metamorphic relations
        mr_score = self._metamorphic_score(prompt, candidate)
        
        # NCD tiebreaker (max 15%)
        ncd = self._ncd(prompt, candidate)
        ncd_score = 1.0 - ncd
        
        # Weighted combination
        final = 0.5 * struct_score + 0.35 * mr_score + 0.15 * ncd_score
        return np.clip(final, 0.0, 1.0)
    
    def _parse_propositions(self, text: str) -> Dict:
        """Extract structural features."""
        t_lower = text.lower()
        props = {
            'negations': len(re.findall(r'\b(not|no|never|neither|nor)\b', t_lower)),
            'comparatives': re.findall(r'(\d+\.?\d*)\s*(>|<|>=|<=|=|equals?)\s*(\d+\.?\d*)', t_lower),
            'conditionals': len(re.findall(r'\b(if|then|when|unless|implies)\b', t_lower)),
            'causal': len(re.findall(r'\b(because|since|leads to|results in|causes)\b', t_lower)),
            'ordering': re.findall(r'\b(before|after|first|last|earlier|later)\b', t_lower),
            'quantifiers': len(re.findall(r'\b(all|every|some|none|any|each)\b', t_lower)),
            'numbers': [float(x) for x in re.findall(r'\b\d+\.?\d*\b', t_lower)],
        }
        return props
    
    def _numeric_eval(self, prompt: str, candidate: str) -> float:
        """Handle numeric comparison questions."""
        # Extract comparison pattern
        comp_match = re.search(r'(\d+\.?\d*)\s+(>|<|greater|less|larger|smaller)\s+(\d+\.?\d*)', prompt.lower())
        if not comp_match:
            return None
        
        n1_str, op, n2_str = comp_match.groups()
        n1 = float(n1_str) if '.' in n1_str else float(n1_str)
        n2 = float(n2_str) if '.' in n2_str else float(n2_str)
        
        # Determine correct answer
        if op in ['>', 'greater', 'larger']:
            correct = n1 > n2
        else:
            correct = n1 < n2
        
        # Match candidate
        c_lower = candidate.lower()
        if 'yes' in c_lower or 'true' in c_lower or 'correct' in c_lower:
            return 0.95 if correct else 0.05
        elif 'no' in c_lower or 'false' in c_lower or 'incorrect' in c_lower:
            return 0.05 if correct else 0.95
        
        return None
    
    def _structural_consistency(self, p_props: Dict, c_props: Dict, prompt: str, candidate: str) -> float:
        """Check logical consistency between prompt and candidate."""
        score = 0.5
        
        # Negation handling
        if 'not' in prompt.lower() and 'not' in candidate.lower():
            score += 0.2
        elif 'not' in prompt.lower() and 'yes' in candidate.lower():
            score -= 0.3
        
        # Quantifier agreement
        if p_props['quantifiers'] > 0 and c_props['quantifiers'] > 0:
            score += 0.15
        
        # Conditional structure
        if p_props['conditionals'] > 0:
            if 'if' in prompt.lower() and 'then' in candidate.lower():
                score += 0.2
        
        # Number presence
        if len(p_props['numbers']) > 0 and len(c_props['numbers']) > 0:
            if any(n in p_props['numbers'] for n in c_props['numbers']):
                score += 0.15
        
        return np.clip(score, 0.0, 1.0)
    
    def _metamorphic_score(self, prompt: str, candidate: str) -> float:
        """Apply metamorphic transformations and check consistency."""
        original_sat = self._check_sat(prompt, candidate)
        
        # MR1: Negate and check flip
        neg_prompt = self._negate_conditionals(prompt)
        neg_sat = self._check_sat(neg_prompt, candidate)
        
        # MR2: Swap symmetric elements
        swap_prompt = self._swap_symmetric(prompt)
        swap_sat = self._check_sat(swap_prompt, candidate)
        
        # Count satisfied MRs
        mr_count = 0
        total_mr = 0
        
        if neg_prompt != prompt:
            total_mr += 1
            if original_sat != neg_sat:  # Should flip
                mr_count += 1
        
        if swap_prompt != prompt:
            total_mr += 1
            if swap_sat == original_sat:  # Should stay same
                mr_count += 1
        
        if total_mr == 0:
            return 0.5
        
        return mr_count / total_mr
    
    def _check_sat(self, prompt: str, candidate: str) -> bool:
        """Simplified SAT check for consistency."""
        combined = prompt.lower() + ' ' + candidate.lower()
        
        # Check for obvious contradictions
        if 'not' in combined and 'yes' in candidate.lower():
            if 'is not' in prompt.lower() or 'not true' in prompt.lower():
                return False
        
        return True
    
    def _negate_conditionals(self, text: str) -> str:
        """MR: Negate conditionals."""
        text = re.sub(r'\bis\s+', 'is not ', text)
        text = re.sub(r'\bare\s+', 'are not ', text)
        return text
    
    def _swap_symmetric(self, text: str) -> str:
        """MR: Swap symmetric numeric inputs."""
        numbers = re.findall(r'\b\d+\.?\d*\b', text)
        if len(numbers) >= 2:
            text = text.replace(numbers[0], '__TEMP__', 1)
            text = text.replace(numbers[1], numbers[0], 1)
            text = text.replace('__TEMP__', numbers[1], 1)
        return text
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _compute_confidence(self, prompt: str, answer: str, score: float) -> float:
        """Compute confidence based on score and structural certainty."""
        # Never exceed 0.9 unless definitive computation
        p_props = self._parse_propositions(prompt)
        
        # High confidence if numeric evaluation succeeded
        if len(p_props['comparatives']) > 0 and score > 0.9:
            return 0.88
        
        # Medium confidence for structural match
        if score > 0.7:
            return 0.65
        elif score > 0.5:
            return 0.5
        else:
            return 0.3
    
    def _explain_score(self, prompt: str, candidate: str, score: float, meta_conf: float) -> str:
        """Generate reasoning explanation."""
        if meta_conf < 0.5:
            return f"Low confidence due to ambiguity/presupposition in prompt (meta={meta_conf:.2f})"
        
        p_props = self._parse_propositions(prompt)
        if len(p_props['comparatives']) > 0:
            return f"Numeric comparison detected, score={score:.2f}"
        
        return f"Structural+metamorphic score={score:.2f}, meta={meta_conf:.2f}"