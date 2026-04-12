import re
import zlib
from typing import Dict, List, Any

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, solve_linear_system
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, compare_conditional_marginal

class ReasoningTool:
    """Seismology x Bayesian Networks - Simpson Paradox Detection"""

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
        """Extract entities, rates, and question from prompt using seismology-inspired fault line detection."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find entity names (capitalized multi-word phrases that appear before rates)
        entity_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        entities = {}
        
        # Find all percentage rates in the prompt
        rate_pattern = r'(\d+(?:\.\d+)?)%'
        all_rates = re.findall(rate_pattern, prompt)
        rates = [float(r) / 100.0 for r in all_rates]
        
        # Extract entity-rate associations by looking for patterns like "Entity X: Y%"
        for line in lines:
            # Look for patterns like "Hospital A: 58%" or "Drug B had 42% success"
            matches = re.findall(rf'({entity_pattern}.*?{rate_pattern})', line)
            for match in matches:
                full_text = match[0]
                entity_name = match[1]
                rate_value = float(match[2]) / 100.0
                
                if entity_name not in entities:
                    entities[entity_name] = {"rates": [], "mentions": 0}
                entities[entity_name]["rates"].append(rate_value)
                entities[entity_name]["mentions"] += 1
        
        # If we couldn't extract entities by pattern, use the capitalized phrases near rates
        if not entities and rates:
            # Find capitalized phrases that appear near percentage mentions
            for i, line in enumerate(lines):
                caps = re.findall(entity_pattern, line)
                rates_in_line = re.findall(rate_pattern, line)
                if caps and rates_in_line:
                    for cap in caps:
                        if cap not in entities:
                            entities[cap] = {"rates": [], "mentions": 0}
                        entities[cap]["rates"].extend([float(r)/100.0 for r in rates_in_line])
                        entities[cap]["mentions"] += 1
        
        # Determine if this is a two-group comparison (like hospital A vs B)
        entity_names = list(entities.keys())
        if len(entity_names) >= 2:
            primary_entities = entity_names[:2]
        else:
            primary_entities = entity_names
        
        return {
            "entities": entities,
            "rates": rates,
            "question": question,
            "primary_entities": primary_entities,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply seismology-inspired reasoning: treat aggregated data as surface waves and subgroup data as deep seismic layers."""
        entities = structure["entities"]
        rates = structure["rates"]
        primary_entities = structure["primary_entities"]
        
        if len(rates) < 4 or len(primary_entities) < 2:
            # Not enough data for Simpson's paradox analysis
            computed_answer = "Insufficient data"
            confidence = 0.1
            reasoning = "Not enough rates or entities extracted"
            return {"answer": computed_answer, "confidence": confidence, "reasoning": reasoning}
        
        # Seismology concept: Surface waves (aggregated data) can show different patterns
        # than body waves (subgroup data) due to subsurface heterogeneity.
        # We'll treat the aggregated rates as surface measurements and subgroup rates
        # as deeper seismic layers that reveal the true structure.
        
        # Extract aggregated rates (first two rates typically represent overall success rates)
        if len(rates) >= 2:
            aggregated_rates = rates[:2]
        else:
            aggregated_rates = rates
        
        # Extract subgroup rates (remaining rates)
        subgroup_rates = rates[2:] if len(rates) > 2 else []
        
        # CRITICAL PRIMITIVE 1: Use entropy to measure disorder in the rate distribution
        # High entropy = more chaotic distribution = potential for paradox
        rate_entropy = entropy([r for r in rates if 0 < r < 1])
        
        # Build a simple Bayesian network to model the Simpson's paradox scenario
        # Network: Entity -> Success | Subgroup
        edges = [("Entity", "Success"), ("Subgroup", "Success")]
        
        # Prepare CPDs using extracted rates
        cpd_specs = {}
        
        # Entity CPD: Two entities with equal prior probability
        entity_probs = [0.5, 0.5] if len(primary_entities) >= 2 else [1.0]
        cpd_specs["Entity"] = {"variable": "Entity", "values": entity_probs}
        
        # Subgroup CPD: Two subgroups with probabilities based on extracted rates
        if len(subgroup_rates) >= 2:
            # Normalize subgroup rates to get probabilities
            subgroup_sum = sum(subgroup_rates[:2])
            if subgroup_sum > 0:
                subgroup_probs = [subgroup_rates[0]/subgroup_sum, subgroup_rates[1]/subgroup_sum]
            else:
                subgroup_probs = [0.5, 0.5]
        else:
            subgroup_probs = [0.5, 0.5]
        cpd_specs["Subgroup"] = {"variable": "Subgroup", "values": subgroup_probs}
        
        # Success CPD: P(Success | Entity, Subgroup)
        # Use the extracted rates to parameterize this
        success_values = []
        if len(rates) >= 4:
            # Assume first 4 rates correspond to: Entity1-Subgroup1, Entity1-Subgroup2, Entity2-Subgroup1, Entity2-Subgroup2
            for i in range(2):  # For each entity
                for j in range(2):  # For each subgroup
                    idx = i * 2 + j
                    if idx < len(rates):
                        success_values.append([rates[idx], 1 - rates[idx]])
                    else:
                        success_values.append([0.5, 0.5])  # Default if not enough rates
        else:
            # Not enough rates, use uniform
            success_values = [[0.5, 0.5], [0.5, 0.5], [0.5, 0.5], [0.5, 0.5]]
        
        cpd_specs["Success"] = {
            "variable": "Success",
            "parents": ["Entity", "Subgroup"],
            "values": success_values
        }
        
        # CRITICAL AMINO ACID 1: Build Bayesian network
        model = build_bn(edges, cpd_specs)
        
        # CRITICAL AMINO ACID 2: Check for Simpson's paradox by comparing conditional vs marginal
        paradox_detected = False
        better_entity = None
        
        if model and len(primary_entities) >= 2:
            # Check if conditioning on Subgroup reverses the trend
            try:
                # P(Success | Entity=0) - overall for entity 0
                result0 = conditional_query(model, ["Success"], {"Entity": 0})
                # P(Success | Entity=1) - overall for entity 1
                result1 = conditional_query(model, ["Success"], {"Entity": 1})
                
                if result0 and result1 and "Success" in result0 and "Success" in result1:
                    overall_success0 = result0["Success"].get(1, 0.5)  # Success=1 means success
                    overall_success1 = result1["Success"].get(1, 0.5)
                    
                    # Determine which entity is better overall
                    overall_better = 0 if overall_success0 > overall_success1 else 1
                    
                    # Now check within each subgroup
                    subgroup_reversal = False
                    for subgroup in [0, 1]:
                        result0_sub = conditional_query(model, ["Success"], {"Entity": 0, "Subgroup": subgroup})
                        result1_sub = conditional_query(model, ["Success"], {"Entity": 1, "Subgroup": subgroup})
                        
                        if result0_sub and result1_sub and "Success" in result0_sub and "Success" in result1_sub:
                            success0_sub = result0_sub["Success"].get(1, 0.5)
                            success1_sub = result1_sub["Success"].get(1, 0.5)
                            
                            # Check if trend reverses in this subgroup
                            if overall_better == 0:  # Entity 0 better overall
                                if success0_sub < success1_sub:  # But worse in subgroup
                                    subgroup_reversal = True
                                    subgroup_better = 1
                            else:  # Entity 1 better overall
                                if success0_sub > success1_sub:  # But worse in subgroup
                                    subgroup_reversal = True
                                    subgroup_better = 0
                    
                    if subgroup_reversal:
                        paradox_detected = True
                        better_entity = primary_entities[subgroup_better] if subgroup_better < len(primary_entities) else primary_entities[0]
            except:
                # Amino acid failed, fall back to primitive-based reasoning
                pass
        
        # CRITICAL PRIMITIVE 2: Bayesian update to refine confidence
        # Use the entropy as prior uncertainty, paradox detection as evidence
        prior_uncertainty = min(rate_entropy, 0.99)  # Cap at 0.99
        likelihood_paradox = 0.8 if paradox_detected else 0.2
        posterior_confidence = bayesian_update(prior_uncertainty, likelihood_paradox, false_positive=0.1)
        
        # CRITICAL PRIMITIVE 3: Solve linear system to find "true" success rates
        # Model: overall_rate = w1*subgroup1_rate + w2*subgroup2_rate
        if len(rates) >= 4:
            # Set up equations: overall1 = a*s11 + b*s12, overall2 = a*s21 + b*s22
            # Where a+b=1 (weights sum to 1)
            A = [
                [rates[0] - rates[2], rates[1] - rates[3]],  # From: overall1 - overall2 = a(s11-s21) + b(s12-s23)
                [1, 1]  # a + b = 1
            ]
            b = [rates[0] - rates[2], 1]
            
            weights = solve_linear_system(A, b)
            if weights:
                # The entity with higher weighted average across subgroups is truly better
                weighted_avg0 = weights[0]*rates[0] + weights[1]*rates[1] if len(weights) >= 2 else rates[0]
                weighted_avg1 = weights[0]*rates[2] + weights[1]*rates[3] if len(weights) >= 2 else rates[2]
                
                truly_better_idx = 0 if weighted_avg0 > weighted_avg1 else 1
                truly_better = primary_entities[truly_better_idx] if truly_better_idx < len(primary_entities) else primary_entities[0]
                
                # If paradox detected, the truly better entity is the one from subgroup analysis
                if paradox_detected:
                    computed_answer = better_entity
                else:
                    computed_answer = truly_better
            else:
                # Linear system failed, use simple comparison
                if paradox_detected:
                    computed_answer = better_entity
                else:
                    # Compare aggregated rates
                    if len(aggregated_rates) >= 2:
                        better_idx = 0 if aggregated_rates[0] > aggregated_rates[1] else 1
                        computed_answer = primary_entities[better_idx] if better_idx < len(primary_entities) else "Cannot determine"
                    else:
                        computed_answer = "Cannot determine"
        else:
            # Not enough rates for linear system
            if paradox_detected:
                computed_answer = better_entity
            else:
                computed_answer = primary_entities[0] if primary_entities else "Cannot determine"
        
        # CRITICAL PRIMITIVE 4: Confidence from agreement of multiple indicators
        indicators = []
        if paradox_detected:
            indicators.append(0.9)  # High confidence if paradox detected
        else:
            indicators.append(0.5)  # Medium confidence otherwise
        
        if rate_entropy > 0.5:
            indicators.append(0.7)  # Higher confidence if high entropy (more complex distribution)
        
        if len(rates) >= 4:
            indicators.append(0.8)  # Higher confidence if we have subgroup data
        
        final_confidence = confidence_from_agreement(indicators) if indicators else 0.5
        final_confidence = min(max(final_confidence * posterior_confidence, 0.1), 0.95)
        
        reasoning_text = f"Seismology analysis: Surface waves (aggregated) show "
        if paradox_detected:
            reasoning_text += f"reversal when analyzing deep layers (subgroups). True better entity is {computed_answer}."
        else:
            reasoning_text += f"consistent pattern with deep layers. Better entity is {computed_answer}."
        reasoning_text += f" Entropy: {rate_entropy:.3f}, Confidence: {final_confidence:.3f}"
        
        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "reasoning": reasoning_text,
            "paradox_detected": paradox_detected
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        confidence = reasoning_result["confidence"]
        
        scored = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match of computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity between reasoning text and candidate
                base_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
            # Adjust score by confidence
            adjusted_score = base_score * confidence
            
            scored.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score,
                "confidence": confidence
            })
        
        return scored

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Simple calibration: ensure scores are between 0 and 1
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
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)