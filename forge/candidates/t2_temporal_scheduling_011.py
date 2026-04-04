import re
import zlib
from typing import List, Dict, Any, Tuple

from forge_primitives import (
    topological_sort,
    information_sufficiency,
    solve_constraints,
    confidence_from_agreement,
    entropy,
    dag_traverse
)
from forge.amino_acids.constraint_acids import is_uniquely_solvable

class ReasoningTool:
    """Electromagnetism x Constraint Satisfaction - temporal_scheduling"""

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
        """Parse prompt to extract events, temporal constraints, and question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        
        events = []
        constraints = []
        question = lines[-1] if lines else ""
        
        # Extract event names (capitalized words that appear as entities)
        # Look for patterns like "Event A", "Meeting X", "Task 1"
        event_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*|\b[A-Z]\b|\bTask\s+\d+\b|\bMeeting\s+\w+\b)'
        
        # Extract temporal relations: "before", "after", "must occur between", "cannot overlap"
        temporal_keywords = ['before', 'after', 'between', 'overlap', 'simultaneous', 'concurrent']
        
        for line in lines:
            # Find potential event names
            found_events = re.findall(event_pattern, line)
            for ev in found_events:
                if ev not in events and len(ev) > 1:  # Filter out single letters unless they're standalone
                    events.append(ev)
            
            # Extract temporal constraints
            if 'before' in line.lower():
                # Pattern: "Event A before Event B"
                parts = line.lower().split('before')
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip()
                    # Match to actual event names
                    left_event = self._match_event(left, events)
                    right_event = self._match_event(right, events)
                    if left_event and right_event:
                        constraints.append((left_event, right_event, 'before'))
            
            elif 'after' in line.lower():
                # Pattern: "Event A after Event B"
                parts = line.lower().split('after')
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip()
                    left_event = self._match_event(left, events)
                    right_event = self._match_event(right, events)
                    if left_event and right_event:
                        constraints.append((right_event, left_event, 'before'))  # Convert 'after' to 'before'
            
            # Extract duration or time window constraints
            time_pattern = r'(\d+)\s*(?:hour|minute|second|day)s?'
            times = re.findall(time_pattern, line.lower())
            if times and found_events:
                # Associate time with the last mentioned event
                event = found_events[-1]
                if 'duration' in line.lower() or 'lasts' in line.lower():
                    # This is a duration constraint
                    if 'duration' not in structure:
                        structure['durations'] = {}
                    structure['durations'][event] = int(times[0])
        
        # Clean up events list (remove duplicates and empty strings)
        events = [e for e in events if e and len(e) > 1]
        
        return {
            "events": events,
            "constraints": constraints,
            "question": question,
            "raw": prompt
        }

    def _match_event(self, text: str, events: List[str]) -> str:
        """Find the event name that best matches the text."""
        text_lower = text.lower()
        for event in events:
            if event.lower() in text_lower or text_lower in event.lower():
                return event
        # Try to find by first word
        first_word = text.split()[0] if text.split() else ""
        for event in events:
            if first_word.lower() in event.lower():
                return event
        return ""

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use electromagnetic field theory to resolve scheduling conflicts.
        
        Conceptual mapping:
        - Events = charged particles
        - Temporal constraints = electromagnetic forces (attraction/repulsion)
        - Schedule = field configuration minimizing potential energy
        - Conflicts = repulsive forces that cannot be satisfied
        - Solution = stable equilibrium configuration
        """
        events = structure["events"]
        constraints = structure["constraints"]
        
        # Convert constraints to DAG edges for topological sort
        edges = []
        for src, dst, rel in constraints:
            if rel == 'before':
                edges.append((src, dst))
        
        # Use topological_sort primitive (T1) - represents field line ordering
        try:
            sorted_events = topological_sort(edges)
            if sorted_events is None:
                # Cyclic constraints detected - electromagnetic repulsion too strong
                sorted_events = []
        except Exception:
            sorted_events = []
        
        # Use information_sufficiency primitive (T1) - check if system is determined
        # Analogous to checking if field equations have unique solution
        n_events = len(events)
        n_constraints = len(constraints)
        sufficiency = information_sufficiency(n_events, n_constraints)
        
        # Use solve_constraints primitive (T1) - find valid schedule
        # Map to finding potential minimum in electromagnetic field
        variables = events
        domains = {event: list(range(len(events))) for event in events}  # Simple ordering
        
        def before_constraint(a_val, b_val):
            return a_val < b_val
        
        constraint_list = []
        for src, dst, rel in constraints:
            if rel == 'before':
                constraint_list.append(([src, dst], before_constraint))
        
        schedule_solution = solve_constraints(variables, domains, constraint_list)
        
        # Use is_uniquely_solvable amino acid - check solution uniqueness
        # Analogous to checking if field has unique ground state
        unique_solution = False
        try:
            unique_solution = is_uniquely_solvable(
                {v: list(range(len(events))) for v in events},
                constraint_list
            )
        except Exception:
            unique_solution = False
        
        # Use entropy primitive (T1) - measure uncertainty in schedule
        # Analogous to entropy of field configuration
        if schedule_solution:
            # Create probability distribution from solution
            positions = list(schedule_solution.values())
            max_pos = max(positions) if positions else 1
            probs = [positions.count(i) / len(positions) for i in range(max_pos + 1)]
            schedule_entropy = entropy(probs) if probs else 0.0
        else:
            schedule_entropy = 1.0  # Maximum entropy = completely disordered
        
        # Determine answer based on electromagnetic stability
        if schedule_solution:
            # Find the event that appears first in all valid schedules (lowest potential)
            # This is the event with minimum position in the solution
            if sorted_events:
                computed_answer = sorted_events[0]  # First in topological order
            else:
                # Use the event with smallest position in constraint solution
                min_pos_event = min(schedule_solution.items(), key=lambda x: x[1])[0]
                computed_answer = min_pos_event
            confidence = 0.9 - (schedule_entropy * 0.5)  # Lower entropy = higher confidence
        else:
            # No valid schedule - electromagnetic repulsion prevents solution
            computed_answer = "No valid schedule exists"
            confidence = 0.5
        
        # Use confidence_from_agreement primitive (T1) - combine multiple indicators
        confidence_sources = []
        if sorted_events:
            confidence_sources.append(0.8)
        if schedule_solution:
            confidence_sources.append(0.7)
        if unique_solution:
            confidence_sources.append(0.9)
        else:
            confidence_sources.append(0.3)
        
        if confidence_sources:
            final_confidence = confidence_from_agreement(confidence_sources)
        else:
            final_confidence = confidence
        
        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "reasoning": f"Electromagnetic field analysis: {sufficiency}, entropy={schedule_entropy:.2f}, unique={unique_solution}",
            "schedule": schedule_solution,
            "sorted_events": sorted_events
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            results.append({
                "candidate": candidate,
                "raw_score": score,
                "reasoning_match": reasoning_result
            })
        
        return results

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

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence from reasoning."""
        if not scored:
            return scored
        
        # Get confidence from reasoning result
        confidence = scored[0]["reasoning_match"]["confidence"]
        
        # Adjust scores based on confidence
        calibrated = []
        for item in scored:
            raw_score = item["raw_score"]
            # Scale score by confidence (higher confidence = less adjustment)
            adjusted_score = raw_score * (0.5 + 0.5 * confidence)
            
            calibrated.append({
                "candidate": item["candidate"],
                "score": adjusted_score,
                "raw_score": raw_score,
                "confidence": confidence
            })
        
        return calibrated