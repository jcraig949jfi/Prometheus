from typing import Dict, Tuple

import re
import math
import random
from collections import defaultdict
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    MCTS-based reasoning combining falsificationism and Kolmogorov complexity.
    
    Builds a search tree over logical interpretations of candidate answers.
    Each node contains propositions extracted via regex. Priors based on
    description length (Kolmogorov approximation). Rewards based on
    falsification: rollouts that find contradictions get 0, consistent ones get 1.
    Final score is W/N (unfalsified probability) weighted by low complexity.
    """
    
    def __init__(self, simulations=50, c_explore=1.414):
        self.simulations = simulations
        self.c_explore = c_explore
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._mcts_score(prompt, cand)
            conf = self.confidence(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score * conf,
                "reasoning": f"MCTS unfalsified prob {score:.3f}, confidence {conf:.3f}"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        comp_conf = self._computation_confidence(prompt, answer)
        return min(meta_conf, comp_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p = prompt.lower()
        if re.search(r'\b(have you stopped|have you quit|did you stop|why did .+ fail)', p):
            return 0.2
        if re.search(r'\bevery .+ (a |an |the )', p) and '?' in prompt:
            return 0.25
        if re.search(r'\b(he|she) (was|is)\b', p) and re.search(r'\bwho\b', p):
            return 0.25
        if re.search(r'\b(either .+ or)\b', p) and not re.search(r'\bonly\b', p):
            return 0.3
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p):
            return 0.35
        if re.search(r'\b(cannot be determined|insufficient information)\b', p):
            return 0.3
        return 0.95
    
    def _computation_confidence(self, prompt: str, answer: str) -> float:
        if self._compute_numeric(prompt, answer):
            return 0.85
        if self._compute_probability(prompt, answer):
            return 0.8
        if self._detect_structural_match(prompt, answer):
            return 0.7
        return 0.4
    
    def _mcts_score(self, prompt: str, candidate: str) -> float:
        text = prompt + " " + candidate
        root = MCTSNode(self._extract_propositions(text))
        symbol_freq = self._symbol_frequencies(text)
        
        for _ in range(self.simulations):
            node = self._select(root)
            child = self._expand(node, text, symbol_freq)
            reward = self._simulate(child if child else node, text)
            self._backpropagate(child if child else node, reward)
        
        return root.w / max(root.n, 1)
    
    def _select(self, node):
        while node.children:
            node = max(node.children, key=lambda c: self._ucb1(c, node.n))
        return node
    
    def _ucb1(self, child, parent_n):
        if child.n == 0:
            return float('inf')
        exploit = child.w / child.n
        explore = self.c_explore * math.sqrt(math.log(parent_n) / child.n)
        return exploit + explore + child.prior
    
    def _expand(self, node, text, symbol_freq):
        new_props = self._generate_new_propositions(text, node.propositions)
        if not new_props:
            return None
        prop = random.choice(new_props)
        child_props = node.propositions | {prop}
        child = MCTSNode(child_props, self._kolmogorov_prior(child_props, symbol_freq))
        node.children.append(child)
        return child
    
    def _simulate(self, node, text):
        props = set(node.propositions)
        for _ in range(10):
            new = self._generate_new_propositions(text, props)
            if not new:
                break
            props.add(random.choice(new))
        return 0.0 if self._has_contradiction(props) else 1.0
    
    def _backpropagate(self, node, reward):
        while node:
            node.n += 1
            node.w += reward
            node = node.parent
    
    def _extract_propositions(self, text):
        props = set()
        props.update(self._extract_negations(text))
        props.update(self._extract_comparatives(text))
        props.update(self._extract_conditionals(text))
        props.update(self._extract_numerics(text))
        props.update(self._extract_causal(text))
        props.update(self._extract_ordering(text))
        return props
    
    def _extract_negations(self, text):
        return set(re.findall(r'\b(not|no|never|none) (\w+)', text.lower()))
    
    def _extract_comparatives(self, text):
        return set(re.findall(r'(\w+) (greater than|less than|more|fewer) (\w+)', text.lower()))
    
    def _extract_conditionals(self, text):
        return set(re.findall(r'if (.+?) then (.+?)(?:\.|,|$)', text.lower()))
    
    def _extract_numerics(self, text):
        return set(re.findall(r'(\w+)\s*[=:]\s*([\d.]+)', text.lower()))
    
    def _extract_causal(self, text):
        return set(re.findall(r'(\w+) (because|due to|leads to) (\w+)', text.lower()))
    
    def _extract_ordering(self, text):
        return set(re.findall(r'(\w+) (before|after|precede|follow) (\w+)', text.lower()))
    
    def _generate_new_propositions(self, text, existing):
        all_props = self._extract_propositions(text)
        return list(all_props - existing)
    
    def _kolmogorov_prior(self, props, symbol_freq):
        total = sum(symbol_freq.values())
        length = sum(-math.log2(symbol_freq.get(str(p), 1) / total) for p in props)
        return 2 ** (-length / 10)
    
    def _symbol_frequencies(self, text):
        freq = defaultdict(int)
        for word in re.findall(r'\w+', text.lower()):
            freq[word] += 1
        return freq
    
    def _has_contradiction(self, props):
        nums = {}
        for p in props:
            if isinstance(p, tuple) and len(p) == 2:
                nums[p[0]] = float(p[1]) if self._is_number(p[1]) else p[1]
        
        for p in props:
            if isinstance(p, tuple) and len(p) >= 3:
                if p[1] in ['greater than', 'more'] and p[0] in nums and p[2] in nums:
                    if nums[p[0]] <= nums[p[2]]:
                        return True
                if p[1] in ['less than', 'fewer'] and p[0] in nums and p[2] in nums:
                    if nums[p[0]] >= nums[p[2]]:
                        return True
        return False
    
    def _is_number(self, s):
        try:
            float(s)
            return True
        except:
            return False
    
    def _compute_numeric(self, prompt: str, answer: str):
        nums = re.findall(r'\b(\d+\.?\d*)\b', prompt + " " + answer)
        if len(nums) >= 2:
            try:
                floats = [float(n) for n in nums]
                if re.search(r'\bless than\b|\bsmaller\b|\b<\b', prompt.lower()):
                    return True
                if re.search(r'\bgreater than\b|\blarger\b|\b>\b', prompt.lower()):
                    return True
            except:
                pass
        return False
    
    def _compute_probability(self, prompt: str, answer: str):
        return bool(re.search(r'\bprobability\b|\bchance\b|\blikelihood\b', prompt.lower()))
    
    def _detect_structural_match(self, prompt: str, answer: str):
        p_neg = len(re.findall(r'\bnot\b|\bno\b', prompt.lower()))
        a_neg = len(re.findall(r'\bnot\b|\bno\b', answer.lower()))
        return (p_neg % 2) == (a_neg % 2)


class MCTSNode:
    def __init__(self, propositions, prior=0.0, parent=None):
        self.propositions = propositions
        self.prior = prior
        self.parent = parent
        self.children = []
        self.n = 0
        self.w = 0.0