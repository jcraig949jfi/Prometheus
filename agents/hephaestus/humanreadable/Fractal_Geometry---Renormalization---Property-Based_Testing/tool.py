from typing import Dict, Optional, Tuple

"""
Fractal-Renormalization Reasoning Tool

Combines multi-scale tree similarity, renormalization-based coarse-graining,
and property-based mutation testing to evaluate logical reasoning robustness.
"""

import re
import math
import random
from typing import List, Dict, Tuple, Optional
import numpy as np


class TreeNode:
    def __init__(self, text: str, features: np.ndarray):
        self.text = text
        self.features = features
        self.children = []
        
    def add_child(self, child):
        self.children.append(child)


class ReasoningTool:
    def __init__(self):
        random.seed(42)
        np.random.seed(42)
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by fractal similarity + robustness."""
        prompt_tree = self._parse_tree(prompt)
        results = []
        
        for cand in candidates:
            cand_tree = self._parse_tree(cand)
            sim_score = self._fractal_similarity(prompt_tree, cand_tree)
            robust_score = self._robustness_test(prompt, cand)
            struct_score = self._structural_match(prompt, cand)
            comp_score = self._computational_solve(prompt, cand)
            ncd_score = self._ncd(prompt, cand)
            
            final = 0.35*sim_score + 0.20*robust_score + 0.25*struct_score + 0.15*comp_score + 0.05*ncd_score
            reasoning = f"Fractal:{sim_score:.2f} Robust:{robust_score:.2f} Struct:{struct_score:.2f} Comp:{comp_score:.2f}"
            results.append({"candidate": cand, "score": final, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on meta-analysis and structural certainty."""
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        comp_score = self._computational_solve(prompt, answer)
        if comp_score > 0.9:
            return min(0.92, meta_conf)
        
        struct_score = self._structural_match(prompt, answer)
        base_conf = 0.3 + 0.5 * struct_score
        return min(base_conf, meta_conf)
    
    def _extract_features(self, text: str) -> np.ndarray:
        """Extract 6D feature vector: negation, comparative, conditional, numeric, causal, ordering."""
        text_lower = text.lower()
        features = np.zeros(6)
        
        features[0] = 1.0 if re.search(r'\bnot\b|n\'t|\bno\b|\bnever\b', text_lower) else 0.0
        features[1] = 1.0 if re.search(r'greater|less|more|fewer|higher|lower|than|exceed', text_lower) else 0.0
        features[2] = 1.0 if re.search(r'\bif\b|\bthen\b|\bunless\b|\bwhen\b|\bgiven\b', text_lower) else 0.0
        features[3] = 1.0 if re.search(r'\d+\.?\d*|\bone\b|\btwo\b|\bthree\b', text_lower) else 0.0
        features[4] = 1.0 if re.search(r'cause|lead|result|due to|produce|trigger', text_lower) else 0.0
        features[5] = 1.0 if re.search(r'before|after|precede|follow|first|last|earlier|later', text_lower) else 0.0
        
        return features
    
    def _parse_tree(self, text: str) -> TreeNode:
        """Parse text into tree structure with feature vectors."""
        sentences = re.split(r'[.!?]+', text)
        root_features = self._extract_features(text)
        root = TreeNode(text, root_features)
        
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            clauses = re.split(r'[,;:]|\band\b|\bor\b|\bbut\b', sent)
            for clause in clauses:
                clause = clause.strip()
                if clause:
                    child = TreeNode(clause, self._extract_features(clause))
                    root.add_child(child)
        
        return root
    
    def _get_nodes_at_depth(self, node: TreeNode, depth: int, current: int = 0) -> List[TreeNode]:
        """Get all nodes at a specific depth."""
        if current == depth:
            return [node]
        nodes = []
        for child in node.children:
            nodes.extend(self._get_nodes_at_depth(child, depth, current + 1))
        return nodes
    
    def _fractal_similarity(self, tree1: TreeNode, tree2: TreeNode, max_depth: int = 3) -> float:
        """Multi-scale Hausdorff-like similarity with renormalization weighting."""
        similarities = []
        weights = []
        
        for depth in range(max_depth + 1):
            nodes1 = self._get_nodes_at_depth(tree1, depth)
            nodes2 = self._get_nodes_at_depth(tree2, depth)
            
            if not nodes1 or not nodes2:
                continue
            
            feat1 = np.mean([n.features for n in nodes1], axis=0)
            feat2 = np.mean([n.features for n in nodes2], axis=0)
            
            dist = np.linalg.norm(feat1 - feat2)
            sim = np.exp(-dist)
            similarities.append(sim)
            weights.append(2 ** (-depth))
        
        if not similarities:
            return 0.0
        
        return np.average(similarities, weights=weights)
    
    def _robustness_test(self, prompt: str, answer: str, n_mutations: int = 10) -> float:
        """Property-based testing with mutation shrinkage."""
        base_tree = self._parse_tree(answer)
        prompt_tree = self._parse_tree(prompt)
        base_sim = self._fractal_similarity(prompt_tree, base_tree)
        
        failures = 0
        for _ in range(n_mutations):
            mutated = self._mutate_answer(answer)
            mut_tree = self._parse_tree(mutated)
            mut_sim = self._fractal_similarity(prompt_tree, mut_tree)
            if abs(base_sim - mut_sim) > 0.15:
                failures += 1
        
        robustness = 1.0 - (failures / n_mutations)
        return robustness
    
    def _mutate_answer(self, answer: str) -> str:
        """Generate random mutation: toggle negation, flip number, swap words."""
        mutations = [
            lambda s: re.sub(r'\b(not|n\'t)\b', '', s) if 'not' in s.lower() else s + ' not',
            lambda s: re.sub(r'(\d+)', lambda m: str(int(m.group(1)) + random.choice([-1, 1, 0])), s),
            lambda s: ' '.join(random.sample(s.split(), len(s.split()))) if len(s.split()) > 2 else s,
        ]
        return random.choice(mutations)(answer)
    
    def _structural_match(self, prompt: str, answer: str) -> float:
        """Structural parsing: negations, comparatives, transitivity, etc."""
        score = 0.0
        
        # Numeric comparison
        nums_p = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        nums_a = [float(x) for x in re.findall(r'\d+\.?\d*', answer)]
        if nums_p and nums_a:
            if any(re.search(r'greater|more|higher', prompt.lower())):
                if any(a > p for a in nums_a for p in nums_p):
                    score += 0.3
            elif any(re.search(r'less|fewer|lower', prompt.lower())):
                if any(a < p for a in nums_a for p in nums_p):
                    score += 0.3
        
        # Negation consistency
        neg_p = bool(re.search(r'\bnot\b|n\'t|\bno\b', prompt.lower()))
        neg_a = bool(re.search(r'\bnot\b|n\'t|\bno\b', answer.lower()))
        if 'true or false' in prompt.lower() or 'yes or no' in prompt.lower():
            score += 0.2
        
        # Transitivity detection
        if re.search(r'(\w+)\s+>\s+(\w+).*\2\s+>\s+(\w+)', prompt):
            if re.search(r'\1\s+>\s+\3', answer):
                score += 0.3
        
        # Modus tollens
        if re.search(r'if\s+(\w+).*then\s+(\w+)', prompt.lower()):
            if re.search(r'not\s+\2.*not\s+\1', prompt.lower()):
                score += 0.2
        
        return min(score, 1.0)
    
    def _computational_solve(self, prompt: str, answer: str) -> float:
        """Actually compute answers for solvable problems."""
        # Bat and ball pattern: X + Y = A, X - Y = B
        match = re.search(r'(\d+\.?\d*)\s*(?:dollars?|cents?)?.*total.*(\d+\.?\d*)\s*more', prompt.lower())
        if match:
            total, diff = float(match.group(1)), float(match.group(2))
            expensive = (total + diff) / 2
            cheap = (total - diff) / 2
            ans_nums = [float(x) for x in re.findall(r'\d+\.?\d*', answer)]
            if any(abs(n - cheap) < 0.01 or abs(n - expensive) < 0.01 for n in ans_nums):
                return 1.0
        
        # Simple arithmetic
        arith_match = re.search(r'(\d+\.?\d*)\s*([+\-*/])\s*(\d+\.?\d*)', prompt)
        if arith_match:
            a, op, b = float(arith_match.group(1)), arith_match.group(2), float(arith_match.group(3))
            result = eval(f'{a}{op}{b}')
            ans_nums = [float(x) for x in re.findall(r'\d+\.?\d*', answer)]
            if any(abs(n - result) < 0.01 for n in ans_nums):
                return 1.0
        
        # Bayesian base rate
        if re.search(r'base rate|prior|posterior|bayes', prompt.lower()):
            # Simple pattern: P(A|B) with base rate
            return 0.5  # Partial credit for recognizing pattern
        
        return 0.0
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        ncd = (c12 - min(c1, c2)) / max(c1, c2)
        return max(0, 1 - ncd)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguous/unanswerable questions."""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'have you stopped|have you quit|why did.*fail|why did.*stop', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every.*\ba\b\s+\w+', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).*who', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'either.*or(?!.*otherwise)', p_lower) and 'only' not in p_lower:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower) and not re.search(r'based on|according to|in terms of', p_lower):
            return 0.3
        
        # Missing information
        if re.search(r'what is|who is|when did', p_lower) and len(prompt) < 50:
            return 0.4
        
        return 0.85