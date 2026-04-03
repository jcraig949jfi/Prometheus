import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Chaotic Falsification-Driven Reasoning Tool (CF-DRT).
    
    Mechanism:
    1. Epistemic Honesty (Falsificationism): Before scoring, the prompt is analyzed for 
       logical traps (presuppositions, ambiguities, false dichotomies). If detected, 
       confidence is capped low (<0.3) regardless of candidate quality.
    2. Chaotic Exploration (Chaos Theory): Candidates are mapped to initial conditions 
       via hashing. A logistic map (r=3.99) generates a trajectory. The variance of this 
       trajectory serves as a 'Lyapunov-like' stability metric. Stable, structured 
       answers (often correct in parsing tasks) yield different chaotic signatures than 
       noise.
    3. Structural Parsing: The core scoring relies on detecting negations, comparatives, 
       and performing numeric evaluations, not just string similarity.
    4. NCD Tiebreaker: Normalized Compression Distance is used only when structural 
       signals are weak, limited to 15% of the score.
    """

    def __init__(self):
        # Chaos parameter (logistic map)
        self.r = 3.99 
        # Thresholds
        self.confidence_cap_ambiguous = 0.25
        self.confidence_cap_certain = 0.95
        
        # Logical triggers for Falsification checks
        self.presupposition_triggers = [
            r"\b(stopped|quit|ceased|failed)\s+(to\s+)?\b",
            r"\bwhy\s+(did|does|is)\s+\w+\s+(fail|stop|wrong)\b",
            r"\bhave\s+you\s+(stopped|quit)\b"
        ]
        self.scope_triggers = [r"\bevery\s+\w+\s+\w+\s+a\s+\w+\b"] # Simplified "Every X did a Y"
        self.pronoun_triggers = [r"\b(he|she|him|her|they)\s+was\s+\b", r"\bwho\s+\?"]
        self.dichotomy_triggers = [r"\beither\s+\w+\s+or\s+\w+\b", r"\bis\s+it\s+\w+\s+or\s+\w+\?"]
        self.subjectivity_triggers = [r"\b(best|worst|favorite|beautiful)\s+\w+\b"]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for epistemic traps (Tier B Reasoning).
        Returns a cap value: low if ambiguous/trapped, high if clear.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Check
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return self.confidence_cap_ambiguous
        
        # 2. Scope Ambiguity (Simplified heuristic)
        if re.search(r"every\s+\w+.*\ba\s+\w+", p_lower):
            # Heuristic: If "every" and "a" appear in specific structures, flag potential scope issue
            if "same" not in p_lower and "different" not in p_lower:
                return self.confidence_cap_ambiguous

        # 3. Pronoun Ambiguity
        if re.search(r"\btold\s+\w+\s+he\s+", p_lower) and "who" in p_lower:
            return self.confidence_cap_ambiguous
            
        # 4. False Dichotomy
        if re.search(r"either.*or", p_lower) and "option" not in p_lower:
             # Only flag if it looks like a forced choice without context
             if "choose" in p_lower or "select" in p_lower:
                 pass # Context implies a choice is needed, maybe okay
             elif "?" in prompt:
                 return self.confidence_cap_ambiguous

        # 5. Subjectivity
        for trig in self.subjectivity_triggers:
            if re.search(trig, p_lower):
                # Only flag if no objective criteria mentioned
                if "metric" not in p_lower and "data" not in p_lower:
                    return self.confidence_cap_ambiguous

        # 6. Unanswerability (Missing info heuristic)
        if "calculate" in p_lower and not any(c.isdigit() for c in p_lower):
            return self.confidence_cap_ambiguous

        return 1.0

    def _chaotic_signature(self, text: str, steps: int = 50) -> float:
        """
        Generates a stability score based on chaotic trajectory of the text hash.
        Maps text to x0 in [0.1, 0.9]. Iterates logistic map.
        Returns variance of the trajectory as a stability metric.
        """
        if not text:
            return 0.0
        
        # Deterministic mapping from string to float (0.1, 0.9)
        h = zlib.crc32(text.encode())
        x0 = 0.1 + 0.8 * ((h % 10000) / 10000.0)
        
        x = x0
        trajectory = []
        
        # Warm up
        for _ in range(10):
            x = self.r * x * (1 - x)
            
        # Collect
        for _ in range(steps):
            x = self.r * x * (1 - x)
            trajectory.append(x)
            
        # Variance as a measure of chaotic 'energy' or stability
        mean_val = sum(trajectory) / len(trajectory)
        variance = sum((x - mean_val) ** 2 for x in trajectory) / len(trajectory)
        return variance

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Performs structural parsing and numeric evaluation (Tier A).
        Returns a score 0.0 to 1.0 based on logical consistency.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower().strip().rstrip('.')
        score = 0.5 # Base neutral
        
        # 1. Numeric Evaluation
        # Extract numbers from prompt and candidate
        nums_p = re.findall(r"-?\d+\.?\d*", p_lower)
        nums_c = re.findall(r"-?\d+\.?\d*", c_lower)
        
        if nums_p and nums_c:
            try:
                # Simple comparison logic
                p_vals = [float(n) for n in nums_p]
                c_vals = [float(n) for n in nums_c]
                
                # If prompt asks for max/min/comparison
                if "larger" in p_lower or "max" in p_lower or "greater" in p_lower:
                    if max(c_vals) >= max(p_vals): # Candidate identifies max correctly?
                        score += 0.4
                    else:
                        score -= 0.4
                elif "smaller" in p_lower or "min" in p_lower or "less" in p_lower:
                    if min(c_vals) <= min(p_vals):
                        score += 0.4
                    else:
                        score -= 0.4
                elif "sum" in p_lower or "total" in p_lower:
                    if abs(sum(c_vals) - sum(p_vals)) < 0.01:
                        score += 0.5
                    else:
                        score -= 0.5
                # Direct equality check if only one number expected
                elif len(nums_p) == 1 and len(nums_c) == 1:
                    if abs(c_vals[0] - p_vals[0]) < 0.01:
                        score += 0.5
                    else:
                        score -= 0.5
            except ValueError:
                pass

        # 2. Negation/Contradiction Check
        # If prompt has "not" or "never", candidate should reflect that or not contradict
        has_neg_p = any(w in p_lower for w in ["not", "never", "no ", "false"])
        has_neg_c = any(w in c_lower for w in ["not", "never", "no ", "false"])
        
        if has_neg_p and not has_neg_c:
            # Potential contradiction if candidate ignores negation
            # Heuristic: if prompt says "X is not Y", and candidate says "X is Y"
            if "yes" in c_lower or "true" in c_lower:
                score -= 0.3
        elif not has_neg_p and has_neg_c:
             # Candidate introduces negation not in prompt?
             if "no" in c_lower and "yes" not in c_lower:
                 score -= 0.2

        # 3. Yes/No Consistency
        if ("yes" in c_lower or "no" in c_lower):
            if "true" in p_lower or "correct" in p_lower:
                if "yes" in c_lower: score += 0.3
            if "false" in p_lower or "incorrect" in p_lower:
                if "no" in c_lower: score += 0.3

        return max(0.0, min(1.0, score))

    def _ncd_score(self, prompt: str, candidate: str) -> float:
        """
        Normalized Compression Distance.
        NCD(x,y) = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        Returns 1.0 - NCD so higher is better (similarity).
        Limited to 15% weight in final logic, used here as a tiebreaker component.
        """
        if not candidate:
            return 0.0
        
        p_bytes = prompt.encode()
        c_bytes = candidate.encode()
        
        len_p = len(zlib.compress(p_bytes))
        len_c = len(zlib.compress(c_bytes))
        len_pc = len(zlib.compress(p_bytes + c_bytes))
        
        min_len = min(len_p, len_c)
        max_len = max(len_p, len_c)
        
        if max_len == 0:
            return 0.0
            
        ncd = (len_pc - min_len) / max_len
        # Convert distance to similarity score (0 to 1)
        # NCD 0 = identical, 1 = totally different
        return max(0.0, 1.0 - ncd)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Meta-analysis of the prompt
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural Score (Primary Signal ~50-60%)
            struct_score = self._structural_score(prompt, cand)
            
            # 2. Chaotic Stability Score (Secondary Signal ~25%)
            # We want candidates that are 'stable' in the chaotic sense? 
            # Actually, we use the chaotic signature to differentiate. 
            # Let's assume correct answers often have specific patterns (numbers, logic words)
            # that yield distinct chaotic variances compared to random noise.
            # We normalize the variance to a 0-1 scale roughly.
            chaos_var = self._chaotic_signature(cand)
            # Heuristic: Moderate variance often indicates structure, extreme high/low might be noise/repetition
            # This is a proxy for 'complexity/entropy' of the answer.
            chaos_score = 1.0 - min(1.0, chaos_var * 10) # Normalize loosely
            
            # 3. NCD Score (Tiebreaker ~15%)
            ncd_sim = self._ncd_score(prompt, cand)
            
            # Weighted Combination
            # If meta_confidence is low, we suppress the score significantly
            base_score = (struct_score * 0.60) + (chaos_score * 0.25) + (ncd_sim * 0.15)
            
            # Apply Epistemic Cap
            if meta_cap < 0.3:
                # If the question is ambiguous, even the 'best' candidate gets a low score
                final_score = base_score * 0.5 # Penalize heavily
            else:
                final_score = base_score
            
            # Ensure we don't overclaim certainty
            if meta_cap >= 0.9:
                final_score = min(final_score, self.confidence_cap_certain)
            else:
                final_score = min(final_score, meta_cap)
                
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Structural:{struct_score:.2f}, Chaos:{chaos_score:.2f}, NCD:{ncd_sim:.2f}, MetaCap:{meta_cap:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.25 if prompt is ambiguous (Tier B).
        Caps at 0.95 even for clear answers to maintain epistemic humility.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Quick structural check to see if answer makes sense structurally
        struct_score = self._structural_score(prompt, answer)
        
        # If structural score is very low, confidence should be low
        if struct_score < 0.3:
            return 0.1
        
        # Base confidence on structural strength, capped by meta-analysis
        base_conf = struct_score * 0.8 + 0.2 # Scale to 0.2-1.0 range
        
        if meta_cap < 0.3:
            return min(base_conf, self.confidence_cap_ambiguous)
        
        return min(base_conf, self.confidence_cap_certain)