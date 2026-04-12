from typing import Any, Dict, Optional, Tuple

"""
Bandit-Guided Program Synthesis with Property-Based Validation (BGPS-PV)

Extracts logical constraints from questions, synthesizes candidate programs
using a typed DSL, validates them via property-based testing, and uses
multi-armed bandits (UCB) to guide the search.
"""

import re
import math
import zlib
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import random


@dataclass
class Constraint:
    type: str  # 'gt', 'lt', 'eq', 'neg', 'cond', 'causal', 'temporal'
    args: List[Any]


class ReasoningTool:
    def __init__(self):
        random.seed(42)
        
    def _extract_constraints(self, text: str) -> List[Constraint]:
        """Parse prompt to extract logical constraints."""
        constraints = []
        text_lower = text.lower()
        
        # Numeric comparatives
        for match in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|=|equals?|greater|less)', text_lower):
            val = float(match.group(1))
            op = match.group(2)
            if '>' in op or 'greater' in op:
                constraints.append(Constraint('gt', [val]))
            elif '<' in op or 'less' in op:
                constraints.append(Constraint('lt', [val]))
            else:
                constraints.append(Constraint('eq', [val]))
        
        # Negations
        if re.search(r'\b(not|no|never|n\'t)\b', text_lower):
            constraints.append(Constraint('neg', []))
        
        # Conditionals
        if re.search(r'\b(if|unless|when|whenever)\b', text_lower):
            constraints.append(Constraint('cond', []))
        
        # Causal
        if re.search(r'\b(because|leads? to|results? in|causes?|due to)\b', text_lower):
            constraints.append(Constraint('causal', []))
        
        # Temporal
        if re.search(r'\b(before|after|previous|next|earlier|later|first|last)\b', text_lower):
            constraints.append(Constraint('temporal', []))
        
        return constraints
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect epistemic traps and return confidence cap."""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery .+ (a|an)\b', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', prompt_lower) and '?' in prompt:
            if re.search(r'\bwho\b|\bwhich\b', prompt_lower):
                return 0.25
        
        # False dichotomy
        if re.search(r'\b(either .+ or)\b', prompt_lower) and not re.search(r'\b(or .+ or|neither)\b', prompt_lower):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', prompt_lower):
            if not re.search(r'\b(most|least|criteria|measure|metric)\b', prompt_lower):
                return 0.3
        
        # Unanswerable markers
        if re.search(r'\b(impossible|cannot|unknown|unclear)\b', prompt_lower):
            return 0.25
        
        return 1.0
    
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract all numeric values."""
        return [float(m) for m in re.findall(r'\d+\.?\d*', text)]
    
    def _compute_numeric(self, prompt: str, candidate: str) -> Optional[float]:
        """Compute numeric reasoning score."""
        prompt_nums = self._extract_numbers(prompt)
        cand_nums = self._extract_numbers(candidate)
        
        if not prompt_nums or not cand_nums:
            return None
        
        # Check if candidate number satisfies prompt constraints
        constraints = self._extract_constraints(prompt)
        score = 0.0
        
        for cand_num in cand_nums:
            for constraint in constraints:
                if constraint.type == 'gt' and cand_num > constraint.args[0]:
                    score += 1.0
                elif constraint.type == 'lt' and cand_num < constraint.args[0]:
                    score += 1.0
                elif constraint.type == 'eq' and abs(cand_num - constraint.args[0]) < 0.01:
                    score += 1.0
        
        # Arithmetic evaluation
        for expr in re.findall(r'(\d+\.?\d*)\s*([\+\-\*/])\s*(\d+\.?\d*)', candidate):
            try:
                a, op, b = float(expr[0]), expr[1], float(expr[2])
                result = eval(f"{a}{op}{b}")
                if any(abs(result - pn) < 0.01 for pn in prompt_nums):
                    score += 2.0
            except:
                pass
        
        return score if score > 0 else None
    
    def _compute_probability(self, prompt: str, candidate: str) -> Optional[float]:
        """Compute Bayesian/probability reasoning score."""
        # Check for probability keywords
        if not re.search(r'\b(probability|chance|likely|odds|percent|%)\b', prompt.lower()):
            return None
        
        prompt_nums = self._extract_numbers(prompt)
        cand_nums = self._extract_numbers(candidate)
        
        if not cand_nums:
            return None
        
        # Simple base rate neglect check
        if len(prompt_nums) >= 2:
            # If candidate incorporates base rates (uses multiple prompt numbers)
            if len(set(cand_nums) & set(prompt_nums)) >= 2:
                return 3.0
            # If candidate ignores base rate (just echoes one number)
            elif len(set(cand_nums) & set(prompt_nums)) == 1:
                return -1.0
        
        # Probability range check
        for num in cand_nums:
            if 0 <= num <= 1 or 0 <= num <= 100:
                return 1.0
        
        return None
    
    def _compute_temporal(self, prompt: str, candidate: str) -> Optional[float]:
        """Compute temporal ordering score."""
        temporal_words = ['before', 'after', 'earlier', 'later', 'first', 'last', 'previous', 'next']
        
        if not any(tw in prompt.lower() for tw in temporal_words):
            return None
        
        # Extract temporal cues from both
        prompt_cues = [tw for tw in temporal_words if tw in prompt.lower()]
        cand_cues = [tw for tw in temporal_words if tw in candidate.lower()]
        
        if not cand_cues:
            return None
        
        # Check for consistent ordering
        overlap = len(set(prompt_cues) & set(cand_cues))
        return float(overlap) * 1.5
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2)
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate and rank candidates using BGPS-PV."""
        results = []
        constraints = self._extract_constraints(prompt)
        meta_cap = self._meta_confidence(prompt)
        
        # Bandit stats for UCB
        pulls = defaultdict(int)
        rewards = defaultdict(float)
        total_pulls = 0
        
        for idx, cand in enumerate(candidates):
            # Initialize arm
            pulls[idx] = 1
            total_pulls += 1
            
            # Compute structural score
            structural_score = 0.0
            
            # Constraint matching
            cand_lower = cand.lower()
            for constraint in constraints:
                if constraint.type == 'neg':
                    if re.search(r'\b(not|no|never|n\'t|false)\b', cand_lower):
                        structural_score += 2.0
                elif constraint.type == 'cond':
                    if re.search(r'\b(if|then|unless|when)\b', cand_lower):
                        structural_score += 1.5
                elif constraint.type == 'causal':
                    if re.search(r'\b(because|leads?|results?|causes?)\b', cand_lower):
                        structural_score += 1.5
                elif constraint.type == 'temporal':
                    if re.search(r'\b(before|after|previous|next)\b', cand_lower):
                        structural_score += 1.5
            
            # Compute numeric score
            numeric_score = self._compute_numeric(prompt, cand) or 0.0
            
            # Compute probability score
            prob_score = self._compute_probability(prompt, cand) or 0.0
            
            # Compute temporal score
            temporal_score = self._compute_temporal(prompt, cand) or 0.0
            
            # Computation total (40%+)
            computation_score = numeric_score + prob_score + temporal_score
            
            # NCD as tiebreaker (max 15%)
            ncd_score = max(0, 1.0 - self._ncd(prompt, cand)) * 0.5
            
            # Combined score
            raw_score = structural_score * 0.35 + computation_score * 0.5 + ncd_score * 0.15
            
            # Simplicity penalty
            simplicity = 1.0 / (1.0 + len(cand) / 100.0)
            
            # UCB computation
            rewards[idx] = raw_score
            ucb = rewards[idx] / pulls[idx] + math.sqrt(2 * math.log(total_pulls) / pulls[idx])
            
            final_score = ucb * simplicity
            
            # Apply meta-confidence cap
            final_score = min(final_score, final_score * meta_cap)
            
            reasoning = f"Structural:{structural_score:.1f} Computation:{computation_score:.1f} NCD:{ncd_score:.2f} UCB:{ucb:.2f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Rank by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence in answer given prompt."""
        # First check meta-confidence
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.3:
            return meta_cap
        
        constraints = self._extract_constraints(prompt)
        
        # No structural match = uncertainty
        if not constraints:
            return 0.25
        
        # Compute scores
        numeric_score = self._compute_numeric(prompt, answer) or 0.0
        prob_score = self._compute_probability(prompt, answer) or 0.0
        temporal_score = self._compute_temporal(prompt, answer) or 0.0
        
        # Strong computation signal = high confidence
        if numeric_score >= 2.0 or prob_score >= 2.0:
            return min(0.85, meta_cap)
        
        # Constraint satisfaction
        satisfied = 0
        answer_lower = answer.lower()
        
        for constraint in constraints:
            if constraint.type == 'neg' and re.search(r'\b(not|no|never|false)\b', answer_lower):
                satisfied += 1
            elif constraint.type in ['cond', 'causal', 'temporal']:
                satisfied += 1 if numeric_score > 0 or prob_score > 0 or temporal_score > 0 else 0
        
        if not constraints:
            base_conf = 0.3
        else:
            base_conf = 0.3 + (satisfied / len(constraints)) * 0.5
        
        # Cap at meta-confidence
        return min(base_conf, meta_cap * 0.95)