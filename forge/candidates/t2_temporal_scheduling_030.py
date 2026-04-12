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
    """Statistical mechanics x Constraint satisfaction - Temporal scheduling"""

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
        
        # Find events (capitalized phrases that appear as subjects)
        event_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        all_words = re.findall(r'\b\w+\b', prompt)
        
        # Look for event declarations (e.g., "Event A", "Meeting X")
        for i, line in enumerate(lines):
            matches = re.findall(event_pattern, line)
            for match in matches:
                if len(match.split()) <= 3 and match.lower() not in ['the', 'and', 'but', 'or']:
                    if match not in events:
                        events.append(match)
            
            # Look for temporal constraints
            if 'before' in line.lower() or 'after' in line.lower():
                parts = re.split(r'\bbefore\b|\bafter\b', line, flags=re.IGNORECASE)
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip().rstrip('.')
                    
                    # Extract event names from each side
                    left_events = re.findall(event_pattern, left)
                    right_events = re.findall(event_pattern, right)
                    
                    if left_events and right_events:
                        left_event = left_events[-1]
                        right_event = right_events[0]
                        
                        if 'before' in line.lower():
                            constraints.append((left_event, right_event))
                        else:  # after
                            constraints.append((right_event, left_event))
            
            # Look for duration or time constraints
            if 'minutes' in line.lower() or 'hours' in line.lower() or 'duration' in line.lower():
                # Extract numerical durations
                numbers = re.findall(r'(\d+)\s*(?:minute|hour|duration)', line.lower())
                if numbers:
                    # This could be used for statistical mechanics energy calculations
                    pass
        
        # Last line is usually the question
        if lines:
            question = lines[-1]
        
        # Remove duplicates while preserving order
        events = list(dict.fromkeys(events))
        
        return {
            "events": events,
            "constraints": constraints,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use statistical mechanics of constraint satisfaction to find optimal schedule."""
        events = structure["events"]
        constraints = structure["constraints"]
        
        if not events:
            return {"answer": "No events found", "confidence": 0.0, "reasoning": "No events extracted"}
        
        # CRITICAL PATH 1: Topological sort to find a valid ordering
        # This represents the "ground state" of the scheduling system
        topological_order = topological_sort(constraints)
        
        # CRITICAL PATH 2: Constraint satisfaction to check feasibility
        # Map events to variables for CSP
        variables = {event: [i for i in range(len(events))] for event in events}
        
        # Create constraints: if A before B, then position(A) < position(B)
        csp_constraints = []
        for a, b in constraints:
            if a in variables and b in variables:
                def make_constraint(var_a, var_b):
                    return lambda vals: vals[var_a] < vals[var_b]
                csp_constraints.append(([a, b], make_constraint(a, b)))
        
        # Use amino acid to find first solution
        solution = solve_first(variables, csp_constraints)
        
        # CRITICAL PATH 3: Check if solution is unique using amino acid
        # In statistical mechanics, uniqueness corresponds to zero entropy ground state
        is_unique = is_uniquely_solvable(variables, csp_constraints) if solution else False
        
        # CRITICAL PATH 4: Information sufficiency analysis
        # Determines if constraints fully specify the schedule
        n_unknowns = len(events)
        n_constraints = len(constraints)
        info_status = information_sufficiency(n_unknowns, n_constraints)
        
        # Statistical mechanics analogy: 
        # - Topological order = ground state configuration
        # - Constraint satisfaction = energy minimization
        # - Uniqueness = zero entropy (ordered phase)
        # - Information sufficiency = phase boundary determination
        
        # Determine the answer based on reasoning
        computed_answer = ""
        confidence = 0.5
        
        if topological_order:
            # Use topological order as the canonical schedule
            # In statistical mechanics, this is the lowest energy configuration
            computed_answer = topological_order[0]  # First event in schedule
            confidence = 0.8
            
            # Adjust confidence based on uniqueness
            if is_unique:
                confidence = 0.95  # Zero entropy ground state
            else:
                confidence = 0.7   # Degenerate ground states
            
            # Adjust based on information sufficiency
            if info_status == "determined":
                confidence = min(confidence + 0.1, 1.0)
            elif info_status == "underdetermined":
                confidence = max(confidence - 0.2, 0.3)
        elif solution:
            # Fallback to CSP solution
            # Sort events by their assigned positions
            sorted_events = sorted(solution.items(), key=lambda x: x[1])
            if sorted_events:
                computed_answer = sorted_events[0][0]  # Earliest event
                confidence = 0.6
        else:
            # No valid schedule found
            computed_answer = "No valid schedule"
            confidence = 0.3
        
        # CRITICAL PATH 5: Confidence aggregation
        # Multiple reasoning paths provide different confidence estimates
        confidences = []
        if topological_order:
            confidences.append(0.8)
        if solution:
            confidences.append(0.7)
        if is_unique is not None:
            confidences.append(0.9 if is_unique else 0.5)
        
        if confidences:
            # Use primitive to combine confidence estimates
            final_confidence = confidence_from_agreement(confidences)
            confidence = (confidence + final_confidence) / 2
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Schedule analysis: {info_status}, unique={is_unique}, topological_order_exists={bool(topological_order)}",
            "topological_order": topological_order if topological_order else [],
            "csp_solution": solution if solution else {},
            "is_unique": is_unique
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact or partial match of computed answer
            score = 0.0
            
            # Check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 0.9
            else:
                # Fallback: NCD similarity between reasoning and candidate
                ncd_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
                score = ncd_score * 0.7
            
            # Boost score if candidate mentions scheduling concepts
            scheduling_terms = ['schedule', 'order', 'before', 'after', 'first', 'last']
            if any(term in candidate.lower() for term in scheduling_terms):
                score = min(score + 0.1, 1.0)
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence from reasoning."""
        if not scored:
            return scored
        
        # Simple calibration: normalize scores to [0, 1] range
        scores = [item["raw_score"] for item in scored]
        if scores:
            min_score = min(scores)
            max_score = max(scores)
            if max_score > min_score:
                for item in scored:
                    item["score"] = (item["raw_score"] - min_score) / (max_score - min_score)
            else:
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