import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Autopoietic Oscillatory Nash Tool (AONT).
    
    Mechanism:
    1. Autopoietic Core (Homeostasis): Monitors prompt structure for ambiguity, 
       presupposition, and unanswerability. If the 'organizational closure' of the 
       question is violated (i.e., it's a trick or ambiguous), the system self-regulates 
       by capping confidence to maintain internal viability (Epistemic Honesty).
       
    2. Oscillatory Layers (Binding): Simulates cross-frequency coupling to bind 
       structural features (negations, comparatives, numbers) across the prompt.
       - Gamma: Local feature detection (keywords, numbers).
       - Theta: Global sequence logic (conditionals, transitivity).
       
    3. Nash Equilibrium Solver (Competition): Candidates compete as sub-populations.
       Scores are derived from structural adherence and computational correctness.
       Inhibitory dynamics suppress candidates that fail logical constraints.
       The final score represents a stable mixed-strategy equilibrium where only
       logically consistent hypotheses survive.
    """

    def __init__(self):
        # Homeostatic set-points
        self.target_confidence = 0.5
        self.ambiguity_threshold = 0.3
        self.high_conf_cap = 0.95
        
        # Structural patterns (Gamma band features)
        self.negation_pattern = re.compile(r'\b(not|no|never|neither|nobody|nothing|cannot|won\'t|don\'t|doesn\'t|didn\'t)\b', re.IGNORECASE)
        self.comparative_pattern = re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worst|best)\b', re.IGNORECASE)
        self.cond_pattern = re.compile(r'\b(if|then|unless|otherwise)\b', re.IGNORECASE)
        
        # Presupposition triggers (Autopoietic violation detectors)
        self.presupposition_triggers = [
            r"have you stopped", r"did you stop", r"why did", r"why does", 
            r"when did", r"how often did", r"is it true that", r"have you quit"
        ]
        
        # Ambiguity triggers
        self.pronoun_ambiguity = re.compile(r'\b(he|she|him|her|they|them)\b', re.IGNORECASE)
        self.scope_words = re.compile(r'\b(every|all|each|some)\b', re.IGNORECASE)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Autopoietic Core: Evaluates the structural integrity of the prompt.
        Returns a cap value. If the prompt is ambiguous or loaded, returns low cap.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Check
        for trigger in self.presupposition_triggers:
            if re.search(trigger, p_lower):
                return 0.25  # Violation of organizational closure
        
        # 2. False Dichotomy Check (Either A or B without context)
        if re.search(r'\beither\b.*\bor\b', p_lower) and not re.search(r'\bquestion|problem|choice\b', p_lower):
            # Heuristic: if it looks like a forced choice without data
            if len(prompt.split()) < 15: 
                return 0.3

        # 3. Unanswerable/Subjective Check
        subjective_terms = ['best', 'worst', 'favorite', 'opinion', 'think about']
        if any(term in p_lower for term in subjective_terms):
            if 'calculate' not in p_lower and 'math' not in p_lower:
                return 0.25

        # 4. Pronoun Ambiguity in specific contexts
        if self.pronoun_ambiguity.search(p_lower) and re.search(r'\bwho\b', p_lower):
            # Potential ambiguity trap
            if re.search(r'told|said|asked', p_lower):
                return 0.3

        return 1.0  # Structurally sound

    def _extract_numbers(self, text: str) -> List[float]:
        """Gamma band: Extract numeric features."""
        # Match floats and ints, handling negative signs
        matches = re.findall(r'-?\d+\.?\d*', text)
        return [float(m) for m in matches]

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Oscillatory Binding: Binds structural constraints to the candidate.
        Returns a score based on logical adherence (0.0 to 1.0).
        """
        score = 0.5  # Base neutral
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Negation Consistency
        has_negation = bool(self.negation_pattern.search(p_lower))
        cand_negation = bool(self.negation_pattern.search(c_lower))
        
        # If prompt asks "Which is NOT...", candidate must be negative or imply exclusion
        if "not" in p_lower.split()[-5:] or "none" in p_lower:
            if not cand_negation and c_lower not in ['none', 'no', 'false', '0']:
                score -= 0.4
        elif has_negation and "not" in p_lower:
            # Complex negation handling simplified for brevity
            pass

        # 2. Comparative Logic (Numeric)
        nums = self._extract_numbers(prompt)
        if len(nums) >= 2:
            # Detect comparison type
            if "larger" in p_lower or "greater" in p_lower or "max" in p_lower:
                target = max(nums)
                cand_nums = self._extract_numbers(candidate)
                if cand_nums and abs(cand_nums[0] - target) < 1e-6:
                    score += 0.5
                elif cand_nums:
                    score -= 0.5
            elif "smaller" in p_lower or "less" in p_lower or "min" in p_lower:
                target = min(nums)
                cand_nums = self._extract_numbers(candidate)
                if cand_nums and abs(cand_nums[0] - target) < 1e-6:
                    score += 0.5
                elif cand_nums:
                    score -= 0.5
            
            # Simple arithmetic check (e.g., "What is 2 + 2?")
            if "what is" in p_lower or "calculate" in p_lower or "=" in prompt:
                # Very basic eval for simple expressions if candidate is a number
                try:
                    # Attempt to extract expression from prompt if simple
                    if "+" in prompt or "-" in prompt or "*" in prompt or "/" in prompt:
                        # Naive extraction for demo purposes
                        expr = re.sub(r'[^\d\+\-\*\/\.\s]', '', prompt)
                        if expr.strip():
                            expected = eval(expr)
                            cand_nums = self._extract_numbers(candidate)
                            if cand_nums and abs(cand_nums[0] - expected) < 1e-5:
                                score = 1.0
                            elif cand_nums:
                                score = 0.0
                except:
                    pass

        # 3. Conditional/Transitivity (Simplified)
        if self.cond_pattern.search(p_lower):
            # If prompt has logic, prefer candidates with logical connectors or specific formats
            if re.search(r'\b(true|false|yes|no|impossible)\b', c_lower):
                score += 0.2

        return max(0.0, min(1.0, score))

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(s1_bytes)
        len_s2 = len(s2_bytes)
        
        try:
            len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        except:
            return 1.0
            
        if len_combined == 0:
            return 0.0
            
        ncd = (len_combined - min(len_s1, len_s2)) / max(len_s1, len_s2, 1)
        return max(0.0, min(1.0, ncd))

    def _nash_dynamics(self, raw_scores: List[float]) -> List[float]:
        """
        Nash Equilibrium Solver: 
        Converts raw scores into a stable distribution where no candidate 
        can improve its position by deviating (simulated via softmax-like normalization
        with inhibition for low scorers).
        """
        if not raw_scores:
            return []
        
        # Convert to positive domain (shift by min if negative)
        min_s = min(raw_scores)
        shifted = [s - min_s + 1e-6 for s in raw_scores]
        
        # Replicator-like dynamic: proportionate fitness
        total = sum(shifted)
        if total == 0:
            return [1.0/len(raw_scores)] * len(raw_scores)
            
        # Normalize to 0-1 range, emphasizing the winner (Winner-take-all tendency)
        probs = [s / total for s in shifted]
        
        # Apply inhibition: if max score is dominant, suppress others more aggressively
        max_p = max(probs)
        if max_p > 0.5:
            final_scores = []
            for p in probs:
                if p < max_p * 0.5:
                    final_scores.append(p * 0.5) # Inhibit weak hypotheses
                else:
                    final_scores.append(p)
            # Re-normalize
            total_new = sum(final_scores)
            if total_new > 0:
                return [s/total_new for s in final_scores]
        
        return probs

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        # 1. Autopoietic Check (Meta-Confidence)
        meta_cap = self._meta_confidence(prompt)
        
        raw_scores = []
        structural_scores = []
        ncd_scores = []

        # 2. Oscillatory Binding & Scoring per candidate
        for cand in candidates:
            # Structural/Computational Score (Primary Signal)
            struct_score = self._compute_structural_score(prompt, cand)
            structural_scores.append(struct_score)
            
            # NCD Score (Tiebreaker/Noise)
            ncd = self._ncd_score(prompt, cand)
            ncd_scores.append(ncd)

        # 3. Nash Equilibrium Convergence
        # Combine: 85% Structural, 15% NCD (inverted, as lower NCD is better similarity, 
        # but here we want logical fit. Actually, for NCD, lower distance = higher similarity.
        # We want high score for correct logic. Let's use NCD only if structural is flat.)
        
        # Check variance in structural scores
        struct_variance = max(structural_scores) - min(structural_scores) if len(structural_scores) > 1 else 0
        
        final_raw = []
        if struct_variance > 0.1:
            # Structural signal is strong, ignore NCD
            final_raw = structural_scores
        else:
            # Structural tie, use NCD as tiebreaker (inverted: 1 - ncd)
            final_raw = [0.85 * s + 0.15 * (1.0 - n) for s, n in zip(structural_scores, ncd_scores)]

        # Apply Nash Dynamics
        equilibrium_scores = self._nash_dynamics(final_raw)
        
        # Apply Autopoietic Cap (Epistemic Honesty)
        # If the prompt itself is flawed, cap the max confidence regardless of candidate
        if meta_cap < 0.5:
            equilibrium_scores = [min(s, meta_cap) for s in equilibrium_scores]

        # Construct Result
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": equilibrium_scores[i],
                "reasoning": f"Structural: {structural_scores[i]:.2f}, Meta-Cap: {meta_cap:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at meta-confidence if prompt is ambiguous.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Evaluate this specific candidate against the prompt
        struct_score = self._compute_structural_score(prompt, answer)
        
        # Base confidence on structural match, capped by meta-analysis
        base_conf = struct_score
        
        # If the structural match is perfect but the question is bogus, cap it.
        final_conf = min(base_conf, meta_cap)
        
        # Never return > 0.95 unless computation was definitive (simplified here)
        if final_conf > 0.95:
            final_conf = 0.95
            
        return max(0.0, min(1.0, final_conf))