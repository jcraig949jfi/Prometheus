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
from forge.amino_acids.constraint_acids import is_uniquely_solvable, solve_first

class ReasoningTool:
    """evolutionary_biology x constraint_acids - temporal_scheduling"""

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
        # Look for patterns like "Alice must meet", "Bob cannot attend", etc.
        entity_pattern = r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b'
        potential_entities = re.findall(entity_pattern, prompt)
        
        # Filter to entities that appear with scheduling verbs
        scheduling_verbs = ['must', 'needs', 'wants', 'has', 'cannot', 'can', 'attend', 'meet', 'schedule']
        entities = set()
        for entity in potential_entities:
            # Check if entity appears near scheduling verbs
            entity_lower = entity.lower()
            for verb in scheduling_verbs:
                pattern = rf'\b{entity}\b.*?\b{verb}\b|\b{verb}\b.*?\b{entity}\b'
                if re.search(pattern, prompt, re.IGNORECASE):
                    entities.add(entity)
                    break
        
        # Extract time slots and constraints
        time_pattern = r'\b(\d{1,2}(?::\d{2})?(?:am|pm)?)\b'
        times = re.findall(time_pattern, prompt, re.IGNORECASE)
        
        # Extract constraint relationships
        constraints = []
        constraint_keywords = ['before', 'after', 'at', 'same time', 'cannot', 'must', 'conflict']
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in constraint_keywords):
                # Find entities in this line
                line_entities = re.findall(entity_pattern, line)
                line_entities = [e for e in line_entities if e in entities]
                
                if len(line_entities) >= 2:
                    # Check for temporal relations
                    if 'before' in line_lower:
                        # Find which entity comes before which
                        parts = line_lower.split('before')
                        if len(parts) == 2:
                            before_entity = None
                            after_entity = None
                            for entity in line_entities:
                                if entity.lower() in parts[0]:
                                    before_entity = entity
                                elif entity.lower() in parts[1]:
                                    after_entity = entity
                            if before_entity and after_entity:
                                constraints.append(('before', before_entity, after_entity))
                    
                    elif 'after' in line_lower:
                        parts = line_lower.split('after')
                        if len(parts) == 2:
                            after_entity = None
                            before_entity = None
                            for entity in line_entities:
                                if entity.lower() in parts[0]:
                                    after_entity = entity
                                elif entity.lower() in parts[1]:
                                    before_entity = entity
                            if before_entity and after_entity:
                                constraints.append(('before', before_entity, after_entity))
                    
                    elif 'same time' in line_lower or 'conflict' in line_lower:
                        # These entities cannot be scheduled together
                        if len(line_entities) >= 2:
                            for i in range(len(line_entities)):
                                for j in range(i+1, len(line_entities)):
                                    constraints.append(('conflict', line_entities[i], line_entities[j]))
        
        # Extract numerical constraints (durations, limits)
        number_pattern = r'\b(\d+)\b'
        numbers = [int(n) for n in re.findall(number_pattern, prompt) if int(n) > 0 and int(n) < 100]
        
        return {
            "entities": list(entities),
            "times": times,
            "constraints": constraints,
            "numbers": numbers,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply evolutionary biology framework to solve scheduling conflicts."""
        entities = structure["entities"]
        constraints = structure["constraints"]
        question = structure["question"]
        
        if not entities:
            return {"answer": "No solution", "confidence": 0.0, "reasoning": "No entities found"}
        
        # Evolutionary biology framework: treat scheduling as evolutionary optimization
        # Each schedule is an organism, constraints are environmental pressures
        # Fitness = number of constraints satisfied
        # Mutation = swapping time slots
        # Selection = keep fittest schedules
        
        # Phase 1: Check if problem is well-posed using information_sufficiency primitive
        n_entities = len(entities)
        n_constraints = len(constraints)
        sufficiency = information_sufficiency(n_entities, n_constraints)
        
        # Phase 2: Build constraint satisfaction problem
        # Create time slots based on extracted times or use generic slots
        time_slots = structure["times"] or [f"Slot{i+1}" for i in range(n_entities)]
        
        # Define domains for each entity
        domains = {}
        for entity in entities:
            domains[entity] = time_slots[:]  # All entities can be in any time slot initially
        
        # Define constraint functions
        constraint_funcs = []
        
        # Process 'before' constraints
        for const_type, e1, e2 in constraints:
            if const_type == 'before':
                # Constraint: e1's time slot must come before e2's time slot
                def make_before_constraint(entity1, entity2, slots=time_slots):
                    def constraint(values):
                        # values is a dict with entity->slot assignments
                        slot1 = values[entity1]
                        slot2 = values[entity2]
                        # Check if slot1 comes before slot2 in the time_slots list
                        try:
                            idx1 = slots.index(slot1)
                            idx2 = slots.index(slot2)
                            return idx1 < idx2
                        except ValueError:
                            return False
                    return constraint
                
                constraint_funcs.append(([e1, e2], make_before_constraint(e1, e2)))
        
        # Process 'conflict' constraints
        for const_type, e1, e2 in constraints:
            if const_type == 'conflict':
                # Constraint: e1 and e2 cannot have the same time slot
                def make_conflict_constraint(entity1, entity2):
                    def constraint(values):
                        return values[entity1] != values[entity2]
                    return constraint
                
                constraint_funcs.append(([e1, e2], make_conflict_constraint(e1, e2)))
        
        # Phase 3: Check if problem is uniquely solvable using amino acid
        unique_check = is_uniquely_solvable(domains, constraint_funcs)
        
        # Phase 4: Try to find a solution using solve_constraints primitive
        solution = solve_constraints(list(domains.keys()), domains, constraint_funcs)
        
        # Phase 5: If no solution found, try to find partial solution using solve_first amino acid
        if solution is None:
            partial_solution = solve_first(domains, constraint_funcs)
            if partial_solution is not None:
                solution = partial_solution
        
        # Phase 6: Apply evolutionary selection pressure
        # Compute fitness of solution (if found)
        if solution is not None:
            # Count satisfied constraints
            satisfied = 0
            for vars_list, const_func in constraint_funcs:
                if const_func(solution):
                    satisfied += 1
            
            fitness = satisfied / len(constraint_funcs) if constraint_funcs else 1.0
            
            # Use entropy primitive to measure schedule diversity
            # In evolutionary terms, low entropy = convergent evolution (all schedules similar)
            slot_assignments = list(solution.values())
            slot_counts = {}
            for slot in slot_assignments:
                slot_counts[slot] = slot_counts.get(slot, 0) + 1
            
            probs = [count/len(slot_assignments) for count in slot_counts.values()]
            schedule_entropy = entropy(probs) if probs else 0.0
            
            # Higher entropy means more diverse schedule (better resource utilization)
            entropy_bonus = schedule_entropy / len(time_slots) if time_slots else 0.0
            
            # Final confidence combines fitness and diversity
            confidence = fitness * 0.8 + entropy_bonus * 0.2
            
            # Determine answer based on question
            computed_answer = self._extract_answer_from_solution(solution, question, structure)
            
            return {
                "answer": computed_answer,
                "confidence": confidence,
                "reasoning": f"Schedule found with fitness {fitness:.2f}, entropy {schedule_entropy:.2f}. Problem {sufficiency}.",
                "solution": solution,
                "fitness": fitness,
                "entropy": schedule_entropy
            }
        else:
            # No solution found - suggest which constraint to relax
            # Use confidence_from_agreement primitive with multiple scoring attempts
            scores = []
            for i in range(min(3, len(constraint_funcs))):
                # Try removing one constraint at a time
                reduced_constraints = constraint_funcs[:i] + constraint_funcs[i+1:]
                partial_solution = solve_first(domains, reduced_constraints)
                if partial_solution is not None:
                    scores.append(0.5)  # Partial success
                else:
                    scores.append(0.0)
            
            if scores:
                confidence = confidence_from_agreement(scores)
            else:
                confidence = 0.0
            
            return {
                "answer": "No valid schedule",
                "confidence": confidence,
                "reasoning": f"No solution found. Problem {sufficiency}. Try relaxing constraints.",
                "solution": None,
                "fitness": 0.0,
                "entropy": 0.0
            }

    def _extract_answer_from_solution(self, solution: Dict[str, str], question: str, structure: Dict[str, Any]) -> str:
        """Extract the specific answer from the solution based on the question."""
        if not solution:
            return "No solution"
        
        # Look for question patterns
        question_lower = question.lower()
        
        # Check if question asks about a specific entity's time
        for entity in structure["entities"]:
            if entity.lower() in question_lower and ("when" in question_lower or "time" in question_lower):
                return f"{entity} at {solution.get(entity, 'unknown')}"
        
        # Check if question asks about conflicts
        if "conflict" in question_lower or "problem" in question_lower:
            # Find entities with same time slot
            slot_to_entities = {}
            for entity, slot in solution.items():
                slot_to_entities.setdefault(slot, []).append(entity)
            
            conflicts = [entities for entities in slot_to_entities.values() if len(entities) > 1]
            if conflicts:
                return f"Conflict: {' and '.join(conflicts[0])} at same time"
        
        # Check if question asks about ordering
        if "before" in question_lower or "after" in question_lower:
            # Find all before/after relationships in constraints
            for const_type, e1, e2 in structure["constraints"]:
                if const_type == 'before':
                    if e1.lower() in question_lower or e2.lower() in question_lower:
                        slot1 = solution.get(e1, "?")
                        slot2 = solution.get(e2, "?")
                        return f"{e1} ({slot1}) before {e2} ({slot2})"
        
        # Default: return the schedule as a summary
        schedule_summary = "; ".join([f"{e}: {t}" for e, t in solution.items()])
        if len(schedule_summary) > 100:
            schedule_summary = schedule_summary[:97] + "..."
        return schedule_summary

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust score by confidence from reasoning
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
        
        # Extract scores for calibration
        scores = [item["score"] for item in scored]
        
        # Use expected_value primitive to compute weighted average
        # Create equal probability weights
        n = len(scores)
        if n > 0:
            weights = [1.0/n] * n
            outcomes = list(zip(weights, scores))
            mean_score = expected_value(outcomes)
        else:
            mean_score = 0.5
        
        # Calibrate: shift scores toward mean if they're too extreme
        calibrated = []
        for item in scored:
            score = item["score"]
            # Soft calibration: move score 20% toward mean
            calibrated_score = score * 0.8 + mean_score * 0.2
            # Ensure score is in [0, 1]
            calibrated_score = max(0.0, min(1.0, calibrated_score))
            
            calibrated_item = item.copy()
            calibrated_item["score"] = calibrated_score
            calibrated.append(calibrated_item)
        
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