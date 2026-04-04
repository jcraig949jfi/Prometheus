import re
import zlib
from typing import Dict, List, Any, Tuple, Optional
from forge_primitives import (
    solve_constraints,
    topological_sort,
    information_sufficiency,
    confidence_from_agreement,
    dag_traverse,
    temporal_order
)
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable, check_consistency

class ReasoningTool:
    """Climate modeling x Constraint satisfaction - Temporal scheduling"""

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
        
        # Find entity names (capitalized words that appear as subjects of constraints)
        # Look for patterns like "Task A", "Meeting X", "Event Y"
        entity_pattern = r'\b([A-Z][a-z]+\s+[A-Z][a-z]+|[A-Z][a-z]+)\b'
        potential_entities = re.findall(entity_pattern, prompt)
        # Filter to likely entities (not common words, appear with temporal words)
        temporal_keywords = ['before', 'after', 'during', 'starts', 'ends', 'at', 'on', 'must', 'cannot']
        entities = []
        for ent in set(potential_entities):
            # Check if entity appears near temporal keywords
            context = prompt.lower()
            ent_lower = ent.lower()
            idx = context.find(ent_lower)
            if idx != -1:
                snippet = context[max(0, idx-50):min(len(context), idx+50)]
                if any(keyword in snippet for keyword in temporal_keywords):
                    entities.append(ent)
        
        # Extract temporal constraints
        constraints = []
        # Pattern for "X before Y", "X after Y", "X cannot overlap with Y"
        before_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:must be|is)\s+before\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
        after_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:must be|is)\s+after\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
        overlap_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:cannot|must not)\s+(?:overlap|co-occur)\s+with\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
        
        for match in re.finditer(before_pattern, prompt, re.IGNORECASE):
            constraints.append(('before', match.group(1), match.group(2)))
        for match in re.finditer(after_pattern, prompt, re.IGNORECASE):
            constraints.append(('after', match.group(1), match.group(2)))
        for match in re.finditer(overlap_pattern, prompt, re.IGNORECASE):
            constraints.append(('no_overlap', match.group(1), match.group(2)))
        
        # Extract time slots or durations if mentioned
        time_slots = []
        time_pattern = r'(\d+:\d+\s*(?:AM|PM)?)\s*to\s*(\d+:\d+\s*(?:AM|PM)?)'
        for match in re.finditer(time_pattern, prompt, re.IGNORECASE):
            time_slots.append((match.group(1), match.group(2)))
        
        duration_pattern = r'(\d+)\s*(?:hour|minute|hr|min)s?\s*(?:long|duration)'
        durations = [int(match.group(1)) for match in re.finditer(duration_pattern, prompt, re.IGNORECASE)]
        
        return {
            "entities": entities,
            "constraints": constraints,
            "time_slots": time_slots,
            "durations": durations,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply climate modeling concepts to resolve scheduling conflicts."""
        entities = structure["entities"]
        constraints = structure["constraints"]
        
        if not entities:
            return {"answer": "", "confidence": 0.0, "reasoning": "No entities found"}
        
        # Climate modeling concept: Treat scheduling as a coupled system
        # where constraints act like radiative forcings, and the schedule
        # is the equilibrium state reached through iterative relaxation.
        
        # Build constraint graph for topological analysis
        edges = []
        for cons_type, a, b in constraints:
            if cons_type == 'before':
                edges.append((a, b))
            elif cons_type == 'after':
                edges.append((b, a))
        
        # Use topological_sort primitive (T1)
        topological_order = topological_sort(edges)
        
        # Use information_sufficiency primitive (T1)
        n_unknowns = len(entities)
        n_constraints = len(constraints)
        sufficiency = information_sufficiency(n_unknowns, n_constraints)
        
        # Convert constraints to CSP format for amino acid
        variables = {ent: list(range(len(entities))) for ent in entities}
        
        def csp_constraints():
            # Create constraint functions for the CSP
            cons_funcs = []
            
            # Before/after constraints
            for cons_type, a, b in constraints:
                if cons_type in ['before', 'after']:
                    def make_before_constraint(x, y):
                        return lambda vals: vals[x] < vals[y]
                    # Find indices
                    if a in entities and b in entities:
                        idx_a = entities.index(a)
                        idx_b = entities.index(b)
                        cons_funcs.append(([a, b], make_before_constraint(idx_a, idx_b)))
            
            # No overlap constraints (must be different time slots)
            for cons_type, a, b in constraints:
                if cons_type == 'no_overlap':
                    def make_no_overlap_constraint(x, y):
                        return lambda vals: vals[x] != vals[y]
                    if a in entities and b in entities:
                        idx_a = entities.index(a)
                        idx_b = entities.index(b)
                        cons_funcs.append(([a, b], make_no_overlap_constraint(idx_a, idx_b)))
            
            return cons_funcs
        
        constraint_funcs = csp_constraints()
        
        # Use constraint amino acid (solve_first)
        solution = None
        try:
            solution = solve_first(variables, constraint_funcs)
        except Exception:
            solution = None
        
        # Use is_uniquely_solvable amino acid
        unique = False
        try:
            unique = is_uniquely_solvable(variables, constraint_funcs)
        except Exception:
            unique = False
        
        # Use check_consistency amino acid
        consistent = False
        try:
            consistent = check_consistency(variables, constraint_funcs)
        except Exception:
            consistent = False
        
        # Climate modeling: If system is overconstrained (like radiative imbalance),
        # find the "forcing" that needs adjustment
        if sufficiency == "overconstrained" or not consistent:
            # Find conflicting constraints
            conflict_info = "System is overconstrained. "
            if edges:
                # Use dag_traverse primitive (T1) to find reachable nodes
                if edges:
                    start_node = edges[0][0]
                    reachable = dag_traverse(edges, start_node)
                    conflict_info += f"Constraint chain starts from {start_node} reaches {len(reachable)} nodes. "
            
            # Determine which entity is most constrained (highest indegree)
            indegree = {ent: 0 for ent in entities}
            for _, a, b in constraints:
                if a in indegree:
                    indegree[a] += 1
                if b in indegree:
                    indegree[b] += 1
            
            if indegree:
                most_constrained = max(indegree.items(), key=lambda x: x[1])
                computed_answer = most_constrained[0]
                reasoning = f"{conflict_info}Most constrained entity is {computed_answer} with {most_constrained[1]} constraints."
            else:
                computed_answer = entities[0] if entities else ""
                reasoning = "No clear constraint structure."
        else:
            # System is solvable, find the schedule
            if solution:
                # Sort entities by their assigned time slot
                scheduled = sorted(solution.items(), key=lambda x: x[1])
                computed_answer = scheduled[0][0]  # First entity in schedule
                reasoning = f"Schedule found. {computed_answer} is first in the sequence."
            elif topological_order:
                computed_answer = topological_order[0]
                reasoning = f"Partial order found. {computed_answer} comes first topologically."
            else:
                computed_answer = entities[0]
                reasoning = "Using first entity as default."
        
        # Use confidence_from_agreement primitive (T1)
        # Create multiple scoring methods
        scores = []
        
        # Score 1: Based on constraint satisfaction
        if solution is not None:
            scores.append(0.9)
        else:
            scores.append(0.3)
        
        # Score 2: Based on topological consistency
        if topological_order and len(topological_order) == len(entities):
            scores.append(0.8)
        else:
            scores.append(0.4)
        
        # Score 3: Based on uniqueness
        if unique:
            scores.append(0.95)
        else:
            scores.append(0.5)
        
        confidence = 0.5
        if scores:
            confidence = confidence_from_agreement(scores)
        
        # Climate modeling: Adjust confidence based on "system equilibrium"
        # If constraints are balanced (like radiative equilibrium), confidence is higher
        constraint_balance = abs(len([c for c in constraints if c[0] == 'before']) - 
                               len([c for c in constraints if c[0] == 'after']))
        balance_factor = 1.0 / (1.0 + constraint_balance)
        confidence = (confidence + balance_factor) / 2
        
        return {
            "answer": computed_answer,
            "confidence": min(max(confidence, 0.0), 1.0),
            "reasoning": reasoning,
            "constraint_count": len(constraints),
            "entity_count": len(entities),
            "solution_exists": solution is not None
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() in candidate.lower():
                base_score = 0.9
            else:
                # Fallback: NCD similarity to reasoning text
                base_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
            # Adjust based on candidate characteristics
            # Candidates that mention scheduling terms get slight boost
            scheduling_terms = ['schedule', 'time', 'order', 'sequence', 'first', 'before', 'after']
            term_count = sum(1 for term in scheduling_terms if term in candidate.lower())
            term_boost = min(0.1 * term_count, 0.3)
            
            final_score = min(base_score + term_boost, 1.0)
            
            results.append({
                "candidate": candidate,
                "score": final_score,
                "base_score": base_score,
                "term_boost": term_boost
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using climate modeling equilibrium concept."""
        if not scored:
            return scored
        
        # Climate modeling: Apply "energy balance" calibration
        # Scores represent "temperature" - normalize to equilibrium distribution
        scores = [item["score"] for item in scored]
        max_score = max(scores) if scores else 1.0
        min_score = min(scores) if scores else 0.0
        
        if max_score - min_score > 0:
            # Boltzmann-like normalization: exp(score) / sum(exp(score))
            # Temperature parameter T = 0.5 (moderate smoothing)
            T = 0.5
            exp_scores = [pow(2.71828, s/T) for s in scores]
            sum_exp = sum(exp_scores)
            calibrated_scores = [e/sum_exp for e in exp_scores]
            
            for i, item in enumerate(scored):
                item["score"] = calibrated_scores[i]
                item["calibrated"] = True
        else:
            # All scores equal - distribute uniformly
            uniform_score = 1.0 / len(scored)
            for item in scored:
                item["score"] = uniform_score
                item["calibrated"] = True
        
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