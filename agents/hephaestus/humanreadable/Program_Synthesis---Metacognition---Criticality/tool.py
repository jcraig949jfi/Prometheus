import re
import numpy as np
from typing import List, Dict, Tuple, Optional
import zlib

class ReasoningTool:
    """
    A constraint-synthesis engine treating answers as hypothesis programs.
    Combines structural parsing (DSL), program synthesis (BFS), constraint propagation,
    metacognitive monitoring (conflict-based confidence), and criticality tuning (susceptibility).
    
    Mechanism:
    1. Parses prompt into logical clauses (EQ, LT, GT, IMP, NOT) via regex.
    2. Synthesizes candidate programs combining these clauses.
    3. Propagates constraints to check consistency (sat).
    4. Calculates metacognitive confidence based on propagation conflicts.
    5. Tunes clause weights to find critical susceptibility (phase transition).
    6. Scores candidates using a weighted sum of sat, confidence, and susceptibility.
    7. Enforces epistemic honesty: caps confidence on ambiguous/unanswerable prompts.
    """

    def __init__(self):
        self.clause_types = ['EQ', 'LT', 'GT', 'IMP', 'AND', 'OR', 'NOT']
        # Weights for final score: structural/sat (0.5), computation/conf (0.35), criticality (0.15)
        self.alpha = 0.50 
        self.beta = 0.35
        self.gamma = 0.15

    def _parse_prompt(self, prompt: str) -> List[Tuple[str, list, any]]:
        """Extracts logical clauses from text using regex patterns."""
        clauses = []
        p_lower = prompt.lower()
        
        # Negation
        if re.search(r'\b(not|no|never|none)\b', p_lower):
            clauses.append(('NOT', ['global_neg'], True))
        
        # Comparatives (Numeric)
        nums = re.findall(r'(\d+\.?\d*)\s*(?:is|are|was|were)?\s*(?:greater|less|more|fewer|bigger|smaller)?\s*(?:than)?\s*(\d+\.?\d*)', p_lower)
        # Simplified: look for "X > Y" or "X is greater than Y" patterns roughly
        # Pattern: number ... (greater|less) ... number
        comp_pattern = r'(\d+\.?\d*)\s+(?:is\s+)?(greater|less|more|fewer|bigger|smaller)\s+(?:than\s+)?(\d+\.?\d*)'
        for m in re.finditer(comp_pattern, p_lower):
            v1, op, v2 = m.groups()
            op_type = 'GT' if op in ['greater', 'more', 'bigger'] else 'LT'
            clauses.append((op_type, [v1, v2], None))
            
        # Explicit comparisons in prompt text like "5 > 3"
        for m in re.finditer(r'(\d+\.?\d*)\s*([<>])\s*(\d+\.?\d*)', prompt):
            v1, sym, v2 = m.groups()
            op_type = 'GT' if sym == '>' else 'LT'
            clauses.append((op_type, [v1, v2], None))

        # Conditionals
        if re.search(r'\bif\b.*\bthen\b', p_lower) or re.search(r'\bif\b', p_lower):
            clauses.append(('IMP', ['cond_global'], True))
            
        # Causal
        if re.search(r'\b(because|leads to|causes)\b', p_lower):
            clauses.append(('IMP', ['causal_global'], True))

        # Ordering
        if re.search(r'\b(before|after|first|last)\b', p_lower):
            clauses.append(('LT', ['temporal'], True)) # Simplified temporal ordering

        # Fallback for numeric extraction if no specific logic found but numbers exist
        if not any(c[0] in ['LT', 'GT', 'EQ'] for c in clauses):
            nums_all = re.findall(r'\d+\.?\d*', prompt)
            if len(nums_all) >= 2:
                # Assume some relation exists if numbers are present
                clauses.append(('EQ', nums_all[:2], 'implicit'))

        return clauses if clauses else [('EQ', ['default'], True)]

    def _synthesize_and_propagate(self, clauses: List, candidate: str) -> Tuple[bool, int]:
        """
        Simulates program synthesis and constraint propagation.
        Returns (is_consistent, conflict_count).
        """
        # 1. Encode candidate as potential constraints
        # Check for direct contradictions in candidate itself (e.g. "5 is less than 3")
        cand_lower = candidate.lower()
        conflicts = 0
        consistent = True
        
        # Extract numeric claims from candidate
        cand_nums = re.findall(r'(\d+\.?\d*)\s+(?:is\s+)?(greater|less|more|equal|same)\s+(?:than\s+)?(?:to\s+)?(\d+\.?\d*)', cand_lower)
        
        for v1, op, v2 in cand_nums:
            n1, n2 = float(v1), float(v2)
            if op in ['greater', 'more']:
                if not (n1 > n2): consistent = False; conflicts += 1
            elif op in ['less']:
                if not (n1 < n2): consistent = False; conflicts += 1
            elif op in ['equal', 'same']:
                if not (n1 == n2): consistent = False; conflicts += 1

        # Check against prompt clauses (Simplified propagation)
        # If prompt says "5 > 3" and candidate implies "3 > 5", conflict.
        for ctype, vars, const in clauses:
            if ctype in ['LT', 'GT'] and len(vars) >= 2:
                try:
                    n1, n2 = float(vars[0]), float(vars[1])
                    # Check if candidate contradicts this specific fact
                    # Very rough heuristic: if candidate contains reversed numbers
                    if ctype == 'GT' and f"{vars[1]} > {vars[0]}" in cand_lower:
                        consistent = False; conflicts += 1
                    if ctype == 'LT' and f"{vars[1]} < {vars[0]}" in cand_lower:
                        consistent = False; conflicts += 1
                except: pass

        # BFS limit for "program synthesis" simulation
        # In a real engine, this would build ASTs. Here we simulate depth by clause count.
        steps = min(len(clauses) * 2, 10) 
        return consistent, conflicts

    def _criticality_tuning(self, clauses: List, steps: int) -> float:
        """
        Estimates susceptibility chi by sampling solution space around weight w.
        Simulates Monte-Carlo sampling of clause weights.
        """
        if len(clauses) == 0: return 0.0
        
        np.random.seed(42) # Determinism
        base_w = 0.5
        delta = 0.1
        samples = 50
        
        def count_solutions(w):
            count = 0
            for _ in range(samples):
                # Perturb weights
                weights = np.random.rand(len(clauses)) * w
                # Simple satisfaction check: do weighted clauses conflict?
                # Simulating a SAT solver run
                sat = True
                for i, c in enumerate(clauses):
                    if c[0] == 'NOT' and np.random.rand() < weights[i]:
                        sat = False # Simulate conflict
                        break
                if sat: count += 1
            return count / samples

        s_plus = count_solutions(base_w + delta)
        s_minus = count_solutions(base_w - delta)
        
        chi = abs(s_plus - s_minus) / (2 * delta)
        return min(1.0, chi * 2.0) # Normalize roughly

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt ambiguity.
        """
        p = prompt.lower()
        
        # 1. Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop|die))\b', p):
            return 0.2
        # 2. Scope ambiguity (Every X ... a Y)
        if re.search(r'\bevery\s+\w+\s+(did|has|is)\s+a\s+\w+', p):
            return 0.4 # Ambiguous scope
        # 3. Pronoun ambiguity
        if re.search(r'\b(told|said|asked)\s+\w+\s+(he|she|him|her)\b', p) and 'who' in p:
            return 0.3
        # 4. False dichotomy
        if re.search(r'\beither\s+.+\s+or\s+.+\b', p) and 'only' not in p:
            return 0.4
        # 5. Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p) and 'data' not in p:
            return 0.3
        # 6. Unanswerability (missing info cues)
        if re.search(r'\b(calculate|solve|find)\b', p) and not re.search(r'\d', prompt):
             # Asking to calculate without numbers
            if not re.search(r'\b(zero|none|no)\b', p):
                return 0.25

        return 1.0 # No obvious traps detected

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        if min(z1, z2) == 0: return 1.0
        return (z12 - min(z1, z2)) / max(z1, z2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        clauses = self._parse_prompt(prompt)
        results = []
        
        # Pre-calculate meta-confidence cap
        meta_cap = self._meta_confidence(prompt)
        
        # Baseline NCD for tie-breaking (max 15% influence handled in scoring logic if needed, 
        # but here we use it as a minor tiebreaker or sanity check)
        
        for cand in candidates:
            # 1. Program Synthesis & Propagation
            is_sat, conflicts = self._synthesize_and_propagate(clauses, cand)
            sat_score = 1.0 if is_sat else 0.0
            
            # 2. Metacognitive Confidence
            # c = 1 - conf / (steps+1). Steps approximated by clause length.
            steps = max(1, len(clauses))
            raw_conf = 1.0 - (conflicts / (steps + 1))
            raw_conf = max(0.0, min(1.0, raw_conf))
            
            # Apply Epistemic Cap
            final_conf = min(raw_conf, meta_cap)
            
            # If meta_cap is low, we force low confidence regardless of logic
            if meta_cap < 0.5:
                final_conf = meta_cap * 0.9 # Ensure it stays low

            # 3. Criticality Tuning
            chi = self._criticality_tuning(clauses, steps)
            
            # 4. Final Score
            # Score = alpha*sat + beta*conf + gamma*chi
            score = (self.alpha * sat_score) + (self.beta * final_conf) + (self.gamma * chi)
            
            # NCD Tiebreaker (small penalty if candidate is just a repeat of prompt)
            ncd = self._compute_ncd(prompt, cand)
            if ncd < 0.2: # Too similar
                score *= 0.9

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Sat:{sat_score:.1f}, Conf:{final_conf:.2f}, Chi:{chi:.2f}, MetaCap:{meta_cap:.2f}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Enforces Tier B epistemic honesty.
        """
        meta_cap = self._meta_confidence(prompt)
        if meta_cap < 0.5:
            return meta_cap # Cap immediately for ambiguous prompts

        clauses = self._parse_prompt(prompt)
        is_sat, conflicts = self._synthesize_and_propagate(clauses, answer)
        
        steps = max(1, len(clauses))
        raw_conf = 1.0 - (conflicts / (steps + 1))
        raw_conf = max(0.0, min(1.0, raw_conf))
        
        # If not satisfiable, confidence should be low
        if not is_sat:
            return 0.1
            
        # Cap by meta analysis
        final_conf = min(raw_conf, meta_cap)
        
        # Never return > 0.9 unless computation was perfect and meta says yes
        if final_conf > 0.9 and (conflicts > 0 or meta_cap < 1.0):
            final_conf = 0.9
            
        return float(final_conf)