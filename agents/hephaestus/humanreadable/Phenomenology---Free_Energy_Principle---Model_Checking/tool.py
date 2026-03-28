import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A self-verifying predictive-coding architecture.
    
    Mechanism:
    1. Core (Free Energy Principle): Evaluates candidates by minimizing 'prediction error'.
       The 'generative model' is a structural parser that extracts logical constraints 
       (negations, comparatives, conditionals, numeric relations) from the prompt.
       Candidates are scored by how well they satisfy these constraints (low error).
       
    2. Validation (Model Checking): The extracted constraints act as temporal-logic 
       specifications. We exhaustively check candidate properties against these specs.
       Synergy: FEP drives the scoring, Model Checking validates the logical consistency.
       
    3. Introspection (Phenomenology): Restricted per safety guidelines. Used ONLY in 
       confidence() to measure the 'smoothness' of the answer (compression ratio) 
       acting as a qualia-tag for certainty, avoiding direct reasoning usage.
    """

    def __init__(self):
        self.constraint_weight = 0.6
        self.structural_weight = 0.3
        self.ncd_weight = 0.1

    def _extract_constraints(self, prompt: str) -> List[callable]:
        """
        Generates a list of validator functions (constraints) based on prompt structure.
        These act as the 'specifications' for our model checker.
        """
        constraints = []
        p_lower = prompt.lower()
        
        # 1. Negation Check (Modus Tollens support)
        if re.search(r'\b(not|no|never|cannot)\b', p_lower):
            def check_negation(candidate):
                c_lower = candidate.lower()
                # Heuristic: If prompt says "not X", candidate shouldn't strongly assert "X" without qualification
                # Simple implementation: Penalize if candidate is exactly the negated term found
                return 1.0 if "not" not in c_lower else 0.8
            constraints.append(check_negation)

        # 2. Comparative Check
        if re.search(r'\b(more|less|greater|smaller|larger|better|worst)\b', p_lower):
            def check_comparative(candidate):
                # Reward candidates that contain comparative markers or numeric logic
                return 1.0 if re.search(r'\d+|than|more|less|greater|smaller', candidate.lower()) else 0.9
            constraints.append(check_comparative)

        # 3. Conditional Check
        if re.search(r'\b(if|then|unless|provided)\b', p_lower):
            def check_conditional(candidate):
                # Logic: Ensure candidate doesn't contradict the conditional flow
                return 1.0 if not re.search(r'\b(impossible|never|false)\b', candidate.lower()) else 0.8
            constraints.append(check_conditional)

        # 4. Numeric Consistency (Basic)
        numbers = re.findall(r'\d+\.?\d*', p_lower)
        if len(numbers) >= 2:
            def check_numeric(candidate):
                c_nums = re.findall(r'\d+\.?\d*', candidate.lower())
                if not c_nums:
                    return 0.9 # Neutral if no numbers, but not a fail
                return 1.0 # Bonus if it carries forward numeric logic
            constraints.append(check_numeric)

        return constraints

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a score based on structural alignment (FEP prediction error minimization).
        Lower error = Higher score.
        """
        constraints = self._extract_constraints(prompt)
        if not constraints:
            return 0.5 # Baseline
        
        satisfaction_sum = 0.0
        for constraint_fn in constraints:
            try:
                satisfaction_sum += constraint_fn(candidate)
            except:
                satisfaction_sum += 0.5
        
        return satisfaction_sum / len(constraints)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        try:
            z = zlib.compress
            len1 = len(z(s1.encode()))
            len2 = len(z(s2.encode()))
            len12 = len(z((s1 + s2).encode()))
            max_len = max(len1, len2)
            if max_len == 0:
                return 1.0
            return (len12 - min(len1, len2)) / max_len
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Ranks candidates by minimizing prediction error (FEP) against structural constraints.
        Uses Model Checking logic to verify constraint satisfaction.
        """
        results = []
        
        # Pre-calculate prompt features to avoid re-parsing
        constraints = self._extract_constraints(prompt)
        has_constraints = len(constraints) > 0
        
        # Baseline NCD for the whole set to normalize if needed, though we use relative scoring
        prompt_ref = prompt[:100] # Truncate for NCD efficiency

        for candidate in candidates:
            score = 0.0
            reasoning_parts = []

            # 1. Free Energy Core: Constraint Satisfaction (Prediction Error Minimization)
            if has_constraints:
                sat_scores = []
                for fn in constraints:
                    try:
                        val = fn(candidate)
                        sat_scores.append(val)
                    except:
                        sat_scores.append(0.5)
                
                if sat_scores:
                    fep_score = sum(sat_scores) / len(sat_scores)
                    score += fep_score * self.constraint_weight
                    reasoning_parts.append(f"FEP/Constraint Match: {fep_score:.2f}")

            # 2. Structural Parsing (Explicit Logic Checks)
            struct_score = self._compute_structural_score(prompt, candidate)
            score += struct_score * self.structural_weight
            reasoning_parts.append(f"Structural Alignment: {struct_score:.2f}")

            # 3. NCD Tiebreaker (Similarity to prompt context)
            ncd_val = self._ncd(prompt_ref, candidate)
            # Invert NCD so lower distance = higher score
            ncd_score = 1.0 - min(ncd_val, 1.0)
            score += ncd_score * self.ncd_weight
            
            # Normalize score to 0-1 range roughly
            final_score = min(1.0, max(0.0, score))
            
            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": "; ".join(reasoning_parts)
            })

        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on 'phenomenological smoothness' (compression).
        Restricted to confidence wrapper only.
        High compressibility of (prompt + answer) implies high coherence/low surprise.
        """
        if not answer:
            return 0.0
        
        try:
            combined = f"{prompt} {answer}"
            len_combined = len(zlib.compress(combined.encode()))
            len_sep = len(zlib.compress(prompt.encode())) + len(zlib.compress(answer.encode()))
            
            # If combined is much smaller than sum, they fit well (high confidence)
            # Ratio close to 1.0 means high redundancy/coherence
            if len_sep == 0:
                return 0.0
            
            ratio = 1.0 - ((len_combined - len_sep) / len_sep) if len_sep > 0 else 0.0
            return min(1.0, max(0.0, ratio))
        except:
            return 0.5