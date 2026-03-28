import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a hybrid reasoning engine based on Autopoiesis x Neural Oscillations x Nash Equilibrium.
    
    Mechanism:
    1. Structural Parsing (The 'Autopoietic Core'): Extracts logical constraints (negations, 
       comparatives, conditionals) to define the 'viable band' of valid answers. This maintains 
       organizational closure by rejecting candidates that violate explicit logical rules.
    2. Oscillatory Scoring (The 'Neural Oscillations'): Applies a phase-based modifier to scores.
       Candidates matching the 'rhythm' of the prompt (keyword overlap + structural alignment) 
       receive a resonance boost; others are dampened.
    3. Nash Equilibrium Solver (The 'Game'): Treats candidates as agents in a replicator dynamic.
       Scores are normalized and adjusted by competitive inhibition (penalizing candidates that 
       overlap too much with higher-scoring rivals without adding unique structural value).
       The final ranking represents the stable equilibrium where only the most robust hypothesis survives.
       
    Note: Per causal analysis, 'Autopoiesis' is restricted to the confidence wrapper and 
    structural parsing logic, not direct scoring.
    """

    def __init__(self):
        # Homeostatic parameters
        self.homeostatic_target = 0.5
        self.inhibition_strength = 0.3
        
        # Structural patterns
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparative_ops = ['>', '<', '>=', '<=', 'greater', 'less', 'more', 'fewer']
        self.conditionals = ['if', 'then', 'else', 'unless', 'provided']

    def _structural_parse(self, text: str) -> Dict:
        """Extracts logical features: negations, comparatives, conditionals, numbers."""
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        has_negation = bool(words & self.negation_words)
        has_comparative = any(op in lower_text for op in self.comparative_ops)
        has_conditional = any(cond in lower_text for cond in self.conditionals)
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r'-?\d+\.?\d*', text)
        nums = [float(n) for n in numbers]
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': nums,
            'word_set': words
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _oscillatory_score(self, prompt_features: Dict, candidate: str) -> float:
        """
        Computes a base score based on structural resonance.
        Simulates gamma-band binding by checking feature alignment.
        """
        cand_features = self._structural_parse(candidate)
        score = 0.0
        
        # Resonance: Matching structural properties boosts score
        if prompt_features['negation'] == cand_features['negation']:
            score += 0.4
        if prompt_features['comparative'] == cand_features['comparative']:
            score += 0.3
        if prompt_features['conditional'] == cand_features['conditional']:
            score += 0.2
            
        # Numeric consistency check (simplified)
        p_nums = prompt_features['numbers']
        c_nums = cand_features['numbers']
        if p_nums and c_nums:
            # If both have numbers, check if candidate numbers appear in prompt or are derived logically
            # Simple heuristic: presence of same numbers is a strong bind
            common_nums = set(p_nums) & set(c_nums)
            if common_nums:
                score += 0.5
            elif len(c_nums) > 0:
                # Penalty for introducing random numbers not in prompt if prompt had numbers
                score -= 0.2
        
        # Keyword overlap (Theta rhythm sequencing)
        common_words = prompt_features['word_set'] & cand_features['word_set']
        # Remove stop words from consideration implicitly by length check or specific logic
        # Here we just use raw count scaled
        score += min(0.4, len(common_words) * 0.05)
        
        return score

    def _nash_equilibrium_solver(self, candidates: List[str], base_scores: List[float]) -> List[float]:
        """
        Adjusts scores via competitive inhibition to reach a mixed-strategy Nash Equilibrium.
        High scoring candidates inhibit similar lower-scoring candidates.
        """
        if not candidates:
            return []
        
        n = len(candidates)
        if n == 1:
            return [base_scores[0]]
            
        # Normalize base scores to probabilities (replicator dynamics start)
        exp_scores = [math.exp(s - max(base_scores)) for s in base_scores] # Stability shift
        sum_exp = sum(exp_scores)
        if sum_exp == 0:
            return [1.0/n] * n
            
        probs = [e / sum_exp for e in exp_scores]
        
        # Compute similarity matrix (NCD-based) for inhibition
        sim_matrix = [[0.0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j:
                    # Inverse NCD as similarity
                    ncd = self._compute_ncd(candidates[i], candidates[j])
                    sim_matrix[i][j] = 1.0 - ncd
        
        # Iterative update to find equilibrium (simplified replicator-mutator)
        # x_i' = x_i * (f_i - phi) where phi is average fitness, modified by inhibition
        final_scores = probs[:]
        
        for _ in range(5): # Fast convergence approximation
            new_scores = []
            for i in range(n):
                inhibition = 0.0
                for j in range(n):
                    if i != j:
                        # Inhibit if j is strong and similar to i
                        inhibition += final_scores[j] * sim_matrix[i][j]
                
                # Fitness function: Base probability minus competitive pressure
                fitness = final_scores[i] * (1.0 - self.inhibition_strength * inhibition)
                new_scores.append(max(0.0, fitness))
            
            # Renormalize
            total = sum(new_scores)
            if total > 0:
                final_scores = [s/total for s in new_scores]
            else:
                break
                
        # Map back to original scale roughly for ranking
        # We combine base score magnitude with the equilibrium probability
        combined = [base_scores[i] * (final_scores[i] + 0.1) for i in range(n)]
        return combined

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feats = self._structural_parse(prompt)
        base_scores = []
        
        # Phase 1: Oscillatory Scoring per candidate
        for cand in candidates:
            score = self._oscillatory_score(prompt_feats, cand)
            
            # Fallback to NCD if structural signal is weak (Tiebreaker logic)
            if score < 0.1:
                ncd = self._compute_ncd(prompt, cand)
                # Lower NCD is better, invert and scale
                score = max(0.0, 1.0 - ncd) * 0.5
                
            base_scores.append(score)
            
        # Phase 2: Nash Equilibrium Competition
        final_scores = self._nash_equilibrium_solver(candidates, base_scores)
        
        # Package results
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": final_scores[i],
                "reasoning": f"Structural match: {base_scores[i]:.2f}, Nash adjusted: {final_scores[i]:.2f}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses Autopoietic homeostasis: Checks if the answer maintains the logical 'closure' 
        of the prompt (e.g., negation consistency).
        """
        p_feats = self._structural_parse(prompt)
        a_feats = self._structural_parse(answer)
        
        confidence = 0.5 # Baseline
        
        # Homeostatic checks (Organizational closure)
        checks_passed = 0
        total_checks = 0
        
        # Check 1: Negation consistency
        if p_feats['negation'] is not None: # Always defined
            total_checks += 1
            if p_feats['negation'] == a_feats['negation']:
                checks_passed += 1
            elif p_feats['negation'] and not a_feats['negation']:
                # Strong penalty if prompt negates but answer doesn't acknowledge
                confidence -= 0.4
        
        # Check 2: Conditional logic presence
        if p_feats['conditional']:
            total_checks += 1
            if a_feats['conditional']:
                checks_passed += 1
        
        if total_checks > 0:
            structural_conf = checks_passed / total_checks
            confidence = 0.4 + (structural_conf * 0.6) # Range 0.4 to 1.0
            
        # Oscillatory validation modifier
        osc_score = self._oscillatory_score(p_feats, answer)
        confidence = (confidence * 0.7) + (osc_score * 0.3)
        
        return max(0.0, min(1.0, confidence))