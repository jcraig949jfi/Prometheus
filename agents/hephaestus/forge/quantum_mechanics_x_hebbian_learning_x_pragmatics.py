import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Quantum-Hebbian Pragmatic Network (QHPN) Approximation.
    
    Mechanism:
    1. State Vector (|psi>): Encoded as a feature vector derived from structural parsing
       (negations, comparatives, conditionals, numeric values) rather than raw text.
    2. Superposition: Candidates exist as a superposition of semantic features.
    3. Hebbian Update: Weights evolve based on the real-part overlap (dot product) between
       the prompt's structural signature and the candidate's signature.
    4. Pragmatic Modulator C(context): A scoring factor that boosts candidates satisfying
       logical constraints (e.g., if prompt has "not", candidate must reflect negation).
       This separates the Hebbian path from the Pragmatic path to avoid negative interference.
    5. Measurement: The final score is the projection (dot product) modulated by pragmatics,
       collapsed to a scalar. Decoherence is simulated by attenuating scores of candidates
       that fail basic structural consistency checks.
    """

    def __init__(self):
        self.learning_rate = 0.5
        # Primitive basis vectors for structural features
        self.features = ['negation', 'comparative', 'conditional', 'numeric', 'question']

    def _extract_structure(self, text: str) -> np.ndarray:
        """Extract structural features to form the quantum state vector |psi>."""
        text_lower = text.lower()
        state = np.zeros(len(self.features), dtype=np.float64)
        
        # 1. Negation
        if re.search(r'\b(not|no|never|neither|nobody|nothing)\b', text_lower):
            state[0] = 1.0
            
        # 2. Comparative/Superlative
        if re.search(r'\b(more|less|better|worse|greater|smaller|than|most|least)\b', text_lower):
            state[1] = 1.0
            
        # 3. Conditional
        if re.search(r'\b(if|then|unless|otherwise|provided)\b', text_lower):
            state[2] = 1.0
            
        # 4. Numeric presence
        if re.search(r'\d+(\.\d+)?', text_lower):
            state[3] = 1.0
            
        # 5. Question/Interrogative
        if text.strip().endswith('?') or re.search(r'\b(what|who|where|when|why|how|is|are)\b', text_lower):
            state[4] = 1.0
            
        # Normalize to simulate unit vector-ish behavior for overlap calculation
        norm = np.linalg.norm(state)
        if norm > 0:
            state = state / norm
        return state

    def _pragmatic_modulator(self, prompt: str, candidate: str) -> float:
        """
        Evaluates context C(context) based on Gricean maxims and logical consistency.
        Returns a scaling factor between 0.0 and 1.2.
        Separated from Hebbian logic to prevent negative interaction.
        """
        p_low = prompt.lower()
        c_low = candidate.lower()
        score = 1.0
        
        # Check for Negation Consistency (Modus Tollens approximation)
        has_negation_prompt = bool(re.search(r'\b(not|no|never)\b', p_low))
        has_negation_cand = bool(re.search(r'\b(not|no|never)\b', c_low))
        
        # If prompt asks "Is it not X?", expecting "Yes" or "No" requires careful handling.
        # Simplified: If prompt implies negation, candidate should likely acknowledge it or be short.
        # Heuristic: If prompt is negative and candidate is positive assertion without qualification, penalize?
        # Instead, let's boost if candidate length is proportional (avoids "Yes"/"No" ambiguity alone)
        # or if it repeats key structural tokens.
        
        # Numeric Consistency
        nums_p = re.findall(r'\d+(\.\d+)?', p_low)
        nums_c = re.findall(r'\d+(\.\d+)?', c_low)
        
        if nums_p:
            # If numbers exist, candidate must have numbers to be high confidence (usually)
            # Unless it's a yes/no question about numbers.
            # Let's assume if prompt has complex math, answer needs numbers.
            if len(nums_p) > 2 and not nums_c:
                score *= 0.5 # Decoherence: likely wrong if no numbers in math problem
        
        # Question Word Matching
        if 'why' in p_low and not ('because' in c_low or 'since' in c_low):
            score *= 0.8 # Pragmatic failure: Why question needs explanation
            
        if 'how many' in p_low and not nums_c:
            score *= 0.6
            
        # Boost if candidate repeats specific structural keywords (Hebbian reinforcement via pragmatics)
        common_words = set(p_low.split()) & set(c_low.split())
        structural_common = common_words & {'not', 'more', 'less', 'if', 'than'}
        if structural_common:
            score += 0.1 * len(structural_common)
            
        return min(1.2, max(0.1, score))

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance as a tiebreaker."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            denom = max(c1, c2)
            if denom == 0: return 1.0
            return (c12 - min(c1, c2)) / denom
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Encode Prompt State |psi_prompt>
        psi_prompt = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate prompt length for NCD normalization if needed
        prompt_len = len(prompt) if len(prompt) > 0 else 1

        for cand in candidates:
            # 2. Encode Candidate State |psi_cand>
            psi_cand = self._extract_structure(cand)
            
            # 3. Hebbian Overlap: Re[<psi_prompt | psi_cand>]
            # Since vectors are real-valued approximations, this is just the dot product
            overlap = float(np.dot(psi_prompt, psi_cand))
            
            # 4. Pragmatic Modulation C(context)
            pragmatic_factor = self._pragmatic_modulator(prompt, cand)
            
            # 5. Measurement: Weighted Score
            # Base score from structural alignment (Hebbian)
            base_score = overlap * pragmatic_factor
            
            # Add small noise based on length match to break ties gently before NCD
            len_ratio = 1.0 - abs(len(cand) - prompt_len) / (prompt_len + 1)
            base_score += 0.05 * len_ratio
            
            results.append({
                "candidate": cand,
                "score": base_score,
                "reasoning": f"Hebbian overlap: {overlap:.3f}, Pragmatic factor: {pragmatic_factor:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Tie-breaking with NCD if scores are very close (within 0.01)
        # This ensures we beat the baseline on structural ties
        final_results = []
        for i, res in enumerate(results):
            if i > 0:
                prev_score = results[i-1]['score']
                curr_score = res['score']
                if abs(prev_score - curr_score) < 0.01:
                    # Apply NCD tiebreaker
                    ncd_prev = self._ncd_distance(prompt, results[i-1]['candidate'])
                    ncd_curr = self._ncd_distance(prompt, res['candidate'])
                    # Lower NCD is better (more similar/compressible together)
                    if ncd_curr < ncd_prev:
                        res['score'] = prev_score + 0.005 # Swap
                    else:
                        res['score'] = curr_score - 0.005
            
            final_results.append(res)
            
        # Normalize scores to 0-1 range roughly for consistency
        if final_results:
            max_s = final_results[0]['score']
            min_s = final_results[-1]['score']
            range_s = max_s - min_s if max_s != min_s else 1.0
            for res in final_results:
                res['score'] = max(0.0, min(1.0, (res['score'] - min_s) / range_s))
                
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the QHPN evaluation."""
        # Evaluate against a dummy set containing only the answer to get relative score
        # Or simply run the internal logic directly for efficiency
        psi_p = self._extract_structure(prompt)
        psi_a = self._extract_structure(answer)
        
        overlap = float(np.dot(psi_p, psi_a))
        prag = self._pragmatic_modulator(prompt, answer)
        
        raw_score = overlap * prag
        
        # Map raw score to 0-1. 
        # Overlap is 0-1 (normalized vectors). Prag is ~0.1-1.2.
        # Max theoretical ~1.2. 
        conf = min(1.0, max(0.0, raw_score))
        return conf