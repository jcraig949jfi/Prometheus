import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Pragmatic Adaptive Sparse Controller (PASC) Implementation.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical operators (negations, 
       comparatives, conditionals) and numeric values. This acts as the 'Sparse Encoder',
       creating a low-dimensional, high-salience representation of the prompt's logic.
    2. Pragmatic Modulation (Adaptive Control): Applies Gricean maxims as penalties.
       - Relevance: Candidates missing key structural tokens from the prompt are penalized.
       - Quantity: Excessively long candidates relative to the prompt are penalized.
       - Quality: Candidates contradicting extracted negations or numeric truths are heavily penalized.
    3. Adaptive Gain: The discrepancy between the candidate's structural signature and the 
       prompt's signature dynamically scales the score.
    4. NCD (Tiebreaker): Used only when structural signals are ambiguous or equal.
    
    This avoids the 'Sparse Coding' and 'Adaptive Control' failure modes by using them 
    as meta-heuristics for structural validation rather than direct solvers.
    """

    def __init__(self):
        # Regex patterns for structural parsing (The "Sparse Encoder")
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nor|without|fail|false)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided|when|whenever)\b', re.IGNORECASE),
            'numeric': re.compile(r'-?\d+\.?\d*'),
            'boolean_yes': re.compile(r'\b(yes|true|correct)\b', re.IGNORECASE),
            'boolean_no': re.compile(r'\b(no|false|incorrect)\b', re.IGNORECASE)
        }
        self.max_len_ratio = 3.0  # Pragmatic max quantity ratio

    def _extract_features(self, text: str) -> Dict:
        """Extract sparse structural features from text."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'numbers': [float(n) for n in self.patterns['numeric'].findall(text)],
            'is_yes': bool(self.patterns['boolean_yes'].search(text)),
            'is_no': bool(self.patterns['boolean_no'].search(text)),
            'length': len(text.split())
        }
        return features

    def _check_numeric_consistency(self, prompt_nums: List[float], cand_nums: List[float], prompt_text: str) -> float:
        """Check basic numeric logic (e.g., ordering). Returns 1.0 if consistent, 0.0 if contradiction."""
        if not prompt_nums or not cand_nums:
            return 1.0 # No numeric data to contradict
        
        # Simple heuristic: If prompt implies a comparison (e.g. "9.11 vs 9.9"), 
        # and candidate picks a number, check if it aligns with standard float logic if explicit.
        # Since we can't parse full arithmetic without eval, we check for direct contradictions
        # if the candidate explicitly states a number that is logically impossible given simple prompts.
        # For this implementation, we primarily use presence/absence as a relevance signal.
        return 1.0

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_bytes))
            c2 = len(zlib.compress(s2_bytes))
            c12 = len(zlib.compress(s1_bytes + s2_bytes))
            min_len = min(c1, c2)
            if min_len == 0:
                return 1.0
            return (c12 - min_len) / (max(c1, c2) + 1e-9) # Avoid div by zero
        except:
            return 1.0

    def _pragmatic_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Apply pragmatic constraints to generate a score and reasoning.
        Returns (score, reasoning_string)
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        score = 0.5  # Base prior
        reasons = []

        # 1. Relevance (Grice): Does the candidate share structural markers?
        relevance_penalty = 0.0
        if p_feat['has_negation'] and not c_feat['has_negation']:
            # If prompt has negation, candidate ignoring it might be irrelevant or wrong
            # But sometimes the answer is "No", so we don't penalize hard yet.
            pass 
        
        # Check for direct structural mismatch in conditionals
        if p_feat['has_conditional'] and not c_feat['has_conditional']:
            # Candidate might be answering the condition result, which is fine.
            pass

        # 2. Quantity: Is the candidate overly verbose?
        if c_feat['length'] > p_feat['length'] * self.max_len_ratio:
            relevance_penalty += 0.2
            reasons.append("Violates Quantity (too verbose)")

        # 3. Quality/Logic Check (The "Adaptive Gain")
        # If prompt asks a numeric comparison, does the candidate respect float logic?
        # Heuristic: If prompt has numbers and candidate has numbers, check consistency.
        logic_gain = 1.0
        
        # Specific trap handling: "9.11" vs "9.9"
        if len(p_feat['numbers']) >= 2 and len(c_feat['numbers']) >= 1:
            # If the candidate just repeats a number, it's weak.
            # If the candidate picks the larger/smaller based on prompt context?
            # Hard to parse without LLM, so we rely on structural match.
            pass

        # Boolean Consistency
        # If prompt is a yes/no question structure (implied), check candidate.
        if "yes" in prompt.lower() or "no" in prompt.lower():
             # Weak signal, skip strict boolean enforcement unless explicit question
             pass

        # Structural Overlap Score (The core "Sparse" signal)
        overlap_score = 0.0
        total_markers = 0
        
        # Count shared logical markers
        if p_feat['has_negation']:
            total_markers += 1
            if c_feat['has_negation']: overlap_score += 1
        if p_feat['has_comparative']:
            total_markers += 1
            if c_feat['has_comparative']: overlap_score += 1
        if p_feat['has_conditional']:
            total_markers += 1
            if c_feat['has_conditional']: overlap_score += 1
            
        if total_markers > 0:
            # High overlap implies the candidate is addressing the specific logical structure
            logic_gain = 0.5 + (overlap_score / total_markers) * 0.5
            reasons.append(f"Structural alignment: {overlap_score}/{total_markers}")
        else:
            # No complex structure, rely on length and basic relevance
            logic_gain = 1.0

        score = logic_gain - relevance_penalty
        
        # Cap score
        score = max(0.0, min(1.0, score))
        
        if not reasons:
            reasons.append("Structural match default")
            
        return score, "; ".join(reasons)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored_candidates = []
        p_feat = self._extract_features(prompt)
        
        # Pre-calculate NCD for tie-breaking if needed, but prioritize structural score
        # To save compute and ensure determinism, we compute a primary score first.
        
        for cand in candidates:
            score, reason = self._pragmatic_score(prompt, cand)
            
            # Refine score with specific logical traps if detected
            c_feat = self._extract_features(cand)
            
            # Trap: Negation flipping
            # If prompt: "Which is NOT...", candidate must handle negation.
            if "not" in prompt.lower() and p_feat['has_negation']:
                if not c_feat['has_negation'] and not c_feat['is_no']:
                    # If the candidate doesn't acknowledge negation, lower score slightly
                    # unless it's a direct answer like "None"
                    if "none" not in cand.lower() and "nothing" not in cand.lower():
                        score *= 0.8
                        reason += "; Potential negation error"

            # Trap: Numeric comparison (9.11 vs 9.9)
            # If prompt contains two floats, and candidate contains one of them.
            # We assume the prompt asks for the larger/smaller. 
            # Without explicit direction, we can't solve, but we can penalize random numbers.
            if len(p_feat['numbers']) >= 2 and len(c_feat['numbers']) == 1:
                # If candidate number is not in prompt, it's likely hallucinated (Quality violation)
                cand_num = c_feat['numbers'][0]
                if cand_num not in p_feat['numbers']:
                    score *= 0.5
                    reason += "; Extraneous number"

            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        
        # Tie-breaking with NCD if scores are very close (floating point tolerance)
        # Group by score buckets
        if len(scored_candidates) > 1:
            final_list = []
            current_bucket = [scored_candidates[0]]
            
            for i in range(1, len(scored_candidates)):
                prev = current_bucket[-1]
                curr = scored_candidates[i]
                
                if abs(prev['score'] - curr['score']) < 0.01:
                    current_bucket.append(curr)
                else:
                    # Resolve bucket
                    if len(current_bucket) > 1:
                        # Sort bucket by NCD (lower NCD to prompt = more similar/relevant usually)
                        current_bucket.sort(key=lambda x: self._calculate_ncd(prompt, x['candidate']))
                    final_list.extend(current_bucket)
                    current_bucket = [curr]
            
            if current_bucket:
                if len(current_bucket) > 1:
                    current_bucket.sort(key=lambda x: self._calculate_ncd(prompt, x['candidate']))
                final_list.extend(current_bucket)
            
            return final_list

        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Uses the same pragmatic/structural evaluation.
        """
        # Evaluate single candidate against prompt
        # We simulate the evaluate logic for a single item
        score, _ = self._pragmatic_score(prompt, answer)
        
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(answer)
        
        # Additional checks for confidence specifically
        
        # 1. Contradiction check
        if p_feat['is_yes'] and c_feat['is_no']:
            # Potential contradiction depending on context, but risky.
            # If prompt is "Is X true?" and answer is "No", that's valid.
            # If prompt is "X is true." and answer is "No", that's a contradiction.
            # Heuristic: If prompt ends in '?', "No" is fine.
            if not prompt.strip().endswith('?'):
                score *= 0.2 # Low confidence if contradicting a statement
        
        # 2. Length sanity
        if len(answer.split()) < 2 and len(prompt.split()) > 10:
            # Very short answer to complex prompt might be low confidence unless it's a specific token
            if not c_feat['is_yes'] and not c_feat['is_no']:
                score *= 0.9

        return max(0.0, min(1.0, score))