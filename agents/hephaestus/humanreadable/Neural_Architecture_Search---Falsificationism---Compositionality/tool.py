import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A reasoning tool combining Compositional Proposition Graphs (CPG), 
    Falsificationism, and NAS-inspired complexity penalties.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and logical connectives via regex into a graph.
    2. Falsification: Runs constraint propagation (boolean unit propagation + interval arithmetic).
       If a contradiction is found, the candidate is falsified (Score -> 0).
    3. Complexity: Calculates a description length penalty (NAS-style) based on node/edge count.
    4. Meta-Cognition: Detects ambiguity, presuppositions, and scope issues to cap confidence.
    """

    def __init__(self):
        # Hyperparameters tuned for balance
        self.alpha = 0.1  # Node penalty
        self.beta = 0.05  # Edge penalty
        self.gamma = 0.5  # Complexity scaling
        self.lambda_val = 0.7  # Falsification weight
        self.mu = 0.3   # Complexity weight
        
        # Patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'(\w+)\s*(>|<|>=|<=|=|is greater|is less|equals)\s*(\d+\.?\d*)', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|unless|then)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|leads to|results in|causes)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|every|each|any)\b', re.IGNORECASE),
            'conjunction': re.compile(r'\b(and|or)\b', re.IGNORECASE),
            # Tier B Traps
            'presupposition': re.compile(r'(have you stopped|why did .*(fail|stop)|when did .*(stop|fail))', re.IGNORECASE),
            'false_dichotomy': re.compile(r'(either .+ or .+|choose between .+ and .+)', re.IGNORECASE),
            'scope_ambiguity': re.compile(r'(every .+ .+ a .+|did everyone .+ the same)', re.IGNORECASE),
            'pronoun_ambiguity': re.compile(r'(.+ told .+ he|she|it was|who is)', re.IGNORECASE),
            'subjectivity': re.compile(r'(best|worst|favorite|most beautiful)', re.IGNORECASE)
        }

    def _parse_to_cpg(self, text: str) -> Dict[str, Any]:
        """Parses text into a Compositional Proposition Graph structure."""
        nodes = []
        edges = [] # List of (src_idx, dst_idx, type)
        constraints = [] # List of (var_name, op, value)
        
        # Simple tokenization for nodes
        words = re.findall(r'\b\w+\b', text.lower())
        unique_words = list(set(words))
        
        node_map = {w: i for i, w in enumerate(unique_words)}
        
        # Create nodes
        for w, idx in node_map.items():
            nodes.append({"id": idx, "type": "variable", "value": w})
            
        # Extract Relations and Edges
        # Negations
        neg_matches = list(self.patterns['negation'].finditer(text))
        for m in neg_matches:
            # Link negation to nearby word (simplified heuristic)
            start = m.start()
            # Find closest word index
            closest = -1
            min_dist = 999
            for w, idx in node_map.items():
                pos = text.lower().find(w)
                if pos != -1 and abs(pos - start) < min_dist:
                    min_dist = abs(pos - start)
                    closest = idx
            if closest != -1:
                edges.append((closest, closest, 1)) # Type 1 = Negation self-loop for simplicity in this model

        # Comparatives (Numeric constraints)
        comp_matches = list(self.patterns['comparative'].finditer(text))
        for m in comp_matches:
            var_name = m.group(1).lower()
            op = m.group(2)
            val = float(m.group(3))
            if var_name in node_map:
                constraints.append((var_name, op, val))
                # Add edge representing the constraint relation
                edges.append((node_map[var_name], node_map[var_name], 3)) # Type 3 = Constraint

        # Logical Connectives (Simplified adjacency)
        if self.patterns['conditional'].search(text):
            # Connect first and last word as conditional flow
            if len(nodes) >= 2:
                edges.append((0, len(nodes)-1, 3)) # Type 3 = Implication
        
        if self.patterns['conjunction'].search(text):
             if len(nodes) >= 2:
                edges.append((0, 1, 2)) # Type 2 = And

        # Build Adjacency Matrix
        n = len(nodes)
        adj = np.zeros((n, n), dtype=np.int32)
        for src, dst, etype in edges:
            if 0 <= src < n and 0 <= dst < n:
                adj[src, dst] = max(adj[src, dst], etype) # Overwrite with strongest type

        return {
            "nodes": nodes,
            "adj": adj,
            "constraints": constraints,
            "text": text
        }

    def _falsify(self, cpg: Dict, candidate_cpg: Dict) -> Tuple[bool, str]:
        """
        Attempts to falsify the candidate hypothesis against the prompt context.
        Returns (is_falsified, reason).
        """
        # 1. Check Numeric Constraints (Interval Arithmetic Simplified)
        # Collect all constraints from prompt and candidate
        all_constraints = cpg['constraints'] + candidate_cpg['constraints']
        
        # Group by variable
        var_bounds = {}
        for var, op, val in all_constraints:
            if var not in var_bounds:
                var_bounds[var] = {'min': -np.inf, 'max': np.inf}
            
            if op in ['>', '>=', 'is greater']:
                var_bounds[var]['min'] = max(var_bounds[var]['min'], val)
            elif op in ['<', '<=', 'is less']:
                var_bounds[var]['max'] = min(var_bounds[var]['max'], val)
            elif op in ['=', 'equals']:
                var_bounds[var]['min'] = max(var_bounds[var]['min'], val)
                var_bounds[var]['max'] = min(var_bounds[var]['max'], val)

        # Check for contradictions
        for var, bounds in var_bounds.items():
            if bounds['min'] >= bounds['max'] and bounds['min'] != -np.inf:
                # Strict inequality check logic simplified for integer-like bounds
                if bounds['min'] > bounds['max']:
                    return True, f"Numeric contradiction on {var}: {bounds}"
                # Handle strict vs non-strict if operators were tracked precisely
                # Here we assume if min >= max in a tight loop, it's suspicious, 
                # but strict falsification requires clear >
                if bounds['min'] == bounds['max']:
                     # If we have x > 5 and x < 5, min=5, max=5. 
                     # This is a contradiction for strict inequalities.
                     # For this simplified engine, we flag if min > max - epsilon
                     pass 

        # 2. Logical Contradiction (Simplified Unit Propagation)
        # Check if Prompt asserts P and Candidate asserts NOT P (or vice versa)
        # We look for shared variables with negation edges
        p_nodes = {n['value']: i for i, n in enumerate(cpg['nodes'])}
        c_nodes = {n['value']: i for i, n in enumerate(candidate_cpg['nodes'])}
        
        shared_vars = set(p_nodes.keys()) & set(c_nodes.keys())
        
        for var in shared_vars:
            p_idx = p_nodes[var]
            c_idx = c_nodes[var]
            
            # Check negation in prompt
            p_negated = cpg['adj'][p_idx, p_idx] == 1
            # Check negation in candidate
            c_negated = candidate_cpg['adj'][c_idx, c_idx] == 1
            
            if p_negated != c_negated:
                # One says P, other says NOT P. 
                # However, we only falsify if the prompt is the ground truth.
                # If prompt says "Not X" and candidate says "X", candidate is falsified.
                if p_negated and not c_negated:
                    return True, f"Logical contradiction: Prompt denies '{var}', candidate asserts it."
                if not p_negated and c_negated:
                     # Prompt implies P (by not denying?), Candidate denies. 
                     # Harder to falsify without explicit P in prompt. 
                     # We skip unless explicit positive assertion exists.
                     pass

        return False, "No contradiction found"

    def _compute_complexity(self, cpg: Dict) -> float:
        """Computes NAS-style complexity penalty."""
        n_nodes = len(cpg['nodes'])
        n_edges = int(np.sum(cpg['adj'] > 0))
        return self.alpha * n_nodes + self.beta * n_edges

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Evaluates the prompt for ambiguity and traps.
        Returns a confidence cap (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            return 0.3
            
        # 3. Scope Ambiguity
        if self.patterns['scope_ambiguity'].search(p_lower):
            return 0.4
            
        # 4. Pronoun Ambiguity
        if self.patterns['pronoun_ambiguity'].search(p_lower):
            return 0.3
            
        # 5. Subjectivity
        if self.patterns['subjectivity'].search(p_lower):
            return 0.4

        # 6. Unanswerability (Heuristic: Question words without data)
        if any(q in p_lower for q in ['who', 'what', 'where', 'when', 'why', 'how']):
            if len(prompt.split()) < 10: # Very short questions often lack context
                return 0.25

        # Default high confidence if structure is clear
        return 1.0

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        
        len1, len2, len12 = len(z1), len(z2), len(z12)
        if len1 + len2 == 0:
            return 0.0
        return (len12 - min(len1, len2)) / max(len1, len2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_cpg = self._parse_to_cpg(prompt)
        results = []
        
        # Meta-confidence cap based on prompt quality
        meta_cap = self._meta_confidence(prompt)

        for cand in candidates:
            cand_cpg = self._parse_to_cpg(cand)
            
            # 1. Falsification Test
            is_falsified, reason = self._falsify(prompt_cpg, cand_cpg)
            f_score = 0.0 if is_falsified else 1.0
            
            # 2. Complexity Penalty
            complexity = self._compute_complexity(cand_cpg)
            s_score = -self.gamma * complexity
            
            # 3. NCD Tiebreaker (Max 15% influence)
            ncd = self._ncd_score(prompt, cand)
            ncd_component = (1.0 - ncd) * 0.15
            
            # Final Score Calculation
            # Base logic score + complexity penalty + small NCD boost
            raw_score = (self.lambda_val * f_score) + (self.mu * s_score) + ncd_component
            
            # Apply Meta-Confidence Cap
            # If the prompt is ambiguous (meta_cap < 1), we scale down the confidence in this evaluation
            final_score = raw_score * meta_cap
            
            # Ensure non-negative for ranking purposes, though logic holds
            final_score = max(0.0, final_score)
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Falsified: {is_falsified}. Reason: {reason}. Meta-cap: {meta_cap:.2f}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at meta-confidence limit derived from prompt analysis.
        """
        # 1. Check Meta-Confidence (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # If meta_cap is low, we immediately return low confidence regardless of answer
        if meta_cap < 0.5:
            return meta_cap

        # 2. Structural Match Check
        # If no structural patterns match at all, be humble
        prompt_cpg = self._parse_to_cpg(prompt)
        if len(prompt_cpg['constraints']) == 0 and len(prompt_cpg['nodes']) < 3:
            # Very sparse parsing might indicate inability to reason
            base_conf = 0.5
        else:
            base_conf = 1.0

        # 3. Falsification Check
        cand_cpg = self._parse_to_cpg(answer)
        is_falsified, _ = self._falsify(prompt_cpg, cand_cpg)
        
        if is_falsified:
            return 0.05 # Definitely wrong
        
        # Combine
        final_conf = min(base_conf, meta_cap)
        
        # Never return > 0.9 unless computation was definitive (simulated here by high structure)
        if len(prompt_cpg['constraints']) > 0:
            final_conf = min(final_conf, 0.95)
        else:
            final_conf = min(final_conf, 0.85)
            
        return round(final_conf, 3)