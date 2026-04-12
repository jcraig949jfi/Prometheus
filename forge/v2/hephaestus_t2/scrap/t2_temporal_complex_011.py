import re
import zlib
from typing import Dict, List, Any

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    solve_linear_system,
    modular_arithmetic,
    temporal_order,
    expected_value
)
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Behavioral Economics x Constraint Satisfaction - temporal_complex"""

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
        """Extract temporal entities, values, and constraints from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find time-related entities (capitalized phrases that appear with time units)
        time_entities = []
        time_values = {}  # entity -> list of (value, unit)
        constraints = []
        
        # Look for time patterns: "X hours", "Y minutes", "Z days", etc.
        time_patterns = [
            (r'(\d+\.?\d*)\s*hours?', 'hours'),
            (r'(\d+\.?\d*)\s*minutes?', 'minutes'),
            (r'(\d+\.?\d*)\s*days?', 'days'),
            (r'(\d+\.?\d*)\s*weeks?', 'weeks'),
            (r'(\d+\.?\d*)\s*months?', 'months'),
            (r'(\d+\.?\d*)\s*years?', 'years'),
            (r'(\d+\.?\d*)\s*seconds?', 'seconds')
        ]
        
        # Find capitalized entity names (potential subjects of temporal operations)
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        
        for line in lines:
            # Extract entities
            entities = re.findall(entity_pattern, line)
            for entity in entities:
                if entity not in time_entities and len(entity.split()) <= 3:
                    time_entities.append(entity)
            
            # Extract time values and associate with nearest entity
            for pattern, unit in time_patterns:
                matches = re.findall(pattern, line.lower())
                for match in matches:
                    value = float(match)
                    # Find the closest entity to this value in the line
                    if entities:
                        # Use the last entity mentioned before the number
                        entity = entities[-1] if entities else "Unknown"
                        if entity not in time_values:
                            time_values[entity] = []
                        time_values[entity].append((value, unit))
            
            # Extract temporal constraints: "before", "after", "takes longer than"
            if "before" in line.lower() or "after" in line.lower() or "takes longer" in line.lower():
                constraints.append(line)
        
        # Extract arithmetic operations: "sum", "difference", "total", "combined"
        arithmetic_ops = []
        for line in lines:
            if any(op in line.lower() for op in ["sum", "total", "combined", "together", "add"]):
                arithmetic_ops.append("add")
            if any(op in line.lower() for op in ["difference", "subtract", "less than", "more than"]):
                arithmetic_ops.append("subtract")
            if any(op in line.lower() for op in ["product", "times", "multiplied"]):
                arithmetic_ops.append("multiply")
            if any(op in line.lower() for op in ["quotient", "divided by", "ratio"]):
                arithmetic_ops.append("divide")
        
        return {
            "entities": time_entities,
            "time_values": time_values,
            "constraints": constraints,
            "arithmetic_ops": list(set(arithmetic_ops)),
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply behavioral economics principles to temporal reasoning."""
        entities = structure["entities"]
        time_values = structure["time_values"]
        constraints = structure["constraints"]
        arithmetic_ops = structure["arithmetic_ops"]
        
        # Behavioral Economics: People discount future values hyperbolically
        # We'll model time preferences using a discount factor
        
        # Convert all time values to a common unit (minutes)
        converted_values = {}
        for entity, values in time_values.items():
            total_minutes = 0
            for val, unit in values:
                if unit == 'hours':
                    total_minutes += val * 60
                elif unit == 'days':
                    total_minutes += val * 24 * 60
                elif unit == 'weeks':
                    total_minutes += val * 7 * 24 * 60
                elif unit == 'minutes':
                    total_minutes += val
                elif unit == 'seconds':
                    total_minutes += val / 60
            converted_values[entity] = total_minutes
        
        # Use T1 primitive: expected_value for temporal discounting
        # Hyperbolic discounting: value = 1 / (1 + k*t)
        # k is discount rate (behavioral parameter)
        k = 0.1  # moderate discount rate
        
        discounted_values = {}
        for entity, minutes in converted_values.items():
            # Convert minutes to days for discounting
            days = minutes / (24 * 60)
            discounted = 1 / (1 + k * days)
            discounted_values[entity] = discounted
        
        # Use T1 primitive: entropy to measure uncertainty in temporal estimates
        if discounted_values:
            probs = list(discounted_values.values())
            # Normalize to probabilities
            total = sum(probs)
            if total > 0:
                normalized = [p/total for p in probs]
                temporal_uncertainty = entropy(normalized)
            else:
                temporal_uncertainty = 0.0
        else:
            temporal_uncertainty = 0.0
        
        # Use amino acid: solve_first for temporal constraint satisfaction
        # Build a CSP for temporal ordering if we have constraints
        csp_solution = None
        if constraints and len(entities) >= 2:
            # Create variables for temporal positions
            variables = {entity: list(range(len(entities))) for entity in entities}
            
            # Define constraints based on "before"/"after" relationships
            csp_constraints = []
            for constraint in constraints:
                constraint_lower = constraint.lower()
                for i, e1 in enumerate(entities):
                    for j, e2 in enumerate(entities):
                        if i != j:
                            if e1.lower() in constraint_lower and e2.lower() in constraint_lower:
                                if "before" in constraint_lower:
                                    # e1 before e2
                                    csp_constraints.append(([e1, e2], lambda x, y: x < y))
                                elif "after" in constraint_lower:
                                    # e1 after e2
                                    csp_constraints.append(([e1, e2], lambda x, y: x > y))
            
            if csp_constraints:
                csp_solution = solve_first(variables, csp_constraints)
        
        # Use T1 primitive: solve_linear_system for temporal arithmetic
        # Look for equations like "X + Y = Z" or "X - Y = W"
        linear_system = None
        if arithmetic_ops and len(converted_values) >= 2:
            # Try to set up equations based on extracted values
            entity_list = list(converted_values.keys())
            if len(entity_list) >= 2:
                # Create a simple system: entity1 + entity2 = sum_of_first_two
                A = [[1, 1]]
                b = [converted_values[entity_list[0]] + converted_values[entity_list[1]]]
                linear_system = solve_linear_system(A, b)
        
        # Use T1 primitive: modular_arithmetic for time conversions
        # Convert minutes to hours and remaining minutes
        modular_results = {}
        for entity, minutes in converted_values.items():
            hours = minutes // 60
            remaining_minutes = minutes % 60
            # Use modular arithmetic to handle wrap-around (e.g., 90 minutes = 1 hour 30 minutes)
            mod_result = modular_arithmetic(int(hours), int(remaining_minutes), 60)
            modular_results[entity] = mod_result
        
        # Use T1 primitive: temporal_order if we have explicit ordering
        temporal_relations = []
        for constraint in constraints:
            for e1 in entities:
                for e2 in entities:
                    if e1 != e2 and e1.lower() in constraint.lower() and e2.lower() in constraint.lower():
                        if "before" in constraint.lower():
                            temporal_relations.append((e1, "before", e2))
                        elif "after" in constraint.lower():
                            temporal_relations.append((e1, "after", e2))
        
        ordered_events = []
        if temporal_relations:
            ordered_events = temporal_order(temporal_relations)
        
        # Determine the answer using behavioral economics: choose option with
        # highest discounted present value (hyperbolic discounting)
        computed_answer = None
        reasoning_explanation = ""
        
        if discounted_values:
            # Use amino acid: is_uniquely_solvable to check if CSP has unique solution
            unique_csp = False
            if constraints and len(entities) >= 2:
                variables = {entity: list(range(len(entities))) for entity in entities}
                csp_constraints = []
                for constraint in constraints:
                    constraint_lower = constraint.lower()
                    for i, e1 in enumerate(entities):
                        for j, e2 in enumerate(entities):
                            if i != j:
                                if e1.lower() in constraint_lower and e2.lower() in constraint_lower:
                                    if "before" in constraint_lower:
                                        csp_constraints.append(([e1, e2], lambda x, y: x < y))
                                    elif "after" in constraint_lower:
                                        csp_constraints.append(([e1, e2], lambda x, y: x > y))
                
                if csp_constraints:
                    unique_csp = is_uniquely_solvable(variables, csp_constraints)
            
            # Combine discounted value with CSP uniqueness
            best_entity = max(discounted_values.items(), key=lambda x: x[1])[0]
            
            # Use T1 primitive: confidence_from_agreement on multiple reasoning paths
            scores_to_agree = []
            
            # Path 1: Discounted value ranking
            if discounted_values:
                sorted_by_discount = sorted(discounted_values.items(), key=lambda x: x[1], reverse=True)
                if sorted_by_discount:
                    top_score = sorted_by_discount[0][1]
                    second_score = sorted_by_discount[1][1] if len(sorted_by_discount) > 1 else 0
                    agreement1 = top_score - second_score if top_score > 0 else 0
                    scores_to_agree.append(agreement1)
            
            # Path 2: Temporal ordering confidence
            if ordered_events:
                # First in order gets higher confidence
                if best_entity in ordered_events:
                    position = ordered_events.index(best_entity)
                    confidence_pos = 1.0 / (position + 1) if position >= 0 else 0
                    scores_to_agree.append(confidence_pos)
            
            # Path 3: CSP solution confidence
            if csp_solution and best_entity in csp_solution:
                # Check if best entity has a unique position
                entity_pos = csp_solution[best_entity]
                other_positions = [csp_solution[e] for e in csp_solution if e != best_entity]
                if entity_pos not in other_positions:
                    scores_to_agree.append(1.0)
                else:
                    scores_to_agree.append(0.5)
            
            confidence = confidence_from_agreement(scores_to_agree) if scores_to_agree else 0.5
            
            computed_answer = best_entity
            reasoning_explanation = (
                f"Behavioral economics: {best_entity} has highest discounted present value "
                f"(hyperbolic discounting with k={k}). "
                f"Temporal uncertainty: {temporal_uncertainty:.2f}. "
                f"CSP unique: {unique_csp}. "
                f"Modular conversion result: {modular_results.get(best_entity, 'N/A')}."
            )
        else:
            # Fallback: use entity with most time mentions
            if entities:
                computed_answer = entities[0]
                reasoning_explanation = "Fallback: first mentioned entity"
                confidence = 0.3
            else:
                computed_answer = "Unknown"
                reasoning_explanation = "No entities found"
                confidence = 0.1
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": reasoning_explanation,
            "discounted_values": discounted_values,
            "temporal_uncertainty": temporal_uncertainty,
            "csp_solution": csp_solution,
            "linear_system": linear_system,
            "modular_results": modular_results,
            "ordered_events": ordered_events
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact or partial match of computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Use NCD as fallback
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust by confidence from reasoning
            adjusted_score = base_score * confidence
            
            results.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score,
                "confidence": confidence
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using behavioral economics insights."""
        # Behavioral calibration: people overweight immediate outcomes
        # Apply a recency bias to scores
        if not scored:
            return scored
        
        # Sort by base score to identify top candidates
        sorted_by_base = sorted(scored, key=lambda x: x["base_score"], reverse=True)
        
        # Apply hyperbolic discounting to ranking positions
        calibrated = []
        for i, item in enumerate(scored):
            # Position discount: later positions are discounted
            position_discount = 1.0 / (1.0 + 0.5 * i)  # Hyperbolic discount of position
            
            # Combine with original score
            final_score = item["score"] * position_discount
            
            calibrated.append({
                "candidate": item["candidate"],
                "score": final_score,
                "base_score": item["base_score"],
                "confidence": item["confidence"]
            })
        
        return calibrated

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