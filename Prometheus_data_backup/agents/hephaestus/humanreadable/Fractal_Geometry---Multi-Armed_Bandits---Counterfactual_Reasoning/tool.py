import re
import math
import numpy as np
from collections import deque
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning tool combining Fractal Geometry, Multi-Armed Bandits, and Counterfactuals.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (numeric, conditional, causal, comparative) into a graph.
    2. Fractal Weight: Estimates graph dimension via box-counting on the adjacency matrix to weight complexity.
    3. Counterfactual Reward: Simulates 'do-operations' by toggling proposition truth values and counting constraint violations.
    4. Bandit Selection: Uses UCB1 to select the best candidate answer based on counterfactual stability.
    5. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence.
    """

    def __init__(self):
        self.regex_num = re.compile(r'-?\d+(?:\.\d+)?')
        self.regex_cond = re.compile(r'if\s+(.+?)\s+(?:then|,)?\s+(.+?)', re.IGNORECASE)
        self.regex_comp = re.compile(r'(.+?)\s+(greater than|less than|more than|fewer than|equals|is equal to)\s+(.+?)', re.IGNORECASE)
        self.regex_causal = re.compile(r'(.+?)\s+(causes|leads to|results in|precedes|follows)\s+(.+?)', re.IGNORECASE)
        self.presupposition_triggers = ["have you stopped", "have you quit", "why did", "why does", "when did"]
        self.ambiguity_triggers = ["every x", "x told y he", "either a or b", "best", "worst", "favorite"]

    def _extract_numbers(self, text: str) -> List[float]:
        return [float(x) for x in self.regex_num.findall(text)]

    def _parse_propositions(self, text: str) -> Tuple[List[dict], np.ndarray]:
        """Parses text into propositions and builds adjacency matrix."""
        props = []
        edges = []
        text_lower = text.lower()
        
        # Simple tokenization for propositions
        words = re.split(r'[,\s]+', text_lower)
        prop_id = 0
        
        # Extract specific structures
        # 1. Numerical facts
        nums = self._extract_numbers(text)
        if len(nums) >= 2:
            props.append({'type': 'numeric', 'val': nums, 'text': text})
            prop_id += 1
            
        # 2. Conditionals
        for m in self.regex_cond.finditer(text):
            props.append({'type': 'conditional', 'ant': m.group(1), 'cons': m.group(2), 'text': text})
            edges.append((prop_id-1 if prop_id > 0 else 0, prop_id))
            prop_id += 1
            
        # 3. Comparatives
        for m in self.regex_comp.finditer(text):
            props.append({'type': 'comparative', 'l': m.group(1), 'op': m.group(2), 'r': m.group(3), 'text': text})
            prop_id += 1
            
        # 4. Causal
        for m in self.regex_causal.finditer(text):
            props.append({'type': 'causal', 'cause': m.group(1), 'eff': m.group(2), 'text': text})
            prop_id += 1

        # Fallback if no structure found but text exists
        if not props and text.strip():
            props.append({'type': 'atomic', 'text': text})
            prop_id = 1

        n = max(len(props), 1)
        A = np.zeros((n, n), dtype=np.uint8)
        
        # Build adjacency from logical flow (simplified transitivity)
        for i in range(n-1):
            A[i, i+1] = 1
            
        # Add extracted edges
        for u, v in edges:
            if u < n and v < n:
                A[u, v] = 1
                
        return props, A

    def _fractal_dimension(self, A: np.ndarray) -> float:
        """Approximates Hausdorff dimension via box-counting on graph reachability."""
        if A.shape[0] == 0:
            return 1.0
            
        n = A.shape[0]
        if n == 1:
            return 1.0

        # Compute reachability via boolean matrix powers (simplified box counting)
        # Box size epsilon ~ 1/k hops. 
        # We simulate scales by k-hop reachability
        R = A.astype(bool)
        curr = A.astype(bool)
        
        scales = []
        counts = []
        
        # Max hops to consider
        K = min(5, n)
        
        for k in range(1, K+1):
            if k > 1:
                curr = np.logical_or(curr, np.dot(curr, A))
            
            # Count connected components or covered nodes as proxy for N(epsilon)
            # Here: number of nodes reachable from any node within k hops
            # Simplified: Count non-zero rows in reachability matrix
            reachable = np.any(curr, axis=1)
            n_boxes = np.sum(reachable) + 1 # +1 for isolated
            
            if n_boxes > 0:
                epsilon = 1.0 / (k + 1)
                scales.append(np.log(1.0/epsilon))
                counts.append(np.log(max(n_boxes, 1)))

        if len(scales) < 2:
            return 1.0
            
        # Linear fit for dimension
        try:
            slope, _ = np.polyfit(scales, counts, 1)
            return max(0.1, min(5.0, slope)) # Clamp dimension
        except:
            return 1.0

    def _evaluate_counterfactuals(self, prompt: str, candidate: str, props: List[dict], A: np.ndarray) -> float:
        """Evaluates candidate by simulating constraint violations in counterfactual worlds."""
        if not props:
            return 0.0
            
        total_violations = 0
        worlds = 0
        
        # Base truth values (heuristic: assume text implies truth)
        base_truth = [True] * len(props)
        
        # Generate counterfactuals by flipping one proposition at a time
        for i in range(len(props)):
            world_truth = base_truth.copy()
            world_truth[i] = not world_truth[i] # Do-operation: flip truth
            worlds += 1
            
            violations = 0
            
            # Check consistency with candidate
            cand_nums = self._extract_numbers(candidate)
            prompt_nums = self._extract_numbers(prompt)
            
            # 1. Numeric Consistency
            if cand_nums and prompt_nums:
                # Simple check: if candidate contradicts explicit prompt numbers
                # This is a simplification of full constraint propagation
                if len(cand_nums) == len(prompt_nums):
                    for cn, pn in zip(cand_nums, prompt_nums):
                        if abs(cn - pn) > 1e-6: # Strict equality for exact numbers
                             # Only violate if the proposition wasn't the one flipped (causal chain)
                             if i != 0: 
                                 violations += 1

            # 2. Logical Consistency (Conditional)
            for j, p in enumerate(props):
                if p['type'] == 'conditional':
                    # If antecedent true and consequent false in this world -> violation
                    # Simplified: assume antecedent is prop[j], consequent is prop[j+1] if exists
                    if j < len(world_truth) - 1:
                        if world_truth[j] and not world_truth[j+1]:
                            violations += 1
                            
            total_violations += violations

        # Reward = negative weighted violations
        D = self._fractal_dimension(A)
        w = D / (D + 1.0)
        
        if worlds == 0:
            return 0.0
            
        mean_violations = total_violations / worlds
        return -w * mean_violations

    def _bandit_select(self, prompt: str, candidates: List[str], props: List[dict], A: np.ndarray) -> List[Dict]:
        """Runs UCB1 bandit to rank candidates."""
        if not candidates:
            return []
            
        T = len(candidates) * 2  # Number of pulls
        n_arms = len(candidates)
        
        mu = np.zeros(n_arms)
        counts = np.zeros(n_arms)
        rewards = [] # Store computed rewards to avoid re-calc if needed, but here we calc on pull
        
        # Pre-calculate rewards (deterministic environment for this tool)
        true_rewards = []
        for c in candidates:
            r = self._evaluate_counterfactuals(prompt, c, props, A)
            
            # Add constructive computation bonus
            cand_nums = self._extract_numbers(c)
            prompt_nums = self._extract_numbers(prompt)
            
            # Heuristic: If prompt has math ops, reward correct calculation
            if "plus" in prompt or "+" in prompt or "sum" in prompt:
                if cand_nums and prompt_nums:
                    if abs(sum(cand_nums) - sum(prompt_nums)) < 1e-6:
                        r += 2.0 # Strong reward for correct sum
            
            true_rewards.append(r)

        results = []
        for t in range(1, T + 1):
            ucb_values = []
            for i in range(n_arms):
                if counts[i] == 0:
                    ucb_values.append(float('inf'))
                else:
                    ucb = mu[i] + math.sqrt(2 * math.log(t) / counts[i])
                    ucb_values.append(ucb)
            
            arm = int(np.argmax(ucb_values))
            
            # Pull arm
            reward = true_rewards[arm]
            counts[arm] += 1
            mu[arm] += (reward - mu[arm]) / counts[arm]
            
        # Rank by empirical mean
        ranked_indices = np.argsort(mu)[::-1]
        for idx in ranked_indices:
            results.append({
                "candidate": candidates[idx],
                "score": float(mu[idx]),
                "reasoning": f"Fractal-Counterfactual Score: {mu[idx]:.4f}"
            })
            
        return results

    def _meta_confidence(self, prompt: str) -> float:
        """Checks for ambiguity, presupposition, and unanswerability."""
        p_lower = prompt.lower()
        
        # 1. Presupposition
        for trigger in self.presupposition_triggers:
            if trigger in p_lower:
                return 0.2
                
        # 2. Ambiguity markers
        for trigger in self.ambiguity_triggers:
            if trigger in p_lower:
                return 0.25
                
        # 3. Lack of structural content (too short or no numbers/logic)
        if len(prompt.split()) < 4:
            return 0.3
            
        return 1.0 # Default high confidence if structure exists

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        props, A = self._parse_propositions(prompt)
        ranked = self._bandit_select(prompt, candidates, props, A)
        
        # Adjust scores based on meta-confidence if needed, but primarily return ranking
        # The score inside the dict is the raw bandit output
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        # Epistemic Honesty Check
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
            
        # Structural check
        props, A = self._parse_propositions(prompt)
        
        # If no structure parsed and prompt is long, it might be unanswerable noise
        if len(props) == 0 and len(prompt.split()) > 10:
            return 0.25
            
        # Compute a quick validity score
        # If answer contains numbers, do they match prompt logic?
        p_nums = self._extract_numbers(prompt)
        a_nums = self._extract_numbers(answer)
        
        score = 0.5 # Base confidence
        
        if p_nums and a_nums:
            # If numbers exist, check simple consistency
            # This is a heuristic proxy for the full counterfactual eval
            if len(p_nums) == len(a_nums):
                match = all(abs(p-a) < 1e-6 for p, a in zip(p_nums, a_nums))
                if match:
                    score = 0.85
                else:
                    score = 0.3
            else:
                # Mismatched count suggests transformation (good or bad)
                score = 0.6
        elif not p_nums and not a_nums:
            # Non-numeric: rely on structural parse success
            score = 0.7 if len(props) > 0 else 0.4
            
        # Cap by meta-confidence
        final_conf = min(score, meta_conf)
        
        # Never exceed 0.9 without definitive computation (which we approximate)
        if final_conf > 0.9:
            final_conf = 0.9
            
        return final_conf