import re
import zlib
from typing import Dict, List, Any, Tuple, Set
from forge_primitives import (
    topological_sort,
    solve_constraints,
    information_sufficiency,
    entropy,
    confidence_from_agreement,
    temporal_order
)
from forge.amino_acids.constraint_acids import is_uniquely_solvable, solve_first


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
        """Extract entities, temporal constraints, and the question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find entity names (capitalized words that appear in constraints)
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        all_entities = set(re.findall(entity_pattern, prompt))
        
        # Filter to likely scheduling entities (events, tasks, people)
        entities = []
        for ent in all_entities:
            if len(ent.split()) <= 3 and ent.lower() not in ['before', 'after', 'must', 'cannot', 'and', 'or']:
                entities.append(ent)
        
        # Extract temporal constraints
        constraints = []
        before_after_pattern = r'(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b)\s+(before|after)\s+(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b)'
        matches = re.findall(before_after_pattern, prompt, re.IGNORECASE)
        
        for match in matches:
            entity1, relation, entity2 = match
            if relation.lower() == 'before':
                constraints.append((entity1, entity2))
            else:  # after
                constraints.append((entity2, entity1))
        
        # Extract mutual exclusion constraints
        cannot_pattern = r'(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b)\s+and\s+(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b)\s+cannot\s+be\s+at\s+the\s+same\s+time'
        cannot_matches = re.findall(cannot_pattern, prompt, re.IGNORECASE)
        
        mutual_exclusions = []
        for match in cannot_matches:
            if len(match) == 2:
                mutual_exclusions.append((match[0], match[1]))
        
        # Extract time slots or positions if mentioned
        time_slots = []
        slot_pattern = r'(?:slot|position|time)\s+(\d+)'
        slot_matches = re.findall(slot_pattern, prompt, re.IGNORECASE)
        for match in slot_matches:
            time_slots.append(int(match))
        
        return {
            "entities": entities,
            "constraints": constraints,
            "mutual_exclusions": mutual_exclusions,
            "time_slots": sorted(time_slots) if time_slots else [],
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use thermodynamic principles to find optimal schedule."""
        entities = structure["entities"]
        constraints = structure["constraints"]
        mutual_exclusions = structure["mutual_exclusions"]
        time_slots = structure["time_slots"]
        
        # THERMODYNAMIC ANALOGY:
        # - Each schedule is a microstate
        # - Constraints reduce entropy (available microstates)
        # - Optimal schedule minimizes free energy (maximizes constraint satisfaction)
        
        # Phase 1: Check if problem is well-constrained using information_sufficiency
        n_unknowns = len(entities)
        n_constraints = len(constraints) + len(mutual_exclusions)
        sufficiency = information_sufficiency(n_unknowns, n_constraints)
        
        # Use topological_sort to get initial ordering
        try:
            topo_order = topological_sort(constraints)
            if topo_order is None:
                # Cycle detected - use constraint solving
                topo_order = []
        except Exception:
            topo_order = []
        
        # Use entropy to measure uncertainty in scheduling
        if time_slots:
            # If time slots are specified, compute entropy of uniform distribution
            n_slots = len(time_slots) if time_slots else len(entities)
            uniform_probs = [1.0/n_slots] * n_slots
            schedule_entropy = entropy(uniform_probs)
        else:
            schedule_entropy = entropy([1.0/len(entities)] * len(entities)) if entities else 1.0
        
        # Use constraint solving to find valid schedules
        valid_schedules = []
        computed_answer = ""
        
        # Build CSP for scheduling
        if entities:
            # Create variables (entities) and domains (time positions)
            variables = entities
            n_positions = len(time_slots) if time_slots else len(entities)
            domains = {var: list(range(n_positions)) for var in variables}
            
            # Define constraints
            csp_constraints = []
            
            # Temporal ordering constraints
            for a, b in constraints:
                def make_before_constraint(a_var, b_var):
                    return lambda vals: vals[a_var] < vals[b_var]
                csp_constraints.append(([a, b], make_before_constraint(a, b)))
            
            # Mutual exclusion constraints
            for a, b in mutual_exclusions:
                def make_exclusion_constraint(a_var, b_var):
                    return lambda vals: vals[a_var] != vals[b_var]
                csp_constraints.append(([a, b], make_exclusion_constraint(a, b)))
            
            # All-different constraint (implied by mutual exclusions if not specified)
            if not mutual_exclusions and len(entities) <= n_positions:
                def all_different(vals):
                    return len(set(vals.values())) == len(vals)
                csp_constraints.append((variables, all_different))
            
            # Use solve_constraints primitive
            solution = solve_constraints(variables, domains, csp_constraints)
            
            if solution:
                # Convert solution to ordered list
                sorted_entities = sorted(solution.items(), key=lambda x: x[1])
                schedule_order = [ent for ent, _ in sorted_entities]
                
                # Use amino acid to check uniqueness
                unique_check = is_uniquely_solvable(variables, domains, csp_constraints)
                
                # Use solve_first amino acid to get first solution for comparison
                first_solution = solve_first(variables, domains, csp_constraints)
                
                if first_solution:
                    # Convert to same format for comparison
                    first_sorted = sorted(first_solution.items(), key=lambda x: x[1])
                    first_order = [ent for ent, _ in first_sorted]
                    
                    # Check if solutions match
                    if schedule_order == first_order:
                        valid_schedules.append(schedule_order)
                        computed_answer = schedule_order[0]  # First in schedule
                    else:
                        # Multiple solutions - take first from topological sort if available
                        if topo_order:
                            computed_answer = topo_order[0]
                        else:
                            computed_answer = schedule_order[0]
                else:
                    # Fallback to topological order
                    if topo_order:
                        computed_answer = topo_order[0]
                    else:
                        computed_answer = entities[0] if entities else ""
            else:
                # No solution found - use temporal_order primitive
                event_relations = []
                for a, b in constraints:
                    event_relations.append((a, b, "before"))
                
                if event_relations:
                    temporal_result = temporal_order(event_relations)
                    if temporal_result:
                        computed_answer = temporal_result[0]
                    else:
                        computed_answer = entities[0] if entities else ""
                else:
                    computed_answer = entities[0] if entities else ""
        else:
            computed_answer = ""
        
        # Use confidence_from_agreement on multiple reasoning paths
        confidence_scores = []
        if topo_order:
            # Confidence from topological ordering
            confidence_scores.append(0.8 if len(topo_order) == len(entities) else 0.5)
        
        if valid_schedules:
            # Confidence from constraint solving
            confidence_scores.append(0.9)
        
        if schedule_entropy < 1.0:
            # Lower entropy means more certain
            confidence_scores.append(1.0 - schedule_entropy)
        
        if confidence_scores:
            confidence = confidence_from_agreement(confidence_scores)
        else:
            confidence = 0.5
        
        # Thermodynamic reasoning: optimal schedule minimizes free energy
        # Free energy = Entropy - (Constraint satisfaction * Temperature)
        # Here we use confidence as inverse of free energy
        if sufficiency == "determined":
            confidence = min(confidence * 1.2, 1.0)
        elif sufficiency == "underdetermined":
            confidence = confidence * 0.8
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Schedule analysis using thermodynamic principles. {sufficiency} system with entropy {schedule_entropy:.2f}. Optimal first element: {computed_answer}",
            "schedule_entropy": schedule_entropy,
            "sufficiency": sufficiency
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
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
        """Calibrate scores using thermodynamic temperature concept."""
        # Temperature adjusts confidence spread
        # High temperature = more uniform scores (uncertain)
        # Low temperature = more peaked scores (confident)
        
        if not scored:
            return scored
        
        # Extract raw scores
        raw_scores = [item["raw_score"] for item in scored]
        
        # Compute entropy of score distribution
        if raw_scores:
            # Normalize to probabilities
            total = sum(raw_scores)
            if total > 0:
                probs = [s/total for s in raw_scores]
                score_entropy = entropy(probs)
                
                # Temperature inversely related to confidence
                # Lower entropy (more peaked) -> lower temperature -> more amplification
                temperature = score_entropy
                
                # Apply Boltzmann-like adjustment
                calibrated = []
                for item in scored:
                    raw = item["raw_score"]
                    if temperature > 0:
                        # exp(-energy/temperature) where energy = 1 - score
                        energy = 1.0 - raw
                        adjusted = raw * (1.0 + (1.0 - energy) / (1.0 + temperature))
                    else:
                        adjusted = raw
                    
                    # Clip to [0, 1]
                    adjusted = max(0.0, min(1.0, adjusted))
                    
                    calibrated.append({
                        "candidate": item["candidate"],
                        "score": adjusted
                    })
                
                return calibrated
        
        return [{"candidate": item["candidate"], "score": item["raw_score"]} for item in scored]

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