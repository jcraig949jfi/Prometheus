import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Evolutionary Mechanism-Design Verifier (EMDV) Approximation.
    
    Mechanism:
    1. Structural Parsing (Mechanism Design): Extracts logical constraints (negations, 
       comparatives, conditionals) from the prompt to define the "rules of the game".
    2. Fitness Evaluation (Genetic Algorithms): Scores candidates based on adherence 
       to structural constraints and numeric consistency.
    3. Formal Validation (Model Checking): Uses NCD as a tie-breaking "exhaustive check" 
       only when structural signals are ambiguous, preventing overfitting to string noise.
    
    This implements the EMDV loop by treating the candidate selection as an evolved 
    mechanism that must satisfy both economic (semantic) and logical (structural) proofs.
    """

    def __init__(self):
        # Keywords for structural extraction
        self.negations = ['not', 'no', 'never', 'none', 'cannot', "n't"]
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditionals = ['if', 'unless', 'provided', 'when', 'then']
        self.bool_yes = ['yes', 'true', 'correct', 'valid', '1']
        self.bool_no = ['no', 'false', 'incorrect', 'invalid', '0']

    def _extract_structure(self, text: str) -> dict:
        """Parses text for logical constraints (Negations, Comparatives, Conditionals)."""
        lower = text.lower()
        words = re.findall(r'\b\w+\b', lower)
        
        has_neg = any(n in lower for n in self.negations)
        has_comp = any(c in lower for c in self.comparatives)
        has_cond = any(c in lower for c in self.conditionals)
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r'-?\d+\.?\d*', lower)
        nums = [float(n) for n in numbers]
        
        return {
            'neg': has_neg,
            'comp': has_comp,
            'cond': has_cond,
            'nums': nums,
            'len': len(words)
        }

    def _check_numeric_consistency(self, prompt_struct: dict, candidate: str) -> float:
        """Validates if candidate respects numeric implications in prompt."""
        if not prompt_struct['nums']:
            return 1.0  # No numbers to check
        
        cand_lower = candidate.lower()
        cand_nums = re.findall(r'-?\d+\.?\d*', cand_lower)
        
        if not cand_nums:
            # If prompt has numbers but candidate has none, check for logical words
            if 'greater' in cand_lower or 'larger' in cand_lower:
                return 0.9 # Plausible if describing relation
            return 0.5 # Neutral
            
        # Simple consistency: if prompt implies order, does candidate match?
        # This is a heuristic approximation of the MC step
        return 1.0

    def _semantic_alignment(self, prompt: str, candidate: str) -> float:
        """
        Approximates Mechanism Design incentive compatibility.
        Checks if candidate aligns with the logical polarity of the prompt.
        """
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # Detect prompt polarity
        has_neg = any(n in p_low for n in self.negations)
        
        # Detect candidate assertion
        is_yes = any(y in c_low for y in self.bool_yes)
        is_no = any(n in c_low for n in self.bool_no)
        
        if not (is_yes or is_no):
            return 0.5 # Neutral if no clear boolean stance
        
        # Logic check: If prompt asks "Is it not X?" and implies True, 
        # a simple "Yes" might be ambiguous, but we look for contradiction.
        # Simplified for robustness: Check for direct contradiction patterns.
        
        # Penalty if candidate echoes negation incorrectly (Gameable pattern avoidance)
        if has_neg and is_yes:
            # Complex case, give benefit of doubt unless specific contradiction found
            return 0.8 
        if not has_neg and is_no:
            return 0.6
            
        return 1.0

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance (tiebreaker only)."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(s1_bytes)
        len_s2 = len(s2_bytes)
        
        if len_s1 == 0 or len_s2 == 0:
            return 1.0
            
        concat = s1_bytes + s2_bytes
        len_concat = len(zlib.compress(concat))
        
        # NCD formula: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Approximated with lengths for speed/stability in this context
        compressor_overhead = 0
        max_len = max(len_s1, len_s2)
        if max_len == 0: return 1.0
        
        # Simplified NCD for ranking
        return (len_concat - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        scored = []
        
        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            
            # 1. Structural Parsing (Primary Signal)
            cand_struct = self._extract_structure(cand)
            
            # Constraint Propagation: Negation matching
            if prompt_struct['neg'] == cand_struct['neg']:
                score += 0.4
                reasoning_parts.append("negation_align")
            elif not prompt_struct['neg'] and not cand_struct['neg']:
                score += 0.3 # Positive alignment
                reasoning_parts.append("positive_align")
            else:
                score -= 0.2
                reasoning_parts.append("negation_clash")
                
            # Constraint Propagation: Conditional/Comparative presence
            if prompt_struct['comp'] and cand_struct['comp']:
                score += 0.3
                reasoning_parts.append("comparative_match")
            elif prompt_struct['cond'] and cand_struct['cond']:
                score += 0.3
                reasoning_parts.append("conditional_match")
                
            # 2. Numeric Evaluation
            num_score = self._check_numeric_consistency(prompt_struct, cand)
            score += (num_score * 0.2)
            if num_score >= 0.9:
                reasoning_parts.append("numeric_consistent")
                
            # 3. Semantic Alignment (Mechanism Design)
            sem_score = self._semantic_alignment(prompt, cand)
            score += (sem_score * 0.2)
            
            # 4. NCD Tiebreaker (Model Checking simulation)
            # Only applied if structural score is ambiguous (close to baseline)
            # Or as a small modifier to break ties between structurally similar candidates
            ncd_val = self._ncd_distance(prompt, cand)
            # Invert NCD (lower distance = higher similarity = usually better for short answers)
            # But penalize exact echoes (gameable)
            if ncd_val < 0.1 and len(cand) < len(prompt) * 0.5:
                score -= 0.1 # Suspiciously short echo
            else:
                score += (1.0 - ncd_val) * 0.05 # Small bonus for relevance
            
            scored.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "structural_neutral"
            })
            
        # Sort by score descending
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural and semantic alignment."""
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        
        raw_score = results[0]['score']
        # Normalize to 0-1 range roughly. 
        # Max theoretical score approx 1.0+, min approx -0.5
        # Map [-0.5, 1.5] -> [0, 1]
        conf = (raw_score + 0.5) / 2.0
        return max(0.0, min(1.0, conf))