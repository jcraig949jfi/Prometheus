from typing import Dict, Tuple

import re
import numpy as np
from typing import List, Dict, Tuple
import zlib

class ReasoningTool:
    """
    Compressed Sensing x Compositionality x Mechanism Design reasoning tool.
    
    Treats answer evaluation as sparse recovery: parses text into atomic propositions,
    builds measurement matrix A where rows=surface patterns, columns=propositions,
    solves LASSO to find sparsest logical explanation, scores via proper scoring rule.
    
    Computes answers via formal representations (constraints, algebra, logic) rather
    than pattern matching. Includes epistemic honesty via meta-confidence.
    """
    
    def __init__(self):
        self.proposition_dict = {}
        self.prop_index = 0
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            reasoning = self._explain_score(prompt, cand, score)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        comp_conf = self._computational_confidence(prompt, answer)
        return min(meta_conf, comp_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity, presupposition, unanswerability in prompt."""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you|did you) (stop|quit|cease)\b', p_lower):
            return 0.2
        if re.search(r'\bwhy (did|does|is).*(fail|stop|wrong)\b', p_lower):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\b(a|an)\b', p_lower):
            return 0.3
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\b(either|only) (a|b)\b.*\bor\b', p_lower):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower):
            return 0.4
        
        return 1.0
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        # Extract propositions
        prompt_props = self._extract_propositions(prompt)
        cand_props = self._extract_propositions(candidate)
        
        # Computational scoring (50%)
        comp_score = self._computational_score(prompt, candidate)
        
        # Sparse recovery scoring (35%)
        sparse_score = self._sparse_recovery_score(prompt_props, cand_props)
        
        # NCD tiebreaker (15%)
        ncd_score = 1.0 - self._ncd(prompt, candidate)
        
        return 0.5 * comp_score + 0.35 * sparse_score + 0.15 * ncd_score
    
    def _computational_score(self, prompt: str, candidate: str) -> float:
        """Compute answer via formal representations."""
        scores = []
        
        # Numeric comparison
        num_score = self._numeric_comparison(prompt, candidate)
        if num_score is not None:
            scores.append(num_score)
        
        # Algebraic solving (bat-and-ball)
        alg_score = self._algebraic_solve(prompt, candidate)
        if alg_score is not None:
            scores.append(alg_score)
        
        # Logic (modus tollens, transitivity)
        log_score = self._logic_compute(prompt, candidate)
        if log_score is not None:
            scores.append(log_score)
        
        # Bayesian update
        bayes_score = self._bayesian_compute(prompt, candidate)
        if bayes_score is not None:
            scores.append(bayes_score)
        
        # Constraint satisfaction
        csp_score = self._constraint_solve(prompt, candidate)
        if csp_score is not None:
            scores.append(csp_score)
        
        return max(scores) if scores else 0.5
    
    def _numeric_comparison(self, prompt: str, candidate: str) -> float:
        """Parse and compute numeric comparisons."""
        nums_p = re.findall(r'\b\d+\.?\d*\b', prompt)
        nums_c = re.findall(r'\b\d+\.?\d*\b', candidate)
        
        if len(nums_p) >= 2 and len(nums_c) >= 1:
            vals_p = [float(n) for n in nums_p]
            val_c = float(nums_c[0])
            
            if re.search(r'\b(greater|larger|more)\b', prompt.lower()):
                correct = max(vals_p)
                return 1.0 if abs(val_c - correct) < 0.01 else 0.0
            elif re.search(r'\b(less|smaller|fewer)\b', prompt.lower()):
                correct = min(vals_p)
                return 1.0 if abs(val_c - correct) < 0.01 else 0.0
        
        return None
    
    def _algebraic_solve(self, prompt: str, candidate: str) -> float:
        """Solve algebraic word problems."""
        # Bat and ball: total X, one costs Y more, find price
        match = re.search(r'cost.*\$?(\d+\.?\d*).*one.*\$?(\d+\.?\d*)\s*more', prompt.lower())
        if match:
            total = float(match.group(1))
            diff = float(match.group(2))
            # ball = (total - diff) / 2
            ball = (total - diff) / 2.0
            
            nums_c = re.findall(r'\d+\.?\d*', candidate)
            if nums_c:
                val_c = float(nums_c[0])
                return 1.0 if abs(val_c - ball) < 0.01 else 0.0
        
        return None
    
    def _logic_compute(self, prompt: str, candidate: str) -> float:
        """Execute logical inference."""
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Modus tollens: if A then B, not B, therefore not A
        if re.search(r'if\s+(\w+).*then\s+(\w+)', p_lower):
            match = re.search(r'if\s+(\w+).*then\s+(\w+)', p_lower)
            a_term = match.group(1)
            b_term = match.group(2)
            
            if re.search(r'not\s+' + b_term, p_lower):
                if re.search(r'not\s+' + a_term, c_lower):
                    return 1.0
                elif re.search(r'\b' + a_term + r'\b', c_lower) and 'not' not in c_lower:
                    return 0.0
        
        # Transitivity: A > B, B > C => A > C
        trans_match = re.findall(r'(\w+)\s*>\s*(\w+)', p_lower)
        if len(trans_match) >= 2:
            relations = {trans_match[0][0]: trans_match[0][1], 
                        trans_match[1][0]: trans_match[1][1]}
            # Check transitive conclusion
            if trans_match[0][1] == trans_match[1][0]:
                expected = f"{trans_match[0][0]} > {trans_match[1][1]}"
                if expected.lower() in c_lower.replace(' ', ''):
                    return 1.0
        
        return None
    
    def _bayesian_compute(self, prompt: str, candidate: str) -> float:
        """Compute Bayesian posterior."""
        # P(A|B) = P(B|A) * P(A) / P(B)
        probs = re.findall(r'(\d+\.?\d*)%', prompt)
        if len(probs) >= 2:
            # Simple base rate: prior and likelihood
            prior = float(probs[0]) / 100.0
            likelihood = float(probs[1]) / 100.0
            
            # Assume P(B) in denominator
            if len(probs) >= 3:
                p_b = float(probs[2]) / 100.0
            else:
                p_b = likelihood * prior + (1 - likelihood) * (1 - prior)
            
            posterior = (likelihood * prior) / p_b if p_b > 0 else 0.0
            
            nums_c = re.findall(r'\d+\.?\d*', candidate)
            if nums_c:
                val_c = float(nums_c[0]) / 100.0 if '%' in candidate else float(nums_c[0])
                return 1.0 if abs(val_c - posterior) < 0.05 else 0.0
        
        return None
    
    def _constraint_solve(self, prompt: str, candidate: str) -> float:
        """Constraint satisfaction via elimination."""
        # Extract entities and constraints
        entities = re.findall(r'\b([A-Z][a-z]+)\b', prompt)
        if len(entities) >= 3:
            # Simple elimination: "not A, not B => C"
            negations = re.findall(r'not\s+([A-Z][a-z]+)', prompt.lower())
            remaining = [e for e in entities if e.lower() not in negations]
            
            if remaining and remaining[0].lower() in candidate.lower():
                return 1.0
        
        return None
    
    def _sparse_recovery_score(self, prompt_props: List[Tuple], cand_props: List[Tuple]) -> float:
        """LASSO sparse recovery over propositions."""
        # Build dictionary
        all_props = list(set(prompt_props + cand_props))
        n = len(all_props)
        if n == 0:
            return 0.5
        
        prop_to_idx = {p: i for i, p in enumerate(all_props)}
        
        # Measurement matrix A: patterns x propositions
        patterns = self._extract_patterns(cand_props)
        m = len(patterns)
        if m == 0:
            return 0.5
        
        A = np.zeros((m, n))
        for i, pat in enumerate(patterns):
            for j, prop in enumerate(all_props):
                if self._pattern_matches_prop(pat, prop):
                    A[i, j] = 1.0
        
        # Observation vector b
        b = np.ones(m)
        
        # ISTA
        x_hat = self._ista(A, b, lambda_reg=0.1, max_iter=50)
        
        # Proper scoring rule
        residual = np.linalg.norm(A @ x_hat - b) ** 2
        sparsity = np.sum(np.abs(x_hat))
        score = -(0.5 * residual + 0.1 * sparsity)
        
        # Normalize to [0, 1]
        return 1.0 / (1.0 + np.exp(-score))
    
    def _ista(self, A: np.ndarray, b: np.ndarray, lambda_reg: float, max_iter: int) -> np.ndarray:
        """Iterative Soft-Thresholding Algorithm for LASSO."""
        n = A.shape[1]
        x = np.zeros(n)
        L = np.linalg.norm(A.T @ A, 2) + 1e-6
        alpha = 1.0 / L
        
        for _ in range(max_iter):
            grad = A.T @ (A @ x - b)
            x = self._soft_threshold(x - alpha * grad, alpha * lambda_reg)
        
        return x
    
    def _soft_threshold(self, x: np.ndarray, threshold: float) -> np.ndarray:
        """Soft thresholding operator."""
        return np.sign(x) * np.maximum(np.abs(x) - threshold, 0)
    
    def _extract_propositions(self, text: str) -> List[Tuple]:
        """Parse text into (subject, predicate, object, flags) tuples."""
        props = []
        sentences = re.split(r'[.!?]', text)
        
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            
            # Extract SVO
            tokens = sent.split()
            if len(tokens) < 2:
                continue
            
            # Simple heuristic: first noun = subject, verb, last noun = object
            subj = tokens[0]
            pred = tokens[1] if len(tokens) > 1 else ""
            obj = tokens[-1] if len(tokens) > 2 else ""
            
            # Flags
            has_neg = 'not' in sent.lower() or "n't" in sent.lower()
            has_comp = bool(re.search(r'\b(more|less|greater|fewer)\b', sent.lower()))
            has_cond = bool(re.search(r'\b(if|unless)\b', sent.lower()))
            has_causal = bool(re.search(r'\b(because|leads|results)\b', sent.lower()))
            
            props.append((subj, pred, obj, has_neg, has_comp, has_cond, has_causal))
        
        return props
    
    def _extract_patterns(self, props: List[Tuple]) -> List[str]:
        """Extract surface patterns from propositions."""
        patterns = []
        for p in props:
            subj, pred, obj, neg, comp, cond, caus = p
            if neg:
                patterns.append("NEG")
            if comp:
                patterns.append("COMP")
            if cond:
                patterns.append("COND")
            if caus:
                patterns.append("CAUS")
            patterns.append(f"PRED_{pred}")
        return list(set(patterns))
    
    def _pattern_matches_prop(self, pattern: str, prop: Tuple) -> bool:
        """Check if pattern is explained by proposition."""
        subj, pred, obj, neg, comp, cond, caus = prop
        if pattern == "NEG" and neg:
            return True
        if pattern == "COMP" and comp:
            return True
        if pattern == "COND" and cond:
            return True
        if pattern == "CAUS" and caus:
            return True
        if pattern.startswith("PRED_") and pred in pattern:
            return True
        return False
    
    def _computational_confidence(self, prompt: str, answer: str) -> float:
        """Confidence based on computational certainty."""
        # If we computed a definitive answer, high confidence
        if self._numeric_comparison(prompt, answer) == 1.0:
            return 0.95
        if self._algebraic_solve(prompt, answer) == 1.0:
            return 0.95
        if self._logic_compute(prompt, answer) == 1.0:
            return 0.9
        if self._bayesian_compute(prompt, answer) == 1.0:
            return 0.85
        
        # Otherwise moderate
        return 0.6
    
    def _ncd(self, x: str, y: str) -> float:
        """Normalized Compression Distance."""
        cx = len(zlib.compress(x.encode()))
        cy = len(zlib.compress(y.encode()))
        cxy = len(zlib.compress((x + y).encode()))
        return (cxy - min(cx, cy)) / max(cx, cy) if max(cx, cy) > 0 else 0.0
    
    def _explain_score(self, prompt: str, candidate: str, score: float) -> str:
        """Generate reasoning explanation."""
        comp = self._computational_score(prompt, candidate)
        if comp > 0.9:
            return f"Computed answer matches (score={score:.2f})"
        elif comp > 0.5:
            return f"Partial computational match (score={score:.2f})"
        else:
            return f"Sparse recovery score (score={score:.2f})"