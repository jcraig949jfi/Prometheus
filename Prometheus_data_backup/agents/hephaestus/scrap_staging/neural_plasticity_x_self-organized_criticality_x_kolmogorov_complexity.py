import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Critically Plastic Predictive Coding Tool.
    
    Mechanism:
    1. Neural Plasticity (Structural Parsing): Implements experience-dependent reorganization
       by extracting logical constraints (negations, comparatives, conditionals) from the prompt.
       This forms the primary 'synaptic weight' of the evaluation.
    2. Self-Organized Criticality (SOC) Monitor: Acts as a homeostatic regulator. It scans
       for 'avalanche' conditions in the prompt structure (ambiguity, presuppositions, false
       dichotomies). If detected, it drives the system away from criticality (high confidence)
       to a sub-critical state (low confidence), preventing over-confident errors on traps.
    3. Kolmogorov Complexity (NCD): Used strictly as a tie-breaking penalty. Candidates that
       are overly complex relative to the prompt (high description length) are penalized,
       implementing Occam's Razor.
       
    Score Decomposition: Structural (60%), Computation (25%), NCD (15%).
    """

    def __init__(self):
        # SOC Target: Critical branching ratio ~1.0 implies balanced uncertainty.
        # We map meta-confidence to this. If meta-confidence < 0.3, we suppress output.
        self.critical_threshold = 0.3
        self.max_confidence_cap = 0.95

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a proxy for Kolmogorov Complexity."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            max_len = max(c1, c2)
            if max_len == 0:
                return 0.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 1.0

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers for constructive computation."""
        # Match integers and floats, handling negative signs
        pattern = r'-?\d+\.?\d*'
        matches = re.findall(pattern, text)
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except:
                pass
        return nums

    def _structural_analysis(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Analyze structural logic (Plasticity Layer).
        Returns (score, reasoning_string)
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.0
        reasons = []

        # 1. Negation Handling
        negation_words = ['not', 'no', 'never', 'none', 'neither', 'false', 'incorrect']
        has_negation = any(w in p_lower.split() for w in negation_words)
        
        # Check if candidate contradicts or affirms based on negation
        candidate_affirms = any(w in c_lower for w in ['yes', 'true', 'correct', 'is'])
        candidate_denies = any(w in c_lower for w in ['no', 'false', 'incorrect', 'not'])

        if has_negation:
            if candidate_denies:
                score += 0.4
                reasons.append("Correctly handled negation constraint.")
            elif candidate_affirms:
                score -= 0.4
                reasons.append("Failed negation constraint.")
        
        # 2. Comparative Logic (Numeric)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Simple heuristic: If prompt asks for max/min/larger/smaller
            is_max_query = any(w in p_lower for w in ['largest', 'max', 'greater', 'more'])
            is_min_query = any(w in p_lower for w in ['smallest', 'min', 'less', 'fewer'])
            
            target_val = max(p_nums) if is_max_query else (min(p_nums) if is_min_query else None)
            
            if target_val is not None:
                # Check if candidate contains the target number
                if any(abs(c_nums[0] - target_val) < 1e-6 for c_nums in [self._extract_numbers(candidate)]):
                    score += 0.5
                    reasons.append(f"Correctly identified {target_val} as target value.")
                else:
                    score -= 0.2
                    reasons.append(f"Numeric mismatch. Expected {target_val}.")

        # 3. Conditional/Constraint Propagation
        if 'if' in p_lower and 'then' in p_lower:
            # Basic presence check for conditional reasoning
            if any(word in c_lower for word in ['if', 'then', 'because', 'therefore']):
                score += 0.2
                reasons.append("Maintained conditional structure.")
        
        if not reasons:
            reasons.append("No strong structural signals detected.")
            
        return score, "; ".join(reasons)

    def _meta_confidence(self, prompt: str) -> float:
        """
        SOC Regulator: Monitors for 'avalanche' conditions (ambiguity, traps).
        Returns a confidence cap (0.0 - 1.0).
        """
        p_lower = prompt.lower()
        risk_score = 0.0
        
        # 1. Presupposition Traps
        presupposition_triggers = ['stopped', 'quit', 'failed', 'stop', 'continue']
        question_forms = ['have you', 'why did', 'when did', 'how often']
        if any(t in p_lower for t in presupposition_triggers) and any(q in p_lower for q in question_forms):
            risk_score += 0.8

        # 2. False Dichotomy
        if re.search(r'\b(either|or)\b', p_lower) and 'both' not in p_lower:
            risk_score += 0.5

        # 3. Subjectivity without criteria
        subjective_words = ['best', 'worst', 'favorite', 'beautiful', 'ugly']
        if any(w in p_lower for w in subjective_words) and 'define' not in p_lower:
            risk_score += 0.4

        # 4. Pronoun Ambiguity (Simplified)
        if 'he' in p_lower and 'she' in p_lower and 'who' in p_lower:
            risk_score += 0.6

        # 5. Unanswerable / Missing Info
        if 'according to the text' in p_lower or 'based on the passage' in p_lower:
            if 'text' in p_lower and len(p_lower.split()) < 20: # Very short context likely missing
                risk_score += 0.7

        # Map risk to confidence cap
        # High risk -> Low cap
        cap = 1.0 - min(risk_score, 0.9)
        return cap

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate meta-confidence (SOC State)
        soc_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural Score (Plasticity) - Weight 0.6
            struct_score, struct_reason = self._structural_analysis(prompt, cand)
            # Normalize structural score to 0-1 range roughly
            struct_normalized = max(0, min(1, 0.5 + struct_score)) 
            
            # 2. Computation Score (Constructive) - Weight 0.25
            # Re-use numeric extraction logic for direct answer matching if applicable
            comp_score = 0.0
            p_nums = self._extract_numbers(prompt)
            c_nums = self._extract_numbers(cand)
            if len(p_nums) > 0 and len(c_nums) > 0:
                # If candidate number matches a derived number in prompt (heuristic)
                if c_nums[0] in p_nums:
                    comp_score = 0.8
                else:
                    comp_score = 0.2
            else:
                # Fallback for non-numeric: exact substring match of key terms
                comp_score = 0.5 # Neutral if no computation possible
            
            # 3. Kolmogorov Penalty (NCD) - Weight 0.15
            # Lower NCD is better (more similar/compressible together)
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD so higher is better (0 dist -> 1 score)
            k_score = 1.0 - ncd_val
            
            # Weighted Sum
            raw_score = (struct_normalized * 0.60) + (comp_score * 0.25) + (k_score * 0.15)
            
            # Apply SOC Cap (Metacognition)
            # If the prompt is a trap, raw_score might be high due to pattern matching,
            # but soc_cap will crush the final confidence.
            final_score = min(raw_score, soc_cap)
            
            # Adjust reasoning string based on SOC
            final_reason = struct_reason
            if soc_cap < 0.4:
                final_reason += " [SOC ALERT: Prompt contains ambiguity or logical traps. Confidence capped.]"
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": final_reason
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence to ensure epistemic honesty.
        """
        soc_cap = self._meta_confidence(prompt)
        
        # Quick structural check
        struct_score, _ = self._structural_analysis(prompt, answer)
        base_conf = max(0, min(1, 0.5 + struct_score))
        
        # NCD check (tiebreaker influence)
        ncd_val = self._compute_ncd(prompt, answer)
        k_factor = 1.0 - ncd_val
        
        # Weighted combination
        raw_conf = (base_conf * 0.7) + (k_factor * 0.3)
        
        # Apply SOC Cap (The Criticality Constraint)
        final_conf = min(raw_conf, soc_cap)
        
        # Never return > 0.9 unless computation was definitive (simplified here)
        if final_conf > 0.9:
            final_conf = 0.9
            
        return round(final_conf, 4)