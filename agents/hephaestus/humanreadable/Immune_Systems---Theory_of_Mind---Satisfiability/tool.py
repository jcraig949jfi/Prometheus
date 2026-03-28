import re
import numpy as np
import zlib
from collections import defaultdict
from typing import List, Dict, Tuple, Optional, Set

class ReasoningTool:
    """
    A hybrid reasoning tool combining structural logic parsing, constructive computation,
    and immune-inspired mutation with Theory-of-Mind belief weighting.
    
    Mechanism:
    1. Structural Parsing: Extracts logical clauses (negations, conditionals, comparatives).
    2. Constructive Computation: Solves numeric/math expressions directly.
    3. SAT-based Conflict Detection: Uses a lightweight DPLL-like check to find contradictions.
    4. Immune Clonal Selection: Mutates answers slightly to test robustness; penalizes instability.
    5. ToM Belief Aggregation: Weights scores based on the distribution of mutant successes.
    6. Epistemic Honesty: Caps confidence if the prompt contains ambiguity traps.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|cannot|impossible)\b', re.I),
            'conditional': re.compile(r'\b(if|unless|only if|then)\b', re.I),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads to)\b', re.I),
            'quantifier': re.compile(r'\b(all|every|some|at least one|no)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|equal)\b', re.I),
            'numeric_cmp': re.compile(r'(\d+(?:\.\d+)?)\s*(<|>|=|==|!=|<=|>=)\s*(\d+(?:\.\d+)?)'),
            'presupposition': re.compile(r'\b(have you stopped|why did|why does|when did)\b', re.I),
            'false_dichotomy': re.compile(r'\b(either .+ or .+|only two options)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|beautiful|ugly)\b', re.I),
        }
        self.epsilon = 0.05  # Improvement threshold for clonal selection

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_clauses(self, text: str) -> List[str]:
        """Extract atomic logical propositions and relations."""
        clauses = []
        t_low = text.lower()
        
        # Simple extraction based on connectors
        segments = re.split(r'\s*(?:,|and|but|however|;)\s*', text)
        for seg in segments:
            if len(seg.strip()) > 3:
                clauses.append(seg.strip())
        return clauses

    def _check_numeric_truth(self, text: str) -> Optional[bool]:
        """Constructive computation for numeric comparisons."""
        matches = self.patterns['numeric_cmp'].findall(text)
        if not matches:
            return None
        
        for m in matches:
            try:
                a = float(m[0])
                op = m[1]
                b = float(m[2])
                if op == '<': res = a < b
                elif op == '>': res = a > b
                elif op == '=' or op == '==': res = a == b
                elif op == '!=': res = a != b
                elif op == '<=': res = a <= b
                elif op == '>=': res = a >= b
                else: res = False
                
                if not res:
                    return False # Found a false numeric statement
            except ValueError:
                continue
        return True if matches else None

    def _sat_check(self, prompt_clauses: List[str], answer_clauses: List[str]) -> Tuple[bool, int]:
        """
        Lightweight SAT check. 
        Returns (is_satisfiable, conflict_size).
        Since full DPLL is complex for regex-only, we simulate via contradiction detection.
        """
        p_text = " ".join(prompt_clauses).lower()
        a_text = " ".join(answer_clauses).lower()
        full_text = f"{p_text} {a_text}"
        
        conflicts = 0
        
        # Check direct negation contradictions
        for clause in answer_clauses:
            c_low = clause.lower()
            # If answer says "X is Y" and prompt says "X is not Y"
            if self.patterns['negation'].search(clause):
                # Remove negation word to find base proposition
                base = re.sub(self.patterns['negation'], '', c_low).strip()
                if base in p_text:
                    conflicts += 1
            else:
                # If answer says "X is Y" and prompt says "X is not Y"
                neg_base = "not " + c_low
                if neg_base in p_text or re.search(r'\bno\b\s+' + re.escape(c_low), p_text):
                    conflicts += 1

        # Numeric contradiction
        num_res = self._check_numeric_truth(full_text)
        if num_res is False:
            conflicts += 1
            
        is_sat = (conflicts == 0)
        return is_sat, conflicts

    def _generate_mutants(self, answer: str) -> List[str]:
        """Immune clonal selection: Generate variations of the answer."""
        mutants = [answer]
        a_low = answer.lower()
        
        # Mutation 1: Negation flip
        if "not " in a_low:
            mutants.append(answer.replace("not ", "", 1).replace("Not ", "", 1))
        elif " is " in a_low:
            mutants.append(answer.replace(" is ", " is not ", 1).replace(" Is ", " Is not ", 1))
            
        # Mutation 2: Quantifier shift (All -> Some)
        if "all " in a_low:
            mutants.append(re.sub(r'all ', 'some ', answer, flags=re.I))
        if "some " in a_low:
            mutants.append(re.sub(r'some ', 'all ', answer, flags=re.I))
            
        # Mutation 3: Synonym swap (Basic)
        swaps = {'yes': 'no', 'true': 'false', 'correct': 'incorrect'}
        for k, v in swaps.items():
            if k in a_low:
                mutants.append(re.sub(re.escape(k), v, answer, flags=re.I))
                
        return list(set(mutants))

    def _score_candidate(self, prompt: str, candidate: str) -> float:
        """Core scoring logic combining SAT, Computation, and Immune/ToM layers."""
        p_clauses = self._extract_clauses(prompt)
        a_clauses = self._extract_clauses(candidate)
        
        # 1. Structural & SAT Score (Base)
        is_sat, conflict_count = self._sat_check(p_clauses, a_clauses)
        base_score = 1.0 if is_sat else max(0.0, 1.0 - (conflict_count * 0.5))
        
        # 2. Constructive Computation Bonus/Penalty
        # If the candidate contains a numeric claim that is demonstrably false, penalize heavily
        num_truth = self._check_numeric_truth(candidate)
        if num_truth is False:
            base_score = 0.0
        elif num_truth is True:
            base_score = min(1.0, base_score + 0.2) # Bonus for correct math
            
        # 3. Immune Clonal Selection & ToM Belief Update
        # Generate mutants and see if they score better (exploration)
        mutants = self._generate_mutants(candidate)
        mutant_scores = []
        
        for mut in mutants:
            m_sat, m_conf = self._sat_check(p_clauses, self._extract_clauses(mut))
            m_num = self._check_numeric_truth(mut)
            
            s = 1.0 if m_sat else max(0.0, 1.0 - (m_conf * 0.5))
            if m_num is False: s = 0.0
            elif m_num is True: s = min(1.0, s + 0.2)
            mutant_scores.append(s)
        
        # ToM: Expectation over the belief distribution of mutants
        # If the original is stable (better than or equal to mutants), keep score.
        # If a mutant is significantly better, the original belief is weak.
        if mutant_scores:
            best_mutant = max(mutant_scores)
            if best_mutant > base_score + self.epsilon:
                # The answer is unstable; a small mutation makes it much better.
                # Penalize the original for being sub-optimal in its local neighborhood.
                base_score = best_mutant - self.epsilon 
            else:
                # Stable: Aggregate belief (weighted average)
                base_score = (base_score + sum(mutant_scores)/len(mutant_scores)) / 2.0

        return max(0.0, min(1.0, base_score))

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Detects ambiguity, presuppositions, and unanswerable structures.
        Returns a cap for confidence (0.0 to 1.0).
        """
        p_low = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_low):
            return 0.2
        
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_low):
            return 0.3
            
        # 3. Subjectivity without context
        if self.patterns['subjectivity'].search(p_low) and "context" not in p_low:
            return 0.4
            
        # 4. Pronoun/Scope Ambiguity (Heuristic: "he", "she", "it" with multiple subjects)
        # Simple check: if question asks "who" and prompt has multiple names
        if re.search(r'\bwho\b', p_low):
            names = re.findall(r'\b[A-Z][a-z]+\b', prompt)
            if len(set(names)) > 1:
                return 0.25

        # 5. Unanswerable / Missing Info
        if re.search(r'\b(calculate|solve|find)\b', p_low) and not re.search(r'\d', prompt):
            return 0.1

        return 1.0

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2: return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            len_s1 = len(zlib.compress(s1_b))
            len_s2 = len(zlib.compress(s2_b))
            len_comb = len(zlib.compress(s1_b + s2_b))
            min_len = min(len_s1, len_s2)
            if min_len == 0: return 1.0
            return (len_comb - min_len) / max(len_s1, len_s2) # Simplified NCD
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        # Pre-calculate NCD to prompt for tie-breaking
        ncd_scores = [(c, self._ncd_distance(prompt, c)) for c in candidates]
        ncd_map = {c: score for c, score in ncd_scores}
        
        for cand in candidates:
            # Primary Score: Structural + Logical + Immune/ToM
            raw_score = self._score_candidate(prompt, cand)
            
            # Apply Epistemic Cap (Tier B Honesty)
            # If the prompt is a trap, even a "matching" answer shouldn't get high confidence
            if meta_cap < 0.5:
                # If the prompt is ambiguous, we downgrade the score significantly
                # unless the answer explicitly addresses the ambiguity (hard to detect generically)
                # So we cap the score at the meta_confidence level roughly
                final_score = min(raw_score, meta_cap + (raw_score * 0.2)) 
            else:
                final_score = raw_score

            # NCD Tiebreaker (max 15% influence)
            # If scores are close, prefer lower NCD (more relevant/concise)
            # This is handled implicitly by sorting logic later, but we can add a tiny epsilon
            ncd_penalty = ncd_map[cand] * 0.05 
            final_score = max(0.0, min(1.0, final_score - ncd_penalty))

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural/SAT:{raw_score:.2f}, MetaCap:{meta_cap:.2f}, NCD:{ncd_map[cand]:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence to ensure epistemic honesty on traps.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Calculate raw structural/logical confidence
        p_clauses = self._extract_clauses(prompt)
        a_clauses = self._extract_clauses(answer)
        is_sat, conflicts = self._sat_check(p_clauses, a_clauses)
        
        raw_conf = 1.0 if is_sat else max(0.0, 1.0 - (conflicts * 0.4))
        
        # Numeric verification
        num_res = self._check_numeric_truth(answer)
        if num_res is False:
            raw_conf = 0.0
        elif num_res is True:
            raw_conf = min(1.0, raw_conf + 0.1)
            
        # If no structural signal found (raw_conf near 1.0 default but no checks passed),
        # and meta_cap is low, trust meta_cap.
        # If meta_cap is low (trap detected), force low confidence.
        if meta_cap < 0.3:
            return min(raw_conf, meta_cap)
        
        # General cap: Never return > 0.9 unless computation was definitive (numeric)
        if num_res is None: # No numeric computation done
            raw_conf = min(raw_conf, 0.85)
            
        return max(0.0, min(1.0, raw_conf))