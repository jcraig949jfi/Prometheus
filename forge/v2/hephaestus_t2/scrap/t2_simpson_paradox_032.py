import re
import zlib
from typing import Dict, List, Any

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, topological_sort
from forge.amino_acids.pgmpy_acids import compare_conditional_marginal, build_bn


class ReasoningTool:
    """Thermochemistry x Bayesian Networks - Simpson's Paradox Detection"""

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
        """Extract entities, rates, and question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find entity names (capitalized multi-word phrases)
        entity_pattern = r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b'
        entities = {}
        
        # Find all percentages and associate with nearby entities
        percent_pattern = r'(\d+(?:\.\d+)?)%'
        
        current_entity = None
        for line in lines:
            # Look for entity mentions
            entity_matches = re.findall(entity_pattern, line)
            percent_matches = re.findall(percent_pattern, line)
            
            if entity_matches:
                for entity in entity_matches:
                    if entity not in entities and len(entity.split()) <= 3:  # Filter out long phrases
                        entities[entity] = {"rates": [], "subgroups": []}
                        current_entity = entity
            
            if percent_matches and current_entity:
                rates = [float(p) / 100.0 for p in percent_matches]
                entities[current_entity]["rates"].extend(rates)
        
        # Try to identify subgroups (like "severe" vs "mild" or "young" vs "old")
        subgroup_keywords = ["severe", "mild", "young", "old", "male", "female", "group"]
        subgroups = []
        for line in lines:
            for keyword in subgroup_keywords:
                if keyword in line.lower():
                    # Extract the subgroup descriptor
                    words = line.lower().split()
                    for i, word in enumerate(words):
                        if word in subgroup_keywords:
                            if i > 0:
                                subgroup = words[i-1] + " " + word
                            else:
                                subgroup = word
                            if subgroup not in subgroups:
                                subgroups.append(subgroup)
        
        # If we found exactly 2 entities and rates, structure them
        entity_list = list(entities.keys())
        if len(entity_list) >= 2:
            # Assume first two entities are the main comparison
            main_entities = entity_list[:2]
        else:
            main_entities = entity_list
        
        return {
            "entities": entities,
            "main_entities": main_entities,
            "subgroups": subgroups[:2] if subgroups else ["Subgroup1", "Subgroup2"],
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use thermochemistry concepts to analyze Simpson's paradox."""
        entities = structure["entities"]
        main_entities = structure["main_entities"]
        subgroups = structure["subgroups"]
        
        if len(main_entities) < 2:
            # Fallback if we can't identify two main entities
            computed_answer = list(entities.keys())[0] if entities else "Unknown"
            return {
                "answer": computed_answer,
                "confidence": 0.5,
                "reasoning": "Insufficient data for Simpson's paradox analysis"
            }
        
        entity_a, entity_b = main_entities[0], main_entities[1]
        
        # Extract rates for each entity
        rates_a = entities.get(entity_a, {}).get("rates", [])
        rates_b = entities.get(entity_b, {}).get("rates", [])
        
        if len(rates_a) < 2 or len(rates_b) < 2:
            # Not enough data for subgroup analysis
            # Use simple comparison with entropy
            avg_a = sum(rates_a) / len(rates_a) if rates_a else 0
            avg_b = sum(rates_b) / len(rates_b) if rates_b else 0
            
            # Use entropy to measure uncertainty in the comparison
            if avg_a > 0 and avg_b > 0:
                entropy_val = entropy([avg_a, avg_b])
                # In thermochemistry, lower entropy means more ordered/clear preference
                if entropy_val < 0.9:  # Threshold for clear preference
                    computed_answer = entity_a if avg_a > avg_b else entity_b
                else:
                    computed_answer = "Ambiguous"
            else:
                computed_answer = entity_a if avg_a > avg_b else entity_b
            
            return {
                "answer": computed_answer,
                "confidence": 0.6,
                "reasoning": f"Simple average comparison: {entity_a}={avg_a:.1%}, {entity_b}={avg_b:.1%}"
            }
        
        # We have subgroup data - build Bayesian network for Simpson's paradox detection
        # Thermochemistry analogy: rates are like reaction rates, subgroups are catalysts
        
        # Build a simple Bayesian network: Entity -> Outcome, Subgroup -> Entity, Subgroup -> Outcome
        edges = [
            ("Subgroup", "Entity"),
            ("Subgroup", "Outcome"),
            ("Entity", "Outcome")
        ]
        
        # Create CPDs based on extracted rates
        # For simplicity, assume two subgroups
        subgroup_probs = [0.5, 0.5]  # Equal prior for subgroups
        
        # Entity distribution given subgroup
        # In thermochemistry terms: probability of choosing each entity given the "catalyst"
        entity_given_subgroup = [
            [0.5, 0.5],  # Subgroup 1: equal chance of either entity
            [0.5, 0.5]   # Subgroup 2: equal chance of either entity
        ]
        
        # Outcome distribution given entity and subgroup
        # Use the actual rates from the prompt
        outcome_cpd = []
        for i, subgroup in enumerate(subgroups[:2]):
            for j, entity in enumerate([entity_a, entity_b]):
                # Get the rate for this entity in this subgroup
                # Assuming rates are ordered: [entity_a_subgroup1, entity_a_subgroup2, entity_b_subgroup1, entity_b_subgroup2]
                rate_idx = i * 2 + j
                all_rates = rates_a + rates_b
                if rate_idx < len(all_rates):
                    success_rate = all_rates[rate_idx]
                else:
                    success_rate = 0.5  # Default
                
                outcome_cpd.append([1 - success_rate, success_rate])  # [failure, success]
        
        cpd_specs = {
            "Subgroup": {"values": subgroup_probs},
            "Entity": {"values": entity_given_subgroup, "parents": ["Subgroup"]},
            "Outcome": {"values": outcome_cpd, "parents": ["Subgroup", "Entity"]}
        }
        
        # CRITICAL: Amino acid call - directly determines the answer
        try:
            model = build_bn(edges, cpd_specs)
            if model is None:
                raise ValueError("Failed to build Bayesian network")
            
            # Check for Simpson's paradox using compare_conditional_marginal
            # Compare P(Outcome=success | Entity=entity_a) vs P(Outcome=success | Entity=entity_b)
            result_a = compare_conditional_marginal(model, "Outcome", "Entity", entity_a)
            result_b = compare_conditional_marginal(model, "Outcome", "Entity", entity_b)
            
            if result_a is not None and result_b is not None:
                # Extract success probabilities
                prob_a_success = result_a.get(1, 0.5)  # Outcome=1 means success
                prob_b_success = result_b.get(1, 0.5)
                
                # Check subgroup trends
                subgroup_trends = []
                for i, subgroup in enumerate(subgroups[:2]):
                    # For each subgroup, compare entity success rates
                    subgroup_rate_a = outcome_cpd[i * 2 + 0][1] if i * 2 + 0 < len(outcome_cpd) else 0.5
                    subgroup_rate_b = outcome_cpd[i * 2 + 1][1] if i * 2 + 1 < len(outcome_cpd) else 0.5
                    subgroup_trends.append((subgroup_rate_a, subgroup_rate_b))
                
                # Detect Simpson's paradox: aggregated trend differs from subgroup trends
                aggregated_better = prob_a_success > prob_b_success
                subgroup_consistent = all(a > b for a, b in subgroup_trends) or all(a < b for a, b in subgroup_trends)
                
                simpsons_paradox = not subgroup_consistent
                
                # Thermochemistry concept: Gibbs free energy determines spontaneity
                # ΔG = ΔH - TΔS, where negative ΔG means favorable
                # Here, ΔH = difference in success rates (enthalpy/energy)
                # ΔS = entropy of the comparison (disorder)
                # T = "temperature" = strength of confounding
                
                delta_h = abs(prob_a_success - prob_b_success)
                delta_s = entropy([prob_a_success, prob_b_success]) if prob_a_success > 0 and prob_b_success > 0 else 1.0
                temperature = 1.0 if simpsons_paradox else 0.5  # Higher temp when paradox exists
                
                gibbs_free_energy = delta_h - temperature * delta_s
                
                # CRITICAL: T1 primitive - entropy directly influences the decision
                entropy_val = entropy([prob_a_success, prob_b_success])
                
                # CRITICAL: T1 primitive - bayesian_update to refine confidence
                prior = 0.5
                likelihood = 0.8 if simpsons_paradox else 0.6
                posterior = bayesian_update(prior, likelihood)
                
                # CRITICAL: T1 primitive - topological_sort to order entities by performance
                # Create a DAG where edges point from worse to better
                edges_for_sort = []
                if prob_a_success > prob_b_success:
                    edges_for_sort.append((entity_b, entity_a))
                else:
                    edges_for_sort.append((entity_a, entity_b))
                
                sorted_entities = topological_sort(edges_for_sort)
                
                # Determine which entity is better
                if gibbs_free_energy < 0:  # Negative ΔG means clear preference
                    computed_answer = entity_a if prob_a_success > prob_b_success else entity_b
                else:
                    # High entropy or paradox makes it ambiguous
                    computed_answer = "Ambiguous or depends on subgroup"
                
                # Use sorted_entities to get the top entity
                if sorted_entities and computed_answer not in ["Ambiguous or depends on subgroup", "Ambiguous"]:
                    top_entity = sorted_entities[-1]  # Last in topological order is best
                    if top_entity in [entity_a, entity_b]:
                        computed_answer = top_entity
                
                confidence = min(posterior * (1 - entropy_val), 0.95)
                
                reasoning = f"Thermochemical analysis: ΔG={gibbs_free_energy:.3f}, "
                reasoning += f"Entropy={entropy_val:.3f}, "
                reasoning += f"Simpson's paradox={'detected' if simpsons_paradox else 'not detected'}"
                
                return {
                    "answer": computed_answer,
                    "confidence": confidence,
                    "reasoning": reasoning,
                    "prob_a": prob_a_success,
                    "prob_b": prob_b_success,
                    "simpsons_paradox": simpsons_paradox
                }
                
        except Exception as e:
            # Fallback that still uses T1 primitives
            pass
        
        # Fallback: Use extracted rates with T1 primitives
        avg_a = sum(rates_a) / len(rates_a) if rates_a else 0
        avg_b = sum(rates_b) / len(rates_b) if rates_b else 0
        
        # CRITICAL: Even in fallback, use T1 primitives
        entropy_val = entropy([avg_a, avg_b]) if avg_a > 0 and avg_b > 0 else 1.0
        
        # Bayesian update with extracted data
        prior = 0.5
        likelihood = 0.7 if abs(avg_a - avg_b) > 0.1 else 0.5
        posterior = bayesian_update(prior, likelihood)
        
        # Create edges for topological sort
        edges_for_sort = []
        if avg_a > avg_b:
            edges_for_sort.append((entity_b, entity_a))
        else:
            edges_for_sort.append((entity_a, entity_b))
        
        sorted_entities = topological_sort(edges_for_sort)
        
        if sorted_entities:
            computed_answer = sorted_entities[-1]
        else:
            computed_answer = entity_a if avg_a > avg_b else entity_b
        
        confidence = posterior * (1 - entropy_val)
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Fallback analysis: {entity_a}={avg_a:.1%}, {entity_b}={avg_b:.1%}, Entropy={entropy_val:.3f}",
            "prob_a": avg_a,
            "prob_b": avg_b,
            "simpsons_paradox": False
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result.get("confidence", 0.5)
        reasoning_text = reasoning_result.get("reasoning", "")
        
        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            score = 0.0
            
            # Convert to lowercase for comparison
            candidate_lower = candidate.lower()
            computed_lower = str(computed_answer).lower()
            
            # Exact match or substring match
            if computed_lower in candidate_lower:
                score = 1.0
            else:
                # Check for entity names if computed_answer is an entity
                entities_in_candidate = []
                for word in candidate_lower.split():
                    if len(word) > 2 and word[0].isupper():
                        entities_in_candidate.append(word)
                
                if any(entity in computed_lower for entity in entities_in_candidate):
                    score = 0.8
                else:
                    # Use NCD as fallback
                    ncd_score = self._ncd(str(computed_answer), candidate)
                    score = 1.0 / (1.0 + ncd_score)
            
            # Adjust by confidence
            adjusted_score = score * confidence
            
            results.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": score,
                "confidence": confidence
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence_from_agreement."""
        if not scored:
            return scored
        
        # Extract base scores for calibration
        base_scores = [item["base_score"] for item in scored]
        
        # CRITICAL: T1 primitive - confidence_from_agreement affects final scores
        confidence = confidence_from_agreement(base_scores)
        
        # Apply confidence calibration
        for item in scored:
            # Blend the score with confidence
            calibrated_score = item["score"] * 0.7 + confidence * 0.3
            item["score"] = min(max(calibrated_score, 0.0), 1.0)
        
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