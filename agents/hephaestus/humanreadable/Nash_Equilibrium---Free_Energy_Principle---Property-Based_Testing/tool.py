from typing import Dict, Set, Tuple

"""
Nash-Free-Energy-Property-Based Reasoning Tool

Combines game-theoretic equilibrium selection, variational free energy minimization,
and property-based shrinking to score candidate answers by finding stable, low-error,
parsimonious interpretations of logical structure.
"""

import re
import math
import zlib
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    def __init__(self):
        self.alpha = 0.5  # Free energy weight
        self.beta = 0.3   # Complexity penalty
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            reasoning = self._explain_score(prompt, cand, score)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        comp_conf = self._computational_confidence(prompt, answer)
        if comp_conf is not None:
            return min(0.95, comp_conf)
        
        struct_score = self._score_candidate(prompt, answer)
        base_conf = min(0.85, struct_score)
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        # Presupposition detection
        presup_patterns = [r"have you (stopped|quit|ceased)", r"why did .+ (fail|stop|end)",
                          r"when did you (stop|quit|start)", r"do you still"]
        for pat in presup_patterns:
            if re.search(pat, p_lower):
                return 0.2
        
        # Scope ambiguity: "every X did a Y"
        if re.search(r"every .+ (did|has|had|took|found) a ", p_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r"(he|she|they|it) (was|is|were)", p_lower) and "who" in p_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r"either .+ or .+\?", p_lower) and "only" not in p_lower:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r"(best|worst|favorite|better|worse)", p_lower):
            if not re.search(r"(most|least|more|less|faster|slower|cheaper)", p_lower):
                return 0.3
        
        # Unanswerable: "is this enough information"
        if "enough information" in p_lower or "can we determine" in p_lower:
            return 0.4
        
        return 1.0
    
    def _computational_confidence(self, prompt: str, answer: str) -> float:
        # Try computational solvers
        comp_result = self._compute_answer(prompt)
        if comp_result is not None:
            ans_lower = answer.lower().strip()
            if str(comp_result).lower() in ans_lower or ans_lower in str(comp_result).lower():
                return 0.95
            else:
                return 0.05
        return None
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        # Computational solving (50% weight)
        comp_score = self._computational_score(prompt, candidate)
        
        # Free energy + Nash equilibrium (35% weight)
        fe_score = self._free_energy_nash_score(prompt, candidate)
        
        # NCD tiebreaker (15% weight)
        ncd_score = self._ncd_score(prompt, candidate)
        
        final = 0.5 * comp_score + 0.35 * fe_score + 0.15 * ncd_score
        return max(0.0, min(1.0, final))
    
    def _computational_score(self, prompt: str, candidate: str) -> float:
        computed = self._compute_answer(prompt)
        if computed is None:
            return 0.5
        
        cand_lower = candidate.lower().strip()
        comp_str = str(computed).lower()
        
        if comp_str in cand_lower or cand_lower in comp_str:
            return 1.0
        
        # Numeric tolerance
        cand_nums = re.findall(r"-?\d+\.?\d*", candidate)
        if cand_nums and isinstance(computed, (int, float)):
            try:
                if abs(float(cand_nums[0]) - computed) < 0.01:
                    return 1.0
            except:
                pass
        
        return 0.0
    
    def _compute_answer(self, prompt: str):
        # Numeric comparison
        match = re.search(r"(\d+\.?\d*)\s*(>|<|>=|<=|greater|less|larger|smaller)\s*(\d+\.?\d*)", prompt)
        if match:
            a, op, b = float(match.group(1)), match.group(2), float(match.group(3))
            if '>' in op or 'greater' in op or 'larger' in op:
                return a > b
            else:
                return a < b
        
        # Bat and ball algebra
        if re.search(r"bat and ball.+total.+(\d+\.?\d*).+bat costs.+(\d+\.?\d*)\s+more", prompt.lower()):
            match = re.search(r"total.+?(\d+\.?\d*)", prompt.lower())
            total = float(match.group(1)) if match else None
            match = re.search(r"(\d+\.?\d*)\s+more", prompt.lower())
            diff = float(match.group(1)) if match else None
            if total and diff:
                ball = (total - diff) / 2
                return ball
        
        # All-but-N pattern
        match = re.search(r"all but (\d+)", prompt.lower())
        if match:
            n_match = re.search(r"(\d+)\s+(items|apples|students|people)", prompt.lower())
            if n_match:
                total = int(n_match.group(1))
                excluded = int(match.group(1))
                return total - excluded
        
        # Modular arithmetic
        if "remainder" in prompt.lower() or "mod" in prompt.lower():
            nums = re.findall(r"\b(\d+)\b", prompt)
            if len(nums) >= 2:
                return int(nums[0]) % int(nums[1])
        
        # Simple arithmetic in prompt
        match = re.search(r"(\d+)\s*([+\-*/])\s*(\d+)", prompt)
        if match:
            a, op, b = int(match.group(1)), match.group(2), int(match.group(3))
            if op == '+': return a + b
            elif op == '-': return a - b
            elif op == '*': return a * b
            elif op == '/': return a / b if b != 0 else None
        
        return None
    
    def _free_energy_nash_score(self, prompt: str, candidate: str) -> float:
        # Parse hypergraph
        prompt_graph = self._parse_hypergraph(prompt)
        cand_graph = self._parse_hypergraph(candidate)
        
        if not prompt_graph:
            return 0.5
        
        # Initial strategy: align with candidate
        strategy = self._initialize_strategy(prompt_graph, cand_graph)
        
        # Nash equilibrium via iterated best response
        for _ in range(5):
            fe = self._free_energy(strategy, prompt_graph, cand_graph)
            new_strategy = self._best_response(strategy, prompt_graph, cand_graph)
            if new_strategy == strategy:
                break
            strategy = new_strategy
        
        # Shrink strategy
        strategy = self._shrink_strategy(strategy, prompt_graph, cand_graph)
        
        # Final free energy
        fe = self._free_energy(strategy, prompt_graph, cand_graph)
        complexity = sum(strategy.values())
        
        score = math.exp(-self.alpha * fe) / (1 + self.beta * complexity)
        return score
    
    def _parse_hypergraph(self, text: str) -> Dict[str, Tuple[float, float]]:
        graph = {}
        text_lower = text.lower()
        
        # Negations
        for match in re.finditer(r"(not|no|never|n't)\s+(\w+)", text_lower):
            prop = f"NOT_{match.group(2)}"
            graph[prop] = (1.0, 0.0)  # (weight, empirical_prob)
        
        # Comparatives
        for match in re.finditer(r"(\w+)\s+(more|less|greater|smaller|higher|lower)\s+than\s+(\w+)", text_lower):
            prop = f"{match.group(1)}_CMP_{match.group(3)}"
            graph[prop] = (0.9, 1.0)
        
        # Conditionals
        for match in re.finditer(r"if\s+(.+?)\s+then\s+(.+?)[\.,]", text_lower):
            prop = f"IF_{match.group(1)[:10]}_THEN_{match.group(2)[:10]}"
            graph[prop] = (0.8, 1.0)
        
        # Causal
        for match in re.finditer(r"(\w+)\s+(because|leads to|results in|causes)\s+(\w+)", text_lower):
            prop = f"{match.group(1)}_CAUSE_{match.group(3)}"
            graph[prop] = (0.85, 1.0)
        
        # Numeric values
        for match in re.finditer(r"\b(\d+\.?\d*)\b", text_lower):
            prop = f"NUM_{match.group(1)}"
            graph[prop] = (1.0, 1.0)
        
        return graph
    
    def _initialize_strategy(self, prompt_graph: Dict, cand_graph: Dict) -> Dict[str, int]:
        strategy = {}
        for prop in prompt_graph.keys():
            strategy[prop] = 1 if prop in cand_graph else 0
        return strategy
    
    def _free_energy(self, strategy: Dict[str, int], prompt_graph: Dict, cand_graph: Dict) -> float:
        fe = 0.0
        for prop, (weight, _) in prompt_graph.items():
            s_i = strategy.get(prop, 0)
            p_hat = cand_graph[prop][1] if prop in cand_graph else 0.5
            fe += weight * (s_i - p_hat) ** 2
        return fe
    
    def _best_response(self, strategy: Dict[str, int], prompt_graph: Dict, cand_graph: Dict) -> Dict[str, int]:
        best_strat = strategy.copy()
        best_fe = self._free_energy(strategy, prompt_graph, cand_graph)
        
        for prop in strategy.keys():
            test_strat = strategy.copy()
            test_strat[prop] = 1 - test_strat[prop]
            test_fe = self._free_energy(test_strat, prompt_graph, cand_graph)
            if test_fe < best_fe:
                best_fe = test_fe
                best_strat = test_strat
        
        return best_strat
    
    def _shrink_strategy(self, strategy: Dict[str, int], prompt_graph: Dict, cand_graph: Dict) -> Dict[str, int]:
        shrunk = strategy.copy()
        current_fe = self._free_energy(shrunk, prompt_graph, cand_graph)
        
        for prop in list(shrunk.keys()):
            if shrunk[prop] == 1:
                test = shrunk.copy()
                test[prop] = 0
                test_fe = self._free_energy(test, prompt_graph, cand_graph)
                if test_fe <= current_fe:
                    shrunk = test
                    current_fe = test_fe
        
        return shrunk
    
    def _ncd_score(self, prompt: str, candidate: str) -> float:
        def ncd(s1, s2):
            c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
            c12 = zlib.compress((s1 + s2).encode())
            return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2))
        
        dist = ncd(prompt, candidate)
        return max(0, 1 - dist)
    
    def _explain_score(self, prompt: str, candidate: str, score: float) -> str:
        comp = self._compute_answer(prompt)
        if comp is not None:
            return f"Computational: {comp}, Score: {score:.2f}"
        return f"Free-energy equilibrium score: {score:.2f}"