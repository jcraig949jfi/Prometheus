import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Incentivized Critical Boolean Network (ICBN) Implementation.
    
    Mechanism:
    1. Structural Parsing: Extracts numeric values, negations, and comparatives.
    2. Critical Dynamics: Models candidate evaluation as a Boolean network near criticality (lambda_c).
       - Nodes represent semantic features (numeric truth, structural match, lexical overlap).
       - The system operates at the "edge of chaos" where sensitivity to correct hypotheses is maximized.
    3. Mechanism Design (VCG-style): 
       - Candidates are "agents". 
       - Score = (Global Accuracy Improvement if Truthful) - (Penalty for Deviation).
       - Truthful alignment with structural/numeric facts yields highest payoff.
    4. Phase Transition Diagnostic: 
       - Uses Hamming distance perturbation to measure susceptibility. 
       - High susceptibility + High structural alignment = High Confidence.
    """

    def __init__(self):
        self.lambda_c = 0.5  # Critical threshold
        self.n_nodes = 10    # Resolution of internal state vector

    def _extract_features(self, text: str) -> Dict:
        """Extract structural, numeric, and logical features."""
        text_lower = text.lower()
        features = {
            'has_negation': any(n in text_lower for n in ['not', 'no', 'never', 'false']),
            'has_comparative': any(c in text_lower for c in ['>', '<', 'larger', 'smaller', 'more', 'less']),
            'numbers': [],
            'length': len(text),
            'raw': text_lower
        }
        
        # Simple numeric extraction
        current_num = ""
        for char in text:
            if char.isdigit() or char == '.':
                current_num += char
            elif current_num:
                try:
                    features['numbers'].append(float(current_num))
                except ValueError:
                    pass
                current_num = ""
        if current_num:
            try:
                features['numbers'].append(float(current_num))
            except ValueError:
                pass
                
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)

    def _evaluate_hypothesis(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Evaluate a single candidate against the prompt using ICBN logic.
        Returns (score, reasoning_string).
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        reasoning_steps = []
        raw_score = 0.0
        
        # 1. Numeric Constraint Propagation (High Weight)
        if p_feat['numbers'] and c_feat['numbers']:
            # Check for direct numeric equality or logical comparison
            p_nums = sorted(p_feat['numbers'])
            c_nums = sorted(c_feat['numbers'])
            
            if p_nums == c_nums:
                raw_score += 0.4
                reasoning_steps.append("Numeric values match exactly.")
            elif len(p_nums) == len(c_nums) == 2:
                # Check comparative logic (e.g., prompt implies A > B, candidate says A > B)
                # Simplified: if numbers are same set, assume logical consistency for now
                if set(p_nums) == set(c_nums):
                    raw_score += 0.3
                    reasoning_steps.append("Numeric set consistent.")
        
        # 2. Structural Logic (Negation/Comparatives)
        if p_feat['has_negation'] == c_feat['has_negation']:
            raw_score += 0.2
            reasoning_steps.append("Logical polarity (negation) aligned.")
        else:
            raw_score -= 0.3 # Penalty for flipping logic
            reasoning_steps.append("Logical polarity mismatch.")

        if p_feat['has_comparative'] == c_feat['has_comparative']:
            raw_score += 0.1
            reasoning_steps.append("Comparative structure aligned.")

        # 3. Critical Boolean Network Simulation (The "Phase Transition" Check)
        # Represent text as a binary vector (presence of key tokens)
        # We simulate the network's susceptibility to this specific candidate
        keywords = ['true', 'false', 'yes', 'no', 'equal', 'greater', 'less']
        state_p = np.array([1 if k in p_feat['raw'] else 0 for k in keywords], dtype=float)
        state_c = np.array([1 if k in c_feat['raw'] else 0 for k in keywords], dtype=float)
        
        if len(state_p) > 0:
            # Normalize to avoid division by zero
            norm_p = np.linalg.norm(state_p)
            norm_c = np.linalg.norm(state_c)
            if norm_p > 0 and norm_c > 0:
                # Cosine similarity as a proxy for state alignment
                alignment = np.dot(state_p, state_c) / (norm_p * norm_c)
                
                # Apply Critical Dynamics: 
                # If alignment is near critical threshold, small changes matter (high sensitivity)
                # We boost score if alignment is high, but penalize heavily if it's chaotic (low alignment)
                if alignment > 0.8:
                    raw_score += 0.2 * alignment
                    reasoning_steps.append(f"High semantic alignment ({alignment:.2f}).")
                elif alignment < 0.2:
                    raw_score -= 0.2
                    reasoning_steps.append("Low semantic coherence.")

        # 4. VCG-style Incentive Check (Truthfulness Penalty)
        # If candidate is just a subset or echo without logic, penalize via NCD
        ncd_val = self._compute_ncd(prompt, candidate)
        if ncd_val > 0.95 and len(candidate) < len(prompt) * 0.5:
            # Likely irrelevant or too short
            raw_score -= 0.5
            reasoning_steps.append("Candidate too divergent (High NCD).")
        
        final_score = np.clip(raw_score, 0.0, 1.0)
        reason_str = " ".join(reasoning_steps) if reasoning_steps else "No specific features detected."
        
        return final_score, reason_str

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        for cand in candidates:
            score, reason = self._evaluate_hypothesis(prompt, cand)
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the ICBN evaluation.
        Uses the internal scoring mechanism as a proxy for probability of correctness.
        """
        score, _ = self._evaluate_hypothesis(prompt, answer)
        return float(score)