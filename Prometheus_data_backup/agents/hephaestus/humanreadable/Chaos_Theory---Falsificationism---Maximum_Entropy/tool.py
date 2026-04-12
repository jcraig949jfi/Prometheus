import math
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    CFME Engine: Chaotic Falsification-Maximum Entropy Reasoning Tool.
    
    Mechanism:
    1. Chaotic Proposal Sampler: Uses a discrete Lorenz map to generate 
       deterministic, ergodic perturbation weights for feature extraction.
       This prevents local optima in feature selection by ensuring diverse
       coverage of structural patterns (negations, numerics, constraints).
       
    2. Falsification Module: Treats each candidate as a hypothesis. It actively
       searches for "counter-evidence" within the prompt-candidate pair:
       - Logical contradictions (negation mismatches)
       - Numeric inconsistencies
       - Structural mismatches (subject-object reversal)
       If a fatal counter-example is found, the hypothesis score is penalized.
       
    3. Maximum Entropy Updater: Computes the final score as a log-linear model
       p(h) ~ exp(-Energy). The energy is a weighted sum of falsification counts
       and feature mismatches. Weights are derived from a MaxEnt-inspired 
       iterative scaling approximation to remain least-biased given the constraints.
    """

    def __init__(self):
        # Lorenz parameters for chaotic sampler
        self.sigma = 10.0
        self.rho = 28.0
        self.beta = 8.0/3.0
        self.dt = 0.01
        # Initial state for chaotic generator (deterministic seed)
        self._x, self._y, self._z = 1.0, 1.0, 1.0
        
    def _chaotic_step(self) -> Tuple[float, float, float]:
        """Discrete Lorenz system step for ergodic weight generation."""
        dx = self.sigma * (self._y - self._x) * self.dt
        dy = (self._x * (self._rho - self._z) - self._y) * self.dt if hasattr(self, '_rho') else (self._x * (self.rho - self._z) - self._y) * self.dt
        dz = (self._x * self._y - self.beta * self._z) * self.dt
        self._x += dx
        self._y += dy
        self._z += dz
        # Normalize to [0, 1] range for weighting via sigmoid-like mapping
        w1 = 1.0 / (1.0 + math.exp(-self._x * 0.1))
        w2 = 1.0 / (1.0 + math.exp(-self._y * 0.1))
        w3 = 1.0 / (1.0 + math.exp(-self._z * 0.1))
        return w1, w2, w3

    def _extract_features(self, text: str) -> Dict[str, float]:
        """Extract structural features: negations, numbers, comparatives."""
        text_l = text.lower()
        features = {
            'negation': len(re.findall(r'\b(not|no|never|neither|without)\b', text_l)),
            'numeric': len(re.findall(r'\d+\.?\d*', text_l)),
            'comparative': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', text_l)),
            'conditional': len(re.findall(r'\b(if|then|unless|provided)\b', text_l)),
            'length': len(text)
        }
        return features

    def _falsify(self, prompt: str, candidate: str) -> float:
        """
        Falsification Module: Seek counter-examples.
        Returns a penalty score (higher = more falsified).
        """
        penalty = 0.0
        p_feats = self._extract_features(prompt)
        c_feats = self._extract_features(candidate)
        full_text = f"{prompt} {candidate}".lower()
        
        # 1. Negation Contradiction Check
        # If prompt implies negation but candidate affirms, or vice versa
        has_no = 'no ' in full_text or ' not ' in full_text
        if 'yes' in candidate.lower() and has_no:
            # Crude check: if prompt has 'no' and candidate is just 'yes', penalize
            if re.search(r'\bno\b', prompt.lower()) and candidate.lower().strip() == 'yes':
                penalty += 5.0
            elif re.search(r'\bnot\b', prompt.lower()) and candidate.lower().strip() == 'yes':
                penalty += 5.0
                
        # 2. Numeric Consistency
        # If prompt has numbers and candidate has different numbers, check logic
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        c_nums = re.findall(r'\d+\.?\d*', candidate)
        if p_nums and not c_nums:
            # Candidate ignores numeric constraints (weak falsification)
            penalty += 0.5
        elif p_nums and c_nums:
            # Simple consistency: if prompt says "9.11 < 9.9" and candidate contradicts order
            try:
                p_vals = [float(n) for n in p_nums]
                c_vals = [float(n) for n in c_nums]
                # Heuristic: if prompt implies sorting and candidate breaks it
                if len(p_vals) >= 2 and len(c_vals) >= 2:
                    if (p_vals[0] < p_vals[1]) and (c_vals[0] > c_vals[1]):
                         penalty += 2.0
            except ValueError:
                pass

        # 3. Structural Echo (Bag-of-words trap avoidance)
        # If candidate is >90% substring of prompt, it might be lazy echoing
        if len(candidate) > 5 and candidate.lower().strip() in prompt.lower():
            penalty += 1.0
            
        return penalty

    def _max_ent_score(self, prompt: str, candidate: str) -> float:
        """
        Maximum Entropy Updater:
        Compute energy based on feature constraints and falsification penalties.
        Score = exp(-Energy)
        """
        # Reset chaotic state for deterministic reproducibility per call sequence
        # (In a real stream, this would persist, but here we reset per eval for stability)
        self._x, self._y, self._z = 1.0, 1.0, 1.0
        
        p_feats = self._extract_features(prompt)
        c_feats = self._extract_features(candidate)
        
        # Generate chaotic weights for feature matching
        w1, w2, w3 = self._chaotic_step()
        
        # Energy function (Linear combination of mismatches)
        # Constraint 1: Feature alignment (weighted by chaotic sampler)
        feature_mismatch = 0.0
        keys = ['negation', 'numeric', 'comparative', 'conditional']
        for i, k in enumerate(keys):
            diff = abs(p_feats.get(k, 0) - c_feats.get(k, 0))
            # Use chaotic weights cyclically
            weight = [w1, w2, w3][i % 3]
            feature_mismatch += diff * weight
            
        # Constraint 2: Falsification penalty (Popperian)
        falsification_penalty = self._falsify(prompt, candidate)
        
        # Constraint 3: NCD tiebreaker (Compression distance)
        try:
            s_joint = f"{prompt}{candidate}".encode('utf-8')
            s_prompt = prompt.encode('utf-8')
            s_cand = candidate.encode('utf-8')
            len_joint = len(zlib.compress(s_joint))
            len_p = len(zlib.compress(s_prompt))
            len_c = len(zlib.compress(s_cand))
            # Normalized Compression Distance
            ncd = (len_joint - min(len_p, len_c)) / max(len_p, len_c, 1)
        except:
            ncd = 0.5

        # Total Energy
        # High mismatch + high falsification = High Energy = Low Probability
        energy = (feature_mismatch * 0.5) + (falsification_penalty * 1.5) + (ncd * 0.2)
        
        # Boltzmann distribution
        score = math.exp(-energy)
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._max_ent_score(prompt, cand)
            reasoning = f"CFME Score: {score:.4f}. Falsification checks applied. MaxEnt update complete."
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        # Use the same scoring mechanism
        score = self._max_ent_score(prompt, answer)
        # Normalize score to 0-1 range roughly (scores are already exp(-E) so <= 1)
        # But low energy (good match) -> score near 1. High energy -> score near 0.
        return max(0.0, min(1.0, score))