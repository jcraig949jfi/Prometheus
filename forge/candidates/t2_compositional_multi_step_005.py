import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    topological_sort,
    solve_linear_system,
    information_sufficiency
)
from forge.amino_acids.pgmpy_acids import (
    build_bn,
    conditional_query,
    detect_confounders,
    do_calculus
)
from forge.amino_acids.constraint_acids import (
    solve_first,
    is_uniquely_solvable
)


class ReasoningTool:
    """Optics x Bayesian Networks & Constraint Solving - compositional_multi_step"""

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
        """Extract entities, values, relationships, and question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find entity names (capitalized multi-word phrases)
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        entities = {}
        for line in lines:
            matches = re.findall(entity_pattern, line)
            for ent in matches:
                if ent not in entities and len(ent) > 1:
                    entities[ent] = {"values": [], "mentions": 0}
        
        # Count mentions
        for ent in entities:
            entities[ent]["mentions"] = prompt.count(ent)
        
        # Extract numerical values and associate with entities
        number_pattern = r'([0-9]+\.?[0-9]*)%?'
        for line in lines:
            numbers = re.findall(number_pattern, line)
            if numbers:
                # Try to associate numbers with nearby entities
                nearby_ents = re.findall(entity_pattern, line)
                for ent in nearby_ents:
                    if ent in entities:
                        for num in numbers:
                            try:
                                val = float(num)
                                entities[ent]["values"].append(val)
                            except ValueError:
                                pass
        
        # Extract causal/temporal relationships
        relationships = []
        causal_words = ["causes", "affects", "influences", "leads to", "results in"]
        for line in lines:
            for word in causal_words:
                if word in line.lower():
                    # Find entities before and after causal word
                    parts = line.lower().split(word)
                    if len(parts) >= 2:
                        before = re.findall(entity_pattern, parts[0])
                        after = re.findall(entity_pattern, parts[1])
                        if before and after:
                            relationships.append((before[-1], after[0]))
        
        # Extract constraints/equations
        equations = []
        eq_pattern = r'([A-Za-z]+)\s*[=<>]+\s*([0-9\.]+)'
        for line in lines:
            eq_matches = re.findall(eq_pattern, line)
            equations.extend(eq_matches)
        
        return {
            "entities": entities,
            "relationships": relationships,
            "equations": equations,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Optical reasoning: treat multi-step inference as light propagation through lenses."""
        entities = structure["entities"]
        relationships = structure["relationships"]
        equations = structure["equations"]
        question = structure["question"]
        
        # Step 1: Build dependency graph (optical path)
        edges = []
        for rel in relationships:
            edges.append(rel)
        
        # Use topological_sort to determine processing order (critical path)
        if edges:
            try:
                order = topological_sort(edges)
                if order is None:
                    order = list(entities.keys())
            except Exception:
                order = list(entities.keys())
        else:
            order = list(entities.keys())
        
        # Step 2: Solve linear equations if present (refraction through lenses)
        variable_values = {}
        if equations:
            # Build linear system
            var_names = []
            coeff_matrix = []
            const_vector = []
            
            for eq in equations:
                var, const = eq
                if var not in var_names:
                    var_names.append(var)
                # Simple equation: var = const
                row = [0] * len(var_names)
                row[var_names.index(var)] = 1
                coeff_matrix.append(row)
                const_vector.append(float(const))
            
            if coeff_matrix and const_vector:
                solution = solve_linear_system(coeff_matrix, const_vector)
                if solution:
                    for i, var in enumerate(var_names):
                        if i < len(solution):
                            variable_values[var] = solution[i]
        
        # Step 3: Build Bayesian network for probabilistic reasoning (interference pattern)
        bn_result = None
        if edges:
            try:
                # Create simple CPDs based on extracted values
                cpd_specs = {}
                for node in entities:
                    if entities[node]["values"]:
                        avg_val = sum(entities[node]["values"]) / len(entities[node]["values"])
                        # Normalize to probability
                        prob = min(1.0, avg_val / 100.0) if avg_val > 1 else avg_val
                        cpd_specs[node] = [[prob, 1 - prob]]
                
                model = build_bn(edges, cpd_specs)
                if model:
                    # Query the most mentioned entity
                    target = max(entities.items(), key=lambda x: x[1]["mentions"])[0] if entities else None
                    if target:
                        evidence = {}
                        # Use other entities with values as evidence
                        for ent in entities:
                            if ent != target and entities[ent]["values"]:
                                avg_val = sum(entities[ent]["values"]) / len(entities[ent]["values"])
                                evidence[ent] = 1 if avg_val > 50 else 0
                        
                        if evidence:
                            bn_result = conditional_query(model, [target], evidence)
            except Exception:
                bn_result = None
        
        # Step 4: Constraint solving for combinatorial problems (diffraction grating)
        constraint_result = None
        if variable_values:
            # Create a CSP from variable values
            variables = list(variable_values.keys())
            domains = {var: [variable_values[var]] for var in variables}
            
            # Add constraints based on relationships
            constraints = []
            for rel in relationships:
                src, dst = rel
                if src in variables and dst in variables:
                    def greater_than(vals):
                        return vals[0] > vals[1]
                    constraints.append(([src, dst], greater_than))
            
            if constraints:
                constraint_result = solve_first(variables, domains, constraints)
        
        # Step 5: Information sufficiency check (optical resolution limit)
        n_unknowns = len([e for e in entities if not entities[e]["values"]])
        n_constraints = len(equations) + len(relationships)
        info_status = information_sufficiency(n_unknowns, n_constraints)
        
        # Step 6: Bayesian update for belief refinement (polarization filter)
        prior = 0.5
        likelihood = 0.7
        if entities:
            # Use entropy of entity values as likelihood measure
            all_values = []
            for ent in entities:
                all_values.extend(entities[ent]["values"])
            if all_values:
                # Normalize values to probabilities
                norm_vals = [v/100.0 for v in all_values if v > 0]
                if norm_vals:
                    likelihood = 1.0 - min(1.0, entropy(norm_vals))
        
        posterior = bayesian_update(prior, likelihood)
        
        # Step 7: Determine final answer using optical analogy
        # If BN gives result, use it (constructive interference)
        computed_answer = None
        confidence = 0.5
        
        if bn_result and isinstance(bn_result, dict):
            for key, val in bn_result.items():
                if isinstance(val, (int, float)):
                    # Find entity with closest value
                    best_ent = None
                    best_diff = float('inf')
                    for ent in entities:
                        if entities[ent]["values"]:
                            avg_val = sum(entities[ent]["values"]) / len(entities[ent]["values"])
                            diff = abs(avg_val - val * 100)
                            if diff < best_diff:
                                best_diff = diff
                                best_ent = ent
                    if best_ent:
                        computed_answer = best_ent
                        confidence = posterior
                        break
        
        # Fallback 1: Use constraint result (diffraction pattern)
        if not computed_answer and constraint_result:
            # Find entity with value matching constraint result
            for ent in entities:
                if entities[ent]["values"]:
                    avg_val = sum(entities[ent]["values"]) / len(entities[ent]["values"])
                    for var, val in constraint_result.items():
                        if abs(avg_val - val) < 10:  # Within tolerance
                            computed_answer = ent
                            confidence = posterior * 0.8
                            break
                if computed_answer:
                    break
        
        # Fallback 2: Use topological order (light path)
        if not computed_answer and order:
            # First entity in processing order (source)
            computed_answer = order[0]
            confidence = posterior * 0.6
        
        # Fallback 3: Most mentioned entity
        if not computed_answer and entities:
            computed_answer = max(entities.items(), key=lambda x: x[1]["mentions"])[0]
            confidence = posterior * 0.4
        
        # Final confidence calibration using agreement of multiple methods
        scores = []
        if bn_result:
            scores.append(confidence)
        if constraint_result:
            scores.append(confidence * 0.8)
        if order:
            scores.append(confidence * 0.6)
        
        if scores:
            final_confidence = confidence_from_agreement(scores)
        else:
            final_confidence = confidence
        
        # Ensure computed_answer is a string
        if computed_answer is None:
            computed_answer = "Unknown"
        
        return {
            "answer": str(computed_answer),
            "confidence": final_confidence,
            "reasoning": f"Optical multi-step inference: {info_status}, posterior={posterior:.3f}",
            "order": order,
            "posterior": posterior
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary: exact match or substring match
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Use NCD similarity
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
        
        # Normalize scores to [0, 1] range
        scores = [item["score"] for item in scored]
        if scores:
            min_score = min(scores)
            max_score = max(scores)
            if max_score > min_score:
                for item in scored:
                    item["score"] = (item["score"] - min_score) / (max_score - min_score)
            else:
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