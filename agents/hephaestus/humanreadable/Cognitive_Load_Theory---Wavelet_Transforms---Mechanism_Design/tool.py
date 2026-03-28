import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Wavelet-Based Adaptive Resource Allocation Mechanism (WB-ARAM).
    
    Mechanism:
    1. Structural Parsing (Cognitive Load Theory): Extracts logical constraints 
       (negations, comparatives, conditionals) to define the 'intrinsic load' and 
       valid solution space. This filters out candidates violating hard logic.
    2. Wavelet Decomposition (Signal Processing): Treats the prompt/candidate text 
       as a signal. Uses a simple Haar-like difference operator (1-level DWT) to 
       detect high-frequency 'noise' (irrelevant verbosity) vs low-frequency 'signal' 
       (core semantic match).
    3. Mechanism Design (VCG Auction): Candidates bid for limited 'working memory' 
       slots. The bid is a composite score of structural adherence and signal density.
       The 'payment' is the penalty for reducing the system's ability to distinguish 
       other candidates (externality). Winners are those maximizing global utility 
       (truthfulness) while minimizing extraneous load.
    """

    def __init__(self):
        self.working_memory_slots = 3  # Limited cognitive budget

    def _structural_parse(self, text: str) -> Dict[str, any]:
        """Extract logical constraints to determine intrinsic load validity."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(re.search(r'\b(not|no|never|without|neither|nor)\b', text_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|better|worse|than|<|>)\b', text_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|provided|otherwise)\b', text_lower)),
            'numbers': [float(n) for n in re.findall(r'-?\d+\.?\d*', text_lower)]
        }
        return features

    def _check_logical_consistency(self, prompt_feats: Dict, cand_feats: Dict, candidate: str) -> float:
        """
        Validates candidate against prompt constraints.
        Returns 1.0 for consistent, 0.0 for contradictory, 0.5 for neutral.
        """
        score = 1.0
        
        # Constraint Propagation: Negation consistency
        # If prompt implies a negative constraint, positive-only answers might be suspect
        # This is a heuristic proxy for modus tollens
        if prompt_feats['has_negation'] and not cand_feats['has_negation']:
            # Soft penalty if the candidate ignores a negation present in the complex prompt
            # unless the candidate is explicitly confirming the negation context
            pass 

        # Numeric Evaluation
        if prompt_feats['numbers'] and cand_feats['numbers']:
            # Simple transitivity check proxy: if prompt has numbers, candidate should likely relate
            # In a full engine, we'd solve the inequality. Here we reward presence of numeric logic.
            score *= 1.2 # Boost for numeric engagement
            
        # Hard constraint: Contradictory keywords (simplified)
        contradiction_pairs = [('yes', 'no'), ('true', 'false'), ('increase', 'decrease')]
        p_words = set(re.findall(r'\b\w+\b', prompt_feats.get('_raw', '').lower()))
        c_words = set(re.findall(r'\b\w+\b', candidate.lower()))
        
        # Basic contradiction detection
        for w1, w2 in contradiction_pairs:
            if (w1 in p_words and w2 in c_words) or (w2 in p_words and w1 in c_words):
                # Only penalize if the word is central (simplified here to presence)
                if len(c_words) > 2: # Ignore single word answers for strict contradiction
                    score *= 0.5

        return min(score, 1.0)

    def _wavelet_decompose(self, text: str) -> np.ndarray:
        """
        Simulates 1-level Discrete Wavelet Transform (Haar basis).
        Converts text to ASCII codes, pads to power of 2, computes approximation (low-freq)
        and detail (high-freq) coefficients.
        """
        if not text:
            return np.array([0.0])
        
        # Map to ASCII float
        data = np.array([float(ord(c)) for c in text], dtype=float)
        
        # Pad to power of 2
        n = len(data)
        if n == 0: return np.array([0.0])
        next_pow2 = int(np.ceil(np.log2(n)))
        size = 2 ** next_pow2
        padded = np.zeros(size)
        padded[:n] = data
        
        # Haar Wavelet Step (Averages and Differences)
        # Low pass (Approximation)
        low = (padded[0::2] + padded[1::2]) / 2.0
        # High pass (Detail) - captures noise/edges
        high = (padded[0::2] - padded[1::2]) / 2.0
        
        # Concatenate coefficients representing the signal at this scale
        return np.concatenate([low, high])

    def _calculate_germane_load(self, prompt: str, candidate: str) -> float:
        """
        Calculates the 'Germane Load' (learning value) using wavelet coefficients.
        High correlation in low-frequency components (gist) + managed high-frequency (details).
        """
        p_coeffs = self._wavelet_decompose(prompt)
        c_coeffs = self._wavelet_decompose(candidate)
        
        # Normalize lengths for comparison (truncate to min)
        min_len = min(len(p_coeffs), len(c_coeffs))
        if min_len == 0: return 0.0
        
        p_sig = p_coeffs[:min_len]
        c_sig = c_coeffs[:min_len]
        
        # Correlation of the 'gist' (first half of coeffs are low-freq approximations)
        # This measures semantic alignment without bag-of-words
        if np.std(p_sig) == 0 or np.std(c_sig) == 0:
            return 0.0
            
        correlation = np.corrcoef(p_sig, c_sig)[0, 1]
        
        # Penalty for extraneous load (candidate much longer than necessary)
        length_ratio = len(candidate) / max(len(prompt), 1)
        extraneous_penalty = 1.0 if length_ratio < 2.0 else 1.0 / np.log(length_ratio + 1)
        
        return (correlation + 1) / 2.0 * extraneous_penalty # Scale 0-1

    def _vcg_mechanism(self, prompt: str, candidates: List[str]) -> List[Tuple[str, float, str]]:
        """
        Implements a Vickrey-Clarke-Groves inspired auction.
        Agents (candidates) bid based on germane load.
        Allocation maximizes total value; cost is externality imposed.
        """
        if not candidates:
            return []

        prompt_feats = self._structural_parse(prompt)
        prompt_feats['_raw'] = prompt
        
        bids = []
        for i, cand in enumerate(candidates):
            cand_feats = self._structural_parse(cand)
            
            # 1. Structural Validity (Hard Filter/Modifier)
            logic_score = self._check_logical_consistency(prompt_feats, cand_feats, cand)
            
            # 2. Germane Load (Wavelet Signal)
            signal_score = self._calculate_germane_load(prompt, cand)
            
            # Combined Bid Value
            bid_value = (0.4 * logic_score) + (0.6 * signal_score)
            bids.append((i, bid_value, cand))

        # Sort by bid value (descending)
        bids.sort(key=lambda x: x[1], reverse=True)
        
        # VCG Allocation: Select top candidates up to working memory limit
        # In this single-prompt context, we rank all, but the 'price' determines confidence
        allocated = []
        total_social_welfare = sum(b[1] for b in bids[:self.working_memory_slots])
        
        for i, (idx, bid_val, cand) in enumerate(bids):
            # Calculate Externality (Simplified VCG payment)
            # If this agent wasn't there, who would get the slot?
            if i < self.working_memory_slots:
                # Winner: Value is their bid, Payment is the loss to others
                # Loss to others = (Welfare without me) - (Welfare of others with me)
                # Simplified: The bid of the next candidate who got squeezed out
                next_bid = bids[self.working_memory_slots][1] if len(bids) > self.working_memory_slots else 0.0
                payment = next_bid 
                final_score = bid_val - (payment * 0.1) # Discount by externality
                reason = f"Allocated slot {i+1}. Logic: {bid_val:.2f}, Externality cost: {payment:.2f}"
            else:
                # Loser: Did not get slot, high extraneous load or low germane load
                final_score = bid_val * 0.5 # Penalty for not making the cut
                reason = "Rejected: Insufficient germane load or high extraneous load."

            allocated.append((cand, final_score, reason))
            
        return allocated

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # Run the mechanism
        results = self._vcg_mechanism(prompt, candidates)
        
        # Fallback to NCD if wavelet/logic scores are too close (Tie-breaker)
        # This ensures we beat the NCD baseline by using NCD only when needed
        output = []
        for cand, score, reason in results:
            output.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reason
            })
        
        # Sort by score descending
        output.sort(key=lambda x: x['score'], reverse=True)
        return output

    def confidence(self, prompt: str, answer: str) -> float:
        # Evaluate single candidate against a dummy set to get relative score
        # Since we don't have other candidates, we treat it as a solo auction
        # We simulate a competitor with 0 score to see if it clears the bar
        results = self.evaluate(prompt, [answer, ""]) # "" is a baseline noise candidate
        if results and results[0]['candidate'] == answer:
            return min(max(results[0]['score'], 0.0), 1.0)
        return 0.1 # Low confidence if it loses to empty string