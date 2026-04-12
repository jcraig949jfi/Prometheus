from typing import Dict, Tuple

"""
Spectral-Emergent Metamorphic Scorer (SEMS)
Combines frequency-domain analysis of structural features with metamorphic testing
to detect emergent inconsistencies in reasoning candidates.
"""
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    def __init__(self):
        # Metamorphic relations: (feature_i, feature_j, weight)
        self.metamorphic_edges = [
            (0, 1, 1.0),  # negation vs comparative
            (2, 3, 1.0),  # conditional vs numeric
            (4, 5, 1.0),  # causal vs ordering
            (1, 5, 0.8),  # comparative vs ordering
            (3, 5, 0.9),  # numeric vs ordering
        ]
        
    def _extract_features(self, text: str) -> np.ndarray:
        """Extract structural features into binary matrix (sentences x features)"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences:
            sentences = [text]
        
        features = []
        for sent in sentences:
            sent_lower = sent.lower()
            feat = [
                int(bool(re.search(r'\b(not|no|never|neither|nor)\b', sent_lower))),  # 0: negation
                int(bool(re.search(r'\b(more|less|greater|smaller|fewer|larger) than\b', sent_lower))),  # 1: comparative
                int(bool(re.search(r'\b(if|when|unless|provided)\b.*\b(then|will|would)\b', sent_lower))),  # 2: conditional
                int(bool(re.search(r'\b\d+\.?\d*\b', sent))),  # 3: numeric
                int(bool(re.search(r'\b(because|since|leads to|causes|results in|produces)\b', sent_lower))),  # 4: causal
                int(bool(re.search(r'\b(before|after|greater than|less than|earlier|later)\b', sent_lower))),  # 5: ordering
                int(bool(re.search(r'\b(all|every|each|some|any|most)\b', sent_lower))),  # 6: quantifier
            ]
            features.append(feat)
        
        return np.array(features, dtype=np.int8)
    
    def _compute_spectral_score(self, F: np.ndarray) -> float:
        """Compute SEMS score using spectral analysis + metamorphic constraints"""
        if F.shape[0] < 2:
            return 0.5
        
        n, m = F.shape
        e = np.zeros(m, dtype=np.float32)
        
        # Spectral step: compute power spectrum for each feature
        power_spectra = []
        for i in range(m):
            if F[:, i].sum() == 0:
                power_spectra.append(0.0)
            else:
                fft = np.fft.rfft(F[:, i].astype(np.float32))
                power = np.abs(fft) ** 2
                power_spectra.append(np.max(power) if len(power) > 0 else 0.0)
        
        P = np.array(power_spectra)
        
        # Constraint propagation via metamorphic edges
        for _ in range(5):
            for i, j, w in self.metamorphic_edges:
                if i < m and j < m:
                    violation = w * abs(P[i] - P[j])
                    e[j] += violation
        
        # Score: inverse of inconsistency norm
        score = 1.0 / (1.0 + np.linalg.norm(e))
        return float(score)
    
    def _parse_numeric_comparison(self, prompt: str, candidate: str) -> float:
        """Parse numeric comparisons like 9.11 vs 9.9"""
        nums_p = re.findall(r'\b\d+\.?\d*\b', prompt)
        nums_c = re.findall(r'\b\d+\.?\d*\b', candidate)
        
        if len(nums_p) >= 2 and nums_c:
            try:
                a, b = float(nums_p[0]), float(nums_p[1])
                answer = float(nums_c[0]) if nums_c[0].replace('.', '').isdigit() else None
                
                if answer is not None:
                    if 'greater' in prompt.lower() or 'larger' in prompt.lower():
                        return 1.0 if (a > b and str(a) in candidate) or (b > a and str(b) in candidate) else 0.3
                    elif 'less' in prompt.lower() or 'smaller' in prompt.lower():
                        return 1.0 if (a < b and str(a) in candidate) or (b < a and str(b) in candidate) else 0.3
            except:
                pass
        return 0.5
    
    def _parse_bat_and_ball(self, prompt: str, candidate: str) -> float:
        """Solve bat-and-ball style algebra problems"""
        match = re.search(r'total.*?(\d+\.?\d*).*?more.*?(\d+\.?\d*)', prompt.lower())
        if match:
            total, diff = float(match.group(1)), float(match.group(2))
            correct = (total - diff) / 2
            nums_c = re.findall(r'\b\d+\.?\d*\b', candidate)
            if nums_c:
                try:
                    ans = float(nums_c[0])
                    return 1.0 if abs(ans - correct) < 0.01 else 0.2
                except:
                    pass
        return 0.5
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance"""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguous/unanswerable questions"""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you|did you) (stop|quit|cease)', p_lower):
            return 0.2
        if re.search(r'why (did|does|is).*\b(fail|stop|wrong)', p_lower):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', p_lower):
            return 0.3
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).*who', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p_lower) and 'neither' not in p_lower:
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower):
            return 0.35
        
        # Multiple question marks (confusion)
        if prompt.count('?') > 1:
            return 0.3
        
        return 1.0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates using SEMS + structural parsers"""
        results = []
        
        for cand in candidates:
            # Extract features
            F_prompt = self._extract_features(prompt)
            F_cand = self._extract_features(cand)
            F_combined = np.vstack([F_prompt, F_cand]) if F_cand.shape[0] > 0 else F_prompt
            
            # Spectral-emergent score (50%)
            spectral_score = self._compute_spectral_score(F_combined)
            
            # Structural parsers (30%)
            numeric_score = self._parse_numeric_comparison(prompt, cand)
            algebra_score = self._parse_bat_and_ball(prompt, cand)
            structural_score = (numeric_score + algebra_score) / 2
            
            # NCD tiebreaker (15%)
            ncd = self._ncd(prompt, cand)
            ncd_score = 1.0 - ncd
            
            # Feature consistency (5%)
            feat_consistency = 1.0 - np.mean(np.abs(F_prompt.mean(axis=0) - F_cand.mean(axis=0))) if F_cand.shape[0] > 0 else 0.5
            
            # Weighted combination
            final_score = (0.50 * spectral_score + 
                          0.30 * structural_score + 
                          0.15 * ncd_score + 
                          0.05 * feat_consistency)
            
            reasoning = f"Spectral: {spectral_score:.3f}, Structural: {structural_score:.3f}, NCD: {ncd_score:.3f}"
            results.append({"candidate": cand, "score": float(final_score), "reasoning": reasoning})
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 with epistemic honesty"""
        # Check for ambiguity/unanswerability
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.4:
            return meta_conf
        
        # Evaluate answer
        eval_result = self.evaluate(prompt, [answer])[0]
        base_score = eval_result["score"]
        
        # Cap confidence based on question properties
        if meta_conf < 0.6:
            max_conf = 0.5
        elif meta_conf < 0.8:
            max_conf = 0.7
        else:
            max_conf = 0.95
        
        # Scale score to confidence
        confidence = min(base_score * meta_conf, max_conf)
        
        return float(confidence)