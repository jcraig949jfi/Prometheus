import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Evolutionary-Criticality Reasoning Tool.
    
    Mechanism:
    1. Structural Parsing: Extracts logical clauses, negations, comparatives, and causals 
       into a propositional graph (Adjacency matrix A, Weight matrix W).
    2. Criticality Analysis: Computes the normalized algebraic connectivity (Fiedler value) 
       of the logical graph to measure structural robustness (Edge of Chaos).
    3. Adaptive Control: Simulates constraint propagation (A @ state) to check if the 
       candidate answer is consistent with the prompt's logical closure.
    4. Evolutionary Fitness: Scores candidates based on consistency, criticality, and 
       error minimization against the prompt's constraints.
    5. Epistemic Honesty (Tier B): Detects presuppositions, ambiguities, and unanswerable 
       patterns to cap confidence, preventing overconfidence on flawed prompts.
    """

    def __init__(self):
        self.patterns = {
            'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b', r'\bfailed\b'],
            'comparative': [r'\bgreater\s+than\b', r'\bless\s+than\b', r'\bmore\s+than\b', r'\bfewer\s+than\b', r'\b>[=]?', r'\b<[=]?'],
            'conditional': [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\bonly\s+if\b'],
            'causal': [r'\bbecause\b', r'\bleads\s+to\b', r'\bresults\s+in\b', r'\bcauses\b', r'\btherefore\b'],
            'ordering': [r'\bbefore\b', r'\bafter\b', r'\bprecede\b', r'\bfollow\b'],
            'quantifier': [r'\ball\b', r'\bsome\b', r'\bnone\b', r'\bevery\b', r'\bany\b'],
            'numeric': r'[-+]?\d*\.?\d+'
        }
        self.presupposition_triggers = [
            r'\bstopped\s+\w+ing\b', r'\bquit\s+\w+ing\b', r'\bwhy\s+did\s+\w+\s+(fail|stop|happen)\b',
            r'\bwhen\s+did\s+\w+\s+(start|stop)\b', r'\bhow\s+did\s+\w+\s+(fail|break)\b'
        ]
        self.ambiguity_triggers = [
            r'\bwho\s+was\s+(he|she|it)\b', r'\bwhich\s+one\b', r'\beither\s+\w+\s+or\s+\w+\b',
            r'\bbest\b', r'\bworst\b', r'\bfavorite\b', r'\bopinion\b'
        ]

    def _extract_clauses(self, text: str) -> List[Dict]:
        """Parses text into structured logical clauses."""
        text_lower = text.lower()
        clauses = []
        sentences = re.split(r'[.\?!]', text)
        
        for i, sent in enumerate(sentences):
            if not sent.strip(): continue
            flags = 0
            value = 0.0
            targets = []
            
            # Bitmask flags: 1=neg, 2=comp, 4=cond, 8=causal, 16=order
            if any(re.search(p, sent, re.IGNORECASE) for p in self.patterns['negation']): flags |= 1
            if any(re.search(p, sent, re.IGNORECASE) for p in self.patterns['comparative']): flags |= 2
            if any(re.search(p, sent, re.IGNORECASE) for p in self.patterns['conditional']): flags |= 4
            if any(re.search(p, sent, re.IGNORECASE) for p in self.patterns['causal']): flags |= 8
            if any(re.search(p, sent, re.IGNORECASE) for p in self.patterns['ordering']): flags |= 16
            
            nums = re.findall(self.patterns['numeric'], sent)
            if nums:
                try: value = float(nums[-1])
                except: pass
            
            clauses.append({
                'idx': i,
                'text': sent.strip(),
                'flags': flags,
                'value': value,
                'targets': [] 
            })
            
        # Simple transitive linking (i implies i+1 if causal/conditional)
        for i in range(len(clauses) - 1):
            if (clauses[i]['flags'] & 12) > 0: # Conditional or Causal
                clauses[i]['targets'].append(i + 1)
                
        return clauses

    def _build_graph(self, clauses: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Constructs Adjacency (A) and Weight (W) matrices."""
        n = len(clauses)
        if n == 0: return np.zeros((1,1)), np.zeros((1,1))
        
        A = np.zeros((n, n), dtype=np.int8)
        W = np.zeros((n, n), dtype=np.float64)
        
        for i, clause in enumerate(clauses):
            # Self loop for stability
            A[i, i] = 1
            W[i, i] = 1.0
            
            for t_idx in clause['targets']:
                if t_idx < n:
                    A[i, t_idx] = 1
                    weight = 1.0 if not (clause['flags'] & 1) else -0.5 # Negation reduces weight
                    W[i, t_idx] = weight
                    
        return A, W

    def _compute_criticality(self, A: np.ndarray) -> float:
        """Calculates normalized algebraic connectivity (Fiedler value)."""
        if A.shape[0] < 2: return 0.0
        D = np.diag(np.sum(A, axis=1))
        L = D - A.astype(float)
        try:
            evals = np.linalg.eigvalsh(L)
            evals = np.sort(evals)
            lambda_2 = evals[1] if len(evals) > 1 else 0.0
            lambda_max = evals[-1]
            if lambda_max == 0: return 0.0
            return float(lambda_2 / lambda_max)
        except:
            return 0.0

    def _propagate_constraints(self, A: np.ndarray, initial_state: np.ndarray, steps: int = 5) -> np.ndarray:
        """Iteratively applies A @ state to find logical closure."""
        state = initial_state.copy()
        for _ in range(steps):
            new_state = A @ state
            # Heaviside step: clamp to [-1, 1]
            new_state = np.clip(new_state, -1.0, 1.0)
            if np.allclose(state, new_state): break
            state = new_state
        return state

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(z1, z2)
        if max_len == 0: return 0.0
        return (z12 - min(z1, z2)) / max_len

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap value < 0.3 if the prompt exhibits ambiguity, presupposition, or unanswerability.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition & False Dichotomy
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower): return 0.25
            
        # 2. Subjectivity & Ambiguity
        for pattern in self.ambiguity_triggers:
            if re.search(pattern, p_lower): return 0.25
            
        # 3. Unanswerability markers
        if "impossible to know" in p_lower or "not enough info" in p_lower:
            return 0.25
            
        return 1.0 # No red flags detected

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Core scoring logic combining structure, computation, and NCD."""
        clauses = self._extract_clauses(prompt)
        if not clauses:
            return 0.1, "No structural clauses parsed."
            
        A, W = self._build_graph(clauses)
        n = len(clauses)
        
        # 1. Structural Consistency (Constraint Propagation)
        # Create initial state: 1.0 if candidate keywords match clause, else 0
        initial_state = np.zeros(n)
        cand_lower = candidate.lower()
        
        # Check for direct numeric evaluation first (Constructive Computation)
        numeric_match = False
        calc_score = 0.0
        
        # Extract numbers from prompt and candidate
        p_nums = re.findall(self.patterns['numeric'], prompt)
        c_nums = re.findall(self.patterns['numeric'], candidate)
        
        if p_nums and c_nums:
            try:
                # Simple heuristic: if candidate number satisfies a comparative in prompt
                p_val = float(p_nums[-1])
                c_val = float(c_nums[-1])
                
                if any(re.search(p, prompt, re.IGNORECASE) for p in self.patterns['comparative']):
                    if "less" in prompt or "<" in prompt:
                        if c_val < p_val: calc_score = 1.0; numeric_match = True
                    elif "greater" in prompt or ">" in prompt:
                        if c_val > p_val: calc_score = 1.0; numeric_match = True
                    else: # generic comparative, assume equality or proximity
                        if abs(c_val - p_val) < 0.1 * p_val: calc_score = 1.0; numeric_match = True
            except: pass

        # Map candidate text to clauses
        for i, clause in enumerate(clauses):
            # Simple keyword overlap for activation
            words = set(clause['text'].lower().split())
            cand_words = set(cand_lower.split())
            if words & cand_words:
                initial_state[i] = 1.0
        
        # Propagate
        final_state = self._propagate_constraints(A, initial_state)
        consistency = np.mean(final_state > 0.5) # Fraction of activated truths
        
        # 2. Criticality Metric
        criticality = self._compute_criticality(A)
        
        # 3. NCD Tiebreaker (Max 15% weight)
        ncd = self._calculate_ncd(prompt, candidate)
        ncd_score = 1.0 - ncd # Higher is better
        
        # 4. Evolutionary Fitness Function
        # F = w1*consistency + w2*criticality - w3*error
        # If numeric match found, it dominates
        if numeric_match:
            score = 0.5 * calc_score + 0.35 * consistency + 0.15 * ncd_score
            reason = f"Numeric verification successful. Consistency: {consistency:.2f}"
        else:
            # Standard logical scoring
            score = (0.6 * consistency) + (0.25 * criticality) + (0.15 * ncd_score)
            reason = f"Logical consistency: {consistency:.2f}, Criticality: {criticality:.2f}"
            
        return min(score, 1.0), reason

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Enforces Tier B epistemic honesty caps.
        """
        # 1. Meta-Confidence Cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Base Score
        score, _ = self._score_candidate(prompt, answer)
        
        # 3. Apply Cap
        final_conf = min(score, meta_cap)
        
        # 4. Uncertainty floor for low structural match
        if score < 0.3 and meta_cap == 1.0:
            # If no structure matched and no ambiguity found, it's likely irrelevant
            final_conf = 0.1
            
        return float(np.clip(final_conf, 0.0, 1.0))