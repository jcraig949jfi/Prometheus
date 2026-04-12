import numpy as np
import zlib
import re
from collections import Counter

class ReasoningTool:
    """
    Energy-Based Sparse Compositional Autoencoder (ESCA) Approximation.
    
    Mechanism:
    1. Thermodynamics (Energy): Defines an energy function E = Reconstruction_Error + Sparsity_Cost - Entropy.
       Lower energy implies a more stable, plausible hypothesis.
    2. Sparse Autoencoders: Simulates sparsity by tokenizing text and penalizing high-frequency, 
       non-discriminative tokens (common words) while rewarding rare, specific tokens (sparse features).
    3. Compositionality: Uses a rule-based parser to detect logical structures (negations, comparatives).
       It constructs a 'grammar tree' score based on the presence of logical operators and numeric consistency.
    
    The final score is derived from the negative exponential of the computed energy, normalized.
    """

    def __init__(self):
        # Common stop-words act as high-energy noise in our sparse coding analogy
        self.stop_words = set(["the", "a", "an", "is", "are", "was", "were", "be", "been", "being", 
                               "have", "has", "had", "do", "does", "did", "will", "would", "could", 
                               "should", "may", "might", "must", "shall", "can", "need", "dare", 
                               "ought", "used", "to", "of", "in", "for", "on", "with", "at", "by", 
                               "from", "as", "into", "through", "during", "before", "after", "above", 
                               "below", "between", "under", "again", "further", "then", "once", "here", 
                               "there", "when", "where", "why", "how", "all", "each", "few", "more", 
                               "most", "other", "some", "such", "no", "nor", "not", "only", "own", 
                               "same", "so", "than", "too", "very", "just", "and", "but", "if", "or", 
                               "because", "until", "while", "this", "that", "these", "those", "it", "its"])
        
        # Logical operators for compositional parsing
        self.negations = ["no", "not", "never", "none", "neither", "nobody", "nothing", "nowhere"]
        self.comparatives = ["greater", "less", "more", "fewer", "higher", "lower", "better", "worse"]
        self.conditionals = ["if", "then", "else", "unless", "provided"]

    def _tokenize(self, text):
        """Simple tokenizer: lowercase, remove non-alphanumeric, split."""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s\.\-]', ' ', text)
        return [t for t in text.split() if t]

    def _compute_sparsity_cost(self, tokens):
        """
        Simulates L1 penalty on latent features.
        Rare tokens (low frequency in corpus of prompt+candidates) are 'sparse features' (low cost).
        Common tokens are 'dense noise' (high cost).
        """
        if not tokens:
            return 1.0
        
        counts = Counter(tokens)
        total = len(tokens)
        cost = 0.0
        
        # Entropy-like term: H(z) = -sum(p log p)
        # We want High Entropy (diverse usage) to Lower Energy.
        # So we subtract entropy from the cost.
        
        freq_dist = [c / total for c in counts.values()]
        entropy = -sum(p * np.log2(p + 1e-9) for p in freq_dist)
        
        # Sparsity penalty: Penalize presence of stop-words heavily
        sparse_penalty = 0.0
        for t in tokens:
            if t in self.stop_words:
                sparse_penalty += 0.5  # High energy for common words
            elif t.isdigit():
                sparse_penalty += 0.1  # Low energy for numbers (specific)
            else:
                sparse_penalty += 0.2  # Medium energy for content words
        
        # Normalize by length to avoid bias towards long answers
        avg_sparsity = sparse_penalty / len(tokens)
        
        # Free Energy component: E = U - TS (Here: Sparsity - Beta*Entropy)
        # Minimizing E means minimizing sparsity cost and maximizing entropy
        return avg_sparsity - 0.1 * entropy

    def _compute_compositional_score(self, text):
        """
        Grammar-guided decoder simulation.
        Checks for logical consistency markers.
        """
        tokens = self._tokenize(text)
        score = 0.0
        
        # Detect negation scope (simplified)
        has_neg = any(n in tokens for n in self.negations)
        has_comp = any(c in tokens for c in self.comparatives)
        has_cond = any(c in tokens for c in self.conditionals)
        
        # Reward structural complexity (compositionality)
        if has_neg: score += 0.2
        if has_comp: score += 0.2
        if has_cond: score += 0.2
        
        # Numeric consistency check (heuristic)
        numbers = [float(t) for t in tokens if t.replace('.', '').isdigit() and '.' in t or t.isdigit()]
        if len(numbers) >= 2:
            # If numbers exist, check if they are used in a comparative context if comparatives exist
            if has_comp:
                score += 0.3 # Boost if numbers and comparatives co-occur
                
        return score

    def _compute_reconstruction_error(self, prompt, candidate):
        """
        Approximates ||x - decoder(z)||^2 using NCD.
        If candidate is a good compression of the 'truth' implied by prompt, NCD is low.
        """
        s1 = prompt.encode('utf-8')
        s2 = candidate.encode('utf-8')
        
        try:
            c1 = len(zlib.compress(s1))
            c2 = len(zlib.compress(s2))
            c12 = len(zlib.compress(s1 + s2))
            
            # Normalized Compression Distance
            ncd = (c12 - min(c1, c2)) / max(c1, c2)
            return ncd
        except:
            return 1.0

    def _calculate_energy(self, prompt, candidate):
        """
        E(z) = Reconstruction_Error + lambda * Sparsity_Cost - Beta * Compositional_Score
        Lower energy = Better hypothesis.
        """
        tokens = self._tokenize(candidate)
        
        # Thermodynamic terms
        recon_err = self._compute_reconstruction_error(prompt, candidate)
        sparse_cost = self._compute_sparsity_cost(tokens)
        
        # Compositional terms (act as negative energy / stability boosters)
        comp_score = self._compute_compositional_score(candidate)
        
        # Weighted sum (Free Energy approximation)
        # Lambda (sparsity weight) = 0.4
        # Beta (composition weight) = 0.5
        energy = recon_err + 0.4 * sparse_cost - 0.5 * comp_score
        
        return energy

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
        
        results = []
        energies = []
        
        # Calculate energy for all candidates
        for cand in candidates:
            e = self._calculate_energy(prompt, cand)
            energies.append(e)
        
        # Convert to scores (Boltzmann distribution analogy: P ~ exp(-E))
        # Shift energies to be positive for stability
        min_e = min(energies)
        shifted_energies = [e - min_e + 1e-6 for e in energies]
        
        # Invert: Lower energy -> Higher score
        # Score = 1 / (1 + Energy) to keep it bounded and deterministic
        scores = [1.0 / (1.0 + e) for e in shifted_energies]
        
        # Normalize scores to 0-1 range roughly
        max_s = max(scores)
        if max_s > 0:
            scores = [s / max_s for s in scores]
            
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": float(scores[i]),
                "reasoning": f"Energy={energies[i]:.4f}, SparseCost={self._compute_sparsity_cost(self._tokenize(cand)):.4f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on the inverse energy of the single answer.
        0 = definitely wrong (high energy), 1 = definitely correct (low energy).
        """
        energy = self._calculate_energy(prompt, answer)
        # Map energy to 0-1. 
        # Heuristic: Energy < 0.2 is very confident, > 1.0 is low confidence.
        # Using a sigmoid-like mapping: 1 / (1 + exp(k * (E - threshold)))
        # Simplified to linear inverse for determinism and simplicity within bounds
        conf = 1.0 / (1.0 + energy)
        return float(np.clip(conf, 0.0, 1.0))