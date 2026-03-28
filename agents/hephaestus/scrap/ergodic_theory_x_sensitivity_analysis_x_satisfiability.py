import re
import numpy as np
from typing import List, Dict, Tuple, Set, Optional

class ReasoningTool:
    """
    Ergodic-SAT Reasoning Tool.
    Mechanism: Parses text into logical clauses (conditionals, negations, comparatives).
    Applies Monte-Carlo sensitivity analysis (ergodic averaging) via a lightweight DPLL solver.
    Robustness score = frequency of satisfiability under perturbation.
    NCD is used only as a tiebreaker.
    """
    
    def __init__(self):
        self.var_map = {}
        self.reverse_map = {}
        self.var_count = 0

    def _get_var_id(self, name: str) -> int:
        if name not in self.var_map:
            self.var_map[name] = self.var_count
            self.reverse_map[self.var_count] = name
            self.var_count += 1
        return self.var_map[name]

    def _parse_clauses(self, text: str) -> Tuple[List[List[Tuple[int, int]]], Dict[int, Tuple[float, float]]]:
        """Extract logical clauses and numeric intervals from text."""
        clauses = []
        intervals = {} # Maps var_id to (min, max)
        text_lower = text.lower()
        
        # Helper to add clause
        def add_clause(lits):
            if lits: clauses.append(lits)

        # 1. Extract Comparatives (A > B, A < B, etc) -> Create boolean var v_comp
        # Pattern: word number comparator number word
        comp_pattern = r'(\w+)\s*(>|<|>=|<=|==|!=)\s*(\d+\.?\d*)'
        for m in re.finditer(comp_pattern, text_lower):
            subject, op, val = m.group(1), m.group(2), float(m.group(3))
            var_name = f"{subject}_{op}_{val}"
            vid = self._get_var_id(var_name)
            
            # Determine truth based on context if possible, else assume wide interval
            # For robustness, we store the constraint logic. 
            # Here we simulate the "numeric constraint" by setting a baseline interval
            # If the text implies a fact (e.g., "5 > 3"), we might fix it, but for 
            # candidate evaluation, we treat the claim as a variable to be tested.
            intervals[vid] = (val - 1.0, val + 1.0) 
            
            # Add clause: The comparative holds (single literal clause for now)
            add_clause([(vid, 1)])

        # 2. Extract Conditionals (if A then B -> not A or B)
        # Simple regex for "if X then Y" or "X causes Y"
        cond_pattern = r'(?:if|when)\s+([^.]+?)(?:\s+then|\s+,)?\s*(.+?)(?:\.|,|$)'
        for m in re.finditer(cond_pattern, text_lower):
            cond_part, res_part = m.group(1).strip(), m.group(2).strip()
            c_vid = self._get_var_id(f"stmt:{cond_part}")
            r_vid = self._get_var_id(f"stmt:{res_part}")
            # Not Cond OR Res
            add_clause([(c_vid, -1), (r_vid, 1)])

        # 3. Extract Causal (A causes B)
        cause_pattern = r'([^.]+?)\s+(causes|leads to|implies)\s+([^.]+?)\.'
        for m in re.finditer(cause_pattern, text_lower):
            c_vid = self._get_var_id(f"stmt:{m.group(1).strip()}")
            r_vid = self._get_var_id(f"stmt:{m.group(3).strip()}")
            add_clause([(c_vid, -1), (r_vid, 1)])

        # 4. Extract Negations (not A) -> Not A
        neg_pattern = r'(?:it is not true that|does not|cannot|no|not)\s+([^.]+?)\.'
        for m in re.finditer(neg_pattern, text_lower):
            stmt = m.group(1).strip()
            # Avoid double negatives in simple regex
            if "not" not in stmt:
                s_vid = self._get_var_id(f"stmt:{stmt}")
                add_clause([(s_vid, -1)])

        # Fallback: If no structure found, treat whole text as a single assertion
        if not clauses:
            main_vid = self._get_var_id("main_assertion")
            add_clause([(main_vid, 1)])
            
        return clauses, intervals

    def _dpll(self, clauses: List[List[Tuple[int, int]]], assignment: Dict[int, int]) -> bool:
        """Lightweight DPLL solver."""
        # Check satisfaction
        unassigned = []
        for clause in clauses:
            is_sat = False
            is_unassigned = False
            for var, sign in clause:
                if var in assignment:
                    if assignment[var] == sign:
                        is_sat = True
                        break
                else:
                    is_unassigned = True
            if not is_sat:
                if not is_unassigned:
                    return False # Conflict
                unassigned.append(clause)
        
        if not unassigned:
            return True # All satisfied

        # Heuristic: Pick first var from first unassigned clause
        clause = unassigned[0]
        var = clause[0][0]
        if var in assignment:
            # Should not happen with proper filtering, but safety check
            return self._dpll(clauses, assignment)
            
        # Try True
        assignment[var] = 1
        if self._dpll(clauses, assignment):
            return True
        
        # Try False
        assignment[var] = -1
        if self._dpll(clauses, assignment):
            return True
            
        # Backtrack
        del assignment[var]
        return False

    def _check_sat(self, clauses: List[List[Tuple[int, int]]], perturbations: Dict[int, int]) -> bool:
        """Apply perturbations to literals and run DPLL."""
        # Perturb literals: if var in perturbations, flip sign in clause
        new_clauses = []
        for clause in clauses:
            new_clause = []
            for var, sign in clause:
                if var in perturbations:
                    # Flip sign if perturbation says so
                    new_sign = sign * perturbations[var]
                else:
                    new_sign = sign
                new_clause.append((var, new_sign))
            new_clauses.append(new_clause)
        
        return self._dpll(new_clauses, {})

    def _compute_ergodic_score(self, text: str, T: int = 50, p: float = 0.1) -> float:
        """Run Monte-Carlo sensitivity analysis."""
        self.var_map = {}
        self.reverse_map = {}
        self.var_count = 0
        
        clauses, intervals = self._parse_clauses(text)
        if not clauses:
            return 0.5 # Neutral if nothing parsed

        vars_list = list(intervals.keys())
        sat_count = 0
        
        # Seed for determinism within the function context based on text hash
        np.random.seed(hash(text) % (2**32))
        
        for _ in range(T):
            perturbations = {}
            # Perturb numeric bounds (simulated by flipping boolean interpretation of intervals)
            for vid in vars_list:
                if np.random.random() < p:
                    perturbations[vid] = -1 # Flip logic
            
            # Perturb structural clauses (flip a random literal in a random clause)
            if clauses and np.random.random() < p:
                idx = np.random.randint(0, len(clauses))
                if len(clauses[idx]) > 0:
                    lit_idx = np.random.randint(0, len(clauses[idx]))
                    var = clauses[idx][lit_idx][0]
                    perturbations[var] = -1

            if self._check_sat(clauses, perturbations):
                sat_count += 1
                
        return sat_count / T

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        if max(c1, c2) == 0: return 0.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        # Pre-calculate prompt structure weight
        prompt_score = self._compute_ergodic_score(prompt)
        
        scored_candidates = []
        for cand in candidates:
            # Primary Signal: Structural Robustness of the combined Prompt+Answer
            # We evaluate the coherence of the answer within the prompt's context
            combined = f"{prompt} {cand}"
            robustness = self._compute_ergodic_score(combined)
            
            # Secondary Signal: NCD Tiebreaker (similarity to prompt implies relevance)
            ncd_val = self._ncd(prompt, cand)
            
            # Score formulation:
            # High robustness is good. 
            # Low NCD (high similarity) is slightly favored as tiebreaker.
            score = robustness * 0.8 + (1.0 - ncd_val) * 0.2
            
            # Penalty for empty or too short answers
            if len(cand.strip()) < 2:
                score = 0.0
                
            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Robustness: {robustness:.3f}, NCD: {ncd_val:.3f}"
            })
        
        # Rank by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on ergodic robustness."""
        combined = f"{prompt} {answer}"
        robustness = self._compute_ergodic_score(combined)
        
        # Map robustness to confidence
        # If robustness > 0.5, it's likely consistent. 
        # If < 0.5, it's fragile.
        confidence = max(0.0, min(1.0, robustness))
        return confidence