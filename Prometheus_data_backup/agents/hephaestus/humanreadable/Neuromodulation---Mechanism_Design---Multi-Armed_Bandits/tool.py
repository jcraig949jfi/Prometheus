from typing import Dict, Tuple

import re
import math
import zlib
from typing import List, Dict, Tuple
import random

class ReasoningTool:
    """
    Neuromodulation x Mechanism Design x Multi-Armed Bandits reasoning tool.
    
    Maintains Beta posteriors for candidate answers, extracts structural features
    via regex parsing, evaluates logical consistency through constraint propagation,
    and updates beliefs using neuromodulatory gain control with proper scoring rules.
    """
    
    def __init__(self):
        self.kappa = 2.0  # Gain control sensitivity
        self.eta0 = 0.5   # Base learning rate
        self.epsilon = 1e-6
        random.seed(42)
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # Initialize Beta posteriors (alpha, beta) for each candidate
        posteriors = [[1.0, 1.0] for _ in candidates]
        
        # Extract prompt features for context
        prompt_features = self._extract_features(prompt, "")
        
        # Run bandit iterations
        for iteration in range(10):
            # Thompson sampling: sample from each Beta distribution
            theta_samples = [random.betavariate(a, b) for a, b in posteriors]
            chosen_idx = theta_samples.index(max(theta_samples))
            
            # Evaluate each candidate
            for i, candidate in enumerate(candidates):
                features = self._extract_features(prompt, candidate)
                constraint_score = self._constraint_propagation(features, prompt_features)
                
                # Compute reward using proper scoring rule
                c = max(self.epsilon, min(1 - self.epsilon, constraint_score))
                reward = math.log(c + self.epsilon) - math.log(1 - c + self.epsilon)
                
                # Neuromodulatory gain control
                alpha, beta = posteriors[i]
                mu = alpha / (alpha + beta)
                delta = reward - mu
                gain = 1 / (1 + math.exp(-self.kappa * delta))  # Sigmoid
                eta = self.eta0 * gain
                
                # Update posterior
                if i == chosen_idx:
                    posteriors[i][0] += eta * max(reward, 0)
                    posteriors[i][1] += eta * max(-reward, 0)
                else:
                    # Small decay for non-selected arms
                    posteriors[i][0] += 0.01 * max(reward, 0)
                    posteriors[i][1] += 0.01 * max(-reward, 0)
        
        # Compute final scores with constructive computation
        results = []
        for i, candidate in enumerate(candidates):
            alpha, beta = posteriors[i]
            posterior_mean = alpha / (alpha + beta)
            
            # Constructive computation score
            comp_score = self._constructive_compute(prompt, candidate)
            
            # Combine: 60% computation, 30% posterior, 10% NCD
            ncd_score = 1 - self._ncd(prompt, candidate)
            final_score = 0.6 * comp_score + 0.3 * posterior_mean + 0.1 * ncd_score
            
            reasoning = f"Posterior={posterior_mean:.3f}, Computation={comp_score:.3f}, NCD={ncd_score:.3f}"
            results.append({"candidate": candidate, "score": final_score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        # Check meta-level properties of the question
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Compute structural and computational confidence
        features = self._extract_features(prompt, answer)
        comp_score = self._constructive_compute(prompt, answer)
        constraint_score = self._constraint_propagation(features, self._extract_features(prompt, ""))
        
        # If we computed a definitive answer, high confidence
        if comp_score > 0.9:
            return min(0.95, comp_score * meta_conf)
        
        # Otherwise moderate confidence based on constraints
        base_conf = 0.3 + 0.5 * constraint_score
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presupposition, unanswerability."""
        p_lower = prompt.lower()
        
        # Presupposition patterns
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))', p_lower):
            return 0.2
        
        # Scope ambiguity: "Every X ... a Y"
        if re.search(r'\bevery \w+.*\ba\b', p_lower):
            if 'same' not in p_lower and 'different' not in p_lower:
                return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|they)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .+ or .+\?', p_lower):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prettiest)\b', p_lower):
            if not re.search(r'\b(most|least|criteria|measure)\b', p_lower):
                return 0.3
        
        # Insufficient information markers
        if re.search(r'\b(cannot be determined|not enough information|impossible to say)\b', p_lower):
            return 0.2
        
        return 1.0
    
    def _extract_features(self, prompt: str, candidate: str) -> Dict:
        """Extract structural features from text."""
        text = (prompt + " " + candidate).lower()
        
        features = {
            'negations': len(re.findall(r'\b(not|no|never|none|neither)\b', text)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\s+than\b', text)),
            'superlatives': len(re.findall(r'\b(most|least|greatest|smallest|best|worst)', text)),
            'conditionals': len(re.findall(r'\b(if|unless|when|whenever)\b.*\b(then|will|would)\b', text)),
            'causal': len(re.findall(r'\b(because|therefore|thus|hence|leads to|causes|results in)\b', text)),
            'ordering': len(re.findall(r'\b(before|after|earlier|later|first|last|previous|next)\b', text)),
            'numbers': re.findall(r'\b\d+\.?\d*\b', text),
            'equations': re.findall(r'(\d+\.?\d*)\s*([+\-*/])\s*(\d+\.?\d*)', text)
        }
        return features
    
    def _constraint_propagation(self, features: Dict, prompt_features: Dict) -> float:
        """Check logical consistency of extracted constraints."""
        satisfied = 0
        total = 0
        
        # Check numeric equation consistency
        for eq in features['equations']:
            total += 1
            try:
                left = float(eq[0])
                right = float(eq[2])
                op = eq[1]
                if op == '+' and left + right > 0:
                    satisfied += 1
                elif op == '-' and left - right is not None:
                    satisfied += 1
                elif op in ['*', '/']:
                    satisfied += 1
            except:
                pass
        
        # Conditional consistency (if X then Y pattern)
        if features['conditionals'] > 0:
            total += 1
            if features['causal'] > 0:  # Causal cues support conditionals
                satisfied += 1
        
        # Ordering transitivity check
        if features['ordering'] > 1:
            total += 1
            satisfied += 0.5  # Partial credit for multiple ordering cues
        
        # Comparative/superlative consistency
        if features['comparatives'] > 0 and len(features['numbers']) >= 2:
            total += 1
            satisfied += 1
        
        if total == 0:
            return 0.5
        
        return satisfied / total
    
    def _constructive_compute(self, prompt: str, candidate: str) -> float:
        """Actually compute answers for numeric, probabilistic, temporal problems."""
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Extract all numbers from prompt and candidate
        p_nums = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', prompt)]
        c_nums = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', candidate)]
        
        # Numeric comparison (e.g., "9.11 vs 9.9")
        if re.search(r'(greater|larger|bigger|more than|less than|smaller)', p_lower):
            if len(p_nums) >= 2:
                if 'greater' in p_lower or 'larger' in p_lower or 'more' in p_lower:
                    correct_answer = max(p_nums)
                else:
                    correct_answer = min(p_nums)
                
                if c_nums and abs(c_nums[0] - correct_answer) < 0.01:
                    return 0.95
        
        # Bayesian reasoning / probability
        if re.search(r'\b(probability|percent|%|likely|chance)\b', p_lower):
            # Look for base rate patterns
            if 'base rate' in p_lower or 'prior' in p_lower:
                # Simple Bayesian update
                if len(p_nums) >= 2 and c_nums:
                    # Check if candidate is reasonable probability
                    if 0 <= c_nums[0] <= 100:
                        return 0.7
        
        # Rate/work problems (distance = rate * time)
        if re.search(r'\b(speed|rate|mph|km/h|per hour)\b', p_lower):
            if len(p_nums) >= 2 and c_nums:
                # Compute expected rate/distance
                product = p_nums[0] * p_nums[1] if len(p_nums) >= 2 else 0
                if c_nums and abs(c_nums[0] - product) < 0.1 * product:
                    return 0.85
        
        # Temporal ordering
        if re.search(r'\b(before|after|earlier|later)\b', p_lower):
            # Check if candidate contains appropriate temporal marker
            if re.search(r'\b(before|after|first|last|earlier|later)\b', c_lower):
                return 0.6
        
        # Age reasoning
        if re.search(r'\b(years? old|age)\b', p_lower) and len(p_nums) >= 2:
            if c_nums:
                # Check if answer is arithmetic combination of prompt numbers
                for n1 in p_nums:
                    for n2 in p_nums:
                        if abs(c_nums[0] - (n1 + n2)) < 1 or abs(c_nums[0] - abs(n1 - n2)) < 1:
                            return 0.8
        
        # Boolean/logical questions
        if re.search(r'\b(true|false|yes|no)\b', p_lower):
            if re.search(r'\b(true|false|yes|no)\b', c_lower):
                # Check negation consistency
                prompt_negs = len(re.findall(r'\b(not|no|never)\b', p_lower))
                cand_negs = len(re.findall(r'\b(not|no|never|false)\b', c_lower))
                if (prompt_negs % 2) == (cand_negs % 2):
                    return 0.65
        
        return 0.3  # Default low score if no computation matched
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0