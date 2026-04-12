import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    solve_linear_system,
    topological_sort,
    information_sufficiency
)
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable
from forge.amino_acids.pysat_acids import check_entailment


class ReasoningTool:
    """Error-correcting codes x Constraint satisfaction - compositional_multi_step"""

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
        """Extract entities, values, and relationships from the prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find all capitalized multi-word phrases as potential entities
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        entities = {}
        
        # Extract numerical values and associate with nearby entities
        for line in lines:
            # Find percentages and regular numbers
            percentages = re.findall(r'([0-9]+\.?[0-9]*)%', line)
            numbers = re.findall(r'\b([0-9]+\.?[0-9]*)\b(?!%)', line)
            all_numbers = [float(n) for n in percentages + numbers]
            
            # Find entity names in this line
            found_entities = re.findall(entity_pattern, line)
            
            for entity in found_entities:
                if entity not in entities:
                    entities[entity] = {"values": [], "mentions": 0, "context": []}
                entities[entity]["values"].extend(all_numbers)
                entities[entity]["mentions"] += 1
                entities[entity]["context"].append(line)
        
        # Extract relationships (A > B, A causes B, etc.)
        relationships = []
        for line in lines:
            if ">" in line or "greater than" in line.lower():
                parts = re.split(r'>|greater than', line, flags=re.IGNORECASE)
                if len(parts) >= 2:
                    left = re.search(entity_pattern, parts[0])
                    right = re.search(entity_pattern, parts[1])
                    if left and right:
                        relationships.append((left.group(), right.group()))
        
        # Extract constraints (equations, inequalities)
        constraints = []
        for line in lines:
            if "=" in line and any(c.isalpha() for c in line):
                # Simple equation extraction
                eq_parts = line.split('=')
                if len(eq_parts) == 2:
                    constraints.append(line.strip())
        
        return {
            "entities": entities,
            "relationships": relationships,
            "constraints": constraints,
            "question": question,
            "raw_lines": lines
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply error-correcting codes framework to multi-step reasoning."""
        entities = structure["entities"]
        relationships = structure["relationships"]
        constraints = structure["constraints"]
        question = structure["question"]
        
        # Step 1: Build dependency graph from relationships (error detection)
        edges = []
        for a, b in relationships:
            edges.append((a, b))
        
        # CRITICAL PRIMITIVE 1: Topological sort to find reasoning order
        # This determines which steps depend on which others
        reasoning_order = topological_sort(edges)
        if reasoning_order is None:
            # Graph has cycles, use alphabetical order as fallback
            reasoning_order = sorted(entities.keys())
        
        # Step 2: Extract numerical values as "codewords" that need verification
        all_values = []
        for entity, data in entities.items():
            all_values.extend(data["values"])
        
        # CRITICAL PRIMITIVE 2: Entropy of extracted values (information measure)
        # In error-correcting codes, entropy measures information content
        if all_values:
            # Normalize values to probabilities for entropy calculation
            total = sum(all_values)
            if total > 0:
                probs = [v/total for v in all_values]
                info_entropy = entropy(probs)
            else:
                info_entropy = 0.0
        else:
            info_entropy = 0.0
        
        # Step 3: Parse constraints as linear equations (parity checks)
        equations = []
        for constr in constraints:
            # Simple parsing: look for patterns like "A + B = C" or "2A = B"
            numbers = re.findall(r'\b([0-9]+\.?[0-9]*)\b', constr)
            entity_names = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', constr)
            
            if len(entity_names) >= 2 and "=" in constr:
                # Try to extract coefficients
                coeffs = {}
                for name in entity_names:
                    # Look for coefficient before entity
                    pattern = rf'([0-9]+\.?[0-9]*)\s*{re.escape(name)}'
                    match = re.search(pattern, constr)
                    if match:
                        coeffs[name] = float(match.group(1))
                    else:
                        coeffs[name] = 1.0
                
                # Find constant on right side
                right_side = constr.split('=')[1]
                right_numbers = re.findall(r'([0-9]+\.?[0-9]*)', right_side)
                if right_numbers:
                    constant = float(right_numbers[0])
                    equations.append((coeffs, constant))
        
        # Step 4: Solve constraint system (error correction)
        computed_answer = None
        confidence = 0.5
        
        if equations and len(equations) >= 2:
            # Build linear system
            entity_list = list(entities.keys())
            A = []
            b = []
            
            for coeffs, constant in equations:
                row = []
                for entity in entity_list:
                    row.append(coeffs.get(entity, 0.0))
                A.append(row)
                b.append(constant)
            
            # CRITICAL PRIMITIVE 3: Solve linear system
            solution = solve_linear_system(A, b)
            
            if solution is not None:
                # CRITICAL AMINO ACID 1: Check if solution is unique (error detection)
                # Represent constraints as CSP
                variables = entity_list
                domains = {var: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] for var in variables}
                
                # Convert equations to constraints
                csp_constraints = []
                for coeffs, constant in equations:
                    def make_eq_constraint(coeffs_dict, target):
                        def constraint(assignment):
                            total = 0
                            for var, val in assignment.items():
                                total += coeffs_dict.get(var, 0) * val
                            return abs(total - target) < 0.001
                        return constraint
                    
                    csp_constraints.append((variables, make_eq_constraint(coeffs, constant)))
                
                # Check uniqueness
                is_unique = is_uniquely_solvable(variables, domains, csp_constraints)
                
                if is_unique:
                    # Map solution to entity with highest value
                    entity_values = {}
                    for i, entity in enumerate(entity_list):
                        if i < len(solution):
                            entity_values[entity] = solution[i]
                    
                    if entity_values:
                        # Find entity with maximum value
                        best_entity = max(entity_values.items(), key=lambda x: x[1])[0]
                        
                        # CRITICAL PRIMITIVE 4: Bayesian update for confidence
                        # Use entropy as prior uncertainty
                        prior = 1.0 - min(info_entropy, 1.0)
                        likelihood = 0.8 if is_unique else 0.5
                        confidence = bayesian_update(prior, likelihood)
                        
                        computed_answer = best_entity
                else:
                    # Multiple solutions, use topological order
                    if reasoning_order:
                        computed_answer = reasoning_order[0]
                        confidence = 0.3
            else:
                # System inconsistent, use relationship-based reasoning
                if reasoning_order:
                    computed_answer = reasoning_order[0]
                    confidence = 0.2
        else:
            # Not enough equations, use relationship-based reasoning
            if reasoning_order:
                computed_answer = reasoning_order[0]
                
                # CRITICAL PRIMITIVE 5: Information sufficiency check
                n_unknowns = len(entities)
                n_constraints = len(constraints) + len(relationships)
                sufficiency = information_sufficiency(n_unknowns, n_constraints)
                
                if sufficiency == "determined":
                    confidence = 0.7
                elif sufficiency == "underdetermined":
                    confidence = 0.4
                else:
                    confidence = 0.2
        
        # Fallback if no answer computed
        if computed_answer is None and entities:
            computed_answer = list(entities.keys())[0]
            confidence = 0.1
        
        # CRITICAL PRIMITIVE 6: Final confidence aggregation
        # Combine multiple confidence sources
        confidence_sources = [confidence]
        if entities:
            # Add confidence based on entity mentions
            mention_counts = [data["mentions"] for data in entities.values()]
            if mention_counts:
                max_mentions = max(mention_counts)
                mention_confidence = max_mentions / (max_mentions + 1)
                confidence_sources.append(mention_confidence)
        
        final_confidence = confidence_from_agreement(confidence_sources)
        
        return {
            "answer": str(computed_answer) if computed_answer else "",
            "confidence": final_confidence,
            "reasoning": f"Multi-step reasoning using error-correcting codes framework. "
                        f"Topological order: {reasoning_order[:3] if reasoning_order else []}. "
                        f"Information entropy: {info_entropy:.3f}. "
                        f"Constraints: {len(constraints)} equations.",
            "entities": list(entities.keys()),
            "values": all_values
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match of computed answer
            if computed_answer and computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust by confidence
            adjusted_score = base_score * confidence
            
            results.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score,
                "confidence": confidence
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Simple min-max normalization
        scores = [item["score"] for item in scored]
        if scores:
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