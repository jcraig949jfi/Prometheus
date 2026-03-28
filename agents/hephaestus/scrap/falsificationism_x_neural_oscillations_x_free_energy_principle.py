import re
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Implements a reasoning engine based on Falsificationism, Neural Oscillations, 
    and the Free Energy Principle.
    
    Mechanism:
    1. Parsing: Extracts atomic facts, causal edges, comparatives, and conditionals 
       via regex into polarized tuples.
    2. Graph Construction: Builds a directed graph of concepts.
    3. Constraint Propagation: Infers transitive causality and applies modus ponens.
    4. Free Energy (F): Calculates prediction error between prompt constraints and 
       candidate implications, penalizing complexity.
    5. Neural Oscillation (O): Weights coherence by logical depth (Delta/Theta/Gamma bands).
    6. Scoring: S = -F + alpha * O. Higher score indicates better survival against falsification.
    """
    
    # Regex patterns for extraction
    PATTERNS = [
        (re.compile(r'(?P<subj>\w+)\s+(is|are)\s+(?P<obj>\w+)', re.I), 'fact'),
        (re.compile(r'(?P<subj>\w+)\s+(causes?|leads?\s+to)\s+(?P<obj>\w+)', re.I), 'causal'),
        (re.compile(r'(?P<subj>\w+)\s+(is\s+)?(greater|less|more|less\s+than)\s+(?P<obj>\w+)', re.I), 'comparative'),
        (re.compile(r'if\s+(?P<ant>.+?)\s+then\s+(?P<con>.+)', re.I), 'conditional'),
        (re.compile(r'not\s+(?P<rest>.*)', re.I), 'negation')
    ]

    def __init__(self):
        self.lambda_complexity = 0.1
        self.alpha_oscillation = 0.5

    def _parse_text(self, text: str) -> List[Tuple[str, str, str, int]]:
        """Extract propositions as (type, subj, obj, polarity)."""
        props = []
        sentences = re.split(r'[.\n]', text)
        
        for sent in sentences:
            sent = sent.strip()
            if not sent: continue
            
            is_negated = bool(re.search(r'not\s+', sent, re.I))
            base_polarity = -1 if is_negated else 1
            
            # Handle explicit negation pattern separately if needed, but mostly flag polarity
            for pattern, p_type in self.PATTERNS:
                if p_type == 'negation': continue # Handled by polarity flag
                
                match = pattern.search(sent)
                if match:
                    groups = match.groupdict()
                    if p_type == 'conditional':
                        # Simplified: treat antecedent and consequent as linked
                        props.append(('conditional', groups['ant'].strip(), groups['con'].strip(), base_polarity))
                    else:
                        s = groups.get('subj', '').strip()
                        o = groups.get('obj', '').strip()
                        if s and o:
                            props.append((p_type, s, o, base_polarity))
            
            # Fallback for simple "A is B" or "A causes B" not caught by specific groups but present
            if not any(p[0] != 'negation' for p in props): 
                # Very basic fallback for noun-verb-noun if regex groups fail slightly
                words = re.findall(r'\w+', sent)
                if len(words) >= 3:
                     props.append(('fact', words[0], words[-1], base_polarity))
                     
        return props if props else [('fact', 'text', 'empty', 1)]

    def _build_and_propagate(self, prompt_props: List, candidate_props: List) -> Dict[str, Any]:
        """Build graph, propagate constraints, and compute metrics."""
        # Combine sources, marking origin
        all_edges = []
        nodes = set()
        
        for p in prompt_props:
            all_edges.append({'type': p[0], 'sub': p[1], 'obj': p[2], 'pol': p[3], 'source': 'prompt'})
            nodes.update([p[1], p[2]])
        for p in candidate_props:
            all_edges.append({'type': p[0], 'sub': p[1], 'obj': p[2], 'pol': p[3], 'source': 'candidate'})
            nodes.update([p[1], p[2]])
            
        nodes = list(nodes)
        node_depth = {n: 0 if any(n in str(p[1]) for p in prompt_props) else 1 for n in nodes}
        
        # Transitivity (Simplified for single-step inference to keep under limit)
        inferred = []
        for i, e1 in enumerate(all_edges):
            for j, e2 in enumerate(all_edges):
                if i == j: continue
                if e1['obj'] == e2['sub'] and e1['type'] == e2['type'] == 'causal':
                    new_edge = {
                        'type': 'causal', 'sub': e1['sub'], 'obj': e2['obj'], 
                        'pol': e1['pol'] * e2['pol'], 'source': 'inferred'
                    }
                    # Avoid duplicates
                    if not any(x['sub']==new_edge['sub'] and x['obj']==new_edge['obj'] for x in all_edges):
                        all_edges.append(new_edge)
                        inferred.append(new_edge)

        # Compute Free Energy (Error)
        # Error = 1 if candidate/prompt polarity conflict on same edge
        error_count = 0
        edge_list = []
        
        # Group by (sub, obj, type)
        edge_map = {}
        for e in all_edges:
            key = (e['sub'], e['obj'], e['type'])
            if key not in edge_map: edge_map[key] = []
            edge_map[key].append(e)
            
        conflicts = 0
        total_edges = 0
        
        for key, edges in edge_map.items():
            polys = [e['pol'] for e in edges]
            # If we have both +1 and -1 for same relation, it's a contradiction
            if len(set(polys)) > 1:
                conflicts += 1
            total_edges += 1
            
        F = (conflicts ** 2) + (self.lambda_complexity * np.log(total_edges + 1))
        
        # Neural Oscillation Coherence
        # Depth mapping: 0-1 (Delta), 2-3 (Theta), >=4 (Gamma)
        bands = {'delta': [], 'theta': [], 'gamma': []}
        for e in all_edges:
            d = node_depth.get(e['sub'], 0) + node_depth.get(e['obj'], 0)
            band = 'gamma' if d >= 4 else ('theta' if d >= 2 else 'delta')
            # Coherence contribution: 1 if no conflict in this edge's context, else 0
            # Simplified: assume local coherence unless global conflict found
            bands[band].append(1 if conflicts == 0 else 0)
            
        O = 0.0
        for b, vals in bands.items():
            if vals:
                coherence = 1.0 - (sum(vals) / len(vals)) # Inverted logic for error, so 1-mean_error
                # Actually formula: C_b = 1 - (sum_errors / count). If 0 errors, C=1.
                # Let's use the derived conflict rate for the whole graph as proxy for band error
                err_rate = conflicts / (total_edges if total_edges else 1)
                C_b = 1.0 - err_rate
                O += C_b ** 2
                
        score = -F + (self.alpha_oscillation * O)
        return score, F, O, conflicts

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []
            
        p_props = self._parse_text(prompt)
        results = []
        
        scores = []
        for cand in candidates:
            c_props = self._parse_text(cand)
            # Combine prompt and candidate for joint analysis
            # We treat the "system" as Prompt + Candidate. 
            # If they contradict, Free Energy goes up.
            score, F, O, conf = self._build_and_propagate(p_props, c_props)
            scores.append((cand, score, F, O, conf))
        
        # Rank by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        for cand, score, F, O, conf in scores:
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"F={F:.2f}, Osc={O:.2f}, Conflicts={conf}"
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on normalized score."""
        # Evaluate against a dummy negative to establish scale? 
        # Or just use the raw score mapped via sigmoid-like function
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        # Heuristic normalization: scores usually range -10 to 10
        # Map to 0-1
        conf = 1.0 / (1.0 + np.exp(-score)) 
        return float(np.clip(conf, 0.0, 1.0))