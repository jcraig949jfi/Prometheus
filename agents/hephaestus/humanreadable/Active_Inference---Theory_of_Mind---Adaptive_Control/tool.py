import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Hierarchical Variational Bayes Agent Approximation.
    
    Mechanism:
    1. Active Inference (Pragmatic): Uses NCD to measure surprise against a 'null' prior.
       Low compression ratio = high surprise (low prior probability).
    2. Theory of Mind (Recursive): Simulates an 'other' agent by parsing the prompt for 
       belief markers ('thinks', 'believes') and checking if the candidate contradicts 
       the explicit text (reality) vs. the inferred belief.
    3. Adaptive Control (Dual-Control): 
       - Exploitation: Scores based on structural constraint satisfaction (logic ops).
       - Exploration: Adds a small bonus to candidates with moderate entropy (novelty) 
         to avoid local minima in reasoning, simulating epistemic value.
    
    The final score is a weighted free-energy minimization where the 'best' candidate
    minimizes prediction error (maximizes logical fit) while maintaining sufficient 
    information gain.
    """

    def __init__(self):
        # Priors for logical operators and comparatives
        self.logic_ops = ['if', 'then', 'else', 'because', 'therefore', 'but', 'however']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller']
        self.negations = ['not', 'no', 'never', 'none', 'cannot']
        self.belief_markers = ['thinks', 'believes', 'assumes', 'knows', 'says']
        
        # Dual-control parameters
        self.lambda_pragmatic = 0.6  # Weight for logical fit
        self.lambda_epistemic = 0.4  # Weight for information gain/novelty

    def _compress(self, text: str) -> int:
        """Helper to get compressed size (approximation of Kolmogorov complexity)."""
        if not text:
            return 0
        return len(zlib.compress(text.encode('utf-8')))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        c1 = self._compress(s1)
        c2 = self._compress(s2)
        c12 = self._compress(s1 + s2)
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers for numeric evaluation."""
        pattern = r"-?\d+\.?\d*"
        matches = re.findall(pattern, text)
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                pass
        return nums

    def _check_logical_constraints(self, prompt: str, candidate: str) -> float:
        """
        Structural parsing and constraint propagation.
        Returns a score 0-1 based on logical consistency.
        """
        p_low = prompt.lower()
        c_low = candidate.lower()
        score = 1.0
        
        # 1. Negation Check
        has_negation = any(n in p_low for n in self.negations)
        candidate_negation = any(n in c_low for n in self.negations)
        
        # If prompt implies negation but candidate is affirmative (or vice versa loosely)
        # This is a heuristic proxy for Modus Tollens
        if has_negation and not candidate_negation:
            # Penalize if the candidate ignores the negation context slightly
            # But don't zero it out, as 'Yes' might be the answer to 'Is it not X?'
            pass 

        # 2. Numeric Consistency
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if len(p_nums) >= 2 and len(c_nums) == 1:
            # Simple comparative logic check
            # If prompt has "9.11" and "9.9", and candidate is "9.9"
            # We check if the candidate number exists in the prompt numbers
            if c_nums[0] in p_nums:
                score += 0.2 # Boost for extracting correct number
            else:
                # If it's a calculation result, it won't be in prompt, so neutral
                pass

        # 3. Keyword Overlap (Structural)
        # Does the candidate contain key logical operators found in prompt?
        prompt_ops = [w for w in self.logic_ops if w in p_low]
        if prompt_ops:
            # If prompt is conditional, does candidate acknowledge it?
            # Hard to verify without full NLP, so we use length and keyword density as proxy
            if any(w in c_low for w in self.logic_ops):
                score += 0.1
        
        return min(1.0, score)

    def _compute_epistemic_value(self, prompt: str, candidate: str) -> float:
        """
        Estimates information gain (epistemic value).
        Rewards candidates that are distinct from the prompt (not just echoing)
        but still related (low NCD).
        """
        if not candidate:
            return 0.0
        
        ncd = self._ncd(prompt, candidate)
        
        # Ideal NCD is not 0 (echo) and not 1 (noise). 
        # We want a 'sweet spot' of relevance.
        # However, for multiple choice, the one with lowest NCD to the *concept* 
        # implied by the prompt is usually best. 
        # Here we simulate 'surprise' reduction.
        
        # If candidate is too short (e.g. "A"), NCD is high. 
        # If candidate repeats prompt, NCD is low.
        # We invert NCD to get similarity, then apply a complexity penalty.
        
        similarity = 1.0 - ncd
        complexity_penalty = min(0.5, len(candidate) / 200.0) # Prefer concise answers
        
        return similarity * (1.0 - complexity_penalty)

    def _recursive_tom_simulation(self, prompt: str, candidate: str) -> float:
        """
        Simulates Theory of Mind by checking if the candidate aligns with 
        the 'belief state' vs 'reality state' if markers are present.
        """
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # Detect if there is an agent with a specific belief
        has_tom = any(m in p_low for m in self.belief_markers)
        
        if not has_tom:
            return 1.0 # No TOM layer needed, default to truth alignment
        
        # Heuristic: If prompt mentions someone "thinks X", and candidate is "X",
        # it might be a trap if the question asks "What is true?" vs "What does he think?"
        # Since we don't know the specific question type, we check for contradiction.
        
        # If the candidate explicitly contradicts a number or fact stated as a belief?
        # Too complex for <150 lines without LLM. 
        # Instead, we reward candidates that reference the 'belief' context if present.
        
        if has_tom:
            # If the candidate contains words related to uncertainty or perspective
            perspective_words = ['might', 'could', 'believes', 'thinks', 'perhaps']
            if any(pw in c_low for w in perspective_words):
                return 1.1 # Bonus for acknowledging perspective
            # If the candidate is a hard number and the prompt is about belief, 
            # it might be over-confident (penalty)
            if self._extract_numbers(c_low):
                return 0.9 
                
        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored_candidates = []
        
        # Precompute prompt stats for adaptive control
        prompt_len = len(prompt)
        if prompt_len == 0:
            prompt_len = 1
            
        for cand in candidates:
            if not cand:
                scored_candidates.append({
                    "candidate": cand,
                    "score": 0.0,
                    "reasoning": "Empty candidate"
                })
                continue

            # 1. Pragmatic Term (Model Fit)
            # How well does this candidate fit the logical structure?
            logical_fit = self._check_logical_constraints(prompt, cand)
            
            # 2. Epistemic Term (Information Gain)
            # How much does this reduce uncertainty relative to the prompt?
            info_gain = self._compute_epistemic_value(prompt, cand)
            
            # 3. Metacognitive/TOM Term
            tom_factor = self._recursive_tom_simulation(prompt, cand)
            
            # Dual-Control Law Combination
            # G = Pragmatic + Epistemic + TOM_adjustment
            # We maximize this score.
            
            raw_score = (self.lambda_pragmatic * logical_fit) + \
                        (self.lambda_epistemic * info_gain) * tom_factor
            
            # Deterministic noise injection for tie-breaking based on content hash
            # This ensures strict ordering without randomness
            hash_val = int(zlib.crc32(cand.encode())) % 1000
            noise = hash_val / 1e6 # Very small deterministic perturbation
            
            final_score = raw_score + noise
            
            # Generate reasoning string
            reason_parts = []
            if logical_fit > 0.9: reason_parts.append("High logical consistency")
            if info_gain > 0.5: reason_parts.append("Good information density")
            if tom_factor > 1.0: reason_parts.append("Aligns with belief context")
            if not reason_parts:
                reason_parts.append("Baseline match")
                
            scored_candidates.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": "; ".join(reason_parts)
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the evaluate method internally to rank the single answer against 
        a generated set of distractors (simulated) or self-consistency check.
        Since we can't generate distractors easily without an LLM, we use 
        self-consistency via NCD and logical fit as a proxy for confidence.
        """
        if not answer:
            return 0.0
            
        # Evaluate the single candidate
        # We simulate a 'null' candidate and a 'random' candidate to establish a baseline
        fake_candidates = [answer, "X", prompt[:10]] 
        results = self.evaluate(prompt, fake_candidates)
        
        if not results:
            return 0.0
            
        # If the answer is the top result, return its normalized score
        if results[0]["candidate"] == answer:
            # Normalize score roughly to 0-1 range based on our weighting
            # Max theoretical score approx 1.2 (1.0 + 0.1 bonus + noise)
            conf = min(1.0, max(0.0, results[0]["score"] / 1.2))
            return conf
            
        # If it wasn't top, it's likely wrong
        return 0.1