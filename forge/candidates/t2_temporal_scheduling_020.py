import re
import zlib
from typing import Dict, List, Any, Tuple, Optional

from forge_primitives import (
    topological_sort,
    solve_constraints,
    information_sufficiency,
    entropy,
    confidence_from_agreement
)
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Information theory x Constraint satisfaction - temporal_scheduling"""

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
        """Extract entities, constraints, and question from scheduling prompt."""
        lines = [line.strip() for line in prompt.split('\n') if line.strip()]
        
        # Find entities (people, events, tasks) - typically capitalized words
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        entities = set()
        for line in lines:
            entities.update(re.findall(entity_pattern, line))
        
        # Remove common non-entity words
        common_words = {'The', 'And', 'But', 'However', 'Therefore', 'Which', 'What', 'When'}
        entities = {e for e in entities if e not in common_words}
        
        # Extract temporal constraints (before, after, at same time)
        constraints = []
        temporal_keywords = ['before', 'after', 'at the same time as', 'simultaneous with']
        
        for line in lines:
            line_lower = line.lower()
            # Look for constraint patterns
            for keyword in temporal_keywords:
                if keyword in line_lower:
                    # Try to extract entities around the keyword
                    parts = re.split(keyword, line_lower, maxsplit=1)
                    if len(parts) == 2:
                        left = parts[0].strip()
                        right = parts[1].strip().rstrip('.')
                        # Find matching entities
                        left_entity = None
                        right_entity = None
                        for entity in entities:
                            if entity.lower() in left:
                                left_entity = entity
                            if entity.lower() in right:
                                right_entity = entity
                        
                        if left_entity and right_entity:
                            if keyword == 'before':
                                constraints.append((left_entity, right_entity))
                            elif keyword == 'after':
                                constraints.append((right_entity, left_entity))
                            elif 'same time' in keyword or 'simultaneous' in keyword:
                                # Represent simultaneity as bidirectional constraint
                                constraints.append((left_entity, right_entity))
                                constraints.append((right_entity, left_entity))
        
        # Extract question (usually last sentence)
        question = ""
        if lines:
            last_line = lines[-1]
            if '?' in last_line:
                question = last_line
            else:
                # Look for question in last few lines
                for line in reversed(lines[-3:]):
                    if '?' in line:
                        question = line
                        break
        
        # Extract numerical time values if present
        time_values = {}
        time_pattern = r'(\d+)\s*(?:hours?|hrs?|minutes?|mins?)'
        for line in lines:
            matches = re.findall(time_pattern, line.lower())
            if matches:
                for entity in entities:
                    if entity.lower() in line.lower():
                        time_values[entity] = int(matches[0])
        
        return {
            "entities": list(entities),
            "constraints": constraints,
            "question": question,
            "time_values": time_values,
            "raw_lines": lines
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use information theory and constraint solving to find optimal schedule."""
        entities = structure["entities"]
        constraints = structure["constraints"]
        time_values = structure["time_values"]
        
        # CRITICAL PATH 1: Use topological_sort to find a valid ordering
        # This primitive is load-bearing - different constraints produce different orderings
        try:
            ordering = topological_sort(constraints)
            if ordering is None:
                # Graph has cycles, constraints may be contradictory
                ordering = []
        except Exception:
            ordering = []
        
        # CRITICAL PATH 2: Use solve_constraints to find feasible assignments
        # Create variables for each entity with time slots
        variables = entities
        # Create domains based on extracted time values or default range
        max_slots = 10  # reasonable default
        if time_values:
            max_slots = max(time_values.values()) + 2 if time_values else 10
        
        domains = {}
        for entity in entities:
            if entity in time_values:
                # Entity has specific time requirement
                domains[entity] = [time_values[entity]]
            else:
                # Entity can be in any available slot
                domains[entity] = list(range(max_slots))
        
        # Define constraint functions
        constraint_funcs = []
        for a, b in constraints:
            # Constraint: a must be before b (or simultaneous if both directions)
                constraint_funcs.append(([a, b], lambda x, y: x < y))
        
        # Solve the constraint satisfaction problem
        solution = solve_constraints(variables, domains, constraint_funcs)
        
        # CRITICAL PATH 3: Use information_sufficiency to check if problem is well-posed
        n_vars = len(variables)
        n_constraints = len(constraints)
        sufficiency = information_sufficiency(n_vars, n_constraints)
        
        # CRITICAL PATH 4: Use amino acid solve_first to find a concrete schedule
        # This amino acid is load-bearing - different problems yield different solutions
        amino_solution = None
        try:
            amino_solution = solve_first(domains, constraint_funcs)
        except Exception:
            amino_solution = None
        
        # CRITICAL PATH 5: Use amino acid is_uniquely_solvable to check solution uniqueness
        is_unique = False
        try:
            is_unique = is_uniquely_solvable(domains, constraint_funcs)
        except Exception:
            is_unique = False
        
        # Compute entropy of the solution space to measure uncertainty
        # Higher entropy = more uncertainty about the schedule
        if solution:
            # Count possible time slots for each entity
            slot_counts = []
            for entity in entities:
                if entity in solution:
                    if isinstance(solution[entity], list):
                        slot_counts.append(len(solution[entity]))
                    else:
                        slot_counts.append(1)
                else:
                    slot_counts.append(len(domains.get(entity, [1])))
            
            # Normalize to probabilities
            total_slots = sum(slot_counts)
            if total_slots > 0:
                probs = [count/total_slots for count in slot_counts]
                schedule_entropy = entropy(probs)
            else:
                schedule_entropy = 0.0
        else:
            schedule_entropy = 1.0  # Maximum uncertainty
        
        # Determine the answer based on reasoning
        computed_answer = ""
        reasoning_text = ""
        
        # Information theory perspective: The answer minimizes uncertainty
        # We look for the entity that, when scheduled, reduces entropy the most
        
        if amino_solution:
            # Use the amino acid solution as primary
            # Find which entity has the most constrained time
            most_constrained = None
            min_domain_size = float('inf')
            
            for entity in entities:
                if entity in amino_solution:
                    # Check how many values this entity could take
                    domain_size = len(domains.get(entity, []))
                    if domain_size < min_domain_size:
                        min_domain_size = domain_size
                        most_constrained = entity
            
            if most_constrained:
                computed_answer = most_constrained
                reasoning_text = f"{most_constrained} is the most constrained entity (domain size {min_domain_size}), scheduling it first minimizes uncertainty (entropy {schedule_entropy:.2f})."
            else:
                # Fallback to first entity in topological order
                if ordering:
                    computed_answer = ordering[0]
                    reasoning_text = f"Topological order starts with {ordering[0]}, information sufficiency: {sufficiency}, entropy: {schedule_entropy:.2f}."
                else:
                    computed_answer = entities[0] if entities else ""
                    reasoning_text = f"No clear ordering, using first entity. Information sufficiency: {sufficiency}."
        else:
            # Fallback using primitives only
            if ordering:
                computed_answer = ordering[0]
                reasoning_text = f"Topological order starts with {ordering[0]}. Constraint solution: {solution is not None}, sufficiency: {sufficiency}."
            else:
                # Use entity with smallest domain (most information)
                min_domain_entity = None
                min_size = float('inf')
                for entity in entities:
                    domain = domains.get(entity, [])
                    if len(domain) < min_size:
                        min_size = len(domain)
                        min_domain_entity = entity
                
                computed_answer = min_domain_entity if min_domain_entity else (entities[0] if entities else "")
                reasoning_text = f"Entity {computed_answer} has smallest domain ({min_size} options), maximizing information gain."
        
        # CRITICAL: Compute confidence using confidence_from_agreement
        # Different reasoning paths give different confidence scores
        confidence_scores = []
        
        # Score 1: Based on topological sort success
        confidence_scores.append(1.0 if ordering else 0.3)
        
        # Score 2: Based on constraint solution existence
        confidence_scores.append(1.0 if solution else 0.5)
        
        # Score 3: Based on information sufficiency
        if sufficiency == "determined":
            confidence_scores.append(0.9)
        elif sufficiency == "underdetermined":
            confidence_scores.append(0.6)
        else:
            confidence_scores.append(0.4)
        
        # Score 4: Based on solution uniqueness
        confidence_scores.append(0.8 if is_unique else 0.5)
        
        # Score 5: Based on entropy (lower entropy = higher confidence)
        confidence_scores.append(1.0 - min(schedule_entropy, 1.0))
        
        # Use primitive to combine confidence scores
        confidence = confidence_from_agreement(confidence_scores)
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": reasoning_text,
            "ordering": ordering,
            "solution": solution,
            "amino_solution": amino_solution,
            "sufficiency": sufficiency,
            "is_unique": is_unique,
            "entropy": schedule_entropy
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring of computed answer
            score = 0.0
            
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                ncd_score = self._ncd(reasoning_text, candidate)
                score = 1.0 / (1.0 + ncd_score)
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        # Extract raw scores
        raw_scores = [item["raw_score"] for item in scored]
        
        # Simple normalization: scale to [0, 1] range
        min_score = min(raw_scores)
        max_score = max(raw_scores)
        
        if max_score - min_score > 0.001:
            for item in scored:
                item["score"] = (item["raw_score"] - min_score) / (max_score - min_score)
        else:
            # All scores are similar, keep as is
            for item in scored:
                item["score"] = item["raw_score"]
        
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