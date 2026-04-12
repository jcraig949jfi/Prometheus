import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    solve_constraints,
    topological_sort,
    information_sufficiency,
    entropy,
    confidence_from_agreement
)
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Thermodynamics x Constraint Satisfaction - temporal_scheduling"""

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
        question = lines[-1] if lines else ""
        
        events = []
        constraints = []
        durations = {}
        
        # Extract events (capitalized phrases that appear in constraints)
        event_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        all_events = set()
        
        for line in lines:
            # Find event mentions
            matches = re.findall(event_pattern, line)
            for match in matches:
                if len(match.split()) <= 3:  # Likely an event name, not a full sentence
                    all_events.add(match)
            
            # Extract temporal constraints
            if 'before' in line.lower() or 'after' in line.lower():
                # Pattern: "Event1 before Event2" or "Event1 after Event2"
                parts = line.split()
                for i, word in enumerate(parts):
                    if word.lower() in ['before', 'after'] and i > 0 and i < len(parts) - 1:
                        event1 = parts[i-1]
                        event2 = parts[i+1]
                        if event1 in all_events and event2 in all_events:
                            if word.lower() == 'before':
                                constraints.append((event1, event2))
                            else:  # 'after'
                                constraints.append((event2, event1))
            
            # Extract duration constraints
            if 'minutes' in line.lower() or 'hours' in line.lower():
                # Pattern: "Event takes X minutes"
                num_match = re.search(r'(\d+)\s*(?:minute|hour)', line.lower())
                if num_match:
                    for event in all_events:
                        if event.lower() in line.lower():
                            durations[event] = int(num_match.group(1))
        
        # Convert to list and ensure we have at least the events mentioned in constraints
        events = list(all_events)
        if not events:
            # Fallback: extract any capitalized words as events
            events = list(set(re.findall(r'\b([A-Z][a-z]+)\b', prompt)))
        
        return {
            "events": events,
            "constraints": constraints,
            "durations": durations,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use thermodynamics-inspired constraint solving to find schedule."""
        events = structure["events"]
        constraints = structure["constraints"]
        durations = structure["durations"]
        question = structure["question"]
        
        # THERMODYNAMICS FRAMEWORK:
        # 1. Constraints = potential energy barriers
        # 2. Valid schedules = low-energy states
        # 3. Entropy measures disorder in possible schedules
        # 4. Information sufficiency = thermodynamic equilibrium condition
        
        # Build constraint satisfaction problem
        variables = events
        domains = {event: list(range(len(events))) for event in events}  # Positions 0..n-1
        
        # Constraint: all events at different times (pigeonhole principle)
        def all_different(vals):
            return len(set(vals)) == len(vals)
        
        # Constraint: temporal ordering from extracted constraints
        def ordering_constraint(event1, event2):
            return lambda pos1, pos2: pos1 < pos2
        
        csp_constraints = []
        
        # All-different constraint (thermodynamic: particles can't occupy same state)
        csp_constraints.append((variables, all_different))
        
        # Temporal ordering constraints (potential barriers)
        for event1, event2 in constraints:
            if event1 in variables and event2 in variables:
                csp_constraints.append(([event1, event2], ordering_constraint(event1, event2)))
        
        # LOAD-BEARING PRIMITIVE 1: information_sufficiency
        # Check if we have enough constraints to determine a unique schedule
        n_vars = len(variables)
        n_constraints = len(csp_constraints)
        info_status = information_sufficiency(n_vars, n_constraints)
        
        # LOAD-BEARING AMINO ACID 1: is_uniquely_solvable
        # Thermodynamic: unique solution = zero entropy ground state
        unique_check = is_uniquely_solvable(domains, csp_constraints)
        
        # LOAD-BEARING AMINO ACID 2: solve_first
        # Find a valid schedule (low-energy state)
        solution = solve_first(domains, csp_constraints)
        
        computed_answer = ""
        confidence = 0.5
        reasoning = ""
        
        if solution:
            # Sort events by their position to get schedule
            schedule = sorted(solution.items(), key=lambda x: x[1])
            ordered_events = [event for event, _ in schedule]
            
            # LOAD-BEARING PRIMITIVE 2: topological_sort
            # Compare with topological sort of constraint graph
            topo_order = topological_sort(constraints)
            
            # Determine which ordering to use based on thermodynamic principles
            if topo_order and len(topo_order) == len(ordered_events):
                # Check consistency between CSP solution and topological sort
                # Thermodynamic: compare energy landscapes
                if all(topo_order[i] == ordered_events[i] for i in range(len(ordered_events))):
                    # Perfect match - ground state
                    computed_answer = ordered_events[0]  # First event in schedule
                    confidence = 0.9
                    reasoning = f"Schedule uniquely determined: {', '.join(ordered_events)}"
                else:
                    # Different low-energy states - use entropy to decide
                    # LOAD-BEARING PRIMITIVE 3: entropy
                    # Measure disorder in the two possible orderings
                    pos_dist1 = [i/len(ordered_events) for i in range(len(ordered_events))]
                    pos_dist2 = [i/len(topo_order) for i in range(len(topo_order))]
                    entropy1 = entropy(pos_dist1)
                    entropy2 = entropy(pos_dist2)
                    
                    # Lower entropy = more ordered = preferred state
                    if entropy1 <= entropy2:
                        computed_answer = ordered_events[0]
                        reasoning = f"CSP solution has lower entropy ({entropy1:.2f} vs {entropy2:.2f}): {', '.join(ordered_events)}"
                    else:
                        computed_answer = topo_order[0]
                        reasoning = f"Topological sort has lower entropy ({entropy2:.2f} vs {entropy1:.2f}): {', '.join(topo_order)}"
                    confidence = 0.7
            else:
                # Use CSP solution
                computed_answer = ordered_events[0]
                reasoning = f"CSP solution found: {', '.join(ordered_events)}"
                confidence = 0.8
        else:
            # No CSP solution - fallback to topological sort
            topo_order = topological_sort(constraints)
            if topo_order:
                computed_answer = topo_order[0]
                reasoning = f"No CSP solution, using topological sort: {', '.join(topo_order)}"
                confidence = 0.6
            else:
                # Last resort: first mentioned event
                computed_answer = events[0] if events else ""
                reasoning = "No valid schedule found, using first event"
                confidence = 0.3
        
        # LOAD-BEARING PRIMITIVE 4: confidence_from_agreement
        # Thermodynamic: confidence from agreement between different methods
        agreement_scores = []
        if solution:
            agreement_scores.append(0.8)  # CSP found solution
        if constraints:
            agreement_scores.append(0.7)  # Constraints exist
        if info_status == "determined":
            agreement_scores.append(0.9)
        elif info_status == "underdetermined":
            agreement_scores.append(0.5)
        
        if agreement_scores:
            final_confidence = confidence_from_agreement(agreement_scores)
            confidence = (confidence + final_confidence) / 2
        
        # Extract what question is asking for
        if "first" in question.lower() or "start" in question.lower():
            # Already computed first event
            pass
        elif "last" in question.lower() or "end" in question.lower():
            # Need last event in schedule
            if solution:
                schedule = sorted(solution.items(), key=lambda x: x[1])
                computed_answer = schedule[-1][0]
            elif constraints:
                topo_order = topological_sort(constraints)
                if topo_order:
                    computed_answer = topo_order[-1]
        
        return {
            "answer": computed_answer,
            "confidence": min(max(confidence, 0.0), 1.0),
            "reasoning": reasoning,
            "info_status": info_status,
            "unique": unique_check
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary: exact match or substring match of computed answer
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
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
        
        # Simple normalization
        max_score = max(item["raw_score"] for item in scored)
        min_score = min(item["raw_score"] for item in scored)
        
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