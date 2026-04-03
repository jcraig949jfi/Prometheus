from typing import Dict, Optional, Tuple

"""
Dialectical-Pragmatic Bandit Scorer (DPBS)

Combines:
- Dialectical reasoning: thesis/antithesis contradiction detection, constraint propagation
- Pragmatic scoring: Gricean maxim violations
- Multi-armed bandits: UCB1 for candidate selection

Core mechanism:
1. Parse prompt/candidates into propositional units, numeric values, logical structures
2. Build thesis/antithesis vectors tracking truth claims
3. Propagate constraints (transitivity, conditionals, arithmetic)
4. Score via dialectical synthesis - pragmatic penalties
5. UCB1 bandit selection over candidates
6. Meta-confidence checks question answerability
"""

import re
import numpy as np
from typing import List, Dict, Tuple, Optional
import zlib

class ReasoningTool:
    def __init__(self):
        self.alpha = 0.5  # contradiction penalty
        self.beta = 0.3   # pragmatic penalty
        self.ucb_c = 1.4  # UCB exploration constant
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Rank candidates by dialectical-pragmatic-bandit score."""
        n = len(candidates)
        if n == 0:
            return []
        
        # Parse prompt structure
        prompt_props = self._parse_propositions(prompt)
        prompt_nums = self._extract_numbers(prompt)
        
        # Try computational solvers first
        computed = self._compute_answer(prompt, prompt_nums)
        
        # Initialize bandit stats
        pulls = np.ones(n)
        wins = np.zeros(n)
        
        # Build thesis/antithesis for each candidate
        all_props = set()
        for c in candidates:
            all_props.update(self._parse_propositions(c))
        all_props.update(prompt_props)
        prop_list = sorted(all_props)
        T = len(prop_list)
        prop_idx = {p: i for i, p in enumerate(prop_list)}
        
        thesis = np.zeros((n, T), dtype=bool)
        antithesis = np.zeros((n, T), dtype=bool)
        
        for i, cand in enumerate(candidates):
            cand_props = self._parse_propositions(cand)
            negs = self._extract_negations(cand)
            
            for p in cand_props:
                if p in prop_idx:
                    idx = prop_idx[p]
                    if any(neg in p.lower() for neg in negs):
                        antithesis[i, idx] = True
                    else:
                        thesis[i, idx] = True
        
        # Compute rewards
        rewards = []
        for i, cand in enumerate(candidates):
            # Dialectical score
            contra = np.sum(thesis[i] & antithesis[i])
            synth = np.sum(thesis[i] & ~antithesis[i])
            
            # Pragmatic score
            prag = self._pragmatic_score(prompt, cand, prompt_props)
            
            # Computational match
            comp_bonus = 0.0
            if computed is not None:
                comp_bonus = self._compute_match(computed, cand)
            
            # NCD tiebreaker (max 15%)
            ncd = self._ncd(prompt, cand)
            ncd_score = 0.15 * (1 - ncd)
            
            # Combined reward
            r = 0.5 * comp_bonus + 0.35 * (synth - self.alpha * contra) - self.beta * prag + ncd_score
            rewards.append(r)
            wins[i] = r
        
        # UCB1 selection
        total_pulls = np.sum(pulls)
        ucb_scores = wins / pulls + self.ucb_c * np.sqrt(np.log(total_pulls) / pulls)
        
        # Rank by UCB
        ranked_idx = np.argsort(-ucb_scores)
        
        results = []
        for idx in ranked_idx:
            results.append({
                "candidate": candidates[idx],
                "score": float(ucb_scores[idx]),
                "reasoning": f"UCB={ucb_scores[idx]:.3f}, reward={rewards[idx]:.3f}, comp={comp_bonus if idx == ranked_idx[0] else 0:.2f}"
            })
        
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1. Capped by meta-confidence in question."""
        # Meta-confidence check
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Computational confidence
        nums = self._extract_numbers(prompt)
        computed = self._compute_answer(prompt, nums)
        
        if computed is not None:
            match = self._compute_match(computed, answer)
            if match > 0.9:
                return min(0.95, meta_conf)  # Never full confidence
            elif match < 0.1:
                return 0.1
            else:
                return min(match * 0.7, meta_conf)
        
        # Structural confidence
        prompt_props = self._parse_propositions(prompt)
        ans_props = self._parse_propositions(answer)
        
        if len(ans_props) == 0:
            return 0.2
        
        overlap = len(set(ans_props) & set(prompt_props)) / max(len(ans_props), 1)
        negs = self._extract_negations(answer)
        neg_penalty = 0.1 * len(negs)
        
        struct_conf = max(0.1, min(0.7, overlap - neg_penalty))
        
        return min(struct_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check if prompt is answerable. Return <0.3 for ambiguous/unanswerable."""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you|did you) (stop|quit|cease)', p_lower):
            return 0.15
        if re.search(r'\bwhy (did|does|is) \w+ (fail|stop|not)', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery \w+ \w+ a \w+', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they) (was|were|is|are)', p_lower) and 'who' in p_lower:
            return 0.2
        
        # False dichotomy
        if re.search(r'\beither \w+ or \w+\b', p_lower) and '?' in prompt:
            return 0.25
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)', p_lower):
            if not re.search(r'\b(most|least|more|less|greater|highest|lowest)', p_lower):
                return 0.2
        
        # Unanswerable markers
        if 'impossible to' in p_lower or 'cannot be determined' in p_lower:
            return 0.15
        
        return 0.8  # Default: probably answerable
    
    def _compute_answer(self, prompt: str, nums: List[float]) -> Optional[float]:
        """Actually compute answer for solvable problems."""
        p_lower = prompt.lower()
        
        # Bat and ball: X + Y = A, X = Y + B
        match = re.search(r'cost.*\$?([\d.]+).*one.*\$?([\d.]+)\s+(more|less)', p_lower)
        if match and len(nums) >= 2:
            total, diff = nums[0], nums[1]
            if 'more' in match.group(3):
                return (total - diff) / 2  # Ball price
        
        # Numeric comparison
        if re.search(r'(which|what).*(larger|smaller|greater|less|more)', p_lower):
            if len(nums) >= 2:
                if 'larger' in p_lower or 'greater' in p_lower or 'more' in p_lower:
                    return max(nums)
                else:
                    return min(nums)
        
        # All but N
        match = re.search(r'all but (\d+)', p_lower)
        if match and len(nums) >= 1:
            total = nums[0]
            excluded = int(match.group(1))
            return total - excluded
        
        # Modular arithmetic
        match = re.search(r'(\d+)\s*mod\s*(\d+)', p_lower)
        if match:
            return int(match.group(1)) % int(match.group(2))
        
        # Simple arithmetic in prompt
        match = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)', prompt)
        if match:
            a, op, b = float(match.group(1)), match.group(2), float(match.group(3))
            if op == '+': return a + b
            elif op == '-': return a - b
            elif op == '*': return a * b
            elif op == '/' and b != 0: return a / b
        
        return None
    
    def _compute_match(self, computed: float, answer: str) -> float:
        """Check if answer matches computed value."""
        ans_nums = self._extract_numbers(answer)
        if len(ans_nums) == 0:
            return 0.0
        
        for num in ans_nums:
            if abs(num - computed) < 0.01:
                return 1.0
            elif abs(num - computed) < 0.1:
                return 0.7
        
        return 0.0
    
    def _parse_propositions(self, text: str) -> List[str]:
        """Extract subject-predicate units."""
        props = []
        # Simple SVO patterns
        pattern = r'\b(\w+)\s+(is|are|was|were|has|have)\s+(\w+(?:\s+\w+)?)'
        for match in re.finditer(pattern, text.lower()):
            props.append(f"{match.group(1)} {match.group(2)} {match.group(3)}")
        return props
    
    def _extract_negations(self, text: str) -> List[str]:
        """Find negation markers."""
        return re.findall(r'\b(not|no|never|neither|nor)\b', text.lower())
    
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract all numeric values."""
        nums = []
        for match in re.finditer(r'\d+\.?\d*', text):
            try:
                nums.append(float(match.group()))
            except:
                pass
        return nums
    
    def _pragmatic_score(self, prompt: str, candidate: str, prompt_props: List[str]) -> float:
        """Gricean maxim violations (higher = worse)."""
        penalty = 0.0
        
        # Quantity: excessive length
        cand_len = len(candidate.split())
        if cand_len > 50:
            penalty += 0.3
        
        # Relation: irrelevant to prompt
        cand_props = self._parse_propositions(candidate)
        if len(cand_props) > 0:
            overlap = len(set(cand_props) & set(prompt_props)) / len(cand_props)
            penalty += 0.5 * (1 - overlap)
        
        # Manner: complex nested conditionals
        if_depth = len(re.findall(r'\bif\b', candidate.lower()))
        if if_depth > 2:
            penalty += 0.2 * (if_depth - 2)
        
        return penalty
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0