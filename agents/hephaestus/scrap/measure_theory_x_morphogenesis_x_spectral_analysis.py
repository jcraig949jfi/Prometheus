import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Measure-Valued Spectral-Morphogenetic Reasoning Tool (Computational Analogue).
    
    Mechanism:
    1. Measure Theory (Probability Mass): Candidates are treated as discrete measures.
       We compute a 'structural mass' based on the presence of logical operators 
       (negations, comparatives, conditionals) and numeric consistency.
    2. Morphogenesis (Structural Evolution): We simulate a 'reaction-diffusion' 
       process on the text structure. The 'drift' is the alignment with prompt constraints.
       The 'diffusion' is the penalty for length mismatch or missing logical branches.
       Candidates that fail to 'morph' into the logical shape required by the prompt 
       (e.g., answering 'Yes' to a numeric comparison) lose mass.
    3. Spectral Analysis (Residual Monitoring): We treat the character/word sequence 
       as a signal. We compute a simple spectral residual by comparing the frequency 
       distribution of tokens in the candidate against the prompt's expected logical 
       conclusion pattern. High frequency of 'contradiction tokens' (e.g., 'not' when 
       expected 'is') increases the residual energy, lowering the score.
    
    This implementation prioritizes structural parsing and numeric evaluation as 
    primary drivers (per causal analysis), using NCD only as a tie-breaking 'diffusion' term.
    """

    def __init__(self):
        # Logical operators for structural parsing
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'false', 'impossible'}
        self.comparatives = {'greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<', '>=', '<='}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided', 'when'}
        self affirmatives = {'yes', 'true', 'correct', 'indeed', 'certainly'}

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract integers and floats
        matches = re.findall(r'-?\d+(?:\.\d+)?', text)
        return [float(m) for m in matches]

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a score based on logical consistency and structural parsing.
        This is the 'Reaction' term in the PDE analogy.
        """
        score = 0.0
        p_tokens = self._tokenize(prompt)
        c_tokens = self._tokenize(candidate)
        c_set = set(c_tokens)
        
        # 1. Negation Consistency
        # If prompt implies negation, candidate should reflect it (simplified heuristic)
        has_neg_prompt = any(t in self.negations for t in p_tokens)
        has_neg_cand = any(t in self.negations for t in c_tokens)
        
        # Heuristic: If prompt asks "Is it not...", affirmative answer might need care.
        # Instead, we check for direct contradiction patterns.
        if has_neg_prompt and not has_neg_cand:
            # Potential trap, but not always wrong. Small penalty if prompt is strongly negative.
            if any(word in prompt.lower() for word in ['impossible', 'never']):
                if not any(word in candidate.lower() for word in ['no', 'not', 'false']):
                    score -= 0.2

        # 2. Numeric Evaluation (The strongest signal)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if len(p_nums) >= 2:
            # Check if candidate contains a number that matches the logic of p_nums
            # Example: "Which is larger, 5 or 3?" -> Candidate should ideally contain "5" or "larger"
            max_p = max(p_nums)
            min_p = min(p_nums)
            
            # Detect comparison direction in prompt
            is_larger_query = any(t in self.comparatives and ('larger' in t or 'greater' in t or 'more' in t or '>' in t) for t in p_tokens)
            is_smaller_query = any(t in self.comparatives and ('smaller' in t or 'less' in t or 'fewer' in t or '<' in t) for t in p_tokens)
            
            if c_nums:
                c_val = c_nums[0]
                if is_larger_query:
                    if math.isclose(c_val, max_p, rel_tol=1e-5):
                        score += 1.0
                    elif math.isclose(c_val, min_p, rel_tol=1e-5):
                        score -= 1.0
                elif is_smaller_query:
                    if math.isclose(c_val, min_p, rel_tol=1e-5):
                        score += 1.0
                    elif math.isclose(c_val, max_p, rel_tol=1e-5):
                        score -= 1.0
                else:
                    # Generic numeric presence bonus if logic isn't clear
                    if any(math.isclose(c_val, n, rel_tol=1e-5) for n in p_nums):
                        score += 0.5

        # 3. Conditional/Constraint Propagation
        # If prompt has "if", check candidate for logical consequence markers or direct answer
        if any(t in self.conditionals for t in p_tokens):
            # Simple check: did the candidate ignore the condition? 
            # Hard to verify without NLP, so we rely on length and keyword overlap as proxy
            if len(c_tokens) < 3 and len(p_tokens) > 10:
                score -= 0.3 # Too short for a conditional answer

        # 4. Affirmative/Negative Alignment
        # If prompt asks a Yes/No question (contains '?')
        if '?' in prompt:
            is_yes_no = any(t in self.affirmatives or t in self.negations for t in p_tokens)
            if is_yes_no or any(t in ['is', 'are', 'do', 'does', 'can'] for t in p_tokens):
                # Check candidate for clear yes/no
                has_yes = any(t in self.affirmatives for t in c_set)
                has_no = any(t in self.negations for t in c_set)
                
                # Crude heuristic: if candidate has numbers, it's not a simple yes/no
                if not c_nums:
                    if has_yes: score += 0.2
                    if has_no: score += 0.2
        
        return score

    def _spectral_residual(self, prompt: str, candidate: str) -> float:
        """
        Simulates spectral analysis by comparing token frequency distributions.
        High divergence indicates 'model misspecification' (wrong answer type).
        Returns a penalty (lower is better).
        """
        p_tokens = self._tokenize(prompt)
        c_tokens = self._tokenize(candidate)
        
        if not p_tokens or not c_tokens:
            return 0.0

        # Build frequency maps (Spectral density analogue)
        def get_freq_dist(tokens):
            freq = {}
            for t in tokens:
                freq[t] = freq.get(t, 0) + 1
            return freq

        p_freq = get_freq_dist(p_tokens)
        c_freq = get_freq_dist(c_tokens)
        
        # Calculate overlap (Inverse of residual)
        # We look for key logical words in candidate that appear in prompt
        overlap_score = 0.0
        total_weight = 0.0
        
        # Weight logical keywords higher
        for word, count in c_freq.items():
            if word in p_freq:
                weight = 1.0
                if word in self.negations or word in self.comparatives or word in self.conditionals:
                    weight = 3.0
                overlap_score += min(count, p_freq[word]) * weight
                total_weight += weight
            else:
                # Penalty for unknown words (noise) - small
                overlap_score -= 0.1 * count
        
        if total_weight == 0:
            return -0.5 # No overlap is bad
            
        return overlap_score / (len(c_tokens) + 1) # Normalize slightly

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        concat = s1_bytes + s2_bytes
        
        c_s1 = len(zlib.compress(s1_bytes))
        c_s2 = len(zlib.compress(s2_bytes))
        c_concat = len(zlib.compress(concat))
        
        max_len = max(c_s1, c_s2)
        if max_len == 0:
            return 0.0
        return (c_concat - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        for cand in candidates:
            # 1. Structural Parsing (Primary Signal)
            struct_score = self._structural_score(prompt, cand)
            
            # 2. Spectral Residual (Secondary Signal / Sanity Check)
            spectral_score = self._spectral_residual(prompt, cand)
            
            # 3. NCD (Tiebreaker / Diffusion Term)
            # We want candidates that are compressible with the prompt (high similarity)
            # But NCD is 0 for identical, 1 for different. We invert logic: lower NCD is better.
            ncd_val = self._ncd_distance(prompt, cand)
            ncd_bonus = (1.0 - ncd_val) * 0.1 # Small bonus for similarity
            
            # Total Score = Structural + Spectral + NCD_bonus
            # Structural is dominant (-2 to +2 range roughly)
            total_score = struct_score + (spectral_score * 0.5) + ncd_bonus
            
            results.append({
                "candidate": cand,
                "score": total_score,
                "reasoning": f"Structural: {struct_score:.2f}, Spectral: {spectral_score:.2f}, NCD: {ncd_val:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the internal scoring mechanism normalized to [0, 1].
        """
        # Evaluate single candidate against itself conceptually
        # We simulate a 'null' candidate to get a baseline? 
        # Instead, we use the absolute magnitude of the structural score.
        
        struct = self._structural_score(prompt, answer)
        spectral = self._spectral_residual(prompt, answer)
        
        # Raw score can be negative. Map to 0-1.
        # Assume range [-2, 2] covers most cases.
        raw_score = struct + (spectral * 0.5)
        
        # Sigmoid-like mapping
        # If score > 1.0 -> ~0.9
        # If score < -1.0 -> ~0.1
        confidence = 1.0 / (1.0 + math.exp(-raw_score))
        
        # Clamp
        return max(0.0, min(1.0, confidence))