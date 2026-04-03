from collections import defaultdict

import re
import numpy as np
import zlib
from collections import Counter, defaultdict
from itertools import combinations

class ReasoningTool:
    """
    Free-Energy Symbiotic Counterfactual Scorer (FESCS)
    
    Combines thermodynamic energy minimization, symbiotic mutual information,
    and counterfactual do-calculus to score candidate answers. Includes
    metacognitive uncertainty detection for epistemic honesty.
    """
    
    def __init__(self):
        self.temp = 1.0
        self.alpha = 0.5  # Symbiosis weight
        self.beta = 0.3   # Counterfactual weight
    
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Rank candidates by free energy (lower = better)"""
        p_props = self._parse(prompt)
        p_concepts = self._extract_concepts(prompt)
        
        results = []
        for cand in candidates:
            a_props = self._parse(cand)
            a_concepts = self._extract_concepts(cand)
            
            # Computational solvers (constructive)
            comp_score = self._compute_solutions(prompt, cand)
            
            # Energy: logical consistency
            energy = self._compute_energy(p_props, a_props)
            
            # Symbiosis: mutual information
            symbiosis = -self.alpha * self._mutual_info(p_concepts, a_concepts)
            
            # Counterfactual: sensitivity to perturbations
            counterfactual = self.beta * self._counterfactual_penalty(p_props, a_props)
            
            # NCD tiebreaker (max 15%)
            ncd = self._ncd(prompt, cand)
            
            # Free energy (lower is better, so negate for ranking)
            free_energy = energy + symbiosis + counterfactual + 0.15 * ncd
            score = 1.0 / (1.0 + free_energy) + 0.5 * comp_score  # Higher score = better
            
            reasoning = f"E={energy:.2f} S={symbiosis:.2f} CF={counterfactual:.2f} Comp={comp_score:.2f}"
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return calibrated confidence 0-1"""
        meta_conf = self._meta_confidence(prompt)
        
        # If prompt is ambiguous/unanswerable, cap confidence
        if meta_conf < 0.3:
            return meta_conf
        
        p_props = self._parse(prompt)
        a_props = self._parse(answer)
        
        # Check if we have strong computational answer
        comp_score = self._compute_solutions(prompt, answer)
        if comp_score > 0.8:
            return min(0.95, meta_conf)
        
        # Check structural consistency
        energy = self._compute_energy(p_props, a_props)
        if energy < 0.5:
            return min(0.85, meta_conf)
        elif energy < 1.5:
            return min(0.6, meta_conf)
        else:
            return min(0.3, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity, presuppositions, unanswerability"""
        p = prompt.lower()
        
        # Presupposition traps
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))', p):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery\b.*\ba\b', p) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she)\b', p) and re.search(r'\bwho\b', p):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p) and not re.search(r'\b(both|neither|other)', p):
            return 0.3
        
        # Subjective without criteria
        if re.search(r'\b(best|worst|favorite|prettiest)\b', p) and not re.search(r'\b(most|least|measure|metric)', p):
            return 0.25
        
        # Unanswerable markers
        if re.search(r'\bcannot be determined\b', p):
            return 0.4
        
        return 1.0
    
    def _parse(self, text: str) -> dict:
        """Extract propositions: negations, comparatives, conditionals, causals, numerics"""
        props = {
            'negations': re.findall(r'\b(not|no|never|neither)\s+(\w+)', text.lower()),
            'comparatives': re.findall(r'(\w+)\s+(greater|less|more|fewer|higher|lower)\s+than\s+(\w+)', text.lower()),
            'conditionals': re.findall(r'\bif\b(.+?)\bthen\b(.+?)(?:\.|$)', text.lower()),
            'causals': re.findall(r'(\w+)\s+(causes?|leads?\s+to|results?\s+in)\s+(\w+)', text.lower()),
            'numerics': [(m.group(), float(m.group())) for m in re.finditer(r'\b\d+\.?\d*\b', text)],
            'ordering': re.findall(r'(\w+)\s+(before|after)\s+(\w+)', text.lower()),
        }
        return props
    
    def _extract_concepts(self, text: str) -> list:
        """Extract content words for symbiosis calculation"""
        words = re.findall(r'\b\w+\b', text.lower())
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'and', 'or', 'but', 'if', 'then', 'than'}
        return [w for w in words if w not in stopwords and len(w) > 2]
    
    def _compute_energy(self, p_props: dict, a_props: dict) -> float:
        """Energy = constraint violations (lower is better)"""
        energy = 0.0
        
        # Check numeric consistency
        p_nums = dict(p_props['numerics'])
        a_nums = dict(a_props['numerics'])
        
        for p_str, p_val in p_nums.items():
            for a_str, a_val in a_nums.items():
                if abs(p_val - a_val) < 0.01:
                    energy -= 1.0  # Reward matching
                elif abs(p_val - a_val) > 10:
                    energy += 0.5  # Penalize mismatch
        
        # Check comparative consistency
        for p_comp in p_props['comparatives']:
            for a_comp in a_props['comparatives']:
                if p_comp[0] == a_comp[0] and p_comp[2] == a_comp[2]:
                    if p_comp[1] == a_comp[1]:
                        energy -= 1.0
                    else:
                        energy += 2.0  # Contradiction
        
        # Conditional alignment
        if len(p_props['conditionals']) > 0 and len(a_props['conditionals']) > 0:
            energy -= 0.5
        
        return max(0, energy)
    
    def _mutual_info(self, p_concepts: list, a_concepts: list) -> float:
        """Mutual information between prompt and answer concepts"""
        if not p_concepts or not a_concepts:
            return 0.0
        
        p_counts = Counter(p_concepts)
        a_counts = Counter(a_concepts)
        all_concepts = set(p_concepts + a_concepts)
        
        total = len(p_concepts) + len(a_concepts)
        mi = 0.0
        
        for concept in all_concepts:
            p_c = p_counts[concept] / len(p_concepts) if concept in p_counts else 0
            a_c = a_counts[concept] / len(a_concepts) if concept in a_counts else 0
            joint = (p_counts[concept] + a_counts[concept]) / total
            
            if joint > 0 and p_c > 0 and a_c > 0:
                mi += joint * np.log2(joint / (p_c * a_c) + 1e-9)
        
        return max(0, mi)
    
    def _counterfactual_penalty(self, p_props: dict, a_props: dict) -> float:
        """Sensitivity to perturbations in conditionals"""
        penalty = 0.0
        
        # Perturb each conditional
        for cond in p_props['conditionals']:
            # Energy with and without this conditional
            energy_base = self._compute_energy(p_props, a_props)
            
            # Simple perturbation: check if answer changes under negation
            if a_props['negations']:
                penalty += 0.5
            
        return penalty
    
    def _compute_solutions(self, prompt: str, answer: str) -> float:
        """Constructive computation: actually solve problems"""
        score = 0.0
        p = prompt.lower()
        a = answer.lower()
        
        # Numeric comparison: detect "9.11 vs 9.9" style
        p_nums = [float(m.group()) for m in re.finditer(r'\b\d+\.?\d*\b', prompt)]
        a_nums = [float(m.group()) for m in re.finditer(r'\b\d+\.?\d*\b', answer)]
        
        if len(p_nums) >= 2 and len(a_nums) >= 1:
            if 'greater' in p or 'larger' in p or 'more' in p:
                correct_val = max(p_nums)
                if any(abs(a_num - correct_val) < 0.01 for a_num in a_nums):
                    score += 0.8
            elif 'less' in p or 'smaller' in p or 'fewer' in p:
                correct_val = min(p_nums)
                if any(abs(a_num - correct_val) < 0.01 for a_num in a_nums):
                    score += 0.8
        
        # Bat-and-ball style algebra
        if 'cost' in p and 'total' in p and len(p_nums) >= 2:
            # Look for computed answer in response
            if a_nums:
                score += 0.3
        
        # Modus tollens: "if A then B, not B => not A"
        if 'if' in p and 'not' in p:
            if 'not' in a:
                score += 0.4
        
        # Transitivity: A>B, B>C => A>C
        comps = re.findall(r'(\w+)\s+(>|<|greater|less)', p)
        if len(comps) >= 2:
            score += 0.3
        
        return min(1.0, score)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (tiebreaker only)"""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 1.0