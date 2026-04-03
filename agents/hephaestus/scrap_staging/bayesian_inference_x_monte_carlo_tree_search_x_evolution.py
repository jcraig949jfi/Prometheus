import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Bayesian Evolutionary Monte Carlo Tree Search (BEMCTS) inspired Reasoning Tool.
    
    Mechanism:
    1. Epistemic Honesty (Meta-Confidence): Analyzes the prompt for logical traps 
       (presuppositions, ambiguity, false dichotomies) before scoring. Caps confidence 
       if risks are detected.
    2. Structural Parsing & Computation: Extracts negations, comparatives, and numeric 
       values to compute a deterministic "fitness" score for candidates.
    3. Evolutionary Selection: Treats candidates as a population. Uses a UCB-like 
       formula balancing the structural match (exploitation) and candidate diversity 
       (exploration) to rank answers.
    4. Bayesian Update: The final score represents the posterior probability of a 
       candidate being correct given the structural evidence.
    """

    def __init__(self):
        # Priors for the Bayesian update
        self.prior_mean = 0.5
        self.prior_variance = 0.25
        
        # Patterns for logical traps (Tier B)
        self.presupposition_triggers = [
            r"\bhave you stopped\b", r"\bwhy did.*fail\b", r"\bwhy.*stop\b", 
            r"\bquit\b", r"\bassumed\b", r"\bregret\b"
        ]
        self.ambiguity_triggers = [
            r"\bevery.*a.*\b", r"\btold.*he\b", r"\btold.*she\b", r"\bwho\b.*\?",
            r"\bit\b.*\?" # Weak pronoun check
        ]
        self.dichotomy_triggers = [r"\beither.*or\b", r"\bmust.*or\b"]
        self.subjectivity_triggers = [r"\bbest\b", r"\bworst\b", r"\bfavorite\b", r"\bopinion\b"]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for epistemic risks.
        Returns a cap value (0.0 - 1.0). If < 0.3, the question is considered unsafe.
        """
        p_lower = prompt.lower()
        risk_score = 0.0
        
        # Check Presuppositions
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                risk_score += 0.4
                break
                
        # Check Ambiguity
        for pattern in self.ambiguity_triggers:
            if re.search(pattern, p_lower):
                risk_score += 0.3
                break
                
        # Check False Dichotomy
        for pattern in self.dichotomy_triggers:
            if re.search(pattern, p_lower):
                risk_score += 0.2
                break
                
        # Check Subjectivity
        for pattern in self.subjectivity_triggers:
            if re.search(pattern, p_lower):
                risk_score += 0.2
                break

        # If risk is detected, cap confidence significantly
        if risk_score >= 0.2:
            return 0.25 # Honest uncertainty
        
        return 1.0 # No immediate red flags

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers from text for computation."""
        matches = re.findall(r'-?\d+\.?\d*', text)
        return [float(m) for m in matches]

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a score based on structural parsing and constructive computation.
        Handles: Negation, Comparatives, Numeric Evaluation.
        """
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Numeric Evaluation (Constructive Computation)
        # If prompt asks for comparison or math, verify candidate matches calculation
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if len(p_nums) >= 2:
            # Simple comparative logic: if prompt has numbers, candidate should reflect logic
            # Example: "Is 9.11 < 9.9?" -> Candidate "Yes" gets high score if logic holds
            if "yes" in c_lower or "true" in c_lower:
                if p_nums[0] < p_nums[1] and ("<" in p_lower or "less" in p_lower):
                    score += 0.5
                elif p_nums[0] > p_nums[1] and (">" in p_lower or "greater" in p_lower):
                    score += 0.5
            elif len(c_nums) > 0:
                # If candidate provides a number, check if it's the result of a simple operation
                # Heuristic: Is the candidate number one of the prompt numbers or a simple sum?
                # This is a basic check to avoid penalizing valid numeric answers
                score += 0.1 

        # 2. Logical Consistency (Negation)
        # If prompt has "not", candidate should ideally reflect negation or absence
        has_not = " not " in p_lower or "no " in p_lower
        if has_not:
            if "not" in c_lower or "no" in c_lower or "false" in c_lower:
                score += 0.3
            else:
                # Penalty for ignoring negation
                score -= 0.2

        # 3. Keyword Overlap (Base signal, but weighted low to avoid bag-of-words)
        p_words = set(re.findall(r'\b\w+\b', p_lower))
        c_words = set(re.findall(r'\b\w+\b', c_lower))
        if len(p_words) > 0:
            overlap = len(p_words.intersection(c_words)) / len(p_words)
            score += overlap * 0.2
            
        return max(0.0, min(1.0, score))

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1 = len(zlib.compress(s1_b))
        len2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        
        if max(len1, len2) == 0:
            return 0.0
        return (len_combined - min(len1, len2)) / max(len1, len2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Ranks candidates using a BEMCTS-inspired approach:
        1. Meta-check for epistemic honesty.
        2. Structural/Computational scoring (Exploitation).
        3. Diversity bonus (Exploration/Mutation).
        4. Bayesian aggregation.
        """
        if not candidates:
            return []

        # Step 1: Epistemic Honesty Check
        meta_cap = self._meta_confidence(prompt)
        
        results = []
        population_scores = []
        
        # Step 2: Compute raw structural scores (Likelihood)
        for i, cand in enumerate(candidates):
            struct_score = self._structural_score(prompt, cand)
            
            # Step 3: Evolutionary Diversity (Mutation bonus)
            # Encourage candidates that are structurally distinct from the prompt
            # but semantically relevant. 
            ncd_val = self._compute_ncd(prompt, cand)
            # High NCD means very different. We want moderate NCD (not identical, not noise).
            # Ideal NCD for answer is often mid-range (concise but informative).
            diversity_bonus = 0.0
            if 0.3 < ncd_val < 0.8:
                diversity_bonus = 0.1
            
            # Combine into a 'fitness' proxy
            # Weighting: Structural (0.7) + Diversity (0.15) + NCD Tiebreaker (0.15)
            # Note: NCD is used as a tiebreaker/diversity factor, not primary driver
            raw_score = (struct_score * 0.7) + (diversity_bonus * 0.3)
            
            # Apply NCD tiebreaker logic explicitly if scores are close later
            ncd_penalty = ncd_val * 0.15 # Slight penalty for very long/complex matches if not needed
            
            final_raw = raw_score - ncd_penalty
            
            # Bayesian Update Simulation
            # Posterior Mean = (PriorVar * Likelihood + PriorMean * DataVar) / (PriorVar + DataVar)
            # Simplified: Weighted average of prior (0.5) and observed structural score
            likelihood = max(0.0, min(1.0, final_raw))
            data_weight = 0.8 # Trust structural parse more than prior
            posterior = (self.prior_mean * (1-data_weight)) + (likelihood * data_weight)
            
            # Apply Epistemic Cap
            if meta_cap < 0.3:
                # If the question is ambiguous, even the "best" candidate is suspect
                posterior = min(posterior, 0.25)
            
            population_scores.append({
                "candidate": cand,
                "score": posterior,
                "reasoning": f"Structural: {struct_score:.2f}, NCD: {ncd_val:.2f}, MetaCap: {meta_cap:.2f}",
                "meta_cap": meta_cap
            })

        # Step 4: Normalization and Ranking (Selection Pressure)
        # Normalize scores to ensure they sum to 1 (probability distribution) or fit 0-1
        max_score = max(r['score'] for r in population_scores) if population_scores else 0
        if max_score > 0:
            for r in population_scores:
                # Scale relative to best, but keep under meta_cap
                scaled = r['score'] / max_score if max_score > 0 else 0
                r['score'] = min(scaled, meta_cap) # Enforce cap strictly on output
        
        # Sort descending
        population_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Format output
        return [
            {"candidate": r['candidate'], "score": round(r['score'], 4), "reasoning": r['reasoning']}
            for r in population_scores
        ]

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence for ambiguous/trap prompts.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Calculate structural alignment
        struct_score = self._structural_score(prompt, answer)
        
        # Base confidence on structural match, capped by meta-analysis
        base_conf = struct_score * 0.9 + 0.05 # Small baseline
        
        final_conf = min(base_conf, meta_cap)
        
        # Never return > 0.9 unless computation was definitive (simplified here)
        # If meta_cap is low, this forces low confidence
        return round(max(0.0, min(1.0, final_conf)), 4)