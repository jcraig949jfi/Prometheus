import zlib
import re
import math

class ReasoningTool:
    """
    Implements a self-correcting hypothesis testing loop using Falsificationism,
    Pragmatism, and Feedback Control concepts.
    
    Mechanism:
    1. Falsificationism (Bold Conjectures): Candidates are treated as hypotheses.
       We attempt to falsify them by checking for logical contradictions with the prompt
       (e.g., negation mismatches, constraint violations).
    2. Pragmatism (Utility): We evaluate the 'usefulness' of a candidate by its
       structural alignment with the prompt (keyword overlap, length appropriateness).
       This acts as a prior utility score.
    3. Feedback Control (PID-style Regulator): 
       - Error Signal: Difference between expected structural complexity and candidate.
       - Proportional: Immediate penalty for logical mismatches.
       - Integral: Accumulated bias against candidates that consistently fail simple checks.
       - Derivative: Dampening factor based on string volatility (noise).
       
    The final score is a weighted fusion where logical falsification acts as a hard gate,
    pragmatic utility boosts plausible candidates, and control terms adjust the threshold
    dynamically based on the 'error' landscape of the candidate set.
    """

    def __init__(self):
        # State for the feedback loop (Integral term accumulator)
        self._integral_error = 0.0
        self._last_error = 0.0
        # PID Constants
        self._kp = 1.5  # Proportional gain
        self._ki = 0.1  # Integral gain
        self._kd = 0.05 # Derivative gain
        
        # Keywords for pragmatic utility detection
        self._negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self._comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'}
        self._conditionals = {'if', 'then', 'unless', 'provided', 'when'}

    def _normalize(self, text):
        return text.lower().strip()

    def _get_tokens(self, text):
        return set(re.findall(r'\b\w+\b', self._normalize(text)))

    def _check_falsification(self, prompt, candidate):
        """
        Attempts to falsify the candidate based on logical constraints in the prompt.
        Returns a falsification score (0.0 = definitely falsified, 1.0 = survives).
        """
        p_tokens = self._get_tokens(prompt)
        c_tokens = self._get_tokens(candidate)
        score = 1.0

        # Check 1: Negation Contradiction
        # If prompt has strong negation context but candidate affirms without qualification
        has_prompt_neg = bool(p_tokens & self._negations)
        has_cand_neg = bool(c_tokens & self._negations)
        
        # Heuristic: If prompt asks "What is not X?" and candidate is just "X", penalize?
        # Instead, we look for direct contradiction patterns if we had NLI. 
        # Simplified: If prompt contains "not" and candidate is a single word affirmative, slight penalty.
        if has_prompt_neg and not has_cand_neg and len(c_tokens) == 1:
            score -= 0.3

        # Check 2: Constraint Propagation (Transitivity/Numbers)
        # Detect simple number comparisons if present
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        c_nums = re.findall(r'\d+\.?\d*', candidate)
        
        if p_nums and not c_nums:
            # Prompt has numbers, candidate ignores them (potential falsification via omission)
            # Only if the prompt implies a calculation or comparison
            if any(w in p_tokens for w in self._comparatives):
                score -= 0.4
        
        return max(0.0, score)

    def _compute_pragmatic_utility(self, prompt, candidate):
        """
        Evaluates practical payoff: alignment with prompt context.
        Returns utility score 0.0 to 1.0.
        """
        p_tokens = self._get_tokens(prompt)
        c_tokens = self._get_tokens(candidate)
        
        if not c_tokens:
            return 0.0

        # Overlap ratio
        intersection = p_tokens & c_tokens
        overlap_score = len(intersection) / (len(c_tokens) + 1e-6)
        
        # Length heuristic: Candidate shouldn't be wildly disproportionate
        len_ratio = min(len(candidate), len(prompt)) / (max(len(candidate), len(prompt)) + 1e-6)
        
        # Boost if candidate contains specific domain keywords found in prompt
        keyword_boost = 0.0
        if any(k in c_tokens for k in self._conditionals):
            keyword_boost = 0.1
            
        return min(1.0, (overlap_score * 0.6) + (len_ratio * 0.3) + keyword_boost)

    def _compute_ncd(self, s1, s2):
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            numerator = c12 - min(c1, c2)
            denominator = max(c1, c2)
            return numerator / (denominator + 1e-6)
        except:
            return 1.0

    def _pid_control_signal(self, error):
        """Calculates adjustment factor based on PID logic."""
        # Proportional
        p_term = self._kp * error
        
        # Integral
        self._integral_error += error
        i_term = self._ki * self._integral_error
        
        # Derivative
        d_term = self._kd * (error - self._last_error)
        self._last_error = error
        
        # Output is a gain modifier
        return p_term + i_term + d_term

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        results = []
        base_prompt = self._normalize(prompt)
        
        # Pre-calculate errors for the population to feed the controller
        # We treat "lack of overlap" as a proxy for error in this context
        population_errors = []
        for cand in candidates:
            util = self._compute_pragmatic_utility(prompt, cand)
            # Error is inverse of utility for the control loop
            population_errors.append(1.0 - util)
            
        avg_error = sum(population_errors) / len(population_errors) if population_errors else 1.0
        
        # PID Adjustment for the whole batch (Global gain tuning)
        gain_modifier = self._pid_control_signal(avg_error)
        # Clamp gain to avoid explosion
        gain_modifier = max(-0.5, min(0.5, gain_modifier))

        for cand in candidates:
            # 1. Falsification Check
            falsification_score = self._check_falsification(prompt, cand)
            
            # 2. Pragmatic Utility
            utility_score = self._compute_pragmatic_utility(prompt, cand)
            
            # 3. NCD Tiebreaker (Local similarity)
            ncd = self._compute_ncd(base_prompt, self._normalize(cand))
            ncd_score = 1.0 - ncd # Convert distance to similarity
            
            # Fusion Logic
            # Base score is utility, heavily penalized by falsification
            base_score = utility_score * falsification_score
            
            # Apply Control Loop Gain: 
            # If system error is high, we might boost exploration (utility) or penalize low-confidence
            # Here we modulate the threshold: high error -> stricter requirements (lower effective score)
            adjusted_score = base_score * (1.0 - gain_modifier * 0.5)
            
            # NCD as a tiebreaker/small boost for exact matches
            final_score = adjusted_score + (ncd_score * 0.1)
            
            # Ensure bounds
            final_score = max(0.0, min(1.0, final_score))
            
            reasoning = f"Falsification:{falsification_score:.2f}, Utility:{utility_score:.2f}, NCD:{ncd_score:.2f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Reuse evaluate logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]