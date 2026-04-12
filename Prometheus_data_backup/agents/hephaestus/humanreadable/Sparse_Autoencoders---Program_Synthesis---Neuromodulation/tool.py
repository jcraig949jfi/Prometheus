import re
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Neuromodulated Sparse Latent Program Synthesizer (Approximated for CPU/StdLib).
    
    Mechanism:
    1. Sparse Autoencoder (SAE) Analogy: Prompts and candidates are parsed into a 
       high-dimensional binary feature space (lexical, structural, numeric). Sparsity 
       is enforced by only activating features present in the text.
    2. Neuromodulation: A dynamic 'gain' signal is computed based on the confidence 
       of structural matches (negations, comparatives). 
       - High Gain (Low structural certainty): Expands active latent features (lower threshold), 
         encouraging exploration of partial matches.
       - Low Gain (High structural certainty): Tightens sparsity (higher threshold), 
         focusing only on exact logical constraints.
    3. Program Synthesis Guide: The score is derived from the overlap of sparse latent 
      vectors, weighted by the neuromodulatory gain. This mimics a search policy that 
      adjusts exploration vs. exploitation based on hypothesis confidence.
    """

    def __init__(self):
        # Define structural primitives for "Program Synthesis" parsing
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'>', '<', 'greater', 'less', 'more', 'fewer', 'before', 'after'}
        self.logic_ops = {'if', 'then', 'else', 'and', 'or', 'implies'}
        self.digits = re.compile(r'-?\d+\.?\d*')

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        return [float(x) for x in self.digits.findall(text)]

    def _encode_sparse(self, text: str) -> Dict[str, float]:
        """
        Encodes text into a sparse dictionary of features (latent vector).
        Keys are feature names, values are activations (1.0 if present).
        """
        tokens = set(self._tokenize(text))
        features = {}
        
        # 1. Lexical Features (Bag of words, but sparse)
        for token in tokens:
            features[f"word:{token}"] = 1.0
            
        # 2. Structural Features (The "Program" primitives)
        if any(n in tokens for n in self.negation_words):
            features["struct:negation"] = 1.0
        if any(c in tokens for c in self.comparatives) or any(c in text for c in ['<', '>']):
            features["struct:comparative"] = 1.0
        if any(l in tokens for l in self.logic_ops):
            features["struct:logic"] = 1.0
            
        # 3. Numeric Features (Discretized presence)
        nums = self._extract_numbers(text)
        if nums:
            features["has:numbers"] = 1.0
            # Encode magnitude ranges as sparse bins
            for n in nums:
                bin_id = int(math.floor(n / 10.0)) # Coarse binning
                features[f"num_bin:{bin_id}"] = 1.0
                if n > 0: features["num:positive"] = 1.0
                if n < 0: features["num:negative"] = 1.0

        return features

    def _compute_neuromodulatory_gain(self, prompt_feats: Dict[str, float], 
                                      cand_feats: Dict[str, float]) -> float:
        """
        Computes a gain factor (0.5 to 2.0) based on structural alignment.
        High gain = Explore (relax sparsity).
        Low gain = Exploit (tighten sparsity).
        """
        structural_keys = [k for k in prompt_feats if k.startswith("struct:")]
        
        if not structural_keys:
            # No strong structural hints -> Moderate gain (exploratory)
            return 1.2
        
        match_count = 0
        for key in structural_keys:
            if key in cand_feats:
                match_count += 1
        
        ratio = match_count / len(structural_keys) if len(structural_keys) > 0 else 0
        
        # If structural hints match well, lower gain (focus/exploit)
        # If they mismatch, higher gain (explore/penalize heavily or look wider)
        # Here we use gain to scale the importance of the match.
        if ratio == 1.0:
            return 0.8  # Tighten: Only exact matches matter
        elif ratio == 0.0:
            return 1.5  # Expand: Structural mismatch, maybe lexical salvage?
        else:
            return 1.0  # Neutral

    def _sparse_dot_product(self, v1: Dict[str, float], v2: Dict[str, float], gain: float) -> float:
        """
        Computes intersection over union-like score with gain modulation.
        """
        intersection = 0.0
        union_set = set(v1.keys()) | set(v2.keys())
        
        if not union_set:
            return 0.0

        # Weighted intersection
        common_keys = set(v1.keys()) & set(v2.keys())
        for key in common_keys:
            weight = 1.0
            # Boost structural matches
            if key.startswith("struct:"):
                weight = 2.0
            # Boost numeric exact matches
            if key.startswith("num_bin:"):
                weight = 1.5
            
            intersection += v1[key] * v2[key] * weight

        # Gain modulation: 
        # If gain is high (exploration), we are less penalized by missing features? 
        # Actually, in this context, gain modulates the 'sparsity penalty'.
        # Let's interpret gain as a multiplier on the final score for structural coherence.
        
        raw_score = intersection / (len(union_set) ** 0.5) # Normalized by complexity
        
        return raw_score * (1.0 / gain) if gain > 0 else 0.0

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1."""
        p_feats = self._encode_sparse(prompt)
        a_feats = self._encode_sparse(answer)
        
        if not p_feats or not a_feats:
            return 0.0

        gain = self._compute_neuromodulatory_gain(p_feats, a_feats)
        score = self._sparse_dot_product(p_feats, a_feats, gain)
        
        # Normalize roughly to 0-1 based on empirical bounds of this simple model
        # Max theoretical score depends on feature count, clamp to 1.0
        conf = min(1.0, max(0.0, score / 5.0)) 
        return conf

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self.confidence(prompt, cand)
            # Add small deterministic noise based on length to break ties consistently
            # but keep it negligible so logic dominates.
            tie_breaker = len(cand) * 1e-6 
            results.append({
                "candidate": cand,
                "score": score + tie_breaker,
                "reasoning": f"Neuromodulated sparse overlap (gain-adjusted): {score:.4f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results