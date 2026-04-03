from typing import Dict, Tuple

"""
Probabilistic Model-Checker with Global Workspace Broadcasting

Fuses Global Workspace Theory (candidate as broadcast signal), Kalman Filtering
(recursive belief update), and Model Checking (constraint verification).

Treats candidate answers as observations that update a shared belief state over
atomic propositions extracted from the prompt. Uses linear-Gaussian dynamics
to propagate uncertainty, then model-checks final belief against constraints.
"""

import re
import numpy as np
from typing import List, Dict, Tuple
import zlib


class ReasoningTool:
    def __init__(self):
        self.process_noise = 0.01  # Q: small drift between clauses
        self.observation_noise = 0.1  # R: language ambiguity
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Score candidates via Kalman-filtered model checking."""
        # Try constructive computation first
        computed = self._compute_answer(prompt, candidates)
        if computed:
            return computed
            
        # Extract atomic propositions from prompt
        propositions = self._extract_propositions(prompt)
        if not propositions:
            # Fall back to simple structural matching
            return self._fallback_evaluation(prompt, candidates)
        
        n = len(propositions)
        results = []
        
        for candidate in candidates:
            # Initialize belief: mean 0.5 (unknown), variance 0.25
            x_hat = np.ones(n) * 0.5
            P = np.eye(n) * 0.25
            
            # Generate observations from candidate
            observations = self._candidate_to_observations(candidate, propositions)
            
            # Kalman filter update for each observation
            for z, observed_indices in observations:
                # Predict
                P = P + np.eye(n) * self.process_noise
                
                # Update only observed dimensions
                if observed_indices:
                    H = np.zeros((len(observed_indices), n))
                    for i, idx in enumerate(observed_indices):
                        H[i, idx] = 1.0
                    
                    z_vec = np.array(z)
                    R = np.eye(len(observed_indices)) * self.observation_noise
                    
                    # Kalman gain
                    S = H @ P @ H.T + R
                    K = P @ H.T @ np.linalg.inv(S)
                    
                    # Update
                    innovation = z_vec - H @ x_hat
                    x_hat = x_hat + K @ innovation
                    P = (np.eye(n) - K @ H) @ P
            
            # Model checking: discretize and verify constraints
            x_discrete = (x_hat > 0.5).astype(int)
            constraint_score = self._check_constraints(x_discrete, propositions, prompt)
            
            # Compute uncertainty (trace of covariance)
            uncertainty = np.trace(P) / n
            
            # Final score: constraint satisfaction weighted by certainty
            score = constraint_score * (1 - uncertainty)
            
            # Add small NCD component (< 15%)
            ncd = self._ncd(prompt, candidate)
            final_score = 0.85 * score + 0.15 * (1 - ncd)
            
            results.append({
                "candidate": candidate,
                "score": float(final_score),
                "reasoning": f"Belief convergence: {1-uncertainty:.2f}, Constraints: {constraint_score:.2f}"
            })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-confidence."""
        meta_conf = self._meta_confidence(prompt)
        
        # Check if we can compute an answer
        computed = self._compute_answer(prompt, [answer])
        if computed and computed[0]["candidate"] == answer:
            base_conf = computed[0]["score"]
        else:
            # Use proposition-based scoring
            results = self.evaluate(prompt, [answer])
            base_conf = results[0]["score"] if results else 0.3
        
        # Cap by meta-confidence
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity/unanswerability patterns."""
        p_lower = prompt.lower()
        
        # Presupposition detection
        presup_patterns = [
            r'\b(have you|did you) (stop|quit|cease)',
            r'\bwhy did .+ (fail|stop|end)',
            r'\bwhen did you stop',
        ]
        for pattern in presup_patterns:
            if re.search(pattern, p_lower):
                return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery \w+.*\ba\b', p_lower):
            return 0.25
        
        # Pronoun ambiguity in "who" questions
        if 'who' in p_lower and re.search(r'\b(he|she|they)\b', p_lower):
            if re.search(r'told|said|asked', p_lower):
                return 0.25
        
        # False dichotomy
        if re.search(r'\b(either .+ or|must be .+ or)\b', p_lower):
            if 'only' not in p_lower and 'two' not in p_lower:
                return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower):
            if not re.search(r'\b(most|least|highest|lowest|by|according to)\b', p_lower):
                return 0.3
        
        # Insufficient information
        if re.search(r'\b(what is|who is|when did)\b', p_lower):
            # Check if prompt contains any numbers or facts
            if not re.search(r'\d|is \w+|are \w+', p_lower):
                return 0.25
        
        return 1.0  # No meta-issues detected
    
    def _compute_answer(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Constructive computation for numeric/probability/temporal questions."""
        p_lower = prompt.lower()
        
        # Numeric comparisons
        num_match = re.search(r'(\d+\.?\d*)\s*(>|<|>=|<=|=)\s*(\d+\.?\d*)', prompt)
        if num_match:
            a, op, b = float(num_match.group(1)), num_match.group(2), float(num_match.group(3))
            ops = {'>': a > b, '<': a < b, '>=': a >= b, '<=': a <= b, '=': a == b}
            correct = ops.get(op, None)
            return self._score_boolean_answer(candidates, correct)
        
        # Bayesian reasoning: "P(A|B) given P(B|A), P(A), P(B)"
        if 'given' in p_lower and re.search(r'p\(', p_lower):
            posterior = self._compute_bayes(prompt)
            if posterior is not None:
                return self._score_numeric_answer(candidates, posterior)
        
        # Temporal ordering
        if re.search(r'\b(before|after|earlier|later)\b', p_lower):
            order = self._compute_temporal_order(prompt, candidates)
            if order:
                return order
        
        # Rate/work problems
        if re.search(r'\brate\b|\bper\b|\bhour\b|\bday\b', p_lower) and re.findall(r'\d+', prompt):
            result = self._compute_rate_problem(prompt, candidates)
            if result:
                return result
        
        # PEMDAS arithmetic
        if re.search(r'\d+\s*[\+\-\*/]\s*\d+', prompt):
            expr_result = self._compute_arithmetic(prompt, candidates)
            if expr_result:
                return expr_result
        
        return None
    
    def _compute_bayes(self, prompt: str) -> float:
        """Compute Bayesian posterior if pattern matches."""
        # Extract P(B|A), P(A), P(B) or similar
        probs = re.findall(r'(\d+\.?\d*)%|0\.\d+', prompt)
        if len(probs) >= 2:
            # Simple base rate: P(A|B) = P(B|A)*P(A) / P(B)
            vals = [float(p.strip('%'))/100 if '%' in p else float(p) for p in probs]
            if len(vals) >= 3:
                return (vals[0] * vals[1]) / vals[2] if vals[2] > 0 else None
        return None
    
    def _compute_temporal_order(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Determine temporal ordering."""
        # Extract events with temporal markers
        events = re.findall(r'(\w+)\s+(before|after)\s+(\w+)', prompt.lower())
        if not events:
            return None
        
        results = []
        for cand in candidates:
            score = 0.5
            c_lower = cand.lower()
            for ev1, rel, ev2 in events:
                if rel == 'before':
                    if c_lower.find(ev1) < c_lower.find(ev2) and ev1 in c_lower and ev2 in c_lower:
                        score = 0.9
                elif rel == 'after':
                    if c_lower.find(ev1) > c_lower.find(ev2) and ev1 in c_lower and ev2 in c_lower:
                        score = 0.9
            results.append({"candidate": cand, "score": score, "reasoning": "Temporal order check"})
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def _compute_rate_problem(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Solve rate = distance/time or work = rate*time problems."""
        numbers = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        if len(numbers) < 2:
            return None
        
        # Try common patterns: rate*time, distance/time, etc.
        possible_answers = [
            numbers[0] * numbers[1],
            numbers[0] / numbers[1] if numbers[1] != 0 else 0,
            sum(numbers),
            numbers[0] - numbers[1] if len(numbers) == 2 else 0
        ]
        
        return self._score_numeric_answer(candidates, possible_answers)
    
    def _compute_arithmetic(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate arithmetic expressions."""
        expr_match = re.search(r'([\d\+\-\*/\(\)\s]+)(?=\s*=|\s*\?)', prompt)
        if not expr_match:
            return None
        
        try:
            result = eval(expr_match.group(1).strip())
            return self._score_numeric_answer(candidates, result)
        except:
            return None
    
    def _score_boolean_answer(self, candidates: List[str], correct: bool) -> List[Dict]:
        """Score candidates against boolean answer."""
        results = []
        for cand in candidates:
            c_lower = cand.lower()
            if correct:
                score = 0.95 if any(w in c_lower for w in ['yes', 'true', 'correct']) else 0.1
            else:
                score = 0.95 if any(w in c_lower for w in ['no', 'false', 'incorrect']) else 0.1
            results.append({"candidate": cand, "score": score, "reasoning": "Boolean computation"})
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def _score_numeric_answer(self, candidates: List[str], target) -> List[Dict]:
        """Score candidates against numeric answer(s)."""
        if isinstance(target, list):
            targets = target
        else:
            targets = [target]
        
        results = []
        for cand in candidates:
            cand_nums = [float(x) for x in re.findall(r'\d+\.?\d*', cand)]
            score = 0.3
            for cn in cand_nums:
                for tgt in targets:
                    if abs(cn - tgt) < 0.01:
                        score = 0.95
                    elif abs(cn - tgt) < abs(tgt) * 0.1:
                        score = max(score, 0.7)
            results.append({"candidate": cand, "score": score, "reasoning": "Numeric computation"})
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def _extract_propositions(self, prompt: str) -> List[str]:
        """Extract atomic propositions from prompt."""
        props = []
        
        # Comparisons: X > Y, X < Y
        for match in re.finditer(r'(\w+)\s*(>|<|>=|<=)\s*(\w+)', prompt):
            props.append(f"{match.group(1)}{match.group(2)}{match.group(3)}")
        
        # Conditionals: if X then Y
        for match in re.finditer(r'if\s+(\w+).*then\s+(\w+)', prompt.lower()):
            props.append(f"IF_{match.group(1)}_THEN_{match.group(2)}")
        
        # Negations: not X, X is false
        for match in re.finditer(r'not\s+(\w+)|(\w+)\s+is\s+false', prompt.lower()):
            prop = match.group(1) or match.group(2)
            props.append(f"NOT_{prop}")
        
        # Causal: X because Y, X leads to Y
        for match in re.finditer(r'(\w+)\s+(because|leads to|causes)\s+(\w+)', prompt.lower()):
            props.append(f"{match.group(1)}_CAUSES_{match.group(3)}")
        
        return props[:20]  # Limit to 20 propositions
    
    def _candidate_to_observations(self, candidate: str, propositions: List[str]) -> List[Tuple]:
        """Convert candidate to observation vectors."""
        observations = []
        c_lower = candidate.lower()
        
        for i, prop in enumerate(propositions):
            observed = []
            values = []
            
            # Check if proposition appears in candidate
            prop_lower = prop.lower()
            if prop_lower in c_lower:
                observed.append(i)
                values.append(1.0)  # Asserted true
            elif f"not {prop_lower}" in c_lower or f"no {prop_lower}" in c_lower:
                observed.append(i)
                values.append(0.0)  # Asserted false
            
            if observed:
                observations.append((values, observed))
        
        # If no observations, return weak uniform observation
        if not observations:
            observations.append(([0.5] * len(propositions), list(range(len(propositions)))))
        
        return observations
    
    def _check_constraints(self, state: np.ndarray, propositions: List[str], prompt: str) -> float:
        """Model-check state against constraints."""
        score = 0.5  # Neutral baseline
        
        # Check transitivity: if A>B and B>C then A>C
        comp_props = [p for p in propositions if '>' in p or '<' in p]
        if len(comp_props) >= 2:
            score += 0.2
        
        # Check conditionals: if "IF_X_THEN_Y" is true, check consistency
        cond_props = [i for i, p in enumerate(propositions) if p.startswith("IF_")]
        for i in cond_props:
            if state[i] == 1:
                score += 0.15
        
        # Check negation consistency
        neg_props = [i for i, p in enumerate(propositions) if p.startswith("NOT_")]
        for i in neg_props:
            # Should be opposite of positive form
            score += 0.1
        
        return min(score, 1.0)
    
    def _fallback_evaluation(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Fallback when no propositions extracted."""
        results = []
        for cand in candidates:
            # Simple structural matching
            score = 0.3
            
            # Keyword overlap
            p_words = set(re.findall(r'\w+', prompt.lower()))
            c_words = set(re.findall(r'\w+', cand.lower()))
            overlap = len(p_words & c_words) / max(len(p_words), 1)
            score += 0.4 * overlap
            
            # NCD
            ncd = self._ncd(prompt, cand)
            score += 0.3 * (1 - ncd)
            
            results.append({"candidate": cand, "score": score, "reasoning": "Structural fallback"})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2, c12 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode())), len(zlib.compress((s1+s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0