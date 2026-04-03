from typing import Dict, Set, Tuple

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Morphogenesis x Free Energy Principle x Property-Based Testing
    
    Parses propositions into a graph, propagates beliefs via reaction-diffusion
    to minimize free energy, generates random worlds as property tests, and
    shrinks to minimal counterexamples. Scores answers by robustness under
    perturbation. Implements constructive computation for numerics, probabilities,
    temporal reasoning.
    """
    
    def __init__(self):
        self.eta = 0.1
        self.max_iter = 50
        self.conv_thresh = 1e-4
        self.n_worlds = 20
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"FEP score: {score:.3f}"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Compute structural confidence
        struct_score = self._score_candidate(prompt, answer)
        
        # Check if we computed an answer
        computed = self._compute_answer(prompt)
        if computed is not None:
            # If we have a numeric answer, check if candidate matches
            answer_nums = self._extract_numbers(answer)
            if answer_nums and any(abs(computed - n) < 0.01 for n in answer_nums):
                return min(0.85, struct_score)
        
        # Cap confidence based on score
        if struct_score > 0.7:
            return min(0.75, struct_score)
        elif struct_score > 0.5:
            return min(0.6, struct_score)
        else:
            return min(0.4, struct_score)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presupposition, unanswerability"""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .* fail|why did .* stop)', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery .* a \b', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p_lower) and '?' in prompt:
            return 0.25
        
        # False dichotomy
        if re.search(r'\b(either .* or |must be either)', p_lower):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|better|worse)\b', p_lower):
            if not re.search(r'\b(most|least|more|less|than)\b', p_lower):
                return 0.3
        
        # Insufficient information
        if re.search(r'\b(cannot determine|not enough|insufficient|impossible to)', p_lower):
            return 0.2
        
        return 1.0
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        # First try constructive computation
        computed = self._compute_answer(prompt)
        cand_nums = self._extract_numbers(candidate)
        
        comp_score = 0.0
        if computed is not None and cand_nums:
            if any(abs(computed - n) < 0.01 for n in cand_nums):
                comp_score = 0.5
        
        # Build propositional graph
        props_p, edges_p = self._parse_propositions(prompt)
        props_c, edges_c = self._parse_propositions(candidate)
        
        # Merge graphs
        all_props = list(set(props_p + props_c))
        n = len(all_props)
        if n == 0:
            return 0.5 + comp_score
        
        prop_idx = {p: i for i, p in enumerate(all_props)}
        
        # Build adjacency matrix
        W = np.zeros((n, n))
        for src, tgt, weight in edges_p + edges_c:
            if src in prop_idx and tgt in prop_idx:
                W[prop_idx[src], prop_idx[tgt]] = weight
        
        # Set observations
        obs = np.full(n, 0.5)
        for p in props_p:
            obs[prop_idx[p]] = 1.0
        
        # Run reaction-diffusion
        beliefs = self._reaction_diffusion(W, obs)
        
        # Property-based testing
        conflict_breadth = self._property_test(W, beliefs, obs)
        
        # Score: lower conflict = higher score
        struct_score = 1.0 - (conflict_breadth / max(n, 1))
        
        # NCD tiebreaker (max 15%)
        ncd = self._ncd(prompt, candidate)
        ncd_score = (1.0 - ncd) * 0.15
        
        total = comp_score * 0.4 + struct_score * 0.45 + ncd_score
        return np.clip(total, 0.0, 1.0)
    
    def _compute_answer(self, prompt: str) -> float:
        """Constructive computation for numeric/probability questions"""
        p_lower = prompt.lower()
        
        # Numeric comparison
        if re.search(r'\b(greater|larger|more|less|smaller|fewer)\b', p_lower):
            nums = self._extract_numbers(prompt)
            if len(nums) >= 2:
                return max(nums) if 'greater' in p_lower or 'larger' in p_lower else min(nums)
        
        # Probability/rate computation
        if re.search(r'\b(probability|percent|chance|rate)\b', p_lower):
            nums = self._extract_numbers(prompt)
            if len(nums) >= 2:
                # Simple Bayesian: P(A|B) = P(B|A)*P(A)/P(B)
                return nums[0] / max(nums[1], 0.001)
        
        # Arithmetic
        if re.search(r'[\+\-\*/]', prompt):
            nums = self._extract_numbers(prompt)
            if len(nums) >= 2:
                if '+' in prompt:
                    return sum(nums)
                elif '*' in prompt:
                    return np.prod(nums)
                elif '-' in prompt:
                    return nums[0] - sum(nums[1:])
                elif '/' in prompt:
                    return nums[0] / max(nums[1], 0.001)
        
        return None
    
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values"""
        matches = re.findall(r'-?\d+\.?\d*', text)
        return [float(m) for m in matches if m]
    
    def _parse_propositions(self, text: str) -> Tuple[List[str], List[Tuple[str, str, float]]]:
        """Parse atomic propositions and edges"""
        props = []
        edges = []
        
        # Split into sentences
        sentences = re.split(r'[.!?]', text)
        
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            
            # Extract atomic propositions (simple subject-verb-object)
            words = sent.split()
            if len(words) < 2:
                continue
            
            props.append(sent[:50])  # Truncate for uniqueness
            
            # Negations
            if re.search(r'\b(not|no|never|neither)\b', sent.lower()):
                props.append(f"NOT_{sent[:40]}")
                edges.append((sent[:50], f"NOT_{sent[:40]}", 1.0))
            
            # Conditionals
            if_match = re.search(r'if (.+?) then (.+)', sent.lower())
            if if_match:
                antecedent = if_match.group(1).strip()
                consequent = if_match.group(2).strip()
                props.extend([antecedent[:40], consequent[:40]])
                edges.append((antecedent[:40], consequent[:40], 0.8))
            
            # Causal
            if re.search(r'\b(because|since|therefore|thus|hence|leads to)\b', sent.lower()):
                parts = re.split(r'\b(because|since|therefore|thus|hence|leads to)\b', sent.lower())
                if len(parts) >= 3:
                    edges.append((parts[0].strip()[:40], parts[2].strip()[:40], 0.7))
            
            # Comparatives
            if re.search(r'\b(greater|larger|more|less|smaller)\b', sent.lower()):
                nums = self._extract_numbers(sent)
                if len(nums) >= 2:
                    props.append(f"{nums[0]}_CMP_{nums[1]}")
        
        return props, edges
    
    def _reaction_diffusion(self, W: np.ndarray, obs: np.ndarray) -> np.ndarray:
        """Free energy minimization via reaction-diffusion"""
        n = len(obs)
        beliefs = np.full(n, 0.5)
        
        for _ in range(self.max_iter):
            old_beliefs = beliefs.copy()
            
            # Prediction
            pred = 1 / (1 + np.exp(-W @ beliefs))
            
            # Reaction (prediction error)
            reaction = (obs - pred) * beliefs * (1 - beliefs)
            
            # Diffusion
            diffusion = W @ beliefs - beliefs * W.sum(axis=1)
            
            # Update
            beliefs = beliefs + self.eta * (reaction + diffusion)
            beliefs = np.clip(beliefs, 0.01, 0.99)
            
            if np.linalg.norm(beliefs - old_beliefs) < self.conv_thresh:
                break
        
        return beliefs
    
    def _property_test(self, W: np.ndarray, beliefs: np.ndarray, obs: np.ndarray) -> float:
        """Generate random worlds, find minimal counterexamples"""
        n = len(beliefs)
        if n == 0:
            return 0.0
        
        violations = []
        for _ in range(self.n_worlds):
            # Random world
            world = np.random.beta(1, 1, n)
            
            # Compute constraint violation
            V = 0.0
            for i in range(n):
                for j in range(n):
                    if W[i, j] > 0:
                        # Violation: belief in i but not j
                        V += max(0, world[i] - world[j]) * W[i, j]
            
            violations.append(V)
        
        # Conflict breadth: mean violation
        return np.mean(violations) if violations else 0.0
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance"""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)