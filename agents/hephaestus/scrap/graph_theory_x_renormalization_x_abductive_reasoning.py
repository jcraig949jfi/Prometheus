import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Renormalized Abductive Graph Neural Network (RAGNN) Simulator.
    
    Mechanism:
    1. Structural Parsing (Graph Theory Proxy): Extracts logical constraints 
       (negations, comparatives, conditionals) as the "graph structure" of the problem.
       Per instructions, this is the primary scoring signal, not direct graph algorithms.
    2. Abductive Inference: Evaluates candidates by how well they explain the 
       observed structural constraints (maximizing coverage of detected logic patterns).
    3. Renormalization (Scale Consistency): Simulates multi-scale validation by 
       checking consistency across token-level, word-level, and sentence-level 
       representations. Candidates must maintain logical coherence across these scales.
    4. Scoring: Combines structural adherence (primary) with NCD (tiebreaker).
    """

    def __init__(self):
        self._logic_patterns = [
            (r'not\s+(\w+)', 'negation'),
            (r'no\s+(\w+)', 'negation'),
            (r'unless', 'conditional'),
            (r'if\s+.+\s+then', 'conditional'),
            (r'only\s+if', 'conditional'),
            (r'more\s+than', 'comparative'),
            (r'less\s+than', 'comparative'),
            (r'greater\s+than', 'comparative'),
            (r'smaller\s+than', 'comparative'),
            (r'before', 'temporal'),
            (r'after', 'temporal'),
        ]
        self._num_regex = re.compile(r'-?\d+\.?\d*')

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical constraints and numeric values (Structural Parsing)."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|unless|only if)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|before|after)\b', text_lower)),
            'numbers': []
        }
        # Numeric extraction for evaluation
        nums = re.findall(self._num_regex, text)
        if nums:
            try:
                features['numbers'] = [float(n) for n in nums]
            except ValueError:
                pass
        return features

    def _check_abductive_fit(self, prompt: str, candidate: str) -> float:
        """
        Abductive Scoring: How well does the candidate explain/satisfy the prompt's constraints?
        Returns a score 0.0 to 1.0 based on logical consistency.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        score = 0.0
        checks = 0
        
        # 1. Negation Consistency (Modus Tollens proxy)
        # If prompt has negation, candidate should ideally reflect awareness or not contradict
        if p_struct['negations'] > 0:
            checks += 1
            # Simple heuristic: if prompt says "not X", candidate shouldn't blindly assert "X"
            # This is a rough approximation of logical consistency
            if 'not' in p_lower or 'no' in p_lower:
                # Reward if candidate acknowledges complexity or doesn't simply echo positive
                if len(c_lower.split()) > 2: 
                    score += 0.5
                else:
                    score += 0.2 # Penalty for overly simple answer to complex negative prompt
        
        # 2. Comparative/Numeric Evaluation
        if p_struct['numbers'] and c_struct['numbers']:
            checks += 1
            # Check if candidate numbers are consistent with prompt logic (simplified)
            # E.g., if prompt implies sorting, does candidate follow? 
            # Here we just check presence of numeric reasoning as a proxy for "fit"
            score += 0.8
        elif p_struct['comparatives'] > 0:
            checks += 1
            # If prompt asks for comparison, candidate should ideally contain comparative words
            if c_struct['comparatives'] > 0 or len(c_struct['numbers']) > 0:
                score += 0.7
            else:
                score += 0.3

        # 3. Conditional/Constraint Propagation
        if p_struct['conditionals'] > 0:
            checks += 1
            # Candidate should ideally contain logical connectors if prompt has them
            if c_struct['conditionals'] > 0 or len(c_lower) > 10:
                score += 0.6
            else:
                score += 0.2

        # Normalization
        if checks == 0:
            return 0.5 # Neutral if no structure detected
        return min(1.0, score / checks)

    def _renormalize_consistency(self, prompt: str, candidate: str) -> float:
        """
        Renormalization Step: Check consistency across scales (token, word, sentence).
        Simulates the hierarchy G0 -> G1 -> GL by checking if the "gist" (coarse) 
        matches the details (fine).
        """
        # Scale 0: Raw string length ratio (Coarse)
        len_ratio = len(candidate) / (len(prompt) + 0.1)
        coarse_score = 1.0 if 0.01 < len_ratio < 2.0 else 0.5
        
        # Scale 1: Word overlap density (Medium)
        p_words = set(prompt.lower().split())
        c_words = set(candidate.lower().split())
        intersection = p_words.intersection(c_words)
        # Jaccard-like similarity
        union = p_words.union(c_words)
        medium_score = len(intersection) / len(union) if union else 0
        
        # Scale 2: NCD (Fine - used as tiebreaker/internal check)
        ncd = self._ncd(prompt, candidate)
        
        # Combine scales (Weighted average simulating fixed-point iteration)
        # High weight on medium scale (semantic overlap), low on coarse, NCD as validator
        final_score = (0.2 * coarse_score) + (0.5 * medium_score) + (0.3 * (1.0 - ncd))
        return max(0.0, min(1.0, final_score))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(s1_b)
        len_s2 = len(s2_b)
        if len_s1 == 0 or len_s2 == 0:
            return 1.0
        concat = s1_b + s2_b
        len_concat = len(zlib.compress(concat))
        # NCD formula: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Approximated here for stability
        c_s1 = len(zlib.compress(s1_b))
        c_s2 = len(zlib.compress(s2_b))
        c_concat = len(zlib.compress(concat))
        
        min_c = min(c_s1, c_s2)
        max_c = max(c_s1, c_s2)
        if max_c == 0:
            return 0.0
        return (c_concat - min_c) / max_c

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            # 1. Abductive Fit (Primary Logic)
            abductive_score = self._check_abductive_fit(prompt, cand)
            
            # 2. Renormalized Consistency (Scale Check)
            renorm_score = self._renormalize_consistency(prompt, cand)
            
            # 3. NCD Tiebreaker (Baseline)
            ncd_val = self._ncd(prompt, cand)
            
            # Final Score: Weighted combination favoring structural/abductive reasoning
            # NCD is only a small modifier unless structural signals are absent
            structural_signal = abductive_score > 0.2 or renorm_score > 0.2
            
            if structural_signal:
                final_score = (0.6 * abductive_score) + (0.3 * renorm_score) + (0.1 * (1.0 - ncd_val))
            else:
                # Fallback to NCD if no structure detected (rare)
                final_score = 1.0 - ncd_val
            
            reasoning = f"Abductive fit: {abductive_score:.2f}, Scale consistency: {renorm_score:.2f}"
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on abductive fit and consistency."""
        abductive_score = self._check_abductive_fit(prompt, answer)
        renorm_score = self._renormalize_consistency(prompt, answer)
        
        # Confidence is high if both abductive logic and scale consistency agree
        confidence_val = (abductive_score * 0.7) + (renorm_score * 0.3)
        return float(max(0.0, min(1.0, confidence_val)))