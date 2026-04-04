import re
import zlib
from typing import Dict, List, Any, Tuple, Set

from forge_primitives import (
    information_sufficiency,
    topological_sort,
    solve_constraints,
    confidence_from_agreement,
    entropy
)
from forge.amino_acids.constraint_acids import is_uniquely_solvable


class ReasoningTool:
    """Information theory x Constraint satisfaction - Temporal scheduling"""

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
        """Extract entities, temporal constraints, and the question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find all capitalized entity names (people, events, tasks)
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        entities = set(re.findall(entity_pattern, prompt))
        
        # Remove common non-entity capitalized words
        common_words = {'The', 'A', 'An', 'And', 'But', 'Or', 'For', 'Nor', 'So', 'Yet'}
        entities = {e for e in entities if e not in common_words}
        
        # Extract temporal relations
        relations = []
        temporal_keywords = {
            'before': 'before', 'after': 'after', 'earlier': 'before',
            'later': 'after', 'precedes': 'before', 'follows': 'after',
            'must be scheduled before': 'before', 'must be scheduled after': 'after'
        }
        
        for line in lines:
            line_lower = line.lower()
            for keyword, relation in temporal_keywords.items():
                if keyword in line_lower:
                    # Find entities in this line
                    line_entities = re.findall(entity_pattern, line)
                    if len(line_entities) >= 2:
                        if relation == 'before':
                            relations.append((line_entities[0], line_entities[1]))
                        else:  # 'after'
                            relations.append((line_entities[1], line_entities[0]))
        
        # Extract time slots or durations if mentioned
        time_pattern = r'(\d+)\s*(?:hour|minute|day|slot|time)'
        times = re.findall(time_pattern, prompt.lower())
        durations = [int(t) for t in times] if times else []
        
        return {
            "entities": list(entities),
            "relations": relations,
            "question": question,
            "durations": durations,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use information theory to analyze constraint satisfaction in scheduling."""
        entities = structure["entities"]
        relations = structure["relations"]
        question = structure["question"]
        
        if not entities or not relations:
            return {"answer": "No solution", "confidence": 0.0, "reasoning": "Insufficient data"}
        
        # 1. Use information_sufficiency primitive to check if system is determined
        n_unknowns = len(entities)
        n_constraints = len(relations)
        sufficiency = information_sufficiency(n_unknowns, n_constraints)
        
        # 2. Build constraint satisfaction problem
        # Each entity is a variable that can be assigned a time slot
        variables = entities
        # Create domains based on number of entities
        max_slots = len(entities) + 3  # Allow some extra slots
        domains = {var: list(range(1, max_slots + 1)) for var in variables}
        
        # Define constraints: if A before B, then slot(A) < slot(B)
        constraints = []
        for a, b in relations:
            def make_constraint(x, y):
                return lambda vals: vals[x] < vals[y]
            constraints.append(([a, b], make_constraint(a, b)))
        
        # 3. Use solve_constraints primitive to find a solution
        solution = solve_constraints(variables, domains, constraints)
        
        # 4. Use amino acid is_uniquely_solvable to check solution uniqueness
        unique_check = is_uniquely_solvable(variables, domains, constraints)
        
        # 5. Use topological_sort primitive to find partial order
        topological_order = topological_sort(relations)
        
        # 6. Calculate information entropy of the solution space
        # If multiple solutions exist, entropy is higher
        if solution:
            # Count possible solutions by trying different domain sizes
            solution_count = 1
            if not unique_check:
                # Estimate solution count based on constraint tightness
                solution_count = max(2, len(entities) - len(relations))
            
            # Create probability distribution for solution existence
            if solution_count > 1:
                p_solution = 1.0
                p_other = 0.0
            else:
                p_solution = 0.8 if solution else 0.2
                p_other = 1 - p_solution
            
            probs = [p_solution, p_other]
            info_entropy = entropy(probs) if all(0 <= p <= 1 for p in probs) else 1.0
        else:
            info_entropy = 1.0  # Maximum uncertainty if no solution
        
        # Determine answer based on question type
        computed_answer = ""
        reasoning_text = ""
        
        if "order" in question.lower() or "sequence" in question.lower():
            if topological_order:
                computed_answer = " -> ".join(topological_order)
                reasoning_text = f"Topological order: {computed_answer}"
            else:
                computed_answer = "No valid order"
                reasoning_text = "Constraints contain cycles"
        
        elif "possible" in question.lower() or "feasible" in question.lower():
            if solution:
                computed_answer = "Yes"
                reasoning_text = f"Solution exists: {solution}"
            else:
                computed_answer = "No"
                reasoning_text = "No solution satisfies all constraints"
        
        elif "unique" in question.lower():
            if unique_check:
                computed_answer = "Yes"
                reasoning_text = "Exactly one solution exists"
            else:
                computed_answer = "No"
                reasoning_text = "Multiple solutions possible"
        
        else:
            # Default: provide the schedule if solution exists
            if solution:
                # Sort entities by their assigned time slots
                scheduled = sorted(solution.items(), key=lambda x: x[1])
                computed_answer = ", ".join([f"{e}({t})" for e, t in scheduled])
                reasoning_text = f"Schedule: {computed_answer}"
            else:
                computed_answer = "No valid schedule"
                reasoning_text = "Constraints are inconsistent"
        
        # Calculate confidence using multiple metrics
        confidence_scores = []
        
        # Confidence from solution existence
        if solution:
            confidence_scores.append(0.8)
        else:
            confidence_scores.append(0.2)
        
        # Confidence from topological order consistency
        if topological_order:
            confidence_scores.append(0.7)
        
        # Confidence from information sufficiency
        if sufficiency == "determined":
            confidence_scores.append(0.9)
        elif sufficiency == "underdetermined":
            confidence_scores.append(0.5)
        else:
            confidence_scores.append(0.3)
        
        # Confidence from entropy (lower entropy = higher confidence)
        confidence_scores.append(1.0 - min(info_entropy, 1.0))
        
        # Use confidence_from_agreement primitive
        if confidence_scores:
            final_confidence = confidence_from_agreement(confidence_scores)
        else:
            final_confidence = 0.5
        
        # Adjust confidence based on uniqueness
        if unique_check:
            final_confidence = min(1.0, final_confidence * 1.2)
        
        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "reasoning": f"{reasoning_text}. System: {sufficiency}. Entropy: {info_entropy:.2f}.",
            "raw_solution": solution,
            "topological_order": topological_order
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
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
        if not scores:
            return scored
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score - min_score < 0.01:  # All scores are nearly equal
            for item in scored:
                item["score"] = 0.5
        else:
            # Normalize to 0-1 range
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        
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