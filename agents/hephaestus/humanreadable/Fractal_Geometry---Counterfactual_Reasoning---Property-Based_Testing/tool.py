from typing import Dict, Set, Tuple

"""
Fractal Counterfactual Property Scorer (FCPS)
Combines fractal-scale logical graphs, counterfactual perturbation, 
property-based testing, and dynamical trajectory analysis.
"""

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Set
from collections import defaultdict

class ReasoningTool:
    def __init__(self):
        self.rng = np.random.RandomState(42)
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Score candidates by fractal counterfactual dynamics."""
        results = []
        for cand in candidates:
            score, reasoning = self._score_candidate(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return calibrated confidence capped by meta-analysis."""
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        score, _ = self._score_candidate(prompt, answer)
        raw_conf = min(0.95, score)
        return min(raw_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity/unanswerability markers."""
        p = prompt.lower()
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))', p):
            return 0.2
        # Scope ambiguity
        if re.search(r'\bevery\b.+\ba\b', p) and '?' in p:
            return 0.25
        # Pronoun ambiguity
        if re.search(r'\b(he|she)\b', p) and re.search(r'\bwho\b', p):
            return 0.25
        # False dichotomy
        if re.search(r'\beither\b.+\bor\b', p) and not re.search(r'\bonly\b', p):
            return 0.3
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite)\b', p) and not re.search(r'\b(most|least|highest|lowest)\b', p):
            return 0.35
        return 0.95
    
    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Multi-component scoring."""
        # Parse structures
        p_clauses = self._parse_clauses(prompt)
        c_clauses = self._parse_clauses(candidate)
        
        # Dynamics score (40%)
        dyn_score = self._dynamics_score(p_clauses, c_clauses)
        
        # Structural score (30%)
        struct_score = self._structural_score(p_clauses, c_clauses)
        
        # Computational score (20%)
        comp_score = self._computational_score(prompt, candidate)
        
        # NCD tiebreaker (10%)
        ncd_score = 1.0 - self._ncd(prompt, candidate)
        
        total = 0.4*dyn_score + 0.3*struct_score + 0.2*comp_score + 0.1*ncd_score
        reasoning = f"dyn={dyn_score:.2f} struct={struct_score:.2f} comp={comp_score:.2f}"
        return total, reasoning
    
    def _parse_clauses(self, text: str) -> Dict:
        """Extract logical/numeric clauses with fractal depth."""
        clauses = {"nums": [], "comps": [], "negs": [], "conds": [], "depth": 0}
        
        # Numbers
        clauses["nums"] = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', text)]
        
        # Comparatives
        clauses["comps"] = re.findall(r'(greater|less|more|fewer|above|below|than|>', text.lower())
        
        # Negations
        clauses["negs"] = re.findall(r'\b(not|no|never|none)\b', text.lower())
        
        # Conditionals
        clauses["conds"] = re.findall(r'\b(if|then|when|because|causes?|leads? to)\b', text.lower())
        
        # Depth from nesting
        clauses["depth"] = text.count('(') + text.count('[')
        
        return clauses
    
    def _dynamics_score(self, p_clauses: Dict, c_clauses: Dict) -> float:
        """Trajectory stability via state evolution."""
        # Build state vector from prompt clauses
        p_state = self._build_state_vector(p_clauses)
        c_state = self._build_state_vector(c_clauses)
        
        # Generate counterfactual perturbations
        cf_states = self._generate_counterfactuals(c_state, k=5)
        
        # Measure convergence stability
        stability = self._compute_stability(p_state, c_state, cf_states)
        
        return stability
    
    def _build_state_vector(self, clauses: Dict) -> np.ndarray:
        """Convert clauses to 10D state vector."""
        vec = np.zeros(10)
        if clauses["nums"]:
            vec[0] = np.mean(clauses["nums"])
            vec[1] = np.std(clauses["nums"]) if len(clauses["nums"]) > 1 else 0
        vec[2] = len(clauses["comps"]) / 10.0
        vec[3] = len(clauses["negs"]) / 5.0
        vec[4] = len(clauses["conds"]) / 5.0
        vec[5] = clauses["depth"] * 0.1
        vec[6] = 0.5 ** clauses["depth"]  # Fractal scale
        vec[7:] = self.rng.randn(3) * 0.1  # Reservoir noise
        return np.clip(vec, -5, 5)
    
    def _generate_counterfactuals(self, state: np.ndarray, k: int) -> List[np.ndarray]:
        """Apply k perturbations to state vector."""
        cfs = []
        for i in range(k):
            cf = state.copy()
            # Perturb random dimensions
            idx = self.rng.choice(len(state), size=2, replace=False)
            cf[idx[0]] += self.rng.randn() * 0.5
            cf[idx[1]] *= -1 if self.rng.rand() < 0.3 else 1
            cfs.append(np.clip(cf, -5, 5))
        return cfs
    
    def _compute_stability(self, p_state: np.ndarray, c_state: np.ndarray, 
                          cf_states: List[np.ndarray]) -> float:
        """Lyapunov-style stability measure."""
        # Distance from prompt to candidate
        base_dist = np.linalg.norm(p_state - c_state)
        if base_dist > 3.0:
            return 0.1
        
        # Compute trajectory variance under perturbations
        cf_dists = [np.linalg.norm(p_state - cf) for cf in cf_states]
        cf_variance = np.var(cf_dists) if cf_dists else 1.0
        
        # Stability = low base distance, low perturbation variance
        stability = np.exp(-base_dist) * np.exp(-cf_variance)
        return min(1.0, stability * 2.0)
    
    def _structural_score(self, p_clauses: Dict, c_clauses: Dict) -> float:
        """Graph-based structural coherence."""
        score = 0.0
        
        # Numeric consistency
        if p_clauses["nums"] and c_clauses["nums"]:
            p_set = set(p_clauses["nums"])
            c_set = set(c_clauses["nums"])
            overlap = len(p_set & c_set) / max(len(p_set), len(c_set), 1)
            score += 0.3 * overlap
        
        # Comparative alignment
        if p_clauses["comps"]:
            comp_match = len([c for c in c_clauses["comps"] if c in p_clauses["comps"]])
            score += 0.3 * min(1.0, comp_match / len(p_clauses["comps"]))
        
        # Negation consistency
        p_neg = len(p_clauses["negs"])
        c_neg = len(c_clauses["negs"])
        if p_neg > 0 and c_neg > 0:
            score += 0.2
        elif p_neg == 0 and c_neg == 0:
            score += 0.2
        
        # Depth similarity (fractal scale)
        depth_diff = abs(p_clauses["depth"] - c_clauses["depth"])
        score += 0.2 * np.exp(-depth_diff * 0.5)
        
        return min(1.0, score)
    
    def _computational_score(self, prompt: str, candidate: str) -> float:
        """Solve numeric/logical problems."""
        score = 0.0
        
        # Numeric comparison
        p_nums = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', prompt)]
        c_nums = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', candidate)]
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Check if comparison is correct
            if '>' in prompt or 'greater' in prompt.lower():
                if p_nums[0] > p_nums[1] and 'yes' in candidate.lower():
                    score += 0.5
                elif p_nums[0] <= p_nums[1] and 'no' in candidate.lower():
                    score += 0.5
            if '<' in prompt or 'less' in prompt.lower():
                if p_nums[0] < p_nums[1] and 'yes' in candidate.lower():
                    score += 0.5
                elif p_nums[0] >= p_nums[1] and 'no' in candidate.lower():
                    score += 0.5
        
        # Negation logic
        if re.search(r'\bnot\b', prompt.lower()):
            if re.search(r'\b(no|false|incorrect)\b', candidate.lower()):
                score += 0.3
        
        # Conditional modus ponens
        if re.search(r'\bif\b.+\bthen\b', prompt.lower()):
            if re.search(r'\b(therefore|thus|so)\b', candidate.lower()):
                score += 0.2
        
        return min(1.0, score)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)