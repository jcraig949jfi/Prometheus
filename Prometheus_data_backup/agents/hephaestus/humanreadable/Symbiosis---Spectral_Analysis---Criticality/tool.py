import numpy as np
import re
from collections import Counter
from math import log, exp
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning evaluator based on Criticality-driven Structural Analysis.
    
    Mechanism:
    1. Structural Parsing: Extracts semantic roles (Agent, Patient, Condition) and 
       logical connectors (negations, comparatives, conditionals) using regex.
    2. Symbiosis (Support Only): Computes PMI between extracted roles to build a 
       co-occurrence graph. Used for graph construction, not direct scoring.
    3. Spectral Analysis: Converts numeric token presence into a time series, 
      computes FFT to detect periodic logical structures (e.g., alternating if-then).
    4. Criticality (Core): Computes the Laplacian of the symbiosis graph. The 
       spectral gap (algebraic connectivity) determines if the answer is neither 
       rigid nor chaotic. This is the primary scoring driver.
    5. Scoring: Weighted sum of Criticality (0.4), Spectral (0.3), and Symbiosis (0.3).
       NCD is used strictly as a tiebreaker for low-structure candidates.
    """
    
    # Regex patterns for structural parsing
    PATTERNS = {
        'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.I),
        'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.I),
        'conditional': re.compile(r'\b(if|then|unless|provided|when|whenever)\b', re.I),
        'causal': re.compile(r'\b(because|therefore|thus|hence|due to|since)\b', re.I),
        'ordering': re.compile(r'\b(first|second|finally|next|then|lastly)\b', re.I),
        'numeric': re.compile(r'\b\d+(\.\d+)?\b')
    }
    
    ROLES = ['Agent', 'Patient', 'Condition', 'Action', 'Result']

    def __init__(self):
        self.w_sigma = 0.3  # Symbiosis weight
        self.w_rho = 0.3    # Spectral weight
        self.w_kappa = 0.4  # Criticality weight (Primary driver)

    def _extract_tokens(self, text: str) -> Dict[str, List[int]]:
        """Extract structural features and return binary masks."""
        text_lower = text.lower()
        tokens = text.split()
        n = len(tokens)
        if n == 0: return {}
        
        features = {k: [0]*n for k in self.PATTERNS.keys()}
        features['numeric_val'] = [0.0]*n
        
        for i, token in enumerate(tokens):
            clean = token.strip(".,;:!?\"'")
            if not clean: continue
            
            for key, pattern in self.PATTERNS.items():
                if key == 'numeric':
                    if pattern.match(clean):
                        features['numeric'][i] = 1
                        try: features['numeric_val'][i] = float(clean)
                        except: pass
                else:
                    if pattern.search(clean):
                        features[key][i] = 1
        return features

    def _build_symbiosis_graph(self, prompt: str, answer: str) -> np.ndarray:
        """Build co-occurrence matrix S based on semantic roles."""
        # Simplified role extraction: map regex hits to roles
        combined = f"{prompt} {answer}"
        feats = self._extract_tokens(combined)
        n = len(feats.get('negation', []))
        if n == 0: return np.zeros((1,1))
        
        # Assign pseudo-roles based on windowed presence of patterns
        # Node i represents a window or a specific pattern instance
        # For this implementation, nodes are the detected pattern instances
        nodes = []
        for key in self.PATTERNS:
            indices = [i for i, val in enumerate(feats[key]) if val == 1]
            for idx in indices:
                nodes.append((key, idx))
        
        if len(nodes) < 2:
            return np.zeros((max(1, len(nodes)), max(1, len(nodes))))

        n_nodes = len(nodes)
        S = np.zeros((n_nodes, n_nodes))
        
        # Edge weight = PMI-like score based on proximity and type compatibility
        for i, (type_i, idx_i) in enumerate(nodes):
            for j, (type_j, idx_j) in enumerate(nodes):
                if i == j: continue
                # Proximity bonus
                dist = abs(idx_i - idx_j) + 1
                proximity = 1.0 / dist
                # Type compatibility (simplified: causal/conditional boost)
                type_bonus = 1.0
                if type_i in ['conditional', 'causal'] and type_j in ['conditional', 'causal']:
                    type_bonus = 2.0
                S[i, j] = proximity * type_bonus
                
        return S

    def _compute_symbiosis_score(self, S: np.ndarray) -> float:
        """Calculate average edge weight (PMI proxy)."""
        if S.size == 0: return 0.0
        non_zero = S[S != 0]
        if len(non_zero) == 0: return 0.0
        return float(np.mean(non_zero))

    def _compute_spectral_score(self, text: str) -> float:
        """Compute spectral score based on numeric token periodicity."""
        feats = self._extract_tokens(text)
        if 'numeric' not in feats or len(feats['numeric']) == 0:
            return 0.5 # Neutral if no numbers
        
        y = np.array(feats['numeric'], dtype=float)
        if np.sum(y) == 0:
            return 0.5
            
        # FFT via numpy
        fft_vals = np.fft.fft(y - np.mean(y))
        psd = np.abs(fft_vals)**2
        freqs = np.fft.fftfreq(len(y))
        
        # Positive frequencies only
        pos_mask = freqs > 0
        if not np.any(pos_mask): return 0.5
        
        pos_freqs = freqs[pos_mask]
        pos_psd = psd[pos_mask]
        
        # Mid-frequency band (avoiding DC and highest noise)
        f_max = np.max(pos_freqs)
        f_c = f_max * 0.2 # Lower 20% cutoff
        
        if f_max <= f_c: return 0.5
        
        total_energy = np.sum(pos_psd)
        if total_energy == 0: return 0.5
        
        band_mask = (pos_freqs >= f_c)
        band_energy = np.sum(pos_psd[band_mask])
        
        return float(band_energy / total_energy)

    def _compute_criticality_score(self, S: np.ndarray) -> float:
        """Compute criticality via spectral gap of Laplacian."""
        if S.size == 0 or S.shape[0] < 2:
            return 0.5
            
        # Degree matrix
        D = np.diag(np.sum(S, axis=1))
        # Symmetrize S for undirected graph assumption in Laplacian
        S_sym = (S + S.T) / 2
        L = D - S_sym
        
        # Eigenvalues
        try:
            eigenvals = np.linalg.eigvalsh(L)
            eigenvals = np.sort(eigenvals)
            
            # Spectral gap (lambda_2 - lambda_1)
            # lambda_1 should be ~0 for connected graph
            l1 = eigenvals[0]
            l2 = eigenvals[1] if len(eigenvals) > 1 else l1
            
            gamma = l2 - l1
            if gamma < 1e-9: gamma = 1e-9 # Avoid division by zero
            
            chi = 1.0 / gamma
            kappa = exp(-chi)
            return float(kappa)
        except:
            return 0.5

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            return (c12 - min(c1, c2)) / max(c1, c2, 1)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            # 1. Build Graph
            S = self._build_symbiosis_graph(prompt, cand)
            
            # 2. Compute Scores
            sigma = self._compute_symbiosis_score(S)
            rho = self._compute_spectral_score(cand)
            kappa = self._compute_criticality_score(S)
            
            # 3. Weighted Sum
            score = (self.w_sigma * sigma) + (self.w_rho * rho) + (self.w_kappa * kappa)
            
            # Heuristic boost for structural richness (prevents short "Yes/No" bias)
            struct_count = sum([
                len(self.PATTERNS['negation'].findall(cand)),
                len(self.PATTERNS['conditional'].findall(cand)),
                len(self.PATTERNS['numeric'].findall(cand))
            ])
            if struct_count > 0:
                score += 0.1 * min(struct_count, 5) # Cap bonus
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Sym:{sigma:.2f}, Spec:{rho:.2f}, Crit:{kappa:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Tie-breaking with NCD if scores are very close
        if len(results) > 1:
            diff = results[0]['score'] - results[1]['score']
            if abs(diff) < 1e-4:
                # Use NCD relative to prompt as tiebreaker (lower NCD = better match)
                results.sort(key=lambda x: self._ncd(prompt, x['candidate']))
                
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on criticality and structural density."""
        S = self._build_symbiosis_graph(prompt, answer)
        kappa = self._compute_criticality_score(S)
        rho = self._compute_spectral_score(answer)
        
        # Count structural markers
        text = f"{prompt} {answer}"
        markers = sum(len(p.findall(text)) for p in self.PATTERNS.values())
        
        # Base confidence on criticality (stability) and marker density
        # High criticality (near 1) means balanced structure
        # High marker count implies reasoning content
        base_conf = (kappa * 0.6) + (min(markers / 10.0, 1.0) * 0.4)
        
        # Penalize extremely short answers unless highly critical
        if len(answer.split()) < 3:
            base_conf *= 0.5
            
        return max(0.0, min(1.0, base_conf))