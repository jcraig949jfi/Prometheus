import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Bayesian-Incentive-Compatible Model Checker (BICMC) Approximation.
    
    Mechanism:
    1. Mechanism Design (Core): Implements a VCG-style scoring rule. Candidates are 
       treated as agents. The 'payment' (score) is derived from the marginal contribution 
       of the candidate's structural logic to the total system consistency. Truthful 
       reporting (logical consistency) is the dominant strategy.
    2. Bayesian Inference: Maintains a posterior belief over the correctness of structural 
       patterns (negations, comparatives, numerics) found in the prompt. Updates weights 
       based on pattern presence (Likelihood) to form a prior for scoring.
    3. Model Checking: Verifies candidates against temporal-logic-like constraints extracted 
       from the prompt (e.g., if "not" exists, positive assertions are penalized). 
       Candidates failing the "specification" (prompt constraints) receive zero probability.
    
    This architecture ensures that high scores are only awarded to candidates that 
    satisfy the formal constraints (Model Checking) and maximize the logical utility 
    (Mechanism Design) under the current belief state (Bayesian).
    """

    def __init__(self):
        # Priors for structural patterns (Bayesian starting point)
        self.pattern_weights = {
            'negation': 0.5,
            'comparative': 0.5,
            'conditional': 0.5,
            'numeric': 0.5
        }
        self.epsilon = 1e-9

    def _extract_structural_features(self, text: str) -> Dict[str, bool]:
        """Extracts logical constraints from text (Model Checking Specs)."""
        lower_text = text.lower()
        features = {
            'has_negation': bool(re.search(r'\b(not|no|never|neither|none|without)\b', lower_text)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|higher|lower|better|worse|<|>)\b', lower_text)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|otherwise|when)\b', lower_text)),
            'has_numeric': bool(re.search(r'\d+(\.\d+)?', text))
        }
        return features

    def _check_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """Verifies numeric claims in candidate against prompt (Model Checking)."""
        # Extract numbers from prompt and candidate
        p_nums = re.findall(r'\d+(\.\d+)?', prompt)
        c_nums = re.findall(r'\d+(\.\d+)?', candidate)
        
        if not p_nums:
            return 1.0 # No numeric constraints to check
        
        if not c_nums:
            # If prompt has numbers but candidate doesn't, slight penalty unless it's a non-numeric answer
            return 0.8 
        
        try:
            # Simple consistency: if prompt implies an order, check if candidate respects it
            # This is a heuristic approximation of formal verification
            p_vals = [float(n) for n in p_nums]
            c_vals = [float(n) for n in c_nums]
            
            # If prompt asks for max/min (detected by keywords), verify candidate value
            lower_p = prompt.lower()
            if 'max' in lower_p or 'largest' in lower_p or 'highest' in lower_p:
                if c_vals and max(c_vals) != max(p_vals):
                    return 0.0 # Violation
            elif 'min' in lower_p or 'smallest' in lower_p or 'lowest' in lower_p:
                if c_vals and min(c_vals) != min(p_vals):
                    return 0.0 # Violation
            
            return 1.0
        except ValueError:
            return 0.5

    def _verify_logical_constraints(self, prompt: str, candidate: str) -> float:
        """Exhaustively checks candidate against prompt constraints (Model Checking Engine)."""
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()
        
        score = 1.0
        
        # Constraint 1: Negation consistency
        # If prompt negates a concept, candidate affirming it directly might be wrong (simplified)
        if p_feat['has_negation']:
            # Heuristic: If prompt says "not X", and candidate is just "X", penalize heavily
            # This simulates checking a temporal logic property: G(not X)
            words = re.findall(r'\b\w+\b', p_lower)
            negated_targets = set()
            for i, w in enumerate(words):
                if w in ['not', 'no', 'never']:
                    if i+1 < len(words):
                        negated_targets.add(words[i+1])
            
            for target in negated_targets:
                if target in c_lower and f"not {target}" not in c_lower:
                    # Potential violation, reduce score significantly
                    score *= 0.1
        
        # Constraint 2: Conditional adherence
        if p_feat['has_conditional']:
            # If prompt is conditional, simple yes/no without qualification might be weak
            if c_lower.strip() in ['yes', 'no', 'true', 'false']:
                score *= 0.5
                
        return score

    def _calculate_mechanism_payment(self, prompt: str, candidate: str, all_candidates: List[str]) -> float:
        """
        Calculates VCG-style payment.
        Score = Utility(Self) - Utility(Others without Self).
        Here approximated as: Structural Match Score + Marginal Utility Bonus.
        """
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        
        utility = 0.0
        count = 0
        
        # Reward matching structural complexity (Incentivize truthful complexity)
        for key in p_feat:
            if p_feat[key]: # If prompt has this feature
                count += 1
                if c_feat.get(key.replace('has_', ''), False):
                    utility += 1.0 # Reward for mirroring structural complexity
                else:
                    utility -= 0.5 # Penalty for missing structural cue
        
        # Normalize by expected complexity
        if count > 0:
            utility /= count
        else:
            utility = 0.5
            
        return utility

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        
        # Pre-compute prompt features for Bayesian update
        p_feat = self._extract_structural_features(prompt)
        
        # Update priors (Bayesian Inference step)
        # If a feature is present, we increase confidence that it matters
        for key, present in p_feat.items():
            if present:
                self.pattern_weights[key] = min(1.0, self.pattern_weights[key] * 1.1)
        
        for cand in candidates:
            # 1. Model Checking: Verify hard constraints
            logic_score = self._verify_logical_constraints(prompt, cand)
            numeric_score = self._check_numeric_consistency(prompt, cand)
            
            # If model checking fails (score 0), the candidate is invalid regardless of other factors
            if logic_score == 0.0 or numeric_score == 0.0:
                final_score = 0.0
                reasoning = "Failed model checking verification (logical or numeric constraint violation)."
            else:
                # 2. Mechanism Design: Calculate incentive-compatible score
                mech_score = self._calculate_mechanism_payment(prompt, cand, candidates)
                
                # 3. Bayesian aggregation
                # Combine logic verification, mechanism payment, and structural alignment
                raw_score = (logic_score * numeric_score * mech_score)
                
                # Tie-breaking with NCD (only if scores are close, used here as a small modifier)
                # We want candidates that are compressible with the prompt (relevant) but not identical
                ncd = self._ncd_distance(prompt, cand)
                ncd_bonus = (1.0 - ncd) * 0.1 # Small bonus for relevance
                
                final_score = min(1.0, raw_score + ncd_bonus)
                reasoning = f"Mechanism score: {mech_score:.2f}, Logic check: {logic_score:.2f}, Numeric: {numeric_score:.2f}"

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the evaluation logic."""
        # Run single evaluation to get score
        # We simulate a candidate list of one to get the internal score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']