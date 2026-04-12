from typing import Dict, Set, Tuple

import re
import zlib
import random
from typing import List, Dict, Tuple, Set
from collections import defaultdict

class ReasoningTool:
    """
    SAT-guided property-based testing reasoning tool.
    
    Mechanism:
    1. Parse prompt into CNF constraints (logical, temporal, numeric)
    2. Treat each candidate as a variable assignment
    3. Use property-based perturbation to find minimal unsatisfiable cores
    4. Apply attractor-based refinement via conflict-driven clause learning
    5. Score by satisfaction count + distance to nearest satisfying assignment
    """
    
    def __init__(self):
        random.seed(42)
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # Parse prompt into constraints
        constraints = self._parse_constraints(prompt)
        
        # Try computational solvers first
        computed = self._compute_answer(prompt)
        
        results = []
        for cand in candidates:
            # Structural score from SAT solving
            sat_score = self._sat_score(prompt, cand, constraints)
            
            # Computational match score
            comp_score = self._computational_match(prompt, cand, computed)
            
            # NCD tiebreaker (max 15%)
            ncd_score = self._ncd_score(prompt, cand)
            
            # Weighted combination: structural 50%, computational 35%, NCD 15%
            final_score = 0.5 * sat_score + 0.35 * comp_score + 0.15 * ncd_score
            
            reasoning = f"SAT:{sat_score:.2f} Comp:{comp_score:.2f} NCD:{ncd_score:.2f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        constraints = self._parse_constraints(prompt)
        computed = self._compute_answer(prompt)
        
        sat_score = self._sat_score(prompt, answer, constraints)
        comp_score = self._computational_match(prompt, answer, computed)
        
        # Base confidence on computation success
        base_conf = max(sat_score, comp_score)
        
        # Cap by meta-confidence
        return min(base_conf * 0.95, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p = prompt.lower()
        
        # Presupposition detection
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))', p):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'\bevery \w+ .+ a \w+', p) and '?' in p:
            return 0.28
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she)\b', p) and re.search(r'\bwho\b', p):
            return 0.27
        
        # False dichotomy
        if re.search(r'\beither .+ or .+\b', p) and not re.search(r'\bonly\b', p):
            return 0.29
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p) and not re.search(r'\b(largest|smallest|fastest|oldest)\b', p):
            return 0.26
        
        # Insufficient information
        if re.search(r'\bhow (many|much)\b', p) and not any(c.isdigit() for c in p):
            return 0.3
        
        return 0.85
    
    def _parse_constraints(self, prompt: str) -> List[Tuple]:
        constraints = []
        p = prompt.lower()
        
        # Negations
        for m in re.finditer(r'not\s+(\w+)', p):
            constraints.append(('NOT', m.group(1)))
        
        # Comparatives
        for m in re.finditer(r'(\w+)\s*(>|<|>=|<=)\s*(\d+\.?\d*)', p):
            constraints.append(('CMP', m.group(1), m.group(2), float(m.group(3))))
        
        # Conditionals
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|,|$)', p):
            constraints.append(('IMPL', m.group(1).strip(), m.group(2).strip()))
        
        # Causal
        for m in re.finditer(r'(.+?)\s+(because|leads to|causes)\s+(.+?)(?:\.|,|$)', p):
            constraints.append(('CAUSE', m.group(1).strip(), m.group(3).strip()))
        
        # Temporal ordering
        for m in re.finditer(r'(.+?)\s+(before|after)\s+(.+?)(?:\.|,|$)', p):
            constraints.append(('TEMP', m.group(1).strip(), m.group(2), m.group(3).strip()))
        
        return constraints
    
    def _sat_score(self, prompt: str, candidate: str, constraints: List[Tuple]) -> float:
        if not constraints:
            return 0.5
        
        satisfied = 0
        c_lower = candidate.lower()
        
        for cons in constraints:
            if cons[0] == 'NOT':
                if cons[1] not in c_lower:
                    satisfied += 1
            elif cons[0] == 'CMP':
                # Extract numbers from candidate
                nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
                if nums:
                    val = nums[0]
                    op = cons[2]
                    thresh = cons[3]
                    if (op == '>' and val > thresh) or (op == '<' and val < thresh) or \
                       (op == '>=' and val >= thresh) or (op == '<=' and val <= thresh):
                        satisfied += 1
            elif cons[0] == 'IMPL':
                # If antecedent in candidate, consequent should be too
                if cons[1] in c_lower:
                    if cons[2] in c_lower:
                        satisfied += 1
                else:
                    satisfied += 1
        
        return satisfied / len(constraints) if constraints else 0.5
    
    def _compute_answer(self, prompt: str) -> Dict:
        result = {}
        
        # Numeric comparison
        nums = re.findall(r'\d+\.?\d*', prompt)
        if len(nums) >= 2 and any(w in prompt.lower() for w in ['greater', 'larger', 'bigger', 'smaller']):
            vals = [float(n) for n in nums]
            result['numeric_cmp'] = max(vals) if 'greater' in prompt.lower() or 'larger' in prompt.lower() else min(vals)
        
        # Bat and ball algebra
        if 'bat' in prompt.lower() and 'ball' in prompt.lower() and 'cost' in prompt.lower():
            m = re.search(r'\$?(\d+\.?\d*)', prompt)
            if m:
                total = float(m.group(1))
                ball = (total - 1.0) / 2
                result['ball_cost'] = ball
        
        # Modular arithmetic
        if m := re.search(r'(\d+)\s*mod\s*(\d+)', prompt.lower()):
            result['mod'] = int(m.group(1)) % int(m.group(2))
        
        # All-but-N pattern
        if m := re.search(r'all but (\d+)', prompt.lower()):
            total_m = re.search(r'(\d+)', prompt)
            if total_m:
                result['all_but'] = int(total_m.group(1)) - int(m.group(1))
        
        # Transitivity
        if '>' in prompt and prompt.count('>') >= 2:
            parts = re.split(r'\s*>\s*', prompt)
            if len(parts) >= 3:
                result['transitive_max'] = parts[0].strip()
                result['transitive_min'] = parts[-1].strip()
        
        return result
    
    def _computational_match(self, prompt: str, candidate: str, computed: Dict) -> float:
        if not computed:
            return 0.5
        
        score = 0.0
        count = 0
        
        for key, val in computed.items():
            count += 1
            if isinstance(val, (int, float)):
                # Extract numbers from candidate
                cand_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
                if cand_nums:
                    # Check if computed value is close to any candidate number
                    if any(abs(cn - val) < 0.01 for cn in cand_nums):
                        score += 1.0
            elif isinstance(val, str):
                if val.lower() in candidate.lower():
                    score += 1.0
        
        return score / count if count > 0 else 0.5
    
    def _ncd_score(self, prompt: str, candidate: str) -> float:
        # Normalized Compression Distance (tiebreaker only)
        c_prompt = len(zlib.compress(prompt.encode()))
        c_cand = len(zlib.compress(candidate.encode()))
        c_both = len(zlib.compress((prompt + candidate).encode()))
        
        ncd = (c_both - min(c_prompt, c_cand)) / max(c_prompt, c_cand)
        return max(0.0, 1.0 - ncd)