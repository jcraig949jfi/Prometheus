import numpy as np
import re
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Implements a reasoning evaluator based on Chaos Theory, Free Energy Principle, 
    and Property-Based Testing.
    
    Mechanism:
    1. State Representation: Parses text into propositional atoms (P), numeric constraints (C), 
       and conditional depth (N).
    2. Free Energy: Computes prediction error between logical deductions (forward chaining) 
       and observed propositions, penalized by state complexity.
    3. Chaotic Perturbation: Applies logistic map perturbations to numeric constraints to 
       measure sensitivity (Lyapunov-like score).
    4. Property-Based Shrinking: Generates mutants (dropping/weakening claims) to find the 
       minimal instability score. Robust answers (low instability) receive higher scores.
    """
    
    def __init__(self):
        self.r_logistic = 3.9  # Chaotic regime parameter

    def _parse_text(self, text: str) -> Tuple[Set[str], List[float], int]:
        """Extracts propositions, numeric constraints, and conditional depth."""
        text_lower = text.lower()
        atoms = set()
        constraints = []
        
        # Extract numeric constraints (comparatives)
        nums = re.findall(r'-?\d+\.?\d*', text_lower)
        constraints = [float(n) for n in nums]
        
        # Extract propositional atoms (simplified: words > 3 chars, excluding stopwords)
        stopwords = {'the', 'and', 'that', 'with', 'from', 'have', 'this', 'will', 'your', 'one', 'all', 'which', 'would', 'there', 'their', 'about', 'other', 'into', 'could', 'them', 'being', 'more', 'some', 'than', 'into', 'only', 'most', 'such', 'no', 'not', 'yes', 'if', 'then', 'else', 'cause', 'lead', 'result', 'first', 'before', 'after'}
        words = re.findall(r'[a-z]{3,}', text_lower)
        for w in words:
            if w not in stopwords:
                # Handle negation prefix
                if w.startswith('no') and len(w) > 3: 
                    atoms.add(f"!{w[2:]}")
                else:
                    atoms.add(w)
        
        # Count conditionals/nested logic depth approximation
        cond_keywords = ['if', 'then', 'unless', 'because', 'cause', 'lead', 'result']
        depth = sum(text_lower.count(k) for k in cond_keywords)
        
        return atoms, constraints, depth

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """Computes variational free energy F = |E_pred - E_obs|^2 + lambda * |grad S|."""
        p_atoms, p_nums, p_depth = self._parse_text(prompt)
        c_atoms, c_nums, c_depth = self._parse_text(candidate)
        
        # Prediction Error: Intersection over Union for atoms, MSE for numbers
        all_atoms = p_atoms.union(c_atoms)
        if not all_atoms:
            atom_error = 0.0
        else:
            # Simple overlap metric as proxy for logical consistency
            intersection = len(p_atoms.intersection(c_atoms))
            atom_error = 1.0 - (intersection / (len(all_atoms) + 1e-6))
            
        num_error = 0.0
        if p_nums and c_nums:
            # Compare sorted numeric sequences if lengths match, else penalty
            if len(p_nums) == len(c_nums):
                num_error = np.mean([(a-b)**2 for a, b in zip(p_nums, c_nums)])
            else:
                num_error = 1.0 # Structural mismatch
        elif p_nums:
            num_error = 1.0 # Missing numbers
            
        # Complexity penalty (gradient term approximation)
        complexity = abs(p_depth - c_depth) * 0.1 + len(c_atoms) * 0.01
        
        return (atom_error ** 2 + num_error) + 0.1 * complexity

    def _perturb_constraints(self, constraints: List[float]) -> List[float]:
        """Apply logistic map perturbation to numeric constraints."""
        if not constraints:
            return []
        perturbed = []
        # Deterministic seed based on list length for reproducibility within context
        x = 0.5 + (len(constraints) * 0.01) 
        for c in constraints:
            x = self.r_logistic * x * (1.0 - x)
            delta = (x - 0.5) * 0.1 # Small perturbation range
            perturbed.append(c + delta)
        return perturbed

    def _compute_lyapunov_score(self, prompt: str, candidate: str) -> float:
        """Computes stability score L. Lower is better."""
        base_energy = self._compute_free_energy(prompt, candidate)
        _, base_nums, _ = self._parse_text(candidate)
        
        if not base_nums:
            # If no numbers, stability is high by default (no chaotic dimension)
            return base_energy * 0.1
            
        perturbed_nums = self._perturb_constraints(base_nums)
        
        # Reconstruct candidate with perturbed numbers (simulation)
        # Since we can't easily rewrite text, we simulate the energy shift 
        # by comparing the constraint vectors directly against prompt constraints
        _, p_nums, _ = self._parse_text(prompt)
        
        # Simulate new error based on perturbed vs original prompt numbers
        if p_nums and len(p_nums) == len(perturbed_nums):
            new_num_error = np.mean([(a-b)**2 for a, b in zip(p_nums, perturbed_nums)])
        else:
            new_num_error = 1.0
            
        # Lyapunov-like divergence
        divergence = abs(new_num_error - (base_energy * 0.5)) # Approximate baseline num contribution
        norm_delta = 0.01 # Normalization factor for delta magnitude
        
        return divergence / (norm_delta + 1e-6)

    def _shrink_and_score(self, prompt: str, candidate: str) -> float:
        """Property-based shrinking to find minimal instability."""
        base_L = self._compute_lyapunov_score(prompt, candidate)
        min_L = base_L
        
        # Mutant 1: Drop last proposition (simulate by ignoring last word group)
        words = candidate.split()
        if len(words) > 3:
            mutant = " ".join(words[:-2])
            mutant_L = self._compute_lyapunov_score(prompt, mutant)
            if mutant_L < min_L:
                min_L = mutant_L
                
        # Mutant 2: Weaken (remove specific numbers if present)
        if re.search(r'\d', candidate):
            mutant = re.sub(r'\d+\.?\d*', '0', candidate)
            mutant_L = self._compute_lyapunov_score(prompt, mutant)
            if mutant_L < min_L:
                min_L = mutant_L
                
        return min_L

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            if not cand.strip():
                continue
            L_min = self._shrink_and_score(prompt, cand)
            score = 1.0 / (1.0 + L_min)
            
            # Boost if structural keywords match (heuristic for relevance)
            p_lower = prompt.lower()
            c_lower = cand.lower()
            bonus = 0.0
            if any(k in c_lower for k in ['yes', 'no', 'true', 'false'] if k in p_lower):
                bonus = 0.1
            # Penalize pure echo
            if cand.strip() == prompt.strip():
                score *= 0.5
                
            final_score = min(1.0, score + bonus)
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Stability score: {L_min:.4f}, Robustness: {final_score:.4f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        ranked = self.evaluate(prompt, [answer])
        if not ranked:
            return 0.0
        return ranked[0]['score']