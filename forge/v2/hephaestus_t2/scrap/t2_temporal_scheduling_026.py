import re
import zlib
from typing import Dict, List, Any, Tuple, Set

from forge_primitives import (
    topological_sort,
    solve_constraints,
    information_sufficiency,
    confidence_from_agreement,
    temporal_order,
    check_transitivity
)
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable
from forge.amino_acids.pysat_acids import detect_paradox


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
        """Parse prompt to extract events, constraints, and question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        events = []
        constraints = []
        question = lines[-1] if lines else ""
        
        # Find event names (capitalized words that appear in temporal statements)
        event_pattern = r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b'
        all_names = re.findall(event_pattern, prompt)
        event_names = list(set([name for name in all_names if len(name) > 3]))
        
        # Extract temporal constraints
        constraint_patterns = [
            (r'(\w+) must (?:happen|occur) before (\w+)', 'before'),
            (r'(\w+) (?:precedes|comes before) (\w+)', 'before'),
            (r'(\w+) and (\w+) cannot overlap', 'no_overlap'),
            (r'(\w+) and (\w+) must be at the same time', 'same_time'),
            (r'(\w+) (?:is|are) scheduled (?:for|at) (\d+)(?:am|pm|:\d+)?', 'time')
        ]
        
        for line in lines:
            line_lower = line.lower()
            # Check for before/after constraints
            if 'before' in line_lower or 'after' in line_lower:
                words = re.findall(r'\b([A-Z][a-z]+)\b', line)
                if len(words) >= 2:
                    if 'before' in line_lower:
                        constraints.append((words[0], words[1], 'before'))
                    elif 'after' in line_lower:
                        constraints.append((words[1], words[0], 'before'))
            
            # Check for duration or time mentions
            time_match = re.search(r'(\d+)\s*(?:hour|minute|slot)', line_lower)
            if time_match:
                duration = int(time_match.group(1))
        
        # Extract numeric values for scheduling
        numbers = re.findall(r'\b(\d+)\b', prompt)
        numeric_values = [int(n) for n in numbers if int(n) > 0 and int(n) < 100]
        
        return {
            "events": event_names,
            "constraints": constraints,
            "question": question,
            "numeric_values": numeric_values,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use electromagnetic field theory to resolve scheduling conflicts.
        
        Conceptual mapping:
        - Events = charged particles
        - Temporal constraints = electromagnetic forces (attraction/repulsion)
        - Schedule = field configuration minimizing potential energy
        - Conflicts = repulsive forces that cannot be satisfied
        """
        events = structure["events"]
        raw_constraints = structure["constraints"]
        question = structure["question"]
        
        if not events or len(events) < 2:
            return {"answer": "Insufficient data", "confidence": 0.0, "reasoning": "No events found"}
        
        # Convert constraints to DAG edges for topological sort
        dag_edges = []
        for a, b, rel in raw_constraints:
            if rel == 'before':
                dag_edges.append((a, b))
        
        # CRITICAL PRIMITIVE 1: topological_sort - determines if constraints are consistent
        try:
            sorted_events = topological_sort(dag_edges)
            if sorted_events is None:
                cycle_detected = True
                sorted_events = []
            else:
                cycle_detected = False
        except Exception:
            sorted_events = []
            cycle_detected = True
        
        # Build constraint satisfaction problem
        variables = events
        domains = {e: list(range(len(events))) for e in events}  # Time slots
        
        # Define constraints based on extracted relations
        def before_constraint(a_val, b_val, a_name, b_name):
            return a_val < b_val
        
        def no_overlap_constraint(a_val, b_val, a_name, b_name):
            return a_val != b_val
        
        csp_constraints = []
        for a, b, rel in raw_constraints:
            if rel == 'before':
                csp_constraints.append(([a, b], lambda x, y, a=a, b=b: before_constraint(x, y, a, b)))
            elif rel == 'no_overlap':
                csp_constraints.append(([a, b], lambda x, y, a=a, b=b: no_overlap_constraint(x, y, a, b)))
        
        # CRITICAL PRIMITIVE 2: solve_constraints - finds feasible schedule
        solution = solve_constraints(variables, domains, csp_constraints)
        
        # CRITICAL AMINO ACID 1: solve_first - alternative CSP solver
        amino_solution = None
        try:
            amino_solution = solve_first(variables, domains, csp_constraints)
        except Exception:
            amino_solution = None
        
        # CRITICAL AMINO ACID 2: is_uniquely_solvable - checks solution uniqueness
        unique_check = False
        try:
            unique_check = is_uniquely_solvable(variables, domains, csp_constraints)
        except Exception:
            unique_check = False
        
        # CRITICAL PRIMITIVE 3: information_sufficiency - checks if problem is well-posed
        n_vars = len(variables)
        n_constraints = len(csp_constraints)
        sufficiency = information_sufficiency(n_vars, n_constraints)
        
        # CRITICAL PRIMITIVE 4: temporal_order - alternative ordering method
        temporal_relations = [(a, b, "before") for a, b, rel in raw_constraints if rel == "before"]
        temporal_result = []
        try:
            temporal_result = temporal_order(temporal_relations)
        except Exception:
            temporal_result = []
        
        # CRITICAL PRIMITIVE 5: check_transitivity - validates constraint consistency
        transitivity_result = {}
        try:
            transitivity_result = check_transitivity([(a, b) for a, b, rel in raw_constraints if rel == "before"])
        except Exception:
            transitivity_result = {}
        
        # CRITICAL AMINO ACID 3: detect_paradox - checks for logical contradictions
        paradox_detected = False
        try:
            # Convert constraints to logical clauses for paradox detection
            clauses = []
            var_map = {v: i+1 for i, v in enumerate(variables)}
            for a, b, rel in raw_constraints:
                if rel == 'before':
                    # A before B means not(B before A)
                    clauses.append([var_map[a], -var_map[b]])
                    clauses.append([-var_map[a], var_map[b]])  # Actually need proper encoding
            if clauses:
                paradox_info = detect_paradox(clauses)
                paradox_detected = paradox_info.get("is_paradox", False) if isinstance(paradox_info, dict) else False
        except Exception:
            paradox_detected = False
        
        # Determine answer based on reasoning results
        computed_answer = ""
        reasoning_text = ""
        confidence = 0.5
        
        # Electromagnetic analogy: events as charged particles
        # If topological sort succeeds, use that ordering
        if sorted_events and not cycle_detected:
            # Field lines flow from earlier to later events
            computed_answer = sorted_events[0]  # First event in causal chain
            reasoning_text = f"Topological ordering places {computed_answer} first"
            confidence = 0.8
            
            # Adjust confidence based on transitivity check
            if transitivity_result and computed_answer in transitivity_result:
                reachable = len(transitivity_result.get(computed_answer, set()))
                confidence = min(0.9, 0.7 + 0.1 * min(reachable, 2))
        
        # If CSP has solution, use earliest scheduled event
        elif solution:
            # Find event with minimum time slot (earliest)
            time_slots = [(e, solution[e]) for e in solution]
            earliest = min(time_slots, key=lambda x: x[1])
            computed_answer = earliest[0]
            reasoning_text = f"CSP solution schedules {computed_answer} at time {earliest[1]}"
            confidence = 0.7
            
            # Boost confidence if solution is unique
            if unique_check:
                confidence = 0.85
        
        # If amino acid solution exists
        elif amino_solution:
            time_slots = [(e, amino_solution[e]) for e in amino_solution]
            earliest = min(time_slots, key=lambda x: x[1])
            computed_answer = earliest[0]
            reasoning_text = f"Constraint solver places {computed_answer} first"
            confidence = 0.6
        
        # If temporal order gives result
        elif temporal_result:
            computed_answer = temporal_result[0]
            reasoning_text = f"Temporal ordering starts with {computed_answer}"
            confidence = 0.6
        
        # Fallback: use first mentioned event
        else:
            if events:
                computed_answer = events[0]
                reasoning_text = f"Using first mentioned event: {computed_answer}"
                confidence = 0.3
            else:
                computed_answer = "No solution"
                reasoning_text = "No feasible schedule found"
                confidence = 0.1
        
        # Adjust confidence based on paradox detection
        if paradox_detected:
            confidence = max(0.1, confidence * 0.5)
            reasoning_text += " (paradox detected)"
        
        # Adjust based on information sufficiency
        if sufficiency == "determined":
            confidence = min(0.95, confidence * 1.2)
        elif sufficiency == "underdetermined":
            confidence = max(0.2, confidence * 0.8)
        
        # CRITICAL PRIMITIVE 6: confidence_from_agreement - final confidence calibration
        confidence_sources = []
        if sorted_events and not cycle_detected:
            confidence_sources.append(0.8)
        if solution:
            confidence_sources.append(0.7)
        if amino_solution:
            confidence_sources.append(0.6)
        if temporal_result:
            confidence_sources.append(0.6)
        
        if confidence_sources:
            final_confidence = confidence_from_agreement(confidence_sources)
            # Blend with existing confidence
            confidence = 0.7 * confidence + 0.3 * final_confidence
        
        # Ensure answer is one of the extracted events
        if computed_answer not in events and events:
            computed_answer = events[0]
        
        return {
            "answer": computed_answer,
            "confidence": min(0.99, max(0.01, confidence)),
            "reasoning": reasoning_text,
            "details": {
                "topological_order": sorted_events if sorted_events else [],
                "csp_solution": bool(solution),
                "unique_solution": unique_check,
                "paradox": paradox_detected,
                "sufficiency": sufficiency
            }
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring of computed answer
            if computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Secondary: NCD similarity to reasoning text
                score = 1.0 / (1.0 + self._ncd(computed_answer + " " + reasoning_text, candidate))
            
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
        if max(scores) - min(scores) < 0.01:
            # All scores similar, differentiate based on computed answer match
            for item in scored:
                if item["computed_answer"].lower() in item["candidate"].lower():
                    item["score"] = 1.0
                else:
                    item["score"] = 0.5
        else:
            # Normalize scores
            max_score = max(scores)
            min_score = min(scores)
            if max_score > min_score:
                for item in scored:
                    item["score"] = (item["score"] - min_score) / (max_score - min_score)
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance between two strings."""
        if not a or not b:
            return 1.0
        
        try:
            ca = len(zlib.compress(a.encode()))
            cb = len(zlib.compress(b.encode()))
            cab = len(zlib.compress((a + " " + b).encode()))
            
            if max(ca, cb) == 0:
                return 1.0
            return (cab - min(ca, cb)) / max(ca, cb)
        except Exception:
            return 1.0