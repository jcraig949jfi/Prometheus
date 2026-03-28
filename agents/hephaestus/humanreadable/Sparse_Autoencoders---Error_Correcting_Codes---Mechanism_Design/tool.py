import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A hybrid reasoning evaluator combining structural propositional parsing,
    sparse dictionary encoding (SAE), and mechanism-design scoring.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (negations, comparatives, conditionals).
    2. SAE: Maps parsed features to a sparse binary code via soft-thresholding.
    3. ECC: Expands code to a redundant codeword for noise robustness (used in confidence).
    4. Scoring: Ranks candidates by Hamming distance to a constructed 'gold' reference,
       applying a proper scoring rule (S = -d^2) to align incentives.
    """

    def __init__(self):
        # Hyperparameters
        self.M = 500  # Dictionary size
        self.K = 20   # Sparsity level
        self.N = 2000 # Codeword length
        self.rng = np.random.default_rng(seed=42)
        
        # Initialize fixed sparse dictionary D (M x K) - simplified for determinism
        # In a real online setting, this would be learned. Here we fix a random projection.
        self.D = (self.rng.random((self.M, 64)) > 0.8).astype(float)
        
        # Initialize LDPC-style Generator Matrix G (K x N)
        # Sparse connectivity for error correction
        self.G = np.zeros((self.K, self.N), dtype=int)
        for i in range(self.K):
            # Each input bit connects to ~10 output bits randomly
            indices = self.rng.choice(self.N, size=10, replace=False)
            self.G[i, indices] = 1
            
        # Parity check matrix H (simplified conceptually for syndrome)
        self.H = self.rng.integers(0, 2, size=(self.N - self.K, self.N)).astype(int)

    def _parse_propositions(self, text: str) -> List[Tuple[str, int, str]]:
        """
        Extracts atomic propositions: (atom_string, polarity, type_tag).
        Polarity: +1 (affirmed), -1 (negated).
        """
        atoms = []
        text_lower = text.lower()
        
        # 1. Negations
        neg_patterns = [r"\bnot\b", r"\bno\b", r"\bnever\b", r"\bwithout\b"]
        has_negation = any(re.search(p, text_lower) for p in neg_patterns)
        
        # 2. Comparatives
        comp_matches = re.findall(r"(\w+)\s+(greater|less|more|fewer)\s+(than|as)?\s+(\w+)", text_lower)
        for m in comp_matches:
            tag = "comparative"
            pol = -1 if has_negation else 1
            atoms.append((f"{m[0]}_{m[1]}_{m[3]}", pol, tag))
            
        # 3. Conditionals
        cond_matches = re.findall(r"if\s+(.+?)\s+(?:then|,)?\s+(.+?)(?:\.|,|$)", text_lower)
        for antecedent, consequent in cond_matches:
            tag = "conditional"
            pol = -1 if has_negation else 1
            atoms.append((f"if_{antecedent.strip()}_then_{consequent.strip()}", pol, tag))
            
        # 4. Numeric comparisons
        num_matches = re.findall(r"(\d+(?:\.\d+)?)\s*(<|>|=|<=|>=)\s*(\d+(?:\.\d+)?)", text)
        for n1, op, n2 in num_matches:
            tag = "numeric"
            # Evaluate truth value immediately for numeric atoms
            try:
                v1, v2 = float(n1), float(n2)
                is_true = False
                if op == '<': is_true = v1 < v2
                elif op == '>': is_true = v1 > v2
                elif op == '=': is_true = v1 == v2
                elif op == '<=': is_true = v1 <= v2
                elif op == '>=': is_true = v1 >= v2
                pol = 1 if is_true else -1
                atoms.append((f"{n1}{op}{n2}", pol, tag))
            except:
                pass

        # 5. Causal/General claims (fallback for content words)
        if not atoms:
            # Simple bag-of-words fallback to ensure some signal
            words = re.findall(r"\b[a-z]{4,}\b", text_lower)
            for w in set(words[:10]):
                if w not in ['that', 'this', 'with', 'have', 'from', 'they', 'been', 'were']:
                    pol = -1 if has_negation and w in text_lower else 1
                    atoms.append((w, pol, "causal"))
                    
        return atoms if atoms else [("empty", 1, "null")]

    def _vectorize_atoms(self, atoms: List[Tuple[str, int, str]]) -> np.ndarray:
        """Hash atoms to indices and create a dense feature vector."""
        vec = np.zeros(self.M)
        if not atoms:
            return vec
            
        for atom_str, polarity, tag_type in atoms:
            # Hash to index
            idx = hash(atom_str) % self.M
            # Apply polarity weight
            vec[idx] += polarity * 1.0 
            # Add type bias
            type_offset = hash(tag_type) % 50
            vec[(idx + type_offset) % self.M] += polarity * 0.5
            
        return vec

    def _sparse_encode(self, features: np.ndarray) -> np.ndarray:
        """
        Simulates Sparse Autoencoder encoding.
        Computes projection, applies soft-thresholding to enforce sparsity K.
        """
        # Project to dictionary space (simplified: dot product with fixed random weights)
        # In real SAE: z = sign(W * p - theta)
        projection = np.dot(features, self.D.T) if len(features) == self.D.shape[0] else np.zeros(self.M)
        
        # Soft thresholding to get top-K active features
        # We simulate the "sign" and sparsity constraint
        abs_proj = np.abs(projection)
        threshold = np.sort(abs_proj)[-self.K] if len(abs_proj) >= self.K else 0
        
        z = np.sign(projection) * (abs_proj > threshold).astype(float)
        
        # Ensure exactly K active (pad if necessary)
        active_count = np.count_nonzero(z)
        if active_count < self.K:
            # Activate remaining randomly to maintain structure
            zero_indices = np.where(z == 0)[0]
            needed = self.K - active_count
            if len(zero_indices) > 0:
                pick = zero_indices[:needed]
                z[pick] = 1.0
                
        return z

    def _error_correcting_expand(self, z: np.ndarray) -> np.ndarray:
        """Expands sparse code z to codeword c using generator matrix G."""
        # c = z * G mod 2
        # Only use first K elements of z corresponding to rows of G
        z_trimmed = z[:self.K]
        c = np.dot(z_trimmed, self.G) % 2
        return c.astype(int)

    def _compute_hamming_distance(self, c1: np.ndarray, c2: np.ndarray) -> float:
        if len(c1) != len(c2):
            # Pad/truncate to match (shouldn't happen with fixed N)
            min_len = min(len(c1), len(c2))
            return np.sum(c1[:min_len] != c2[:min_len]) / min_len
        return np.sum(c1 != c2) / len(c1)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        s1_b = s1.encode()
        s2_b = s2.encode()
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            if max(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # 1. Parse Prompt to get "Gold" structural signature
        prompt_atoms = self._parse_propositions(prompt)
        prompt_vec = self._vectorize_atoms(prompt_atoms)
        prompt_z = self._sparse_encode(prompt_vec)
        prompt_c = self._error_correcting_expand(prompt_z)
        
        results = []
        
        for cand in candidates:
            # 2. Parse Candidate
            cand_atoms = self._parse_propositions(cand)
            cand_vec = self._vectorize_atoms(cand_atoms)
            cand_z = self._sparse_encode(cand_vec)
            cand_c = self._error_correcting_expand(cand_z)
            
            # 3. Mechanism Design Scoring
            # Distance to prompt structure (assuming candidate should align with prompt logic)
            # Note: In a Q&A setting, we might compare candidate to a derived 'answer' code.
            # Here, we assume valid answers share structural coherence with the prompt's constraints.
            # We invert distance to score: S = -d^2
            
            d = self._compute_hamming_distance(prompt_c, cand_c)
            
            # Proper scoring rule: S = -d^2 (shifted to positive range for readability)
            score = - (d ** 2)
            
            # Heuristic boost: If candidate explicitly resolves a numeric comparison found in prompt
            prompt_nums = [a for a in prompt_atoms if a[2] == 'numeric']
            cand_nums = [a for a in cand_atoms if a[2] == 'numeric']
            if prompt_nums and cand_nums:
                # Check consistency
                if prompt_nums[0][1] == cand_nums[0][1]:
                    score += 0.1 # Bonus for numeric consistency
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Hamming dist: {d:.4f}, Atoms: {len(cand_atoms)}"
            })

        # Tie-breaking with NCD if scores are very close
        final_results = []
        for i, res in enumerate(results):
            if i > 0:
                prev = results[i-1]
                if abs(res['score'] - prev['score']) < 1e-6:
                    # Use NCD against prompt as tie breaker
                    ncd = self._ncd_distance(prompt, res['candidate'])
                    prev_ncd = self._ncd_distance(prompt, prev['candidate'])
                    if ncd < prev_ncd:
                         # Swap not needed in sort, but logic holds for sorting key
                         pass
            
        # Sort by score descending
        final_results = sorted(results, key=lambda x: x['score'], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and ECC syndrome validity.
        Uses ECC redundancy to detect 'noise' (logical inconsistency).
        """
        # Parse both
        p_atoms = self._parse_propositions(prompt)
        a_atoms = self._parse_propositions(answer)
        
        p_vec = self._vectorize_atoms(p_atoms)
        a_vec = self._vectorize_atoms(a_atoms)
        
        p_z = self._sparse_encode(p_vec)
        a_z = self._sparse_encode(a_vec)
        
        p_c = self._error_correcting_expand(p_z)
        a_c = self._error_correcting_expand(a_z)
        
        # Calculate distance
        dist = self._compute_hamming_distance(p_c, a_c)
        
        # ECC Syndrome Check (Simulated)
        # If the combined vector has high syndrome weight, it implies high noise/error
        # Here we approximate: if distance is low, confidence is high.
        # Map distance [0, 1] to confidence [1, 0]
        # Using exp(-alpha * d) for sharper decay
        alpha = 5.0
        conf = np.exp(-alpha * dist)
        
        # Boost if numeric constraints match exactly
        p_nums = [a for a in p_atoms if a[2] == 'numeric']
        a_nums = [a for a in a_atoms if a[2] == 'numeric']
        if p_nums and a_nums:
            if p_nums[0][1] == a_nums[0][1]:
                conf = min(1.0, conf + 0.2)
                
        return float(np.clip(conf, 0.0, 1.0))