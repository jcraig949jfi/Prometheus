from typing import Dict, Optional, Tuple

"""
Falsification-Metamorphic Property Score (FMPS) Reasoning Tool

Combines Popperian falsificationism, metamorphic testing, and property-based testing
to evaluate logical consistency of candidate answers through structural parsing and
metamorphic relation validation.
"""

import re
import random
import zlib
from typing import List, Dict, Tuple, Optional
import numpy as np

class ReasoningTool:
    def __init__(self):
        self.n_tests_per_prop = 15
        random.seed(42)
        np.random.seed(42)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity/unanswerability patterns."""
        p_lower = prompt.lower()
        
        # Presupposition patterns
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop)|when did .+ stop)\b', p_lower):
            return 0.2
        
        # Scope ambiguity with "every"
        if re.search(r'\bevery \w+.*\b(a|an|the)\b', p_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she|they)\b.*\bwho\b', p_lower) or re.search(r'\bwho\b.*\b(he|she|they)\b', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .+ or .+\?', p_lower) and 'or neither' not in p_lower:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prettiest|ugliest)\b', p_lower) and not re.search(r'\b(according to|based on|measured by)\b', p_lower):
            return 0.3
        
        return 1.0
    
    def _parse_propositions(self, text: str) -> List[Tuple]:
        """Extract atomic propositions using regex."""
        props = []
        
        # Numeric comparatives: "X > Y", "A is greater than B", "5.2 < 10"
        for m in re.finditer(r'(\w+(?:\.\w+)?)\s*(?:is\s+)?(?:greater|more|larger|higher)\s+than\s+(\w+(?:\.\w+)?)', text, re.I):
            props.append(('GT', m.group(1), m.group(2)))
        for m in re.finditer(r'(\w+(?:\.\w+)?)\s*(?:is\s+)?(?:less|fewer|smaller|lower)\s+than\s+(\w+(?:\.\w+)?)', text, re.I):
            props.append(('LT', m.group(1), m.group(2)))
        for m in re.finditer(r'([\w.]+)\s*>\s*([\w.]+)', text):
            props.append(('GT', m.group(1), m.group(2)))
        for m in re.finditer(r'([\w.]+)\s*<\s*([\w.]+)', text):
            props.append(('LT', m.group(1), m.group(2)))
        for m in re.finditer(r'([\w.]+)\s*=\s*([\w.]+)', text):
            props.append(('EQ', m.group(1), m.group(2)))
        
        # Negations
        for m in re.finditer(r'\b(not|no|never)\s+(\w+)', text, re.I):
            props.append(('NOT', m.group(2)))
        
        # Conditionals
        for m in re.finditer(r'\bif\s+(.+?)\s+then\s+(.+?)(?:\.|,|$)', text, re.I):
            props.append(('IMPLIES', m.group(1).strip(), m.group(2).strip()))
        
        # Causals
        for m in re.finditer(r'(\w+)\s+(?:because|leads to|results in|causes)\s+(\w+)', text, re.I):
            props.append(('CAUSE', m.group(1), m.group(2)))
        
        return props if props else [('TRIVIAL', text[:20])]
    
    def _apply_metamorphic_relation(self, prop: Tuple) -> Optional[Tuple]:
        """Apply random metamorphic relation to a proposition."""
        ptype = prop[0]
        
        if ptype == 'GT' and len(prop) == 3:
            choice = random.choice(['swap', 'scale'])
            if choice == 'swap':
                return ('LT', prop[2], prop[1])
            else:  # numeric scaling
                return ('GT', prop[1], prop[2], random.uniform(0.5, 2.0))
        
        elif ptype == 'LT' and len(prop) == 3:
            choice = random.choice(['swap', 'scale'])
            if choice == 'swap':
                return ('GT', prop[2], prop[1])
            else:
                return ('LT', prop[1], prop[2], random.uniform(0.5, 2.0))
        
        elif ptype == 'NOT' and len(prop) == 2:
            return ('POS', prop[1])  # flip negation
        
        elif ptype == 'IMPLIES' and len(prop) == 3:
            # Contrapositive
            return ('IMPLIES', f"not {prop[2]}", f"not {prop[1]}")
        
        elif ptype == 'CAUSE' and len(prop) == 3:
            # Asymmetry violation check
            return ('CAUSE', prop[2], prop[1])
        
        return None
    
    def _verify_metamorphic_variant(self, original: Tuple, variant: Tuple, all_props: List[Tuple]) -> bool:
        """Check if metamorphic variant is consistent with original propositions."""
        if variant is None:
            return True
        
        vtype = variant[0]
        
        # Swapped comparatives should NOT appear in original set
        if vtype in ['GT', 'LT'] and len(variant) == 3:
            if vtype == 'GT':
                # If we swapped GT to LT, original should NOT contain this LT
                return ('LT', variant[1], variant[2]) not in all_props
            elif vtype == 'LT':
                return ('GT', variant[1], variant[2]) not in all_props
        
        # Flipped negations should NOT appear
        if vtype == 'POS' and len(variant) == 2:
            return ('NOT', variant[1]) not in all_props
        
        # Contrapositive should be valid if original IMPLIES is valid
        if vtype == 'IMPLIES':
            return True  # Contrapositive always valid
        
        # Reversed CAUSE should NOT appear (asymmetry)
        if vtype == 'CAUSE' and len(variant) == 3:
            return ('CAUSE', variant[1], variant[2]) not in all_props
        
        return True
    
    def _compute_fmps_score(self, text: str) -> float:
        """Compute Falsification-Metamorphic Property Score."""
        props = self._parse_propositions(text)
        if not props:
            return 0.5
        
        total_tests = 0
        falsifications = 0
        
        for prop in props:
            for _ in range(self.n_tests_per_prop):
                variant = self._apply_metamorphic_relation(prop)
                total_tests += 1
                
                if not self._verify_metamorphic_variant(prop, variant, props):
                    falsifications += 1
        
        if total_tests == 0:
            return 0.5
        
        score = 1.0 - (falsifications / total_tests)
        return max(0.0, min(1.0, score))
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by FMPS + NCD."""
        results = []
        
        for cand in candidates:
            fmps = self._compute_fmps_score(cand)
            ncd = 1.0 - self._ncd(prompt, cand)
            
            # 70% FMPS, 15% NCD, 15% length bonus
            len_score = min(1.0, len(cand.split()) / 20.0)
            final_score = 0.70 * fmps + 0.15 * ncd + 0.15 * len_score
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"FMPS={fmps:.2f}, NCD={ncd:.2f}, len={len_score:.2f}"
            })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-confidence."""
        meta_conf = self._meta_confidence(prompt)
        
        # If prompt is problematic, cap confidence low
        if meta_conf < 0.5:
            return meta_conf
        
        # Compute answer quality
        fmps = self._compute_fmps_score(answer)
        props = self._parse_propositions(answer)
        
        # No structure detected = low confidence
        if len(props) <= 1 and props[0][0] == 'TRIVIAL':
            return 0.3
        
        # Base confidence on FMPS and proposition count
        prop_conf = min(1.0, len(props) / 5.0)
        base_conf = 0.4 * fmps + 0.3 * prop_conf + 0.3
        
        # Cap by meta-confidence
        return min(base_conf, meta_conf, 0.85)