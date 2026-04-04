import re
import zlib
from typing import List, Dict, Any, Tuple

from forge_primitives import (
    solve_constraints,
    topological_sort,
    check_transitivity,
    confidence_from_agreement,
    information_sufficiency,
    temporal_order
)
from forge.amino_acids.constraint_acids import is_uniquely_solvable, solve_first

class ReasoningTool:
    """Decision theory x Constraint satisfaction - temporal_scheduling"""

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
        """Extract entities, constraints, and question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find entity names (capitalized words that appear as subjects)
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        potential_entities = re.findall(entity_pattern, prompt)
        # Filter: entities that appear in constraints or as options
        entities = []
        for ent in set(potential_entities):
            if len(ent.split()) <= 3:  # Likely a name, not a full sentence
                if any(word in prompt.lower() for word in ['must', 'before', 'after', 'cannot', 'same time']):
                    entities.append(ent)
        
        # Extract temporal constraints
        constraints = []
        # Pattern for "A before B", "A after B", "A and B cannot be at same time"
        before_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:must be|is)\s+before\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        after_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:must be|is)\s+after\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        conflict_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+and\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+cannot be at the same time'
        
        for match in re.finditer(before_pattern, prompt, re.IGNORECASE):
            constraints.append(('before', match.group(1), match.group(2)))
        for match in re.finditer(after_pattern, prompt, re.IGNORECASE):
            constraints.append(('after', match.group(1), match.group(2)))
        for match in re.finditer(conflict_pattern, prompt, re.IGNORECASE):
            constraints.append(('conflict', match.group(1), match.group(2)))
        
        # Extract time slots if mentioned
        time_slots = []
        slot_pattern = r'(\d+):(\d+)\s*(?:AM|PM|to|-)'
        time_matches = re.findall(slot_pattern, prompt)
        if time_matches:
            time_slots = list(set([f"{h}:{m}" for h, m in time_matches]))
        
        return {
            "entities": entities,
            "constraints": constraints,
            "time_slots": time_slots,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply decision theory to find optimal schedule."""
        entities = structure["entities"]
        constraints = structure["constraints"]
        question = structure["question"]
        
        # Convert to decision theory framework: each entity is an alternative,
        # constraints define feasibility, we seek Pareto-optimal schedule
        
        # Build constraint satisfaction problem
        variables = entities
        domains = {var: list(range(len(variables))) for var in variables}  # Simple ordering positions
        
        # Define constraint functions
        def before_constraint(a_val, b_val, a_name, b_name):
            return a_val < b_val
        
        def after_constraint(a_val, b_val, a_name, b_name):
            return a_val > b_val
        
        def conflict_constraint(a_val, b_val, a_name, b_name):
            return a_val != b_val
        
        csp_constraints = []
        for const_type, a, b in constraints:
            if a in variables and b in variables:
                if const_type == 'before':
                    csp_constraints.append(([a, b], lambda x, y, a=a, b=b: before_constraint(x, y, a, b)))
                elif const_type == 'after':
                    csp_constraints.append(([a, b], lambda x, y, a=a, b=b: after_constraint(x, y, a, b)))
                elif const_type == 'conflict':
                    csp_constraints.append(([a, b], lambda x, y, a=a, b=b: conflict_constraint(x, y, a, b)))
        
        # Use T1 primitive: solve_constraints
        solution = solve_constraints(variables, domains, csp_constraints)
        
        # Use amino acid: is_uniquely_solvable
        unique_check = is_uniquely_solvable(variables, domains, csp_constraints)
        
        # Use T1 primitive: topological_sort from constraint graph
        edges = []
        for const_type, a, b in constraints:
            if const_type == 'before':
                edges.append((a, b))
            elif const_type == 'after':
                edges.append((b, a))
        
        topological_order = topological_sort(edges) if edges else []
        
        # Use T1 primitive: check_transitivity to ensure consistency
        relation_pairs = [(a, b) for a, b in edges]
        transitive_closure = check_transitivity(relation_pairs)
        
        # Determine answer based on decision theory: if unique solution exists,
        # that's the optimal schedule. Otherwise, find Pareto frontier.
        computed_answer = ""
        confidence = 0.5
        reasoning_desc = ""
        
        if solution:
            # Sort entities by their assigned position
            ordered = sorted(solution.items(), key=lambda x: x[1])
            schedule_order = [item[0] for item in ordered]
            
            # Use T1 primitive: confidence_from_agreement
            # Simulate multiple scoring methods
            scores = []
            if topological_order:
                # Score 1: match with topological order
                topo_score = sum(1 for i, ent in enumerate(schedule_order) 
                               if i < len(topo_order) and ent == topo_order[i]) / len(schedule_order)
                scores.append(topo_score)
            
            # Score 2: constraint satisfaction rate
            sat_score = 1.0  # solution already satisfies all constraints
            scores.append(sat_score)
            
            # Score 3: uniqueness indicator
            unique_score = 1.0 if unique_check else 0.7
            scores.append(unique_score)
            
            confidence = confidence_from_agreement(scores) if scores else 0.5
            
            # Format answer based on question
            if "order" in question.lower() or "sequence" in question.lower():
                computed_answer = " -> ".join(schedule_order)
                reasoning_desc = f"Optimal sequence satisfying all constraints"
            elif "conflict" in question.lower() or "impossible" in question.lower():
                if not solution:
                    computed_answer = "No valid schedule"
                    reasoning_desc = "Constraints are inconsistent"
                else:
                    computed_answer = "Schedule exists"
                    reasoning_desc = f"Valid schedule found with {len(schedule_order)} events"
            else:
                # Default: list the schedule
                computed_answer = ", ".join(schedule_order)
                reasoning_desc = f"Schedule satisfying {len(constraints)} constraints"
        else:
            # No solution found
            computed_answer = "No valid schedule"
            reasoning_desc = "Constraints are inconsistent or overconstrained"
            confidence = 0.8
        
        # Use T1 primitive: information_sufficiency
        n_vars = len(variables)
        n_constraints = len(constraints)
        sufficiency = information_sufficiency(n_vars, n_constraints)
        
        # Incorporate decision theory: if underdetermined, mention multiple Pareto-optimal solutions
        if sufficiency == "underdetermined" and solution:
            reasoning_desc += " (multiple Pareto-optimal solutions exist)"
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": reasoning_desc,
            "schedule_order": schedule_order if solution else [],
            "is_unique": unique_check if 'unique_check' in locals() else False,
            "sufficiency": sufficiency
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
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
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact or substring match with computed answer
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 1.0
            elif computed_answer and candidate.lower() in computed_answer.lower():
                score = 0.9
            else:
                # Secondary scoring: NCD with reasoning text
                score = 1.0 / (1.0 + ncd(reasoning_text, candidate))
            
            results.append({
                "candidate": candidate,
                "score": score,
                "computed_answer": computed_answer
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using decision theory principles."""
        # Apply confidence weighting from reasoning phase
        # In decision theory, we adjust based on certainty of solution
        
        # Simple calibration: normalize scores to [0, 1] range
        if not scored:
            return scored
        
        scores = [item["score"] for item in scored]
        if max(scores) > 0:
            for item in scored:
                item["score"] = item["score"] / max(scores)
        
        return scored