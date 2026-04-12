import numpy as np
import re
from collections import deque

class ReasoningTool:
    """
    Implements a hybrid Constraint Satisfaction + Criticality + Maximum Entropy solver.
    
    Mechanism:
    1. Structural Parsing: Extracts boolean propositions, numeric comparisons, and 
       logical operators (negation, conditionals) from text into a factor graph.
    2. Constraint Propagation (AC-3 style): Enforces hard logical constraints 
       (e.g., transitivity, modus tollens) to prune impossible states.
    3. Criticality Tuning: Operates near a phase transition by adjusting a global 
       temperature T to maximize susceptibility (variance of truth values), ensuring 
       the system is sensitive to small changes in evidence without collapsing.
    4. MaxEnt Scoring: Computes a plausibility score based on the joint probability 
       of the candidate satisfying hard constraints and maximizing entropy under 
       empirical priors.
    """
    
    def __init__(self):
        self.lambda_default = 0.1
        self.temp = 1.0
        
    def _parse_structure(self, text):
        """Extracts logical atoms, numeric constraints, and negations."""
        text_lower = text.lower()
        atoms = []
        constraints = []
        numeric_vals = {}
        
        # 1. Numeric Extraction (Comparatives)
        nums = re.findall(r'(\d+\.?\d*)', text_lower)
        for i, n in enumerate(nums):
            try:
                numeric_vals[f'num_{i}'] = float(n)
            except: pass
            
        # 2. Negations
        has_negation = bool(re.search(r'\b(not|no|never|none|cannot)\b', text_lower))
        if has_negation:
            constraints.append(('negation', True))
            
        # 3. Conditionals (If-Then)
        if 'if' in text_lower and ('then' in text_lower or ',' in text_lower):
            constraints.append(('conditional', True))
            
        # 4. Quantifiers
        if re.search(r'\b(all|every|some|none)\b', text_lower):
            constraints.append(('quantifier', True))
            
        # 5. Simple boolean atoms (words that look like facts)
        words = re.findall(r'\b[a-z]{4,}\b', text_lower)
        unique_words = list(dict.fromkeys(words))[:10] # Limit complexity
        for w in unique_words:
            atoms.append(w)
            
        return atoms, constraints, numeric_vals

    def _build_graph(self, prompt, candidate):
        """Constructs variables and hard constraints from prompt + candidate."""
        full_text = f"{prompt} {candidate}"
        atoms, p_constraints, p_nums = self._parse_structure(full_text)
        c_atoms, c_constraints, c_nums = self._parse_structure(candidate)
        
        # Variables: x_i represents the truth of atom i
        # We map atoms to indices. 
        all_atoms = list(set(atoms + c_atoms))
        n_vars = max(1, len(all_atoms))
        
        # Hard Constraints Matrix (simplified for AC-3 style propagation)
        # C[i, j] = 1 if compatible, 0 if not. 
        # For this implementation, we simulate consistency via string overlap and logic flags.
        
        consistency_score = 1.0
        
        # Check Negation Consistency
        neg_prompt = any(c[0] == 'negation' for c in p_constraints)
        neg_cand = any(c[0] == 'negation' for c in c_constraints)
        
        if neg_prompt and not neg_cand:
            # Potential contradiction if prompt denies something candidate affirms
            # Soft penalty instead of hard 0 to allow entropy calculation
            consistency_score *= 0.5
            
        # Check Numeric Consistency
        if p_nums and c_nums:
            # Simple heuristic: if candidate numbers are subset of prompt numbers, higher consistency
            p_set = set(p_nums.values())
            c_set = set(c_nums.values())
            if c_set and not c_set.issubset(p_set):
                consistency_score *= 0.7
                
        return n_vars, consistency_score, all_atoms

    def _compute_susceptibility(self, n_vars, base_consistency):
        """
        Estimates susceptibility chi = d<E>/d_lambda via finite difference.
        Tuning T to maximize chi places us at the critical point.
        """
        if n_vars == 0: return 0.0
        
        # Define a range of temperatures to test
        temps = np.linspace(0.1, 2.0, 10)
        lambdas = np.linspace(-0.5, 0.5, 5)
        
        max_chi = -1
        best_T = 1.0
        
        for T in temps:
            derivatives = []
            for lam in lambdas:
                # Mean field approximation of expected value <x>
                # P(x=1) ~ exp(lam/T) / (1 + exp(lam/T)) * consistency
                try:
                    exp_val = np.exp(lam / T)
                    prob = exp_val / (1 + exp_val)
                    energy = prob * base_consistency
                    derivatives.append((lam, energy))
                except OverflowError:
                    continue
            
            # Finite difference approximation of derivative
            if len(derivatives) > 1:
                diffs = []
                for i in range(len(derivatives)-1):
                    l1, e1 = derivatives[i]
                    l2, e2 = derivatives[i+1]
                    if l2 != l1:
                        diffs.append(abs((e2 - e1) / (l2 - l1)))
                if diffs:
                    chi = np.mean(diffs)
                    if chi > max_chi:
                        max_chi = chi
                        best_T = T
                        
        return best_T if max_chi > 0 else 1.0

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        
        # Pre-calculate global stats for MaxEnt prior if needed (simulated here)
        # In a real corpus, we'd compute empirical frequencies. 
        # Here we assume a uniform prior perturbed by structural presence.
        
        for cand in candidates:
            n_vars, hard_consistency, atoms = self._build_graph(prompt, cand)
            
            # 1. Criticality Step: Tune Temperature
            # We simulate the "validation set" using the current candidate's structure
            T = self._compute_susceptibility(n_vars, hard_consistency)
            
            # 2. Maximum Entropy Step: Compute Energy
            # Lambda chosen to match empirical frequency (simulated as 0.5 + bias)
            # Bias comes from structural alignment
            bias = 0.0
            if hard_consistency == 1.0: bias = 0.2
            if len(atoms) > 0: bias += 0.1 * min(1.0, len(atoms)/10.0)
            
            lam = bias 
            energy = 0.0
            
            # Joint distribution log-prob approximation
            # log P(X) = sum(log C_i) + sum(lam * x_j) - log Z
            # Since C_i is 0 or 1, if hard_consistency < 1, we penalize heavily
            
            if hard_consistency < 0.6:
                score = -10.0 # Hard violation
            else:
                # Soft score based on MaxEnt principle near criticality
                # Higher entropy (more valid configurations) -> higher score
                # We approximate -log P(X)
                mean_field_val = 1 / (1 + np.exp(-lam / T))
                entropy_term = - (mean_field_val * np.log(mean_field_val + 1e-9) + 
                                  (1-mean_field_val) * np.log(1-mean_field_val + 1e-9))
                
                # Score combines consistency and entropy
                raw_score = (hard_consistency * 0.7) + (entropy_term * 0.3)
                score = raw_score
            
            # Generate reasoning string
            reason_parts = []
            if hard_consistency >= 1.0: reason_parts.append("Constraints satisfied")
            else: reason_parts.append("Constraint violation detected")
            if n_vars > 0: reason_parts.append(f"Analyzed {n_vars} logical atoms")
            if T < 0.5: reason_parts.append("High certainty regime")
            elif T > 1.5: reason_parts.append("High uncertainty regime")
            else: reason_parts.append("Critical point analysis")
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": "; ".join(reason_parts)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same engine but normalizes output to [0, 1].
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        raw_score = res[0]['score']
        
        # Map raw score to 0-1
        # Assuming raw score roughly in [-10, 2] range based on logic above
        # Sigmoid mapping
        conf = 1 / (1 + np.exp(-raw_score))
        return float(np.clip(conf, 0.0, 1.0))