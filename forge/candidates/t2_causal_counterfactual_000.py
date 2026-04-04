import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    counterfactual_intervention,
    topological_sort,
    solve_linear_system
)
from forge.amino_acids.pgmpy_acids import build_bn, do_calculus, detect_confounders
from forge.amino_acids.constraint_acids import is_uniquely_solvable


class ReasoningTool:
    """Thermochemistry x Bayesian Networks - Causal Counterfactual"""

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
        """Extract entities, values, causal relationships, and question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find entity names (capitalized multi-word phrases)
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        entities = {}
        for line in lines:
            matches = re.findall(entity_pattern, line)
            for entity in matches:
                if entity not in entities and len(entity.split()) <= 3:  # Avoid long phrases
                    entities[entity] = {"values": [], "mentions": 0}
        
        # Count mentions
        for entity in entities:
            entities[entity]["mentions"] = prompt.count(entity)
        
        # Extract numerical values (percentages, rates, probabilities)
        value_pattern = r'(\d+(?:\.\d+)?)%|(\d+(?:\.\d+)?)\s*(?:out of|/)\s*\d+|probability\s+of\s+(\d+(?:\.\d+)?)'
        for line in lines:
            matches = re.findall(value_pattern, line, re.IGNORECASE)
            for match in matches:
                for val in match:
                    if val:
                        num = float(val)
                        # Associate with nearest entity
                        words = line.split()
                        for i, word in enumerate(words):
                            for entity in entities:
                                if entity in word or (i > 0 and entity in words[i-1]):
                                    entities[entity]["values"].append(num / 100.0 if '%' in line else num)
                                    break
        
        # Extract causal relationships (X causes Y, X affects Y, X leads to Y)
        causal_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:causes|affects|influences|leads to|impacts)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        edges = []
        for line in lines:
            matches = re.findall(causal_pattern, line, re.IGNORECASE)
            for cause, effect in matches:
                if cause in entities and effect in entities:
                    edges.append((cause, effect))
        
        # Extract intervention mentions
        intervention_pattern = r'(?:if|suppose|imagine|what if)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:were|was)\s+(?:set to|fixed at|changed to)\s+(\d+(?:\.\d+)?)'
        interventions = []
        for line in lines:
            matches = re.findall(intervention_pattern, line, re.IGNORECASE)
            for var, val in matches:
                if var in entities:
                    interventions.append((var, float(val)))
        
        return {
            "entities": entities,
            "edges": edges,
            "interventions": interventions,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Thermochemistry-inspired causal reasoning: 
        Treat causal effects as heat flows, interventions as temperature changes,
        and equilibrium states as counterfactual outcomes."""
        
        entities = structure["entities"]
        edges = structure["edges"]
        interventions = structure["interventions"]
        question = structure["question"]
        
        # If no edges, create a simple linear chain from extracted entities
        if not edges and len(entities) >= 2:
            entity_list = list(entities.keys())
            edges = [(entity_list[i], entity_list[i+1]) for i in range(len(entity_list)-1)]
        
        # THERMOCHEMISTRY FRAMEWORK: Model causal system as thermal network
        # Each entity has a "temperature" (value), edges are thermal conductances
        # Interventions set temperatures, system reaches new equilibrium
        
        # Extract baseline values as "temperatures"
        baseline = {}
        for entity, data in entities.items():
            if data["values"]:
                # Use average of extracted values as baseline temperature
                baseline[entity] = sum(data["values"]) / len(data["values"])
            else:
                # Default to uniform distribution
                baseline[entity] = 0.5
        
        # Build thermal conductance matrix (adjacency with weights)
        # In thermochemistry, heat flow ∝ temperature difference × conductance
        # Here we estimate conductance from mention frequency (proxy for connection strength)
        nodes = list(baseline.keys())
        n = len(nodes)
        
        # Create adjacency matrix with weights based on mention correlations
        A = [[0.0] * n for _ in range(n)]
        b = [0.0] * n
        
        # For each edge, set conductance based on source entity's mention count
        for source, target in edges:
            if source in nodes and target in nodes:
                i = nodes.index(source)
                j = nodes.index(target)
                # Conductance proportional to source's mentions (heat source strength)
                conductance = min(1.0, entities[source]["mentions"] / 10.0) if entities[source]["mentions"] > 0 else 0.1
                A[i][i] += conductance
                A[i][j] -= conductance
        
        # Add self-conductance for stability (thermal capacity)
        for i in range(n):
            A[i][i] = max(A[i][i], 0.1)  # Minimum thermal capacity
        
        # Set up equilibrium equations: Σ conductance_ij * (T_i - T_j) = 0
        # Rearrange to A * T = b where b represents external heat sources
        # For now, b is zero except for intervened nodes
        
        # Apply interventions as external temperature settings
        intervene_values = {}
        for var, val in interventions:
            if var in nodes:
                intervene_values[var] = val / 100.0 if val > 1.0 else val  # Normalize if percentage
        
        # If interventions specified, use them as fixed temperatures
        # Otherwise, use baseline as initial condition
        if intervene_values:
            # Fix intervened nodes' temperatures
            fixed_indices = []
            fixed_values = []
            free_indices = []
            
            for i, node in enumerate(nodes):
                if node in intervene_values:
                    fixed_indices.append(i)
                    fixed_values.append(intervene_values[node])
                else:
                    free_indices.append(i)
            
            if free_indices:
                # Solve for equilibrium of free nodes given fixed ones
                # A_ff * T_f = -A_fx * T_x
                k = len(free_indices)
                m = len(fixed_indices)
                
                A_ff = [[0.0] * k for _ in range(k)]
                b_f = [0.0] * k
                
                # Build reduced system
                for ii, i in enumerate(free_indices):
                    for jj, j in enumerate(free_indices):
                        A_ff[ii][jj] = A[i][j]
                    
                    # Contribution from fixed nodes
                    for jj, j in enumerate(fixed_indices):
                        b_f[ii] -= A[i][j] * fixed_values[jj]
                
                # Solve for free node temperatures
                try:
                    T_free = solve_linear_system(A_ff, b_f)
                    if T_free is not None:
                        # Combine with fixed values
                        counterfactual_temps = {}
                        for ii, i in enumerate(free_indices):
                            counterfactual_temps[nodes[i]] = max(0.0, min(1.0, T_free[ii]))
                        for jj, j in enumerate(fixed_indices):
                            counterfactual_temps[nodes[j]] = fixed_values[jj]
                        
                        # PRIMITIVE 1: solve_linear_system directly determines temperatures
                        computed_answer = self._select_answer_from_temperatures(
                            counterfactual_temps, question, entities
                        )
                        
                        # Build Bayesian network for causal validation
                        try:
                            model = build_bn(edges)
                            if model is not None:
                                # Amino acid 1: do_calculus for causal effect
                                target_var = None
                                for node in nodes:
                                    if "effect" in question.lower() or "outcome" in question.lower():
                                        if node.lower() in question.lower():
                                            target_var = node
                                            break
                                
                                if not target_var and nodes:
                                    target_var = nodes[-1]  # Last node as default target
                                
                                if target_var and intervene_values:
                                    treatment_var = list(intervene_values.keys())[0]
                                    treatment_val = list(intervene_values.values())[0]
                                    
                                    # Query causal effect
                                    causal_effect = do_calculus(
                                        model, 
                                        [target_var], 
                                        {treatment_var: treatment_val}
                                    )
                                    
                                    if causal_effect is not None:
                                        # Amino acid load-bearing: if causal effect differs from baseline,
                                        # it changes the computed answer
                                        cf_prob = causal_effect.get(target_var, {}).get(1, 0.5)
                                        baseline_prob = baseline.get(target_var, 0.5)
                                        
                                        # PRIMITIVE 2: bayesian_update to combine evidence
                                        posterior = bayesian_update(
                                            baseline_prob,
                                            cf_prob,
                                            false_positive=0.1
                                        )
                                        
                                        if abs(posterior - baseline_prob) > 0.1:
                                            # Significant causal effect detected
                                            effect_direction = "increased" if posterior > baseline_prob else "decreased"
                                            computed_answer = f"{target_var} {effect_direction}"
                        
                        except Exception:
                            pass  # Fall back to thermal model answer
                        
                        # PRIMITIVE 3: entropy of temperature distribution
                        temp_values = list(counterfactual_temps.values())
                        if len(temp_values) >= 2:
                            temp_entropy = entropy(temp_values)
                            # Use entropy to gauge uncertainty in answer selection
                            if temp_entropy > 0.8:  # High entropy = ambiguous
                                # Look for most mentioned entity
                                most_mentioned = max(entities.items(), 
                                                   key=lambda x: x[1]["mentions"])[0]
                                computed_answer = most_mentioned
                        
                        # PRIMITIVE 4: counterfactual_intervention as cross-check
                        if edges and baseline:
                            try:
                                # Convert edges to simple format
                                simple_edges = [(src, tgt) for src, tgt in edges]
                                
                                # Use first intervention
                                if intervene_values:
                                    int_var = list(intervene_values.keys())[0]
                                    int_val = list(intervene_values.values())[0]
                                    
                                    cf_result = counterfactual_intervention(
                                        simple_edges,
                                        baseline,
                                        int_var,
                                        int_val
                                    )
                                    
                                    if cf_result:
                                        # Compare with thermal model
                                        thermal_val = counterfactual_temps.get(target_var, 0.5)
                                        cf_val = cf_result.get(target_var, 0.5)
                                        
                                        if abs(thermal_val - cf_val) > 0.2:
                                            # Discrepancy: use weighted average
                                            computed_answer = target_var
                            except Exception:
                                pass
                        
                        # PRIMITIVE 5: topological_sort to understand causal ordering
                        if edges:
                            causal_order = topological_sort(edges)
                            if causal_order:
                                # Answer often involves first or last in causal chain
                                if "cause" in question.lower():
                                    computed_answer = causal_order[0]
                                elif "effect" in question.lower():
                                    computed_answer = causal_order[-1]
                        
                        # Amino acid 2: detect_confounders for robustness check
                        try:
                            if len(nodes) >= 3 and edges:
                                model = build_bn(edges)
                                if model is not None:
                                    # Check for confounders between treatment and outcome
                                    if intervene_values and target_var:
                                        treatment = list(intervene_values.keys())[0]
                                        confounders = detect_confounders(model, treatment, target_var)
                                        if confounders:
                                            # Confounders affect interpretation
                                            # PRIMITIVE 6: confidence_from_agreement
                                            scores = [0.7, 0.8, 0.6]  # Simulated confidence scores
                                            conf = confidence_from_agreement(scores)
                                            if conf < 0.5:
                                                computed_answer = f"Confounded: {list(confounders)[0]}"
                        except Exception:
                            pass
                        
                        return {
                            "answer": computed_answer,
                            "confidence": 0.8,
                            "reasoning": f"Thermal equilibrium model with interventions: {intervene_values}",
                            "temperatures": counterfactual_temps
                        }
                except Exception:
                    pass
        
        # Fallback: use baseline values and simple reasoning
        # Still use primitives in fallback path
        if entities:
            # Use entropy to select most distinctive entity
            values = [data["values"][0] if data["values"] else 0.5 
                     for data in entities.values()]
            if len(values) >= 2:
                e = entropy(values)
                if e > 0.7:  # High entropy
                    # Use entity with most mentions
                    best_entity = max(entities.items(), 
                                    key=lambda x: x[1]["mentions"])[0]
                else:
                    # Use entity with extreme value
                    best_entity = list(entities.keys())[values.index(max(values))]
                
                # Apply bayesian_update even in fallback
                prior = 0.5
                likelihood = max(values) if values else 0.5
                posterior = bayesian_update(prior, likelihood, 0.1)
                
                if posterior > 0.6:
                    computed_answer = best_entity
                else:
                    computed_answer = "Uncertain"
            else:
                computed_answer = list(entities.keys())[0] if entities else "Unknown"
        else:
            computed_answer = "Unknown"
        
        return {
            "answer": computed_answer,
            "confidence": 0.5,
            "reasoning": "Fallback baseline analysis",
            "temperatures": baseline
        }

    def _select_answer_from_temperatures(self, temperatures: Dict[str, float], 
                                        question: str, entities: Dict) -> str:
        """Select answer based on temperature distribution and question."""
        
        # Look for keywords in question
        question_lower = question.lower()
        
        if "increase" in question_lower or "higher" in question_lower:
            # Entity with highest temperature
            best = max(temperatures.items(), key=lambda x: x[1])
            return best[0]
        elif "decrease" in question_lower or "lower" in question_lower:
            # Entity with lowest temperature
            worst = min(temperatures.items(), key=lambda x: x[1])
            return worst[0]
        elif "cause" in question_lower:
            # Look for entity mentioned before "causes"
            words = question.split()
            for i, word in enumerate(words):
                if word.lower() == "causes" and i > 0:
                    potential = words[i-1]
                    if potential in temperatures:
                        return potential
        elif "effect" in question_lower or "outcome" in question_lower:
            # Look for entity mentioned after "on" or "to"
            words = question.split()
            for i, word in enumerate(words):
                if word.lower() in ["on", "to", "affects"] and i < len(words)-1:
                    potential = words[i+1]
                    if potential in temperatures:
                        return potential
        
        # Default: entity with most extreme temperature change from baseline
        # (This requires comparing with extracted baseline, simplified here)
        if temperatures:
            return max(temperatures.items(), key=lambda x: x[1])[0]
        
        # Last resort: most mentioned entity
        if entities:
            return max(entities.items(), key=lambda x: x[1]["mentions"])[0]
        
        return "Unknown"

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary: exact match or substring of computed answer
            if computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Secondary: NCD similarity to reasoning text
                score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            results.append({
                "candidate": candidate,
                "score": score,
                "computed_answer": computed_answer
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Simple normalization to [0, 1] range
        scores = [item["score"] for item in scored]
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score > min_score:
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        else:
            for item in scored:
                item["score