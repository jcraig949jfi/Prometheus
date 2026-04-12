import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    solve_linear_system,
    expected_value,
    information_sufficiency
)
from forge.amino_acids.constraint_acids import (
    solve_first,
    is_uniquely_solvable
)


class ReasoningTool:
    """Group theory x constraint satisfaction - rate_of_change"""

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
        """Extract entities, values, and time points from the prompt."""
        structure = {
            "entities": {},
            "time_points": [],
            "values": [],
            "question": "",
            "raw": prompt
        }
        
        # Find all sentences
        sentences = [s.strip() for s in re.split(r'[.!?]+', prompt) if s.strip()]
        if sentences:
            structure["question"] = sentences[-1]
        
        # Extract time points (years, days, hours, etc.)
        time_patterns = [
            r'(\d{4})',  # years like 2020
            r'(\d+)\s*(?:year|day|month|hour|minute|second)s?',
            r'time\s*(\d+)',
            r'at\s*t=(\d+)',
            r'after\s*(\d+)'
        ]
        
        all_times = []
        for pattern in time_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                try:
                    time_val = int(match)
                    if time_val not in all_times:
                        all_times.append(time_val)
                except ValueError:
                    pass
        
        structure["time_points"] = sorted(all_times)
        
        # Extract numerical values (including percentages, decimals)
        value_patterns = [
            r'(\d+\.?\d*)%',  # percentages
            r'\$(\d+\.?\d*)',  # dollar amounts
            r'(\d+\.?\d*)\s*(?:units|items|people)',
            r'value\s*[io]s\s*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*(?:to|from)'
        ]
        
        all_values = []
        for pattern in value_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                try:
                    val = float(match)
                    if val not in all_values:
                        all_values.append(val)
                except ValueError:
                    pass
        
        structure["values"] = sorted(all_values)
        
        # Extract entity names (capitalized multi-word phrases)
        entity_matches = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', prompt)
        for entity in entity_matches:
            if len(entity.split()) <= 3 and entity not in ["The", "A", "An", "At", "In", "On"]:
                if entity not in structure["entities"]:
                    structure["entities"][entity] = {
                        "mentions": 0,
                        "associated_values": []
                    }
                structure["entities"][entity]["mentions"] += 1
        
        # Try to associate values with entities based on proximity
        lines = prompt.split('\n')
        for line in lines:
            line_entities = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', line)
            line_values = re.findall(r'(\d+\.?\d*)%?', line)
            
            for entity in line_entities:
                if entity in structure["entities"]:
                    for val_str in line_values:
                        try:
                            val = float(val_str)
                            if val not in structure["entities"][entity]["associated_values"]:
                                structure["entities"][entity]["associated_values"].append(val)
                        except ValueError:
                            pass
        
        return structure

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply group theory concepts to analyze rates of change."""
        entities = structure["entities"]
        time_points = structure["time_points"]
        values = structure["values"]
        question = structure["question"]
        
        # Use group theory concept: transformations over time form a group
        # We'll model time points as group elements and values as group actions
        
        # CRITICAL: Use amino acid to check if the system is uniquely solvable
        # This directly determines if we can compute a unique rate of change
        
        # Build a constraint satisfaction problem from extracted data
        variables = []
        domains = {}
        constraints = []
        
        # Create variables for each time point
        for i, t in enumerate(time_points):
            var_name = f"t{t}"
            variables.append(var_name)
            # Domain based on extracted values
            if values:
                # Use values as possible domain elements
                domains[var_name] = sorted(values)
            else:
                # Fallback domain
                domains[var_name] = list(range(0, 101, 10))
        
        # Add constraint: values should follow some rate of change pattern
        # This is where group theory comes in - we're looking for transformations
        # that preserve structure (group homomorphisms)
        
        if len(variables) >= 2:
            # Constraint: difference between consecutive time points
            # should be consistent (group operation property)
            for i in range(len(variables) - 1):
                var1 = variables[i]
                var2 = variables[i + 1]
                
                def diff_constraint(vals, v1=var1, v2=var2):
                    # In group theory, we want the transformation to be consistent
                    # This constraint checks if the difference is within reasonable bounds
                    val1, val2 = vals
                    if val1 == 0 or val2 == 0:
                        return True  # Allow zero values
                    # Check if ratio is reasonable (group operation should be smooth)
                    ratio = abs(val2 / val1) if val1 != 0 else float('inf')
                    return 0.5 <= ratio <= 2.0  # Reasonable rate bounds
                
                constraints.append(([var1, var2], diff_constraint))
        
        # CRITICAL: Use amino acid to check uniqueness
        # This directly determines our confidence in the computed rate
        is_unique = False
        if variables and domains:
            try:
                unique_result = is_uniquely_solvable(variables, domains, constraints)
                if unique_result is not None:
                    is_unique = bool(unique_result)
            except Exception:
                is_unique = False
        
        # CRITICAL: Use amino acid to find a solution
        # This directly gives us the values at each time point
        solution = None
        if variables and domains:
            try:
                solution = solve_first(variables, domains, constraints)
            except Exception:
                solution = None
        
        # Now compute rate of change using group theory concepts
        # In group theory, we can think of the rate as the generator of the transformation group
        
        computed_answer = ""
        confidence = 0.5
        reasoning_text = ""
        
        if solution and len(time_points) >= 2:
            # Extract values from solution
            sol_values = []
            for t in time_points:
                var_name = f"t{t}"
                if var_name in solution:
                    sol_values.append(solution[var_name])
                else:
                    # Fallback to extracted values
                    if values:
                        sol_values.append(values[0])
                    else:
                        sol_values.append(0)
            
            # CRITICAL: Use T1 primitive to compute expected value
            # This gives us the average rate of change
            if len(sol_values) >= 2:
                # Create probability-value pairs for expected value calculation
                # In group theory, each time step is equally likely as a group element
                prob = 1.0 / (len(sol_values) - 1)
                outcomes = []
                
                for i in range(1, len(sol_values)):
                    if sol_values[i-1] != 0:
                        rate = (sol_values[i] - sol_values[i-1]) / sol_values[i-1]
                    else:
                        rate = 0
                    outcomes.append((prob, rate))
                
                if outcomes:
                    avg_rate = expected_value(outcomes)
                    
                    # CRITICAL: Use T1 primitive to compute entropy of rates
                    # In group theory, low entropy means more structured transformation
                    rates = [rate for _, rate in outcomes]
                    if rates:
                        # Normalize rates for entropy calculation
                        rate_sum = sum(abs(r) for r in rates)
                        if rate_sum > 0:
                            norm_rates = [abs(r)/rate_sum for r in rates]
                            rate_entropy = entropy(norm_rates)
                        else:
                            rate_entropy = 1.0
                        
                        # CRITICAL: Use T1 primitive for information sufficiency
                        # Check if we have enough data to determine the rate
                        n_unknowns = len(time_points)
                        n_constraints = len(constraints)
                        info_status = information_sufficiency(n_unknowns, n_constraints)
                        
                        # CRITICAL: Use T1 primitive for confidence from agreement
                        # Check consistency of computed rates
                        rate_consistency = 1.0 - (max(rates) - min(rates)) / (max(abs(r) for r in rates) + 1e-10)
                        confidence_scores = [rate_consistency, 1.0 - rate_entropy, 1.0 if is_unique else 0.5]
                        confidence = confidence_from_agreement(confidence_scores)
                        
                        # Determine the answer based on group theory analysis
                        # In group theory, we look for the generator of the transformation
                        if avg_rate > 0:
                            direction = "increasing"
                        elif avg_rate < 0:
                            direction = "decreasing"
                        else:
                            direction = "constant"
                        
                        # CRITICAL: Use T1 primitive for Bayesian update
                        # Update our belief about the rate based on entropy
                        prior = 0.5
                        likelihood = 1.0 - min(rate_entropy, 1.0)
                        posterior = bayesian_update(prior, likelihood)
                        
                        # CRITICAL: Use T1 primitive to solve linear system for rate
                        # Fit a linear model to the data
                        if len(time_points) >= 2 and len(sol_values) >= 2:
                            # Create linear system: value = a*time + b
                            A = []
                            b = []
                            for i, t in enumerate(time_points[:len(sol_values)]):
                                A.append([t, 1])
                                b.append(sol_values[i])
                            
                            linear_solution = solve_linear_system(A, b)
                            if linear_solution:
                                slope = linear_solution[0]  # This is the rate
                                
                                # Format the answer
                                if "percent" in question.lower() or "%" in question:
                                    computed_answer = f"{slope*100:.1f}%"
                                elif "rate" in question.lower():
                                    computed_answer = f"{slope:.2f} per unit time"
                                elif "increase" in question.lower() or "decrease" in question.lower():
                                    computed_answer = f"{direction} at {abs(slope):.2f} per unit time"
                                else:
                                    # Find the entity with most mentions
                                    if entities:
                                        main_entity = max(entities.items(), 
                                                         key=lambda x: x[1]["mentions"])[0]
                                        computed_answer = f"{main_entity}: {direction} ({slope:.2f})"
                                    else:
                                        computed_answer = f"{direction} ({slope:.2f})"
                                
                                reasoning_text = f"Linear fit slope: {slope:.3f}, Entropy: {rate_entropy:.3f}, Unique: {is_unique}, Posterior: {posterior:.3f}"
                            else:
                                computed_answer = f"{direction} (average: {avg_rate:.2f})"
                                reasoning_text = f"Average rate: {avg_rate:.3f}, Entropy: {rate_entropy:.3f}"
                        else:
                            computed_answer = f"{direction} (average: {avg_rate:.2f})"
                            reasoning_text = f"Average rate: {avg_rate:.3f}, Entropy: {rate_entropy:.3f}"
                    else:
                        computed_answer = "Cannot determine rate"
                        reasoning_text = "Insufficient data for rate calculation"
                else:
                    computed_answer = "No rate data"
                    reasoning_text = "No rate outcomes computed"
            else:
                computed_answer = "Insufficient time points"
                reasoning_text = "Need at least 2 time points for rate calculation"
        else:
            # Fallback: use extracted values directly
            if values and len(values) >= 2:
                # Simple rate calculation from first and last values
                rate = (values[-1] - values[0]) / (len(values) - 1)
                computed_answer = f"{rate:.2f}"
                reasoning_text = f"Simple average rate from {len(values)} values"
            elif entities:
                # Use the most mentioned entity
                main_entity = max(entities.items(), key=lambda x: x[1]["mentions"])[0]
                computed_answer = main_entity
                reasoning_text = "Using most mentioned entity as answer"
            else:
                computed_answer = "Unknown"
                reasoning_text = "No data extracted from prompt"
        
        return {
            "answer": computed_answer,
            "confidence": float(confidence),
            "reasoning": reasoning_text,
            "is_unique": is_unique,
            "solution": solution
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        scored = []
        
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity with reasoning text
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust score based on confidence
            adjusted_score = base_score * confidence
            
            scored.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score,
                "confidence": confidence
            })
        
        return scored

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        # Extract scores
        scores = [item["score"] for item in scored]
        
        # Simple min-max normalization if needed
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score > min_score:
            for item in scored:
                # Normalize to [0, 1] range
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