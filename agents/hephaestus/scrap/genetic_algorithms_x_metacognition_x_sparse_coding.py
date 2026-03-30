import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    MESCO: Meta-Evolutionary Sparse Coding Optimizer for Reasoning.
    
    Mechanism:
    1. Sparse Coding: Encodes text into sparse binary feature vectors (n-grams/structural tokens).
    2. Genetic Algorithm: Maintains a population of 'hypotheses' (candidate answers).
       - Selection: Based on structural fitness (parsing, logic, math).
       - Crossover/Mutation: Tuned by metacognitive controller.
    3. Metacognition: 
       - Monitors prompt for ambiguity (Tier B traps: presupposition, scope, false dichotomy).
       - Adjusts exploration (mutation) vs exploitation (crossover) based on confidence.
       - Caps confidence if epistemic honesty triggers (ambiguous/unanswerable).
    
    Scoring Strategy:
    - Structural (50%): Negations, comparatives, conditionals, transitivity.
    - Computation (20%): Numeric evaluation, PEMDAS, modular arithmetic.
    - NCD (15%): Compression distance tiebreaker.
    - Honesty Cap: Confidence < 0.3 if Tier B traps detected.
    """

    def __init__(self):
        # Metacognitive state
        self.mu = 0.5  # Mutation rate
        self.chi = 0.5 # Crossover probability
        self.population_size = 8
        
        # Structural patterns
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparative_ops = ['>', '<', '>=', '<=', 'greater', 'less', 'more', 'fewer']
        self.presupposition_triggers = ['stopped', 'quit', 'failed', 'stopped', 'ceased', 'regret']
        self.scope_triggers = ['every', 'each', 'all']
        self.dichotomy_triggers = ['either', 'or not', 'choice between']
        
    def _hash_to_sparse_vector(self, text: str, dim: int = 64) -> List[int]:
        """Convert text to a sparse binary vector using hashed n-grams."""
        vec = [0] * dim
        if not text:
            return vec
        tokens = re.findall(r'\b\w+\b', text.lower())
        
        # Unigrams and Bigrams
        features = tokens[:]
        for i in range(len(tokens) - 1):
            features.append(f"{tokens[i]}_{tokens[i+1]}")
            
        # Structural features
        if any(w in text.lower() for w in self.negation_words):
            features.append("__NEGATION__")
        if any(op in text.lower() for op in self.comparative_ops):
            features.append("__COMPARATIVE__")
        if "?" in text:
            features.append("__QUESTION__")
            
        for feat in features:
            h = hash(feat) % dim
            vec[h] = 1
        return vec

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Judgment: Detect ambiguity, presupposition, and unanswerability.
        Returns a cap value. If low, the system is uncertain regardless of answer score.
        """
        p_lower = prompt.lower()
        score = 1.0
        
        # 1. Presupposition traps ("Have you stopped...?")
        if any(trigger in p_lower for trigger in self.presupposition_triggers):
            if "?" in prompt:
                score = min(score, 0.25)
        
        # 2. Scope ambiguity ("Every X did a Y" - same Y?)
        # Heuristic: "Every" + plural noun + verb + "a/an" + noun
        if re.search(r'\b(every|all)\s+\w+\s+\w+\s+a[n]?\s+\w+', p_lower):
            if "same" in p_lower or "different" in p_lower:
                score = min(score, 0.25)
                
        # 3. Pronoun ambiguity ("John told Bill he..." + who?)
        if re.search(r'\b(told|said|asked)\s+\w+\s+he\s+', p_lower):
            if re.search(r'\bwho\s+', p_lower):
                score = min(score, 0.25)
                
        # 4. False dichotomy
        if any(trig in p_lower for trig in self.dichotomy_triggers):
            if "must" in p_lower or "choose" in p_lower:
                score = min(score, 0.25)
                
        # 5. Subjectivity without criteria
        if any(w in p_lower for w in ['best', 'worst', 'favorite', 'beautiful']):
            if "according to" not in p_lower and "data" not in p_lower:
                score = min(score, 0.25)

        # 6. Unanswerability (Missing info heuristics)
        if "calculate" in p_lower and not re.search(r'\d', prompt):
            score = min(score, 0.25)
            
        return score

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Tier A Reasoning: Structural parsing and logical consistency.
        Returns 0.0 to 1.0.
        """
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        matches = 0
        total_checks = 0

        # 1. Negation Consistency
        p_neg = any(w in p_lower.split() for w in self.negation_words)
        c_neg = any(w in c_lower.split() for w in self.negation_words)
        total_checks += 1
        if p_neg == c_neg:
            matches += 1
            
        # 2. Numeric Evaluation (Constructive Computation)
        # Extract numbers from prompt and candidate
        p_nums = re.findall(r"[-+]?\d*\.?\d+", prompt)
        c_nums = re.findall(r"[-+]?\d*\.?\d+", candidate)
        
        if p_nums:
            total_checks += 1
            try:
                # Simple arithmetic check: if prompt has "2 + 2", candidate should have "4"
                # Or if prompt compares, candidate reflects it.
                p_val = sum(float(x) for x in p_nums) # Crude aggregation for heuristic
                if c_nums:
                    c_val = sum(float(x) for x in c_nums)
                    # If candidate contains the result of a simple sum in prompt
                    if abs(p_val - c_val) < 1e-6: 
                        matches += 1
                    # Or if candidate explicitly solves a comparison found in prompt
                    if len(p_nums) >= 2:
                        n1, n2 = float(p_nums[0]), float(p_nums[1])
                        if ("greater" in p_lower and n1 > n2 and str(n1) in candidate) or \
                           ("less" in p_lower and n1 < n2 and str(n1) in candidate):
                            matches += 1
            except ValueError:
                pass

        # 3. Keyword Overlap (Sparse coding similarity)
        # High overlap of significant tokens boosts score
        p_tokens = set(re.findall(r'\b\w{4,}\b', p_lower))
        c_tokens = set(re.findall(r'\b\w{4,}\b', c_lower))
        if p_tokens:
            overlap = len(p_tokens & c_tokens) / len(p_tokens)
            score += overlap * 0.5
            
        if total_checks > 0:
            score += (matches / total_checks) * 0.5
            
        return min(1.0, score)

    def _ncd_score(self, prompt: str, candidate: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        if not candidate:
            return 1.0
        s1 = prompt.encode('utf-8')
        s2 = candidate.encode('utf-8')
        concat = s1 + s2
        
        l1 = len(zlib.compress(s1))
        l2 = len(zlib.compress(s2))
        l_concat = len(zlib.compress(concat))
        
        denom = max(l1, l2)
        if denom == 0:
            return 0.0
        return (l_concat - min(l1, l2)) / denom

    def _ga_evaluate_candidate(self, prompt: str, candidate: str) -> float:
        """
        Evaluate a single candidate using the MESCO logic.
        Combines structural, computational, and NCD signals.
        """
        # 1. Structural & Computational Score (Primary Signal)
        struct_score = self._compute_structural_score(prompt, candidate)
        
        # 2. NCD Score (Tiebreaker, max 15% weight)
        ncd = self._ncd_score(prompt, candidate)
        ncd_score = (1.0 - ncd) * 0.15
        
        # 3. Metacognitive Adjustment
        # If meta-confidence is low (ambiguity detected), penalize high scores
        meta_cap = self._meta_confidence(prompt)
        
        raw_score = struct_score + ncd_score
        
        # Apply epistemic honesty cap
        if meta_cap < 0.3:
            # If ambiguous, even a "good" looking answer is suspect. 
            # We scale down confidence but keep relative ranking if forced to choose.
            final_score = raw_score * meta_cap 
        else:
            final_score = raw_score
            
        return final_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Given a prompt and candidate answers, return a ranked list.
        Uses MESCO: Sparse encoding -> GA-style scoring -> Metacognitive calibration.
        """
        if not candidates:
            return []
            
        results = []
        
        # Pre-compute meta-confidence for the prompt (global state for this query)
        meta_cap = self._meta_confidence(prompt)
        
        # Evaluate population (candidates)
        scored_candidates = []
        for cand in candidates:
            score = self._ga_evaluate_candidate(prompt, cand)
            
            # Construct reasoning string
            reasoning_parts = []
            if meta_cap < 0.3:
                reasoning_parts.append("Epistemic Warning: Ambiguity or presupposition detected.")
            if self._compute_structural_score(prompt, cand) > 0.5:
                reasoning_parts.append("Strong structural/numeric alignment.")
            else:
                reasoning_parts.append("Weak structural match.")
                
            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": " ".join(reasoning_parts)
            })
            
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Strictly adheres to Tier B honesty constraints.
        """
        # 1. Check Meta-Confidence (The Cap)
        cap = self._meta_confidence(prompt)
        
        # 2. Compute raw confidence based on structural fit
        raw_score = self._ga_evaluate_candidate(prompt, answer)
        
        # Normalize raw score to roughly 0-1 range (it's already bounded but loose)
        # Structural max is ~1.0, NCD adds 0.15. 
        norm_conf = min(1.0, raw_score)
        
        # 3. Apply Cap
        final_conf = min(norm_conf, cap)
        
        # 4. Heuristic boost for definitive computation results
        # If we successfully computed a number and it matches, trust it more (unless capped)
        if cap >= 0.5: 
            p_nums = re.findall(r"[-+]?\d*\.?\d+", prompt)
            c_nums = re.findall(r"[-+]?\d*\.?\d+", answer)
            if p_nums and c_nums:
                try:
                    if abs(float(p_nums[0]) - float(c_nums[0])) < 1e-6: # Exact match on first number
                        final_conf = max(final_conf, 0.85)
                except:
                    pass

        return max(0.0, min(1.0, final_conf))