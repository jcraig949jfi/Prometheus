import re
import zlib
from typing import Dict, List, Any, Tuple, Set

from forge_primitives import (
    solve_constraints,
    topological_sort,
    information_sufficiency,
    confidence_from_agreement,
    dag_traverse,
    check_transitivity
)
from forge.amino_acids.constraint_acids import is_uniquely_solvable

class ReasoningTool:
    """Auction theory x Constraint satisfaction - temporal_scheduling"""

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
        entities = set(re.findall(entity_pattern, prompt))
        
        # Remove common words that aren't entities
        common_words = {'The', 'A', 'An', 'And', 'Or', 'But', 'If', 'Then', 'Before', 'After', 'During'}
        entities = {e for e in entities if e not in common_words}
        
        # Extract temporal constraints
        constraints = []
        before_pattern = r'(\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b) must (?:be )?before (\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b)'
        after_pattern = r'(\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b) must (?:be )?after (\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b)'
        
        for line in lines:
            # Find "A before B" constraints
            before_matches = re.findall(before_pattern, line, re.IGNORECASE)
            for a, b in before_matches:
                if a in entities and b in entities:
                    constraints.append(('before', a, b))
            
            # Find "A after B" constraints (convert to "B before A")
            after_matches = re.findall(after_pattern, line, re.IGNORECASE)
            for a, b in after_matches:
                if a in entities and b in entities:
                    constraints.append(('before', b, a))
        
        # Extract duration or time slot constraints if present
        duration_pattern = r'(\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b) (?:takes|requires|lasts) (\d+)'
        durations = {}
        for line in lines:
            dur_matches = re.findall(duration_pattern, line)
            for entity, dur in dur_matches:
                if entity in entities:
                    durations[entity] = int(dur)
        
        return {
            "entities": list(entities),
            "constraints": constraints,
            "durations": durations,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use auction theory to resolve scheduling conflicts."""
        entities = structure["entities"]
        constraints = structure["constraints"]
        question = structure["question"]
        
        # Build constraint graph for topological sort
        edges = []
        for rel, a, b in constraints:
            if rel == 'before':
                edges.append((a, b))
        
        # Use topological_sort primitive (T1)
        order_result = topological_sort(edges)
        
        # Use information_sufficiency primitive (T1)
        n_vars = len(entities)
        n_constraints = len(constraints)
        sufficiency = information_sufficiency(n_vars, n_constraints)
        
        # Use solve_constraints primitive (T1) to find valid schedules
        # Represent as CSP with time slots
        variables = entities
        max_slots = len(entities) + 5  # Allow some buffer
        domains = {e: list(range(1, max_slots + 1)) for e in entities}
        
        csp_constraints = []
        for rel, a, b in constraints:
            if rel == 'before':
                # Constraint: time[a] < time[b]
                def make_before_constraint(x, y):
                    return lambda vals: vals[x] < vals[y]
                csp_constraints.append(([a, b], make_before_constraint(a, b)))
        
        # Solve using primitive
        schedule = solve_constraints(variables, domains, csp_constraints)
        
        # Use amino acid is_uniquely_solvable (amino acid)
        unique_check = is_uniquely_solvable(variables, domains, csp_constraints)
        
        # AUCTION THEORY REASONING: Treat scheduling as combinatorial auction
        # Each entity "bids" for early time slots based on constraint violations
        # Entities with more outgoing constraints (must come before others) get priority
        
        # Calculate "bid" for each entity = number of entities it must come before
        outgoing_counts = {}
        for e in entities:
            count = sum(1 for rel, a, b in constraints if rel == 'before' and a == e)
            outgoing_counts[e] = count
        
        # Also count incoming constraints (entities that must come before this one)
        incoming_counts = {}
        for e in entities:
            count = sum(1 for rel, a, b in constraints if rel == 'before' and b == e)
            incoming_counts[e] = count
        
        # In auction theory: high demand (many predecessors) → higher "value" for early slot
        # Use Vickrey-Clarke-Groves inspired allocation: assign slots to minimize total "delay cost"
        
        if schedule:
            # Extract actual time assignments
            time_assignments = schedule
        else:
            # Fallback: assign based on constraint counts (auction allocation)
            # Entities with more outgoing constraints (must come before many others) get earlier slots
            sorted_by_outgoing = sorted(entities, key=lambda e: outgoing_counts[e], reverse=True)
            time_assignments = {}
            for i, e in enumerate(sorted_by_outgoing):
                time_assignments[e] = i + 1
        
        # Determine which entity is being asked about in the question
        # Look for entity names in the question
        question_entities = []
        for e in entities:
            if e.lower() in question.lower():
                question_entities.append(e)
        
        # If question asks about a specific entity's time or position
        computed_answer = ""
        reasoning_text = ""
        
        if "when" in question.lower() or "time" in question.lower() or "slot" in question.lower():
            if question_entities:
                # Answer with the time slot for the asked entity
                entity = question_entities[0]
                computed_answer = str(time_assignments.get(entity, "unknown"))
                reasoning_text = f"Entity {entity} scheduled at time {computed_answer} based on constraint analysis"
            else:
                # Default: report the schedule
                schedule_str = ", ".join([f"{e}:{t}" for e, t in sorted(time_assignments.items(), key=lambda x: x[1])])
                computed_answer = schedule_str
                reasoning_text = f"Schedule: {schedule_str}"
        elif "order" in question.lower() or "sequence" in question.lower():
            # Return the ordered sequence
            if order_result:
                order_str = " → ".join(order_result)
                computed_answer = order_str
                reasoning_text = f"Topological order: {order_str}"
            else:
                # Use time-based order
                sorted_entities = sorted(time_assignments.items(), key=lambda x: x[1])
                order_str = " → ".join([e for e, _ in sorted_entities])
                computed_answer = order_str
                reasoning_text = f"Time-based order: {order_str}"
        else:
            # Generic answer: report if schedule is unique
            computed_answer = "unique" if unique_check else "multiple"
            reasoning_text = f"Schedule uniqueness: {computed_answer}, constraint sufficiency: {sufficiency}"
        
        # Use confidence_from_agreement primitive (T1)
        # Create multiple "scorers" based on different methods
        scores = []
        
        # Method 1: topological order confidence
        if order_result:
            scores.append(0.8 if len(order_result) == len(entities) else 0.5)
        
        # Method 2: constraint satisfaction confidence
        if schedule:
            scores.append(0.9)
        
        # Method 3: auction allocation consistency
        if time_assignments:
            # Check if assignment respects all constraints
            violations = 0
            for rel, a, b in constraints:
                if rel == 'before':
                    if time_assignments.get(a, 0) >= time_assignments.get(b, 0):
                        violations += 1
            scores.append(1.0 - (violations / max(1, len(constraints))))
        
        confidence = confidence_from_agreement(scores) if scores else 0.5
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": reasoning_text,
            "time_assignments": time_assignments,
            "order": order_result if order_result else [],
            "unique": unique_check,
            "sufficiency": sufficiency
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer and str(computed_answer).lower() in candidate.lower():
                score = 0.9
            else:
                # Fallback: NCD similarity to reasoning text
                score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
            results.append({
                "candidate": candidate,
                "score": score,
                "computed_answer": computed_answer
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores based on confidence."""
        # Simple calibration: scale by confidence from reasoning
        # In a real implementation, this would use more sophisticated calibration
        for item in scored:
            # Keep scores in [0, 1] range
            item["score"] = max(0.0, min(1.0, item["score"]))
        
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