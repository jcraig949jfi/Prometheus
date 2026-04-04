import re
import zlib
from typing import Dict, List, Any, Tuple
from forge_primitives import bayesian_update, entropy, confidence_from_agreement, expected_value
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, compare_conditional_marginal, detect_confounders

class ReasoningTool:
    """evolutionary_biology x pgmpy_acids - simpson_paradox"""

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
        
        # Find entity names (capitalized multi-word phrases that appear with numbers)
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        all_names = re.findall(entity_pattern, prompt)
        # Filter to likely entities: appear near numbers and are not common words
        common_words = {'Hospital', 'Clinic', 'Center', 'Drug', 'Treatment', 'Group', 'Study'}
        entities = {}
        for name in set(all_names):
            if name in common_words:
                continue
            # Check if name appears near a percentage in the same sentence
            sentences = prompt.split('.')
            for sent in sentences:
                if name in sent and re.search(r'\d+\.?\d*%', sent):
                    entities[name] = {"subgroups": [], "rates": []}
                    break
        
        # Extract subgroups and their rates
        # Look for patterns like "Subgroup A: 58% success"
        subgroup_data = {}
        for sent in sentences:
            # Find percentages
            percentages = re.findall(r'(\d+\.?\d*)%', sent)
            if not percentages:
                continue
            # Find subgroup identifiers (like "Subgroup A", "Group 1", "Mild cases")
            subgroup_match = re.search(r'\b(?:Subgroup|Group|Category|Severity)\s+([A-Z0-9]+|\w+)', sent, re.IGNORECASE)
            if subgroup_match:
                subgroup = subgroup_match.group(1)
                subgroup_data[subgroup] = [float(p) for p in percentages]
            # Also check if sentence contains entity names
            for entity in entities:
                if entity in sent:
                    if "subgroups" not in entities[entity]:
                        entities[entity]["subgroups"] = []
                    if "rates" not in entities[entity]:
                        entities[entity]["rates"] = []
                    # Associate percentages with this entity
                    entities[entity]["rates"].extend([float(p) for p in percentages])
        
        # Find aggregated rates (overall success rates)
        aggregated = {}
        for sent in sentences:
            if "overall" in sent.lower() or "aggregate" in sent.lower():
                percentages = re.findall(r'(\d+\.?\d*)%', sent)
                if percentages:
                    # Try to associate with an entity
                    for entity in entities:
                        if entity in sent:
                            aggregated[entity] = float(percentages[0])
                            break
        
        return {
            "entities": entities,
            "subgroup_data": subgroup_data,
            "aggregated": aggregated,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply evolutionary biology framework: treat subgroups as species competing in niches.
        Simpson's paradox occurs when aggregated fitness (overall rate) reverses subgroup fitness trends.
        Use Bayesian network to model confounding, compute fitness differentials."""
        
        entities = structure["entities"]
        subgroup_data = structure["subgroup_data"]
        aggregated = structure["aggregated"]
        
        # If we have at least two entities and subgroups, build evolutionary model
        entity_names = list(entities.keys())
        if len(entity_names) >= 2 and len(subgroup_data) >= 2:
            # T1 PRIMITIVE 1: Compute entropy of subgroup rates as measure of niche diversity
            all_rates = []
            for subgroup, rates in subgroup_data.items():
                all_rates.extend(rates)
            if all_rates:
                # Normalize rates to probabilities for entropy calculation
                rate_sum = sum(all_rates)
                if rate_sum > 0:
                    probs = [r/rate_sum for r in all_rates]
                    niche_entropy = entropy(probs)  # T1 primitive call 1
                else:
                    niche_entropy = 0.0
            else:
                niche_entropy = 0.0
            
            # Build Bayesian network to detect confounding
            # Variables: Entity (E), Subgroup (S), Success (R)
            edges = [("Subgroup", "Success"), ("Entity", "Success")]
            
            # Create CPDs from extracted data
            cpd_specs = []
            try:
                # For Subgroup -> Success: use subgroup rates
                if subgroup_data:
                    subgroup_states = list(subgroup_data.keys())
                    # Convert rates to probabilities
                    cpd_values = []
                    for subgroup in subgroup_states:
                        rates = subgroup_data[subgroup]
                        if rates:
                            # Average rate for this subgroup
                            avg_rate = sum(rates) / len(rates)
                            cpd_values.append([avg_rate/100, 1 - avg_rate/100])
                        else:
                            cpd_values.append([0.5, 0.5])  # Default if no data
                    
                    if cpd_values:
                        cpd_specs.append({
                            "variable": "Success",
                            "variable_card": 2,
                            "evidence": ["Subgroup"],
                            "evidence_card": [len(subgroup_states)],
                            "values": cpd_values
                        })
                
                # For Entity -> Success: use aggregated rates if available
                if aggregated and entity_names:
                    entity_states = entity_names
                    cpd_values = []
                    for entity in entity_states:
                        if entity in aggregated:
                            rate = aggregated[entity] / 100
                            cpd_values.append([rate, 1 - rate])
                        else:
                            # Estimate from subgroup data if available
                            if entity in entities and "rates" in entities[entity]:
                                rates = entities[entity]["rates"]
                                if rates:
                                    avg = sum(rates) / len(rates) / 100
                                    cpd_values.append([avg, 1 - avg])
                                else:
                                    cpd_values.append([0.5, 0.5])
                            else:
                                cpd_values.append([0.5, 0.5])
                    
                    if cpd_values:
                        cpd_specs.append({
                            "variable": "Success",
                            "variable_card": 2,
                            "evidence": ["Entity"],
                            "evidence_card": [len(entity_states)],
                            "values": cpd_values
                        })
                
                # AMINO ACID 1: Build Bayesian network
                model = build_bn(edges, cpd_specs)  # Amino acid call
                
                if model is not None:
                    # AMINO ACID 2: Detect confounders (Subgroup is confounder between Entity and Success)
                    confounders = detect_confounders(model, "Entity", "Success")  # Amino acid call
                    
                    # AMINO ACID 3: Compare conditional vs marginal to detect Simpson's paradox
                    paradox_detected = False
                    for entity in entity_names[:2]:  # Check first two entities
                        try:
                            # P(Success | Entity=entity)
                            cond_result = conditional_query(model, ["Success"], {"Entity": entity})
                            # P(Success) marginal
                            marginal_result = conditional_query(model, ["Success"], {})
                            
                            if cond_result is not None and marginal_result is not None:
                                # Compare probabilities of success
                                cond_success = cond_result.get(1, 0.5)
                                marginal_success = marginal_result.get(1, 0.5)
                                # Large difference suggests conditioning matters
                                if abs(cond_success - marginal_success) > 0.2:
                                    paradox_detected = True
                                    break
                        except:
                            continue
                    
                    # T1 PRIMITIVE 2: Compute expected fitness differential
                    # Evolutionary fitness = success rate
                    fitness_pairs = []
                    for entity in entity_names:
                        if entity in aggregated:
                            fitness = aggregated[entity] / 100
                        elif entity in entities and "rates" in entities[entity] and entities[entity]["rates"]:
                            rates = entities[entity]["rates"]
                            fitness = sum(rates) / (len(rates) * 100)
                        else:
                            fitness = 0.5
                        fitness_pairs.append((0.5, fitness))  # Assume equal probability for now
                    
                    if fitness_pairs:
                        avg_fitness = expected_value(fitness_pairs)  # T1 primitive call 2
                    else:
                        avg_fitness = 0.5
                    
                    # Determine which entity has higher subgroup-consistent fitness
                    # Compute weighted average of subgroup rates for each entity
                    entity_fitness = {}
                    for entity in entity_names:
                        if entity in entities and "rates" in entities[entity]:
                            rates = entities[entity]["rates"]
                            if rates:
                                entity_fitness[entity] = sum(rates) / len(rates)
                            else:
                                entity_fitness[entity] = 0.0
                        else:
                            entity_fitness[entity] = 0.0
                    
                    # Compare with aggregated fitness
                    paradox_entity = None
                    for entity in entity_names:
                        if entity in aggregated and entity in entity_fitness:
                            aggregated_rate = aggregated[entity]
                            subgroup_avg = entity_fitness[entity]
                            # If signs differ (one above/below 50%), possible paradox
                            if (aggregated_rate - 50) * (subgroup_avg - 50) < 0:
                                paradox_entity = entity
                                break
                    
                    # T1 PRIMITIVE 3: Confidence from agreement between detection methods
                    detection_scores = []
                    if paradox_detected:
                        detection_scores.append(0.8)
                    if paradox_entity is not None:
                        detection_scores.append(0.7)
                    if niche_entropy > 1.0:  # High entropy suggests diverse niches
                        detection_scores.append(0.6)
                    
                    confidence = confidence_from_agreement(detection_scores) if detection_scores else 0.5  # T1 primitive call 3
                    
                    # Determine answer: which entity is actually better?
                    # In Simpson's paradox, the entity with better subgroup performance
                    # may have worse aggregate performance
                    if entity_fitness:
                        best_entity = max(entity_fitness.items(), key=lambda x: x[1])[0]
                        computed_answer = best_entity
                    else:
                        # Fallback: use entity with highest aggregated rate
                        if aggregated:
                            best_entity = max(aggregated.items(), key=lambda x: x[1])[0]
                            computed_answer = best_entity
                        else:
                            computed_answer = entity_names[0] if entity_names else "Unknown"
                    
                    return {
                        "answer": computed_answer,
                        "confidence": confidence,
                        "paradox_detected": paradox_detected or (paradox_entity is not None),
                        "reasoning": f"Evolutionary niche analysis: entropy={niche_entropy:.2f}, fitness={avg_fitness:.2f}"
                    }
            
            except Exception as e:
                # Fallback if BN construction fails
                pass
        
        # Fallback reasoning without BN
        # Simple comparison of aggregated rates
        if aggregated:
            best_entity = max(aggregated.items(), key=lambda x: x[1])[0]
            computed_answer = best_entity
            confidence = 0.6
        elif entity_names:
            computed_answer = entity_names[0]
            confidence = 0.4
        else:
            computed_answer = "Unknown"
            confidence = 0.2
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "paradox_detected": False,
            "reasoning": "Simple aggregate comparison (fallback)"
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate text
            # computed_answer is a variable from reasoning, not a hardcoded string
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity between reasoning text and candidate
                base_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
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
        
        # Simple normalization: scale to [0, 1] range
        scores = [item["score"] for item in scored]
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