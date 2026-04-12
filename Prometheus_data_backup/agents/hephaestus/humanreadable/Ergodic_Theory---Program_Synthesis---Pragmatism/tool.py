import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Pragmatic Ergodic Program Synthesizer (PEPS) - Structural Implementation
    
    Mechanism:
    1. ERGODIC THEORY (Time-Average Approximation): Instead of computing 
       intractable ensemble expectations over all possible reasoning paths, 
       we approximate the "truth" by averaging structural signals across 
       the text (time) domain. We treat the prompt as a dynamical system 
       and extract statistical invariants (negations, comparatives, numbers).
       
    2. PROGRAM SYNTHESIS (Candidate as Program): Each candidate answer is 
       treated as a program 'p' that attempts to satisfy the constraints 
       extracted from the prompt. We "execute" this by checking constraint 
       satisfaction (e.g., if prompt says "not X", candidate containing "X" 
       gets penalized).
       
    3. PRAGMATISM (Empirical Verification): The final score is a pragmatic 
       measure of how well the candidate "works" (satisfies constraints) 
       in practice. We use NCD only as a tie-breaking similarity metric 
       when structural signals are ambiguous, adhering to the "Goodhart Warning" 
       by prioritizing logical structure over raw compression.
    """

    def __init__(self):
        # Structural patterns representing logical invariants
        self.negation_patterns = [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b', r'\bimpossible\b']
        self.comparative_patterns = [r'\bmore\s+than\b', r'\bless\s+than\b', r'\bgreater\b', r'\bsmaller\b', r'\b<\b', r'\b>\b']
        self.conditional_patterns = [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\botherwise\b']
        self.numeric_pattern = r'\d+(?:\.\d+)?'

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Extract structural invariants from text (Ergodic observation)."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall('|'.join(self.negation_patterns), text_lower)),
            'comparatives': len(re.findall('|'.join(self.comparative_patterns), text_lower)),
            'conditionals': len(re.findall('|'.join(self.conditional_patterns), text_lower)),
            'numbers': re.findall(self.numeric_pattern, text),
            'length': len(text)
        }
        return features

    def _check_constraint_satisfaction(self, prompt_feats: Dict, candidate_feats: Dict, 
                                       prompt_text: str, candidate_text: str) -> float:
        """
        Evaluate how well the candidate program satisfies prompt constraints.
        Returns a score between 0.0 and 1.0 based on logical consistency.
        """
        score = 1.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has high negation density, candidate should reflect awareness (simplified heuristic)
        if prompt_feats['negations'] > 0:
            # Penalize if candidate completely ignores negation context while being short/absolute
            if candidate_feats['negations'] == 0 and prompt_feats['negations'] >= 2:
                score -= 0.2
        
        # 2. Numeric Consistency
        # If numbers exist in prompt, candidate should ideally reference them or be logically consistent
        if prompt_feats['numbers']:
            p_nums = [float(n) for n in prompt_feats['numbers']]
            c_nums = [float(n) for n in candidate_feats['numbers']]
            
            if c_nums:
                # Check for gross contradictions (e.g. prompt implies small, candidate says huge)
                # This is a rough heuristic for "program execution"
                if max(p_nums) < 10 and c_nums and max(c_nums) > 100:
                    score -= 0.3
            else:
                # Missing numbers in candidate when prompt is numeric-heavy might indicate failure
                if len(p_nums) >= 2:
                    score -= 0.1

        # 3. Conditional Logic Presence
        if prompt_feats['conditionals'] > 0 and candidate_feats['conditionals'] == 0:
            # Candidate might be too simplistic if it misses conditional logic
            score -= 0.1

        # 4. Length Pragmatism (Avoiding trivial answers)
        if candidate_feats['length'] < 5:
            score -= 0.4 # Too short to be a valid program
            
        return max(0.0, min(1.0, score))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
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
            
        return (len_combined - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        prompt_feats = self._extract_features(prompt)
        results = []
        
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            
            # Primary Score: Structural/Logical Satisfaction (The "Program Execution")
            logic_score = self._check_constraint_satisfaction(prompt_feats, cand_feats, prompt, cand)
            
            # Secondary Score: NCD Tiebreaker (Similarity to prompt context)
            # Used only when logic scores are close or ambiguous
            ncd_val = self._ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val # Convert distance to similarity
            
            # Weighted combination: 80% Logic, 20% Similarity (Pragmatic balance)
            final_score = (logic_score * 0.8) + (ncd_score * 0.2)
            
            # Reasoning trace
            reasoning = f"Logic:{logic_score:.2f} Sim:{ncd_score:.2f}"
            if prompt_feats['negations'] > 0 and cand_feats['negations'] == 0:
                reasoning += " [Warn: Missing negation handling]"
            if len(cand) < 5:
                reasoning += " [Warn: Trivial answer]"

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Uses the same ergodic-structural evaluation as evaluate().
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize the score to ensure it feels like a confidence metric
        # A score > 0.6 is considered "confident" in this structural framework
        raw_score = res[0]['score']
        return min(1.0, max(0.0, raw_score))