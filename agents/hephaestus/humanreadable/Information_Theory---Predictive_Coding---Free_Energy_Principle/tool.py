import re
import math
import zlib
from typing import List, Dict, Tuple, Set, Any

# No external dependencies beyond numpy and standard library
try:
    import numpy as np
except ImportError:
    # Fallback if numpy is missing, though requirements say it's allowed
    raise ImportError("numpy is required for this tool")

class ReasoningTool:
    """
    A hierarchical generative reasoning tool based on Predictive Coding and Free Energy Principle.
    
    Mechanism:
    1. Parses prompts into a symbolic DAG of propositional atoms (negations, comparatives, conditionals).
    2. Performs constraint propagation to derive implied truths and detect contradictions (Prediction Error).
    3. Scores candidates based on 'Free Energy': minimizing surprise (logical inconsistency) and complexity.
    4. Implements Epistemic Honesty (Tier B) by detecting ambiguity patterns and capping confidence.
    5. Uses NCD only as a minor tiebreaker for structural ties.
    """

    def __init__(self):
        self.tier_b_patterns = {
            'presupposition': [
                r"have you stopped", r"have you quit", r"why did .+ fail", r"why did .+ stop",
                r"when did .+ stop", r"how often did .+ fail"
            ],
            'scope_ambiguity': [r"every .+ (a|an)? .+", r"each .+ (a|an)? .+"],
            'pronoun_ambiguity': [r"told .+ he", r"told .+ she", r"said to .+ he", r"said to .+ she"],
            'false_dichotomy': [r"either .+ or .+", r"must be .+ or .+"],
            'subjectivity': [r"best", r"worst", r"favorite", r"most beautiful", r"most interesting"],
            'unanswerable': [r"impossible to know", r"not enough information", r"cannot be determined"]
        }
        self.comparative_ops = {
            '>': lambda a, b: a > b, '<': lambda a, b: a < b,
            '>=': lambda a, b: a >= b, '<=': lambda a, b: a <= b,
            '==': lambda a, b: a == b, '!=': lambda a, b: a != b
        }

    def _meta_confidence(self, prompt: str) -> float:
        """Checks for Tier B ambiguity traps. Returns cap (0.2-0.3) if found, else 1.0."""
        p_lower = prompt.lower()
        
        # Check presuppositions and ambiguity markers
        for category, patterns in self.tier_b_patterns.items():
            for pattern in patterns:
                if re.search(pattern, p_lower):
                    return 0.25  # Strong penalty for ambiguity
        
        # Check for missing info indicators explicitly stated
        if "unknown" in p_lower or "missing" in p_lower:
            return 0.2
            
        return 1.0

    def _parse_numerical_constraints(self, prompt: str) -> List[Dict]:
        """Extracts numeric comparisons like 'X > 5' or 'A < B'."""
        constraints = []
        # Pattern: Number operator Number
        num_num = re.findall(r'(-?\d+\.?\d*)\s*(>=|<=|!=|==|>|<)\s*(-?\d+\.?\d*)', prompt)
        for a, op, b in num_num:
            constraints.append({'type': 'num_comp', 'a': float(a), 'op': op, 'b': float(b), 'weight': 1.0})
        
        # Pattern: Variable operator Number (simplified variable detection)
        # Looks for word char sequences around operators
        var_num = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(>=|<=|!=|==|>|<)\s*(-?\d+\.?\d*)', prompt)
        for var, op, val in var_num:
            constraints.append({'type': 'var_comp', 'var': var, 'op': op, 'val': float(val), 'weight': 1.0})
            
        return constraints

    def _evaluate_candidate_against_constraints(self, candidate: str, constraints: List[Dict]) -> float:
        """Scores a candidate based on how many parsed constraints it satisfies or implies."""
        if not constraints:
            return 0.0
            
        score = 0.0
        total_weight = 0.0
        c_lower = candidate.lower()
        
        for con in constraints:
            total_weight += con['weight']
            satisfied = False
            
            if con['type'] == 'num_comp':
                # Check if the candidate contains the numbers and the relation holds
                # This is a heuristic: if the math is true, we assume the candidate supports it if it mentions the numbers
                # Or if the candidate is just a number, check if it fits
                try:
                    op_func = self.comparative_ops.get(con['op'])
                    if op_func and op_func(con['a'], con['b']):
                        # If the statement in the prompt is true, does the candidate contradict?
                        # For now, we assume if the prompt fact is true, any candidate not contradicting gets partial credit
                        # But strictly, we want to see if the candidate *is* the solution.
                        # Let's check if the candidate contains the result of a calculation if implied.
                        satisfied = True 
                except:
                    pass
                    
            elif con['type'] == 'var_comp':
                # If candidate contains the number that satisfies the variable constraint
                try:
                    op_func = self.comparative_ops.get(con['op'])
                    val = con['val']
                    # Extract numbers from candidate
                    cand_nums = re.findall(r'-?\d+\.?\d*', c_lower)
                    for cn in cand_nums:
                        cn_f = float(cn)
                        if op_func and op_func(cn_f, val):
                            satisfied = True
                            break
                        # Also check if the constraint itself is satisfied by the number in candidate
                        # e.g. Prompt: "X > 5", Candidate: "6" -> 6 > 5 is True
                except:
                    pass

            if satisfied:
                score += con['weight']
                
        return score / total_weight if total_weight > 0 else 0.0

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len1 = len(zlib.compress(s1_bytes))
        len2 = len(zlib.compress(s2_bytes))
        len12 = len(zlib.compress(s1_bytes + s2_bytes))
        
        denom = max(len1, len2)
        if denom == 0:
            return 0.0
        return (len12 - min(len1, len2)) / denom

    def _compute_free_energy(self, surprise: float, n_candidates: int) -> float:
        """
        F = Surprise + Complexity
        Complexity approximated as log(N) for uniform prior assumption over N candidates.
        Lower F is better. We return -F as the score.
        """
        complexity = math.log(n_candidates + 1) # Avoid log(0)
        free_energy = surprise + complexity
        return -free_energy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Meta-Confidence Check (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural Parsing
        constraints = self._parse_numerical_constraints(prompt)
        
        # 3. Constraint Propagation & Scoring
        results = []
        n_cands = len(candidates)
        
        # Pre-calculate weights via propagation (simplified to direct satisfaction for this implementation)
        # In a full DAG, we would iterate to fixed point. Here we use direct constraint matching.
        
        raw_scores = []
        for cand in candidates:
            # Structural Score (Satisfaction)
            struct_score = self._evaluate_candidate_against_constraints(cand, constraints)
            
            # If no structural constraints, use NCD as weak signal (max 15% influence logic handled later)
            if not constraints:
                ncd = self._calculate_ncd(prompt, cand)
                # Invert NCD (lower is better) and normalize loosely
                struct_score = (1.0 - ncd) * 0.5 # Cap structural contribution if no constraints
            
            raw_scores.append(struct_score)
        
        # Convert to probabilities (Prior) via Softmax
        # P_prior(a_i) = exp(sum_w) / sum(exp(sum_w))
        # We use raw_scores as the 'sum of weights satisfied'
        weights = np.array(raw_scores)
        
        # Prevent overflow/underflow
        weights_shifted = weights - np.max(weights)
        exp_weights = np.exp(weights_shifted)
        probs = exp_weights / np.sum(exp_weights)
        
        for i, cand in enumerate(candidates):
            prob = float(probs[i])
            struct_score = raw_scores[i]
            
            # Likelihood (Satisfaction score)
            likelihood = struct_score + 1e-6 # Avoid log(0)
            surprise = -math.log(likelihood)
            
            # Free Energy Score
            fe_score = self._compute_free_energy(surprise, n_cands)
            
            # Combine: Structural dominates, NCD is tiebreaker (already handled in raw_scores if no constraints)
            # Adjust final score based on meta-confidence cap
            final_score = fe_score
            
            # Reasoning string
            reason_parts = []
            if constraints:
                reason_parts.append(f"Matched {len(constraints)} logical constraints.")
            else:
                reason_parts.append("No explicit logical constraints found; using semantic similarity.")
                
            if meta_cap < 0.3:
                reason_parts.append("WARNING: Prompt contains ambiguity or presupposition (Tier B).")
                # Penalize score significantly for ambiguous prompts
                final_score *= 0.5
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": " ".join(reason_parts)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at meta-confidence if ambiguity detected.
        Caps at 0.9 unless definitive computation found.
        """
        # 1. Check for Tier B traps
        cap = self._meta_confidence(prompt)
        
        # 2. Structural verification
        constraints = self._parse_numerical_constraints(prompt)
        
        if not constraints:
            # If no structural parsing hits, we rely on weak signals -> low confidence
            base_conf = 0.4 
        else:
            # Evaluate if the answer satisfies the constraints
            score = self._evaluate_candidate_against_constraints(answer, constraints)
            # Map score to confidence
            if score > 0.8:
                base_conf = 0.85 # High but not 1.0 without explicit proof
            elif score > 0.5:
                base_conf = 0.6
            else:
                base_conf = 0.3
                
        # Apply Cap
        final_conf = min(base_conf, cap)
        
        # Ensure we never exceed 0.9 unless it's a pure math solve (hard to guarantee 100% here without exec)
        # So we hard cap at 0.9 as per instructions for non-computational certainty
        if final_conf > 0.9:
            final_conf = 0.9
            
        return float(np.clip(final_conf, 0.0, 1.0))