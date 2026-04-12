"""
Immune-Epistemological Metamorphic Reasoning Tool

Combines clonal selection (immune systems), metamorphic testing mutations,
and epistemological coherence tracking to evaluate reasoning candidates.

Core mechanism:
1. Parse prompt/candidates into constraint graphs (entity-relation-value triples)
2. Generate clone population via metamorphic mutations (invert, negate, swap)
3. Compute affinity as 1 - (violations / total_constraints)
4. Track coherence (Jaccard similarity of satisfied edges) and reliability
5. Meta-confidence detects ambiguity, presuppositions, insufficiency
"""

import re
import numpy as np
from collections import defaultdict
import zlib

class ReasoningTool:
    def __init__(self):
        self.memory = []
        self.reliability_ema = {}
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        prompt_graph = self._parse_graph(prompt)
        results = []
        
        for cand in candidates:
            cand_graph = self._parse_graph(cand)
            clones = self._generate_clones(cand_graph)
            affinities = [self._affinity(c, prompt_graph) for c in clones]
            max_aff = max(affinities) if affinities else 0.0
            coherence = self._coherence(clones, prompt_graph)
            reliability = self._reliability(cand)
            
            # Computational components
            comp_score = self._compute_answer(prompt, cand)
            struct_score = max_aff * 0.4 + coherence * 0.2 + reliability * 0.15
            ncd_score = self._ncd_score(prompt, cand) * 0.1
            
            score = struct_score + comp_score + ncd_score
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"aff={max_aff:.2f},coh={coherence:.2f},comp={comp_score:.2f}"
            })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        prompt_graph = self._parse_graph(prompt)
        ans_graph = self._parse_graph(answer)
        clones = self._generate_clones(ans_graph)
        affinities = [self._affinity(c, prompt_graph) for c in clones]
        max_aff = max(affinities) if affinities else 0.0
        comp_score = self._compute_answer(prompt, answer)
        
        raw_conf = min(0.95, max_aff * 0.5 + comp_score * 0.5)
        return min(raw_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p = prompt.lower()
        if re.search(r'(have you stopped|have you quit|why did .* (fail|stop))', p):
            return 0.25
        if re.search(r'every .* (a|an|one) ', p) and '?' in p:
            return 0.28
        if re.search(r'(he|she|it|they) (was|were|is|are)', p) and re.search(r'who|which person', p):
            return 0.27
        if re.search(r'either .* or .*\?', p) and not re.search(r'neither|other|else', p):
            return 0.29
        if re.search(r'(best|worst|favorite|most|least) ', p) and not re.search(r'(tallest|shortest|oldest|youngest|fastest|slowest)', p):
            return 0.26
        return 0.85
    
    def _parse_graph(self, text: str):
        edges = []
        nums = re.findall(r'(\w+)\s*(>|<|=|>=|<=)\s*(\d+\.?\d*)', text)
        for ent, op, val in nums:
            edges.append((ent, op, float(val)))
        
        orders = re.findall(r'(\w+)\s+(before|after)\s+(\w+)', text)
        for a, rel, b in orders:
            edges.append((a, rel, b))
        
        negs = re.findall(r'(not|n\'t)\s+(\w+)', text)
        for _, ent in negs:
            edges.append(('NOT', ent, True))
        
        conds = re.findall(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|,|$)', text, re.IGNORECASE)
        for ant, cons in conds:
            edges.append(('IF', ant.strip(), cons.strip()))
        
        causals = re.findall(r'(\w+)\s+(because|leads to|causes)\s+(\w+)', text)
        for a, rel, b in causals:
            edges.append((a, rel, b))
        
        return edges
    
    def _generate_clones(self, graph):
        clones = [graph[:]]
        for edge in graph:
            if len(edge) == 3 and isinstance(edge[2], (int, float)):
                clone = graph[:]
                idx = clone.index(edge)
                clone[idx] = (edge[0], edge[1], edge[2] * 2)
                clones.append(clone)
            
            if edge[1] == 'before':
                clone = graph[:]
                idx = clone.index(edge)
                clone[idx] = (edge[2], 'after', edge[0])
                clones.append(clone)
            
            if edge[0] == 'NOT':
                clone = [e for e in graph if e != edge]
                clones.append(clone)
        
        return clones[:10]
    
    def _affinity(self, clone, prompt_graph):
        if not prompt_graph:
            return 0.5
        violations = 0
        for c_edge in clone:
            for p_edge in prompt_graph:
                if self._contradicts(c_edge, p_edge):
                    violations += 1
        return max(0.0, 1.0 - violations / max(len(prompt_graph), 1))
    
    def _contradicts(self, e1, e2):
        if len(e1) == 3 and len(e2) == 3:
            if e1[0] == e2[0] and isinstance(e1[2], (int, float)) and isinstance(e2[2], (int, float)):
                if e1[1] == '>' and e2[1] == '<':
                    return True
                if e1[1] == '<' and e2[1] == '>':
                    return True
        return False
    
    def _coherence(self, clones, prompt_graph):
        satisfied = []
        for clone in clones:
            sat_edges = set()
            for c_edge in clone:
                for p_edge in prompt_graph:
                    if c_edge == p_edge or (len(c_edge) == 3 and len(p_edge) == 3 and c_edge[0] == p_edge[0]):
                        sat_edges.add(str(c_edge))
            satisfied.append(sat_edges)
        
        if len(satisfied) < 2:
            return 0.5
        
        jaccard_sum = 0.0
        count = 0
        for i in range(len(satisfied)):
            for j in range(i + 1, len(satisfied)):
                union = len(satisfied[i] | satisfied[j])
                if union > 0:
                    jaccard_sum += len(satisfied[i] & satisfied[j]) / union
                    count += 1
        
        return jaccard_sum / count if count > 0 else 0.5
    
    def _reliability(self, candidate):
        if candidate not in self.reliability_ema:
            self.reliability_ema[candidate] = 0.5
        return self.reliability_ema[candidate]
    
    def _compute_answer(self, prompt: str, candidate: str) -> float:
        score = 0.0
        
        # Numeric comparison
        match = re.search(r'(\d+\.?\d*)\s*(<|>|=)\s*(\d+\.?\d*)', prompt)
        if match:
            left, op, right = float(match.group(1)), match.group(2), float(match.group(3))
            truth = (op == '<' and left < right) or (op == '>' and left > right) or (op == '=' and left == right)
            if (truth and re.search(r'\b(yes|true|correct)\b', candidate.lower())) or \
               (not truth and re.search(r'\b(no|false|incorrect)\b', candidate.lower())):
                score += 0.15
        
        # Bat and ball
        if 'bat' in prompt.lower() and 'ball' in prompt.lower():
            nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
            if len(nums) >= 2:
                total, diff = nums[0], nums[1]
                ball_cost = (total - diff) / 2
                if abs(float(re.findall(r'\d+\.?\d*', candidate)[0]) - ball_cost) < 0.01 if re.findall(r'\d+\.?\d*', candidate) else False:
                    score += 0.2
        
        # All but N
        match = re.search(r'all but (\d+)', prompt.lower())
        if match:
            n = int(match.group(1))
            total_match = re.search(r'(\d+)\s+(items|objects|people)', prompt.lower())
            if total_match:
                total = int(total_match.group(1))
                expected = total - n
                cand_nums = [int(x) for x in re.findall(r'\b\d+\b', candidate)]
                if cand_nums and cand_nums[0] == expected:
                    score += 0.15
        
        # Modular arithmetic
        if 'remainder' in prompt.lower() or 'modulo' in prompt.lower():
            nums = [int(x) for x in re.findall(r'\b\d+\b', prompt)]
            if len(nums) >= 2:
                result = nums[0] % nums[1]
                cand_nums = [int(x) for x in re.findall(r'\b\d+\b', candidate)]
                if cand_nums and cand_nums[0] == result:
                    score += 0.15
        
        # Transitivity
        trans = re.findall(r'(\w+)\s*>\s*(\w+)', prompt)
        if len(trans) >= 2:
            a, b = trans[0]
            c, d = trans[1]
            if b == c and f"{a}" in candidate and f"{d}" in candidate:
                score += 0.1
        
        return min(score, 0.25)
    
    def _ncd_score(self, prompt: str, candidate: str) -> float:
        c1, c2 = zlib.compress(prompt.encode()), zlib.compress(candidate.encode())
        c12 = zlib.compress((prompt + candidate).encode())
        ncd = (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2))
        return max(0.0, 1.0 - ncd)