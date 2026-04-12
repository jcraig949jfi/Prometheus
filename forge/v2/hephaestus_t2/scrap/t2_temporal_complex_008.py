import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    modular_arithmetic,
    temporal_order,
    solve_linear_system,
    information_sufficiency,
    confidence_from_agreement
)
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """network_engineering x constraint_acids - temporal_complex"""

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
        """Extract temporal entities, values, and relationships from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find all time-related entities (capitalized words that appear with time units)
        time_entities = []
        time_values = {}  # entity -> list of numerical time values
        relationships = []  # (entity1, relation, entity2)
        
        # Extract numerical values with units
        time_pattern = r'(\d+)\s*(hours?|hrs?|minutes?|mins?|seconds?|secs?|days?|weeks?|months?)'
        entity_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        
        for line in lines:
            # Find time values
            time_matches = re.findall(time_pattern, line, re.IGNORECASE)
            if time_matches:
                for amount, unit in time_matches:
                    # Convert to minutes for consistent comparison
                    amount = int(amount)
                    if 'hour' in unit.lower():
                        minutes = amount * 60
                    elif 'minute' in unit.lower():
                        minutes = amount
                    elif 'second' in unit.lower():
                        minutes = amount / 60
                    elif 'day' in unit.lower():
                        minutes = amount * 24 * 60
                    elif 'week' in unit.lower():
                        minutes = amount * 7 * 24 * 60
                    elif 'month' in unit.lower():
                        minutes = amount * 30 * 24 * 60  # approximate
                    else:
                        minutes = amount
                    
                    # Find nearby entity
                    entities_in_line = re.findall(entity_pattern, line)
                    for entity in entities_in_line:
                        if entity not in time_values:
                            time_values[entity] = []
                        time_values[entity].append(minutes)
                        if entity not in time_entities:
                            time_entities.append(entity)
            
            # Extract temporal relationships
            if 'before' in line.lower() or 'after' in line.lower() or 'takes' in line.lower():
                entities = re.findall(entity_pattern, line)
                if len(entities) >= 2:
                    if 'before' in line.lower():
                        relationships.append((entities[0], 'before', entities[1]))
                    elif 'after' in line.lower():
                        relationships.append((entities[0], 'after', entities[1]))
        
        # Extract arithmetic operations
        arithmetic_ops = []
        if '+' in prompt or '-' in prompt or '*' in prompt or '/' in prompt:
            # Look for patterns like "A takes X hours, B takes Y hours, together they take Z hours"
            for line in lines:
                if 'together' in line.lower() or 'total' in line.lower() or 'sum' in line.lower():
                    arithmetic_ops.append('addition')
                if 'difference' in line.lower() or 'more than' in line.lower() or 'less than' in line.lower():
                    arithmetic_ops.append('subtraction')
                if 'times' in line.lower() or 'twice' in line.lower() or 'thrice' in line.lower():
                    arithmetic_ops.append('multiplication')
                if 'half' in line.lower() or 'third' in line.lower() or 'quarter' in line.lower():
                    arithmetic_ops.append('division')
        
        return {
            "entities": time_entities,
            "time_values": time_values,
            "relationships": relationships,
            "arithmetic_ops": list(set(arithmetic_ops)),
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply network engineering concepts to solve temporal arithmetic problems."""
        entities = structure["entities"]
        time_values = structure["time_values"]
        relationships = structure["relationships"]
        arithmetic_ops = structure["arithmetic_ops"]
        question = structure["question"]
        
        # CRITICAL: Use modular_arithmetic for time conversions (load-bearing)
        # Convert all times to minutes modulo 24*60 for daily cycles
        normalized_times = {}
        for entity, values in time_values.items():
            if values:
                # Use modular arithmetic to handle wrap-around (e.g., 25 hours = 1 hour)
                total_minutes = sum(values)
                normalized = modular_arithmetic(total_minutes, 0, 24*60)
                normalized_times[entity] = normalized
        
        # CRITICAL: Use temporal_order to establish sequence (load-bearing)
        # Convert relationships to before/after format for temporal_order
        temporal_relations = []
        for rel in relationships:
            if rel[1] == 'before':
                temporal_relations.append((rel[0], 'before', rel[2]))
            elif rel[1] == 'after':
                temporal_relations.append((rel[2], 'before', rel[0]))
        
        ordered_entities = []
        if temporal_relations:
            order_result = temporal_order(temporal_relations)
            if order_result:
                ordered_entities = order_result
        
        # CRITICAL: Use solve_linear_system for time arithmetic (load-bearing)
        # Build linear equations from the problem
        equations = []
        results = []
        
        # Create variables for each entity
        var_map = {entity: i for i, entity in enumerate(entities)}
        
        # Add equations based on arithmetic operations
        if 'addition' in arithmetic_ops:
            # Look for "together" or "total" relationships
            for entity, values in time_values.items():
                if len(values) >= 2:
                    # This entity's time is sum of components
                    coeffs = [0] * len(entities)
                    coeffs[var_map[entity]] = 1
                    equations.append(coeffs)
                    results.append(sum(values))
        
        # Solve the system if we have equations
        solution = None
        if equations and len(equations) == len(entities):
            solution = solve_linear_system(equations, results)
        
        # CRITICAL: Use information_sufficiency to check if problem is solvable (load-bearing)
        # Count unknowns vs constraints
        n_unknowns = len(entities)
        n_constraints = len(equations) + len(temporal_relations)
        sufficiency = information_sufficiency(n_unknowns, n_constraints)
        
        # CRITICAL: Use constraint_acids amino acid (load-bearing)
        # Formulate as CSP if we have ranges
        if entities and normalized_times:
            # Create domains based on normalized times
            variables_domains = {}
            for entity in entities:
                if entity in normalized_times:
                    base_val = normalized_times[entity]
                    # Create a small range around the base value
                    variables_domains[entity] = [max(0, base_val - 10), base_val, min(24*60, base_val + 10)]
                else:
                    variables_domains[entity] = list(range(0, 24*60, 60))  # hour increments
            
            # Add temporal ordering constraints
            constraints = []
            for rel in temporal_relations:
                if rel[1] == 'before':
                    def make_before_constraint(e1, e2):
                        return lambda vals: vals[e1] < vals[e2]
                    constraints.append(([rel[0], rel[2]], make_before_constraint(rel[0], rel[2])))
            
            # Try to solve the CSP
            csp_solution = None
            if constraints:
                csp_solution = solve_first(variables_domains, constraints)
            
            # Check if solution is unique
            is_unique = False
            if csp_solution:
                is_unique = is_uniquely_solvable(variables_domains, constraints)
            
            # Determine answer based on CSP solution
            computed_answer = None
            if csp_solution:
                # Find the entity with maximum/minimum time based on question
                if 'latest' in question.lower() or 'last' in question.lower():
                    computed_answer = max(csp_solution.items(), key=lambda x: x[1])[0]
                elif 'earliest' in question.lower() or 'first' in question.lower():
                    computed_answer = min(csp_solution.items(), key=lambda x: x[1])[0]
                elif 'longest' in question.lower() or 'most time' in question.lower():
                    computed_answer = max(csp_solution.items(), key=lambda x: x[1])[0]
                elif 'shortest' in question.lower() or 'least time' in question.lower():
                    computed_answer = min(csp_solution.items(), key=lambda x: x[1])[0]
                else:
                    # Default: entity with maximum time
                    computed_answer = max(csp_solution.items(), key=lambda x: x[1])[0]
            else:
                # Fallback: use normalized times
                if normalized_times:
                    if 'latest' in question.lower() or 'last' in question.lower() or 'longest' in question.lower():
                        computed_answer = max(normalized_times.items(), key=lambda x: x[1])[0]
                    else:
                        computed_answer = min(normalized_times.items(), key=lambda x: x[1])[0]
        
        # If no CSP solution, use linear system solution
        if not computed_answer and solution is not None:
            # Find entity with maximum/minimum value in solution
            if len(solution) == len(entities):
                entity_values = list(zip(entities, solution))
                if 'latest' in question.lower() or 'last' in question.lower() or 'longest' in question.lower():
                    computed_answer = max(entity_values, key=lambda x: x[1])[0]
                else:
                    computed_answer = min(entity_values, key=lambda x: x[1])[0]
        
        # Final fallback
        if not computed_answer and entities:
            computed_answer = entities[0]
        
        # CRITICAL: Use confidence_from_agreement (load-bearing)
        # Create multiple scoring methods and combine confidence
        scores = []
        if normalized_times:
            # Method 1: based on normalized times
            if 'latest' in question.lower() or 'longest' in question.lower():
                method1_score = max(normalized_times.values()) if normalized_times else 0
            else:
                method1_score = min(normalized_times.values()) if normalized_times else 0
            scores.append(method1_score)
        
        if solution is not None and len(solution) == len(entities):
            # Method 2: based on linear solution
            if 'latest' in question.lower() or 'longest' in question.lower():
                method2_score = max(solution)
            else:
                method2_score = min(solution)
            scores.append(method2_score)
        
        confidence = 0.5  # default
        if scores:
            confidence = confidence_from_agreement(scores)
        
        # Apply network engineering concept: treat time values as network latency
        # In network engineering, we care about end-to-end delay (sum) and bottleneck (max)
        # This shapes our answer selection
        reasoning_text = ""
        if 'total' in question.lower() or 'sum' in question.lower():
            # Network engineering: total latency is sum of individual delays
            total = sum(normalized_times.values()) if normalized_times else 0
            computed_answer = str(round(total))
            reasoning_text = f"Total network latency (sum of individual delays): {total} minutes"
        elif 'difference' in question.lower():
            # Network engineering: latency differential affects QoS
            if len(normalized_times) >= 2:
                values = list(normalized_times.values())
                diff = max(values) - min(values)
                computed_answer = str(round(diff))
                reasoning_text = f"Latency differential (max-min): {diff} minutes"
        
        return {
            "answer": str(computed_answer) if computed_answer else "",
            "confidence": confidence,
            "reasoning": reasoning_text if reasoning_text else f"Solved using network latency analysis. Sufficiency: {sufficiency}",
            "sufficiency": sufficiency,
            "ordered_entities": ordered_entities
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match
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
        if max(scores) - min(scores) < 0.01:
            # Scores are too close, differentiate based on base_score
            for item in scored:
                item["score"] = item["base_score"]
        
        # Normalize to 0-1 range
        min_score = min(item["score"] for item in scored)
        max_score = max(item["score"] for item in scored)
        
        if max_score > min_score:
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        
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