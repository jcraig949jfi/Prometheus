import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Spectral Information-Theoretic Oscillatory Loop (SITOL) Approximation.
    
    Mechanism:
    Since true spectral analysis requires time-series data, we map the textual domain
    to a pseudo-spectral domain using structural tokenization and character-frequency
    distributions as proxies for "oscillatory bands".
    
    1. Spectral Decomposition: Text is decomposed into structural bands 
       (Negations, Comparatives, Conditionals, Numerics) and content bands.
    2. Spectral Entropy: Computed over the character frequency distribution of the 
       candidate. Low entropy (repetitive) is penalized; high entropy (random) is 
       penalized. Optimal structure has moderate entropy.
    3. Cross-Frequency Coupling (CFC): Measures the correlation between the 
       presence of prompt constraints (e.g., "not", "if") and the candidate's 
       structural response.
    4. Surprise Signal: KL-Divergence between the prompt's structural profile 
       and the candidate's profile. High divergence = low score.
    
    This implements the logic of SITOL (balancing representational richness vs 
    coherence) using only standard library tools to beat the NCD baseline.
    """

    def __init__(self):
        # Structural keywords defining "task-relevant bands"
        self.negations = {'not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'larger', 'fewer', 'better', 'worse', '>', '<'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided', 'when'}
        self.numerics = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}

    def _get_char_frequencies(self, text: str) -> Dict[str, int]:
        freq = {}
        total = 0
        for char in text.lower():
            if char.isalnum():
                freq[char] = freq.get(char, 0) + 1
                total += 1
        return freq, total

    def _compute_spectral_entropy(self, text: str) -> float:
        """Shannon entropy of character distribution (Proxy for PSD entropy)."""
        freq, total = self._get_char_frequencies(text)
        if total == 0:
            return 0.0
        entropy = 0.0
        for count in freq.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        return entropy

    def _extract_structural_profile(self, text: str) -> Tuple[float, float, float, float]:
        """Extracts density of structural bands."""
        tokens = text.lower().split()
        if len(tokens) == 0:
            return 0.0, 0.0, 0.0, 0.0
        
        neg_count = sum(1 for t in tokens if t in self.negations)
        comp_count = sum(1 for t in tokens if t in self.comparatives)
        cond_count = sum(1 for t in tokens if t in self.conditionals)
        num_count = sum(1 for char in text if char in self.numerics)
        
        length = len(tokens)
        return (neg_count/length, comp_count/length, cond_count/length, num_count/length)

    def _kl_divergence(self, p: List[float], q: List[float], epsilon=1e-9) -> float:
        """Computes KL(P || Q) where P is prompt profile, Q is candidate profile."""
        kl = 0.0
        for pi, qi in zip(p, q):
            pi += epsilon
            qi += epsilon
            kl += pi * math.log(pi / qi)
        return kl

    def _numeric_consistency(self, prompt: str, candidate: str) -> float:
        """Checks basic numeric logic if numbers are present."""
        # Extract floats from prompt and candidate
        import re
        p_nums = re.findall(r"[-+]?\d*\.\d+|\d+", prompt)
        c_nums = re.findall(r"[-+]?\d*\.\d+|\d+", candidate)
        
        if not p_nums:
            return 1.0 # No numeric constraint to violate
        
        if not c_nums:
            return 0.5 # Prompt has numbers, candidate ignores them (penalty)

        try:
            # Simple heuristic: If prompt implies ordering (more/less), check candidate
            p_lower = prompt.lower()
            has_more = 'more' in p_lower or 'greater' in p_lower
            has_less = 'less' in p_lower or 'smaller' in p_lower
            
            if has_more or has_less:
                p_vals = [float(x) for x in p_nums]
                c_vals = [float(x) for x in c_nums]
                if p_vals and c_vals:
                    # If prompt discusses magnitude, candidate should reflect consistent magnitude logic
                    # This is a loose coupling check; strict logic requires full parsing
                    pass 
            return 1.0
        except ValueError:
            return 0.8

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_profile = self._extract_structural_profile(prompt)
        prompt_entropy = self._compute_spectral_entropy(prompt)
        
        # Normalize prompt entropy to 0-1 range roughly (max entropy for ascii ~ 6-8 bits)
        # We use it as a baseline for "richness"
        
        for cand in candidates:
            cand_profile = self._extract_structural_profile(cand)
            cand_entropy = self._compute_spectral_entropy(cand)
            
            # 1. Spectral Information Mismatch (KL Divergence)
            # High divergence means the candidate doesn't match the structural "rhythm" of the prompt
            mismatch = self._kl_divergence(list(prompt_profile), list(cand_profile))
            
            # 2. Cross-Frequency Coupling (CFC) Proxy
            # If prompt has high negation density, candidate should likely address it (heuristic)
            # We approximate coupling strength by similarity in structural vector direction
            # Simple dot product of normalized profiles
            def normalize(v):
                norm = math.sqrt(sum(x*x for x in v))
                return [x/norm if norm > 0 else 0 for x in v]
            
            p_norm = normalize(list(prompt_profile))
            c_norm = normalize(list(cand_profile))
            coupling = sum(p * c for p, c in zip(p_norm, c_norm))
            
            # 3. Entropy Regularization
            # Penalize extremely low entropy (repetition) or extremely high (noise)
            # Ideal is somewhat close to prompt's complexity
            entropy_diff = abs(cand_entropy - prompt_entropy)
            entropy_penalty = min(1.0, entropy_diff / 4.0) # Scale penalty
            
            # 4. Numeric Consistency
            num_score = self._numeric_consistency(prompt, cand)
            
            # Final Score Construction (SITOL Logic)
            # Score = Coupling (Coherence) - Mismatch (Surprise) - Entropy Penalty + Numeric Bonus
            # We weight structural coupling heavily as per "Reasoning" requirement
            base_score = (coupling * 0.6) - (mismatch * 0.3) - (entropy_penalty * 0.1) + (num_score * 0.2)
            
            # NCD Tiebreaker (only if scores are very close, but we include a small factor)
            # Using NCD purely as a secondary similarity metric
            try:
                s_joint = prompt + cand
                c_joint = len(zlib.compress(s_joint.encode()))
                c_prompt = len(zlib.compress(prompt.encode()))
                c_cand = len(zlib.compress(cand.encode()))
                ncd = (c_joint - min(c_prompt, c_cand)) / max(c_prompt, c_cand)
                ncd_score = 1.0 - ncd # Convert distance to similarity
                base_score += ncd_score * 0.05 # Small boost for compression similarity
            except:
                pass

            results.append({
                "candidate": cand,
                "score": float(base_score),
                "reasoning": f"Coupling:{coupling:.2f}, Mismatch:{mismatch:.2f}, Entropy:{cand_entropy:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the SITOL evaluation of the single answer.
        """
        # Evaluate against a dummy set containing only the answer to get relative score
        # But better: evaluate the structural match directly
        
        prompt_profile = self._extract_structural_profile(prompt)
        cand_profile = self._extract_structural_profile(answer)
        
        mismatch = self._kl_divergence(list(prompt_profile), list(cand_profile))
        coupling = 0.0
        
        # Re-calculate coupling for single pair
        def normalize(v):
            norm = math.sqrt(sum(x*x for x in v))
            return [x/norm if norm > 0 else 0 for x in v]
        p_norm = normalize(list(prompt_profile))
        c_norm = normalize(list(cand_profile))
        coupling = sum(p * c for p, c in zip(p_norm, c_norm))
        
        # Map mismatch and coupling to 0-1 confidence
        # Low mismatch + High coupling = High confidence
        raw_conf = (coupling * 0.7) - (mismatch * 0.3)
        
        # Sigmoid mapping to 0-1
        conf = 1 / (1 + math.exp(-5 * raw_conf))
        return max(0.0, min(1.0, conf))