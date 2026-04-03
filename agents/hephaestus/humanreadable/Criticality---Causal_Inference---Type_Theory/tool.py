import numpy as np
from collections import defaultdict

class ReasoningTool:
    def __init__(self):
        # Type hierarchy: 0=Prop, 1=Causal, 2=Quant, 3=Cond
        self.type_lattice = np.array([[1,1,1,1],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
        self.weights = {'type': 0.5, 'causal': 0.3, 'criticality': 0.2}
        
    def _parse_proposition(self, text):
        """Extract typed propositions and causal edges"""
        nodes, edges = [], []
        var_to_idx = {}
        idx = 0
        
        # Causal patterns
        causal_pat = r'(\w+(?:\s+\w+)*)\s+(causes?|leads? to|results? in|increases?|decreases?)\s+(\w+(?:\s+\w+)*)'
        for match in re.finditer(causal_pat, text, re.I):
            cause, verb, effect = match.groups()
            if cause not in var_to_idx:
                var_to_idx[cause] = idx
                nodes.append({'text': cause, 'type': 1, 'negated': False})
                idx += 1
            if effect not in var_to_idx:
                var_to_idx[effect] = idx
                nodes.append({'text': effect, 'type': 1, 'negated': False})
                idx += 1
            edges.append((var_to_idx[cause], var_to_idx[effect]))
        
        # Quantitative comparisons
        quant_pat = r'(\w+(?:\s+\w+)*)\s+(>|<|>=|<=|=|equals?|more than|less than|greater|smaller)\s+(\w+(?:\s+\w+)*|\d+\.?\d*)'
        for match in re.finditer(quant_pat, text, re.I):
            lhs, op, rhs = match.groups()
            if lhs not in var_to_idx:
                var_to_idx[lhs] = idx
                nodes.append({'text': lhs, 'type': 2, 'negated': False, 'op': op, 'rhs': rhs})
                idx += 1
        
        # Conditionals
        cond_pat = r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$|,)'
        for match in re.finditer(cond_pat, text, re.I):
            antecedent, consequent = match.groups()
            if antecedent not in var_to_idx:
                var_to_idx[antecedent] = idx
                nodes.append({'text': antecedent, 'type': 3, 'negated': False})
                idx += 1
            if consequent not in var_to_idx:
                var_to_idx[consequent] = idx
                nodes.append({'text': consequent, 'type': 3, 'negated': False})
                idx += 1
            edges.append((var_to_idx[antecedent], var_to_idx[consequent]))
        
        # Negations
        for i, node in enumerate(nodes):
            if re.search(r'\b(not|never|no|n\'t)\b', node['text'], re.I):
                node['negated'] = True
        
        return nodes, edges
    
    def _type_unify(self, nodes):
        """Hindley-Milner style type unification via constraint solving"""
        if not nodes:
            return 0.0
        
        type_vec = np.array([n['type'] for n in nodes])
        constraints = []
        
        # Build constraints from shared variables
        var_types = defaultdict(list)
        for i, n in enumerate(nodes):
            var_types[n['text']].append(i)
        
        # Variables must have consistent types
        for indices in var_types.values():
            if len(indices) > 1:
                constraints.append((indices[0], indices[1], 'eq'))
        
        # Solve constraints: compute type error as variance
        type_error = 0.0
        for idx_list in var_types.values():
            types = [nodes[i]['type'] for i in idx_list]
            if len(types) > 1:
                type_error += np.var(types)
        
        return 1.0 / (1.0 + type_error)
    
    def _causal_score(self, edges, n_nodes):
        """Check acyclicity and compute criticality via path length variance"""
        if not edges or n_nodes == 0:
            return 1.0, 0.0
        
        # Check for cycles using topological_sort
        try:
            order = topological_sort(edges)
            cycle_penalty = 0.0
        except:
            cycle_penalty = 1.0
            order = list(range(n_nodes))
        
        # Compute criticality: variance in path lengths from each node
        adj_matrix = np.zeros((n_nodes, n_nodes))
        for u, v in edges:
            if u < n_nodes and v < n_nodes:
                adj_matrix[u, v] = 1
        
        path_lengths = []
        for start in range(n_nodes):
            try:
                reachable = dag_traverse(edges, start)
                path_lengths.append(len(reachable))
            except:
                path_lengths.append(0)
        
        susceptibility = np.var(path_lengths) if path_lengths else 0.0
        
        return cycle_penalty, susceptibility
    
    def _meta_confidence(self, prompt):
        """Detect epistemic issues that should lower confidence"""
        issues = 0
        
        # Presupposition
        if re.search(r'\b(have you stopped|did you quit|why did .+ (fail|stop))', prompt, re.I):
            issues += 1
        
        # Scope ambiguity
        if re.search(r'\bevery .+ (a |an |one )', prompt, re.I):
            issues += 1
        
        # Pronoun ambiguity with "who" question
        if re.search(r'(he|she|they|it).+(who|which person)', prompt, re.I):
            issues += 1
        
        # False dichotomy
        if re.search(r'\b(either .+ or |only two)', prompt, re.I) and not re.search(r'(other|else|also)', prompt, re.I):
            issues += 1
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful|most important)\b', prompt, re.I):
            issues += 1
        
        # Unanswerability markers
        if re.search(r'(cannot be determined|insufficient|not enough|ambiguous)', prompt, re.I):
            issues += 1
        
        # Cap confidence based on issues
        return max(0.3, 1.0 - 0.2 * issues)
    
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Rank candidates by critical-causal-type score"""
        prompt_nodes, prompt_edges = self._parse_proposition(prompt)
        results = []
        
        for cand in candidates:
            cand_nodes, cand_edges = self._parse_proposition(cand)
            all_nodes = prompt_nodes + cand_nodes
            all_edges = prompt_edges + cand_edges
            n_nodes = len(all_nodes)
            
            # Type unification score
            type_score = self._type_unify(all_nodes)
            
            # Causal consistency
            cycle_penalty, susceptibility = self._causal_score(all_edges, n_nodes)
            causal_score = 1.0 - cycle_penalty
            
            # Criticality (penalize high susceptibility)
            crit_score = 1.0 / (1.0 + susceptibility)
            
            # Combine scores
            score = (self.weights['type'] * type_score +
                    self.weights['causal'] * causal_score +
                    self.weights['criticality'] * crit_score)
            
            # NCD tiebreaker (max 10%)
            import zlib
            ncd = len(zlib.compress((prompt + cand).encode())) / (
                len(zlib.compress(prompt.encode())) + len(zlib.compress(cand.encode())) + 1e-9)
            score += 0.1 * (1.0 - ncd)
            
            reasoning = f"Type:{type_score:.2f} Causal:{causal_score:.2f} Crit:{crit_score:.2f} NCD:{1-ncd:.2f}"
            results.append({'candidate': cand, 'score': score, 'reasoning': reasoning})
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-confidence check"""
        meta_cap = self._meta_confidence(prompt)
        
        # Parse and score
        prompt_nodes, prompt_edges = self._parse_proposition(prompt)
        ans_nodes, ans_edges = self._parse_proposition(answer)
        
        # No structure parsed -> honest uncertainty
        if not ans_nodes and not ans_edges:
            return min(0.25, meta_cap)
        
        all_nodes = prompt_nodes + ans_nodes
        all_edges = prompt_edges + ans_edges
        n_nodes = len(all_nodes)
        
        type_score = self._type_unify(all_nodes)
        cycle_penalty, susceptibility = self._causal_score(all_edges, n_nodes)
        causal_score = 1.0 - cycle_penalty
        crit_score = 1.0 / (1.0 + susceptibility)
        
        # Aggregate confidence
        base_conf = (self.weights['type'] * type_score +
                     self.weights['causal'] * causal_score +
                     self.weights['criticality'] * crit_score)
        
        # Apply meta-cap
        return min(base_conf, meta_cap)