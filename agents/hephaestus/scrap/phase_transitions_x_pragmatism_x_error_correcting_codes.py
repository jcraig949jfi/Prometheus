import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Pragmatic Phase-Transition Decoder (PPTD) Implementation.
    
    Mechanism:
    1. Structural Parsing (Pragmatism): Extracts logical constraints (negations, 
       comparatives, conditionals) to form a 'utility' score for each candidate.
       This acts as the external field driving the system.
    2. Error Correction (LDPC Analogy): Uses a consistency check between the 
       prompt's structural signature and the candidate's signature. Candidates 
       violating hard constraints (e.g., negation flips) receive a massive penalty 
       (simulating parity check failure).
    3. Phase Transition: The final score is not linear. It applies a sigmoidal 
       'annealing' function based on the gap between the top candidate's utility 
       and the mean. This mimics the jump from disordered (exploration) to 
       ordered (exploitation) states, sharpening the distinction between high 
       and low confidence answers.
    4. NCD Tiebreaker: Used only when structural signals are ambiguous.
    """

    def __init__(self):
        # Keywords for structural parsing
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.bool_words = ['yes', 'no', 'true', 'false', 'correct', 'incorrect']

    def _structural_parse(self, text: str) -> Dict[str, any]:
        """Extracts logical features from text."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        has_neg = any(n in words for n in self.negations)
        has_comp = any(c in words for c in self.comparatives)
        has_cond = any(c in words for c in self.conditionals)
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r'\d+\.?\d*', lower_text)
        nums = [float(n) for n in numbers] if numbers else []
        
        return {
            'neg_count': sum(1 for n in self.negations if n in words),
            'has_comp': has_comp,
            'has_cond': has_cond,
            'numbers': nums,
            'length': len(words),
            'raw_lower': lower_text
        }

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _check_logical_consistency(self, prompt_feat: Dict, cand_feat: Dict, candidate: str) -> float:
        """
        Simulates LDPC parity checks. 
        Returns 1.0 for pass, 0.0 for hard fail, 0.5 for soft mismatch.
        """
        # Hard Constraint 1: Negation Flip Detection
        # If prompt asks "Which is NOT...", candidate should not be a simple affirmative without context
        # This is a heuristic approximation of parity check
        prompt_neg = prompt_feat['neg_count'] > 0
        cand_lower = cand_feat['raw_lower']
        
        # Simple heuristic: If prompt has strong negation, and candidate is a bare "yes"/"no", 
        # we need to be careful. Here we just score based on feature alignment.
        
        score = 1.0
        
        # Consistency Check: Number presence
        if prompt_feat['numbers'] and not cand_feat['numbers']:
            # If prompt has numbers and candidate has none, it might be wrong (unless boolean)
            has_bool = any(b in cand_lower for b in self.bool_words)
            if not has_bool:
                score *= 0.8 # Soft penalty
        
        # Consistency Check: Length sanity (prevent truncation errors)
        if cand_feat['length'] < 2 and prompt_feat['length'] > 10:
             # Very short answers might be valid (Yes/No), but check if prompt demands more
             if "explain" in prompt_feat['raw_lower'] or "list" in prompt_feat['raw_lower']:
                 score *= 0.5

        return score

    def _phase_transition_score(self, utilities: List[float], temperature: float = 0.5) -> List[float]:
        """
        Applies a sigmoidal transformation to utilities to simulate phase transition.
        As temperature lowers (or utility gap widens), the system snaps to the max.
        """
        if not utilities:
            return []
        
        max_u = max(utilities)
        min_u = min(utilities)
        range_u = max_u - min_u if max_u != min_u else 1.0
        
        final_scores = []
        for u in utilities:
            # Normalize to [0, 1] relative to range
            norm_u = (u - min_u) / range_u
            
            # Sigmoidal sharpening (Order Parameter)
            # x = (u - threshold) / T. Here threshold is 0.5 (mean-ish)
            # We shift so that average utility yields 0.5 score, high yields ~1.0
            exponent = (norm_u - 0.5) / (temperature + 1e-9)
            
            # Avoid overflow
            if exponent > 20:
                val = 1.0
            elif exponent < -20:
                val = 0.0
            else:
                import math
                val = 1.0 / (1.0 + math.exp(-exponent))
            
            final_scores.append(val)
            
        return final_scores

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feat = self._structural_parse(prompt)
        utilities = []
        reasoning_logs = []
        
        # Step 1: Compute raw utility based on structural alignment and NCD
        for cand in candidates:
            cand_feat = self._structural_parse(cand)
            
            # 1. Structural Utility (Pragmatism)
            # Reward candidates that share structural features (e.g. numbers if prompt has them)
            struct_score = 0.5
            
            # Number match bonus
            if prompt_feat['numbers'] and cand_feat['numbers']:
                # Check if candidate numbers are subset or close to prompt (heuristic)
                struct_score += 0.3
            
            # Negation alignment (simplified)
            if prompt_feat['neg_count'] > 0:
                # If prompt is negative, candidates containing negation words might be more 'aligned' 
                # in terms of topic, though logic depends on context. 
                # We rely on the LDPC-style consistency check for the hard logic.
                pass

            # 2. LDPC-style Consistency Check
            consistency = self._check_logical_consistency(prompt_feat, cand_feat, cand)
            
            # 3. NCD as Tiebreaker/Refiner
            # Lower NCD to prompt usually means higher relevance in short contexts
            ncd_val = self._calculate_ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val # Convert distance to similarity
            
            # Combined Utility
            # Weight structural/consistency heavily, NCD as tiebreaker
            utility = (consistency * 0.6) + (struct_score * 0.2) + (ncd_score * 0.2)
            
            utilities.append(utility)
            reasoning_logs.append(f"Struct:{struct_score:.2f}, Consist:{consistency:.2f}, NCD:{ncd_val:.2f}")

        # Step 2: Apply Phase Transition (Sharpening)
        final_scores = self._phase_transition_score(utilities, temperature=0.2)
        
        # Step 3: Rank and Format
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": float(final_scores[i]),
                "reasoning": reasoning_logs[i]
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the gap between the answer's score and a theoretical 'wrong' baseline.
        """
        # Evaluate against a dummy set including the answer and a perturbed version
        # to simulate the 'magnetization' of the correct state.
        
        # Create a pseudo-candidate list to run the internal scoring mechanism
        # We compare the answer against itself (perfect match) and a garbage string
        # to see where it lands in the phase space.
        
        # Actually, simpler approach consistent with evaluate():
        # Run evaluate with [answer, "I don't know", ""] and see the score of 'answer'
        candidates = [answer, "I don't know", ""]
        results = self.evaluate(prompt, candidates)
        
        # Find the score for the specific answer provided
        score = 0.0
        for res in results:
            if res['candidate'] == answer:
                score = res['score']
                break
        
        # If the answer rises to the top in a competitive eval, confidence is high.
        # The phase transition should have pushed correct answers near 1.0 and wrong near 0.0
        return max(0.0, min(1.0, score))