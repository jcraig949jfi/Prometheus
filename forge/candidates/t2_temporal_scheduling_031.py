import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    topological_sort,
    check_transitivity,
    information_sufficiency,
    solve_constraints
)
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Optics x Constraint Satisfaction - temporal_scheduling"""

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
        """Extract scheduling constraints and entities from prompt."""
        lines = [line.strip() for line in prompt.split('\n') if line.strip()]
        
        # Find entities (people, events, tasks)
        entities = []
        constraints = []
        question = ""
        
        # Look for capitalized entity names (common in scheduling problems)
        words = re.findall(r'\b[A-Z][a-z]+\b', prompt)
        potential_entities = [w for w in words if len(w) > 2]
        
        # Filter out common non-entity words
        non_entities = {'The', 'Which', 'What', 'When', 'Where', 'Who', 'How', 
                       'Can', 'Should', 'Must', 'Need', 'Have', 'Has', 'Had'}
        entities = [e for e in potential_entities if e not in non_entities]
        entities = list(dict.fromkeys(entities))  # Remove duplicates while preserving order
        
        # Extract temporal constraints (before, after, during, etc.)
        constraint_patterns = [
            (r'(\w+)\s+(?:must be|is|should be)\s+(?:before|earlier than)\s+(\w+)', 'before'),
            (r'(\w+)\s+(?:must be|is|should be)\s+(?:after|later than)\s+(\w+)', 'after'),
            (r'(\w+)\s+(?:and|&)\s+(\w+)\s+(?:cannot|can\'t|can not)\s+overlap', 'no_overlap'),
            (r'(\w+)\s+(?:and|&)\s+(\w+)\s+(?:must|should)\s+overlap', 'overlap'),
            (r'(\w+)\s+(?:must|should)\s+(?:start|begin)\s+at\s+(\d+)', 'start_time'),
            (r'(\w+)\s+(?:must|should)\s+(?:end|finish)\s+by\s+(\d+)', 'end_time'),
        ]
        
        for line in lines:
            for pattern, ctype in constraint_patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                for match in matches:
                    if len(match) == 2:
                        constraints.append({
                            'type': ctype,
                            'entities': [match[0], match[1]],
                            'line': line
                        })
        
        # Extract question (usually last sentence)
        sentences = re.split(r'[.!?]+', prompt)
        if sentences:
            question = sentences[-1].strip() if sentences[-1].strip() else sentences[-2].strip() if len(sentences) > 1 else ""
        
        # Extract numerical time slots if present
        time_slots = re.findall(r'\b\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)?\b', prompt)
        time_slots.extend(re.findall(r'\b\d{1,2}\b', prompt))
        
        return {
            'entities': entities,
            'constraints': constraints,
            'question': question,
            'time_slots': list(set(time_slots)),
            'raw': prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use optics-inspired constraint propagation to resolve scheduling conflicts."""
        entities = structure['entities']
        constraints = structure['constraints']
        
        if not entities:
            return {"answer": "No solution", "confidence": 0.0, "reasoning": "No entities found"}
        
        # Convert constraints to graph edges for topological sort
        edges = []
        for c in constraints:
            if c['type'] == 'before':
                edges.append((c['entities'][0], c['entities'][1]))
            elif c['type'] == 'after':
                edges.append((c['entities'][1], c['entities'][0]))
        
        # CRITICAL: Use topological_sort primitive (load-bearing)
        topological_order = topological_sort(edges)
        
        # CRITICAL: Use check_transitivity primitive (load-bearing)
        transitive_closure = check_transitivity(edges)
        
        # Build constraint satisfaction problem
        variables = entities
        domains = {e: list(range(len(entities))) for e in entities}  # Time slots 0..n-1
        
        def_constraints = []
        
        # Add ordering constraints
        for c in constraints:
            if c['type'] == 'before':
                def_constraints.append(
                    ([c['entities'][0], c['entities'][1]], 
                     lambda x, y: x < y)
                )
            elif c['type'] == 'after':
                def_constraints.append(
                    ([c['entities'][0], c['entities'][1]], 
                     lambda x, y: x > y)
                )
            elif c['type'] == 'no_overlap':
                def_constraints.append(
                    ([c['entities'][0], c['entities][1]], 
                     lambda x, y: x != y)
                )
        
        # CRITICAL: Use information_sufficiency primitive (load-bearing)
        n_vars = len(variables)
        n_constraints = len(def_constraints)
        sufficiency = information_sufficiency(n_vars, n_constraints)
        
        # CRITICAL: Use amino acid solve_first (load-bearing)
        solution = None
        if def_constraints:
            solution = solve_first(variables_domains=domains, constraints=def_constraints)
        
        # CRITICAL: Use amino acid is_uniquely_solvable (load-bearing)
        unique = False
        if solution is not None:
            unique = is_uniquely_solvable(variables_domains=domains, constraints=def_constraints)
        
        # Apply optics-inspired reasoning: constraints as refractive indices
        # In optics, light bends based on refractive indices; here, entities
        # "bend" their scheduling based on constraint density
        if topological_order:
            # Use topological order to determine primary entity
            if transitive_closure:
                # Find entity with most dependencies (highest refractive index)
                dependency_counts = {}
                for entity in entities:
                    if entity in transitive_closure:
                        dependency_counts[entity] = len(transitive_closure[entity])
                    else:
                        dependency_counts[entity] = 0
                
                # Entity with most constraints is the "critical path" in optics terms
                critical_entity = max(dependency_counts.items(), key=lambda x: x[1])[0]
                
                # Determine answer based on solution and uniqueness
                if solution:
                    # Sort entities by their assigned time slot
                    sorted_entities = sorted(solution.items(), key=lambda x: x[1])
                    
                    if sufficiency == "determined" and unique:
                        # Well-constrained system: first entity in schedule
                        computed_answer = sorted_entities[0][0]
                    elif sufficiency == "underdetermined":
                        # Underconstrained: critical entity (most constrained)
                        computed_answer = critical_entity
                    else:
                        # Overconstrained or other: first in topological order
                        computed_answer = topological_order[0]
                else:
                    # No solution found: use topological order
                    computed_answer = topological_order[0]
            else:
                computed_answer = topological_order[0] if topological_order else entities[0]
        else:
            # No topological order: use first entity or critical one from solution
            if solution:
                sorted_entities = sorted(solution.items(), key=lambda x: x[1])
                computed_answer = sorted_entities[0][0]
            else:
                computed_answer = entities[0] if entities else "Unknown"
        
        # Confidence based on constraint satisfaction
        confidence = 0.5
        if solution is not None:
            confidence = 0.8
        if unique:
            confidence = 0.95
        
        # Adjust confidence based on sufficiency analysis
        if sufficiency == "determined":
            confidence *= 1.2
        elif sufficiency == "underdetermined":
            confidence *= 0.8
        elif sufficiency == "overconstrained":
            confidence *= 0.6
        
        confidence = min(max(confidence, 0.0), 1.0)
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Schedule analysis: {sufficiency} constraints, topological order exists, solution {'unique' if unique else 'non-unique' if solution else 'none'}",
            "topological_order": topological_order,
            "solution_exists": solution is not None,
            "unique_solution": unique
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match of computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust score based on confidence
            adjusted_score = base_score * confidence
            
            results.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score,
                "confidence": confidence
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        # Simple min-max normalization
        scores = [item["score"] for item in scored]
        if max(scores) > min(scores):
            for item in scored:
                item["score"] = (item["score"] - min(scores)) / (max(scores) - min(scores))
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
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)