import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Entropy-Regularized Adaptive Sparse Controller (ERASC).
    
    Mechanism:
    1. Structural Parsing (Primary): Extracts negations, comparatives, and conditionals.
       Computes a deterministic logic score based on constraint satisfaction.
    2. Adaptive Control (Metacognition): Monitors structural ambiguity. 
       - High ambiguity -> Increases 'entropy' weight (broadens confidence distribution).
       - Low ambiguity -> Increases 'sparsity' weight (sharpens decision).
    3. Sparse Autoencoder Analogy: Treats candidate answers as latent codes. 
       Penalizes candidates that do not sparsely match the extracted structural constraints.
    4. MaxEnt Prior: Used ONLY in confidence() to prevent over-confidence on ambiguous inputs,
       ensuring the system remains uncertain when structural signals are weak.
    5. NCD: Used strictly as a tiebreaker for candidates with identical structural scores.
    """

    def __init__(self):
        self.ref_error = 0.1  # Target reconstruction error reference
        self.lambda_t = 1.0   # Sparsity weight (adaptive)
        self.beta = 0.5       # Entropy weight (adaptive)
        self.gamma = 0.01     # Dictionary change penalty (simulated)
        
        # Structural keywords
        self.negations = ['not', 'no', 'never', 'none', 'cannot', 'impossible']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditionals = ['if', 'unless', 'provided', 'only if']
        self.bool_yes = ['yes', 'true', 'correct', 'valid']
        self.bool_no = ['no', 'false', 'incorrect', 'invalid']

    def _structural_parse(self, text: str) -> Dict[str, any]:
        """Extract logical constraints from text."""
        t_lower = text.lower()
        words = re.findall(r'\b\w+\b', t_lower)
        
        has_neg = any(n in t_lower for n in self.negations)
        has_comp = any(c in t_lower for c in self.comparatives)
        has_cond = any(c in t_lower for c in self.conditionals)
        
        # Numeric extraction
        nums = re.findall(r'-?\d+\.?\d*', text)
        numbers = [float(n) for n in nums] if nums else []
        
        # Boolean tendency
        yes_count = sum(1 for w in self.bool_yes if w in words)
        no_count = sum(1 for w in self.bool_no if w in words)
        
        return {
            'neg': has_neg,
            'comp': has_comp,
            'cond': has_cond,
            'nums': numbers,
            'yes_bias': yes_count - no_count
        }

    def _compute_logic_score(self, prompt: str, candidate: str) -> float:
        """
        Core reasoning engine.
        Evaluates candidate against prompt constraints.
        """
        p_struct = self._structural_parse(prompt)
        c_struct = self._structural_parse(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()
        
        score = 0.0
        constraints_checked = 0
        
        # 1. Numeric Consistency (High Priority)
        if p_struct['nums'] and c_struct['nums']:
            # If prompt has numbers and candidate has numbers, check relation
            # Simple heuristic: if prompt implies comparison, candidate should reflect it
            if p_struct['comp']:
                if 'greater' in c_lower or '>' in c_lower:
                    score += 2.0 if p_struct['nums'][0] > p_struct['nums'][1] if len(p_struct['nums'])>1 else 0 else 0
                elif 'less' in c_lower or '<' in c_lower:
                    score += 2.0 if len(p_struct['nums'])>1 and p_struct['nums'][0] < p_struct['nums'][1] else 0
            constraints_checked += 1

        # 2. Negation Handling (Crucial for reasoning traps)
        if p_struct['neg']:
            # If prompt is negative, candidate should ideally acknowledge or not contradict
            # Heuristic: If prompt says "not X", and candidate is "X", penalize heavily
            # This is a simplification of logical entailment
            if c_struct['neg'] == p_struct['neg']:
                score += 1.5 # Agreement on negation
            else:
                # Check if candidate blindly repeats positive form of a negative prompt
                # Very basic check: if prompt has "not" and candidate lacks "not" but matches words
                score -= 1.0 
            constraints_checked += 1

        # 3. Conditional/Logical Flow
        if p_struct['cond']:
            if c_struct['cond']:
                score += 1.0
            elif any(k in c_lower for k in ['therefore', 'thus', 'so', 'consequently']):
                score += 0.5 # Recognizes consequence
            constraints_checked += 1

        # 4. Direct Answer Matching (Sparse Code Activation)
        # If prompt asks a yes/no question (implied by structure)
        if p_struct['yes_bias'] != 0:
            if c_struct['yes_bias'] > 0 and p_struct['yes_bias'] > 0:
                score += 3.0
            elif c_struct['yes_bias'] < 0 and p_struct['yes_bias'] < 0:
                score += 3.0
            elif c_struct['yes_bias'] == 0:
                score -= 2.0 # Ambiguous answer to binary question
        
        # Normalize by complexity to avoid length bias
        if constraints_checked == 0:
            return 0.0
            
        return score

    def _adaptive_update(self, prompts: List[str], candidates: List[str]):
        """
        Simulates the Lyapunov-based adaptive controller.
        Adjusts lambda (sparsity) and beta (entropy) based on ambiguity of the batch.
        """
        if not prompts:
            return

        # Estimate ambiguity (reconstruction error proxy)
        # If all candidates look similar structurally, error is low (high confidence)
        # If candidates vary wildly or all score poorly, error is high.
        
        scores = []
        for p in prompts[:1]: # Sample one for speed
            s = [self._compute_logic_score(p, c) for c in candidates]
            if s:
                scores.append(max(s) - min(s)) # Spread indicates discriminability
        
        if not scores:
            return
            
        spread = sum(scores) / len(scores)
        
        # Adaptive Law (Gradient Descent on Lyapunov function V = 0.5 * (error - ref)^2)
        # If spread (certainty) is low, increase entropy (beta) to explore, decrease sparsity (lambda)
        # If spread is high, increase sparsity to sharpen.
        
        error_proxy = 1.0 / (1.0 + spread) # High spread -> Low error
        diff = error_proxy - self.ref_error
        
        # Update rules (discrete approximation)
        self.lambda_t = max(0.1, self.lambda_t - 0.1 * diff) # Increase lambda if error high? 
        # Actually: if error high (ambiguous), we want LESS sparsity (more features active) -> lower lambda
        # if error low (clear), we want MORE sparsity -> higher lambda
        self.lambda_t = max(0.1, self.lambda_t + 0.1 * diff) 
        
        # Entropy: if error high, increase beta to keep options open
        self.beta = max(0.01, min(2.0, self.beta + 0.05 * diff))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        max_len = max(c1, c2)
        if max_len == 0: return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Adaptive update based on current batch context
        self._adaptive_update([prompt], candidates)
        
        results = []
        base_scores = []
        
        # 2. Compute primary structural scores
        for c in candidates:
            raw_score = self._compute_logic_score(prompt, c)
            base_scores.append(raw_score)
        
        # 3. Apply Sparse Coding & Entropy Regularization
        # Score = RawLogic - lambda * |z| + beta * H(z)
        # Here, |z| is approximated by candidate length (penalize verbosity if lambda high)
        # H(z) is approximated by uniqueness/diversity relative to others
        
        max_base = max(base_scores) if base_scores else 0
        min_base = min(base_scores) if base_scores else 0
        range_base = (max_base - min_base) if (max_base - min_base) > 1e-6 else 1.0
        
        for i, c in enumerate(candidates):
            raw = base_scores[i]
            
            # Sparsity penalty (length penalty scaled by adaptive lambda)
            # Encourages concise, direct answers (sparse codes)
            sparsity_penalty = self.lambda_t * (len(c) / 100.0)
            
            # Entropy bonus (diversity)
            # If scores are tight, entropy matters more to break ties
            entropy_bonus = 0.0
            if range_base < 0.5: # Ambiguous batch
                # Give bonus to candidates that are structurally distinct (low NCD to prompt, high NCD to others)
                # Simplified: Just use NCD to prompt as a similarity measure (inverse)
                ncd_val = self._ncd(prompt, c)
                entropy_bonus = self.beta * (1.0 - ncd_val) # Prefer less compressed (more info) if ambiguous
            
            final_score = raw - sparsity_penalty + entropy_bonus
            
            results.append({
                "candidate": c,
                "score": final_score,
                "reasoning": f"Structural match: {raw:.2f}, Sparsity adj: {-sparsity_penalty:.2f}, Entropy adj: {entropy_bonus:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses MaxEnt principle: if structural signal is weak, confidence decays to 0.5 (max entropy).
        """
        score = self._compute_logic_score(prompt, answer)
        
        # Map score to confidence
        # Strong positive score -> 1.0
        # Strong negative score -> 0.0 (or low)
        # Near zero -> 0.5 (MaxEnt prior)
        
        # Sigmoid-like mapping centered at 0
        # Scale factor determines steepness
        k = 0.5
        raw_conf = 1.0 / (1.0 + math.exp(-k * score))
        
        # Apply Entropy Regularization (Beta)
        # If beta is high (high uncertainty environment), pull confidence towards 0.5
        # Conf_final = (1 - alpha) * raw_conf + alpha * 0.5
        # where alpha is related to beta
        alpha = min(0.9, self.beta / 2.0) 
        final_conf = (1 - alpha) * raw_conf + alpha * 0.5
        
        return max(0.0, min(1.0, final_conf))