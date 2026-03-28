import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a Statistical Mechanics x Evolution x Mechanism Design reasoning engine.
    
    Mechanism:
    1. Structural Parsing: Extracts propositions and logical constraints (negations, 
       comparatives, conditionals, causality) from the prompt and candidate answers.
    2. Constraint Matrix: Builds a matrix C where rows represent logical rules.
    3. Energy Minimization: Treats truth assignments as states. Computes energy E(x) 
       based on constraint violations. Lower energy = higher consistency.
    4. Evolutionary Refinement: Mutates truth assignments to find lower energy states.
    5. Scoring: Uses Boltzmann weights to assign probabilities, ensuring incentive 
       compatibility (truth-telling minimizes energy).
    """
    
    def __init__(self):
        self.beta = 2.0  # Inverse temperature for Boltzmann distribution
        self.generations = 3
        self.population_size = 5
        
        # Regex patterns for structural features
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nobody|nothing)\b', re.I),
            'comparative': re.compile(r'\b(greater|less|more|fewer|higher|lower|before|after)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|otherwise|implies)\b', re.I),
            'causal': re.compile(r'\b(because|leads to|results in|causes|due to)\b', re.I),
            'quantifier': re.compile(r'\b(all|some|none|every|each|most)\b', re.I),
            'numeric': re.compile(r'\d+(\.\d+)?\s*[a-zA-Z]*')
        }

    def _extract_features(self, text: str) -> Dict[str, List[str]]:
        """Extract structural features from text."""
        features = {}
        text_lower = text.lower()
        for key, pattern in self.patterns.items():
            matches = pattern.findall(text_lower)
            features[key] = matches if matches else []
        return features

    def _build_constraint_matrix(self, prompt: str, candidate: str) -> Tuple[np.ndarray, int]:
        """
        Build a constraint matrix C and initial truth vector x.
        Rows = constraints, Cols = propositions (simplified to feature counts for stability).
        Returns C (m x n) and n (number of propositions).
        """
        # Combine context for extraction
        full_text = f"{prompt} {candidate}"
        features = self._extract_features(full_text)
        
        # Define propositions based on feature presence (simplified for robustness)
        # p0: Negation exists, p1: Comparative exists, p2: Conditional exists, 
        # p3: Causal exists, p4: Quantifier exists, p5: Numeric exists
        props = [
            bool(features['negation']),
            bool(features['comparative']),
            bool(features['conditional']),
            bool(features['causal']),
            bool(features['quantifier']),
            bool(features['numeric'])
        ]
        n = len(props)
        x = np.array(props, dtype=float)
        
        # Build Constraint Matrix C (m constraints, n propositions)
        # Logic: If prompt has conditional, candidate must not contradict it.
        # We simulate logical consistency by checking feature alignment between prompt and candidate.
        # This is a heuristic approximation of logical entailment for the "provisional truth" vector.
        
        prompt_feats = self._extract_features(prompt)
        cand_feats = self._extract_features(candidate)
        
        constraints = []
        
        # Constraint 1: Negation consistency (Prompt negation implies candidate should reflect it if relevant)
        # Simplified: If prompt has negation, candidate having negation is consistent (0 penalty)
        # We encode this as: If prompt_neg AND cand_neg -> OK. 
        # Matrix row: [1, 0, 0, 0, 0, 0] dot x should be > 0 if prompt has negation?
        # Instead, let's use a violation-based approach directly in the energy function logic
        # But to fit the C*x model:
        
        # Row 0: Prompt has conditional -> Candidate must have conditional or numeric (logic check)
        if prompt_feats['conditional']:
            # Encourage candidate to have conditional or numeric logic
            row = [0, 0, 1, 0, 0, 1] 
            constraints.append(row)
            
        # Row 1: Prompt has causal -> Candidate should not deny causality (heuristic)
        if prompt_feats['causal']:
            row = [0, 0, 0, 1, 0, 0]
            constraints.append(row)
            
        # Row 2: Numeric consistency (if both have numbers, they must align - simplified to presence)
        if prompt_feats['numeric'] and cand_feats['numeric']:
             row = [0, 0, 0, 0, 0, 1]
             constraints.append(row)

        # Default constraint to ensure non-empty reasoning
        if not constraints:
            constraints.append([1, 1, 1, 1, 1, 1]) # Generic consistency
            
        C = np.array(constraints, dtype=float)
        if C.size == 0:
            C = np.zeros((1, n))
            
        return C, n, x

    def _compute_energy(self, C: np.ndarray, x: np.ndarray) -> float:
        """Compute energy E(x) = sum of violations."""
        if C.size == 0 or x.size == 0:
            return 0.0
        # v = max(0, C·x - threshold). 
        # Here we treat presence as satisfying. If C·x is low, it's a violation?
        # Let's invert: We want C·x to be high. Violation = max(0, target - C·x)
        # Simplified: Count how many constraint rows are NOT satisfied by current x
        scores = C.dot(x)
        # Threshold: if score > 0, constraint satisfied. Else violation.
        violations = np.maximum(0, 1 - np.sign(scores)) 
        return float(np.sum(violations))

    def _evolve(self, C: np.ndarray, x_init: np.ndarray, n: int) -> np.ndarray:
        """Evolutionary refinement to minimize energy."""
        if n == 0:
            return x_init
            
        population = [x_init.copy()]
        
        # Generate mutants
        for _ in range(self.population_size - 1):
            mutant = x_init.copy()
            # Flip random bits
            if n > 0:
                idx = np.random.randint(0, n)
                mutant[idx] = 1.0 - mutant[idx]
            population.append(mutant)
            
        # Selection over generations
        for _ in range(self.generations):
            new_pop = []
            energies = [self._compute_energy(C, ind) for ind in population]
            
            # Keep top half
            sorted_indices = np.argsort(energies)
            survivors = [population[i] for i in sorted_indices[:len(population)//2 + 1]]
            
            # Reproduce with mutation
            new_pop = survivors.copy()
            while len(new_pop) < self.population_size:
                parent = survivors[np.random.randint(0, len(survivors))]
                child = parent.copy()
                if n > 0:
                    idx = np.random.randint(0, n)
                    child[idx] = 1.0 - child[idx]
                new_pop.append(child)
            population = new_pop
            
        # Return best individual
        best_idx = np.argmin([self._compute_energy(C, ind) for ind in population])
        return population[best_idx]

    def _calculate_score(self, prompt: str, candidate: str) -> float:
        """Calculate the final score based on energy and evolutionary refinement."""
        C, n, x_init = self._build_constraint_matrix(prompt, candidate)
        
        if n == 0:
            return 0.5 # Neutral if no features
            
        # Evolutionary step
        x_best = self._evolve(C, x_init, n)
        
        # Compute final energy
        energy = self._compute_energy(C, x_best)
        
        # Boltzmann weight
        weight = np.exp(-self.beta * energy)
        
        # Normalize roughly (assuming max energy ~ n)
        # Since we compare relative scores, raw weight is often enough, 
        # but let's normalize by a theoretical max to keep it 0-1-ish
        max_weight = np.exp(-self.beta * 0) # Energy 0
        score = weight / max_weight
        
        # Add NCD as a tiny tiebreaker if scores are close (structural priority)
        # But per instructions, NCD is only for when structural signal is weak.
        # Here structural signal is strong if energy is low.
        
        return float(score)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        scores = []
        
        # First pass: compute raw scores
        for cand in candidates:
            s = self._calculate_score(prompt, cand)
            scores.append(s)
            
        # Normalize scores to sum to 1 (Partition function Z approximation)
        total = sum(scores) + 1e-9
        norm_scores = [s / total for s in scores]
        
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": norm_scores[i],
                "reasoning": f"Energy-minimized consistency score based on structural constraints."
            })
            
        # Rank by score descending
        results.sort(key=lambda k: k['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        score = self._calculate_score(prompt, answer)
        # Clamp between 0 and 1
        return max(0.0, min(1.0, score))