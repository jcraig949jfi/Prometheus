import re
import zlib
from typing import Dict, List, Any, Tuple
from forge_primitives import (
    modular_arithmetic,
    fencepost_count,
    temporal_order,
    solve_linear_system,
    information_sufficiency,
    confidence_from_agreement
)
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Combinatorics x Constraint Satisfaction - temporal_complex"""

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
        lines = [line.strip() for line in prompt.split('\n') if line.strip()]
        
        # Find all temporal entities (capitalized words that appear with times)
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        entities = set()
        for line in lines:
            entities.update(re.findall(entity_pattern, line))
        
        # Extract numerical values with units
        time_values = []
        value_pattern = r'(\d+)\s*(hours?|hrs?|minutes?|mins?|seconds?|secs?|days?|weeks?|months?|years?)'
        for line in lines:
            matches = re.findall(value_pattern, line.lower())
            for num, unit in matches:
                time_values.append((int(num), unit))
        
        # Extract temporal relations (before, after, later, earlier)
        relations = []
        for line in lines:
            if 'before' in line.lower() or 'after' in line.lower():
                # Find pairs of entities with before/after between them
                words = line.split()
                for i, word in enumerate(words):
                    if word.lower() in ['before', 'after']:
                        if i > 0 and i < len(words) - 1:
                            left = words[i-1]
                            right = words[i+1]
                            if left in entities and right in entities:
                                if word.lower() == 'before':
                                    relations.append((left, right))
                                else:
                                    relations.append((right, left))
        
        # Extract arithmetic constraints (sum, difference, ratio)
        constraints = []
        for line in lines:
            if 'total' in line.lower() or 'sum' in line.lower() or 'difference' in line.lower():
                # Look for equations like "A + B = 10 hours"
                if '=' in line:
                    parts = line.split('=')
                    if len(parts) == 2:
                        left, right = parts
                        # Find numbers on right side
                        right_nums = re.findall(r'\d+', right)
                        if right_nums:
                            constraints.append({
                                'expression': left.strip(),
                                'value': int(right_nums[0]),
                                'unit': self._extract_unit(right)
                            })
        
        # Find the question
        question = ""
        for line in reversed(lines):
            if '?' in line:
                question = line
                break
        
        return {
            'entities': list(entities),
            'time_values': time_values,
            'relations': relations,
            'constraints': constraints,
            'question': question,
            'raw_lines': lines
        }

    def _extract_unit(self, text: str) -> str:
        """Extract time unit from text."""
        units = ['hour', 'minute', 'second', 'day', 'week', 'month', 'year']
        text_lower = text.lower()
        for unit in units:
            if unit in text_lower:
                return unit
        return 'hour'  # default

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply combinatorial constraint reasoning to solve temporal problem."""
        entities = structure['entities']
        relations = structure['relations']
        constraints = structure['constraints']
        time_values = structure['time_values']
        
        # Convert all times to minutes for consistent arithmetic
        base_units = []
        for value, unit in time_values:
            base_units.append(self._to_minutes(value, unit))
        
        # Use temporal_order primitive to get partial ordering
        temporal_edges = []
        for rel in relations:
            temporal_edges.append((rel[0], rel[1], 'before'))
        
        ordered_events = []
        if temporal_edges:
            try:
                ordered_events = temporal_order(temporal_edges)
            except Exception:
                ordered_events = []
        
        # Apply combinatorial reasoning: treat as constraint satisfaction problem
        # Variables are the entities, domains are possible time values
        variables = entities
        domains = {}
        
        # Create domains based on extracted values
        if base_units:
            min_val = min(base_units)
            max_val = max(base_units) * 2  # Allow some range
        else:
            min_val = 0
            max_val = 1000
        
        for var in variables:
            # Create domain of possible time values in minutes
            domain = list(range(min_val, min_val + 100, 5))  # 5-minute intervals
            domains[var] = domain
        
        # Build constraints for the CSP
        csp_constraints = []
        
        # 1. Temporal ordering constraints
        if ordered_events:
            for i in range(len(ordered_events) - 1):
                def order_constraint(vals, e1=ordered_events[i], e2=ordered_events[i+1]):
                    return vals[0] < vals[1]
                csp_constraints.append(([ordered_events[i], ordered_events[i+1]], order_constraint))
        
        # 2. Arithmetic constraints from prompt
        for constr in constraints:
            expr = constr['expression']
            target = constr['value']
            unit = constr['unit']
            target_minutes = self._to_minutes(target, unit)
            
            # Parse simple expressions like "A + B" or "A - B"
            if '+' in expr:
                parts = expr.split('+')
                if len(parts) == 2:
                    var1 = parts[0].strip()
                    var2 = parts[1].strip()
                    if var1 in variables and var2 in variables:
                        def sum_constraint(vals, t=target_minutes):
                            return abs(vals[0] + vals[1] - t) <= 5  # Allow small tolerance
                        csp_constraints.append(([var1, var2], sum_constraint))
            
            elif '-' in expr:
                parts = expr.split('-')
                if len(parts) == 2:
                    var1 = parts[0].strip()
                    var2 = parts[1].strip()
                    if var1 in variables and var2 in variables:
                        def diff_constraint(vals, t=target_minutes):
                            return abs(vals[0] - vals[1] - t) <= 5
                        csp_constraints.append(([var1, var2], diff_constraint))
        
        # 3. Use modular_arithmetic for cyclic time constraints (e.g., 24-hour clock)
        # Find if there are modulo operations mentioned
        has_modulo = any('mod' in line.lower() or 'remainder' in line.lower() 
                        for line in structure['raw_lines'])
        
        mod_result = None
        if has_modulo and len(base_units) >= 2:
            try:
                # Use modular_arithmetic primitive
                mod_result = modular_arithmetic(base_units[0], base_units[1], 60)  # mod 60 minutes
            except Exception:
                mod_result = None
        
        # 4. Use fencepost_count for interval problems
        # Check if problem involves counting intervals between events
        has_intervals = any('interval' in line.lower() or 'between' in line.lower() 
                           for line in structure['raw_lines'])
        
        fencepost_result = None
        if has_intervals and base_units:
            try:
                # Estimate number of segments from time values
                max_time = max(base_units) if base_units else 0
                segments = max(1, max_time // 30)  # Rough estimate
                fencepost_result = fencepost_count(segments, include_both_ends=True)
            except Exception:
                fencepost_result = None
        
        # 5. Use solve_linear_system if we have linear equations
        linear_eqs = []
        linear_vars = []
        for constr in constraints:
            if '+' in constr['expression'] or '-' in constr['expression']:
                # Try to extract linear equation
                try:
                    # Simple parsing for A + B = C type
                    expr = constr['expression']
                    if '+' in expr:
                        parts = expr.split('+')
                        if len(parts) == 2:
                            var1 = parts[0].strip()
                            var2 = parts[1].strip()
                            if var1 in variables and var2 in variables:
                                # Create equation: 1*x1 + 1*x2 = target
                                if var1 not in linear_vars:
                                    linear_vars.append(var1)
                                if var2 not in linear_vars:
                                    linear_vars.append(var2)
                                
                                coeffs = [0] * len(linear_vars)
                                coeffs[linear_vars.index(var1)] = 1
                                coeffs[linear_vars.index(var2)] = 1
                                target_min = self._to_minutes(constr['value'], constr['unit'])
                                linear_eqs.append((coeffs, target_min))
                except Exception:
                    pass
        
        linear_solution = None
        if len(linear_eqs) >= len(linear_vars) and linear_vars:
            try:
                A = [eq[0] + [0] * (len(linear_vars) - len(eq[0])) for eq in linear_eqs[:len(linear_vars)]]
                b = [eq[1] for eq in linear_eqs[:len(linear_vars)]]
                linear_solution = solve_linear_system(A, b)
            except Exception:
                linear_solution = None
        
        # 6. Use information_sufficiency to check if problem is well-posed
        n_unknowns = len(variables)
        n_constraints = len(csp_constraints) + len(linear_eqs)
        info_status = information_sufficiency(n_unknowns, n_constraints)
        
        # 7. Use constraint_acids amino acids to solve CSP
        solution = None
        if variables and domains and csp_constraints:
            try:
                # First try solve_first amino acid
                solution = solve_first(domains, csp_constraints)
            except Exception:
                solution = None
            
            # If solution found, check uniqueness with is_uniquely_solvable
            unique_check = False
            if solution is not None:
                try:
                    unique_check = is_uniquely_solvable(domains, csp_constraints)
                except Exception:
                    unique_check = False
        
        # Determine the answer based on reasoning
        computed_answer = ""
        confidence = 0.5
        
        # Priority 1: Use constraint solution if available
        if solution is not None and solution:
            # Find which entity has the most interesting value (not zero/minimum)
            non_zero_vals = {k: v for k, v in solution.items() if v > 0}
            if non_zero_vals:
                # Pick entity with median value
                sorted_vals = sorted(non_zero_vals.items(), key=lambda x: x[1])
                if sorted_vals:
                    median_idx = len(sorted_vals) // 2
                    computed_answer = f"{sorted_vals[median_idx][1]} minutes"
                    confidence = 0.8 if unique_check else 0.7
            else:
                computed_answer = f"{list(solution.values())[0]} minutes"
                confidence = 0.6
        
        # Priority 2: Use linear system solution
        elif linear_solution is not None and linear_vars:
            computed_answer = f"{round(linear_solution[0])} minutes"
            confidence = 0.75
        
        # Priority 3: Use modular arithmetic result
        elif mod_result is not None:
            computed_answer = f"{mod_result} minutes"
            confidence = 0.65
        
        # Priority 4: Use fencepost result
        elif fencepost_result is not None:
            computed_answer = f"{fencepost_result}"
            confidence = 0.6
        
        # Priority 5: Use information sufficiency to guide fallback
        else:
            if info_status == "determined":
                # If determined but no solution, use extracted values
                if base_units:
                    computed_answer = f"{sum(base_units) // len(base_units)} minutes"
                    confidence = 0.55
                else:
                    computed_answer = "Cannot determine"
                    confidence = 0.3
            else:
                computed_answer = "Insufficient information"
                confidence = 0.4
        
        # Use confidence_from_agreement to refine confidence
        confidence_sources = []
        if solution is not None:
            confidence_sources.append(0.8)
        if linear_solution is not None:
            confidence_sources.append(0.75)
        if mod_result is not None:
            confidence_sources.append(0.65)
        if fencepost_result is not None:
            confidence_sources.append(0.6)
        
        if confidence_sources:
            try:
                refined_confidence = confidence_from_agreement(confidence_sources)
                confidence = max(confidence, refined_confidence)
            except Exception:
                pass
        
        return {
            "answer": computed_answer,
            "confidence": min(confidence, 0.95),
            "reasoning": f"Applied combinatorial constraint solving with {len(csp_constraints)} constraints. Info status: {info_status}. Solution: {solution}",
            "raw_solution": solution,
            "linear_solution": linear_solution,
            "mod_result": mod_result,
            "fencepost_result": fencepost_result
        }

    def _to_minutes(self, value: int, unit: str) -> int:
        """Convert time value to minutes."""
        unit = unit.lower().rstrip('s')
        if unit == 'hour' or unit == 'hr':
            return value * 60
        elif unit == 'minute' or unit == 'min':
            return value
        elif unit == 'second' or unit == 'sec':
            return value // 60
        elif unit == 'day':
            return value * 24 * 60
        elif unit == 'week':
            return value * 7 * 24 * 60
        elif unit == 'month':
            return value * 30 * 24 * 60  # Approximation
        elif unit == 'year':
            return value * 365 * 24 * 60  # Approximation
        return value

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        results = []
        
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Use NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust score based on confidence
            adjusted_score = base_score * reasoning_result["confidence"]
            
            results.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score
            })
        
        return results

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

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        scores = [item["score"] for item in scored]
        if not scores:
            return scored
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score - min_score < 0.001:
            # All scores are nearly equal, differentiate slightly
            for i, item in enumerate(scored):
                item["score"] = 0.5 + (i * 0.01)
        else:
            # Normalize to [0, 1] range
            for item in scored:
                if max_score > min_score:
                    item["score"] = (item["score"] - min_score) / (max_score - min_score)
                else:
                    item["score"] = 0.5
        
        return scored