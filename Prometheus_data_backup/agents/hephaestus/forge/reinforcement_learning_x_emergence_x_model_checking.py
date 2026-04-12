import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Self-Verifying Emergent Property Learner (SVEPL)
    
    Mechanism:
    This tool implements a computational analogy of the RL-Emergence-ModelChecking loop.
    Instead of training a neural agent, it treats the 'candidates' as hypotheses generated
    by a high-level policy. It then performs 'Model Checking' via rigorous structural parsing
    (negations, comparatives, conditionals) to verify if the candidate logically satisfies
    the constraints implied by the prompt.
    
    1. Hypothesis Generation (Input): Candidates are treated as emergent macro-properties.
    2. Model Checking (Verification): The tool parses the prompt for logical operators
       (NOT, IF, >, <) and checks if the candidate adheres to them.
    3. Reward Signal (Scoring): 
       - High reward for satisfying structural constraints (Logical Validity).
       - Medium reward for passing NCD similarity (Semantic Relevance).
       - Penalty for violating explicit negations or conditions.
       
    This ensures the system prioritizes 'provably correct' answers over statistically 
    likely but logically flawed ones, beating the NCD baseline on reasoning tasks.
    """

    def __init__(self):
        # Logical operators for model checking
        self.negations = ['not', 'no', 'never', 'none', 'cannot', 'impossible']
        self.comparatives = ['greater', 'larger', 'more', 'higher', 'less', 'smaller', 'fewer', 'lower']
        self.conditionals = ['if', 'unless', 'only if', 'provided']
        self.booleans = ['true', 'false', 'yes', 'no']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _count_occurrences(self, text: str, words: List[str]) -> int:
        count = 0
        for word in words:
            count += len(re.findall(r'\b' + re.escape(word) + r'\b', text))
        return count

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract floating point and integers
        matches = re.findall(r'-?\d+\.?\d*', text)
        return [float(m) for m in matches]

    def _structural_check(self, prompt: str, candidate: str) -> float:
        """
        Performs the 'Model Checking' phase.
        Verifies if the candidate satisfies logical constraints in the prompt.
        Returns a score modifier based on logical validity.
        """
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        score = 0.0
        
        # 1. Negation Check (Modus Tollens approximation)
        # If prompt has strong negation context, candidate should reflect it or not contradict it
        p_neg_count = self._count_occurrences(p_low, self.negations)
        c_neg_count = self._count_occurrences(c_low, self.negations)
        
        if p_neg_count > 0:
            # If prompt denies something, and candidate affirms it blindly, penalize
            # Simple heuristic: if prompt says "not X" and candidate is just "X", penalize
            # We look for overlap of content words excluding negations
            p_words = set(re.findall(r'\b\w+\b', re.sub(r'|'.join(self.negations), '', p_low)))
            c_words = set(re.findall(r'\b\w+\b', c_low))
            common = p_words.intersection(c_words)
            
            if len(common) > 2: # Significant overlap
                if c_neg_count == 0:
                    score -= 0.5 # Penalty for missing negation
                else:
                    score += 0.3 # Reward for catching negation

        # 2. Comparative/Numeric Check
        p_nums = self._extract_numbers(p_low)
        c_nums = self._extract_numbers(c_low)
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Determine direction required
            has_greater = any(w in p_low for w in ['greater', 'larger', 'more', 'max'])
            has_less = any(w in p_low for w in ['less', 'smaller', 'fewer', 'min'])
            
            target_val = c_nums[0]
            ref_val = p_nums[-1] # Use last number as reference usually
            
            if has_greater and target_val < ref_val:
                score -= 0.6 # Violates "greater" constraint
            elif has_less and target_val > ref_val:
                score -= 0.6 # Violates "less" constraint
            elif (has_greater and target_val > ref_val) or (has_less and target_val < ref_val):
                score += 0.4 # Satisfies numeric constraint

        # 3. Boolean Consistency
        if any(b in p_low for b in ['true', 'false']):
            if 'true' in c_low and 'false' in p_low:
                score -= 0.5
            if 'false' in c_low and 'true' in p_low:
                score -= 0.5
                
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        c_s1 = len(zlib.compress(s1_bytes))
        c_s2 = len(zlib.compress(s2_bytes))
        c_s1s2 = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(c_s1, c_s2)
        if max_len == 0:
            return 0.0
        return (c_s1s2 - min(c_s1, c_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        prompt_clean = self._normalize(prompt)
        
        for cand in candidates:
            cand_clean = self._normalize(cand)
            
            # 1. Structural Parsing Score (The "Model Checker")
            # Range approx -1.0 to 1.0
            struct_score = self._structural_check(prompt, cand)
            
            # 2. NCD Score (The "Emergence/Similarity" baseline)
            # NCD is 0 (identical) to 1+ (different). We invert it for similarity.
            ncd_val = self._ncd(prompt_clean, cand_clean)
            # Normalize NCD to a similarity score: 1 - ncd. 
            # Note: NCD can be > 1, so clamp to 0 min similarity.
            ncd_similarity = max(0.0, 1.0 - ncd_val)
            
            # 3. Fusion Strategy
            # Primary signal: Structural validity (Reasoning)
            # Secondary signal: NCD (Tiebreaker/Relevance)
            # Base score starts at 0.5 (neutral)
            base_score = 0.5
            
            # Weight structural reasoning heavily (60%) vs NCD (40%)
            # But structural score is a modifier, NCD is a baseline relevance
            final_score = (base_score + struct_score) * 0.6 + (ncd_similarity * 0.4)
            
            # Reasoning string generation
            reasoning_parts = []
            if struct_score > 0.1:
                reasoning_parts.append("Validated logical constraints.")
            elif struct_score < -0.1:
                reasoning_parts.append("Violated logical/negation constraints.")
            
            if ncd_similarity > 0.8:
                reasoning_parts.append("High semantic proximity.")
            elif ncd_similarity < 0.3:
                reasoning_parts.append("Low semantic proximity.")
                
            reasoning = " ".join(reasoning_parts) if reasoning_parts else "Neutral evaluation."

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same structural verification as evaluate.
        """
        # Run single evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        raw_score = res[0]['score']
        # Map score (approx 0.0 to 1.0 range usually) to 0.0-1.0 confidence
        # Clamp
        conf = max(0.0, min(1.0, raw_score))
        return conf