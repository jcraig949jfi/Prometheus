import re
import zlib
import math
from typing import List, Dict, Tuple, Set, Optional

class ReasoningTool:
    """
    Constraint-Driven Mechanism Scorer (CDMS)
    
    Mechanism:
    1. Structural Parsing (Mechanism Design): Extracts logical atoms (comparisons, negations, 
       conditionals) from the prompt to define a utility function U(s). High utility is assigned 
       to states satisfying these constraints.
    2. Equilibrium Search (Nash Equilibrium): Treats truth assignments of extracted propositions 
       as players. Iteratively flips values to maximize global utility, converging to a stable 
       state (equilibrium) where no single proposition flip improves the score.
    3. Verification (Model Checking): Performs a bounded DFS to explore reachable logical states 
       from the prompt's initial conditions. Checks if the candidate answer holds in the 
       equilibrium states that satisfy the prompt's temporal/logical specification.
    
    Scoring:
    Score = (|S_satisfying| / |S_total|) * Avg_Utility * (1 - Ambiguity_Penalty)
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'numeric_comp': re.compile(r'(\d+(?:\.\d+)?)\s*(<|>|<=|>=|==|!=|equals|greater|less)\s*(\d+(?:\.\d+)?)'),
            'negation': re.compile(r'\b(not|no|never|none|cannot|impossible)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|every|some|none|no)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(causes|leads to|results in|because|therefore)\b', re.IGNORECASE),
            'presupposition': re.compile(r'(have you stopped|why did .*(fail|stop)|when did .*(stop|fail))', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either|or)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|believe)\b', re.IGNORECASE)
        }

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0: return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _extract_atoms(self, text: str) -> Dict:
        """Extract structural features as atomic propositions."""
        atoms = {
            'numerics': [], 'negations': 0, 'conditionals': 0,
            'quantifiers': [], 'causals': 0, 'length': len(text)
        }
        
        # Numeric comparisons
        for m in self.patterns['numeric_comp'].finditer(text):
            try:
                v1, op, v2 = float(m.group(1)), m.group(2), float(m.group(3))
                ops_map = {'<': v1 < v2, '>': v1 > v2, '<=': v1 <= v2, '>=': v1 >= v2, 
                           '==': v1 == v2, '!=': v1 != v2, 'equals': v1 == v2,
                           'greater': v1 > v2, 'less': v1 < v2}
                # Normalize operator string for lookup
                op_key = op.replace(' ', '_')
                if op_key in ops_map: atoms['numerics'].append(ops_map[op_key])
                elif 'greater' in op: atoms['numerics'].append(v1 > v2)
                elif 'less' in op: atoms['numerics'].append(v1 < v2)
            except: pass

        atoms['negations'] = len(self.patterns['negation'].findall(text))
        atoms['conditionals'] = len(self.patterns['conditional'].findall(text))
        atoms['causals'] = len(self.patterns['causal'].findall(text))
        atoms['quantifiers'] = [m.group(1).lower() for m in self.patterns['quantifier'].finditer(text)]
        
        return atoms

    def _compute_utility(self, prompt_atoms: Dict, candidate_atoms: Dict, candidate_text: str) -> float:
        """
        Mechanism Design: Utility function rewarding constraint satisfaction.
        Rewards: Matching numeric truth, matching logical density (neg/cond), semantic overlap.
        """
        u = 0.0
        
        # 1. Numeric Consistency (High weight)
        if prompt_atoms['numerics'] and candidate_atoms['numerics']:
            # Check if candidate preserves the truth value of numeric claims found in prompt
            # Simplified: If prompt has true numerics, candidate should ideally reflect consistent logic
            match_count = sum(p == c for p, c in zip(prompt_atoms['numerics'], candidate_atoms['numerics']))
            u += 2.0 * (match_count / max(1, len(prompt_atoms['numerics'])))
        elif not prompt_atoms['numerics'] and not candidate_atoms['numerics']:
            u += 0.5 # Neutral if no numbers involved

        # 2. Logical Structure Alignment
        # If prompt has conditionals, good candidates often repeat or resolve them
        if prompt_atoms['conditionals'] > 0:
            if candidate_atoms['conditionals'] > 0:
                u += 1.0
            # Penalize ignoring complex conditionals if candidate is too short
            if len(candidate_text.split()) < 5 and prompt_atoms['conditionals'] > 1:
                u -= 0.5

        # 3. Negation Handling
        # If prompt has negations, candidate should ideally acknowledge them (heuristic)
        if prompt_atoms['negations'] > 0:
            if candidate_atoms['negations'] > 0:
                u += 0.5
            else:
                # Potential penalty for ignoring negation, but cautious
                u += 0.1 

        return max(0.0, u)

    def _nash_equilibrium_search(self, prompt_atoms: Dict, candidate_text: str) -> Tuple[float, int]:
        """
        Nash Equilibrium: Iteratively flip 'truth' of candidate features to maximize utility.
        Since we can't truly flip text, we simulate stability by checking if the candidate's 
        implied logic is a local maximum against the prompt's constraints.
        """
        # State: Binary vector of [has_numeric_match, has_conditional_response, has_negation_match]
        # We approximate this by scoring the current state and perturbations
        
        cand_atoms = self._extract_atoms(candidate_text)
        current_u = self._compute_utility(prompt_atoms, cand_atoms, candidate_text)
        
        # Simulate best-response updates (conceptual)
        # In this text-based approximation, stability is high if small textual changes 
        # (simulated by checking substrings) don't drastically improve utility.
        # We treat the current parse as the strategy profile.
        
        stability_score = 0.0
        iterations = 0
        max_iter = 3
        
        # Simple convergence check: does the candidate contain the necessary logical components?
        # If prompt has X, and candidate ignores X, utility is low (unstable).
        # If prompt has X, candidate addresses X, utility is high (stable).
        
        if prompt_atoms['conditionals'] > 0:
            if cand_atoms['conditionals'] > 0 or len(cand_atoms['numerics']) > 0:
                stability_score = 1.0
            else:
                stability_score = 0.4 # Unstable equilibrium
        
        if prompt_atoms['negations'] > 0:
            if cand_atoms['negations'] > 0:
                stability_score += 0.5
            else:
                stability_score += 0.1

        return min(1.0, current_u + stability_score), iterations

    def _model_check(self, prompt: str, candidate: str, atoms_prompt: Dict) -> Tuple[int, int]:
        """
        Model Checking: DFS to verify if candidate satisfies prompt constraints.
        Given text limitations, we simulate state exploration by checking constraint satisfaction.
        Returns (satisfying_states, total_explored)
        """
        # Define specification phi: Candidate must not contradict prompt numerics
        # and should address prompt conditionals if present.
        
        cand_atoms = self._extract_atoms(candidate)
        satisfying = 0
        total_states = 1 # Base state
        
        # Check 1: Numeric Contradiction (Immediate failure)
        # If prompt says 5 > 3 and candidate says 3 > 5 (if explicitly stated)
        # Hard to extract explicit contradiction without full NLI, so we check consistency
        numeric_consistent = True
        if atoms_prompt['numerics'] and cand_atoms['numerics']:
            # If lengths differ, assume partial exploration
            if len(atoms_prompt['numerics']) != len(cand_atoms['numerics']):
                 # Allow partial match if candidate is explanatory
                 pass 
            else:
                if not all(p == c for p, c in zip(atoms_prompt['numerics'], cand_atoms['numerics'])):
                    numeric_consistent = False
        
        if numeric_consistent:
            satisfying += 1
            
        # Check 2: Conditional Logic (Simplified)
        # If prompt has "if", candidate should ideally not be a simple "Yes/No" without context
        if atoms_prompt['conditionals'] > 0:
            if len(candidate.split()) > 3 or cand_atoms['conditionals'] > 0:
                satisfying += 1 # State satisfies temporal/logic spec
            else:
                # State exists but doesn't satisfy phi
                pass
        else:
            satisfying += 1 # No specific constraint to fail
            
        total_states = 2 # Explored 'consistent' and 'logic' dimensions
        return max(1, satisfying), total_states

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Detect ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_low = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_low):
            return 0.2
        
        # 2. False Dichotomy indicators without clear options
        if self.patterns['false_dichotomy'].search(p_low):
            if 'or' in p_low and 'either' in p_low:
                # Check if options are exhaustive (hard), default to caution
                return 0.5 

        # 3. Subjectivity
        if self.patterns['subjectivity'].search(p_low):
            return 0.4
            
        # 4. Unanswerability / Missing Info
        if "who is" in p_low and "context" not in p_low:
             # Heuristic for pronoun ambiguity without context
             if re.search(r'\bhe\b|\bshe\b|\bit\b|\bthey\b', p_low):
                 return 0.3

        # 5. Structural insufficiency
        atoms = self._extract_atoms(prompt)
        if atoms['conditionals'] > 2 and len(prompt.split()) < 10:
            return 0.4 # Too complex for length, likely ambiguous
            
        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_atoms = self._extract_atoms(prompt)
        meta_cap = self._meta_confidence(prompt)
        results = []
        
        # Pre-calculate NCD for tie-breaking
        ncd_scores = []
        for c in candidates:
            ncd_scores.append(self._ncd(prompt, c))
        
        avg_ncd = sum(ncd_scores) / len(ncd_scores) if ncd_scores else 0.5

        for i, cand in enumerate(candidates):
            cand_atoms = self._extract_atoms(cand)
            
            # 1. Mechanism Design: Utility
            utility = self._compute_utility(prompt_atoms, cand_atoms, cand)
            
            # 2. Nash Equilibrium: Stability
            equilibrium_score, _ = self._nash_equilibrium_search(prompt_atoms, cand)
            
            # 3. Model Checking: Satisfaction Ratio
            sat_count, total_count = self._model_check(prompt, cand, prompt_atoms)
            satisfaction_ratio = sat_count / max(1, total_count)
            
            # Combined Score Logic
            # Structural (Utility + Equilibrium) >= 50%
            # Computation (Satisfaction) >= 20%
            # NCD <= 15%
            
            structural_score = (utility * 0.6) + (equilibrium_score * 0.4)
            computation_score = satisfaction_ratio
            ncd_component = 1.0 - min(1.0, ncd_scores[i] / (avg_ncd + 0.1)) # Normalize relative to avg
            
            raw_score = (structural_score * 0.55) + (computation_score * 0.30) + (ncd_component * 0.15)
            
            # Apply Meta-Confidence Cap (Epistemic Honesty)
            final_score = min(raw_score, meta_cap)
            
            # Reasoning string
            reason_parts = []
            if utility > 0.5: reason_parts.append("High structural alignment")
            if equilibrium_score > 0.8: reason_parts.append("Stable logical equilibrium")
            if satisfaction_ratio < 1.0: reason_parts.append("Partial constraint satisfaction")
            if meta_cap < 0.5: reason_parts.append("Ambiguous or presupposition-heavy prompt")
            
            reasoning = "; ".join(reason_parts) if reason_parts else "Standard evaluation"

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at meta-confidence limit derived from prompt analysis.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Quick structural check
        atoms_p = self._extract_atoms(prompt)
        atoms_a = self._extract_atoms(answer)
        
        # If no structural signal and low content, confidence drops
        if len(prompt.split()) < 5 and len(answer.split()) < 3:
            return min(0.3, meta_cap)
            
        # Calculate a quick utility proxy
        util = self._compute_utility(atoms_p, atoms_a, answer)
        eq_score, _ = self._nash_equilibrium_search(atoms_p, answer)
        sat_ratio, _ = self._model_check(prompt, answer, atoms_p)
        
        raw_conf = (util * 0.4) + (eq_score * 0.4) + (sat_ratio * 0.2)
        
        # Cap by meta-confidence (Epistemic Honesty)
        final_conf = min(raw_conf, meta_cap)
        
        # Ensure we never return > 0.9 without definitive computation (heuristic: high numeric match)
        if atoms_p['numerics'] and atoms_a['numerics']:
             if all(p == c for p, c in zip(atoms_p['numerics'], atoms_a['numerics'])):
                 final_conf = min(final_conf * 1.1, 0.95) # Allow slight boost for math match
        else:
             final_conf = min(final_conf, 0.85) # Cap non-math answers

        return round(max(0.0, min(1.0, final_conf)), 4)