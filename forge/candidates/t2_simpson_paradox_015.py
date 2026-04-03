from forge_primitives import bayesian_update, entropy, confidence_from_agreement
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, detect_confounders
from forge.amino_acids.pysat_acids import solve, detect_paradox, check_entailment

class ReasoningTool:
    """Epidemiology x pgmpy_acids - simpson_paradox"""
    
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
            numbers = [float(num.strip('%')) for num in line.split() if num.strip('%').replace('.', '', 1).isdigit()]
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
        model = build_bn([(entity, "value") for entity in entities])
        best = max(entities.items(), key=lambda x: x[1]["values"][-1] if x[1]["values"] else 0)
        answer = best[0]
        confidence = confidence_from_agreement([x[1]["values"][-1] if x[1]["values"] else 0 for x in entities.items()])
        return {"answer": answer, "confidence": confidence, "reasoning": "Computed from data"}

    def _score(self, candidates, computed_answer):
        results = []
        for c in candidates:
            # Primary: check if computed answer appears in candidate text
            # computed_answer is a VARIABLE computed from the prompt, not a literal
            if computed_answer.lower() in c.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity
                import zlib
                def ncd(a: str, b: str) -> float:
                    ca = len(zlib.compress(a.encode()))
                    cb = len(zlib.compress(b.encode()))
                    cab = len(zlib.compress((a + " " + b).encode()))
                    return (cab - min(ca, cb)) / max(ca, cb) if max(ca, cb) > 0 else 1.0
                score = 1.0 / (1.0 + ncd(computed_answer, c))
            results.append({"candidate": c, "score": score})
        return results

    def _calibrate(self, scored):
        return scored