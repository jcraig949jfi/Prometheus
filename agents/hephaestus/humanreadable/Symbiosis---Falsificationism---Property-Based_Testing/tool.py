from typing import Dict, Set, Tuple

import re
import zlib
import random
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Symbiosis x Falsificationism x Property-Based Testing with Dynamics Tracking.
    
    Parses logical structure into typed predicates, generates property-based
    counter-examples via random sampling, scores via constraint overlap (symbiosis),
    and tracks state evolution dynamics for trajectory stability.
    """
    
    def __init__(self):
        self.alpha = 0.6  # overlap weight
        self.beta = 0.4   # counter-example penalty
        random.seed(42)
        np.random.seed(42)
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            conf = self.confidence(prompt, cand)
            reasoning = f"Symbiosis score: {score:.3f}, Confidence: {conf:.3f}"
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta = self._meta_confidence(prompt)
        structural = self._structural_confidence(prompt, answer)
        dynamic = self._dynamic_confidence(prompt, answer)
        return min(meta, 0.4 * structural + 0.6 * dynamic)
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        bg_clauses = self._parse_to_clauses(prompt)
        hyp_clauses = self._parse_to_clauses(candidate)
        
        # Structural component
        overlap = self._symbiosis_overlap(bg_clauses, hyp_clauses)
        
        # Falsification component
        counter_ex_size = self._find_minimal_counterexample(bg_clauses, hyp_clauses)
        
        # Computational component
        comp_score = self._computational_agreement(prompt, candidate)
        
        # NCD tiebreaker
        ncd = self._ncd(prompt, candidate)
        
        # Dynamics component
        dyn_score = self._trajectory_stability(prompt, candidate)
        
        # Weighted combination
        struct_score = self.alpha * overlap - self.beta * (counter_ex_size / 10.0)
        final = 0.3 * struct_score + 0.25 * comp_score + 0.35 * dyn_score + 0.1 * (1 - ncd)
        return max(0.0, min(1.0, final))
    
    def _parse_to_clauses(self, text: str) -> Dict[str, List[Tuple]]:
        clauses = {"negation": [], "comparative": [], "conditional": [], 
                   "causal": [], "numeric": [], "ordering": []}
        
        # Negation
        for m in re.finditer(r'\b(?:not|no|never|n\'t)\s+(\w+)', text, re.I):
            clauses["negation"].append(("not", m.group(1).lower()))
        
        # Comparative
        for m in re.finditer(r'(\w+)\s+(greater|less|more|fewer|larger|smaller)\s+than\s+(\w+)', text, re.I):
            clauses["comparative"].append((m.group(1).lower(), m.group(2).lower(), m.group(3).lower()))
        
        # Numeric comparisons
        for m in re.finditer(r'([\d.]+)\s*([<>=!]+)\s*([\d.]+)', text):
            clauses["numeric"].append((float(m.group(1)), m.group(2), float(m.group(3))))
        
        # Conditional
        for m in re.finditer(r'\b(?:if|when)\s+([^,]+?)\s+(?:then|,)\s*(.+?)(?:\.|$)', text, re.I):
            clauses["conditional"].append((m.group(1).strip().lower(), m.group(2).strip().lower()))
        
        # Causal
        for m in re.finditer(r'(\w+)\s+because\s+(.+?)(?:\.|$)', text, re.I):
            clauses["causal"].append((m.group(2).strip().lower(), m.group(1).strip().lower()))
        
        # Ordering
        for m in re.finditer(r'(\w+)\s+before\s+(\w+)', text, re.I):
            clauses["ordering"].append((m.group(1).lower(), "before", m.group(2).lower()))
        
        return clauses
    
    def _symbiosis_overlap(self, bg: Dict, hyp: Dict) -> float:
        bg_set = set()
        hyp_set = set()
        
        for key in bg:
            bg_set.update([str(x) for x in bg[key]])
        for key in hyp:
            hyp_set.update([str(x) for x in hyp[key]])
        
        if not bg_set and not hyp_set:
            return 0.5
        
        union = bg_set | hyp_set
        intersection = bg_set & hyp_set
        
        return len(intersection) / len(union) if union else 0.0
    
    def _find_minimal_counterexample(self, bg: Dict, hyp: Dict) -> int:
        # Generate random assignments and check for contradictions
        combined = {k: bg[k] + hyp[k] for k in bg}
        
        for _ in range(20):
            assignment = {f"var{i}": random.randint(1, 10) for i in range(5)}
            
            # Check numeric constraints
            for left, op, right in combined["numeric"]:
                if op == ">" and not (left > right):
                    return 3
                elif op == "<" and not (left < right):
                    return 3
                elif op == "=" and not (abs(left - right) < 0.01):
                    return 3
            
            # Check for negation contradictions
            neg_set = set([x[1] for x in combined["negation"]])
            pos_set = set()
            for clauses in combined.values():
                for clause in clauses:
                    if isinstance(clause, tuple) and len(clause) > 0:
                        pos_set.add(str(clause[-1]))
            
            if neg_set & pos_set:
                return 2
        
        return 0
    
    def _computational_agreement(self, prompt: str, candidate: str) -> float:
        # Numeric evaluation
        nums_prompt = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', prompt)]
        nums_cand = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', candidate)]
        
        if nums_prompt and nums_cand:
            # Check if candidate contains result of operation
            for i, n1 in enumerate(nums_prompt):
                for n2 in nums_prompt[i+1:]:
                    ops = [n1 + n2, n1 - n2, n1 * n2, n1 / n2 if n2 != 0 else 0]
                    for result in ops:
                        if any(abs(result - cn) < 0.01 for cn in nums_cand):
                            return 0.8
        
        # Check comparison correctness (9.11 vs 9.9)
        for m in re.finditer(r'([\d.]+)\s+(greater|less|larger|smaller)\s+than\s+([\d.]+)', prompt, re.I):
            n1, rel, n2 = float(m.group(1)), m.group(2).lower(), float(m.group(3))
            expected = (n1 > n2) if "great" in rel or "larg" in rel else (n1 < n2)
            
            if ("yes" in candidate.lower() or "true" in candidate.lower()) and expected:
                return 0.9
            elif ("no" in candidate.lower() or "false" in candidate.lower()) and not expected:
                return 0.9
        
        return 0.5
    
    def _trajectory_stability(self, prompt: str, candidate: str) -> float:
        """Dynamics tracking: model reasoning as state evolution."""
        sentences = re.split(r'[.!?]', prompt + " " + candidate)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # State vector: 8-dimensional embedding
        state = np.zeros(8)
        trajectories = [state.copy()]
        
        # Reservoir-style update
        for sent in sentences:
            clauses = self._parse_to_clauses(sent)
            
            # Update based on clause types
            update = np.zeros(8)
            update[0] = len(clauses["negation"]) * 0.3
            update[1] = len(clauses["comparative"]) * 0.4
            update[2] = len(clauses["conditional"]) * 0.5
            update[3] = len(clauses["causal"]) * 0.5
            update[4] = len(clauses["numeric"]) * 0.6
            update[5] = len(clauses["ordering"]) * 0.4
            update[6] = len(re.findall(r'\b\d+', sent)) * 0.2
            update[7] = len(sent.split()) * 0.05
            
            # Recurrent update with decay
            state = 0.7 * state + 0.3 * update
            trajectories.append(state.copy())
        
        # Analyze trajectory stability
        if len(trajectories) < 3:
            return 0.5
        
        traj_array = np.array(trajectories)
        
        # Convergence: variance in last 3 states
        final_variance = np.var(traj_array[-3:], axis=0).mean()
        convergence_score = 1.0 / (1.0 + final_variance)
        
        # Stability: difference between consecutive states
        diffs = np.diff(traj_array, axis=0)
        stability = 1.0 / (1.0 + np.linalg.norm(diffs, axis=1).mean())
        
        return 0.5 * convergence_score + 0.5 * stability
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presuppositions, unanswerability."""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .+ fail|when did .+ stop)', prompt_lower):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'\bevery \w+.*?\ba\b', prompt_lower):
            return 0.28
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she|they)\b', prompt_lower) and "who" in prompt_lower:
            return 0.26
        
        # False dichotomy
        if re.search(r'\beither .+ or .+\b', prompt_lower) and "?" in prompt:
            return 0.29
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prefer)\b', prompt_lower):
            return 0.3
        
        # Insufficient information
        if "not enough information" in prompt_lower or "cannot be determined" in prompt_lower:
            return 0.27
        
        return 1.0
    
    def _structural_confidence(self, prompt: str, answer: str) -> float:
        clauses_p = self._parse_to_clauses(prompt)
        clauses_a = self._parse_to_clauses(answer)
        
        total_clauses = sum(len(v) for v in clauses_p.values()) + sum(len(v) for v in clauses_a.values())
        
        if total_clauses == 0:
            return 0.25
        elif total_clauses > 5:
            return 0.75
        else:
            return 0.5
    
    def _dynamic_confidence(self, prompt: str, answer: str) -> float:
        return min(0.85, self._trajectory_stability(prompt, answer))
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2))