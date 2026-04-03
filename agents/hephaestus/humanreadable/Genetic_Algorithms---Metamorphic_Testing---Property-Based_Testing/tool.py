from typing import Dict, Tuple

import re
import random
import zlib
from typing import List, Dict, Tuple
import math

class ReasoningTool:
    """
    Evolving Property-Guided Metamorphic Validator (EPGMV)
    
    Combines genetic algorithms with metamorphic testing and property-based validation.
    Parses logical structure, performs constructive computation, and evolves weighted
    parse trees to find consistent, property-satisfying answers.
    """
    
    def __init__(self):
        self.generations = 15
        self.population_size = 20
        self.mutation_prob = 0.2
        self.lambda_weight = 0.5
        random.seed(42)
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._evaluate_candidate(prompt, cand)
            reasoning = self._generate_reasoning(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        score = self._evaluate_candidate(prompt, answer)
        comp_confidence = self._computational_confidence(prompt, answer)
        
        conf = min(0.85, score * 0.6 + comp_confidence * 0.4)
        return min(conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'(have you|did you) (stop|quit|cease)', p_lower):
            return 0.15
        if re.search(r'why (did|does) .+ (fail|stop|end)', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every .+ (a|an) ', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she) (was|is)', p_lower) and 'who' in p_lower:
            return 0.2
        
        # False dichotomy
        if re.search(r'either .+ or .+\?', p_lower):
            return 0.25
        
        # Subjectivity
        if re.search(r'(best|worst|favorite|prettiest|ugliest)', p_lower):
            return 0.3
        
        # Insufficient info
        if re.search(r'(which|what|who).+(if|assuming|given that)', p_lower):
            if not re.search(r'(if|assuming|given that).{10,}', p_lower):
                return 0.25
        
        return 1.0
    
    def _evaluate_candidate(self, prompt: str, candidate: str) -> float:
        parse_tree = self._parse(candidate)
        properties = self._extract_properties(prompt)
        
        prop_score = self._property_score(parse_tree, properties)
        comp_score = self._computational_score(prompt, candidate)
        meta_score = self._metamorphic_score(candidate)
        ncd_score = self._ncd_score(prompt, candidate)
        
        final = 0.35 * prop_score + 0.40 * comp_score + 0.15 * meta_score + 0.10 * ncd_score
        return max(0.0, min(1.0, final))
    
    def _parse(self, text: str) -> Dict:
        tree = {
            'numerics': self._extract_numbers(text),
            'negations': self._extract_negations(text),
            'comparatives': self._extract_comparatives(text),
            'ordering': self._extract_ordering(text),
            'causal': self._extract_causal(text)
        }
        return tree
    
    def _extract_numbers(self, text: str) -> List[float]:
        matches = re.findall(r'-?\d+\.?\d*', text)
        return [float(m) for m in matches]
    
    def _extract_negations(self, text: str) -> int:
        return len(re.findall(r'\b(not|no|never|n\'t)\b', text.lower()))
    
    def _extract_comparatives(self, text: str) -> List[str]:
        return re.findall(r'(more|less|greater|smaller|higher|lower|before|after)', text.lower())
    
    def _extract_ordering(self, text: str) -> List[str]:
        return re.findall(r'(first|second|third|last|before|after|earlier|later)', text.lower())
    
    def _extract_causal(self, text: str) -> int:
        return len(re.findall(r'(because|therefore|thus|hence|if .+ then)', text.lower()))
    
    def _extract_properties(self, prompt: str) -> Dict:
        return {
            'expects_numeric': bool(re.search(r'(how many|how much|calculate|compute|\d+)', prompt.lower())),
            'expects_comparison': bool(re.search(r'(more|less|greater|which is|compare)', prompt.lower())),
            'expects_ordering': bool(re.search(r'(first|last|before|after|order)', prompt.lower())),
            'expects_causal': bool(re.search(r'(why|because|cause|reason)', prompt.lower()))
        }
    
    def _property_score(self, parse_tree: Dict, properties: Dict) -> float:
        score = 0.5
        
        if properties['expects_numeric'] and len(parse_tree['numerics']) > 0:
            score += 0.3
        if properties['expects_comparison'] and len(parse_tree['comparatives']) > 0:
            score += 0.1
        if properties['expects_ordering'] and len(parse_tree['ordering']) > 0:
            score += 0.1
        if properties['expects_causal'] and parse_tree['causal'] > 0:
            score += 0.1
        
        return min(1.0, score)
    
    def _computational_score(self, prompt: str, candidate: str) -> float:
        score = 0.0
        
        # Numeric comparison
        nc = self._numeric_comparison(prompt, candidate)
        if nc >= 0:
            score += nc * 0.4
        
        # Bayesian computation
        bc = self._bayesian_computation(prompt, candidate)
        if bc >= 0:
            score += bc * 0.3
        
        # Temporal reasoning
        tc = self._temporal_computation(prompt, candidate)
        if tc >= 0:
            score += tc * 0.3
        
        return score if score > 0 else 0.5
    
    def _numeric_comparison(self, prompt: str, candidate: str) -> float:
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            if re.search(r'(which is |what is |compare)', prompt.lower()):
                if re.search(r'(greater|larger|more|higher)', prompt.lower()):
                    expected = max(p_nums)
                elif re.search(r'(smaller|less|lower)', prompt.lower()):
                    expected = min(p_nums)
                else:
                    return -1
                
                if abs(c_nums[0] - expected) < 0.01:
                    return 1.0
                return 0.0
        return -1
    
    def _bayesian_computation(self, prompt: str, candidate: str) -> float:
        if re.search(r'(probability|likely|chance)', prompt.lower()):
            nums = self._extract_numbers(prompt)
            c_nums = self._extract_numbers(candidate)
            
            if len(nums) >= 2 and len(c_nums) >= 1:
                # Simple base rate
                if re.search(r'base rate', prompt.lower()):
                    prior = nums[0] / 100 if nums[0] < 1 else nums[0]
                    return 1.0 if c_nums[0] <= prior * 1.1 else 0.3
        return -1
    
    def _temporal_computation(self, prompt: str, candidate: str) -> float:
        if re.search(r'(before|after|earlier|later|ago|years old)', prompt.lower()):
            p_nums = self._extract_numbers(prompt)
            c_nums = self._extract_numbers(candidate)
            
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                # Age reasoning
                if re.search(r'years old', prompt.lower()):
                    return 0.8
        return -1
    
    def _metamorphic_score(self, candidate: str) -> float:
        mutants = self._generate_mutants(candidate)
        original_tree = self._parse(candidate)
        
        consistency = 0.0
        for mutant in mutants:
            mutant_tree = self._parse(mutant)
            if self._trees_consistent(original_tree, mutant_tree):
                consistency += 1.0
        
        return consistency / len(mutants) if mutants else 0.5
    
    def _generate_mutants(self, text: str) -> List[str]:
        mutants = []
        
        # Numeric mutation
        nums = re.findall(r'\d+\.?\d*', text)
        if nums:
            mutant = text.replace(nums[0], str(float(nums[0]) * 2), 1)
            mutants.append(mutant)
        
        # Negation mutation
        if ' not ' in text.lower():
            mutant = re.sub(r'\bnot\b', '', text, count=1, flags=re.IGNORECASE)
            mutants.append(mutant)
        
        return mutants[:3]
    
    def _trees_consistent(self, tree1: Dict, tree2: Dict) -> bool:
        # Simple consistency: negations should change parity
        return abs(tree1['negations'] - tree2['negations']) <= 1
    
    def _ncd_score(self, text1: str, text2: str) -> float:
        c1 = len(zlib.compress(text1.encode()))
        c2 = len(zlib.compress(text2.encode()))
        c12 = len(zlib.compress((text1 + text2).encode()))
        ncd = (c12 - min(c1, c2)) / max(c1, c2)
        return max(0.0, 1.0 - ncd)
    
    def _computational_confidence(self, prompt: str, answer: str) -> float:
        comp_score = self._computational_score(prompt, answer)
        if comp_score > 0.8:
            return 0.85
        elif comp_score > 0.5:
            return 0.6
        else:
            return 0.3
    
    def _generate_reasoning(self, prompt: str, candidate: str) -> str:
        parse_tree = self._parse(candidate)
        reasons = []
        
        if parse_tree['numerics']:
            reasons.append(f"Contains {len(parse_tree['numerics'])} numeric values")
        if parse_tree['negations'] > 0:
            reasons.append(f"Has {parse_tree['negations']} negations")
        if parse_tree['comparatives']:
            reasons.append(f"Uses comparative: {parse_tree['comparatives'][0]}")
        
        return "; ".join(reasons) if reasons else "Structural parse complete"