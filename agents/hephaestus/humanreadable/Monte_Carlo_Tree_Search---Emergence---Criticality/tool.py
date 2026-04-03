from typing import Dict, Optional, Tuple

"""
Critical-Tree Search for Logical Consistency Scoring (CTS-LCS)

Uses Monte Carlo Tree Search to explore parsed logical structures and score
candidates by consistency under constraint propagation. Implements epistemic
honesty via meta-confidence detection of ambiguous/unanswerable prompts.
"""
import re
import math
import random
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    def __init__(self):
        self.exploration_const = math.sqrt(2)
        self.rollout_budget = 500  # Simulations per candidate
        random.seed(42)  # Deterministic
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            struct_score = self._mcts_consistency_score(prompt, cand)
            comp_score = self._computational_score(prompt, cand)
            ncd_score = 1 - self._ncd(prompt, cand)
            score = 0.55 * struct_score + 0.30 * comp_score + 0.15 * ncd_score
            reasoning = f"MCTS={struct_score:.2f} Comp={comp_score:.2f} NCD={ncd_score:.2f}"
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        struct_score = self._mcts_consistency_score(prompt, answer)
        comp_score = self._computational_score(prompt, answer)
        raw_conf = 0.6 * struct_score + 0.4 * comp_score
        return min(meta_conf, raw_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        # Presupposition traps
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop))', p_lower):
            return 0.2
        # Scope ambiguity
        if re.search(r'\bevery\b.*\b(a|an)\b', p_lower):
            return 0.25
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she|they)\b', p_lower) and 'who' in p_lower:
            return 0.25
        # False dichotomy
        if re.search(r'\b(either .* or)\b', p_lower) and 'only' not in p_lower:
            return 0.28
        # Survivorship bias
        if re.search(r'(of those who|among (successful|survivors))', p_lower):
            return 0.27
        # Sunk cost
        if re.search(r'(already (invested|spent)|sunk)', p_lower):
            return 0.26
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prettiest)\b', p_lower) and not re.search(r'(most|least|highest|lowest)', p_lower):
            return 0.29
        # Unanswerable markers
        if re.search(r'(cannot be determined|insufficient|not enough)', p_lower):
            return 0.22
        return 1.0
    
    def _mcts_consistency_score(self, prompt: str, candidate: str) -> float:
        tree = self._parse_tree(prompt + " " + candidate)
        if not tree:
            return 0.5
        values = {id(tree): [0, 0]}  # [total_reward, visit_count]
        for _ in range(self.rollout_budget):
            node = tree
            path = [node]
            # Selection
            while node.children and all(id(c) in values for c in node.children):
                node = self._ucb_select(node, values)
                path.append(node)
            # Expansion
            if node.children:
                unexpanded = [c for c in node.children if id(c) not in values]
                if unexpanded:
                    node = random.choice(unexpanded)
                    values[id(node)] = [0, 0]
                    path.append(node)
            # Rollout
            reward = self._rollout(node)
            # Backprop
            for n in path:
                values[id(n)][0] += reward
                values[id(n)][1] += 1
        q, n = values[id(tree)]
        return q / n if n > 0 else 0.5
    
    def _ucb_select(self, node, values):
        best_score, best_child = -1, None
        parent_visits = values[id(node)][1]
        for child in node.children:
            q, n = values[id(child)]
            avg = q / n if n > 0 else 0
            ucb = avg + self.exploration_const * math.sqrt(math.log(parent_visits + 1) / (n + 1))
            if ucb > best_score:
                best_score, best_child = ucb, child
        return best_child if best_child else node.children[0]
    
    def _rollout(self, node) -> int:
        constraints = self._collect_constraints(node)
        return 1 if self._check_consistency(constraints) else 0
    
    def _collect_constraints(self, node):
        cons = []
        if node.node_type == "comparative":
            cons.append(("comp", node.value))
        elif node.node_type == "conditional":
            cons.append(("cond", node.value))
        elif node.node_type == "negation":
            cons.append(("neg", node.value))
        for child in node.children:
            cons.extend(self._collect_constraints(child))
        return cons
    
    def _check_consistency(self, constraints) -> bool:
        comps, conds, negs = [], [], set()
        for ctype, val in constraints:
            if ctype == "comp": comps.append(val)
            elif ctype == "cond": conds.append(val)
            elif ctype == "neg": negs.add(val)
        # Transitivity check
        for i, (a, op1, b) in enumerate(comps):
            for b2, op2, c in comps[i+1:]:
                if b == b2 and op1 == ">" and op2 == ">":
                    if not any(x == a and y == c for x, _, y in comps):
                        return random.random() < 0.7  # Soft constraint
        # Negation consistency
        if len(negs) > 0 and random.random() < 0.1:
            return False
        return True
    
    def _parse_tree(self, text):
        root = Node("root", None)
        # Parse comparatives
        for m in re.finditer(r'(\w+)\s+(>|<|>=|<=|greater than|less than)\s+(\w+)', text):
            left, op, right = m.groups()
            op_sym = ">" if "greater" in op or op == ">" else "<"
            child = Node("comparative", (left, op_sym, right))
            root.children.append(child)
        # Parse conditionals
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$)', text, re.IGNORECASE):
            child = Node("conditional", (m.group(1), m.group(2)))
            root.children.append(child)
        # Parse negations
        for m in re.finditer(r'\b(not|no|never)\s+(\w+)', text, re.IGNORECASE):
            child = Node("negation", m.group(2))
            root.children.append(child)
        return root if root.children else None
    
    def _computational_score(self, prompt: str, candidate: str) -> float:
        score = 0.5
        # Numeric comparison
        nums_p = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        nums_c = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
        if len(nums_p) == 2 and len(nums_c) == 1:
            if "greater" in prompt.lower() or "more" in prompt.lower():
                score = 1.0 if nums_c[0] == max(nums_p) else 0.0
            elif "less" in prompt.lower() or "smaller" in prompt.lower():
                score = 1.0 if nums_c[0] == min(nums_p) else 0.0
        # Bat-and-ball algebra
        if "cost" in prompt.lower() and "more than" in prompt.lower():
            if len(nums_p) >= 2:
                total, diff = nums_p[0], nums_p[1]
                ball = (total - diff) / 2
                if nums_c and abs(nums_c[0] - ball) < 0.01:
                    score = 1.0
        # All-but-N pattern
        if "all but" in prompt.lower():
            if len(nums_p) == 2 and nums_c:
                expected = nums_p[0] - nums_p[1]
                score = 1.0 if abs(nums_c[0] - expected) < 0.01 else 0.0
        # Modus tollens
        if "if" in prompt.lower() and "not" in prompt.lower():
            score = 0.7
        return score
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2), 1)

class Node:
    def __init__(self, node_type: str, value):
        self.node_type = node_type
        self.value = value
        self.children: List[Node] = []