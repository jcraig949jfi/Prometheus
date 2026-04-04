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
from forge.amino_acids.constraint_acids import is_uniquely_solvable


class ReasoningTool:
    """signal_processing x constraint_acids - temporal_scheduling"""

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
        """Extract events, temporal constraints, and question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        
        events = []
        constraints = []
        question = lines[-1] if lines else ""
        
        # Signal processing concept: treat events as discrete time signals
        # Extract event names (capitalized words that appear as entities)
        for line in lines:
            # Find potential event names (capitalized multi-word phrases)
            # This is like detecting signal components in a waveform
            potential_events = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', line)
            for event in potential_events:
                if event not in events and len(event.split()) <= 3:  # Filter out long phrases
                    events.append(event)
            
            # Extract temporal constraints (before/after relationships)
            # This is like identifying phase relationships between signals
            if 'before' in line.lower() or 'after' in line.lower():
                words = line.split()
                for i, word in enumerate(words):
                    if word.lower() == 'before':
                        if i > 0 and i < len(words) - 1:
                            event_a = words[i-1]
                            event_b = words[i+1]
                            constraints.append((event_a, event_b, 'before'))
                    elif word.lower() == 'after':
                        if i > 0 and i < len(words) - 1:
                            event_a = words[i+1]  # "A after B" means B before A
                            event_b = words[i-1]
                            constraints.append((event_a, event_b, 'before'))
        
        # Also look for numerical time constraints (like "takes X hours")
        # This is like extracting signal durations
        durations = {}
        for line in lines:
            time_matches = re.findall(r'(\d+)\s*(?:hour|minute|day|week)s?', line.lower())
            if time_matches:
                # Try to associate with nearby event
                for event in events:
                    if event.lower() in line.lower():
                        durations[event] = int(time_matches[0])
                        break
        
        return {
            "events": events,
            "constraints": constraints,
            "durations": durations,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use signal processing concepts to resolve scheduling conflicts."""
        events = structure["events"]
        constraints = structure["constraints"]
        durations = structure["durations"]
        
        if not events:
            return {"answer": "No events found", "confidence": 0.0, "reasoning": "Extraction failed"}
        
        # Signal processing concept: treat scheduling as signal reconstruction
        # Each event is a signal component, constraints are phase relationships
        # We need to find a valid ordering (signal sequence) that satisfies all phase constraints
        
        # Convert constraints to DAG edges for topological sort
        edges = []
        for a, b, rel in constraints:
            if rel == 'before':
                edges.append((a, b))
        
        # Use topological_sort primitive (T1)
        ordering = topological_sort(edges)
        
        # Use information_sufficiency primitive (T1)
        # Check if we have enough constraints to determine a unique order
        sufficiency = information_sufficiency(len(events), len(constraints))
        
        # Build constraint satisfaction problem for more complex cases
        # This is like solving for signal timing with multiple constraints
        variables = events
        domains = {event: list(range(len(events))) for event in events}  # Positions 0..n-1
        
        def all_different_constraint(vars_vals):
            """All events must have different positions."""
            positions = [vars_vals[var] for var in vars_vals]
            return len(set(positions)) == len(positions)
        
        def before_constraint(vars_vals, a, b):
            """Event A must come before event B."""
            return vars_vals.get(a, -1) < vars_vals.get(b, len(events))
        
        csp_constraints = []
        csp_constraints.append((events, all_different_constraint))
        
        for a, b, rel in constraints:
            if rel == 'before':
                csp_constraints.append(([a, b], lambda vals, a=a, b=b: before_constraint(vals, a, b)))
        
        # Use solve_constraints primitive (T1)
        solution = solve_constraints(variables, domains, csp_constraints)
        
        # Use amino acid is_uniquely_solvable
        unique_check = is_uniquely_solvable(variables, domains, csp_constraints)
        
        # Signal processing: compute entropy of possible orderings
        # Low entropy = more certain schedule (like low noise in signal)
        if solution:
            # Create probability distribution over events based on their positions
            # Events that can only be in few positions have low entropy
            position_counts = {event: [0] * len(events) for event in events}
            
            # Simple heuristic: events with many constraints have more certain positions
            constraint_counts = {event: 0 for event in events}
            for a, b, _ in constraints:
                constraint_counts[a] = constraint_counts.get(a, 0) + 1
                constraint_counts[b] = constraint_counts.get(b, 0) + 1
            
            # Normalize to probabilities
            max_constraints = max(constraint_counts.values()) if constraint_counts else 1
            probs = [constraint_counts.get(event, 0) / max_constraints for event in events]
            
            # Use entropy primitive (T1)
            schedule_entropy = entropy(probs) if probs else 1.0
            
            # Determine which event is most constrained (likely answer to "which must be first/last")
            if constraint_counts:
                most_constrained = max(constraint_counts.items(), key=lambda x: x[1])[0]
                least_constrained = min(constraint_counts.items(), key=lambda x: x[1])[0]
            else:
                most_constrained = events[0] if events else ""
                least_constrained = events[-1] if events else ""
            
            # Signal processing: confidence is inverse of entropy (like signal-to-noise ratio)
            confidence = 1.0 - min(schedule_entropy, 1.0)
            
            # Determine answer based on question
            question = structure["question"].lower()
            computed_answer = ""
            
            if "first" in question or "begin" in question:
                if ordering:
                    computed_answer = ordering[0]
                elif solution:
                    # Find event with smallest position in solution
                    computed_answer = min(solution.items(), key=lambda x: x[1])[0]
                else:
                    computed_answer = most_constrained
            elif "last" in question or "end" in question or "after" in question:
                if ordering:
                    computed_answer = ordering[-1]
                elif solution:
                    # Find event with largest position in solution
                    computed_answer = max(solution.items(), key=lambda x: x[1])[0]
                else:
                    computed_answer = least_constrained
            elif "conflict" in question or "impossible" in question:
                # Check if scheduling is impossible (like conflicting phase relationships)
                if not ordering and not solution:
                    computed_answer = "Yes"  # Conflict exists
                else:
                    computed_answer = "No"   # No conflict
            else:
                # Default: return the most constrained event
                computed_answer = most_constrained
            
            # Use confidence_from_agreement primitive (T1)
            # Create multiple scoring methods and check agreement
            scores = []
            if ordering:
                scores.append(confidence * 0.8)  # Weight for topological sort
            if solution:
                scores.append(confidence * 0.9)  # Weight for CSP solution
            if unique_check is not None:
                scores.append(0.7 if unique_check else 0.3)  # Weight for uniqueness
            
            final_confidence = confidence_from_agreement(scores) if scores else confidence
            
            reasoning_text = f"Signal processing analysis: {len(events)} events, {len(constraints)} constraints. "
            reasoning_text += f"Sufficiency: {sufficiency}. "
            if ordering:
                reasoning_text += f"Topological order: {' → '.join(ordering)}. "
            if solution:
                reasoning_text += f"CSP solution found. "
            reasoning_text += f"Entropy: {schedule_entropy:.2f} (lower = more certain). "
            reasoning_text += f"Most constrained event: {most_constrained}."
            
            return {
                "answer": computed_answer,
                "confidence": final_confidence,
                "reasoning": reasoning_text,
                "ordering": ordering if ordering else [],
                "solution": solution if solution else {}
            }
        
        else:
            # No solution found - conflict exists
            return {
                "answer": "Conflict detected",
                "confidence": 0.8,
                "reasoning": f"No valid schedule found for {len(events)} events with {len(constraints)} constraints.",
                "ordering": [],
                "solution": {}
            }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result.get("answer", "")
        reasoning_text = reasoning_result.get("reasoning", "")
        
        results = []
        
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 0.9  # Strong match
            else:
                # Fallback: NCD similarity with reasoning text
                score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
            results.append({
                "candidate": candidate,
                "score": score,
                "computed_answer": computed_answer
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        scores = [item["score"] for item in scored]
        if not scores:
            return scored
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score > min_score:
            # Normalize to 0-1 range
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
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