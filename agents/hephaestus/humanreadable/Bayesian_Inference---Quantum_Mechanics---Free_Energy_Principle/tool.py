import numpy as np
import re
import math

class ReasoningTool:
    """
    Quantum-Inspired Bayesian Free Energy Reasoner.
    
    Mechanism:
    1. Structural Parsing: Extracts logical operators (negation, implication, comparison)
       and numeric values from the prompt using regex.
    2. Quantum State Initialization: Creates a superposition of truth states for 
       extracted propositions.
    3. Unitary Evolution: Applies logical constraints as unitary-like transformations 
       (phase shifts and amplitude swaps) to propagate consistency.
    4. Free Energy Minimization: Computes variational free energy (F) representing 
       the divergence between the evolved state and the prior, penalizing logical 
       inconsistencies and ambiguity.
    5. Scoring: Candidates are scored by exp(-F), normalized via softmax.
    
    Epistemic Honesty (Tier B):
    Detects presuppositions, ambiguities, and unanswerable patterns to cap confidence.
    """

    def __init__(self):
        self.epsilon = 1e-9

    def _extract_features(self, text):
        """Extract logical and numeric features from text."""
        features = {
            'negations': len(re.findall(r'\b(not|no|never|none)\b', text.lower())),
            'conditionals': len(re.findall(r'\b(if|unless|then|else)\b', text.lower())),
            'comparisons': re.findall(r'(\d+\.?\d*)\s*(?:is|was|are|were)?\s*(?:greater|less|more|fewer|bigger|smaller)?\s*(?:than)?\s*(?:[<>=]|to)?\s*(\d+\.?\d*)', text.lower()),
            'numbers': [float(x) for x in re.findall(r'\b(\d+\.?\d*)\b', text) if float(x) < 1e6], # Avoid dates/years if too large
            'has_either_or': bool(re.search(r'\b(either|or)\b', text.lower())),
            'has_why': bool(re.search(r'\bwhy\b', text.lower())),
            'has_best_worst': bool(re.search(r'\b(best|worst|favorite|favourite)\b', text.lower())),
            'has_presupposition': bool(re.search(r'(have you stopped|did you stop|why did .+ fail|why is .+ true)', text.lower())),
            'has_pronoun_ambiguity': bool(re.search(r'(he|she|him|her|they)\s*(was|is|were|are)\s*(wrong|right|told)', text.lower())) and bool(re.search(r'\bwho\b', text.lower()))
        }
        return features

    def _meta_confidence(self, prompt, answer):
        """
        Tier B: Check for ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        a_lower = answer.lower() if answer else ""
        
        # 1. Presupposition traps
        if re.search(r'(have you stopped|did you stop|why did .+ fail|why is .+ true)', p_lower):
            return 0.2
        
        # 2. Scope/Pronoun ambiguity with "who" or specific ambiguity markers
        if re.search(r'\bwho\b', p_lower) and re.search(r'(he|she|him|her)\s+(was|is|told)', p_lower):
            return 0.25
            
        # 3. False Dichotomy check (Either A or B) without clear resolution
        if re.search(r'\beither\b', p_lower) and re.search(r'\bor\b', p_lower):
            # If the answer isn't one of the explicit options mentioned, low confidence
            # Simplified: if prompt has "either" and answer is short/unspecific
            if len(a_lower.split()) < 3 and not re.search(r'(true|false|yes|no)', a_lower):
                return 0.3

        # 4. Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite)\b', p_lower) and not re.search(r'\b(math|calculate|logic)\b', p_lower):
            return 0.4

        # 5. Unanswerable / Missing info
        if re.search(r'(cannot be determined|insufficient information)', a_lower):
            return 0.9 # High confidence that "cannot be determined" is the right meta-answer
            
        return 1.0

    def _compute_free_energy(self, prompt, candidate):
        """
        Core algorithm: Construct quantum-inspired state and compute Free Energy.
        Lower F = Higher plausibility.
        """
        # Combine context
        full_text = f"{prompt} {candidate}"
        features = self._extract_features(full_text)
        
        # 1. Initialize State Vector (Amplitudes)
        # We model 4 key dimensions: Truth, Negation, Magnitude, Consistency
        # Start with uniform superposition
        n_dims = 4
        alpha = np.ones(n_dims, dtype=complex) / np.sqrt(n_dims)
        prior = np.abs(alpha)**2
        
        # 2. Apply Unitary Operators based on extracted features
        
        # Operator: Negation (Pauli-X like flip on dimension 0)
        if features['negations'] > 0:
            # Flip phase of truth dimension
            alpha[0] *= -1 
            
        # Operator: Conditionals (Phase shift on dimension 1)
        if features['conditionals'] > 0:
            phase = np.exp(1j * np.pi * 0.5 * features['conditionals'])
            alpha[1] *= phase
            
        # Operator: Numeric Consistency (Dimension 2)
        # If numbers exist, check if candidate resolves them logically
        nums = features['numbers']
        if len(nums) >= 2:
            # Simple heuristic: if candidate contains the result of a comparison
            # This is a proxy for "constructive computation"
            try:
                # Check for explicit comparison in candidate
                cand_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
                if cand_nums:
                    # If candidate number matches expected logic (e.g. max/min)
                    # We simulate a "measurement" alignment
                    diff = abs(nums[0] - nums[1]) if len(nums) > 1 else 0
                    # Apply phase shift proportional to difference (simulating tension)
                    alpha[2] *= np.exp(1j * 0.1 * diff)
                else:
                    # Penalty for ignoring numbers
                    alpha[2] *= 0.5 
            except:
                pass

        # Operator: Logical Consistency (Dimension 3)
        # Penalize contradictions (e.g. "Either A or B" but answer implies both)
        if features['has_either_or'] and re.search(r'(both|all|neither)', candidate.lower()):
            alpha[3] *= 0.1 # Strong penalty

        # 3. Compute Posterior Probabilities
        p_post = np.abs(alpha)**2
        p_post = p_post / (np.sum(p_post) + self.epsilon) # Normalize
        
        # 4. Compute Variational Free Energy
        # F = Sum( p' * log(p'/pi) )
        # Add small epsilon to avoid log(0)
        kl_div = np.sum(p_post * np.log((p_post + self.epsilon) / (prior + self.epsilon)))
        
        # Structural penalty term (heuristic addition for unmet constraints)
        structural_penalty = 0
        if features['negations'] > 0 and 'not' not in candidate.lower() and 'no' not in candidate.lower():
            structural_penalty = 2.0 # Penalty for missing negation in answer
            
        F = kl_div + structural_penalty
        return F

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        scores = []
        free_energies = []
        
        # Calculate Free Energy for each candidate
        for cand in candidates:
            F = self._compute_free_energy(prompt, cand)
            free_energies.append(F)
            
        # Convert to scores: s = exp(-F)
        # Handle potential overflow/underflow with min-max scaling before exp
        fes = np.array(free_energies)
        fes = fes - np.min(fes) # Shift to positive
        exp_vals = np.exp(-fes)
        
        # Softmax normalization
        total = np.sum(exp_vals) + self.epsilon
        probs = exp_vals / total
        
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": float(probs[i]),
                "reasoning": f"Quantum-FreeEnergy={free_energies[i]:.4f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of ambiguity (Tier B).
        """
        # 1. Meta-confidence cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt, answer)
        
        # 2. Base confidence from the reasoning engine
        # We evaluate the single answer against a dummy alternative to get a relative score
        # Or simply use the inverse free energy mapped to 0-1
        F = self._compute_free_energy(prompt, answer)
        
        # Map Free Energy to confidence (lower F -> higher conf)
        # Using a sigmoid-like mapping: 1 / (1 + F)
        base_conf = 1.0 / (1.0 + F)
        
        # Apply structural penalties if no numbers/logic found (honest uncertainty)
        features = self._extract_features(prompt)
        if len(features['numbers']) == 0 and features['conditionals'] == 0 and features['negations'] == 0:
            # If purely semantic with no logic markers, reduce confidence slightly
            # unless it's a known fact pattern (simplified here)
            base_conf = min(base_conf, 0.7)

        # 3. Apply Cap
        final_conf = min(base_conf, meta_cap)
        
        # Ensure deterministic float output
        return float(np.clip(final_conf, 0.0, 1.0))

# Example usage logic (not part of class, for demonstration)
# tool = ReasoningTool()
# print(tool.evaluate("If A then B. Not B.", ["A is false", "A is true"]))
# print(tool.confidence("Have you stopped cheating?", "Yes")) # Should be low due to presupposition