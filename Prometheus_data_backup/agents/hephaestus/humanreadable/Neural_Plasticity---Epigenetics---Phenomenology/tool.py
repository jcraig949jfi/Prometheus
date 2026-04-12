import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A hybrid reasoning tool implementing a 'Meta-Plastic Epigenetic Self-Model'.
    
    Mechanism:
    1. Structural Parsing (Neural Plasticity Backbone): Extracts logical operators 
       (negations, comparatives, conditionals) and numeric values. This forms the 
       primary 'sensory-motor' stream for immediate logical validation.
    2. Epigenetic Gating (Confidence Wrapper): A slow-timescale modifier that 
       suppresses scores for candidates exhibiting 'confirmation bias' patterns 
       (e.g., ignoring negations) or lacking structural alignment with the prompt.
       It acts as a learning-rate gate: if structural mismatch is high, plasticity 
       (score adjustment) is suppressed or inverted.
    3. Phenomenological Consistency (Introspective Module): Generates an internal 
       'report' of certainty based on the coherence between the prompt's constraints 
       and the candidate's structure. A variational-like loss is simulated by checking 
       if the candidate's 'feeling' (semantic density/logic) matches the expected 
       signature of a correct answer (e.g., precise numbers for math, specific 
       logical connectors for deduction).
       
    This implementation prioritizes structural parsing and numeric evaluation as 
    the primary scoring signal, using NCD only as a tiebreaker, adhering to the 
    'Goodhart Warning' constraints.
    """

    def __init__(self):
        # Epigenetic state: running average of recent activity (simulated per call)
        self._activity_trace = 0.0
        
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers for numeric evaluation."""
        pattern = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
        try:
            return [float(x) for x in re.findall(pattern, text)]
        except ValueError:
            return []

    def _parse_structure(self, text: str) -> Dict[str, any]:
        """Extract logical structures: negations, comparatives, conditionals."""
        lower_text = text.lower()
        return {
            'has_negation': bool(re.search(r'\b(not|no|never|neither|nor|without)\b', lower_text)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|larger|fewer|better|worse|than|>=|<=|>|<)\b', lower_text)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|provided|otherwise)\b', lower_text)),
            'word_count': len(text.split()),
            'numbers': self._extract_numbers(text)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance as a tiebreaker."""
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
        return (len_combined - min(len_s1, len_s2)) / max_len

    def _phenomenological_report(self, prompt_struct: Dict, cand_struct: Dict, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Simulates the introspective module generating a 'report' (r) and 
        comparing it to expected hypothesis signature.
        Returns (consistency_score, reason_string)
        """
        reasons = []
        score = 0.5 # Base prior
        
        # Check Numeric Consistency
        if prompt_struct['numbers'] and cand_struct['numbers']:
            # If both have numbers, check if the candidate numbers are logically derived
            # Simple heuristic: if prompt has 2 nums and candidate has 1, it might be a result
            p_count = len(prompt_struct['numbers'])
            c_count = len(cand_struct['numbers'])
            if p_count >= 2 and c_count == 1:
                score += 0.2
                reasons.append("Numeric derivation detected")
            elif p_count == c_count:
                # Check for direct copy (lazy) vs transformation
                if prompt_struct['numbers'] == cand_struct['numbers']:
                    score -= 0.1
                    reasons.append("Numbers merely copied")
                else:
                    score += 0.1
                    reasons.append("Numeric transformation detected")
        
        # Check Logical Consistency (Negation gating)
        if prompt_struct['has_negation'] and not cand_struct['has_negation']:
            # Candidate might be missing the negation constraint
            # Unless the answer is explicitly "No" or similar
            if not re.search(r'\b(no|false|incorrect|disagree)\b', candidate.lower()):
                score -= 0.3
                reasons.append("Missing negation constraint")
            else:
                score += 0.2
                reasons.append("Negation properly addressed")
        
        # Check Comparative/Conditional alignment
        if prompt_struct['has_comparative'] and not cand_struct['has_comparative']:
            # If prompt asks for comparison, answer should ideally reflect it
            if len(cand_struct['numbers']) == 0: 
                score -= 0.1
                reasons.append("Comparative context ignored")
        
        if prompt_struct['has_conditional']:
            if re.search(r'\b(therefore|thus|hence|so|because)\b', candidate.lower()):
                score += 0.15
                reasons.append("Logical connector present")

        return score, "; ".join(reasons) if reasons else "Structural baseline"

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Uses structural parsing and phenomenological consistency.
        """
        p_struct = self._parse_structure(prompt)
        a_struct = self._parse_structure(answer)
        
        # Phenomenological consistency check
        phen_score, _ = self._phenomenological_report(p_struct, a_struct, prompt, answer)
        
        # Epigenetic gating: 
        # If the prompt has strong logical constraints (negation/conditional) 
        # but the answer is too short or lacks structure, gate down confidence.
        gate = 1.0
        if (p_struct['has_negation'] or p_struct['has_conditional']) and a_struct['word_count'] < 3:
            gate = 0.4 # Suppress confidence for overly simple answers to complex logic
        
        base_conf = max(0.0, min(1.0, phen_score))
        final_conf = base_conf * gate
        
        # Normalize to 0-1 range strictly
        return round(final_conf, 4)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates based on structural parsing and phenomenological fit.
        Returns ranked list.
        """
        p_struct = self._parse_structure(prompt)
        scored_candidates = []
        
        for cand in candidates:
            c_struct = self._parse_structure(cand)
            
            # 1. Structural Parsing Score (Primary Signal)
            struct_score = 0.0
            
            # Numeric Evaluation
            if p_struct['numbers'] and c_struct['numbers']:
                # Heuristic: If prompt implies math, reward candidates with calculated-looking numbers
                # Simple check: if candidate number is different from prompt numbers (result vs input)
                if len(p_struct['numbers']) >= 2 and len(c_struct['numbers']) == 1:
                    struct_score += 0.4
                elif len(p_struct['numbers']) == len(c_struct['numbers']):
                    # Check if values changed (transformation)
                    if p_struct['numbers'] != c_struct['numbers']:
                        struct_score += 0.2
                    else:
                        struct_score -= 0.1 # Penalty for just repeating numbers
            
            # Constraint Propagation (Negation)
            if p_struct['has_negation']:
                if c_struct['has_negation'] or re.search(r'\b(no|never|false|not)\b', cand.lower()):
                    struct_score += 0.3
                else:
                    struct_score -= 0.4 # Heavy penalty for ignoring negation
            
            # Conditional Logic
            if p_struct['has_conditional']:
                if re.search(r'\b(if|then|therefore|thus|because)\b', cand.lower()):
                    struct_score += 0.2

            # 2. Phenomenological Consistency (Introspective Report)
            phen_score, reason_str = self._phenomenological_report(p_struct, c_struct, prompt, cand)
            
            # 3. Epigenetic Gating (Meta-plasticity)
            # Adjust learning rate (score weight) based on 'heritable' trace of complexity
            # If prompt is complex (high word count + logic), simple answers get gated down
            complexity_gate = 1.0
            if p_struct['word_count'] > 20 and c_struct['word_count'] < 5:
                complexity_gate = 0.5
            
            # Combine scores
            # Structural parsing is the driver (per instructions)
            raw_score = (struct_score * 0.6) + (phen_score * 0.4)
            final_score = raw_score * complexity_gate
            
            # 4. NCD Tiebreaker (Only if structural signals are weak/equal)
            # We add a tiny epsilon based on NCD to break ties without dominating
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD (lower distance = higher score) and scale down significantly
            ncd_bonus = (1.0 - ncd_val) * 0.01 
            
            total_score = final_score + ncd_bonus
            
            scored_candidates.append({
                "candidate": cand,
                "score": round(total_score, 4),
                "reasoning": f"Structural:{struct_score:.2f}; Phenomenological:{phen_score:.2f}; Gate:{complexity_gate:.2f} ({reason_str})"
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates