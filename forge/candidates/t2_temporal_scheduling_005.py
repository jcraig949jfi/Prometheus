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
from forge.amino_acids.pysat_acids import check_entailment


class ReasoningTool:
    """Feedback Systems x Constraint Satisfaction - Temporal Scheduling"""

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
        """Extract entities, constraints, and question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find entity names (capitalized words that appear in constraints)
        entity_pattern = r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b'
        potential_entities = re.findall(entity_pattern, prompt)
        
        # Filter to entities that appear in constraint-like sentences
        entities = set()
        constraint_sentences = []
        time_values = {}
        
        for line in lines:
            line_lower = line.lower()
            # Look for constraint indicators
            if any(word in line_lower for word in ['before', 'after', 'during', 'while', 
                                                   'must', 'cannot', 'needs', 'requires',
                                                   'at least', 'at most', 'exactly']):
                constraint_sentences.append(line)
                # Extract entities from this constraint
                line_entities = re.findall(entity_pattern, line)
                entities.update(line_entities)
            
            # Extract time values (numbers with units)
            time_matches = re.findall(r'(\d+)\s*(?:hour|minute|day|week|month)s?', line_lower)
            if time_matches:
                # Associate with nearby entity if possible
                for entity in re.findall(entity_pattern, line):
                    if entity not in time_values:
                        time_values[entity] = []
                    time_values[entity].extend([int(t) for t in time_matches])
        
        # Also look for explicit "Event X takes Y hours" patterns
        duration_pattern = r'([A-Z][a-z]+(?: [A-Z][a-z]+)*)\s+(?:takes|requires|needs)\s+(\d+)\s*(?:hour|minute|day)'
        for match in re.finditer(duration_pattern, prompt, re.IGNORECASE):
            entity, duration = match.groups()
            entities.add(entity)
            if entity not in time_values:
                time_values[entity] = []
            time_values[entity].append(int(duration))
        
        # Extract ordering constraints (X before/after Y)
        ordering_constraints = []
        for sentence in constraint_sentences:
            # Pattern for "X must be before Y" or "X before Y"
            before_pattern = r'([A-Z][a-z]+(?: [A-Z][a-z]+)*)\s+(?:must be |is )?before\s+([A-Z][a-z]+(?: [A-Z][a-z]+)*)'
            after_pattern = r'([A-Z][a-z]+(?: [A-Z][a-z]+)*)\s+(?:must be |is )?after\s+([A-Z][a-z]+(?: [A-Z][a-z]+)*)'
            
            for match in re.finditer(before_pattern, sentence, re.IGNORECASE):
                x, y = match.groups()
                ordering_constraints.append((x, y))
                entities.update([x, y])
            
            for match in re.finditer(after_pattern, sentence, re.IGNORECASE):
                x, y = match.groups()
                ordering_constraints.append((y, x))  # Convert "X after Y" to "Y before X"
                entities.update([x, y])
        
        # Extract resource/conflict constraints
        conflict_constraints = []
        for sentence in constraint_sentences:
            if 'cannot' in sentence.lower() and 'same' in sentence.lower():
                # Pattern for "X and Y cannot be at the same time"
                and_pattern = r'([A-Z][a-z]+(?: [A-Z][a-z]+)*)\s+and\s+([A-Z][a-z]+(?: [A-Z][a-z]+)*)'
                matches = re.findall(and_pattern, sentence)
                for x, y in matches:
                    conflict_constraints.append((x, y))
                    entities.update([x, y])
        
        return {
            "entities": list(entities),
            "ordering_constraints": ordering_constraints,
            "conflict_constraints": conflict_constraints,
            "time_values": time_values,
            "question": question,
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply feedback systems reasoning to resolve scheduling conflicts."""
        entities = structure["entities"]
        ordering_constraints = structure["ordering_constraints"]
        conflict_constraints = structure["conflict_constraints"]
        time_values = structure["time_values"]
        question = structure["question"]
        
        # FEEDBACK SYSTEMS CONCEPT: Treat scheduling as a dynamic system with
        # constraints as negative feedback loops. Each constraint violation
        # generates corrective pressure. The solution is the equilibrium state
        # where all feedback signals are balanced (constraints satisfied).
        
        # Step 1: Check if system is determined using information_sufficiency primitive
        n_entities = len(entities)
        n_constraints = len(ordering_constraints) + len(conflict_constraints)
        system_status = information_sufficiency(n_entities, n_constraints)
        
        # Step 2: Build constraint satisfaction problem
        # Create time slots as domain (simplified to discrete positions)
        max_slots = 10  # Reasonable upper bound
        domains = {entity: list(range(max_slots)) for entity in entities}
        
        constraints = []
        
        # Add ordering constraints: entity1 < entity2
        for e1, e2 in ordering_constraints:
            if e1 in domains and e2 in domains:
                constraints.append(
                    ([e1, e2], lambda x, y: x < y)
                )
        
        # Add conflict constraints: entity1 != entity2
        for e1, e2 in conflict_constraints:
            if e1 in domains and e2 in domains:
                constraints.append(
                    ([e1, e2], lambda x, y: x != y)
                )
        
        # Add duration constraints if we have time values
        for entity, durations in time_values.items():
            if entity in domains and durations:
                avg_duration = sum(durations) / len(durations)
                # Convert to slot count (simplified: 1 slot per time unit)
                duration_slots = int(avg_duration)
                # Constraint: entity must fit within schedule
                # This is a simplified representation
                if duration_slots > 0:
                    # For now, just ensure it's not at the very end if duration matters
                    max_pos = max_slots - duration_slots
                    if max_pos > 0:
                        domains[entity] = [i for i in domains[entity] if i <= max_pos]
        
        # Step 3: Use constraint_acids to find solution
        # First check if uniquely solvable using amino acid
        unique_check = is_uniquely_solvable(domains, constraints)
        
        # Find first solution using amino acid
        solution = solve_first(domains, constraints)
        
        # If amino acid fails, fall back to T1 primitive
        if solution is None:
            solution = solve_constraints(list(domains.keys()), domains, constraints)
        
        # Step 4: Apply feedback systems analysis
        # Compute entropy of solution space as measure of uncertainty
        if solution:
            # Create probability distribution over possible positions
            # (simplified: uniform over solution if multiple exist)
            position_counts = {}
            for entity, pos in solution.items():
                position_counts[pos] = position_counts.get(pos, 0) + 1
            
            total = len(solution)
            probs = [count/total for count in position_counts.values()]
            schedule_entropy = entropy(probs) if probs else 0.0
            
            # Use topological_sort primitive to get linear order
            # Convert ordering constraints to edges for DAG
            edges = [(e1, e2) for e1, e2 in ordering_constraints 
                    if e1 in solution and e2 in solution]
            
            topological_order = topological_sort(edges)
            
            # If topological sort fails (cycles), use solution order
            if topological_order is None or len(topological_order) != len(entities):
                # Sort by assigned time slot
                topological_order = sorted(solution.keys(), key=lambda x: solution[x])
            
            # Determine which entity is being asked about
            # Look for question patterns
            computed_answer = None
            confidence = 0.5
            
            # Common question patterns in scheduling problems
            if 'first' in question.lower():
                computed_answer = topological_order[0] if topological_order else entities[0]
                confidence = 0.8
            elif 'last' in question.lower():
                computed_answer = topological_order[-1] if topological_order else entities[-1]
                confidence = 0.8
            elif 'cannot' in question.lower() or 'conflict' in question.lower():
                # Find entities that conflict the most
                conflict_counts = {entity: 0 for entity in entities}
                for e1, e2 in conflict_constraints:
                    if e1 in conflict_counts:
                        conflict_counts[e1] += 1
                    if e2 in conflict_counts:
                        conflict_counts[e2] += 1
                
                if conflict_counts:
                    max_conflict = max(conflict_counts.values())
                    most_conflicting = [e for e, c in conflict_counts.items() if c == max_conflict]
                    computed_answer = most_conflicting[0] if most_conflicting else entities[0]
                    confidence = 0.7
            elif 'when' in question.lower() or 'time' in question.lower():
                # Extract entity being asked about
                question_entities = re.findall(r'[A-Z][a-z]+(?: [A-Z][a-z]+)*', question)
                if question_entities:
                    target = question_entities[0]
                    if target in solution:
                        computed_answer = f"slot {solution[target]}"
                        confidence = 0.9
                    else:
                        computed_answer = topological_order[0] if topological_order else entities[0]
                        confidence = 0.6
                else:
                    computed_answer = topological_order[0] if topological_order else entities[0]
                    confidence = 0.6
            else:
                # Default: return the schedule order as answer
                computed_answer = " -> ".join(topological_order) if topological_order else "no solution"
                confidence = 0.5
            
            # Use confidence_from_agreement primitive with multiple metrics
            metrics = [
                confidence,
                1.0 - (schedule_entropy / len(entities)),  # Normalized entropy
                1.0 if unique_check else 0.5,  # Uniqueness contributes to confidence
                0.8 if solution else 0.2  # Existence of solution
            ]
            final_confidence = confidence_from_agreement(metrics)
            
            # Use expected_value primitive to assess solution quality
            # Higher quality = more constraints satisfied relative to total
            quality_score = len(constraints) / (len(constraints) + 1) if constraints else 0.5
            quality_metrics = [(0.7, quality_score), (0.3, final_confidence)]
            overall_quality = expected_value(quality_metrics)
            
            return {
                "answer": computed_answer,
                "confidence": final_confidence,
                "reasoning": f"Schedule: {' -> '.join(topological_order) if topological_order else 'No valid order'}. "
                           f"System is {system_status}. "
                           f"Solution {'unique' if unique_check else 'not unique'}. "
                           f"Entropy: {schedule_entropy:.2f}. "
                           f"Quality: {overall_quality:.2f}",
                "topological_order": topological_order,
                "solution": solution,
                "system_status": system_status
            }
        else:
            # No solution found
            return {
                "answer": "no valid schedule",
                "confidence": 0.8,
                "reasoning": f"No valid schedule exists. System is {system_status}. "
                           f"Constraints are inconsistent.",
                "topological_order": [],
                "solution": None,
                "system_status": system_status
            }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        def ncd(a: str, b: str) -> float:
            """Normalized Compression Distance."""
            if not a or not b:
                return 1.0
            ca = len(zlib.compress(a.encode()))
            cb = len(zlib.compress(b.encode()))
            cab = len(zlib.compress((a + " " + b).encode()))
            return (cab - min(ca, cb)) / max(ca, cb) if max(ca, cb) > 0 else 1.0
        
        scored = []
        for candidate in candidates:
            # Primary scoring: direct match of computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Check if candidate contains any entity from topological order
                topological_order = reasoning_result.get("topological_order", [])
                contains_entity = any(
                    entity.lower() in candidate.lower() 
                    for entity in topological_order
                )
                
                if contains_entity and topological_order:
                    base_score = 0.7
                else:
                    # Fallback: NCD similarity to reasoning text
                    similarity = 1.0 - ncd(reasoning_text, candidate)
                    base_score = similarity * 0.5
            
            # Adjust based on confidence
            confidence = reasoning_result.get("confidence", 0.5)
            adjusted_score = base_score * confidence
            
            scored.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score,
                "confidence_multiplier": confidence
            })
        
        return scored

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using feedback systems concept of stability."""
        if not scored:
            return scored
        
        # FEEDBACK SYSTEMS: Apply damping to prevent overshooting
        # High confidence scores get boosted, low confidence scores get damped
        
        scores = [item["score"] for item in scored]
        if scores:
            max_score = max(scores)
            min_score = min(scores)
            score_range = max_score - min_score if max_score > min_score else 1.0
            
            for item in scored:
                raw_score = item["score"]
                confidence = item["confidence_multiplier"]
                
                # Feedback control: error = distance from ideal (1.0)
                error = 1.0 - raw_score
                
                # Proportional control with confidence as gain
                # Higher confidence = stronger correction
                correction = error * confidence * 0.3  # Damping factor
                
                calibrated_score = raw_score + correction
                calibrated_score = max(0.0, min(1.0, calibrated_score))
                
                item["score"] = calibrated_score
        
        return scored