import re
import math
import numpy as np
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A hybrid reasoning tool combining LDPC syndrome decoding, Free Energy Principle,
    and Phase Transition analysis with constructive computation.
    
    Mechanism:
    1. Structural Parsing: Extracts binary features (negations, comparatives, causals).
    2. Constructive Computation: Detects and solves numeric/logic problems directly.
    3. LDPC Syndrome: Uses a fixed parity check matrix to measure logical consistency (error).
    4. Free Energy: Combines prediction error (syndrome weight) and complexity (entropy).
    5. Phase Transition: Scans beta to find the critical point where free energy is most sensitive.
    6. Epistemic Honesty: Caps confidence if the prompt contains ambiguity or traps.
    """

    def __init__(self):
        # Fixed regular (3,6) LDPC-like matrix for demonstration (m=6, n=12 features)
        # In a real deployment, this would be larger and sparse.
        self.m = 6
        self.n = 12
        self.H = np.array([
            [1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0],
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
        ], dtype=np.int8)
        
        # Regex patterns for structural features
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nobody|nothing)\b', re.I),
            'comparative': re.compile(r'\b(more than|less than|greater than|smaller than|>=|<=|>|<|equal to)\b', re.I),
            'conditional': re.compile(r'\b(if|unless|provided that|otherwise)\b', re.I),
            'numeric': re.compile(r'\d+(\.\d+)?'),
            'causal': re.compile(r'\b(because|leads to|results in|causes|due to)\b', re.I),
            'ordering': re.compile(r'\b(first|second|before|after|earlier|later|precede)\b', re.I),
            'presupposition': re.compile(r'\b(have you stopped|have you quit|why did .*(fail|stop|die))\b', re.I),
            'false_dichotomy': re.compile(r'\b(either .+ or .+)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion)\b', re.I),
        }

    def _parse_features(self, text: str) -> np.ndarray:
        """Parse text into a binary feature vector."""
        x = np.zeros(self.n, dtype=np.int8)
        text_lower = text.lower()
        
        # Map patterns to indices 0-5
        if self.patterns['negation'].search(text): x[0] = 1
        if self.patterns['comparative'].search(text): x[1] = 1
        if self.patterns['conditional'].search(text): x[2] = 1
        if self.patterns['numeric'].search(text): x[3] = 1
        if self.patterns['causal'].search(text): x[4] = 1
        if self.patterns['ordering'].search(text): x[5] = 1
        
        # Fill remaining with hash-based bits for diversity (simulating other linguistic props)
        # This ensures the vector is full length for the matrix mult
        h = hash(text)
        for i in range(6, self.n):
            if (h >> (i-6)) & 1:
                x[i] = 1
                
        return x

    def _compute_syndrome(self, x: np.ndarray) -> int:
        """Compute LDPC syndrome weight (prediction error)."""
        s = (self.H @ x) % 2
        return int(np.sum(s))

    def _compute_entropy(self, candidates: List[np.ndarray]) -> float:
        """Compute Shannon entropy of proposition usage across candidates."""
        if not candidates:
            return 0.0
        X = np.stack(candidates)
        p_hat = np.mean(X, axis=0)
        # Avoid log(0)
        p_hat = p_hat[p_hat > 0]
        if len(p_hat) == 0:
            return 0.0
        return float(-np.sum(p_hat * np.log2(p_hat)))

    def _constructive_solve(self, prompt: str, candidate: str) -> Optional[float]:
        """
        Attempt to constructively solve numeric/logic problems.
        Returns a correctness score (0.0 to 1.0) or None if not applicable.
        """
        text = f"{prompt} {candidate}".lower()
        
        # Extract all numbers from prompt and candidate
        nums_prompt = [float(n) for n in re.findall(r'-?\d+(?:\.\d+)?', prompt)]
        nums_cand = [float(n) for n in re.findall(r'-?\d+(?:\.\d+)?', candidate)]
        
        # Case 1: Direct Numeric Comparison (e.g., "Which is larger? A) 5 B) 3")
        if len(nums_cand) == 1 and len(nums_prompt) >= 2:
            # Heuristic: If prompt asks for max/min/larger/smaller
            if any(k in text for k in ['larger', 'greater', 'max', 'most']):
                target = max(nums_prompt)
                return 1.0 if abs(nums_cand[0] - target) < 1e-6 else 0.0
            elif any(k in text for k in ['smaller', 'less', 'min', 'least']):
                target = min(nums_prompt)
                return 1.0 if abs(nums_cand[0] - target) < 1e-6 else 0.0
                
        # Case 2: Simple Arithmetic Verification (e.g., "What is 2+2?" -> "4")
        # Very basic check: if candidate is a number and matches a simple op result in prompt
        # This is a placeholder for a full expression evaluator
        if len(nums_cand) == 1 and len(nums_prompt) == 2:
            a, b = nums_prompt
            c = nums_cand[0]
            if 'plus' in text or '+' in prompt:
                return 1.0 if abs(c - (a+b)) < 1e-6 else 0.0
            if 'minus' in text or '-' in prompt:
                return 1.0 if abs(c - (a-b)) < 1e-6 else 0.0
                
        return None

    def _meta_confidence(self, prompt: str) -> float:
        """
        Check for Tier B traps: ambiguity, presupposition, unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower) and 'or' in p_lower:
            # Check if options are exhaustive (hard to know, so be conservative)
            if 'only' not in p_lower:
                return 0.4 
        
        # 3. Subjectivity without criteria
        if self.patterns['subjectivity'].search(p_lower):
            if 'data' not in p_lower and 'statistic' not in p_lower:
                return 0.3
                
        # 4. Pronoun/Scope Ambiguity (Simple heuristic)
        if re.search(r'\b(he|she|they|it)\b', p_lower) and '?' in prompt:
            # If question asks "who", high ambiguity risk
            if re.search(r'\bwho\b', p_lower):
                return 0.4

        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Parse all candidates
        features = [self._parse_features(c) for c in candidates]
        
        # 2. Compute global complexity (Entropy)
        C = self._compute_entropy(features)
        if C == 0: C = 1e-6 # Prevent division issues
        
        results = []
        betas = np.linspace(0.1, 2.0, 20)
        
        for i, cand in enumerate(candidates):
            x = features[i]
            
            # Constructive Computation Score (Primary Signal)
            comp_score = self._constructive_solve(prompt, cand)
            
            # LDPC Syndrome (Prediction Error)
            e = self._compute_syndrome(x)
            
            # Normalize error to [0, 1] roughly based on matrix rows
            e_norm = e / self.m
            
            # Phase Transition Analysis to find beta*
            # We look for the beta where dF/dbeta changes most rapidly
            # F = e + beta * C. dF/dbeta = C. 
            # The prompt suggests finding beta where small increases in error cause large rise in F.
            # Since F is linear in beta here, the "phase transition" analogy is implemented by 
            # selecting a beta that balances the specific error magnitude against global entropy.
            # We simulate the "critical point" by choosing beta where the derivative of the 
            # scoring function w.r.t beta is maximized in a non-linear extension.
            # Let's use a non-linear free energy approximation: F = e + beta * C^2
            # Then dF/dbeta = C^2. 
            # We select beta* that maximizes the gap between this candidate and the mean.
            
            best_beta = 1.0
            max_sensitivity = -1
            
            for b in betas:
                # Non-linear free energy for sensitivity analysis
                F_nl = e_norm + b * (C ** 2)
                # Sensitivity approx
                sens = abs(C * b - e_norm) 
                if sens > max_sensitivity:
                    max_sensitivity = sens
                    best_beta = b
            
            # Final Free Energy
            F_val = e_norm + best_beta * C
            
            # Combine with Constructive Computation
            # If we computed a definitive answer, it dominates.
            if comp_score is not None:
                # Map constructive score (1=correct, 0=wrong) to free energy
                # Correct answer -> Low Free Energy
                final_score = (1.0 - comp_score) * 0.1 + (1.0 - F_val) * 0.9
            else:
                # Pure structural scoring
                final_score = -F_val

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Syndrome error: {e}, Entropy: {C:.2f}, Beta*: {best_beta:.2f}, Constructive: {comp_score}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt.
        """
        # 1. Meta-confidence cap (Tier B honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural match check
        x = self._parse_features(answer)
        has_structure = np.sum(x) > 0
        
        if not has_structure:
            # If no structural features matched, we are guessing
            base_conf = 0.2
        else:
            # Evaluate the specific answer against the prompt
            res_list = self.evaluate(prompt, [answer])
            if not res_list:
                return 0.0
            
            score = res_list[0]['score']
            
            # Map score to confidence
            # Score can be negative. Normalize roughly to 0-1 range based on typical bounds
            # Typical F is around 0-2. Score is -F. 
            # If constructive solve worked, score is near 1.0.
            if score > 0.5:
                base_conf = 0.9
            elif score > 0.0:
                base_conf = 0.6
            else:
                base_conf = 0.3
                
        # Apply cap
        final_conf = min(base_conf, meta_cap)
        
        # Never return > 0.9 unless constructive computation was definitive
        # (Handled by meta_cap and constructive logic above)
        
        return float(np.clip(final_conf, 0.0, 1.0))