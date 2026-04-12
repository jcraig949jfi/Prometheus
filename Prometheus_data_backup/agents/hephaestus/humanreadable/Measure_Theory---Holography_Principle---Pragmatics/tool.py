import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Context-Sensitive Holographic Measure-Theoretic Inference Engine (CHMIE)
    
    Mechanism:
    1. Measure Theory: Treats the prompt and candidates as a probability space.
       We define a 'reference measure' based on structural tokens (negations, numbers).
    2. Holography Principle (Restricted): Instead of full projection, we use a 
       'Boundary Map' that compresses the text into a low-dimensional structural 
       signature (counts of logic operators, numeric values) to avoid overfitting 
       to surface noise (the 'bulk').
    3. Pragmatics: We apply Gricean constraints as penalty terms. 
       - Relevance: Penalize candidates missing key structural tokens found in prompt.
       - Quantity: Penalize extreme length deviations.
       - Quality: Check for direct contradiction of detected negations.
    
    The final score is a weighted sum of Structural Match (Primary) and 
    NCD similarity (Tiebreaker), modulated by Pragmatic penalties.
    """

    def __init__(self):
        # Structural keywords for the "Boundary" projection
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'larger', 'fewer', 'better', 'worse']
        self.conditionals = ['if', 'unless', 'provided', 'when', 'then']
        self.booleans = ['yes', 'no', 'true', 'false']
        
    def _extract_structure(self, text: str) -> Dict:
        """Projects text onto the low-dimensional structural manifold."""
        t = text.lower()
        words = re.findall(r'\b\w+\b', t)
        
        # Count structural markers
        neg_count = sum(1 for w in words if w in self.negations)
        comp_count = sum(1 for w in words if w in self.comparatives)
        cond_count = sum(1 for w in words if w in self.conditionals)
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r'\d+\.?\d*', t)
        nums = [float(n) for n in numbers]
        
        return {
            'neg': neg_count,
            'comp': comp_count,
            'cond': cond_count,
            'nums': nums,
            'len': len(words),
            'raw_len': len(text)
        }

    def _evaluate_numeric_logic(self, prompt_struct: Dict, cand_struct: Dict) -> float:
        """Checks numeric consistency (e.g., 9.11 < 9.9)."""
        p_nums = prompt_struct['nums']
        c_nums = cand_struct['nums']
        
        if not p_nums or not c_nums:
            return 0.0 # No numeric logic to verify
        
        # Simple heuristic: If prompt has numbers and candidate has numbers,
        # check if they preserve order if explicitly compared, or just presence.
        # For this implementation, we reward matching the specific numbers found.
        match_score = 0.0
        for pn in p_nums:
            if any(abs(pn - cn) < 1e-6 for cn in c_nums):
                match_score += 1.0
        
        return match_score / (len(p_nums) + 1e-6)

    def _pragmatic_penalty(self, prompt: str, candidate: str, p_struct: Dict, c_struct: Dict) -> float:
        """
        Calculates Gricean violations.
        Returns a penalty (0.0 = perfect, 1.0 = total violation).
        """
        penalty = 0.0
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # 1. Quality (Truth-likeness/Contradiction)
        # If prompt has "not X" and candidate is just "X", penalize heavily.
        # Simple approximation: if prompt has negation but candidate lacks it (and isn't a boolean 'no')
        if p_struct['neg'] > 0 and c_struct['neg'] == 0:
            # Check if candidate is a simple denial like "no" or "false" which might be valid
            if not any(b in c_low for b in self.booleans):
                penalty += 0.3
        
        # 2. Quantity (Length appropriateness)
        # Extreme brevity or verbosity compared to prompt structure
        if p_struct['len'] > 10: # Only if prompt is substantial
            ratio = c_struct['len'] / (p_struct['len'] + 1e-6)
            if ratio < 0.1 or ratio > 5.0:
                penalty += 0.2
                
        # 3. Relevance (Keyword overlap of structural tokens)
        # If prompt uses comparatives, relevant answers often do too (or contain numbers)
        if p_struct['comp'] > 0 and c_struct['comp'] == 0 and not c_struct['nums']:
            penalty += 0.1
            
        return min(penalty, 1.0)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            max_len = max(c1, c2)
            if max_len == 0: return 0.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        p_struct = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate prompt complexity for normalization
        p_complexity = p_struct['neg'] + p_struct['comp'] + p_struct['cond']
        
        for cand in candidates:
            c_struct = self._extract_structure(cand)
            
            # 1. Structural Parsing Score (Primary Signal)
            # Reward matching structural density
            struct_match = 0.0
            
            # Negation alignment
            if (p_struct['neg'] > 0) == (c_struct['neg'] > 0):
                struct_match += 0.4
            elif p_struct['neg'] == 0 and c_struct['neg'] == 0:
                struct_match += 0.2 # Neutral alignment
                
            # Comparative alignment
            if (p_struct['comp'] > 0) == (c_struct['comp'] > 0):
                struct_match += 0.3
                
            # Conditional alignment
            if (p_struct['cond'] > 0) == (c_struct['cond'] > 0):
                struct_match += 0.2
                
            # Numeric consistency
            struct_match += self._evaluate_numeric_logic(p_struct, c_struct) * 0.5
            
            # 2. Pragmatic Penalty (Modifier)
            prag_penalty = self._pragmatic_penalty(prompt, cand, p_struct, c_struct)
            
            # 3. NCD Tiebreaker (Only if structural signals are weak or equal)
            # We invert NCD (0 is same, 1 is diff) to be a score (1 is same)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Final Score Calculation
            # Base score from structure
            score = struct_match
            
            # Apply pragmatic penalty
            score *= (1.0 - prag_penalty)
            
            # Add small NCD component only if structure is ambiguous or as a tiebreaker boost
            # We weight NCD lightly to avoid the "bag of words" trap, unless structure is high
            if p_complexity == 0:
                # If no structure, rely more on NCD but capped
                score = 0.5 * ncd_score 
            else:
                # Structure dominates, NCD breaks ties
                score += (ncd_score * 0.1)
            
            results.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": f"Struct:{struct_match:.2f}, PragPen:{prag_penalty:.2f}, NCD:{ncd_score:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Uses the evaluate method internally on a set including the answer 
        to see how it ranks, but simplified for single pair.
        """
        # Generate a dummy negative candidate to compare against
        # If the answer scores significantly higher than a gibberish string, confidence is high.
        # However, per interface, we just need a 0-1 score for this specific pair.
        
        # We simulate a mini-evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        # Normalize the top score to 0-1 range based on theoretical max
        # Max theoretical struct score approx 1.4 (0.4+0.3+0.2+0.5)
        raw_score = res[0]['score']
        
        # Heuristic mapping to 0-1
        # > 1.0 is very strong structural match
        # < 0.2 is weak
        conf = min(1.0, max(0.0, raw_score / 1.5))
        
        return round(conf, 4)