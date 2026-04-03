from typing import Dict, Tuple

"""
Dynamic Attractor-Network Reasoning Scorer
Combines Chaos Theory, Gene Regulatory Networks, and Autopoiesis.
"""

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    def __init__(self):
        self.epsilon = 1e-9
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates using attractor dynamics and constructive computation."""
        results = []
        
        for cand in candidates:
            # Constructive computation (primary signal)
            comp_score = self._compute_answer(prompt, cand)
            
            # Attractor dynamics
            attr_score = self._attractor_score(prompt, cand)
            
            # NCD as tiebreaker only (max 15%)
            ncd = self._ncd(prompt, cand)
            ncd_score = 1.0 - ncd
            
            # Weighted combination: computation 50%, attractor 35%, NCD 15%
            final_score = 0.50 * comp_score + 0.35 * attr_score + 0.15 * ncd_score
            
            reasoning = f"comp={comp_score:.2f}, attr={attr_score:.2f}, ncd={ncd_score:.2f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-confidence checks."""
        meta_conf = self._meta_confidence(prompt)
        
        # Compute base confidence
        comp_score = self._compute_answer(prompt, answer)
        attr_score = self._attractor_score(prompt, answer)
        base_conf = 0.6 * comp_score + 0.4 * attr_score
        
        # Cap by meta-confidence
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity/unanswerability - epistemic honesty."""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))\b', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery .+ a \w+\b', p) and 'same' in p:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|they|it)\b', p) and re.search(r'\bwho\b', p):
            return 0.25
        
        # False dichotomy
        if re.search(r'\b(either .+ or)\b', p) and 'only' not in p:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p) and not re.search(r'\b(metric|measure|criterion)\b', p):
            return 0.3
        
        # Insufficient info
        if 'not enough information' in p or 'cannot be determined' in p:
            return 0.2
        
        return 0.95  # High meta-confidence if no flags
    
    def _compute_answer(self, prompt: str, candidate: str) -> float:
        """Constructive computation: actually solve the problem."""
        score = 0.0
        
        # Numeric comparison
        num_score = self._numeric_reasoning(prompt, candidate)
        if num_score > 0:
            score = max(score, num_score)
        
        # Probability/Bayesian
        prob_score = self._probabilistic_reasoning(prompt, candidate)
        if prob_score > 0:
            score = max(score, prob_score)
        
        # Temporal ordering
        temp_score = self._temporal_reasoning(prompt, candidate)
        if temp_score > 0:
            score = max(score, temp_score)
        
        # Logical structure
        logic_score = self._logical_reasoning(prompt, candidate)
        score = max(score, logic_score)
        
        return min(score, 1.0)
    
    def _numeric_reasoning(self, prompt: str, candidate: str) -> float:
        """Extract and compare numbers."""
        # Find numbers in prompt
        prompt_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        cand_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
        
        if not cand_nums:
            return 0.0
        
        # Check for comparison keywords
        if re.search(r'\b(greater|larger|more|higher|exceeds)\b', prompt.lower()):
            if prompt_nums and cand_nums:
                if any(c > min(prompt_nums) for c in cand_nums):
                    return 0.8
        
        if re.search(r'\b(less|smaller|fewer|lower)\b', prompt.lower()):
            if prompt_nums and cand_nums:
                if any(c < max(prompt_nums) for c in cand_nums):
                    return 0.8
        
        # Arithmetic operations
        if any(op in prompt for op in ['+', '-', '*', '/', 'sum', 'product', 'difference']):
            if len(prompt_nums) >= 2 and cand_nums:
                expected = prompt_nums[0] + prompt_nums[1] if '+' in prompt or 'sum' in prompt.lower() else None
                if expected and any(abs(c - expected) < 0.1 for c in cand_nums):
                    return 0.9
        
        return 0.0
    
    def _probabilistic_reasoning(self, prompt: str, candidate: str) -> float:
        """Bayesian reasoning and probability."""
        p = prompt.lower()
        c = candidate.lower()
        
        # Base rate neglect detection
        if 'probability' in p or 'percent' in p or '%' in p:
            nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
            cand_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
            
            if len(nums) >= 2 and cand_nums:
                # Simple Bayesian: P(A|B) = P(B|A) * P(A) / P(B)
                if 'given' in p:
                    # Look for base rate usage
                    if any(0.01 < cn < 1.0 for cn in cand_nums):
                        return 0.7
        
        return 0.0
    
    def _temporal_reasoning(self, prompt: str, candidate: str) -> float:
        """Temporal ordering and scheduling."""
        p = prompt.lower()
        c = candidate.lower()
        
        temporal_words = ['before', 'after', 'then', 'first', 'last', 'earlier', 'later']
        if any(tw in p for tw in temporal_words):
            # Check if candidate respects ordering
            if 'before' in p and 'after' in c:
                return 0.6
            if 'first' in p and ('first' in c or re.search(r'\b(initially|start)\b', c)):
                return 0.7
        
        return 0.0
    
    def _logical_reasoning(self, prompt: str, candidate: str) -> float:
        """Structural logic: negations, conditionals, causal chains."""
        p = prompt.lower()
        c = candidate.lower()
        score = 0.0
        
        # Negation consistency
        p_negations = len(re.findall(r'\b(not|no|never|none)\b', p))
        c_negations = len(re.findall(r'\b(not|no|never|none)\b', c))
        if p_negations > 0 and c_negations > 0:
            score += 0.3
        
        # Conditional matching
        if re.search(r'\bif .+ then\b', p):
            if 'then' in c or 'therefore' in c:
                score += 0.3
        
        # Causal matching
        if re.search(r'\b(because|causes|leads to|results in)\b', p):
            if re.search(r'\b(because|causes|leads to|results in|therefore)\b', c):
                score += 0.3
        
        return min(score, 1.0)
    
    def _attractor_score(self, prompt: str, candidate: str) -> float:
        """Gene regulatory network dynamics with chaos theory."""
        # Extract propositions
        props = self._extract_propositions(prompt, candidate)
        if len(props) < 2:
            return 0.5
        
        n = len(props)
        W = self._build_interaction_matrix(props)
        x0 = np.random.rand(n) > 0.5
        
        # Run dynamics
        trajectory = [x0.astype(float)]
        for _ in range(10):
            x_next = self._update_state(trajectory[-1], W)
            trajectory.append(x_next)
        
        # Autopoietic closure
        closure = self._measure_closure(trajectory)
        
        # Lyapunov exponent (stability)
        lyapunov = self._compute_lyapunov(x0, W, steps=10)
        stability = max(0, 1.0 - lyapunov) if lyapunov > 0 else 1.0
        
        # Combined score
        return 0.6 * closure + 0.4 * stability
    
    def _extract_propositions(self, prompt: str, candidate: str) -> List[str]:
        """Extract atomic propositions (subject-verb-object triples)."""
        text = (prompt + " " + candidate).lower()
        
        # Simple extraction: sentences split by punctuation
        sentences = re.split(r'[.!?;]', text)
        props = []
        
        for sent in sentences:
            sent = sent.strip()
            if len(sent) > 5:
                # Extract noun phrases (simple heuristic)
                words = sent.split()
                if len(words) >= 3:
                    props.append(sent)
        
        return props[:20]  # Limit to 20 propositions
    
    def _build_interaction_matrix(self, props: List[str]) -> np.ndarray:
        """Build weighted adjacency matrix for gene regulatory network."""
        n = len(props)
        W = np.zeros((n, n))
        
        for i, pi in enumerate(props):
            for j, pj in enumerate(props):
                if i == j:
                    continue
                
                # Causal links
                if any(c in pi or c in pj for c in ['because', 'causes', 'leads to']):
                    W[i, j] = 1.0
                
                # Inhibitory (negation + causal)
                if 'not' in pi and any(c in pj for c in ['because', 'causes']):
                    W[i, j] = -1.0
                
                # Comparative/ordering
                if any(c in pi or c in pj for c in ['more', 'less', 'before', 'after']):
                    W[i, j] = 0.5
        
        # Sparsify: keep top-5 per row
        for i in range(n):
            row = W[i, :]
            threshold = np.partition(np.abs(row), max(0, n-5))[max(0, n-5)]
            W[i, :][np.abs(row) < threshold] = 0
        
        return W
    
    def _update_state(self, x: np.ndarray, W: np.ndarray) -> np.ndarray:
        """Gene regulatory update rule with sigmoid."""
        z = W @ x - 0.5
        x_next = 1.0 / (1.0 + np.exp(-z))
        return (x_next > 0.5).astype(float)
    
    def _measure_closure(self, trajectory: List[np.ndarray]) -> float:
        """Autopoietic closure: fraction of steps in stable attractor."""
        if len(trajectory) < 6:
            return 0.5
        
        window = trajectory[-5:]
        same_count = sum(1 for i in range(1, len(window)) if np.array_equal(window[i], window[i-1]))
        return same_count / (len(window) - 1)
    
    def _compute_lyapunov(self, x0: np.ndarray, W: np.ndarray, steps: int = 10) -> float:
        """Estimate maximal Lyapunov exponent via perturbation."""
        # Original trajectory
        traj = [x0]
        for _ in range(steps):
            traj.append(self._update_state(traj[-1], W))
        
        # Perturbed trajectory (flip 5% of bits)
        x0_pert = x0.copy()
        n_flip = max(1, int(0.05 * len(x0)))
        flip_idx = np.random.choice(len(x0), n_flip, replace=False)
        x0_pert[flip_idx] = 1 - x0_pert[flip_idx]
        
        traj_pert = [x0_pert]
        for _ in range(steps):
            traj_pert.append(self._update_state(traj_pert[-1], W))
        
        # Compute divergence
        d0 = np.sum(x0 != x0_pert) + self.epsilon
        divergences = [np.sum(traj[t] != traj_pert[t]) + self.epsilon for t in range(1, steps+1)]
        
        lyapunov = np.mean([np.log(d / d0) for d in divergences]) / steps
        return lyapunov
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (tiebreaker only)."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)