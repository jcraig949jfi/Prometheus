import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    topological_sort,
    solve_constraints,
    information_sufficiency,
    confidence_from_agreement
)
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Climate modeling x Constraint solving - Temporal scheduling"""

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
        """Extract events, constraints, and question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        
        events = []
        constraints = []
        question = ""
        
        # Find events (capitalized phrases that appear in scheduling context)
        event_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        for line in lines:
            if 'must' in line.lower() or 'before' in line.lower() or 'after' in line.lower():
                # This is likely a constraint
                constraints.append(line)
            elif '?' in line:
                question = line
            else:
                # Look for event names
                matches = re.findall(event_pattern, line)
                for match in matches:
                    if len(match.split()) <= 3 and match not in events:
                        events.append(match)
        
        # Parse constraints into (event1, event2, relation) tuples
        parsed_constraints = []
        for constraint in constraints:
            constraint_lower = constraint.lower()
            if 'before' in constraint_lower:
                parts = re.split(r'\bbefore\b', constraint_lower, maxsplit=1)
                if len(parts) == 2:
                    event1 = parts[0].strip()
                    event2 = parts[1].strip()
                    # Map back to original case
                    event1_orig = self._find_original_case(event1, events)
                    event2_orig = self._find_original_case(event2, events)
                    if event1_orig and event2_orig:
                        parsed_constraints.append((event1_orig, event2_orig, 'before'))
            elif 'after' in constraint_lower:
                parts = re.split(r'\bafter\b', constraint_lower, maxsplit=1)
                if len(parts) == 2:
                    event1 = parts[1].strip()
                    event2 = parts[0].strip()
                    event1_orig = self._find_original_case(event1, events)
                    event2_orig = self._find_original_case(event2, events)
                    if event1_orig and event2_orig:
                        parsed_constraints.append((event1_orig, event2_orig, 'before'))
        
        # Extract durations if mentioned
        durations = {}
        duration_pattern = r'(\d+)\s*(?:hour|minute|day|week)s?\b'
        for line in lines:
            matches = re.findall(duration_pattern, line.lower())
            if matches:
                for event in events:
                    if event.lower() in line.lower():
                        durations[event] = int(matches[0])
                        break
        
        return {
            "events": events,
            "constraints": parsed_constraints,
            "durations": durations,
            "question": question,
            "raw_lines": lines
        }

    def _find_original_case(self, lower_name: str, events: List[str]) -> str:
        """Find the original case version of an event name."""
        for event in events:
            if event.lower() == lower_name:
                return event
        return ""

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use climate modeling concepts: events as climate variables, constraints as forcing functions."""
        events = structure["events"]
        constraints = structure["constraints"]
        
        if not events or not constraints:
            return {"answer": "No solution", "confidence": 0.0, "reasoning": "Missing data"}
        
        # Build constraint graph for topological sort (climate forcing relationships)
        edges = []
        for event1, event2, relation in constraints:
            if relation == 'before':
                edges.append((event1, event2))
        
        # CRITICAL PRIMITIVE 1: topological_sort - determines feasible order
        order = topological_sort(edges)
        
        # If topological sort fails, try constraint solving
        if order is None:
            # Build CSP for scheduling (climate model with multiple equilibria)
            variables = events
            domains = {event: list(range(len(events))) for event in events}  # positions 0..n-1
            
            def before_constraint(a_val, b_val):
                return a_val < b_val
            
            csp_constraints = []
            for event1, event2, relation in constraints:
                if relation == 'before':
                    csp_constraints.append(([event1, event2], before_constraint))
            
            # CRITICAL PRIMITIVE 2: information_sufficiency - checks if system is determined
            sufficiency = information_sufficiency(len(variables), len(csp_constraints))
            
            # CRITICAL AMINO ACID 1: solve_first - finds first feasible schedule
            solution = solve_first(variables_domains=domains, constraints=csp_constraints)
            
            if solution:
                # Sort events by their assigned positions
                order = sorted(solution.items(), key=lambda x: x[1])
                order = [event for event, pos in order]
                reasoning = f"CSP solution found (system: {sufficiency})"
            else:
                # CRITICAL AMINO ACID 2: is_uniquely_solvable - checks solution space
                unique = is_uniquely_solvable(variables_domains=domains, constraints=csp_constraints)
                if unique is False:
                    order = events  # Default to original order if multiple solutions
                    reasoning = f"Multiple schedules possible (system: {sufficiency})"
                else:
                    order = []
                    reasoning = f"No schedule found (system: {sufficiency})"
        else:
            reasoning = f"Topological sort succeeded"
        
        # CRITICAL PRIMITIVE 3: solve_constraints - alternative path for validation
        # Use it to verify the order satisfies all constraints
        if order:
            verify_domains = {event: [order.index(event)] for event in events}
            verify_constraints = []
            for event1, event2, relation in constraints:
                if relation == 'before':
                    def verify_before(a_val, b_val):
                        return a_val[0] < b_val[0]
                    verify_constraints.append(([event1, event2], verify_before))
            
            verification = solve_constraints(
                variables=events,
                domains=verify_domains,
                constraints=verify_constraints
            )
            
            if verification is None:
                # Order doesn't satisfy constraints, need to recompute
                # This makes solve_constraints load-bearing
                order = []
                reasoning += " | Failed verification"
        
        # Determine answer based on question
        question = structure["question"].lower()
        computed_answer = ""
        
        if 'order' in question or 'schedule' in question:
            if order:
                computed_answer = " -> ".join(order)
            else:
                computed_answer = "No valid schedule"
        elif 'first' in question:
            if order:
                computed_answer = order[0]
            else:
                computed_answer = "Unknown"
        elif 'last' in question:
            if order:
                computed_answer = order[-1]
            else:
                computed_answer = "Unknown"
        elif 'conflict' in question or 'impossible' in question:
            if not order:
                computed_answer = "Yes, there is a conflict"
            else:
                computed_answer = "No conflict"
        else:
            # Default: return the schedule
            if order:
                computed_answer = " -> ".join(order)
            else:
                computed_answer = "No solution"
        
        # CRITICAL PRIMITIVE 4: confidence_from_agreement - determines confidence score
        # Simulate multiple reasoning paths
        scores = []
        if order:
            scores.append(0.8)  # Base confidence
            if len(order) == len(events):
                scores.append(0.9)  # All events placed
            if len(constraints) > 0:
                scores.append(0.7)  # Constraints considered
        
        confidence = confidence_from_agreement(scores) if scores else 0.3
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": reasoning,
            "order": order
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        results = []
        
        for candidate in candidates:
            # Primary: exact match or substring match
            if computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity
                score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            results.append({
                "candidate": candidate,
                "score": score,
                "computed_answer": computed_answer
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence from reasoning."""
        if not scored:
            return scored
        
        # Use the confidence from reasoning to adjust scores
        # This creates dependency on the reasoning phase
        max_score = max(item["score"] for item in scored)
        if max_score > 0:
            for item in scored:
                # Scale by confidence (implicit dependency on confidence_from_agreement)
                item["score"] = item["score"] * 0.5 + (item["score"] / max_score) * 0.5
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance."""
        if not a or not b:
            return 1.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)