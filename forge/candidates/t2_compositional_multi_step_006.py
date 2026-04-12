import re
import zlib
from typing import Dict, List, Any, Optional

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    solve_linear_system,
    topological_sort,
    expected_value
)
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query
from forge.amino_acids.constraint_acids import solve_first


class ReasoningTool:
    """Climate modeling x Bayesian networks - compositional_multi_step"""

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
        """Extract entities, values, and relationships from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find all capitalized multi-word phrases as potential entities
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        entities = {}
        values = []
        
        for line in lines:
            # Extract percentages and numbers
            percentages = re.findall(r'([0-9]+\.?[0-9]*)%', line)
            numbers = re.findall(r'\b([0-9]+\.?[0-9]*)\b', line)
            
            # Extract entity names
            found_entities = re.findall(entity_pattern, line)
            
            for entity in found_entities:
                if entity not in entities:
                    entities[entity] = {"values": [], "mentions": 0}
                entities[entity]["mentions"] += 1
            
            # Store all numeric values
            for pct in percentages:
                values.append(float(pct) / 100.0)
            for num in numbers:
                if '.' in num:
                    values.append(float(num))
                else:
                    values.append(int(num))
        
        # Find relationships (causal/temporal links)
        relationships = []
        causal_words = ["causes", "affects", "influences", "leads to", "results in"]
        for line in lines:
            for word in causal_words:
                if word in line.lower():
                    # Extract entities around causal word
                    parts = line.lower().split(word)
                    if len(parts) >= 2:
                        # Find entities in each part
                        before_entities = re.findall(entity_pattern, parts[0])
                        after_entities = re.findall(entity_pattern, parts[1])
                        if before_entities and after_entities:
                            relationships.append((before_entities[-1], after_entities[0]))
        
        return {
            "entities": entities,
            "values": values,
            "relationships": relationships,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Climate modeling approach: treat multi-step reasoning as energy flow through a system."""
        entities = structure["entities"]
        values = structure["values"]
        relationships = structure["relationships"]
        question = structure["question"]
        
        # Step 1: Build causal network using climate modeling analogy
        # In climate modeling, we track energy flows through interconnected systems
        edges = []
        for rel in relationships:
            if rel[0] in entities and rel[1] in entities:
                edges.append((rel[0], rel[1]))
        
        # Use topological_sort to determine processing order (critical path)
        processing_order = topological_sort(edges)
        if processing_order is None:
            # If cycles exist, use entity mention order
            processing_order = sorted(entities.keys(), 
                                     key=lambda e: entities[e]["mentions"], 
                                     reverse=True)
        
        # Step 2: Bayesian network for uncertainty propagation (climate modeling)
        # Build a simple BN with extracted values as evidence
        computed_answer = None
        confidence = 0.5
        
        if edges and len(values) >= 2:
            try:
                # Create CPDs based on extracted values
                cpd_specs = {}
                for i, node in enumerate(processing_order[:3]):  # Limit to first 3 nodes
                    if i < len(values):
                        # Convert value to probability (climate modeling: normalize to [0,1])
                        prob = min(max(values[i], 0.0), 1.0)
                        cpd_specs[node] = [[prob], [1 - prob]]
                
                # Build Bayesian network
                model = build_bn(edges, cpd_specs)
                
                if model and processing_order:
                    # Query the last node in processing chain
                    target = processing_order[-1]
                    evidence = {}
                    
                    # Set evidence from first node if we have values
                    if processing_order[0] in cpd_specs and values:
                        # Use bayesian_update to refine evidence strength
                        prior = 0.5
                        likelihood = values[0] if values[0] <= 1.0 else values[0] / 100.0
                        updated = bayesian_update(prior, likelihood)
                        if updated is not None:
                            evidence[processing_order[0]] = 1 if updated > 0.5 else 0
                    
                    # Query conditional probability
                    query_result = conditional_query(model, [target], evidence)
                    
                    if query_result is not None and target in query_result:
                        # Determine answer based on query result
                        prob = query_result[target].get(1, 0.0)
                        if prob > 0.5:
                            computed_answer = target
                        else:
                            # Find alternative entity with highest mention count
                            alt_entities = [e for e in entities.keys() if e != target]
                            if alt_entities:
                                computed_answer = max(alt_entities, 
                                                    key=lambda e: entities[e]["mentions"])
                        confidence = prob
            except Exception:
                # Fallback to linear system solving (climate modeling: energy balance equations)
                pass
        
        # Step 3: If BN fails, use linear system solving (energy balance approach)
        if computed_answer is None and len(values) >= 2:
            # Create a simple linear system: A * x = b
            # Climate modeling analogy: energy inputs = energy outputs
            n = min(3, len(values))
            A = []
            b = []
            
            for i in range(n):
                row = [0.0] * n
                row[i] = 1.0
                A.append(row)
                # Normalize values to [0,1] range
                val = values[i] if values[i] <= 1.0 else values[i] / 100.0
                b.append(val)
            
            solution = solve_linear_system(A, b)
            if solution is not None and len(solution) > 0:
                # Use entropy to measure uncertainty in solution
                probs = [abs(s) for s in solution[:3]]
                if probs:
                    total = sum(probs)
                    if total > 0:
                        normalized = [p/total for p in probs]
                        uncertainty = entropy(normalized)
                        
                        # Lower entropy = more certain answer
                        if uncertainty < 0.8 and processing_order:
                            # Select entity with highest probability
                            idx = probs.index(max(probs))
                            if idx < len(processing_order):
                                computed_answer = processing_order[idx]
                                confidence = 1.0 - uncertainty
        
        # Step 4: If still no answer, use constraint solving (climate modeling: constraint satisfaction)
        if computed_answer is None and entities:
            try:
                # Create variables and domains
                variables = list(entities.keys())[:3]  # Limit to first 3 entities
                domains = {var: [0, 1] for var in variables}
                
                # Constraints based on relationships
                constraints = []
                for rel in relationships[:2]:  # Use first 2 relationships
                    if rel[0] in variables and rel[1] in variables:
                        # Constraint: if A causes B, they shouldn't both be 0
                        def causality_constraint(a, b):
                            return not (a == 0 and b == 0)
                        constraints.append(([rel[0], rel[1]], causality_constraint))
                
                if constraints:
                    solution = solve_first(variables, domains, constraints)
                    if solution is not None:
                        # Use expected_value to evaluate solution quality
                        outcomes = []
                        for var, val in solution.items():
                            if var in entities:
                                weight = entities[var]["mentions"] / 10.0
                                outcomes.append((weight, val))
                        
                        if outcomes:
                            ev = expected_value(outcomes)
                            # Select entity with highest value in solution
                            best_var = max(solution.items(), key=lambda x: x[1])[0]
                            computed_answer = best_var
                            confidence = min(abs(ev), 1.0)
            except Exception:
                pass
        
        # Final fallback: use entity with most mentions
        if computed_answer is None and entities:
            computed_answer = max(entities.keys(), 
                                 key=lambda e: entities[e]["mentions"])
            confidence = 0.3
        
        # Calculate final confidence using multiple metrics
        confidence_scores = []
        if 'confidence' in locals():
            confidence_scores.append(confidence)
        
        # Add confidence from agreement if we have multiple scoring methods
        if len(confidence_scores) > 1:
            final_confidence = confidence_from_agreement(confidence_scores)
        elif confidence_scores:
            final_confidence = confidence_scores[0]
        else:
            final_confidence = 0.5
        
        return {
            "answer": str(computed_answer) if computed_answer else "",
            "confidence": final_confidence,
            "reasoning": f"Climate modeling approach: processed {len(processing_order)} nodes in causal chain",
            "entities": list(entities.keys())
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact or substring match
            if computed_answer and computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
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
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        scores = [item["score"] for item in scored]
        if not scores:
            return scored
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score > min_score:
            # Normalize to [0, 1] range
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        else:
            # All scores equal, assign uniform scores
            for item in scored:
                item["score"] = 0.5
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance."""
        if not a or not b:
            return 1.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)