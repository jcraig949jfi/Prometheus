import re
import math
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    A reasoning tool implementing the Free Energy Principle (FEP) for logical consistency,
    supported by Sensitivity Analysis for robustness. Property-Based Testing is restricted
    to the confidence wrapper to avoid negative synergy with FEP during scoring.
    
    Mechanism:
    1. Parse prompts/candidates into logical literals (negations, comparatives, conditionals).
    2. Construct a factor graph where clauses impose energy penalties on inconsistent truth assignments.
    3. Minimize Variational Free Energy (Energy - Entropy) via mean-field iteration to find optimal literal probabilities.
    4. Score based on minimized Free Energy (fit) and Sensitivity to weight perturbations (robustness).
    5. Use NCD only as a tiebreaker when structural signals are weak.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|only if|implies)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|leads to|results in|causes)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater than|less than|more than|fewer than|higher|lower)\b|[><=]', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|none|every|any|at least|at most)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+(?:\.\d+)?')
        }

    def _extract_literals(self, text: str) -> List[Tuple[str, bool]]:
        """Extract logical features as (feature_name, presence) tuples."""
        literals = []
        text_lower = text.lower()
        
        # Check structural presence
        literals.append(('has_negation', bool(self.patterns['negation'].search(text_lower))))
        literals.append(('has_conditional', bool(self.patterns['conditional'].search(text_lower))))
        literals.append(('has_causal', bool(self.patterns['causal'].search(text_lower))))
        literals.append(('has_comparative', bool(self.patterns['comparative'].search(text_lower))))
        literals.append(('has_quantifier', bool(self.patterns['quantifier'].search(text_lower))))
        
        # Numeric consistency check (simplified)
        nums = self.patterns['numbers'].findall(text)
        if nums:
            try:
                vals = [float(n) for n in nums]
                # Add literal indicating if numbers are sorted (heuristic for logical flow)
                is_sorted = all(vals[i] <= vals[i+1] for i in range(len(vals)-1))
                literals.append(('nums_sorted', is_sorted))
                literals.append(('num_count', len(vals) > 0))
            except ValueError:
                pass
                
        return literals

    def _build_factors(self, prompt_literals: Set[str], answer_literals: Set[str]) -> List[np.ndarray]:
        """
        Build factor arrays representing logical constraints between prompt and answer.
        Each factor is a truth table slice penalizing inconsistencies.
        """
        factors = []
        all_feats = list(set(prompt_literals) | set(answer_literals))
        if not all_feats:
            return [np.array([1.0, 0.0])] # Default penalty if no features
        
        # Create mapping for indexing
        feat_to_idx = {f: i for i, f in enumerate(all_feats)}
        n_feats = len(all_feats)
        
        # Factor 1: Prompt Negation implies Answer Negation (Modus Ponens approx)
        # If prompt has negation, answer should ideally reflect it or not contradict
        if 'has_negation' in feat_to_idx:
            idx = feat_to_idx['has_negation']
            # Simple factor: Prefer states where negation presence matches or is handled
            # Shape (2,) for single literal: [P(False), P(True)] -> penalize True if inconsistent
            # Here we just create a compatibility matrix placeholder logic
            pass

        # Simplified Factor Construction for Mean Field:
        # We create a factor for each feature type requiring consistency
        # Factor logic: Energy = 0 if consistent, 1 if inconsistent
        
        # 1. Consistency Factor: Features present in both or absent in both reduce energy
        # Represented as a vector over the joint space (simplified to unary potentials for mean-field)
        unary_potentials = np.ones(n_feats) 
        
        for feat in all_feats:
            idx = feat_to_idx[feat]
            in_prompt = feat in prompt_literals
            in_answer = feat in answer_literals
            
            # High energy (low prob) if prompt has it but answer doesn't (missing constraint)
            # Low energy if both have it or both lack it (though lacking is neutral)
            if in_prompt and not in_answer:
                unary_potentials[idx] = 0.2 # Penalty
            elif in_prompt and in_answer:
                unary_potentials[idx] = 1.0 # Reward
            else:
                unary_potentials[idx] = 0.8 # Neutral/Slight bias to simplicity
                
        factors.append(unary_potentials)
        return factors

    def _compute_free_energy(self, prompt: str, candidate: str) -> Tuple[float, float]:
        """
        Compute Variational Free Energy F = E - H.
        Returns (FreeEnergy, SensitivityScore).
        """
        p_lits_raw = self._extract_literals(prompt)
        c_lits_raw = self._extract_literals(candidate)
        
        # Convert to sets of present features
        p_feats = {name for name, val in p_lits_raw if val}
        c_feats = {name for name, val in c_lits_raw if val}
        
        # If no structural features found, return high energy (uncertain)
        if not p_feats and not c_feats:
            return 10.0, 0.0

        factors = self._build_factors(p_feats, c_feats)
        if not factors:
            return 10.0, 0.0
            
        n = len(factors[0]) # Number of literals/features
        if n == 0: return 10.0, 0.0

        # Initialize Mean-Field Q (probabilities of each literal being True)
        q = np.full(n, 0.5) 
        weights = np.ones(n) # Initialize weights to 1
        
        def calc_energy(q_vec, w_vec):
            # E = - sum(w * q * factor_potential)
            # Simplified: Energy is low when q aligns with factor potentials
            # Using the unary potentials from _build_factors as the "field"
            pot = factors[0]
            # Expected energy: sum over states weighted by Q
            # Approximation: E = - sum(w_i * q_i * log(pot_i)) 
            # To keep it simple and numpy-based: E = - dot(w, q * pot)
            return -np.dot(w_vec, q_vec * pot)

        def calc_entropy(q_vec):
            # H = - sum(q log q + (1-q) log (1-q))
            eps = 1e-10
            return -np.sum(q_vec * np.log(q_vec + eps) + (1 - q_vec) * np.log(1 - q_vec + eps))

        # Fixed-point iteration to minimize F
        prev_f = float('inf')
        for _ in range(50): # Max iterations
            # Update rule: q_i ~ exp(-E_i) / Z (Mean field update)
            # Simplified gradient step approximation for stability
            pot = factors[0]
            # Gradient of F w.r.t q: w * pot + log(q/(1-q)) = 0
            # q = sigmoid(w * pot)
            logits = weights * pot
            q_new = 1 / (1 + np.exp(-logits))
            q_new = np.clip(q_new, 1e-5, 0.995)
            
            q = q_new
            current_e = calc_energy(q, weights)
            current_h = calc_entropy(q)
            current_f = current_e - current_h
            
            if abs(prev_f - current_f) < 1e-4:
                break
            prev_f = current_f

        base_energy = current_f
        
        # Sensitivity Analysis: Perturb weights
        epsilon = 0.01
        sens_sum = 0.0
        for i in range(n):
            w_plus = weights.copy()
            w_minus = weights.copy()
            w_plus[i] += epsilon
            w_minus[i] -= epsilon
            
            # Recompute energy approx (skip full convergence for speed in sensitivity)
            # F(w+eps) - F(w-eps)
            e_plus = -np.dot(w_plus, q * factors[0])
            e_minus = -np.dot(w_minus, q * factors[0])
            sens_sum += ((e_plus - e_minus) / (2 * epsilon)) ** 2
            
        sensitivity = np.sqrt(sens_sum)
        
        return base_energy, sensitivity

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        if max(len_s1, len_s2) == 0: return 0.0
        return (len_both - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        lambda_param = 0.5
        
        # Pre-calculate prompt features to ensure we don't score based on prompt noise
        if not prompt.strip():
            return [{"candidate": c, "score": 0.0, "reasoning": "Empty prompt"} for c in candidates]

        for cand in candidates:
            free_energy, sensitivity = self._compute_free_energy(prompt, cand)
            
            # Score formulation: -F + lambda * (1 - S/(S+1))
            # Lower F is better (higher score). Lower S is better (higher score).
            robust_term = 1.0 - (sensitivity / (sensitivity + 1.0))
            score = -free_energy + lambda_param * robust_term
            
            # NCD Tiebreaker: If structural signal is weak (high energy), boost via NCD
            # Heuristic: If free_energy > threshold (meaning poor logical fit), use NCD to rank similarity
            if free_energy > 5.0: 
                ncd_val = self._ncd(prompt, cand)
                # NCD 0=identical, 1=different. We want high score for similar.
                score += (1.0 - ncd_val) * 0.5 

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"FreeEnergy={free_energy:.4f}, Sensitivity={sensitivity:.4f}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses Property-Based Testing concept here (as per instructions: restrict PBT to confidence wrapper).
        Generates minimal perturbations to check stability.
        """
        base_score_data = self.evaluate(prompt, [answer])
        if not base_score_data:
            return 0.0
            
        base_score = base_score_data[0]['score']
        
        # Property-Based Testing: Shrinking loop simulation
        # We simulate "falsification" by checking if small textual changes drastically drop the score.
        # Since we can't easily flip bits in text, we test robustness by removing words.
        words = answer.split()
        if len(words) <= 1:
            # Cannot shrink further, rely on base score normalization
            return min(1.0, max(0.0, (base_score + 10) / 20.0)) # Rough normalization
            
        min_score = base_score
        for i in range(len(words)):
            # Create a "shrunk" version by removing one word
            shrunk_words = words[:i] + words[i+1:]
            shrunk_ans = " ".join(shrunk_words)
            if not shrunk_ans.strip():
                continue
                
            shrunk_res = self.evaluate(prompt, [shrunk_ans])
            if shrunk_res:
                s = shrunk_res[0]['score']
                if s < min_score:
                    min_score = s
        
        # If the score drops significantly when shrinking, confidence is lower.
        # If the score remains high (or base is high), confidence is high.
        # Normalize to 0-1 range assuming typical scores are between -15 and 5
        normalized_conf = (base_score + 10) / 15.0
        penalty = (base_score - min_score) * 0.1
        
        final_conf = normalized_conf - penalty
        return float(min(1.0, max(0.0, final_conf)))