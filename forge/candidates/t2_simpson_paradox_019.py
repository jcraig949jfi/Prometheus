from forge_primitives import bayesian_update, entropy, confidence_from_agreement
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, detect_confounders
from forge.amino_acids.pysat_acids import solve, detect_paradox, check_entailment

class ReasoningTool:
    """Network Engineering x pgmpy_acids - Simpson Paradox"""
    
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
        # Find entity names and numerical values
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
        # Use Bayesian network to model relationships
        model = build_bn([(entity, "outcome") for entity in entities])
        # Compute conditional probabilities
        probs = {}
        for entity in entities:
            probs[entity] = conditional_query(model, ["outcome"], {entity: True})
        # Detect confounders
        confounders = detect_confounders(model, "outcome", list(entities.keys())[0])
        # Update probabilities using Bayes' rule
        updated_probs = {}
        for entity in entities:
            prior = probs[entity]
            likelihood = 0.5  # Assuming equal likelihood for simplicity
            updated_probs[entity] = bayesian_update(prior, likelihood)
        # Determine the entity with the highest probability
        best_entity = max(updated_probs, key=updated_probs.get)
        return {"answer": best_entity, "confidence": updated_probs[best_entity], "reasoning": "Bayesian network and conditional probability"}

    def _score(self, candidates, computed_answer):
        results = []
        for c in candidates:
            if computed_answer["answer"].lower() in c.lower():
                score = 1.0
            else:
                # Fallback: use entropy to compare similarity
                score = 1.0 / (1.0 + entropy([computed_answer["answer"], c]))
            results.append({"candidate": c, "score": score})
        return results

    def _calibrate(self, scored):
        # Use confidence from agreement to adjust scores
        agreements = [s["score"] for s in scored]
        confidence = confidence_from_agreement(agreements)
        calibrated = [{"candidate": s["candidate"], "score": s["score"] * confidence} for s in scored]
        return calibrated