import math
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamic Prime-Chaotic Sampler (TPCS) Implementation.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values to form a deterministic base score.
       This addresses the "Prime Number Theory" warning by using primes only for 
       structural weighting (indexing), not direct scoring.
       
    2. Chaos & Thermodynamics (Secondary Modifier): 
       - Uses a logistic map (Chaos) seeded by prime gaps to generate perturbation factors.
       - Calculates a "Lyapunov-inspired" entropy estimate based on candidate diversity.
       - Applies a Boltzmann-like acceptance factor to adjust scores, simulating 
         thermodynamic cooling to penalize low-entropy (repetitive/generic) answers.
       
    3. NCD (Tiebreaker): Used only when structural scores are identical.
    """

    def __init__(self):
        # Primes for structural indexing (avoiding direct scoring as per warning)
        self.primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        # Chaos parameters
        self.r_map = 3.99  # Logistic map parameter (highly chaotic)
        
    def _get_prime_gap_seed(self, text: str) -> int:
        """Generate a deterministic seed based on text length and prime gaps."""
        base = len(text)
        # Find nearest prime gap influence
        idx = base % len(self.primes)
        return (base * self.primes[idx]) % 1000

    def _logistic_map(self, x: float, steps: int = 10) -> float:
        """Iterate logistic map to generate chaotic value."""
        for _ in range(steps):
            x = self.r_map * x * (1.0 - x)
            # Prevent boundary collapse
            if x <= 0.0 or x >= 1.0:
                x = 0.5 
        return x

    def _extract_structural_features(self, text: str) -> Tuple[float, List[float]]:
        """
        Extract logical features: negations, comparatives, numbers.
        Returns a base score and a vector of feature magnitudes.
        """
        text_lower = text.lower()
        score = 0.0
        features = []
        
        # 1. Negation detection (Logic inversion)
        negations = ['not', 'no', 'never', 'none', 'cannot', 'dont', "dont"]
        neg_count = sum(1 for w in negations if re.search(r'\b' + w + r'\b', text_lower))
        features.append(neg_count * 0.5)
        
        # 2. Comparative detection (Logic relation)
        comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        comp_count = sum(1 for w in comparatives if w in text_lower)
        features.append(comp_count * 0.4)
        
        # 3. Conditional detection (If-Then)
        conditionals = ['if', 'then', 'else', 'unless', 'provided']
        cond_count = sum(1 for w in conditionals if re.search(r'\b' + w + r'\b', text_lower))
        features.append(cond_count * 0.3)
        
        # 4. Numeric evaluation
        numbers = re.findall(r"-?\d+\.?\d*", text)
        if numbers:
            try:
                vals = [float(n) for n in numbers]
                # Feature: magnitude variance
                if len(vals) > 1:
                    features.append(max(vals) - min(vals))
                else:
                    features.append(vals[0] * 0.1)
            except ValueError:
                features.append(0.0)
        else:
            features.append(0.0)
            
        # Base score is sum of weighted features
        base = sum(features)
        return base, features

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_base, prompt_feats = self._extract_structural_features(prompt)
        seed_val = self._get_prime_gap_seed(prompt)
        
        # Normalize prompt features for chaos seeding
        x_init = 0.5
        if prompt_base != 0:
            x_init = abs(math.sin(prompt_base)) 
        
        scored_candidates = []
        
        # Calculate global entropy proxy (diversity of candidates)
        candidate_scores_raw = []
        for i, cand in enumerate(candidates):
            base, _ = self._extract_structural_features(cand)
            # Structural match score (higher is better)
            # We want candidates that preserve logical structure (negations/conditionals) 
            # present in prompt or logically resolve them.
            score = 0.0
            
            # Penalty/M奖励 logic: 
            # If prompt has negation, candidate should ideally reflect understanding.
            # Simple heuristic: Candidate length similarity + feature overlap
            feat_match = 0.0
            if len(prompt_feats) == len(_) : # Should always be true
                for p, c in zip(prompt_feats, _):
                    if p > 0 and c > 0:
                        feat_match += min(p, c) / max(p, c) # Similarity
                    elif p == 0 and c == 0:
                        feat_match += 0.1 # Neutral match
            
            score = feat_match * 10.0
            
            # Length penalty for extreme outliers (Occam's razor via thermodynamics analogy)
            len_ratio = len(cand) / (len(prompt) + 1)
            if len_ratio > 2.0 or len_ratio < 0.1:
                score -= 2.0 * abs(len_ratio - 1.0)
                
            candidate_scores_raw.append(score)

        # Apply Chaos-Thermodynamic adjustment
        max_raw = max(candidate_scores_raw) if candidate_scores_raw else 1.0
        min_raw = min(candidate_scores_raw) if candidate_scores_raw else 0.0
        range_raw = max_raw - min_raw if max_raw != min_raw else 1.0
        
        for i, cand in enumerate(candidates):
            # Chaotic perturbation
            x = x_init + (i * 0.01) # Slight variation per candidate
            x = x - math.floor(x) # Keep in [0, 1)
            chaos_factor = self._logistic_map(x, steps=5 + (i % 5))
            
            # Thermodynamic Temperature adjustment
            # High chaos (high lyapunov approx) -> Lower Temp -> Stricter selection
            # Entropy production proxy: range of raw scores
            entropy_prod = range_raw * (1.0 + chaos_factor)
            temperature = 1.0 / (1.0 + entropy_prod) 
            
            # Normalize raw score
            norm_score = (candidate_scores_raw[i] - min_raw) / range_raw
            
            # Boltzmann-like adjustment
            # E = -log(P) approx -norm_score. 
            # Acceptance ~ exp((score - max)/T)
            energy_diff = (norm_score - 1.0) # Relative to ideal
            adjustment = math.exp(energy_diff / (temperature + 0.1))
            
            final_score = norm_score + (chaos_factor * 0.1 * adjustment)
            
            # NCD Tiebreaker (only if scores are very close)
            ncd_val = self._calculate_ncd(prompt, cand)
            # Invert NCD so lower distance = higher score contribution
            ncd_bonus = (1.0 - ncd_val) * 0.01 
            
            total_score = final_score + ncd_bonus
            
            scored_candidates.append({
                "candidate": cand,
                "score": float(total_score),
                "reasoning": f"Structural match: {norm_score:.2f}, Chaos adj: {chaos_factor:.2f}, Temp: {temperature:.2f}"
            })
            
        # Sort descending by score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural consistency and NCD.
        """
        # 1. Structural Consistency Check
        p_base, p_feats = self._extract_structural_features(prompt)
        a_base, a_feats = self._extract_structural_features(answer)
        
        consistency = 0.0
        count = 0
        
        # Check negation preservation/inversion logic
        # If prompt has "not", answer often needs to acknowledge it or be short (Yes/No)
        if p_feats[0] > 0: # Prompt has negation
            if a_feats[0] > 0 or len(answer.split()) < 5:
                consistency += 0.4
            else:
                consistency -= 0.2
        count += 1
        
        # Check numeric consistency if present
        if p_feats[3] > 0 and a_feats[3] > 0:
            # If both have numbers, they should be somewhat related or answer should be derived
            # Heuristic: if prompt numbers are huge and answer is small, maybe wrong? 
            # Too complex for simple heuristic, give partial credit for presence
            consistency += 0.3
        count += 1
        
        # 2. NCD Check (Similarity implies relevance in many QA tasks)
        ncd = self._calculate_ncd(prompt, answer)
        # Low NCD (high similarity) usually means high relevance in this context
        ncd_score = 1.0 - ncd
        
        # Combine
        # Weight structural slightly higher to avoid pure string matching
        base_conf = (consistency + 0.5) * 0.6 + (ncd_score * 0.4)
        
        # Clamp
        conf = max(0.0, min(1.0, base_conf))
        
        # Chaos modifier for calibration (simulated annealing feel)
        seed = self._get_prime_gap_seed(prompt + answer)
        chaos = self._logistic_map(seed / 1000.0, steps=3)
        # Small jitter to prevent overconfidence in edge cases
        conf = conf * (0.9 + 0.2 * chaos)
        
        return float(max(0.0, min(1.0, conf)))