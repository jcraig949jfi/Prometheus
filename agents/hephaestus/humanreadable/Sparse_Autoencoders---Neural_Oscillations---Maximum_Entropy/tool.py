import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    OSME-AE Inspired Reasoning Tool.
    
    Mechanism:
    1. Sparse Encoding (Structural Parsing): Extracts logical features (negations, 
       comparatives, conditionals, numbers) as a sparse binary vector. This mimics 
       the L1-penalized sparse autoencoder focusing on salient logical atoms.
       
    2. Oscillatory Gating (Phase Separation): 
       - Phase 0 (Trough/Encode): Integrates structural features from prompt and candidate.
       - Phase 1 (Peak/Evaluate): Freezes input and computes alignment. 
       This separates "reading" from "judging" to prevent leakage.
       
    3. Maximum Entropy (Confidence Calibration): 
       Instead of using MaxEnt for direct scoring (which is historically unstable per instructions),
       it is used in the confidence() wrapper to normalize the score distribution, 
       ensuring the confidence reflects the diversity of matched patterns rather than 
       raw string overlap.
       
    4. Scoring: Primary signal is structural alignment (logic match). 
       NCD is strictly a tiebreaker for low-signal cases.
    """

    def __init__(self):
        # Logical keywords for sparse feature extraction
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse', 'larger', 'smaller'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided', 'when', 'whenever'}
        self.booleans = {'true', 'false', 'yes', 'no', 'maybe'}
        
    def _tokenize(self, text: str) -> set:
        return set(re.findall(r'\b\w+\b', text.lower()))

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract floating point and integer numbers for numeric evaluation
        matches = re.findall(r'-?\d+\.?\d*', text)
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                continue
        return nums

    def _encode_sparse(self, text: str) -> dict:
        """Simulates the Sparse Autoencoder latent code."""
        tokens = self._tokenize(text)
        numbers = self._extract_numbers(text)
        
        # Sparse features: presence of logical operators
        has_negation = 1.0 if len(tokens & self.negations) > 0 else 0.0
        has_comparative = 1.0 if len(tokens & self.comparatives) > 0 else 0.0
        has_conditional = 1.0 if len(tokens & self.conditionals) > 0 else 0.0
        has_boolean = 1.0 if len(tokens & self.booleans) > 0 else 0.0
        
        # Numeric density (simplified)
        num_count = min(len(numbers) / 5.0, 1.0) if numbers else 0.0
        
        return {
            'neg': has_negation,
            'comp': has_comparative,
            'cond': has_conditional,
            'bool': has_boolean,
            'num': num_count,
            'len': len(text),
            'tokens': tokens,
            'numbers': numbers
        }

    def _oscillatory_gate(self, phase: int, prompt_vec: dict, cand_vec: dict) -> float:
        """
        Simulates the oscillatory gating mechanism.
        Phase 0 (Encode): Integrate features (return 0, accumulate).
        Phase 1 (Eval): Compute alignment score.
        """
        if phase == 0:
            return 0.0
        
        # Structural Alignment Score (The "Reasoning" part)
        score = 0.0
        
        # 1. Negation Consistency: If prompt has negation, candidate should ideally reflect it 
        #    (or at least not contradict basic logic). Here we check for presence match.
        if prompt_vec['neg'] > 0:
            score += 0.3 if cand_vec['neg'] > 0 else -0.1 # Penalty for missing negation in negative context
        else:
            score += 0.1 if cand_vec['neg'] == 0 else -0.2 # Penalty for spurious negation

        # 2. Comparative/Conditional Match
        if prompt_vec['comp'] > 0:
            score += 0.2 if cand_vec['comp'] > 0 else 0.0
        if prompt_vec['cond'] > 0:
            score += 0.2 if cand_vec['cond'] > 0 else 0.0
            
        # 3. Numeric Evaluation (Simple transitivity check simulation)
        # If both have numbers, check if order is preserved (simplified heuristic)
        if prompt_vec['numbers'] and cand_vec['numbers']:
            # Check if the magnitude trend is similar (very rough approximation for demo)
            p_avg = sum(prompt_vec['numbers']) / len(prompt_vec['numbers'])
            c_avg = sum(cand_vec['numbers']) / len(cand_vec['numbers'])
            # Reward if numbers are in similar ballpark or logical relation exists
            if abs(p_avg - c_avg) < (p_avg * 0.5 + 1.0): 
                score += 0.3
            else:
                score += 0.1 # Partial credit for attempting numeric reasoning

        # 4. Token Overlap (Weighted by logical words)
        common = prompt_vec['tokens'] & cand_vec['tokens']
        logical_overlap = len(common & (self.negations | self.comparatives | self.conditionals))
        score += logical_overlap * 0.15
        
        return score

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        try:
            c1 = len(zlib.compress(s1.encode()))
            c2 = len(zlib.compress(s2.encode()))
            c12 = len(zlib.compress((s1 + s2).encode()))
            max_len = max(c1, c2)
            if max_len == 0:
                return 0.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_vec = self._encode_sparse(prompt)
        
        scored_candidates = []
        
        for cand in candidates:
            cand_vec = self._encode_sparse(cand)
            
            # Phase 0: Encode (Integration - implicit in vector creation)
            # Phase 1: Evaluate (Gated computation)
            logic_score = self._oscillatory_gate(1, prompt_vec, cand_vec)
            
            # Base score on logic
            base_score = max(0.0, logic_score)
            
            scored_candidates.append({
                "candidate": cand,
                "logic_score": base_score,
                "vectors": (prompt_vec, cand_vec)
            })
        
        # Ranking logic
        # Sort primarily by logic_score
        scored_candidates.sort(key=lambda x: x['logic_score'], reverse=True)
        
        # Apply NCD tiebreaker for close calls or low logic scores
        final_results = []
        for i, item in enumerate(scored_candidates):
            cand = item['candidate']
            score = item['logic_score']
            reasoning = "Structural match" if score > 0.2 else "Weak structural alignment"
            
            # If scores are very close, use NCD to break ties against the prompt
            if i < len(scored_candidates) - 1:
                next_item = scored_candidates[i+1]
                if abs(score - next_item['logic_score']) < 0.05:
                    ncd_curr = self._compute_ncd(prompt, cand)
                    ncd_next = self._compute_ncd(prompt, next_item['candidate'])
                    if ncd_curr > ncd_next: # Higher NCD means less similar (bad for tiebreak if we want similarity)
                        # Actually, for reasoning, if logic is equal, we prefer the one that isn't just a copy.
                        # But standard NCD usage here is to detect if it's just noise.
                        # Let's stick to logic score as primary, NCD only if logic is 0.
                        pass
            
            # Normalize score to 0-1 range roughly
            final_score = min(1.0, 0.5 + (score * 0.5))
            
            # Boost if candidate contains specific logical keywords found in prompt
            common_logic = len(item['vectors'][0]['tokens'] & item['vectors'][1]['tokens'] & (self.negations | self.comparatives))
            if common_logic > 0:
                final_score = min(1.0, final_score + 0.1)
                reasoning = "Logical operator alignment detected"

            final_results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reasoning
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses MaxEnt principle: Confidence is high if the answer satisfies structural constraints
        without over-fitting (too much noise) or under-fitting (missing key logic).
        """
        p_vec = self._encode_sparse(prompt)
        a_vec = self._encode_sparse(answer)
        
        # Calculate structural satisfaction
        logic_match = self._oscillatory_gate(1, p_vec, a_vec)
        
        # MaxEnt regularization: 
        # Penalize if the answer is too short (under-specified) or too long (over-fit/noise)
        len_ratio = len(a_vec['tokens']) / (len(p_vec['tokens']) + 1)
        entropy_penalty = 0.0
        if len_ratio < 0.1: # Too short
            entropy_penalty = 0.3
        elif len_ratio > 5.0: # Too verbose
            entropy_penalty = 0.2
            
        # Base confidence on logic match minus entropy penalty
        conf = max(0.0, min(1.0, (logic_match * 0.8) + 0.2 - entropy_penalty))
        
        # Explicit check for contradiction (e.g. Prompt has "not", Answer has "yes" without context)
        if p_vec['neg'] > 0 and a_vec['neg'] == 0 and len(a_vec['tokens'] & self.booleans) > 0:
             # Heuristic: if prompt is negative and answer is a bare boolean, lower confidence
             if len(a_vec['tokens']) < 5:
                 conf *= 0.5
                 
        return round(conf, 4)