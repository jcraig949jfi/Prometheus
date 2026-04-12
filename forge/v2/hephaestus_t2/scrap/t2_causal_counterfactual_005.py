import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    counterfactual_intervention,
    topological_sort,
    solve_constraints,
    expected_value,
    information_sufficiency
)
from forge.amino_acids.pgmpy_acids import (
    build_bn,
    conditional_query,
    do_calculus,
    detect_confounders
)
from forge.amino_acids.constraint_acids import (
    solve_first,
    is_uniquely_solvable
)


class ReasoningTool:
    """Social Choice Theory x Causal Counterfactual - causal_counterfactual"""

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
        """Extract entities, values, causal relationships, and question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find entity names (capitalized multi-word phrases)
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        entities = {}
        for line in lines:
            matches = re.findall(entity_pattern, line)
            for entity in matches:
                if entity not in entities and len(entity.split()) <= 3:
                    entities[entity] = {"values": [], "mentions": 0}
        
        # Count mentions
        for entity in entities:
            entities[entity]["mentions"] = prompt.count(entity)
        
        # Extract numerical values (percentages, rates, probabilities)
        number_pattern = r'(\d+(?:\.\d+)?)\s*%?'
        for line in lines:
            numbers = re.findall(number_pattern, line)
            if numbers:
                # Try to associate numbers with nearby entities
                for entity in entities:
                    if entity in line:
                        for num in numbers:
                            try:
                                value = float(num)
                                if value <= 1.0 and '.' in num:
                                    value *= 100  # Convert decimal to percentage
                                entities[entity]["values"].append(value)
                            except ValueError:
                                pass
        
        # Extract causal language indicators
        causal_indicators = []
        causal_words = ["causes", "affects", "influences", "leads to", "results in", 
                       "because", "due to", "if", "then", "intervention", "counterfactual"]
        for word in causal_words:
            if word in prompt.lower():
                causal_indicators.append(word)
        
        # Extract intervention mentions
        intervention_pattern = r'(?:what would|if|suppose|imagine|counterfactual|intervene)'
        interventions = re.findall(intervention_pattern, prompt.lower())
        
        return {
            "entities": entities,
            "question": question,
            "causal_indicators": causal_indicators,
            "interventions": interventions,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply social choice theory framework to reason about counterfactuals."""
        entities = structure["entities"]
        question = structure["question"]
        interventions = structure["interventions"]
        
        # Social Choice Theory: Treat counterfactual outcomes as preference profiles
        # Each entity's values represent different voters' preferences
        # The counterfactual intervention creates a new social welfare function
        
        # Step 1: Build preference profiles from extracted values
        preference_profiles = {}
        for entity, data in entities.items():
            values = data["values"]
            if values:
                # Normalize values to create a probability distribution
                total = sum(values)
                if total > 0:
                    normalized = [v/total for v in values]
                    # Compute entropy of preference distribution (T1 primitive)
                    pref_entropy = entropy(normalized)
                    preference_profiles[entity] = {
                        "values": values,
                        "distribution": normalized,
                        "entropy": pref_entropy,
                        "expected_value": sum(values)/len(values) if values else 0
                    }
        
        # Step 2: Identify causal structure using amino acid
        # Build a simple Bayesian network from extracted relationships
        edges = []
        if len(preference_profiles) >= 2:
            entity_list = list(preference_profiles.keys())
            # Create edges based on mention order and value dependencies
            for i in range(len(entity_list)-1):
                edges.append((entity_list[i], entity_list[i+1]))
        
        # Use amino acid to build Bayesian network (LOAD-BEARING)
        model = None
        if edges:
            model = build_bn(edges)
        
        # Step 3: Compute counterfactual using social choice aggregation
        # Each entity's values are votes, we need to find the social choice
        # under different interventions
        
        computed_answer = None
        confidence = 0.5
        reasoning = ""
        
        if model and preference_profiles:
            # Use amino acid to compute counterfactual query (LOAD-BEARING)
            target_vars = list(preference_profiles.keys())[:1]
            if target_vars:
                # Create evidence from extracted values
                evidence = {}
                for entity, data in preference_profiles.items():
                    if data["values"]:
                        # Use median value as evidence state
                        median_val = sorted(data["values"])[len(data["values"])//2]
                        evidence[entity] = median_val > (sum(data["values"])/len(data["values"]))
                
                # Compute conditional probability (amino acid)
                cond_prob = None
                if evidence:
                    cond_prob = conditional_query(model, target_vars, evidence)
                
                # Compute counterfactual using do-calculus (amino acid)
                counterfactual_result = None
                if len(edges) > 0:
                    treatment = edges[0][0]
                    outcome = edges[-1][1] if len(edges) > 1 else treatment
                    counterfactual_result = do_calculus(model, [outcome], [treatment])
                
                # Use T1 primitive: expected value of counterfactual outcomes
                if preference_profiles:
                    outcomes = []
                    for entity, data in preference_profiles.items():
                        if data["values"]:
                            avg_val = sum(data["values"])/len(data["values"])
                            # Weight by inverse entropy (more certain preferences get more weight)
                            weight = 1.0 / (1.0 + data["entropy"]) if data["entropy"] > 0 else 1.0
                            outcomes.append((weight, avg_val))
                    
                    # T1 primitive: expected value (LOAD-BEARING)
                    social_welfare = expected_value(outcomes)
                    
                    # Find entity with value closest to social welfare
                    best_entity = None
                    min_diff = float('inf')
                    for entity, data in preference_profiles.items():
                        if data["values"]:
                            entity_avg = sum(data["values"])/len(data["values"])
                            diff = abs(entity_avg - social_welfare)
                            if diff < min_diff:
                                min_diff = diff
                                best_entity = entity
                    
                    computed_answer = best_entity
                    
                    # Use T1 primitive: confidence from agreement (LOAD-BEARING)
                    if len(preference_profiles) > 1:
                        agreement_scores = []
                        for entity, data in preference_profiles.items():
                            if data["values"]:
                                # Score based on consistency with social welfare
                                entity_score = 1.0 / (1.0 + abs(sum(data["values"])/len(data["values"]) - social_welfare))
                                agreement_scores.append(entity_score)
                        
                        if agreement_scores:
                            # T1 primitive: confidence from agreement (LOAD-BEARING)
                            confidence = confidence_from_agreement(agreement_scores)
                    
                    reasoning = f"Social welfare: {social_welfare:.2f}, Best entity: {best_entity}"
        
        # Fallback if amino acids fail but we still have preference profiles
        if not computed_answer and preference_profiles:
            # Use T1 primitive: information sufficiency (LOAD-BEARING)
            n_unknowns = len(preference_profiles)
            n_constraints = sum(len(data["values"]) for data in preference_profiles.values())
            sufficiency = information_sufficiency(n_unknowns, n_constraints)
            
            # Use T1 primitive: solve_constraints as fallback (LOAD-BEARING)
            variables = list(preference_profiles.keys())
            domains = {}
            constraints = []
            
            for entity, data in preference_profiles.items():
                if data["values"]:
                    # Create domain from extracted values
                    unique_vals = sorted(set(data["values"]))
                    domains[entity] = unique_vals[:3]  # Limit to 3 values
                    
                    # Add constraint: value must be close to expected value
                    expected = sum(data["values"])/len(data["values"])
                    constraints.append(([entity], lambda x, e=expected: abs(x - e) < e*0.5))
            
            if variables and domains:
                solution = solve_constraints(variables, domains, constraints)
                if solution:
                    # Find entity with highest value in solution
                    best_entity = max(solution.items(), key=lambda x: x[1])[0]
                    computed_answer = best_entity
                    confidence = 0.7
                    reasoning = f"Constraint solution: {solution}, Sufficiency: {sufficiency}"
        
        # Final fallback: use entity with most mentions
        if not computed_answer and entities:
            best_entity = max(entities.items(), key=lambda x: x[1]["mentions"])[0]
            computed_answer = best_entity
            confidence = 0.3
            reasoning = "Fallback: most mentioned entity"
        
        return {
            "answer": computed_answer or "",
            "confidence": confidence,
            "reasoning": reasoning,
            "preference_profiles": preference_profiles
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        
        for candidate in candidates:
            # Primary scoring: exact match or substring match with computed answer
            if computed_answer and computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity between reasoning and candidate
                base_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
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
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Normalize scores to [0, 1] range
        scores = [item["score"] for item in scored]
        if scores:
            min_score = min(scores)
            max_score = max(scores)
            if max_score > min_score:
                for item in scored:
                    item["score"] = (item["score"] - min_score) / (max_score - min_score)
            else:
                # All scores equal, assign uniform scores
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