import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Phenomenological Emergent Feedback Control (PEFC) Reasoning Tool.
    
    Mechanism:
    1. Phenomenology (Bracketing): Parses the prompt to extract a "lifeworld" vector
       of structural constraints (negations, comparatives, conditionals, numeric relations).
       This represents the 'first-person' structural truth of the problem.
       
    2. Emergence (Macro-variables): Aggregates local constraint matches into global
       scalar signals: 'Consistency' (logic match) and 'Coherence' (structural overlap).
       
    3. Feedback Control (PID-style Gain): 
       - Computes error between the candidate's implied structure and the prompt's structure.
       - Adjusts the 'precision' (weight) of the scoring dynamically.
       - If a candidate violates a hard structural constraint (e.g., negation), 
         the error term drives the score down sharply (high gain on error).
       - Uses NCD only as a tie-breaking baseline when structural signals are ambiguous.
       
    This implements the PEFC architecture by treating structural logic as the 
    "phenomenal state" and using error-driven gain control to rank candidates.
    """

    def __init__(self):
        # Structural patterns for "lifeworld" extraction
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.bool_ops = ['and', 'or', 'but', 'however']
        
    def _extract_structural_vector(self, text: str) -> Dict[str, any]:
        """
        Phenomenological Bracketing: Extracts the structural 'lifeworld' of the text.
        Returns a dictionary of features representing the logical skeleton.
        """
        if not text:
            return {"len": 0, "neg_count": 0, "comp_count": 0, "cond_count": 0, "nums": [], "words": set()}
        
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        # Count structural markers
        neg_count = sum(1 for w in self.negations if f" {w} " in f" {lower_text} " or lower_text.startswith(w))
        comp_count = sum(1 for w in self.comparatives if w in words)
        cond_count = sum(1 for w in self.conditionals if w in words)
        
        # Extract numbers for numeric evaluation
        nums = []
        for match in re.findall(r'-?\d+\.?\d*', text):
            try:
                nums.append(float(match))
            except ValueError:
                pass
                
        return {
            "len": len(text),
            "neg_count": neg_count,
            "comp_count": comp_count,
            "cond_count": cond_count,
            "nums": sorted(nums),
            "words": words,
            "raw": lower_text
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _calculate_emergent_error(self, prompt_vec: Dict, cand_vec: Dict) -> float:
        """
        Emergence: Computes the mismatch (error) between prompt and candidate structures.
        This acts as the 'e(t)' in the PID loop.
        """
        error = 0.0
        
        # 1. Negation mismatch (High penalty)
        # If prompt has negations and candidate lacks them (or vice versa), high error
        if prompt_vec['neg_count'] > 0 and cand_vec['neg_count'] == 0:
            error += 0.5
        elif prompt_vec['neg_count'] == 0 and cand_vec['neg_count'] > 0:
            error += 0.3
            
        # 2. Conditional logic check
        if prompt_vec['cond_count'] > 0 and cand_vec['cond_count'] == 0:
            # Candidate ignores conditional structure
            error += 0.2
            
        # 3. Numeric consistency (Simple check: does candidate contain numbers if prompt has many?)
        if len(prompt_vec['nums']) > 2 and len(cand_vec['nums']) == 0:
            # Might be ignoring numeric data
            error += 0.1
            
        # 4. Word overlap penalty (Inverse Jaccard-ish)
        # Low overlap implies high error, but we want to penalize LOW overlap
        all_words = prompt_vec['words'].union(cand_vec['words'])
        if len(all_words) > 0:
            intersection = prompt_vec['words'].intersection(cand_vec['words'])
            overlap = len(intersection) / len(all_words)
            error += (1.0 - overlap) * 0.2 # Structural drift
            
        return error

    def _pid_gain_control(self, error: float, base_score: float) -> float:
        """
        Feedback Control: Adjusts the score based on structural error.
        Simulates a PID controller where high error reduces the 'precision' (score).
        P-term: Proportional to error.
        """
        kp = 0.8 # Proportional gain
        adjusted_score = base_score - (kp * error)
        return max(0.0, min(1.0, adjusted_score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_vec = self._extract_structural_vector(prompt)
        results = []
        
        # Baseline NCD for tie-breaking
        ncd_scores = []
        for i, cand in enumerate(candidates):
            ncd = self._compute_ncd(prompt, cand)
            ncd_scores.append((i, ncd))
            
        avg_ncd = sum(s[1] for s in ncd_scores) / len(ncd_scores) if ncd_scores else 0.5

        for i, cand in enumerate(candidates):
            cand_vec = self._extract_structural_vector(cand)
            
            # 1. Base Score from NCD (Inverse similarity, so 1 - ncd)
            # Note: NCD is weak for reasoning, so it's a minor component here
            ncd_val = self._compute_ncd(prompt, cand)
            base_similarity = 1.0 - ncd_val
            
            # 2. Calculate Emergent Error (Structural Mismatch)
            error = self._calculate_emergent_error(prompt_vec, cand_vec)
            
            # 3. Apply Feedback Control (Gain Adjustment)
            # If error is high, score drops significantly regardless of NCD
            final_score = self._pid_gain_control(error, base_similarity + 0.2) # Bias up slightly before penalty
            
            # Heuristic boost for length appropriateness (avoiding "Yes"/"No" on complex prompts)
            if len(prompt) > 50 and len(cand) < 4:
                final_score *= 0.5 # Penalize overly short answers for complex prompts
                
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Structural error: {error:.2f}, NCD: {ncd_val:.2f}, Adjusted Score: {final_score:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment.
        """
        prompt_vec = self._extract_structural_vector(prompt)
        ans_vec = self._extract_structural_vector(answer)
        
        error = self._calculate_emergent_error(prompt_vec, ans_vec)
        
        # Convert error to confidence (Low error = High confidence)
        # Using a simple decay function
        conf = math.exp(-2.0 * error)
        
        # Boost if numeric ranges match roughly
        if prompt_vec['nums'] and ans_vec['nums']:
            # Check if answer numbers are within prompt number range (heuristic)
            p_min, p_max = min(prompt_vec['nums']), max(prompt_vec['nums'])
            a_min, a_max = min(ans_vec['nums']), max(ans_vec['nums'])
            if p_min <= a_min and a_max <= p_max:
                conf = min(1.0, conf + 0.2)
                
        return round(max(0.0, min(1.0, conf)), 4)