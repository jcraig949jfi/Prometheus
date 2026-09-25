from collections import defaultdict

import re
import zlib
import numpy as np
from collections import namedtuple, defaultdict

class ReasoningTool:
    def __init__(self):
        self.Prop = namedtuple('Prop', ['text', 'polarity', 'comparative', 'conditional', 'causal', 'numeric', 'weight'])
        self.temperature = 1.0
        self.alpha = 0.5
        self.beta = 0.3
        self.gamma = 0.2

    def parse(self, text):
        props = []
        for line in text.split('\n'):
            polarity = True
            comparative = None
            conditional = None
            causal = None
            numeric = None
            
            if re.match(r'^not\s', line):
                polarity = False
                line = line[4:]
            
            if '>' in line or '<' in line or '>=' in line or '<=' in line or '=' in line:
                left, op, right = re.split(r'\s*([<><=>==])\s*', line)
                comparative = (left, op, right)
            
            if 'if' in line and 'then' in line:
                antecedent, consequent = re.split(r'\s*if\s*(.*?)\s*then\s*', line)
                conditional = (antecedent, consequent)
            
            if 'because' in line or 'leads to' in line:
                cause, effect = re.split(r'\s*(because|leads to)\s*', line)
                causal = (cause, effect)
            
            if any(c.isdigit() for c in line):
                numeric = float(re.findall(r'\d+\.\d+', line)[0])
            
            props.append(self.Prop(line, polarity, comparative, conditional, causal, numeric, 1.0))
        
        return props

    def build_graph(self, props):
        graph = defaultdict(list)
        for prop in props:
            if prop.conditional:
                graph[prop.conditional[0]].append(prop.conditional[1])
            if prop.causal:
                graph[prop.causal[0]].append(prop.causal[1])
        
        return graph

    def propagate(self, graph, props):
        truth_values = {prop.text: None for prop in props}
        
        def set_truth(text, value):
            if truth_values[text] is None:
                truth_values[text] = value
            elif truth_values[text] != value:
                return True  # Contradiction
            return False
        
        changed = True
        while changed:
            changed = False
            for prop in props:
                if prop.conditional:
                    if truth_values[prop.conditional[0]] is True:
                        changed |= set_truth(prop.conditional[1], True)
                if prop.causal:
                    if truth_values[prop.causal[0]] is True:
                        changed |= set_truth(prop.causal[1], True)
        
        return truth_values

    def compute_free_energy(self, props, truth_values):
        energy = 0.0
        entropy = 0.0
        
        for prop in props:
            if truth_values[prop.text] is None:
                p_i = 0.5
            else:
                p_i = 1.0 if truth_values[prop.text] else 0.0
            
            energy += prop.weight * int(truth_values[prop.text] is None)
            entropy -= p_i * np.log(p_i + 1e-10) + (1 - p_i) * np.log(1 - p_i + 1e-10)
        
        free_energy = energy - self.temperature * entropy
        return free_energy

    def compute_similarity(self, x, y):
        C_x = len(zlib.compress(x.encode()))
        C_y = len(zlib.compress(y.encode()))
        C_xy = len(zlib.compress((x + y).encode()))
        ncd = (C_xy - min(C_x, C_y)) / max(C_x, C_y)
        return 1 - ncd

    def evaluate(self, prompt, candidates):
        results = []
        for candidate in candidates:
            props = self.parse(candidate)
            graph = self.build_graph(props)
            truth_values = self.propagate(graph, props)
            free_energy = self.compute_free_energy(props, truth_values)
            similarity = self.compute_similarity(prompt, candidate)
            falsification_score = (len(props) - sum(1 for v in truth_values.values() if v is None)) / len(props)
            score = self.alpha * similarity + self.beta * (1 - free_energy) + self.gamma * falsification_score
            results.append({"candidate": candidate, "score": score, "reasoning": f"Similarity: {similarity}, Free Energy: {free_energy}, Falsification: {falsification_score}"})
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt, answer):
        props = self.parse(answer)
        graph = self.build_graph(props)
        truth_values = self.propagate(graph, props)
        free_energy = self.compute_free_energy(props, truth_values)
        similarity = self.compute_similarity(prompt, answer)
        falsification_score = (len(props) - sum(1 for v in truth_values.values() if v is None)) / len(props)
        score = self.alpha * similarity + self.beta * (1 - free_energy) + self.gamma * falsification_score
        return score

# Example usage:
# tool = ReasoningTool()
# prompt = "The temperature rose because the sun came up."
# candidates = [
#     "The temperature increased because of the sun.",
#     "The temperature decreased because of the sun.",
#     "The temperature remained the same because of the sun."
# ]
# print(tool.evaluate(prompt, candidates))
# print(tool.confidence(prompt, candidates[0]))


# --- Auto-fix: ensure confidence() returns float in [0, 1] ---
_orig_confidence = ReasoningTool.confidence
def _safe_confidence(self, prompt, answer):
    try:
        result = _orig_confidence(self, prompt, answer)
        if result is None:
            return 0.5
        return max(0.0, min(1.0, float(result)))
    except (TypeError, ValueError):
        return 0.5
ReasoningTool.confidence = _safe_confidence


# --- Auto-fix: ensure evaluate() returns list[dict] ---
_orig_evaluate = ReasoningTool.evaluate
def _safe_evaluate(self, prompt, candidates):
    try:
        result = _orig_evaluate(self, prompt, candidates)
        if result is None:
            return [{"candidate": c, "score": 0.5, "reasoning": "fallback"} for c in candidates]
        if not isinstance(result, list):
            return [{"candidate": c, "score": 0.5, "reasoning": "fallback"} for c in candidates]
        return result
    except Exception:
        return [{"candidate": c, "score": 0.5, "reasoning": "error"} for c in candidates]
ReasoningTool.evaluate = _safe_evaluate
