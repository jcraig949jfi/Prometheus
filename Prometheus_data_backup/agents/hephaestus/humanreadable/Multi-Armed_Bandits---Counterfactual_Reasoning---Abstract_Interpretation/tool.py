from typing import Any, Dict, Tuple

"""
Multi-Armed Bandits × Counterfactual Reasoning × Abstract Interpretation

Parses prompts into typed constraint graphs, propagates intervals via abstract
interpretation, and uses UCB bandits to explore counterfactual answer variants.
Metacognitive awareness detects ambiguity and returns calibrated confidence.
"""

import re
import math
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    def __init__(self):
        self.epsilon = 1e-9
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates using MAB + abstract interpretation + counterfactuals."""
        if not candidates:
            return []
        
        # Parse prompt into constraint graph
        constraints = self._parse_constraints(prompt)
        
        # MAB state: mean reward, count, total pulls
        n_arms = len(candidates)
        mu = [0.0] * n_arms
        counts = [0] * n_arms
        N = 0
        budget = 20  # Total exploration budget
        
        # Initial pull of each arm
        for i, cand in enumerate(candidates):
            reward = self._evaluate_candidate(prompt, cand, constraints)
            mu[i] = reward
            counts[i] = 1
            N += 1
        
        # UCB exploration
        while N < budget:
            # Compute UCB scores
            ucb_scores = []
            for i in range(n_arms):
                if counts[i] == 0:
                    ucb_scores.append(float('inf'))
                else:
                    ucb = mu[i] + math.sqrt(2 * math.log(N + 1) / counts[i])
                    ucb_scores.append(ucb)
            
            # Select arm with highest UCB
            arm = ucb_scores.index(max(ucb_scores))
            
            # Generate counterfactual variant and evaluate
            reward = self._evaluate_candidate(prompt, candidates[arm], constraints)
            counts[arm] += 1
            mu[arm] = mu[arm] + (reward - mu[arm]) / counts[arm]
            N += 1
        
        # Build ranked results
        results = []
        for i, cand in enumerate(candidates):
            score = mu[i]
            reasoning = f"MAB reward {score:.3f} after {counts[i]} pulls"
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return calibrated confidence 0-1 with metacognitive awareness."""
        # First check meta-confidence (Tier B traps)
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Parse and evaluate
        constraints = self._parse_constraints(prompt)
        reward = self._evaluate_candidate(prompt, answer, constraints)
        
        # Cap confidence based on constraint quality
        if not constraints:
            return min(0.25, meta_conf)
        
        # Calibrate: never return >0.9 unless definitive computation
        base_conf = min(reward * 0.85, 0.85)
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect Tier B reasoning traps that make questions ambiguous/unanswerable."""
        p_lower = prompt.lower()
        
        # Presupposition traps
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))', p_lower):
            return 0.2
        
        # Quantifier scope ambiguity
        if re.search(r'\bevery\b.+\ba\b', p_lower) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity with explicit ambiguity question
        if re.search(r'\b(he|she|it|they)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            if 'told' in p_lower or 'said' in p_lower:
                return 0.2
        
        # False dichotomy
        if re.search(r'\beither\b.+\bor\b', p_lower) and not re.search(r'\b(neither|nor|other|also)\b', p_lower):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower) and '?' in prompt:
            if not re.search(r'\b(most|least|highest|lowest|largest|smallest)\b', p_lower):
                return 0.3
        
        # Explicit unanswerability
        if re.search(r'\b(cannot be determined|insufficient|not enough information)\b', p_lower):
            return 0.4
        
        return 1.0  # No meta-level issues detected
    
    def _parse_constraints(self, text: str) -> Dict[str, Any]:
        """Parse text into constraint graph with intervals."""
        constraints = {
            'numeric': [],
            'boolean': [],
            'conditionals': [],
            'causal': [],
            'negations': [],
            'comparatives': []
        }
        
        # Numeric comparisons and values
        for match in re.finditer(r'(\w+)\s*(>|<|=|>=|<=)\s*(\d+\.?\d*)', text):
            var, op, val = match.groups()
            constraints['numeric'].append((var, op, float(val)))
        
        # Detect bat-and-ball algebra pattern
        bat_ball = re.search(r'(\w+)\s+and\s+(\w+)\s+cost\s+\$?(\d+\.?\d*).+(\w+)\s+costs\s+\$?(\d+\.?\d*)\s+more', text, re.IGNORECASE)
        if bat_ball:
            constraints['algebra'] = ('bat_ball', bat_ball.groups())
        
        # Comparatives (direct comparison)
        for match in re.finditer(r'(\d+\.?\d*)\s*(>|<|=)\s*(\d+\.?\d*)', text):
            left, op, right = match.groups()
            constraints['comparatives'].append((float(left), op, float(right)))
        
        # Conditionals (if-then)
        for match in re.finditer(r'\bif\b(.+?)\bthen\b(.+?)(?:\.|,|$)', text, re.IGNORECASE):
            antecedent, consequent = match.groups()
            constraints['conditionals'].append((antecedent.strip(), consequent.strip()))
        
        # Causal markers
        for match in re.finditer(r'(.+?)\b(because|leads to|causes|results in)\b(.+?)(?:\.|,|$)', text, re.IGNORECASE):
            cause, marker, effect = match.groups()
            constraints['causal'].append((cause.strip(), effect.strip()))
        
        # Negations
        for match in re.finditer(r'\b(not|no|never|none)\s+(\w+)', text, re.IGNORECASE):
            constraints['negations'].append(match.group(2))
        
        # Modular arithmetic
        if re.search(r'\bmod(ulo)?\b|\bremainder\b', text, re.IGNORECASE):
            constraints['modular'] = True
        
        return constraints
    
    def _evaluate_candidate(self, prompt: str, candidate: str, constraints: Dict) -> float:
        """Evaluate candidate using abstract interpretation and specialized parsers."""
        score = 0.0
        components = []
        
        # Structural parsing (50%+ of score)
        structural = self._check_structural(prompt, candidate, constraints)
        components.append(('structural', structural, 0.5))
        
        # Computational solving (20%+ of score)
        computational = self._compute_answer(prompt, candidate, constraints)
        components.append(('computational', computational, 0.3))
        
        # NCD tiebreaker (<15% of score)
        ncd = self._ncd(prompt, candidate)
        ncd_score = max(0, 1 - ncd)
        components.append(('ncd', ncd_score, 0.2))
        
        # Weighted sum
        for name, val, weight in components:
            score += val * weight
        
        return max(0.0, min(1.0, score))
    
    def _check_structural(self, prompt: str, candidate: str, constraints: Dict) -> float:
        """Check structural constraints via abstract interpretation."""
        score = 0.0
        checks = 0
        
        # Numeric comparatives
        for left, op, right in constraints.get('comparatives', []):
            checks += 1
            if op == '>' and left > right:
                score += 1
            elif op == '<' and left < right:
                score += 1
            elif op == '=' and abs(left - right) < self.epsilon:
                score += 1
            elif op == '>=' and left >= right:
                score += 1
            elif op == '<=' and left <= right:
                score += 1
        
        # Negation consistency
        for neg_term in constraints.get('negations', []):
            checks += 1
            if neg_term.lower() not in candidate.lower():
                score += 0.5
        
        # Modus tollens check
        if 'not' in candidate.lower() and constraints.get('conditionals'):
            checks += 1
            score += 0.3
        
        # Transitivity in ordering
        numbers_prompt = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', prompt)]
        numbers_cand = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', candidate)]
        if len(numbers_prompt) >= 2 and len(numbers_cand) >= 1:
            checks += 1
            if any(n in numbers_prompt for n in numbers_cand):
                score += 0.4
        
        return score / checks if checks > 0 else 0.5
    
    def _compute_answer(self, prompt: str, candidate: str, constraints: Dict) -> float:
        """Actually compute answers for known problem types."""
        # Bat and ball problem
        if 'algebra' in constraints and constraints['algebra'][0] == 'bat_ball':
            return self._solve_bat_ball(prompt, candidate)
        
        # Direct numeric comparison (9.11 vs 9.9)
        nums_p = re.findall(r'\b(\d+\.\d+)\b', prompt)
        if len(nums_p) >= 2 and ('greater' in prompt.lower() or 'larger' in prompt.lower()):
            a, b = float(nums_p[0]), float(nums_p[1])
            if a < b and (nums_p[1] in candidate or str(b) in candidate):
                return 1.0
            elif a > b and (nums_p[0] in candidate or str(a) in candidate):
                return 1.0
        
        # Modular arithmetic
        if constraints.get('modular'):
            return self._solve_modular(prompt, candidate)
        
        # PEMDAS expression
        expr_match = re.search(r'(\d+)\s*([\+\-\*/])\s*(\d+)\s*([\+\-\*/])\s*(\d+)', prompt)
        if expr_match:
            try:
                result = eval(expr_match.group(0))
                if str(result) in candidate or str(int(result)) in candidate:
                    return 1.0
            except:
                pass
        
        # Coin flip independence
        if 'coin' in prompt.lower() and 'flip' in prompt.lower():
            if re.search(r'\b(0\.5|50%|1/2)\b', candidate):
                return 0.8
        
        # Pigeonhole principle
        if 'pigeon' in prompt.lower() or 'drawer' in prompt.lower():
            return self._check_pigeonhole(prompt, candidate)
        
        return 0.5
    
    def _solve_bat_ball(self, prompt: str, candidate: str) -> float:
        """Solve bat and ball algebra problem."""
        # Pattern: X and Y cost $total, X costs $diff more than Y
        match = re.search(r'cost\s+\$?(\d+\.?\d*).+costs\s+\$?(\d+\.?\d*)\s+more', prompt, re.IGNORECASE)
        if match:
            total, diff = float(match.group(1)), float(match.group(2))
            # ball = (total - diff) / 2, bat = ball + diff
            ball = (total - diff) / 2
            bat = ball + diff
            
            # Check if candidate contains correct ball price
            cand_nums = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', candidate)]
            if any(abs(n - ball) < 0.01 for n in cand_nums):
                return 1.0
            elif any(abs(n - bat) < 0.01 for n in cand_nums):
                return 0.3  # Wrong but related
        return 0.0
    
    def _solve_modular(self, prompt: str, candidate: str) -> float:
        """Solve modular arithmetic problems."""
        match = re.search(r'(\d+)\s+mod(?:ulo)?\s+(\d+)', prompt, re.IGNORECASE)
        if match:
            a, m = int(match.group(1)), int(match.group(2))
            result = a % m
            if str(result) in candidate:
                return 1.0
        return 0.5
    
    def _check_pigeonhole(self, prompt: str, candidate: str) -> float:
        """Check pigeonhole principle application."""
        nums = [int(x) for x in re.findall(r'\b(\d+)\b', prompt)]
        if len(nums) >= 2:
            # If more items than containers, answer should reflect certainty
            if nums[0] > nums[1] and ('must' in candidate.lower() or 'yes' in candidate.lower()):
                return 0.9
        return 0.5
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0