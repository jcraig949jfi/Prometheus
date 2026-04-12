from collections import deque
from typing import Dict, Optional, Set, Tuple

"""
Structural Causal Counterfactual Scorer (SCCS)

Builds a DAG from propositions, performs constraint propagation,
counterfactual do-calculus simulation, and emergence weighting.
Combines causal inference with emergent macro-nodes for reasoning.
"""

import re
import numpy as np
from collections import defaultdict, deque
from typing import List, Dict, Tuple, Set, Optional


class ReasoningTool:
    def __init__(self):
        self.lambda_cf = 0.3  # Balance causal vs emergent
        self.emergence_threshold = 0.6
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for candidate in candidates:
            score = self._score_candidate(prompt, candidate)
            results.append({
                "candidate": candidate,
                "score": score,
                "reasoning": f"SCCS={score:.3f}"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        score = self._score_candidate(prompt, answer)
        # Cap by meta-confidence for epistemic honesty
        return min(meta_conf, min(0.95, score))
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity/unanswerability markers"""
        p_lower = prompt.lower()
        
        # Presupposition traps
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop))', p_lower):
            return 0.2
        
        # Scope ambiguity: "Every X ... a Y"
        if re.search(r'\bevery \w+.*\ba\b', p_lower):
            return 0.25
        
        # Pronoun ambiguity in questions
        if re.search(r'\b(he|she|it|they)\b', p_lower) and '?' in prompt:
            if re.search(r'\bwho\b', p_lower):
                return 0.25
        
        # False dichotomy
        if re.search(r'\b(either .* or|only two)', p_lower):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower):
            if not re.search(r'\b(most|least|metric|measure|criterion)', p_lower):
                return 0.3
        
        # Unanswerability markers
        if re.search(r'\b(impossible to|cannot determine|not enough|insufficient)', p_lower):
            return 0.2
        
        return 0.8  # Default confidence in prompt quality
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        # Try computational parsers first (>=70% weight)
        comp_score = self._computational_score(prompt, candidate)
        if comp_score is not None:
            return comp_score
        
        # Build DAG from prompt + candidate
        dag = self._build_dag(prompt + " " + candidate)
        
        # Constraint propagation
        satisfied, penalty = self._propagate_constraints(dag)
        
        # Counterfactual simulation
        cf_score = self._counterfactual_score(dag)
        
        # Emergence weighting
        struct_score = self._emergence_weighted_score(dag, satisfied)
        
        # NCD tiebreaker (<=15%)
        ncd = self._ncd(prompt, candidate)
        
        final = 0.55 * struct_score + 0.3 * cf_score + 0.15 * (1 - ncd) + penalty
        return max(0.0, min(1.0, final))
    
    def _computational_score(self, prompt: str, candidate: str) -> Optional[float]:
        """Execute actual computation on parsed problems"""
        # Numeric comparison
        match = re.search(r'(\d+\.?\d*)\s*(>|<|>=|<=|=)\s*(\d+\.?\d*)', prompt)
        if match:
            a, op, b = float(match.group(1)), match.group(2), float(match.group(3))
            ops = {'>': a > b, '<': a < b, '>=': a >= b, '<=': a <= b, '=': abs(a-b) < 0.001}
            computed = ops.get(op, False)
            cand_answer = 'yes' in candidate.lower() or 'true' in candidate.lower()
            return 0.95 if computed == cand_answer else 0.05
        
        # Bat-and-ball algebra: "X and Y cost Z, X costs Y + A, Y costs?"
        match = re.search(r'cost[s]?\s+\$?(\d+\.?\d*)[^\d]+cost[s]?\s+\$?(\d+\.?\d*)\s*more', prompt)
        if match and '?' in prompt:
            total, diff = float(match.group(1)), float(match.group(2))
            y = (total - diff) / 2
            try:
                cand_val = float(re.search(r'\d+\.?\d*', candidate).group())
                return 0.95 if abs(cand_val - y) < 0.01 else 0.1
            except:
                pass
        
        # All-but-N pattern
        match = re.search(r'all but (\d+)', prompt.lower())
        if match:
            n = int(match.group(1))
            total_match = re.search(r'(\d+)\s+(items|people|things)', prompt.lower())
            if total_match:
                total = int(total_match.group(1))
                result = total - n
                try:
                    cand_val = int(re.search(r'\d+', candidate).group())
                    return 0.95 if cand_val == result else 0.05
                except:
                    pass
        
        # Modular arithmetic
        match = re.search(r'(\d+)\s*mod\s*(\d+)', prompt.lower())
        if match:
            a, m = int(match.group(1)), int(match.group(2))
            result = a % m
            try:
                cand_val = int(re.search(r'\d+', candidate).group())
                return 0.95 if cand_val == result else 0.05
            except:
                pass
        
        # Modus tollens: "If A then B. Not B. Therefore?"
        if re.search(r'if .+ then', prompt.lower()) and re.search(r'\bnot\b', prompt.lower()):
            if 'not' in candidate.lower()[:20]:
                return 0.85
        
        return None
    
    def _build_dag(self, text: str) -> Dict:
        """Extract propositions and build DAG"""
        dag = {
            'nodes': [],
            'edges': [],
            'macro_nodes': []
        }
        
        text_lower = text.lower()
        
        # Extract causal propositions
        for match in re.finditer(r'(\w+)\s+(causes?|leads? to|results? in)\s+(\w+)', text_lower):
            src, rel, tgt = match.group(1), match.group(2), match.group(3)
            node_id_src = self._add_node(dag, src, False, None)
            node_id_tgt = self._add_node(dag, tgt, False, None)
            dag['edges'].append((node_id_src, node_id_tgt, 'CAUSE'))
        
        # Extract conditionals
        for match in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:[.,;]|$)', text_lower):
            antecedent, consequent = match.group(1).strip(), match.group(2).strip()
            node_id_ant = self._add_node(dag, antecedent, False, None)
            node_id_cons = self._add_node(dag, consequent, False, None)
            dag['edges'].append((node_id_ant, node_id_cons, 'CONDITIONAL'))
        
        # Extract negations
        for match in re.finditer(r'\b(not|no)\s+(\w+)', text_lower):
            prop = match.group(2)
            self._add_node(dag, prop, True, None)
        
        # Extract numeric comparisons
        for match in re.finditer(r'(\w+)\s*(>|<|>=|<=)\s*(\d+\.?\d*)', text_lower):
            var, op, val = match.group(1), match.group(2), float(match.group(3))
            bounds = self._op_to_bounds(op, val)
            self._add_node(dag, var, False, bounds)
        
        return dag
    
    def _add_node(self, dag: Dict, text: str, negated: bool, bounds: Optional[Tuple]) -> int:
        """Add node to DAG and return its ID"""
        for i, node in enumerate(dag['nodes']):
            if node['text'] == text:
                if negated:
                    node['negated'] = True
                if bounds:
                    node['bounds'] = bounds
                return i
        dag['nodes'].append({
            'text': text,
            'negated': negated,
            'bounds': bounds,
            'satisfied': None
        })
        return len(dag['nodes']) - 1
    
    def _op_to_bounds(self, op: str, val: float) -> Tuple[float, float]:
        """Convert comparison operator to interval bounds"""
        if op == '>':
            return (val + 0.001, float('inf'))
        elif op == '<':
            return (float('-inf'), val - 0.001)
        elif op == '>=':
            return (val, float('inf'))
        elif op == '<=':
            return (float('-inf'), val)
        return (float('-inf'), float('inf'))
    
    def _propagate_constraints(self, dag: Dict) -> Tuple[int, float]:
        """Constraint propagation with transitive closure"""
        satisfied = 0
        penalty = 0.0
        
        # Transitive closure on CAUSE edges
        for _ in range(3):  # Fixed iterations
            for src, tgt, rel in dag['edges']:
                if rel == 'CAUSE':
                    # If src satisfied, tgt should be satisfied
                    if dag['nodes'][src].get('satisfied'):
                        dag['nodes'][tgt]['satisfied'] = True
        
        # Modus ponens on CONDITIONAL edges
        for src, tgt, rel in dag['edges']:
            if rel == 'CONDITIONAL':
                if dag['nodes'][src].get('satisfied'):
                    dag['nodes'][tgt]['satisfied'] = True
        
        # Check for contradictions
        for node in dag['nodes']:
            if node.get('satisfied') and node.get('negated'):
                penalty -= 1.0
            elif node.get('satisfied') is not None:
                satisfied += 1
        
        return satisfied, penalty
    
    def _counterfactual_score(self, dag: Dict) -> float:
        """Simulate do-calculus interventions"""
        if not dag['nodes']:
            return 0.5
        
        baseline_sat = sum(1 for n in dag['nodes'] if n.get('satisfied'))
        total_change = 0.0
        interventions = 0
        
        # Try intervening on each node
        for i, node in enumerate(dag['nodes']):
            # Create intervention: remove incoming edges, set value
            intervention_dag = self._copy_dag(dag)
            intervention_dag['edges'] = [(s, t, r) for s, t, r in intervention_dag['edges'] if t != i]
            intervention_dag['nodes'][i]['satisfied'] = True
            
            # Re-propagate
            sat_after, _ = self._propagate_constraints(intervention_dag)
            change = abs(sat_after - baseline_sat) / max(1, len(dag['nodes']))
            total_change += change
            interventions += 1
        
        return total_change / max(1, interventions)
    
    def _emergence_weighted_score(self, dag: Dict, satisfied: int) -> float:
        """Weight by emergence with macro-nodes"""
        if not dag['nodes']:
            return 0.5
        
        # Create macro-nodes from clusters
        clusters = self._find_clusters(dag)
        
        total_weight = 0.0
        weighted_sat = 0.0
        
        for node in dag['nodes']:
            weight = 1.0
            if node.get('satisfied'):
                weighted_sat += weight
            total_weight += weight
        
        # Macro-node contribution
        for cluster in clusters:
            if len(cluster) >= 2:
                weight = np.log(1 + len(cluster))
                all_satisfied = all(dag['nodes'][i].get('satisfied') for i in cluster)
                if all_satisfied:
                    weighted_sat += weight
                total_weight += weight
        
        return weighted_sat / max(1, total_weight)
    
    def _find_clusters(self, dag: Dict) -> List[List[int]]:
        """Find connected components for macro-nodes"""
        if not dag['nodes']:
            return []
        
        adj = defaultdict(list)
        for src, tgt, _ in dag['edges']:
            adj[src].append(tgt)
            adj[tgt].append(src)
        
        visited = set()
        clusters = []
        
        for i in range(len(dag['nodes'])):
            if i not in visited:
                cluster = []
                queue = deque([i])
                while queue:
                    node = queue.popleft()
                    if node in visited:
                        continue
                    visited.add(node)
                    cluster.append(node)
                    for neighbor in adj[node]:
                        if neighbor not in visited:
                            queue.append(neighbor)
                clusters.append(cluster)
        
        return clusters
    
    def _copy_dag(self, dag: Dict) -> Dict:
        """Deep copy DAG for interventions"""
        return {
            'nodes': [n.copy() for n in dag['nodes']],
            'edges': dag['edges'].copy(),
            'macro_nodes': dag['macro_nodes'].copy()
        }
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance"""
        import zlib
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0