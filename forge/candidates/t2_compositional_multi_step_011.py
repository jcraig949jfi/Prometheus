import re
import zlib
from typing import Dict, List, Any

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    topological_sort,
    solve_constraints,
    modus_ponens,
    expected_value,
    information_sufficiency
)
from forge.amino_acids.constraint_acids import (
    solve_first,
    is_uniquely_solvable,
    check_consistency
)
from forge.amino_acids.pysat_acids import (
    check_entailment,
    detect_paradox
)


class ReasoningTool:
    """Category theory x Constraint satisfaction - compositional_multi_step"""

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
        """Extract entities, values, relationships, and the question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find entity names (capitalized phrases)
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        entities = {}
        for line in lines:
            matches = re.findall(entity_pattern, line)
            for entity in matches:
                if entity not in entities and len(entity.split()) <= 3:
                    entities[entity] = {"values": [], "relations": []}
        
        # Extract numerical values and associate with entities
        number_pattern = r'(\d+(?:\.\d+)?)%?'
        for line in lines:
            numbers = re.findall(number_pattern, line)
            if numbers:
                # Find the nearest entity to associate with
                for entity in entities:
                    if entity in line:
                        for num in numbers:
                            try:
                                value = float(num)
                                entities[entity]["values"].append(value)
                            except ValueError:
                                pass
        
        # Extract relationships (A causes B, A implies B, etc.)
        relations = []
        implication_pattern = r'(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b)\s+(?:causes|implies|leads to|affects)\s+(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b)'
        for line in lines:
            matches = re.findall(implication_pattern, line, re.IGNORECASE)
            for a, b in matches:
                if a in entities and b in entities:
                    relations.append((a, b))
                    entities[a]["relations"].append(b)
        
        # Extract constraints (if A then B, either X or Y)
        constraints = []
        constraint_pattern = r'if\s+(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b)\s+then\s+(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b)'
        for line in lines:
            matches = re.findall(constraint_pattern, line, re.IGNORECASE)
            for a, b in matches:
                if a in entities and b in entities:
                    constraints.append((a, b))
        
        return {
            "entities": entities,
            "relations": relations,
            "constraints": constraints,
            "question": question,
            "raw_lines": lines
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Category theory approach: compose reasoning steps as morphisms between problem states."""
        entities = structure["entities"]
        relations = structure["relations"]
        constraints = structure["constraints"]
        question = structure["question"]
        
        # Step 1: Build dependency graph from relations (morphism composition)
        # Use topological_sort to determine valid reasoning order
        sorted_entities = []
        if relations:
            try:
                sorted_result = topological_sort(relations)
                if sorted_result:
                    sorted_entities = sorted_result
            except Exception:
                sorted_entities = list(entities.keys())
        else:
            sorted_entities = list(entities.keys())
        
        # Step 2: Check if the system is uniquely solvable using constraint satisfaction
        # This represents checking if the limit/colimit exists uniquely
        is_unique = False
        if constraints:
            # Build CSP from constraints
            variables = list(entities.keys())
            domains = {var: ["True", "False"] for var in variables}
            
            def constraint_func(vars_vals):
                a_val, b_val = vars_vals
                # Implication: if A then B
                return not (a_val == "True" and b_val == "False")
            
            csp_constraints = []
            for a, b in constraints:
                csp_constraints.append(([a, b], constraint_func))
            
            # Check uniqueness using amino acid
            unique_check = is_uniquely_solvable(variables_domains=domains, constraints=csp_constraints)
            if unique_check is not None:
                is_unique = unique_check
            else:
                # Fallback using T1 primitive
                info_status = information_sufficiency(len(variables), len(constraints))
                is_unique = (info_status == "determined")
        
        # Step 3: Apply modus ponens reasoning chain (morphism composition)
        derived_facts = set()
        if constraints:
            # Convert constraints to implication premises
            premises = [(a, b) for a, b in constraints]
            # Start with facts from numerical values
            initial_facts = set()
            for entity, data in entities.items():
                if data["values"]:
                    avg_val = sum(data["values"]) / len(data["values"])
                    if avg_val > 50:  # Threshold for "True"
                        initial_facts.add(entity)
            
            # Apply modus ponens
            derived = modus_ponens(premises, initial_facts)
            if derived:
                derived_facts = derived
        
        # Step 4: Compute expected value of different reasoning paths
        outcomes = []
        for entity in entities:
            if entities[entity]["values"]:
                avg_val = sum(entities[entity]["values"]) / len(entities[entity]["values"])
                # Probability based on normalized value
                prob = avg_val / 100.0 if avg_val <= 100 else 1.0
                outcomes.append((prob, avg_val))
        
        expected_val = 0.0
        if outcomes:
            expected_val = expected_value(outcomes)
        
        # Step 5: Bayesian update on derived conclusions
        prior = 0.5  # Default prior
        likelihood = 0.0
        if derived_facts:
            # Compute likelihood based on number of derived facts
            likelihood = len(derived_facts) / len(entities) if entities else 0.0
        
        posterior = bayesian_update(prior, likelihood)
        
        # Step 6: Entropy of the reasoning state
        probs = []
        for entity in entities:
            if entities[entity]["values"]:
                avg = sum(entities[entity]["values"]) / len(entities[entity]["values"])
                probs.append(avg / 100.0)
        
        reasoning_entropy = 0.0
        if probs:
            # Normalize to distribution
            total = sum(probs)
            if total > 0:
                norm_probs = [p/total for p in probs]
                reasoning_entropy = entropy(norm_probs)
        
        # Step 7: Determine final answer using constraint solving
        computed_answer = ""
        if constraints and entities:
            # Try to solve the CSP
            variables = list(entities.keys())
            domains = {var: ["True", "False"] for var in variables}
            
            def constraint_impl(vars_vals):
                a_val, b_val = vars_vals
                return not (a_val == "True" and b_val == "False")
            
            csp_constraints = []
            for a, b in constraints:
                csp_constraints.append(([a, b], constraint_impl))
            
            # Use amino acid to solve
            solution = solve_first(variables_domains=domains, constraints=csp_constraints)
            
            if solution:
                # Find entity with value "True" that's mentioned in question
                true_entities = [e for e, val in solution.items() if val == "True"]
                if true_entities:
                    # Pick the one most relevant to question
                    for entity in true_entities:
                        if entity.lower() in question.lower():
                            computed_answer = entity
                            break
                    if not computed_answer:
                        computed_answer = true_entities[0]
                else:
                    # No true entities, pick based on values
                    best_entity = max(entities.items(), 
                                    key=lambda x: sum(x[1]["values"]) if x[1]["values"] else 0)
                    computed_answer = best_entity[0]
            else:
                # CSP unsolvable, use topological order
                if sorted_entities:
                    computed_answer = sorted_entities[0]
                else:
                    computed_answer = list(entities.keys())[0] if entities else ""
        else:
            # No constraints, use entity with highest average value
            if entities:
                best_entity = max(entities.items(), 
                                key=lambda x: sum(x[1]["values"]) if x[1]["values"] else 0)
                computed_answer = best_entity[0]
            else:
                computed_answer = ""
        
        # Step 8: Confidence from agreement of multiple reasoning methods
        scores = []
        if posterior > 0.5:
            scores.append(1.0)
        if expected_val > 50:
            scores.append(1.0)
        if reasoning_entropy < 0.5:  # Low entropy = more certain
            scores.append(1.0)
        if is_unique:
            scores.append(1.0)
        
        confidence = 0.5  # Default
        if scores:
            confidence = confidence_from_agreement(scores)
        
        # CRITICAL: computed_answer MUST be determined by primitive outputs
        # If posterior is low, we might need to reconsider
        if posterior < 0.3 and computed_answer:
            # Check consistency of answer with constraints
            if constraints:
                # Build SAT clauses for entailment check
                clauses = []
                var_map = {entity: i+1 for i, entity in enumerate(entities)}
                
                for a, b in constraints:
                    if a in var_map and b in var_map:
                        # A → B is ¬A ∨ B
                        clauses.append([-var_map[a], var_map[b]])
                
                # Check if answer being true is entailed
                if computed_answer in var_map:
                    answer_lit = var_map[computed_answer]
                    entailment = check_entailment(clauses, [answer_lit])
                    if entailment is False:
                        # Answer not entailed, pick different one
                        for entity in entities:
                            if entity != computed_answer and entity in var_map:
                                alt_lit = var_map[entity]
                                alt_entailment = check_entailment(clauses, [alt_lit])
                                if alt_entailment:
                                    computed_answer = entity
                                    break
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "entropy": reasoning_entropy,
            "posterior": posterior,
            "expected_value": expected_val,
            "is_unique": is_unique,
            "derived_facts": list(derived_facts),
            "sorted_order": sorted_entities
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring of computed answer
            if computed_answer and computed_answer.lower() in candidate.lower():
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
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        scores = [item["score"] for item in scored]
        if not scores:
            return scored
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score - min_score > 0:
            # Normalize to [0, 1] range
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        else:
            # All scores equal, assign uniform scores
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
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)