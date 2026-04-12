import re
import math
import zlib
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A reasoning tool combining Ergodic Theory, Ecosystem Dynamics, and Free Energy Principle.
    
    Mechanism:
    1. Parsing: Extracts propositions (SVO triples), logical operators, and numeric values via regex.
    2. Interaction Matrix: Builds a weighted adjacency matrix where edges represent support, 
       contradiction, or causal links based on token overlap and logical consistency.
    3. Free Energy: Computes prediction error (how well a proposition is supported by others).
    4. Ergodic Consistency: Normalizes the matrix to find a stationary distribution (entropy).
    5. Ecosystem Stability: Approximates the Jacobian to find the leading eigenvalue (resilience).
    6. Scoring: Combines entropy, stability, and prediction error into a single score.
    
    Epistemic Honesty: Detects ambiguity, presuppositions, and unanswerable queries to cap confidence.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'triple': re.compile(r'(\w+)\s+(\w+ed?\s*\w*|\w+ing|\w+s)\s+(\w+)', re.IGNORECASE),
            'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|otherwise)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|leads to|causes|results in)\b', re.IGNORECASE),
            'numeric': re.compile(r'(-?\d+(?:\.\d+)?)\s*(%|kg|m|s|units)?'),
            'presupposition': re.compile(r'(have you stopped|why did|when did|who is the)', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either|or)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion)\b', re.IGNORECASE)
        }

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Extract structural features from text."""
        text_lower = text.lower()
        features = {
            'propositions': [],
            'negations': len(self.patterns['negation'].findall(text_lower)),
            'comparatives': len(self.patterns['comparative'].findall(text_lower)),
            'conditionals': len(self.patterns['conditional'].findall(text_lower)),
            'causal': len(self.patterns['causal'].findall(text_lower)),
            'numbers': [],
            'tokens': set(re.findall(r'\w+', text_lower))
        }
        
        # Extract numbers
        for match in self.patterns['numeric'].findall(text):
            try:
                features['numbers'].append(float(match[0]))
            except ValueError:
                pass
        
        # Simple SVO extraction (heuristic)
        # This is a simplified parser; real NLP would use spaCy/NLTK
        words = re.findall(r'\w+', text)
        for i in range(len(words) - 2):
            # Heuristic: Noun-Verb-Noun pattern approximation
            if i > 0 and i < len(words)-1:
                # Very rough heuristic for demo purposes
                if words[i].lower() in ['the', 'a', 'an'] or words[i+2].lower() in ['the', 'a', 'an']:
                     pass # Skip articles
                features['propositions'].append((words[i], words[i+1], words[i+2]))
                
        return features

    def _build_interaction_matrix(self, candidates: List[str]) -> Tuple[np.ndarray, List[Dict]]:
        """Build the weighted adjacency matrix W and store features."""
        n = len(candidates)
        if n == 0:
            return np.array([]), []
        
        features_list = [self._extract_features(c) for c in candidates]
        W = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    W[i, j] = 1.0
                    continue
                
                f_i = features_list[i]
                f_j = features_list[j]
                
                # Jaccard similarity on tokens
                intersection = len(f_i['tokens'] & f_j['tokens'])
                union = len(f_i['tokens'] | f_j['tokens'])
                jaccard = intersection / union if union > 0 else 0.0
                
                # Support edge: shared subject/predicate, no negation conflict
                # Simplified: High token overlap implies support unless negation count differs wildly
                neg_conflict = abs(f_i['negations'] - f_j['negations']) > 0
                
                if neg_conflict:
                    W[i, j] = -jaccard  # Contradiction
                else:
                    W[i, j] = jaccard   # Support
                
                # Causal boost
                if f_i['causal'] > 0 and f_j['causal'] > 0:
                    W[i, j] += 0.5
                
                # Numeric consistency
                if f_i['numbers'] and f_j['numbers']:
                    # Check if numbers are consistent (simple equality check for demo)
                    # If both have numbers, penalize difference
                    v_i = np.mean(f_i['numbers'])
                    v_j = np.mean(f_j['numbers'])
                    max_v = max(abs(v_i), abs(v_j), 1.0)
                    diff_penalty = abs(v_i - v_j) / max_v
                    W[i, j] -= diff_penalty

        return W, features_list

    def _compute_ergodic_entropy(self, W: np.ndarray) -> float:
        """Compute stationary distribution and entropy."""
        if W.size == 0:
            return 0.0
            
        # Make rows non-negative and normalize (Markov transition matrix)
        W_pos = np.maximum(W, 0)
        row_sums = W_pos.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1  # Avoid division by zero
        P = W_pos / row_sums
        
        # Power iteration for stationary distribution
        n = P.shape[0]
        pi = np.ones((n, 1)) / n
        for _ in range(50):  # Converge
            pi_new = P.T @ pi
            if np.linalg.norm(pi_new - pi) < 1e-6:
                break
            pi = pi_new
            
        # Normalize pi
        pi = pi / pi.sum()
        
        # Entropy H = -sum(pi log pi)
        epsilon = 1e-10
        H = -np.sum(pi * np.log(pi + epsilon))
        max_H = np.log(n) if n > 1 else 1.0
        return H / max_H if max_H > 0 else 0.0

    def _compute_ecosystem_stability(self, W: np.ndarray) -> float:
        """Compute leading eigenvalue magnitude of Jacobian approximation."""
        if W.size == 0 or W.shape[0] < 2:
            return 0.0
            
        # Jacobian approximation: J = W - diag(row_sums(W))
        # This mimics linear stability analysis in dynamical systems
        row_sums = W.sum(axis=1)
        J = W - np.diag(row_sums)
        
        try:
            eigvals = np.linalg.eigvals(J)
            lambda_max = np.max(np.abs(eigvals))
            # Normalize: smaller is more stable. Map to 0-1 range roughly.
            # If lambda_max is 0, stability is 1. If large, stability approaches 0.
            stability = 1.0 / (1.0 + lambda_max)
            return stability
        except np.linalg.LinAlgError:
            return 0.5

    def _compute_prediction_error(self, W: np.ndarray) -> float:
        """Compute mean prediction error."""
        if W.size == 0:
            return 1.0
        # e_i = 1 - max_j(W_ij) for off-diagonal
        # Normalize W to 0-1 for this calculation
        W_norm = np.copy(W)
        W_norm = (W_norm - W_norm.min()) / (W_norm.max() - W_norm.min() + 1e-9)
        
        errors = []
        for i in range(W_norm.shape[0]):
            row = W_norm[i, :]
            # Mask self
            row_masked = np.concatenate([row[:i], row[i+1:]]) if len(row) > 1 else np.array([0])
            max_support = np.max(row_masked) if len(row_masked) > 0 else 0
            errors.append(1.0 - max_support)
            
        return np.mean(errors) if errors else 1.0

    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presuppositions, and unanswerability."""
        p_lower = prompt.lower()
        score = 1.0
        
        # 1. Presupposition
        if self.patterns['presupposition'].search(p_lower):
            score = min(score, 0.2)
            
        # 2. False Dichotomy (heuristic)
        if 'either' in p_lower and 'or' in p_lower:
            # Check if it implies only two options without context
            if 'option' in p_lower or 'choice' in p_lower:
                score = min(score, 0.3)
                
        # 3. Subjectivity
        if self.patterns['subjectivity'].search(p_lower):
            score = min(score, 0.4)
            
        # 4. Pronoun ambiguity (very rough heuristic)
        if re.search(r'\b(he|she|it|they)\b', p_lower) and 'who' in p_lower:
            score = min(score, 0.3)
            
        return score

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        len1 = len(z(s1.encode()))
        len2 = len(z(s2.encode()))
        len12 = len(z((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len12 - min(len1, len2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Structural Analysis (Primary Signal)
        W, features_list = self._build_interaction_matrix(candidates)
        
        scores = []
        reasoning_logs = []
        
        if W.size > 0:
            # 2. Free Energy (Prediction Error)
            pred_error = self._compute_prediction_error(W)
            
            # 3. Ergodic Consistency (Entropy)
            entropy_norm = self._compute_ergodic_entropy(W)
            
            # 4. Ecosystem Stability
            stability = self._compute_ecosystem_stability(W)
            
            # 5. Combine Scores
            # High score = Low Entropy (coherent), High Stability, Low Prediction Error
            # Note: Entropy in ergodic theory here measures dispersion. 
            # Low entropy = high alignment.
            ergodic_score = 1.0 - entropy_norm
            
            composite_score = (ergodic_score + stability + (1.0 - pred_error)) / 3.0
            
            base_scores = [composite_score] * len(candidates)
            
            # Adjust individual candidate scores based on their specific connectivity
            # Candidates that are strongly supported by others get a boost
            if W.shape[0] > 1:
                support_vector = np.sum(W, axis=0) # Column sum = how much others support this
                max_support = np.max(support_vector)
                min_support = np.min(support_vector)
                range_support = max_support - min_support if max_support != min_support else 1.0
                normalized_support = (support_vector - min_support) / range_support
                base_scores = [float(s * 0.7 + norm * 0.3) for s, norm in zip(base_scores, normalized_support)]

            for i, c in enumerate(candidates):
                scores.append(base_scores[i])
                reasoning_logs.append(f"Structural coherence: {base_scores[i]:.3f}, Stability: {stability:.3f}")
        else:
            scores = [0.5] * len(candidates)
            reasoning_logs = ["No structural patterns detected."] * len(candidates)

        # 6. NCD Tiebreaker (Max 15% weight)
        # Compare candidate to prompt. Higher similarity (lower NCD) is slightly better if structural scores are close.
        final_scores = []
        prompt_rep = prompt[:500] # Limit length for NCD
        
        for i, c in enumerate(candidates):
            ncd_val = self._ncd_score(prompt_rep, c[:500])
            # NCD is 0 (identical) to ~1 (different). We want high score for low NCD.
            ncd_score = 1.0 - ncd_val
            
            # Blend: 85% structural, 15% NCD
            final_score = scores[i] * 0.85 + ncd_score * 0.15
            final_scores.append(final_score)

        # Rank and format
        results = []
        sorted_indices = np.argsort(final_scores)[::-1]
        
        for idx in sorted_indices:
            results.append({
                "candidate": candidates[idx],
                "score": float(final_scores[idx]),
                "reasoning": reasoning_logs[idx]
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt for ambiguity.
        """
        # 1. Meta-confidence check (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural match check
        # If no structural patterns found in prompt, confidence should be low
        features = self._extract_features(prompt)
        has_structure = (
            features['negations'] > 0 or 
            features['comparatives'] > 0 or 
            features['conditionals'] > 0 or 
            features['causal'] > 0 or
            len(features['numbers']) > 0
        )
        
        if not has_structure:
            # If no structure, rely heavily on meta_cap
            base_conf = 0.2 if meta_cap < 0.5 else 0.4
        else:
            # If structure exists, we can be more confident, but capped by meta
            base_conf = 0.75
            
        final_conf = min(base_conf, meta_cap)
        
        # Never return > 0.9 unless it's a pure calculation (hard to verify without exec)
        # Be conservative
        if final_conf > 0.9:
            final_conf = 0.9
            
        return float(np.clip(final_conf, 0.0, 1.0))