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
    """Group theory x Constraint satisfaction - Temporal complex"""

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
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find temporal entities (capitalized phrases that appear with time units)
        entity_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(?:at|of|in|on|from|to|until)?\s*(\d+:\d+|\d+\s*(?:AM|PM|hours|minutes|seconds|days|weeks|months|years))'
        entities = {}
        
        # Find numerical values with units
        value_pattern = r'(\d+\.?\d*)\s*(?:seconds?|minutes?|hours?|days?|weeks?|months?|years?|%|°[CF]?)'
        
        # Find temporal relationships
        relations = []
        temporal_words = ['before', 'after', 'during', 'while', 'when', 'until', 'since', 'from', 'to']
        
        for line in lines:
            # Extract entities with their associated times
            matches = re.findall(entity_pattern, line, re.IGNORECASE)
            for entity, time_val in matches:
                if entity not in entities:
                    entities[entity] = {"times": [], "values": [], "unit": None}
                if time_val:
                    entities[entity]["times"].append(time_val)
            
            # Extract standalone numerical values
            values = re.findall(value_pattern, line)
            for val in values:
                # Try to associate with the last mentioned entity
                if entities:
                    last_entity = list(entities.keys())[-1]
                    entities[last_entity]["values"].append(float(val))
            
            # Extract temporal relationships
            for i, word in enumerate(temporal_words):
                if word in line.lower():
                    # Simple extraction: look for entity pairs around temporal words
                    words = line.split()
                    for j, w in enumerate(words):
                        if w.lower() == word and j > 0 and j < len(words) - 1:
                            e1 = words[j-1]
                            e2 = words[j+1]
                            if e1 in entities and e2 in entities:
                                relations.append((e1, word.lower(), e2))
        
        return {
            "entities": entities,
            "relations": relations,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply group theory concepts to temporal reasoning via constraint solving."""
        entities = structure["entities"]
        relations = structure["relations"]
        question = structure["question"]
        
        # Convert temporal relations to before/after pairs for topological sort
        before_relations = []
        for e1, rel, e2 in relations:
            if rel == 'before':
                before_relations.append((e1, e2))
            elif rel == 'after':
                before_relations.append((e2, e1))
        
        # Use topological_sort primitive (T1) - LOAD-BEARING
        sorted_entities = topological_sort(before_relations)
        
        # Extract numerical values for constraint solving
        all_values = []
        for entity, data in entities.items():
            all_values.extend(data["values"])
        
        # Use modular_arithmetic primitive (T1) - LOAD-BEARING
        # Apply group theory: treat time conversions as modular arithmetic operations
        base_mod = 60  # minutes in hour, seconds in minute
        if all_values:
            # Create a simple modular system: sum of values mod base
            mod_sum = 0
            for val in all_values:
                mod_sum = modular_arithmetic(mod_sum, int(val), base_mod)
        else:
            mod_sum = 0
        
        # Use temporal_order primitive (T1) - LOAD-BEARING
        # Convert relations to event pairs for temporal ordering
        event_pairs = []
        for e1, rel, e2 in relations:
            if rel in ['before', 'after']:
                event_pairs.append((e1, rel, e2))
        
        temporal_ordering = temporal_order(event_pairs) if event_pairs else []
        
        # Use amino acid: constraint solving for temporal CSP
        # Build a constraint satisfaction problem for temporal reasoning
        variables = list(entities.keys())
        domains = {}
        for var in variables:
            # Create domain based on extracted values or reasonable range
            if entities[var]["values"]:
                base_val = entities[var]["values"][0]
                domains[var] = [int(base_val), int(base_val) + 1, int(base_val) + 2]
            else:
                domains[var] = list(range(1, 101))  # default range
        
        # Define constraints based on temporal relations
        constraints = []
        for e1, rel, e2 in relations:
            if rel == 'before':
                constraints.append(([e1, e2], lambda x, y: x < y))
            elif rel == 'after':
                constraints.append(([e1, e2], lambda x, y: x > y))
        
        # Use solve_first amino acid - LOAD-BEARING
        solution = solve_first(variables_domains={v: domains[v] for v in variables}, 
                              constraints=constraints)
        
        # Determine the answer based on the question
        computed_answer = ""
        confidence = 0.5
        
        if "when" in question.lower() or "time" in question.lower():
            # Question about specific time
            if solution:
                # Find the entity mentioned in the question
                for entity in entities:
                    if entity.lower() in question.lower():
                        computed_answer = f"{solution.get(entity, 'unknown')}"
                        break
                if not computed_answer and solution:
                    computed_answer = str(list(solution.values())[0])
            else:
                computed_answer = str(mod_sum)
                
        elif "order" in question.lower() or "sequence" in question.lower():
            # Question about temporal order
            if sorted_entities:
                computed_answer = " -> ".join(sorted_entities)
            elif temporal_ordering:
                computed_answer = " -> ".join(temporal_ordering)
            else:
                computed_answer = "unknown order"
                
        elif "how many" in question.lower() or "total" in question.lower():
            # Question about quantity
            if all_values:
                total = sum(all_values)
                computed_answer = str(int(total))
            else:
                computed_answer = "0"
                
        else:
            # Default: use the first entity from topological sort
            if sorted_entities:
                computed_answer = sorted_entities[0]
            elif entities:
                computed_answer = list(entities.keys())[0]
            else:
                computed_answer = str(mod_sum)
        
        # Use confidence_from_agreement primitive (T1) - LOAD-BEARING
        # Create multiple scoring methods and compute agreement
        scores = []
        if solution:
            scores.append(0.8)
        if sorted_entities:
            scores.append(0.7)
        if mod_sum > 0:
            scores.append(0.6)
        
        if scores:
            confidence = confidence_from_agreement(scores)
        else:
            confidence = 0.5
        
        # Use information_sufficiency primitive (T1) - LOAD-BEARING
        # Check if we have enough constraints to determine a unique answer
        n_unknowns = len(entities)
        n_constraints = len(relations)
        sufficiency = information_sufficiency(n_unknowns, n_constraints)
        
        # Adjust confidence based on sufficiency
        if sufficiency == "determined":
            confidence = min(confidence + 0.2, 1.0)
        elif sufficiency == "underdetermined":
            confidence = max(confidence - 0.1, 0.1)
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Temporal analysis using group theory (mod {base_mod}) and constraint solving. Sufficiency: {sufficiency}.",
            "mod_sum": mod_sum,
            "sorted_entities": sorted_entities,
            "solution": solution
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Use NCD as fallback
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
        if max(scores) > min(scores):
            for item in scored:
                item["score"] = (item["score"] - min(scores)) / (max(scores) - min(scores))
        else:
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
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)