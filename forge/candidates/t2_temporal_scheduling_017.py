import re
import zlib
from typing import List, Dict, Any, Tuple
from forge_primitives import (
    topological_sort,
    solve_constraints,
    information_sufficiency,
    confidence_from_agreement,
    entropy,
    expected_value
)
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


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
        """Parse prompt to extract entities, constraints, and question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Extract entity names (capitalized words that appear in constraints)
        # Look for patterns like "Alice must meet", "Bob cannot attend", etc.
        entity_pattern = r'\b([A-Z][a-z]+)\b'
        potential_entities = re.findall(entity_pattern, prompt)
        
        # Filter to entities that appear with scheduling keywords
        scheduling_keywords = ['meet', 'attend', 'schedule', 'before', 'after', 'cannot', 'must', 'available']
        entities = set()
        for entity in potential_entities:
            # Check if entity appears near scheduling keywords
            entity_context = re.search(rf'\b{entity}\b[^.]*?(?:{"|".join(scheduling_keywords)})', prompt, re.IGNORECASE)
            if entity_context:
                entities.add(entity)
        
        # Extract temporal constraints
        constraints = []
        time_slots = set()
        
        # Look for time slot mentions (numbers, hours, days)
        time_patterns = [
            r'(\d+):(\d+)\s*(?:AM|PM|am|pm)',
            r'(\d+)\s*(?:AM|PM|am|pm)',
            r'\b(\d+)\s*(?:o\'clock|hour)',
            r'\b([Mm]onday|[Tt]uesday|[Ww]ednesday|[Tt]hursday|[Ff]riday|[Ss]aturday|[Ss]unday)\b',
            r'\b(\d+)(?:st|nd|rd|th)\b'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, prompt)
            for match in matches:
                if isinstance(match, tuple):
                    time_slots.add(''.join(match))
                else:
                    time_slots.add(match)
        
        # Extract numerical time slots
        num_pattern = r'\b(\d+)\b'
        numbers = re.findall(num_pattern, prompt)
        for num in numbers:
            if 1 <= int(num) <= 24:  # Likely hour or slot number
                time_slots.add(num)
        
        # Parse constraint sentences
        for line in lines:
            line_lower = line.lower()
            
            # "A before B" constraints
            before_match = re.search(r'(\b[A-Z][a-z]+\b)\s+(?:must be|is)\s+before\s+(\b[A-Z][a-z]+\b)', line, re.IGNORECASE)
            if before_match:
                a, b = before_match.groups()
                if a in entities and b in entities:
                    constraints.append((a, b, 'before'))
            
            # "A after B" constraints
            after_match = re.search(r'(\b[A-Z][a-z]+\b)\s+(?:must be|is)\s+after\s+(\b[A-Z][a-z]+\b)', line, re.IGNORECASE)
            if after_match:
                a, b = after_match.groups()
                if a in entities and b in entities:
                    constraints.append((b, a, 'before'))  # Convert "A after B" to "B before A"
            
            # "A cannot be with B" or conflict constraints
            conflict_match = re.search(r'(\b[A-Z][a-z]+\b)\s+(?:cannot|can\'t)\s+(?:be with|meet|attend with)\s+(\b[A-Z][a-z]+\b)', line, re.IGNORECASE)
            if conflict_match:
                a, b = conflict_match.groups()
                if a in entities and b in entities:
                    constraints.append((a, b, 'conflict'))
            
            # "A must be at time X" constraints
            time_match = re.search(r'(\b[A-Z][a-z]+\b)\s+(?:must be|is)\s+(?:at|on)\s+(\d+|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)', line, re.IGNORECASE)
            if time_match:
                entity, time = time_match.groups()
                if entity in entities:
                    time_slots.add(time)
                    constraints.append((entity, time, 'fixed'))
        
        return {
            "entities": list(entities),
            "time_slots": list(time_slots),
            "constraints": constraints,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply evolutionary biology framework to find optimal schedule."""
        entities = structure["entities"]
        time_slots = structure["time_slots"]
        constraints = structure["constraints"]
        
        if not entities or not time_slots:
            return {"answer": "No solution", "confidence": 0.0, "reasoning": "Insufficient data"}
        
        # Evolutionary biology framework: treat schedules as organisms competing for time slots
        # Fitness = constraint satisfaction, Selection pressure = uniqueness requirement
        # Mutation = alternative assignments, Speciation = distinct valid schedules
        
        # Phase 1: Check information sufficiency (ecosystem carrying capacity)
        n_unknowns = len(entities)
        n_constraints = len([c for c in constraints if c[2] in ['before', 'fixed']])
        info_status = information_sufficiency(n_unknowns, n_constraints)
        
        # Phase 2: Build constraint satisfaction problem (population of possible schedules)
        variables = entities
        domains = {entity: time_slots.copy() for entity in entities}
        
        # Apply constraints to domains (environmental pressures)
        csp_constraints = []
        
        for a, b, rel in constraints:
            if rel == 'before':
                # Temporal ordering constraint
                def make_before_constraint(slot_a, slot_b, time_order=time_slots):
                    if slot_a not in time_order or slot_b not in time_order:
                        return True  # Invalid slots fail
                    return time_order.index(slot_a) < time_order.index(slot_b)
                
                csp_constraints.append(([a, b], make_before_constraint))
            
            elif rel == 'conflict':
                # Cannot have same time slot (competitive exclusion principle)
                def different_slots(slot_a, slot_b):
                    return slot_a != slot_b
                
                csp_constraints.append(([a, b], different_slots))
            
            elif rel == 'fixed':
                # Fixed time assignment (niche specialization)
                domains[a] = [b]  # Entity a must be at time b
        
        # Phase 3: Find first solution (initial population)
        solution = solve_constraints(variables, domains, csp_constraints)
        
        if solution is None:
            # No solution found (extinction event)
            return {"answer": "No valid schedule", "confidence": 0.0, "reasoning": "Constraints are inconsistent"}
        
        # Phase 4: Check if solution is unique (speciation event)
        # In evolutionary terms: is there only one viable species (schedule) in this niche?
        unique = is_uniquely_solvable(variables, domains, csp_constraints)
        
        if unique:
            uniqueness_confidence = 0.9
            reasoning = "Unique optimal schedule found (single species dominance)"
        else:
            # Multiple solutions exist (biodiversity)
            uniqueness_confidence = 0.6
            reasoning = "Multiple valid schedules exist (ecological diversity)"
        
        # Phase 5: Compute schedule fitness metrics
        # Fitness = 1 - normalized entropy of time slot distribution
        slot_assignments = list(solution.values())
        slot_counts = {}
        for slot in time_slots:
            slot_counts[slot] = slot_assignments.count(slot)
        
        probs = [count/len(entities) for count in slot_counts.values()]
        schedule_entropy = entropy(probs) if probs else 0
        
        # Lower entropy = more clustered schedule (like species clustering in habitats)
        max_entropy = entropy([1/len(time_slots)] * len(time_slots)) if time_slots else 1
        normalized_entropy = schedule_entropy / max_entropy if max_entropy > 0 else 0
        fitness_score = 1 - normalized_entropy
        
        # Phase 6: Build topological order for temporal constraints (phylogenetic tree)
        temporal_edges = [(a, b) for a, b, rel in constraints if rel == 'before']
        try:
            topological_order = topological_sort(temporal_edges)
            if topological_order:
                order_str = " → ".join(topological_order)
                reasoning += f". Temporal order: {order_str}"
        except:
            pass  # Topological sort may fail if cycles exist
        
        # Determine answer based on question type
        question = structure["question"].lower()
        computed_answer = ""
        
        if "when" in question and "meet" in question:
            # Find meeting time for specific entity
            for entity in entities:
                if entity.lower() in question.lower():
                    computed_answer = f"{entity} at {solution.get(entity, 'unknown')}"
                    break
        
        elif "schedule" in question or "order" in question:
            # Return the schedule as a string
            schedule_parts = [f"{e}: {t}" for e, t in solution.items()]
            computed_answer = "; ".join(schedule_parts)
        
        elif "conflict" in question or "problem" in question:
            # Identify conflicting constraints
            conflict_pairs = [(a, b) for a, b, rel in constraints if rel == 'conflict']
            if conflict_pairs:
                computed_answer = f"Conflict between {conflict_pairs[0][0]} and {conflict_pairs[0][1]}"
            else:
                computed_answer = "No conflicts detected"
        
        else:
            # Default: return first entity's schedule
            if entities and solution:
                first_entity = entities[0]
                computed_answer = f"{first_entity}: {solution[first_entity]}"
            else:
                computed_answer = "Valid schedule exists"
        
        # Compute confidence from multiple metrics (evolutionary stability)
        confidence_metrics = [
            uniqueness_confidence,
            fitness_score,
            0.8 if solution else 0.2
        ]
        overall_confidence = confidence_from_agreement(confidence_metrics)
        
        return {
            "answer": computed_answer,
            "confidence": overall_confidence,
            "reasoning": reasoning,
            "solution": solution,
            "fitness": fitness_score,
            "unique": unique
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
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
            # Primary scoring: exact or substring match of computed answer
            if computed_answer.lower() in candidate.lower():
                score = 0.9 + (0.1 * reasoning_result["confidence"])
            else:
                # Secondary: NCD similarity to computed answer
                answer_similarity = 1.0 / (1.0 + ncd(computed_answer, candidate))
                
                # Tertiary: NCD similarity to reasoning (for partial credit)
                reasoning_similarity = 1.0 / (1.0 + ncd(reasoning_text, candidate))
                
                score = max(answer_similarity, reasoning_similarity * 0.7)
            
            scored.append({
                "candidate": candidate,
                "score": score,
                "computed_answer": computed_answer
            })
        
        return scored

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        scores = [item["score"] for item in scored]
        if not scores:
            return scored
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score - min_score < 0.01:  # All scores nearly equal
            # Add small differentiation based on candidate length (shorter = better)
            for item in scored:
                length_penalty = len(item["candidate"]) / 100.0
                item["score"] = item["score"] - min(length_penalty, 0.05)
        else:
            # Normalize to [0, 1] range
            for item in scored:
                if max_score > min_score:
                    item["score"] = (item["score"] - min_score) / (max_score - min_score)
        
        return scored