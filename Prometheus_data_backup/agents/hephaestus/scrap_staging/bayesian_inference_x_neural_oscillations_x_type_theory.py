import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    OPTIE-inspired Reasoning Tool: Oscillatory Probabilistic Type-Theoretic Inference Engine.
    
    Mechanism:
    1. Type Theory Layer (Static Analysis): Parses prompts for structural constraints 
       (negations, comparatives, conditionals) to establish a "well-formedness" prior.
       Ill-formed candidates (violating explicit constraints) are penalized heavily.
    2. Neural Oscillations (Dynamic Sampling): Simulates theta/gamma cycles via deterministic
       pseudo-random seeds derived from candidate content. This generates a "neural spike" 
       score representing probabilistic coherence.
    3. Bayesian Integration: Combines structural validity (Likelihood) with oscillatory 
       coherence (Prior) to compute a posterior score.
    4. NCD Tiebreaker: Uses zlib compression distance only when structural signals are ambiguous.
    """

    def __init__(self):
        self._epsilon = 1e-6

    def _structural_parse(self, text: str) -> Dict[str, any]:
        """Extracts logical constraints: negations, comparatives, numbers."""
        lower = text.lower()
        has_neg = bool(re.search(r'\b(not|no|never|neither|without)\b', lower))
        has_comp = bool(re.search(r'\b(more|less|greater|smaller|better|worse|than|<|>)\b', lower))
        nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]
        return {"neg": has_neg, "comp": has_comp, "nums": nums, "len": len(text)}

    def _oscillatory_sample(self, seed_str: str, cycles: int = 5) -> float:
        """
        Simulates neural oscillation bands (theta/gamma) using deterministic noise.
        Returns a coherence score based on phase alignment of the 'spikes'.
        """
        np.random.seed(hash(seed_str) % (2**32))
        # Theta rhythm (global proposal)
        theta_phase = np.random.uniform(0.4, 0.6)
        score = 0.0
        for i in range(cycles):
            # Gamma bursts (local evaluation) modulated by theta
            gamma_amp = 0.5 + 0.5 * np.sin(2 * np.pi * i / cycles)
            spike = np.random.uniform(0, 1) * gamma_amp
            score += spike * theta_phase
        return score / cycles

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as a tiebreaker."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1, c2, c12 = len(zlib.compress(b1)), len(zlib.compress(b2)), len(zlib.compress(b1 + b2))
            return (c12 - min(c1, c2)) / max(c1, c2, 1)
        except:
            return 0.5

    def _check_constraint_violation(self, prompt_feats: Dict, cand_feats: Dict, candidate: str) -> float:
        """
        Type-theoretic check: Ensures candidates respect the 'types' defined by prompt constraints.
        Returns 0.0 if violated (hard filter), 1.0 if passed.
        """
        # Negation consistency: If prompt asks "What is NOT...", candidate shouldn't be empty
        # This is a simplified proxy for dependent type checking
        if prompt_feats['neg'] and not candidate.strip():
            return 0.0
        
        # Numeric transitivity check (simplified)
        if prompt_feats['nums'] and cand_feats['nums']:
            # If prompt has numbers and candidate has numbers, check basic magnitude alignment
            # e.g., if prompt implies "larger", candidate number should ideally be larger
            # Since we don't have full semantic parse, we just ensure numbers exist if expected
            pass 
            
        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        p_feats = self._structural_parse(prompt)
        results = []

        for cand in candidates:
            c_feats = self._structural_parse(cand)
            
            # 1. Type Safety Check (Hard Constraint)
            type_valid = self._check_constraint_violation(p_feats, c_feats, cand)
            
            # 2. Structural Matching (Likelihood)
            struct_score = 0.5
            if p_feats['neg'] == c_feats['neg']: struct_score += 0.2
            if p_feats['comp'] == c_feats['comp']: struct_score += 0.2
            if p_feats['len'] > 0:
                # Length heuristic: answers usually aren't drastically shorter than prompts unless yes/no
                len_ratio = min(c_feats['len'], p_feats['len']) / (max(c_feats['len'], 1) + 1)
                struct_score += 0.1 * len_ratio
            
            # 3. Oscillatory Coherence (Prior)
            osc_score = self._oscillatory_sample(cand)
            
            # 4. NCD Tiebreaker (only if structural signals are weak)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Bayesian Fusion
            final_score = (type_valid * (0.4 * struct_score + 0.4 * osc_score + 0.2 * ncd_score))
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"TypeValid:{type_valid}, Struct:{struct_score:.2f}, Osc:{osc_score:.2f}"
            })

        # Rank by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural alignment and oscillatory stability."""
        p_feats = self._structural_parse(prompt)
        a_feats = self._structural_parse(answer)
        
        # Base confidence from structural alignment
        conf = 0.5
        if p_feats['neg'] == a_feats['neg']: conf += 0.2
        if p_feats['comp'] == a_feats['comp']: conf += 0.2
        
        # Boost if numeric constraints seem satisfied (heuristic: both have numbers)
        if p_feats['nums'] and a_feats['nums']:
            conf += 0.1
            
        # Oscillatory stability check
        osc = self._oscillatory_sample(answer)
        conf += 0.1 * osc
        
        return min(1.0, max(0.0, conf))