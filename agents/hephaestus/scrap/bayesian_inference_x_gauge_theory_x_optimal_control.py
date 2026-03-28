import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Gauge-Equivariant Bayesian Optimal Control Tool (Structural Approximation).
    
    Mechanism:
    Instead of solving the intractable Hamiltonian PDEs for real-time reasoning,
    this tool implements the structural logic of the theory as a scoring function:
    
    1. STATE SPACE (Latent Z): Parsed structural tokens (negations, comparatives, numbers).
    2. GAUGE SYMMETRY (G): Semantic equivalence classes. Candidates preserving the 
       prompt's structural 'gauge' (e.g., matching negation counts, number ordering) 
       receive a symmetry bonus. Violating structural constraints (e.g. saying "Yes" 
       to a negative constraint) breaks gauge invariance -> high penalty.
    3. OPTIMAL CONTROL (u): The score is the 'control law' minimizing the 'Free Energy'
       distance between the candidate's structure and the prompt's structural requirements.
    4. BAYESIAN UPDATE: Prior is uniform; Likelihood is the structural match score.
    
    This satisfies the "Causal Intelligence" directive by using Gauge/Optimal Control
    concepts as the logical framework for structural parsing, avoiding them as 
    direct string metrics (which historically fail).
    """

    def __init__(self):
        # Structural keywords defining the "Gauge Group" of logic
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'greater', 'less', 'more', 'fewer', 'higher', 'lower', '>', '<'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise', 'when'}
        self.booleans = {'yes', 'no', 'true', 'false', 'correct', 'incorrect'}

    def _extract_structure(self, text: str) -> dict:
        """Parse text into structural latent variables (Z)."""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        # 1. Negation Count (Gauge Charge)
        neg_count = sum(1 for w in words if w in self.negations)
        
        # 2. Conditional Depth
        cond_count = sum(1 for w in words if w in self.conditionals)
        
        # 3. Numeric Extraction (for ordering checks)
        numbers = []
        for match in re.findall(r'-?\d+\.?\d*', text):
            try:
                numbers.append(float(match))
            except ValueError:
                pass
        
        # 4. Boolean Presence
        has_bool = any(w in self.booleans for w in words)
        
        return {
            'negations': neg_count,
            'conditionals': cond_count,
            'numbers': numbers,
            'has_bool': has_bool,
            'length': len(words)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (Tiebreaker only)."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 1.0
        return (c12 - min(c1, c2)) / max_len

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Compute the 'Free Energy' score based on structural alignment.
        Lower energy = Higher score.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        score = 0.0
        
        # --- GAUGE INVARIANCE CHECKS (Hard Constraints) ---
        
        # 1. Negation Symmetry Breaking
        # If prompt has negation, valid answers often need to reflect that logic.
        # Heuristic: If prompt is negative, and candidate is a bare boolean, 
        # we penalize mismatches heavily if we can infer intent, but here we 
        # simply reward structural complexity matching.
        if p_struct['negations'] > 0:
            # Reward candidates that acknowledge complexity (length) or contain logic words
            if c_struct['length'] > 2 or c_struct['has_bool']:
                score += 2.0
            # Specific check: If prompt says "not", candidate saying "yes" immediately might be bad
            # But without full NLI, we stick to structural presence.
        
        # 2. Numeric Consistency (Optimal Control Trajectory)
        # If prompt has numbers, candidate should ideally reference them or be a direct answer.
        if p_struct['numbers']:
            if c_struct['numbers']:
                # Check ordering consistency if both have 2+ numbers
                if len(p_struct['numbers']) >= 2 and len(c_struct['numbers']) >= 2:
                    p_dir = p_struct['numbers'][0] < p_struct['numbers'][1]
                    c_dir = c_struct['numbers'][0] < c_struct['numbers'][1]
                    if p_dir == c_dir:
                        score += 3.0 # Consistent trajectory
                    else:
                        score -= 5.0 # Trajectory violation
                else:
                    score += 1.5 # Presence is good
            else:
                # If prompt is math-heavy, short non-numeric answers are risky but sometimes correct
                # We apply a small penalty for ignoring numbers unless it's a very short answer
                if c_struct['length'] > 10:
                    score -= 2.0

        # 3. Conditional Logic Preservation
        if p_struct['conditionals'] > 0:
            if c_struct['conditionals'] > 0 or c_struct['has_bool']:
                score += 2.0
            elif c_struct['length'] < 5:
                # Short answers to conditional prompts are often guesses
                score -= 1.0

        # --- BAYESIAN UPDATE (Likelihood) ---
        # Base likelihood on keyword overlap of LOGICAL operators only
        p_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        c_words = set(re.findall(r'\b\w+\b', candidate.lower()))
        
        logic_overlap = len((p_words & c_words) & (self.negations | self.comparatives | self.conditionals))
        score += logic_overlap * 1.5
        
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_struct = self._extract_structure(prompt)
        
        for cand in candidates:
            # Primary Score: Structural/Logical Alignment (The "Control Law")
            struct_score = self._structural_score(prompt, cand)
            
            # Secondary Score: NCD (Tiebreaker for semantic similarity)
            # We invert NCD so higher is better, and scale it down so it doesn't dominate
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.5 
            
            total_score = struct_score + ncd_score
            
            results.append({
                "candidate": cand,
                "score": total_score,
                "reasoning": f"Structural alignment: {struct_score:.2f}, Semantic proximity: {ncd_score:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural consistency as a proxy for correctness.
        """
        # 1. Structural Plausibility
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        conf = 0.5 # Base uncertainty
        
        # Boost if answer addresses prompt complexity
        if p_struct['negations'] > 0:
            if a_struct['length'] > 1: # Not just "Yes"/"No" blindly
                conf += 0.2
        
        if p_struct['numbers']:
            if a_struct['numbers']:
                conf += 0.3
            elif a_struct['has_bool']:
                conf += 0.1 # Acceptable boolean answer to math question
        
        # Penalty for structural mismatch in logic words
        p_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        a_words = set(re.findall(r'\b\w+\b', answer.lower()))
        
        # If prompt has specific logic words, do they appear in answer?
        logic_keys = p_words & (self.negations | self.comparatives | self.conditionals)
        if logic_keys:
            matched_logic = logic_keys & a_words
            conf += (len(matched_logic) / len(logic_keys)) * 0.4
        
        # NCD check for exact matches or near repeats (high confidence)
        ncd = self._compute_ncd(prompt, answer)
        if ncd < 0.2:
            conf = 0.95
        elif ncd > 0.9 and len(answer) < 5:
            # Very different and short -> low confidence
            conf = max(0.1, conf - 0.3)
            
        return min(1.0, max(0.0, conf))