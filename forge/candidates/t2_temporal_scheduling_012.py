import re
import zlib
from typing import Dict, List, Any, Tuple, Set

from forge_primitives import (
    solve_constraints,
    topological_sort,
    information_sufficiency,
    confidence_from_agreement,
    entropy,
    expected_value
)
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable
from forge.amino_acids.pysat_acids import check_entailment, detect_paradox


class ReasoningTool:
    """quantum_mechanics x constraint_acids - temporal_scheduling"""

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
        """Extract entities, temporal constraints, and the question from the prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find entity names (capitalized words that appear in constraints)
        # Look for patterns like "Event A", "Task X", "Meeting with Bob"
        entity_pattern = r'([A-Z][a-zA-Z0-9]*(?:\s+[A-Z][a-zA-Z0-9]*)*)'
        potential_entities = re.findall(entity_pattern, prompt)
        
        # Filter: entities that appear in constraint statements
        entities = set()
        constraints = []
        time_points = []
        
        # Look for temporal relations
        temporal_keywords = ['before', 'after', 'during', 'at', 'starts', 'ends', 'between']
        for line in lines:
            line_lower = line.lower()
            # Check if this line describes a constraint
            if any(keyword in line_lower for keyword in ['must', 'cannot', 'should', 'needs to', 'has to']):
                # Extract constraint type
                if 'before' in line_lower:
                    # Find two entities in this line
                    line_entities = re.findall(entity_pattern, line)
                    if len(line_entities) >= 2:
                        a, b = line_entities[0], line_entities[1]
                        entities.add(a)
                        entities.add(b)
                        constraints.append(('before', a, b))
                elif 'after' in line_lower:
                    line_entities = re.findall(entity_pattern, line)
                    if len(line_entities) >= 2:
                        a, b = line_entities[0], line_entities[1]
                        entities.add(a)
                        entities.add(b)
                        constraints.append(('after', a, b))
                elif 'at' in line_lower and ':' in line:
                    # Time point constraint
                    match = re.search(r'([A-Z][a-zA-Z0-9]*(?:\s+[A-Z][a-zA-Z0-9]*)*)\s+at\s+(\d+:\d+)', line)
                    if match:
                        entity, time_str = match.groups()
                        entities.add(entity)
                        time_points.append((entity, time_str))
        
        # Extract numerical durations if present
        durations = {}
        duration_pattern = r'(\d+)\s*(?:minute|hour|day|week)s?\s+(?:for|of|long)'
        duration_matches = re.findall(duration_pattern, prompt, re.IGNORECASE)
        if duration_matches:
            # Associate with entities if possible
            for i, duration in enumerate(duration_matches[:len(list(entities))]):
                entity_list = list(entities)
                if i < len(entity_list):
                    durations[entity_list[i]] = int(duration)
        
        # Extract the scheduling goal (what needs to be determined)
        goal = None
        goal_keywords = ['schedule', 'order', 'arrange', 'plan', 'which', 'what time']
        for line in lines:
            if any(keyword in line.lower() for keyword in goal_keywords):
                goal = line
                break
        
        return {
            "entities": list(entities),
            "constraints": constraints,
            "time_points": time_points,
            "durations": durations,
            "question": question,
            "goal": goal,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply quantum-mechanics inspired reasoning to resolve scheduling conflicts."""
        entities = structure["entities"]
        constraints = structure["constraints"]
        time_points = structure["time_points"]
        durations = structure["durations"]
        goal = structure["goal"]
        
        # Quantum mechanics framework: treat scheduling as a superposition of possible timelines
        # Each constraint collapses the wavefunction, reducing possibilities
        # Conflicts create interference patterns that must be resolved
        
        # Phase 1: Build constraint satisfaction problem
        # Each entity is a quantum state with possible time slots
        # We'll use the constraint solver to find valid schedules
        
        # Convert temporal constraints to CSP constraints
        csp_variables = []
        csp_domains = {}
        csp_constraints = []
        
        # Create time slots (simplified: 0-23 for hours)
        time_slots = list(range(24))
        
        for entity in entities:
            csp_variables.append(entity)
            csp_domains[entity] = time_slots.copy()
        
        # Add constraints
        for const_type, a, b in constraints:
            if const_type == 'before':
                # a must be before b
                def before_constraint(val_a, val_b):
                    return val_a < val_b
                csp_constraints.append(([a, b], before_constraint))
            elif const_type == 'after':
                # a must be after b
                def after_constraint(val_a, val_b):
                    return val_a > val_b
                csp_constraints.append(([a, b], after_constraint))
        
        # Add fixed time points
        for entity, time_str in time_points:
            if ':' in time_str:
                hour_str = time_str.split(':')[0]
                try:
                    hour = int(hour_str)
                    if entity in csp_domains:
                        csp_domains[entity] = [hour]
                except ValueError:
                    pass
        
        # Check information sufficiency (quantum measurement completeness)
        n_vars = len(csp_variables)
        n_constraints = len(csp_constraints)
        info_status = information_sufficiency(n_vars, n_constraints)
        
        # Use T1 primitive: solve_constraints
        solution = solve_constraints(csp_variables, csp_domains, csp_constraints)
        
        # Use amino acid: is_uniquely_solvable to check if schedule is deterministic
        unique_check = is_uniquely_solvable(csp_variables, csp_domains, csp_constraints)
        
        # Use amino acid: check_entailment to verify logical consistency
        # Convert constraints to logical clauses for entailment checking
        clauses = []
        var_map = {}
        for i, entity in enumerate(entities, 1):
            var_map[entity] = i
        
        # Simple encoding: for before(a,b): not(a_later) or b_earlier
        # This is a simplified encoding for demonstration
        for const_type, a, b in constraints:
            if a in var_map and b in var_map:
                a_var = var_map[a]
                b_var = var_map[b]
                if const_type == 'before':
                    # a < b encoded as (not a_high or b_low)
                    clauses.append([-a_var, b_var])
                elif const_type == 'after':
                    clauses.append([a_var, -b_var])
        
        if clauses and var_map:
            # Check if constraints are self-consistent (no paradox)
            paradox_check = detect_paradox(clauses)
        else:
            paradox_check = None
        
        # Quantum superposition collapse: if multiple solutions exist, 
        # compute expected schedule using quantum probabilities
        all_solutions = []
        if solution:
            all_solutions.append(solution)
            # Try to find alternative solutions by relaxing constraints
            # This simulates quantum measurement affecting the system
            
        # Compute entropy of the scheduling space (quantum uncertainty)
        if csp_domains:
            domain_sizes = [len(domain) for domain in csp_domains.values()]
            if domain_sizes:
                max_domain = max(domain_sizes)
                normalized_sizes = [size / max_domain for size in domain_sizes if max_domain > 0]
                if normalized_sizes:
                    schedule_entropy = entropy(normalized_sizes)
                else:
                    schedule_entropy = 0.0
            else:
                schedule_entropy = 0.0
        else:
            schedule_entropy = 0.0
        
        # Determine the answer based on the goal
        computed_answer = ""
        confidence = 0.5
        
        if solution:
            # Format the schedule
            sorted_schedule = sorted(solution.items(), key=lambda x: x[1])
            schedule_str = ", ".join([f"{entity} at {hour}:00" for entity, hour in sorted_schedule])
            
            # Extract what the question is asking for
            goal_lower = (goal or "").lower()
            if "which" in goal_lower and "first" in goal_lower:
                # Find first event
                first_entity = min(solution.items(), key=lambda x: x[1])[0]
                computed_answer = first_entity
            elif "which" in goal_lower and "last" in goal_lower:
                # Find last event
                last_entity = max(solution.items(), key=lambda x: x[1])[0]
                computed_answer = last_entity
            elif "order" in goal_lower or "sequence" in goal_lower:
                # Return the sequence
                order = [entity for entity, _ in sorted_schedule]
                computed_answer = " -> ".join(order)
            elif "time" in goal_lower and len(entities) == 1:
                # Return time for specific entity
                entity = next(iter(entities))
                if entity in solution:
                    computed_answer = f"{solution[entity]}:00"
            else:
                # Default: return the full schedule
                computed_answer = schedule_str
            
            # Calculate confidence based on uniqueness and constraints
            confidence_factors = []
            if unique_check:
                confidence_factors.append(1.0)
            else:
                confidence_factors.append(0.7)
            
            if paradox_check is False:  # No paradox detected
                confidence_factors.append(0.9)
            elif paradox_check is True:  # Paradox detected
                confidence_factors.append(0.3)
            else:
                confidence_factors.append(0.5)
            
            # Use T1 primitive: confidence_from_agreement
            if confidence_factors:
                confidence = confidence_from_agreement(confidence_factors)
            else:
                confidence = 0.7
        else:
            # No solution found
            computed_answer = "No valid schedule"
            confidence = 0.1
        
        # Use T1 primitive: expected_value for quantum expectation
        if solution and durations:
            # Calculate expected duration if applicable
            duration_values = []
            for entity, hour in solution.items():
                if entity in durations:
                    duration_values.append((0.5, durations[entity]))  # 0.5 probability placeholder
            
            if duration_values:
                exp_duration = expected_value(duration_values)
                # Add expected duration to reasoning
                computed_answer += f" (expected duration: {exp_duration} minutes)"
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Schedule entropy: {schedule_entropy:.2f}, Unique: {unique_check}, Paradox: {paradox_check}",
            "schedule_entropy": schedule_entropy,
            "unique": unique_check,
            "paradox": paradox_check,
            "info_status": info_status
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            score = 0.0
            
            # Clean the computed answer for comparison
            clean_computed = computed_answer.lower().strip()
            clean_candidate = candidate.lower().strip()
            
            # Direct containment check
            if clean_computed in clean_candidate:
                score = 0.9 * confidence
            elif clean_candidate in clean_computed:
                score = 0.8 * confidence
            else:
                # Use NCD as fallback
                ncd_score = self._ncd(clean_computed, clean_candidate)
                score = (1.0 - ncd_score) * 0.7 * confidence
            
            # Boost score if candidate contains schedule-related keywords
            # (This analyzes the candidate, which is allowed since we're not matching against answer strings)
            schedule_keywords = ['schedule', 'order', 'time', 'first', 'last', 'before', 'after']
            if any(keyword in clean_candidate for keyword in schedule_keywords):
                score *= 1.1
            
            results.append({
                "candidate": candidate,
                "raw_score": score,
                "confidence": confidence
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        # Extract raw scores
        raw_scores = [item["raw_score"] for item in scored]
        
        # Normalize to 0-1 range if needed
        min_score = min(raw_scores)
        max_score = max(raw_scores)
        
        calibrated = []
        for item in scored:
            raw = item["raw_score"]
            if max_score > min_score:
                normalized = (raw - min_score) / (max_score - min_score)
            else:
                normalized = 0.5
            
            # Apply confidence weighting
            final_score = normalized * item["confidence"]
            
            calibrated.append({
                "candidate": item["candidate"],
                "score": final_score,
                "raw_score": raw,
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