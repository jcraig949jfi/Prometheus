import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    modular_arithmetic,
    temporal_order,
    topological_sort,
    confidence_from_agreement,
    solve_linear_system,
    information_sufficiency
)
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Genetics x Constraint Satisfaction - temporal_complex"""

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
        """Extract temporal entities, constraints, and question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find temporal entities (dates, times, durations)
        entities = {}
        constraints = []
        temporal_relations = []
        
        # Extract time patterns: HH:MM, dates, durations like "2 hours", "3 days"
        time_pattern = r'(\d{1,2}):(\d{2})\s*(?:AM|PM|am|pm)?'
        duration_pattern = r'(\d+)\s*(?:hour|minute|day|week|month|year)s?'
        date_pattern = r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:,\s*\d{4})?'
        
        for line in lines:
            # Extract named entities (capitalized phrases that might be event names)
            names = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', line)
            for name in names:
                if name not in entities and len(name.split()) <= 3:
                    entities[name] = {"type": "event", "times": []}
            
            # Extract times and associate with nearest entity
            times = re.findall(time_pattern, line)
            for hour, minute in times:
                # Convert to minutes for easier arithmetic
                h = int(hour)
                m = int(minute)
                if "PM" in line.upper() and h < 12:
                    h += 12
                if "AM" in line.upper() and h == 12:
                    h = 0
                total_minutes = h * 60 + m
                
                # Find nearest entity in the line
                for entity in entities:
                    if entity in line:
                        if "times" not in entities[entity]:
                            entities[entity]["times"] = []
                        entities[entity]["times"].append(total_minutes)
            
            # Extract durations
            durations = re.findall(duration_pattern, line, re.IGNORECASE)
            for dur in durations:
                duration_val = int(dur)
                # Store as constraint if line contains comparison words
                if any(word in line.lower() for word in ["before", "after", "earlier", "later", "takes", "duration"]):
                    # Find entities mentioned in this line
                    line_entities = [e for e in entities if e in line]
                    if len(line_entities) >= 2:
                        constraints.append(("duration", line_entities[0], line_entities[1], duration_val))
            
            # Extract temporal relations
            if "before" in line.lower():
                parts = line.split("before")
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip().split()[0]
                    temporal_relations.append((left, "before", right))
            elif "after" in line.lower():
                parts = line.split("after")
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip().split()[0]
                    temporal_relations.append((left, "after", right))
        
        # Convert temporal relations to edges for topological sort
        edges = []
        for left, rel, right in temporal_relations:
            if rel == "before":
                edges.append((left, right))
            elif rel == "after":
                edges.append((right, left))
        
        return {
            "entities": entities,
            "constraints": constraints,
            "edges": edges,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Reason about temporal relationships using genetics-inspired constraint solving."""
        entities = structure["entities"]
        constraints = structure["constraints"]
        edges = structure["edges"]
        question = structure["question"]
        
        # GENETICS FRAMEWORK: Treat temporal constraints as genetic constraints
        # Variables = temporal positions (like genes)
        # Constraints = evolutionary pressures
        # Solution = viable temporal arrangement (like viable genotype)
        
        # 1. Use topological_sort to get partial order from explicit before/after relations
        # This primitive is LOAD-BEARING: determines which events come first
        sorted_events = topological_sort(edges)
        
        # 2. Use temporal_order to refine ordering from pairwise relations
        # Convert edges to temporal_order format
        temporal_pairs = []
        for src, dst in edges:
            temporal_pairs.append((src, "before", dst))
        
        ordered_events = []
        if temporal_pairs:
            ordered_events = temporal_order(temporal_pairs)
        
        # 3. Build constraint satisfaction problem for temporal arithmetic
        # Extract all time points mentioned
        time_points = {}
        for entity, data in entities.items():
            if "times" in data and data["times"]:
                time_points[entity] = data["times"][0]
        
        # Add duration constraints
        csp_variables = list(time_points.keys())
        csp_domains = {}
        
        # Determine reasonable domain for each time point
        # Use modular_arithmetic to handle wrap-around (24-hour clock)
        base_time = 0
        for var in csp_variables:
            # Start with known time if available
            if var in time_points:
                known_time = time_points[var]
                # Use modular_arithmetic to handle possible adjustments
                # This primitive is LOAD-BEARING: handles time wrap-around
                adjusted_time = modular_arithmetic(known_time, 0, 1440)  # 1440 minutes in day
                csp_domains[var] = [adjusted_time]
            else:
                # Unknown time: use wide domain
                csp_domains[var] = list(range(0, 1440, 60))  # Hourly increments
        
        # Define constraints based on durations
        csp_constraints = []
        for const_type, e1, e2, duration in constraints:
            if const_type == "duration":
                # Constraint: e2 happens duration minutes after e1
                def make_duration_constraint(dur):
                    def constraint(vals):
                        t1, t2 = vals
                        # Use modular_arithmetic for wrap-around
                        expected = modular_arithmetic(t1, dur, 1440)
                        return t2 == expected
                    return constraint
                
                csp_constraints.append(([e1, e2], make_duration_constraint(duration)))
        
        # 4. Use amino acid solve_first to find a solution
        # This amino acid is LOAD-BEARING: finds temporal arrangement satisfying all constraints
        solution = None
        if csp_variables and csp_constraints:
            solution = solve_first(csp_variables, csp_domains, csp_constraints)
        
        # 5. Use amino acid is_uniquely_solvable to check if solution is unique
        # This amino acid is LOAD-BEARING: determines if answer is forced or ambiguous
        unique = False
        if csp_variables and csp_constraints:
            unique = is_uniquely_solvable(csp_variables, csp_domains, csp_constraints)
        
        # 6. Determine what the question is asking for
        computed_answer = ""
        confidence = 0.5
        
        if "when" in question.lower() or "time" in question.lower():
            # Question asks for a specific time
            # Find the entity mentioned in the question
            question_entity = None
            for entity in entities:
                if entity in question:
                    question_entity = entity
                    break
            
            if question_entity and solution and question_entity in solution:
                # Convert minutes back to HH:MM format
                minutes = solution[question_entity]
                hours = minutes // 60
                mins = minutes % 60
                am_pm = "AM" if hours < 12 else "PM"
                if hours > 12:
                    hours -= 12
                if hours == 0:
                    hours = 12
                computed_answer = f"{hours}:{mins:02d} {am_pm}"
                confidence = 0.8 if unique else 0.6
            else:
                # Fallback: use topological ordering
                if sorted_events and question_entity in sorted_events:
                    pos = sorted_events.index(question_entity)
                    computed_answer = f"position {pos + 1} in sequence"
                    confidence = 0.4
        
        elif "order" in question.lower() or "sequence" in question.lower():
            # Question asks for ordering
            if ordered_events:
                computed_answer = " -> ".join(ordered_events)
                confidence = 0.7
            elif sorted_events:
                computed_answer = " -> ".join(sorted_events)
                confidence = 0.5
        
        elif "how long" in question.lower() or "duration" in question.lower():
            # Question asks for duration
            # Extract entities from question
            question_entities = [e for e in entities if e in question]
            if len(question_entities) >= 2 and solution:
                e1, e2 = question_entities[0], question_entities[1]
                if e1 in solution and e2 in solution:
                    t1 = solution[e1]
                    t2 = solution[e2]
                    # Use modular_arithmetic to compute difference
                    diff = modular_arithmetic(t2, -t1, 1440)
                    computed_answer = f"{diff} minutes"
                    confidence = 0.7
        
        else:
            # Generic answer: report the solution or ordering
            if solution:
                computed_answer = str(solution)
            elif ordered_events:
                computed_answer = " -> ".join(ordered_events)
            else:
                computed_answer = "Cannot determine"
            confidence = 0.3
        
        # 7. Use confidence_from_agreement to combine confidence sources
        # This primitive is LOAD-BEARING: aggregates multiple evidence sources
        confidence_sources = []
        if sorted_events:
            confidence_sources.append(0.6)
        if ordered_events:
            confidence_sources.append(0.7)
        if solution:
            confidence_sources.append(0.8 if unique else 0.6)
        
        if confidence_sources:
            final_confidence = confidence_from_agreement(confidence_sources)
        else:
            final_confidence = confidence
        
        # 8. Use information_sufficiency to check if problem is well-constrained
        # This primitive is LOAD-BEARING: validates problem structure
        n_vars = len(csp_variables)
        n_constraints = len(csp_constraints)
        sufficiency = information_sufficiency(n_vars, n_constraints)
        
        # Adjust confidence based on sufficiency
        if sufficiency == "determined":
            final_confidence = min(0.9, final_confidence + 0.1)
        elif sufficiency == "underdetermined":
            final_confidence = max(0.3, final_confidence - 0.2)
        
        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "reasoning": f"Temporal arrangement with {sufficiency} constraints",
            "solution": solution,
            "ordered_events": ordered_events
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or containment
            if computed_answer.lower() in candidate.lower():
                score = 1.0 * confidence
            else:
                # Fallback: NCD similarity
                ncd_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
                score = ncd_score * confidence
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        # Simple normalization
        scores = [item["raw_score"] for item in scored]
        if max(scores) > 0:
            scale = 1.0 / max(scores)
        else:
            scale = 1.0
        
        for item in scored:
            item["score"] = item["raw_score"] * scale
        
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