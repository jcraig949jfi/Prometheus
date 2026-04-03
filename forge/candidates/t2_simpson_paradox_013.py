from forge_primitives import bayesian_update, entropy, confidence_from_agreement
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, detect_confounders
from forge.amino_acids.pysat_acids import solve, detect_paradox, check_entailment
import zlib

class ReasoningTool:
    """Number theory x pgmpy_acids - Simpson's paradox"""
    
    def _extract(self, prompt):
        lines = prompt.split('.')
        entities = {}
        question = lines[-1].strip() if lines else ""
        for line in lines:
            numbers = [float(num) for num in line.split() if num.replace('.', '', 1).isdigit()]
            names = [word for word in line.split() if word.istitle()]
            for name in names:
                if name not in entities:
                    entities[name] = {"values": []}
                for num in numbers:
                    entities[name]["values"].append(num)
        return {"entities": entities, "question": question, "raw": prompt}

    def _reason(self, structure):
        entities = structure["entities"]
        best = max(entities.items(), key=lambda x: sum(x[1]["values"]) if x[1]["values"] else 0)
        return {"answer": best[0], "confidence": 0.8, "reasoning": "Computed from data"}

    def _ncd(self, a: str, b: str) -> float:
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        return (cab - min(ca, cb)) / max(ca, cb) if max(ca, cb) > 0 else 1.0

    def _score_candidates(self, candidates, computed_answer):
        results = []
        for c in candidates:
            if computed_answer.lower() in c.lower():
                score = 1.0
            else:
                score = 1.0 / (1.0 + self._ncd(computed_answer, c))
            results.append({"candidate": c, "score": score})
        return results

    def _calibrate(self, scored):
        return scored

    def evaluate(self, prompt, candidates):
        structure = self._extract(prompt)
        reasoning_result = self._reason(structure)
        scored = self._score_candidates(candidates, reasoning_result["answer"])
        calibrated = self._calibrate(scored)
        return sorted(calibrated, key=lambda x: x["score"], reverse=True)