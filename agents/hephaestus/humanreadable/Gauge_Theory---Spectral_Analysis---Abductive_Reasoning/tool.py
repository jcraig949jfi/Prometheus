from typing import Dict, Tuple

"""
Gauge-Spectral-Abductive Reasoning Tool

Core mechanism:
1. Parse propositions into a directed graph with typed edges (negation, comparison, causal, etc.)
2. Assign U(1) gauge phases: each edge type adds a fixed phase shift
3. Measure spectral coherence: FFT on node phases; low-frequency = coherent, high leakage = contradictory
4. Count abductive assumptions needed to validate each relation
5. Combine with computational solvers for numbers, algebra, logic

Metacognition: Detect presuppositions, ambiguity, false dichotomies -> low confidence
"""

import re
import numpy as np
from typing import List, Dict, Tuple
import zlib


class ReasoningTool:
    def __init__(self):
        # Gauge phases for different relation types
        self.PHASE_MAP = {
            'neg': np.pi,           # negation
            'lt': np.pi/2,          # less than
            'gt': -np.pi/2,         # greater than
            'implies': 0.0,         # conditional
            'cause': -np.pi/4,      # causal
            'eq': 0.0,              # equality
            'before': np.pi/3,      # temporal
            'after': -np.pi/3,
        }
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reasoning = self._score_candidate(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        score, _ = self._score_candidate(prompt, answer)
        base_conf = min(0.95, score)
        return min(meta_conf, base_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p = prompt.lower()
        # Presupposition traps
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))\b', p):
            return 0.15
        # Scope ambiguity
        if re.search(r'\bevery .+ (a|an|the) \b', p):
            return 0.25
        # Pronoun ambiguity with explicit "who" question
        if re.search(r'\b(he|she|they)\b', p) and re.search(r'\bwho\b', p):
            return 0.25
        # False dichotomy
        if re.search(r'\beither .+ or .+\?', p) and not re.search(r'\b(only|must)\b', p):
            return 0.3
        # Subjective without criteria
        if re.search(r'\b(best|worst|favorite|better)\b', p) and not re.search(r'\b(more|most|less|least|faster|slower|cheaper)\b', p):
            return 0.3
        # Unanswerable markers
        if re.search(r'\b(cannot be determined|not enough information|insufficient)\b', p):
            return 0.2
        return 1.0
    
    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        # Try computational solvers first
        comp_score, comp_reason = self._computational_solve(prompt, candidate)
        if comp_score > 0:
            struct_score = self._gauge_spectral_score(prompt, candidate)
            ncd_score = self._ncd_score(prompt, candidate)
            final = 0.5 * comp_score + 0.35 * struct_score + 0.15 * ncd_score
            return final, f"Computational({comp_score:.2f})+Spectral({struct_score:.2f})+{comp_reason}"
        
        # Fallback to gauge-spectral
        struct_score = self._gauge_spectral_score(prompt, candidate)
        ncd_score = self._ncd_score(prompt, candidate)
        final = 0.7 * struct_score + 0.3 * ncd_score
        return final, f"Spectral({struct_score:.2f})+NCD({ncd_score:.2f})"
    
    def _computational_solve(self, prompt: str, candidate: str) -> Tuple[float, str]:
        # Numeric comparison
        nums_p = re.findall(r'\d+\.?\d*', prompt)
        nums_c = re.findall(r'\d+\.?\d*', candidate)
        if len(nums_p) >= 2 and len(nums_c) >= 1:
            if re.search(r'\b(greater|larger|more than|bigger)\b', prompt.lower()):
                vals = [float(n) for n in nums_p[:2]]
                cand_val = float(nums_c[0])
                if abs(cand_val - max(vals)) < 0.01:
                    return 0.95, "NumericMax"
            elif re.search(r'\b(less|smaller|fewer)\b', prompt.lower()):
                vals = [float(n) for n in nums_p[:2]]
                cand_val = float(nums_c[0])
                if abs(cand_val - min(vals)) < 0.01:
                    return 0.95, "NumericMin"
        
        # Bat-and-ball algebra: X + Y = A, X - Y = B -> X = (A+B)/2
        match = re.search(r'(\d+\.?\d*).+together.+(\d+\.?\d*).+more than', prompt)
        if match:
            total, diff = float(match.group(1)), float(match.group(2))
            expected = (total + diff) / 2
            if nums_c and abs(float(nums_c[0]) - expected) < 0.01:
                return 0.95, "BatBall"
        
        # All-but-N pattern
        if re.search(r'all but (\d+)', prompt.lower()):
            match = re.search(r'all but (\d+)', prompt.lower())
            n = int(match.group(1))
            total_match = re.search(r'(\d+)', prompt)
            if total_match:
                total = int(total_match.group(1))
                expected = total - n
                if nums_c and abs(float(nums_c[0]) - expected) < 0.01:
                    return 0.95, "AllButN"
        
        # Negation logic
        if re.search(r'\bnot\b.*\b(true|false|yes|no)\b', prompt.lower()):
            if 'not true' in prompt.lower() and 'false' in candidate.lower():
                return 0.9, "Negation"
            if 'not false' in prompt.lower() and 'true' in candidate.lower():
                return 0.9, "Negation"
        
        return 0.0, ""
    
    def _gauge_spectral_score(self, prompt: str, candidate: str) -> float:
        text = prompt + " " + candidate
        graph, abductive_cost = self._build_gauge_graph(text)
        
        if len(graph) < 2:
            return 0.5
        
        # Assign phases via DFS
        phases = self._assign_gauge_phases(graph)
        
        # Spectral coherence
        if len(phases) < 2:
            spectral_coherence = 0.5
        else:
            cos_phases = np.cos(phases)
            sin_phases = np.sin(phases)
            fft_cos = np.fft.fft(cos_phases)
            fft_sin = np.fft.fft(sin_phases)
            power = np.abs(fft_cos)**2 + np.abs(fft_sin)**2
            total_power = np.sum(power)
            if total_power > 0:
                leakage = np.sum(power[1:]) / total_power
                spectral_coherence = 1 - leakage
            else:
                spectral_coherence = 0.5
        
        # Abductive penalty
        abductive_score = np.exp(-0.5 * abductive_cost)
        
        # Combined
        return 0.6 * spectral_coherence + 0.4 * abductive_score
    
    def _build_gauge_graph(self, text: str) -> Tuple[List[Tuple[int, int, str]], int]:
        tokens = re.findall(r'\b\w+\b', text.lower())
        nodes = []
        edges = []
        abductive_cost = 0
        
        # Extract propositions (simplified: key phrases)
        for i, token in enumerate(tokens):
            if token in ['not', 'no', 'never']:
                if i+1 < len(tokens):
                    edges.append((i, i+1, 'neg'))
            elif token in ['greater', 'more', 'larger', 'bigger']:
                if i+1 < len(tokens):
                    edges.append((i, i+1, 'gt'))
            elif token in ['less', 'fewer', 'smaller']:
                if i+1 < len(tokens):
                    edges.append((i, i+1, 'lt'))
            elif token in ['because', 'causes', 'leads']:
                if i > 0 and i+1 < len(tokens):
                    edges.append((i-1, i+1, 'cause'))
            elif token in ['if', 'then', 'implies']:
                if i > 0 and i+1 < len(tokens):
                    edges.append((i-1, i+1, 'implies'))
            elif token in ['before']:
                if i > 0 and i+1 < len(tokens):
                    edges.append((i-1, i+1, 'before'))
            elif token in ['after']:
                if i > 0 and i+1 < len(tokens):
                    edges.append((i-1, i+1, 'after'))
        
        # Count abductive assumptions (missing intermediate nodes)
        for src, tgt, rel in edges:
            if abs(tgt - src) > 2:
                abductive_cost += abs(tgt - src) - 2
        
        return edges, abductive_cost
    
    def _assign_gauge_phases(self, graph: List[Tuple[int, int, str]]) -> np.ndarray:
        if not graph:
            return np.array([0.0])
        
        # Find all nodes
        nodes = set()
        for src, tgt, _ in graph:
            nodes.add(src)
            nodes.add(tgt)
        nodes = sorted(nodes)
        
        # Phase assignment
        phase_dict = {nodes[0]: 0.0}
        visited = {nodes[0]}
        
        # DFS
        stack = [nodes[0]]
        while stack:
            node = stack.pop()
            for src, tgt, rel in graph:
                if src == node and tgt not in visited:
                    phase_shift = self.PHASE_MAP.get(rel, 0.0)
                    phase_dict[tgt] = (phase_dict[node] + phase_shift) % (2 * np.pi)
                    visited.add(tgt)
                    stack.append(tgt)
        
        # Convert to array
        phases = np.array([phase_dict.get(n, 0.0) for n in nodes])
        return phases
    
    def _ncd_score(self, prompt: str, candidate: str) -> float:
        def ncd(s1, s2):
            c1, c2, c12 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode())), len(zlib.compress((s1+s2).encode()))
            return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
        
        dist = ncd(prompt, candidate)
        return max(0, 1 - dist)