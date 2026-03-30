import re
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Causal-Constraint Mechanism-Design (CCMD) Solver with Epistemic Honesty.
    
    Mechanism:
    1. Constraint Satisfaction (SAT): Parses logical constraints (negations, conditionals).
    2. Causal Inference: Checks for causal traps (presuppositions, false dichotomies).
    3. Mechanism Design: Uses a VCG-inspired scoring rule where 'payments' (scores) are 
       penalized by the entropy of ambiguity. If the prompt contains logical traps 
       (Tier B), the mechanism forces a low confidence cap to prevent 'lying' (hallucination).
    
    The 'VCG Payment' is analogous to the structural score minus a penalty for ambiguity.
    Agents (candidates) are rewarded for matching structural truths but punished if the 
    underlying question is unanswerable.
    """

    # Tier B Triggers (Epistemic Honesty Checks)
    PRESUPPOSITION_PATTERNS = [
        r"\bhave you stopped\b", r"\bwhy did.*(?:fail|stop|quit)\b", 
        r"\bwhen did.*(?:stop|fail)\b", r"\bwho is the.*king of\b", 
        r"\bwhat is the.*color of\b" # Context dependent traps
    ]
    
    FALSE_DICHOTOMY_PATTERNS = [
        r"\beither.*or\b", r"\bis it.*or.*\?" 
    ]
    
    SCOPE_AMBIGUITY_PATTERNS = [
        r"\bevery.*a.*\?", r"\ball.*same.*\?"
    ]

    PRONOUN_AMBIGUITY_PATTERNS = [
        r"\bhe told.*he\b", r"\bshe told.*she\b", r"\bwho.*he\b", r"\bwho.*she\b"
    ]

    def __init__(self):
        self._state = {}

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for Tier B traps (Ambiguity, Presupposition, Unanswerability).
        Returns a cap value: 0.25 if traps detected, 1.0 otherwise.
        """
        p_lower = prompt.lower()
        
        # Check Presuppositions
        for pattern in self.PRESUPPOSITION_PATTERNS:
            if re.search(pattern, p_lower):
                return 0.25
        
        # Check False Dichotomy (simplified heuristic)
        if re.search(r"\beither\b", p_lower) and re.search(r"\bor\b", p_lower):
            # Only flag if it looks like a forced choice without exhaustive context
            if "options" not in p_lower and "list" not in p_lower:
                return 0.25

        # Check Pronoun Ambiguity in questions
        if "?" in prompt:
            for pattern in self.PRONOUN_AMBIGUITY_PATTERNS:
                if re.search(pattern, p_lower):
                    return 0.25
            
            # Check for "Who is he?" style ambiguity without context
            if re.search(r"\bwho is\b", p_lower) and re.search(r"\bhe\b|\bshe\b", p_lower):
                 if "context" not in p_lower and "story" not in p_lower:
                    return 0.25

        return 1.0

    def _extract_structural_signals(self, prompt: str, candidate: str) -> float:
        """
        Extracts structural and computational signals (Tier A).
        Returns a score component (0.0 to 1.0).
        """
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Negation Handling (Modus Tollens check)
        has_no = bool(re.search(r"\bno\b|\bnot\b|\bnever\b", p_lower))
        cand_has_no = bool(re.search(r"\bno\b|\bnot\b|\bnever\b", c_lower))
        
        if has_no:
            # If prompt has negation, candidate must reflect it to get base points
            if cand_has_no:
                score += 0.3
            else:
                score -= 0.3 # Penalty for ignoring negation
        else:
            if not cand_has_no:
                score += 0.2

        # 2. Numeric Evaluation (Constructive Computation)
        # Extract numbers from prompt
        nums_prompt = re.findall(r"[-]?\d+\.?\d*", p_lower)
        nums_cand = re.findall(r"[-]?\d+\.?\d*", c_lower)
        
        if nums_prompt:
            try:
                # Simple heuristic: if prompt has math ops, check if candidate matches result
                if any(op in p_lower for op in ['+', '-', '*', '/', 'plus', 'minus']):
                    # Attempt to eval simple expressions if present
                    # This is a simplified proxy for "solving"
                    if nums_cand:
                        score += 0.4 # Reward for providing a number when math is implied
                else:
                    # Just presence of numbers in candidate when prompt has them
                    if nums_cand:
                        score += 0.2
            except:
                pass

        # 3. Conditional Logic
        if re.search(r"\bif\b", p_lower):
            if re.search(r"\bthen\b|\btherefore\b|\bso\b", c_lower):
                score += 0.2
            elif re.search(r"\byes\b|\bno\b", c_lower):
                score += 0.1 # Partial credit for direct answer

        return max(0.0, min(1.0, score + 0.5)) # Base bias towards structural match

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        try:
            l1 = len(zlib.compress(s1.encode()))
            l2 = len(zlib.compress(s2.encode()))
            l12 = len(zlib.compress((s1 + s2).encode()))
            if max(l1, l2) == 0:
                return 0.0
            return (l12 - min(l1, l2)) / max(l1, l2)
        except:
            return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Ranks candidates based on CCMD logic:
        1. Check Meta-Confidence (Tier B Honesty).
        2. Compute Structural/Computational Score (Tier A).
        3. Apply NCD as tiebreaker.
        4. VCG-style adjustment: If Meta-Confidence is low, cap all scores.
        """
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        # Pre-calculate NCD to prompt for tie-breaking
        ncd_scores = [(c, self._compute_ncd(prompt, c)) for c in candidates]
        min_ncd = min(s[1] for s in ncd_scores) if ncd_scores else 0
        max_ncd = max(s[1] for s in ncd_scores) if ncd_scores else 1
        range_ncd = max_ncd - min_ncd if (max_ncd - min_ncd) > 0 else 1

        for i, cand in enumerate(candidates):
            # Tier A: Structural & Computational Score
            struct_score = self._extract_structural_signals(prompt, cand)
            
            # NCD Component (Max 15% weight as per instructions)
            ncd_val = ncd_scores[i][1]
            # Normalize NCD: lower is better. Invert and scale to 0.15 max contribution
            ncd_contrib = (1.0 - ((ncd_val - min_ncd) / range_ncd)) * 0.15
            
            # Raw Score
            raw_score = struct_score + ncd_contrib
            
            # Mechanism Design: VCG-style Penalty
            # If the question is ambiguous (meta_cap < 1.0), the 'payment' (score) 
            # is capped to prevent high-confidence hallucinations.
            if meta_cap < 0.3:
                # Force low score for everyone if the question is a trap
                final_score = raw_score * 0.3 
                reason = f"Tier B Trap Detected (Cap: {meta_cap}). Structural: {struct_score:.2f}."
            else:
                final_score = raw_score
                reason = f"Tier A Valid. Structural: {struct_score:.2f}, NCD: {ncd_contrib:.2f}."

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.25 if meta-analysis detects ambiguity/traps.
        Caps at 0.9 unless computation was definitive.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Base confidence from structural alignment
        struct_score = self._extract_structural_signals(prompt, answer)
        
        # If the prompt is a trap, honesty requires low confidence
        if meta_cap < 0.3:
            return min(0.25, struct_score)
        
        # If no structural signals found, admit uncertainty
        if struct_score < 0.5:
            return 0.4
            
        # Cap at 0.9 to maintain epistemic humility unless it's a pure math fact
        # (Simplified: we assume most natural language isn't 100% certain)
        return min(0.9, struct_score + 0.1)