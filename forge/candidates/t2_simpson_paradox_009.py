from forge_primitives import bayesian_update, entropy, confidence_from_agreement
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, detect_confounders
from forge.amino_acids.pysat_acids import solve, detect_paradox, check_entailment

class ReasoningTool:
    """Thermochemistry x pgmpy_acids - simpson_paradox"""
    
    def evaluate(self, prompt, candidates):
        # Phase 1: EXTRACT
        structure = self._extract(prompt)
        
        # Phase 2: REASON
        reasoning_result = self._reason(structure)
        
        # Phase 3: SCORE
        scored = self._score(candidates, reasoning_result)
        
        # Phase 4: CALIBRATE
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
        best = max(entities.items(), key=lambda x: x[1]["values"][-1] if x[1]["values"] else 0)
        model = build_bn([(best[0], entity) for entity in entities.keys() if entity != best[0]])
        confounder = detect_confounders(model, best[0], list(entities.keys())[0])
        query = conditional_query(model, [best[0]], {confounder: True})
        answer = best[0]
        confidence = query[best[0]]
        reasoning = "Computed from data using Bayesian network"
        return {"answer": answer, "confidence": confidence, "reasoning": reasoning}

    def _score(self, candidates, computed_answer):
        results = []
        for c in candidates:
            if computed_answer["answer"].lower() in c.lower():
                score = 1.0
            else:
                score = 1.0 / (1.0 + entropy([0.5, 0.5]))
            results.append({"candidate": c, "score": score})
        return results

    def _calibrate(self, scored):
        calibrated = []
        for result in scored:
            calibrated.append({"candidate": result["candidate"], "score": bayesian_update(0.5, result["score"])})
        return calibrated