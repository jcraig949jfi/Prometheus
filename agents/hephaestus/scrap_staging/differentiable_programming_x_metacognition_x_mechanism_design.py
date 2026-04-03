import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A Differentiable Meta-Mechanism for Self-Interested Hypothesis Agents.
    
    Implements a computational analog of the proposed architecture:
    1. Hypothesis Generators: Structural parsers and computational solvers (Tier A).
    2. Critic Agents: Epistemic honesty checks for ambiguity and presupposition (Tier B).
    3. Mechanism Design Layer: A smooth, incentive-compatible scoring rule that rewards
       high-utility (correct) and easily verifiable (structural/computational) answers,
       while penalizing overconfidence in ambiguous contexts via a Clarke-Groves inspired
       penalty term approximated through confidence capping.
    4. Metacognitive Controller: Adjusts the weight of structural vs. NCD signals based
       on the detected ambiguity of the prompt.
       
    The system prioritizes Epistemic Honesty (Tier B) while maintaining competence (Tier A).
    """

    def __init__(self):
        # Metacognitive state: Tracks recent ambiguity levels to adjust temperature
        self._ambiguity_rate = 0.0
        self._alpha = 0.5  # Weight for structural/computational signals
        self._beta = 0.35  # Weight for NCD/tie-breaking
        self._gamma = 0.15 # Weight for mechanism penalty
        
        # Preset keywords for Tier B detection
        self._presupposition_triggers = [
            r"have you stopped", r"have you quit", r"why did.*fail", r"why did.*stop",
            r"when did.*stop", r"is it true that.*failed"
        ]
        self._false_dichotomy_triggers = [r"either.*or", r"choose between.*and", r"must.*or"]
        self._subjectivity_triggers = [r"best", r"worst", r"favorite", r"most beautiful", r"opinion"]
        self._pronoun_triggers = [r"who is.*he", r"who is.*she", r"who does.*him refer", r"who does.*her refer"]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Detects ambiguity, presupposition, and unanswerability.
        Returns a cap value (low if ambiguous, 1.0 if clear).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Check
        for pattern in self._presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.25
        
        # 2. False Dichotomy Check
        for pattern in self._false_dichotomy_triggers:
            if re.search(pattern, p_lower):
                # Only flag if no context suggests exhaustive options (simplified heuristic)
                if "only" in p_lower or "exclusive" in p_lower:
                    return 0.25
                # Heuristic: if it asks to choose between two specific things without "or other"
                if re.search(r"either.*or", p_lower):
                    return 0.25

        # 3. Subjectivity Check
        for pattern in self._subjectivity_triggers:
            if re.search(pattern, p_lower):
                # If asking for "best" without data, it's subjective
                if "according to" not in p_lower and "data" not in p_lower:
                    return 0.25

        # 4. Pronoun Ambiguity (Simplified)
        if re.search(r"who is.*he", p_lower) or re.search(r"who is.*she", p_lower):
             if "told" in p_lower or "said" in p_lower:
                return 0.25

        # 5. Unanswerability (Missing info heuristic)
        # If the prompt asks a question but has no numbers/facts and isn't general knowledge
        if "?" in prompt:
            has_facts = bool(re.search(r"\d+", prompt)) or bool(re.search(r"(is|are|was|were)\s+\w+", p_lower))
            if not has_facts and len(prompt.split()) < 10:
                 # Very short questions without facts might be unanswerable contextually
                 pass # Let it pass to structural check, don't hard cap unless obvious
        
        return 1.0

    def _structural_parse(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Tier A: Structural Parsing & Constructive Computation.
        Extracts logic, negations, comparatives, and performs numeric evaluation.
        Returns (score, reasoning_string).
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.0
        reasons = []

        # 1. Numeric Evaluation (Constructive Computation)
        # Detect patterns like "Is 9.11 > 9.9?" or "Which is larger: 5 or 3?"
        numbers = re.findall(r"[-+]?\d*\.?\d+", prompt)
        if len(numbers) >= 2:
            try:
                vals = [float(n) for n in numbers]
                # Check for comparison keywords
                if any(k in p_lower for k in ["larger", "greater", "more", "max", "highest"]):
                    correct_val = max(vals)
                    if str(correct_val) in candidate or f"{correct_val:.2f}" in candidate:
                        score += 0.9
                        reasons.append("Numeric max identified")
                    elif any(str(v) in candidate for v in vals) and str(correct_val) not in candidate:
                        score -= 0.5 # Penalty for wrong numeric choice
                        reasons.append("Numeric max mismatch")
                        
                elif any(k in p_lower for k in ["smaller", "less", "min", "lowest"]):
                    correct_val = min(vals)
                    if str(correct_val) in candidate or f"{correct_val:.2f}" in candidate:
                        score += 0.9
                        reasons.append("Numeric min identified")
                    elif any(str(v) in candidate for v in vals) and str(correct_val) not in candidate:
                        score -= 0.5
                        reasons.append("Numeric min mismatch")
                        
                # Simple arithmetic check (e.g., "What is 2+2?")
                if "?" in prompt and len(numbers) == 2 and any(op in prompt for op in ["+", "-", "*", "plus", "minus"]):
                    # Very basic arithmetic heuristic
                    if "+" in prompt or "plus" in p_lower:
                        target = vals[0] + vals[1]
                    elif "-" in prompt or "minus" in p_lower:
                        target = vals[0] - vals[1]
                    else:
                        target = None
                    
                    if target is not None:
                        if str(target) in candidate or f"{target:.1f}" in candidate:
                            score += 1.0
                            reasons.append("Arithmetic solved")
                        else:
                            score -= 0.5
                            reasons.append("Arithmetic mismatch")
            except ValueError:
                pass

        # 2. Logical Negation & Modus Tollens
        if "not" in p_lower and "true" in p_lower:
            if "false" in c_lower or "no" in c_lower:
                score += 0.6
                reasons.append("Negation logic aligned")
            elif "true" in c_lower or "yes" in c_lower:
                score -= 0.6
                reasons.append("Negation logic failed")

        # 3. Transitivity (A>B, B>C => A>C)
        if "greater" in p_lower and "than" in p_lower:
            # Simplified transitivity check
            if re.search(r"a.*>.*b.*b.*>.*c", p_lower.replace(" ", "")) or re.search(r"a.*>.*b.*b.*>.*c", p_lower):
                 if "a.*c" in c_lower or "first.*last" in c_lower:
                     score += 0.7
                     reasons.append("Transitivity detected")

        if not reasons:
            reasons.append("No structural pattern matched")
            
        return score, "; ".join(reasons)

    def _mechanism_payment(self, base_score: float, confidence_cap: float, is_structural: bool) -> float:
        """
        Mechanism Design Layer: Clarke-Groves inspired smooth payment.
        Incentivizes truthfulness (high confidence only when structural evidence exists).
        Payment = Base Utility - (Social Cost approximated by ambiguity penalty)
        """
        if confidence_cap < 0.3:
            # If the meta-cognitive controller detects ambiguity, the "payment" for high confidence is negative
            # This forces the score down regardless of base_score, enforcing honesty.
            return base_score * 0.2 
        
        # Smooth softmax-like adjustment
        # If structural evidence is strong, boost score. If weak, rely on NCD but capped.
        adjustment = 1.0
        if is_structural and base_score > 0.5:
            adjustment = 1.2 # Reward verifiable hypotheses
        elif not is_structural and base_score > 0.5:
            adjustment = 0.8 # Penalize non-verifiable high scores slightly
            
        return min(1.0, base_score * adjustment * confidence_cap)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        len1 = len(s1.encode('utf-8'))
        len2 = len(s2.encode('utf-8'))
        if len1 == 0 or len2 == 0:
            return 1.0
        
        concat = s1 + s2
        len_concat = len(concat.encode('utf-8'))
        
        # NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Approximation using lengths as proxy for complexity if compression ratios are similar
        # Real NCD requires compressing each.
        c1 = len(zlib.compress(s1.encode('utf-8')))
        c2 = len(zlib.compress(s2.encode('utf-8')))
        c12 = len(zlib.compress(concat.encode('utf-8')))
        
        min_c = min(c1, c2)
        max_c = max(c1, c2)
        
        if max_c == 0:
            return 1.0
            
        ncd = (c12 - min_c) / max_c
        return max(0.0, min(1.0, ncd))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # 1. Metacognitive Assessment of the Prompt
        meta_cap = self._meta_confidence(prompt)
        is_ambiguous = meta_cap < 0.3
        
        # 2. Evaluate each candidate (Hypothesis Generator & Critic)
        for candidate in candidates:
            # Structural Parse (Tier A)
            struct_score, struct_reason = self._structural_parse(prompt, candidate)
            has_structural_match = struct_score > 0.5
            
            # NCD Score (Baseline/Tiebreaker)
            # Invert NCD so 1.0 is perfect match, 0.0 is totally different
            ncd_val = self._compute_ncd(prompt, candidate)
            # Heuristic: If candidate is very short (Yes/No) and prompt is long, NCD is high (bad).
            # We want semantic similarity. 
            # Since we can't do semantic similarity without models, we use NCD as a weak tiebreaker.
            # If the candidate is a subset of the prompt or vice versa, it might be relevant.
            # Better approach for NCD here: Compare candidate to a "ideal" template? 
            # No, stick to prompt-candidate NCD but weight it low.
            ncd_score = 1.0 - ncd_val 
            
            # Combine Scores
            # If structural match found, it dominates (Weight ~0.7)
            # If no structural match, rely on NCD but heavily discounted by ambiguity
            
            final_score = 0.0
            reasoning_parts = []
            
            if has_structural_match:
                final_score = struct_score
                reasoning_parts.append(f"Structural: {struct_reason}")
            else:
                # Fallback to NCD if no logic found, but penalize heavily if ambiguous
                if is_ambiguous:
                    final_score = ncd_score * 0.1 # Strong penalty
                    reasoning_parts.append("Ambiguous prompt; low confidence fallback")
                else:
                    final_score = ncd_score * 0.4 # Weak signal
                    reasoning_parts.append(f"No structure; NCD similarity: {ncd_score:.2f}")

            # 3. Mechanism Payment Application
            # Apply the incentive-compatible rule
            payment_score = self._mechanism_payment(final_score, meta_cap, has_structural_match)
            
            # Ensure score is within [0, 1]
            payment_score = max(0.0, min(1.0, payment_score))
            
            # If ambiguous, force score down even if NCD is high
            if is_ambiguous:
                payment_score = min(payment_score, 0.25)
                reasoning_parts.append("Meta-cap applied: Ambiguity detected")

            results.append({
                "candidate": candidate,
                "score": payment_score,
                "reasoning": "; ".join(reasoning_parts)
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly enforces epistemic honesty caps.
        """
        # 1. Meta Check (The "Critic")
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural Check (The "Generator")
        struct_score, _ = self._structural_parse(prompt, answer)
        has_structure = struct_score > 0.5
        
        # 3. Base Confidence Calculation
        base_conf = 0.5
        if has_structure:
            base_conf = 0.85 # High confidence if logic holds
        else:
            # If no structure, check NCD just in case it's a tautology
            ncd = self._compute_ncd(prompt, answer)
            if ncd < 0.2: # Very similar strings
                base_conf = 0.6
            else:
                base_conf = 0.3 # Low confidence for guesswork

        # 4. Apply Mechanism Cap
        final_conf = base_conf * meta_cap
        
        # Hard constraints from prompt requirements
        if meta_cap < 0.3:
            return min(final_conf, 0.25)
        
        # Never return > 0.9 unless computation produced definitive answer
        if not has_structure:
            final_conf = min(final_conf, 0.85)
            
        return max(0.0, min(1.0, final_conf))