import re
import numpy as np
from typing import List, Dict, Tuple, Set, Any

class ReasoningTool:
    """
    A reasoning tool combining structural parsing, game-theoretic equilibrium,
    and metacognitive confidence calibration.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (negations, comparatives, conditionals, causals, ordinals, numbers).
    2. Payoff Matrix: Computes pairwise compatibility between candidates based on shared logic, 
       pragmatic implicature, and numeric consistency.
    3. Nash Equilibrium: Solves for the mixed-strategy equilibrium to weight candidates.
    4. Metacognition: Calibrates confidence based on equilibrium entropy and prompt ambiguity checks.
    """
    
    def __init__(self):
        # Weights for payoff computation
        self.w1 = 0.4  # Shared propositions
        self.w2 = 0.3  # Contradictions
        self.w3 = 0.2  # Pragmatics
        self.w4 = 0.1  # Numeric consistency
        
        # Regex patterns for parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.I),
            'comparative': re.compile(r'\b(greater|less|more|fewer|higher|lower|before|after)\b.*?\b(than|to)\b|(\>|\<|\>=|<=)', re.I),
            'conditional': re.compile(r'\b(if|unless|when|then)\b', re.I),
            'causal': re.compile(r'\b(because|due to|leads to|causes|therefore)\b', re.I),
            'ordinal': re.compile(r'\b(first|last|next|previous|before|after)\b', re.I),
            'number': re.compile(r'-?\d+\.?\d*'),
            'quantifier': re.compile(r'\b(all|some|none|every|any)\b', re.I)
        }
        
        # Ambiguity triggers for Tier B (Epistemic Honesty)
        self.ambiguity_triggers = [
            re.compile(r'\b(stopped|quit|ceased)\b.*\b(have|has)\b', re.I), # Presupposition
            re.compile(r'\b(every|all)\b.*\b(same|different|one)\b', re.I), # Scope
            re.compile(r'\b(he|she|him|her|it|they)\b.*\b(who|which one)\b', re.I), # Pronoun
            re.compile(r'\b(either|or)\b.*\b(choice|option)\b', re.I), # False dichotomy hint
            re.compile(r'\b(best|worst|favorite|opinion)\b', re.I), # Subjectivity
            re.compile(r'\b(why|how)\b.*\b(fail|stop|impossible)\b', re.I) # Unanswerable/Presupposition
        ]

    def _parse_text(self, text: str) -> Set[Tuple]:
        """Converts text into a set of atomic proposition tuples."""
        props = set()
        text_lower = text.lower()
        
        # Negations
        if self.patterns['negation'].search(text_lower):
            props.add(('negation', 'present'))
            
        # Comparatives
        if self.patterns['comparative'].search(text_lower):
            props.add(('comparative', 'present'))
            
        # Conditionals
        if self.patterns['conditional'].search(text_lower):
            props.add(('conditional', 'present'))
            
        # Causal
        if self.patterns['causal'].search(text_lower):
            props.add(('causal', 'present'))
            
        # Ordinal/Temporal
        if self.patterns['ordinal'].search(text_lower):
            props.add(('ordinal', 'present'))
            
        # Quantifiers
        if self.patterns['quantifier'].search(text_lower):
            props.add(('quantifier', 'present'))

        # Numeric literals
        nums = self.patterns['number'].findall(text)
        for n in nums:
            props.add(('num', float(n)))
            
        # Simple keyword extraction for content overlap (bag-of-words fallback for logic)
        words = set(re.findall(r'\b[a-z]{4,}\b', text_lower))
        for w in words:
            if w not in {'than', 'then', 'from', 'with', 'have', 'been', 'would', 'could', 'should'}:
                props.add(('word', w))
                
        return props

    def _check_numeric_consistency(self, s1: Set[Tuple], s2: Set[Tuple]) -> int:
        """Checks if numeric constraints in two sets are consistent."""
        nums1 = sorted([x[1] for x in s1 if x[0] == 'num'])
        nums2 = sorted([x[1] for x in s2 if x[0] == 'num'])
        
        if not nums1 or not nums2:
            return 1 # No numeric conflict if none present
        
        # Simple interval check: do they overlap significantly?
        # If one set says "5" and other says "100", likely conflict if context implies single value
        # Heuristic: If ranges are disjoint and far apart, penalize.
        if abs(np.mean(nums1) - np.mean(nums2)) > (max(nums1 + nums2) * 0.5 + 1):
            return -1
        return 1

    def _pragmatics_match(self, s1: Set[Tuple], s2: Set[Tuple]) -> float:
        """
        Rewards cases where antecedents in s1 imply consequences in s2.
        Simplified Gricean check: If s1 has conditional and s2 has the consequent logic.
        """
        score = 0.0
        has_cond_1 = ('conditional', 'present') in s1
        has_cond_2 = ('conditional', 'present') in s2
        
        # If both have conditionals, they are compatible structures
        if has_cond_1 and has_cond_2:
            score += 0.5
            
        # If s1 implies causality and s2 has the effect (heuristic: shared words)
        if ('causal', 'present') in s1:
            common_words = {x for x in s1 if x[0] == 'word'} & {x for x in s2 if x[0] == 'word'}
            if common_words:
                score += 0.3
                
        return score

    def _compute_payoff_matrix(self, candidates: List[str]) -> np.ndarray:
        """Computes the NxN payoff matrix."""
        n = len(candidates)
        if n == 0:
            return np.array([])
        if n == 1:
            return np.array([[1.0]])
            
        parsed = [self._parse_text(c) for c in candidates]
        payoff = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                s1, s2 = parsed[i], parsed[j]
                
                # Shared propositions
                shared = len(s1 & s2)
                
                # Symmetric difference (contradictions/divergence)
                diff = len(s1 ^ s2)
                
                # Pragmatics
                prag = self._pragmatics_match(s1, s2)
                
                # Numeric consistency
                num_cons = self._check_numeric_consistency(s1, s2)
                
                val = (self.w1 * shared) - (self.w2 * diff * 0.1) + (self.w3 * prag) + (self.w4 * num_cons)
                payoff[i, j] = val
                
        return payoff

    def _solve_nash(self, payoff: np.ndarray) -> np.ndarray:
        """
        Approximates mixed-strategy Nash Equilibrium using replicator dynamics.
        Since exact LP solving without scipy is verbose, we use iterative normalization
        which converges to the equilibrium for symmetric games in this context.
        """
        n = payoff.shape[0]
        if n == 0:
            return np.array([])
        if n == 1:
            return np.array([1.0])
            
        # Initialize uniform strategy
        x = np.ones(n) / n
        
        # Replicator dynamics iteration
        for _ in range(100):
            payoffs = payoff @ x
            avg_payoff = np.dot(x, payoffs)
            if avg_payoff == 0:
                break
            x_new = x * (payoffs / (avg_payoff + 1e-9))
            # Normalize to sum to 1
            if np.sum(x_new) > 0:
                x = x_new / np.sum(x_new)
            else:
                break
                
        # Normalize to ensure stability
        if np.sum(x) == 0:
            return np.ones(n) / n
        return x / np.sum(x)

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        """
        Tier B Check: Evaluates prompt ambiguity and presuppositions.
        Returns a cap value (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # Check for ambiguity triggers
        for pattern in self.ambiguity_triggers:
            if pattern.search(p_lower):
                return 0.25  # High ambiguity/presupposition detected
        
        # Check for lack of structural signal in answer (if answer is too short/vague)
        if len(answer.strip()) < 3:
            return 0.3
            
        # If we have numbers, check if the answer actually computes them (basic check)
        # This is a heuristic; true computation verification is complex.
        # We rely on the structural score for the rest.
        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Structural Parsing & Payoff
        payoff = self._compute_payoff_matrix(candidates)
        
        # 2. Nash Equilibrium
        weights = self._solve_nash(payoff)
        
        # 3. Metacognitive Scoring
        # Confidence calibration based on entropy
        epsilon = 1e-9
        entropy = -np.sum(weights * np.log(weights + epsilon))
        max_entropy = np.log(len(candidates)) if len(candidates) > 1 else 1
        conf_calib = 1.0 - (entropy / (max_entropy + epsilon))
        conf_calib = max(0.0, min(1.0, conf_calib))
        
        # Error monitoring (variance of expected payoff)
        if payoff.size > 0:
            expected_payoffs = payoff @ weights
            err_variance = np.var(expected_payoffs)
        else:
            err_variance = 1.0
            
        results = []
        for i, cand in enumerate(candidates):
            base_score = weights[i]
            
            # Final score formula from spec
            final_score = (base_score * conf_calib) / (1.0 + err_variance)
            
            # Reasoning string
            reason = f"Equilibrium weight: {base_score:.3f}, Entropy conf: {conf_calib:.3f}, Payoff var: {err_variance:.3f}"
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reason
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt for ambiguity.
        """
        # 1. Meta-check (Tier B)
        meta_cap = self._meta_confidence(prompt, answer)
        
        if meta_cap < 0.3:
            return meta_cap
            
        # 2. Structural validation
        # If the answer shares structural features with the prompt, boost confidence slightly
        p_props = self._parse_text(prompt)
        a_props = self._parse_text(answer)
        
        # Intersection over Union of structural features (excluding specific numbers/words for general fit)
        struct_keys_p = {x for x in p_props if x[0] in ['negation', 'comparative', 'conditional', 'causal', 'ordinal', 'quantifier']}
        struct_keys_a = {x for x in a_props if x[0] in ['negation', 'comparative', 'conditional', 'causal', 'ordinal', 'quantifier']}
        
        if not struct_keys_p:
            # If prompt has no structure, rely on meta_cap
            return min(0.5, meta_cap)
            
        overlap = len(struct_keys_p & struct_keys_a)
        total = len(struct_keys_p | struct_keys_a)
        
        struct_score = overlap / total if total > 0 else 0.0
        
        # Base confidence on structural alignment, capped by meta-analysis
        raw_conf = 0.4 + (0.6 * struct_score) # Base 0.4, up to 1.0
        final_conf = min(raw_conf, meta_cap)
        
        # Never exceed 0.9 unless computation is definitive (hard to verify generically, so cap at 0.9)
        return min(final_conf, 0.9)