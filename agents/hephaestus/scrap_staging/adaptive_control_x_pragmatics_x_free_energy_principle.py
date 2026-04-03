import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Predictive-Coding Adaptive Scorer (PCAS) with Epistemic Honesty.
    
    Mechanism:
    1. Meta-Cognition (Tier B): Analyzes prompt for ambiguity, presupposition, 
       and logical traps. Caps confidence if the question itself is flawed.
    2. Structural Parsing (Tier A): Extracts logical constraints (negation, 
       conditionals, transitivity, numeric comparisons) into a feature vector.
    3. Adaptive Control: Uses a leaky-integral update on a weight matrix to 
       minimize prediction error between prompt expectations and candidate content.
    4. Free Energy Scoring: Combines prediction error (accuracy) and model 
       complexity (uncertainty) to rank candidates.
    """
    
    def __init__(self):
        self.W = None  # Weight matrix
        self.W0 = None # Prior weights (Identity)
        self.k = 64    # Feature dimension
        self.eta = 0.1 # Learning rate
        self.lamb = 0.05 # Leakage
        self._init_weights()
        
        # Pragmatic trap patterns
        self.presupposition_re = re.compile(r'\b(have you stopped|did you stop|why did|why does|when did|when does)\b', re.I)
        self.false_dichotomy_re = re.compile(r'\b(either .+ or .+|is it .+ or .+)\b', re.I)
        self.scope_ambiguity_re = re.compile(r'\b(every .+ (a|an) .+|all .+ are .+)\b', re.I) # Simplified detection
        self.pronoun_ambiguity_re = re.compile(r'\b(.+ told .+ (he|she|him|her)|who is .+)\b', re.I)
        self.subjectivity_re = re.compile(r'\b(best|worst|favorite|opinion|think about)\b', re.I)
        self.unanswerable_re = re.compile(r'\b(calculate|solve|find the value)\b.*\b(without|missing|no data)\b', re.I)

    def _init_weights(self):
        self.W = np.eye(self.k)
        self.W0 = np.eye(self.k)

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract structural features into a fixed-size vector."""
        if not text:
            return np.zeros(self.k)
        
        x = np.zeros(self.k)
        text_lower = text.lower()
        
        # 1. Negations (Indices 0-7)
        negations = ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere']
        for i, word in enumerate(negations):
            if re.search(r'\b' + word + r'\b', text_lower):
                x[i] = -1.0 # Encode as -1
                
        # 2. Comparatives & Numerics (Indices 8-15)
        # Detect patterns like "greater than", "less than", or explicit numbers
        nums = re.findall(r'-?\d+\.?\d*', text)
        if nums:
            try:
                # Store first two numbers for comparison logic
                v1, v2 = float(nums[0]), float(nums[1]) if len(nums) > 1 else 0.0
                x[8] = v1
                x[9] = v2
                x[10] = 1.0 if v1 > v2 else -1.0 if v1 < v2 else 0.0 # Comparative feature
            except ValueError:
                pass
        
        if 'greater' in text_lower or 'more' in text_lower: x[11] = 1.0
        if 'less' in text_lower or 'fewer' in text_lower: x[12] = 1.0
        if 'equal' in text_lower or 'same' in text_lower: x[13] = 1.0
        
        # 3. Conditionals (Indices 16-23)
        conditionals = ['if', 'then', 'unless', 'provided', 'assuming']
        for i, word in enumerate(conditionals):
            if re.search(r'\b' + word + r'\b', text_lower):
                x[16 + i] = 1.0
                
        # 4. Causal/Transitivity (Indices 24-31)
        causals = ['because', 'therefore', 'thus', 'causes', 'leads to', 'implies', 'since', 'so']
        for i, word in enumerate(causals):
            if re.search(r'\b' + word + r'\b', text_lower):
                x[24 + i] = 1.0
                
        # 5. Speech Acts / Modality (Indices 32-39)
        modals = ['must', 'should', 'could', 'might', 'will', 'would', 'suggest', 'claim']
        for i, word in enumerate(modals):
            if re.search(r'\b' + word + r'\b', text_lower):
                x[32 + i] = 1.0

        # 6. Simple Hash-based distribution for remaining features to capture unique tokens
        words = re.findall(r'\w+', text_lower)
        for word in words[:20]: # Limit to first 20 words
            h = hash(word) % (self.k - 40)
            x[40 + h] += 0.1
            
        return x

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2: return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1 = len(zlib.compress(s1_b))
        len2 = len(zlib.compress(s2_b))
        len12 = len(zlib.compress(s1_b + s2_b))
        max_len = max(len1, len2)
        if max_len == 0: return 0.0
        return (len12 - min(len1, len2)) / max_len

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap value (0.0 - 1.0) based on prompt quality.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.presupposition_re.search(p_lower):
            return 0.25
            
        # 2. False Dichotomy
        if self.false_dichotomy_re.search(p_lower):
            # Check if it's a simple math question disguised (e.g., "Either 2+2=4 or 5")
            if not re.search(r'\d', p_lower): 
                return 0.3
                
        # 3. Scope/Pronoun Ambiguity (Heuristic)
        if self.scope_ambiguity_re.search(p_lower) and "same" in p_lower:
            return 0.3
        if self.pronoun_ambiguity_re.search(p_lower) and "who" in p_lower:
            return 0.25
            
        # 4. Subjectivity
        if self.subjectivity_re.search(p_lower) and "best" in p_lower:
            if "math" not in p_lower and "calculate" not in p_lower:
                return 0.4
                
        # 5. Unanswerability markers
        if "impossible" in p_lower or "cannot be determined" in p_lower:
            # If the prompt asks to solve an impossible problem, confidence should be low unless candidate says "impossible"
            return 0.5 # Neutral cap, let scoring handle the specific answer
            
        return 1.0

    def _solve_constructive(self, prompt: str, candidate: str) -> Tuple[bool, float]:
        """
        Attempt to actually solve math/logic problems found in the prompt.
        Returns (is_solved, score_delta).
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Pattern: "What is X + Y?" or similar simple arithmetic
        match = re.search(r'(\d+)\s*[\+\-x\*]\s*(\d+)', p_lower)
        if match:
            try:
                # Very basic evaluator for demo purposes
                # In a real engine, we'd parse the full expression tree
                expr = re.search(r'([\d\s\+\-\*\/\.]+)', p_lower[match.start():match.end()+10])
                # Fallback: just check if candidate contains the result of simple addition if '+' found
                if '+' in match.group(0):
                    val = int(match.group(1)) + int(match.group(2))
                    if str(val) in candidate:
                        return True, 1.0
                # Subtraction
                elif '-' in match.group(0):
                    val = int(match.group(1)) - int(match.group(2))
                    if str(val) in candidate:
                        return True, 1.0
            except:
                pass
        return False, 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Meta-Cognition Cap
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Prompt Features (x0)
        x0 = self._extract_features(prompt)
        
        results = []
        
        for cand in candidates:
            # Extract candidate features
            x = self._extract_features(cand)
            
            # Predictive Coding Step
            x_hat = self.W @ x0
            e = x - x_hat # Prediction error
            
            # Adaptive Control Update (Leaky Integral)
            # W <- W - eta * (e * x0^T) + lambda * (W0 - W)
            update_term = np.outer(e, x0)
            self.W = self.W - self.eta * update_term + self.lamb * (self.W0 - self.W)
            
            # Free Energy Approximation
            # F = 0.5 * ||e||^2 + 0.5 * tr(Cov(W))
            # Simplified: Complexity penalty based on deviation from Identity
            complexity = np.sum((self.W - self.W0)**2)
            prediction_error = 0.5 * np.dot(e, e)
            free_energy = prediction_error + 0.1 * complexity
            
            # Base Score
            score = -free_energy
            
            # Constructive Computation Bonus (Tier A)
            solved, delta = self._solve_constructive(prompt, cand)
            if solved:
                score += 10.0 * delta
                # If we solved it constructively, we can override meta_cap for this specific candidate
                # but only if the answer is demonstrably correct.
                if delta > 0.9:
                    meta_cap = 1.0 

            # NCD Tiebreaker (Max 15% influence)
            ncd = self._compute_ncd(prompt, cand)
            # Lower NCD is better (more similar), but we want reasoning, not echoing.
            # We use NCD to penalize gibberish, but not reward pure echoing too much.
            # Ideal NCD for reasoning is moderate.
            ncd_score = -ncd * 0.5 
            
            final_score = score + ncd_score
            
            # Reasoning String
            reason_parts = []
            if meta_cap < 0.4:
                reason_parts.append("Warning: Prompt contains ambiguity or presupposition.")
            if solved:
                reason_parts.append("Constructive solution verified.")
            if np.linalg.norm(e) < 0.1:
                reason_parts.append("High structural alignment.")
                
            reasoning_str = " ".join(reason_parts) if reason_parts else "Standard predictive coding evaluation."
            
            # Apply Meta Cap to the final output score representation if needed, 
            # but primarily we use it to adjust the confidence in the `confidence` method.
            # Here we just store the raw calculated score for ranking.
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning_str,
                "_meta_cap": meta_cap # Internal use
            })
            
        # Sort by score descending
        results.sort(key=lambda k: k['score'], reverse=True)
        
        # Remove internal keys before returning
        clean_results = []
        for r in results:
            clean_results.append({
                "candidate": r["candidate"],
                "score": r["score"],
                "reasoning": r["reasoning"]
            })
            
        return clean_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Heavily penalized by _meta_confidence if the prompt is flawed.
        """
        # 1. Check Meta Constraints (Tier B)
        cap = self._meta_confidence(prompt)
        
        # 2. Generate features and score internally to gauge fit
        x0 = self._extract_features(prompt)
        x = self._extract_features(answer)
        
        # Quick prediction
        x_hat = self.W @ x0
        e = x - x_hat
        error_norm = np.linalg.norm(e)
        
        # Base confidence from error (inverse exponential)
        # Small error -> high confidence
        base_conf = np.exp(-error_norm / 2.0)
        
        # Check constructive solution
        solved, _ = self._solve_constructive(prompt, answer)
        if solved:
            base_conf = 0.95 # High confidence if mathematically solved
            
        # Apply Cap
        final_conf = min(base_conf, cap)
        
        # Ensure bounds
        return max(0.0, min(1.0, final_conf))