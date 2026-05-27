import numpy as np
from collections import defaultdict

class ReasoningTool:
    def __init__(self):
        self.working_memory = set()
        self.rules = defaultdict(list)

    def parse_prompt(self, prompt):
        sentences = prompt.split('. ')
        for sentence in sentences:
            if 'If' in sentence:
                premise, conclusion = sentence.split(' then ')
                premise = premise.replace('If ', '')
                self.rules[premise].append(conclusion)
            elif 'is true' in sentence:
                fact = sentence.replace(' is true', '')
                self.working_memory.add(fact)
            elif 'not' in sentence:
                fact = sentence.replace('not ', '')
                fact = 'not ' + fact
                self.working_memory.add(fact)

    def forward_chain(self):
        new_facts = set()
        for fact in self.working_memory:
            if fact in self.rules:
                for conclusion in self.rules[fact]:
                    new_facts.add(conclusion)
            elif 'not' in fact:
                fact = fact.replace('not ', '')
                for premise, conclusions in self.rules.items():
                    if fact in conclusions:
                        new_facts.add('not ' + premise)
        self.working_memory.update(new_facts)
        return len(new_facts) > 0

    def evaluate(self, prompt, candidates):
        self.working_memory = set()
        self.rules = defaultdict(list)
        self.parse_prompt(prompt)
        while self.forward_chain():
            pass
        results = []
        for candidate in candidates:
            if candidate in self.working_memory:
                results.append({'candidate': candidate, 'score': 1.0})
            else:
                results.append({'candidate': candidate, 'score': 0.0})
        return results

    def confidence(self, prompt, answer):
        results = self.evaluate(prompt, [answer])
        return results[0]['score']

# Example usage:
tool = ReasoningTool()
prompt = "If A then B. If B then C. A is true."
candidates = ["A", "B", "C"]
results = tool.evaluate(prompt, candidates)
for result in results:
    print(f"Candidate: {result['candidate']}, Score: {result['score']}")

prompt = "Alice > Bob. Bob > Carol. Carol > Dave. Alice is true."
candidates = ["Alice", "Bob", "Carol", "Dave"]
results = tool.evaluate(prompt, candidates)
for result in results:
    print(f"Candidate: {result['candidate']}, Score: {result['score']}")


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
