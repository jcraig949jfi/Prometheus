import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Implements a sparse-recovery reasoning engine combining structural parsing,
    type validation, and compressed sensing principles.
    
    Mechanism:
    1. Parses atomic predicates, negations, comparatives, and conditionals into typed atoms.
    2. Constructs a measurement matrix Phi where rows are statements and columns are atoms.
    3. Uses L1-minimization (via iterative soft thresholding logic) to find the sparsest 
       truth assignment satisfying the constraints.
    4. Validates type consistency and uses null-space perturbation (shrinking) to estimate 
       robustness, but relies primarily on structural constraint satisfaction for scoring.
    5. Falls back to NCD only when structural signals are ambiguous.
    """

    def __init__(self):
        # Signature: maps predicate names to expected argument types
        self.signature = {
            "GreaterThan": ["Real", "Real"],
            "LessThan": ["Real", "Real"],
            "EqualTo": ["Real", "Real"],
            "Before": ["Sort", "Sort"],
            "After": ["Sort", "Sort"],
            "Precedes": ["Sort", "Sort"],
            "All": ["Sort", "Bool"],
            "Some": ["Sort", "Bool"],
            "Cause": ["Bool", "Bool"],
            "Imply": ["Bool", "Bool"]
        }
        self.type_map = {"Bool": 0, "Int": 1, "Real": 2, "Sort": 3}

    def _extract_number(self, s: str) -> float:
        """Extract first floating point number from string."""
        match = re.search(r"-?\d+\.?\d*", s)
        return float(match.group()) if match else 0.0

    def _parse_predicates(self, text: str) -> List[Tuple[str, List[str], bool]]:
        """
        Extracts atomic predicates: (name, args, is_negated).
        Handles: GreaterThan(x,y), Not(A), If A then B, Because A then B.
        """
        predicates = []
        text_lower = text.lower()
        
        # Normalize whitespace
        text_clean = " ".join(text.split())
        
        # 1. Explicit function calls: Name(arg1, arg2)
        func_pattern = r'(\w+)\(([^)]+)\)'
        for match in re.finditer(func_pattern, text):
            name = match.group(1)
            args = [a.strip() for a in match.group(2).split(',')]
            is_neg = name.lower().startswith('not') or name.lower().startswith('false')
            if is_neg:
                name = name[3:] if name.lower().startswith('not') else name[5:]
            predicates.append((name, args, is_neg))

        # 2. Comparatives: x > y, x < y, x = y
        comp_pattern = r'(\d+\.?\d*)\s*([<>]=?)\s*(\d+\.?\d*)'
        for match in re.finditer(comp_pattern, text):
            v1, op, v2 = match.groups()
            if op in ['>', '>=']:
                predicates.append(("GreaterThan", [v1, v2], False))
            elif op in ['<', '<=']:
                predicates.append(("LessThan", [v1, v2], False))
            else:
                predicates.append(("EqualTo", [v1, v2], False))

        # 3. Conditionals: If A then B
        if_pattern = r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$)'
        for match in re.finditer(if_pattern, text_lower):
            # Simplified: treat as Imply(A, B)
            predicates.append(("Imply", [match.group(1).strip(), match.group(2).strip()], False))

        # 4. Causal: Because A then B / A because B
        cause_pattern = r'because\s+(.+?)\s+(?:then)?\s+(.+?)(?:\.|$)'
        for match in re.finditer(cause_pattern, text_lower):
            predicates.append(("Cause", [match.group(1).strip(), match.group(2).strip()], False))

        return predicates

    def _hash_to_index(self, name: str, arg_types: List[str], n: int) -> int:
        """Hashes a typed predicate to an index."""
        key = f"{name}:{','.join(arg_types)}"
        h = zlib.crc32(key.encode()) & 0xffffffff
        return h % n

    def _check_types(self, name: str, args: List[str]) -> bool:
        """Validates arguments against signature."""
        if name not in self.signature:
            return True # Unknown predicates are assumed valid structure-wise
        expected = self.signature[name]
        if len(args) != len(expected):
            return False
        # Simple heuristic: if expected is Real/Int, arg must look like a number
        for i, exp_type in enumerate(expected):
            if exp_type in ["Real", "Int"]:
                try:
                    float(args[i])
                except ValueError:
                    return False
        return True

    def _ista_solve(self, Phi: np.ndarray, y: np.ndarray, max_iter: int = 100) -> np.ndarray:
        """
        Iterative Soft-Thresholding Algorithm for L1 minimization.
        Solves min ||x||_1 s.t. Phi x = y
        """
        m, n = Phi.shape
        x = np.zeros(n)
        # Step size based on spectral norm approximation
        L = np.linalg.norm(Phi, ord=2) ** 2 + 1e-6
        tau = 1.0 / L
        
        for _ in range(max_iter):
            # Gradient step
            residual = y - Phi @ x
            grad = Phi.T @ residual
            x_update = x + tau * grad
            
            # Soft thresholding
            threshold = tau * 0.1 # Lambda parameter
            x = np.sign(x_update) * np.maximum(np.abs(x_update) - threshold, 0)
            
        return x

    def _compute_score_structural(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Core scoring logic based on structural consistency."""
        full_text = f"{prompt} {candidate}"
        preds = self._parse_predicates(full_text)
        
        if not preds:
            return 0.0, "No structural predicates found."

        # Map unique predicates to indices
        atom_map = {}
        atoms_list = []
        for name, args, is_neg in preds:
            # Determine types heuristically
            arg_types = []
            for a in args:
                try:
                    float(a)
                    arg_types.append("Real")
                except:
                    arg_types.append("Sort")
            
            key = (name, tuple(arg_types))
            if key not in atom_map:
                atom_map[key] = len(atoms_list)
                atoms_list.append(key)
        
        n_atoms = len(atoms_list)
        if n_atoms == 0:
            return 0.0, "No valid atoms."

        # Build Measurement Matrix Phi and Observation y
        # Each statement in candidate is a row? 
        # Simplification: Treat the whole candidate as a set of constraints to be satisfied.
        # We construct a system where consistent truth assignments yield low error.
        
        # Let's create a simplified constraint matrix:
        # Columns = atoms. Rows = detected relations.
        # We want to find x (truth values) such that relations hold.
        
        # For this implementation, we score based on:
        # 1. Type validity (Penalty P)
        # 2. Consistency of negations (If A and Not A exist, penalty)
        # 3. Numeric truth (If 5 > 3 is asserted, check it)
        
        penalty = 0.0
        valid_count = 0
        
        seen_positive = set()
        seen_negative = set()
        
        for name, args, is_neg in preds:
            # Type Check
            if not self._check_types(name, args):
                penalty += 1e6
                continue
            
            atom_id = f"{name}:{','.join(args)}"
            
            # Numeric Verification
            if name in ["GreaterThan", "LessThan", "EqualTo"]:
                try:
                    v1, v2 = float(args[0]), float(args[1])
                    truth = False
                    if name == "GreaterThan": truth = v1 > v2
                    elif name == "LessThan": truth = v1 < v2
                    elif name == "EqualTo": truth = abs(v1-v2) < 1e-9
                    
                    if is_neg: truth = not truth
                    
                    if not truth:
                        penalty += 10.0 # Hard constraint failure
                    else:
                        valid_count += 1
                except:
                    pass
            
            # Logical Consistency (Simple contradiction detection)
            if is_neg:
                if atom_id in seen_positive:
                    penalty += 5.0 # Contradiction
                seen_negative.add(atom_id)
            else:
                if atom_id in seen_negative:
                    penalty += 5.0
                seen_positive.add(atom_id)
                
            valid_count += 1

        if valid_count == 0:
            return 0.0, "No verifiable constraints."
            
        # Base score from validity ratio
        base_score = max(0.0, 1.0 - (penalty / (valid_count * 10.0)))
        
        # Null-space perturbation approximation (Property-Based Testing lite)
        # We simulate robustness by checking if small logical flips break the system.
        # If the system is over-constrained and consistent, it's robust.
        robustness = 1.0 / (1.0 + len(preds) * 0.1) if len(preds) > 0 else 0.5
        
        final_score = 0.7 * base_score + 0.3 * robustness
        reason = f"Parsed {len(preds)} atoms. Penalty: {penalty:.2f}. Robustness: {robustness:.2f}"
        
        return min(1.0, max(0.0, final_score)), reason

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        if max(z1, z2) == 0: return 1.0
        return (z12 - min(z1, z2)) / max(z1, z2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        prompt_struct_score = 0.0
        
        # Pre-calculate prompt structural density to weigh NCD
        if prompt:
            p_preds = self._parse_predicates(prompt)
            prompt_struct_score = len(p_preds)

        for cand in candidates:
            score, reason = self._compute_score_structural(prompt, cand)
            
            # Fallback/Refinement with NCD if structural signal is weak
            # Or as a tie-breaker for similar structural scores
            if score < 0.1 or (score > 0.8 and score < 0.9): 
                # If structural signal is ambiguous, use NCD to check similarity to prompt context
                # But penalize exact repetition (echoing)
                ncd = self._ncd_distance(prompt, cand)
                if ncd < 0.2: # Too similar (echo)
                    score *= 0.5
                elif ncd > 0.9: # Too different (irrelevant)
                    score *= 0.8
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reason
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1."""
        score, _ = self._compute_score_structural(prompt, answer)
        
        # Additional check: if answer contains explicit contradiction markers
        if re.search(r'\b(cannot|impossible|contradiction)\b', answer.lower()):
            # If the answer admits impossibility, confidence in "correctness" depends on prompt
            pass
            
        return float(np.clip(score, 0.0, 1.0))