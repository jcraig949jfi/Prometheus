import re
import zlib
from typing import Dict, List, Any, Tuple, Optional

from forge_primitives import (
    topological_sort,
    solve_constraints,
    information_sufficiency,
    confidence_from_agreement,
    entropy,
    temporal_order
)
from forge.amino_acids.constraint_acids import is_uniquely_solvable


class ReasoningTool:
    """fluid_dynamics x constraint_acids - temporal_scheduling"""

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
        """Extract entities, constraints, and question from prompt using fluid dynamics concepts."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Fluid dynamics: events are like particles with temporal positions
        # Constraints are like flow boundaries
        events = []
        constraints = []
        durations = {}
        temporal_relations = []
        
        # Parse for event names (capitalized or quoted)
        event_pattern = r'"(.*?)"|([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        time_pattern = r'(\d+)\s*(?:hour|minute|day|week)s?'
        duration_pattern = r'lasts?\s*(\d+)\s*(?:hour|minute|day|week)s?'
        before_after_pattern = r'(before|after)\s+(?:the\s+)?(?:"(.*?)"|([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*))'
        
        for line in lines:
            # Find event names
            event_matches = re.findall(event_pattern, line)
            for match in event_matches:
                event_name = match[0] if match[0] else match[1]
                if event_name and event_name not in events and event_name != "I":
                    events.append(event_name)
            
            # Find durations
            dur_match = re.search(duration_pattern, line.lower())
            if dur_match:
                # Associate with the most recent event mentioned
                if events:
                    durations[events[-1]] = int(dur_match.group(1))
            
            # Find temporal relations
            ba_match = re.search(before_after_pattern, line.lower())
            if ba_match and events:
                relation = ba_match.group(1)
                other_event = ba_match.group(2) if ba_match.group(2) else ba_match.group(3)
                if other_event and events[-1]:
                    if relation == "before":
                        temporal_relations.append((events[-1], other_event))
                    else:
                        temporal_relations.append((other_event, events[-1]))
        
        # Remove duplicates
        events = list(set(events))
        
        # Fluid dynamics: constraints create pressure gradients
        # Extract explicit constraints like "A cannot be on Monday"
        constraint_lines = []
        for line in lines:
            if any(word in line.lower() for word in ["cannot", "must", "only", "never", "always"]):
                constraint_lines.append(line)
        
        return {
            "events": events,
            "durations": durations,
            "temporal_relations": temporal_relations,
            "constraint_lines": constraint_lines,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply fluid dynamics reasoning to scheduling constraints."""
        events = structure["events"]
        durations = structure["durations"]
        temporal_relations = structure["temporal_relations"]
        constraint_lines = structure["constraint_lines"]
        question = structure["question"]
        
        # Fluid dynamics concept: events flow through time like fluid through pipes
        # Constraints create resistance, durations create viscosity
        # We'll model this as a constraint satisfaction problem
        
        # Build domains based on extracted information
        # Default time slots if not specified
        time_slots = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Create variable domains
        variables = events
        domains = {}
        for event in events:
            domains[event] = time_slots.copy()
        
        # Apply temporal relation constraints (fluid flow direction)
        constraints = []
        
        # Constraint 1: Temporal ordering (before/after)
        for before_event, after_event in temporal_relations:
            if before_event in events and after_event in events:
                def make_order_constraint(bef, aft):
                    def constraint(values):
                        # Get indices in time_slots
                        try:
                            bef_idx = time_slots.index(values[bef])
                            aft_idx = time_slots.index(values[aft])
                            return bef_idx < aft_idx
                        except ValueError:
                            return False
                    return constraint
                
                constraints.append(([before_event, after_event], 
                                   make_order_constraint(before_event, after_event)))
        
        # Constraint 2: Duration constraints (viscosity effects)
        # Events with longer durations might restrict adjacent time slots
        for event, duration in durations.items():
            if event in events:
                # Simple constraint: if duration > 1, it might span multiple days
                # For now, just mark as requiring special handling
                pass
        
        # Constraint 3: Parse explicit constraint lines
        for line in constraint_lines:
            line_lower = line.lower()
            # Check for day restrictions
            for day in time_slots:
                if day.lower() in line_lower:
                    # Find which event this applies to
                    for event in events:
                        if event.lower() in line_lower:
                            if "cannot" in line_lower or "never" in line_lower:
                                # Remove this day from domain
                                if day in domains[event]:
                                    domains[event].remove(day)
                            elif "must" in line_lower or "only" in line_lower:
                                # Restrict to only this day
                                domains[event] = [day]
        
        # Use T1 primitive: information_sufficiency to check if problem is well-posed
        n_unknowns = len(variables)
        n_constraints = len(constraints)
        sufficiency = information_sufficiency(n_unknowns, n_constraints)
        
        # Use T1 primitive: solve_constraints to find a solution
        solution = solve_constraints(variables, domains, constraints)
        
        # Use amino acid: is_uniquely_solvable to check solution uniqueness
        unique_check = False
        if solution is not None:
            unique_check_result = is_uniquely_solvable(variables, domains, constraints)
            if unique_check_result is not None:
                unique_check = unique_check_result
        
        # Use T1 primitive: topological_sort on temporal relations
        # Build edges for topological sort
        edges = []
        for before_event, after_event in temporal_relations:
            if before_event in events and after_event in events:
                edges.append((before_event, after_event))
        
        topological_order = topological_sort(edges)
        
        # Fluid dynamics: compute "pressure" (constraint density) and "flow" (solution flexibility)
        # Pressure = constraints per variable
        pressure = n_constraints / max(1, n_unknowns)
        
        # Flow = domain size entropy (higher entropy = more flexibility)
        domain_entropies = []
        for event in events:
            if event in domains:
                # Convert domain sizes to probabilities for entropy calculation
                domain_size = len(domains[event])
                if domain_size > 0:
                    # Uniform distribution over domain
                    probs = [1.0/domain_size] * domain_size
                    domain_ent = entropy(probs)
                    domain_entropies.append(domain_ent)
        
        avg_flow = sum(domain_entropies) / max(1, len(domain_entropies)) if domain_entropies else 0
        
        # Determine answer based on question type
        computed_answer = ""
        confidence = 0.5
        
        if solution is not None:
            # If question asks for specific event timing
            if "when" in question.lower() and "what time" not in question.lower():
                # Find which event is being asked about
                for event in events:
                    if event.lower() in question.lower():
                        computed_answer = f"{event} on {solution[event]}"
                        break
                if not computed_answer and events:
                    # Default to first event
                    first_event = events[0]
                    computed_answer = f"{first_event} on {solution[first_event]}"
            
            # If question asks about feasibility or conflicts
            elif any(word in question.lower() for word in ["possible", "feasible", "conflict", "schedule"]):
                if unique_check:
                    computed_answer = "Unique schedule exists"
                else:
                    computed_answer = "Multiple schedules possible"
            
            # If question asks about specific ordering
            elif "order" in question.lower() or "sequence" in question.lower():
                if topological_order:
                    computed_answer = " -> ".join(topological_order)
                else:
                    computed_answer = "Partial order constraints"
        
        # Use T1 primitive: confidence_from_agreement
        # Create multiple confidence sources
        confidence_sources = []
        if solution is not None:
            confidence_sources.append(0.8)
        if sufficiency == "determined":
            confidence_sources.append(0.7)
        else:
            confidence_sources.append(0.3)
        if unique_check:
            confidence_sources.append(0.9)
        else:
            confidence_sources.append(0.5)
        
        if confidence_sources:
            confidence = confidence_from_agreement(confidence_sources)
        
        # Fallback if no specific answer computed
        if not computed_answer:
            if solution:
                # Create a summary of the schedule
                schedule_parts = [f"{event}: {day}" for event, day in solution.items()]
                computed_answer = "; ".join(schedule_parts)
            else:
                computed_answer = "No feasible schedule found"
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Fluid dynamics analysis: pressure={pressure:.2f}, flow={avg_flow:.2f}. {sufficiency} system.",
            "solution": solution,
            "topological_order": topological_order,
            "unique": unique_check
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback 1: NCD similarity to computed answer
                ncd1 = self._ncd(computed_answer, candidate)
                # Fallback 2: NCD similarity to reasoning text (more detailed)
                ncd2 = self._ncd(reasoning_text, candidate)
                # Use the better (lower) NCD
                score = 1.0 / (1.0 + min(ncd1, ncd2))
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using fluid dynamics pressure-flow relationship."""
        if not scored:
            return scored
        
        # Extract raw scores
        raw_scores = [item["raw_score"] for item in scored]
        
        # Fluid dynamics calibration: scores flow like fluid under pressure
        # Higher pressure (more constraints) should amplify differences
        # Lower pressure (fewer constraints) should smooth differences
        
        # For now, simple normalization to [0, 1] range
        min_score = min(raw_scores)
        max_score = max(raw_scores)
        
        if max_score > min_score:
            for item in scored:
                # Normalize and apply slight sigmoid shaping
                normalized = (item["raw_score"] - min_score) / (max_score - min_score)
                # Sigmoid to emphasize differences near 0.5
                item["score"] = 1.0 / (1.0 + (1.0 / max(0.01, normalized) - 1.0) ** 2)
        else:
            # All scores equal
            for item in scored:
                item["score"] = 0.5
        
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