from forge_primitives import bayesian_update, entropy, confidence_from_agreement
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, detect_confounders
from forge.amino_acids.pysat_acids import solve, detect_paradox, check_entailment

class ReasoningTool:
    """Hydrology x pgmpy_acids - simpson_paradox"""
    
    def evaluate(self, prompt, candidates):
        structure = self._extract(prompt)
        reasoning_result = self._reason(structure)
        scored = self._score(candidates, reasoning_result)
        calibrated = self._calibrate(scored)
        return sorted(calibrated, key=lambda x: x["score"], reverse=True)

    def _extract(self, prompt):
        lines = prompt.split('.')
        entities = {}
        question = lines[-1].strip() if lines else ""
        for line in lines:
            numbers = [float(num) for num in line.split() if num.replace('.', '', 1).isdigit()]
            names = [name for name in line.split() if name.istitle()]
            for name in names:
                if name not in entities:
                    entities[name] = {"values": []}
                for num in numbers:
                    entities[name]["values"].append(num)
        return {"entities": entities, "question": question, "raw": prompt}

    def _reason(self, structure):
        entities = structure["entities"]
        best = max(entities.items(), key=lambda x: sum(x[1]["values"]) if x[1]["values"] else 0)
        model = build_bn([(best[0], "outcome")], {})
        query = conditional_query(model, ["outcome"], {})
        answer = best[0]
        confidence = bayesian_update(0.5, query, 0.0)
        reasoning = "Computed from data"
        return {"answer": answer, "confidence": confidence, "reasoning": reasoning}

    def _score(self, candidates, computed_answer):
        results = []
        for c in candidates:
            if computed_answer["answer"].lower() in c.lower():
                score = 1.0
            else:
                score = 1.0 / (1.0 + entropy([len(c), len(computed_answer["answer"])]))
            results.append({"candidate": c, "score": score})
        return results

    def _calibrate(self, scored):
        return scored