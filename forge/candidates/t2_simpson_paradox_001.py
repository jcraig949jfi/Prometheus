from forge_primitives import bayesian_update, entropy, confidence_from_agreement
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, detect_confounders
from forge.amino_acids.pysat_acids import solve, detect_paradox, check_entailment

class ReasoningTool:
    """Neuroscience x pgmpy_acids - Simpson Paradox"""
    
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
            numbers = [float(num.strip('%')) for num in line.split() if num.endswith('%')]
            names = [name for name in line.split() if name.isalpha() and name.istitle()]
            for name in names:
                if name not in entities:
                    entities[name] = {"values": []}
                for num in numbers:
                    entities[name]["values"].append(num)
        return {"entities": entities, "question": question, "raw": prompt}

    def _reason(self, structure):
        entities = structure["entities"]
        best = max(entities.items(), key=lambda x: x[1]["values"][-1] if x[1]["values"] else 0)
        model = build_bn([(best[0], entity) for entity in entities])
        confounder = detect_confounders(model, best[0], list(entities.keys())[0])
        if confounder:
            # Adjust for confounder
            adjusted_prob = conditional_query(model, [best[0]], {confounder: True})
            answer = best[0] if adjusted_prob > 0.5 else list(entities.keys())[0]
        else:
            answer = best[0]
        return {"answer": answer, "confidence": 0.8, "reasoning": "Computed from data"}

    def _score(self, candidates, computed_answer):
        import zlib
        def ncd(a: str, b: str) -> float:
            ca = len(zlib.compress(a.encode()))
            cb = len(zlib.compress(b.encode()))
            cab = len(zlib.compress((a + " " + b).encode()))
            return (cab - min(ca, cb)) / max(ca, cb) if max(ca, cb) > 0 else 1.0
        
        results = []
        for c in candidates:
            if computed_answer.lower() in c.lower():
                score = 1.0
            else:
                score = 1.0 / (1.0 + ncd(computed_answer, c))
            results.append({"candidate": c, "score": score})
        return results

    def _calibrate(self, scored):
        return scored