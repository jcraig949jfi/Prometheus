from forge_primitives import entropy, bayesian_update, confidence_from_agreement
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, detect_confounders, compare_conditional_marginal

class ReasoningTool:
    """Fluid dynamics x pgmpy_acids - Simpson paradox"""
    
    def evaluate(self, prompt, candidates):
        # Phase 1: Extract structure
        structure = self._extract(prompt)
        
        # Phase 2: Reason
        reasoning_result = self._reason(structure)
        
        # Phase 3: Score
        scored = self._score(candidates, reasoning_result)
        
        # Phase 4: Calibrate
        calibrated = self._calibrate(scored)
        
        return sorted(calibrated, key=lambda x: x["score"], reverse=True)

    def _extract(self, prompt):
        # Find percentages and associate with nearby entities
        lines = prompt.split('.')
        entities = {}
        question = lines[-1].strip() if lines else ""
        for line in lines:
            numbers = [float(num) for num in line.split() if num.replace('.', '', 1).replace('%', '', 1).isdigit()]
            names = [name for name in line.split() if name.isalpha() and name.istitle()]
            for name in names:
                if name not in entities:
                    entities[name] = {"values": []}
                for num in numbers:
                    entities[name]["values"].append(num)
        return {"entities": entities, "question": question, "raw": prompt}

    def _reason(self, structure):
        entities = structure["entities"]
        # Use fluid dynamics analogy: detect 'turbulence' (paradox) in data
        model = build_bn([(entity, "value") for entity in entities])
        for entity in entities:
            # Use conditional query to compute P(value | entity)
            prob = conditional_query(model, ["value"], {entity: True})
            # Check for Simpson's paradox using compare_conditional_marginal
            paradox = compare_conditional_marginal(model, "value", entity, True)
            if paradox:
                # If paradox detected, update confidence using Bayes' rule
                confidence = bayesian_update(0.5, prob, 0.1)  # Prior, likelihood, false positive rate
                return {"answer": entity, "confidence": confidence, "reasoning": "Simpson's paradox detected"}
        # If no paradox, use entropy to determine most uncertain entity
        entropies = {entity: entropy(entities[entity]["values"]) for entity in entities}
        max_entropy_entity = max(entropies, key=entropies.get)
        return {"answer": max_entropy_entity, "confidence": 0.8, "reasoning": "Most uncertain entity"}

    def _score(self, candidates, computed_answer):
        import zlib
        def ncd(a: str, b: str) -> float:
            ca = len(zlib.compress(a.encode()))
            cb = len(zlib.compress(b.encode()))
            cab = len(zlib.compress((a + " " + b).encode()))
            return (cab - min(ca, cb)) / max(ca, cb) if max(ca, cb) > 0 else 1.0
        
        results = []
        for c in candidates:
            if computed_answer["answer"].lower() in c.lower():
                score = 1.0
            else:
                score = 1.0 / (1.0 + ncd(computed_answer["answer"], c))
            results.append({"candidate": c, "score": score})
        return results

    def _calibrate(self, scored):
        # Calibrate scores using confidence_from_agreement
        agreements = [score["score"] for score in scored]
        calibrated_scores = confidence_from_agreement(agreements)
        for i, score in enumerate(scored):
            score["score"] = calibrated_scores[i]
        return scored