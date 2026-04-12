import re
import zlib
import math
import numpy as np

class ReasoningTool:
    """
    Wavelet-Boltzmann Multi-Scale Reasoning Engine (WB-MRE).
    
    Mechanism:
    This tool implements a computational analogy of the Wavelet-Boltzmann Machine.
    1. Wavelet Decomposition (MODWT analogy): The input text is parsed into a 
       multi-scale feature vector. Scales represent:
       - Scale 0 (Fast): Local lexical tokens (words).
       - Scale 1 (Medium): Structural operators (negations, comparatives, conditionals).
       - Scale 2 (Slow): Global numeric and logical constraints.
       
    2. Boltzmann Energy Function: Candidates are evaluated by an energy function:
       E = - (Structural_Alignment + Numeric_Consistency) + Noise_Penalty
       Lower energy (higher score) indicates a better fit. The "Hidden Units" are 
       latent logical consistency checks derived from the prompt's structural signature.
       
    3. Inference: Scores are derived from the negative energy (Free Energy approximation),
       normalized to [0, 1] for confidence.
    """

    def __init__(self):
        # Structural keywords defining the "regulatory motifs" of logic
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<', '>=', '<='}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided', 'when', 'only'}
        self.booleans = {'true', 'false', 'yes', 'no'}

    def _extract_numbers(self, text):
        """Extract floating point numbers for numeric evaluation."""
        pattern = r"[-+]?\d*\.?\d+"
        return [float(x) for x in re.findall(pattern, text)]

    def _wavelet_decompose(self, text):
        """
        Analogous to MODWT: Decomposes text into multi-scale features.
        Returns a dict of features at different 'scales'.
        """
        lower = text.lower()
        words = set(re.findall(r'\b\w+\b', lower))
        
        # Scale 0: Lexical presence
        has_bools = any(b in words for b in self.booleans)
        
        # Scale 1: Structural operators (The "Fast" dynamics)
        neg_count = sum(1 for w in words if w in self.negations)
        comp_count = sum(1 for w in words if w in self.comparatives or w in {'>', '<', '=', '>=', '<='})
        cond_count = sum(1 for w in words if w in self.conditionals)
        
        # Scale 2: Numeric trends (The "Slow" dynamics)
        numbers = self._extract_numbers(text)
        num_trend = 0
        if len(numbers) > 1:
            # Simple trend detection: is it increasing?
            diffs = [numbers[i+1] - numbers[i] for i in range(len(numbers)-1)]
            num_trend = sum(1 for d in diffs if d > 0) - sum(1 for d in diffs if d < 0)

        return {
            'neg': neg_count,
            'comp': comp_count,
            'cond': cond_count,
            'has_bool': int(has_bools),
            'num_trend': num_trend,
            'numbers': numbers,
            'length': len(text)
        }

    def _compute_energy(self, prompt_feat, cand_feat):
        """
        Computes the energy E(v, h) of the candidate given the prompt.
        Lower energy = Higher probability.
        Uses an Ising-like interaction between prompt structure and candidate structure.
        """
        energy = 0.0
        
        # Interaction 1: Numeric Consistency (Strong constraint)
        # If prompt has numbers, candidate should ideally relate or not contradict
        p_nums = prompt_feat['numbers']
        c_nums = cand_feat['numbers']
        
        if p_nums and c_nums:
            # Check for direct contradiction in simple comparisons if both have 2+ numbers
            # This is a simplified heuristic for the "Free Energy" difference
            if len(p_nums) >= 2 and len(c_nums) >= 2:
                p_diff = p_nums[1] - p_nums[0]
                c_diff = c_nums[1] - c_nums[0]
                if (p_diff > 0 and c_diff < 0) or (p_diff < 0 and c_diff > 0):
                    energy += 10.0 # High penalty for reversing trend
        
        # Interaction 2: Structural Alignment (Negation/Conditional matching)
        # If prompt has strong negation, candidate should reflect logical negation or absence
        # Heuristic: If prompt is complex (high struct), simple "Yes/No" might be insufficient unless aligned
        p_complexity = prompt_feat['neg'] + prompt_feat['comp'] + prompt_feat['cond']
        c_complexity = cand_feat['neg'] + cand_feat['comp'] + cand_feat['cond']
        
        # Penalty for complexity mismatch (Over-simplification of complex logic)
        if p_complexity > 2 and c_complexity == 0 and not cand_feat['has_bool']:
            energy += 2.0
            
        # Reward for matching negation counts roughly (proxy for logical consistency)
        if prompt_feat['neg'] > 0:
            if cand_feat['neg'] == 0:
                # Potential trap: Prompt says "not", candidate ignores it
                # Unless the answer is explicitly correcting it. 
                # We apply a small penalty for ignoring negation in short answers
                if cand_feat['length'] < 20: 
                    energy += 1.5

        # Regularization: Length penalty (Occam's razor) but not too harsh
        energy += 0.001 * cand_feat['length']
        
        return -energy # Return negative energy as score component

    def _ncd_distance(self, s1, s2):
        """Normalized Compression Distance as a tiebreaker."""
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

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        prompt_feat = self._wavelet_decompose(prompt)
        results = []
        
        # Pre-calculate NCD for tie-breaking
        # We want candidates close to prompt context, so lower NCD is better
        ncd_scores = []
        for cand in candidates:
            ncd_scores.append(self._ncd_distance(prompt, cand))
        
        min_ncd = min(ncd_scores) if ncd_scores else 0
        max_ncd = max(ncd_scores) if ncd_scores else 1
        ncd_range = max_ncd - min_ncd if (max_ncd - min_ncd) > 1e-9 else 1.0

        for i, cand in enumerate(candidates):
            cand_feat = self._wavelet_decompose(cand)
            
            # Primary Score: Structural/Energy based
            energy_score = self._compute_energy(prompt_feat, cand_feat)
            
            # Normalize energy roughly to [0, 5] range for combination
            # (Heuristic scaling based on penalty magnitudes defined in _compute_energy)
            norm_energy = max(0, 5 + energy_score) 
            
            # Tiebreaker: NCD (inverted so higher is better)
            # If energy scores are close, prefer lower NCD (higher similarity)
            ncd_norm = 1.0 - ((ncd_scores[i] - min_ncd) / ncd_range)
            
            # Final Score: Weighted sum. Structural reasoning dominates (90%), NCD tiebreaks (10%)
            final_score = 0.9 * (norm_energy / 5.0) + 0.1 * ncd_norm
            
            # Add small deterministic jitter based on index to ensure strict ordering if needed
            # but primarily rely on the physics-based score.
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Energy={energy_score:.2f}, NCD={ncd_scores[i]:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the energy gap between the answer 
        and a hypothetical 'null' answer.
        """
        # Evaluate against itself and a dummy alternative to gauge relative energy
        candidates = [answer, ""] 
        ranked = self.evaluate(prompt, candidates)
        
        if not ranked:
            return 0.0
            
        top = ranked[0]
        if top['candidate'] == answer:
            # It won. How much did it win by?
            if len(ranked) > 1:
                gap = top['score'] - ranked[1]['score']
                # Map gap to 0.5 - 1.0
                conf = 0.5 + min(0.5, gap * 2.0)
                return conf
            else:
                return 0.8 # Default high if no competition
        else:
            # It lost.
            return 0.2 # Default low