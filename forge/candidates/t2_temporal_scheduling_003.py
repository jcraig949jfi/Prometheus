import re
import zlib
from typing import Dict, List, Any, Tuple, Set

from forge_primitives import (
    check_transitivity,
    information_sufficiency,
    solve_constraints,
    topological_sort,
    confidence_from_agreement,
    entropy
)
from forge.amino_acids.constraint_acids import is_uniquely_solvable
from forge.amino_acids.pysat_acids import check_entailment


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
        return sorted(alibrated, key=lambda x: x["score"], reverse=True)

    def _extract(self, prompt: str) -> Dict[str, Any]:
        """Extract events, temporal constraints, and the question from the prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""

        # Find event names (capitalized words or phrases, often in quotes or before constraints)
        event_pattern = r'"([^"]+)"|([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:must|before|after|during|at)'
        event_matches = re.findall(event_pattern, prompt)
        events = set()
        for quoted, unquoted in event_matches:
            if quoted:
                events.add(quoted)
            elif unquoted and len(unquoted.split()) <= 3:  # Avoid capturing full sentences
                events.add(unquoted)

        # Find temporal constraints: "A before B", "A must occur after B", "A during B"
        before_pattern = r'([^\.]+?)\s+(?:must\s+be\s+|is\s+)?before\s+([^\.]+?)[\.\s]'
        after_pattern = r'([^\.]+?)\s+(?:must\s+be\s+|is\s+)?after\s+([^\.]+?)[\.\s]'
        same_time_pattern = r'([^\.]+?)\s+(?:must\s+)?(?:occur\s+)?(?:at\s+the\s+same\s+time|simultaneously)\s+with\s+([^\.]+?)[\.\s]'

        constraints = []
        for pattern, rel in [(before_pattern, 'before'), (after_pattern, 'after'), (same_time_pattern, 'same')]:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            for a, b in matches:
                a_clean = a.strip().strip('"')
                b_clean = b.strip().strip('"')
                if a_clean and b_clean:
                    if rel == 'before':
                        constraints.append((a_clean, b_clean, '<'))
                    elif rel == 'after':
                        constraints.append((b_clean, a_clean, '<'))  # Convert to before relation
                    elif rel == 'same':
                        constraints.append((a_clean, b_clean, '='))

        # Find duration or time window hints (e.g., "takes 2 hours", "between 9 and 11")
        duration_pattern = r'(\d+)\s+(?:hour|minute|day)s?'
        durations = re.findall(duration_pattern, prompt)
        time_window_pattern = r'between\s+(\d+)\s+and\s+(\d+)'
        windows = re.findall(time_window_pattern, prompt)

        return {
            "events": list(events),
            "constraints": constraints,
            "question": question,
            "durations": [int(d) for d in durations],
            "windows": [(int(start), int(end)) for start, end in windows],
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply relativistic reasoning to scheduling constraints."""
        events = structure["events"]
        raw_constraints = structure["constraints"]
        question = structure["question"]

        if not events or not raw_constraints:
            # Fallback: return first event as placeholder
            return {
                "answer": events[0] if events else "unknown",
                "confidence": 0.1,
                "reasoning": "Insufficient data extracted",
                "schedule": []
            }

        # Build constraint graph for topological sort
        edges = []
        for a, b, rel in raw_constraints:
            if rel == '<':
                edges.append((a, b))
            elif rel == '=':
                # For equality, we need to handle specially - treat as same node or add both directions
                edges.append((a, b))
                edges.append((b, a))

        # Use topological_sort primitive
        order_result = topological_sort(edges)
        if order_result is None:
            # Graph has cycles, use constraint solving
            order_result = []

        # Build CSP for more complex constraints
        variables = events
        domains = {e: list(range(len(events))) for e in events}  # Simple positions

        def before_constraint(a_val, b_val):
            return a_val < b_val

        def same_constraint(a_val, b_val):
            return a_val == b_val

        csp_constraints = []
        for a, b, rel in raw_constraints:
            if rel == '<':
                csp_constraints.append(([a, b], before_constraint))
            elif rel == '=':
                csp_constraints.append(([a, b], same_constraint))

        # Use solve_constraints primitive
        solution = solve_constraints(variables, domains, csp_constraints)

        # Use information_sufficiency primitive
        n_vars = len(variables)
        n_constraints = len(csp_constraints)
        sufficiency = information_sufficiency(n_vars, n_constraints)

        # Use check_transitivity primitive
        binary_relations = [(a, b) for a, b, rel in raw_constraints if rel == '<']
        transitive_closure = check_transitivity(binary_relations)

        # Use amino acid: check if schedule is uniquely solvable
        unique_solution = False
        if solution:
            # Convert to CSP format for amino acid
            csp_vars_domains = {v: list(range(len(events))) for v in variables}
            csp_constraints_list = []
            for a, b, rel in raw_constraints:
                if rel == '<':
                    csp_constraints_list.append(([a, b], lambda x, y: x < y))
                elif rel == '=':
                    csp_constraints_list.append(([a, b], lambda x, y: x == y))
            
            unique_check = is_uniquely_solvable(csp_vars_domains, csp_constraints_list)
            if unique_check is not None:
                unique_solution = unique_check

        # Relativity-inspired reasoning: events are like worldlines in spacetime
        # Constraints define causal structure (light cones)
        # The schedule is a foliation of spacetime into simultaneous slices
        
        # Compute entropy of possible schedules (uncertainty in foliation)
        if solution:
            # If we have a solution, entropy is low
            schedule_entropy = 0.1
        else:
            # Multiple solutions possible
            schedule_entropy = 0.8
        
        # Use entropy primitive
        if order_result:
            prob_dist = [1.0/len(order_result)] * len(order_result)
            ordering_entropy = entropy(prob_dist)
        else:
            ordering_entropy = 1.0

        # Determine answer based on question type
        computed_answer = ""
        if "which event" in question.lower() or "what must happen" in question.lower():
            # Find critical event based on constraint graph
            if transitive_closure and events:
                # Event with most successors (most constrained)
                successor_counts = {e: len(transitive_closure.get(e, set())) for e in events}
                computed_answer = max(successor_counts.items(), key=lambda x: x[1])[0]
            else:
                computed_answer = events[0] if events else "unknown"
        elif "order" in question.lower() or "sequence" in question.lower():
            # Return the schedule
            if order_result:
                computed_answer = order_result[0] if order_result else events[0]
            elif solution:
                # Sort events by their assigned values
                sorted_events = sorted(solution.items(), key=lambda x: x[1])
                computed_answer = sorted_events[0][0] if sorted_events else events[0]
            else:
                computed_answer = events[0] if events else "unknown"
        elif "conflict" in question.lower() or "impossible" in question.lower():
            # Check for contradictions
            if order_result is None or not solution:
                computed_answer = "yes"
            else:
                computed_answer = "no"
        else:
            # Default: first event
            computed_answer = events[0] if events else "unknown"

        # Use confidence_from_agreement primitive
        agreement_scores = []
        if order_result:
            agreement_scores.append(0.8)
        if solution:
            agreement_scores.append(0.7)
        if unique_solution:
            agreement_scores.append(0.9)
        if sufficiency == "determined":
            agreement_scores.append(0.8)
        
        confidence = confidence_from_agreement(agreement_scores) if agreement_scores else 0.5

        # Apply relativistic time dilation: confidence contracts with entropy
        relativistic_confidence = confidence * (1.0 - schedule_entropy * 0.5)

        return {
            "answer": computed_answer,
            "confidence": relativistic_confidence,
            "reasoning": f"Schedule analysis: {sufficiency}, unique={unique_solution}, entropy={schedule_entropy:.2f}",
            "schedule": order_result if order_result else [],
            "solution": solution,
            "transitive_closure": transitive_closure
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
                # Fallback: NCD similarity to reasoning text
                score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using relativistic confidence weighting."""
        if not scored:
            return scored
        
        # Simple normalization
        max_score = max(item["raw_score"] for item in scored)
        if max_score > 0:
            for item in scored:
                item["score"] = item["raw_score"] / max_score
        else:
            for item in scored:
                item["score"] = 0.0
        
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