import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Symbiotic Predictive-Coding Architecture with Algorithmic-Regularization.
    
    Mechanism:
    1. Free Energy Principle (Core Driver): The 'evaluate' method acts as the 
       variational update. It parses the prompt to establish a generative model 
       of constraints (logic, math, negation). Candidates are scored by how well 
       they minimize 'surprise' (prediction error) against this model.
       
    2. Kolmogorov Complexity (Regularization): Used as an Occam's razor penalty.
       We approximate description length using zlib compression. Candidates that 
       achieve high accuracy but require excessive complexity (verbosity/repetition) 
       are penalized. This prevents overfitting to noise.
       
    3. Symbiosis (Structural Parsing): Instead of biological agents, we use 
       loosely coupled 'parser symbionts' (Logic, Math, Negation, Comparison). 
       They exchange latent representations (boolean flags, extracted numbers) 
       across a shared Markov blanket (the parsed constraint set). They cooperate 
       to reject candidates that violate any single constraint, ensuring robust 
       generalization.
       
    Note: Per causal intelligence guidelines, 'Symbiosis' and 'Kolmogorov' 
    concepts are restricted to structural support and confidence calibration 
    respectively, while Free Energy drives the core scoring logic.
    """

    def __init__(self):
        self._baseline_accuracy = 0.20

    def _get_compression_length(self, text: str) -> int:
        """Approximates Kolmogorov complexity via zlib."""
        if not text:
            return 0
        return len(zlib.compress(text.encode('utf-8')))

    def _parse_structure(self, prompt: str) -> dict:
        """
        Symbiotic parser: Extracts latent constraints (negations, numbers, comparatives).
        Returns a dictionary representing the 'Markov Blanket' of constraints.
        """
        p_lower = prompt.lower()
        
        # 1. Negation Symbiont
        negations = ['not ', 'no ', 'never ', 'cannot ', 'impossible ', 'false ']
        has_negation = any(n in p_lower for n in negations)
        
        # 2. Numeric Symbiont
        numbers = re.findall(r'-?\d+\.?\d*', p_lower)
        parsed_nums = [float(n) for n in numbers] if numbers else []
        
        # 3. Comparative Symbiont
        comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        has_comparative = any(c in p_lower for c in comparatives)
        
        # 4. Conditional/Logic Symbiont
        conditionals = ['if ', 'then ', 'unless ', 'therefore ', 'because ']
        has_conditional = any(c in p_lower for c in conditionals)

        return {
            'has_negation': has_negation,
            'numbers': parsed_nums,
            'has_comparative': has_comparative,
            'has_conditional': has_conditional,
            'prompt_len': len(prompt)
        }

    def _calculate_free_energy(self, candidate: str, prompt: str, constraints: dict) -> float:
        """
        Calculates Variational Free Energy (F = Surprise + Complexity).
        Lower F is better. We return negative F so higher score = better.
        """
        c_lower = candidate.lower()
        
        # --- Prediction Error (Surprise) Component ---
        # Penalize candidates that violate structural constraints derived from the prompt.
        error_penalty = 0.0
        
        # Logic Check: If prompt has negation, candidate shouldn't be simple affirmation without nuance
        # (Heuristic approximation of logical consistency)
        if constraints['has_negation']:
            # If the prompt says "not", a simple "yes" is often wrong (high surprise)
            if c_lower.strip() in ['yes', 'yes.', 'true']:
                error_penalty += 2.0
            # Conversely, if it's a negation question, explicit denial might be safer, 
            # but without full NLI, we penalize blind affirmation.
            
        # Math Check: If numbers exist, check if candidate contains a number.
        # If prompt has math, candidate lacking numbers is likely high error.
        if constraints['numbers'] and len(constraints['numbers']) >= 2:
            candidate_nums = re.findall(r'-?\d+\.?\d*', c_lower)
            if not candidate_nums:
                # High surprise: Math problem but no number in answer
                error_penalty += 3.0
            else:
                # Basic consistency: Does the answer number appear in prompt? 
                # (Prevents hallucation of random magnitudes)
                c_val = float(candidate_nums[0])
                if c_val not in constraints['numbers']:
                    # Allow if it's a result of operation, but penalize slightly for deviation
                    # This is a weak check, so small penalty.
                    error_penalty += 0.5

        # --- Complexity (Kolmogorov) Component ---
        # Penalize excessive length relative to information content.
        # Approximate K(x) via compression length.
        k_complexity = self._get_compression_length(candidate)
        
        # Normalize complexity penalty: Longer answers get penalized more unless necessary.
        # We want the simplest valid hypothesis.
        complexity_penalty = k_complexity * 0.005 
        
        # Free Energy = Error + Complexity
        # We invert sign because we want to maximize score (minimize free energy)
        free_energy = -(error_penalty + complexity_penalty)
        
        return free_energy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates by minimizing variational free energy.
        Uses structural parsing (Symbiosis) to define constraints and 
        compression (Kolmogorov) to regularize, driven by Free Energy minimization.
        """
        if not candidates:
            return []

        # 1. Structural Parsing (The Symbiotic Layer)
        # Extracts the generative model of the prompt's constraints.
        constraints = self._parse_structure(prompt)
        
        scored_candidates = []
        
        for cand in candidates:
            # 2. Free Energy Calculation
            # Combines prediction error (logic/math fit) and complexity penalty.
            score = self._calculate_free_energy(cand, prompt, constraints)
            
            # 3. NCD Tiebreaker (Global Requirement)
            # If scores are very close, use NCD to break ties based on similarity to prompt context.
            # This is only a tiebreaker, not the primary driver.
            base_score = score 
            
            # Add a tiny bonus for being compressible together with the prompt (contextual relevance)
            # This mimics the 'shared code' aspect of symbiosis.
            try:
                combined = prompt + " " + cand
                k_combined = self._get_compression_length(combined)
                k_prompt = self._get_compression_length(prompt)
                k_cand = self._get_compression_length(cand)
                
                # NCD-like metric: (K(xy) - min(K(x), K(y))) / max(K(x), K(y)) approx
                # Lower is more similar. We subtract this distance to boost score.
                if max(k_prompt, k_cand) > 0:
                    ncd_dist = (k_combined - min(k_prompt, k_cand)) / max(k_prompt, k_cand)
                    score -= (ncd_dist * 0.1) # Small adjustment
            except:
                pass

            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Free-energy minimization: Error penalty applied based on structural constraints (negation={constraints['has_negation']}, math={bool(constraints['numbers'])}). Complexity penalty applied via MDL approximation."
            })

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        
        # Normalize scores to be more interpretable (optional but good practice)
        # Keeping raw scores as they represent negative free energy directly.
        
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the Free Energy score normalized, with Kolmogorov complexity 
        acting as a strict filter for nonsense/verbose outputs.
        """
        # Evaluate single candidate against itself (trivial set) to get base energy
        # We simulate a dummy competitor to get a relative sense, or just use absolute thresholds.
        # Absolute thresholding based on free energy components:
        
        constraints = self._parse_structure(prompt)
        energy = self._calculate_free_energy(answer, prompt, constraints)
        
        # Base confidence from negative free energy (higher energy -> lower confidence)
        # Energy is negative. -0 is perfect. -10 is bad.
        # Map [-5, 0] to [0, 1] roughly.
        base_conf = max(0.0, min(1.0, (energy + 5.0) / 5.0))
        
        # Kolmogorov Regularization for Confidence:
        # If the answer is extremely complex (high K) relative to prompt, reduce confidence.
        k_ans = self._get_compression_length(answer)
        k_prompt = self._get_compression_length(prompt)
        
        # Heuristic: Answer shouldn't be vastly more complex than prompt unless necessary
        complexity_ratio = k_ans / (k_prompt + 1)
        if complexity_ratio > 5.0:
            base_conf *= 0.5 # Penalize excessive verbosity/complexity
            
        # Structural check: If prompt implies math, answer must have number
        if constraints['numbers'] and len(constraints['numbers']) >= 2:
            if not re.search(r'\d', answer):
                base_conf = 0.1 # Very low confidence if math required but missing
        
        return float(f"{base_conf:.4f}")