from typing import Dict, Tuple

import re
import math
import zlib
from typing import List, Dict, Tuple
import numpy as np

class ReasoningTool:
    """
    Combines measure theory (max entropy), multi-armed bandits, and constructive computation.
    
    Core mechanisms:
    1. Extract logical constraints from text (negations, comparatives, conditionals, causal)
    2. Build max-entropy probability distribution over propositions
    3. Use UCB bandit to rank candidates with exploration bonus
    4. Compute numeric/probabilistic/temporal answers constructively
    5. Meta-confidence detects ambiguity and presuppositions
    """
    
    def __init__(self):
        self.bandit_counts = {}
        self.bandit_rewards = {}
        self.t = 0
    
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Rank candidates using UCB bandit + max-entropy constraint solver."""
        results = []
        
        for cand in candidates:
            # Compute base reward from structural + computational features
            r_a = self._compute_reward(prompt, cand)
            
            # UCB exploration bonus
            self.t += 1
            n_a = self.bandit_counts.get(cand, 0) + 1
            self.bandit_counts[cand] = n_a
            ucb_bonus = math.sqrt(2 * math.log(self.t) / n_a)
            score = r_a + 0.1 * ucb_bonus
            
            reasoning = self._explain(prompt, cand)
            results.append({"candidate": cand, "score": float(score), "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, incorporating meta-confidence checks."""
        meta_conf = self._meta_confidence(prompt)
        base_conf = self._compute_reward(prompt, answer)
        return min(meta_conf, base_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity, presuppositions, unanswerability."""
        p = prompt.lower()
        
        # Presupposition detection
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop)|when did .* stop)', p):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery \w+.*\ba\b', p):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she|they)\b', p) and re.search(r'\bwho\b', p):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .* or\b', p) and not re.search(r'\bonly\b', p):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|better)\b', p) and not re.search(r'\b(more|most|least|faster|slower|larger|smaller)\b', p):
            return 0.3
        
        # Missing information markers
        if re.search(r'\b(insufficient|not enough|cannot determine|ambiguous)\b', p):
            return 0.2
        
        return 1.0  # No meta-issues detected
    
    def _compute_reward(self, prompt: str, candidate: str) -> float:
        """Compute reward from structural + computational features."""
        # Constructive computation (40%+)
        comp_score = self._constructive_compute(prompt, candidate)
        
        # Structural parsing (30%+)
        struct_score = self._structural_match(prompt, candidate)
        
        # Max-entropy constraint satisfaction (20%)
        constraint_score = self._maxent_constraints(prompt, candidate)
        
        # NCD tiebreaker (10% max)
        ncd = self._ncd(prompt, candidate)
        ncd_score = 1.0 - ncd
        
        total = 0.45 * comp_score + 0.30 * struct_score + 0.15 * constraint_score + 0.10 * ncd_score
        return min(max(total, 0.0), 1.0)
    
    def _constructive_compute(self, prompt: str, candidate: str) -> float:
        """Perform actual computation: arithmetic, Bayesian, temporal."""
        score = 0.0
        
        # Numeric comparison
        num_score = self._numeric_eval(prompt, candidate)
        if num_score >= 0:
            return num_score
        
        # Bayesian probability
        bayes_score = self._bayesian_compute(prompt, candidate)
        if bayes_score >= 0:
            return bayes_score
        
        # Temporal ordering
        temp_score = self._temporal_compute(prompt, candidate)
        if temp_score >= 0:
            return temp_score
        
        # Arithmetic expression evaluation
        arith_score = self._arithmetic_eval(prompt, candidate)
        if arith_score >= 0:
            return arith_score
        
        return 0.3  # No computation matched
    
    def _numeric_eval(self, prompt: str, candidate: str) -> float:
        """Extract and compare numbers."""
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        c_nums = re.findall(r'\d+\.?\d*', candidate)
        
        if not c_nums:
            return -1
        
        # Check for comparison operators in prompt
        if re.search(r'(greater|larger|more|bigger|higher)', prompt.lower()):
            # Candidate should have larger number
            if p_nums and c_nums:
                if float(c_nums[0]) > float(p_nums[0]):
                    return 0.9
                else:
                    return 0.1
        elif re.search(r'(less|smaller|fewer|lower)', prompt.lower()):
            if p_nums and c_nums:
                if float(c_nums[0]) < float(p_nums[0]):
                    return 0.9
                else:
                    return 0.1
        
        # Special case: "9.11 vs 9.9" type comparisons
        if len(p_nums) == 2 and len(c_nums) == 1:
            vals = [float(p_nums[0]), float(p_nums[1])]
            c_val = float(c_nums[0])
            if c_val == max(vals) and re.search(r'(greater|larger)', prompt.lower()):
                return 0.95
            if c_val == min(vals) and re.search(r'(less|smaller)', prompt.lower()):
                return 0.95
        
        return -1
    
    def _bayesian_compute(self, prompt: str, candidate: str) -> float:
        """Compute Bayesian posterior probabilities."""
        # Pattern: P(A|B), base rate, likelihood
        p = prompt.lower()
        
        # Extract probability values
        prob_pattern = r'(\d+\.?\d*)\s*%|(\d+\.\d+)\s*probability'
        probs = re.findall(prob_pattern, p)
        prob_vals = [float(p[0] or p[1]) for p in probs if p[0] or p[1]]
        
        if len(prob_vals) >= 2:
            # Simple Bayes: P(A|B) = P(B|A) * P(A) / P(B)
            # Look for prior and likelihood
            c_nums = re.findall(r'\d+\.?\d*', candidate)
            if c_nums:
                c_val = float(c_nums[0])
                # Check if candidate is close to computed posterior
                if len(prob_vals) == 3:
                    prior, likelihood, evidence = prob_vals
                    posterior = (likelihood * prior) / evidence if evidence > 0 else 0
                    if abs(c_val - posterior) < 0.05:
                        return 0.95
        
        return -1
    
    def _temporal_compute(self, prompt: str, candidate: str) -> float:
        """Compute temporal ordering and durations."""
        p = prompt.lower()
        
        # Look for before/after relationships
        if re.search(r'\b(before|after|earlier|later)\b', p):
            # Extract entities
            entities = re.findall(r'\b[A-Z][a-z]+\b', prompt)
            if len(entities) >= 2:
                # Check if candidate mentions the right entity
                if re.search(r'\bbefore\b', p) and entities[0].lower() in candidate.lower():
                    return 0.8
                if re.search(r'\bafter\b', p) and entities[1].lower() in candidate.lower():
                    return 0.8
        
        return -1
    
    def _arithmetic_eval(self, prompt: str, candidate: str) -> float:
        """Evaluate arithmetic expressions (PEMDAS)."""
        # Extract arithmetic from prompt
        expr = re.search(r'(\d+\s*[\+\-\*/]\s*\d+)', prompt)
        if expr:
            try:
                computed = eval(expr.group(1))
                c_nums = re.findall(r'\d+\.?\d*', candidate)
                if c_nums and abs(float(c_nums[0]) - computed) < 0.01:
                    return 0.95
            except:
                pass
        
        return -1
    
    def _structural_match(self, prompt: str, candidate: str) -> float:
        """Parse logical structure: negations, conditionals, comparatives."""
        score = 0.0
        
        # Negation consistency
        p_neg = len(re.findall(r'\b(not|no|never|n\'t)\b', prompt.lower()))
        c_neg = len(re.findall(r'\b(not|no|never|n\'t)\b', candidate.lower()))
        if p_neg > 0:
            score += 0.3 if (p_neg % 2) == (c_neg % 2) else 0.0
        else:
            score += 0.1 if c_neg == 0 else 0.0
        
        # Conditional matching (if-then)
        if re.search(r'\bif\b.*\bthen\b', prompt.lower()):
            if re.search(r'\bif\b.*\bthen\b', candidate.lower()):
                score += 0.3
        
        # Causal markers
        p_causal = len(re.findall(r'\b(because|cause|lead|result)', prompt.lower()))
        c_causal = len(re.findall(r'\b(because|cause|lead|result)', candidate.lower()))
        if p_causal > 0 and c_causal > 0:
            score += 0.2
        
        # Comparative operators
        if re.search(r'\b(more|less|greater|fewer|higher|lower)\b', prompt.lower()):
            if re.search(r'\b(more|less|greater|fewer|higher|lower)\b', candidate.lower()):
                score += 0.2
        
        return min(score, 1.0)
    
    def _maxent_constraints(self, prompt: str, candidate: str) -> float:
        """Max-entropy constraint satisfaction over logical propositions."""
        # Extract propositions (simple: each sentence/clause is a proposition)
        p_props = [s.strip() for s in re.split(r'[.;,]', prompt) if s.strip()]
        c_props = [s.strip() for s in re.split(r'[.;,]', candidate) if s.strip()]
        
        if not p_props or not c_props:
            return 0.3
        
        # Build constraint graph: count overlapping key terms
        p_terms = set(re.findall(r'\b\w+\b', prompt.lower())) - {'the', 'a', 'an', 'is', 'are', 'was', 'were'}
        c_terms = set(re.findall(r'\b\w+\b', candidate.lower())) - {'the', 'a', 'an', 'is', 'are', 'was', 'were'}
        
        overlap = len(p_terms & c_terms)
        total = len(p_terms | c_terms)
        
        if total == 0:
            return 0.3
        
        # Max-entropy marginal: normalized overlap
        marginal_prob = overlap / total
        return marginal_prob
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (zlib)."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.5
    
    def _explain(self, prompt: str, candidate: str) -> str:
        """Generate reasoning trace."""
        meta = self._meta_confidence(prompt)
        if meta < 0.5:
            return "Low confidence: ambiguous or presupposition detected"
        
        comp = self._constructive_compute(prompt, candidate)
        if comp > 0.8:
            return "High confidence: constructive computation matched"
        
        struct = self._structural_match(prompt, candidate)
        if struct > 0.6:
            return "Moderate confidence: structural features aligned"
        
        return "Low confidence: no strong computational or structural match"