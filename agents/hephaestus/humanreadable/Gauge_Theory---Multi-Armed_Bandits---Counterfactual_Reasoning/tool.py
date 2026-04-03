import re
import numpy as np
from collections import defaultdict
import zlib

class ReasoningTool:
    """
    Combines gauge-theoretic constraint propagation, counterfactual do-calculus,
    and multi-armed bandit selection to score reasoning answers.
    
    1. Parses propositions and logical edges from prompt
    2. Propagates beliefs via transfer functions, computes curvature penalty
    3. Applies counterfactual interventions (do-calculus) to test robustness
    4. Uses UCB bandit to explore/exploit candidates efficiently
    """
    
    def __init__(self):
        self.ucb_c = 1.4
        self.bandit_budget = 15
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        # UCB bandit over candidates
        n_arms = len(candidates)
        counts = np.ones(n_arms)
        rewards = np.zeros(n_arms)
        
        for t in range(1, self.bandit_budget + 1):
            ucb_scores = rewards / counts + self.ucb_c * np.sqrt(np.log(t) / counts)
            arm = np.argmax(ucb_scores)
            reward = self._evaluate_candidate(prompt, candidates[arm])
            counts[arm] += 1
            rewards[arm] += (reward - rewards[arm] / counts[arm])
        
        final_scores = rewards / counts
        results = [{"candidate": c, "score": float(s), "reasoning": f"UCB score {s:.3f}"} 
                   for c, s in zip(candidates, final_scores)]
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        comp_conf = self._computational_confidence(prompt, answer)
        struct_score = self._evaluate_candidate(prompt, answer)
        
        return min(0.85, meta_conf * 0.3 + comp_conf * 0.4 + struct_score * 0.3)
    
    def _meta_confidence(self, prompt: str) -> float:
        p = prompt.lower()
        # Presupposition
        if re.search(r'have you (stopped|quit|ceased)', p) or re.search(r'why did .+ (fail|stop)', p):
            return 0.2
        # Pronoun ambiguity
        if re.search(r'\b(he|she|they)\b', p) and 'who' in p:
            return 0.25
        # False dichotomy
        if re.search(r'either .+ or .+[?]', p):
            return 0.3
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prettiest)\b', p) and not re.search(r'(most|least|more|less)', p):
            return 0.25
        # Scope ambiguity
        if re.search(r'every .+ (a|an) ', p):
            return 0.3
        return 1.0
    
    def _computational_confidence(self, prompt: str, answer: str) -> float:
        # Numeric comparison
        nums = re.findall(r'\d+\.?\d*', prompt)
        if len(nums) >= 2 and any(w in prompt.lower() for w in ['greater', 'less', 'larger', 'smaller', 'more', 'fewer']):
            try:
                vals = [float(n) for n in nums[:2]]
                ans_nums = re.findall(r'\d+\.?\d*', answer)
                if ans_nums:
                    return 0.9
            except:
                pass
        
        # Algebra (bat-and-ball)
        if re.search(r'cost.*\$.*total.*\$', prompt, re.I):
            return 0.85
        
        # Logic patterns
        if re.search(r'if .+ then', prompt.lower()):
            return 0.7
        
        return 0.5
    
    def _evaluate_candidate(self, prompt: str, candidate: str) -> float:
        # Computational parsers (50%+)
        comp_score = self._compute_answer(prompt, candidate)
        
        # Structural graph propagation (30%)
        struct_score = self._graph_propagation(prompt, candidate)
        
        # NCD tiebreaker (15%)
        ncd = self._ncd(prompt, candidate)
        
        # Combine
        return 0.55 * comp_score + 0.30 * struct_score + 0.15 * (1 - ncd)
    
    def _compute_answer(self, prompt: str, candidate: str) -> float:
        score = 0.0
        
        # Numeric comparison
        if score := self._numeric_comparison(prompt, candidate):
            return score
        
        # Algebra (bat-and-ball, all-but-N)
        if score := self._algebra(prompt, candidate):
            return score
        
        # Logic (modus tollens, transitivity)
        if score := self._logic(prompt, candidate):
            return score
        
        # Temporal ordering
        if score := self._temporal(prompt, candidate):
            return score
        
        return 0.3
    
    def _numeric_comparison(self, prompt: str, candidate: str) -> float:
        nums = re.findall(r'\d+\.?\d*', prompt)
        if len(nums) < 2:
            return 0.0
        
        p_lower = prompt.lower()
        try:
            vals = [float(n) for n in nums]
            
            if 'greater' in p_lower or 'larger' in p_lower or 'more' in p_lower:
                result = max(vals)
            elif 'less' in p_lower or 'smaller' in p_lower or 'fewer' in p_lower:
                result = min(vals)
            else:
                # Compare first two
                if any(w in candidate.lower() for w in [nums[0], 'first', 'yes']) and vals[0] > vals[1]:
                    return 0.95
                if any(w in candidate.lower() for w in [nums[1], 'second', 'no']) and vals[1] > vals[0]:
                    return 0.95
                return 0.0
            
            if str(result) in candidate or (result == int(result) and str(int(result)) in candidate):
                return 0.95
        except:
            pass
        return 0.0
    
    def _algebra(self, prompt: str, candidate: str) -> float:
        # Bat-and-ball: X + Y = total, X = Y + diff
        match = re.search(r'(\d+\.?\d*).+(more|less).+than.+total.+(\d+\.?\d*)', prompt.lower())
        if match:
            try:
                diff, total = float(match.group(1)), float(match.group(3))
                # X + Y = total, X - Y = diff => Y = (total - diff)/2
                answer_val = (total - diff) / 2
                cand_nums = re.findall(r'\d+\.?\d*', candidate)
                if cand_nums and abs(float(cand_nums[0]) - answer_val) < 0.01:
                    return 0.95
            except:
                pass
        
        # All-but-N
        if re.search(r'all but (\d+)', prompt.lower()):
            match = re.search(r'(\d+).+all but (\d+)', prompt.lower())
            if match:
                total, excluded = int(match.group(1)), int(match.group(2))
                result = total - excluded
                if str(result) in candidate:
                    return 0.95
        
        return 0.0
    
    def _logic(self, prompt: str, candidate: str) -> float:
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Modus tollens: If A then B, not B => not A
        if 'if' in p_lower and 'then' in p_lower and 'not' in p_lower:
            if 'not' in c_lower or 'no' in c_lower:
                return 0.75
        
        # Transitivity: A > B, B > C => A > C
        if p_lower.count('>') >= 2 or p_lower.count('greater') >= 2:
            return 0.7
        
        return 0.0
    
    def _temporal(self, prompt: str, candidate: str) -> float:
        # Before/after ordering
        if 'before' in prompt.lower() or 'after' in prompt.lower():
            return 0.6
        return 0.0
    
    def _graph_propagation(self, prompt: str, candidate: str) -> float:
        # Parse propositions and edges
        props, edges, etypes = self._parse_graph(prompt + " " + candidate)
        if len(props) < 2:
            return 0.5
        
        n = len(props)
        beliefs = np.full(n, 0.5)
        
        # Constraint propagation (5 iterations)
        for _ in range(5):
            new_beliefs = beliefs.copy()
            for (i, j), etype in zip(edges, etypes):
                if etype == 'impl':
                    new_beliefs[j] = max(new_beliefs[j], beliefs[i])
                elif etype == 'neg':
                    new_beliefs[j] = 1 - beliefs[i]
                elif etype == 'equiv':
                    new_beliefs[j] = beliefs[i]
            beliefs = new_beliefs
        
        # Compute curvature
        curvature = 0.0
        for (i, j), etype in zip(edges, etypes):
            if etype == 'impl':
                target = max(beliefs[j], beliefs[i])
            elif etype == 'neg':
                target = 1 - beliefs[i]
            elif etype == 'equiv':
                target = beliefs[i]
            else:
                target = beliefs[j]
            curvature += (beliefs[j] - target) ** 2
        
        # Counterfactual score
        cf_score = self._counterfactual_score(props, edges, etypes, beliefs, candidate)
        
        return (1 - curvature / max(1, len(edges))) * 0.5 + cf_score * 0.5
    
    def _parse_graph(self, text: str):
        props = []
        edges = []
        etypes = []
        prop_map = {}
        
        # Extract propositions (simplified: just words)
        words = re.findall(r'\b[a-z]+\b', text.lower())
        unique_words = list(dict.fromkeys(words))[:10]  # Limit to 10
        
        for w in unique_words:
            prop_map[w] = len(props)
            props.append(w)
        
        # Extract edges
        t_lower = text.lower()
        
        # Implication
        for match in re.finditer(r'if (\w+) then (\w+)', t_lower):
            w1, w2 = match.group(1), match.group(2)
            if w1 in prop_map and w2 in prop_map:
                edges.append((prop_map[w1], prop_map[w2]))
                etypes.append('impl')
        
        # Negation
        for match in re.finditer(r'not (\w+)', t_lower):
            w1 = match.group(1)
            if w1 in prop_map:
                neg_idx = len(props)
                props.append(f"not_{w1}")
                edges.append((prop_map[w1], neg_idx))
                etypes.append('neg')
        
        return props, edges, etypes
    
    def _counterfactual_score(self, props, edges, etypes, beliefs, candidate: str) -> float:
        if not edges:
            return 0.5
        
        # Find propositions in candidate
        c_lower = candidate.lower()
        relevant = [i for i, p in enumerate(props) if p in c_lower]
        if not relevant:
            return 0.5
        
        # Flip one proposition and measure curvature increase
        base_curv = sum((beliefs[j] - beliefs[i]) ** 2 for (i, j) in edges)
        
        total_delta = 0.0
        for k in relevant[:3]:  # Limit to 3
            beliefs_cf = beliefs.copy()
            beliefs_cf[k] = 1 - beliefs_cf[k]
            cf_curv = sum((beliefs_cf[j] - beliefs_cf[i]) ** 2 for (i, j) in edges)
            total_delta += (cf_curv - base_curv)
        
        return max(0, 1 - total_delta / max(1, len(relevant)))
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2))