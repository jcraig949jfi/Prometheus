"""
Immune-Spectral Kalman Estimator (ISKE)

Combines spectral analysis of logical structure, immune-inspired clonal selection,
and Kalman filtering for recursive correctness estimation.

Architecture:
1. Parse structural features (negations, comparatives, conditionals, causals, temporals)
2. Compute power spectral density of feature vectors via FFT
3. Generate clonal variants via bit-flip mutations
4. Select high-affinity clones using spectral distance from reference prototype
5. Update correctness estimate via Kalman filter
6. Apply epistemic honesty checks for ambiguous/unanswerable questions
"""

import re
import numpy as np
from forge_primitives import (
    bayesian_update, solve_constraints, modus_ponens,
    check_transitivity, temporal_order, confidence_from_agreement,
    information_sufficiency, negate
)

class ReasoningTool:
    def __init__(self):
        # Reference prototype spectrum (high-quality answer pattern)
        self.prototype_spectrum = self._build_prototype()
        self.feature_dim = 20
        self.fft_len = 64
        
        # Kalman filter parameters
        self.process_noise = 0.01
        self.measurement_noise = 0.1
        self.spectral_weights = np.ones(self.fft_len) / self.fft_len
        
        # Immune parameters
        self.n_clones = 5
        self.mutation_rate = 0.05
        self.survival_rate = 0.6
        
    def _build_prototype(self):
        # Prototype: balanced logical structure (moderate spectral power)
        proto_features = np.array([1,0,1,0,1,0,0,1,0,0,1,0,0,0,1,0,0,0,0,0])
        padded = np.pad(proto_features, (0, 64 - len(proto_features)))
        fft = np.fft.fft(padded)
        return np.abs(fft)**2 / 64
        
    def _extract_features(self, text):
        """Extract binary structural features from text"""
        features = np.zeros(self.feature_dim)
        text_lower = text.lower()
        
        # Negations
        features[0] = bool(re.search(r'\b(not|no|never|neither|nor)\b', text_lower))
        features[1] = bool(re.search(r"n't\b", text_lower))
        
        # Comparatives
        features[2] = bool(re.search(r'\b(more|less|greater|smaller|bigger)\b', text_lower))
        features[3] = bool(re.search(r'[<>]=?', text))
        
        # Conditionals
        features[4] = bool(re.search(r'\b(if|then|when|unless)\b', text_lower))
        features[5] = bool(re.search(r'\b(implies|therefore|thus)\b', text_lower))
        
        # Numeric constants
        features[6] = bool(re.search(r'\b\d+\.?\d*\b', text))
        features[7] = len(re.findall(r'\b\d+', text)) > 2
        
        # Causal cues
        features[8] = bool(re.search(r'\b(because|since|causes?|leads? to)\b', text_lower))
        features[9] = bool(re.search(r'\b(result|effect|consequence)\b', text_lower))
        
        # Temporal/ordering
        features[10] = bool(re.search(r'\b(before|after|first|last|then)\b', text_lower))
        features[11] = bool(re.search(r'\b(earlier|later|previously|next)\b', text_lower))
        
        # Logical structure
        features[12] = bool(re.search(r'\b(all|every|each)\b', text_lower))
        features[13] = bool(re.search(r'\b(some|any|exist)\b', text_lower))
        features[14] = bool(re.search(r'\b(and|or|but)\b', text_lower))
        
        # Modality
        features[15] = bool(re.search(r'\b(must|should|could|might|may)\b', text_lower))
        features[16] = bool(re.search(r'\b(always|sometimes|often|rarely)\b', text_lower))
        
        # Question markers
        features[17] = bool(re.search(r'\b(who|what|where|when|why|how)\b', text_lower))
        features[18] = '?' in text
        
        # Complexity
        features[19] = len(text.split()) > 20
        
        return features
        
    def _compute_spectrum(self, features):
        """Compute power spectral density"""
        padded = np.pad(features, (0, self.fft_len - len(features)))
        fft = np.fft.fft(padded)
        return np.abs(fft)**2 / self.fft_len
        
    def _clonal_selection(self, spectrum):
        """Generate and select high-affinity clones"""
        clones = []
        for _ in range(self.n_clones):
            # Mutate spectrum by small perturbations
            mutation = np.random.binomial(1, self.mutation_rate, len(spectrum))
            mutated = spectrum * (1 + 0.1 * (mutation - 0.5))
            affinity = np.exp(-np.linalg.norm(mutated - self.prototype_spectrum))
            clones.append((mutated, affinity))
        
        # Select top survivors
        clones.sort(key=lambda x: x[1], reverse=True)
        n_survive = max(1, int(len(clones) * self.survival_rate))
        return [c[0] for c in clones[:n_survive]]
        
    def _kalman_update(self, observation, prior_mean=0.5, prior_cov=0.5):
        """Kalman filter update step"""
        # Prediction
        pred_mean = prior_mean
        pred_cov = prior_cov + self.process_noise
        
        # Update
        innovation = observation - np.dot(self.spectral_weights, pred_mean * np.ones(self.fft_len))
        innovation_cov = pred_cov + self.measurement_noise
        kalman_gain = pred_cov / innovation_cov
        
        post_mean = pred_mean + kalman_gain * innovation
        post_cov = (1 - kalman_gain) * pred_cov
        
        return float(np.clip(post_mean, 0, 1)), post_cov
        
    def _meta_confidence(self, prompt):
        """Check prompt for ambiguity/unanswerability (Tier B)"""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|did you quit|why did.*fail|when did.*stop)\b', prompt_lower):
            return 0.2
            
        # Scope ambiguity
        if re.search(r'\b(every|each|all).*\ba\b', prompt_lower):
            return 0.25
            
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b.*\b(who|which)\b', prompt_lower):
            return 0.25
            
        # False dichotomy
        if re.search(r'\b(either.*or|only two)\b', prompt_lower) and not re.search(r'\b(other|else)\b', prompt_lower):
            return 0.3
            
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', prompt_lower) and not re.search(r'\b(most|least|criteria)\b', prompt_lower):
            return 0.3
            
        return 1.0  # No meta-level issues detected
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Rank candidates using ISKE pipeline"""
        results = []
        prompt_features = self._extract_features(prompt)
        
        for candidate in candidates:
            # Spectral analysis
            cand_features = self._extract_features(candidate)
            combined_features = np.concatenate([prompt_features, cand_features])[:self.feature_dim]
            spectrum = self._compute_spectrum(combined_features)
            
            # Clonal selection
            clones = self._clonal_selection(spectrum)
            
            # Kalman filtering over clones
            scores = []
            for clone_spectrum in clones:
                obs = np.dot(self.spectral_weights, clone_spectrum)
                score, _ = self._kalman_update(obs)
                scores.append(score)
            
            # Aggregate via confidence_from_agreement primitive
            final_score = confidence_from_agreement(scores)
            
            # NCD tiebreaker (max 10% influence)
            import zlib
            ncd = len(zlib.compress((prompt + candidate).encode())) / (
                len(zlib.compress(prompt.encode())) + len(zlib.compress(candidate.encode())) + 1e-9
            )
            ncd_bonus = 0.1 * (1 - ncd)
            
            total_score = 0.9 * final_score + 0.1 * ncd_bonus
            
            reasoning = f"Spectral affinity: {final_score:.3f}, Clones: {len(clones)}, NCD: {ncd:.3f}"
            results.append({"candidate": candidate, "score": total_score, "reasoning": reasoning})
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
        
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence in answer given prompt"""
        # Meta-level check first
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.5:
            return meta_conf
            
        # Evaluate answer
        results = self.evaluate(prompt, [answer])
        base_conf = results[0]["score"]
        
        # Cap confidence - never return > 0.9 unless structural certainty
        if not re.search(r'\d+', answer) and not re.search(r'\b(yes|no|true|false)\b', answer.lower()):
            base_conf = min(base_conf, 0.85)
        
        return float(np.clip(meta_conf * base_conf, 0, 1))