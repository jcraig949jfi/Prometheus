import re
import zlib
from typing import Dict, List, Any, Tuple, Set

from forge_primitives import (
    solve_constraints,
    topological_sort,
    information_sufficiency,
    confidence_from_agreement,
    dag_traverse,
    check_transitivity
)
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Control theory x Constraint satisfaction - temporal_scheduling"""

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
        """Extract entities, temporal constraints, and the question from the prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find entity names (capitalized words that appear in constraints)
        # Look for patterns like "Event A", "Task X", or standalone capitalized names
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        potential_entities = re.findall(entity_pattern, prompt)
        
        # Filter to likely entities (not common words, appear multiple times)
        word_counts = {}
        for word in potential_entities:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        entities = [word for word, count in word_counts.items() 
                   if count > 1 and word not in ['The', 'A', 'An', 'And', 'Or', 'But']]
        
        # Extract temporal constraints
        constraints = []
        before_pattern = r'(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b)\s+(?:must be before|before|precedes)\s+(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b)'
        after_pattern = r'(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b)\s+(?:must be after|after|follows)\s+(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b)'
        
        for line in lines:
            # Find "A before B" patterns
            before_matches = re.findall(before_pattern, line, re.IGNORECASE)
            for a, b in before_matches:
                if a in entities and b in entities:
                    constraints.append((a, b, "before"))
            
            # Find "A after B" patterns (convert to B before A)
            after_matches = re.findall(after_pattern, line, re.IGNORECASE)
            for a, b in after_matches:
                if a in entities and b in entities:
                    constraints.append((b, a, "before"))
        
        # Extract numerical time windows if present
        time_windows = {}
        time_pattern = r'(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b)\s+(?:takes|requires|needs)\s+(\d+)\s*(?:minutes|hours|time units)'
        for line in lines:
            time_matches = re.findall(time_pattern, line, re.IGNORECASE)
            for entity, duration in time_matches:
                if entity in entities:
                    time_windows[entity] = int(duration)
        
        # Extract conflict statements
        conflicts = []
        conflict_pattern = r'(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b)\s+(?:and|&)\s+(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b)\s+(?:cannot|can\'t|can not)\s+be\s+(?:at the same time|simultaneous|concurrent)'
        for line in lines:
            conflict_matches = re.findall(conflict_pattern, line, re.IGNORECASE)
            for a, b in conflict_matches:
                if a in entities and b in entities:
                    conflicts.append((a, b))
        
        return {
            "entities": entities,
            "constraints": constraints,
            "time_windows": time_windows,
            "conflicts": conflicts,
            "question": question,
            "raw_lines": lines
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply control theory principles to resolve scheduling conflicts."""
        entities = structure["entities"]
        constraints = structure["constraints"]
        conflicts = structure["conflicts"]
        question = structure["question"]
        
        # Control theory: Model scheduling as a dynamical system with constraints as state-space boundaries
        # The feasible schedule is the reachable set in state space that satisfies all constraints
        
        # Build constraint graph edges for topological sort
        edges = []
        for a, b, rel in constraints:
            if rel == "before":
                edges.append((a, b))
        
        # Use topological_sort primitive (T1)
        try:
            sorted_order = topological_sort(edges)
            if sorted_order is None:
                # Graph has cycles, constraints are inconsistent
                sorted_order = []
        except Exception:
            sorted_order = []
        
        # Use information_sufficiency primitive (T1)
        n_unknowns = len(entities)
        n_constraints = len(constraints) + len(conflicts)
        sufficiency = information_sufficiency(n_unknowns, n_constraints)
        
        # Build CSP for constraint satisfaction
        variables = entities
        domains = {entity: list(range(len(entities))) for entity in entities}
        
        csp_constraints = []
        
        # Add ordering constraints
        for a, b, rel in constraints:
            if rel == "before":
                def make_before_constraint(x, y):
                    return lambda vals: vals[x] < vals[y]
                csp_constraints.append(([a, b], make_before_constraint(a, b)))
        
        # Add conflict constraints (cannot be at same time)
        for a, b in conflicts:
            def make_conflict_constraint(x, y):
                return lambda vals: vals[x] != vals[y]
            csp_constraints.append(([a, b], make_conflict_constraint(a, b)))
        
        # Use solve_constraints primitive (T1)
        solution = None
        if variables and csp_constraints:
            solution = solve_constraints(variables, domains, csp_constraints)
        
        # Use amino acid: solve_first from constraint_acids
        amino_solution = None
        try:
            amino_solution = solve_first(domains, csp_constraints)
        except Exception:
            amino_solution = None
        
        # Use amino acid: is_uniquely_solvable from constraint_acids
        is_unique = False
        try:
            is_unique = is_uniquely_solvable(domains, csp_constraints)
        except Exception:
            is_unique = False
        
        # Control theory: Compute system "stability" - how many valid schedules exist
        # More solutions = more flexible schedule = more "stable" system
        stability_score = 0.0
        if solution is not None:
            # Count how many entities have flexibility in their positions
            if amino_solution:
                # Try to find alternative solutions by perturbing the first solution
                alternative_count = 0
                for entity in entities:
                    # Create modified domain excluding current assignment
                    if entity in amino_solution:
                        current_pos = amino_solution[entity]
                        modified_domains = domains.copy()
                        modified_domains[entity] = [p for p in domains[entity] if p != current_pos]
                        
                        # Check if still solvable with this modification
                        try:
                            if solve_first(modified_domains, csp_constraints) is not None:
                                alternative_count += 1
                        except Exception:
                            pass
                
                stability_score = alternative_count / len(entities) if entities else 0.0
        
        # Determine answer based on question type
        computed_answer = ""
        reasoning_explanation = ""
        
        if "which" in question.lower() and "first" in question.lower():
            # Question asks which entity should be scheduled first
            if sorted_order:
                computed_answer = sorted_order[0]
                reasoning_explanation = f"Based on topological ordering, {sorted_order[0]} must come first"
            elif solution:
                # Find entity with smallest position in solution
                first_entity = min(solution.items(), key=lambda x: x[1])[0]
                computed_answer = first_entity
                reasoning_explanation = f"Based on constraint satisfaction, {first_entity} has the earliest position"
        
        elif "which" in question.lower() and "conflict" in question.lower():
            # Question asks about conflicting entities
            if conflicts:
                computed_answer = f"{conflicts[0][0]} and {conflicts[0][1]}"
                reasoning_explanation = f"These cannot be scheduled at the same time"
        
        elif "order" in question.lower() or "sequence" in question.lower():
            # Question asks for the complete order
            if sorted_order:
                computed_answer = " -> ".join(sorted_order)
                reasoning_explanation = f"Topological order: {' -> '.join(sorted_order)}"
            elif solution:
                ordered = sorted(solution.items(), key=lambda x: x[1])
                computed_answer = " -> ".join([e for e, _ in ordered])
                reasoning_explanation = f"Constraint-based order: {' -> '.join([e for e, _ in ordered])}"
        
        else:
            # Default: return feasibility assessment
            if solution is not None or amino_solution is not None:
                computed_answer = "Feasible schedule exists"
                reasoning_explanation = f"System is {sufficiency} with stability {stability_score:.2f}"
            else:
                computed_answer = "No feasible schedule"
                reasoning_explanation = f"Constraints are inconsistent, system is {sufficiency}"
        
        # Use confidence_from_agreement primitive (T1)
        agreement_scores = []
        if solution is not None:
            agreement_scores.append(1.0)
        if amino_solution is not None:
            agreement_scores.append(1.0)
        if sorted_order:
            agreement_scores.append(0.8)
        
        confidence = 0.5  # Default
        if agreement_scores:
            confidence = confidence_from_agreement(agreement_scores)
        
        # Control theory: Adjust confidence based on system stability
        # More stable systems (multiple solutions) give lower confidence in specific answer
        if stability_score > 0.5:
            confidence *= 0.8  # Reduce confidence for highly flexible systems
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": reasoning_explanation,
            "stability": stability_score,
            "sufficiency": sufficiency,
            "sorted_order": sorted_order if sorted_order else []
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        def ncd(a: str, b: str) -> float:
            """Normalized Compression Distance."""
            if not a or not b:
                return 1.0
            ca = len(zlib.compress(a.encode()))
            cb = len(zlib.compress(b.encode()))
            cab = len(zlib.compress((a + " " + b).encode()))
            return (cab - min(ca, cb)) / max(ca, cb) if max(ca, cb) > 0 else 1.0
        
        scored = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback 1: NCD with computed answer
                score1 = 1.0 / (1.0 + ncd(computed_answer, candidate))
                
                # Fallback 2: NCD with reasoning explanation
                score2 = 1.0 / (1.0 + ncd(reasoning_text, candidate))
                
                score = max(score1, score2) * 0.8  # Penalize for not exact match
            
            scored.append({
                "candidate": candidate,
                "raw_score": score,
                "match_type": "exact" if computed_answer and computed_answer.lower() in candidate.lower() else "similarity"
            })
        
        return scored

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using control theory stability adjustment."""
        if not scored:
            return []
        
        # Extract raw scores
        raw_scores = [item["raw_score"] for item in scored]
        
        # Control theory: Apply damping based on score distribution
        # If scores are very similar (low variance), damp the differences
        # If scores are very different (high variance), amplify the differences
        
        if len(raw_scores) > 1:
            mean_score = sum(raw_scores) / len(raw_scores)
            variance = sum((s - mean_score) ** 2 for s in raw_scores) / len(raw_scores)
            
            # Damping factor: higher variance = less damping
            damping = 1.0 / (1.0 + variance * 10)
            
            calibrated = []
            for item in scored:
                # Apply damping: pull scores toward mean
                calibrated_score = damping * mean_score + (1 - damping) * item["raw_score"]
                
                # Ensure score is in [0, 1]
                calibrated_score = max(0.0, min(1.0, calibrated_score))
                
                calibrated.append({
                    "candidate": item["candidate"],
                    "score": calibrated_score,
                    "match_type": item["match_type"]
                })
            
            return calibrated
        
        return [{"candidate": item["candidate"], "score": item["raw_score"], 
                "match_type": item["match_type"]} for item in scored]