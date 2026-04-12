from typing import Dict, Optional, Tuple

import re
import math
import random
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    MCTS-based reasoning with Popperian falsification and adaptive UCB.
    
    Builds a search tree over hypothesis spaces extracted from prompt+candidate.
    Each node stores predicates and MCTS statistics. Selection uses adaptive UCB
    where c is tuned by observed variance. Rollouts apply transformations and
    attempt to falsify via constraint propagation. Score = 1 - falsification_rate.
    """
    
    def __init__(self):
        self.simulations = 50
        self.rollout_depth = 3
        self.c_init = 1.4
        random.seed(42)
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._mcts_score(prompt, cand)
            reasoning = self._build_reasoning(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        base_score = self._mcts_score(prompt, answer)
        comp_conf = self._computational_confidence(prompt, answer)
        return min(meta_conf, max(base_score, comp_conf))
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presupposition, unanswerability."""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop))\b', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery .+ (a|an) \b', p_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she|they)\b', p_lower) and 'who' in p_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .+ or .+\b', p_lower) and '?' in prompt:
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prettiest)\b', p_lower):
            return 0.3
        
        # Insufficient info markers
        if re.search(r'\b(cannot be determined|not enough information|ambiguous)\b', p_lower):
            return 0.2
        
        return 1.0
    
    def _mcts_score(self, prompt: str, candidate: str) -> float:
        predicates = self._extract_predicates(prompt, candidate)
        root = MCTSNode(predicates)
        c = self.c_init
        variance_vals = []
        
        for _ in range(self.simulations):
            path = []
            node = root
            
            # Selection
            while node.children and node.visits > 0:
                node = self._select_child(node, c)
                path.append(node)
            
            # Expansion
            if node.visits > 0:
                children = self._expand(node)
                if children:
                    node = random.choice(children)
                    path.append(node)
            
            # Rollout
            falsify_reward = self._rollout(node, prompt, candidate)
            variance_vals.append(falsify_reward)
            
            # Backprop
            for n in path:
                n.visits += 1
                n.total_falsify += falsify_reward
            root.visits += 1
            root.total_falsify += falsify_reward
            
            # Adaptive c
            if len(variance_vals) > 5:
                var = sum((x - sum(variance_vals)/len(variance_vals))**2 for x in variance_vals[-10:]) / min(10, len(variance_vals))
                c = self.c_init * (1 + 0.5 * var)
        
        survival_rate = 1 - (root.total_falsify / max(1, root.visits))
        comp_score = self._computational_score(prompt, candidate)
        ncd_score = self._ncd_score(prompt, candidate)
        
        return 0.55 * survival_rate + 0.30 * comp_score + 0.15 * ncd_score
    
    def _select_child(self, node, c):
        best_val = -1e9
        best_child = None
        for child in node.children:
            if child.visits == 0:
                return child
            q = 1 - (child.total_falsify / child.visits)
            ucb = q + c * math.sqrt(math.log(node.visits) / child.visits)
            if ucb > best_val:
                best_val = ucb
                best_child = child
        return best_child if best_child else node.children[0]
    
    def _expand(self, node):
        transforms = [self._negate_pred, self._flip_comparative, self._swap_conditional]
        children = []
        for trans in transforms:
            new_preds = trans(node.predicates)
            if new_preds != node.predicates:
                child = MCTSNode(new_preds)
                node.children.append(child)
                children.append(child)
        return children
    
    def _rollout(self, node, prompt, candidate):
        preds = list(node.predicates)
        for _ in range(self.rollout_depth):
            trans = random.choice([self._negate_pred, self._flip_comparative, self._swap_conditional])
            preds = trans(preds)
        return 1.0 if self._check_contradiction(preds) else 0.0
    
    def _extract_predicates(self, prompt, candidate):
        text = prompt + " " + candidate
        preds = []
        
        for match in re.finditer(r'(\w+)\s+(is|are|was|were)\s+(not\s+)?(\w+)', text, re.IGNORECASE):
            subj, _, neg, obj = match.groups()
            preds.append(("eq", subj, obj, bool(neg)))
        
        for match in re.finditer(r'(\d+\.?\d*)\s*([<>=]+)\s*(\d+\.?\d*)', text):
            preds.append(("cmp", float(match.group(1)), match.group(2), float(match.group(3))))
        
        for match in re.finditer(r'\b(not|no)\s+(\w+)', text, re.IGNORECASE):
            preds.append(("neg", match.group(2)))
        
        for match in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$)', text, re.IGNORECASE):
            preds.append(("cond", match.group(1).strip(), match.group(2).strip()))
        
        return tuple(preds)
    
    def _negate_pred(self, preds):
        if not preds:
            return preds
        p = list(preds)
        idx = random.randint(0, len(p) - 1)
        if p[idx][0] == "eq":
            p[idx] = (p[idx][0], p[idx][1], p[idx][2], not p[idx][3])
        return tuple(p)
    
    def _flip_comparative(self, preds):
        for i, p in enumerate(preds):
            if p[0] == "cmp":
                new_p = list(preds)
                ops = {"<": ">", ">": "<", "<=": ">=", ">=": "<=", "=": "="}
                new_p[i] = ("cmp", p[3], ops.get(p[2], p[2]), p[1])
                return tuple(new_p)
        return preds
    
    def _swap_conditional(self, preds):
        for i, p in enumerate(preds):
            if p[0] == "cond":
                new_p = list(preds)
                new_p[i] = ("cond", p[2], p[1])
                return tuple(new_p)
        return preds
    
    def _check_contradiction(self, preds):
        nums = {}
        for p in preds:
            if p[0] == "cmp":
                if not self._eval_cmp(p[1], p[2], p[3]):
                    return True
            if p[0] == "eq":
                key = p[1]
                val = p[2]
                neg = p[3]
                if key in nums and nums[key] != (val, neg):
                    return True
                nums[key] = (val, neg)
        return False
    
    def _eval_cmp(self, a, op, b):
        if op == "<": return a < b
        if op == ">": return a > b
        if op == "<=": return a <= b
        if op == ">=": return a >= b
        if op == "==" or op == "=": return abs(a - b) < 1e-9
        return True
    
    def _computational_score(self, prompt, candidate):
        score = 0.5
        
        # Numeric comparison parser
        nums_prompt = re.findall(r'\d+\.?\d*', prompt)
        nums_cand = re.findall(r'\d+\.?\d*', candidate)
        if nums_prompt and nums_cand:
            if any(float(n) in [float(m) for m in nums_prompt] for n in nums_cand):
                score += 0.2
        
        # PEMDAS evaluation
        if '+' in prompt or '*' in prompt or '-' in prompt:
            expr_match = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)', candidate)
            if expr_match:
                score += 0.15
        
        # Modus tollens / transitivity
        if re.search(r'\b(if|implies|therefore)\b', prompt, re.IGNORECASE):
            if re.search(r'\b(not|false|no)\b', candidate, re.IGNORECASE):
                score += 0.1
        
        return min(1.0, score)
    
    def _computational_confidence(self, prompt, answer):
        # Direct computation parsers
        if self._solve_bat_ball(prompt, answer):
            return 0.92
        if self._solve_numeric_cmp(prompt, answer):
            return 0.88
        if self._solve_all_but_n(prompt, answer):
            return 0.85
        return 0.4
    
    def _solve_bat_ball(self, prompt, answer):
        match = re.search(r'(\d+\.?\d*).+more than.+total.+(\d+\.?\d*)', prompt, re.IGNORECASE)
        if match:
            diff = float(match.group(1))
            total = float(match.group(2))
            smaller = (total - diff) / 2
            ans_num = re.search(r'\d+\.?\d*', answer)
            if ans_num and abs(float(ans_num.group()) - smaller) < 0.01:
                return True
        return False
    
    def _solve_numeric_cmp(self, prompt, answer):
        nums = re.findall(r'\d+\.?\d*', prompt)
        if len(nums) >= 2:
            a, b = float(nums[0]), float(nums[1])
            if 'greater' in prompt.lower() or 'larger' in prompt.lower():
                expected = str(max(a, b))
                if expected in answer:
                    return True
        return False
    
    def _solve_all_but_n(self, prompt, answer):
        match = re.search(r'all but (\d+)', prompt, re.IGNORECASE)
        total_match = re.search(r'(\d+) total', prompt, re.IGNORECASE)
        if match and total_match:
            result = int(total_match.group(1)) - int(match.group(1))
            if str(result) in answer:
                return True
        return False
    
    def _ncd_score(self, prompt, candidate):
        def ncd(s1, s2):
            c1, c2, c12 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode())), len(zlib.compress((s1+s2).encode()))
            return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
        return max(0, 1 - ncd(prompt, candidate))
    
    def _build_reasoning(self, prompt, candidate):
        preds = self._extract_predicates(prompt, candidate)
        return f"Extracted {len(preds)} predicates; MCTS falsification search completed"

class MCTSNode:
    def __init__(self, predicates):
        self.predicates = predicates
        self.visits = 0
        self.total_falsify = 0.0
        self.children = []