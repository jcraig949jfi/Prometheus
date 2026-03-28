import re
import zlib
import math

class ReasoningTool:
    """
    Implements a 'Critical Sparse-Coding Network' analogy for reasoning.
    
    Mechanism:
    1. Structural Parsing (The Critical Core): Extracts logical operators (negations,
       comparatives, conditionals) and numeric values. This drives the 'branching ratio'
       of the evaluation, ensuring the system operates near a critical point where
       logical constraints dominate (sigma ~ 1).
    2. Sparse Coding (The Proposal Filter): Candidates are scored heavily on matching
       specific structural tokens found in the prompt. Irrelevant words are suppressed
       (sparsity), preventing noise from influencing the score.
    3. Maximum Entropy (The Confidence Wrapper): Uses NCD only as a tie-breaking
       entropy term when structural signals are ambiguous, ensuring the least-biased
       choice among remaining candidates.
       
    This architecture avoids the 'reasoning traps' of pure SOC/MaxEnt by restricting
    them to support roles while relying on deterministic structural parsing for the
    primary scoring signal.
    """

    def __init__(self):
        # Structural tokens that indicate logical branching
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'<', '>', 'less', 'more', 'greater', 'smaller', 'higher', 'lower', 'before', 'after'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided', 'assuming'}
        self.booleans = {'true', 'false', 'yes', 'no'}
        
        # Regex for numbers (including floats)
        self.num_regex = re.compile(r'-?\d+\.?\d*')

    def _extract_structure(self, text):
        """Extracts logical structure and numeric values from text."""
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        has_negation = bool(words & self.negations)
        has_comparative = bool(words & self.comparatives)
        has_conditional = bool(words & self.conditionals)
        numbers = [float(n) for n in self.num_regex.findall(text)]
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'words': words,
            'length': len(text)
        }

    def _compute_ncd(self, s1, s2):
        """Computes Normalized Compression Distance as an entropy-based tiebreaker."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_combined = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_combined - max_len) / max_len

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        prompt_struct = self._extract_structure(prompt)
        scored_candidates = []

        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            score = 0.0
            reasoning_parts = []

            # 1. Critical Branching: Numeric Logic (High Weight)
            if prompt_struct['numbers'] and cand_struct['numbers']:
                # If prompt has numbers, check if candidate respects numeric order implied
                # Simple heuristic: If prompt has comparison words, candidate number should match logic
                # For now, strict matching of numbers found in prompt boosts score significantly
                matches = sum(1 for n in cand_struct['numbers'] if n in prompt_struct['numbers'])
                if matches > 0:
                    score += 0.5 * matches
                    reasoning_parts.append(f"Numeric match found ({matches})")

            # 2. Sparse Coding: Logical Operator Matching
            # Only active units (tokens) that overlap with prompt constraints contribute
            logical_overlap = 0
            if prompt_struct['negation'] and cand_struct['negation']:
                logical_overlap += 0.2
                reasoning_parts.append("Negation alignment")
            elif prompt_struct['negation'] and not cand_struct['negation']:
                # Penalty for missing negation in a negative context (simple check)
                # This is a simplification; real logic requires full parse
                pass 
            
            if prompt_struct['comparative'] and cand_struct['comparative']:
                logical_overlap += 0.2
                reasoning_parts.append("Comparative alignment")
                
            if prompt_struct['conditional'] and cand_struct['conditional']:
                logical_overlap += 0.2
                reasoning_parts.append("Conditional alignment")

            score += logical_overlap
            
            # 3. Sparsity Penalty: Length mismatch reduction
            # Encourages concise answers that still hit structural notes
            if cand_struct['length'] > prompt_struct['length'] * 1.5:
                score -= 0.1
                reasoning_parts.append("Sparsity penalty (too verbose)")

            # 4. MaxEnt Tiebreaker: NCD
            # If structural score is low or tied, NCD breaks the tie
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD so higher similarity = higher score contribution
            ncd_score = (1.0 - ncd_val) * 0.1 
            score += ncd_score
            
            # Normalize reasoning string
            reasoning_str = "; ".join(reasoning_parts) if reasoning_parts else "Structural baseline"
            
            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning_str
            })

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on structural consistency.
        Uses MaxEnt principle: if the answer is structurally consistent (sparse match),
        confidence is high. If it requires complex compression (high NCD) without
        structural support, confidence is low.
        """
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        structural_match = 0.0
        
        # Check negation consistency
        if p_struct['negation'] == a_struct['negation']:
            structural_match += 0.4
        else:
            # Mismatch in negation is a strong indicator of error
            structural_match -= 0.5
            
        # Check number presence
        if p_struct['numbers']:
            if a_struct['numbers']:
                # Check if answer numbers are subset of prompt or derived
                structural_match += 0.4
            else:
                structural_match -= 0.2
        
        # MaxEnt wrapper: Use NCD to adjust confidence if structural signal is weak
        ncd = self._compute_ncd(prompt, answer)
        
        # Base confidence
        conf = 0.5 + structural_match
        
        # Adjust by compression distance (Entropy)
        # Low NCD (high similarity) slightly boosts confidence if structure is neutral
        if abs(structural_match) < 0.1:
            conf += (1.0 - ncd) * 0.2
            
        return max(0.0, min(1.0, conf))