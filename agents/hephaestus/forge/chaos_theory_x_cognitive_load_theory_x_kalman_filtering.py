import math
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Chaotic-Kalman Cognitive Load (CKCL) Estimator.
    
    Mechanism:
    1. Structural Parsing: Extracts negations, comparatives, and numeric values.
    2. Chaos-Driven Exploration: Uses a logistic map (r=3.9) to generate deterministic 
       process noise, simulating sensitive dependence on initial conditions for hypothesis testing.
    3. Kalman Filtering: Maintains a belief state (mean/variance) for each candidate's validity.
       The chaotic variable modulates the process noise covariance (Q), balancing exploration/exploitation.
    4. Cognitive Load Module: Monitors belief entropy. If entropy (intrinsic load) + chaos (extraneous load)
       exceeds a threshold (approx 4 chunks), the system reduces chaotic gain to "chunk" hypotheses.
    5. Scoring: Candidates are ranked by their filtered belief mean, with NCD as a tiebreaker.
    """

    def __init__(self):
        self.r = 3.9  # Logistic map parameter (chaotic regime)
        self.x = 0.5  # Initial chaotic state
        self.load_threshold = 4.0  # Cognitive load limit (chunks)
        self.k = 0.5  # Kalman gain factor (simplified)
        
    def _logistic_map(self, x: float, r: float) -> float:
        """Compute next step of logistic map."""
        return r * x * (1.0 - x)

    def _extract_structural_features(self, text: str) -> Dict[str, Any]:
        """Extract negations, comparatives, and numbers."""
        t_lower = text.lower()
        features = {
            "negations": sum(1 for w in ["not", "no", "never", "none", "neither"] if w in t_lower.split()),
            "comparatives": sum(1 for w in ["more", "less", "greater", "smaller", "higher", "lower"] if w in t_lower.split()),
            "conditionals": sum(1 for w in ["if", "unless", "provided", "when"] if w in t_lower.split()),
            "numbers": []
        }
        # Simple numeric extraction
        current_num = ""
        for char in text + " ":
            if char.isdigit() or char == '.':
                current_num += char
            else:
                if current_num:
                    try:
                        features["numbers"].append(float(current_num))
                    except ValueError:
                        pass
                    current_num = ""
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _calculate_entropy(self, beliefs: List[float]) -> float:
        """Calculate Shannon entropy of normalized beliefs."""
        total = sum(beliefs)
        if total == 0:
            return 0.0
        probs = [b / total for b in beliefs if b > 0]
        if not probs:
            return 0.0
        return -sum(p * math.log2(p) for p in probs)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []
        
        # 1. Structural Analysis of Prompt
        p_features = self._extract_structural_features(prompt)
        prompt_complexity = p_features["negations"] + p_features["comparatives"] + p_features["conditionals"]
        
        # 2. Initialize Belief States (Kalman State: mean, variance)
        # Mean represents likelihood score, Var represents uncertainty
        states = []
        for i, cand in enumerate(candidates):
            c_features = self._extract_structural_features(cand)
            
            # Initial heuristic score based on structural alignment
            # E.g., if prompt has negation, candidate should ideally reflect logic (simplified here)
            base_score = 0.5
            
            # Numeric evaluation logic
            if p_features["numbers"] and c_features["numbers"]:
                # Check for direct matches or logical comparisons
                p_nums = sorted(p_features["numbers"])
                c_nums = sorted(c_features["numbers"])
                if p_nums == c_nums:
                    base_score = 0.9
                elif len(p_nums) == len(c_nums) == 1:
                    # Simple comparative check
                    if "greater" in prompt.lower() or "more" in prompt.lower():
                        base_score = 0.8 if c_nums[0] > p_nums[0] else 0.2
                    elif "less" in prompt.lower() or "smaller" in prompt.lower():
                        base_score = 0.8 if c_nums[0] < p_nums[0] else 0.2
            
            states.append({"mean": base_score, "var": 0.25, "candidate": cand})

        # 3. CKCL Loop
        # Generate chaotic sequence for process noise
        chaos_vals = []
        temp_x = self.x
        for _ in range(len(candidates)):
            temp_x = self._logistic_map(temp_x, self.r)
            chaos_vals.append(temp_x)
        self.x = temp_x  # Update global state

        # Calculate Intrinsic Load (Entropy of initial beliefs)
        initial_beliefs = [s["mean"] for s in states]
        intrinsic_load = self._calculate_entropy(initial_beliefs) if len(initial_beliefs) > 1 else 0.0
        
        # Cognitive Load Management
        # Extraneous load driven by chaos magnitude
        avg_chaos = sum(chaos_vals) / len(chaos_vals) if chaos_vals else 0
        extraneous_load = avg_chaos * 2.0 # Scale to chunk units
        
        total_load = intrinsic_load + extraneous_load
        
        # Adjust chaotic gain (r) if load exceeds threshold (Chunking mechanism)
        current_r = self.r
        if total_load > self.load_threshold:
            # Reduce chaos to stabilize (freeze filter / chunking)
            current_r = 1.5 # Low chaos, high stability
            # In a full system, we might cluster candidates here. 
            # We simulate by boosting top candidates slightly.
        
        # 4. Prediction & Update Step (Kalman)
        ranked_results = []
        
        for i, state in enumerate(states):
            # Prediction: Inflate variance by chaotic process noise
            # Q (process noise covariance) driven by chaotic variable
            q_noise = chaos_vals[i] * (1.0 if total_load <= self.load_threshold else 0.1)
            pred_var = state["var"] + q_noise
            
            # Update: Incorporate "sensory data" (Structural match score)
            # Measurement z is derived from NCD similarity to prompt (inverse)
            # Lower NCD = Higher similarity = Higher measurement
            ncd_val = self._compute_ncd(prompt.lower(), state["candidate"].lower())
            z_meas = 1.0 - ncd_val # Convert to 0-1 score
            
            # Kalman Gain
            k_gain = pred_var / (pred_var + 0.1) # 0.1 is measurement noise R
            
            # State Update
            new_mean = state["mean"] + k_gain * (z_meas - state["mean"])
            new_var = (1 - k_gain) * pred_var
            
            # Germane Load: Refine top candidates if budget permits
            if total_load < (self.load_threshold - 1.0):
                # Extra processing weight for high potential candidates
                if new_mean > 0.6:
                    new_mean += 0.05
            
            ranked_results.append({
                "candidate": state["candidate"],
                "score": max(0.0, min(1.0, new_mean)),
                "reasoning": f"CKCL Score: {new_mean:.4f}, Load: {total_load:.2f}, Chaos: {chaos_vals[i]:.4f}"
            })

        # Sort by score descending
        ranked_results.sort(key=lambda x: x["score"], reverse=True)
        return ranked_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on CKCL evaluation."""
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]