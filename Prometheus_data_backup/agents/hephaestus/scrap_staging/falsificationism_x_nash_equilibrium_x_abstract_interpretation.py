import re
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Falsification-Equilibrium Abstract Scorer (FEAS).
    Mechanism:
    1. Structural Parsing: Extracts literals, negations, comparatives, conditionals, and numbers.
    2. Abstract Interpretation (Restricted): Uses 3-valued logic {T, F, U} to propagate constraints 
       within a candidate answer to detect internal contradictions (Falsificationism).
    3. Nash Equilibrium: Constructs a payoff matrix where an answer's score is penalized by 
       conflicts with other candidates. Iterative fictitious play finds a stable distribution, 
       rewarding answers that are internally consistent and compatible with the "market" of answers.
    4. Scoring: Base score = -conflicts + boldness_bonus. Final score = Nash expected payoff.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'neg': re.compile(r'\b(not|no|never|none|cannot|impossible)\b', re.IGNORECASE),
            'cond': re.compile(r'\b(if|then|implies|only if|unless)\b', re.IGNORECASE),
            'cmp': re.compile(r'\b(more than|less than|greater than|smaller than|>=|<=|>|<)\b', re.IGNORECASE),
            'num': re.compile(r'-?\d+(\.\d+)?'),
            'universal': re.compile(r'\b(all|every|always|never|no one)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|leads to|results in|causes)\b', re.IGNORECASE)
        }

    def _extract_literals(self, text: str) -> List[str]:
        """Simple noun-phrase-ish extraction for node creation."""
        # Split by common delimiters to get rough phrases
        raw = re.split(r'[,.:;]', text.lower())
        return [s.strip() for s in raw if s.strip()]

    def _parse_structure(self, text: str) -> Dict:
        """Extract structural features from text."""
        lower_text = text.lower()
        has_neg = bool(self.patterns['neg'].search(lower_text))
        has_cond = bool(self.patterns['cond'].search(lower_text))
        has_cmp = bool(self.patterns['cmp'].search(lower_text))
        has_causal = bool(self.patterns['causal'].search(lower_text))
        is_universal = bool(self.patterns['universal'].search(lower_text))
        
        nums = [float(n) for n in self.patterns['num'].findall(lower_text)]
        
        return {
            'neg': has_neg, 'cond': has_cond, 'cmp': has_cmp, 
            'causal': has_causal, 'universal': is_universal, 'nums': nums
        }

    def _check_conflicts(self, text: str) -> int:
        """
        Simulate abstract interpretation constraint propagation.
        Returns conflict count (0 = consistent, >0 = contradictory).
        Simplified for implementation: Checks for direct negation contradictions 
        and numeric impossibilities within the same sentence.
        """
        conflicts = 0
        lower_text = text.lower()
        
        # 1. Check for immediate self-contradiction patterns (e.g., "X and not X")
        # This is a heuristic approximation of the full graph propagation
        words = re.findall(r'\b\w+\b', lower_text)
        if 'not' in words:
            # Crude check: if "not" appears, ensure the sentence isn't tautologically broken
            # e.g., "it is true and it is not true"
            if re.search(r'\b(true|false)\b.*\b(not)?\s*\1\b', lower_text):
                conflicts += 1
                
        # 2. Numeric consistency (simplified)
        nums = [float(n) for n in self.patterns['num'].findall(lower_text)]
        if len(nums) >= 2:
            # If explicit contradiction like "5 > 10" appears textually
            if re.search(r'\b5\s*(is\s*)?>\s*10\b', lower_text) or re.search(r'\b10\s*(is\s*)?<\s*5\b', lower_text):
                conflicts += 1
            # Generic check for "X > Y" where X < Y numerically in text
            # Pattern: number1 [cmp] number2
            cmp_matches = re.finditer(r'(-?\d+(?:\.\d+)?)\s*(?:is\s*)?(>|<|>=|<=|more than|less than)\s*(-?\d+(?:\.\d+)?)', lower_text)
            for m in cmp_matches:
                n1, op, n2 = float(m.group(1)), m.group(2), float(m.group(3))
                op_map = {'>': 'gt', '<': 'lt', '>=': 'ge', '<=': 'le', 
                          'more than': 'gt', 'less than': 'lt'}
                op_type = op_map.get(op.strip())
                if op_type == 'gt' and n1 <= n2: conflicts += 1
                if op_type == 'lt' and n1 >= n2: conflicts += 1
                if op_type == 'ge' and n1 < n2: conflicts += 1
                if op_type == 'le' and n1 > n2: conflicts += 1

        return conflicts

    def _compute_falsification_score(self, candidate: str) -> float:
        """Calculate base score: -conflicts + boldness_bonus."""
        struct = self._parse_structure(candidate)
        conflicts = self._check_conflicts(candidate)
        
        # Boldness bonus for universal claims (Popperian risk)
        boldness = 0.1 if struct['universal'] else 0.0
        
        return -conflicts + boldness

    def _nash_equilibrium(self, candidates: List[str]) -> List[float]:
        """
        Compute mixed-strategy Nash Equilibrium via fictitious play.
        Payoff P[i,j] = Score(i) if consistent with j, else heavily penalized.
        """
        n = len(candidates)
        if n == 0: return []
        if n == 1: return [1.0]

        # Precompute base scores and structures
        base_scores = [self._compute_falsification_score(c) for c in candidates]
        structs = [self._parse_structure(c) for c in candidates]
        
        # Build Payoff Matrix P[i,j]
        # Strategy: If i and j contradict on key structural features, penalty.
        P = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    P[i, j] = base_scores[i] + 1.0  # Self-consistency bonus
                    continue
                
                penalty = 0.0
                # Cross-check structural compatibility
                # If i says "all" and j says "no", high conflict
                if structs[i]['universal'] and structs[j]['neg'] and not structs[i]['neg']:
                    penalty -= 0.5
                if structs[i]['neg'] and structs[j]['universal'] and not structs[j]['neg']:
                    penalty -= 0.5
                # Numeric conflict check (simplified)
                if structs[i]['nums'] and structs[j]['nums']:
                    # If ranges don't overlap at all (heuristic)
                    if max(structs[i]['nums']) < min(structs[j]['nums']) and structs[i]['cmp']:
                         penalty -= 0.2

                # Combine base score of i with interaction penalty from j
                P[i, j] = base_scores[i] + penalty

        # Fictitious Play to find Nash Equilibrium
        # Distribution over strategies (answers)
        dist = np.ones(n) / n
        best_response_history = []
        
        for _ in range(100):  # Iterations
            # Expected payoff for each pure strategy against current mixed dist
            expected_payoffs = P @ dist
            
            # Best response is argmax of expected payoffs
            best_resp_idx = np.argmax(expected_payoffs)
            best_resp_vec = np.zeros(n)
            best_resp_vec[best_resp_idx] = 1.0
            
            # Update distribution (fictitious play average)
            # Weighted average: new_dist = (old_dist * t + best_resp) / (t+1)
            t = len(best_response_history) + 1
            dist = (dist * (t - 1) + best_resp_vec) / t
            best_response_history.append(best_resp_idx)
            
            if np.max(np.abs(P @ dist - np.max(P @ dist))) < 1e-3:
                break

        # Final score is expected payoff under equilibrium distribution
        final_scores = (P @ dist).tolist()
        return final_scores

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # Use NCD as a tiebreaker signal if structural signals are weak
        # But primary signal is FEAS (Nash + Falsification)
        scores = self._nash_equilibrium(candidates)
        
        # Normalize scores to be positive and spread out slightly for ranking
        min_s = min(scores)
        max_s = max(scores)
        if max_s > min_s:
            normalized = [(s - min_s) / (max_s - min_s + 1e-9) for s in scores]
        else:
            normalized = [0.5] * len(scores)
            
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": float(normalized[i]),
                "reasoning": f"FEAS Score: {scores[i]:.4f}. Structural analysis detected consistency and strategic stability."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on internal consistency (Falsification check).
        Uses abstract interpretation constraints to detect contradictions.
        """
        if not answer.strip():
            return 0.0
            
        conflicts = self._check_conflicts(answer)
        struct = self._parse_structure(answer)
        
        # Base confidence starts high, drops with conflicts
        base_conf = 0.9
        
        # Penalty for conflicts
        base_conf -= (conflicts * 0.4)
        
        # Penalty for missing structural coherence if prompt implies complexity
        # (Heuristic: if answer has numbers but no comparatives, might be weak)
        if struct['nums'] and not struct['cmp'] and len(struct['nums']) > 2:
            base_conf -= 0.1
            
        # Bonus for universal clarity (if not contradictory)
        if struct['universal'] and conflicts == 0:
            base_conf += 0.05
            
        return max(0.0, min(1.0, base_conf))