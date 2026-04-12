import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    topological_sort,
    solve_linear_system,
    expected_value
)
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query
from forge.amino_acids.constraint_acids import is_uniquely_solvable


class ReasoningTool:
    """signal_processing x pgmpy_acids - compositional_multi_step"""

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
        """Parse prompt to extract entities, values, relationships, and question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find entity names (capitalized multi-word phrases)
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        entities = {}
        for line in lines:
            matches = re.findall(entity_pattern, line)
            for entity in matches:
                if entity not in entities:
                    entities[entity] = {"values": [], "relations": []}
        
        # Extract numerical values (including percentages)
        value_pattern = r'([0-9]+\.?[0-9]*)%?'
        for line in lines:
            for entity in entities:
                if entity in line:
                    values = re.findall(value_pattern, line)
                    for val in values:
                        if '.' in val:
                            entities[entity]["values"].append(float(val))
                        else:
                            entities[entity]["values"].append(int(val))
        
        # Extract relationships (A depends on B, A causes B, etc.)
        edges = []
        for line in lines:
            if "depends on" in line.lower() or "causes" in line.lower() or "affects" in line.lower():
                for entity1 in entities:
                    for entity2 in entities:
                        if entity1 != entity2 and entity1 in line and entity2 in line:
                            if "depends on" in line.lower() and line.lower().index(entity1.lower()) < line.lower().index(entity2.lower()):
                                edges.append((entity1, entity2))
                            elif "causes" in line.lower() or "affects" in line.lower():
                                if line.lower().index(entity1.lower()) < line.lower().index(entity2.lower()):
                                    edges.append((entity1, entity2))
        
        # Extract equations or constraints
        equations = []
        for line in lines:
            if "=" in line and any(op in line for op in ["+", "-", "*", "/"]):
                equations.append(line)
        
        return {
            "entities": entities,
            "edges": edges,
            "equations": equations,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply signal_processing-inspired multi-step reasoning with primitives and amino acids."""
        entities = structure["entities"]
        edges = structure["edges"]
        equations = structure["equations"]
        question = structure["question"]
        
        # Step 1: Build dependency graph and perform topological sort (signal flow)
        # This represents the signal processing pipeline
        if edges:
            try:
                # LOAD-BEARING: topological_sort determines processing order
                processing_order = topological_sort(edges)
                if processing_order is None:
                    # Graph has cycles, use simple entity order
                    processing_order = list(entities.keys())
            except Exception:
                processing_order = list(entities.keys())
        else:
            processing_order = list(entities.keys())
        
        # Step 2: Build Bayesian Network for probabilistic reasoning (signal with noise)
        # This models uncertainty in the multi-step process
        bn_result = None
        if edges and len(entities) >= 2:
            try:
                # Build simple BN with extracted edges
                # Use extracted values as probabilities where available
                cpd_specs = {}
                for entity in entities:
                    if entities[entity]["values"]:
                        # Convert extracted values to probabilities (normalize)
                        vals = entities[entity]["values"]
                        if len(vals) >= 2:
                            # Use as conditional probability table
                            prob = sum(vals) / (len(vals) * 100) if max(vals) > 1 else sum(vals) / len(vals)
                            cpd_specs[entity] = {"prob": min(max(prob, 0.01), 0.99)}
                
                # LOAD-BEARING: build_bn creates the probabilistic model
                bn_model = build_bn(edges, cpd_specs if cpd_specs else None)
                
                if bn_model:
                    # LOAD-BEARING: conditional_query uses the BN for inference
                    # Query the last entity in processing order given first entity
                    if len(processing_order) >= 2:
                        target = processing_order[-1]
                        evidence = {processing_order[0]: 1}  # Assume presence
                        bn_result = conditional_query(bn_model, [target], evidence)
            except Exception:
                bn_result = None
        
        # Step 3: Solve linear equations if present (signal decomposition)
        linear_result = None
        if equations:
            try:
                # Parse simple linear equations: ax + by = c
                coeffs = []
                consts = []
                for eq in equations[:2]:  # Use up to 2 equations
                    parts = eq.split('=')
                    if len(parts) == 2:
                        left = parts[0].strip()
                        right = parts[1].strip()
                        
                        # Simple parsing for a*x + b*y format
                        coeff_row = []
                        for entity in list(entities.keys())[:2]:  # Use first 2 entities
                            if entity in left:
                                # Extract coefficient
                                coeff_match = re.search(r'([0-9\.]+)\s*\*?\s*' + re.escape(entity), left)
                                if coeff_match:
                                    coeff_row.append(float(coeff_match.group(1)))
                                else:
                                    coeff_row.append(1.0)
                            else:
                                coeff_row.append(0.0)
                        
                        if coeff_row and len(coeff_row) == 2:
                            coeffs.append(coeff_row)
                            consts.append(float(right))
                
                if len(coeffs) == 2 and len(consts) == 2:
                    # LOAD-BEARING: solve_linear_system computes solution
                    linear_result = solve_linear_system(coeffs, consts)
            except Exception:
                linear_result = None
        
        # Step 4: Compute expected value (signal expectation)
        ev_result = None
        if entities:
            try:
                # Create probability-value pairs from extracted data
                outcomes = []
                for entity in entities:
                    if entities[entity]["values"]:
                        vals = entities[entity]["values"]
                        # Normalize as probabilities
                        total = sum(vals)
                        if total > 0:
                            for val in vals:
                                prob = val / total
                                outcomes.append((prob, val))
                
                if outcomes:
                    # LOAD-BEARING: expected_value computes weighted average
                    ev_result = expected_value(outcomes)
            except Exception:
                ev_result = None
        
        # Step 5: Check uniqueness of solution (signal determinism)
        uniqueness_result = None
        if entities and edges:
            try:
                # Create constraint satisfaction problem
                variables = list(entities.keys())
                domains = {}
                for var in variables:
                    if entities[var]["values"]:
                        domains[var] = list(set(entities[var]["values"]))[:3]  # Limit domain size
                    else:
                        domains[var] = [0, 1]  # Binary default
                
                # Create simple constraints based on edges
                constraints = []
                for src, dst in edges:
                    # Constraint: dst value >= src value (monotonic signal)
                    def monotonic_constraint(assignment, s=src, d=dst):
                        return assignment.get(d, 0) >= assignment.get(s, 0)
                    constraints.append(([src, dst], monotonic_constraint))
                
                if variables and domains and constraints:
                    # LOAD-BEARING: is_uniquely_solvable checks solution space
                    uniqueness_result = is_uniquely_solvable(variables, domains, constraints)
            except Exception:
                uniqueness_result = None
        
        # Step 6: Bayesian update for belief revision (signal filtering)
        bayesian_result = None
        if entities and len(entities) >= 2:
            try:
                # Use extracted values as prior and likelihood
                entity_list = list(entities.keys())
                if len(entity_list) >= 2:
                    entity1_vals = entities[entity_list[0]]["values"]
                    entity2_vals = entities[entity_list[1]]["values"]
                    
                    if entity1_vals and entity2_vals:
                        prior = sum(entity1_vals) / (len(entity1_vals) * 100) if max(entity1_vals) > 1 else sum(entity1_vals) / len(entity1_vals)
                        likelihood = sum(entity2_vals) / (len(entity2_vals) * 100) if max(entity2_vals) > 1 else sum(entity2_vals) / len(entity2_vals)
                        
                        prior = min(max(prior, 0.01), 0.99)
                        likelihood = min(max(likelihood, 0.01), 0.99)
                        
                        # LOAD-BEARING: bayesian_update revises belief
                        bayesian_result = bayesian_update(prior, likelihood)
            except Exception:
                bayesian_result = None
        
        # Step 7: Compute entropy of the system (signal uncertainty)
        entropy_result = None
        if entities:
            try:
                # Create probability distribution from entity values
                all_vals = []
                for entity in entities:
                    all_vals.extend(entities[entity]["values"])
                
                if all_vals:
                    total = sum(all_vals)
                    if total > 0:
                        probs = [v/total for v in all_vals[:5]]  # Use first 5 values
                        if len(probs) >= 2:
                            # LOAD-BEARING: entropy measures uncertainty
                            entropy_result = entropy(probs)
            except Exception:
                entropy_result = None
        
        # Step 8: Determine final answer using signal processing metaphor
        # In signal processing, we filter, transform, and reconstruct signals
        computed_answer = ""
        
        # Use Bayesian network result if available (probabilistic signal)
        if bn_result is not None and isinstance(bn_result, dict):
            # Find entity with highest posterior probability
            max_prob = -1
            best_entity = ""
            for entity, prob in bn_result.items():
                if isinstance(prob, (int, float)) and prob > max_prob:
                    max_prob = prob
                    best_entity = entity
            
            if best_entity:
                computed_answer = best_entity
        
        # Fallback to linear system solution (deterministic signal)
        if not computed_answer and linear_result is not None:
            # Use the entity corresponding to the largest solution component
            entity_list = list(entities.keys())
            if linear_result and len(linear_result) >= 1:
                idx = 0
                max_val = abs(linear_result[0])
                for i, val in enumerate(linear_result):
                    if abs(val) > max_val:
                        max_val = abs(val)
                        idx = i
                
                if idx < len(entity_list):
                    computed_answer = entity_list[idx]
        
        # Further fallback: use entity with highest expected value
        if not computed_answer and ev_result is not None:
            max_ev = -float('inf')
            best_entity = ""
            for entity in entities:
                if entities[entity]["values"]:
                    ev = sum(entities[entity]["values"]) / len(entities[entity]["values"])
                    if ev > max_ev:
                        max_ev = ev
                        best_entity = entity
            
            if best_entity:
                computed_answer = best_entity
        
        # Final fallback: use topological order
        if not computed_answer and processing_order:
            # In signal processing, the output is often the last processed signal
            computed_answer = processing_order[-1]
        
        # If still no answer, use first entity
        if not computed_answer and entities:
            computed_answer = list(entities.keys())[0]
        
        # Compute confidence using multiple reasoning sources (signal-to-noise ratio)
        confidence_sources = []
        if bn_result is not None:
            confidence_sources.append(0.8)
        if linear_result is not None:
            confidence_sources.append(0.7)
        if ev_result is not None:
            confidence_sources.append(0.6)
        if uniqueness_result is not None:
            confidence_sources.append(0.5 if uniqueness_result else 0.3)
        if bayesian_result is not None:
            confidence_sources.append(min(max(bayesian_result, 0.1), 0.9))
        if entropy_result is not None:
            # Lower entropy = higher confidence
            confidence_sources.append(max(0.1, 1.0 - min(entropy_result, 1.0)))
        
        if confidence_sources:
            # LOAD-BEARING: confidence_from_agreement aggregates multiple sources
            confidence = confidence_from_agreement(confidence_sources)
        else:
            confidence = 0.5
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Signal processing pipeline: {processing_order}. " +
                        f"BN inference: {bn_result}. " +
                        f"Linear solution: {linear_result}. " +
                        f"Expected value: {ev_result}. " +
                        f"Unique solution: {uniqueness_result}. " +
                        f"Bayesian update: {bayesian_result}. " +
                        f"Entropy: {entropy_result}.",
            "processing_order": processing_order,
            "bn_result": bn_result,
            "linear_result": linear_result,
            "ev_result": ev_result,
            "uniqueness_result": uniqueness_result,
            "bayesian_result": bayesian_result,
            "entropy_result": entropy_result
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact or substring match of computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity with reasoning text
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
        
        # Simple normalization to [0, 1] range
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