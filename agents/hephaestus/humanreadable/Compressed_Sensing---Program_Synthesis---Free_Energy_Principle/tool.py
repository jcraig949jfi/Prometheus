from typing import Dict, Tuple

import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Compressed Sensing x Program Synthesis x Free Energy Principle
    
    Treats candidates as sparse programs in a DSL, prompt as constraint measurements.
    Recovers sparsest program p minimizing F = ||Ap - b||^2 + lambda*||p||_1
    via ISTA (Iterative Shrinkage-Thresholding Algorithm).
    """
    
    def __init__(self):
        self.lambda_reg = 0.1
        self.ista_steps = 50
        self.step_size = 0.01
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by free energy minimization."""
        results = []
        prompt_constraints = self._parse_constraints(prompt)
        
        for cand in candidates:
            cand_program = self._parse_constraints(cand)
            A, b = self._build_measurement_matrix(prompt_constraints, cand_program)
            
            if A.size == 0:
                # Fallback to NCD
                score = self._ncd_score(prompt, cand)
                reasoning = "NCD fallback (no constraints parsed)"
            else:
                p_sparse = self._ista_solve(A, b)
                free_energy = self._compute_free_energy(A, b, p_sparse)
                
                # Compute structural score
                struct_score = self._structural_match(prompt, cand)
                numeric_score = self._numeric_eval(prompt, cand)
                ncd_score = self._ncd_score(prompt, cand)
                
                # Weighted combination
                score = (-free_energy * 0.5 + struct_score * 0.3 + 
                         numeric_score * 0.15 + ncd_score * 0.05)
                reasoning = f"FE={free_energy:.3f}, struct={struct_score:.2f}"
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Confidence with epistemic honesty checks."""
        meta_conf = self._meta_confidence(prompt)
        
        if meta_conf < 0.3:
            return meta_conf
        
        prompt_constraints = self._parse_constraints(prompt)
        answer_program = self._parse_constraints(answer)
        A, b = self._build_measurement_matrix(prompt_constraints, answer_program)
        
        if A.size == 0:
            return min(0.4, meta_conf)
        
        p_sparse = self._ista_solve(A, b)
        residual = np.linalg.norm(A @ p_sparse - b)
        sparsity = np.sum(np.abs(p_sparse) > 1e-3) / max(len(p_sparse), 1)
        
        # Lower residual + higher sparsity = higher confidence
        conf = np.clip(np.exp(-residual) * (1 - 0.5 * sparsity), 0, 0.95)
        return min(float(conf), meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity/unanswerability markers."""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|quit|why did .* fail|when did .* stop)', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', p_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.2
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p_lower):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower):
            return 0.35
        
        return 1.0
    
    def _parse_constraints(self, text: str) -> List[Tuple[str, str, str]]:
        """Extract (left, op, right) triples."""
        constraints = []
        
        # Numeric comparisons
        for match in re.finditer(r'([a-zA-Z0-9.]+)\s*([<>=!]+)\s*([a-zA-Z0-9.]+)', text):
            constraints.append((match.group(1), match.group(2), match.group(3)))
        
        # Negations
        for match in re.finditer(r'\b(not|no|never)\s+(\w+)', text):
            constraints.append(('NOT', match.group(2), ''))
        
        # Conditionals
        for match in re.finditer(r'\bif\s+(\w+).*then\s+(\w+)', text, re.IGNORECASE):
            constraints.append((match.group(1), 'IMPLIES', match.group(2)))
        
        return constraints
    
    def _build_measurement_matrix(self, prompt_constr, cand_constr) -> Tuple[np.ndarray, np.ndarray]:
        """Construct A and b from constraints."""
        all_symbols = set()
        for c in prompt_constr + cand_constr:
            all_symbols.update([c[0], c[2]])
        all_symbols.discard('')
        
        if not all_symbols:
            return np.array([]), np.array([])
        
        sym_list = sorted(all_symbols)
        n = len(sym_list)
        sym_idx = {s: i for i, s in enumerate(sym_list)}
        
        rows = []
        targets = []
        
        for left, op, right in prompt_constr:
            row = np.zeros(n)
            if left in sym_idx:
                row[sym_idx[left]] = 1
            if right in sym_idx:
                row[sym_idx[right]] = -1 if op in ['>', '<', '!='] else 1
            rows.append(row)
            targets.append(1.0 if op not in ['NOT'] else 0.0)
        
        for left, op, right in cand_constr:
            row = np.zeros(n)
            if left in sym_idx:
                row[sym_idx[left]] = 1
            if right in sym_idx:
                row[sym_idx[right]] = 1
            rows.append(row)
            targets.append(1.0)
        
        A = np.array(rows) if rows else np.array([])
        b = np.array(targets) if targets else np.array([])
        
        return A, b
    
    def _ista_solve(self, A: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Iterative Shrinkage-Thresholding for sparse recovery."""
        if A.size == 0:
            return np.array([])
        
        n = A.shape[1]
        p = np.zeros(n)
        
        for _ in range(self.ista_steps):
            gradient = A.T @ (A @ p - b)
            p = self._soft_threshold(p - self.step_size * gradient, 
                                      self.lambda_reg * self.step_size)
        
        return p
    
    def _soft_threshold(self, x: np.ndarray, threshold: float) -> np.ndarray:
        """Soft thresholding operator."""
        return np.sign(x) * np.maximum(np.abs(x) - threshold, 0)
    
    def _compute_free_energy(self, A: np.ndarray, b: np.ndarray, p: np.ndarray) -> float:
        """F = ||Ap - b||^2 + lambda*||p||_1"""
        if A.size == 0:
            return 10.0
        residual = np.linalg.norm(A @ p - b) ** 2
        sparsity_penalty = self.lambda_reg * np.sum(np.abs(p))
        return residual + sparsity_penalty
    
    def _structural_match(self, prompt: str, candidate: str) -> float:
        """Score structural agreement."""
        score = 0.0
        
        # Negation consistency
        prompt_neg = bool(re.search(r'\b(not|no|never)\b', prompt.lower()))
        cand_neg = bool(re.search(r'\b(not|no|never)\b', candidate.lower()))
        if prompt_neg == cand_neg:
            score += 0.3
        
        # Conditional presence
        if 'if' in prompt.lower() and 'if' in candidate.lower():
            score += 0.2
        
        return score
    
    def _numeric_eval(self, prompt: str, candidate: str) -> float:
        """Evaluate numeric comparisons."""
        prompt_nums = re.findall(r'\b\d+\.?\d*\b', prompt)
        cand_nums = re.findall(r'\b\d+\.?\d*\b', candidate)
        
        if not prompt_nums or not cand_nums:
            return 0.0
        
        # Check if numeric comparison is correct
        comp_match = re.search(r'(\d+\.?\d*)\s*([<>])\s*(\d+\.?\d*)', prompt)
        if comp_match:
            left, op, right = comp_match.groups()
            left_val, right_val = float(left), float(right)
            
            is_correct = (op == '<' and left_val < right_val) or \
                        (op == '>' and left_val > right_val)
            
            if is_correct and any(n in candidate for n in [left, right]):
                return 0.5
        
        return 0.1 if set(prompt_nums) & set(cand_nums) else 0.0
    
    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (capped at 15% weight)."""
        import zlib
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        ncd = (c12 - min(c1, c2)) / max(c1, c2, 1)
        return 1.0 - ncd