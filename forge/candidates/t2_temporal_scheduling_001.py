import re
import zlib
from typing import Dict, List, Any, Tuple, Set
from forge_primitives import (
    check_transitivity,
    topological_sort,
    solve_constraints,
    confidence_from_agreement,
    information_sufficiency,
    temporal_order
)
from forge.amino_acids.constraint_acids import is_uniquely_solvable, solve_first

class ReasoningTool:
    """Relativity x Constraint Satisfaction - temporal_scheduling"""

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
        """Extract events, constraints, and question from prompt using relativity-inspired frame analysis."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        events = set()
        constraints = []
        question = lines[-1] if lines else ""
        
        # Find event names (capitalized phrases that appear in constraints)
        # In relativity, events are points in spacetime with their own reference frames
        event_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        all_names = re.findall(event_pattern, prompt)
        
        # Filter to likely events: names that appear in ordering statements
        ordering_keywords = ['before', 'after', 'during', 'while', 'when', 'must', 'cannot']
        for name in all_names:
            # Check if name appears near ordering keywords
            name_context = prompt.lower().find(name.lower())
            if name_context != -1:
                context_window = prompt[max(0, name_context-50):min(len(prompt), name_context+50)].lower()
                if any(keyword in context_window for keyword in ordering_keywords):
                    events.add(name)
        
        # Extract temporal constraints (relativity: causal structure defines light cones)
        # Format: "A before B", "A after B", "A and B cannot overlap", "A must happen during B"
        for line in lines:
            line_lower = line.lower()
            
            # Before/after relations
            if 'before' in line_lower or 'after' in line_lower:
                parts = re.split(r'\bbefore\b|\bafter\b', line_lower, flags=re.IGNORECASE)
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip()
                    
                    # Find matching event names
                    left_event = None
                    right_event = None
                    for event in events:
                        if event.lower() in left:
                            left_event = event
                        if event.lower() in right:
                            right_event = event
                    
                    if left_event and right_event:
                        if 'before' in line_lower:
                            constraints.append(('before', left_event, right_event))
                        else:  # after
                            constraints.append(('before', right_event, left_event))
            
            # Mutual exclusion (cannot overlap) - relativity: spacelike separation
            elif 'cannot' in line_lower and ('overlap' in line_lower or 'same' in line_lower):
                # Find two events mentioned
                mentioned = []
                for event in events:
                    if event.lower() in line_lower:
                        mentioned.append(event)
                if len(mentioned) >= 2:
                    for i in range(len(mentioned)):
                        for j in range(i+1, len(mentioned)):
                            constraints.append(('exclude', mentioned[i], mentioned[j]))
            
            # Duration constraints (relativity: proper time intervals)
            elif 'duration' in line_lower or 'last' in line_lower or 'take' in line_lower:
                # Extract numbers for durations
                numbers = re.findall(r'(\d+)\s*(?:hour|minute|day|week|month|year)s?', line_lower)
                if numbers:
                    # Associate with events mentioned in same line
                    line_events = [e for e in events if e.lower() in line_lower]
                    for event in line_events:
                        if event not in events:
                            continue
                        for num in numbers:
                            constraints.append(('duration', event, int(num)))
        
        # Extract the specific question about scheduling
        # In relativity, the question is about causal order in different reference frames
        question_type = "unknown"
        if 'which' in question.lower() and 'first' in question.lower():
            question_type = "first_event"
        elif 'which' in question.lower() and 'last' in question.lower():
            question_type = "last_event"
        elif 'conflict' in question.lower() or 'impossible' in question.lower():
            question_type = "conflict_detection"
        elif 'order' in question.lower() or 'sequence' in question.lower():
            question_type = "full_order"
        
        return {
            "events": list(events),
            "constraints": constraints,
            "question": question,
            "question_type": question_type,
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply relativity-inspired reasoning: events as spacetime points with causal structure."""
        events = structure["events"]
        constraints = structure["constraints"]
        question_type = structure["question_type"]
        
        # Build causal graph from before/after constraints (relativity: light cone structure)
        before_edges = []
        for const in constraints:
            if const[0] == 'before':
                before_edges.append((const[1], const[2]))
        
        # Use topological_sort primitive to check for cycles (relativity: closed timelike curves)
        topological_result = topological_sort(before_edges)
        has_cycle = topological_result is None
        
        # Use check_transitivity primitive to compute transitive closure (relativity: causal future/past)
        transitive_result = check_transitivity(before_edges)
        
        # Build CSP for scheduling (relativity: finding consistent foliations of spacetime)
        # Represent time slots as positions in sequence
        n_events = len(events)
        variables = events
        domains = {event: list(range(n_events)) for event in events}
        
        # Define constraints for CSP
        csp_constraints = []
        
        # Before/after constraints
        for const in constraints:
            if const[0] == 'before':
                A, B = const[1], const[2]
                def before_constraint(a_pos, b_pos):
                    return a_pos < b_pos
                csp_constraints.append(([A, B], before_constraint))
        
        # Mutual exclusion constraints (cannot be at same time)
        for const in constraints:
            if const[0] == 'exclude':
                A, B = const[1], const[2]
                def exclude_constraint(a_pos, b_pos):
                    return a_pos != b_pos
                csp_constraints.append(([A, B], exclude_constraint))
        
        # All events must have distinct times (relativity: worldlines cannot intersect at same proper time)
        def all_distinct(*positions):
            return len(set(positions)) == len(positions)
        csp_constraints.append((events, all_distinct))
        
        # Use solve_constraints primitive to find a solution
        solution = solve_constraints(variables, domains, csp_constraints)
        
        # Use amino acid is_uniquely_solvable to check solution uniqueness
        # Relativity: multiple foliations may be possible (different reference frames)
        unique_check = is_uniquely_solvable(variables, domains, csp_constraints)
        
        # Use information_sufficiency primitive to check if constraints determine the schedule
        # Relativity: enough data to fix the causal structure?
        n_unknowns = len(events)
        n_constraints = len([c for c in constraints if c[0] in ['before', 'exclude']])
        info_status = information_sufficiency(n_unknowns, n_constraints)
        
        # Determine answer based on question type
        computed_answer = ""
        confidence = 0.5
        reasoning = ""
        
        if solution:
            # Sort events by their assigned time
            ordered_events = sorted(solution.items(), key=lambda x: x[1])
            
            if question_type == "first_event":
                computed_answer = ordered_events[0][0]  # Event with smallest time
                confidence = 0.8
                reasoning = f"Event '{computed_answer}' must occur first based on constraint analysis"
            
            elif question_type == "last_event":
                computed_answer = ordered_events[-1][0]  # Event with largest time
                confidence = 0.8
                reasoning = f"Event '{computed_answer}' must occur last based on constraint analysis"
            
            elif question_type == "conflict_detection":
                if has_cycle:
                    computed_answer = "impossible"
                    confidence = 0.9
                    reasoning = "Cycle detected in temporal constraints makes schedule impossible"
                else:
                    computed_answer = "possible"
                    confidence = 0.7
                    reasoning = "No conflicts detected, schedule is possible"
            
            elif question_type == "full_order":
                # Return the complete sequence
                computed_answer = " -> ".join([e[0] for e in ordered_events])
                confidence = 0.75
                reasoning = f"Complete temporal order derived from constraints"
            
            else:
                # Default: return the first event
                computed_answer = ordered_events[0][0]
                confidence = 0.6
                reasoning = f"Defaulting to first event '{computed_answer}' in derived schedule"
        else:
            # No solution found
            computed_answer = "no solution"
            confidence = 0.9 if has_cycle else 0.6
            reasoning = "No valid schedule exists given the constraints"
        
        # Use confidence_from_agreement primitive to refine confidence
        # Relativity: agreement between different observers/reference frames
        agreement_scores = []
        if solution:
            agreement_scores.append(0.8)  # Solution exists
        if unique_check:
            agreement_scores.append(0.9)  # Solution is unique
        else:
            agreement_scores.append(0.5)  # Multiple solutions possible
        
        if info_status == "determined":
            agreement_scores.append(0.85)
        elif info_status == "underdetermined":
            agreement_scores.append(0.4)
        
        if agreement_scores:
            refined_confidence = confidence_from_agreement(agreement_scores)
            confidence = (confidence + refined_confidence) / 2
        
        return {
            "answer": computed_answer,
            "confidence": min(max(confidence, 0.0), 1.0),
            "reasoning": reasoning,
            "solution": solution,
            "has_cycle": has_cycle,
            "is_unique": unique_check,
            "info_status": info_status
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = str(reasoning_result["answer"])
        results = []
        
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate text
            # Relativity: different representations of same causal structure
            candidate_lower = candidate.lower()
            computed_lower = computed_answer.lower()
            
            if computed_lower in candidate_lower:
                score = 0.95  # Strong match
            else:
                # Fallback: NCD similarity
                score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using relativity-inspired normalization."""
        if not scored:
            return scored
        
        # Extract raw scores
        raw_scores = [item["raw_score"] for item in scored]
        
        if len(raw_scores) == 1:
            # Single candidate
            scored[0]["score"] = 0.5
            return scored
        
        # Relativity: normalize to local frame (min-max scaling)
        min_score = min(raw_scores)
        max_score = max(raw_scores)
        
        if max_score - min_score > 0.001:
            for item in scored:
                # Linear normalization with slight compression
                normalized = (item["raw_score"] - min_score) / (max_score - min_score)
                # Apply sigmoid-like compression to emphasize differences
                item["score"] = normalized ** 0.8
        else:
            # All scores similar - assign uniform scores
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
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)