import re
import zlib
from typing import List, Dict, Any, Tuple

from forge_primitives import (
    solve_constraints,
    topological_sort,
    information_sufficiency,
    confidence_from_agreement,
    entropy
)
from forge.amino_acids.constraint_acids import is_uniquely_solvable


class ReasoningTool:
    """social_choice_theory x constraint_acids - temporal_scheduling"""

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
        
        # Find entity names (capitalized words that appear in constraints)
        # Look for patterns like "Alice must meet before Bob" or "Meeting X at time Y"
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        potential_entities = re.findall(entity_pattern, prompt)
        
        # Filter to likely entities (not common words, appear multiple times)
        common_words = {'The', 'A', 'An', 'And', 'But', 'Or', 'For', 'Nor', 'Yet', 'So'}
        entities = []
        for ent in set(potential_entities):
            if ent not in common_words and prompt.count(ent) >= 2:
                entities.append(ent)
        
        # Extract temporal constraints
        constraints = []
        # Patterns for before/after constraints
        before_pattern = r'(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b)\s+(?:must\s+)?(?:be\s+)?before\s+(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b)'
        after_pattern = r'(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b)\s+(?:must\s+)?(?:be\s+)?after\s+(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b)'
        
        for match in re.finditer(before_pattern, prompt, re.IGNORECASE):
            constraints.append((match.group(1), match.group(2), 'before'))
        
        for match in re.finditer(after_pattern, prompt, re.IGNORECASE):
            constraints.append((match.group(1), match.group(2), 'after'))
        
        # Extract time slots if mentioned
        time_slots = []
        time_pattern = r'(\d+:\d+\s*(?:AM|PM|am|pm)?|\d+\s*(?:am|pm|AM|PM))'
        time_slots = re.findall(time_pattern, prompt)
        
        # Extract duration constraints if any
        duration_pattern = r'(\d+)\s*(?:hour|minute|min|hr)s?'
        durations = re.findall(duration_pattern, prompt)
        
        return {
            "entities": entities,
            "constraints": constraints,
            "time_slots": time_slots,
            "durations": [int(d) for d in durations],
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply social choice theory to resolve scheduling conflicts."""
        entities = structure["entities"]
        constraints = structure["constraints"]
        question = structure["question"]
        
        if not entities or not constraints:
            # Fallback if extraction fails
            return {
                "answer": "No valid schedule",
                "confidence": 0.0,
                "reasoning": "Insufficient data extracted from prompt"
            }
        
        # Convert constraints to DAG edges for topological sort
        edges = []
        for a, b, rel in constraints:
            if rel == 'before':
                edges.append((a, b))
            elif rel == 'after':
                edges.append((b, a))
        
        # Use topological_sort primitive
        schedule_order = topological_sort(edges)
        
        # Use information_sufficiency primitive
        n_entities = len(entities)
        n_constraints = len(constraints)
        sufficiency = information_sufficiency(n_entities, n_constraints)
        
        # Build constraint satisfaction problem
        variables = entities
        # Simple domains: positions 0..n-1
        domains = {var: list(range(len(entities))) for var in variables}
        
        # Define constraint functions
        csp_constraints = []
        
        # All-different constraint (implicit in topological sort)
        def all_different(values):
            return len(set(values)) == len(values)
        
        csp_constraints.append((variables, all_different))
        
        # Add ordering constraints from edges
        for a, b in edges:
            def make_order_constraint(var_a, var_b):
                def constraint(values_dict):
                    return values_dict[var_a] < values_dict[var_b]
                return constraint
            
            csp_constraints.append(([a, b], make_order_constraint(a, b)))
        
        # Use solve_constraints primitive
        solution = solve_constraints(variables, domains, csp_constraints)
        
        # Use is_uniquely_solvable amino acid
        unique = is_uniquely_solvable(variables, domains, csp_constraints)
        
        # Apply social choice theory: treat each constraint as a voter preference
        # Borda count: each constraint votes for its preferred ordering
        borda_scores = {entity: 0 for entity in entities}
        
        for a, b, rel in constraints:
            if rel == 'before':
                # 'a before b' gives points to a for earlier position
                borda_scores[a] += 2
                borda_scores[b] += 1
            elif rel == 'after':
                # 'a after b' gives points to b for earlier position
                borda_scores[a] += 1
                borda_scores[b] += 2
        
        # Find entity with highest Borda score (social choice winner)
        if borda_scores:
            social_choice_winner = max(borda_scores.items(), key=lambda x: x[1])[0]
        else:
            social_choice_winner = entities[0] if entities else "Unknown"
        
        # Calculate entropy of Borda scores as measure of conflict
        if borda_scores:
            total = sum(borda_scores.values())
            if total > 0:
                probs = [score/total for score in borda_scores.values()]
                conflict_entropy = entropy(probs)
            else:
                conflict_entropy = 0.0
        else:
            conflict_entropy = 0.0
        
        # Determine answer based on social choice and CSP solution
        computed_answer = ""
        reasoning_text = ""
        
        if solution is not None:
            # Sort entities by position in solution
            ordered = sorted(solution.items(), key=lambda x: x[1])
            schedule = [entity for entity, _ in ordered]
            
            if unique:
                computed_answer = " -> ".join(schedule)
                reasoning_text = f"Unique schedule found: {' -> '.join(schedule)}. Social choice winner: {social_choice_winner}."
            else:
                computed_answer = social_choice_winner
                reasoning_text = f"Multiple possible schedules. Social choice winner (Borda count): {social_choice_winner}. Conflict entropy: {conflict_entropy:.2f}."
        else:
            # No valid schedule
            computed_answer = "No valid schedule"
            reasoning_text = f"Constraints are inconsistent. Social choice winner would be {social_choice_winner} but no schedule satisfies all constraints."
        
        # Use confidence_from_agreement primitive
        # Create multiple scoring methods
        scores = []
        
        # Score 1: based on whether solution exists
        scores.append(1.0 if solution is not None else 0.0)
        
        # Score 2: based on uniqueness
        scores.append(1.0 if unique else 0.5)
        
        # Score 3: based on Borda score dominance
        if borda_scores:
            max_score = max(borda_scores.values())
            min_score = min(borda_scores.values())
            if max_score > min_score:
                dominance = (max_score - min_score) / max_score
                scores.append(dominance)
            else:
                scores.append(0.0)
        
        confidence = confidence_from_agreement(scores) if scores else 0.5
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": reasoning_text,
            "social_choice_winner": social_choice_winner,
            "schedule_order": schedule_order if schedule_order else [],
            "constraint_sufficiency": sufficiency,
            "is_consistent": solution is not None,
            "is_unique": unique
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        social_choice_winner = reasoning_result.get("social_choice_winner", "")
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 1.0
            # Secondary: check if social choice winner appears
            elif social_choice_winner and social_choice_winner.lower() in candidate.lower():
                score = 0.8
            # Tertiary: use NCD similarity with reasoning text
            else:
                score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
            results.append({
                "candidate": candidate,
                "score": score,
                "computed_answer": computed_answer
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores based on confidence."""
        if not scored:
            return scored
        
        # Simple calibration: scale by confidence from reasoning phase
        # In a real implementation, this would use more sophisticated calibration
        calibrated = []
        for item in scored:
            calibrated.append({
                "candidate": item["candidate"],
                "score": item["score"],
                "computed_answer": item.get("computed_answer", "")
            })
        
        return calibrated

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