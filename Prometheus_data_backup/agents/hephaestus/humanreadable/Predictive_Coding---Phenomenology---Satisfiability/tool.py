from typing import Dict, Optional, Tuple

import re
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Predictive Coding x Phenomenology x SAT reasoning tool.
    
    Parses prompts/answers into weighted propositional clauses using phenomenological
    bracketing, then uses SAT solving to compute prediction error between prompt
    (top-down) and candidate (bottom-up) models. Lower error = higher score.
    """
    
    def __init__(self):
        self.literal_counter = 0
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._compute_score(prompt, cand)
            conf = self.confidence(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"SAT-based score={score:.3f}, confidence={conf:.3f}"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        score = self._compute_score(prompt, answer)
        numeric_conf = self._numeric_confidence(prompt, answer)
        
        if numeric_conf > 0:
            return min(0.95, numeric_conf)
        
        base_conf = min(0.85, score * 0.9)
        return max(meta_conf, base_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you|did you) (stop|quit|cease)', p):
            return 0.2
        if re.search(r'\bwhy did .+ (fail|stop|end)', p):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'\bevery \w+ .+ a \w+', p):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|they|it)\s', p) and re.search(r'\bwho\b', p):
            return 0.2
        
        # False dichotomy
        if re.search(r'\beither .+ or .+\?', p) and not re.search(r'\bonly\b', p):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prettiest)\b', p) and not re.search(r'\b(most|least|highest|lowest)\b', p):
            return 0.3
        
        # Unanswerable markers
        if re.search(r'\b(impossible|cannot determine|not enough|insufficient)\b', p):
            return 0.25
        
        return 1.0
    
    def _numeric_confidence(self, prompt: str, answer: str) -> float:
        nums_p = self._extract_numbers(prompt)
        nums_a = self._extract_numbers(answer)
        
        if not nums_p or not nums_a:
            return 0.0
        
        # Probability/percentage check
        if re.search(r'\b(probability|chance|percent)\b', prompt.lower()):
            result = self._compute_bayesian(prompt, answer)
            if result > 0:
                return 0.9
        
        # Arithmetic check
        if re.search(r'[\+\-\*/]', prompt):
            result = self._compute_arithmetic(prompt, answer)
            if result > 0:
                return 0.92
        
        # Comparison check
        comp_result = self._check_numeric_comparison(prompt, answer)
        if comp_result > 0:
            return 0.88
        
        return 0.0
    
    def _compute_score(self, prompt: str, candidate: str) -> float:
        # Parse into literals and clauses
        p_literals, p_clauses, p_weights = self._parse_text(prompt)
        c_literals, c_clauses, c_weights = self._parse_text(candidate)
        
        # Structural score via SAT
        sat_score = self._sat_score(p_literals, p_clauses, p_weights, 
                                     c_literals, c_clauses, c_weights)
        
        # Numeric computation score
        numeric_score = self._numeric_score(prompt, candidate)
        
        # NCD as tiebreaker (max 15%)
        ncd_score = 1.0 - self._ncd(prompt, candidate)
        
        # Weight: 50% structural, 35% numeric, 15% NCD
        final = 0.5 * sat_score + 0.35 * numeric_score + 0.15 * ncd_score
        return max(0.0, min(1.0, final))
    
    def _parse_text(self, text: str) -> Tuple[Dict, List, List]:
        literals = {}
        clauses = []
        weights = []
        
        text = text.lower()
        
        # Extract negations
        for match in re.finditer(r'\b(not|no|never)\s+(\w+)', text):
            lit_id = self.literal_counter
            self.literal_counter += 1
            literals[lit_id] = ('neg', match.group(2), False)
            clauses.append([(-1, lit_id)])
            weights.append(1.0)
        
        # Extract comparatives
        for match in re.finditer(r'(\w+)\s*(>|<|>=|<=|more than|less than)\s*(\w+)', text):
            lit_id = self.literal_counter
            self.literal_counter += 1
            literals[lit_id] = ('comp', match.group(1), match.group(2), match.group(3))
            clauses.append([(1, lit_id)])
            weights.append(1.5)
        
        # Extract conditionals
        for match in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)[\.\,\;]', text):
            lit_p = self.literal_counter
            self.literal_counter += 1
            lit_q = self.literal_counter
            self.literal_counter += 1
            literals[lit_p] = ('cond_ante', match.group(1))
            literals[lit_q] = ('cond_cons', match.group(2))
            clauses.append([(-1, lit_p), (1, lit_q)])
            weights.append(2.0)
        
        # Extract causal
        for match in re.finditer(r'(\w+)\s+(because|leads to|causes)\s+(\w+)', text):
            lit_id = self.literal_counter
            self.literal_counter += 1
            literals[lit_id] = ('causal', match.group(1), match.group(3))
            clauses.append([(1, lit_id)])
            weights.append(1.5)
        
        return literals, clauses, weights
    
    def _sat_score(self, p_lit, p_clauses, p_weights, c_lit, c_clauses, c_weights) -> float:
        all_clauses = p_clauses + c_clauses
        all_weights = p_weights + c_weights
        
        if not all_clauses:
            return 0.5
        
        # Simple DPLL-lite: try to satisfy all clauses
        assignment = {}
        for clause in all_clauses:
            satisfied = False
            for polarity, lit_id in clause:
                if lit_id in assignment:
                    if (polarity > 0 and assignment[lit_id]) or (polarity < 0 and not assignment[lit_id]):
                        satisfied = True
                        break
            
            if not satisfied:
                # Try to satisfy by assigning first literal
                if clause:
                    polarity, lit_id = clause[0]
                    assignment[lit_id] = (polarity > 0)
        
        # Compute error
        unsatisfied_weight = 0.0
        total_weight = sum(all_weights) if all_weights else 1.0
        
        for i, clause in enumerate(all_clauses):
            satisfied = False
            for polarity, lit_id in clause:
                if lit_id in assignment:
                    if (polarity > 0 and assignment[lit_id]) or (polarity < 0 and not assignment[lit_id]):
                        satisfied = True
                        break
            
            if not satisfied and i < len(all_weights):
                unsatisfied_weight += all_weights[i]
        
        error = unsatisfied_weight / total_weight if total_weight > 0 else 0.5
        return 1.0 - error
    
    def _numeric_score(self, prompt: str, candidate: str) -> float:
        # Bayesian
        bayes = self._compute_bayesian(prompt, candidate)
        if bayes > 0:
            return bayes
        
        # Arithmetic
        arith = self._compute_arithmetic(prompt, candidate)
        if arith > 0:
            return arith
        
        # Comparison
        comp = self._check_numeric_comparison(prompt, candidate)
        if comp > 0:
            return comp
        
        # Temporal
        temp = self._compute_temporal(prompt, candidate)
        if temp > 0:
            return temp
        
        return 0.5
    
    def _compute_bayesian(self, prompt: str, candidate: str) -> float:
        # Extract P(A|B), P(B|A), base rates
        nums_p = self._extract_numbers(prompt)
        nums_c = self._extract_numbers(candidate)
        
        if len(nums_p) >= 2 and nums_c:
            # Simple Bayes: posterior proportional to likelihood * prior
            prior = nums_p[0] / 100.0 if nums_p[0] <= 1.0 else nums_p[0]
            likelihood = nums_p[1] / 100.0 if nums_p[1] <= 1.0 else nums_p[1]
            
            posterior = (likelihood * prior) / ((likelihood * prior) + (1 - prior) * 0.5)
            
            candidate_val = nums_c[0] / 100.0 if nums_c[0] <= 1.0 else nums_c[0]
            
            error = abs(posterior - candidate_val)
            return max(0.0, 1.0 - error * 5)
        
        return 0.0
    
    def _compute_arithmetic(self, prompt: str, candidate: str) -> float:
        nums_c = self._extract_numbers(candidate)
        if not nums_c:
            return 0.0
        
        # Try to evaluate expression in prompt
        try:
            expr = re.search(r'[\d\.\+\-\*/\(\)\s]+', prompt)
            if expr:
                result = eval(expr.group())
                error = abs(result - nums_c[0])
                return max(0.0, 1.0 - error / (abs(result) + 1))
        except:
            pass
        
        return 0.0
    
    def _check_numeric_comparison(self, prompt: str, candidate: str) -> float:
        nums_p = self._extract_numbers(prompt)
        
        if len(nums_p) >= 2:
            a, b = nums_p[0], nums_p[1]
            
            if re.search(r'\bgreater\b|\bmore\b|>\b', prompt.lower()):
                if (a > b and re.search(r'\byes\b|true|correct', candidate.lower())) or \
                   (a <= b and re.search(r'\bno\b|false|incorrect', candidate.lower())):
                    return 0.95
            
            if re.search(r'\bless\b|\bfewer\b|<\b', prompt.lower()):
                if (a < b and re.search(r'\byes\b|true|correct', candidate.lower())) or \
                   (a >= b and re.search(r'\bno\b|false|incorrect', candidate.lower())):
                    return 0.95
        
        return 0.0
    
    def _compute_temporal(self, prompt: str, candidate: str) -> float:
        # Extract temporal ordering
        before = re.findall(r'(\w+)\s+before\s+(\w+)', prompt.lower())
        after = re.findall(r'(\w+)\s+after\s+(\w+)', prompt.lower())
        
        if before or after:
            # Check if candidate preserves ordering
            for a, b in before:
                if a in candidate.lower() and b in candidate.lower():
                    if candidate.lower().index(a) < candidate.lower().index(b):
                        return 0.85
            
            for a, b in after:
                if a in candidate.lower() and b in candidate.lower():
                    if candidate.lower().index(a) > candidate.lower().index(b):
                        return 0.85
        
        return 0.0
    
    def _extract_numbers(self, text: str) -> List[float]:
        matches = re.findall(r'\b\d+\.?\d*\b', text)
        return [float(m) for m in matches]
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2))