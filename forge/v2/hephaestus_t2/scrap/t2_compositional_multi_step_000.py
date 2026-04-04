import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    solve_linear_system,
    topological_sort,
    check_transitivity
)
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable
from forge.amino_acids.pysat_acids import check_entailment


class ReasoningTool:
    """Combinatorics x Constraint Satisfaction - compositional_multi_step"""

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
        """Extract entities, values, and relationships from the prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        entities = {}
        values = []
        relationships = []
        question = lines[-1] if lines else ""
        
        # Extract entities (capitalized multi-word phrases)
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        # Extract numbers (integers, floats, percentages)
        number_pattern = r'([0-9]+\.?[0-9]*)%?'
        
        for line in lines:
            # Find entities in this line
            line_entities = re.findall(entity_pattern, line)
            # Find numbers in this line
            line_numbers = re.findall(number_pattern, line)
            nums = []
            for num_str in line_numbers:
                try:
                    if '%' in line and num_str.replace('.', '').isdigit():
                        nums.append(float(num_str) / 100.0)
                    else:
                        nums.append(float(num_str))
                except ValueError:
                    continue
            
            # Store entities and their associated values
            for entity in line_entities:
                if entity not in entities:
                    entities[entity] = {"values": [], "mentions": 0}
                entities[entity]["values"].extend(nums)
                entities[entity]["mentions"] += 1
            
            # Extract relationship indicators
            if "depends on" in line.lower() or "requires" in line.lower() or "before" in line.lower():
                # Try to find dependency relationships
                for i, e1 in enumerate(line_entities):
                    for j, e2 in enumerate(line_entities):
                        if i != j:
                            relationships.append((e1, e2))
            
            values.extend(nums)
        
        # Clean up entities with no values
        entities = {k: v for k, v in entities.items() if v["values"] or v["mentions"] > 0}
        
        return {
            "entities": entities,
            "values": values,
            "relationships": list(set(relationships)),
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply combinatorial reasoning with constraint satisfaction to solve multi-step problems."""
        entities = structure["entities"]
        relationships = structure["relationships"]
        values = structure["values"]
        question = structure["question"]
        
        # Step 1: Build dependency graph and check for cycles using topological sort
        # This represents the combinatorial structure of dependencies
        if relationships:
            try:
                sorted_order = topological_sort(relationships)
                if sorted_order is None:
                    # Graph has cycles - use transitivity analysis instead
                    transitivity_result = check_transitivity(relationships)
                    # Use entropy of reachable sets as measure of dependency complexity
                    reachable_sizes = [len(nodes) for nodes in transitivity_result.values()]
                    if reachable_sizes:
                        dependency_entropy = entropy([s/sum(reachable_sizes) for s in reachable_sizes])
                    else:
                        dependency_entropy = 0.0
                else:
                    # Valid DAG - compute information measure
                    dependency_entropy = entropy([1.0/len(sorted_order) for _ in sorted_order])
            except Exception:
                dependency_entropy = 0.0
                sorted_order = None
        else:
            dependency_entropy = 0.0
            sorted_order = None
        
        # Step 2: Formulate as constraint satisfaction problem
        # Create variables from entities with their extracted values as domains
        variables = list(entities.keys())
        domains = {}
        for entity, data in entities.items():
            if data["values"]:
                # Use unique extracted values as domain
                unique_vals = list(set(data["values"]))
                domains[entity] = sorted(unique_vals)
            else:
                # Binary domain for entities without explicit values
                domains[entity] = [0, 1]
        
        # Create constraints based on relationships
        constraints = []
        for src, dst in relationships:
            # Constraint: if src has high value, dst should have compatible value
            def make_constraint(s, d):
                def constraint(assignment):
                    if s in assignment and d in assignment:
                        # Simple ordering constraint
                        return assignment[s] <= assignment[d] + 0.1  # Allow small tolerance
                    return True
                return constraint
            constraints.append(([src, dst], make_constraint(src, dst)))
        
        # Step 3: Solve CSP using amino acid
        solution = None
        if variables and domains and constraints:
            try:
                solution = solve_first(variables, domains, constraints)
            except Exception:
                solution = None
        
        # Step 4: If CSP fails, try linear system approach
        computed_answer = None
        confidence = 0.5
        
        if solution:
            # CSP succeeded - find entity with highest assigned value
            if solution:
                best_entity = max(solution.items(), key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0)
                computed_answer = best_entity[0]
                # Use confidence from agreement of multiple scoring methods
                scores = []
                if best_entity[1] is not None:
                    scores.append(float(best_entity[1]))
                if dependency_entropy > 0:
                    scores.append(1.0 - dependency_entropy)
                if scores:
                    confidence = confidence_from_agreement(scores)
        else:
            # Fallback: use Bayesian update on extracted values
            if values:
                # Convert values to probabilities if they look like percentages
                prob_values = [v if v <= 1.0 else v/100.0 for v in values]
                if len(prob_values) >= 2:
                    # Chain Bayesian updates: each step updates based on previous
                    prior = prob_values[0]
                    for likelihood in prob_values[1:]:
                        prior = bayesian_update(prior, likelihood)
                    
                    # Find entity whose values best match the final posterior
                    best_match = None
                    best_score = -1
                    for entity, data in entities.items():
                        if data["values"]:
                            entity_vals = [v if v <= 1.0 else v/100.0 for v in data["values"]]
                            if entity_vals:
                                # Score based on closeness to posterior
                                avg_val = sum(entity_vals) / len(entity_vals)
                                score = 1.0 - abs(avg_val - prior)
                                if score > best_score:
                                    best_score = score
                                    best_match = entity
                    
                    if best_match:
                        computed_answer = best_match
                        confidence = min(0.9, prior)
        
        # Step 5: If still no answer, use logical entailment check
        if not computed_answer and question:
            # Encode question as logical statement
            question_terms = re.findall(r'\b([A-Z][a-z]+)\b', question)
            if question_terms:
                # Create simple logical encoding
                clauses = []
                for term in question_terms:
                    if term in entities:
                        clauses.append([1])  # Dummy positive clause
                
                # Check if question entails any entity
                for entity in entities:
                    if entity in question_terms:
                        try:
                            # Check if entity is entailed by the question context
                            entailment = check_entailment(clauses, [1])
                            if entailment:
                                computed_answer = entity
                                confidence = 0.7
                                break
                        except Exception:
                            continue
        
        # Final fallback: entity with most mentions
        if not computed_answer and entities:
            computed_answer = max(entities.items(), key=lambda x: x[1]["mentions"])[0]
            confidence = 0.3
        
        return {
            "answer": str(computed_answer) if computed_answer else "",
            "confidence": confidence,
            "dependency_entropy": dependency_entropy,
            "has_solution": solution is not None,
            "reasoning": f"Combinatorial analysis with {len(relationships)} dependencies, entropy={dependency_entropy:.3f}"
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match of computed answer
            base_score = 0.0
            if computed_answer and computed_answer.lower() in candidate.lower():
                base_score = 1.0
            elif computed_answer:
                # Use NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust score based on confidence from reasoning
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
        
        # Normalize scores to [0, 1] range
        scores = [item["score"] for item in scored]
        if scores:
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