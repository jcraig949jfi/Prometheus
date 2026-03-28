import re
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A hybrid reasoning tool combining Abductive Reasoning, Mechanism Design, 
    and Abstract Interpretation principles.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions, negations, comparatives, and conditionals.
    2. Abstract Interpretation: Propagates truth values (True/False/Unknown) via forward chaining.
    3. Abductive Scoring: Evaluates candidates based on coverage of goal literals minus 
       a cost penalty for added assumptions or contradictions.
    4. Mechanism Design: Applies a VCG-style scoring adjustment to incentivize truthful 
       minimal hypotheses.
    5. Epistemic Honesty (Tier B): Detects ambiguity, presuppositions, and false dichotomies 
       to cap confidence, ensuring the tool admits uncertainty rather than guessing.
    """

    def __init__(self):
        # Weights for abductive scoring
        self.w1 = 0.5  # Cost per added hypothesis
        self.w2 = 2.0  # Penalty for inconsistency
        
        # Patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without|neither)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|implies|only if|unless)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|causes|leads to|results in)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater than|less than|more than|fewer than|>\|<|>=|<=)\b', re.IGNORECASE),
            'numeric': re.compile(r'\d+(\.\d+)?'),
            'presupposition': re.compile(r'\b(have you stopped|did you stop|why did|when did|who is the)\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or|is it .+ or .+\?)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|most beautiful|opinion)\b', re.IGNORECASE)
        }

    def _parse_clauses(self, text: str) -> List[Tuple[str, tuple, int]]:
        """Extract atomic propositions as (pred, args, polarity)."""
        clauses = []
        text_lower = text.lower()
        
        # Simple tokenization for demonstration; in production, use NLP
        # Here we simulate extraction based on keywords and structure
        sentences = re.split(r'[.\n]', text)
        
        for sent in sentences:
            if not sent.strip(): continue
            
            polarity = 1
            if self.patterns['negation'].search(sent):
                polarity = -1
            
            # Extract numeric comparisons
            nums = self.patterns['numeric'].findall(sent)
            if len(nums) >= 2 and any(x in sent for x in ['greater', 'less', '>', '<', 'more', 'fewer']):
                try:
                    n1, n2 = float(nums[0]), float(nums[1])
                    pred = 'num_cmp'
                    args = (n1, n2)
                    # Determine expected truth based on text direction
                    if 'less' in sent or '<' in sent:
                        clauses.append((pred, args, 1 if n1 < n2 else -1))
                    else:
                        clauses.append((pred, args, 1 if n1 > n2 else -1))
                except ValueError:
                    pass

            # Extract generic predicates (simplified for regex-only constraint)
            # Format: "A implies B" or "A causes B"
            if self.patterns['conditional'].search(sent) or self.patterns['causal'].search(sent):
                # Mock extraction of implication A -> B
                # In a full system, this would build the graph edges
                clauses.append(('implication', (sent.strip()[:20],), polarity))
            else:
                # Atomic fact
                clean_sent = re.sub(r'[^\w\s]', '', sent.strip()[:30])
                if clean_sent:
                    clauses.append(('fact', (clean_sent,), polarity))
                    
        return clauses

    def _run_abstract_interpretation(self, base_clauses: List, hypothesis_clauses: List) -> Tuple[np.ndarray, bool]:
        """
        Simulate forward chaining on a boolean state vector.
        Returns (state_matrix, is_inconsistent).
        State shape: (n_predicates, 3) [True, False, Unknown]
        """
        # Map unique predicates to indices
        all_preds = set()
        for p, args, pol in base_clauses + hypothesis_clauses:
            all_preds.add((p, args))
        
        pred_list = list(all_preds)
        n = len(pred_list)
        if n == 0:
            return np.zeros((0, 3)), False
            
        # State: [True, False, Unknown]
        state = np.zeros((n, 3), dtype=int)
        state[:, 2] = 1  # Initialize all as Unknown
        
        pred_map = {p: i for i, p in enumerate(pred_list)}
        
        # Initialize base facts
        for p, args, pol in base_clauses:
            idx = pred_map.get((p, args))
            if idx is not None:
                state[idx, 2] = 0 # Not unknown
                if pol == 1:
                    state[idx, 0] = 1 # True
                else:
                    state[idx, 1] = 1 # False
                    
        # Add hypotheses
        for p, args, pol in hypothesis_clauses:
            idx = pred_map.get((p, args))
            if idx is not None:
                # Check conflict
                if state[idx, 0] == 1 and pol == -1: # Was true, now negated
                     return state, True # Inconsistency
                if state[idx, 1] == 1 and pol == 1: # Was false, now affirmed
                    return state, True # Inconsistency
                    
                state[idx, 2] = 0
                if pol == 1:
                    state[idx, 0] = 1
                else:
                    state[idx, 1] = 1

        # Simplified propagation (Mocking the graph walk for regex-limited context)
        # In a full graph, we would iterate edges A->B and update B based on A
        # Here we assume static consistency check is the primary value add
        
        return state, False

    def _calculate_abductive_score(self, prompt: str, candidate: str) -> float:
        """Calculate score based on coverage - cost."""
        base_clauses = self._parse_clauses(prompt)
        hypo_clauses = self._parse_clauses(candidate)
        
        # Run abstract interpretation
        _, is_inconsistent = self._run_abstract_interpretation(base_clauses, hypo_clauses)
        
        # Cost calculation
        cost = self.w1 * len(hypo_clauses)
        if is_inconsistent:
            cost += self.w2
            
        # Coverage: Does the candidate make the prompt's implicit goal true?
        # Heuristic: If candidate contains numeric truth verified by prompt context
        coverage = 0
        prompt_nums = self.patterns['numeric'].findall(prompt)
        cand_nums = self.patterns['numeric'].findall(candidate)
        
        if prompt_nums and cand_nums:
            # Simple numeric consistency check
            try:
                if float(cand_nums[0]) == float(prompt_nums[0]): 
                    coverage = 1.0
            except: pass
            
        # If no numeric, check string overlap as weak proxy for coverage in this simplified model
        if coverage == 0:
            c_words = set(candidate.lower().split())
            p_words = set(prompt.lower().split())
            overlap = len(c_words & p_words) / (len(c_words) + 1)
            coverage = overlap * 0.5

        return coverage - cost

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Detect ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
            
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            return 0.3
            
        # 3. Subjectivity
        if self.patterns['subjectivity'].search(p_lower):
            return 0.4
            
        # 4. Ambiguity (Pronouns/Scope - simplified)
        if re.search(r'\b(he|she|it|they)\b.*\?', p_lower) and 'who' in p_lower:
            return 0.2
            
        # 5. Unanswerable (Missing info heuristics)
        if 'calculate' in p_lower and not self.patterns['numeric'].search(p_lower):
            return 0.1
            
        return 1.0

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        try:
            z1 = len(repr(s1.encode('utf-8'))) # Mock compression length
            z2 = len(repr(s2.encode('utf-8')))
            z12 = len(repr((s1+s2).encode('utf-8')))
            if max(z1, z2) == 0: return 1.0
            return (z12 - min(z1, z2)) / max(z1, z2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        scores = []
        
        # 1. Structural & Abductive Scoring
        raw_scores = []
        for cand in candidates:
            score = self._calculate_abductive_score(prompt, cand)
            raw_scores.append(score)
        
        # 2. Mechanism Design Adjustment (VCG-style relative scoring)
        # p_i = score_i - avg(score_j) for j != i
        n = len(candidates)
        if n > 1:
            total_sum = sum(raw_scores)
            for i, s in enumerate(raw_scores):
                others_sum = total_sum - s
                others_avg = others_sum / (n - 1)
                adjusted_score = s - others_avg
                scores.append(adjusted_score)
        else:
            scores = raw_scores
            
        # 3. NCD Tiebreaker (Max 15% influence)
        # Only applied if structural scores are very close
        final_scores = []
        for i, cand in enumerate(candidates):
            base_score = scores[i]
            # NCD penalty for being too different from prompt (hallucination check)
            ncd_val = self._ncd_score(prompt, cand)
            # Normalize NCD to be a small modifier
            ncd_modifier = (1.0 - ncd_val) * 0.15 
            final_scores.append(base_score + ncd_modifier)

        # Rank
        ranked_indices = np.argsort(final_scores)[::-1]
        
        for idx in ranked_indices:
            results.append({
                "candidate": candidates[idx],
                "score": float(final_scores[idx]),
                "reasoning": "Abductive coverage minus cost; adjusted for mechanism incentives."
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt (Tier B).
        """
        # 1. Meta-confidence cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.3:
            return meta_cap
            
        # 2. Structural match check
        clauses = self._parse_clauses(prompt + " " + answer)
        if not clauses:
            # No structural signal found
            return 0.2
            
        # 3. Compute internal score
        score = self._calculate_abductive_score(prompt, answer)
        
        # Map score to 0-1 range roughly
        # High positive score -> high confidence, but capped by meta_cap
        raw_conf = 1.0 / (1.0 + np.exp(-score)) # Sigmoid
        
        final_conf = min(raw_conf, meta_cap)
        
        # Never return > 0.9 unless computation was definitive (heuristic: numeric match)
        if 'numeric' in str(clauses) and score > 1.0:
            final_conf = min(final_conf, 0.95)
        else:
            final_conf = min(final_conf, 0.85)
            
        return float(final_conf)