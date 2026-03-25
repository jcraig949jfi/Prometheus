import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamic Falsification Engine (TFE) Approximation.
    
    Mechanism:
    1. MaxEnt Prior: Initializes candidate weights uniformly (maximum entropy state).
    2. Thermodynamic Cost (EPR): Computes a cost function for each candidate based on:
       - KL-Divergence analog: Semantic mismatch between prompt constraints and candidate.
       - Landauer Cost: Penalty for logical inconsistencies (negation failures, constraint violations).
    3. Falsification: Candidates exceeding a dynamic entropy threshold are discarded (scored 0).
    4. Refinement: Survivors are ranked by minimal entropy production (lowest cost = highest score).
    
    This implements the 'physics-grounded criterion' by treating logical errors as thermodynamic 
    inefficiencies that increase the system's entropy production rate.
    """

    def __init__(self):
        self.threshold_base = 0.5

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a proxy for distributional divergence."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denom

    def _extract_constraints(self, text: str) -> List[Tuple[str, bool]]:
        """Parses text for logical constraints (negations, comparatives)."""
        constraints = []
        text_lower = text.lower()
        
        # Detect negations
        if "not " in text_lower or "never " in text_lower or "no " in text_lower:
            constraints.append(("negation_present", True))
        
        # Detect comparatives
        if "greater" in text_lower or "larger" in text_lower or ">" in text:
            constraints.append(("compare_gt", True))
        if "less" in text_lower or "smaller" in text_lower or "<" in text:
            constraints.append(("compare_lt", True))
            
        # Detect conditionals
        if "if " in text_lower or "unless " in text_lower:
            constraints.append(("conditional", True))
            
        return constraints if constraints else [("none", True)]

    def _calculate_entropy_production(self, prompt: str, candidate: str) -> float:
        """
        Calculates the Entropy Production Rate (EPR) analog.
        High EPR = High Cost = Likely False.
        Low EPR = Low Cost = Likely True.
        """
        # 1. KL-Divergence Analog: Semantic/Structural mismatch
        # We use NCD between prompt+candidate and prompt alone to measure 'surprise'
        # A valid answer should compress well with the prompt context if consistent.
        kl_div = self._compute_ncd(prompt, candidate)
        
        # 2. Landauer Cost: Logical Erasure Penalty
        # Penalty for violating detected constraints in the prompt
        landauer_cost = 0.0
        p_constraints = self._extract_constraints(prompt)
        c_constraints = self._extract_constraints(candidate)
        
        # Check for contradiction in negation logic
        p_has_neg = any(c[0] == "negation_present" for c in p_constraints)
        c_has_neg = any(c[0] == "negation_present" for c in c_constraints)
        
        # Heuristic: If prompt implies a specific direction and candidate opposes without cause
        # We simulate this by checking string overlap of key logical operators
        if ("not" in prompt.lower()) and ("not" not in candidate.lower()) and (len(candidate.split()) < 5):
            # Short answers ignoring negation might be erasing information
            landauer_cost += 0.2
            
        # 3. Numeric Consistency (Simple check)
        # If prompt has numbers and candidate has numbers, check order consistency roughly
        # This is a lightweight proxy for 'thermodynamic work' done to reconcile values
        try:
            p_nums = [float(w) for w in prompt.split() if w.replace('.','').replace('-','').isdigit()]
            c_nums = [float(w) for w in candidate.split() if w.replace('.','').replace('-','').isdigit()]
            if p_nums and c_nums:
                # If prompt says "greater" but candidate number is smaller than prompt ref
                if "greater" in prompt.lower() and c_nums[0] < p_nums[0]:
                    landauer_cost += 0.5
                if "less" in prompt.lower() and c_nums[0] > p_nums[0]:
                    landauer_cost += 0.5
        except ValueError:
            pass

        # Total EPR = KL + Beta * Landauer (Beta set to 1.0 for balance)
        epr = kl_div + landauer_cost
        return epr

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        epr_scores = []
        
        # Phase 1: Calculate EPR for all candidates
        for cand in candidates:
            epr = self._calculate_entropy_production(prompt, cand)
            epr_scores.append((cand, epr))
        
        # Phase 2: Falsification (Pruning)
        # Determine dynamic threshold based on median EPR + variance margin
        if epr_scores:
            vals = [s[1] for s in epr_scores]
            median_epr = sorted(vals)[len(vals)//2]
            # Falsify anything significantly more costly than the median
            threshold = median_epr * 1.5 + 0.1 
        else:
            threshold = 1.0
            
        scored_candidates = []
        for cand, epr in epr_scores:
            if epr > threshold:
                # Falsified: High entropy production, unsustainable hypothesis
                score = 0.0
                reason = f"Falsified: High thermodynamic cost (EPR={epr:.2f} > {threshold:.2f})."
            else:
                # Survived: Convert cost to score (inverse relationship)
                # Lower EPR -> Higher Score
                score = max(0.0, 1.0 - epr)
                reason = f"Survived: Low entropy production (EPR={epr:.2f}). Consistent with constraints."
            
            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
            
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on inverse EPR."""
        epr = self._calculate_entropy_production(prompt, answer)
        # Map EPR to 0-1 confidence. 
        # EPR ~0 -> Confidence 1.0. EPR > 1.0 -> Confidence ~0.0
        conf = 1.0 / (1.0 + math.exp(epr * 2 - 1)) # Sigmoid scaling
        return max(0.0, min(1.0, conf))