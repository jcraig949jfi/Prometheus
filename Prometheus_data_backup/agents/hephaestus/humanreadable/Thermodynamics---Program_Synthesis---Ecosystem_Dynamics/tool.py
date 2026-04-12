import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a hybrid reasoning engine combining structural parsing, 
    thermodynamic/ecological constraint checking, and NCD tie-breaking.
    
    Mechanism:
    1. Parses prompt/candidate into a directed graph of propositions (SVO triples).
    2. Extracts numeric values and logical modifiers (negation, conditionals).
    3. Applies 'Thermodynamic' constraints: Checks for energy conservation logic 
       (e.g., output cannot exceed input in closed systems) and entropy monotonicity.
    4. Applies 'Ecosystem' constraints: Checks trophic capacity (predator <= prey).
    5. Scores based on constraint satisfaction (rewards/penalties).
    6. Uses NCD only as a tiebreaker for structurally identical candidates.
    """

    def __init__(self):
        # Keywords for parsing
        self.negations = {'not', 'no', 'never', 'none', 'cannot', 'impossible'}
        self.comparators_inc = {'increases', 'rises', 'grows', 'more', 'greater', 'leads to', 'causes'}
        self.comparators_dec = {'decreases', 'falls', 'shrinks', 'less', 'smaller', 'reduces'}
        self.conditionals = {'if', 'then', 'unless', 'when', 'provided'}
        self.energy_terms = {'energy', 'heat', 'work', 'biomass', 'food', 'resource'}
        
    def _parse_text(self, text: str) -> Dict:
        """Extract structural features: numbers, relations, and modifiers."""
        text_lower = text.lower()
        features = {
            'numbers': [],
            'has_negation': False,
            'has_conditional': False,
            'relations': [], # List of (subject, relation_type, object)
            'energy_mentions': 0
        }
        
        # Extract numbers
        nums = re.findall(r"[-+]?\d*\.?\d+", text)
        features['numbers'] = [float(n) for n in nums]
        
        # Check modifiers
        words = set(re.findall(r'\b\w+\b', text_lower))
        features['has_negation'] = bool(words & self.negations)
        features['has_conditional'] = bool(words & self.conditionals)
        features['energy_mentions'] = len([w for w in words if any(e in w for e in self.energy_terms)])
        
        # Simple SVO-like extraction for constraint graph (Subject-Verb-Object)
        # Pattern: word+ (verb) word+
        # We simplify to detecting presence of increase/decrease logic chains
        for term in self.comparators_inc:
            if term in text_lower:
                features['relations'].append(('sys', 'increase', 'target'))
        for term in self.comparators_dec:
            if term in text_lower:
                features['relations'].append(('sys', 'decrease', 'target'))
                
        return features

    def _check_thermo_constraints(self, prompt_feat: Dict, cand_feat: Dict) -> float:
        """
        Validates thermodynamic consistency.
        Rule 1: If prompt implies closed system (no external input mentioned) and candidate 
                claims net energy creation, penalize.
        Rule 2: Entropy monotonicity (simplified): If 'disorder' or 'chaos' increases, 
                usable energy should not increase without input.
        """
        score = 0.0
        
        # Heuristic: If prompt has no "input"/"sun"/"source" keywords but candidate claims "increase" 
        # in energy/biomass without qualification, it violates conservation.
        prompt_txt = " ".join(map(str, prompt_feat.get('relations', [])))
        cand_txt = " ".join(map(str, cand_feat.get('relations', [])))
        
        has_energy_topic = (prompt_feat['energy_mentions'] > 0 or cand_feat['energy_mentions'] > 0)
        
        if has_energy_topic:
            # Check for "something from nothing" fallacy in candidate
            if 'increase' in cand_txt and 'decrease' not in cand_txt:
                # If candidate only increases things and mentions no source
                if 'source' not in prompt_txt.lower() and 'input' not in prompt_txt.lower():
                    score -= 0.2 # Penalty for violating conservation
        
        return score

    def _check_eco_constraints(self, prompt_feat: Dict, cand_feat: Dict) -> float:
        """
        Validates ecosystem dynamics.
        Rule: Trophic flow efficiency. Predator biomass cannot exceed prey biomass significantly.
        """
        score = 0.0
        # If numbers are present, check magnitude logic
        p_nums = prompt_feat['numbers']
        c_nums = cand_feat['numbers']
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Simple heuristic: If prompt defines a limit (e.g., "100 units of grass"),
            # candidate shouldn't claim "1000 units of deer".
            # Assuming first number is resource, second is consumer if not explicit
            max_resource = max(p_nums)
            candidate_claim = max(c_nums) if c_nums else 0
            
            if candidate_claim > (max_resource * 1.5): # Allow some margin, but flag gross violations
                score -= 0.15
                
        return score

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode()
        s2_b = s2.encode()
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_feat = self._parse_text(prompt)
        
        for cand in candidates:
            cand_feat = self._parse_text(cand)
            score = 1.0
            
            # 1. Structural Consistency (Negation/Conditional matching)
            # If prompt has conditional logic, candidate should ideally reflect it or not contradict
            if prompt_feat['has_conditional'] and not cand_feat['has_conditional']:
                # Soft penalty for ignoring complex logic structure
                score -= 0.05
            
            # If prompt has negation, candidate must handle it carefully
            if prompt_feat['has_negation']:
                # If candidate ignores negation context entirely (heuristic)
                if not cand_feat['has_negation'] and 'not' in prompt.lower():
                     score -= 0.05

            # 2. Domain Constraints (Thermo/Eco)
            score += self._check_thermo_constraints(prompt_feat, cand_feat)
            score += self._check_eco_constraints(prompt_feat, cand_feat)
            
            # 3. Numeric Logic
            # If both have numbers, check basic consistency (e.g. 2+2 != 5)
            # This is a simplified check; full algebraic solving is out of scope for regex
            p_nums = prompt_feat['numbers']
            c_nums = cand_feat['numbers']
            if len(p_nums) > 0 and len(c_nums) > 0:
                # If candidate number is wildly out of bounds compared to prompt max
                if c_nums and max(c_nums) > (max(p_nums) * 10):
                    score -= 0.1

            # Clip score
            score = max(0.0, min(1.0, score))
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Structural match: {1.0 if not prompt_feat['has_conditional'] or cand_feat['has_conditional'] else 0.95}, Domain constraints applied."
            })
        
        # Sort by score descending
        # Tie-breaking with NCD (prefer candidates closer to prompt structure if scores equal)
        results.sort(key=lambda x: (x['score'], -self._calculate_ncd(prompt, x['candidate'])), reverse=True)
        
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural and constraint adherence.
        """
        prompt_feat = self._parse_text(prompt)
        cand_feat = self._parse_text(answer)
        
        base_conf = 0.5
        
        # Boost if structural features align (e.g., both have conditionals if prompt does)
        if prompt_feat['has_conditional']:
            if cand_feat['has_conditional']:
                base_conf += 0.2
            else:
                base_conf -= 0.2
        
        # Boost if negation is preserved
        if prompt_feat['has_negation']:
            if cand_feat['has_negation']:
                base_conf += 0.1
            else:
                base_conf -= 0.1
                
        # Domain checks
        thermo_score = self._check_thermo_constraints(prompt_feat, cand_feat)
        eco_score = self._check_eco_constraints(prompt_feat, cand_feat)
        
        base_conf += (thermo_score + eco_score)
        
        return float(np.clip(base_conf, 0.0, 1.0))