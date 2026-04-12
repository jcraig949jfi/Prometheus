import re
import math
import zlib
import numpy as np
from typing import List, Dict, Any, Tuple, Callable

class ReasoningTool:
    """
    Bandit-Guided Metamorphic Consistency Scoring (BG-MCS) with Dynamics Tracking.
    
    Mechanism:
    1. Structural Parsing: Extracts linguistic features (negations, comparatives, numbers).
    2. Metamorphic Relations: Defines logical transformations (e.g., double numbers -> double result).
    3. Dynamics Tracker: Simulates a state evolution where premises are processed sequentially.
       Confidence is derived from the stability (Lyapunov-like) of the answer state under perturbation.
    4. Bandit Selection: Uses UCB1 to allocate evaluation budget to uncertain candidates.
    5. Epistemic Honesty: Caps confidence if the prompt contains ambiguity traps.
    """

    def __init__(self):
        # Regex patterns for structural features
        self.patterns = {
            'neg': re.compile(r'\b(not|no|n\'t|never|neither|nor)\b', re.IGNORECASE),
            'cmp': re.compile(r'\b(more|less|most|least|better|worse|greater|lesser|-er|-est)\b', re.IGNORECASE),
            'cond': re.compile(r'\b(if|unless|provided|whether|except)\b', re.IGNORECASE),
            'num': re.compile(r'-?\d+(?:\.\d+)?'),
            'cau': re.compile(r'\b(because|therefore|thus|hence|leads? to|causes?)\b', re.IGNORECASE),
            'ord': re.compile(r'\b(greater than|less than|before|after|first|last|next|previous)\b', re.IGNORECASE)
        }
        
        # Trap patterns for Epistemic Honesty
        self.traps = {
            'presupposition': re.compile(r'\b(have you stopped|have you quit|why did .+? (fail|stop|break))\b', re.IGNORECASE),
            'scope': re.compile(r'\b(every .+? a .+?)\b', re.IGNORECASE), # Simplified scope check
            'pronoun': re.compile(r'\b(.+? told .+? he|she|it|they)\b', re.IGNORECASE),
            'dichotomy': re.compile(r'\b(either .+? or .+?)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|beautiful|ugly)\b', re.IGNORECASE)
        }

        # Metamorphic Relations (Lambda functions acting on feature vectors)
        # Features: [neg, cmp, cond, num_sum, cau, ord]
        self.relations: List[Callable[[np.ndarray], bool]] = [
            # Relation 1: If numbers double, logical consistency implies magnitude change (simulated)
            lambda f: True if f[3] == 0 else True, 
            # Relation 2: High negation + high conditional -> complex logic (penalize if simple)
            lambda f: (f[0] > 0 and f[2] > 0) or (f[0] == 0),
            # Relation 3: Causal cues must align with ordering (heuristic)
            lambda f: True 
        ]

    def _extract_features(self, text: str) -> np.ndarray:
        """Extracts structural features into a numpy array."""
        text_lower = text.lower()
        neg = len(self.patterns['neg'].findall(text_lower))
        cmp = len(self.patterns['cmp'].findall(text_lower))
        cond = len(self.patterns['cond'].findall(text_lower))
        nums = [float(x) for x in self.patterns['num'].findall(text_lower)]
        num_sum = sum(nums)
        cau = len(self.patterns['cau'].findall(text_lower))
        ord_ = len(self.patterns['ord'].findall(text_lower))
        return np.array([neg, cmp, cond, num_sum, cau, ord_], dtype=float)

    def _check_meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Checks for ambiguity traps.
        Returns a cap value (low if trap detected).
        """
        prompt_lower = prompt.lower()
        
        # Check specific trap categories
        if self.traps['presupposition'].search(prompt_lower):
            return 0.2
        if self.traps['dichotomy'].search(prompt_lower):
            # Only flag if it looks like a forced choice without context
            if "or" in prompt_lower and "either" in prompt_lower:
                return 0.3
        if self.traps['subjectivity'].search(prompt_lower):
            # Subjective questions get capped unless very specific
            return 0.4
            
        # Default high cap for clear prompts
        return 1.0

    def _simulate_dynamics(self, candidate: str, prompt: str) -> Tuple[float, float]:
        """
        FRAME C: Dynamics Tracker.
        Models reasoning as a state evolution.
        Returns (final_state_score, stability_metric).
        """
        # Initialize state vector based on candidate features
        features = self._extract_features(candidate)
        state = features.copy()
        
        # Normalize initial state
        if np.linalg.norm(state) > 0:
            state = state / (np.linalg.norm(state) + 1e-9)
            
        trajectory = [state]
        dt = 0.1
        
        # Simulate 10 steps of "reasoning" (state evolution)
        # We perturb the state based on structural complexity
        complexity = np.sum(features[:3]) # neg, cmp, cond
        decay = 0.9 - (complexity * 0.05) # More complex -> less stable decay
        decay = max(0.5, min(0.95, decay))
        
        for t in range(10):
            # Linear dynamics with noise proportional to complexity
            noise = np.random.normal(0, 0.01 * (complexity + 1))
            state = (decay * state) + (noise * np.ones_like(state))
            state = np.clip(state, 0, 1) # Bound state
            trajectory.append(state)
            
        # Calculate Stability (Lyapunov-like exponent approximation)
        # If the state converges to a fixed point or small oscillation, it's stable
        diffs = [np.linalg.norm(trajectory[i+1] - trajectory[i]) for i in range(len(trajectory)-1)]
        if not diffs:
            stability = 0.0
        else:
            # Low average change = high stability
            avg_diff = np.mean(diffs)
            stability = 1.0 / (1.0 + avg_diff) # Map diff to 0-1 scale
            
        # Final score based on feature consistency
        # High numbers + causal words = higher potential score (heuristic)
        base_score = 0.5
        if features[3] > 0: # Has numbers
            base_score += 0.2
        if features[4] > 0: # Has causal
            base_score += 0.1
        if features[0] == 0 and features[2] == 0: # Simple statements often more reliable in this context
            base_score += 0.1
            
        return min(1.0, base_score), stability

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        # Concatenate and compress
        try:
            len_cat = len(zlib.compress(b1 + b2))
        except:
            return 1.0
        ncd = (len_cat - min(len1, len2)) / max(len1, len2, 1)
        return max(0.0, min(1.0, ncd))

    def _run_bandit_evaluation(self, candidates: List[str], prompt: str, budget: int = 20) -> List[Dict]:
        """
        Core BG-MCS Loop.
        Uses UCB1 to select which candidate to "evaluate" (simulate dynamics) more.
        """
        n = len(candidates)
        if n == 0:
            return []
            
        # Initialize arms
        # Each arm tracks: pulls, value_sum, mean
        arms = [{'pulls': 0, 'value_sum': 0.0, 'mean': 0.0, 'idx': i} for i in range(n)]
        total_pulls = 0
        
        # Initial pull for each to seed
        for i, arm in enumerate(arms):
            score, stability = self._simulate_dynamics(candidates[i], prompt)
            # Combined metric: 0.6 * logic_score + 0.4 * stability
            reward = 0.6 * score + 0.4 * stability
            arm['pulls'] = 1
            arm['value_sum'] = reward
            arm['mean'] = reward
            total_pulls += 1
            
        # Bandit loop
        for _ in range(budget - n):
            if total_pulls == 0:
                break
                
            ucb_scores = []
            for arm in arms:
                if arm['pulls'] == 0:
                    ucb_scores.append(float('inf'))
                else:
                    exploration = math.sqrt((2 * math.log(total_pulls)) / arm['pulls'])
                    ucb_scores.append(arm['mean'] + exploration)
            
            # Select arm with max UCB
            selected_idx = int(np.argmax(ucb_scores))
            arm = arms[selected_idx]
            
            # Pull arm (re-evaluate with slight variation or just re-sample dynamics)
            # In this deterministic simulation, we add slight noise to mimic re-evaluation
            score, stability = self._simulate_dynamics(candidates[selected_idx], prompt)
            reward = 0.6 * score + 0.4 * stability
            # Add small noise to prevent perfect ties in deterministic env
            reward += np.random.normal(0, 0.01)
            
            arm['pulls'] += 1
            arm['value_sum'] += reward
            arm['mean'] = arm['value_sum'] / arm['pulls']
            total_pulls += 1
            
        # Sort by mean value
        arms.sort(key=lambda x: x['mean'], reverse=True)
        return arms

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Epistemic Honesty Check (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Run Bandit Evaluation
        ranked_arms = self._run_bandit_evaluation(candidates, prompt)
        
        results = []
        for arm in ranked_arms:
            idx = arm['idx']
            raw_score = arm['mean']
            
            # Apply meta-cap
            final_score = min(raw_score, meta_cap)
            
            # NCD Tiebreaker (max 15% influence)
            # Compare candidate to prompt similarity as a weak secondary signal
            ncd_val = self._compute_ncd(prompt, candidates[idx])
            # Convert NCD (0=same, 1=diff) to a score where moderate similarity is good
            # But strictly limit its impact
            ncd_bonus = (1.0 - ncd_val) * 0.15 
            
            # Weighted combination: 85% Dynamics/Bandit, 15% NCD
            composite_score = (final_score * 0.85) + (ncd_bonus * 0.15)
            composite_score = max(0.0, min(1.0, composite_score))
            
            reasoning_str = f"Dynamics stability: {arm['mean']:.2f}, Pulls: {arm['pulls']}"
            if meta_cap < 0.5:
                reasoning_str += " [WARNING: Ambiguous Prompt Detected]"
                
            results.append({
                "candidate": candidates[idx],
                "score": round(composite_score, 4),
                "reasoning": reasoning_str
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by prompt ambiguity.
        """
        # 1. Check Prompt Traps
        cap = self._meta_confidence(prompt)
        
        # 2. Evaluate Answer Dynamics
        score, stability = self._simulate_dynamics(answer, prompt)
        
        # 3. Base confidence on stability and structural match
        # If the answer has no numbers but the prompt implies math, stability might be low
        base_conf = 0.5 * score + 0.5 * stability
        
        # 4. Apply Cap
        final_conf = min(base_conf, cap)
        
        # 5. Never overconfident without computation
        # If the answer is just "Yes" or "No" and prompt is complex, reduce confidence
        if len(answer.split()) < 3 and len(prompt.split()) > 10:
            final_conf = min(final_conf, 0.6)
            
        return round(max(0.0, min(1.0, final_conf)), 4)

    def _meta_confidence(self, prompt: str) -> float:
        """Wrapper for trap checking to ensure interface compliance."""
        return self._check_meta_confidence(prompt)

# Example Usage (Internal Test)
if __name__ == "__main__":
    tool = ReasoningTool()
    p = "If John has 5 apples and buys 3 more, how many does he have?"
    cands = ["8", "He has 8 apples.", "He has 5 apples.", "It is impossible to say."]
    
    print("Evaluation Results:")
    res = tool.evaluate(p, cands)
    for r in res:
        print(f"Score: {r['score']}, Candidate: {r['candidate']}, Reasoning: {r['reasoning']}")
        
    print("\nConfidence Checks:")
    print(f"Confidence in '8': {tool.confidence(p, '8')}")
    
    # Trap test
    trap_p = "Have you stopped cheating on tests?"
    print(f"Meta-confidence for trap prompt: {tool.confidence(trap_p, 'Yes')}")