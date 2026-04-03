from forge_primitives import bayesian_update, entropy, confidence_from_agreement
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, detect_confounders
from forge.amino_acids.pysat_acids import solve, detect_paradox, check_entailment
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable
from forge.amino_acids.nashpy_acids import find_equilibria, is_dominated

class ReasoningTool:
    """Cryptography x pgmpy_acids - simpson_paradox"""
    
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
        model = build_bn([(best[0], entity) for entity in entities.keys()])
        answer = conditional_query(model, [best[0]], {})
        
        # Use cryptography concepts to analyze the conditional probability
        # For example, consider the encryption and decryption of the probabilities
        encrypted_prob = bayesian_update(answer, 0.5)
        decrypted_prob = bayesian_update(encrypted_prob, 0.5)
        
        return {"answer": best[0], "confidence": decrypted_prob, "reasoning": "Computed from data"}

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
        return scored