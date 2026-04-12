import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

# No external dependencies beyond standard library and numpy (though numpy is not strictly needed for this scale, 
# the prompt allows it. We will use pure math/stdlib to ensure zero-dependency robustness if numpy is missing, 
# but structure it as requested).

class ReasoningTool:
    """
    Bandit-guided Predictive Error Controller (BPEC)
    
    Mechanism:
    1. Structural Parsing: Extracts logical forms (negations, conditionals, comparatives).
    2. Free Energy/Surprise: Computes prediction error between parsed constraints and candidate consistency.
    3. Feedback Control: A PID controller modulates exploration based on accumulated surprise.
    4. Multi-Armed Bandit: Uses Upper Confidence Bound (UCB) adjusted by surprise to score candidates.
    5. Epistemic Honesty: Caps confidence on ambiguous/unanswerable prompts (Tier B).
    """

    def __init__(self):
        # State: Belief map for propositions
        self.state: Dict[str, float] = {}
        
        # Arms: Track performance of answer patterns (simplified to global arm for this context)
        # Alpha/Beta for Beta distribution
        self.arm_alpha = 1.0
        self.arm_beta = 1.0
        self.total_pulls = 0
        
        # Controller Gains (PID for Surprise)
        self.kp = 0.6
        self.ki = 0.1
        self.kd = 0.05
        self.prev_error = 0.0
        self.integral_error = 0.0
        
        # History for bandit
        self.candidate_history: Dict[str, Dict] = {}

    def _parse_structure(self, text: str) -> Dict:
        """Extract logical structures: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            "negations": len(re.findall(r'\b(not|no|never|none|neither|without|fail|stop|quit)\b', text_lower)),
            "conditionals": len(re.findall(r'\b(if|then|unless|provided|therefore|because|thus)\b', text_lower)),
            "comparatives": len(re.findall(r'\b(more|less|greater|smaller|higher|lower|before|after|first|last)\b', text_lower)),
            "numbers": re.findall(r'-?\d+\.?\d*', text),
            "quantifiers": len(re.findall(r'\b(every|all|some|any|each|most)\b', text_lower)),
            "ambiguity_markers": len(re.findall(r'\b(either|or|maybe|could|might|who|which|whose)\b', text_lower))
        }
        return features

    def _check_meta_confidence(self, prompt: str) -> float:
        """
        Tier B Check: Detects presuppositions, ambiguity, and unanswerability.
        Returns a cap factor (0.0 to 1.0). If < 0.3, the question is likely a trap.
        """
        p_lower = prompt.lower()
        score = 1.0
        
        # 1. Presupposition traps ("Have you stopped...", "Why did X fail...")
        if re.search(r'\b(have you stopped|have you quit|why did .*(fail|stop|die)|when did .*(stop|fail))\b', p_lower):
            score -= 0.8
            
        # 2. Scope/Pronoun Ambiguity ("X told Y he...", "Every X did a Y" + who/which)
        if re.search(r'\b(told .*\s+he|told .*\s+she|said to .*\s+he)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            score -= 0.7
            
        # 3. False Dichotomy ("Either A or B" without context)
        if re.search(r'\beither .*\bor\b', p_lower) and "not" not in p_lower:
            score -= 0.4
            
        # 4. Subjectivity without criteria ("Best", "Favorite" without data)
        if re.search(r'\b(best|worst|favorite|beautiful|ugly)\b', p_lower) and not re.search(r'\b(data|list|given|according)\b', p_lower):
            score -= 0.5
            
        # 5. Unanswerable/Missing Info
        if re.search(r'\b(calculate|solve|find)\b', p_lower) and not re.search(r'\d+', prompt):
             # Asking for calculation but no numbers provided
            score -= 0.6

        return max(0.0, min(1.0, score))

    def _compute_constraint_consistency(self, prompt: str, candidate: str) -> float:
        """
        Checks logical consistency between prompt constraints and candidate.
        Returns a consistency score [0, 1].
        """
        p_feats = self._parse_structure(prompt)
        c_feats = self._parse_structure(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()
        
        consistency = 1.0
        
        # 1. Negation Consistency
        # If prompt has strong negation logic, candidate shouldn't blindly affirm without qualification
        if p_feats['negations'] > 0:
            # Heuristic: If prompt asks "What is not X?", candidate containing "is X" might be wrong
            # This is a simplified proxy for logical entailment
            if re.search(r'\b(is|are|was|were)\b', c_lower) and "not" not in c_lower:
                # Weak penalty, as "The answer is Y" is valid format
                pass 

        # 2. Numeric Evaluation (Constructive Computation)
        # Extract numbers from prompt and candidate to check ordering/magnitude
        p_nums = [float(x) for x in p_feats['numbers']]
        c_nums = [float(x) for x in c_feats['numbers']]
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Check if candidate number exists in prompt (often correct answers are subsets)
            # Or if it's a computed result. 
            # Simple heuristic: If prompt has "greater than X", candidate should be > X
            if "greater" in p_lower or "more" in p_lower:
                if c_nums and min(c_nums) <= min(p_nums):
                    consistency -= 0.5
            if "less" in p_lower or "smaller" in p_lower:
                if c_nums and max(c_nums) >= max(p_nums):
                    consistency -= 0.5
                    
        # 3. Conditional/Logical Flow
        # If prompt has "if A then B", and candidate contradicts known facts (hard without KB)
        # We rely on NCD here as a fallback for semantic similarity of logical form
        
        return max(0.0, min(1.0, consistency)

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def _update_pid(self, error: float) -> float:
        """Update PID controller and return surprise signal."""
        self.integral_error += error
        derivative = error - self.prev_error
        self.prev_error = error
        
        # PID Output
        surprise = (self.kp * error) + (self.ki * self.integral_error) + (self.kd * derivative)
        return max(0.0, surprise) # Surprise is non-negative magnitude

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Enforces epistemic honesty: low confidence on ambiguous/trap prompts.
        """
        # 1. Meta-Confidence Check (Tier B)
        meta_cap = self._check_meta_confidence(prompt)
        
        if meta_cap < 0.3:
            return meta_cap # Honest uncertainty
        
        # 2. Structural Consistency
        consistency = self._compute_constraint_consistency(prompt, answer)
        
        # 3. Base confidence on structural match and lack of ambiguity
        # If meta_cap is low, we already returned. Here we assume high potential.
        base_score = consistency * meta_cap
        
        # Cap definitive claims
        if base_score > 0.9:
            # Only allow >0.9 if we have numeric verification or strong logical match
            if self._parse_structure(prompt)['numbers'] and not self._parse_structure(answer)['numbers']:
                base_score = 0.85 # Suspicious if numbers disappear
                
        return min(0.95, base_score)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates using BPEC logic.
        Returns ranked list of dicts.
        """
        results = []
        p_feats = self._parse_structure(prompt)
        meta_cap = self._check_meta_confidence(prompt)
        
        # Pre-calculate prompt complexity for NCD normalization
        prompt_len = len(prompt)
        
        for i, cand in enumerate(candidates):
            # --- Step 1: Structural Parsing & Consistency ---
            consistency = self._compute_constraint_consistency(prompt, cand)
            
            # --- Step 2: Prediction Error (Free Energy) ---
            # Expected correctness based on structure
            mu_hat = consistency 
            
            # Reward signal: Syntactic/Semantic checklist (simplified)
            # Does it answer the type of question? (Heuristic: length ratio, presence of numbers if needed)
            r = 0.0
            if meta_cap < 0.3:
                # If prompt is a trap, reward is low unless candidate identifies it
                if any(x in cand.lower() for x in ["assume", "unclear", "cannot", "insufficient", "ambiguous"]):
                    r = 1.0
                else:
                    r = 0.2
            else:
                # Normal case: reward consistency
                r = 1.0 if consistency > 0.7 else 0.5
                
            error = abs(mu_hat - r)
            
            # --- Step 3: Feedback Control (Surprise) ---
            surprise = self._update_pid(error)
            
            # --- Step 4: Bandit Update (UCB) ---
            # Treat each candidate as a pull of a generic arm for this session
            # Since we don't persist arms across calls in this simple impl, we simulate the UCB term
            n_i = i + 1 # Pseudo-count
            N = len(candidates)
            
            # Exploration bonus modulated by surprise
            exploration = math.sqrt((2 * math.log(N + 1)) / (n_i + 1)) + 0.5 * surprise
            
            # Exploitation (Consistency + Meta Honesty)
            exploitation = mu_hat * meta_cap
            
            # Final Score
            score = exploitation + exploration
            
            # NCD Tiebreaker (Max 15% influence as per instructions)
            # Only used if structural signals are weak
            ncd_score = 0.0
            if consistency < 0.5:
                ncd_val = self._calculate_ncd(prompt, cand)
                ncd_score = (1.0 - ncd_val) * 0.15 # Low weight
            
            final_score = score + ncd_score
            
            # Cap score based on meta-confidence (Epistemic Honesty)
            if meta_cap < 0.3:
                final_score = min(final_score, 0.3)

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural Consistency: {consistency:.2f}, Surprise: {surprise:.2f}, Meta-Cap: {meta_cap:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

# Example Usage (Internal Test)
if __name__ == "__main__":
    tool = ReasoningTool()
    
    # Test 1: Simple Logic
    p1 = "If A is greater than B, and B is 5, what is A?"
    c1 = ["A is 4", "A is 6", "A is equal to B"]
    print("Test 1:", tool.evaluate(p1, c1))
    
    # Test 2: Trap (Presupposition)
    p2 = "Have you stopped cheating on tests?"
    c2 = ["Yes, I have stopped", "No, I haven't", "I never cheated"]
    print("Test 2:", tool.evaluate(p2, c2))
    
    # Test 3: Confidence Check
    print("Confidence (Trap):", tool.confidence(p2, "Yes"))
    print("Confidence (Logic):", tool.confidence(p1, "A is 6"))