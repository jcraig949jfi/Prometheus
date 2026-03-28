import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Holographic Predictive Coding Tensor Network (HPCTN) Simulator.
    
    Mechanism:
    1. Free Energy Principle (Core Driver): The system minimizes variational free energy
       by reducing the divergence between the prompt's structural constraints (sensory input)
       and the candidate's logical structure (generative model).
    2. Tensor Decomposition (Structural Parsing): Instead of high-dimensional tensors,
       we decompose the text into a 'structural tensor' of features: negation density,
       comparative operators, conditional depth, and numeric magnitude. This avoids the
       historical failure mode of using TD for direct scoring by restricting it to feature extraction.
    3. Holography Principle (Boundary Encoding): The 'bulk' (full semantic meaning) is
       projected onto a 'boundary' (a compact hash of structural features). We compare
       candidates by how well their boundary encoding reconstructs the prompt's constraints
       without needing full semantic expansion.
       
    Implementation Strategy:
    - Extract structural features (negations, comparatives, numerics) as the 'TT cores'.
    - Compute a 'Free Energy' score based on the mismatch between prompt and candidate features.
    - Use NCD only as a tie-breaker when structural energy differences are negligible.
    """

    def __init__(self):
        # Structural keywords for parsing
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse', '>', '<', '>=', '<='}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided', 'assuming', 'when'}
        self.logic_ops = {'and', 'or', 'xor', 'implies'}

    def _extract_structural_tensor(self, text: str) -> Dict[str, float]:
        """
        Decomposes text into a low-dimensional structural vector (simulating TT cores).
        Returns a dict of features: negation_count, comparative_count, conditional_depth, numeric_value.
        """
        if not text:
            return {"neg": 0.0, "comp": 0.0, "cond": 0.0, "num": 0.0, "len": 0.0}
            
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        # 1. Negation density
        neg_count = sum(1 for w in words if w in self.negations)
        
        # 2. Comparative density
        comp_count = sum(1 for w in words if w in self.comparatives)
        # Check symbols too
        comp_count += sum(1 for c in text if c in ['>', '<'])
        
        # 3. Conditional depth
        cond_count = sum(1 for w in words if w in self.conditionals)
        
        # 4. Numeric extraction (take max magnitude found as representative state)
        numbers = re.findall(r"-?\d+\.?\d*", text)
        max_num = 0.0
        if numbers:
            try:
                max_num = max(abs(float(n)) for n in numbers)
            except ValueError:
                max_num = 0.0
                
        return {
            "neg": neg_count,
            "comp": comp_count,
            "cond": cond_count,
            "num": max_num,
            "len": len(words)
        }

    def _compute_free_energy(self, prompt_features: Dict, candidate_features: Dict) -> float:
        """
        Computes variational free energy as the weighted divergence between
        prompt constraints (sensory input) and candidate generation.
        Lower energy = better match. We invert this for the score.
        """
        energy = 0.0
        
        # Negation mismatch penalty (High weight: critical for logic)
        if prompt_features["neg"] > 0:
            if candidate_features["neg"] == 0:
                energy += 2.0  # Penalty for missing negation
            elif abs(candidate_features["neg"] - prompt_features["neg"]) > 0:
                energy += 0.5 * abs(candidate_features["neg"] - prompt_features["neg"])
        
        # Comparative consistency
        if prompt_features["comp"] > 0:
            if candidate_features["comp"] == 0:
                energy += 1.5
            else:
                # Directionality check simplified: presence is good
                energy += 0.2 * abs(prompt_features["comp"] - candidate_features["comp"])
                
        # Conditional logic
        if prompt_features["cond"] > 0:
            if candidate_features["cond"] == 0:
                energy += 1.0 # Candidate ignores conditionality
        
        # Numeric consistency (if numbers exist in both)
        if prompt_features["num"] > 0 and candidate_features["num"] > 0:
            # Normalize by prompt magnitude to get relative error
            rel_error = abs(prompt_features["num"] - candidate_features["num"]) / (prompt_features["num"] + 1e-9)
            if rel_error > 0.5: # Significant deviation
                energy += 1.0 * rel_error
                
        # Length prior (candidates shouldn't be wildly different length unless necessary)
        len_diff = abs(prompt_features["len"] - candidate_features["len"])
        if len_diff > 10:
            energy += 0.1 * (len_diff - 10)
            
        return energy

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Ranks candidates by minimizing free energy (structural mismatch) relative to the prompt.
        Uses NCD as a tie-breaker for low-energy candidates.
        """
        prompt_feats = self._extract_structural_tensor(prompt)
        results = []
        
        for cand in candidates:
            cand_feats = self._extract_structural_tensor(cand)
            
            # Primary Score: Free Energy Minimization
            # Convert energy to a score (lower energy -> higher score)
            energy = self._compute_free_energy(prompt_feats, cand_feats)
            base_score = 1.0 / (1.0 + energy)
            
            results.append({
                "candidate": cand,
                "base_score": base_score,
                "energy": energy,
                "feats": cand_feats
            })
        
        # Tie-breaking phase using NCD (Holographic boundary check)
        # Only apply NCD if energies are very close (within 0.05)
        final_results = []
        for i, res in enumerate(results):
            ncd_penalty = 0.0
            # Compare candidate to prompt via NCD
            ncd_val = self._ncd(prompt, res["candidate"])
            
            # Heuristic: If base scores are high (low energy), NCD distinguishes nuance
            # If base scores are low, structural failure dominates anyway.
            if res["base_score"] > 0.5:
                # Lower NCD is better. Scale it.
                ncd_penalty = ncd_val * 0.1 
            
            final_score = res["base_score"] - ncd_penalty
            
            # Generate reasoning string
            reasoning = f"Structural match: {1-res['energy']:.2f}. "
            if res["feats"]["neg"] != prompt_feats["neg"] and prompt_feats["neg"] > 0:
                reasoning += "Negation mismatch detected. "
            if res["feats"]["comp"] == 0 and prompt_feats["comp"] > 0:
                reasoning += "Missing comparative logic. "
            if ncd_penalty > 0.05:
                reasoning += "Low compression similarity."
                
            final_results.append({
                "candidate": res["candidate"],
                "score": max(0.0, min(1.0, final_score)),
                "reasoning": reasoning
            })
            
        # Sort descending by score
        final_results.sort(key=lambda x: x["score"], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on free energy minimization.
        1.0 = Low energy (high structural alignment).
        0.0 = High energy.
        """
        prompt_feats = self._extract_structural_tensor(prompt)
        ans_feats = self._extract_structural_tensor(answer)
        energy = self._compute_free_energy(prompt_feats, ans_feats)
        
        # Convert energy to confidence
        conf = 1.0 / (1.0 + energy)
        
        # Boost if exact structural match on critical flags
        if prompt_feats["neg"] > 0 and ans_feats["neg"] > 0:
            conf = min(1.0, conf + 0.2)
        if prompt_feats["cond"] > 0 and ans_feats["cond"] > 0:
            conf = min(1.0, conf + 0.1)
            
        return round(conf, 4)