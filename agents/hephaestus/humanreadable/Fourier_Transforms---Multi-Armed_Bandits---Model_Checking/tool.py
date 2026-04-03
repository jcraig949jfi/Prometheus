from typing import Dict, Tuple

import re
import zlib
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Hybrid reasoning tool combining:
    - Fourier spectral analysis of token sequences for syntactic pattern detection
    - Multi-armed bandit (UCB) for efficient candidate exploration
    - Model checking via finite automata for constraint verification
    - Constructive computation for numeric/probabilistic/temporal problems
    """
    
    def __init__(self):
        self.vocab = {}
        self.vocab_idx = 0
        self.arm_counts = defaultdict(int)
        self.arm_rewards = defaultdict(float)
        self.total_evals = 0
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        # Reset bandit state for new evaluation
        self.arm_counts.clear()
        self.arm_rewards.clear()
        self.total_evals = 0
        self.vocab.clear()
        self.vocab_idx = 0
        
        # Parse constraints and structure from prompt
        constraints = self._parse_constraints(prompt)
        prompt_spectrum = self._get_spectrum(prompt)
        
        # Try constructive computation first
        computed_answer = self._compute_answer(prompt)
        
        # UCB bandit evaluation
        results = []
        for _ in range(min(len(candidates) * 3, 20)):  # Multiple rounds
            arm_idx = self._select_arm_ucb(len(candidates))
            candidate = candidates[arm_idx]
            
            # Compute spectral similarity
            cand_spectrum = self._get_spectrum(candidate)
            spectral_sim = self._spectral_similarity(prompt_spectrum, cand_spectrum)
            
            # Model checking
            sat_score = self._check_constraints(candidate, constraints)
            
            # Constructive matching
            comp_score = self._match_computed(candidate, computed_answer)
            
            # Structural alignment
            struct_score = self._structural_match(prompt, candidate, constraints)
            
            # NCD (max 15%)
            ncd = self._ncd(prompt, candidate)
            ncd_score = 1.0 - ncd
            
            # Combine: 40% computation, 30% structural, 20% spectral*sat, 10% NCD
            reward = 0.4 * comp_score + 0.3 * struct_score + 0.2 * (spectral_sim * sat_score) + 0.1 * ncd_score
            
            self._update_arm(arm_idx, reward)
            self.total_evals += 1
        
        # Final ranking
        for i, candidate in enumerate(candidates):
            avg_reward = self.arm_rewards[i] / max(self.arm_counts[i], 1)
            reasoning = f"Spectral:{self._spectral_similarity(prompt_spectrum, self._get_spectrum(candidate)):.2f} Constraints:{self._check_constraints(candidate, constraints):.2f} Computation:{self._match_computed(candidate, computed_answer):.2f}"
            results.append({"candidate": candidate, "score": avg_reward, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        # Meta-confidence check for epistemic honesty
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        constraints = self._parse_constraints(prompt)
        computed = self._compute_answer(prompt)
        
        # If we computed an answer and it matches, high confidence
        if computed is not None:
            match = self._match_computed(answer, computed)
            if match > 0.8:
                return min(0.85, meta_conf)  # Cap at 0.85
        
        # Structural confidence
        struct = self._structural_match(prompt, answer, constraints)
        sat = self._check_constraints(answer, constraints)
        
        if len(constraints) > 0 and sat > 0.9:
            return min(0.75, meta_conf)
        
        if struct > 0.7:
            return min(0.6, meta_conf)
        
        return min(0.4, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presuppositions, unanswerable questions"""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop)|when did .* stop)', p):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery \w+.*\ba\b', p):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).*\?', p) and 'who' in p:
            return 0.2
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p) and not re.search(r'\bonly\b', p):
            return 0.25
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful|ugliest)\b', p) and not re.search(r'\b(most|least|highest|lowest)\b.*\d', p):
            return 0.3
        
        # Unanswerable: "not enough information"
        if re.search(r'\b(cannot be determined|not enough|insufficient)', p):
            return 0.2
        
        return 1.0
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        tokens = re.findall(r'\w+|[^\w\s]', text.lower())
        return tokens
    
    def _get_spectrum(self, text: str) -> np.ndarray:
        """Convert text to Fourier spectrum magnitude"""
        tokens = self._tokenize(text)
        if not tokens:
            return np.zeros(10)
        
        # Build vocabulary on the fly
        for token in tokens:
            if token not in self.vocab:
                self.vocab[token] = self.vocab_idx
                self.vocab_idx += 1
        
        # Convert to index sequence
        indices = [self.vocab[t] for t in tokens]
        
        # Pad/truncate to fixed length
        max_len = 64
        if len(indices) < max_len:
            indices += [0] * (max_len - len(indices))
        else:
            indices = indices[:max_len]
        
        # Apply FFT
        signal = np.array(indices, dtype=float)
        spectrum = np.fft.rfft(signal)
        magnitude = np.abs(spectrum)
        
        return magnitude
    
    def _spectral_similarity(self, s1: np.ndarray, s2: np.ndarray) -> float:
        """Compute spectral similarity"""
        norm1 = np.linalg.norm(s1)
        norm2 = np.linalg.norm(s2)
        if norm1 + norm2 == 0:
            return 0.5
        diff = np.linalg.norm(s1 - s2)
        return 1.0 - (diff / (norm1 + norm2))
    
    def _parse_constraints(self, prompt: str) -> Dict:
        """Extract logical constraints from prompt"""
        p = prompt.lower()
        constraints = {
            'negations': re.findall(r'\b(not|no|never|neither)\s+(\w+)', p),
            'comparatives': re.findall(r'(\w+)\s+(greater|less|more|fewer)\s+than\s+(\w+)', p),
            'conditionals': re.findall(r'if\s+(.*?)\s+then\s+(.*?)(?:\.|,|$)', p),
            'numbers': re.findall(r'-?\d+\.?\d*', p),
            'ordering': re.findall(r'(\w+)\s+(before|after|precedes)\s+(\w+)', p),
        }
        return constraints
    
    def _check_constraints(self, candidate: str, constraints: Dict) -> float:
        """Model checking: does candidate satisfy constraints?"""
        c = candidate.lower()
        score = 1.0
        checks = 0
        
        # Check negations
        for neg_word, obj in constraints['negations']:
            checks += 1
            if obj in c and neg_word not in c:
                score *= 0.5
        
        # Check ordering
        for a, rel, b in constraints['ordering']:
            checks += 1
            idx_a = c.find(a)
            idx_b = c.find(b)
            if idx_a != -1 and idx_b != -1:
                if rel == 'before' and idx_a > idx_b:
                    score *= 0.5
                elif rel == 'after' and idx_a < idx_b:
                    score *= 0.5
        
        return score if checks > 0 else 0.8
    
    def _compute_answer(self, prompt: str):
        """Constructive computation: actually solve the problem"""
        p = prompt.lower()
        
        # Extract numbers
        numbers = [float(x) for x in re.findall(r'-?\d+\.?\d*', prompt)]
        
        # Numeric comparison: "is X > Y"
        if re.search(r'is\s+(\d+\.?\d*)\s+(greater|less|more)\s+than\s+(\d+\.?\d*)', p):
            match = re.search(r'is\s+(\d+\.?\d*)\s+(greater|less|more)\s+than\s+(\d+\.?\d*)', p)
            a, rel, b = float(match.group(1)), match.group(2), float(match.group(3))
            if 'greater' in rel or 'more' in rel:
                return 'yes' if a > b else 'no'
            else:
                return 'yes' if a < b else 'no'
        
        # Simple arithmetic
        if re.search(r'(\d+\.?\d*)\s*\+\s*(\d+\.?\d*)', p):
            match = re.search(r'(\d+\.?\d*)\s*\+\s*(\d+\.?\d*)', p)
            return str(float(match.group(1)) + float(match.group(2)))
        
        # Bayesian base rate
        if 'base rate' in p or 'probability' in p:
            if len(numbers) >= 3:
                # Simple Bayes: P(A|B) = P(B|A) * P(A) / P(B)
                return str(round(numbers[0] * numbers[1] / max(numbers[2], 0.001), 3))
        
        return None
    
    def _match_computed(self, candidate: str, computed) -> float:
        """How well does candidate match computed answer?"""
        if computed is None:
            return 0.5
        
        c = candidate.lower().strip()
        comp = str(computed).lower().strip()
        
        # Exact match
        if comp in c or c in comp:
            return 1.0
        
        # Numeric tolerance
        try:
            c_nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', candidate)]
            comp_nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', str(computed))]
            if c_nums and comp_nums:
                if abs(c_nums[0] - comp_nums[0]) < 0.01:
                    return 0.95
        except:
            pass
        
        return 0.3
    
    def _structural_match(self, prompt: str, candidate: str, constraints: Dict) -> float:
        """Structural alignment between prompt and candidate"""
        p_tokens = set(self._tokenize(prompt))
        c_tokens = set(self._tokenize(candidate))
        
        if not p_tokens:
            return 0.5
        
        overlap = len(p_tokens & c_tokens) / len(p_tokens)
        
        # Penalize if negation mismatch
        p_neg = bool(re.search(r'\b(not|no|never)\b', prompt.lower()))
        c_neg = bool(re.search(r'\b(not|no|never)\b', candidate.lower()))
        if p_neg != c_neg:
            overlap *= 0.7
        
        return overlap
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance"""
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2)
    
    def _select_arm_ucb(self, n_arms: int) -> int:
        """UCB arm selection"""
        if self.total_evals < n_arms:
            return self.total_evals  # Explore each arm once
        
        best_ucb = -1
        best_arm = 0
        for i in range(n_arms):
            avg = self.arm_rewards[i] / max(self.arm_counts[i], 1)
            bonus = np.sqrt(2 * np.log(self.total_evals + 1) / max(self.arm_counts[i], 1))
            ucb = avg + bonus
            if ucb > best_ucb:
                best_ucb = ucb
                best_arm = i
        return best_arm
    
    def _update_arm(self, arm: int, reward: float):
        """Update bandit statistics"""
        self.arm_counts[arm] += 1
        self.arm_rewards[arm] += reward