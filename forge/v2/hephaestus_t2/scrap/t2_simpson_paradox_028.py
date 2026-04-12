import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, topological_sort
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, compare_conditional_marginal


class ReasoningTool:
    """Electromagnetism x Bayesian networks - Simpson's paradox detection"""

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
        """Parse prompt to extract entities, rates, and question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find all percentage values
        percentages = []
        for line in lines:
            matches = re.findall(r'(\d+(?:\.\d+)?)%', line)
            percentages.extend([float(m) / 100.0 for m in matches])
        
        # Find entity names (capitalized multi-word phrases)
        entities = {}
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        
        for line in lines:
            matches = re.findall(entity_pattern, line)
            for match in matches:
                if match not in entities and len(match.split()) <= 3:  # Filter out long phrases
                    entities[match] = {"mentions": 0, "rates": []}
        
        # Associate rates with entities based on proximity
        for line in lines:
            line_rates = re.findall(r'(\d+(?:\.\d+)?)%', line)
            line_rates = [float(r) / 100.0 for r in line_rates]
            line_entities = re.findall(entity_pattern, line)
            
            for entity in line_entities:
                if entity in entities:
                    entities[entity]["mentions"] += 1
                    if line_rates:
                        entities[entity]["rates"].extend(line_rates)
        
        # Clean up: remove entities with no rates
        entities = {k: v for k, v in entities.items() if v["rates"]}
        
        # Find subgroup indicators (like "men", "women", "young", "old")
        subgroups = []
        subgroup_keywords = ["men", "women", "male", "female", "young", "old", "children", 
                           "adults", "group a", "group b", "category"]
        for line in lines:
            for keyword in subgroup_keywords:
                if keyword in line.lower():
                    subgroups.append(keyword)
        
        return {
            "entities": entities,
            "percentages": percentages,
            "question": question,
            "subgroups": list(set(subgroups)),
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use electromagnetism-inspired Bayesian analysis to detect Simpson's paradox."""
        entities = structure["entities"]
        percentages = structure["percentages"]
        subgroups = structure["subgroups"]
        
        if len(entities) < 2 or len(percentages) < 4:
            # Fallback: simple comparison if insufficient data
            computed_answer = self._fallback_reasoning(entities, percentages)
            return {
                "answer": computed_answer,
                "confidence": 0.5,
                "reasoning": "Insufficient data for full analysis",
                "paradox_detected": False
            }
        
        # ELECTROMAGNETISM FRAMEWORK:
        # - Entities are like charged particles
        # - Rates create electric fields
        # - Subgroups create magnetic fields that can reverse direction
        # - Bayesian network is the field configuration
        
        # Build causal graph: Subgroup -> Entity -> Outcome
        edges = []
        if subgroups:
            for subgroup in subgroups[:2]:  # Use up to 2 subgroups
                for entity in list(entities.keys())[:2]:  # Use up to 2 entities
                    edges.append((subgroup, entity))
                    edges.append((entity, "outcome"))
        else:
            # If no subgroups mentioned, create synthetic ones
            edges = [("entity_a", "outcome"), ("entity_b", "outcome")]
        
        # Create CPDs using extracted percentages
        cpd_specs = {}
        
        # Use entropy to measure disorder in the data
        if percentages:
            # Normalize percentages for entropy calculation
            norm_percentages = [p / sum(percentages) for p in percentages]
            data_entropy = entropy(norm_percentages)
        else:
            data_entropy = 0.5
        
        # Build Bayesian network
        try:
            model = build_bn(edges, cpd_specs)
            if model is None:
                raise ValueError("Failed to build Bayesian network")
        except Exception:
            model = None
        
        paradox_detected = False
        best_entity = None
        confidence = 0.5
        
        if model and len(entities) >= 2:
            # Compare conditional vs marginal distributions for paradox detection
            entity_list = list(entities.keys())
            
            # Use topological_sort to determine processing order
            try:
                sorted_nodes = topological_sort(edges)
                if sorted_nodes is None:
                    sorted_nodes = entity_list[:2] + ["outcome"]
            except Exception:
                sorted_nodes = entity_list[:2] + ["outcome"]
            
            # Check for Simpson's paradox using compare_conditional_marginal
            paradox_results = []
            for entity in entity_list[:2]:  # Compare first two entities
                try:
                    result = compare_conditional_marginal(model, "outcome", entity, 1)
                    if result and isinstance(result, dict):
                        # Check if conditioning changes distribution significantly
                        if "difference" in result:
                            diff = abs(result["difference"])
                            if diff > 0.1:  # Significant difference
                                paradox_results.append((entity, diff))
                except Exception:
                    continue
            
            if paradox_results:
                paradox_detected = True
                # Entity with largest difference is most affected by paradox
                best_entity = max(paradox_results, key=lambda x: x[1])[0]
                
                # Use bayesian_update to refine confidence
                prior = 0.5
                likelihood = min(1.0, data_entropy * 2)  # Higher entropy -> more uncertainty
                confidence = bayesian_update(prior, likelihood, false_positive=0.1)
                
                if confidence is None:
                    confidence = 0.7
            else:
                # No paradox detected, use simple rate comparison
                best_entity = self._fallback_reasoning(entities, percentages)
                confidence = 0.6
        else:
            # Fallback if Bayesian analysis fails
            best_entity = self._fallback_reasoning(entities, percentages)
            confidence = 0.5
        
        # Final confidence adjustment using confidence_from_agreement
        if percentages:
            # Create multiple confidence estimates
            conf_estimates = [
                confidence,
                min(1.0, len(entities) / 10.0),
                min(1.0, len(percentages) / 20.0)
            ]
            final_conf = confidence_from_agreement(conf_estimates)
            if final_conf is not None:
                confidence = final_conf
        
        return {
            "answer": best_entity or "Unknown",
            "confidence": max(0.1, min(0.99, confidence)),
            "reasoning": f"Simpson's paradox {'detected' if paradox_detected else 'not detected'}",
            "paradox_detected": paradox_detected
        }

    def _fallback_reasoning(self, entities: Dict[str, Any], percentages: List[float]) -> str:
        """Fallback reasoning when Bayesian analysis fails."""
        if not entities:
            return "Unknown"
        
        # Find entity with highest average rate
        entity_avgs = {}
        for entity, data in entities.items():
            if data["rates"]:
                avg_rate = sum(data["rates"]) / len(data["rates"])
                entity_avgs[entity] = avg_rate
        
        if entity_avgs:
            best_entity = max(entity_avgs.items(), key=lambda x: x[1])[0]
            return best_entity
        
        # Last resort: entity with most mentions
        best_entity = max(entities.items(), key=lambda x: x[1]["mentions"])[0]
        return best_entity

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact or partial match with computed answer
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

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Normalize scores to [0, 1] range
        scores = [item["score"] for item in scored]
        if max(scores) > min(scores):
            normalized = [(s - min(scores)) / (max(scores) - min(scores)) for s in scores]
        else:
            normalized = [0.5 for _ in scores]
        
        # Apply softmax for final probabilities
        exp_scores = [2.71828 ** s for s in normalized]
        total = sum(exp_scores)
        if total > 0:
            final_scores = [s / total for s in exp_scores]
        else:
            final_scores = [1.0 / len(scored) for _ in scored]
        
        # Update results
        for i, item in enumerate(scored):
            item["score"] = final_scores[i]
        
        return scored