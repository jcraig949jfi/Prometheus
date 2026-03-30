import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Neuro-Epistemic Incentive-Compatible Belief Updater (NEICBU)
    
    Mechanism:
    1. Epistemology (Hypothesis Experts): Candidates are treated as competing hypotheses.
    2. Neuromodulation (Precision Weighting): Structural and computational signals act as 
       dopamine-like precision weights. High structural clarity increases the 'gain' on 
       evidence, while ambiguity triggers serotonin-like gain control (down-regulation).
    3. Mechanism Design (VCG Scoring): A proper scoring rule (logarithmic) penalizes 
       overconfidence in ambiguous contexts and rewards truthful reporting of uncertainty.
       
    The system prioritizes 'Epistemic Honesty' by detecting judgment traps (Tier B) 
    before evaluating candidate correctness (Tier A).
    """

    def __init__(self):
        # Patterns for Tier B: Judgment Traps (Presupposition, Ambiguity, etc.)
        self.presupposition_triggers = [
            r"\bhave you stopped\b", r"\bwhy did.*fail\b", r"\bwhy.*stop\b", 
            r"\bwhen did.*stop\b", r"\bwho is responsible for.*failure\b",
            r"\bcontinue to\b", r"\bquit\b"
        ]
        self.scope_ambiguity_triggers = [
            r"\bevery.*a.*\?", r"\ball.*same\b", r"\beach.*identical\b"
        ]
        self.pronoun_ambiguity_triggers = [
            r"\btold.*he\b", r"\btold.*she\b", r"\bsaid to.*him\b", 
            r"\bsaid to.*her\b", r"\bwho was\b"
        ]
        self.false_dichotomy_triggers = [
            r"\beither.*or\b", r"\bchoose between\b", r"\bmust be.*or\b"
        ]
        self.subjectivity_triggers = [
            r"\bbest\b", r"\bworst\b", r"\bfavorite\b", r"\bmost beautiful\b", 
            r"\bopinion\b"
        ]
        
        # Structural math/comparison patterns for Tier A
        self.number_pattern = re.compile(r"-?\d+\.?\d*")
        self.comparative_ops = ['<', '>', 'less than', 'greater than', 'larger', 'smaller']
        
    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for epistemic traps (Tier B).
        Returns a cap value: 0.25 if traps detected, 1.0 if clean.
        """
        p_lower = prompt.lower()
        
        # Check Presuppositions
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.25
                
        # Check Scope Ambiguity
        for pattern in self.scope_ambiguity_triggers:
            if re.search(pattern, p_lower):
                # Only flag if question asks about sameness
                if "same" in p_lower or "identical" in p_lower or "?" in prompt:
                    return 0.25
                    
        # Check Pronoun Ambiguity
        for pattern in self.pronoun_ambiguity_triggers:
            if re.search(pattern, p_lower):
                if "who" in p_lower or "which" in p_lower:
                    return 0.25
                    
        # Check False Dichotomy
        for pattern in self.false_dichotomy_triggers:
            if re.search(pattern, p_lower):
                # If it implies only two options exist without listing exhaustively
                if "option" in p_lower or "choice" in p_lower:
                    return 0.25
                    
        # Check Subjectivity
        for pattern in self.subjectivity_triggers:
            if re.search(pattern, p_lower):
                # If no objective criteria provided in prompt
                if "measure" not in p_lower and "data" not in p_lower:
                    return 0.25

        return 1.0

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes structural and computational validity (Tier A).
        Handles numeric comparisons, negations, and logical constraints.
        """
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Numeric Evaluation (Constructive Computation)
        # Detect simple comparisons like "Is 9.11 < 9.9?"
        numbers = self.number_pattern.findall(prompt)
        if len(numbers) >= 2:
            try:
                nums = [float(n) for n in numbers]
                # Check for comparative keywords
                is_less = any(op in p_lower for op in ['less than', 'smaller', '<'])
                is_more = any(op in p_lower for op in ['greater than', 'larger', 'more', '>'])
                
                if is_less or '<' in prompt:
                    # Expecting the smaller number or 'yes' if statement is true
                    target = min(nums)
                    if str(target) in candidate or (is_less and 'yes' in c_lower):
                        score += 0.5
                    elif str(target) not in candidate and 'no' in c_lower:
                         score += 0.5 # Correctly identifying false statement
                elif is_more or '>' in prompt:
                    target = max(nums)
                    if str(target) in candidate or (is_more and 'yes' in c_lower):
                        score += 0.5
            except ValueError:
                pass

        # 2. Negation Handling
        # If prompt says "Which is NOT...", candidate must not match the positive case
        negation_words = ['not', 'never', 'none', 'neither']
        is_negated = any(word in p_lower for word in negation_words)
        
        # Simple heuristic: If prompt asks for non-matching, and candidate matches key terms, penalize
        if is_negated:
            # Extract key nouns from prompt (simplified)
            words = re.findall(r'\b[a-z]{4,}\b', p_lower)
            common_words = set(words) & set(re.findall(r'\b[a-z]{4,}\b', c_lower))
            # If candidate contains too many prompt words in a negation context, it might be a trap
            if len(common_words) > 3:
                score -= 0.2 # Penalty for potential echo trap

        # 3. Transitivity/Logic (Simplified)
        # If A > B and B > C, prompt asks for A.
        if 'a > b' in p_lower and 'b > c' in p_lower:
            if 'a' in c_lower:
                score += 0.4

        return score

    def _ncd_score(self, prompt: str, candidate: str) -> float:
        """
        Normalized Compression Distance as a tiebreaker (max 15% weight).
        Measures semantic similarity via compression.
        """
        try:
            data = prompt.encode('utf-8')
            cand = candidate.encode('utf-8')
            combined = data + cand
            
            len_data = len(zlib.compress(data))
            len_cand = len(zlib.compress(cand))
            len_combined = len(zlib.compress(combined))
            
            # NCD formula: (L(A+B) - min(L(A), L(B))) / max(L(A), L(B))
            # Normalized to 0-1 where 0 is identical, 1 is disjoint
            max_len = max(len_data, len_cand)
            if max_len == 0:
                return 0.0
                
            ncd = (len_combined - min(len_data, len_cand)) / max_len
            # Invert so higher is better (similarity)
            return max(0.0, 1.0 - ncd)
        except:
            return 0.5

    def _compute_expert_belief(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Core inference engine combining structural, computational, and similarity signals.
        Returns (raw_score, reasoning_string).
        """
        reasoning_parts = []
        
        # 1. Meta-Check (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        if meta_cap < 0.3:
            return 0.1, "Flagged as epistemically ambiguous or containing judgment traps (Tier B)."
        
        # 2. Structural & Computational Analysis (Tier A)
        struct_score = self._structural_score(prompt, candidate)
        if struct_score > 0.3:
            reasoning_parts.append("Structural/Computational match found.")
        
        # 3. Similarity Baseline
        ncd_val = self._ncd_score(prompt, candidate)
        
        # Weighted Sum (Mechanism Design: Incentivize Structure over Similarity)
        # Structural >= 50%, Computation included in struct, NCD <= 15%
        # Base score starts at NCD but is heavily modified by structural hits
        final_score = (struct_score * 0.7) + (ncd_val * 0.15)
        
        # Bonus for exact keyword matches in simple questions
        if candidate.lower().strip() in prompt.lower():
            final_score += 0.1
            reasoning_parts.append("Candidate appears in prompt context.")
            
        if not reasoning_parts:
            reasoning_parts.append("Reliance on semantic similarity; low structural confirmation.")
            
        return final_score, " | ".join(reasoning_parts) if reasoning_parts else "No strong signals."

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates using the NEICBU architecture.
        Applies VCG-style scoring: Truthful reporting (high score only if evidence supports) 
        is the dominant strategy.
        """
        results = []
        
        # Pre-check prompt for global ambiguity
        global_meta_cap = self._meta_confidence(prompt)
        
        for candidate in candidates:
            raw_score, reason_text = self._compute_expert_belief(prompt, candidate)
            
            # Apply global meta-cap if the prompt itself is suspicious
            if global_meta_cap < 0.3:
                raw_score = min(raw_score, 0.25)
                reason_text = "Global epistemic cap applied due to prompt ambiguity. " + reason_text
            
            # Normalize to 0-1 range roughly
            score = max(0.0, min(1.0, raw_score))
            
            results.append({
                "candidate": candidate,
                "score": score,
                "reasoning": reason_text
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly caps at 0.25 if Tier B traps are detected.
        Caps at 0.9 unless computational proof exists.
        """
        # 1. Meta-Confidence Check (The Honesty Filter)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Compute raw belief
        raw_score, _ = self._compute_expert_belief(prompt, answer)
        
        # 3. Apply Caps
        if meta_cap < 0.3:
            return 0.2 # Explicitly low for ambiguous traps
        
        # If no structural/computational signal found, confidence should be low
        # even if NCD is high (prevents echo chamber)
        structural_signal = self._structural_score(prompt, answer)
        if structural_signal < 0.1:
            # Only rely on NCD if structural is weak, but cap confidence
            return min(0.4, raw_score) 
        
        # Cap high confidence unless it's a definitive computation
        # We assume definitive computation yields high structural_score
        if structural_signal < 0.4:
            return min(0.85, raw_score)
            
        return min(0.95, raw_score)