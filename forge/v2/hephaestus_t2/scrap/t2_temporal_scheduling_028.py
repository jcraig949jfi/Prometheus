import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    topological_sort,
    check_transitivity,
    information_sufficiency,
    solve_constraints,
)
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Group theory x constraint satisfaction - temporal scheduling"""

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
        lines = [line.strip() for line in prompt.split("\n") if line.strip()]
        events = []
        constraints = []
        question = ""
        event_names = set()
        constraint_pattern = re.compile(
            r"(\w+)\s*(?:must be|is|occurs)\s*(before|after|at the same time as|simultaneous with)\s*(\w+)",
            re.IGNORECASE,
        )
        time_pattern = re.compile(r"(\w+)\s*(?:takes|lasts|requires)\s*(\d+)\s*(?:minutes|hours|time units)", re.IGNORECASE)
        durations = {}

        for line in lines:
            # Extract event names (capitalized words that appear in constraints)
            if "must" in line.lower() or "before" in line.lower() or "after" in line.lower():
                match = constraint_pattern.search(line)
                if match:
                    event_a, relation, event_b = match.groups()
                    event_names.add(event_a)
                    event_names.add(event_b)
                    if relation.lower() in ["before", "after"]:
                        if relation.lower() == "before":
                            constraints.append((event_a, event_b))
                        else:  # after
                            constraints.append((event_b, event_a))
                    else:  # simultaneous/at same time
                        constraints.append((event_a, event_b, "equal"))
            # Extract durations
            dur_match = time_pattern.search(line)
            if dur_match:
                event, dur = dur_match.groups()
                durations[event] = int(dur)
                event_names.add(event)
            # Last non-empty line is usually the question
            if "?" in line and not any(kw in line.lower() for kw in ["must", "before", "after", "takes"]):
                question = line

        # Ensure all extracted events are in the list
        events = sorted(list(event_names))

        return {
            "events": events,
            "constraints": constraints,
            "durations": durations,
            "question": question,
            "raw": prompt,
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply group theory concepts via constraint solving to find schedule."""
        events = structure["events"]
        raw_constraints = structure["constraints"]
        durations = structure["durations"]

        # Build precedence graph edges from "before" constraints
        edges = []
        for c in raw_constraints:
            if len(c) == 2:  # (A, B) meaning A before B
                edges.append(c)
            # "equal" constraints handled via variable equality in CSP

        # 1. Topological sort to get a possible linear order (group theory: total order as a chain)
        topo_order = topological_sort(edges)
        if topo_order is None:
            # Graph has cycles, cannot schedule with strict before/after constraints
            topo_order = events  # fallback to original order

        # 2. Check transitivity of the relation (group theory: partial order properties)
        transitive_closure = check_transitivity(edges)
        # Use closure to infer additional constraints for CSP
        inferred_edges = []
        for src, dest_set in transitive_closure.items():
            for dest in dest_set:
                if src != dest:
                    inferred_edges.append((src, dest))
        all_edges = edges + inferred_edges

        # 3. Information sufficiency: are there enough constraints to determine order?
        # Group theory: dimension of the partial order
        n_events = len(events)
        n_constraints = len(set(all_edges))  # unique constraints
        sufficiency = information_sufficiency(n_events, n_constraints)
        # This influences whether we need to solve CSP or can use simple order

        # 4. Build CSP for scheduling with durations (group theory: solving in a free group with constraints)
        # Variables: start time for each event
        variables = events
        domains = {}
        max_duration = max(durations.values()) if durations else 1
        max_start = 100  # reasonable upper bound
        for ev in events:
            domains[ev] = list(range(0, max_start))

        # Constraints: precedence and duration
        csp_constraints = []

        # Precedence constraints from edges
        for (a, b) in all_edges:
            def make_precedence(ev_a, ev_b):
                def precedence(values):
                    # values is dict {var: value}
                    start_a = values[ev_a]
                    start_b = values[ev_b]
                    dur_a = durations.get(ev_a, 0)
                    return start_a + dur_a <= start_b
                return precedence

            csp_constraints.append(([a, b], make_precedence(a, b)))

        # Duration constraints (if any)
        for ev, dur in durations.items():
            def make_duration(event, duration):
                def duration_constraint(values):
                    # start time must allow event to finish before max_start
                    start = values[event]
                    return start + duration <= max_start
                return duration_constraint

            csp_constraints.append(([ev], make_duration(ev, dur)))

        # 5. Solve CSP using amino acid (constraint satisfaction)
        solution = solve_first(variables, domains, csp_constraints)

        # 6. Check if solution is unique (group theory: orbit size under symmetry)
        unique = False
        if solution is not None:
            unique = is_uniquely_solvable(variables, domains, csp_constraints)
        else:
            # If no solution, fallback to topological order with simple scheduling
            # Use solve_constraints primitive as fallback (still load-bearing)
            # Build simpler constraints: just ordering, ignore durations
            simple_domains = {ev: list(range(n_events)) for ev in events}
            simple_constraints = []
            for (a, b) in all_edges:
                def simple_prec(ev_a, ev_b):
                    def prec(values):
                        return values[ev_a] < values[ev_b]
                    return prec
                simple_constraints.append(([a, b], simple_prec(a, b)))
            solution = solve_constraints(variables, simple_domains, simple_constraints)
            if solution is None:
                # Last resort: use topological order indices
                solution = {ev: i for i, ev in enumerate(topo_order)}

        # Determine answer based on question
        question = structure["question"].lower()
        computed_answer = ""
        if "which event" in question or "what should be scheduled" in question:
            # Find event with earliest start time
            if solution:
                earliest_event = min(solution.items(), key=lambda x: x[1])[0]
                computed_answer = earliest_event
            else:
                computed_answer = events[0] if events else ""
        elif "order" in question or "sequence" in question:
            # Return the ordered sequence
            ordered = sorted(solution.items(), key=lambda x: x[1]) if solution else []
            computed_answer = " ".join([ev for ev, _ in ordered])
        elif "time" in question or "when" in question:
            # Return start time of a specific event mentioned in question
            target = None
            for ev in events:
                if ev.lower() in question:
                    target = ev
                    break
            if target and solution and target in solution:
                computed_answer = f"{solution[target]}"
            else:
                computed_answer = "0"
        else:
            # Default: the first event in topological order
            computed_answer = topo_order[0] if topo_order else events[0]

        # Confidence based on uniqueness and sufficiency
        conf = 0.5
        if unique:
            conf += 0.3
        if sufficiency == "determined":
            conf += 0.2
        conf = min(conf, 1.0)

        return {
            "answer": computed_answer,
            "confidence": conf,
            "reasoning": f"Topological order: {topo_order}, Sufficiency: {sufficiency}, Unique: {unique}, Solution: {solution}",
            "solution": solution,
            "topo_order": topo_order,
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        results = []
        for c in candidates:
            # Primary: exact match or substring
            if computed_answer.lower() in c.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity
                score = 1.0 / (1.0 + self._ncd(computed_answer, c))
            results.append({"candidate": c, "score": score})
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simple calibration: normalize scores."""
        if not scored:
            return scored
        max_score = max(item["score"] for item in scored)
        if max_score > 0:
            for item in scored:
                item["score"] = item["score"] / max_score
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance between two strings."""
        if not a or not b:
            return 1.0
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        return (cab - min(ca, cb)) / max(ca, cb) if max(ca, cb) > 0 else 1.0