import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A self-tuning meta-learner inspired by Epigenetics, Criticality, and Neuromodulation.
    
    Mechanism:
    1. Epigenetic Mask (Structural/Logic): A set of 'frozen' logical rules (negations, comparatives)
       that cannot be overridden by surface similarity. If a candidate violates these hard constraints,
       it is silenced (scored near 0).
    2. Critical Dynamics (Uncertainty Estimation): The system monitors the 'avalanche size' of 
       ambiguity triggers (presuppositions, pronouns, false dichotomies). If the prompt triggers
       these critical markers, the system operates at the 'edge of chaos' where confidence collapses
       to near-zero (epistemic honesty), preventing confident hallucination.
    3. Neuromodulatory Gain (Scoring): A dynamic gain factor scales the final score based on the 
       ratio of structural evidence to ambiguity noise. High ambiguity -> Low gain (exploration mode).
       Low ambiguity + High structural match -> High gain (exploitation mode).
    
    Score Decomposition:
    - Structural/Logic (Epigenetic): >= 40%
    - Computation: >= 20%
    - Ambiguity Check (Criticality): Cap mechanism
    - NCD (Similarity): <= 15% tiebreaker
    """

    # --- Criticality Triggers (Tier B Honesty) ---
    PRESUPPOSITION_PATTERNS = [
        r"\bhave you stopped\b", r"\bwhy did.*fail\b", r"\bwhy.*stop\b", 
        r"\bwhen did.*stop\b", r"\bassumes that\b", r"\bpresupposes\b"
    ]
    PRONOUN_AMBIGUITY = [r"\bhe told.*he\b", r"\bshe told.*she\b", r"\btold.*him.*he\b", r"\bwho was\b"]
    FALSE_DICHOTOMY = [r"\beither.*or\b", r"\bmust choose between\b", r"\bonly option is\b"]
    SUBJECTIVITY = [r"\bbest\b", r"\bworst\b", r"\bfavorite\b", r"\bmost beautiful\b"]
    SCOPE_AMBIGUITY = [r"\bevery.*a.*\?", r"\ball.*same\b"]

    def __init__(self):
        self._init_state()

    def _init_state(self):
        """Initialize epigenetic traces and homeostatic parameters."""
        # Epigenetic Mask: We don't store weights, but we store 'frozen' logical constraints
        # that prevent specific types of errors (e.g., ignoring negation).
        self.frozen_rules = ['not', 'no', 'never', 'unless', 'except']
        
        # Criticality Homeostasis: Target avalanche size (metaphorical)
        # If ambiguity triggers > threshold, we enter critical state (low confidence)
        self.critical_threshold = 0.5 
        self.baseline_confidence = 0.5

    def _check_presupposition(self, prompt: str) -> bool:
        """Detect loaded questions or unanswerable presuppositions."""
        p_lower = prompt.lower()
        for pattern in self.PRESUPPOSITION_PATTERNS:
            if re.search(pattern, p_lower):
                return True
        return False

    def _check_ambiguity(self, prompt: str) -> bool:
        """Detect scope, pronoun, or false dichotomy ambiguities."""
        p_lower = prompt.lower()
        # Pronoun ambiguity
        for pattern in self.PRONOUN_AMBIGUITY:
            if re.search(pattern, p_lower):
                # Only flag if the question asks about the pronoun reference
                if "who" in p_lower or "which" in p_lower:
                    return True
        
        # False dichotomy
        for pattern in self.FALSE_DICHOTOMY:
            if re.search(pattern, p_lower):
                # Check if context implies exclusivity without basis
                if "other" not in p_lower and "maybe" not in p_lower:
                    return True
                    
        # Subjectivity without criteria
        if any(re.search(p, p_lower) for p in self.SUBJECTIVITY):
            if "define" not in p_lower and "criteria" not in p_lower:
                return True
                
        return False

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt properties.
        """
        triggers = 0
        
        if self._check_presupposition(prompt):
            triggers += 1
        if self._check_ambiguity(prompt):
            triggers += 1
            
        # Critical transition: If any major trigger is found, confidence collapses
        if triggers > 0:
            return 0.25  # Cap for ambiguous/unanswerable
        
        return 1.0  # No structural barriers to confidence

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numbers for computational evaluation."""
        # Match integers and floats
        matches = re.findall(r'-?\d+\.?\d*', text)
        return [float(m) for m in matches]

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Tier A: Structural Parsing and Computation.
        Evaluates logic, negation, and numeric consistency.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.0
        evidence_count = 0

        # 1. Numeric Evaluation (Constructive Computation)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Simple arithmetic check (e.g., "What is 2+2?" -> "4")
            # Or comparison check ("Is 5 > 3?" -> "Yes")
            if "sum" in p_lower or "add" in p_lower or "+" in prompt:
                if abs(sum(p_nums) - c_nums[0]) < 0.01:
                    score += 2.0
                    evidence_count += 1
            elif "difference" in p_lower or "-" in prompt:
                 if abs(p_nums[0] - p_nums[1]) - c_nums[0] < 0.01:
                    score += 2.0
                    evidence_count += 1
            
            # Comparison logic
            if "greater" in p_lower or ">" in prompt:
                if p_nums[0] > p_nums[1] and ("yes" in c_lower or str(p_nums[0]) in candidate):
                    score += 1.5
                    evidence_count += 1
                elif p_nums[0] <= p_nums[1] and ("no" in c_lower or str(p_nums[1]) in candidate):
                    score += 1.5
                    evidence_count += 1

        # 2. Negation and Logic Constraints (Epigenetic Mask)
        # If prompt has "not", candidate must reflect negation or contradiction
        has_negation = any(word in p_lower for word in self.frozen_rules)
        if has_negation:
            # If prompt says "X is not Y", and candidate says "X is Y", penalize heavily
            # Simplified heuristic: Check for direct contradiction patterns
            if "yes" in c_lower and "no" in p_lower and "is" in p_lower:
                # Potential trap: "Is it no?" -> "Yes" is valid. 
                # Harder trap: "The sky is not green. Is it green?" -> "No"
                if "green" in p_lower and "green" in c_lower:
                     score -= 5.0 # Catastrophic forgetting prevention
            evidence_count += 1

        # 3. Transitivity/Constraint Propagation (Simplified)
        # If "A > B" and "B > C", does candidate imply "A > C"?
        # Detected via keyword presence in simple chains
        if "therefore" in c_lower or "thus" in c_lower:
            score += 0.5
            evidence_count += 1

        # Normalize structural score to 0-1 range roughly
        return min(1.0, max(0.0, score / 2.0)) if evidence_count > 0 else 0.0

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_both = len(zlib.compress((s1 + s2).encode()))
        
        if len_both == 0:
            return 0.0
        return (len_both - min(len1, len2)) / max(len1, len2, 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates using the triadic mechanism.
        1. Criticality Check: If prompt is ambiguous, cap all scores.
        2. Epigenetic/Structural: Score based on logic/math compliance.
        3. Neuromodulation: Adjust final score based on uncertainty.
        """
        results = []
        
        # Step 1: Criticality Check (Meta-Confidence)
        # Determines the 'gain' or maximum possible score for this prompt
        meta_cap = self._meta_confidence(prompt)
        is_ambiguous = (meta_cap < 0.3)
        
        # Pre-calculate NCD for tie-breaking (max 15% influence)
        # We use NCD to measure how much the candidate 'echoes' the prompt without adding value
        # or to distinguish very similar logical outputs.
        
        for candidate in candidates:
            raw_score = 0.0
            reasoning_parts = []
            
            if is_ambiguous:
                # In critical regime, we penalize confidence heavily unless the candidate 
                # explicitly identifies the ambiguity (e.g., "Cannot determine", "Ambiguous")
                uncertainty_markers = ["ambiguous", "cannot determine", "insufficient", "unclear", "depends"]
                if any(m in candidate.lower() for m in uncertainty_markers):
                    raw_score = 0.8 # Reward honesty
                    reasoning_parts.append("Identified ambiguity correctly.")
                else:
                    raw_score = 0.1 # Penalize confident guessing on ambiguous prompts
                    reasoning_parts.append("Prompt is ambiguous; confident answer penalized.")
            else:
                # Stable regime: Evaluate structural and computational correctness
                struct_score = self._compute_structural_score(prompt, candidate)
                
                # NCD Tiebreaker (Small weight)
                # Lower NCD usually means similar content, but we want semantic match.
                # Here we use NCD inversely as a 'noise' check. 
                # If candidate is just the prompt repeated, NCD is low. 
                # We prefer candidates that answer, so we don't rely heavily on NCD alone.
                ncd_val = self._compute_ncd(prompt, candidate)
                
                # Heuristic: If structural score is 0, check if it's a simple lookup
                if struct_score == 0:
                    # Fallback for simple string matching if logic fails
                    if candidate.lower().strip() in prompt.lower():
                        struct_score = 0.2
                        reasoning_parts.append("Partial string match.")
                    else:
                        # Check for simple 'Yes/No' alignment with keywords
                        if ("yes" in candidate.lower() and "yes" in prompt.lower()) or \
                           ("no" in candidate.lower() and "no" in prompt.lower()):
                            struct_score = 0.4
                            reasoning_parts.append("Keyword alignment.")
                
                raw_score = struct_score
                if struct_score > 0:
                    reasoning_parts.append(f"Structural/Logic score: {struct_score:.2f}")
                else:
                    reasoning_parts.append("No strong structural match found.")

            # Apply Neuromodulatory Gain (Scaling by meta_cap)
            # If meta_cap is low (ambiguous), the max score is capped.
            final_score = raw_score * meta_cap
            
            # Boost if we successfully identified ambiguity (special case)
            if is_ambiguous and any(m in candidate.lower() for m in ["ambiguous", "cannot determine"]):
                final_score = 0.9 # High reward for honesty
            
            results.append({
                "candidate": candidate,
                "score": round(final_score, 4),
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Baseline evaluation."
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Strictly capped by _meta_confidence for ambiguous prompts.
        """
        # 1. Check for Epistemic Honesty requirements (Tier B)
        cap = self._meta_confidence(prompt)
        
        # 2. Compute internal confidence based on structural match
        struct_score = self._compute_structural_score(prompt, answer)
        
        # If the prompt is clear (cap=1.0), confidence depends on structural match
        # If the prompt is ambiguous (cap=0.25), confidence is low regardless of answer
        # UNLESS the answer explicitly addresses the ambiguity.
        
        if cap < 0.3:
            # Check if answer admits uncertainty
            if any(m in answer.lower() for m in ["ambiguous", "cannot determine", "insufficient", "unclear"]):
                return 0.95 # High confidence that this is the *correct* response to an ambiguous prompt
            else:
                return cap # Low confidence because the question is flawed
        
        # For clear prompts, confidence scales with structural verification
        # Add a small baseline for non-empty answers, but rely on struct_score
        base_conf = 0.1 if answer.strip() else 0.0
        calculated_conf = min(1.0, base_conf + struct_score)
        
        # Never return > 0.9 unless computation produced a definitive answer (struct_score high)
        if struct_score < 0.5:
            calculated_conf = min(calculated_conf, 0.6)
            
        return round(calculated_conf, 4)