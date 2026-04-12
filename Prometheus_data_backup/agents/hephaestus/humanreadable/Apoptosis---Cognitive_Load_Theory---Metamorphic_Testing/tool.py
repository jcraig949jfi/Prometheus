from typing import Dict, List, Set, Tuple

import re
import zlib
from typing import NamedTuple, List, Dict, Set, Tuple
import math

class Prop(NamedTuple):
    id: int
    polarity: int  # +1 or -1
    pred: str
    args: Tuple[str, ...]

class ReasoningTool:
    """
    Apoptotic Metamorphic Constraint Scorer (AMCS).
    
    Combines constraint propagation, apoptotic pruning, and cognitive load theory
    to score candidate answers. Extracts logical relations (IMPLIES, ORDER, CAUSE,
    COMPARE) from prompt text, builds a constraint graph, and scores candidates by:
    1. Base consistency - violation counting via BFS entailment
    2. Apoptotic factor - iterative removal of low-viability candidates
    3. Cognitive load - penalty for exceeding working memory (K=4 props)
    """
    
    def __init__(self):
        self.K = 4  # Working memory capacity
        self.lambda_apo = 0.5
        self.alpha_load = 0.3
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # Parse prompt to extract constraints
        prompt_props, prompt_graph = self._parse_text(prompt)
        
        # Score each candidate
        results = []
        for cand in candidates:
            cand_props, cand_graph = self._parse_text(cand)
            combined_graph = self._merge_graphs(prompt_graph, cand_graph)
            
            base_score = self._base_consistency(cand_props, combined_graph, prompt_props)
            load_score = self._cognitive_load(cand_props)
            
            # Numeric evaluation
            numeric_score = self._numeric_eval(prompt, cand)
            
            # NCD tiebreaker (max 15%)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Weighted combination
            score = 0.5 * base_score + 0.2 * numeric_score + 0.15 * load_score + 0.15 * ncd_score
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"base={base_score:.2f}, numeric={numeric_score:.2f}, load={load_score:.2f}"
            })
        
        # Apoptotic pruning
        results = self._apoptotic_pruning(results)
        
        # Normalize and sort
        if results:
            max_s = max(r["score"] for r in results)
            min_s = min(r["score"] for r in results)
            for r in results:
                r["score"] = (r["score"] - min_s) / max(0.01, max_s - min_s)
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        # Meta-confidence: check for ambiguity/unanswerability
        meta_conf = self._meta_confidence(prompt)
        
        # Structural confidence
        prompt_props, prompt_graph = self._parse_text(prompt)
        ans_props, ans_graph = self._parse_text(answer)
        combined_graph = self._merge_graphs(prompt_graph, ans_graph)
        
        base_score = self._base_consistency(ans_props, combined_graph, prompt_props)
        numeric_score = self._numeric_eval(prompt, answer)
        
        struct_conf = 0.6 * base_score + 0.4 * numeric_score
        
        # Cap by meta-confidence
        return min(meta_conf, struct_conf)
    
    def _parse_text(self, text: str) -> Tuple[List[Prop], Dict]:
        text = text.lower()
        props = []
        graph = {}
        pid = 0
        
        # Extract negations
        neg_pattern = r'\b(not|no|never|neither)\s+(\w+)'
        for m in re.finditer(neg_pattern, text):
            props.append(Prop(pid, -1, m.group(2), ()))
            graph[pid] = set()
            pid += 1
        
        # Extract comparatives (numeric)
        comp_pattern = r'(\d+\.?\d*)\s*(>|<|>=|<=|=)\s*(\d+\.?\d*)'
        for m in re.finditer(comp_pattern, text):
            props.append(Prop(pid, 1, 'COMPARE', (m.group(1), m.group(2), m.group(3))))
            graph[pid] = set()
            pid += 1
        
        # Extract conditionals
        cond_pattern = r'if\s+(.+?)\s+then\s+(.+?)[\.\,\;]'
        for m in re.finditer(cond_pattern, text):
            p1 = Prop(pid, 1, 'cond_ant', (m.group(1).strip(),))
            p2 = Prop(pid+1, 1, 'cond_cons', (m.group(2).strip(),))
            props.extend([p1, p2])
            graph[pid] = {(pid+1, 'IMPLIES', 2)}
            graph[pid+1] = set()
            pid += 2
        
        # Extract causal
        cause_pattern = r'because\s+(.+?),\s+(.+?)[\.\;]'
        for m in re.finditer(cause_pattern, text):
            p1 = Prop(pid, 1, 'cause', (m.group(1).strip(),))
            p2 = Prop(pid+1, 1, 'effect', (m.group(2).strip(),))
            props.extend([p1, p2])
            graph[pid] = {(pid+1, 'CAUSE', 1)}
            graph[pid+1] = set()
            pid += 2
        
        # Extract ordering
        order_pattern = r'(before|after|first|second|earlier|later)'
        if re.search(order_pattern, text):
            props.append(Prop(pid, 1, 'ORDER', ()))
            graph[pid] = set()
            pid += 1
        
        # Simple predications
        pred_pattern = r'(\w+)\s+(is|are|was|were)\s+(\w+)'
        for m in re.finditer(pred_pattern, text):
            props.append(Prop(pid, 1, m.group(2), (m.group(1), m.group(3))))
            graph[pid] = set()
            pid += 1
        
        return props, graph
    
    def _merge_graphs(self, g1: Dict, g2: Dict) -> Dict:
        merged = {}
        for k, v in g1.items():
            merged[k] = v.copy()
        offset = max(g1.keys()) + 1 if g1 else 0
        for k, v in g2.items():
            merged[k + offset] = {(nid + offset, rel, w) for nid, rel, w in v}
        return merged
    
    def _base_consistency(self, cand_props: List[Prop], graph: Dict, prompt_props: List[Prop]) -> float:
        if not cand_props:
            return 0.5
        
        violations = 0
        # Check for contradictions
        for cp in cand_props:
            for pp in prompt_props:
                if cp.pred == pp.pred and cp.polarity != pp.polarity:
                    violations += 1
        
        # Check IMPLIES chains
        for pid, edges in graph.items():
            for target, rel, _ in edges:
                if rel == 'IMPLIES' and pid < len(cand_props) and target < len(cand_props):
                    if cand_props[pid].polarity == 1 and cand_props[target].polarity == -1:
                        violations += 1
        
        return 1.0 - (violations / max(1, len(cand_props)))
    
    def _cognitive_load(self, props: List[Prop]) -> float:
        excess = max(0, len(props) - self.K)
        return 1.0 / (1.0 + self.alpha_load * excess)
    
    def _apoptotic_pruning(self, results: List[Dict]) -> List[Dict]:
        if len(results) <= 1:
            return results
        
        removed = 0
        while len(results) > 1:
            results_sorted = sorted(results, key=lambda x: x["score"])
            avg_before = sum(r["score"] for r in results) / len(results)
            avg_after = sum(r["score"] for r in results[1:]) / (len(results) - 1)
            
            if avg_after > avg_before:
                results = results_sorted[1:]
                removed += 1
            else:
                break
        
        apo_factor = math.exp(-self.lambda_apo * removed)
        for r in results:
            r["score"] *= apo_factor
        
        return results
    
    def _numeric_eval(self, prompt: str, candidate: str) -> float:
        # Extract numbers from prompt and candidate
        p_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        c_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
        
        # Check comparisons
        comp_match = re.search(r'(\d+\.?\d*)\s*(>|<|>=|<=)\s*(\d+\.?\d*)', prompt)
        if comp_match:
            a, op, b = float(comp_match.group(1)), comp_match.group(2), float(comp_match.group(3))
            expected = (a > b if op == '>' else a < b if op == '<' else a >= b if op == '>=' else a <= b)
            
            # Check if candidate affirms this
            if ('yes' in candidate.lower() or 'true' in candidate.lower()) and expected:
                return 1.0
            if ('no' in candidate.lower() or 'false' in candidate.lower()) and not expected:
                return 1.0
        
        # Numeric overlap
        if p_nums and c_nums:
            overlap = len(set(p_nums) & set(c_nums))
            return overlap / max(len(p_nums), len(c_nums))
        
        return 0.5
    
    def _meta_confidence(self, prompt: str) -> float:
        text = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .+ fail|why did .+ stop)', text):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'\bevery\s+\w+.*\ba\s+\w+', text):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they)\s+(was|is|said)', text) and 'who' in text:
            return 0.25
        
        # False dichotomy
        if re.search(r'\b(either\s+\w+\s+or\s+\w+)', text):
            return 0.25
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful|ugliest)\b', text) and not re.search(r'(most|least|highest|lowest)', text):
            return 0.25
        
        # Unanswerable markers
        if re.search(r'(cannot be determined|not enough information|impossible to tell)', text):
            return 0.2
        
        return 0.85
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2), 1)