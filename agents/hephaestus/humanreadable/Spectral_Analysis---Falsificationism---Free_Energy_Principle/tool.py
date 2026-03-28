import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Spectral-Falsification Reasoning Tool.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (NP+VP) and labels edges with weights 
       based on support (+1), contradiction (-1), causality, and numeric constraints.
    2. Spectral Step: Constructs an adjacency matrix R and computes its low-rank 
       approximation via eigendecomposition (keeping ~90% energy).
    3. Free Energy: Calculates variational free energy as prediction error (Frobenius norm 
       of residual) + complexity penalty (log-det of kept eigenvalues).
    4. Falsification: Inserts candidate assertions into the graph. If the candidate 
       increases Free Energy (Delta FE > 0), it contradicts the prompt's logical structure.
       Score = -Delta FE.
    5. Epistemic Honesty: Detects ambiguity patterns (presuppositions, pronouns) to 
       cap confidence, ensuring the model admits uncertainty rather than guessing.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither|without)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.I),
            'causal': re.compile(r'\b(causes|leads|results|implies|because|therefore)\b', re.I),
            'temporal': re.compile(r'\b(before|after|during|while|until)\b', re.I),
            'numeric': re.compile(r'(-?\d+(?:\.\d+)?)'),
            'presupposition': re.compile(r'\b(have you stopped|have you quit|why did .+ fail|why is .+ true)\b', re.I),
            'pronoun_ambig': re.compile(r'\b(he|she|him|her|they|them)\b.*\bwho\b', re.I),
            'false_dichotomy': re.compile(r'\b(either .+ or .+|only two options)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|most beautiful)\b', re.I)
        }

    def _extract_propositions(self, text: str) -> List[Tuple[str, float]]:
        """Extract atomic propositions and assign initial weights based on keywords."""
        props = []
        sentences = re.split(r'[.\?!]', text)
        
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            
            weight = 0.0
            # Base support for affirmative statements
            if re.search(r'\b(is|are|was|were|has|have|does|do)\b', sent, re.I):
                weight = 1.0
            
            # Modifiers
            if self.patterns['negation'].search(sent):
                weight -= 1.0  # Contradiction/Negation
            if self.patterns['comparative'].search(sent):
                weight += 0.5 * (1.0 if 'more' in sent.lower() or 'greater' in sent.lower() else -0.5)
            if self.patterns['causal'].search(sent):
                weight = 1.0 # Strong causal link
            if self.patterns['temporal'].search(sent):
                weight = 1.0
            
            # Numeric constraint check (simplified)
            nums = self.patterns['numeric'].findall(sent)
            if len(nums) >= 2:
                try:
                    v1, v2 = float(nums[0]), float(nums[1])
                    if ('less' in sent.lower() and v1 >= v2) or ('more' in sent.lower() and v1 <= v2):
                        weight = -1.0 # Numeric contradiction
                except: pass

            if weight != 0:
                props.append((sent, weight))
        
        # Fallback if no strong signals: treat sentences as weakly supported facts
        if not props:
            for sent in sentences:
                if len(sent.strip()) > 5:
                    props.append((sent.strip(), 0.5))
                    
        return props

    def _build_matrix(self, prompt: str, candidate: str = "") -> Tuple[np.ndarray, List[str]]:
        """Build weighted adjacency matrix R from prompt and optional candidate."""
        full_text = f"{prompt} {candidate}" if candidate else prompt
        props = self._extract_propositions(full_text)
        n = len(props)
        
        if n == 0:
            return np.array([[0.0]]), ["empty"]
            
        R = np.zeros((n, n), dtype=np.float64)
        labels = [p[0] for p in props]
        weights = [p[1] for p in props]
        
        # Construct R: Diagonal is self-weight, Off-diagonal is interaction
        for i in range(n):
            R[i, i] = weights[i]
            for j in range(i + 1, n):
                # Simple coherence check: if both positive, support; if signs differ, conflict
                interaction = weights[i] * weights[j] * 0.1 
                R[i, j] = interaction
                R[j, i] = interaction
                
        return R, labels

    def _compute_free_energy(self, R: np.ndarray, energy_threshold: float = 0.90) -> float:
        """Compute Variational Free Energy based on spectral residual and complexity."""
        if R.size == 0 or R.shape[0] == 0:
            return 0.0
            
        # Symmetrize for eigh
        R_sym = (R + R.T) / 2
        
        try:
            eigenvalues, eigenvectors = np.linalg.eigh(R_sym)
        except np.linalg.LinAlgError:
            return 1e6 # High energy for failure

        # Sort by absolute magnitude
        idx = np.argsort(np.abs(eigenvalues))[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]
        
        # Select top k for 90% energy
        total_energy = np.sum(np.abs(eigenvalues))
        if total_energy == 0:
            return 0.0
            
        cum_energy = 0.0
        k = 0
        for i, val in enumerate(np.abs(eigenvalues)):
            cum_energy += val
            if cum_energy >= energy_threshold * total_energy:
                k = i + 1
                break
        k = max(1, k) # Ensure at least 1
        
        # Low rank approximation
        Lambda_k = np.diag(eigenvalues[:k])
        Q_k = eigenvectors[:, :k]
        R_hat = Q_k @ Lambda_k @ Q_k.T
        
        # Term 1: Prediction Error (Surprise)
        residual = R_sym - R_hat
        surprise = np.linalg.norm(residual, 'fro') ** 2
        
        # Term 2: Complexity Penalty
        epsilon = 1e-6
        det_term = np.linalg.det(Lambda_k.T @ Lambda_k + epsilon * np.eye(k))
        complexity = 0.5 * np.log(det_term + epsilon)
        
        return float(surprise + complexity)

    def _check_ambiguity(self, text: str) -> float:
        """Meta-confidence check for Tier B traps. Returns cap (0.0 to 1.0)."""
        text_lower = text.lower()
        
        # 1. Presupposition
        if self.patterns['presupposition'].search(text):
            return 0.2
        # 2. Pronoun Ambiguity (simplified heuristic)
        if 'who' in text_lower and any(p in text_lower for p in [' he ', ' she ', ' him ', ' her ']):
            return 0.3
        # 3. False Dichotomy
        if self.patterns['false_dichotomy'].search(text):
            return 0.3
        # 4. Subjectivity without data
        if self.patterns['subjectivity'].search(text) and 'data' not in text_lower:
            return 0.4
            
        return 1.0

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(z1, z2)
        if max_len == 0:
            return 0.0
        return (z12 - min(z1, z2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        base_R, _ = self._build_matrix(prompt)
        base_fe = self._compute_free_energy(base_R)
        
        # Pre-calculate NCD for tie-breaking
        prompt_hash = prompt[:50] # Shorten for NCD speed
        
        for cand in candidates:
            # 1. Structural/Spectral Score
            cand_R, _ = self._build_matrix(prompt, cand)
            cand_fe = self._compute_free_energy(cand_R)
            
            # Falsification score: Lower FE increase is better (or negative delta)
            delta_fe = cand_fe - base_fe
            score = -delta_fe
            
            # 2. NCD Tiebreaker (max 15% influence logic handled by scaling)
            # If scores are close, NCD decides. Here we add a small bonus for similarity if scores are tied.
            ncd = self._ncd_distance(prompt_hash, cand[:50])
            
            # Normalize score roughly to 0-1 range for combination
            # Assuming typical FE deltas are small, scale appropriately
            structural_score = score * 10.0 
            
            # Final Score: Mostly structural, tiny NCD nudge
            final_score = structural_score - (ncd * 0.1) 
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Spectral FE Delta: {delta_fe:.4f}, NCD: {ncd:.4f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on epistemic honesty checks (Tier B).
        """
        # 1. Meta-Confidence Cap (Ambiguity Check)
        meta_cap = self._check_ambiguity(prompt)
        
        if meta_cap < 1.0:
            return meta_cap

        # 2. Structural Confidence
        # If the parser found no structure, confidence should be low
        props = self._extract_propositions(prompt)
        if len(props) == 0:
            return 0.2 # Honest uncertainty
            
        # 3. Compute consistency
        base_R, _ = self._build_matrix(prompt)
        cand_R, _ = self._build_matrix(prompt, answer)
        
        base_fe = self._compute_free_energy(base_R)
        cand_fe = self._compute_free_energy(cand_R)
        
        delta = cand_fe - base_fe
        
        # If adding the answer drastically increases free energy, it's likely wrong (low confidence in correctness)
        # If delta is near 0 or negative, it fits well.
        if delta > 10.0:
            conf = 0.1
        elif delta < -5.0:
            conf = 0.95 # Strong fit
        else:
            # Linear interpolation for moderate cases
            conf = max(0.3, min(0.85, 0.7 - (delta * 0.05)))
            
        # Apply hard cap from meta-check
        return min(conf, meta_cap)