import re
import zlib
from typing import Dict, List, Any, Tuple, Set
from forge_primitives import (
    solve_constraints,
    topological_sort,
    information_sufficiency,
    confidence_from_agreement,
    entropy
)
from forge.amino_acids.constraint_acids import is_uniquely_solvable


class ReasoningTool:
    """Immunology x Constraint Satisfaction - temporal_scheduling"""

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
        """Parse prompt to extract entities, constraints, and question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find entity names (capitalized words that appear in constraints)
        entity_pattern = r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b'
        potential_entities = re.findall(entity_pattern, prompt)
        
        # Filter to likely entities (not common words, appear with temporal words)
        temporal_keywords = ['before', 'after', 'during', 'while', 'when', 'must', 'cannot', 'needs']
        entities = set()
        for ent in potential_entities:
            # Check if entity appears near temporal constraints
            context_window = 10
            words = prompt.lower().split()
            if any(kw in prompt.lower() for kw in temporal_keywords):
                # Simple heuristic: if it's mentioned with constraints, it's an entity
                entities.add(ent)
        
        # Extract numerical constraints (durations, times)
        numbers = re.findall(r'\b(\d+)\b', prompt)
        numbers = [int(n) for n in numbers]
        
        # Extract temporal relations
        relations = []
        for line in lines:
            line_lower = line.lower()
            # Look for "X before Y" patterns
            before_match = re.search(r'(\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b)\s+before\s+(\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b)', line)
            if before_match:
                relations.append((before_match.group(1), before_match.group(2)))
            # Look for "X after Y" patterns
            after_match = re.search(r'(\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b)\s+after\s+(\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b)', line)
            if after_match:
                relations.append((after_match.group(2), after_match.group(1)))  # Reverse for before relation
        
        # Extract resource constraints (e.g., "cannot overlap", "must be separate")
        resource_constraints = []
        for line in lines:
            if 'cannot' in line.lower() and ('overlap' in line.lower() or 'same' in line.lower()):
                # Find entities mentioned in this line
                line_entities = re.findall(entity_pattern, line)
                if len(line_entities) >= 2:
                    resource_constraints.append(('no_overlap', line_entities[:2]))
        
        return {
            "entities": list(entities),
            "relations": relations,
            "numbers": numbers,
            "resource_constraints": resource_constraints,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use immunology-inspired constraint resolution to find schedule."""
        entities = structure["entities"]
        relations = structure["relations"]
        
        if not entities:
            return {"answer": "No entities found", "confidence": 0.0, "reasoning": "Could not extract entities"}
        
        # Immunology concept: Immune system resolves conflicts via clonal selection and affinity maturation
        # Map to scheduling: Each schedule is an "antibody", constraints are "antigens"
        # High-affinity schedules satisfy more constraints
        
        # Build constraint satisfaction problem
        variables = entities
        domains = {var: list(range(len(entities))) for var in variables}  # Simple ordering positions
        
        constraints = []
        
        # Add temporal ordering constraints
        for a, b in relations:
            if a in variables and b in variables:
                constraints.append(([a, b], lambda x, y: x < y))
        
        # Add resource constraints (no overlap)
        for const_type, const_entities in structure["resource_constraints"]:
            if const_type == 'no_overlap' and len(const_entities) >= 2:
                a, b = const_entities[0], const_entities[1]
                if a in variables and b in variables:
                    constraints.append(([a, b], lambda x, y: x != y))
        
        # Use T1 primitive: solve_constraints
        solution = solve_constraints(variables, domains, constraints)
        
        # Use T1 primitive: information_sufficiency to check if problem is well-constrained
        n_vars = len(variables)
        n_constraints = len(constraints)
        sufficiency = information_sufficiency(n_vars, n_constraints)
        
        # Use amino acid: is_uniquely_solvable
        unique_check = is_uniquely_solvable(variables, domains, constraints)
        
        # Immunology: Compute "affinity" of solution (how well it satisfies constraints)
        affinity_scores = []
        if solution:
            # Score each constraint satisfaction
            for vars_list, constraint_func in constraints:
                values = [solution[var] for var in vars_list]
                satisfied = constraint_func(*values)
                affinity_scores.append(1.0 if satisfied else 0.0)
        
        # Use T1 primitive: entropy to measure schedule diversity/uncertainty
        if solution:
            position_counts = {}
            for pos in solution.values():
                position_counts[pos] = position_counts.get(pos, 0) + 1
            probs = [count/len(solution) for count in position_counts.values()]
            schedule_entropy = entropy(probs) if probs else 0.0
        else:
            schedule_entropy = 1.0  # High entropy = high uncertainty
        
        # Determine answer based on solution
        if solution:
            # Sort entities by their assigned position
            ordered_entities = sorted(solution.items(), key=lambda x: x[1])
            schedule_order = [ent for ent, _ in ordered_entities]
            
            # Immunology: The "fittest" schedule emerges from constraint resolution
            # Answer is the schedule order or a specific entity mentioned in question
            computed_answer = self._extract_answer_from_question(structure["question"], schedule_order)
            confidence = 0.8 if unique_check else 0.6
            reasoning = f"Schedule determined via constraint satisfaction. Sufficiency: {sufficiency}. Unique: {unique_check}. Entropy: {schedule_entropy:.2f}"
        else:
            # No solution found
            computed_answer = "No valid schedule"
            confidence = 0.3
            reasoning = f"No solution found. Problem {sufficiency}. Constraint count: {n_constraints}"
        
        # Use T1 primitive: confidence_from_agreement
        if affinity_scores:
            confidence_score = confidence_from_agreement(affinity_scores)
            confidence = (confidence + confidence_score) / 2  # Blend
        
        return {
            "answer": computed_answer,
            "confidence": min(max(confidence, 0.0), 1.0),
            "reasoning": reasoning,
            "schedule_order": solution,
            "sufficiency": sufficiency,
            "unique": unique_check
        }

    def _extract_answer_from_question(self, question: str, schedule_order: List[str]) -> str:
        """Extract what the question is asking for."""
        question_lower = question.lower()
        
        # Common temporal scheduling question patterns
        if "first" in question_lower:
            return schedule_order[0] if schedule_order else "Unknown"
        elif "last" in question_lower:
            return schedule_order[-1] if schedule_order else "Unknown"
        elif "order" in question_lower or "sequence" in question_lower:
            return ", ".join(schedule_order) if schedule_order else "No order"
        elif "when" in question_lower:
            # Find entity mentioned in question
            entity_pattern = r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b'
            question_entities = re.findall(entity_pattern, question)
            for ent in question_entities:
                if ent in schedule_order:
                    # Return position
                    position = schedule_order.index(ent) + 1
                    return f"Position {position}"
        
        # Default: return the entire schedule
        return ", ".join(schedule_order) if schedule_order else "No schedule"

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        results = []
        
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity
                score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            results.append({
                "candidate": candidate,
                "score": score,
                "computed_answer": computed_answer
            })
        
        return results

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance."""
        if not a or not b:
            return 1.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores based on confidence and distribution."""
        if not scored:
            return scored
        
        scores = [item["score"] for item in scored]
        if not scores:
            return scored
        
        # Simple calibration: normalize to [0, 1] range
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score - min_score > 0:
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        else:
            # All scores equal
            for item in scored:
                item["score"] = 0.5
        
        return scored