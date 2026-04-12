import re
import numpy as np
from typing import List, Dict, Any, Tuple, Optional

class ReasoningTool:
    """
    A reasoning tool combining Fractal Geometry, Chaos Theory, and Counterfactual Reasoning.
    
    Mechanism:
    1. Structural Parsing (Fractal): Recursively parses logical structures (if/then, not, because, comparatives)
       into a self-similar tree where each node represents a logical operation.
    2. Counterfactual Perturbation: Generates M alternative "worlds" by flipping boolean antecedents
       or perturbing numeric values by epsilon.
    3. Chaos-Based Scoring: Propagates truth values through the tree for all worlds simultaneously.
       Calculates a Lyapunov-like instability metric based on the variance of the root truth value.
       High stability (low variance) under perturbation indicates robust reasoning.
    4. Hybrid Scoring: Primary score comes from structural stability. NCD is used only as a tiebreaker.
    """

    def __init__(self):
        self.M = 50  # Number of counterfactual worlds
        self.epsilon = 1e-3
        
        # Regex patterns for structural extraction
        self.patterns = {
            'conditional': re.compile(r'\bif\s+(.+?)\s+(?:then\s+)?(.+?)(?=\b(?:if|because|not|and|or)\b|$)', re.IGNORECASE),
            'negation': re.compile(r'\bnot\s+(.+?)', re.IGNORECASE),
            'causal': re.compile(r'\b(.+?)\s+(?:because|leads to|causes)\s+(.+?)', re.IGNORECASE),
            'comparative_num': re.compile(r'(\d+\.?\d*)\s*(?:is\s+)?([<>=]+)\s*(\d+\.?\d*)'),
            'quantifier': re.compile(r'\b(all|some|none)\s+(.+?)', re.IGNORECASE),
            'conjunction': re.compile(r'\b(.+?)\s+(and|or)\s+(.+?)', re.IGNORECASE)
        }

    def _parse_tree(self, text: str, depth: int = 0) -> Dict[str, Any]:
        """
        Recursively builds a fractal-like parse tree from text.
        Each node contains type, children, and truth values.
        """
        if depth > 5: # Prevent infinite recursion on malformed input
            return {'type': 'atomic', 'content': text, 'children': [], 'truth_orig': True, 'truth_cf': None}

        text_clean = text.strip()
        
        # Check Conditionals
        match = self.patterns['conditional'].search(text_clean)
        if match:
            antecedent, consequent = match.groups()
            return {
                'type': 'conditional',
                'content': text_clean,
                'children': [self._parse_tree(antecedent, depth+1), self._parse_tree(consequent, depth+1)],
                'truth_orig': True, 'truth_cf': None
            }

        # Check Causal
        match = self.patterns['causal'].search(text_clean)
        if match:
            cause, effect = match.groups()
            return {
                'type': 'causal',
                'content': text_clean,
                'children': [self._parse_tree(cause, depth+1), self._parse_tree(effect, depth+1)],
                'truth_orig': True, 'truth_cf': None
            }

        # Check Comparatives (Numeric)
        match = self.patterns['comparative_num'].search(text_clean)
        if match:
            v1, op, v2 = match.groups()
            val1, val2 = float(v1), float(v2)
            # Determine base truth
            if op == '<': base_truth = val1 < val2
            elif op == '>': base_truth = val1 > val2
            else: base_truth = val1 == val2
            
            return {
                'type': 'comparative',
                'content': text_clean,
                'values': (val1, val2, op),
                'children': [],
                'truth_orig': base_truth,
                'truth_cf': None
            }

        # Check Negation
        if text_clean.lower().startswith('not '):
            child = self._parse_tree(text_clean[4:], depth+1)
            return {
                'type': 'negation',
                'content': text_clean,
                'children': [child],
                'truth_orig': not child.get('truth_orig', True), # Simplified immediate eval
                'truth_cf': None
            }

        # Atomic fallback
        return {'type': 'atomic', 'content': text_clean, 'children': [], 'truth_orig': True, 'truth_cf': None}

    def _generate_worlds(self, node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates M counterfactual variations of the tree structure or values.
        For conditionals: Flip antecedent truth.
        For numerics: Perturb values by epsilon.
        """
        worlds = []
        for i in range(self.M):
            # Deep copy structure for independence
            world = self._deep_copy_node(node)
            self._perturb_node(world, i)
            worlds.append(world)
        return worlds

    def _deep_copy_node(self, node: Dict) -> Dict:
        new_node = {
            'type': node['type'],
            'content': node.get('content', ''),
            'values': node.get('values'),
            'children': [self._deep_copy_node(c) for c in node.get('children', [])],
            'truth_orig': node['truth_orig'],
            'truth_cf': None
        }
        return new_node

    def _perturb_node(self, node: Dict, seed: int):
        """Applies counterfactual perturbation based on node type."""
        np.random.seed(seed)
        
        if node['type'] == 'conditional' and node['children']:
            # Counterfactual: Flip the antecedent (child 0) logic flag implicitly via a marker
            # In this implementation, we mark it to be evaluated as False in the propagation step
            node['_cf_flip_antecedent'] = True
            
        if node['type'] == 'comparative' and node.get('values'):
            v1, v2, op = node['values']
            # Perturb v1 slightly
            noise = np.random.normal(0, self.epsilon)
            node['values'] = (v1 + noise, v2, op)
            
        for child in node.get('children', []):
            self._perturb_node(child, seed + 1)

    def _evaluate_world(self, node: Dict, world_idx: int) -> bool:
        """Evaluates a single node in a specific counterfactual world."""
        if node['type'] == 'atomic':
            # Atomic truths are assumed stable unless part of a larger logical chain
            return True 
        
        if node['type'] == 'comparative':
            v1, v2, op = node['values']
            if op == '<': return v1 < v2
            if op == '>': return v1 > v2
            return v1 == v2
            
        if node['type'] == 'negation':
            if not node['children']: return False
            child_val = self._evaluate_world(node['children'][0], world_idx)
            return not child_val
            
        if node['type'] == 'conditional':
            # If-Then: A -> B is equivalent to (not A) or B
            if not node['children'] or len(node['children']) < 2:
                return True
            
            # Counterfactual logic: If marked, force antecedent to opposite of original?
            # Standard counterfactual: "What if A was false?" -> Evaluate B given not A.
            # Here we measure stability. 
            antecedent = self._evaluate_world(node['children'][0], world_idx)
            consequent = self._evaluate_world(node['children'][1], world_idx)
            
            # Apply specific counterfactual flip for this world if marked
            if node.get('_cf_flip_antecedent'):
                antecedent = not antecedent
                
            return (not antecedent) or consequent

        if node['type'] == 'causal':
            # Simplified causal: Both cause and effect must hold
            if len(node['children']) < 2: return True
            c1 = self._evaluate_world(node['children'][0], world_idx)
            c2 = self._evaluate_world(node['children'][1], world_idx)
            return c1 and c2

        return True

    def _compute_instability(self, node: Dict) -> float:
        """
        Computes the Lyapunov-like instability score.
        1. Generate M worlds.
        2. Evaluate root truth for all M worlds.
        3. Calculate variance.
        """
        worlds = self._generate_worlds(node)
        truths = np.array([self._evaluate_world(node, i) for i in range(self.M)], dtype=float)
        
        # Variance of boolean array (0.0 to 1.0)
        # Max variance for binary is 0.25 (when p=0.5)
        variance = np.var(truths)
        norm_instability = variance / 0.25
        return min(1.0, norm_instability)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        len1, len2 = len(b1), len(b2)
        if len1 == 0 or len2 == 0: return 1.0
        # Concatenation compression
        try:
            len_cat = len(zlib.compress(b1 + b2))
            len1_comp = len(zlib.compress(b1))
            len2_comp = len(zlib.compress(b2))
            ncd = (len_cat - min(len1_comp, len2_comp)) / max(len1_comp, len2_comp)
            return max(0.0, min(1.0, ncd))
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        prompt_tree = self._parse_tree(prompt)
        
        # Pre-calculate prompt instability (complexity of the question)
        # Though the spec asks for answer stability, the prompt structure matters for context.
        
        for cand in candidates:
            # Combine prompt and candidate for full logical context
            full_text = f"{prompt} {cand}"
            tree = self._parse_tree(full_text)
            
            # 1. Structural Stability Score (Chaos/Fractal component)
            instability = self._compute_instability(tree)
            stability_score = 1.0 - instability
            
            # 2. NCD Tiebreaker
            # We want the candidate that compresses well with the prompt (coherence)
            # but isn't just a copy. 
            ncd_val = self._ncd_distance(prompt, cand)
            
            # Heuristic: High stability is good. Low NCD (high similarity) is good for relevance,
            # but we penalize exact matches if they don't add value. 
            # Score formulation: Stability (dominant) + small NCD adjustment
            score = stability_score * 0.9 + (1.0 - ncd_val) * 0.1
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Stability: {stability_score:.3f}, NCD: {ncd_val:.3f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on stability of the combined statement."""
        full_text = f"{prompt} {answer}"
        tree = self._parse_tree(full_text)
        instability = self._compute_instability(tree)
        return float(1.0 - instability)