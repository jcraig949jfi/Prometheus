import re
import zlib
from typing import Dict, List, Any, Tuple, Set

from forge_primitives import (
    solve_constraints,
    topological_sort,
    information_sufficiency,
    entropy,
    confidence_from_agreement,
    temporal_order
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
            # Find capitalized multi-word phrases (potential entity names)
            name_matches = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', line)
            for name in name_matches:
                if len(name.split()) <= 3:  # Avoid overly long phrases
                    entities.add(name)
            
            # Extract temporal constraints
            if any(word in line.lower() for word in ['before', 'after', 'during', 'while', 'when']):
                # Look for patterns like "A before B" or "A after B"
                before_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+before\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', line, re.IGNORECASE)
                after_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+after\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', line, re.IGNORECASE)
                
                if before_match:
                    temporal_relations.append((before_match.group(1), before_match.group(2), 'before'))
                if after_match:
                    temporal_relations.append((after_match.group(2), after_match.group(1), 'before'))  # Convert after to before
            
            # Extract numerical constraints (times, durations)
            time_matches = re.findall(r'(\d+)\s*(?:hour|minute|day|week|month|year)s?', line, re.IGNORECASE)
            if time_matches:
                # Associate times with nearby entities
                for name in name_matches:
                    if name in line:
                        constraints.append((name, 'duration', int(time_matches[0])))
        
        # Convert temporal relations to before/after tuples for temporal_order primitive
        temporal_tuples = []
        for rel in temporal_relations:
            if rel[2] == 'before':
                temporal_tuples.append((rel[0], rel[1], 'before'))
        
        return {
            "entities": list(entities),
            "constraints": constraints,
            "temporal_relations": temporal_tuples,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply information-theoretic constraint reasoning to find schedule."""
        entities = structure["entities"]
        temporal_relations = structure["temporal_relations"]
        constraints = structure["constraints"]
        
        # Use information_sufficiency primitive to check if system is determined
        n_entities = len(entities)
        n_constraints = len(temporal_relations) + len(constraints)
        sufficiency = information_sufficiency(n_entities, n_constraints)
        
        # Use topological_sort primitive to get partial order from temporal relations
        edges = [(rel[0], rel[1]) for rel in temporal_relations if len(rel) >= 2]
        partial_order = topological_sort(edges)
        
        # Use temporal_order primitive to get ordered events
        temporal_order_result = []
        if temporal_relations:
            temporal_order_result = temporal_order(temporal_relations)
        
        # Build constraint satisfaction problem
        variables = entities
        domains = {entity: list(range(len(entities))) for entity in entities}  # Positions 0..n-1
        
        # Define constraints for temporal ordering
        def before_constraint(a_pos, b_pos):
            return a_pos < b_pos
        
        csp_constraints = []
        for a, b, _ in temporal_relations:
            if a in variables and b in variables:
                csp_constraints.append(([a, b], before_constraint))
        
        # Use solve_constraints primitive to find a schedule
        schedule = solve_constraints(variables, domains, csp_constraints)
        
        # Use amino acid is_uniquely_solvable to check solution uniqueness
        unique = False
        if schedule:
            unique = is_uniquely_solvable(variables, domains, csp_constraints)
        
        # Compute information-theoretic metrics
        if schedule:
            # Convert schedule to probability distribution over positions
            positions = list(schedule.values())
            max_pos = max(positions) if positions else 0
            if max_pos > 0:
                # Normalize positions to create probability distribution
                probs = [positions.count(i) / len(positions) for i in range(max_pos + 1)]
                # Use entropy primitive to measure uncertainty in schedule
                schedule_entropy = entropy(probs) if probs else 0.0
            else:
                schedule_entropy = 0.0
        else:
            schedule_entropy = 1.0  # High entropy if no solution
        
        # Determine answer based on reasoning
        computed_answer = ""
        confidence = 0.5
        
        if schedule:
            # Find the entity that should come first (lowest position)
            if schedule:
                first_entity = min(schedule.items(), key=lambda x: x[1])[0]
                computed_answer = first_entity
                # Confidence based on entropy and uniqueness
                confidence = 0.8 - (schedule_entropy * 0.3) + (0.2 if unique else 0.0)
        elif partial_order:
            # Use topological sort result
            computed_answer = partial_order[0] if partial_order else ""
            confidence = 0.6
        elif temporal_order_result:
            # Use temporal order result
            computed_answer = temporal_order_result[0] if temporal_order_result else ""
            confidence = 0.6
        else:
            # Fallback to first entity mentioned
            computed_answer = entities[0] if entities else ""
            confidence = 0.3
        
        # Use confidence_from_agreement primitive with multiple metrics
        confidence_metrics = [
            confidence,
            0.8 if schedule else 0.3,
            0.7 if partial_order else 0.3,
            1.0 - min(schedule_entropy, 1.0)
        ]
        final_confidence = confidence_from_agreement(confidence_metrics)
        
        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "reasoning": f"Schedule entropy: {schedule_entropy:.3f}, Sufficiency: {sufficiency}, Unique: {unique}",
            "schedule": schedule,
            "partial_order": partial_order,
            "temporal_order": temporal_order_result
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
        
        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 0.9  # Strong match
            else:
                # Fallback: NCD similarity to reasoning text
                score = 1.0 / (1.0 + ncd(reasoning_text, candidate))
            
            results.append({
                "candidate": candidate,
                "score": score,
                "computed_answer": computed_answer
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using information-theoretic principles."""
        if not scored:
            return scored
        
        # Extract raw scores
        raw_scores = [item["score"] for item in scored]
        
        # Compute entropy of raw scores
        if raw_scores:
            # Normalize scores to create probability distribution
            total = sum(raw_scores)
            if total > 0:
                probs = [s / total for s in raw_scores]
                score_entropy = entropy(probs)
                
                # Adjust scores based on entropy: if entropy is high (uncertain),
                # compress scores toward mean; if low (certain), amplify differences
                mean_score = sum(raw_scores) / len(raw_scores)
                for item in scored:
                    if score_entropy > 0.7:  # High uncertainty
                        item["score"] = 0.7 * item["score"] + 0.3 * mean_score
                    elif score_entropy < 0.3:  # Low uncertainty
                        # Amplify differences from mean
                        diff = item["score"] - mean_score
                        item["score"] = mean_score + 1.5 * diff
        
        # Ensure scores are in [0, 1]
        for item in scored:
            item["score"] = max(0.0, min(1.0, item["score"]))
        
        return scored