import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool combining structural parsing, sparse dictionary learning (SAE-style),
    and sensitivity analysis to evaluate candidate answers.
    
    Mechanism:
    1. Parses prompts/candidates into atomic propositions (negations, comparatives, numbers).
    2. Uses a fixed, hand-crafted 'dictionary' of logical patterns (simulating SAE latent features)
       to encode propositions into sparse vectors.
    3. Scores candidates based on:
       - Structural alignment with the prompt (logic consistency).
       - Sensitivity robustness (stability under small perturbations).
       - NCD (as a tiebreaker only).
    """
    
    # Regex patterns for logical extraction
    PATTERNS = {
        'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
        'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.IGNORECASE),
        'conditional': re.compile(r'\b(if|then|unless|otherwise|provided)\b', re.IGNORECASE),
        'causal': re.compile(r'\b(because|causes|leads to|due to|therefore)\b', re.IGNORECASE),
        'temporal': re.compile(r'\b(before|after|first|last|then|next)\b', re.IGNORECASE),
        'numeric': re.compile(r'-?\d+(?:\.\d+)?'),
        'quantifier': re.compile(r'\b(all|some|many|few|every|each)\b', re.IGNORECASE)
    }

    def __init__(self):
        # Simulate a small learned dictionary D (k=5 latent features)
        # Rows: [negation, comparative, conditional, causal, numeric_density]
        # These represent disentangled pragmatic/semantic features
        self.D = np.array([
            [1.0, 0.0, 0.0, 0.0, 0.0], # Negation feature
            [0.0, 1.0, 0.0, 0.0, 0.0], # Comparative feature
            [0.0, 0.0, 1.0, 0.0, 0.0], # Conditional feature
            [0.0, 0.0, 0.0, 1.0, 0.0], # Causal feature
            [0.0, 0.0, 0.0, 0.0, 1.0]  # Numeric feature
        ], dtype=np.float64)
        self.k = 5 # Number of latent features
        self.lamb = 0.1 # Sparsity penalty

    def _extract_props(self, text: str) -> List[Tuple[str, tuple, int]]:
        """Parse text into atomic propositions: (predicate, args, polarity)"""
        props = []
        text_lower = text.lower()
        
        # Check polarity context (simple window)
        words = text_lower.split()
        
        # Extract Negations
        for m in self.PATTERNS['negation'].finditer(text):
            props.append(('negation', (m.group(),), -1))
            
        # Extract Comparatives
        for m in self.PATTERNS['comparative'].finditer(text):
            props.append(('comparative', (m.group(),), 1))
            
        # Extract Conditionals
        for m in self.PATTERNS['conditional'].finditer(text):
            props.append(('conditional', (m.group(),), 1))
            
        # Extract Causal
        for m in self.PATTERNS['causal'].finditer(text):
            props.append(('causal', (m.group(),), 1))
            
        # Extract Temporal
        for m in self.PATTERNS['temporal'].finditer(text):
            props.append(('temporal', (m.group(),), 1))

        # Extract Quantifiers
        for m in self.PATTERNS['quantifier'].finditer(text):
            props.append(('quantifier', (m.group(),), 1))

        # Extract Numerics
        nums = self.PATTERNS['numeric'].findall(text)
        if nums:
            # Store as a single numeric proposition per sentence chunk roughly
            props.append(('numeric', tuple(nums[:3]), 1)) # Limit args for simplicity
            
        return props

    def _encode_to_sparse(self, props: List[Tuple]) -> np.ndarray:
        """
        Encode propositions into a sparse latent vector z using hard thresholding.
        Simulates the SAE inference step: z = argmin ||x - Dz||^2 + lambda||z||_1
        """
        if not props:
            return np.zeros(self.k)
        
        # Aggregate raw counts into a feature vector x (simplified one-hot accumulation)
        # Order: neg, comp, cond, causal, numeric
        raw_counts = np.zeros(5)
        for pred, args, pol in props:
            idx_map = {'negation': 0, 'comparative': 1, 'conditional': 2, 'causal': 3, 'numeric': 4}
            if pred in idx_map:
                raw_counts[idx_map[pred]] += pol # Polarity affects count direction slightly
        
        # Normalize to prevent magnitude dominance
        if np.max(np.abs(raw_counts)) > 0:
            raw_counts = raw_counts / np.max(np.abs(raw_counts))
            
        # Hard thresholding simulation (simplified coordinate descent for this specific D)
        # Since D is identity-like in our synthetic setup, z ~ x, but sparsified
        z = np.copy(raw_counts)
        
        # Apply L1 penalty (soft thresholding)
        z = np.sign(z) * np.maximum(np.abs(z) - self.lamb, 0)
        
        return z

    def _compute_sensitivity(self, props: List[Tuple], epsilon: float = 0.1) -> float:
        """
        Compute sensitivity score S = ||J||_F.
        Perturb inputs and measure change in latent encoding.
        """
        if not props:
            return 0.0
            
        z_base = self._encode_to_sparse(props)
        total_dist = 0.0
        count = 0
        
        for i, (pred, args, pol) in enumerate(props):
            if pred == 'numeric' and args:
                # Perturb numeric values
                try:
                    original_val = float(args[0])
                    perturbed_args = (str(original_val + epsilon),) + args[1:]
                    new_props = props[:i] + [(pred, perturbed_args, pol)] + props[i+1:]
                    z_pert = self._encode_to_sparse(new_props)
                    total_dist += np.linalg.norm(z_pert - z_base)
                    count += 1
                except ValueError:
                    pass
            else:
                # Flip polarity for non-numeric
                new_pol = -1 if pol == 1 else 1
                new_props = props[:i] + [(pred, args, new_pol)] + props[i+1:]
                z_pert = self._encode_to_sparse(new_props)
                total_dist += np.linalg.norm(z_pert - z_base)
                count += 1
        
        if count == 0:
            return 0.0
            
        # Approximate Jacobian norm
        return total_dist / count

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib"""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        if min(len_s1, len_s2) == 0:
            return 1.0
        return (len_both - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Compute final score and reasoning string"""
        p_props = self._extract_props(prompt)
        c_props = self._extract_props(candidate)
        
        # 1. Structural Alignment (Dot product of sparse codes)
        z_p = self._encode_to_sparse(p_props)
        z_c = self._encode_to_sparse(c_props)
        
        # Alignment score: higher if candidate activates similar logical features
        # We want candidate to reflect the logical structure of the prompt
        alignment = np.dot(z_p, z_c) / (np.linalg.norm(z_p) * np.linalg.norm(z_c) + 1e-9)
        
        # 2. Sensitivity Analysis (Robustness)
        # We want low sensitivity for the candidate itself (stable meaning)
        # But we also want the candidate to be sensitive to the prompt's constraints?
        # Here we score based on the candidate's internal stability
        sens = self._compute_sensitivity(c_props)
        robustness_score = 1.0 - min(sens, 1.0) # Lower sensitivity = higher score
        
        # 3. Sparsity bonus (Interpretability)
        sparsity = np.count_nonzero(z_c) / self.k
        sparsity_score = sparsity # Higher sparsity (more active features) is better here as it implies engagement
        
        # Weighted combination
        # Alpha for alignment, Beta for robustness, Gamma for sparsity
        score = 0.5 * alignment + 0.3 * robustness_score + 0.2 * sparsity_score
        
        # Heuristic boost: If prompt has numbers and candidate has numbers, boost slightly
        p_has_num = any(p[0] == 'numeric' for p in p_props)
        c_has_num = any(p[0] == 'numeric' for p in c_props)
        if p_has_num and c_has_num:
            score += 0.1
            
        # Heuristic penalty: If prompt has negation but candidate doesn't (and isn't short)
        if any(p[0] == 'negation' for p in p_props):
            if not any(p[0] == 'negation' for p in c_props) and len(c_props) > 0:
                score -= 0.2

        reason = f"Alignment:{alignment:.2f}, Robustness:{robustness_score:.2f}, Sparsity:{sparsity:.2f}"
        return score, reason

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        base_scores = []
        
        # First pass: compute structural scores
        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            base_scores.append((cand, score, reason))
        
        # Find max structural score to determine if we need NCD tie-breaking
        max_struct_score = max([s[1] for s in base_scores]) if base_scores else 0
        threshold = max_struct_score - 0.05 # Tie breaker zone
        
        final_results = []
        for cand, score, reason in base_scores:
            final_score = score
            # Apply NCD only as tie-breaker for close calls
            if max_struct_score > 0 and abs(score - max_struct_score) < 0.01:
                ncd_val = self._ncd(prompt, cand)
                # NCD is distance, so lower is better. Convert to similarity boost.
                # This is a weak signal, so small weight
                final_score += (1.0 - ncd_val) * 0.01 
                reason += f" [NCD boost: {1.0-ncd_val:.2f}]"
            
            final_results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reason
            })
            
        # Sort descending by score
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1"""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score to 0-1 range roughly based on theoretical bounds
        # Alignment is -1 to 1, robustness 0-1, sparsity 0-1. Max ~1.5
        raw_score = res[0]['score']
        conf = max(0.0, min(1.0, (raw_score + 0.5) / 2.0))
        return conf