from typing import Dict, Set, Tuple

import re
import numpy as np
from typing import List, Dict, Tuple, Set
from collections import defaultdict

class ReasoningTool:
    """
    Combines Measure Theory, Gene Regulatory Networks, and Free Energy Principle.
    
    Mechanism:
    1. Parse text into atomic propositions (nodes in factor graph)
    2. Build edges with logical constraints (negation, implication, causal, comparative)
    3. Update beliefs via GRN attractor dynamics: b_i^(t+1) = sigma(sum w_ij * b_j^(t) + theta_i)
    4. Score via free energy: F = KL(q||p) + E_q[-log p(text|z)]
    5. Meta-confidence checks for presuppositions, ambiguity, unanswerability
    """
    
    def __init__(self):
        self.max_iter = 50
        self.convergence_threshold = 1e-4
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._compute_free_energy_score(prompt, cand)
            reasoning = self._explain_score(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Compute structural confidence
        struct_conf = self._structural_confidence(prompt, answer)
        comp_conf = self._computational_confidence(prompt, answer)
        
        # Blend with meta-confidence as cap
        base_conf = 0.5 * struct_conf + 0.5 * comp_conf
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presuppositions, unanswerability."""
        p_lower = prompt.lower()
        
        # Presupposition patterns
        if re.search(r'\b(have you stopped|did you stop|when did.*stop|why did.*fail)', p_lower):
            return 0.2
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b.*\bwho\b', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p_lower) and 'only' not in p_lower:
            return 0.25
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower) and 'criterion' not in p_lower:
            return 0.3
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', p_lower):
            return 0.35
        
        # Unanswerability markers
        if re.search(r'\b(impossible to|cannot determine|insufficient|ambiguous)\b', p_lower):
            return 0.2
        
        return 0.95  # High meta-confidence if no issues detected
    
    def _parse_propositions(self, text: str) -> List[Tuple[str, str, Dict]]:
        """Extract atomic propositions with types and metadata."""
        props = []
        
        # Numeric comparisons
        for m in re.finditer(r'([\d.]+)\s*(>|<|>=|<=|=)\s*([\d.]+)', text):
            props.append((m.group(0), 'numeric', {'left': float(m.group(1)), 'op': m.group(2), 'right': float(m.group(3))}))
        
        # Negations
        for m in re.finditer(r'\b(not|no|never|none)\s+(\w+)', text):
            props.append((m.group(0), 'negation', {'target': m.group(2)}))
        
        # Comparatives
        for m in re.finditer(r'(\w+)\s+(more|less|greater|fewer)\s+than\s+(\w+)', text):
            props.append((m.group(0), 'comparative', {'subject': m.group(1), 'relation': m.group(2), 'object': m.group(3)}))
        
        # Conditionals
        for m in re.finditer(r'\bif\b(.+?)\bthen\b(.+?)(?:\.|$)', text, re.IGNORECASE):
            props.append((m.group(0), 'conditional', {'antecedent': m.group(1), 'consequent': m.group(2)}))
        
        # Causal
        for m in re.finditer(r'(\w+)\s+(because|leads to|causes|results in)\s+(\w+)', text):
            props.append((m.group(0), 'causal', {'cause': m.group(1), 'effect': m.group(3)}))
        
        return props
    
    def _build_factor_graph(self, prompt_props: List, cand_props: List) -> Tuple[np.ndarray, np.ndarray]:
        """Build adjacency matrix and prior beliefs."""
        n = len(prompt_props) + len(cand_props)
        if n == 0:
            return np.zeros((1, 1)), np.array([0.5])
        
        W = np.zeros((n, n))
        prior = np.ones(n) * 0.5
        
        # Build edges based on logical types
        for i, (_, ptype, meta) in enumerate(prompt_props + cand_props):
            if ptype == 'negation':
                for j in range(n):
                    if i != j:
                        W[i, j] = -0.5
            elif ptype == 'conditional':
                W[i, (i+1) % n] = 0.8
            elif ptype == 'causal':
                W[i, (i+1) % n] = 0.7
            elif ptype == 'comparative':
                W[i, (i+1) % n] = 0.6
        
        return W, prior
    
    def _grn_update(self, W: np.ndarray, prior: np.ndarray) -> np.ndarray:
        """GRN-style belief propagation with attractor dynamics."""
        n = len(prior)
        beliefs = prior.copy()
        
        for _ in range(self.max_iter):
            new_beliefs = 1 / (1 + np.exp(-(W @ beliefs + prior - 0.5)))
            if np.max(np.abs(new_beliefs - beliefs)) < self.convergence_threshold:
                break
            beliefs = new_beliefs
        
        return beliefs
    
    def _free_energy(self, q: np.ndarray, p: np.ndarray, likelihood: float) -> float:
        """Compute variational free energy."""
        eps = 1e-10
        kl = np.sum(q * np.log((q + eps) / (p + eps)))
        prediction_error = -np.log(likelihood + eps)
        return kl + prediction_error
    
    def _compute_free_energy_score(self, prompt: str, candidate: str) -> float:
        """Main scoring via free energy minimization."""
        # Computational engines
        comp_score = self._compute_answer(prompt, candidate)
        if comp_score > 0:
            return comp_score
        
        # Parse propositions
        p_props = self._parse_propositions(prompt)
        c_props = self._parse_propositions(candidate)
        
        # Build factor graph
        W, prior = self._build_factor_graph(p_props, c_props)
        
        # GRN update
        beliefs = self._grn_update(W, prior)
        
        # Likelihood from overlap
        likelihood = self._compute_likelihood(prompt, candidate)
        
        # Free energy (lower is better, so negate for score)
        fe = self._free_energy(beliefs, prior, likelihood)
        score = 1.0 / (1.0 + fe)
        
        # Add NCD tiebreaker (max 15%)
        ncd = self._ncd(prompt, candidate)
        final_score = 0.85 * score + 0.15 * (1 - ncd)
        
        return final_score
    
    def _compute_answer(self, prompt: str, candidate: str) -> float:
        """Execute computational engines for standard problem types."""
        # Numeric comparison
        num_score = self._numeric_computation(prompt, candidate)
        if num_score > 0:
            return num_score
        
        # Bat-and-ball algebra
        algebra_score = self._algebra_computation(prompt, candidate)
        if algebra_score > 0:
            return algebra_score
        
        # Logical inference
        logic_score = self._logic_computation(prompt, candidate)
        if logic_score > 0:
            return logic_score
        
        return 0.0
    
    def _numeric_computation(self, prompt: str, candidate: str) -> float:
        """Compute numeric comparisons."""
        nums = re.findall(r'\d+\.?\d*', prompt)
        if len(nums) < 2:
            return 0.0
        
        try:
            vals = [float(n) for n in nums[:2]]
            cand_nums = re.findall(r'\d+\.?\d*', candidate)
            if not cand_nums:
                return 0.0
            
            cand_val = float(cand_nums[0])
            
            # Check if candidate matches a computed result
            if 'sum' in prompt.lower() or 'total' in prompt.lower():
                if abs(cand_val - sum(vals)) < 0.01:
                    return 0.95
            elif 'difference' in prompt.lower() or 'subtract' in prompt.lower():
                if abs(cand_val - abs(vals[0] - vals[1])) < 0.01:
                    return 0.95
            elif 'product' in prompt.lower() or 'multiply' in prompt.lower():
                if abs(cand_val - (vals[0] * vals[1])) < 0.01:
                    return 0.95
            elif '>' in prompt or 'greater' in prompt.lower():
                return 0.9 if vals[0] > vals[1] and 'yes' in candidate.lower() else 0.1
            elif '<' in prompt or 'less' in prompt.lower():
                return 0.9 if vals[0] < vals[1] and 'yes' in candidate.lower() else 0.1
        except:
            pass
        
        return 0.0
    
    def _algebra_computation(self, prompt: str, candidate: str) -> float:
        """Solve bat-and-ball style problems."""
        if 'cost' in prompt.lower() and 'more' in prompt.lower():
            nums = re.findall(r'\d+\.?\d*', prompt)
            if len(nums) >= 2:
                try:
                    total = float(nums[0])
                    diff = float(nums[1])
                    cheaper = (total - diff) / 2
                    cand_nums = re.findall(r'\d+\.?\d*', candidate)
                    if cand_nums and abs(float(cand_nums[0]) - cheaper) < 0.01:
                        return 0.95
                except:
                    pass
        return 0.0
    
    def _logic_computation(self, prompt: str, candidate: str) -> float:
        """Modus ponens, tollens, transitivity."""
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Modus tollens
        if 'if' in p_lower and 'not' in p_lower:
            if re.search(r'if\s+(\w+).*then\s+(\w+)', p_lower) and re.search(r'not\s+\w+', p_lower):
                if 'not' in c_lower or 'no' in c_lower:
                    return 0.85
        
        # Transitivity
        if re.search(r'(\w+)\s+>\s+(\w+)', p_lower) and re.search(r'(\w+)\s+>\s+(\w+)', p_lower):
            trans = re.findall(r'(\w+)\s*>\s*(\w+)', p_lower)
            if len(trans) >= 2 and trans[0][1] == trans[1][0]:
                expected = f"{trans[0][0]} > {trans[1][1]}"
                if expected.lower() in c_lower:
                    return 0.9
        
        return 0.0
    
    def _compute_likelihood(self, prompt: str, candidate: str) -> float:
        """Compute overlap-based likelihood."""
        p_words = set(re.findall(r'\w+', prompt.lower()))
        c_words = set(re.findall(r'\w+', candidate.lower()))
        if not p_words:
            return 0.5
        overlap = len(p_words & c_words) / len(p_words)
        return overlap
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        import zlib
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        if max(c1, c2) == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max(c1, c2)
    
    def _structural_confidence(self, prompt: str, answer: str) -> float:
        """Confidence from structural parsing."""
        props = self._parse_propositions(prompt + " " + answer)
        if len(props) == 0:
            return 0.3
        return min(0.7 + 0.05 * len(props), 0.9)
    
    def _computational_confidence(self, prompt: str, answer: str) -> float:
        """Confidence from computational match."""
        score = self._compute_answer(prompt, answer)
        return score if score > 0 else 0.4
    
    def _explain_score(self, prompt: str, candidate: str) -> str:
        """Generate reasoning explanation."""
        comp_score = self._compute_answer(prompt, candidate)
        if comp_score > 0.8:
            return "Computational match"
        props = self._parse_propositions(prompt + " " + candidate)
        return f"Parsed {len(props)} propositions, GRN convergence"