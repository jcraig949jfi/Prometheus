import numpy as np
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A hybrid reasoning tool combining structural SAT-like constraint parsing,
    predictive coding hierarchy, and phase-transition scoring.
    
    Mechanism:
    1. Parses prompts into boolean/numeric constraints (CNF-like).
    2. Evaluates candidates against these constraints to compute an energy score.
    3. Uses a 'predictive coding' loop where higher-level predictions smooth 
       the candidate's truth values, looking for a phase transition in energy 
       as temperature varies.
    4. Falls back to NCD only if no structural signals are found.
    """
    
    def __init__(self):
        self.lambda_reg = 0.1
        self.tau_steps = np.linspace(0, 1, 20)
        
    def _parse_constraints(self, text: str) -> Tuple[List[str], List[str], List[Tuple[str, str, str]], List[Tuple[str, float, str]]]:
        """Extract negations, conditionals, orderings, and numeric thresholds."""
        text_lower = text.lower()
        negations = []
        conditionals = []
        orderings = []
        numerics = []
        
        # 1. Negations (not X, never X)
        for m in re.finditer(r'(?:not|never)\s+([a-z]+)', text_lower):
            negations.append(m.group(1))
            
        # 2. Conditionals (if P then Q, P implies Q)
        # Simplified pattern matching for demonstration
        if_cond = r'if\s+(.+?)\s+(?:then|,)?\s+(.+?)(?:\.|,|$)'
        for m in re.finditer(if_cond, text_lower):
            conditionals.append((m.group(1).strip(), m.group(2).strip()))
            
        # 3. Comparatives (A > B, A is greater than B)
        comp_patterns = [
            (r'([a-z]+)\s+is\s+greater\s+than\s+([a-z]+)', 'gt'),
            (r'([a-z]+)\s+>\s+([a-z]+)', 'gt'),
            (r'([a-z]+)\s+is\s+less\s+than\s+([a-z]+)', 'lt'),
            (r'([a-z]+)\s+<\s+([a-z]+)', 'lt')
        ]
        for pattern, op in comp_patterns:
            for m in re.finditer(pattern, text_lower):
                orderings.append((m.group(1), op, m.group(2)))
                
        # 4. Numeric thresholds (value > 5.0)
        num_pattern = r'([a-z]+)\s*[><]\s*([\d\.]+)'
        for m in re.finditer(num_pattern, text_lower):
            try:
                numerics.append((m.group(1), float(m.group(2)), '>' if '>' in m.group(0) else '<'))
            except ValueError:
                pass
                
        return negations, conditionals, orderings, numerics

    def _extract_vars(self, text: str) -> List[str]:
        """Extract potential variable names (lowercase words)."""
        return list(set(re.findall(r'\b[a-z]{2,}\b', text.lower())))

    def _check_satisfaction(self, candidate: str, constraints: dict) -> float:
        """Check how many constraints a candidate satisfies. Returns energy (lower is better)."""
        cand_lower = candidate.lower()
        energy = 0.0
        total_weight = 0.0
        
        # Check negations: if "not X" exists, "X" in candidate adds energy
        for var in constraints['negations']:
            if var in cand_lower:
                energy += 2.0 # High penalty
            total_weight += 2.0
            
        # Check conditionals: If P in candidate, Q must be in candidate (simplified)
        # Or if P in prompt implies Q, and candidate asserts P but not Q -> error
        for p, q in constraints['conditionals']:
            # If candidate contains P logic but misses Q
            if p in cand_lower and q not in cand_lower:
                # Only penalize if P is actually asserted as true in candidate context
                # Heuristic: if P is present, Q should be too
                energy += 1.5
            total_weight += 1.5
            
        # Check orderings
        for a, op, b in constraints['orderings']:
            has_a = a in cand_lower
            has_b = b in cand_lower
            if op == 'gt':
                # If both mentioned, order matters? Hard to verify without values.
                # Instead, check for contradiction patterns like "b is greater than a"
                if f"{b} is greater than {a}" in cand_lower or f"{b} > {a}" in cand_lower:
                    energy += 3.0
            total_weight += 1.0
            
        # Check numerics
        for var, threshold, op in constraints['numerics']:
            # Try to find number associated with var in candidate
            pattern = rf"{var}\s*[=:]?\s*([\d\.]+)"
            match = re.search(pattern, cand_lower)
            if match:
                try:
                    val = float(match.group(1))
                    if op == '>' and val <= threshold:
                        energy += 5.0
                    elif op == '<' and val >= threshold:
                        energy += 5.0
                except: pass
            total_weight += 2.0
            
        # Normalize energy slightly by weight to prevent bias by prompt length
        return energy if total_weight == 0 else energy / (total_weight + 1)

    def _compute_predictive_energy_curve(self, candidate: str, prompt: str, constraints: dict) -> Tuple[float, float]:
        """
        Simulate the phase transition.
        1. Encode candidate as binary vector (simplified to presence of key terms).
        2. Generate hierarchical predictions (smoothing).
        3. Vary temperature tau to mix raw vs predicted.
        4. Find critical tau where energy drops most.
        """
        vars_prompt = self._extract_vars(prompt)
        if not vars_prompt:
            return 0.0, 0.0
            
        vars_prompt = vars_prompt[:20] # Limit dimension for speed
        n_vars = len(vars_prompt)
        
        # Level 0: Raw assignment based on candidate presence
        a0 = np.array([1.0 if v in candidate.lower() else 0.0 for v in vars_prompt])
        
        # Build adjacency matrix for smoothing (simple co-occurrence in prompt sentences)
        # For this implementation, we assume all extracted vars are loosely connected
        # to simulate a connected component graph.
        adj = np.ones((n_vars, n_vars)) - np.eye(n_vars)
        
        # Hierarchical predictions (L=3 levels)
        levels = [a0.copy()]
        curr = a0.copy()
        for _ in range(2):
            # Smooth: average neighbors
            if n_vars > 1:
                curr = (curr + np.dot(curr, adj) / (n_vars - 1)) / 2.0
            levels.append(curr.copy())
            
        # Phase transition scan
        energies = []
        taus = self.tau_steps
        
        for tau in taus:
            # Mix raw and hierarchical average
            avg_pred = np.mean(levels, axis=0)
            mixed = (1 - tau) * a0 + tau * avg_pred
            
            # Threshold to boolean
            a_tau = (mixed > 0.5).astype(float)
            
            # Reconstruct string representation for energy check (approximate)
            # We map the boolean vector back to a pseudo-candidate string containing
            # only the variables that are TRUE in this state.
            active_vars = " ".join([vars_prompt[i] for i in range(n_vars) if a_tau[i] == 1.0])
            
            # Compute energy of this state
            # We use a simplified energy function based on constraint satisfaction
            # Since we can't fully re-parse, we estimate satisfaction based on 
            # whether the active variables violate the extracted constraints logic.
            
            e = 0.0
            # Negation penalty
            for var in constraints['negations']:
                if var in vars_prompt:
                    idx = vars_prompt.index(var)
                    if a_tau[idx] == 1.0:
                        e += 2.0
            
            # Conditional penalty (P -> Q)
            for p, q in constraints['conditionals']:
                p_idx = vars_prompt.index(p) if p in vars_prompt else -1
                q_idx = vars_prompt.index(q) if q in vars_prompt else -1
                
                if p_idx != -1 and q_idx != -1:
                    if a_tau[p_idx] == 1.0 and a_tau[q_idx] == 0.0:
                        e += 1.5
                elif p_idx != -1 and q_idx == -1:
                    # If Q not in vars, we assume it's satisfied if P is present? 
                    # Or penalize if we can't verify. Let's assume safe if not tracked.
                    pass
                    
            energies.append(e)
            
        # Find critical point (largest negative jump in energy)
        if len(energies) < 2:
            return 0.0, 0.0
            
        diffs = np.diff(energies)
        min_diff = np.min(diffs) # Most negative jump
        tau_c_idx = np.argmin(diffs)
        tau_c = taus[tau_c_idx]
        
        # Final score: Negative Energy at critical point minus regularization
        # Regularization: distance between raw and final state
        final_state = ( (1-tau_c)*a0 + tau_c*np.mean(levels, axis=0) > 0.5 ).astype(float)
        reg_term = np.sum(np.abs(a0 - final_state))
        
        score = -energies[tau_c_idx] - self.lambda_reg * reg_term
        return score, tau_c

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        import zlib
        l1 = len(zlib.compress(s1.encode()))
        l2 = len(zlib.compress(s2.encode()))
        l12 = len(zlib.compress((s1 + s2).encode()))
        if max(l1, l2) == 0: return 1.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        constraints = {
            'negations': [], 'conditionals': [], 
            'orderings': [], 'numerics': []
        }
        
        # 1. Structural Parsing
        constraints['negations'], constraints['conditionals'], \
        constraints['orderings'], constraints['numerics'] = self._parse_constraints(prompt)
        
        has_structure = any(constraints[k] for k in constraints)
        
        for cand in candidates:
            score = 0.0
            reason = ""
            
            if has_structure:
                # Primary: SAT-like Energy + Phase Transition
                base_energy = self._check_satisfaction(cand, constraints)
                phase_score, tau_c = self._compute_predictive_energy_curve(cand, prompt, constraints)
                
                # Combine: Lower energy is better. Phase score is negative energy.
                # We invert base_energy so higher is better.
                score = (1.0 / (base_energy + 0.1)) + phase_score
                
                reason = f"Structural consistency (neg/cond/num): {1.0/(base_energy+0.1):.2f}, Phase transition score: {phase_score:.2f}"
            else:
                # Fallback: NCD (Compression similarity to prompt implies relevance)
                # Note: Pure NCD is weak, but required as baseline. 
                # We invert distance so higher is better.
                dist = self._ncd_score(prompt, cand)
                score = 1.0 - dist
                reason = "No structural constraints found; using compression similarity."
                
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reason
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural satisfaction."""
        constraints = {
            'negations': [], 'conditionals': [], 
            'orderings': [], 'numerics': []
        }
        constraints['negations'], constraints['conditionals'], \
        constraints['orderings'], constraints['numerics'] = self._parse_constraints(prompt)
        
        if not any(constraints[k] for k in constraints):
            # No structure, low confidence baseline
            return 0.5
            
        energy = self._check_satisfaction(answer, constraints)
        # Map energy to 0-1. 0 energy -> 1.0. High energy -> 0.0
        # Assuming max reasonable energy per constraint is ~5, and avg constraints ~3
        max_exp_energy = 15.0
        conf = max(0.0, min(1.0, 1.0 - (energy / max_exp_energy)))
        return conf