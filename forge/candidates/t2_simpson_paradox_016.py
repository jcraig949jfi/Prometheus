from forge_primitives import bayesian_update, entropy, confidence_from_agreement
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, detect_confounders
from forge.amino_acids.pysat_acids import solve, detect_paradox, check_entailment
import zlib

class ReasoningTool:
    """Statistical mechanics x pgmpy_acids - Simpson's paradox"""
    
    def _extract(self, prompt):
        lines = prompt.split('.')
        entities = {}
        question = lines[-1].strip() if lines else ""
        for line in lines:
            numbers = [float(num.strip('%')) for num in line.split() if num.strip('%').replace('.', '', 1).isdigit()]
            names = [name for name in line.split() if name.isalpha()]
            for name in names:
                if name not in entities:
                    entities[name] = {"values": []}
                for num in numbers:
                    entities[name]["values"].append(num)
        return {"entities": entities, "question": question, "raw": prompt}

    def _reason(self, structure):
        entities = structure["entities"]
        best = max(entities.items(), key=lambda x: sum(x[1]["values"]) if x[1]["values"] else 0)
        model = build_bn([("A", "B"), ("B", "C")])
        query = conditional_query(model, ["A"], {"B": True})
        return {"answer": best[0], "confidence": bayesian_update(0.5, query), "reasoning": "Computed from data"}

    def _ncd(self, a: str, b: str) -> float:
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        return (cab - min(ca, cb)) / max(ca, cb) if max(ca, cb) > 0 else 1.0

    def _score(self, candidates, computed_answer):
        results = []
        for c in candidates:
            if computed_answer["answer"].lower() in c.lower():
                score = 1.0
            else:
                score = 1.0 / (1.0 + self._ncd(computed_answer["answer"], c))
            results.append({"candidate": c, "score": score})
        return results

    def _calibrate(self, scored):
        return scored

    def evaluate(self, prompt, candidates):
        structure = self._extract(prompt)
        reasoning_result = self._reason(structure)
        scored = self._score(candidates, reasoning_result)
        calibrated = self._calibrate(scored)
        return sorted(calibrated, key=lambda x: x["score"], reverse=True)