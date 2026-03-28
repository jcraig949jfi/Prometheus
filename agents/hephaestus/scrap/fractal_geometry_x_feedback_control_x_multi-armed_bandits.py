import zlib
import re
import math

class ReasoningTool:
    """
    Hierarchical Adaptive Bandit (HAB) Reasoning Tool.
    
    Mechanism:
    1. Fractal Geometry (IFS): The hypothesis space is recursively partitioned.
       We simulate this by generating a self-similar set of 'depth' levels based on 
       string features (length, char distribution). Each candidate is mapped to a 
       node in this fractal tree.
    2. Multi-Armed Bandits: Each node acts as an arm. The 'reward' is a structural 
       score derived from parsing the prompt/candidate for logical constraints 
       (negations, comparatives, numeric consistency).
    3. Feedback Control (PID): A PID controller regulates the exploration bonus.
       - Error = Instantaneous regret (difference between current best structural score 
         and the candidate's score).
       - Output (gamma) scales the exploration bonus added to the UCB term.
       - High regret -> High gamma -> Deep exploration (fractal zoom).
       - Low regret -> Low gamma -> Exploitation (pruning).
       
    Scoring Strategy:
    - Primary: Structural parsing (negations, comparatives, numerics).
    - Secondary: Fractal-depth adjusted UCB score.
    - Tiebreaker: NCD (Normalized Compression Distance).
    """

    def __init__(self):
        self.pid_kp = 0.5
        self.pid_ki = 0.1
        self.pid_kd = 0.1
        self.prev_error = 0.0
        self.integral = 0.0
        self.best_reward_history = []

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """Extract logical structure and score consistency."""
        score = 0.0
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # 1. Negation Handling
        negations = ['no', 'not', 'never', 'none', 'cannot', "n't"]
        p_has_neg = any(n in p_low for n in negations)
        c_has_neg = any(n in c_low for n in negations)
        
        if p_has_neg == c_has_neg:
            score += 2.0  # Consistency in negation
        else:
            score -= 2.0  # Penalty for mismatched negation
            
        # 2. Comparative/Numeric Detection
        nums_p = re.findall(r"[-+]?\d*\.?\d+", p_low)
        nums_c = re.findall(r"[-+]?\d*\.?\d+", c_low)
        
        if nums_p and nums_c:
            try:
                # Check if candidate preserves numeric order or magnitude logic
                # Simple heuristic: if prompt has numbers, candidate having numbers is good
                score += 1.5
                if len(nums_p) == len(nums_c):
                    score += 1.0
            except:
                pass
        elif not nums_p and not nums_c:
            score += 0.5 # Neutral
            
        # 3. Constraint Propagation (Subject-Object overlap as proxy)
        # If candidate repeats key non-stopwords from prompt, it's likely relevant
        common_words = set(p_low.split()) & set(c_low.split())
        stop_words = {'the', 'is', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        meaningful_overlap = len([w for w in common_words if w not in stop_words and len(w) > 2])
        score += meaningful_overlap * 0.5
        
        return score

    def _fractal_depth(self, s: str, max_depth: int = 4) -> int:
        """
        Simulate IFS partitioning. 
        Map string properties to a depth in a self-similar tree.
        """
        if not s:
            return 0
        h = hash(s)
        depth = 0
        # Recursive-like partitioning based on hash bits
        for i in range(max_depth):
            if (h >> i) & 1:
                depth += 1
            else:
                break
        return min(depth, max_depth)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denom = max(c1, c2)
        if denom == 0:
            return 0.0
        return (c12 - min(c1, c2)) / denom

    def _pid_control(self, regret: float) -> float:
        """PID controller to adjust exploration gain gamma."""
        self.integral += regret
        derivative = regret - self.prev_error
        gamma = (self.pid_kp * regret) + (self.pid_ki * self.integral) + (self.pid_kd * derivative)
        self.prev_error = regret
        self.best_reward_history.append(regret) # Track for history if needed
        
        # Clamp gamma to positive range for exploration bonus
        return max(0.1, min(5.0, gamma))

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        results = []
        base_scores = []
        
        # Phase 1: Compute structural scores (The "Reward" in Bandit)
        for cand in candidates:
            s_score = self._structural_score(prompt, cand)
            base_scores.append(s_score)
        
        best_base = max(base_scores) if base_scores else 0.0
        current_regret = 1.0 if not base_scores else (best_base - base_scores[0]) if base_scores else 1.0
        
        # Update PID state based on average regret of top candidate so far
        # In a real stream this would be sequential, here we simulate stability
        gamma = self._pid_control(abs(best_base - base_scores[0]) if base_scores else 1.0)

        for i, cand in enumerate(candidates):
            base = base_scores[i]
            
            # Fractal Depth (Hypothesis Scale)
            depth = self._fractal_depth(cand)
            
            # Exploration Bonus (UCB-like) scaled by PID gamma
            # Deeper nodes (higher depth) get more exploration bonus if gamma is high
            exploration_bonus = gamma * (depth / 4.0) * math.sqrt(math.log(len(candidates) + 2) / (i + 1))
            
            final_score = base + exploration_bonus
            
            # NCD as tiebreaker (only if scores are very close)
            # We pre-calculate a small NCD penalty for length mismatch to break ties
            ncd_val = self._compute_ncd(prompt, cand)
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural:{base:.2f} + Fractal_Exp:{exploration_bonus:.2f} (Depth:{depth})",
                "_ncd": ncd_val # Internal use for sorting
            })

        # Sort: Primary by score, Secondary by NCD (lower is better similarity wise, but we want relevance)
        # Actually, for NCD tiebreaker: if scores are equal, prefer lower NCD (more compressible together)
        results.sort(key=lambda x: (x['score'], -x['_ncd']), reverse=True)
        
        # Clean up and return
        final_output = []
        for r in results:
            final_output.append({
                "candidate": r["candidate"],
                "score": round(r["score"], 4),
                "reasoning": r["reasoning"]
            })
            
        return final_output

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural alignment."""
        # Reuse structural logic
        score = self._structural_score(prompt, answer)
        
        # Normalize heuristic: 
        # Base score can be negative. Map range [-5, 10] approx to [0, 1]
        # Strong structural match yields > 3.0
        normalized = 1.0 / (1.0 + math.exp(-0.5 * (score - 2.0)))
        
        # Boost if numeric constraints match
        nums_p = re.findall(r"\d+", prompt)
        nums_a = re.findall(r"\d+", answer)
        if nums_p and nums_a:
            if nums_p == nums_a:
                normalized = min(1.0, normalized + 0.2)
                
        return round(min(1.0, max(0.0, normalized)), 4)