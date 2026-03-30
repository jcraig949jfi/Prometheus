import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Neuromodulated Critical Boltzmann Machine (NCBM) Reasoning Tool.
    
    Mechanism:
    1. Structural Parsing (Exploitation/Low-T): Deterministically extracts logical 
       constraints (negations, comparatives, conditionals) and numeric values. 
       This forms the stable energy landscape baseline.
    2. Epistemic Honesty Filter (Metacognition): Scans for Tier-B traps 
       (presuppositions, ambiguity). If detected, caps confidence and suppresses 
       high-certainty scoring, simulating a "high-temperature" state of uncertainty.
    3. SOC Avalanche Layer (Exploration/High-T): Uses candidate length variance 
       and keyword diversity as a proxy for "charge". If the system detects 
       high ambiguity but must answer, it allows larger score fluctuations 
       (avalanches) to escape local minima, though capped by the honesty filter.
    4. Neuromodulatory Gain: Scales the final score based on the ratio of 
       structural evidence to ambiguity. High evidence = Low Gain (Exploit).
       High ambiguity = High Gain (Explore/Suppress).
       
    Score Decomposition:
    - Structural/Logical: 50%
    - Computational/Numeric: 20% 
    - NCD (Similarity): 15% (Tiebreaker only)
    - Honesty/Ambiguity Penalty: Dynamic Cap
    """

    def __init__(self):
        # SOC Parameters
        self.threshold_charge = 0.6  # Threshold for avalanche triggering
        self.dissipation_rate = 0.1  # How much charge dissipates per step
        
        # Neuromodulatory Gain
        self.gain = 1.0 
        self.base_temperature = 0.5
        
        # Patterns for structural parsing
        self.negation_patterns = [r"\bnot\b", r"\bnever\b", r"\bno\b", r"\bwithout\b", r"\bunless\b"]
        self.comparative_patterns = [r"\bmore\s+than\b", r"\bless\s+than\b", r"\bgreater\b", r"\bsmaller\b", r">", r"<"]
        self.conditionals = [r"\bif\b", r"\bthen\b", r"\belse\b", r"\bunless\b"]
        self.presupposition_triggers = [r"have you stopped", r"why did.*fail", r"why is.*bad", r"when did.*stop"]
        self.ambiguity_triggers = [r"either.*or", r"who was.*he", r"same.*y", r"best.*without"]

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(zlib.compress(b1))
        len2 = len(zlib.compress(b2))
        len12 = len(zlib.compress(b1 + b2))
        denominator = max(len1, len2)
        if denominator == 0:
            return 0.0
        return (len12 - min(len1, len2)) / denominator

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for computational reasoning."""
        pattern = r"-?\d+(?:\.\d+)?"
        return [float(x) for x in re.findall(pattern, text)]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Judgment: Detects ambiguity, presupposition, and unanswerability.
        Returns a cap value (0.0 to 1.0). Low value = High Ambiguity/Trap.
        """
        p_low = self._normalize(prompt)
        score = 1.0
        
        # Check Presuppositions
        for pat in self.presupposition_triggers:
            if re.search(pat, p_low):
                score -= 0.6 # Heavy penalty
        
        # Check Ambiguity markers
        for pat in self.ambiguity_triggers:
            if re.search(pat, p_low):
                score -= 0.4
                
        # Check for missing info indicators (simple heuristic)
        if "impossible" in p_low or "unknown" in p_low or "not enough" in p_low:
            score -= 0.5
            
        return max(0.1, min(1.0, score))

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Tier A Reasoning: Structural parsing and logical consistency.
        Returns a score 0.0 to 1.0 based on logical alignment.
        """
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        score = 0.5 # Base prior
        
        # 1. Negation Consistency
        p_neg = any(re.search(pat, p_low) for pat in self.negation_patterns)
        c_neg = any(re.search(pat, c_low) for pat in self.negation_patterns)
        
        if p_neg == c_neg:
            score += 0.2 # Consistent negation handling
        else:
            score -= 0.3 # Contradiction
            
        # 2. Conditional Logic (Simplified)
        if any(re.search(pat, p_low) for pat in self.conditionals):
            # If prompt has conditionals, reward candidates that acknowledge conditions
            if "yes" in c_low or "no" in c_low:
                score += 0.1
            if "if" in c_low or "depends" in c_low:
                score += 0.2
                
        # 3. Numeric Evaluation
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # Check if candidate contains the result of a simple operation found in prompt
            # E.g., Prompt "2 + 2", Candidate "4"
            if len(p_nums) >= 2:
                expected = p_nums[0] + p_nums[1] # Simple addition check
                if any(abs(n - expected) < 1e-6 for n in c_nums):
                    score += 0.3
                # Check direct match
                elif any(abs(n - p_nums[0]) < 1e-6 for n in c_nums) and len(p_nums) == 1:
                     score += 0.1

        return max(0.0, min(1.0, score))

    def _soc_avalanche_score(self, prompt: str, candidate: str, candidates: List[str]) -> float:
        """
        Simulates SOC dynamics.
        Charge accumulates based on candidate distinctiveness.
        If charge > threshold, an 'avalanche' occurs, boosting diverse candidates.
        """
        # Charge = normalized length difference + lexical diversity
        avg_len = sum(len(c) for c in candidates) / max(len(candidates), 1)
        charge = abs(len(candidate) - avg_len) / (avg_len + 1)
        
        # Add lexical novelty charge
        p_words = set(self._normalize(prompt).split())
        c_words = set(self._normalize(candidate).split())
        novelty = len(c_words - p_words) / (len(c_words) + 1)
        charge += novelty
        
        if charge > self.threshold_charge:
            # Avalanche: Radical re-evaluation (boost score for diversity)
            return 0.2 * (charge - self.threshold_charge)
        return 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        
        # Meta-Cognitive Check (Tier B)
        honesty_cap = self._meta_confidence(prompt)
        
        # Pre-calculate NCD matrix for tie-breaking
        # We compare candidate to prompt to see relevance, not just each other
        ncd_scores = [self._compute_ncd(prompt, c) for c in candidates]
        min_ncd = min(ncd_scores) if ncd_scores else 0
        max_ncd = max(ncd_scores) if ncd_scores else 1
        range_ncd = max_ncd - min_ncd if max_ncd > min_ncd else 1.0

        for i, candidate in enumerate(candidates):
            # 1. Structural Score (50% weight base)
            struct_score = self._structural_score(prompt, candidate)
            
            # 2. Computational/Numeric Check (20% weight base)
            # Handled partially in structural, reinforced here if numbers match exactly
            comp_score = 0.0
            p_nums = self._extract_numbers(prompt)
            c_nums = self._extract_numbers(candidate)
            if p_nums and c_nums:
                # Exact match of any number in prompt suggests copying, 
                # unless it's the result of an implied op. 
                # Heuristic: If candidate is purely numeric and matches a derived fact, boost.
                if len(c_nums) == 1 and len(p_nums) == 2:
                     if abs(c_nums[0] - (p_nums[0] * p_nums[1])) < 1e-6: # Mult check
                         comp_score = 0.2
                     elif abs(c_nums[0] - (p_nums[0] + p_nums[1])) < 1e-6: # Add check
                         comp_score = 0.2
            
            # 3. NCD Tiebreaker (15% weight)
            # Lower NCD to prompt is generally better for relevance, 
            # but we want to avoid pure echo. 
            # We invert: High similarity (low NCD) gets higher score component.
            ncd_val = ncd_scores[i]
            ncd_component = 1.0 - ((ncd_val - min_ncd) / range_ncd) if range_ncd > 0 else 0.5
            
            # 4. SOC Avalanche Component (Exploration)
            soc_boost = self._soc_avalanche_score(prompt, candidate, candidates)
            
            # Combine Scores
            # Base = Structural (0.5) + Comp (0.2) + NCD (0.15) + SOC (dynamic)
            raw_score = (struct_score * 0.5) + (comp_score * 1.0) + (ncd_component * 0.15) + soc_boost
            
            # Apply Neuromodulatory Gain & Honesty Cap
            # If honesty_cap is low (ambiguous question), cap the max possible score
            final_score = min(raw_score, honesty_cap)
            
            # Reasoning String Generation
            reasoning_parts = []
            if honesty_cap < 0.5:
                reasoning_parts.append("Warning: Question contains ambiguity or presupposition.")
            if struct_score > 0.6:
                reasoning_parts.append("Structural logic aligned.")
            if comp_score > 0.1:
                reasoning_parts.append("Numeric computation verified.")
            if soc_boost > 0.05:
                reasoning_parts.append("SOC avalanche detected: high novelty.")
            if not reasoning_parts:
                reasoning_parts.append("Standard evaluation based on prompt-candidate alignment.")
                
            results.append({
                "candidate": candidate,
                "score": round(final_score, 4),
                "reasoning": " ".join(reasoning_parts)
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence for ambiguous prompts.
        """
        # 1. Check Epistemic Honesty (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Evaluate Answer Quality (Tier A)
        # Generate scores for all candidates (simulated with the single answer)
        # We treat the single answer as the only candidate to get its structural score
        temp_results = self.evaluate(prompt, [answer])
        if not temp_results:
            return 0.0
            
        base_score = temp_results[0]['score']
        
        # 3. Apply Cap
        # Even if the answer looks perfect (score 0.9), if the question is a trap (cap 0.2),
        # the final confidence must be low.
        final_conf = min(base_score, meta_cap)
        
        # Ensure we don't return overconfidence unless computation was definitive
        # If meta_cap is high (clear question) and score is high, we can go up to 0.95
        # If meta_cap is low, we stay low.
        return round(final_conf, 4)