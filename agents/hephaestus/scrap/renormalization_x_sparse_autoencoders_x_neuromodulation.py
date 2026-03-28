import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a hierarchical, scale-adaptive sparse coding network with dopamine-like gain control.
    
    Mechanism:
    1. Renormalization (Scale): Analyzes prompt structure at multiple scales (char, word, clause).
       Penalties are applied if candidate complexity diverges from prompt complexity (RG flow).
    2. Sparse Autoencoders (Feature Matching): Simulates top-k sparse coding by extracting
       structural features (negations, comparatives, numerics, conditionals) and matching
       candidate features against prompt features. Only top-k matches contribute to the score.
    3. Neuromodulation (Gain Control): Calculates a 'surprise' metric (prediction error based on
       structural mismatch). High surprise increases gain, loosening sparsity thresholds to allow
       more features to contribute, preventing false negatives on complex queries.
    
    This approach prioritizes structural parsing and numeric evaluation over raw string similarity.
    """

    def __init__(self):
        # Structural patterns for "sparse feature" extraction
        self.negation_patterns = [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b', r'\bexcept\b']
        self.comparative_patterns = [r'\bmore\b', r'\bless\b', r'\bgreater\b', r'\bsmaller\b', r'\b>\b', r'\b<\b', r'\bequal\b']
        self.conditional_patterns = [r'\bif\b', r'\bthen\b', r'\belse\b', r'\bunless\b', r'\bwhen\b']
        self.numeric_pattern = r'\d+\.?\d*'
        
        # Hyperparameters
        self.top_k = 5  # Sparsity level for feature matching
        self.base_sparsity_threshold = 0.5
        self.gain_scale = 2.0

    def _extract_features(self, text: str) -> Dict[str, List]:
        """Extracts structural features simulating a sparse autoencoder dictionary."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall('|'.join(self.negation_patterns), text_lower)),
            'comparatives': len(re.findall('|'.join(self.comparative_patterns), text_lower)),
            'conditionals': len(re.findall('|'.join(self.conditional_patterns), text_lower)),
            'numbers': [float(x) for x in re.findall(self.numeric_pattern, text)],
            'length': len(text),
            'word_count': len(text.split())
        }
        return features

    def _calculate_rg_penalty(self, prompt_feat: Dict, cand_feat: Dict) -> float:
        """
        Renormalization Group term: Penalizes scale mismatch.
        Ensures the effective dimensionality (complexity) of the answer matches the question scale.
        """
        penalty = 0.0
        
        # Scale 1: Numeric density
        p_num_density = len(prompt_feat['numbers']) / (prompt_feat['word_count'] + 1)
        c_num_density = len(cand_feat['numbers']) / (cand_feat['word_count'] + 1)
        penalty += abs(p_num_density - c_num_density) * 0.5
        
        # Scale 2: Logical operator density
        p_logic = (prompt_feat['negations'] + prompt_feat['conditionals']) / (prompt_feat['word_count'] + 1)
        c_logic = (cand_feat['negations'] + cand_feat['conditionals']) / (cand_feat['word_count'] + 1)
        penalty += abs(p_logic - c_logic) * 0.5
        
        return penalty

    def _calculate_surprise(self, prompt: str, candidate: str) -> float:
        """
        Calculates prediction error (surprise) based on structural mismatch.
        High surprise indicates the current coarse representation is insufficient.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        error = 0.0
        # Check negation consistency
        if p_feat['negations'] > 0 and c_feat['negations'] == 0:
            error += 0.5
        # Check numeric presence
        if len(p_feat['numbers']) > 0 and len(c_feat['numbers']) == 0:
            error += 0.5
        # Check conditional logic
        if p_feat['conditionals'] > 0 and c_feat['conditionals'] == 0:
            error += 0.3
            
        return min(error, 1.0)

    def _sparse_code_match(self, prompt: str, candidate: str, gain: float) -> float:
        """
        Simulates Top-K Sparse Autoencoder matching.
        Computes feature overlap, applies sparsity, modulated by gain.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        # Feature vector differences (simulating reconstruction error)
        diffs = []
        
        # Boolean feature matching (normalized)
        if p_feat['negations'] > 0:
            diffs.append(1.0 if c_feat['negations'] > 0 else 0.0)
        if p_feat['comparatives'] > 0:
            diffs.append(1.0 if c_feat['comparatives'] > 0 else 0.0)
        if p_feat['conditionals'] > 0:
            diffs.append(1.0 if c_feat['conditionals'] > 0 else 0.0)
            
        # Numeric evaluation
        if len(p_feat['numbers']) > 0 and len(c_feat['numbers']) > 0:
            # Check if numbers are logically consistent (simplified: presence helps)
            diffs.append(1.0) 
        elif len(p_feat['numbers']) == 0 and len(c_feat['numbers']) == 0:
            diffs.append(1.0) # Both lack numbers, consistent
        else:
            diffs.append(0.0) # Mismatch
            
        # Length/Complexity match (coarse scale)
        len_ratio = min(len(candidate), len(prompt)) / (max(len(candidate), len(prompt)) + 1)
        diffs.append(len_ratio)
        
        # Sparsity: Sort and take top-k contributions (simulating active neurons)
        # Higher gain allows more features to pass the threshold
        threshold = self.base_sparsity_threshold - (gain * 0.2) 
        active_features = [v for v in diffs if v >= threshold]
        
        if not active_features:
            return 0.0
            
        # Sum of top-k active features
        active_features.sort(reverse=True)
        return sum(active_features[:self.top_k]) / self.top_k

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        for cand in candidates:
            # 1. Calculate Surprise (Neuromodulation signal)
            surprise = self._calculate_surprise(prompt, cand)
            
            # 2. Apply Gain Control
            # High surprise -> High Gain -> Looser sparsity (recruit more features)
            gain = 1.0 + (surprise * self.gain_scale)
            
            # 3. Sparse Coding Match (Core reasoning score)
            sparse_score = self._sparse_code_match(prompt, cand, gain)
            
            # 4. Renormalization Penalty (Scale adaptation)
            p_feat = self._extract_features(prompt)
            c_feat = self._extract_features(cand)
            rg_penalty = self._calculate_rg_penalty(p_feat, c_feat)
            
            # 5. NCD Tiebreaker (Only if structural signals are weak or equal)
            ncd_val = self._ncd(prompt, cand)
            
            # Final Score Composition
            # Structural match is primary, RG penalty reduces score for scale mismatch
            # NCD is a minor modifier to break ties or penalize gibberish
            base_score = sparse_score * (1.0 - rg_penalty * 0.5)
            
            # Boost if NCD is very low (high similarity) and structural score is decent
            if ncd_val < 0.3 and base_score > 0.2:
                final_score = min(1.0, base_score + 0.1)
            else:
                final_score = base_score
                
            # Heuristic boost for exact keyword matches in reasoning tasks
            prompt_lower = prompt.lower()
            cand_lower = cand.lower()
            if ('yes' in cand_lower and 'yes' in prompt_lower) or \
               ('no' in cand_lower and 'no' in prompt_lower):
                final_score = max(final_score, 0.6)

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"SparseMatch:{sparse_score:.2f}, Gain:{gain:.2f}, RG_Pen:{rg_penalty:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the evaluation score."""
        # Re-use evaluate logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']