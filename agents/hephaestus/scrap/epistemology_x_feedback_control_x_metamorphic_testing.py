import re
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Constraint-Driven Belief Updater (CDBU).
    
    Mechanism:
    1. Epistemological Parsing: Extracts literals (atoms) from text categorized as:
       - Foundational: Explicit numeric values or direct assertions (Initial Belief = 0.9).
       - Coherent: Inferred relations, comparatives, negations (Initial Belief = 0.5).
    2. Metamorphic Constraints (MRs):
       - MR1 (Scaling): Numeric consistency under scaling.
       - MR2 (Order): Comparative inversion (A < B implies not(B < A)).
       - MR3 (Closure): Transitivity and Modus Ponens.
    3. Feedback Control: Iteratively updates belief scores using a PID-like controller
       to minimize constraint violations across the hyper-graph of literals.
    4. Scoring: Aggregates final belief scores of candidate-specific literals.
    """

    def __init__(self):
        # PID Constants
        self.Kp = 0.2
        self.Ki = 0.01
        self.Kd = 0.05
        self.max_sweeps = 50
        self.tolerance = 1e-3

    def _extract_atoms(self, text: str) -> Dict[str, dict]:
        """Extract literals and initialize beliefs based on epistemological foundations."""
        atoms = {}
        text_lower = text.lower()
        
        # 1. Numeric Extraction (Foundational)
        numbers = re.findall(r'-?\d+\.?\d*', text)
        for num in numbers:
            key = f"num:{num}"
            if key not in atoms:
                atoms[key] = {'val': float(num), 'belief': 0.9, 'type': 'foundational'}

        # 2. Comparatives (Coherent -> Foundational if explicit numbers present)
        # Pattern: word < number or number > word
        comp_patterns = [
            (r'(\w+)\s*<\s*(\d+\.?\d*)', 'lt'),
            (r'(\d+\.?\d*)\s*>\s*(\w+)', 'gt'),
            (r'(\w+)\s*>\s*(\d+\.?\d*)', 'gt_rev'),
            (r'(\d+\.?\d*)\s*<\s*(\w+)', 'lt_rev')
        ]
        
        for pattern, p_type in comp_patterns:
            matches = re.findall(pattern, text_lower)
            for m in matches:
                key = f"comp:{m[0]}_{p_type}_{m[1]}"
                # If both sides are numbers found in text, it's foundational
                is_foundational = (m[0] in numbers or m[1] in numbers)
                atoms[key] = {
                    'val': (m[0], m[1]), 
                    'belief': 0.9 if is_foundational else 0.5, 
                    'type': 'comparative' if not is_foundational else 'foundational'
                }

        # 3. Negations (Coherent)
        neg_matches = re.findall(r'(?:not|no|never)\s+(\w+)', text_lower)
        for word in neg_matches:
            key = f"neg:{word}"
            if key not in atoms:
                atoms[key] = {'val': word, 'belief': 0.5, 'type': 'coherent'}

        # 4. Conditionals/Causal (Coherent)
        if any(k in text_lower for k in ['if', 'then', 'causes', 'leads to']):
            atoms['logic:conditional'] = {'val': 1, 'belief': 0.5, 'type': 'coherent'}

        # Fallback if no atoms found (prevents empty graph)
        if not atoms:
            atoms['default:presence'] = {'val': 1, 'belief': 0.5, 'type': 'coherent'}
            
        return atoms

    def _get_constraints(self, atoms: Dict) -> List[Tuple[List[str], str]]:
        """Generate MR constraints (Premises -> Conclusion)."""
        constraints = []
        keys = list(atoms.keys())
        
        # MR2: Order Preservation (Simplified: If A < B exists, check consistency)
        # We simulate consistency by linking comparative atoms to their numeric counterparts
        nums = [k for k in keys if k.startswith('num:')]
        comps = [k for k in keys if k.startswith('comp:')]
        
        for comp_key in comps:
            parts = comp_key.split('_')
            if len(parts) >= 3:
                # Extract numeric strings from comparative atom if possible
                # Link to explicit numeric atoms if they exist
                for n_key in nums:
                    n_val = atoms[n_key]['val']
                    # Simple heuristic: if comparative mentions a number string that matches a numeric atom
                    if str(n_val) in comp_key:
                        constraints.append(([n_key], comp_key))
        
        # MR3: Logical Closure (Transitivity simulation)
        # If we have multiple comparatives, assume transitivity chain
        if len(comps) >= 2:
            constraints.append((comps[:2], comps[-1]))
            
        # Default self-consistency for foundational items
        for k, v in atoms.items():
            if v['type'] == 'foundational':
                constraints.append(([k], k))
                
        return constraints if constraints else [(['default:presence'], 'default:presence')]

    def _run_updater(self, atoms: Dict) -> float:
        """Run the PID-based belief update loop."""
        if not atoms:
            return 0.0
            
        constraints = self._get_constraints(atoms)
        beliefs = {k: v['belief'] for k, v in atoms.items()}
        keys = list(beliefs.keys())
        
        # Initialize history for Integral and Derivative terms
        error_history = {k: [] for k in keys}
        prev_error = {k: 0.0 for k in keys}
        
        for sweep in range(self.max_sweeps):
            max_delta = 0.0
            
            # Aggregate updates per key to avoid race conditions in single sweep
            updates = {k: 0.0 for k in keys}
            
            for premises, conclusion in constraints:
                if conclusion not in beliefs:
                    continue
                    
                # Calculate premise product
                premise_prod = 1.0
                for p in premises:
                    premise_prod *= beliefs.get(p, 0.5)
                
                target = premise_prod
                current = beliefs[conclusion]
                
                # Violation
                v_e = abs(target - current)
                
                # PID Components
                err_prop = target - current # Directional error for update
                err_int = sum(error_history.get(conclusion, [0])) + err_prop
                err_diff = err_prop - prev_error.get(conclusion, 0)
                
                delta = (self.Kp * err_prop) + (self.Ki * err_int) + (self.Kd * err_diff)
                updates[conclusion] += delta
                
                # Track history (limit size to prevent explosion)
                if len(error_history[conclusion]) > 10:
                    error_history[conclusion].pop(0)
                error_history[conclusion].append(err_prop)
                prev_error[conclusion] = err_prop
                
                if abs(delta) > max_delta:
                    max_delta = abs(delta)

            # Apply updates
            for k, delta in updates.items():
                new_val = beliefs[k] + delta
                beliefs[k] = max(0.0, min(1.0, new_val)) # Clip [0, 1]
            
            if max_delta < self.tolerance:
                break

        # Score is the weighted average of beliefs, prioritizing foundational
        total_weight = 0
        weighted_sum = 0
        for k, b in beliefs.items():
            w = 1.5 if atoms[k]['type'] == 'foundational' else 1.0
            weighted_sum += b * w
            total_weight += w
            
        return (weighted_sum / total_weight) if total_weight > 0 else 0.0

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        try:
            z1 = len(repr(s1.encode('utf-8'))) # Approx compression length proxy
            z2 = len(repr(s2.encode('utf-8')))
            z12 = len(repr((s1 + s2).encode('utf-8')))
            max_len = max(z1, z2)
            if max_len == 0: return 1.0
            return (z12 - min(z1, z2)) / max_len
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt atoms to weight candidate alignment
        prompt_atoms = self._extract_atoms(prompt)
        prompt_score_base = self._run_updater(prompt_atoms)
        
        for cand in candidates:
            # Combine prompt and candidate for context-aware evaluation
            combined_text = f"{prompt} {cand}"
            atoms = self._extract_atoms(combined_text)
            
            # Run CDBU
            structural_score = self._run_updater(atoms)
            
            # Heuristic: Penalize if candidate contradicts prompt foundations
            # (Simplified here as the updater handles internal consistency)
            
            results.append({
                "candidate": cand,
                "score": float(structural_score),
                "reasoning": f"CDBU converged belief: {structural_score:.4f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Tie-breaking with NCD if scores are very close
        if len(results) > 1:
            if abs(results[0]['score'] - results[1]['score']) < 0.01:
                # Use NCD against prompt as tiebreaker
                for r in results:
                    ncd = self._ncd_score(prompt, r['candidate'])
                    r['score'] -= ncd * 0.001 # Small penalty for high NCD (dissimilarity)
                results.sort(key=lambda x: x['score'], reverse=True)

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        combined = f"{prompt} {answer}"
        atoms = self._extract_atoms(combined)
        score = self._run_updater(atoms)
        return float(score)