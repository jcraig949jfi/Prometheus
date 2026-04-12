import re
import zlib
from typing import Dict, List, Any

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, topological_sort
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """evolutionary_biology x constraint_acids - compositional_multi_step"""

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
        """Parse prompt to extract entities, values, and dependencies."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Extract entities (capitalized multi-word phrases)
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        entities = {}
        for line in lines:
            matches = re.findall(entity_pattern, line)
            for entity in matches:
                if entity not in entities:
                    entities[entity] = {"values": [], "dependencies": []}
        
        # Extract numerical values and associate with entities
        number_pattern = r'([0-9]+\.?[0-9]*)%?'
        for line in lines:
            numbers = re.findall(number_pattern, line)
            if numbers:
                # Find nearest entity in the same line
                matches = re.findall(entity_pattern, line)
                for entity in matches:
                    if entity in entities:
                        for num in numbers:
                            try:
                                entities[entity]["values"].append(float(num))
                            except ValueError:
                                pass
        
        # Extract dependency relationships (words like "requires", "depends on", "before")
        dependencies = []
        for line in lines:
            if "requires" in line.lower() or "depends on" in line.lower() or "before" in line.lower():
                entities_in_line = re.findall(entity_pattern, line)
                if len(entities_in_line) >= 2:
                    # Simple heuristic: first entity depends on second
                    dependencies.append((entities_in_line[0], entities_in_line[1]))
        
        # Extract constraints (words like "must", "cannot", "only if")
        constraints = []
        for line in lines:
            if "must" in line.lower() or "cannot" in line.lower() or "only if" in line.lower():
                entities_in_line = re.findall(entity_pattern, line)
                if entities_in_line:
                    constraints.append(line)
        
        return {
            "entities": entities,
            "dependencies": dependencies,
            "constraints": constraints,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Evolutionary biology approach: treat reasoning steps as species in an ecosystem.
        Each step must survive selection pressure (constraints) and dependencies form
        the food chain. The fittest solution emerges through constraint satisfaction."""
        
        entities = structure["entities"]
        dependencies = structure["dependencies"]
        constraints = structure["constraints"]
        
        # Evolutionary biology concept 1: Fitness landscape
        # Each entity's fitness is determined by how well it satisfies constraints
        # Use entropy to measure uncertainty in the solution space
        entity_names = list(entities.keys())
        
        if not entity_names:
            return {"answer": "", "confidence": 0.0, "reasoning": "No entities found"}
        
        # Build constraint satisfaction problem using evolutionary framework
        # Step 1: Define variables (entities) and domains (possible states)
        variables_domains = {}
        for entity in entity_names:
            # Domain: possible positions in the dependency chain (1..n)
            # This represents the "ecological niche" each entity occupies
            n = len(entity_names)
            variables_domains[entity] = list(range(1, n + 1))
        
        # Step 2: Define constraints based on dependencies
        # Each dependency creates a selection pressure
        csp_constraints = []
        
        # Constraint 1: Dependencies must be ordered (A before B)
        for a, b in dependencies:
            def make_dep_constraint(a_var, b_var):
                def dep_constraint(values):
                    # In evolutionary terms: a must occupy a niche before b
                    return values[a_var] < values[b_var]
                return dep_constraint
            csp_constraints.append(([a, b], make_dep_constraint(a, b)))
        
        # Constraint 2: All entities must have unique positions (competitive exclusion principle)
        def all_unique_constraint(values):
            # No two species can occupy the same niche
            positions = list(values.values())
            return len(set(positions)) == len(positions)
        csp_constraints.append((entity_names, all_unique_constraint))
        
        # Step 3: Use amino acid to find first valid solution (evolutionary stable state)
        solution = solve_first(variables_domains, csp_constraints)
        
        # Step 4: Check if solution is uniquely determined (evolutionary convergence)
        is_unique = is_uniquely_solvable(variables_domains, csp_constraints)
        
        # Step 5: Apply evolutionary biology metrics
        # Entropy of the solution space before constraints (diversity)
        initial_entropy = entropy([1.0/len(variables_domains[entity]) for entity in entity_names])
        
        # If solution found, compute posterior confidence using Bayesian update
        # Prior: uniform distribution over entities
        prior = 1.0 / len(entity_names) if entity_names else 0.0
        
        # Likelihood: solution exists and is unique
        likelihood = 1.0 if solution and is_unique else 0.5
        
        # False positive rate: 1 - uniqueness
        fp_rate = 0.0 if is_unique else 0.5
        
        posterior = bayesian_update(prior, likelihood, fp_rate)
        
        # Step 6: Determine answer based on evolutionary fitness
        # The entity with the highest fitness (lowest position in dependency chain)
        # is the "foundational species" in the ecosystem
        computed_answer = ""
        if solution:
            # Find entity with minimum position (most foundational)
            min_pos_entity = min(solution.items(), key=lambda x: x[1])[0]
            computed_answer = min_pos_entity
        else:
            # Fallback: use topological sort on dependencies
            if dependencies:
                sorted_entities = topological_sort(dependencies)
                if sorted_entities:
                    computed_answer = sorted_entities[0]
                else:
                    computed_answer = entity_names[0] if entity_names else ""
            else:
                computed_answer = entity_names[0] if entity_names else ""
        
        # Step 7: Compute confidence from multiple metrics (evolutionary stability)
        metrics = []
        if solution:
            metrics.append(1.0)  # Solution exists
        else:
            metrics.append(0.0)
        
        metrics.append(posterior)  # Bayesian confidence
        metrics.append(1.0 if is_unique else 0.5)  # Uniqueness
        
        # Use confidence_from_agreement to combine metrics (consensus in population)
        confidence = confidence_from_agreement(metrics)
        
        # Adjust confidence based on entropy (higher entropy = more uncertainty)
        confidence = confidence * (1.0 - min(initial_entropy, 1.0))
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Evolutionary constraint satisfaction: {len(dependencies)} dependencies, {len(constraints)} constraints. Solution {'unique' if is_unique else 'multiple'}.",
            "solution": solution,
            "is_unique": is_unique
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        results = []
        
        for candidate in candidates:
            # Primary: exact match or substring match of computed answer
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity
                score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Boost score if candidate mentions uniqueness when solution is unique
            if reasoning_result.get("is_unique", False):
                if "unique" in candidate.lower() or "only" in candidate.lower() or "single" in candidate.lower():
                    score = min(1.0, score * 1.2)
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Normalize scores to [0, 1] range
        scores = [item["raw_score"] for item in scored]
        if max(scores) > min(scores):
            normalized = [(s - min(scores)) / (max(scores) - min(scores)) for s in scores]
        else:
            normalized = [0.5 for _ in scores]
        
        # Apply softmax for final probabilities
        exp_scores = [2.71828 ** s for s in normalized]
        total = sum(exp_scores)
        if total > 0:
            calibrated_scores = [e / total for e in exp_scores]
        else:
            calibrated_scores = normalized
        
        for i, item in enumerate(scored):
            item["score"] = calibrated_scores[i]
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance."""
        if not a or not b:
            return 1.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) > 0:
            return (cab - min(ca, cb)) / max(ca, cb)
        return 1.0