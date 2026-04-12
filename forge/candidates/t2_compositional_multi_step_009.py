import re
import zlib
from typing import Dict, List, Any

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    topological_sort,
    solve_linear_system,
    expected_value,
    information_sufficiency,
    modus_ponens,
    temporal_order,
    solve_constraints,
    solve_sat,
    counterfactual_intervention,
    check_transitivity,
    track_beliefs,
    sally_anne_test,
    dag_traverse,
    modular_arithmetic,
    fencepost_count,
    parity_check,
    negate,
    pigeonhole_check,
    coin_flip_independence,
    bat_and_ball,
    all_but_n,
    direction_composition,
)
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, detect_confounders
from forge.amino_acids.pysat_acids import solve, detect_paradox, check_entailment


class ReasoningTool:
    """chemical_kinetics x constraint_acids - compositional_multi_step"""

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
        number_pattern = r'([0-9]+\.?[0-9]*)\%?'
        
        for line in lines:
            # Find entities
            found_entities = re.findall(entity_pattern, line)
            # Find numbers
            found_numbers = re.findall(number_pattern, line)
            nums = [float(num) for num in found_numbers if num]
            
            for entity in found_entities:
                if entity not in entities:
                    entities[entity] = {"values": [], "mentions": 0}
                entities[entity]["values"].extend(nums)
                entities[entity]["mentions"] += 1
            
            values.extend(nums)
            
            # Extract relationships (if contains "before", "after", "causes", "affects")
            if any(word in line.lower() for word in ["before", "after", "then", "next"]):
                # Try to find temporal relationships
                parts = re.split(r'\b(before|after|then|next)\b', line.lower())
                if len(parts) >= 3:
                    rel = parts[1]
                    # Find entities around the relationship word
                    for i in range(0, len(parts), 2):
                        sub_ents = re.findall(entity_pattern, parts[i])
                        if sub_ents:
                            relationships.append((sub_ents[0], rel, sub_ents[1] if i+2 < len(parts) else ""))
        
        # Clean up entities with no values
        entities = {k: v for k, v in entities.items() if v["values"] or v["mentions"] > 0}
        
        return {
            "entities": entities,
            "values": values,
            "relationships": relationships,
            "question": question,
            "raw_lines": lines,
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply chemical kinetics reasoning to solve multi-step problems."""
        entities = structure["entities"]
        values = structure["values"]
        relationships = structure["relationships"]
        question = structure["question"]
        
        # Step 1: Use chemical kinetics analogy - treat reasoning steps as reaction steps
        # Each step has a "rate" (information flow) and "activation energy" (difficulty)
        # Multi-step problems require chaining through intermediate states
        
        # Extract numerical values for processing
        numeric_values = [v for v in values if isinstance(v, (int, float))]
        
        # CRITICAL PRIMITIVE 1: topological_sort for dependency ordering
        # Build dependency graph from relationships
        edges = []
        for rel in relationships:
            if len(rel) >= 2 and rel[0] and rel[2]:
                edges.append((rel[0], rel[2]))
        
        dependency_order = []
        if edges:
            dep_order = topological_sort(edges)
            if dep_order is not None:
                dependency_order = dep_order
                # Use the first entity in dependency order as key intermediate
                if dependency_order:
                    intermediate_entity = dependency_order[0]
                else:
                    intermediate_entity = list(entities.keys())[0] if entities else ""
            else:
                # Cyclic dependencies - use first entity
                intermediate_entity = list(entities.keys())[0] if entities else ""
        else:
            intermediate_entity = list(entities.keys())[0] if entities else ""
        
        # CRITICAL PRIMITIVE 2: solve_linear_system for rate equations
        # Build simple linear system from extracted values
        # Chemical kinetics: dx/dt = k1*A - k2*B, etc.
        if len(numeric_values) >= 2:
            # Create a 2x2 system: a*x + b*y = c, d*x + e*y = f
            # Use extracted values as coefficients
            if len(numeric_values) >= 6:
                a, b, c, d, e, f = numeric_values[:6]
                A = [[a, b], [d, e]]
                B = [c, f]
            else:
                # Pad with default values
                a, b = numeric_values[0], numeric_values[1] if len(numeric_values) > 1 else 1.0
                c = sum(numeric_values[:2])
                A = [[a, b], [b, a]]
                B = [c, c]
            
            solution = solve_linear_system(A, B)
            if solution is not None and len(solution) >= 1:
                linear_result = solution[0]
            else:
                linear_result = sum(numeric_values[:2]) / 2 if numeric_values else 0
        else:
            linear_result = sum(numeric_values) / len(numeric_values) if numeric_values else 0
        
        # CRITICAL AMINO ACID: solve_first for constraint satisfaction
        # Model multi-step reasoning as constraint satisfaction problem
        # Variables are reasoning steps, domains are possible intermediate results
        if entities:
            # Create CSP variables from entity names
            variables = list(entities.keys())[:3]  # Use up to 3 entities as variables
            if len(variables) < 2:
                variables = ["Step1", "Step2", "Step3"][:3]
            
            # Domains based on extracted values
            domains = {}
            for i, var in enumerate(variables):
                if i < len(numeric_values):
                    # Create domain around extracted values
                    base_val = numeric_values[i]
                    domains[var] = [base_val * 0.5, base_val, base_val * 1.5]
                else:
                    domains[var] = [0, 1, 2]
            
            # Constraints: later steps must be greater than earlier steps (progressive reasoning)
            constraints = []
            for i in range(len(variables)-1):
                var1, var2 = variables[i], variables[i+1]
                constraints.append(([var1, var2], lambda x, y: y > x))
            
            # Also add constraint that final step should be near linear_result
            if variables:
                final_var = variables[-1]
                target_val = linear_result
                constraints.append(([final_var], lambda x: abs(x - target_val) < target_val * 0.5))
            
            # Solve CSP
            csp_solution = solve_first(variables_domains=domains, constraints=constraints)
            
            if csp_solution:
                # Extract final value from CSP solution
                final_step_value = csp_solution.get(variables[-1]) if variables else None
                if final_step_value is not None:
                    csp_final = final_step_value
                else:
                    csp_final = linear_result
            else:
                csp_final = linear_result
        else:
            csp_final = linear_result
        
        # CRITICAL PRIMITIVE 3: bayesian_update for confidence in multi-step chain
        # Each step has reliability; combine using Bayesian updating
        if numeric_values:
            # Normalize values to probabilities
            normalized = [abs(v) / (max(abs(v) for v in numeric_values) if numeric_values else 1) 
                         for v in numeric_values[:3]]
            if len(normalized) >= 2:
                prior = normalized[0]
                likelihood = normalized[1]
                posterior = bayesian_update(prior, likelihood)
                
                # Third step if available
                if len(normalized) >= 3:
                    posterior = bayesian_update(posterior, normalized[2])
            else:
                posterior = normalized[0] if normalized else 0.5
        else:
            posterior = 0.5
        
        # CRITICAL PRIMITIVE 4: entropy to measure uncertainty in multi-step process
        # Chemical kinetics: entropy of reaction pathway
        if numeric_values:
            # Create probability distribution from normalized values
            abs_vals = [abs(v) for v in numeric_values[:4]]
            total = sum(abs_vals)
            if total > 0:
                probs = [v/total for v in abs_vals]
                uncertainty = entropy(probs)
            else:
                uncertainty = 1.0
        else:
            uncertainty = 1.0
        
        # Determine final answer based on reasoning chain
        # Chemical kinetics: product concentration after multi-step reaction
        if entities:
            # Combine CSP result with Bayesian posterior
            combined_result = csp_final * posterior
            
            # Find entity whose values best match the combined result
            best_entity = None
            best_diff = float('inf')
            
            for entity, data in entities.items():
                if data["values"]:
                    avg_val = sum(data["values"]) / len(data["values"])
                    diff = abs(avg_val - combined_result)
                    if diff < best_diff:
                        best_diff = diff
                        best_entity = entity
            
            if best_entity is None:
                best_entity = list(entities.keys())[0] if entities else ""
            
            # Use intermediate entity from dependency analysis if different
            if intermediate_entity and intermediate_entity in entities:
                # Check if intermediate entity should be answer based on question
                if "intermediate" in question.lower() or "step" in question.lower():
                    best_entity = intermediate_entity
            
            computed_answer = best_entity
        else:
            # No entities found, use numerical result
            computed_answer = str(round(combined_result, 2)) if 'combined_result' in locals() else "0"
        
        # Confidence from agreement of multiple methods
        scores_to_agree = []
        if 'linear_result' in locals():
            scores_to_agree.append(linear_result)
        if 'csp_final' in locals():
            scores_to_agree.append(csp_final)
        if 'posterior' in locals():
            scores_to_agree.append(posterior)
        
        if scores_to_agree:
            confidence = confidence_from_agreement(scores_to_agree)
        else:
            confidence = 0.5
        
        # Adjust confidence based on uncertainty (entropy)
        confidence = confidence * (1 - uncertainty * 0.5)
        
        return {
            "answer": computed_answer,
            "confidence": max(0.1, min(0.99, confidence)),
            "reasoning": f"Multi-step kinetics: dependency_order={dependency_order[:2]}, linear_result={linear_result:.2f}, csp_final={csp_final:.2f}, posterior={posterior:.2f}, uncertainty={uncertainty:.2f}",
            "intermediate": intermediate_entity,
            "numeric_result": csp_final if 'csp_final' in locals() else linear_result,
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact or substring match of computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Check if numeric result appears
                if 'numeric_result' in reasoning_result:
                    num_str = str(round(reasoning_result['numeric_result'], 2))
                    if num_str in candidate:
                        base_score = 0.8
                    else:
                        # Fallback to NCD similarity
                        base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
                else:
                    # Fallback to NCD similarity
                    base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Boost score if intermediate entity appears (for multi-step problems)
            if 'intermediate' in reasoning_result and reasoning_result['intermediate']:
                if reasoning_result['intermediate'].lower() in candidate.lower():
                    base_score = min(1.0, base_score * 1.2)
            
            # Apply confidence
            final_score = base_score * confidence
            
            results.append({
                "candidate": candidate,
                "score": final_score,
                "base_score": base_score,
                "confidence": confidence,
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Simple normalization to [0, 1] range
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
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)