from forge_primitives import entropy, confidence_from_agreement, bayesian_update
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, detect_confounders
from forge.amino_acids.pysat_acids import solve, detect_paradox, check_entailment

class ReasoningTool:
    """Graph theory x pgmpy_acids - Simpson's paradox"""
    
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
        # Parse sentences to find entities and their values
        lines = prompt.split('.')
        entities = {}
        question = lines[-1].strip() if lines else ""
        for line in lines:
            # Extract numbers
            numbers = [float(num.strip('%')) for num in line.split() if num.endswith('%')]
            # Extract entity names (capitalized multi-word phrases)
            names = [name for name in line.split() if name.istitle()]
            for name in names:
                if name not in entities:
                    entities[name] = {"values": []}
                for num in numbers:
                    entities[name]["values"].append(num)
        return {"entities": entities, "question": question, "raw": prompt}

    def _reason(self, structure):
        entities = structure["entities"]
        # Compare values for each entity to determine which is better
        # Use amino acids to build a formal model if the relationship is causal
        # The answer is a SPECIFIC ENTITY NAME from the prompt
        best = max(entities.items(), key=lambda x: x[1]["values"][-1] if x[1]["values"] else 0)
        model = build_bn([(best[0], entity) for entity in entities])
        confounder = detect_confounders(model, best[0], list(entities.keys())[1])
        if confounder:
            # Adjust for confounder
            adjusted_prob = conditional_query(model, [best[0]], {confounder: True})
            return {"answer": best[0], "confidence": adjusted_prob, "reasoning": "Adjusted for confounder"}
        else:
            # No confounder, use Bayesian update
            prior = 0.5
            likelihood = entropy([entity["values"][-1] for entity in entities.values()])
            posterior = bayesian_update(prior, likelihood)
            return {"answer": best[0], "confidence": posterior, "reasoning": "Bayesian update"}

    def _score(self, candidates, computed_answer):
        import zlib
        def _ncd(a: str, b: str) -> float:
            ca = len(zlib.compress(a.encode()))
            cb = len(zlib.compress(b.encode()))
            cab = len(zlib.compress((a + " " + b).encode()))
            return (cab - min(ca, cb)) / max(ca, cb) if max(ca, cb) > 0 else 1.0

        results = []
        for c in candidates:
            # Primary: check if computed answer appears in candidate text
            if computed_answer["answer"].lower() in c.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity
                score = 1.0 / (1.0 + _ncd(computed_answer["answer"], c))
            results.append({"candidate": c, "score": score})
        return results

    def _calibrate(self, scored):
        # Use confidence_from_agreement to calibrate scores
        agreement = [score["score"] for score in scored]
        confidence = confidence_from_agreement(agreement)
        calibrated = [{"candidate": score["candidate"], "score": score["score"] * confidence} for score in scored]
        return calibrated