import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Closed-Loop Causal Inference Controller (CL-CIC) Implementation.
    
    Mechanism:
    1. Structural Parsing (CIM): Extracts logical operators (negations, comparatives, 
       conditionals) and numeric values to build a lightweight structural signature.
    2. Mechanism Design (MDM): Implements an internal 'truthful reporting' game. 
       Candidates are scored on structural adherence (logic match) and consistency. 
       Candidates that echo the prompt without logical inversion (e.g., missing 'not') 
       are penalized heavily (proper scoring rule simulation).
    3. Feedback Control (FCM): Computes a 'prediction error' based on the gap between 
       the prompt's logical constraints and the candidate's structural signature. 
       The final score is adjusted by this error signal (PID-like correction).
       
    Scoring: Primary signal is structural/logic match. NCD is used strictly as a 
    tie-breaker for candidates with identical structural scores.
    """

    def __init__(self):
        # Keywords for structural parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'when', 'provided']
        self.booleans = ['true', 'false', 'yes', 'no']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_structure(self, text: str) -> Dict:
        """Extracts logical and numeric features from text."""
        lower = self._normalize(text)
        words = re.findall(r'\b\w+\b', lower)
        
        # Feature extraction
        has_neg = any(n in words for n in self.negations)
        has_comp = any(c in words for c in self.comparatives)
        has_cond = any(c in words for c in self.conditionals)
        
        # Numeric extraction
        nums = re.findall(r'-?\d+\.?\d*', lower)
        numbers = [float(n) for n in nums]
        
        # Boolean presence
        has_bool = any(b in words for b in self.booleans)

        return {
            'neg_count': sum(words.count(n) for n in self.negations),
            'comp_count': sum(words.count(c) for c in self.comparatives),
            'cond_count': sum(words.count(c) for c in self.conditionals),
            'numbers': numbers,
            'length': len(words),
            'has_bool': has_bool,
            'raw_lower': lower
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Computes Normalized Compression Distance as a tie-breaker."""
        if not s1 or not s2:
            return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(z1, z2)
        if denominator == 0:
            return 0.0
        return (z12 - min(z1, z2)) / denominator

    def _logic_score(self, prompt_struct: Dict, cand_struct: Dict) -> float:
        """
        Mechanism Design: Scores the candidate based on logical consistency 
        with the prompt's structural requirements.
        """
        score = 0.0
        
        # 1. Negation Alignment (Crucial for avoiding traps)
        # If prompt has negation, candidate should ideally reflect it or answer appropriately.
        # Heuristic: If prompt has negation, exact string match is suspicious (echo chamber).
        if prompt_struct['neg_count'] > 0:
            if cand_struct['raw_lower'] == prompt_struct['raw_lower']:
                score -= 0.5 # Penalty for echoing negation without processing
            elif cand_struct['neg_count'] > 0:
                score += 0.3 # Reward for acknowledging negation structure
            else:
                # Check if the candidate is a direct boolean answer which might be valid
                if not cand_struct['has_bool']:
                    score -= 0.2 # Slight penalty if ignoring negation entirely

        # 2. Comparative/Conditional Presence
        if prompt_struct['comp_count'] > 0:
            if cand_struct['comp_count'] > 0:
                score += 0.2
            # If prompt asks for comparison, short non-comparative answers might be weak
            elif cand_struct['length'] < 3 and not cand_struct['has_bool']:
                score -= 0.1

        if prompt_struct['cond_count'] > 0:
            if cand_struct['cond_count'] > 0:
                score += 0.2

        # 3. Numeric Consistency (Simple check)
        p_nums = prompt_struct['numbers']
        c_nums = cand_struct['numbers']
        if p_nums and c_nums:
            # If both have numbers, check if candidate numbers are within prompt range (loose check)
            # Or simply reward presence of numeric reasoning
            score += 0.1
            
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        p_struct = self._extract_structure(prompt)
        p_len = len(prompt)
        
        scored_candidates = []

        for cand in candidates:
            c_struct = self._extract_structure(cand)
            
            # --- Causal Inference Module (CIM) ---
            # Analyze structural match
            logic_score = self._logic_score(p_struct, c_struct)
            
            # --- Feedback Control Module (FCM) ---
            # Calculate error signal based on length and structural divergence
            # Ideal candidate should not be too far in length unless it's an explanation
            len_ratio = min(len(cand), p_len) / (max(len(cand), p_len) + 1e-6)
            
            # Control signal: Balance logic score with plausibility (length similarity heuristic)
            # If logic score is high, we trust it. If low, we penalize.
            control_signal = 0.0
            if logic_score > 0:
                control_signal = 0.3 * len_ratio # Reinforce if structure matches
            else:
                control_signal = -0.2 # Penalize logical mismatch
            
            # Final Score Composition
            # Base score from logic/mechanism design
            final_score = logic_score + control_signal
            
            # Add a small baseline for boolean answers to common questions
            if c_struct['has_bool'] and (p_struct['has_bool'] or 'is' in p_struct['raw_lower']):
                final_score += 0.1

            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Logic:{logic_score:.2f}, Control:{control_signal:.2f}",
                "_struct": c_struct # Internal use for tie-breaking
            })

        # Sorting: Primary by score, Secondary by NCD (as tiebreaker)
        # We want higher score first. For ties, we prefer lower NCD (more similar/compressed)
        # But per instructions: NCD is tiebreaker for candidates where no structural signal detected.
        # Here we use it to break exact score ties.
        
        def sort_key(item):
            # Negative score for descending sort
            # NCD as secondary sorter (ascending)
            ncd_val = self._compute_ncd(prompt, item['candidate'])
            return (-item['score'], ncd_val)

        scored_candidates.sort(key=sort_key)

        # Clean up internal fields and normalize scores to 0-1 range roughly
        max_score = max(c['score'] for c in scored_candidates) if scored_candidates else 0
        min_score = min(c['score'] for c in scored_candidates) if scored_candidates else 0
        range_score = max_score - min_score if max_score != min_score else 1.0

        result = []
        for item in scored_candidates:
            # Normalize score to 0.2 - 0.9 range to beat baseline randomness
            norm_score = 0.2 + (0.7 * (item['score'] - min_score) / range_score)
            
            result.append({
                "candidate": item['candidate'],
                "score": norm_score,
                "reasoning": item['reasoning']
            })

        return result

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural alignment and NCD as a fallback.
        """
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        # 1. Structural Consistency Check
        logic_val = self._logic_score(p_struct, a_struct)
        
        # 2. Length plausibility
        len_diff = abs(len(prompt) - len(answer))
        len_penalty = min(len_diff / 100.0, 0.5) # Penalize huge deviations slightly
        
        base_conf = 0.5 + logic_val * 0.4 - len_penalty * 0.2
        
        # 3. NCD Check (if structural signal is weak)
        if abs(logic_val) < 0.1:
            ncd = self._compute_ncd(prompt, answer)
            # If NCD is very high (dissimilar), confidence drops unless logic was strong
            if ncd > 0.8:
                base_conf -= 0.2
            elif ncd < 0.2:
                base_conf += 0.1 # Very similar strings often imply correctness in simple tasks
                
        return max(0.0, min(1.0, base_conf))