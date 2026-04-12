from typing import Dict, Tuple

"""
Bayesian-Neural-Metacognitive Reasoning Tool

Combines Bayesian belief updates with Hebbian plasticity and metacognitive monitoring.
Models reasoning as a dynamical system, tracking belief trajectory stability.
"""

import numpy as np
import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    def __init__(self):
        self.eta = 0.05  # Hebbian learning rate
        self.phi_cache = {}  # Predicate reliability weights
        self.belief_history = []  # For trajectory analysis
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        K = len(candidates)
        if K == 0:
            return []
        
        # Initialize uniform prior belief
        belief = np.ones(K) / K
        self.belief_history = [belief.copy()]
        
        # Parse structural predicates
        predicates = self._parse_predicates(prompt, candidates)
        
        # Process each predicate, updating belief dynamically
        for pred_name, satisfaction in predicates:
            belief = self._bayesian_update(belief, satisfaction, pred_name, candidates)
            self.belief_history.append(belief.copy())
            self._hebbian_adapt(belief, satisfaction, pred_name, candidates)
        
        # Compute trajectory stability (dynamics score)
        stability = self._trajectory_stability()
        
        # Compute NCD scores (max 15% weight)
        ncd_scores = np.array([self._ncd(prompt, c) for c in candidates])
        ncd_scores = 1 - (ncd_scores / (ncd_scores.max() + 1e-9))
        
        # Final score: 70% belief + 15% stability + 15% NCD
        final_scores = 0.70 * belief + 0.15 * stability + 0.15 * ncd_scores
        
        # Metacognitive confidence adjustment
        entropy = -np.sum(belief * np.log(belief + 1e-9))
        max_entropy = np.log(K)
        confidence_factor = 1 - (entropy / max_entropy)
        
        # Build ranked results
        results = []
        for i, cand in enumerate(candidates):
            reasoning = self._explain_score(i, predicates, belief[i], stability[i])
            results.append({
                "candidate": cand,
                "score": float(final_scores[i]),
                "reasoning": reasoning
            })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        # Check for epistemic issues first
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Evaluate with answer as single candidate
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.2
        
        base_conf = results[0]["score"]
        
        # Cap confidence based on structural evidence
        predicates = self._parse_predicates(prompt, [answer])
        if len(predicates) == 0:
            base_conf = min(base_conf, 0.25)  # Low conf if no structure matched
        
        # Never exceed 0.9 unless we have strong computational evidence
        return min(base_conf * meta_conf, 0.85)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect epistemic issues in the prompt"""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop))', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery .* a \b', p_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .* or \b', p_lower) and '?' in prompt:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prettiest)\b', p_lower):
            return 0.35
        
        # Unanswerable pattern
        if re.search(r'\b(impossible|cannot determine|insufficient)\b', p_lower):
            return 0.3
        
        return 1.0
    
    def _parse_predicates(self, prompt: str, candidates: List[str]) -> List[Tuple[str, np.ndarray]]:
        """Extract structural predicates and compute satisfaction vectors"""
        predicates = []
        K = len(candidates)
        
        # Negation detection
        neg_match = re.search(r'\bnot\b|\bno\b|n\'t\b', prompt.lower())
        if neg_match:
            sat = np.array([1.0 if re.search(r'\bnot\b|\bno\b|n\'t\b', c.lower()) else 0.3 for c in candidates])
            predicates.append(("negation", sat))
        
        # Comparative detection and numeric evaluation
        comp_match = re.search(r'(more|less|greater|smaller|larger) than|as .* as', prompt.lower())
        if comp_match:
            sat = self._evaluate_comparative(prompt, candidates)
            predicates.append(("comparative", sat))
        
        # Numeric extraction and comparison
        nums_prompt = re.findall(r'\b\d+\.?\d*\b', prompt)
        if nums_prompt:
            sat = self._evaluate_numeric(prompt, candidates, nums_prompt)
            predicates.append(("numeric", sat))
        
        # Conditional detection
        if re.search(r'\bif\b.*\bthen\b|\bunless\b', prompt.lower()):
            sat = self._evaluate_conditional(prompt, candidates)
            predicates.append(("conditional", sat))
        
        # Causal detection
        if re.search(r'\b(cause|lead to|result in|because)\b', prompt.lower()):
            sat = self._evaluate_causal(prompt, candidates)
            predicates.append(("causal", sat))
        
        # Ordering/temporal
        if re.search(r'\b(before|after|first|last|then|next)\b', prompt.lower()):
            sat = self._evaluate_ordering(prompt, candidates)
            predicates.append(("ordering", sat))
        
        return predicates
    
    def _evaluate_comparative(self, prompt: str, candidates: List[str]) -> np.ndarray:
        """Evaluate comparative predicates"""
        K = len(candidates)
        scores = np.ones(K) * 0.5
        
        # Extract numbers and compare
        p_nums = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', prompt)]
        for i, cand in enumerate(candidates):
            c_nums = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', cand)]
            if p_nums and c_nums:
                if 'less than' in prompt.lower() or 'smaller' in prompt.lower():
                    scores[i] = 0.9 if c_nums[0] < p_nums[0] else 0.1
                elif 'more than' in prompt.lower() or 'greater' in prompt.lower():
                    scores[i] = 0.9 if c_nums[0] > p_nums[0] else 0.1
        
        return scores
    
    def _evaluate_numeric(self, prompt: str, candidates: List[str], nums_prompt: List[str]) -> np.ndarray:
        """Evaluate numeric consistency"""
        K = len(candidates)
        scores = np.ones(K) * 0.5
        
        for i, cand in enumerate(candidates):
            c_nums = re.findall(r'\b\d+\.?\d*\b', cand)
            if c_nums:
                # Check if any prompt number appears in candidate
                overlap = set(nums_prompt) & set(c_nums)
                scores[i] = 0.8 if overlap else 0.3
        
        return scores
    
    def _evaluate_conditional(self, prompt: str, candidates: List[str]) -> np.ndarray:
        """Evaluate conditional logic"""
        K = len(candidates)
        scores = np.ones(K) * 0.5
        
        # Extract antecedent and consequent
        if_match = re.search(r'\bif\b(.+?)\bthen\b(.+)', prompt.lower())
        if if_match:
            antecedent = if_match.group(1).strip()
            consequent = if_match.group(2).strip()
            for i, cand in enumerate(candidates):
                c_lower = cand.lower()
                has_consequent = any(word in c_lower for word in consequent.split()[:3])
                scores[i] = 0.8 if has_consequent else 0.3
        
        return scores
    
    def _evaluate_causal(self, prompt: str, candidates: List[str]) -> np.ndarray:
        """Evaluate causal relationships"""
        K = len(candidates)
        scores = np.ones(K) * 0.5
        
        # Look for causal keywords in candidates
        for i, cand in enumerate(candidates):
            if re.search(r'\b(because|therefore|thus|hence|so)\b', cand.lower()):
                scores[i] = 0.7
        
        return scores
    
    def _evaluate_ordering(self, prompt: str, candidates: List[str]) -> np.ndarray:
        """Evaluate temporal/ordering predicates"""
        K = len(candidates)
        scores = np.ones(K) * 0.5
        
        for i, cand in enumerate(candidates):
            if re.search(r'\b(before|after|first|last|then)\b', cand.lower()):
                scores[i] = 0.7
        
        return scores
    
    def _bayesian_update(self, belief: np.ndarray, likelihood: np.ndarray, 
                        pred_name: str, candidates: List[str]) -> np.ndarray:
        """Update belief via Bayes rule with learned phi weights"""
        K = len(belief)
        weighted_likelihood = np.ones(K)
        
        for k in range(K):
            phi_key = (pred_name, k % 10)  # Modulo for cache efficiency
            phi = self.phi_cache.get(phi_key, 0.7)  # Default reliability
            weighted_likelihood[k] = phi ** likelihood[k]
        
        posterior = belief * weighted_likelihood
        norm = posterior.sum()
        if norm > 1e-9:
            posterior = posterior / norm
        else:
            posterior = belief
        
        return posterior
    
    def _hebbian_adapt(self, belief: np.ndarray, satisfaction: np.ndarray,
                      pred_name: str, candidates: List[str]):
        """Hebbian-like plasticity update of phi weights"""
        K = len(belief)
        b_mean = belief.mean()
        s_mean = satisfaction.mean()
        
        for k in range(K):
            phi_key = (pred_name, k % 10)
            phi = self.phi_cache.get(phi_key, 0.7)
            delta = self.eta * (belief[k] - b_mean) * (satisfaction[k] - s_mean)
            self.phi_cache[phi_key] = np.clip(phi + delta, 0.1, 0.99)
    
    def _trajectory_stability(self) -> np.ndarray:
        """Compute stability scores from belief trajectory (Lyapunov-like)"""
        if len(self.belief_history) < 2:
            return np.ones(len(self.belief_history[0])) * 0.5
        
        history = np.array(self.belief_history)
        K = history.shape[1]
        
        # Compute variance across trajectory (low variance = stable)
        variance = np.var(history, axis=0)
        stability = 1 / (1 + 10 * variance)
        
        # Convergence rate (how fast did belief stabilize)
        if len(history) > 3:
            recent_change = np.abs(history[-1] - history[-2]).sum()
            stability *= (1 - min(recent_change, 1.0))
        
        return stability
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance"""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.5
    
    def _explain_score(self, idx: int, predicates: List, belief: float, 
                      stability: float) -> str:
        """Generate reasoning explanation"""
        parts = [f"Belief={belief:.2f}"]
        if predicates:
            parts.append(f"Predicates={len(predicates)}")
        parts.append(f"Stability={stability:.2f}")
        return ", ".join(parts)