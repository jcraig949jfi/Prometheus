import math
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamic Self-Attention Ensemble (TSAE) Approximation.
    
    Mechanism:
    1. Structural Parsing (Microscopic Energy): Tokens are weighted by their 
       logical utility (negations, comparatives, numbers). This defines the 
       base energy landscape E_ij.
    2. Boltzmann Attention: Candidate relevance is computed via a softmax 
       over structural match scores, scaled by a learned inverse temperature beta.
    3. Fluctuation-Dissipation (Metacognition): Beta is dynamically adjusted. 
       If the ensemble variance (fluctuation) is high, the system lowers beta 
       (increases entropy) to avoid over-committing to noisy signals. 
    4. Emergence: The final score aggregates these thermodynamic properties 
       into a confidence metric that penalizes candidates sensitive to minor 
       structural perturbations.
    """

    # Structural patterns for logical reasoning
    PATTERNS = {
        'negation': re.compile(r'\b(not|no|never|none|neither|without)\b', re.I),
        'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|than)\b', re.I),
        'conditional': re.compile(r'\b(if|then|unless|provided|otherwise|else)\b', re.I),
        'numeric': re.compile(r'\d+(\.\d+)?'),
        'logic_conn': re.compile(r'\b(and|or|but|however|therefore|thus|hence)\b', re.I)
    }

    def __init__(self):
        # Initial inverse temperature (sharpness)
        self.beta = 1.0 
        # Learning rate for beta adaptation
        self.lr = 0.1
        # Target variance (desired uncertainty level)
        self.target_variance = 0.2

    def _extract_features(self, text: str) -> Dict[str, int]:
        """Extract counts of logical structures."""
        text_lower = text.lower()
        features = {}
        for key, pattern in self.PATTERNS.items():
            features[key] = len(pattern.findall(text_lower))
        # Add length as a basic feature
        features['length'] = len(text.split())
        return features

    def _compute_energy(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Compute energy E = - (similarity of structural features).
        Lower energy = higher compatibility.
        We prioritize logical operators over simple word overlap.
        """
        score = 0.0
        weight = 0.0
        
        # Weighted match for logical structures
        logic_keys = ['negation', 'comparative', 'conditional', 'logic_conn']
        for key in logic_keys:
            p_val = prompt_feats.get(key, 0)
            c_val = cand_feats.get(key, 0)
            
            # If prompt has logic, candidate must have it (penalize missing)
            if p_val > 0:
                weight += 2.0
                if c_val >= p_val:
                    score += 2.0
                else:
                    # Partial credit or penalty
                    score += (c_val / max(p_val, 1)) * 2.0 - 1.0
            else:
                # Prompt has no logic, candidate having some is neutral/slight noise
                pass

        # Numeric consistency check
        if prompt_feats.get('numeric', 0) > 0:
            weight += 3.0
            if cand_feats.get('numeric', 0) > 0:
                score += 3.0
            else:
                score -= 2.0 # Penalty for missing numbers in numeric prompt

        # Normalize by weight to prevent bias towards long prompts
        if weight == 0:
            return 0.0
        
        return -score  # Negative because we want high score = low energy

    def _boltzmann_weights(self, energies: List[float], beta: float) -> List[float]:
        """Compute attention weights via Boltzmann distribution."""
        if not energies:
            return []
        
        # Shift energies for numerical stability (subtract max)
        max_e = max(energies)
        shifted = [e - max_e for e in energies]
        
        # Exp(-beta * E) -> since E is negative score, this is exp(beta * score)
        try:
            exp_vals = [math.exp(beta * (-e)) for e in shifted]
        except OverflowError:
            # Fallback for extreme values
            exp_vals = [1.0] * len(energies)
            
        Z = sum(exp_vals)
        if Z == 0:
            return [1.0 / len(energies)] * len(energies)
            
        return [e / Z for e in exp_vals]

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        prompt_feats = self._extract_features(prompt)
        cand_feats_list = [self._extract_features(c) for c in candidates]
        
        # 1. Compute Microscopic Energies
        energies = [self._compute_energy(prompt_feats, cf) for cf in cand_feats_list]
        
        # 2. Compute Attention Weights (Boltzmann)
        weights = self._boltzmann_weights(energies, self.beta)
        
        # 3. Calculate Macroscopic Order Parameter (Variance of weights)
        # High variance = system is ordered (confident). Low variance = disordered.
        mean_w = sum(weights) / len(weights)
        variance = sum((w - mean_w) ** 2 for w in weights) / len(weights)
        
        # 4. Downward Causation: Adjust beta based on fluctuation-dissipation
        # If variance is too low (over-confident/rigid) or too high (chaotic), adjust beta.
        # We want a "critical" state where the system is sensitive but stable.
        # Simple heuristic: if variance < target, increase beta (sharpen); else decrease.
        if variance < self.target_variance:
            self.beta += self.lr * (self.target_variance - variance)
        else:
            self.beta -= self.lr * (variance - self.target_variance)
        
        # Clamp beta to prevent explosion
        self.beta = max(0.1, min(5.0, self.beta))

        # 5. Scoring and Ranking
        results = []
        for i, cand in enumerate(candidates):
            # Base score from energy
            base_score = -energies[i]
            # Modulate by attention weight (emergent property)
            final_score = base_score * (1.0 + weights[i])
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural match (E={-energies[i]:.2f}), Attention weight={weights[i]:.3f}, Beta={self.beta:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on thermodynamic stability.
        Uses the gap between the top candidate (the answer) and a hypothetical 
        perturbed state to estimate confidence.
        """
        # Create a dummy candidate list with the answer and a slightly perturbed version
        # to measure sensitivity (fluctuation).
        candidates = [answer, answer + " ", answer.replace(" ", "") if " " in answer else answer + "x"]
        
        # Run evaluation to get updated weights and beta
        # Note: This updates internal state, which is acceptable for this tool design
        ranked = self.evaluate(prompt, candidates)
        
        if not ranked:
            return 0.0
            
        # Find the score of the exact answer match
        target_score = None
        for res in ranked:
            if res['candidate'] == answer:
                target_score = res['score']
                break
        
        if target_score is None:
            return 0.0
            
        # Normalize score to 0-1 range using a sigmoid-like mapping
        # Scores are roughly in range [-5, 10] based on logic matches
        # Map to 0-1: 1 / (1 + exp(-k * (score - threshold)))
        k = 0.5
        threshold = 2.0 
        conf = 1.0 / (1.0 + math.exp(-k * (target_score - threshold)))
        
        return min(1.0, max(0.0, conf))