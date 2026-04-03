from typing import Any, Dict, Tuple

"""
Dialectic-NAS Reasoning Tool with Criticality and Dynamics Tracking

Combines:
- Logical parsing (propositions, operators, comparatives)
- Neural Architecture Search-style graph construction with dialectic synthesis
- Criticality-based susceptibility metric (perturbation sensitivity)
- Dynamical systems tracking (state evolution, trajectory stability)
"""

import re
import zlib
import hashlib
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple, Any


class ReasoningTool:
    def __init__(self):
        self.max_depth = 2
        self.graph_cache = {}
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        facts = self._extract_facts(prompt)
        results = []
        
        for cand in candidates:
            struct_score = self._compute_structural_score(prompt, cand, facts)
            comp_score = self._compute_computational_score(prompt, cand)
            dyn_score = self._compute_dynamics_score(prompt, cand, facts)
            ncd_score = self._compute_ncd(prompt, cand)
            
            # Weighted combination: dynamics 40%, structural 30%, computational 20%, NCD 10%
            final_score = 0.4*dyn_score + 0.3*struct_score + 0.2*comp_score + 0.1*ncd_score
            
            reasoning = f"dyn={dyn_score:.2f} struct={struct_score:.2f} comp={comp_score:.2f} ncd={ncd_score:.2f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        facts = self._extract_facts(prompt)
        graph, nodes = self._build_graph(answer, facts)
        
        if not graph:
            return 0.2
        
        sat = self._evaluate_graph(graph, nodes, facts)
        chi = self._compute_susceptibility(graph, nodes, facts)
        
        # Dynamics-based confidence: check trajectory stability
        stability = self._trajectory_stability(prompt, answer, facts)
        
        base_conf = min(0.95, sat / (max(len(facts), 1)) * (1.0 / (1.0 + chi)))
        dyn_conf = stability * base_conf
        
        return min(meta_conf, max(0.05, min(0.95, dyn_conf)))
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        # Presupposition detection
        if re.search(r"(have you|did you) (stop|quit|cease)", p_lower):
            return 0.25
        if re.search(r"why (did|does|is) \w+ (fail|stop|wrong)", p_lower):
            return 0.25
        
        # Scope ambiguity
        if re.search(r"every \w+ \w+ a \w+", p_lower):
            return 0.28
        
        # Pronoun ambiguity
        if re.search(r"(he|she|it|they) (was|is|were)", p_lower) and " who " in p_lower:
            return 0.27
        
        # False dichotomy
        if re.search(r"either \w+ or \w+", p_lower) and "?" in prompt:
            return 0.29
        
        # Subjectivity
        if re.search(r"\b(best|worst|favorite|prettiest|ugliest)\b", p_lower):
            return 0.26
        
        return 1.0
    
    def _extract_facts(self, text: str) -> Dict[str, bool]:
        facts = {}
        
        # Extract comparatives: X > Y, X < Y, X = Y
        for match in re.finditer(r"(\w+)\s*(>|<|>=|<=|=|equals?)\s*(\w+)", text):
            lhs, op, rhs = match.groups()
            facts[match.group(0)] = self._eval_comparison(lhs, op, rhs)
        
        # Extract negations
        for match in re.finditer(r"not\s+(\w+)", text, re.IGNORECASE):
            facts[f"NOT_{match.group(1)}"] = True
        
        # Extract simple propositions
        for match in re.finditer(r"(\w+)\s+(is|are)\s+(\w+)", text):
            facts[match.group(0)] = True
        
        return facts
    
    def _eval_comparison(self, lhs: str, op: str, rhs: str) -> bool:
        try:
            l_val = float(lhs)
            r_val = float(rhs)
            if op in [">", "greater"]: return l_val > r_val
            if op in ["<", "less"]: return l_val < r_val
            if op in [">=", "greater_equal"]: return l_val >= r_val
            if op in ["<=", "less_equal"]: return l_val <= r_val
            if op in ["=", "equals", "equal"]: return abs(l_val - r_val) < 1e-9
        except:
            return lhs == rhs if op in ["=", "equals", "equal"] else False
        return False
    
    def _build_graph(self, text: str, facts: Dict) -> Tuple[Dict, Dict]:
        nodes = {}
        graph = defaultdict(list)
        node_id = 0
        
        # Extract atomic propositions
        atoms = []
        for fact_key in facts.keys():
            if fact_key in text:
                atoms.append((fact_key, facts[fact_key]))
        
        if not atoms:
            return {}, {}
        
        # Build nodes for atoms
        for atom_text, atom_val in atoms:
            nodes[node_id] = {"type": "atom", "value": atom_val, "text": atom_text}
            node_id += 1
        
        # Dialectic synthesis: for pairs, create thesis-antithesis-synthesis
        if len(nodes) >= 2:
            pairs = [(i, i+1) for i in range(0, len(nodes)-1, 2)]
            for a_id, b_id in pairs:
                # Synthesis: XOR-like combination
                synth_val = (nodes[a_id]["value"] and not nodes[b_id]["value"]) or \
                           (not nodes[a_id]["value"] and nodes[b_id]["value"])
                nodes[node_id] = {"type": "synthesis", "value": synth_val, "children": [a_id, b_id]}
                graph[node_id] = [a_id, b_id]
                node_id += 1
        
        return dict(graph), nodes
    
    def _evaluate_graph(self, graph: Dict, nodes: Dict, facts: Dict) -> int:
        sat_count = sum(1 for n in nodes.values() if n.get("value", False))
        return sat_count
    
    def _compute_susceptibility(self, graph: Dict, nodes: Dict, facts: Dict) -> float:
        if not graph:
            return 0.0
        
        deltas = []
        base_sat = self._evaluate_graph(graph, nodes, facts)
        
        # Perturb each edge
        for parent, children in graph.items():
            for child in children:
                # Flip child value
                orig_val = nodes[child]["value"]
                nodes[child]["value"] = not orig_val
                new_sat = self._evaluate_graph(graph, nodes, facts)
                deltas.append(abs(new_sat - base_sat))
                nodes[child]["value"] = orig_val
        
        return np.var(deltas) if deltas else 0.0
    
    def _compute_structural_score(self, prompt: str, cand: str, facts: Dict) -> float:
        graph, nodes = self._build_graph(cand, facts)
        if not nodes:
            return 0.3
        
        sat = self._evaluate_graph(graph, nodes, facts)
        chi = self._compute_susceptibility(graph, nodes, facts)
        
        return sat / (1.0 + chi + 1e-6)
    
    def _compute_computational_score(self, prompt: str, cand: str) -> float:
        score = 0.0
        
        # Numeric comparison
        matches = re.findall(r"(\d+\.?\d*)\s*(>|<|=)\s*(\d+\.?\d*)", cand)
        for lhs, op, rhs in matches:
            if self._eval_comparison(lhs, op, rhs):
                score += 0.3
        
        # Arithmetic evaluation
        if re.search(r"\d+\s*[\+\-\*/]\s*\d+", cand):
            score += 0.2
        
        return min(1.0, score)
    
    def _compute_dynamics_score(self, prompt: str, cand: str, facts: Dict) -> float:
        # Model as state evolution: each premise updates state vector
        state = np.zeros(10)  # 10-dimensional state
        premise_order = list(facts.keys())
        
        if not premise_order:
            return 0.5
        
        # Compute trajectory under original order
        trajectory1 = self._evolve_state(state.copy(), premise_order, cand)
        
        # Compute trajectory under permuted order
        perm_order = premise_order[::-1]
        trajectory2 = self._evolve_state(state.copy(), perm_order, cand)
        
        # Stability: how similar are final states?
        stability = 1.0 / (1.0 + np.linalg.norm(trajectory1[-1] - trajectory2[-1]))
        
        # Convergence rate: Lyapunov-inspired
        convergence = self._convergence_rate(trajectory1)
        
        return 0.6 * stability + 0.4 * convergence
    
    def _evolve_state(self, state: np.ndarray, premises: List[str], answer: str) -> List[np.ndarray]:
        trajectory = [state.copy()]
        
        for i, premise in enumerate(premises):
            # Hash premise and answer to get update direction
            h = int(hashlib.md5(f"{premise}{answer}".encode()).hexdigest()[:8], 16)
            update = np.random.RandomState(h % (2**32)).randn(len(state)) * 0.3
            state = 0.8 * state + 0.2 * update  # Reservoir-like update
            trajectory.append(state.copy())
        
        return trajectory
    
    def _convergence_rate(self, trajectory: List[np.ndarray]) -> float:
        if len(trajectory) < 2:
            return 0.5
        
        # Measure how quickly state changes diminish
        diffs = [np.linalg.norm(trajectory[i+1] - trajectory[i]) 
                for i in range(len(trajectory)-1)]
        
        if not diffs:
            return 0.5
        
        # Exponential decay is good
        decay = diffs[-1] / (diffs[0] + 1e-6)
        return min(1.0, max(0.0, 1.0 - decay))
    
    def _trajectory_stability(self, prompt: str, answer: str, facts: Dict) -> float:
        state = np.zeros(8)
        premises = list(facts.keys())
        
        if not premises:
            return 0.5
        
        # Multiple random permutations
        trajectories = []
        for seed in range(3):
            np.random.seed(seed)
            perm = np.random.permutation(premises).tolist()
            traj = self._evolve_state(state.copy(), perm, answer)
            trajectories.append(traj[-1])
        
        # Measure spread of final states
        final_states = np.array(trajectories)
        spread = np.mean(np.std(final_states, axis=0))
        
        return 1.0 / (1.0 + spread)
    
    def _compute_ncd(self, text1: str, text2: str) -> float:
        c1 = len(zlib.compress(text1.encode()))
        c2 = len(zlib.compress(text2.encode()))
        c12 = len(zlib.compress((text1 + text2).encode()))
        ncd = (c12 - min(c1, c2)) / max(c1, c2)
        return max(0.0, 1.0 - ncd)