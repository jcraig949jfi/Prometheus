import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    solve_sat,
    modus_ponens,
    check_transitivity
)
from forge.amino_acids.pysat_acids import check_entailment, detect_paradox


class ReasoningTool:
    """feedback_systems x pysat_acids - argument_strength"""

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
        """Extract premises, conclusion, and entities from the argument."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        
        premises = []
        conclusion = None
        entities = set()
        
        # Look for premise indicators
        premise_indicators = ["since", "because", "given that", "as", "for"]
        # Look for conclusion indicators
        conclusion_indicators = ["therefore", "thus", "hence", "so", "consequently", "it follows that"]
        
        for line in lines:
            line_lower = line.lower()
            
            # Extract capitalized entities (likely proposition names)
            found_entities = re.findall(r'\b([A-Z][a-zA-Z]*)\b', line)
            entities.update(found_entities)
            
            # Check if this is a conclusion
            is_conclusion = any(indicator in line_lower for indicator in conclusion_indicators)
            
            if is_conclusion and conclusion is None:
                conclusion = line
                # Remove conclusion indicator for cleaner text
                for indicator in conclusion_indicators:
                    if indicator in line_lower:
                        conclusion = line_lower.split(indicator)[-1].strip()
                        break
            else:
                # Check if it's a premise
                is_premise = any(indicator in line_lower for indicator in premise_indicators)
                if is_premise or (len(line) > 10 and not is_conclusion):
                    premises.append(line)
        
        # If no conclusion found via indicators, last line might be conclusion
        if conclusion is None and lines:
            conclusion = lines[-1]
            if len(lines) > 1:
                premises = lines[:-1]
        
        # Clean up premises and conclusion
        premises = [p.strip() for p in premises if p.strip()]
        if conclusion:
            conclusion = conclusion.strip()
        
        # Extract logical operators
        operators = []
        all_text = prompt.lower()
        if "and" in all_text:
            operators.append("AND")
        if "or" in all_text:
            operators.append("OR")
        if "not" in all_text or "no " in all_text or "never" in all_text:
            operators.append("NOT")
        if "if" in all_text and "then" in all_text:
            operators.append("IMPLIES")
        
        return {
            "premises": premises,
            "conclusion": conclusion,
            "entities": list(entities),
            "operators": operators,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use feedback systems theory to evaluate argument strength."""
        premises = structure["premises"]
        conclusion = structure["conclusion"]
        entities = structure["entities"]
        operators = structure["operators"]
        
        if not premises or not conclusion:
            return {
                "answer": "Invalid argument structure",
                "confidence": 0.0,
                "reasoning": "Missing premises or conclusion"
            }
        
        # FEEDBACK SYSTEMS APPROACH:
        # 1. Model premises as input signals
        # 2. Model logical operations as transfer functions
        # 3. Model conclusion as output
        # 4. Check stability (no paradox) and gain (entailment strength)
        
        # Step 1: Encode premises and conclusion as SAT clauses
        # Simple encoding: each entity is a variable, "not X" is negation
        var_map = {}
        next_var = 1
        
        for entity in entities:
            var_map[entity] = next_var
            var_map[f"not_{entity}"] = -next_var
            next_var += 1
        
        premise_clauses = []
        for premise in premises:
            clause = []
            premise_lower = premise.lower()
            
            # Check for negations
            for entity in entities:
                entity_lower = entity.lower()
                if entity_lower in premise_lower:
                    # Check if negated
                    negated = False
                    neg_patterns = [
                        f"not {entity_lower}",
                        f"no {entity_lower}",
                        f"never {entity_lower}",
                        f"{entity_lower} is false",
                        f"{entity_lower} is not"
                    ]
                    for pattern in neg_patterns:
                        if pattern in premise_lower:
                            negated = True
                            break
                    
                    if negated:
                        clause.append(-var_map[entity])
                    else:
                        clause.append(var_map[entity])
            
            if clause:
                premise_clauses.append(clause)
        
        # Encode conclusion
        conclusion_clause = []
        if conclusion:
            conclusion_lower = conclusion.lower()
            for entity in entities:
                entity_lower = entity.lower()
                if entity_lower in conclusion_lower:
                    # Check if negated
                    negated = False
                    neg_patterns = [
                        f"not {entity_lower}",
                        f"no {entity_lower}",
                        f"never {entity_lower}",
                        f"{entity_lower} is false",
                        f"{entity_lower} is not"
                    ]
                    for pattern in neg_patterns:
                        if pattern in conclusion_lower:
                            negated = True
                            break
                    
                    if negated:
                        conclusion_clause.append(-var_map[entity])
                    else:
                        conclusion_clause.append(var_map[entity])
        
        # Step 2: Check for paradox (system instability)
        paradox_result = detect_paradox(premise_clauses)
        is_paradox = paradox_result is not None and paradox_result.get("is_paradox", False)
        
        # Step 3: Check logical entailment (system gain)
        entailment_result = None
        if premise_clauses and conclusion_clause:
            entailment_result = check_entailment(premise_clauses, conclusion_clause)
        
        # Step 4: Use feedback systems concepts
        # Entropy of premise distribution represents uncertainty
        if premise_clauses:
            # Estimate probability distribution from clause complexity
            num_clauses = len(premise_clauses)
            avg_clause_len = sum(len(c) for c in premise_clauses) / max(1, num_clauses)
            
            # Create a simple distribution based on clause structure
            if num_clauses > 0:
                p_satisfiable = 0.7 if not is_paradox else 0.1
                p_unsatisfiable = 0.3 if is_paradox else 0.1
                p_ambiguous = 0.2
                probs = [p_satisfiable, p_unsatisfiable, p_ambiguous]
                # Normalize
                total = sum(probs)
                if total > 0:
                    probs = [p/total for p in probs]
                else:
                    probs = [0.33, 0.33, 0.34]
            else:
                probs = [0.33, 0.33, 0.34]
            
            uncertainty = entropy(probs)
        else:
            uncertainty = 1.0  # Maximum uncertainty
        
        # Step 5: Bayesian update of argument strength
        prior_strength = 0.5  # Neutral prior
        likelihood = 0.0
        
        if entailment_result is not None:
            entails = entailment_result.get("entails", False)
            if entails:
                likelihood = 0.9  # Strong evidence for valid argument
            else:
                likelihood = 0.1  # Weak evidence for valid argument
        
        if is_paradox:
            likelihood = 0.01  # Paradox strongly indicates invalid argument
        
        # Use bayesian_update primitive
        posterior_strength = bayesian_update(prior_strength, likelihood)
        
        # Step 6: Check transitivity of logical relations
        # Extract implication relations from "if...then" statements
        relations = []
        all_text = structure["raw"].lower()
        sentences = re.split(r'[.!?]', all_text)
        
        for sentence in sentences:
            if "if" in sentence and "then" in sentence:
                # Simple extraction: if A then B
                parts = sentence.split("then")
                if len(parts) >= 2:
                    if_part = parts[0].replace("if", "").strip()
                    then_part = parts[1].strip()
                    
                    # Find entities in each part
                    for entity in entities:
                        entity_lower = entity.lower()
                        if entity_lower in if_part:
                            for entity2 in entities:
                                entity2_lower = entity2.lower()
                                if entity2_lower in then_part and entity != entity2:
                                    relations.append((entity, entity2))
        
        transitivity_result = check_transitivity(relations)
        
        # Step 7: Use SAT solving to check consistency
        sat_result = None
        if premise_clauses:
            sat_result = solve_sat(premise_clauses, len(var_map))
        
        # Step 8: Determine final answer based on feedback systems analysis
        # Feedback stability: no paradox, high entailment, transitive relations
        
        stability_score = 0.0
        if not is_paradox:
            stability_score += 0.4
        if entailment_result and entailment_result.get("entails", False):
            stability_score += 0.4
        if transitivity_result and len(transitivity_result) > 0:
            # Check if relations form a consistent transitive closure
            has_cycles = False
            for node, reachable in transitivity_result.items():
                if node in reachable:  # Self-reachability indicates cycle
                    has_cycles = True
                    break
            if not has_cycles:
                stability_score += 0.2
        
        # Use modus_ponens to check direct inference
        facts = set()
        rules = []
        
        # Extract simple facts (entities mentioned positively without negation)
        for premise in premises:
            premise_lower = premise.lower()
            for entity in entities:
                entity_lower = entity.lower()
                if entity_lower in premise_lower:
                    # Check if it's a positive assertion
                    neg_patterns = [f"not {entity_lower}", f"no {entity_lower}", f"never {entity_lower}"]
                    is_negated = any(pattern in premise_lower for pattern in neg_patterns)
                    
                    if not is_negated:
                        facts.add(entity)
        
        # Extract rules from "if...then" statements
        for relation in relations:
            a, b = relation
            rules.append((a, b))
        
        inferred = modus_ponens(rules, facts)
        
        # Determine if conclusion is in inferred facts
        conclusion_entity = None
        if conclusion:
            for entity in entities:
                if entity.lower() in conclusion.lower():
                    conclusion_entity = entity
                    break
        
        directly_inferrable = False
        if conclusion_entity and conclusion_entity in inferred:
            directly_inferrable = True
        
        # Compute confidence from multiple measures
        measures = []
        if posterior_strength is not None:
            measures.append(posterior_strength)
        measures.append(stability_score)
        if directly_inferrable:
            measures.append(0.8)
        else:
            measures.append(0.2)
        if sat_result is not None:  # SAT solver found a model
            measures.append(0.7)
        else:
            measures.append(0.3)
        
        confidence = confidence_from_agreement(measures)
        
        # Final decision: is the argument valid/strong?
        if is_paradox:
            argument_valid = False
            strength_label = "Invalid (paradox)"
        elif entailment_result and entailment_result.get("entails", False):
            argument_valid = True
            strength_label = "Valid"
        elif posterior_strength > 0.7 and stability_score > 0.7:
            argument_valid = True
            strength_label = "Strong"
        elif posterior_strength < 0.3 or stability_score < 0.3:
            argument_valid = False
            strength_label = "Weak"
        else:
            argument_valid = posterior_strength > 0.5
            strength_label = "Moderate"
        
        # The computed answer is the strength assessment
        computed_answer = strength_label
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Feedback systems analysis: stability={stability_score:.2f}, "
                        f"entropy={uncertainty:.2f}, "
                        f"posterior={posterior_strength:.2f}, "
                        f"paradox={is_paradox}, "
                        f"entails={entailment_result.get('entails', False) if entailment_result else False}",
            "raw_scores": {
                "posterior_strength": posterior_strength,
                "stability_score": stability_score,
                "uncertainty": uncertainty,
                "is_paradox": is_paradox,
                "entails": entailment_result.get("entails", False) if entailment_result else False,
                "directly_inferrable": directly_inferrable
            }
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
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
        
        # Simple min-max normalization
        scores = [item["score"] for item in scored]
        if len(scores) == 1:
            min_score = max_score = scores[0]
        else:
            min_score = min(scores)
            max_score = max(scores)
        
        calibrated = []
        for item in scored:
            if max_score > min_score:
                norm_score = (item["score"] - min_score) / (max_score - min_score)
            else:
                norm_score = 1.0
            
            calibrated.append({
                "candidate": item["candidate"],
                "score": norm_score
            })
        
        return calibrated

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance between two strings."""
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) > 0:
            return (cab - min(ca, cb)) / max(ca, cb)
        return 1.0