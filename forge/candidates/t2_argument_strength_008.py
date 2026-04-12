import re
import zlib
from typing import Dict, List, Any

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, solve_sat
from forge.amino_acids.pysat_acids import check_entailment


class ReasoningTool:
    """Thermochemistry x SAT entailment - argument_strength"""

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        # Phase 1: EXTRACT
        structure = self._extract(prompt)
        # Phase 2: REASON
        reasoning_result = self._reason(structure)
        # Phase 3: SCORE
        scored = self._score(candidates, reasoning_result)
        # Phase 4: CALIBRATE
        calibrated = self._calibrate(scored)
        return sorted(calibrated, key=lambda x: x["score"], reverse=True)

    def _extract(self, prompt: str) -> Dict[str, Any]:
        """Extract premises, conclusion, and entities from the prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        premises = []
        conclusion = None
        entities = set()
        
        # Find premises (usually statements before "Therefore" or "Thus")
        for line in lines:
            if line.lower().startswith(('therefore', 'thus', 'so', 'hence', 'consequently')):
                conclusion = line
                break
            else:
                premises.append(line)
        
        # If no explicit conclusion marker, last line is conclusion
        if conclusion is None and lines:
            conclusion = lines[-1]
            premises = lines[:-1]
        
        # Extract entities (capitalized words that appear multiple times)
        words = re.findall(r'\b([A-Z][a-z]+)\b', prompt)
        from collections import Counter
        word_counts = Counter(words)
        entities = {word for word, count in word_counts.items() if count > 1}
        
        # Convert premises to propositional variables
        # Simple mapping: each unique premise gets a variable
        premise_vars = {}
        var_counter = 1
        for prem in premises:
            if prem not in premise_vars:
                premise_vars[prem] = var_counter
                var_counter += 1
        
        # Map conclusion to variable
        conclusion_var = var_counter if conclusion else None
        
        return {
            "premises": premises,
            "conclusion": conclusion,
            "entities": list(entities),
            "premise_vars": premise_vars,
            "conclusion_var": conclusion_var,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use thermochemistry-inspired SAT reasoning to evaluate argument strength."""
        premises = structure["premises"]
        conclusion = structure["conclusion"]
        premise_vars = structure["premise_vars"]
        conclusion_var = structure["conclusion_var"]
        
        if not premises or conclusion is None:
            return {"answer": "Invalid", "confidence": 0.0, "reasoning": "Missing premises or conclusion"}
        
        # Convert to CNF clauses for SAT
        # Each premise is a clause with its variable positive
        premise_clauses = [[var] for var in premise_vars.values()]
        
        # Conclusion clause is the negation of conclusion variable
        # For entailment check: premises ∧ ¬conclusion
        if conclusion_var is not None:
            conclusion_clause = [-conclusion_var]
        else:
            conclusion_clause = []
        
        # THERMOCHEMISTRY SCAFFOLD: Model logical energy states
        # Strong arguments have low "entropy" (few satisfying assignments)
        # Valid arguments have high "activation energy" (hard to find counterexamples)
        
        # 1. First primitive: solve_sat to check if premises are consistent
        # This gives us the "ground state" energy
        model = solve_sat(premise_clauses, len(premise_vars))
        if model is None:
            # Premises are inconsistent - argument is vacuously valid but meaningless
            consistency_energy = float('inf')
            valid = True  # From false premises, anything follows
        else:
            # Count how many models satisfy premises (solution space size)
            # Use entropy as measure of premise uncertainty
            # 2. Second primitive: entropy of premise truth values
            premise_truths = [model.get(var, False) for var in premise_vars.values()]
            # Convert to probability distribution for entropy
            true_count = sum(premise_truths)
            false_count = len(premise_truths) - true_count
            total = len(premise_truths)
            if total > 0:
                probs = [true_count/total, false_count/total] if total > 0 else [0.5, 0.5]
                premise_entropy = entropy(probs)
            else:
                premise_entropy = 1.0
            
            # Higher entropy = more uncertainty in premises = weaker argument foundation
            consistency_energy = premise_entropy
        
        # 3. Amino acid: check_entailment for logical validity
        # This is the CORE load-bearing amino acid
        is_entailed = False
        if conclusion_clause and premise_clauses:
            entailment_result = check_entailment(premise_clauses, conclusion_clause)
            is_entailed = (entailment_result is True)  # True means premises entail conclusion
        
        # 4. Third primitive: bayesian_update for confidence based on entailment and consistency
        # Prior: 0.5 (uncertain)
        # Likelihood: high if entailed, low if not
        prior = 0.5
        likelihood = 0.9 if is_entailed else 0.1
        posterior = bayesian_update(prior, likelihood)
        
        # 5. Fourth primitive: confidence_from_agreement
        # Create multiple "scorers" based on different aspects
        scorers = []
        if is_entailed:
            scorers.append(0.9)  # Logical validity scorer
        else:
            scorers.append(0.1)
        
        if consistency_energy < 0.5:  # Low entropy premises
            scorers.append(0.8)
        else:
            scorers.append(0.3)
        
        if len(premises) >= 2:  # Multiple premises
            scorers.append(0.7)
        else:
            scorers.append(0.4)
        
        confidence = confidence_from_agreement(scorers) if scorers else 0.5
        
        # THERMOCHEMISTRY: Final "reaction energy" determines argument strength
        # ΔG = ΔH - TΔS, where:
        # ΔH = enthalpy (entailment result: -1 if valid, +1 if invalid)
        # ΔS = entropy (premise uncertainty)
        # T = temperature (fixed at 1.0)
        delta_H = -1.0 if is_entailed else 1.0
        delta_S = consistency_energy
        T = 1.0
        delta_G = delta_H - T * delta_S
        
        # Strong argument if ΔG < 0 (spontaneous reaction)
        is_strong = delta_G < 0
        
        # Determine answer
        if is_entailed:
            if is_strong:
                computed_answer = "Valid and strong"
            else:
                computed_answer = "Valid but weak"
        else:
            computed_answer = "Invalid"
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Entailment: {is_entailed}, Energy ΔG: {delta_G:.3f}",
            "is_entailed": is_entailed,
            "delta_G": delta_G,
            "premise_entropy": consistency_energy
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or containment
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust by confidence
            adjusted_score = base_score * confidence
            
            results.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score,
                "confidence": confidence
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Simple normalization to [0, 1] range
        scores = [item["score"] for item in scored]
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score > min_score:
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        else:
            # All scores equal
            for item in scored:
                item["score"] = 0.5
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance between two strings."""
        if not a or not b:
            return 1.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) > 0:
            return (cab - min(ca, cb)) / max(ca, cb)
        return 1.0