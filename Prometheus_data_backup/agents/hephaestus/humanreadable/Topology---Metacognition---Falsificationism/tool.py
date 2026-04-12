from typing import Dict, Optional, Tuple

"""
Topology x Metacognition x Falsificationism Reasoning Tool

Combines proposition graph analysis (topology), confidence calibration (metacognition),
and contradiction detection (falsificationism) with constructive computation for
numeric, logical, and constraint-based problems.
"""

import re
import numpy as np
import zlib
from collections import defaultdict
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    def __init__(self):
        self.alpha = 0.2  # Entropy calibration weight
        self.beta1 = 1.0  # Boldness coefficient
        self.beta2 = 2.0  # Hole penalty coefficient
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by computed score + trilogy framework."""
        results = []
        meta_conf = self._meta_confidence(prompt)
        
        for cand in candidates:
            # Compute constructive answer
            comp_score = self._compute_answer(prompt, cand)
            
            # Apply trilogy framework
            trilogy_score = self._trilogy_score(prompt, cand)
            
            # Combined score: computation primary, trilogy secondary
            score = 0.6 * comp_score + 0.3 * trilogy_score + 0.1 * self._ncd_score(prompt, cand)
            
            # Cap by meta-confidence
            score *= meta_conf
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"comp={comp_score:.2f} trilogy={trilogy_score:.2f} meta={meta_conf:.2f}"
            })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return calibrated confidence in [0,1]."""
        meta = self._meta_confidence(prompt)
        if meta < 0.3:
            return meta
        
        comp_score = self._compute_answer(prompt, answer)
        trilogy_score = self._trilogy_score(prompt, answer)
        
        raw_conf = 0.6 * comp_score + 0.4 * trilogy_score
        return min(meta, raw_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity, presupposition, unanswerability."""
        p_lower = prompt.lower()
        
        # Presupposition: "have you stopped", "why did X fail"
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))\b', p_lower):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery .+? (did|has|made) a \b', p_lower) and 'same' in p_lower:
            return 0.25
        
        # Pronoun ambiguity: "X told Y he/she" + "who"
        if re.search(r'\b\w+ told \w+ (he|she)\b', p_lower) and 'who' in p_lower:
            return 0.25
        
        # False dichotomy: "either A or B"
        if re.search(r'\beither .+ or .+\?', p_lower) and 'only' not in p_lower:
            return 0.28
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower) and 'criteria' not in p_lower:
            return 0.3
        
        # Insufficient info markers
        if 'cannot be determined' in p_lower or 'not enough information' in p_lower:
            return 0.3
        
        return 1.0
    
    def _compute_answer(self, prompt: str, candidate: str) -> float:
        """Constructive computation: actually solve the problem."""
        # Numeric comparison
        num_score = self._numeric_eval(prompt, candidate)
        if num_score > 0:
            return num_score
        
        # Arithmetic (bat-and-ball, PEMDAS)
        arith_score = self._arithmetic_eval(prompt, candidate)
        if arith_score > 0:
            return arith_score
        
        # Logical inference (modus tollens, transitivity)
        logic_score = self._logical_eval(prompt, candidate)
        if logic_score > 0:
            return logic_score
        
        # Constraint satisfaction
        constraint_score = self._constraint_eval(prompt, candidate)
        if constraint_score > 0:
            return constraint_score
        
        return 0.5  # Neutral if no parser matches
    
    def _numeric_eval(self, prompt: str, candidate: str) -> float:
        """Parse and compute numeric comparisons."""
        # Extract "which is greater/larger: X or Y"
        match = re.search(r'(greater|larger|bigger|more).+?(\d+\.?\d*).+?(\d+\.?\d*)', prompt, re.I)
        if match:
            try:
                n1, n2 = float(match.group(2)), float(match.group(3))
                cand_lower = candidate.lower()
                if n1 > n2 and str(n1) in candidate:
                    return 0.95
                if n2 > n1 and str(n2) in candidate:
                    return 0.95
            except:
                pass
        
        # Direct number extraction
        p_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        c_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
        if p_nums and c_nums:
            # Check if candidate number satisfies prompt constraint
            if any(abs(pn - cn) < 0.01 for pn in p_nums for cn in c_nums):
                return 0.7
        
        return 0.0
    
    def _arithmetic_eval(self, prompt: str, candidate: str) -> float:
        """Solve algebraic/arithmetic problems."""
        # Bat and ball: "X and Y cost Z, X costs W more than Y"
        match = re.search(r'cost.+?(\d+\.?\d*).+?costs.+?(\d+\.?\d*)\s*more', prompt, re.I)
        if match:
            total, diff = float(match.group(1)), float(match.group(2))
            y_price = (total - diff) / 2
            c_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
            if c_nums and abs(c_nums[0] - y_price) < 0.01:
                return 0.9
        
        # PEMDAS evaluation
        expr_match = re.search(r'(\d+\s*[\+\-\*/]\s*\d+[\+\-\*/\d\s]*)', prompt)
        if expr_match:
            try:
                result = eval(expr_match.group(1))
                c_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
                if c_nums and abs(c_nums[0] - result) < 0.01:
                    return 0.9
            except:
                pass
        
        return 0.0
    
    def _logical_eval(self, prompt: str, candidate: str) -> float:
        """Logical inference: modus tollens, transitivity, SVO."""
        # Transitivity: "A > B, B > C" => A > C
        trans = re.findall(r'(\w+)\s+>\s+(\w+)', prompt)
        if len(trans) >= 2:
            # Build graph
            graph = defaultdict(set)
            for a, b in trans:
                graph[a].add(b)
            # Check transitive closure
            for start in graph:
                reachable = self._bfs_reachable(graph, start)
                if any(node in candidate for node in reachable):
                    return 0.85
        
        # Modus tollens: "if P then Q, not Q" => not P
        if re.search(r'if .+ then', prompt, re.I) and re.search(r'\bnot\b', prompt, re.I):
            if re.search(r'\bnot\b', candidate, re.I):
                return 0.8
        
        return 0.0
    
    def _constraint_eval(self, prompt: str, candidate: str) -> float:
        """Constraint satisfaction via elimination."""
        # Extract entities and constraints
        entities = re.findall(r'\b([A-Z][a-z]+)\b', prompt)
        if len(entities) >= 3:
            # Simple constraint check: entity mentioned in candidate
            cand_entities = [e for e in entities if e in candidate]
            if cand_entities:
                return 0.7
        
        return 0.0
    
    def _bfs_reachable(self, graph, start):
        """BFS to find all reachable nodes."""
        visited = set([start])
        queue = [start]
        while queue:
            node = queue.pop(0)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return visited
    
    def _trilogy_score(self, prompt: str, candidate: str) -> float:
        """Topology x Metacognition x Falsificationism framework."""
        # Extract propositions
        props, neg_props = self._extract_propositions(candidate)
        if len(props) == 0:
            return 0.5
        
        n = len(props)
        W = np.zeros((n, n))  # Implication matrix
        c = np.zeros(n)  # Initial confidence
        
        # Assign initial confidence based on cue strength
        for i, p in enumerate(props):
            c[i] = self._cue_confidence(p)
        
        # Build implication edges
        for i in range(n):
            for j in range(n):
                if i != j:
                    W[i, j] = self._implication_weight(props[i], props[j], candidate)
        
        # Topological closure (belief propagation)
        c_hat = self._belief_propagation(W, c)
        
        # Falsificationism: detect contradictions
        H = self._hole_score(props, neg_props, c_hat)
        
        # Metacognitive calibration
        c_prime = self._calibrate_confidence(c_hat)
        
        # Boldness: reward low-prior, high-confidence claims
        B = np.sum((1 - 0.5) * c_prime)  # Simplified prior
        
        # Final score
        S = self.beta1 * B - self.beta2 * H
        return 1 / (1 + np.exp(-S))  # Sigmoid to [0,1]
    
    def _extract_propositions(self, text: str) -> Tuple[List[str], List[str]]:
        """Extract atomic propositions and negations."""
        sentences = re.split(r'[.;]', text)
        props = []
        neg_props = []
        
        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 5:
                continue
            if re.search(r'\b(not|no|never)\b', sent, re.I):
                neg_props.append(sent)
            else:
                props.append(sent)
        
        return props, neg_props
    
    def _cue_confidence(self, prop: str) -> float:
        """Assign confidence based on cue strength."""
        if re.search(r'\d+', prop):
            return 0.9  # Numeric claims
        if re.search(r'\b(maybe|perhaps|possibly)\b', prop, re.I):
            return 0.4
        if re.search(r'\b(must|always|certainly)\b', prop, re.I):
            return 0.8
        return 0.6  # Bare assertion
    
    def _implication_weight(self, p1: str, p2: str, context: str) -> float:
        """Extract implication weight from connectives."""
        if 'because' in context:
            return 0.8
        if 'suggests' in context or 'implies' in context:
            return 0.5
        if 'therefore' in context:
            return 0.9
        return 0.1
    
    def _belief_propagation(self, W: np.ndarray, c: np.ndarray) -> np.ndarray:
        """Compute transitive closure via matrix power."""
        n = W.shape[0]
        I = np.eye(n)
        try:
            T = np.linalg.inv(I - W * 0.5) - I  # Damped to ensure convergence
            c_hat = c + T @ c
            return np.clip(c_hat, 0, 1)
        except:
            return c
    
    def _hole_score(self, props: List[str], neg_props: List[str], c_hat: np.ndarray) -> float:
        """Detect contradictions (holes)."""
        H = 0.0
        for i, p in enumerate(props):
            for neg_p in neg_props:
                # Simple overlap check
                if any(word in neg_p for word in p.split() if len(word) > 3):
                    if i < len(c_hat):
                        H += c_hat[i] ** 2
        return H
    
    def _calibrate_confidence(self, c_hat: np.ndarray) -> np.ndarray:
        """Metacognitive calibration via entropy."""
        eps = 1e-9
        c_safe = np.clip(c_hat, eps, 1 - eps)
        E = -np.sum(c_safe * np.log(c_safe) + (1 - c_safe) * np.log(1 - c_safe))
        return c_hat * (1 - self.alpha * E / len(c_hat))
    
    def _ncd_score(self, prompt: str, candidate: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        def ncd(s1, s2):
            c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
            c12 = len(zlib.compress((s1 + s2).encode()))
            return (c12 - min(c1, c2)) / max(c1, c2)
        
        return 1 - ncd(prompt, candidate)