from forge_primitives import bayesian_update, entropy, confidence_from_agreement
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, detect_confounders
from forge.amino_acids.pysat_acids import solve, detect_paradox, check_entailment
import zlib

class ReasoningTool:
    """Evolutionary biology x pgmpy_acids - Simpson's paradox"""
    
    def _extract(self, prompt):
        lines = prompt.split('.')
        entities = {}
        question = lines[-1].strip() if lines else ""
        for line in lines:
            numbers = [float(num.strip('%')) for num in line.split() if num.strip('%').replace('.', '', 1).isdigit()]
            names = [name for name in line.split() if name.isalpha() and name.istitle()]
            for name in names:
                if name not in entities:
                    entities[name] = {"values": []}
                for num in numbers:
                    entities[name]["values"].append(num)
        return {"entities": entities, "question": question, "raw": prompt}

    def _reason(self, structure):
        entities = structure["entities"]
        # Use bayesian update to compute the probability of each entity
        probabilities = {}
        for entity, values in entities.items():
            prior = 0.5  # Prior probability
            likelihood = 1.0  # Likelihood of the evidence
            false_positive = 0.0  # False positive rate
            probabilities[entity] = bayesian_update(prior, likelihood, false_positive)
        
        # Use entropy to determine the uncertainty of each entity
        uncertainties = {}
        for entity, prob in probabilities.items():
            uncertainties[entity] = entropy([prob, 1 - prob])
        
        # Use confidence_from_agreement to determine the confidence in each entity
        confidences = {}
        for entity, uncertainty in uncertainties.items():
            confidences[entity] = confidence_from_agreement([uncertainty, 1 - uncertainty])
        
        # Build a Bayesian network to model the relationships between entities
        edges = []
        for entity1 in entities:
            for entity2 in entities:
                if entity1 != entity2:
                    edges.append((entity1, entity2))
        model = build_bn(edges)
        
        # Use conditional query to compute the probability of each entity given the evidence
        evidence = {}
        for entity, values in entities.items():
            evidence[entity] = values[-1]  # Use the last value as evidence
        probabilities_given_evidence = {}
        for entity in entities:
            probabilities_given_evidence[entity] = conditional_query(model, [entity], evidence)
        
        # Use detect_confounders to identify common ancestors (confounders) of two variables
        confounders = {}
        for entity1 in entities:
            for entity2 in entities:
                if entity1 != entity2:
                    confounders[(entity1, entity2)] = detect_confounders(model, entity1, entity2)
        
        # Determine the best entity based on the probabilities and confidences
        best_entity = max(entities, key=lambda x: probabilities_given_evidence[x] * confidences[x])
        
        return {"answer": best_entity, "confidence": confidences[best_entity], "reasoning": "Computed from data"}

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