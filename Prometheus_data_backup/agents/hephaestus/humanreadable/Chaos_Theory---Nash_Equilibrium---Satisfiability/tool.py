from typing import Dict, Set, Tuple

"""
Reasoning tool combining Chaos Theory, Nash Equilibrium, and Satisfiability.

Core mechanism:
1. Parse prompt+candidates into CNF clauses (SAT)
2. Score by clause satisfaction (payoff)
3. Check Nash equilibrium stability (no beneficial unilateral deviation)
4. Compute Lyapunov-style sensitivity (robustness to bit-flips)
5. Final score = payoff * stability * (1 - sensitivity)
"""

import re
import zlib
from typing import List, Dict, Set, Tuple

class ReasoningTool:
    def __init__(self):
        self.var_to_idx = {}
        self.idx_to_var = {}
        self.clauses = []
        self.next_var_id = 0
        
    def _reset(self):
        self.var_to_idx = {}
        self.idx_to_var = {}
        self.clauses = []
        self.next_var_id = 0
        
    def _get_var_idx(self, var_name: str) -> int:
        if var_name not in self.var_to_idx:
            self.var_to_idx[var_name] = self.next_var_id
            self.idx_to_var[self.next_var_id] = var_name
            self.next_var_id += 1
        return self.var_to_idx[var_name]
    
    def _parse_propositions(self, text: str) -> List[Tuple[str, bool]]:
        """Extract propositions as (variable_name, is_positive) pairs."""
        props = []
        text_lower = text.lower()
        
        # Conditionals: if X then Y -> (~X v Y)
        for match in re.finditer(r'if\s+([^,]+?)\s+then\s+([^,.;]+)', text_lower):
            antecedent = match.group(1).strip()
            consequent = match.group(2).strip()
            props.append((f"cond_ant_{antecedent}", False))  # ~X
            props.append((f"cond_cons_{consequent}", True))  # Y
            
        # Causality: X leads to Y, because X, X causes Y
        for match in re.finditer(r'([^,]+?)\s+(?:leads to|causes)\s+([^,.;]+)', text_lower):
            cause = match.group(1).strip()
            effect = match.group(2).strip()
            props.append((f"cause_{cause}", True))
            props.append((f"effect_{effect}", True))
            
        # Negations: not X, X is not Y
        for match in re.finditer(r'(?:not|n\'t)\s+([a-z_]+)', text_lower):
            var = match.group(1).strip()
            props.append((f"neg_{var}", False))
            
        # Comparatives: X > Y, X < Y
        for match in re.finditer(r'([0-9.]+)\s*([<>]=?)\s*([0-9.]+)', text):
            try:
                left = float(match.group(1))
                op = match.group(2)
                right = float(match.group(3))
                result = eval(f"{left} {op} {right}")
                props.append((f"cmp_{match.group(0)}", result))
            except:
                pass
                
        # Simple assertions: extract noun phrases as variables
        words = re.findall(r'\b[a-z]+\b', text_lower)
        for word in words[:10]:  # Limit to first 10 words
            if len(word) > 2:
                props.append((f"word_{word}", True))
                
        return props
    
    def _build_cnf(self, prompt: str, candidates: List[str]):
        """Build CNF formula from prompt and candidates."""
        self._reset()
        
        # Parse prompt
        prompt_props = self._parse_propositions(prompt)
        for var_name, is_pos in prompt_props:
            var_idx = self._get_var_idx(var_name)
            self.clauses.append(frozenset([var_idx if is_pos else -var_idx]))
            
        # Parse each candidate
        for cand in candidates:
            cand_props = self._parse_propositions(cand)
            for var_name, is_pos in cand_props:
                var_idx = self._get_var_idx(var_name)
                # Add as unit clauses
                self.clauses.append(frozenset([var_idx if is_pos else -var_idx]))
    
    def _assignment_from_text(self, text: str, n_vars: int) -> List[int]:
        """Create bitvector assignment from text."""
        props = self._parse_propositions(text)
        assignment = [0] * n_vars
        for var_name, is_pos in props:
            if var_name in self.var_to_idx:
                idx = self.var_to_idx[var_name]
                assignment[idx] = 1 if is_pos else 0
        return assignment
    
    def _evaluate_clause(self, clause: frozenset, assignment: List[int]) -> bool:
        """Check if clause is satisfied by assignment."""
        for lit in clause:
            var_idx = abs(lit) - 1 if lit > 0 else abs(lit)
            is_pos = lit > 0
            if var_idx < len(assignment):
                if (is_pos and assignment[var_idx] == 1) or (not is_pos and assignment[var_idx] == 0):
                    return True
        return len(clause) == 0  # Empty clause = true
    
    def _payoff(self, assignment: List[int]) -> float:
        """Count satisfied clauses."""
        if not self.clauses:
            return 0.0
        satisfied = sum(1 for clause in self.clauses if self._evaluate_clause(clause, assignment))
        return satisfied / max(len(self.clauses), 1)
    
    def _is_nash_equilibrium(self, assignment: List[int]) -> bool:
        """Check if assignment is Nash equilibrium (no profitable unilateral deviation)."""
        current_payoff = self._payoff(assignment)
        for i in range(len(assignment)):
            # Flip bit i
            assignment[i] = 1 - assignment[i]
            new_payoff = self._payoff(assignment)
            assignment[i] = 1 - assignment[i]  # Flip back
            if new_payoff > current_payoff + 1e-6:
                return False
        return True
    
    def _sensitivity(self, assignment: List[int]) -> float:
        """Compute Lyapunov-style sensitivity to perturbations."""
        if len(assignment) == 0:
            return 0.0
        current_payoff = self._payoff(assignment)
        total_delta = 0.0
        for i in range(len(assignment)):
            assignment[i] = 1 - assignment[i]
            new_payoff = self._payoff(assignment)
            assignment[i] = 1 - assignment[i]
            total_delta += abs(current_payoff - new_payoff)
        avg_delta = total_delta / len(assignment)
        return min(avg_delta, 1.0)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity and unanswerable questions."""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .* fail|why .* stopped)', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', p_lower) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p_lower) and not re.search(r'\bneither\b', p_lower):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful)', p_lower):
            return 0.3
        
        return 1.0  # No meta-issues detected
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by combined SAT-Nash-Lyapunov score."""
        if not candidates:
            return []
        
        self._build_cnf(prompt, candidates)
        n_vars = self.next_var_id
        
        results = []
        for cand in candidates:
            assignment = self._assignment_from_text(cand, n_vars)
            
            # SAT payoff
            payoff = self._payoff(assignment)
            
            # Nash stability
            is_nash = self._is_nash_equilibrium(assignment)
            stability = 1.0 if is_nash else 0.5
            
            # Lyapunov sensitivity
            sensitivity = self._sensitivity(assignment)
            
            # Combined score
            sat_score = payoff * stability * (1.0 - sensitivity * 0.5)
            
            # NCD tiebreaker (max 10% weight)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            final_score = 0.7 * sat_score + 0.2 * payoff + 0.1 * ncd_score
            
            reasoning = f"SAT={payoff:.2f} Nash={is_nash} Sens={sensitivity:.2f}"
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on meta-analysis and SAT score."""
        meta_conf = self._meta_confidence(prompt)
        
        if meta_conf < 0.5:
            return meta_conf
        
        self._build_cnf(prompt, [answer])
        n_vars = self.next_var_id
        
        if n_vars == 0:
            return 0.2  # No structure parsed
        
        assignment = self._assignment_from_text(answer, n_vars)
        payoff = self._payoff(assignment)
        is_nash = self._is_nash_equilibrium(assignment)
        sensitivity = self._sensitivity(assignment)
        
        sat_conf = payoff * (1.0 if is_nash else 0.6) * (1.0 - sensitivity * 0.3)
        
        # Cap confidence
        final_conf = min(sat_conf * meta_conf, 0.85)
        
        return max(0.0, min(1.0, final_conf))