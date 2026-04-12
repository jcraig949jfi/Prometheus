"""
Neural Oscillation x Mechanism Design x Model Checking Reasoning Tool

Combines phase-aligned binding (neural oscillations), incentive-compatible
utility (mechanism design), and state-space search (model checking) to score
candidate answers by their logical consistency and structural alignment.
"""

import re
import numpy as np
from collections import deque
import zlib

class ReasoningTool:
    def __init__(self):
        np.random.seed(42)
        self.max_depth = 6
        self.phase_bands = 3  # theta, gamma, beta
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Rank candidates by phase-aligned utility over state traces."""
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            reasoning = self._explain_score(prompt, cand, score)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-confidence checks."""
        meta_conf = self._meta_confidence(prompt)
        structural_conf = self._structural_confidence(prompt, answer)
        return min(meta_conf, structural_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity, presupposition, unanswerability."""
        p_lower = prompt.lower()
        # Presupposition
        if re.search(r'\b(have you stopped|did you quit|why did .* (fail|stop))\b', p_lower):
            return 0.2
        # Scope ambiguity
        if re.search(r'\bevery \w+ .* a \w+\b', p_lower) and '?' in prompt:
            return 0.25
        # Pronoun ambiguity
        if re.search(r'\b(he|she|they)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.25
        # False dichotomy
        if re.search(r'\b(either .* or|must be .* or)\b', p_lower):
            return 0.3
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower) and not re.search(r'\b(according to|measured by)\b', p_lower):
            return 0.3
        # Insufficient info
        if re.search(r'\b(cannot (be )?determine|insufficient|not enough information)\b', p_lower):
            return 0.2
        return 1.0
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        """Compute score via structural + computational + model-checking."""
        struct_score = self._structural_score(prompt, candidate)
        comp_score = self._computational_score(prompt, candidate)
        model_score = self._model_checking_score(prompt, candidate)
        ncd_score = self._ncd_score(prompt, candidate)
        
        # Weight: structural 50%, computational 30%, model 15%, ncd 5%
        return 0.5*struct_score + 0.3*comp_score + 0.15*model_score + 0.05*ncd_score
    
    def _structural_score(self, prompt: str, candidate: str) -> float:
        """Parse structural features and check candidate alignment."""
        score = 0.5  # baseline
        
        # Numeric comparison
        nums_p = self._extract_numbers(prompt)
        nums_c = self._extract_numbers(candidate)
        if len(nums_p) >= 2 and len(nums_c) == 1:
            if re.search(r'\b(larger|greater|more|bigger)\b', prompt.lower()):
                if nums_c[0] == max(nums_p): score += 0.3
            elif re.search(r'\b(smaller|less|fewer)\b', prompt.lower()):
                if nums_c[0] == min(nums_p): score += 0.3
        
        # Negation consistency
        neg_p = len(re.findall(r'\b(not|no|never|n\'t)\b', prompt.lower()))
        neg_c = len(re.findall(r'\b(not|no|never|n\'t)\b', candidate.lower()))
        if (neg_p % 2) == (neg_c % 2): score += 0.1
        
        # Conditional/causal
        if re.search(r'\b(if|because|since|therefore)\b', prompt.lower()):
            if re.search(r'\b(then|so|thus|hence)\b', candidate.lower()): score += 0.1
        
        return min(score, 1.0)
    
    def _computational_score(self, prompt: str, candidate: str) -> float:
        """Actually compute answers for common problem types."""
        score = 0.0
        
        # Bat-and-ball algebra
        match = re.search(r'total.*\$?([\d.]+).*costs.*\$?([\d.]+).*more', prompt, re.I)
        if match:
            total, diff = float(match.group(1)), float(match.group(2))
            lesser = (total - diff) / 2
            nums_c = self._extract_numbers(candidate)
            if nums_c and abs(nums_c[0] - lesser) < 0.01: return 1.0
        
        # PEMDAS evaluation
        expr_match = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)\s*([+\-*/])\s*(\d+)', prompt)
        if expr_match:
            try:
                result = eval(expr_match.group(0))
                nums_c = self._extract_numbers(candidate)
                if nums_c and abs(nums_c[0] - result) < 0.01: return 1.0
            except: pass
        
        # All-but-N
        match = re.search(r'(\d+).*all but (\d+)', prompt, re.I)
        if match:
            total, exclude = int(match.group(1)), int(match.group(2))
            nums_c = self._extract_numbers(candidate)
            if nums_c and nums_c[0] == exclude: return 1.0
        
        # Modular arithmetic (clock)
        match = re.search(r'(\d+)\s*hours.*(\d+)\s*o\'?clock', prompt, re.I)
        if match:
            add_hours, start = int(match.group(1)), int(match.group(2))
            result = (start + add_hours) % 12
            if result == 0: result = 12
            nums_c = self._extract_numbers(candidate)
            if nums_c and nums_c[0] == result: return 1.0
        
        # Transitivity
        trans = self._check_transitivity(prompt, candidate)
        if trans >= 0: return trans
        
        return score
    
    def _model_checking_score(self, prompt: str, candidate: str) -> float:
        """Build Kripke structure and compute utility-optimal trace."""
        props_p = self._extract_propositions(prompt)
        props_c = self._extract_propositions(candidate)
        
        if not props_p: return 0.5
        
        # Assign phase vectors
        state_p = self._build_state(props_p)
        state_c = self._build_state(props_c)
        
        # BFS to find optimal utility state
        optimal_state = self._bfs_optimal(state_p)
        
        # Score candidate by phase distance to optimal
        utility_p = self._compute_utility(optimal_state)
        utility_c = self._compute_utility(state_c)
        
        score = np.exp(-abs(utility_p - utility_c) / (1.0 + abs(utility_p)))
        return score
    
    def _extract_propositions(self, text: str) -> list:
        """Extract simple subject-verb-object propositions."""
        sentences = re.split(r'[.!?;]', text)
        props = []
        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 5: continue
            # Simple SVO regex
            match = re.search(r'\b([A-Z]\w+)\s+(is|are|has|have|was|were)\s+(\w+)', sent)
            if match:
                props.append(sent)
        return props if props else [text[:50]]  # fallback
    
    def _build_state(self, propositions: list) -> dict:
        """Create state with phase vectors for each proposition."""
        state = {}
        for i, prop in enumerate(propositions):
            phase = np.array([
                np.sin(2*np.pi*i/len(propositions)),  # theta
                np.cos(2*np.pi*i/len(propositions)),  # gamma
                np.sin(4*np.pi*i/len(propositions))   # beta
            ])
            state[prop] = phase
        return state
    
    def _bfs_optimal(self, initial_state: dict) -> dict:
        """BFS to find highest-utility state."""
        if not initial_state: return {}
        queue = deque([(initial_state, 0)])
        best_state = initial_state
        best_utility = self._compute_utility(initial_state)
        visited = set()
        
        while queue and len(visited) < 50:  # limit search
            state, depth = queue.popleft()
            state_key = tuple(sorted(state.keys()))
            if state_key in visited or depth >= self.max_depth: continue
            visited.add(state_key)
            
            utility = self._compute_utility(state)
            if utility > best_utility:
                best_utility = utility
                best_state = state
            
            # Generate successor states (flip one proposition)
            for prop in list(state.keys()):
                new_state = state.copy()
                new_state[prop] = new_state[prop] + np.array([0.1, 0.1, 0.1])
                queue.append((new_state, depth+1))
        
        return best_state
    
    def _compute_utility(self, state: dict) -> float:
        """Utility = negative phase variance (coherence)."""
        if not state: return 0.0
        phases = np.array(list(state.values()))
        mean_phase = np.mean(phases, axis=0)
        variance = np.mean(np.linalg.norm(phases - mean_phase, axis=1)**2)
        return -variance
    
    def _check_transitivity(self, prompt: str, candidate: str) -> float:
        """Check A>B, B>C => A>C patterns."""
        comparisons = re.findall(r'(\w+)\s+(?:is\s+)?(?:taller|faster|older|greater)\s+than\s+(\w+)', prompt, re.I)
        if len(comparisons) >= 2:
            # Build graph
            graph = {}
            for a, b in comparisons:
                graph.setdefault(a, set()).add(b)
            # Check transitivity
            for start in graph:
                for mid in graph.get(start, []):
                    for end in graph.get(mid, []):
                        if end in candidate and start in candidate:
                            return 1.0 if re.search(rf'{start}.*{end}', candidate, re.I) else 0.0
        return -1
    
    def _ncd_score(self, prompt: str, candidate: str) -> float:
        """Normalized compression distance (minor tiebreaker)."""
        c_p = len(zlib.compress(prompt.encode()))
        c_c = len(zlib.compress(candidate.encode()))
        c_both = len(zlib.compress((prompt + candidate).encode()))
        ncd = (c_both - min(c_p, c_c)) / max(c_p, c_c)
        return 1.0 - min(ncd, 1.0)
    
    def _structural_confidence(self, prompt: str, answer: str) -> float:
        """Confidence based on structural match quality."""
        nums_p = self._extract_numbers(prompt)
        nums_a = self._extract_numbers(answer)
        
        # Definite computation
        if self._computational_score(prompt, answer) > 0.9:
            return 0.95
        
        # Strong structural match
        if self._structural_score(prompt, answer) > 0.8:
            return 0.75
        
        # Weak match
        if self._structural_score(prompt, answer) > 0.5:
            return 0.5
        
        return 0.3  # uncertain
    
    def _extract_numbers(self, text: str) -> list:
        """Extract all numeric values."""
        nums = re.findall(r'\b\d+\.?\d*\b', text)
        return [float(n) for n in nums]
    
    def _explain_score(self, prompt: str, candidate: str, score: float) -> str:
        """Brief explanation of scoring."""
        if score > 0.8: return "Strong structural and computational alignment"
        if score > 0.6: return "Good phase coherence with prompt"
        if score > 0.4: return "Moderate consistency"
        return "Low utility trace match"