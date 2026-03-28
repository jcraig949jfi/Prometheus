import re
import zlib
import math

class ReasoningTool:
    """
    A self-compressing predictive coding network approximation.
    
    Mechanism:
    1. Kolmogorov Complexity: Approximated via zlib compression length of the 
       combined prompt+answer. Shorter description length = higher prior probability.
    2. Hebbian Learning: Implemented as a co-activation score. We strengthen the 
       'connection' (score) if key structural tokens (negations, comparatives, numbers) 
       in the prompt are semantically preserved or correctly addressed in the candidate.
       Delta w ~ pre (prompt feature) * post (candidate feature).
    3. Mechanism Design: An internal scoring rule that penalizes candidates which 
       reduce complexity (shortness) but fail to activate specific structural constraints 
       detected in the prompt. This makes 'truthful' (structurally consistent) reporting 
       the dominant strategy over 'lazy' (short but ignoring constraints) reporting.
    
    The system minimizes description length subject to incentive-compatible constraint satisfaction.
    """

    def __init__(self):
        # Structural keywords that trigger Hebbian co-activation checks
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'larger', 'shorter', 'better', 'worse', 'higher', 'lower'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided', 'when'}
        self.quantifiers = {'all', 'some', 'every', 'each', 'any', 'most', 'few'}

    def _tokenize(self, text):
        """Simple tokenizer: lowercase, split non-alphanumeric."""
        return re.findall(r'[a-z0-9]+', text.lower())

    def _extract_numbers(self, text):
        """Extract floating point numbers from text."""
        return [float(x) for x in re.findall(r'-?\d+\.?\d*', text)]

    def _check_structure(self, prompt, candidate):
        """
        Hebbian-style structural consistency check.
        Returns a score based on co-activation of logical structures.
        """
        p_tokens = set(self._tokenize(prompt))
        c_tokens = set(self._tokenize(candidate))
        score = 0.0
        active_features = 0

        # Check Negation Consistency
        # If prompt has negation, candidate should reflect it (or explicitly deny it)
        has_p_neg = bool(p_tokens & self.negations)
        has_c_neg = bool(c_tokens & self.negations)
        if has_p_neg:
            active_features += 1
            # Reward if candidate acknowledges negation, or if the candidate is a direct number/logic op
            # Simple heuristic: if prompt says "not", candidate shouldn't be blindly positive unless it says "no"
            if has_c_neg or len(c_tokens) < 5: 
                score += 1.0
            else:
                # Penalty for ignoring negation in long answers
                score -= 0.5
        elif has_c_neg and not has_p_neg:
            # Spontaneous negation without prompt cause
            score -= 0.2

        # Check Comparative Consistency
        has_p_comp = bool(p_tokens & self.comparatives)
        has_c_comp = bool(c_tokens & self.comparatives)
        if has_p_comp:
            active_features += 1
            if has_c_comp:
                score += 1.0
            # If prompt compares, short answers like "A" are okay, but "Yes" is ambiguous
            elif len(c_tokens) <= 3:
                score += 0.5 

        # Check Conditional/Logic
        has_p_cond = bool(p_tokens & self.conditionals)
        if has_p_cond:
            active_features += 1
            # Candidate should ideally contain conditional logic words or be a specific deduction
            if has_c_comp or has_c_neg or any(x in c_tokens for x in self.conditionals):
                score += 1.0
        
        # Normalize by active features to get a consistency ratio
        if active_features == 0:
            return 1.0 # No structural constraints detected
        return max(0.0, 0.5 + (score / (active_features * 2.0))) # Base 0.5, scale by performance

    def _evaluate_numeric(self, prompt, candidate):
        """
        Numeric evaluation: Detect number comparisons.
        """
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if not p_nums:
            return 1.0 # No numbers to check
        
        if not c_nums:
            # If prompt has numbers but candidate doesn't, check for logical words
            c_lower = candidate.lower()
            if any(x in c_lower for x in ['yes', 'no', 'true', 'false', 'correct', 'incorrect']):
                return 1.0 # Accept logical conclusion without repeating numbers
            return 0.8 # Slight penalty for not citing numbers if they are crucial
        
        # If both have numbers, check magnitude consistency if comparatives exist
        p_tokens = self._tokenize(prompt)
        if any(x in self.comparatives for x in p_tokens):
            # Rough check: did the candidate pick a number present in the prompt?
            # Or is it a valid calculation? (Hard to verify calc without eval, so check presence)
            if any(abs(c - p) < 1e-6 for c in c_nums for p in p_nums):
                return 1.0
            # If it's a derived number, we assume correctness for now if length is low
            return 0.9
            
        return 1.0

    def _kolmogorov_estimate(self, text):
        """Estimate Kolmogorov complexity using zlib."""
        if not text:
            return 0
        return len(zlib.compress(text.encode('utf-8')))

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_len = len(prompt)
        
        # Pre-calculate prompt complexity
        k_prompt = self._kolmogorov_estimate(prompt)

        for cand in candidates:
            # 1. Kolmogorov Component: Joint Compression
            # We want the candidate to add information (reduce uncertainty) without adding unnecessary length
            joint_text = f"{prompt} {cand}"
            k_joint = self._kolmogorov_estimate(joint_text)
            
            # Information gain approximation: K(P) - K(P, C) is negative usually, 
            # but we want to minimize K(C|P). 
            # Heuristic: Lower K(Joint) relative to K(P) + K(C) implies high mutual information.
            # However, simpler approach for ranking: Prefer lower K(Joint) if it answers the prompt.
            # Let's use Description Length of the candidate given the prompt context.
            k_cand = self._kolmogorov_estimate(cand)
            
            # 2. Hebbian Structural Score (Consistency)
            struct_score = self._check_structure(prompt, cand)
            
            # 3. Numeric Consistency
            num_score = self._evaluate_numeric(prompt, cand)
            
            # Mechanism Design: Incentive Compatible Scoring
            # Reward = (Structural Consistency * Numeric Consistency) / Description Length Penalty
            # We invert complexity: lower complexity = higher score component.
            # Normalized complexity score: 1 / (1 + k_cand)
            
            # Combined Score Logic:
            # High structural/numeric compliance is a multiplier (gatekeeper).
            # Complexity is the tie-breaker/minimizer.
            
            base_score = struct_score * num_score
            
            # Penalty for excessive length that doesn't add structural value
            # If candidate is just "Yes", k_cand is low. If it repeats prompt, k_cand is high.
            complexity_penalty = k_cand / 1000.0 
            
            final_score = base_score - complexity_penalty
            
            # Adjust for very short candidates (bias towards concise truth)
            if len(cand.split()) <= 3 and base_score > 0.8:
                final_score += 0.1

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural:{struct_score:.2f}, Numeric:{num_score:.2f}, K-complexity:{k_cand}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same logic as evaluate but normalized.
        """
        # Evaluate single candidate against a dummy set to get relative score?
        # No, just run internal scoring.
        struct_score = self._check_structure(prompt, answer)
        num_score = self._evaluate_numeric(prompt, answer)
        
        k_cand = self._kolmogorov_estimate(answer)
        k_prompt = self._kolmogorov_estimate(prompt)
        
        # Baseline confidence from structural alignment
        conf = struct_score * num_score
        
        # Penalize extreme verbosity without structural gain
        if k_cand > (k_prompt * 1.5):
            conf *= 0.8
            
        # Boost if concise and structurally sound
        if k_cand < (k_prompt * 0.2) and struct_score > 0.9:
            conf = min(1.0, conf + 0.1)
            
        return max(0.0, min(1.0, conf))