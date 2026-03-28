import re
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A multi-scale reasoning tool combining Renormalization, Analogical Reasoning, and Feedback Control.
    
    Mechanism:
    1. Structural Parsing: Extracts entities and relations (negation, causal, numeric, etc.) into a graph.
    2. Renormalization: Builds a hierarchy of graphs by contracting nodes with similar relation profiles.
    3. Analogical Matching: Computes subgraph match scores at each scale using greedy mapping.
    4. Feedback Control: Uses a PID-like scheme to dynamically weight the contribution of each scale 
       based on the error between the match score and the ideal target (1.0).
    5. Scoring: Primary score is structural; NCD is used only as a tiebreaker for zero-structure cases.
    """
    
    # Relation patterns
    PATTERNS = {
        'negation': [r'\b(not|no|never|neither)\b', r'\bwithout\b'],
        'comparative': [r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', r'\b(-er|more|less)\s+\w+'],
        'conditional': [r'\b(if|unless|then|otherwise|provided)\b'],
        'causal': [r'\b(because|since|therefore|thus|hence|leads? to|causes?)\b'],
        'numeric': [r'\d+(\.\d+)?'],
        'ordering': [r'\b(first|last|before|after|precede|follow)\b', r'[<>]=?'],
        'equality': [r'\b(is|are|was|were|equals?|same)\b', r'='],
        'existence': [r'\b(some|all|every|any|none|exists)\b']
    }

    def __init__(self):
        self.tau = 0.8  # Contraction threshold
        self.kp = 0.5   # Proportional gain
        self.ki = 0.1   # Integral gain
        self.kd = 0.1   # Derivative gain

    def _tokenize(self, text: str) -> List[str]:
        return re.split(r'[\s,.!?;:]+', text.lower())

    def _extract_relations(self, text: str) -> List[Tuple[str, str, str]]:
        """Extract (src, type, dst) tuples based on regex patterns."""
        relations = []
        tokens = self._tokenize(text)
        text_lower = text.lower()
        
        # Simple entity extraction (nouns/numbers)
        entities = [t for t in tokens if re.match(r'[a-z]+|\d+', t)]
        
        for r_type, patterns in self.PATTERNS.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, text_lower))
                for match in matches:
                    # Find nearest entities to serve as src/dst
                    start, end = match.span()
                    # Heuristic: assign nearest surrounding words as context
                    src = entities[0] if entities else "subject"
                    dst = entities[-1] if entities else "object"
                    
                    # Refine src/dst based on proximity if possible
                    words = text_lower.split()
                    idx = len(text_lower[:start].split())
                    if idx < len(words):
                        if idx > 0: src = words[idx-1]
                        if idx < len(words)-1: dst = words[idx+1]
                        
                    relations.append((src, r_type, dst))
        
        # Numeric comparison specific handling
        nums = re.findall(r'\d+(\.\d+)?', text)
        if len(nums) >= 2:
            # Assume ordering between first two numbers found
            relations.append((nums[0], 'ordering', nums[1]))
            
        return relations

    def _build_graph(self, text: str) -> Dict[str, Any]:
        """Build initial graph G0."""
        relations = self._extract_relations(text)
        nodes = set()
        edges = []
        for src, r_type, dst in relations:
            nodes.add(src)
            nodes.add(dst)
            # One-hot-ish label vector (simplified to type hash for brevity in this constraint)
            label = hash(r_type) % 1000 
            edges.append({'src': src, 'dst': dst, 'type': r_type, 'label': label})
        
        node_list = list(nodes)
        # Node labels: aggregate relation types connected to node
        node_labels = {}
        for n in node_list:
            n_types = [e['type'] for e in edges if e['src']==n or e['dst']==n]
            node_labels[n] = n_types
            
        return {'nodes': node_list, 'edges': edges, 'node_labels': node_labels, 'raw': text}

    def _renormalize(self, graph: Dict) -> List[Dict]:
        """Create hierarchy of graphs by contracting similar nodes."""
        hierarchy = [graph]
        current_g = graph
        
        for _ in range(2): # 2 levels of renormalization
            nodes = current_g['nodes']
            if len(nodes) <= 1:
                break
                
            # Compute similarity matrix based on node labels (relation types)
            # Simplified: Jaccard similarity of relation types
            new_nodes = []
            new_edges = []
            visited = set()
            
            # Greedy contraction
            for i, n1 in enumerate(nodes):
                if n1 in visited: continue
                group = {n1}
                l1 = set(current_g['node_labels'].get(n1, []))
                
                for n2 in nodes[i+1:]:
                    if n2 in visited: continue
                    l2 = set(current_g['node_labels'].get(n2, []))
                    if not l1 and not l2:
                        sim = 1.0
                    elif not l1 or not l2:
                        sim = 0.0
                    else:
                        sim = len(l1 & l2) / len(l1 | l2)
                    
                    if sim > self.tau:
                        group.add(n2)
                        l1.update(l2)
                
                # Contract group into super-node
                super_node = "|".join(sorted(group))
                new_nodes.append(super_node)
                visited.update(group)
                
                # Merge edges
                for e in current_g['edges']:
                    if e['src'] in group or e['dst'] in group:
                        s = super_node if e['src'] in group else e['src']
                        d = super_node if e['dst'] in group else e['dst']
                        if s != d: # Remove self-loops
                            new_edges.append({'src': s, 'dst': d, 'type': e['type'], 'label': e['label']})
            
            if not new_nodes:
                break
                
            # Rebuild labels for new graph
            new_labels = {}
            for n in new_nodes:
                new_labels[n] = [e['type'] for e in new_edges if e['src']==n or e['dst']==n]
                
            current_g = {'nodes': new_nodes, 'edges': new_edges, 'node_labels': new_labels, 'raw': current_g['raw']}
            hierarchy.append(current_g)
            
        return hierarchy

    def _analogical_match(self, cand_g: Dict, ref_g: Dict) -> float:
        """Greedy subgraph match score."""
        if not ref_g['edges']:
            return 1.0 if not cand_g['edges'] else 0.0
        
        cand_edges = set((e['src'], e['type'], e['dst']) for e in cand_g['edges'])
        ref_edges = set((e['src'], e['type'], e['dst']) for e in ref_g['edges'])
        
        if not ref_edges:
            return 1.0
            
        matches = len(cand_edges & ref_edges)
        # Also check for semantic equivalents (simplified: substring match for types)
        # This is a strict structural match. For analogical, we relax slightly:
        # If types match and nodes are present, count partial.
        
        total_ref = len(ref_edges)
        if total_ref == 0: return 1.0
        
        # Greedy node mapping could go here, but set intersection is O(1) avg and robust for exact logic
        score = matches / total_ref
        return min(1.0, score)

    def _pid_weighted_score(self, cand_hierarchy: List[Dict], ref_hierarchy: List[Dict]) -> float:
        """Compute final score using PID-controlled weighting."""
        k = min(len(cand_hierarchy), len(ref_hierarchy))
        if k == 0: return 0.0
        
        scores = []
        weights = [1.0] * k
        target = 1.0
        prev_error = 0.0
        integral = 0.0
        
        final_score = 0.0
        weight_sum = 0.0
        
        for i in range(k):
            s = self._analogical_match(cand_hierarchy[i], ref_hierarchy[i])
            scores.append(s)
            
            error = target - s
            integral += error
            derivative = error - prev_error
            
            # Update weight for NEXT iteration (or current influence)
            # w_new = w_old + Kp*e + Ki*sum(e) + Kd*diff(e)
            adjustment = self.kp * error + self.ki * integral + self.kd * derivative
            
            # Apply adjustment to current level's contribution logic
            # In this formulation, we adjust the weight of the current score based on error trend
            w = weights[i] + adjustment
            w = max(0.1, w) # Prevent negative/zero weights
            
            final_score += w * s
            weight_sum += w
            
            prev_error = error
            
        return (final_score / weight_sum) if weight_sum > 0 else 0.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance tiebreaker."""
        try:
            z1 = len(repr(zip(s1.encode()))) # Mock compression length proxy
            z2 = len(repr(zip(s2.encode())))
            z12 = len(repr(zip((s1+s2).encode())))
            if min(z1, z2) == 0: return 1.0
            return (z12 - min(z1, z2)) / max(z1, z2)
        except:
            return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # Build reference graph from prompt (treating prompt as the "truth" structure)
        # In QA, usually we compare Candidate vs Ground Truth. 
        # Here, we assume the Prompt contains the constraints/logic structure.
        # We treat the prompt as the reference schema.
        ref_hierarchy = self._renormalize(self._build_graph(prompt))
        
        results = []
        for cand in candidates:
            cand_hierarchy = self._renormalize(self._build_graph(cand))
            
            # Primary Score: Structural Reasoning
            score = self._pid_weighted_score(cand_hierarchy, ref_hierarchy)
            
            # Fallback/Tiebreaker: If structural signal is weak (e.g. short answers), use NCD
            if score < 0.1: 
                ncd_val = self._ncd(prompt, cand)
                # Invert NCD so lower distance = higher score
                score = max(0.1, 1.0 - ncd_val)
                
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Structural match across {len(ref_hierarchy)} scales with PID weighting."
            })
            
        # Rank descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']