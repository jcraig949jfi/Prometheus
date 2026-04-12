import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    topological_sort,
    solve_constraints,
    information_sufficiency,
    confidence_from_agreement,
    entropy,
    solve_linear_system
)
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """network_engineering x constraint_acids - temporal_scheduling"""

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        # Phase 1: EXTRACT
        structure = self._extract(prompt)
        
        # Phase 2: REASON
        reasoning_result = self._reason(structure)
        
        # Phase 3: SCORE
        scored = self._score_candidates(candidates, reasoning_result)
        
        # Phase 4: CALIBRATE
        calibrated = self._calibrate(scored)
        
        return sorted(calibrated, key=lambda x: x["score"], reverse=True)

    def _extract(self, prompt: str) -> Dict[str, Any]:
        """Extract scheduling constraints and entities from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        
        # Find question (usually last sentence)
        question = lines[-1] if lines else ""
        
        # Extract entities (capitalized names that appear in constraints)
        entity_pattern = r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b'
        entities = set(re.findall(entity_pattern, prompt))
        
        # Extract temporal constraints (before/after/during)
        constraints = []
        temporal_keywords = ['before', 'after', 'during', 'must', 'cannot', 'while']
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in temporal_keywords):
                # Find entity pairs in constraint
                line_entities = re.findall(entity_pattern, line)
                if len(line_entities) >= 2:
                    # Simple parsing for "A before B" patterns
                    if 'before' in line_lower:
                        # Find which entity comes before which
                        words = line.split()
                        for i, word in enumerate(words):
                            if word.lower() == 'before' and i > 0 and i < len(words) - 1:
                                before_entity = words[i-1]
                                after_entity = words[i+1]
                                if before_entity in entities and after_entity in entities:
                                    constraints.append((before_entity, after_entity))
                    elif 'after' in line_lower:
                        words = line.split()
                        for i, word in enumerate(words):
                            if word.lower() == 'after' and i > 0 and i < len(words) - 1:
                                after_entity = words[i-1]
                                before_entity = words[i+1]
                                if before_entity in entities and after_entity in entities:
                                    constraints.append((before_entity, after_entity))
        
        # Extract durations if mentioned
        durations = {}
        duration_pattern = r'(\d+)\s*(?:minute|hour|day|week)s?\b'
        for line in lines:
            matches = re.findall(duration_pattern, line.lower())
            if matches:
                # Associate duration with nearby entity
                line_entities = re.findall(entity_pattern, line)
                for entity in line_entities:
                    if entity in entities and matches:
                        durations[entity] = int(matches[0])
        
        return {
            "entities": list(entities),
            "constraints": constraints,
            "durations": durations,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply network engineering principles to solve scheduling."""
        entities = structure["entities"]
        constraints = structure["constraints"]
        durations = structure["durations"]
        
        # CRITICAL PATH 1: Topological sort for dependency resolution
        # In network engineering, we find the critical path through task dependencies
        sorted_entities = topological_sort(constraints)
        
        # CRITICAL PATH 2: Constraint satisfaction for scheduling
        # Model as CSP: each entity has a start time, respecting constraints
        variables = entities
        domains = {entity: list(range(0, 100)) for entity in entities}  # 0-99 time slots
        
        # Define constraints: if A before B, then start_A + duration_A <= start_B
        csp_constraints = []
        for a, b in constraints:
            def make_constraint(entity_a, entity_b):
                def constraint(values):
                    start_a = values[entity_a]
                    start_b = values[entity_b]
                    duration_a = durations.get(entity_a, 1)
                    return start_a + duration_a <= start_b
                return constraint
            
            csp_constraints.append(([a, b], make_constraint(a, b)))
        
        # CRITICAL PATH 3: Amino acid - solve_first for CSP solution
        solution = solve_first(variables_domains=domains, constraints=csp_constraints)
        
        # CRITICAL PATH 4: Information sufficiency check
        # In network engineering, we check if constraints fully determine the schedule
        sufficiency = information_sufficiency(len(entities), len(constraints))
        
        # CRITICAL PATH 5: Amino acid - check if solution is unique
        unique = is_uniquely_solvable(variables_domains=domains, constraints=csp_constraints)
        
        # CRITICAL PATH 6: Compute schedule entropy (uncertainty in timing)
        if solution:
            # Extract start times
            start_times = list(solution.values())
            # Normalize to probabilities for entropy calculation
            if start_times:
                max_time = max(start_times)
                if max_time > 0:
                    probs = [t/max_time for t in start_times]
                    # Add small epsilon to avoid zero probabilities
                    probs = [p + 0.001 for p in probs]
                    total = sum(probs)
                    probs = [p/total for p in probs]
                    schedule_entropy = entropy(probs)
                else:
                    schedule_entropy = 0.0
            else:
                schedule_entropy = 0.0
        else:
            schedule_entropy = 1.0  # High entropy = uncertain schedule
        
        # Determine answer based on reasoning
        computed_answer = ""
        
        if solution:
            # In network engineering, we often want the entity that starts first
            # (critical path analysis)
            if sorted_entities:
                # Use topological sort result to determine order
                first_entity = sorted_entities[0]
                computed_answer = first_entity
            else:
                # Fallback: earliest start time from CSP solution
                earliest_entity = min(solution.items(), key=lambda x: x[1])[0]
                computed_answer = earliest_entity
            
            # CRITICAL: Use information sufficiency to adjust confidence
            # If underdetermined, we're less confident
            if sufficiency == "underdetermined":
                computed_answer = f"Either {computed_answer} or ambiguous"
            elif sufficiency == "overconstrained" and not unique:
                computed_answer = "No valid schedule"
        else:
            computed_answer = "No solution possible"
        
        # CRITICAL PATH 7: Confidence from multiple reasoning sources
        confidence_sources = []
        if sorted_entities:
            confidence_sources.append(0.8 if len(sorted_entities) == len(entities) else 0.5)
        if solution:
            confidence_sources.append(0.9)
        if unique:
            confidence_sources.append(0.95)
        else:
            confidence_sources.append(0.6)
        
        confidence = confidence_from_agreement(confidence_sources) if confidence_sources else 0.5
        
        # Apply network engineering principle: low entropy = more reliable schedule
        confidence = confidence * (1.0 - schedule_entropy * 0.5)
        
        return {
            "answer": computed_answer,
            "confidence": max(0.1, min(0.99, confidence)),
            "reasoning": f"Schedule analysis: {sufficiency} constraints, {'unique' if unique else 'multiple'} solutions, entropy={schedule_entropy:.2f}",
            "schedule": solution,
            "order": sorted_entities
        }

    def _score_candidates(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on match with computed answer."""
        computed_answer = reasoning_result["answer"]
        results = []
        
        for candidate in candidates:
            # Primary scoring: exact or substring match with computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust score based on confidence
            adjusted_score = base_score * reasoning_result["confidence"]
            
            results.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score,
                "confidence": reasoning_result["confidence"]
            })
        
        return results

    def _calibrate(self, scored_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper ranking."""
        if not scored_candidates:
            return scored_candidates
        
        # Simple normalization to [0, 1] range
        scores = [item["score"] for item in scored_candidates]
        if scores:
            min_score = min(scores)
            max_score = max(scores)
            if max_score > min_score:
                for item in scored_candidates:
                    item["score"] = (item["score"] - min_score) / (max_score - min_score)
            else:
                # All scores equal
                for item in scored_candidates:
                    item["score"] = 0.5
        
        return scored_candidates

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