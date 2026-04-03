from typing import Dict, Set, Tuple

"""
Gauge-Theoretic Free Energy Reasoning Tool

Parses questions into constraint graphs, evaluates candidates via variational free energy
(prediction error - entropy), and evolves lexical variations through gauge connections.
"""

import re
import numpy as np
from typing import List, Dict, Tuple, Set
import zlib

class ReasoningTool:
    def __init__(self):
        # Gauge connection: synonym table (fiber bundle over predicates)
        self.synonyms = {
            'larger': ['bigger', 'greater', 'more', 'larger'],
            'smaller': ['lesser', 'fewer', 'smaller', 'less'],
            'cause': ['leads to', 'results in', 'produces', 'cause'],
            'equal': ['same', 'identical', 'equal', 'equivalent'],
            'true': ['yes', 'correct', 'true', 'right'],
            'false': ['no', 'incorrect', 'false', 'wrong']
        }
        self.tau = 1.0  # Temperature for free energy
    
    def _extract_constraints(self, text: str) -> Dict:
        """Parse text into logical constraints (DAG base space)"""
        constraints = {
            'negations': [],
            'comparatives': [],
            'conditionals': [],
            'causal': [],
            'numeric': [],
            'ordering': [],
            'quantifiers': []
        }
        
        # Negations
        if re.search(r'\b(not|no|never|none)\b', text, re.I):
            constraints['negations'].append(re.findall(r'\b(not|no|never|none)\s+(\w+)', text, re.I))
        
        # Numeric comparisons
        nums = re.findall(r'\b(\d+\.?\d*)\b', text)
        constraints['numeric'] = [float(n) for n in nums]
        
        # Comparatives
        comp_matches = re.findall(r'(\w+)\s+(more|less|greater|smaller|larger)\s+than\s+(\w+)', text, re.I)
        constraints['comparatives'] = comp_matches
        
        # Ordering relations
        ord_matches = re.findall(r'(\w+)\s+(>|<|>=|<=|at least|at most)\s+(\w+)', text, re.I)
        constraints['ordering'] = ord_matches
        
        # Conditionals
        if re.search(r'\bif\b.*\bthen\b', text, re.I):
            cond = re.findall(r'if\s+(.*?)\s+then\s+(.*?)(?:\.|$)', text, re.I)
            constraints['conditionals'] = cond
        
        # Causal
        causal = re.findall(r'(\w+)\s+(because|leads to|causes|results in)\s+(\w+)', text, re.I)
        constraints['causal'] = causal
        
        # Quantifiers
        quant = re.findall(r'\b(all|some|every|each|none)\s+(\w+)', text, re.I)
        constraints['quantifiers'] = quant
        
        return constraints
    
    def _compute_prediction_error(self, candidate: str, constraints: Dict) -> float:
        """Compute how many constraints the candidate violates"""
        error = 0.0
        cand_lower = candidate.lower()
        
        # Check numeric constraints
        cand_nums = [float(n) for n in re.findall(r'\b(\d+\.?\d*)\b', candidate)]
        if constraints['numeric'] and cand_nums:
            # Numeric consistency check
            if not any(abs(cn - pn) < 0.01 for cn in cand_nums for pn in constraints['numeric']):
                error += 2.0
        
        # Check negations
        for neg_group in constraints['negations']:
            for neg_word, target in neg_group:
                if neg_word.lower() in ['not', 'no', 'never', 'none']:
                    if target.lower() in cand_lower:
                        error += 3.0  # High weight for negation violations
        
        # Check comparatives (transitivity)
        for a, rel, b in constraints['comparatives']:
            if rel.lower() in ['more', 'greater', 'larger']:
                if b.lower() in cand_lower and a.lower() not in cand_lower:
                    error += 1.5
        
        # Check causal claims
        for cause, relation, effect in constraints['causal']:
            if effect.lower() in cand_lower and cause.lower() not in cand_lower:
                error += 2.0
        
        return error
    
    def _compute_entropy(self, candidate: str) -> float:
        """Compute entropy over lexical fiber choices"""
        words = candidate.lower().split()
        entropy = 0.0
        for word in words:
            # Check if word has synonyms in our gauge connection
            for base, syns in self.synonyms.items():
                if word in syns:
                    prob = 1.0 / len(syns)
                    entropy -= prob * np.log(prob + 1e-10)
        return entropy
    
    def _free_energy(self, candidate: str, constraints: Dict) -> float:
        """Variational free energy: F = E - tau * H"""
        error = self._compute_prediction_error(candidate, constraints)
        entropy = self._compute_entropy(candidate)
        return error - self.tau * entropy
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (tiebreaker only)"""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2)
    
    def _compute_answer(self, prompt: str) -> str:
        """Actually COMPUTE answers for known problem types"""
        p = prompt.lower()
        
        # Numeric comparison: "9.11 vs 9.9"
        nums = re.findall(r'\b(\d+\.?\d*)\b', prompt)
        if len(nums) == 2 and ('larger' in p or 'greater' in p or 'more' in p):
            return str(max(float(nums[0]), float(nums[1])))
        if len(nums) == 2 and ('smaller' in p or 'less' in p or 'fewer' in p):
            return str(min(float(nums[0]), float(nums[1])))
        
        # Bat-and-ball algebra: "total $X, one costs $Y more"
        if 'cost' in p and 'more than' in p:
            match = re.search(r'total.*?\$?(\d+\.?\d*)', p)
            match2 = re.search(r'\$?(\d+\.?\d*).*?more', p)
            if match and match2:
                total, diff = float(match.group(1)), float(match2.group(1))
                cheaper = (total - diff) / 2
                return f"${cheaper:.2f}"
        
        # All-but-N: "12 people, all but 5 left"
        match = re.search(r'(\d+).*?all but (\d+)', p, re.I)
        if match:
            total, remaining = int(match.group(1)), int(match.group(2))
            return str(remaining)
        
        # Transitivity: A > B, B > C => A > C
        trans = re.findall(r'(\w+)\s*>\s*(\w+)', p)
        if len(trans) >= 2:
            # Build ordering chain
            order = []
            for a, b in trans:
                if a not in order:
                    order.append(a)
                if b not in order:
                    order.append(b)
            return order[0] if order else ""
        
        return ""
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity/presupposition/unanswerability"""
        p = prompt.lower()
        
        # Presupposition: "Have you stopped X?"
        if re.search(r'\b(have you|did you)\s+(stop|quit|cease)', p):
            return 0.2
        
        # Presupposition: "Why did X fail/stop?"
        if re.search(r'\bwhy (did|does|is).*?(fail|wrong|stop)', p):
            return 0.25
        
        # Scope ambiguity: "Every X ... a Y"
        if re.search(r'\bevery\b.*?\ba\b', p):
            return 0.3
        
        # Pronoun ambiguity with "who" question
        if 'who' in p and re.search(r'\b(he|she|they)\b', p):
            return 0.3
        
        # False dichotomy: "Either A or B"
        if re.search(r'\beither\b.*?\bor\b', p) and 'only' not in p:
            return 0.35
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p) and 'most' not in p:
            return 0.4
        
        # Insufficient information
        if 'impossible to' in p or 'cannot determine' in p or 'not enough' in p:
            return 0.2
        
        return 1.0  # No ambiguity detected
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate candidates via free energy and computation"""
        constraints = self._extract_constraints(prompt)
        computed = self._compute_answer(prompt)
        
        results = []
        for cand in candidates:
            # Free energy score (main signal)
            fe = self._free_energy(cand, constraints)
            fe_score = 1.0 / (1.0 + fe)  # Normalize: lower FE = higher score
            
            # Computational match bonus
            comp_bonus = 0.0
            if computed and computed.lower() in cand.lower():
                comp_bonus = 0.3
            
            # NCD tiebreaker (max 15%)
            ncd = self._ncd(prompt, cand)
            ncd_score = (1.0 - ncd) * 0.15
            
            # Final score: 60% FE + 30% computation + 10% NCD
            score = 0.6 * fe_score + 0.3 * comp_bonus + 0.1 * ncd_score
            
            results.append({
                'candidate': cand,
                'score': score,
                'reasoning': f"FE={fe:.2f}, Computed={computed}, Violations={self._compute_prediction_error(cand, constraints):.1f}"
            })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on question properties"""
        meta_conf = self._meta_confidence(prompt)
        
        if meta_conf < 0.5:
            return meta_conf  # Cap confidence on ambiguous questions
        
        constraints = self._extract_constraints(prompt)
        computed = self._compute_answer(prompt)
        
        # High confidence if we computed an answer and it matches
        if computed and computed.lower() in answer.lower():
            return min(0.85, meta_conf)  # Never exceed 0.9 unless perfect
        
        # Medium confidence if constraints are satisfied
        error = self._compute_prediction_error(answer, constraints)
        if error < 0.5:
            return min(0.7, meta_conf)
        
        # Low confidence otherwise
        return min(0.4, meta_conf)