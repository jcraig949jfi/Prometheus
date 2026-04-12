import re
import numpy as np
from typing import List, Dict, Tuple, Optional, Any

class ReasoningTool:
    """
    Implements a reasoning scorer based on Kolmogorov Complexity (via description length),
    Free Energy Principle (prediction error vs reference), and Sensitivity Analysis.
    
    Mechanism:
    1. Parses candidates into structural graphs (negations, comparatives, causals, numerics).
    2. Computes Description Length (C) as bit-length of structure + numeric precision.
    3. Computes Prediction Error (E) by comparing candidate graph to a synthetic 'gold' 
       derived from the prompt's explicit constraints (simulating a reference).
    4. Calculates Free Energy F = C + E.
    5. Performs Sensitivity Analysis (S) by perturbing numeric values and negations, 
       measuring the change in F.
    6. Scores as exp(-F) / (1 + S). Higher is better.
    """

    REL_TYPES = ['negation', 'comparative', 'conditional', 'causal', 'ordering', 'numeric']
    
    def __init__(self):
        self.epsilon = 0.1

    def _parse_graph(self, text: str) -> Tuple[Dict[int, List[Tuple[int, str, Optional[float]]]], List[float]]:
        """Extracts structural tuples (src, rel, dst) and numeric values."""
        text_lower = text.lower()
        nodes = {}
        edges = [] # (src_id, rel_type, payload)
        node_counter = 0
        
        def get_node_id(entity: str) -> int:
            nonlocal node_counter
            if entity not in nodes:
                nodes[entity] = node_counter
                node_counter += 1
            return nodes[entity]

        # 1. Numeric Extraction (value ± unit)
        nums = re.findall(r'(-?\d+\.?\d*)\s*(?:kg|m|s|%|units)?', text_lower)
        num_vals = []
        for n in nums:
            try:
                val = float(n)
                num_vals.append(val)
                src_id = get_node_id(f"num_{len(num_vals)}")
                edges.append((src_id, 'numeric', val))
            except ValueError:
                pass

        # 2. Negation
        if re.search(r'\b(not|no|never)\b', text_lower):
            src_id = get_node_id("_root_")
            edges.append((src_id, 'negation', None))

        # 3. Comparatives
        if re.search(r'(>|<|more than|less than|greater|smaller)', text_lower):
            src_id = get_node_id("_comp_")
            edges.append((src_id, 'comparative', None))

        # 4. Conditionals
        if re.search(r'\b(if|then|unless)\b', text_lower):
            src_id = get_node_id("_cond_")
            edges.append((src_id, 'conditional', None))

        # 5. Causal
        if re.search(r'\b(because|leads to|results in|causes)\b', text_lower):
            src_id = get_node_id("_cause_")
            edges.append((src_id, 'causal', None))

        # 6. Ordering
        if re.search(r'\b(before|after|first|last|next)\b', text_lower):
            src_id = get_node_id("_order_")
            edges.append((src_id, 'ordering', None))

        # Build Adjacency List
        adj = {i: [] for i in range(len(nodes))}
        for src, rel, payload in edges:
            if src in adj:
                adj[src].append((src, rel, payload)) # Simplified edge storage
                
        return adj, num_vals

    def _calc_description_length(self, num_vals: List[float]) -> float:
        """Approximates Kolmogorov complexity via bit-length of structure and numbers."""
        if not num_vals:
            return 1.0 # Base complexity for empty graph
        arr = np.array(num_vals, dtype=np.float32)
        # Pack bits to get raw length
        packed = np.packbits((arr.view(np.uint8).reshape(-1) > 0).astype(np.uint8))
        return float(len(packed) * 8) + len(num_vals) * 8 # Approx bits

    def _calc_prediction_error(self, cand_nums: List[float], prompt_nums: List[float]) -> float:
        """Computes squared error between candidate numbers and prompt-extracted numbers."""
        if not prompt_nums:
            return 0.0
        if not cand_nums:
            return 100.0 # High penalty for missing numbers if prompt has them
        
        # Align by index (simple approximation of graph matching)
        error = 0.0
        for i, p_val in enumerate(prompt_nums):
            if i < len(cand_nums):
                error += (cand_nums[i] - p_val) ** 2
            else:
                error += p_val ** 2 # Penalty for missing value
        return error

    def _compute_free_energy(self, text: str, ref_nums: List[float]) -> Tuple[float, List[float]]:
        _, nums = self._parse_graph(text)
        C = self._calc_description_length(nums)
        E = self._calc_prediction_error(nums, ref_nums)
        return C + E, nums

    def _sensitivity_analysis(self, text: str, base_F: float, ref_nums: List[float]) -> float:
        """Perturbs text slightly and measures change in Free Energy."""
        perturbations = []
        
        # 1. Numeric Perturbation
        nums = re.findall(r'(-?\d+\.?\d*)', text)
        for n in nums:
            try:
                val = float(n)
                delta = self.epsilon * max(abs(val), 1.0)
                new_val = val + delta
                perturbed_text = text.replace(n, str(round(new_val, 4)), 1)
                F_pert, _ = self._compute_free_energy(perturbed_text, ref_nums)
                perturbations.append(abs(F_pert - base_F))
            except ValueError:
                continue

        # 2. Negation Flip (Simulated by adding 'not' if missing, removing if present)
        # Simple approximation: just add a dummy negation token and re-score
        if 'not' not in text.lower():
            perturbed_text = text + " not."
            F_pert, _ = self._compute_free_energy(perturbed_text, ref_nums)
            perturbations.append(abs(F_pert - base_F))
        else:
            # Remove first 'not'
            perturbed_text = re.sub(r'\bnot\b', '', text, count=1)
            F_pert, _ = self._compute_free_energy(perturbed_text, ref_nums)
            perturbations.append(abs(F_pert - base_F))

        if not perturbations:
            return 0.0
        return float(np.mean(perturbations))

    def _extract_prompt_refs(self, prompt: str) -> List[float]:
        """Extracts numeric constraints from the prompt to serve as 'gold' reference."""
        nums = re.findall(r'(-?\d+\.?\d*)', prompt)
        return [float(n) for n in nums]

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        ref_nums = self._extract_prompt_refs(prompt)
        results = []

        for cand in candidates:
            # 1. Compute Base Free Energy
            F, nums = self._compute_free_energy(cand, ref_nums)
            
            # 2. Compute Sensitivity
            S = self._sensitivity_analysis(cand, F, ref_nums)
            
            # 3. Score: exp(-F) / (1 + S)
            # Lower F (complexity + error) and Lower S (sensitivity) -> Higher Score
            score = np.exp(-F) / (1.0 + S)
            
            # Normalize score to (0, 1] roughly
            score = float(min(1.0, max(0.0, score)))

            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"F={F:.2f}, S={S:.2f}, Nums={len(nums)}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the scoring mechanism."""
        ref_nums = self._extract_prompt_refs(prompt)
        F, _ = self._compute_free_energy(answer, ref_nums)
        S = self._sensitivity_analysis(answer, F, ref_nums)
        score = np.exp(-F) / (1.0 + S)
        return float(min(1.0, max(0.0, score)))