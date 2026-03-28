import numpy as np
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning evaluator combining Renormalization (coarse-graining), 
    Optimal Control (dynamic programming alignment), and Pragmatics (Gricean penalties).
    
    Mechanism:
    1. Parse sentences into feature vectors [negation, comparative, numeric, causal, quantifier].
    2. Renormalize: Coarse-grain features from token to sentence scale via averaging.
    3. Optimal Control: Compute minimal cost path (Edit Distance) between Reference and Candidate
       feature sequences, where transition costs include pragmatic penalties.
    4. Score: Exponential decay of normalized minimal cost.
    """
    
    # Keywords for feature extraction
    NEG_WORDS = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere', 'cannot', "n't"}
    COMP_WORDS = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse', 'than', 'compare'}
    CAUSAL_WORDS = {'because', 'therefore', 'thus', 'hence', 'since', 'so', 'consequently', 'due'}
    QUANT_WORDS = {'all', 'some', 'every', 'each', 'few', 'many', 'most', 'any', 'both', 'either', 'neither'}
    NUM_PATTERN = re.compile(r'-?\d+(?:\.\d+)?')

    def __init__(self):
        self.alpha_info = 0.5
        self.alpha_rel = 1.0
        self.alpha_man = 0.2
        self.lambda_ctrl = 0.5

    def _extract_features(self, text: str) -> List[np.ndarray]:
        """Parse text into a sequence of 5D feature vectors per word."""
        words = re.findall(r'\w+', text.lower())
        if not words:
            return [np.zeros(5)]
        
        features = []
        for word in words:
            f = np.zeros(5)
            # 0: Negation
            if word in self.NEG_WORDS or (word.endswith("n't")):
                f[0] = 1.0
            # 1: Comparative
            if word in self.COMP_WORDS:
                f[1] = 1.0
            # 2: Numeric (log-scaled value if present, else 0)
            num_match = self.NUM_PATTERN.search(word)
            if num_match:
                val = float(num_match.group())
                f[2] = np.log1p(abs(val)) * np.sign(val) # Log scale with sign
            # 3: Causal
            if word in self.CAUSAL_WORDS:
                f[3] = 1.0
            # 4: Quantifier
            if word in self.QUANT_WORDS:
                f[4] = 1.0
            
            features.append(f)
        
        return features if features else [np.zeros(5)]

    def _renormalize(self, features: List[np.ndarray], scale: int) -> List[np.ndarray]:
        """
        Coarse-grain features by averaging over windows of size 2^scale.
        Scale 0 = original tokens.
        """
        if scale == 0:
            return features
        
        window_size = 2 ** scale
        pooled = []
        for i in range(0, len(features), window_size):
            window = features[i:i+window_size]
            if window:
                pooled.append(np.mean(window, axis=0))
        return pooled if pooled else [np.zeros(5)]

    def _compute_pragmatic_penalty(self, ref_feats: List[np.ndarray], cand_feats: List[np.ndarray]) -> float:
        """
        Calculate Gricean maxims violation penalty based on feature mismatches.
        """
        if not ref_feats or not cand_feats:
            return 1.0
            
        ref_sum = np.sum(ref_feats, axis=0)
        cand_sum = np.sum(cand_feats, axis=0)
        
        # Quantity: Excess info (candidate has significantly more active features)
        info_excess = max(0, np.sum(cand_sum) - np.sum(ref_sum))
        
        # Relevance: Missing causal/quantifier flags present in reference
        # (Indices 3 and 4)
        rel_violation = 0.0
        if ref_sum[3] > 0 and cand_sum[3] == 0: rel_violation += 1.0 # Missing cause
        if ref_sum[4] > 0 and cand_sum[4] == 0: rel_violation += 1.0 # Missing quant
        
        # Manner: Disordered numeric magnitude (simplified check)
        manner_violation = 0.0
        if len(ref_feats) > 1 and len(cand_feats) > 1:
            # Check if numeric trend is inverted
            r_nums = [f[2] for f in ref_feats if f[2] != 0]
            c_nums = [f[2] for f in cand_feats if f[2] != 0]
            if r_nums and c_nums:
                if (r_nums[0] > r_nums[-1]) != (c_nums[0] > c_nums[-1]):
                    manner_violation = 0.5

        return (self.alpha_info * info_excess + 
                self.alpha_rel * rel_violation + 
                self.alpha_man * manner_violation)

    def _optimal_control_cost(self, ref_seq: List[np.ndarray], cand_seq: List[np.ndarray]) -> float:
        """
        Dynamic Programming (Edit Distance) with quadratic state cost and pragmatic penalty.
        State x_t = ref_feat - cand_feat.
        Cost = ||x||^2 + lambda * pragmatic_penalty
        """
        n, m = len(ref_seq), len(cand_seq)
        if n == 0 and m == 0: return 0.0
        if n == 0: return float('inf')
        if m == 0: return float('inf')

        # Precompute pragmatic penalty for the whole sequence pair as a context modifier
        # In a full implementation, this might be local, but global works for short texts
        prag_penalty = self._compute_pragmatic_penalty(ref_seq, cand_seq)
        
        # DP Table initialization
        # D[i][j] = min cost to align ref[:i] and cand[:j]
        D = np.zeros((n + 1, m + 1))
        
        # Base cases
        for i in range(1, n + 1):
            diff = np.linalg.norm(ref_seq[i-1]) ** 2
            D[i, 0] = D[i-1, 0] + diff + self.lambda_ctrl * prag_penalty
            
        for j in range(1, m + 1):
            diff = np.linalg.norm(cand_seq[j-1]) ** 2
            D[0, j] = D[0, j-1] + diff + self.lambda_ctrl * prag_penalty

        # Fill table
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                # State difference cost
                diff_vec = ref_seq[i-1] - cand_seq[j-1]
                state_cost = np.dot(diff_vec, diff_vec) # Quadratic cost
                
                # Costs
                c_sub = state_cost + self.lambda_ctrl * prag_penalty
                c_del = np.dot(ref_seq[i-1], ref_seq[i-1]) + self.lambda_ctrl * prag_penalty
                c_ins = np.dot(cand_seq[j-1], cand_seq[j-1]) + self.lambda_ctrl * prag_penalty
                
                D[i, j] = min(
                    D[i-1, j-1] + c_sub, # Substitute/Match
                    D[i-1, j] + c_del,   # Delete from Ref
                    D[i, j-1] + c_ins    # Insert from Cand
                )
        
        return D[n, m]

    def _get_hierarchy_score(self, ref_text: str, cand_text: str) -> float:
        """Compute score using multi-scale renormalization and optimal control."""
        ref_feats = self._extract_features(ref_text)
        cand_feats = self._extract_features(cand_text)
        
        if not ref_feats:
            return 0.0 if not cand_feats else 0.1
            
        total_cost = 0.0
        max_cost = 0.0
        scales = 3 # Levels 0, 1, 2
        
        for l in range(scales):
            ref_pool = self._renormalize(ref_feats, l)
            cand_pool = self._renormalize(cand_feats, l)
            
            cost = self._optimal_control_cost(ref_pool, cand_pool)
            total_cost += cost
            
            # Estimate max possible cost for normalization (rough upper bound)
            max_len = max(len(ref_pool), len(cand_pool))
            max_cost += max_len * 5.0 # 5 is max feature magnitude approx
            
        if max_cost == 0:
            return 1.0
            
        # Normalize and exponential decay
        normalized_cost = min(1.0, total_cost / (max_cost + 1e-6))
        return np.exp(-normalized_cost * 5.0) # Scaling factor for sensitivity

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            # Primary Signal: Structural/Logical alignment
            score = self._get_hierarchy_score(prompt, cand)
            
            # Fallback/Tiebreaker: NCD (Normalized Compression Distance)
            # Only used if structural signal is weak or for fine-grained sorting
            s_prompt = prompt.encode('utf-8')
            s_cand = cand.encode('utf-8')
            try:
                c_p = len(__import__('zlib').compress(s_prompt))
                c_c = len(__import__('zlib').compress(s_cand))
                c_pc = len(__import__('zlib').compress(s_prompt + s_cand))
                ncd = (c_pc - min(c_p, c_c)) / max(c_p, c_c, 1)
                # NCD is distance (0=same), convert to similarity
                ncd_score = 1.0 - ncd
            except:
                ncd_score = 0.5
                
            # Blend: Structural is primary, NCD is tiebreaker/modifier
            # If structural score is very low, NCD helps distinguish noise from relevant short answers
            final_score = 0.7 * score + 0.3 * ncd_score
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural alignment: {score:.4f}, NCD backup: {ncd_score:.4f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural alignment."""
        score = self._get_hierarchy_score(prompt, answer)
        return float(np.clip(score, 0.0, 1.0))