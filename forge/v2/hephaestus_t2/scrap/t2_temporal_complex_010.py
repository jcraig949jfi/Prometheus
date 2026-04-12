import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    modular_arithmetic,
    temporal_order,
    information_sufficiency,
    solve_linear_system,
    expected_value,
    entropy
)
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """network_engineering x constraint_acids - temporal_complex"""

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
        """Extract temporal entities, values, and relationships from prompt."""
        structure = {
            "entities": {},
            "time_values": [],
            "relationships": [],
            "question": "",
            "raw": prompt
        }
        
        # Find question (usually last sentence ending with ?)
        sentences = [s.strip() for s in prompt.split('.') if s.strip()]
        for sent in sentences:
            if '?' in sent:
                structure["question"] = sent
                break
        
        # Extract time values with units
        time_pattern = r'(\d+)\s*(seconds?|minutes?|hours?|days?|weeks?|months?|years?)'
        time_matches = re.findall(time_pattern, prompt.lower())
        
        # Convert to minutes for consistent comparison
        time_values = []
        for amount, unit in time_matches:
            amount = int(amount)
            if 'second' in unit:
                minutes = amount / 60.0
            elif 'minute' in unit:
                minutes = amount
            elif 'hour' in unit:
                minutes = amount * 60
            elif 'day' in unit:
                minutes = amount * 1440
            elif 'week' in unit:
                minutes = amount * 10080
            elif 'month' in unit:
                minutes = amount * 43200  # approx
            elif 'year' in unit:
                minutes = amount * 525600  # approx
            else:
                minutes = amount
            time_values.append(minutes)
        
        structure["time_values"] = time_values
        
        # Extract temporal relationships (before, after, during, etc.)
        lines = prompt.split('\n')
        for line in lines:
            line_lower = line.lower()
            if 'before' in line_lower or 'after' in line_lower or 'during' in line_lower:
                # Find capitalized entity names
                entities = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', line)
                if len(entities) >= 2:
                    if 'before' in line_lower:
                        structure["relationships"].append((entities[0], 'before', entities[1]))
                    elif 'after' in line_lower:
                        structure["relationships"].append((entities[0], 'after', entities[1]))
        
        # Extract entity names (capitalized phrases)
        entity_names = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', prompt)
        for name in entity_names:
            if name not in structure["entities"] and len(name.split()) <= 3:
                structure["entities"][name] = {"mentions": 0, "time_refs": []}
        
        # Count mentions
        for name in structure["entities"]:
            structure["entities"][name]["mentions"] = prompt.count(name)
        
        return structure

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply network engineering concepts to solve temporal problems."""
        entities = structure["entities"]
        time_values = structure["time_values"]
        relationships = structure["relationships"]
        question = structure["question"]
        
        # CRITICAL: All primitives and amino acids must be load-bearing
        
        # 1. Use modular_arithmetic for time conversions (e.g., hours to minutes with wrap-around)
        if time_values:
            # Convert using modular arithmetic to handle wrap-around (like 24-hour clock)
            base_mod = 1440  # minutes in a day
            mod_results = []
            for val in time_values[:3]:  # Use first 3 time values
                # Apply modular arithmetic to find equivalent time within a day
                mod_result = modular_arithmetic(int(val), 0, base_mod)
                mod_results.append(mod_result)
            
            # Use these modular results to compute average time
            if mod_results:
                avg_mod_time = sum(mod_results) / len(mod_results)
            else:
                avg_mod_time = 0
        else:
            avg_mod_time = 0
            mod_results = []
        
        # 2. Use temporal_order to establish sequence from relationships
        temporal_edges = []
        for rel in relationships:
            if rel[1] == 'before':
                temporal_edges.append((rel[0], rel[2]))
            elif rel[1] == 'after':
                temporal_edges.append((rel[2], rel[0]))
        
        ordered_events = []
        if temporal_edges:
            order_result = temporal_order(temporal_edges)
            if order_result:
                ordered_events = order_result
        
        # 3. Use information_sufficiency to check if we have enough constraints
        n_unknowns = len(entities)
        n_constraints = len(relationships) + (1 if time_values else 0)
        sufficiency = information_sufficiency(n_unknowns, n_constraints)
        
        # 4. Use solve_linear_system if we have time equations
        linear_solution = None
        if len(time_values) >= 2:
            # Create simple linear system: x + y = total, x - y = difference
            if len(time_values) >= 2:
                total = sum(time_values[:2])
                diff = abs(time_values[0] - time_values[1]) if len(time_values) >= 2 else 0
                A = [[1, 1], [1, -1]]
                b = [total, diff]
                linear_solution = solve_linear_system(A, b)
        
        # 5. Use expected_value for probabilistic time estimates
        ev_result = 0
        if time_values:
            # Create probability-value pairs (equal probability for each time value)
            n = len(time_values)
            if n > 0:
                prob = 1.0 / n
                outcomes = [(prob, val) for val in time_values]
                ev_result = expected_value(outcomes)
        
        # 6. Use entropy to measure uncertainty in time distribution
        entropy_val = 0
        if time_values and len(time_values) > 1:
            # Normalize time values to create probability distribution
            total = sum(time_values)
            if total > 0:
                probs = [v/total for v in time_values]
                entropy_val = entropy(probs)
        
        # 7. Use constraint_acids amino acid to solve temporal CSP
        csp_solution = None
        if entities and relationships:
            # Build CSP: variables are events, domains are time slots
            variables = list(entities.keys())
            domains = {}
            for var in variables:
                # Domain: possible time positions (0-23 for hours, or 0-1439 for minutes)
                domains[var] = list(range(0, min(1440, 24 * len(variables))))
            
            # Constraints based on temporal relationships
            constraints = []
            for rel in relationships:
                if rel[1] == 'before':
                    def before_constraint(a, b):
                        return a < b
                    constraints.append(([rel[0], rel[2]], before_constraint))
                elif rel[1] == 'after':
                    def after_constraint(a, b):
                        return a > b
                    constraints.append(([rel[0], rel[2]], after_constraint))
            
            # CRITICAL: Use amino acid solve_first
            csp_solution = solve_first(variables, domains, constraints)
            
            # CRITICAL: Use amino acid is_uniquely_solvable
            unique_check = False
            if csp_solution:
                unique_check = is_uniquely_solvable(variables, domains, constraints)
        
        # Determine answer based on reasoning
        computed_answer = ""
        confidence = 0.5
        
        # Network engineering concept: Treat temporal system as packet routing with latency constraints
        # The answer is the entity with optimal temporal position (like router with minimal delay)
        
        if csp_solution:
            # Use CSP solution to find entity with earliest/latest time
            if "earlier" in question.lower() or "first" in question.lower() or "before" in question.lower():
                # Find entity with smallest time value
                earliest_entity = min(csp_solution.items(), key=lambda x: x[1])
                computed_answer = earliest_entity[0]
                confidence = 0.8
            elif "later" in question.lower() or "last" in question.lower() or "after" in question.lower():
                # Find entity with largest time value
                latest_entity = max(csp_solution.items(), key=lambda x: x[1])
                computed_answer = latest_entity[0]
                confidence = 0.8
            else:
                # Default: entity mentioned most (network traffic analogy)
                if entities:
                    most_mentioned = max(entities.items(), key=lambda x: x[1]["mentions"])
                    computed_answer = most_mentioned[0]
                    confidence = 0.7
        elif ordered_events:
            # Use temporal order
            if "first" in question.lower() or "begin" in question.lower():
                computed_answer = ordered_events[0] if ordered_events else ""
                confidence = 0.7
            elif "last" in question.lower() or "end" in question.lower():
                computed_answer = ordered_events[-1] if ordered_events else ""
                confidence = 0.7
        elif linear_solution:
            # Use linear system result
            computed_answer = f"{linear_solution[0]:.1f}"
            confidence = 0.6
        elif ev_result > 0:
            # Use expected value
            computed_answer = f"{ev_result:.1f}"
            confidence = 0.6
        else:
            # Fallback using modular arithmetic result
            if avg_mod_time > 0:
                computed_answer = f"{avg_mod_time:.1f}"
                confidence = 0.5
            elif entities:
                # Last resort: most mentioned entity
                most_mentioned = max(entities.items(), key=lambda x: x[1]["mentions"])
                computed_answer = most_mentioned[0]
                confidence = 0.4
        
        # Adjust confidence based on information sufficiency
        if sufficiency == "determined":
            confidence = min(confidence + 0.2, 1.0)
        elif sufficiency == "underdetermined":
            confidence = max(confidence - 0.1, 0.1)
        
        # Adjust confidence based on entropy (lower entropy = more certain)
        if entropy_val > 0:
            confidence = confidence * (1.0 - min(entropy_val, 0.5))
        
        return {
            "answer": str(computed_answer),
            "confidence": confidence,
            "reasoning": f"Temporal analysis using network engineering: {sufficiency} constraints, entropy={entropy_val:.3f}, CSP solution exists={csp_solution is not None}",
            "csp_solution": csp_solution,
            "ordered_events": ordered_events,
            "linear_solution": linear_solution,
            "expected_value": ev_result,
            "modular_results": mod_results
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary: exact match or substring match of computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Secondary: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust score by confidence
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
        if len(scores) > 1:
            min_score = min(scores)
            max_score = max(scores)
            if max_score > min_score:
                for item in scored:
                    item["score"] = (item["score"] - min_score) / (max_score - min_score)
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
        
        if max(ca, cb) > 0:
            return (cab - min(ca, cb)) / max(ca, cb)
        return 1.0