from dataclasses import field

"""
Topology x Statistical Mechanics x Metamorphic Testing Reasoning Tool

Builds constraint graphs from answers, evaluates via physics-inspired energy,
validates with metamorphic relations, and tracks state dynamics.
"""

import re
import numpy as np
import zlib
from itertools import combinations

class ReasoningTool:
    def __init__(self):
        self.rng = np.random.RandomState(42)
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        for cand in candidates:
            score = self._score_answer(prompt, cand)
            conf = self.confidence(prompt, cand)
            reasoning = f"Energy={score['energy']:.2f}, Beta1={score['beta1']}, Stability={score['stability']:.2f}"
            results.append({
                "candidate": cand,
                "score": score['total'],
                "reasoning": reasoning
            })
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        score = self._score_answer(prompt, answer)
        # Cap confidence based on stability and energy
        base_conf = 1.0 / (1.0 + np.exp(score['energy'] / 10.0))
        stability_factor = min(1.0, score['stability'])
        
        return min(0.85, meta_conf * base_conf * stability_factor)
    
    def _meta_confidence(self, prompt: str) -> float:
        prompt_lower = prompt.lower()
        
        # Presupposition detection
        if re.search(r'\b(have you stopped|have you quit|why did .+ fail|why did .+ stop)', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery \w+ .+ a \w+\b', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she)\b', prompt_lower) and 'who' in prompt_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .+ or .+\b', prompt_lower) and '?' in prompt:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', prompt_lower):
            if not re.search(r'\b(measure|criterion|metric|score)\b', prompt_lower):
                return 0.3
        
        return 1.0
    
    def _score_answer(self, prompt: str, answer: str) -> dict:
        # Build constraint graph
        graph = self._build_graph(answer)
        
        # Topological analysis
        beta1 = self._compute_beta1(graph)
        
        # Statistical mechanics energy
        energy = self._compute_energy(graph)
        
        # Dynamics tracking
        stability = self._track_dynamics(answer)
        
        # Metamorphic validation
        meta_penalty = self._metamorphic_test(answer, graph)
        
        # Numeric evaluation
        numeric_score = self._numeric_eval(prompt, answer)
        
        # NCD tiebreaker (max 15%)
        ncd_score = self._ncd_score(prompt, answer)
        
        # Weighted combination
        total = (
            0.4 * stability +
            0.25 * (1.0 / (1.0 + energy)) +
            0.15 * (1.0 / (1.0 + beta1)) +
            0.1 * numeric_score +
            0.1 * (1.0 - meta_penalty)
        )
        
        return {
            'total': total,
            'energy': energy,
            'beta1': beta1,
            'stability': stability,
            'meta_penalty': meta_penalty
        }
    
    def _build_graph(self, text: str) -> dict:
        tokens = re.findall(r'\b\w+\b', text.lower())
        
        nodes = []
        edges = []
        
        # Extract propositions and relations
        for i, tok in enumerate(tokens):
            if tok not in ['the', 'a', 'an', 'is', 'are', 'was', 'were']:
                nodes.append((i, tok))
        
        # Detect relations
        neg_pattern = r'\b(not|no|never)\s+(\w+)'
        for m in re.finditer(neg_pattern, text.lower()):
            edges.append(('NEG', m.group(2)))
        
        comp_pattern = r'(\w+)\s+(greater|less|more|fewer|equals?)\s+than\s+(\w+)'
        for m in re.finditer(comp_pattern, text.lower()):
            edges.append(('COMPARE', m.group(1), m.group(2), m.group(3)))
        
        cond_pattern = r'if\s+(\w+)\s+then\s+(\w+)'
        for m in re.finditer(cond_pattern, text.lower()):
            edges.append(('IMPLIES', m.group(1), m.group(2)))
        
        cause_pattern = r'(\w+)\s+(leads to|causes|before|after)\s+(\w+)'
        for m in re.finditer(cause_pattern, text.lower()):
            edges.append(('CAUSE', m.group(1), m.group(3)))
        
        return {'nodes': nodes, 'edges': edges}
    
    def _compute_beta1(self, graph: dict) -> int:
        nodes = graph['nodes']
        edges = graph['edges']
        
        if len(nodes) < 2:
            return 0
        
        # Build adjacency for cycle detection
        adj = {}
        for i, n1 in enumerate(nodes):
            adj[i] = set()
            for j, n2 in enumerate(nodes):
                if i != j:
                    for edge in edges:
                        if len(edge) >= 3 and n1[1] in edge and n2[1] in edge:
                            adj[i].add(j)
        
        # Count independent cycles (simplified)
        cycles = 0
        for i in adj:
            for j in adj.get(i, []):
                if i in adj.get(j, []):
                    cycles += 1
        
        return min(cycles // 2, 5)
    
    def _compute_energy(self, graph: dict) -> float:
        nodes = graph['nodes']
        edges = graph['edges']
        
        if not nodes:
            return 0.0
        
        # Initialize spins randomly
        spins = self.rng.choice([0, 1], size=len(nodes))
        
        # Mean-field iteration
        for _ in range(5):
            new_spins = spins.copy()
            for i in range(len(nodes)):
                local_field = 0.0
                for edge in edges:
                    if edge[0] == 'IMPLIES' and len(edge) == 3:
                        if nodes[i][1] in edge:
                            local_field += 0.5
                    elif edge[0] == 'NEG' and len(edge) == 2:
                        if nodes[i][1] == edge[1]:
                            local_field -= 1.0
                new_spins[i] = 1 if local_field > 0 else 0
            spins = new_spins
        
        # Compute energy
        energy = 0.0
        for edge in edges:
            if edge[0] == 'NEG':
                energy += 1.0
            elif edge[0] == 'COMPARE':
                energy += 0.5
        
        return energy
    
    def _track_dynamics(self, text: str) -> float:
        # Reservoir-style state tracking
        sentences = re.split(r'[.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.5
        
        # State vector
        state = np.zeros(10)
        trajectory = []
        
        for sent in sentences:
            # Update state based on sentence features
            update = np.zeros(10)
            update[0] = len(sent) / 100.0
            update[1] = sent.count(',') / 5.0
            update[2] = 1.0 if re.search(r'\bnot\b', sent.lower()) else 0.0
            update[3] = 1.0 if re.search(r'\d', sent) else 0.0
            update[4] = 1.0 if re.search(r'(if|then|because)', sent.lower()) else 0.0
            
            # Reservoir dynamics
            state = 0.7 * state + 0.3 * update
            trajectory.append(state.copy())
        
        # Measure stability
        if len(trajectory) < 2:
            return 0.5
        
        trajectory = np.array(trajectory)
        diffs = np.diff(trajectory, axis=0)
        stability = 1.0 / (1.0 + np.mean(np.linalg.norm(diffs, axis=1)))
        
        return min(1.0, stability)
    
    def _metamorphic_test(self, text: str, graph: dict) -> float:
        # Test synonym swap
        original_energy = self._compute_energy(graph)
        
        # Simple perturbation: swap "greater" and "less"
        perturbed = text.replace('greater', 'TEMP').replace('less', 'greater').replace('TEMP', 'less')
        perturbed_graph = self._build_graph(perturbed)
        perturbed_energy = self._compute_energy(perturbed_graph)
        
        # Expect energy change
        expected_change = abs(len(graph['edges']) - len(perturbed_graph['edges']))
        actual_change = abs(original_energy - perturbed_energy)
        
        penalty = abs(expected_change - actual_change) / max(1.0, expected_change + actual_change)
        return min(1.0, penalty)
    
    def _numeric_eval(self, prompt: str, answer: str) -> float:
        # Extract numbers and comparisons
        prompt_nums = [float(n) for n in re.findall(r'\d+\.?\d*', prompt)]
        answer_nums = [float(n) for n in re.findall(r'\d+\.?\d*', answer)]
        
        if not prompt_nums and not answer_nums:
            return 0.5
        
        # Check for comparison keywords
        if re.search(r'(greater|larger|more|bigger)', prompt.lower()):
            if answer_nums and prompt_nums:
                if any(a > p for a in answer_nums for p in prompt_nums):
                    return 1.0
        
        if re.search(r'(less|smaller|fewer)', prompt.lower()):
            if answer_nums and prompt_nums:
                if any(a < p for a in answer_nums for p in prompt_nums):
                    return 1.0
        
        return 0.5
    
    def _ncd_score(self, prompt: str, answer: str) -> float:
        c_prompt = len(zlib.compress(prompt.encode()))
        c_answer = len(zlib.compress(answer.encode()))
        c_combined = len(zlib.compress((prompt + answer).encode()))
        
        ncd = (c_combined - min(c_prompt, c_answer)) / max(c_prompt, c_answer)
        return 1.0 - min(1.0, ncd)