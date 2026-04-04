import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    information_sufficiency,
    solve_constraints,
    topological_sort,
    confidence_from_agreement,
    entropy
)
from forge.amino_acids.constraint_acids import is_uniquely_solvable


class ReasoningTool:
    """Information theory x Constraint satisfaction - temporal_scheduling"""

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
        
        entities = set()
        constraints = []
        temporal_relations = []
        question = lines[-1] if lines else ""
        
        # Extract entity names (capitalized words or phrases)
        for line in lines:
            # Find capitalized multi-word phrases (potential event/agent names)
            entity_matches = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', line)
            for entity in entity_matches:
                if len(entity.split()) <= 3:  # Avoid long phrases that might be sentences
                    entities.add(entity)
            
            # Extract temporal constraints
            if any(word in line.lower() for word in ['before', 'after', 'during', 'while', 'when']):
                # Look for patterns like "A before B" or "A must happen after B"
                before_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:must\s+)?(?:be\s+)?before\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', line, re.IGNORECASE)
                after_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:must\s+)?(?:be\s+)?after\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', line, re.IGNORECASE)
                
                if before_match:
                    a, b = before_match.group(1), before_match.group(2)
                    temporal_relations.append((a, b))
                    constraints.append(([a, b], lambda x, y: x < y))
                elif after_match:
                    a, b = after_match.group(1), after_match.group(2)
                    temporal_relations.append((b, a))  # Convert "A after B" to "B before A"
                    constraints.append(([b, a], lambda x, y: x < y))
            
            # Extract mutual exclusion constraints
            if any(word in line.lower() for word in ['cannot', "can't", 'conflict', 'same time']):
                # Look for patterns like "A and B cannot happen at the same time"
                entities_in_line = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', line)
                if len(entities_in_line) >= 2:
                    for i in range(len(entities_in_line)):
                        for j in range(i+1, len(entities_in_line)):
                            constraints.append(([entities_in_line[i], entities_in_line[j]], 
                                              lambda x, y: x != y))
        
        # Convert entities to list and create time slots
        entity_list = list(entities)
        time_slots = list(range(len(entity_list)))  # Simple integer time slots
        
        return {
            "entities": entity_list,
            "constraints": constraints,
            "temporal_relations": temporal_relations,
            "question": question,
            "time_slots": time_slots,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use information theory to analyze constraint satisfaction and find optimal schedule."""
        entities = structure["entities"]
        constraints = structure["constraints"]
        time_slots = structure["time_slots"]
        
        if not entities:
            return {"answer": "No schedule possible", "confidence": 0.0, "reasoning": "No entities found"}
        
        # Create variable domains (each entity gets a time slot)
        domains = {entity: time_slots for entity in entities}
        
        # Use T1 primitive: information_sufficiency to check if problem is well-posed
        n_unknowns = len(entities)
        n_constraints = len(constraints)
        sufficiency = information_sufficiency(n_unknowns, n_constraints)
        
        # Use amino acid: is_uniquely_solvable to check solution uniqueness
        unique_check = is_uniquely_solvable(domains, constraints)
        
        # Use T1 primitive: solve_constraints to find a valid schedule
        solution = solve_constraints(list(domains.keys()), domains, constraints)
        
        # Use T1 primitive: topological_sort on temporal relations
        topological_order = None
        if structure["temporal_relations"]:
            topological_order = topological_sort(structure["temporal_relations"])
        
        # Compute information-theoretic metrics
        if solution:
            # Calculate entropy of the schedule (information content)
            schedule_values = list(solution.values())
            if schedule_values:
                # Normalize values to probabilities for entropy calculation
                max_val = max(schedule_values)
                if max_val > 0:
                    probs = [v/max_val for v in schedule_values]
                    schedule_entropy = entropy(probs)
                else:
                    schedule_entropy = 0.0
            else:
                schedule_entropy = 0.0
            
            # Find the entity with earliest/latest time based on question
            if "earliest" in structure["question"].lower():
                computed_answer = min(solution.items(), key=lambda x: x[1])[0]
                reasoning_desc = f"Earliest scheduled entity based on constraint satisfaction"
            elif "latest" in structure["question"].lower():
                computed_answer = max(solution.items(), key=lambda x: x[1])[0]
                reasoning_desc = f"Latest scheduled entity based on constraint satisfaction"
            elif "conflict" in structure["question"].lower() or "impossible" in structure["question"].lower():
                computed_answer = "No valid schedule" if not solution else "Schedule exists"
                reasoning_desc = f"Constraint analysis shows {computed_answer}"
            else:
                # Default: return the schedule as a sorted string
                sorted_schedule = sorted(solution.items(), key=lambda x: x[1])
                computed_answer = ", ".join([f"{entity} at time {time}" for entity, time in sorted_schedule])
                reasoning_desc = f"Complete schedule with entropy {schedule_entropy:.3f}"
            
            # Use T1 primitive: confidence_from_agreement on multiple metrics
            confidence_scores = []
            if solution:
                confidence_scores.append(1.0)  # Solution exists
            if unique_check:
                confidence_scores.append(0.8 if unique_check else 0.5)  # Uniqueness confidence
            if topological_order:
                confidence_scores.append(0.7)  # Temporal consistency
            if sufficiency == "determined":
                confidence_scores.append(0.9)
            elif sufficiency == "underdetermined":
                confidence_scores.append(0.6)
            else:
                confidence_scores.append(0.4)
            
            confidence = confidence_from_agreement(confidence_scores) if confidence_scores else 0.5
            
            reasoning_text = f"Information sufficiency: {sufficiency}. "
            reasoning_text += f"Solution unique: {unique_check}. "
            reasoning_text += f"Schedule entropy: {schedule_entropy:.3f}. "
            if topological_order:
                reasoning_text += f"Topological order: {topological_order}. "
            reasoning_text += reasoning_desc
            
        else:
            computed_answer = "No valid schedule"
            confidence = 0.8
            reasoning_text = f"No solution found. Information sufficiency: {sufficiency}. Constraints may be inconsistent."
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": reasoning_text,
            "raw_solution": solution,
            "sufficiency": sufficiency,
            "unique": unique_check
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = str(reasoning_result["answer"])
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity between reasoning text and candidate
                score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
            results.append({
                "candidate": candidate,
                "score": score,
                "computed_answer": computed_answer
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence from reasoning."""
        if not scored:
            return scored
        
        # Use the confidence from reasoning to adjust scores
        max_score = max(item["score"] for item in scored)
        if max_score > 0:
            for item in scored:
                # Normalize and apply slight confidence-based adjustment
                item["score"] = (item["score"] / max_score) * 0.9 + 0.1
        
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