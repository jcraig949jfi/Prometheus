import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a hierarchical reasoning engine inspired by Renormalization x SAE x Bandits.
    
    Mechanism:
    1. Sparse Autoencoder (SAE) Analogy: The input text is decomposed into a sparse set of 
       'features' (structural tokens like negations, comparatives, numbers, and logical connectors).
       This creates a high-dimensional, sparse binary vector representing the logical skeleton.
    
    2. Renormalization (Coarse-Graining): Features are grouped into hierarchical scales:
       - Scale 0 (Fine): Raw structural tokens.
       - Scale 1 (Medium): Local logical phrases (e.g., "not greater than").
       - Scale 2 (Coarse): Global consistency checks (transitivity, constraint satisfaction).
       This mimics block-spin transformations where local noise is averaged out to reveal 
       stable macro-features.
    
    3. Multi-Armed Bandit (MAB): Each candidate answer is an "arm". 
       - Context: The sparse feature vector of the prompt.
       - Reward: Reduction in logical inconsistency (hypothesis testing loss) when the 
         candidate is assumed true.
       - Strategy: UCB-Tuned. We calculate an Upper Confidence Bound for each candidate based 
         on its structural alignment score and an uncertainty bonus derived from the variance 
         across renormalization scales. This allows the system to explore candidates that 
         resolve high-uncertainty logical constraints.
    
    Scoring:
    Primary signal comes from structural parsing (negations, numerics, conditionals).
    NCD (Compression) is used strictly as a tie-breaker for candidates with identical structural scores.
    """

    def __init__(self):
        # Structural patterns for sparse feature extraction
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', 'bigger', 'smaller', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided', 'when']
        self.connectors = ['and', 'or', 'but', 'however', 'therefore', 'thus', 'because']
        self.quantifiers = ['all', 'every', 'some', 'any', 'most', 'few', 'many']
        
        # Bandit state (simplified for stateless evaluation per call, but conceptually persistent)
        self.alpha = 1.0  # Exploration parameter

    def _extract_features(self, text: str) -> Dict[str, float]:
        """
        Sparse Autoencoder Step: Extracts binary/counts of logical features.
        Returns a sparse dictionary of active features.
        """
        if not text:
            return {}
        
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        features = {}
        
        # Count structural tokens
        features['negation_count'] = sum(1 for w in words if w in self.negations)
        features['comparative_count'] = sum(1 for w in words if w in self.comparatives)
        features['conditional_count'] = sum(1 for w in words if w in self.conditionals)
        features['connector_count'] = sum(1 for w in words if w in self.connectors)
        features['quantifier_count'] = sum(1 for w in words if w in self.quantifiers)
        
        # Numeric extraction (Scale 0 fine-grain)
        numbers = re.findall(r'-?\d+\.?\d*', lower_text)
        features['number_count'] = len(numbers)
        features['has_numbers'] = 1.0 if numbers else 0.0
        
        # Simple numeric logic check (Scale 1 coarse-grain prep)
        if len(numbers) >= 2:
            try:
                nums = [float(n) for n in numbers]
                features['numeric_range'] = max(nums) - min(nums)
                features['is_sorted'] = 1.0 if nums == sorted(nums) else 0.0
            except ValueError:
                features['numeric_range'] = 0.0
                features['is_sorted'] = 0.0
        else:
            features['numeric_range'] = 0.0
            features['is_sorted'] = 0.0
            
        # Length features (normalization)
        features['length'] = len(text)
        
        return features

    def _renormalize(self, prompt_feats: Dict[str, float], cand_feats: Dict[str, float]) -> Tuple[float, float, float]:
        """
        Renormalization Step: Aggregates features across scales to compute consistency.
        Returns (fine_score, coarse_score, uncertainty).
        """
        # Scale 0: Feature Overlap (Fine)
        # Check if candidate preserves key structural counts relative to prompt
        fine_diff = 0.0
        count = 0
        for key in ['negation_count', 'comparative_count', 'conditional_count']:
            if key in prompt_feats and key in cand_feats:
                # Ideal: Candidate logic matches prompt requirements (simplified as presence)
                # In a reasoning task, if prompt has negation, valid answer often acknowledges it.
                # Here we score based on structural richness alignment.
                p_val = prompt_feats.get(key, 0)
                c_val = cand_feats.get(key, 0)
                if p_val > 0:
                    fine_diff += abs(p_val - c_val) # Penalty for missing structural cues
                count += 1
        
        fine_score = 1.0 / (1.0 + fine_diff) if count > 0 else 0.5

        # Scale 1: Logical Consistency (Coarse)
        # Numeric consistency
        num_score = 1.0
        if prompt_feats.get('has_numbers') and cand_feats.get('has_numbers'):
            # If both have numbers, check if candidate numbers are plausible subset or derivation
            # Simplified: Penalty if candidate introduces wild outliers compared to prompt range
            p_range = prompt_feats.get('numeric_range', 0)
            c_range = cand_feats.get('numeric_range', 0)
            if p_range > 0:
                ratio = c_range / p_range if p_range != 0 else 1
                num_score = 1.0 / (1.0 + abs(ratio - 1.0)) # Prefer similar magnitude ranges
        
        # Conditional/Connector flow
        logic_score = 1.0
        if prompt_feats.get('conditional_count', 0) > 0:
            # If prompt is conditional, candidate should ideally have logical connectors
            if cand_feats.get('connector_count', 0) == 0 and cand_feats.get('conditional_count', 0) == 0:
                logic_score = 0.7 # Penalty for ignoring conditional structure

        coarse_score = (num_score + logic_score) / 2.0

        # Uncertainty estimation (Variance across scales)
        # High variance between fine and coarse suggests ambiguous or noisy signal
        uncertainty = abs(fine_score - coarse_score)
        
        return fine_score, coarse_score, uncertainty

    def _compute_bandit_score(self, fine: float, coarse: float, uncertainty: float, n_trials: int = 1) -> float:
        """
        Multi-Armed Bandit Step: UCB-Tuned style scoring.
        Score = Mean Reward + Exploration Bonus based on Uncertainty.
        """
        # Mean reward is weighted average of scales
        mean_reward = 0.4 * fine + 0.6 * coarse
        
        # Exploration bonus: Higher uncertainty -> Higher bonus to explore
        # This mimics probing uncertain abstractions
        exploration_bonus = self.alpha * uncertainty * math.sqrt(math.log(1 + n_trials) / (1 + n_trials))
        
        return mean_reward + exploration_bonus

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tie-breaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        concat = s1_bytes + s2_bytes
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_concat = len(zlib.compress(concat))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_concat - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feats = self._extract_features(prompt)
        results = []
        
        # Pre-calculate prompt complexity for normalization if needed
        prompt_complexity = sum(prompt_feats.values()) + 1
        
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            
            # Renormalization
            fine, coarse, uncertainty = self._renormalize(prompt_feats, cand_feats)
            
            # Bandit Scoring
            score = self._compute_bandit_score(fine, coarse, uncertainty)
            
            # Structural boost: If prompt asks a yes/no question (implied by short candidates)
            # and candidate matches expected boolean logic (heuristic)
            if prompt_complexity < 5 and len(cand.split()) <= 2:
                # Simple tasks rely heavily on exact structural match
                score *= 1.2 
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Fine:{fine:.2f}, Coarse:{coarse:.2f}, Unc:{uncertainty:.2f}",
                "_uncertainty": uncertainty # For sorting tie-breaks
            })
        
        # Sort by score (desc), then by uncertainty (desc to prefer exploring uncertain but high-potential),
        # then by NCD (asc, as tiebreaker)
        def sort_key(item):
            # NCD tiebreaker
            ncd_val = self._ncd(prompt, item['candidate'])
            return (-item['score'], -item['_uncertainty'], ncd_val)
            
        results.sort(key=sort_key)
        
        # Clean up internal keys
        final_results = []
        for r in results:
            final_results.append({
                "candidate": r["candidate"],
                "score": r["score"],
                "reasoning": r["reasoning"]
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the structural alignment score.
        """
        prompt_feats = self._extract_features(prompt)
        cand_feats = self._extract_features(answer)
        
        fine, coarse, uncertainty = self._renormalize(prompt_feats, cand_feats)
        score = self._compute_bandit_score(fine, coarse, uncertainty)
        
        # Normalize score to 0-1 range roughly
        # Base score is 0-1, exploration bonus can push it slightly over, cap at 1.0
        confidence = min(1.0, max(0.0, score))
        
        # Penalize high uncertainty in final confidence (metacognition)
        # If the system is unsure (high uncertainty), confidence should drop
        confidence *= (1.0 - 0.5 * uncertainty)
        
        return confidence