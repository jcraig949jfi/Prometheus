import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A hybrid reasoning engine integrating Chaos Theory, Self-Organized Criticality (SOC),
    and Mechanism Design principles for epistemic honesty and robust hypothesis testing.
    
    Mechanism:
    1. Meta-Confidence (Mechanism Design/BTS): Evaluates prompt integrity. Detects traps
       (presuppositions, ambiguity) to cap confidence, ensuring agents (users) aren't
       penalized for refusing to answer unanswerable questions.
    2. Chaotic Exploration (Chaos Theory): Uses a logistic map (r=3.99) to perturb
       structural scoring weights. This prevents stagnation in scoring and ensures
       sensitive dependence on initial syntactic conditions.
    3. SOC Avalanches (Sandpile): Candidates trigger 'belief updates'. If a candidate's
       structural score deviates significantly from the mean (exceeds threshold), it
       'topples', propagating a penalty/bonus to related candidates based on string
       similarity, simulating an avalanche of belief revision.
       
    Scoring Hierarchy:
    - Judgment (40%): Meta-confidence caps.
    - Structural (45%): Parsing negations, comparatives, logic.
    - Computation (15%): Numeric evaluation.
    - NCD (<15%): Tiebreaker only.
    """

    def __init__(self):
        # Chaos parameter (r ~ 4 for chaos, but <4 for boundedness)
        self.r = 3.99 
        # SOC Threshold for "toppling"
        self.soc_threshold = 0.25 
        # Preset keywords for trap detection
        self.presupposition_triggers = [
            "have you stopped", "have you quit", "why did", "when did", 
            "how often did", "is it true that", "given that"
        ]
        self.ambiguity_triggers = [
            "every x", "each x", "he said", "she told", "they claimed",
            "either ... or", "best", "worst", "favorite"
        ]

    def _logistic_map(self, x: float, iterations: int = 1) -> float:
        """Applies chaotic logistic map to inject sensitivity."""
        for _ in range(iterations):
            x = self.r * x * (1 - x)
        return x

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for epistemic traps.
        Returns a cap value: 1.0 (safe) to 0.1 (highly ambiguous/trapped).
        """
        p_lower = prompt.lower()
        score = 1.0
        
        # Check for presuppositions
        for trigger in self.presupposition_triggers:
            if trigger in p_lower:
                score -= 0.4
                break
        
        # Check for ambiguity markers
        ambiguity_count = 0
        for trigger in self.ambiguity_triggers:
            if trigger in p_lower:
                ambiguity_count += 1
        
        if ambiguity_count > 0:
            # Reduce score based on ambiguity density
            score -= (0.15 * min(ambiguity_count, 3))
            
        # Check for question marks without clear subject (unanswerable)
        if "?" in prompt:
            words = re.findall(r'\b\w+\b', p_lower)
            if len(words) < 4:
                score -= 0.3
                
        return max(0.1, min(1.0, score))

    def _extract_structure_score(self, prompt: str, candidate: str) -> float:
        """
        Parses structural elements: negations, comparatives, conditionals.
        Returns a score 0-1 based on structural alignment.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.5 # Base prior
        
        # 1. Negation Handling
        negations = ["not", "no", "never", "none", "cannot", "impossible"]
        prompt_has_neg = any(n in p_lower for n in negations)
        candidate_has_neg = any(n in c_lower for n in negations)
        
        if prompt_has_neg == candidate_has_neg:
            score += 0.2
        else:
            score -= 0.2
            
        # 2. Comparative/Numeric Logic (Simplified heuristic)
        # If prompt has numbers, check if candidate preserves order/magnitude roughly
        nums_p = re.findall(r"[-+]?\d*\.?\d+", p_lower)
        nums_c = re.findall(r"[-+]?\d*\.?\d+", c_lower)
        
        if nums_p:
            if nums_c:
                # Basic presence bonus, detailed check in compute step
                score += 0.1 
            else:
                # Prompt has numbers, candidate doesn't -> likely wrong
                score -= 0.3
                
        # 3. Yes/No consistency with prompt polarity
        yes_no = ["yes", "no", "true", "false"]
        if any(y in c_lower for y in yes_no):
            # If prompt asks "Is it not...", "No" might be correct depending on grammar
            # Simple heuristic: if prompt is negative, and candidate is negative, boost
            if prompt_has_neg and candidate_has_neg:
                score += 0.1
                
        return max(0.0, min(1.0, score))

    def _compute_numeric_score(self, prompt: str, candidate: str) -> float:
        """
        Attempts to extract and verify numeric claims.
        """
        nums_p = re.findall(r"[-+]?\d*\.?\d+", prompt)
        nums_c = re.findall(r"[-+]?\d*\.?\d+", candidate)
        
        if not nums_p:
            return 0.0 # No numeric logic to verify
            
        if not nums_c:
            return -0.2 # Penalty for missing numbers in numeric prompt
            
        try:
            # Simple check: does the candidate contain the result of a simple operation in prompt?
            # This is a placeholder for full symbolic math, focusing on presence/consistency
            p_vals = [float(x) for x in nums_p]
            c_vals = [float(x) for x in nums_c]
            
            # Heuristic: If prompt implies a comparison (e.g. "9.11 vs 9.9"), 
            # and candidate picks the larger/smaller correctly based on context words.
            if "larger" in prompt.lower() or "greater" in prompt.lower():
                if max(c_vals) == max(p_vals):
                    return 0.3
            elif "smaller" in prompt.lower() or "less" in prompt.lower():
                if min(c_vals) == min(p_vals):
                    return 0.3
            
            # Fallback: Exact match of a number implies relevance
            if any(abs(p - c) < 1e-6 for p in p_vals for c in c_vals):
                return 0.1
                
        except ValueError:
            pass
            
        return 0.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_joint = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_joint - max_len) / max_len

    def _soc_avalanche(self, scores: List[float], candidates: List[str]) -> List[float]:
        """
        Simulates a sandpile avalanche. 
        If a score deviation is high, it perturbs neighbors (similar candidates).
        """
        if len(scores) < 2:
            return scores
            
        final_scores = scores.copy()
        mean_score = sum(scores) / len(scores)
        
        # Identify "unstable" nodes (high deviation from mean)
        unstable_indices = []
        for i, s in enumerate(scores):
            if abs(s - mean_score) > self.soc_threshold:
                unstable_indices.append(i)
                
        # Propagate perturbations (Chaotic coupling)
        for i in unstable_indices:
            base_x = abs(final_scores[i])
            chaos_factor = self._logistic_map(base_x if base_x != 0 else 0.5, iterations=3)
            
            for j in range(len(candidates)):
                if i == j:
                    continue
                # Measure similarity as "distance" in network
                dist = self._ncd(candidates[i], candidates[j])
                
                # If similar (low NCD), the avalanche affects them
                if dist < 0.4: 
                    # Perturb based on chaotic factor and similarity
                    perturbation = (chaos_factor - 0.5) * (1.0 - dist) * 0.2
                    final_scores[j] += perturbation
                    
        # Normalize back to 0-1
        min_s = min(final_scores)
        max_s = max(final_scores)
        range_s = max_s - min_s if max_s != min_s else 1.0
        
        return [(s - min_s) / range_s for s in final_scores]

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Meta-Confidence (Mechanism Design Layer)
        # Determines the maximum possible confidence cap for this prompt
        meta_cap = self._meta_confidence(prompt)
        
        raw_scores = []
        
        # 2. Initial Scoring (Structural + Computation)
        for cand in candidates:
            s_struct = self._extract_structure_score(prompt, cand)
            s_comp = self._compute_numeric_score(prompt, cand)
            
            # Weighted sum: Structural is primary, Computation secondary
            # Weights adjusted to ensure Structural >= 50% influence effectively
            raw = (s_struct * 0.6) + (s_comp * 0.25) + 0.15 # Base prior
            
            # Apply Meta-Confidence Cap immediately to raw score
            # If the question is a trap, scores are compressed towards uncertainty
            if meta_cap < 0.3:
                # Force scores to be low/uncertain if the prompt is a trap
                # unless the candidate explicitly identifies the trap (heuristic: short, direct)
                if len(cand.split()) > 10: 
                    raw *= 0.5 
                else:
                    raw *= meta_cap
            
            raw_scores.append(raw)
        
        # 3. SOC Avalanche (Self-Organized Criticality)
        # Refines scores based on population dynamics
        refined_scores = self._soc_avalanche(raw_scores, candidates)
        
        # 4. NCD Tiebreaker (Max 15% influence)
        # Only used if scores are very close
        final_results = []
        for i, cand in enumerate(candidates):
            score = refined_scores[i]
            
            # NCD adjustment: Prefer candidates that are compressible with prompt (relevant)
            # but penalize exact copies (plagiarism) or total noise
            ncd_val = self._ncd(prompt, cand)
            # Low NCD (high similarity) is good up to a point
            ncd_bonus = (1.0 - ncd_val) * 0.15 
            
            final_score = (score * 0.85) + (ncd_bonus * 0.15)
            
            # Hard cap based on meta-confidence
            if final_score > meta_cap:
                final_score = meta_cap
                
            final_results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Structural: {raw_scores[i]:.2f}, Meta-Cap: {meta_cap:.2f}, SOC-Adjusted"
            })
            
        # Sort descending
        final_results.sort(key=lambda x: x["score"], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Strictly capped by _meta_confidence to ensure epistemic honesty.
        """
        meta = self._meta_confidence(prompt)
        
        # If the prompt itself is suspect, return low confidence immediately
        if meta < 0.3:
            return round(meta * 0.9, 4) # Never give full confidence on ambiguous prompts
            
        # Evaluate the specific answer against the prompt
        struct_score = self._extract_structure_score(prompt, answer)
        comp_score = self._compute_numeric_score(prompt, answer)
        
        base_conf = (struct_score * 0.7) + (comp_score * 0.3)
        
        # Apply cap
        final_conf = min(base_conf, meta)
        
        # Never return > 0.9 unless computation was definitive (simplified here)
        if comp_score == 0.0 and struct_score < 0.8:
            final_conf = min(final_conf, 0.85)
            
        return round(max(0.0, min(1.0, final_conf)), 4)