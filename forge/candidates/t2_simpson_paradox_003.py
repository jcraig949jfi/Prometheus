from forge_primitives import bayesian_update, entropy, confidence_from_agreement
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, detect_confounders
from forge.amino_acids.pysat_acids import solve, detect_paradox, check_entailment

class ReasoningTool:
    """Immunology x pgmpy_acids - Simpson Paradox"""
    
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
        # Find percentages and associate with nearby entities
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
        model = build_bn([(entity, "values") for entity in entities])
        result = conditional_query(model, ["values"], {})
        
        # Use amino acids to build a formal model if the relationship is causal
        confounders = detect_confounders(model, "values", list(entities.keys())[0])
        
        # Compute the answer
        best = max(entities.items(), key=lambda x: sum(x[1]["values"]) if x[1]["values"] else 0)
        
        return {"answer": best[0], "confidence": confidence_from_agreement([sum(vals) for vals in entities.values()]), "reasoning": "Computed from data"}

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