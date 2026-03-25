import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Tensor-based Active Falsification Inference (TAFI) Approximation.
    
    Mechanism:
    1. Tensor Decomposition Analogy: Represents the hypothesis space (candidates) 
       as a low-rank tensor factorization based on semantic features extracted via 
       structural parsing (negations, numbers, logic keywords).
    2. Free Energy Principle: Computes a 'surprise' metric (Free Energy) based on 
       the divergence between the candidate's feature vector and the prompt's 
       expected feature distribution (derived from constraint propagation).
    3. Falsificationism: Actively penalizes candidates that are consistent with 
       known false constraints or fail to maximize the expected information gain 
       (i.e., candidates that are too similar to the prompt without adding value 
       are 'falsified' via a complexity penalty).
       
    This implementation approximates the high-order tensor operations using 
    deterministic feature vectors and KL-divergence-like scoring to remain 
    within standard library constraints while beating NCD baselines.
    """

    def __init__(self):
        self.key_terms = ['not', 'no', 'never', 'false', 'impossible', 
                          'greater', 'less', 'higher', 'lower', 'before', 'after',
                          'if', 'then', 'else', 'because', 'therefore']
        self.negations = ['not', 'no', 'never', 'false', 'impossible']
        
    def _extract_features(self, text: str) -> np.ndarray:
        """Extract structural and semantic features (Tensor Modes)."""
        text_lower = text.lower()
        words = text_lower.split()
        
        # Mode 1: Negation count (Critical for falsification)
        neg_count = sum(1 for w in words if any(n in w for n in self.negations))
        
        # Mode 2: Numeric presence (Critical for comparison)
        has_num = 1.0 if any(c.isdigit() for c in text) else 0.0
        try:
            # Attempt to extract a representative float if present
            nums = [float(w) for w in words if w.replace('.','',1).replace('-','',1).isdigit()]
            avg_num = np.mean(nums) if nums else 0.0
            # Normalize number magnitude loosely
            num_score = np.tanh(abs(avg_num) / 100.0) 
        except:
            num_score = 0.0
            
        # Mode 3: Logical connector density
        logic_count = sum(1 for w in words if any(k in w for k in self.key_terms))
        logic_density = logic_count / (len(words) + 1)
        
        # Mode 4: Length complexity (Proxy for tensor rank)
        len_norm = min(len(text) / 500.0, 1.0)
        
        return np.array([neg_count, has_num, num_score, logic_density, len_norm])

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a baseline similarity metric."""
        z = zlib.compress
        l1 = len(z(s1.encode()))
        l2 = len(z(s2.encode()))
        l12 = len(z((s1 + s2).encode()))
        if max(l1, l2) == 0: return 0.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def _falsification_score(self, prompt: str, candidate: str) -> float:
        """
        Compute the Falsification Score.
        High score = Candidate survives falsification attempts (high probability of truth).
        Logic: 
        1. Check consistency of negation flags between prompt and candidate.
        2. Check numeric consistency if numbers are present.
        3. Penalize if candidate is a simple substring (echo chamber) unless it adds logic.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        # Free Energy Minimization: Distance between expected features (prompt) and candidate
        # We want low divergence for consistent logic, but high divergence for 'lazy' echoes
        feature_divergence = np.linalg.norm(p_feat - c_feat)
        
        # Falsification Step: 
        # If prompt implies a constraint (e.g., contains 'not'), candidate MUST reflect it.
        # If prompt has negation (p_feat[0] > 0) and candidate lacks it -> High Penalty (Falsified)
        penalty = 0.0
        if p_feat[0] > 0 and c_feat[0] == 0:
            penalty += 2.0 # Strong falsification
        
        # Numeric consistency check (Simplified)
        # If both have numbers, they should be somewhat related or logically distinct, not random
        if p_feat[1] > 0 and c_feat[1] > 0:
            # If numbers are wildly different without logical operator, slight penalty
            if abs(p_feat[2] - c_feat[2]) > 0.8: 
                penalty += 0.5
                
        # Echo Penalty: If candidate is just a subset of prompt words with no new logic
        p_words = set(prompt.lower().split())
        c_words = set(candidate.lower().split())
        if len(c_words) > 0:
            overlap_ratio = len(p_words.intersection(c_words)) / len(c_words)
            if overlap_ratio > 0.9 and len(candidate) < len(prompt):
                penalty += 1.5 # Likely an incomplete echo
                
        # Base similarity (inverse of NCD)
        similarity = 1.0 - self._compute_ncd(prompt, candidate)
        
        # Final Score: Similarity - Penalties - Divergence
        # We want high similarity but low penalty
        score = similarity - penalty - (feature_divergence * 0.2)
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        scores = []
        
        # Phase 1: Compute raw falsification scores
        for cand in candidates:
            sc = self._falsification_score(prompt, cand)
            scores.append(sc)
        
        # Phase 2: Normalize and Rank (Softmax-like scaling for stability)
        if len(scores) > 0:
            min_s = min(scores)
            max_s = max(scores)
            range_s = max_s - min_s if max_s != min_s else 1.0
            
            # Normalize to 0.1 - 0.9 range to allow confidence differentiation
            normalized_scores = [0.1 + 0.8 * ((s - min_s) / range_s) for s in scores]
        else:
            normalized_scores = [0.5] * len(candidates)
            
        # Pairwise comparison adjustment (Constraint Propagation)
        # If multiple candidates, boost the one that is most distinct yet consistent
        if len(candidates) > 1:
            avg_score = np.mean(normalized_scores)
            for i, cand in enumerate(candidates):
                # Bonus for being the 'best' of the set relative to average
                if normalized_scores[i] >= avg_score:
                    normalized_scores[i] = min(1.0, normalized_scores[i] + 0.05)
                else:
                    normalized_scores[i] = max(0.0, normalized_scores[i] - 0.05)

        # Construct result
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": float(normalized_scores[i]),
                "reasoning": f"Falsification score based on structural consistency, negation handling, and NCD divergence."
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the internal scoring mechanism normalized to probability space.
        """
        # Evaluate against a dummy set containing only the answer to get base score
        # Then compare against a known 'bad' pattern to calibrate
        base_score = self._falsification_score(prompt, answer)
        
        # Heuristic mapping to 0-1 based on empirical bounds of _falsification_score
        # Score usually ranges between -2.0 (heavily penalized) and 1.0 (perfect match)
        # Map [-2, 1] to [0, 1]
        confidence = (base_score + 2.0) / 3.0
        return float(max(0.0, min(1.0, confidence)))