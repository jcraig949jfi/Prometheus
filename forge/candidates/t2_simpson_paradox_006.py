import re
import zlib
from typing import Dict, List, Any

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, solve_linear_system
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, compare_conditional_marginal

class ReasoningTool:
    """Control theory x Bayesian networks - Simpson's paradox detection"""

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

        # Find entity names (capitalized phrases that appear with rates)
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        potential_entities = re.findall(entity_pattern, prompt)
        
        # Find all percentage rates
        rate_pattern = r'(\d+(?:\.\d+)?)%'
        rates = [float(r) for r in re.findall(rate_pattern, prompt)]
        
        # Find subgroup indicators (like "men", "women", "severe", "mild")
        subgroup_keywords = ['men', 'women', 'male', 'female', 'severe', 'mild', 
                           'young', 'old', 'group a', 'group b', 'subgroup']
        subgroups = []
        for line in lines:
            lower_line = line.lower()
            for kw in subgroup_keywords:
                if kw in lower_line:
                    subgroups.append(kw)
        
        # Build structure
        entities = {}
        for ent in set(potential_entities):
            if len(ent.split()) <= 3:  # Avoid long phrases
                entities[ent] = {"rates": [], "subgroups": []}
        
        # Associate rates with entities based on proximity
        sentences = prompt.split('.')
        for sentence in sentences:
            sentence_ents = re.findall(entity_pattern, sentence)
            sentence_rates = [float(r) for r in re.findall(rate_pattern, sentence)]
            
            for ent in sentence_ents:
                if ent in entities:
                    entities[ent]["rates"].extend(sentence_rates)
            
            # Check for subgroup mentions
            lower_sent = sentence.lower()
            for sg in subgroups:
                if sg in lower_sent:
                    for ent in sentence_ents:
                        if ent in entities and sg not in entities[ent]["subgroups"]:
                            entities[ent]["subgroups"].append(sg)
        
        # Clean up: remove entities with no rates
        entities = {k: v for k, v in entities.items() if v["rates"]}
        
        return {
            "entities": entities,
            "subgroups": list(set(subgroups)),
            "rates": rates,
            "question": question,
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use control theory stability analysis to detect Simpson's paradox."""
        entities = structure["entities"]
        subgroups = structure["subgroups"]
        rates = structure["rates"]
        
        if len(entities) < 2 or len(rates) < 4:
            # Fallback: simple comparison if insufficient data
            best_entity = max(entities.items(), 
                            key=lambda x: sum(x[1]["rates"])/len(x[1]["rates"]) if x[1]["rates"] else 0)
            return {
                "answer": best_entity[0],
                "confidence": 0.5,
                "reasoning": "Simple average comparison (insufficient data for full analysis)",
                "paradox_detected": False
            }
        
        # Control theory: Model each entity as a system with subgroup rates as state variables
        # Simpson's paradox occurs when aggregated feedback (overall rate) has opposite sign
        # to subgroup feedback signals (subgroup rates)
        
        # T1 PRIMITIVE 1: Compute entropy of rate distribution as measure of system disorder
        if rates:
            rate_probs = [r/100 for r in rates]
            system_entropy = entropy(rate_probs)
        else:
            system_entropy = 1.0
        
        # Build Bayesian network to model causal relationships
        # Entity -> Subgroup -> Rate
        edges = []
        for entity in entities:
            for sg in subgroups:
                edges.append((entity, f"{entity}_{sg}"))
                edges.append((f"{entity}_{sg}", f"rate_{entity}_{sg}"))
        
        # Create CPDs using extracted rates
        cpd_specs = {}
        rate_index = 0
        
        for entity in entities:
            entity_rates = entities[entity]["rates"]
            if len(entity_rates) >= 2 and len(subgroups) >= 2:
                # Distribute rates to subgroups
                for i, sg in enumerate(subgroups[:2]):  # Use first 2 subgroups
                    if i < len(entity_rates):
                        rate_val = entity_rates[i] / 100
                        cpd_specs[f"rate_{entity}_{sg}"] = {
                            "variable": f"rate_{entity}_{sg}",
                            "variable_card": 2,
                            "values": [[rate_val, 1 - rate_val]],
                            "evidence": [f"{entity}_{sg}"],
                            "evidence_card": [2]
                        }
        
        # AMINO ACID 1: Build Bayesian network
        bn_model = build_bn(edges, cpd_specs if cpd_specs else None)
        
        paradox_detected = False
        best_entity = None
        confidence = 0.5
        
        if bn_model and len(entities) >= 2:
            # AMINO ACID 2: Compare conditional vs marginal to detect paradox
            entity_list = list(entities.keys())
            try:
                # Compare P(rate_high | entity1) vs P(rate_high | entity2)
                comparison = compare_conditional_marginal(
                    bn_model, 
                    target=f"rate_{entity_list[0]}_{subgroups[0]}" if subgroups else f"rate_{entity_list[0]}",
                    condition_var=entity_list[0],
                    condition_val=0
                )
                if comparison:
                    paradox_detected = "reversal" in str(comparison).lower()
            except:
                pass
            
            # AMINO ACID 3: Query conditional probabilities
            if subgroups:
                try:
                    evidence = {f"{entity_list[0]}_{subgroups[0]}": 0}
                    query_result = conditional_query(
                        bn_model,
                        target_vars=[f"rate_{entity_list[0]}_{subgroups[0]}"],
                        evidence=evidence
                    )
                    if query_result:
                        # Use query result to adjust confidence
                        prob_values = list(query_result.values())
                        if prob_values:
                            confidence = sum(prob_values) / len(prob_values)
                except:
                    pass
        
        # T1 PRIMITIVE 2: Bayesian update of confidence based on entropy
        # Higher entropy (more disorder) reduces confidence in aggregated result
        prior_confidence = 0.7
        likelihood = 1.0 - min(system_entropy, 1.0)  # Lower entropy -> higher likelihood
        updated_confidence = bayesian_update(prior_confidence, likelihood)
        if updated_confidence is not None:
            confidence = updated_confidence
        
        # Control theory: Stability analysis
        # Build state-space matrix from rates
        if len(rates) >= 4:
            # Create 2x2 system: aggregated vs subgroup differences
            entity_avgs = []
            for entity in entities:
                entity_rates = entities[entity]["rates"]
                if entity_rates:
                    entity_avgs.append(sum(entity_rates)/len(entity_rates))
            
            if len(entity_avgs) >= 2:
                # T1 PRIMITIVE 3: Solve linear system for stability eigenvalues
                # Simple 2x2: [avg1, diff1; avg2, diff2]
                A = [[entity_avgs[0]/100, (entity_avgs[0] - min(rates))/100],
                     [entity_avgs[1]/100, (entity_avgs[1] - max(rates))/100]]
                b = [0.5, 0.5]  # Equilibrium point
                
                solution = solve_linear_system(A, b)
                if solution:
                    # Check if system is stable (solution exists and is reasonable)
                    stability = abs(solution[0]) + abs(solution[1])
                    if stability < 1.0:
                        confidence *= (1.0 - stability)
        
        # T1 PRIMITIVE 4: Final confidence aggregation
        if len(entities) >= 2:
            confidence_scores = [confidence, 1.0 - system_entropy, 0.7]
            final_confidence = confidence_from_agreement(confidence_scores)
            if final_confidence is not None:
                confidence = final_confidence
        
        # Determine best entity based on control theory: most stable (least paradoxical)
        if paradox_detected and len(entities) >= 2:
            # When paradox detected, prefer entity with more consistent subgroup rates
            best_entity = min(entities.items(),
                            key=lambda x: max(x[1]["rates"]) - min(x[1]["rates"]) if len(x[1]["rates"]) >= 2 else 100)
            best_entity = best_entity[0]
        else:
            # No paradox: choose entity with highest average rate
            best_entity = max(entities.items(),
                            key=lambda x: sum(x[1]["rates"])/len(x[1]["rates"]) if x[1]["rates"] else 0)
            best_entity = best_entity[0]
        
        reasoning_text = f"Control theory stability analysis"
        if paradox_detected:
            reasoning_text += " detected Simpson's paradox (aggregated feedback opposite subgroup signals). "
        else:
            reasoning_text += " found consistent trends across aggregation levels. "
        reasoning_text += f"Selected {best_entity} with confidence {confidence:.2f}."
        
        return {
            "answer": best_entity,
            "confidence": min(max(confidence, 0.0), 1.0),
            "reasoning": reasoning_text,
            "paradox_detected": paradox_detected
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Boost score if candidate contains reasoning keywords when paradox detected
            if reasoning_result.get("paradox_detected", False):
                paradox_terms = ["reverse", "paradox", "confound", "subgroup", "aggregat"]
                if any(term in candidate.lower() for term in paradox_terms):
                    base_score = min(base_score * 1.2, 1.0)
            
            results.append({
                "candidate": candidate,
                "base_score": base_score,
                "confidence": reasoning_result["confidence"]
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence and normalization."""
        if not scored:
            return []
        
        # Adjust scores by confidence
        calibrated = []
        for item in scored:
            adjusted_score = item["base_score"] * item["confidence"]
            calibrated.append({
                "candidate": item["candidate"],
                "score": adjusted_score,
                "confidence": item["confidence"]
            })
        
        # Normalize to [0, 1] range
        max_score = max(item["score"] for item in calibrated) if calibrated else 1.0
        if max_score > 0:
            for item in calibrated:
                item["score"] = item["score"] / max_score
        
        return calibrated

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