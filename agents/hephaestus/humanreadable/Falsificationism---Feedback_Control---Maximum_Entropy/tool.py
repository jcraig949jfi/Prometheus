import numpy as np
import zlib
import re
from typing import List, Dict, Any

class ReasoningTool:
    """
    Falsification-Entropy Feedback Controller (FEFC) Implementation.
    
    Mechanism:
    1. MaxEnt Prior: Candidates are initialized with uniform probability (maximum entropy).
    2. Falsification Module: Computes an error signal 'e' based on logical consistency.
       - Parses prompt for negations, comparatives, and numeric constraints.
       - Checks candidates against these hard constraints.
       - e = 1.0 if candidate contradicts prompt (Falsified), 0.0 if consistent.
    3. Feedback Control (PID-like): 
       - Adjusts the 'precision' (inverse temperature) of the belief distribution.
       - High error (falsification) -> High precision (sharp peak on survivors).
       - Low error (ambiguous) -> Low precision (broad distribution).
    4. Scoring: Returns the posterior probability adjusted by the control signal.
    """

    def __init__(self):
        self._state = {
            "integral": 0.0,
            "prev_error": 0.0,
            "precision": 1.0  # Inverse temperature
        }

    def _extract_constraints(self, text: str) -> dict:
        """Structural parsing to extract logical constraints."""
        constraints = {
            "negations": [],
            "comparatives": [],
            "numbers": [],
            "must_contain": [],
            "must_not_contain": []
        }
        text_lower = text.lower()
        
        # Detect negations
        if re.search(r'\b(not|no|never|neither|without)\b', text_lower):
            constraints["negations"] = re.findall(r'not\s+(\w+)|no\s+(\w+)', text_lower)
            
        # Detect numbers for comparison logic
        nums = re.findall(r'-?\d+\.?\d*', text_lower)
        if nums:
            constraints["numbers"] = [float(n) for n in nums]
            
        # Detect comparatives
        if any(w in text_lower for w in ["greater", "larger", "more", "higher"]):
            constraints["comparatives"].append("max")
        if any(w in text_lower for w in ["less", "smaller", "fewer", "lower"]):
            constraints["comparatives"].append("min")
            
        # Simple subject-object extraction for "X is Y" patterns
        matches = re.findall(r'(\w+)\s+is\s+(?:not\s+)?(\w+)', text_lower)
        for subj, obj in matches:
            if "not" in text_lower[text_lower.find(subj):text_lower.find(subj)+20]:
                constraints["must_not_contain"].append(obj)
            else:
                constraints["must_contain"].append(obj)

        return constraints

    def _compute_falsification_error(self, prompt: str, candidate: str) -> float:
        """
        Computes error signal e = 1 - P(data | H0).
        If candidate contradicts prompt constraints, e approaches 1.
        If consistent, e approaches 0.
        """
        constraints = self._extract_constraints(prompt)
        cand_lower = candidate.lower()
        error = 0.0
        checks = 0

        # Check numeric constraints
        cand_nums = re.findall(r'-?\d+\.?\d*', cand_lower)
        if constraints["numbers"] and cand_nums:
            try:
                c_val = float(cand_nums[0])
                p_vals = constraints["numbers"]
                
                if "max" in constraints["comparatives"]:
                    # Expect candidate to be the max or indicate the max
                    if not any(str(p) in candidate for p in p_vals if p == c_val):
                         # Heuristic: if prompt asks for max, and candidate isn't the max number found
                         # This is a simplification for the demo
                        pass 
                # Hard falsification: Explicit contradiction
                if "min" in constraints["comparatives"]:
                     if len(p_vals) >= 2 and c_val != min(p_vals):
                         # If prompt asks for min, and candidate is a number but not the min
                         # Only apply if candidate looks like an answer choice containing a number
                         if len(cand_lower.split()) < 5: # Short answer likely just the number
                             error = max(error, 0.9)
            except ValueError:
                pass

        # Check explicit must_not_contain
        for forbidden in constraints["must_not_contain"]:
            if forbidden in cand_lower and len(forbidden) > 2:
                error = max(error, 1.0) # Hard falsification
                checks += 1
        
        # Check explicit must_contain (if prompt implies specific fact)
        # Using NCD as a soft semantic check for "relevance" if no hard falsification found
        if error == 0.0:
            try:
                # Normalize Compression Distance for semantic similarity
                def ncd(a, b):
                    a_b = zlib.compress(a.encode())
                    b_b = zlib.compress(b.encode())
                    ab_b = zlib.compress((a+b).encode())
                    return (len(ab_b) - min(len(a_b), len(b_b))) / max(len(a_b), len(b_b), 1)
                
                # If candidate is completely unrelated (high NCD), increase error slightly
                dist = ncd(prompt, candidate)
                if dist > 0.8: # Arbitrary threshold for "unrelated"
                    error = 0.5 
            except:
                pass

        return min(1.0, error)

    def _pid_step(self, error: float) -> float:
        """Adjusts precision based on error dynamics."""
        kp, ki, kd = 2.0, 0.5, 0.1
        
        # Proportional
        p_term = kp * error
        
        # Integral
        self._state["integral"] += error
        i_term = ki * self._state["integral"]
        
        # Derivative
        d_term = kd * (error - self._state["prev_error"])
        self._state["prev_error"] = error
        
        # Update precision (inverse temperature)
        # High error -> High precision (sharpen focus on survivors)
        # Low error -> Low precision (maintain entropy/explore)
        new_precision = 1.0 + p_term + i_term + d_term
        self._state["precision"] = max(0.1, min(10.0, new_precision)) # Clamp
        
        return self._state["precision"]

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []
            
        # 1. Compute Falsification Errors for all candidates
        errors = [self._compute_falsification_error(prompt, c) for c in candidates]
        
        # 2. Update Controller State (using mean error as global signal)
        avg_error = np.mean(errors) if errors else 0.0
        precision = self._pid_step(avg_error)
        
        # 3. Compute MaxEnt-derived scores
        # Score ~ exp(-precision * error)
        # If error is 1 (falsified), score -> 0
        # If error is 0 (survives), score -> 1 (scaled by precision)
        raw_scores = []
        for e in errors:
            if e >= 1.0:
                raw_scores.append(0.0)
            else:
                # Boltzmann distribution style
                score = np.exp(-precision * e)
                raw_scores.append(score)
        
        # Normalize to [0, 1]
        max_s = max(raw_scores) if raw_scores else 1.0
        if max_s == 0: max_s = 1.0 # Prevent division by zero
        
        normalized_scores = [s / max_s for s in raw_scores]
        
        # 4. Rank and Format
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": float(normalized_scores[i]),
                "reasoning": f"Falsification error: {errors[i]:.2f}, Precision: {precision:.2f}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Reuse evaluate logic for single candidate
        res = self.evaluate(prompt, [answer])
        if res:
            return res[0]["score"]
        return 0.0