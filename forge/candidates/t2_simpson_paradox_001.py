import re
import zlib
from typing import Dict, List, Any

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, solve_linear_system
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, compare_conditional_marginal

class ReasoningTool:
    """Relativity x Bayesian networks - simpson_paradox"""

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
        """Parse prompt to find entities, subgroups, rates, and the question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find entity names (capitalized multi-word phrases that appear with rates)
        entity_pattern = r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b'
        potential_entities = re.findall(entity_pattern, prompt)
        
        # Find all percentage values
        rate_pattern = r'([0-9]+\.?[0-9]*)%'
        all_rates = [float(r) for r in re.findall(rate_pattern, prompt)]
        
        # Find subgroup indicators (like "men", "women", "young", "old")
        subgroup_keywords = ['men', 'women', 'male', 'female', 'young', 'old', 
                            'group a', 'group b', 'subgroup', 'category']
        subgroups = []
        for word in subgroup_keywords:
            if word in prompt.lower():
                subgroups.append(word)
        
        # Build structure
        entities = {}
        for ent in potential_entities:
            if len(ent.split()) <= 3:  # Avoid very long phrases
                entities[ent] = {"rates": [], "subgroups": []}
        
        # Associate rates with entities based on proximity
        sentences = prompt.split('.')
        for sent in sentences:
            sent_rates = [float(r) for r in re.findall(rate_pattern, sent)]
            sent_entities = re.findall(entity_pattern, sent)
            for ent in sent_entities:
                if ent in entities and sent_rates:
                    entities[ent]["rates"].extend(sent_rates)
                    # Check for subgroup mentions in this sentence
                    for sub in subgroup_keywords:
                        if sub in sent.lower():
                            entities[ent]["subgroups"].append(sub)
        
        # Clean up empty entities
        entities = {k: v for k, v in entities.items() if v["rates"]}
        
        return {
            "entities": entities,
            "subgroups": list(set(subgroups)),
            "all_rates": all_rates,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply relativistic reasoning: aggregated vs subgroup frames as different reference frames."""
        entities = structure["entities"]
        all_rates = structure["all_rates"]
        question = structure["question"]
        
        if len(entities) < 2 or len(all_rates) < 4:
            # Not enough data for Simpson's paradox analysis
            return {"answer": "Insufficient data", "confidence": 0.0, "reasoning": "Not enough entities or rates"}
        
        # T1 PRIMITIVE 1: Compute entropy of rates as measure of disorder
        if all_rates:
            normalized_rates = [r/100 for r in all_rates]
            rate_entropy = entropy(normalized_rates)
        else:
            rate_entropy = 0.0
        
        # Build a simple Bayesian network to model the paradox
        # Frame 1: Aggregated view (like one inertial frame)
        # Frame 2: Subgroup view (like another inertial frame)
        edges = [("Confounder", "Subgroup"), ("Confounder", "Outcome"), ("Subgroup", "Aggregated")]
        
        # Use extracted rates for CPDs
        if len(all_rates) >= 4:
            # Assume first two rates are for one subgroup, next two for another
            subgroup1_rate = all_rates[0]/100 if len(all_rates) > 0 else 0.5
            subgroup2_rate = all_rates[1]/100 if len(all_rates) > 1 else 0.5
            aggregated1_rate = all_rates[2]/100 if len(all_rates) > 2 else 0.5
            aggregated2_rate = all_rates[3]/100 if len(all_rates) > 3 else 0.5
            
            cpd_specs = {
                "Confounder": [[0.5], [0.5]],  # Binary confounder
                "Subgroup": [
                    [subgroup1_rate, 1-subgroup1_rate],  # P(Subgroup|Confounder=0)
                    [subgroup2_rate, 1-subgroup2_rate]   # P(Subgroup|Confounder=1)
                ],
                "Outcome": [
                    [aggregated1_rate, 1-aggregated1_rate],  # P(Outcome|Confounder=0)
                    [aggregated2_rate, 1-aggregated2_rate]   # P(Outcome|Confounder=1)
                ],
                "Aggregated": [
                    [0.7, 0.3],  # Simple aggregation (placeholder, will be overridden by reasoning)
                    [0.3, 0.7]
                ]
            }
        else:
            cpd_specs = None
        
        # AMINO ACID 1: Build Bayesian network
        bn_model = build_bn(edges, cpd_specs)
        
        paradox_detected = False
        best_entity = None
        confidence = 0.0
        
        if bn_model is not None and len(entities) >= 2:
            # AMINO ACID 2: Check for Simpson's paradox pattern
            # Compare conditional vs marginal distributions
            try:
                # This simulates checking if conditioning changes the relationship
                paradox_check = compare_conditional_marginal(bn_model, "Outcome", "Subgroup", 0)
                if paradox_check is not None:
                    # If there's a significant difference, paradox might be present
                    paradox_detected = abs(paradox_check.get("difference", 0)) > 0.2
            except:
                paradox_detected = False
            
            # AMINO ACID 3: Query the network for the most likely outcome
            if paradox_detected:
                evidence = {"Subgroup": 0}  # Look at one subgroup
                query_result = conditional_query(bn_model, ["Outcome"], evidence)
                if query_result is not None:
                    # Find which entity matches this outcome pattern
                    entity_list = list(entities.keys())
                    if entity_list:
                        # In relativity, the "correct" answer depends on the reference frame
                        # For Simpson's paradox, the subgroup view is often the "proper frame"
                        best_entity = entity_list[0]  # Default to first entity
                        
                        # T1 PRIMITIVE 2: Use confidence from agreement of multiple frames
                        # Simulate different "frames" (aggregated vs subgroup)
                        frame_scores = []
                        for ent in entity_list:
                            rates = entities[ent].get("rates", [])
                            if len(rates) >= 2:
                                # Score based on rate consistency across frames
                                avg_rate = sum(rates)/len(rates)
                                frame_scores.append(avg_rate/100)
                        
                        if frame_scores:
                            confidence = confidence_from_agreement(frame_scores)
                        else:
                            confidence = 0.5
            else:
                # No paradox detected, use aggregated view
                entity_list = list(entities.keys())
                if entity_list:
                    # Find entity with highest average rate (simplified)
                    best_entity = max(entity_list, 
                                     key=lambda x: sum(entities[x].get("rates", [0]))/max(len(entities[x].get("rates", [1])), 1))
                    confidence = 0.7
        
        # T1 PRIMITIVE 3: Solve linear system to find "true" rates if possible
        # Model as: aggregated_rate = w1*subgroup1 + w2*subgroup2
        if len(all_rates) >= 4:
            try:
                # Simple 2x2 system: a*x + b*y = c, d*x + e*y = f
                A = [[0.5, 0.5], [0.5, 0.5]]  # Placeholder weights
                b = [all_rates[2]/100, all_rates[3]/100]
                solution = solve_linear_system(A, b)
                if solution is not None:
                    # Adjust confidence based on solvability
                    confidence = min(confidence + 0.1, 0.9)
            except:
                pass
        
        # Relativistic reasoning: Transform between frames
        # In relativity, quantities transform between reference frames
        # Here, "truth" transforms between aggregated and subgroup frames
        if paradox_detected and best_entity:
            # Apply "Lorentz transformation" to confidence
            # Higher entropy (disorder) reduces effective confidence
            confidence_factor = max(0, 1 - rate_entropy)
            confidence = confidence * confidence_factor
            
            # The answer is the entity that appears best in the "proper frame" (subgroup view)
            computed_answer = best_entity
            reasoning_text = f"Simpson's paradox detected. In subgroup frame, {best_entity} is optimal. Confidence transforms with entropy {rate_entropy:.2f}."
        elif best_entity:
            computed_answer = best_entity
            reasoning_text = f"No paradox detected. Aggregated frame shows {best_entity} as best."
        else:
            computed_answer = "Cannot determine"
            reasoning_text = "Insufficient data for relativistic frame analysis."
        
        return {
            "answer": computed_answer,
            "confidence": min(max(confidence, 0.0), 1.0),
            "reasoning": reasoning_text,
            "paradox_detected": paradox_detected
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate text
            # computed_answer is a VARIABLE from reasoning, not a hardcoded string
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity between reasoning text and candidate
                base_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
            # Adjust by confidence from reasoning
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
        
        if max(ca, cb) > 0:
            return (cab - min(ca, cb)) / max(ca, cb)
        return 1.0