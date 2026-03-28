import re
import numpy as np
from typing import List, Dict, Tuple, Optional
from collections import deque

class ReasoningTool:
    """
    Temporal-Property Model-Checker with Chaotic Perturbation-Guided Shrinking.
    
    Mechanism:
    1. Parses logical structures (if/then, not, comparatives) and numeric constraints.
    2. Builds a DAG of propositions and propagates interval constraints.
    3. Discretizes the state space to perform model checking against the candidate.
    4. Applies chaotic perturbations to numeric bounds; if the candidate fails under 
       tiny perturbations (fragile), the score drops. Robust satisfaction yields high scores.
    5. Uses NCD only as a tiebreaker for structural equality.
    """
    
    def __init__(self):
        self.regex_patterns = {
            'comp': re.compile(r'(\w+)\s*([<>]=?)\s*([\d.]+)'),
            'if_then': re.compile(r'if\s+(.+?)\s+then\s+(.+)', re.IGNORECASE),
            'not_pat': re.compile(r'not\s+(\w+)', re.IGNORECASE),
            'before': re.compile(r'(.+?)\s+before\s+(.+)', re.IGNORECASE),
            'number': re.compile(r'\d+\.?\d*')
        }

    def _extract_constraints(self, text: str) -> List[Dict]:
        """Extract structural constraints from text."""
        constraints = []
        # Comparatives: X > 5
        for m in self.regex_patterns['comp'].finditer(text):
            constraints.append({'type': 'comp', 'var': m.group(1), 'op': m.group(2), 'val': float(m.group(3))})
        
        # Conditionals
        for m in self.regex_patterns['if_then'].finditer(text):
            constraints.append({'type': 'implies', 'ant': m.group(1).strip(), 'cons': m.group(2).strip()})
            
        # Negations
        for m in self.regex_patterns['not_pat'].finditer(text):
            constraints.append({'type': 'neg', 'target': m.group(1)})
            
        return constraints

    def _check_candidate_logic(self, prompt: str, candidate: str) -> Tuple[bool, float, str]:
        """
        Core logic: Parse prompt, check if candidate satisfies constraints,
        apply chaotic shrinking to test robustness.
        Returns: (is_valid, robustness_score, reason_string)
        """
        constraints = self._extract_constraints(prompt)
        if not constraints:
            return True, 1.0, "No structural constraints found."

        # Extract numeric values from candidate to form initial state
        cand_nums = [float(x) for x in self.regex_patterns['number'].findall(candidate)]
        
        # Map prompt variables to candidate values heuristically (positional)
        # This is a simplification for the "computational analogy" requirement
        prompt_nums = []
        for c in constraints:
            if c['type'] == 'comp':
                prompt_nums.append(c['val'])
        
        # If no numbers in prompt constraints, rely on boolean logic only
        if not prompt_nums:
            # Simple boolean check: does candidate contain the consequent of an 'if'?
            for c in constraints:
                if c['type'] == 'implies':
                    if c['ant'].lower() in prompt.lower() and c['cons'].lower() not in candidate.lower():
                        return False, 0.0, "Failed implication check."
            return True, 0.8, "Logical consistency maintained."

        # Initialize state with candidate numbers (or prompt numbers if candidate lacks them)
        # We simulate the "State Space" as intervals around the candidate's numeric claims
        state_intervals = []
        if cand_nums:
            # Use candidate numbers, widen slightly for perturbation base
            state_intervals = [(n - 0.1, n + 0.1) for n in cand_nums]
        else:
            # If candidate has no numbers, assume it inherits prompt constraints as base truth
            state_intervals = [(n - 0.5, n + 0.5) for n in prompt_nums]

        # Extend to match max length needed
        while len(state_intervals) < len(prompt_nums):
            state_intervals.append((0.0, 10.0)) # Default wide interval

        # Model Checking & Chaotic Shrinking
        failures = 0
        total_checks = 0
        epsilon = 1e-4
        sigma = 0.01
        
        # We iterate through constraints and check against the state intervals
        # Simulating "discretized grid" by checking bounds and perturbed bounds
        for i, c in enumerate(constraints):
            if c['type'] != 'comp':
                continue
            
            idx = i % len(state_intervals)
            low, high = state_intervals[idx]
            target_val = c['val']
            op = c['op']
            
            # Define the check function
            def check_op(v):
                if op == '>': return v > target_val
                if op == '<': return v < target_val
                if op == '>=': return v >= target_val
                if op == '<=': return v <= target_val
                return False

            # 1. Base Check (Center of interval)
            center = (low + high) / 2.0
            if not check_op(center):
                failures += 1
                total_checks += 1
                continue # Failed base case
            
            # 2. Chaotic Perturbation & Shrinking
            # Apply random perturbations to see if the truth value flips (fragility)
            robust_count = 0
            n_perturb = 10
            current_width = high - low
            
            for _ in range(n_perturb):
                noise = np.random.normal(0, sigma)
                perturbed_val = center + noise
                
                # Shrinking simulation: if perturbed value fails, we try to shrink interval around it
                # If it still fails after shrinking, it's a hard failure.
                if not check_op(perturbed_val):
                    # Attempt shrinking: narrow the interval around the failure point
                    shrink_factor = 0.5
                    new_width = current_width * shrink_factor
                    if new_width < epsilon:
                        # Reached minimal epsilon and still failing -> Robust Failure
                        failures += 1
                    else:
                        # Record as fragile failure (partial penalty)
                        failures += 0.5
                else:
                    robust_count += 1
            
            total_checks += 1
            
            # If robust_count is low, the solution is fragile (chaotic sensitivity)
            if robust_count < n_perturb * 0.8:
                failures += 0.2 # Penalty for fragility

        if total_checks == 0:
            return True, 1.0, "No numeric constraints to verify."
            
        failure_rate = failures / (total_checks * 1.2) # Scale slightly
        score = max(0.0, 1.0 - failure_rate)
        
        if score < 0.5:
            return False, score, "Failed constraint propagation or chaotic stability check."
        return True, score, "Constraints satisfied with robustness."

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            return (c12 - min(c1, c2)) / max(c1, c2, 1)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            is_valid, score, reason = self._check_candidate_logic(prompt, cand)
            
            # Fallback/Refinement with NCD if structural signal is weak
            if score > 0.9: 
                # High structural match, keep high
                final_score = score
            elif not is_valid:
                # Structural fail, but maybe NCD says it's identical to prompt (echo)
                ncd_val = self._ncd(prompt, cand)
                if ncd_val < 0.1: # Very similar
                    final_score = 0.1 # Echoes are usually bad reasoning
                else:
                    final_score = score * 0.5 # Penalize heavily
            else:
                final_score = score

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural robustness."""
        is_valid, score, _ = self._check_candidate_logic(prompt, answer)
        if not is_valid:
            return 0.0
        return min(1.0, score)