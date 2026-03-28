import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Epistemic Feedback Control Tool.
    Mechanism:
    1. Structural Parsing: Extracts logical features (negations, comparatives, conditionals, numerics).
    2. MaxEnt Initialization: Assigns initial weights to logical constraints based on prompt density.
    3. Feedback Loop (PID): Iteratively adjusts constraint weights to minimize the error between 
       the computed belief marginal and the expected truth value, simulating epistemic refinement.
    4. Scoring: Primary score is the converged belief probability; NCD is a tiebreaker.
    """
    
    def __init__(self):
        self.Kp = 0.1
        self.Ki = 0.01
        self.Kd = 0.05
        self.steps = 8

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Extract structural logical features using regex."""
        t = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|none)\b', t)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|than|>|<|>=|<=)\b', t)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided|when)\b', t)),
            'causals': len(re.findall(r'\b(because|leads|results|causes|due to)\b', t)),
            'numerics': [float(x) for x in re.findall(r'-?\d+\.?\d*', t)],
            'quantifiers': len(re.findall(r'\b(all|some|every|each|any)\b', t))
        }
        features['has_logic'] = sum([features['negations'], features['comparatives'], 
                                     features['conditionals'], features['causals']]) > 0
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            return (c12 - min(c1, c2)) / max(c1, c2, 1)
        except:
            return 1.0

    def _sigmoid(self, x: float) -> float:
        return 1.0 / (1.0 + np.exp(-x))

    def _run_inference(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Core MaxEnt + PID inference engine."""
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        combined = prompt + " " + candidate
        c_feat_all = self._extract_features(combined)
        
        # Feature vector: [neg, comp, cond, causal, num_match, quant]
        # Numeric match: 1 if candidate numbers appear in prompt or satisfy simple logic
        num_match = 0.0
        if p_feat['numerics'] and c_feat['numerics']:
            # Simple heuristic: does candidate contain a number from prompt?
            matches = [n for n in c_feat['numerics'] if any(abs(n - p) < 1e-6 for p in p_feat['numerics'])]
            num_match = min(1.0, len(matches) / max(1, len(c_feat['numerics'])))
        elif not p_feat['numerics'] and not c_feat['numerics']:
            num_match = 1.0 # Neutral if no numbers involved
            
        x = np.array([
            c_feat['negations'],
            c_feat['comparatives'],
            c_feat['conditionals'],
            c_feat['causals'],
            num_match,
            c_feat['quantifiers']
        ], dtype=float)
        
        # Normalize features slightly to prevent explosion
        x = x / (np.sum(x) + 1e-6) * 5.0 

        # Initialize weights (lambda) for MaxEnt
        lambdas = np.zeros_like(x)
        error_sum = np.zeros_like(x)
        prev_error = np.zeros_like(x)
        
        # Target: We want high belief if features align logically. 
        # Since we don't have ground truth labels during inference, we simulate 
        # a "consistency" target where logical coherence yields y=1.
        # Heuristic: If candidate repeats prompt logic keywords, target is higher.
        logic_overlap = 0
        if p_feat['has_logic']:
            logic_overlap = 0.5 + 0.5 * (min(c_feat['has_logic'], p_feat['has_logic']) / max(1, p_feat['has_logic']))
        else:
            logic_overlap = 0.5 # Default uncertainty

        reasoning_steps = []
        
        # PID Control Loop for Weight Adjustment
        for t in range(self.steps):
            # MaxEnt Probability: P(x) ~ exp(sum(lambda * f))
            # Logits = dot(lambdas, x)
            logits = np.dot(lambdas, x)
            p_belief = self._sigmoid(logits)
            
            # Error signal: Target (logic_overlap) - Current Belief
            error = logic_overlap - p_belief
            
            # PID Terms
            P_term = self.Kp * error
            error_sum += error
            I_term = self.Ki * error_sum
            D_term = self.Kd * (error - prev_error)
            
            # Update weights
            lambdas += (P_term + I_term + D_term) * x * 0.1 # Scaling factor for stability
            
            prev_error = error
            reasoning_steps.append(f"Step {t+1}: Belief={p_belief:.3f}, Error={error:.3f}")

        final_score = float(self._sigmoid(np.dot(lambdas, x)))
        
        # Structural Bonus/Penalty
        if p_feat['numerics'] and c_feat['numerics']:
            # If numbers exist, strict numeric check overrides probabilistic guess
            if num_match == 1.0:
                final_score = min(1.0, final_score + 0.2)
            else:
                final_score = max(0.0, final_score - 0.3)

        reason_str = f"Logical consistency score: {final_score:.4f}. " + "; ".join(reasoning_steps[-2:])
        return final_score, reason_str

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        scores = []
        
        # Phase 1: Compute raw scores
        for cand in candidates:
            score, reason = self._run_inference(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
            scores.append(score)
            
        # Phase 2: Tie-breaking with NCD if scores are too close
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                if abs(results[i]['score'] - results[j]['score']) < 0.01:
                    # Use NCD as tiebreaker
                    ncd_i = self._compute_ncd(prompt, results[i]['candidate'])
                    ncd_j = self._compute_ncd(prompt, results[j]['candidate'])
                    # Lower NCD (more similar/compressible together) gets slight boost? 
                    # Actually, for QA, usually specific answers are shorter. 
                    # Let's boost the one with better structural match (higher score) slightly more if NCD is ambiguous
                    # But per instructions: NCD is tiebreaker. 
                    # Heuristic: Prefer candidate with lower NCD to prompt context if scores equal?
                    # Or prefer candidate that compresses well with prompt (high relevance).
                    if ncd_i < ncd_j:
                        results[i]['score'] += 0.005
                    else:
                        results[j]['score'] += 0.005

        # Sort descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        score, _ = self._run_inference(prompt, answer)
        return max(0.0, min(1.0, score))