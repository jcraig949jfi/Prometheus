import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    solve_constraints,
    topological_sort,
    information_sufficiency,
    confidence_from_agreement,
    entropy
)
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Signal_processing x Constraint_acids - temporal_scheduling"""

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
        # Look for patterns like "Alice", "Bob", "Meeting A", "Task 1"
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        all_words = re.findall(entity_pattern, prompt)
        
        # Filter to likely entities (not common words, appear multiple times)
        word_counts = {}
        for word in all_words:
            if word.lower() not in ['the', 'and', 'but', 'for', 'with', 'that', 'this']:
                word_counts[word] = word_counts.get(word, 0) + 1
        
        entities = [word for word, count in word_counts.items() 
                   if count > 1 or any(c.isdigit() for c in word)]
        
        # Extract temporal constraints
        constraints = []
        time_patterns = [
            r'(\w+)\s+(?:must be|is)\s+(?:before|after)\s+(\w+)',
            r'(\w+)\s+(?:precedes|follows)\s+(\w+)',
            r'(\w+)\s+then\s+(\w+)',
            r'(\w+)\s+before\s+(\w+)',
            r'(\w+)\s+after\s+(\w+)'
        ]
        
        for line in lines:
            for pattern in time_patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                for a, b in matches:
                    if a in entities or b in entities:
                        constraints.append((a, b))
        
        # Extract duration/availability constraints
        duration_constraints = []
        duration_pattern = r'(\w+)\s+(?:takes|requires|lasts)\s+(\d+)\s*(?:hours|minutes|time units)?'
        for line in lines:
            matches = re.findall(duration_pattern, line, re.IGNORECASE)
            for entity, duration in matches:
                if entity in entities:
                    duration_constraints.append((entity, int(duration)))
        
        # Extract conflict constraints
        conflict_constraints = []
        conflict_patterns = [
            r'(\w+)\s+(?:and|&)\s+(\w+)\s+(?:cannot|can\'t)\s+overlap',
            r'(\w+)\s+(?:and|&)\s+(\w+)\s+conflict',
            r'(\w+)\s+(?:and|&)\s+(\w+)\s+at\s+the\s+same\s+time'
        ]
        
        for line in lines:
            for pattern in conflict_patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                for a, b in matches:
                    if a in entities and b in entities:
                        conflict_constraints.append((a, b))
        
        return {
            "entities": entities,
            "temporal_constraints": list(set(constraints)),
            "duration_constraints": duration_constraints,
            "conflict_constraints": conflict_constraints,
            "question": question,
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply signal processing concepts to resolve scheduling conflicts."""
        entities = structure["entities"]
        temporal_constraints = structure["temporal_constraints"]
        duration_constraints = structure["duration_constraints"]
        conflict_constraints = structure["conflict_constraints"]
        question = structure["question"]
        
        # Signal processing concept: Treat scheduling as signal reconstruction
        # Each entity is a signal component, constraints are filters
        # We need to find a schedule that passes through all filters
        
        # Build constraint satisfaction problem
        variables = entities
        domains = {}
        
        # Create time slots (0-23 for hours, or 0-n for discrete slots)
        max_slots = 24  # Default to 24-hour day
        if duration_constraints:
            total_duration = sum(dur for _, dur in duration_constraints)
            max_slots = min(24, total_duration + len(entities) * 2)
        
        for entity in entities:
            domains[entity] = list(range(max_slots))
        
        # Define constraints
        constraints = []
        
        # 1. Temporal ordering constraints (before/after)
        for a, b in temporal_constraints:
            if a in domains and b in domains:
                def make_temporal_constraint(a_var, b_var):
                    def constraint(values):
                        a_val, b_val = values[a_var], values[b_var]
                        # Signal processing: ensure proper phase relationship
                        return a_val < b_val
                    return constraint
                constraints.append(([a, b], make_temporal_constraint(a, b)))
        
        # 2. Conflict constraints (cannot overlap)
        for a, b in conflict_constraints:
            if a in domains and b in domains:
                def make_conflict_constraint(a_var, b_var):
                    def constraint(values):
                        a_val, b_val = values[a_var], values[b_var]
                        # Signal processing: ensure signals don't interfere
                        return a_val != b_val
                    return constraint
                constraints.append(([a, b], make_conflict_constraint(a, b)))
        
        # 3. Duration constraints (if any)
        duration_map = dict(duration_constraints)
        for entity in entities:
            if entity in duration_map:
                duration = duration_map[entity]
                def make_duration_constraint(entity_var, dur):
                    def constraint(values):
                        # Signal processing: ensure minimum bandwidth
                        return values[entity_var] + dur <= max_slots
                    return constraint
                constraints.append(([entity], make_duration_constraint(entity, duration)))
        
        # Use T1 primitive: solve_constraints
        solution = solve_constraints(variables, domains, constraints)
        
        # Use T1 primitive: information_sufficiency
        n_unknowns = len(variables)
        n_constraints = len(constraints)
        sufficiency = information_sufficiency(n_unknowns, n_constraints)
        
        # Use amino acid: solve_first (constraint_acids)
        amino_solution = solve_first(domains, constraints)
        
        # Use amino acid: is_uniquely_solvable
        unique = is_uniquely_solvable(domains, constraints)
        
        # Use T1 primitive: topological_sort to find ordering
        topological_order = []
        if temporal_constraints:
            topological_order = topological_sort(temporal_constraints)
            if topological_order is None:
                topological_order = []
        
        # Determine answer based on question type
        computed_answer = ""
        
        # Signal processing: Compute spectral analysis of schedule
        # Entropy measures uncertainty in scheduling
        if solution:
            # Extract schedule values
            schedule_values = list(solution.values())
            # Use T1 primitive: entropy
            if schedule_values:
                probs = [1.0 / len(schedule_values)] * len(schedule_values)
                schedule_entropy = entropy(probs)
            else:
                schedule_entropy = 0.0
            
            # Find which entity to schedule first/last based on question
            question_lower = question.lower()
            if "first" in question_lower or "start" in question_lower:
                # Find entity with earliest time
                earliest_entity = min(solution.items(), key=lambda x: x[1])[0]
                computed_answer = earliest_entity
            elif "last" in question_lower or "end" in question_lower:
                # Find entity with latest time
                latest_entity = max(solution.items(), key=lambda x: x[1])[0]
                computed_answer = latest_entity
            elif "conflict" in question_lower or "problem" in question_lower:
                # Identify conflicting entities
                if conflict_constraints:
                    computed_answer = f"{conflict_constraints[0][0]} and {conflict_constraints[0][1]}"
                else:
                    computed_answer = "No conflicts"
            else:
                # Default: return the schedule feasibility
                computed_answer = "Feasible schedule exists"
        else:
            # No solution found
            if "why" in question_lower or "reason" in question_lower:
                computed_answer = "Constraints are inconsistent"
            else:
                computed_answer = "No feasible schedule"
        
        # Use T1 primitive: confidence_from_agreement
        # Create multiple scoring perspectives
        scores = []
        if solution:
            scores.append(1.0)
        if amino_solution:
            scores.append(0.9)
        if unique:
            scores.append(0.8)
        if topological_order:
            scores.append(0.7)
        
        confidence = confidence_from_agreement(scores) if scores else 0.5
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Schedule analysis: {sufficiency}, unique={unique}, entropy={schedule_entropy if 'schedule_entropy' in locals() else 0.0:.2f}",
            "solution": solution,
            "topological_order": topological_order
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                score = 1.0 * confidence
            else:
                # Fallback: NCD similarity to reasoning text
                ncd_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
                score = ncd_score * confidence * 0.7  # Penalize for not matching exact answer
            
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
        
        if max_score > min_score:
            for item in scored:
                item["score"] = (item["raw_score"] - min_score) / (max_score - min_score)
        else:
            # All scores equal
            for item in scored:
                item["score"] = 0.5
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance."""
        if not a or not b:
            return 1.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) > 0:
            return (cab - min(ca, cb)) / max(ca, cb)
        return 1.0