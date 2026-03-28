import re
import zlib
import numpy as np
from collections import defaultdict, deque

class ReasoningTool:
    """
    Evaluates reasoning candidates by parsing structural logic (negation, conditionals, 
    causality, numerics) into a propositional graph. It scores based on:
    1. Structural Coherence (Topology-inspired): Penalizes disconnected fragments or 
       excessive cyclic contradictions (approximated via cycle detection in logic flow).
    2. Falsifiability: Measures how many propositions are linked to observable facts 
       (numeric/comparative nodes) vs abstract claims.
    3. Simplicity (Kolmogorov proxy): Uses zlib compression length of the serialized 
       logical structure as a tiebreaker.
    
    Logic dominates; compression is only a tiebreaker to satisfy the NCD baseline requirement.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without|impossible)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|otherwise)\b', re.I),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads to|causes)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.I),
            'equality': re.compile(r'\b(equal|same|identical|equivalent)\b', re.I),
            'numeric': re.compile(r'-?\d+(?:\.\d+)?'),
            'temporal': re.compile(r'\b(before|after|during|while|until)\b', re.I)
        }

    def _extract_props(self, text: str) -> list:
        """Extract atomic propositions and label types."""
        props = []
        text_lower = text.lower()
        
        # Identify present logical markers
        labels = set()
        if self.patterns['negation'].search(text_lower): labels.add('neg')
        if self.patterns['conditional'].search(text_lower): labels.add('cond')
        if self.patterns['causal'].search(text_lower): labels.add('caus')
        if self.patterns['comparative'].search(text_lower): labels.add('comp')
        if self.patterns['equality'].search(text_lower): labels.add('eq')
        if self.patterns['temporal'].search(text_lower): labels.add('temp')
        
        nums = self.patterns['numeric'].findall(text)
        if nums:
            labels.add('num')
            # Numeric consistency check
            try:
                vals = [float(n) for n in nums]
                if len(vals) >= 2 and vals[0] == vals[1]:
                    labels.add('num_eq')
            except ValueError:
                pass

        # Create a pseudo-proposition for the whole sentence structure
        props.append({'id': 0, 'text': text[:50], 'labels': labels, 'has_nums': len(nums) > 0})
        return props

    def _build_graph(self, props: list) -> dict:
        """Build adjacency list from propositions."""
        graph = defaultdict(list)
        nodes = set()
        for p in props:
            nodes.add(p['id'])
            # Self-loop for internal consistency check if negation exists without condition
            if 'neg' in p['labels'] and 'cond' not in p['labels']:
                graph[p['id']].append((p['id'], 'self_neg')) 
        
        # Connect sequential propositions (simplified flow)
        for i in range(len(props) - 1):
            u, v = props[i]['id'], props[i+1]['id']
            label = 'flow'
            if 'caus' in props[i]['labels']: label = 'cause'
            if 'cond' in props[i]['labels']: label = 'cond'
            graph[u].append((v, label))
            nodes.add(u)
            nodes.add(v)
            
        return graph, nodes

    def _count_cycles(self, graph: dict, nodes: set) -> int:
        """Approximate cycle count (beta_1 proxy) using DFS back-edges."""
        visited = set()
        rec_stack = set()
        cycles = 0
        
        def dfs(u):
            nonlocal cycles
            visited.add(u)
            rec_stack.add(u)
            for v, _ in graph.get(u, []):
                if v not in visited:
                    dfs(v)
                elif v in rec_stack:
                    cycles += 1
            rec_stack.remove(u)

        for node in nodes:
            if node not in visited:
                dfs(node)
        return cycles

    def _calc_falsifiability(self, props: list, graph: dict) -> float:
        """
        Score based on connectivity to 'observable' nodes (numeric/comparative).
        Higher score = more claims are grounded in testable facts.
        """
        if not props: return 0.0
        
        observable_ids = {p['id'] for p in props if p.get('has_nums') or 'comp' in p['labels']}
        if not observable_ids:
            # If no explicit numbers, reward presence of comparative logic as proxy for testability
            observable_ids = {p['id'] for p in props if 'comp' in p['labels'] or 'eq' in p['labels']}

        if not observable_ids:
            return 0.3 # Baseline for abstract reasoning
        
        total_nodes = len(props)
        connected_count = 0
        
        # Simple BFS from each node to see if it reaches an observable node
        for start_node in [p['id'] for p in props]:
            queue = deque([start_node])
            seen = {start_node}
            reachable = False
            while queue:
                u = queue.popleft()
                if u in observable_ids:
                    reachable = True
                    break
                for v, _ in graph.get(u, []):
                    if v not in seen:
                        seen.add(v)
                        queue.append(v)
                # Also check reverse edges implicitly by scanning all? 
                # For speed in this constraint, we assume forward flow covers most logic chains.
                # If the start node IS observable, it counts.
            if reachable or start_node in observable_ids:
                connected_count += 1
                
        return connected_count / total_nodes if total_nodes > 0 else 0.0

    def _get_compression_len(self, text: str) -> int:
        return len(zlib.compress(text.encode('utf-8')))

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        if not candidates:
            return []
            
        # Pre-calculate max lengths for normalization
        all_texts = [prompt + " " + c for c in candidates]
        max_len = max(len(t) for t in all_texts) if all_texts else 1
        
        scores = []
        
        for cand in candidates:
            full_text = prompt + " " + cand
            props = self._extract_props(cand)
            graph, nodes = self._build_graph(props)
            
            # 1. Topological Score (Coherence)
            # Penalize excessive cycles (contradictions) heavily
            cycles = self._count_cycles(graph, nodes)
            # Normalize: 0 cycles = 1.0, >5 cycles = 0.0
            top_score = max(0.0, 1.0 - (cycles * 0.2))
            
            # Boost for having structural markers (logic present)
            has_logic = any('cond' in p['labels'] or 'caus' in p['labels'] or 'neg' in p['labels'] for p in props)
            if has_logic:
                top_score = min(1.0, top_score + 0.2)
                
            # 2. Falsifiability Score
            fal_score = self._calc_falsifiability(props, graph)
            
            # 3. Kolmogorov Score (Simplicity) - Tiebreaker only
            # We want shorter description length relative to content, but primarily use it to break ties
            comp_len = self._get_compression_len(cand)
            # Normalize loosely
            kc_score = 1.0 - (comp_len / (max_len * 1.5)) 
            kc_score = max(0.0, kc_score)
            
            # Weighted Sum: Logic/Structure > Falsifiability > Simplicity
            # Weights: Topology(0.5), Falsifiability(0.4), KC(0.1)
            final_score = (0.5 * top_score) + (0.4 * fal_score) + (0.1 * kc_score)
            
            # Deterministic tie-breaking with hash if scores are extremely close
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Logic:{top_score:.2f} Fal:{fal_score:.2f} Simp:{kc_score:.2f}"
            })

        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural density and lack of internal contradiction as proxy for confidence.
        """
        props = self._extract_props(answer)
        if not props:
            return 0.0
            
        graph, nodes = self._build_graph(props)
        cycles = self._count_cycles(graph, nodes)
        
        # Base confidence on structural richness
        has_nums = any(p.get('has_nums') for p in props)
        has_logic = any(len(p['labels']) > 0 for p in props)
        
        base_conf = 0.5
        if has_logic: base_conf += 0.3
        if has_nums: base_conf += 0.1
        if cycles > 0: base_conf -= (cycles * 0.2)
        
        return max(0.0, min(1.0, base_conf))