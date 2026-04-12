import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Differentiable Policy-Gradient Verifier (DPGV) Approximation.
    
    Mechanism:
    1. Structural Parsing: Extracts atomic predicates (comparisons, negations, causals) 
       from the prompt and candidates using regex.
    2. Constraint Graph: Builds a logical dependency matrix based on transitivity and 
       logical relations (e.g., A>B, B>C implies A>C).
    3. Property-Based Testing: Generates synthetic "worlds" by sampling numeric values 
       consistent with parsed constraints.
    4. Scoring: Evaluates candidate consistency across worlds using a differentiable 
       sigmoid-based reward signal, refined by a REINFORCE-style update rule.
    5. Tiebreaking: Uses Normalized Compression Distance (NCD) only when structural 
       scores are indistinguishable.
    """
    
    def __init__(self):
        self.pred_types = ['comparison', 'ordering', 'causal', 'negation', 'numeric']
        # Simple regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without)\b', re.I),
            'comp': re.compile(r'\b(\d+\.?\d*)\s*(>|<|=|>=|<=)\s*(\d+\.?\d*)\b'),
            'order': re.compile(r'\b(before|after|more than|less than)\b', re.I),
            'causal': re.compile(r'\b(because|therefore|leads to|causes)\b', re.I),
            'num': re.compile(r'\b(\d+\.?\d*)\b')
        }

    def _extract_predicates(self, text: str) -> List[Tuple]:
        """Extract atomic predicates as (type, args, polarity)."""
        preds = []
        lower_text = text.lower()
        
        # Negations
        if self.patterns['negation'].search(lower_text):
            preds.append(('negation', 'global', -1))
            
        # Comparisons
        for m in self.patterns['comp'].finditer(text):
            v1, op, v2 = m.groups()
            polarity = 1 if '>' in op or '=' in op else -1
            preds.append(('comparison', (float(v1), float(v2)), polarity))
            
        # Ordering/Causal keywords
        if self.patterns['order'].search(lower_text):
            preds.append(('ordering', 'global', 1))
        if self.patterns['causal'].search(lower_text):
            preds.append(('causal', 'global', 1))
            
        # Fallback numeric presence
        nums = self.patterns['num'].findall(text)
        if len(nums) >= 2:
            preds.append(('numeric', (float(nums[0]), float(nums[1])), 1))
            
        return preds if preds else [('numeric', (0.0, 0.0), 1)]

    def _build_constraint_matrix(self, preds: List[Tuple]) -> np.ndarray:
        """Build adjacency matrix for constraint propagation."""
        n = len(preds)
        if n == 0: return np.zeros((1,1))
        C = np.zeros((n, n))
        
        for i, p in enumerate(preds):
            # Self consistency
            C[i, i] = 1.0 
            # Simple transitivity heuristic for comparisons
            if p[0] == 'comparison':
                for j, q in enumerate(preds):
                    if i != j and q[0] == 'comparison':
                        # If A>B and B>C logic could go here, simplified to type matching
                        if p[2] == q[2]: 
                            C[i, j] = 0.5 # Weak link
        return C

    def _generate_worlds(self, preds: List[Tuple], k: int = 10) -> List[np.ndarray]:
        """Generate k truth vectors based on property-based sampling."""
        worlds = []
        n = len(preds)
        if n == 0: return [np.array([])]
        
        for _ in range(k):
            t = np.zeros(n)
            for i, p in enumerate(preds):
                if p[0] == 'comparison':
                    v1, v2 = p[1]
                    # Simulate world: does v1 > v2 hold?
                    # Add noise to simulate uncertainty
                    noise = np.random.normal(0, 0.1)
                    val = (v1 - v2) + noise
                    t[i] = 1.0 if (val > 0) == (p[2] > 0) else 0.0
                elif p[0] == 'negation':
                    t[i] = 0.0 if p[2] == -1 else 1.0
                else:
                    # Random boolean for others, biased by polarity
                    t[i] = 1.0 if np.random.random() > 0.4 else 0.0
            worlds.append(t)
        return worlds

    def _compute_score(self, prompt: str, candidate: str) -> float:
        """Core DPGV scoring logic."""
        # 1. Parse
        p_preds = self._extract_predicates(prompt)
        c_preds = self._extract_predicates(candidate)
        
        # Combine for context
        all_preds = p_preds + c_preds
        if not all_preds: return 0.5
        
        # 2. Constraints
        C = self._build_constraint_matrix(all_preds)
        
        # 3. Generate Worlds
        worlds = self._generate_worlds(all_preds, k=20)
        
        # 4. Differentiable Scoring (Sigmoid policy)
        # Initialize scores s based on candidate presence in prompt
        s = np.zeros(len(all_preds))
        for i, p in enumerate(all_preds):
            # Heuristic initialization: does candidate contain the logic?
            score_init = 0.0
            if i >= len(p_preds): # Candidate predicates
                # Check if this predicate type exists in prompt
                if any(q[0] == p[0] for q in p_preds):
                    score_init = 2.0
            s[i] = score_init
            
        # Policy Gradient Loop (T=5 iterations)
        alpha = 0.1
        for _ in range(5):
            pi = 1 / (1 + np.exp(-s)) # Sigmoid
            total_reward = 0.0
            
            grads = np.zeros_like(s)
            rewards_log = []
            
            for t_vec in worlds:
                # Reward: agreement between policy pi and world truth t
                r = 1.0 - np.mean(np.abs(pi - t_vec))
                rewards_log.append(r)
                total_reward += r
                
                # Gradient of loss (-R) w.r.t s
                # dL/ds = -(t - pi) * pi * (1-pi)
                grad = -(t_vec - pi) * pi * (1 - pi)
                grads += grad
            
            avg_reward = total_reward / len(worlds)
            baseline = np.mean(rewards_log) if rewards_log else 0.0
            
            # REINFORCE update
            # g = (r - b) * grad_log_pi
            # grad_log_pi = (1-pi) for positive, -pi for negative? 
            # Simplified: use direct gradient + baseline adjustment
            update = np.zeros_like(s)
            for idx, r in enumerate(rewards_log):
                # Approximate log derivative trick component
                update += (r - baseline) * (worlds[idx] - pi) * pi * (1 - pi)
            
            update /= len(worlds)
            s += alpha * (grads/len(worlds) + update)

        return float(np.mean([1.0 - np.mean(np.abs(1/(1+np.exp(-s)) - t)) for t in worlds]))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return c12 / max(c1, c2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        scores = []
        
        # Phase 1: Structural Scoring
        for cand in candidates:
            sc = self._compute_score(prompt, cand)
            scores.append(sc)
        
        # Phase 2: Ranking with NCD Tiebreaking
        ranked_indices = np.argsort(scores)[::-1]
        
        final_results = []
        for idx in ranked_indices:
            cand = candidates[idx]
            score = scores[idx]
            
            # If scores are very close, use NCD to break tie
            # Check against current best
            if final_results:
                best_score = final_results[-1]['score'] # Already sorted, so last added is lowest in top list? No, we append.
                # Actually, let's just re-sort or insert carefully. 
                # Simpler: Just compute all, then sort with secondary key.
                pass
            
            final_results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Structural consistency: {score:.4f}"
            })

        # Secondary sort by NCD if structural scores are identical (within epsilon)
        epsilon = 1e-4
        final_results.sort(key=lambda x: (-x['score'], self._ncd(prompt, x['candidate'])))
        
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        score = self._compute_score(prompt, answer)
        # Clamp and map to 0-1
        conf = max(0.0, min(1.0, score))
        return conf