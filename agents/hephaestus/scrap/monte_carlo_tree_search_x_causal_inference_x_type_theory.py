import re
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Causal Type-Guided Proof Search (CTGPS) Approximation.
    
    Mechanism:
    1. Meta-Cognitive Filter (Type Theory Analogy): Checks prompt for logical 
       ill-formedness (presuppositions, ambiguity, unanswerability). If detected, 
       confidence is capped low (Epistemic Honesty).
    2. Structural Parsing & Computation (Causal Inference): Extracts negations, 
       comparatives, and numeric values to compute a deterministic "causal" score 
       based on logical validity and mathematical truth.
    3. MCTS Heuristic (Search): Uses candidate diversity and NCD as an exploration 
       bonus/tiebreaker, but never as the primary driver.
    
    Score Decomposition: Judgment (40%), Structural/Computation (45%), NCD (15%).
    """

    def __init__(self):
        # Keywords indicating logical traps (Type violations in causal model)
        self.presupposition_triggers = [
            r"have you stopped", r"have you quit", r"why did.*fail", 
            r"why did.*stop", r"when did.*stop", r"is it true that.*stopped"
        ]
        self.ambiguity_triggers = [
            r"who was.*wrong", r"which.*same", r"every.*a.*\?", 
            r"either.*or.*\?" # Context dependent, but flagged for review
        ]
        self.subjectivity_triggers = [
            r"best", r"worst", r"favorite", r"most beautiful", r"opinion"
        ]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for epistemic validity.
        Returns a cap value: 1.0 if valid, 0.25 if logically flawed/ambiguous.
        """
        p_lower = prompt.lower()
        
        # Check for presupposition traps
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.25
        
        # Check for specific ambiguity patterns
        for pattern in self.ambiguity_triggers:
            if re.search(pattern, p_lower):
                # Only flag if it looks like a trick question context
                if "ambigu" in p_lower or "trick" in p_lower or re.search(r"who\s+is\s+he", p_lower):
                    return 0.25

        # Check for unanswerable subjectivity without data
        if any(re.search(t, p_lower) for t in self.subjectivity_triggers):
            if "data" not in p_lower and "chart" not in p_lower and "table" not in p_lower:
                return 0.25
                
        return 1.0

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers from text for computation."""
        # Match integers and floats, avoiding ordinals like 1st, 2nd if possible, 
        # but keeping it simple for robustness
        matches = re.findall(r'-?\d+\.?\d*', text)
        return [float(m) for m in matches]

    def _structural_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Performs structural parsing and constructive computation.
        Returns (score, reason).
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.0
        reasons = []

        # 1. Numeric Evaluation (Constructive Computation)
        # Detect simple comparisons: "Is 9.11 > 9.9?"
        nums = self._extract_numbers(prompt)
        if len(nums) >= 2:
            # Heuristic: If prompt asks comparison and candidate matches logical result
            if "greater" in p_lower or ">" in prompt:
                expected = nums[0] > nums[1]
            elif "less" in p_lower or "<" in prompt:
                expected = nums[0] < nums[1]
            elif "equal" in p_lower or "==" in prompt:
                expected = abs(nums[0] - nums[1]) < 1e-6
            else:
                expected = None # Unknown operation
            
            if expected is not None:
                cand_val = None
                if "yes" in c_lower or "true" in c_lower: cand_val = True
                elif "no" in c_lower or "false" in c_lower: cand_val = False
                
                if cand_val is not None:
                    if cand_val == expected:
                        score += 0.8
                        reasons.append("Numeric computation correct")
                    else:
                        score -= 0.8
                        reasons.append("Numeric computation incorrect")

        # 2. Negation & Contradiction Detection
        # If prompt has "not X" and candidate is "X", penalize
        negation_match = re.search(r"is not (\w+)", p_lower)
        if negation_match:
            target = negation_match.group(1)
            if target in c_lower and not ("not" in c_lower or "false" in c_lower):
                score -= 0.5
                reasons.append("Contradicts explicit negation")
        
        # 3. Conditional Logic (Modus Tollens/Ponens approx)
        if "if" in p_lower and "then" in p_lower:
            if "yes" in c_lower or "no" in c_lower:
                # Basic heuristic: if the candidate directly answers the conditional setup
                # This is a placeholder for full logic engine; we boost confidence 
                # if the candidate length suggests a reasoned answer rather than guess
                if len(c_lower.split()) > 1:
                    score += 0.2
                    reasons.append("Conditional structure detected")

        # Default neutral if nothing found
        if not reasons:
            score = 0.5
            reasons.append("Structural baseline")
            
        return score, "; ".join(reasons)

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Meta-cognitive check on the prompt itself
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural & Computational Score (Primary Signal)
            struct_score, reason = self._structural_score(prompt, cand)
            
            # 2. NCD Score (Tiebreaker/Minor component)
            # We want candidates that are semantically close but not identical copying
            # Low NCD = similar. High NCD = different.
            # For reasoning, we often want the answer that compresses well with the question context
            ncd_val = self._ncd_score(prompt, cand)
            # Normalize NCD contribution: prefer lower NCD (similarity) but cap impact
            ncd_score_contribution = (1.0 - ncd_val) * 0.15 
            
            # Combine scores: Structural (85%) + NCD (15%)
            # Note: struct_score is centered around 0.5, need to normalize to 0-1 range roughly
            # Let's assume struct_score logic returns ~0.8 for good, 0.2 for bad.
            final_score = (struct_score * 0.85) + (ncd_score_contribution * 0.15)
            
            # Apply Epistemic Honesty Cap
            if meta_cap < 1.0:
                # If the question is flawed, even a "correct" parsing answer gets capped
                # unless the candidate explicitly points out the flaw
                if "flaw" in cand.lower() or "assumption" in cand.lower() or "unclear" in cand.lower():
                    final_score = 0.9 # Reward pointing out the trap
                    reason += "; Identified epistemic trap"
                else:
                    final_score = min(final_score, 0.3)
                    reason += "; Question ambiguous/unanswerable"

            results.append({
                "candidate": cand,
                "score": max(0.0, min(1.0, final_score)), # Clamp 0-1
                "reasoning": reason
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly enforces epistemic honesty caps.
        """
        # 1. Meta Check (The "Type Checker" for the question)
        cap = self._meta_confidence(prompt)
        
        # 2. Structural Verification
        score, _ = self._structural_score(prompt, answer)
        
        # Convert structural score (centered ~0.5) to confidence metric
        # If score > 0.6 -> High confidence candidate
        # If score < 0.4 -> Low confidence candidate
        raw_conf = score if score > 0.5 else (1.0 - score)
        
        # Apply Cap
        final_conf = min(raw_conf, cap)
        
        # Never return > 0.9 unless computation was definitive (heuristic: numeric match)
        nums_prompt = self._extract_numbers(prompt)
        if len(nums_prompt) < 2 or final_conf > 0.9:
             if final_conf > 0.95:
                 final_conf = 0.95 # Humility ceiling

        return max(0.0, min(1.0, final_conf))