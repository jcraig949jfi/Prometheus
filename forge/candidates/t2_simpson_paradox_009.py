import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, expected_value
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, compare_conditional_marginal, detect_confounders

class ReasoningTool:
    """fluid_dynamics x pgmpy_acids - simpson_paradox"""

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
        """Extract entities, subgroups, rates, and question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""

        # Find entity names (capitalized multi-word phrases)
        entity_pattern = r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b'
        potential_entities = re.findall(entity_pattern, prompt)
        # Filter: keep those that appear with numerical rates
        entities = {}
        for ent in set(potential_entities):
            # Look for lines containing this entity
            ent_lines = [line for line in lines if ent in line]
            rates = []
            for line in ent_lines:
                # Extract percentages
                percents = re.findall(r'([0-9]+\.?[0-9]*)%', line)
                rates.extend([float(p) for p in percents])
            if rates:
                entities[ent] = {"rates": rates, "lines": ent_lines}

        # Extract subgroups (often demographic categories like "Men", "Women", "Young", "Old")
        subgroup_keywords = ["men", "women", "male", "female", "young", "old", "group a", "group b", "subgroup"]
        subgroups = []
        for line in lines:
            lower_line = line.lower()
            for kw in subgroup_keywords:
                if kw in lower_line:
                    # Extract the subgroup phrase
                    words = line.split()
                    for i, w in enumerate(words):
                        if kw in w.lower():
                            # Take a few words around for context
                            start = max(0, i-1)
                            end = min(len(words), i+2)
                            subgroup = ' '.join(words[start:end])
                            if subgroup not in subgroups:
                                subgroups.append(subgroup)
                            break

        # Extract overall and subgroup rates
        overall_rates = []
        subgroup_data = []  # List of (subgroup_name, rate_entity1, rate_entity2, ...)
        for line in lines:
            percents = re.findall(r'([0-9]+\.?[0-9]*)%', line)
            if percents:
                rates = [float(p) for p in percents]
                if len(rates) >= 2:  # Likely subgroup comparison
                    # Check if line mentions a subgroup
                    has_subgroup = any(sg.lower() in line.lower() for sg in subgroups) if subgroups else False
                    if has_subgroup:
                        # Find which subgroup
                        for sg in subgroups:
                            if sg.lower() in line.lower():
                                subgroup_data.append((sg, rates))
                                break
                    else:
                        overall_rates.extend(rates)

        return {
            "entities": entities,
            "subgroups": subgroups,
            "subgroup_data": subgroup_data,
            "overall_rates": overall_rates,
            "question": question,
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply fluid dynamics principles to detect Simpson's paradox reversals."""
        entities = structure["entities"]
        subgroups = structure["subgroups"]
        subgroup_data = structure["subgroup_data"]
        question = structure["question"]

        # Fluid dynamics analogy: rates are flow velocities, entities are channels,
        # subgroups are laminar layers. Simpson's paradox is like reverse flow
        # in layers vs bulk flow.

        # PHASE 2A: Build a simple Bayesian network to model the relationships
        # Entity -> Outcome, with Subgroup as confounding variable
        edges = []
        cpd_specs = {}

        entity_names = list(entities.keys())
        if len(entity_names) >= 2:
            # Typically two entities being compared (e.g., Hospital A vs Hospital B)
            entity_a, entity_b = entity_names[0], entity_names[1] if len(entity_names) > 1 else entity_names[0]
            
            # Create nodes: Entity, Subgroup, Outcome
            edges = [("Subgroup", "Outcome"), ("Entity", "Outcome")]
            
            # Extract rates for CPDs
            # Use overall rates as priors
            overall_rates = structure["overall_rates"]
            prior_success = overall_rates[0]/100 if overall_rates else 0.5
            
            # Use subgroup data for conditional probabilities
            subgroup_probs = {}
            for sg_data in subgroup_data:
                sg_name, rates = sg_data
                if len(rates) >= 2:
                    # Assume first rate is for entity_a, second for entity_b in that subgroup
                    subgroup_probs[sg_name] = {
                        entity_a: rates[0]/100 if rates[0] <= 100 else 0.01,
                        entity_b: rates[1]/100 if len(rates) > 1 and rates[1] <= 100 else 0.01
                    }
            
            # Build CPD for Outcome given Entity and Subgroup
            if subgroup_probs:
                # Create CPD table
                cpd_values = []
                for entity in [entity_a, entity_b]:
                    for sg in subgroup_probs.keys():
                        prob = subgroup_probs[sg].get(entity, 0.5)
                        cpd_values.append([prob, 1-prob])  # [P(success), P(failure)]
                
                cpd_specs["Outcome"] = {
                    "variables": ["Entity", "Subgroup"],
                    "cardinality": [2, len(subgroup_probs)],
                    "values": cpd_values
                }
                
                # Build the Bayesian network
                bn_model = build_bn(edges, cpd_specs)
                
                # Use amino acid: compare conditional vs marginal to detect paradox
                paradox_detected = False
                if bn_model is not None:
                    # Compare P(Outcome|Entity=A) vs P(Outcome|Entity=B) in marginal
                    try:
                        # Query marginal probabilities
                        marginal_a = conditional_query(bn_model, ["Outcome"], {entity_a: 0})
                        marginal_b = conditional_query(bn_model, ["Outcome"], {entity_b: 0})
                        
                        if marginal_a is not None and marginal_b is not None:
                            # Compare success probabilities
                            success_a = marginal_a.get(1, 0.5) if isinstance(marginal_a, dict) else 0.5
                            success_b = marginal_b.get(1, 0.5) if isinstance(marginal_b, dict) else 0.5
                            
                            # Now check subgroup trends
                            subgroup_trends = []
                            for sg in subgroup_probs.keys():
                                sg_prob_a = subgroup_probs[sg].get(entity_a, 0.5)
                                sg_prob_b = subgroup_probs[sg].get(entity_b, 0.5)
                                subgroup_trends.append((sg, sg_prob_a, sg_prob_b))
                            
                            # Detect reversal: overall A > B but all subgroups A < B, or vice versa
                            if subgroup_trends:
                                overall_a_better = success_a > success_b
                                all_subgroups_opposite = all(
                                    (sg_prob_a < sg_prob_b) if overall_a_better else (sg_prob_a > sg_prob_b)
                                    for _, sg_prob_a, sg_prob_b in subgroup_trends
                                )
                                paradox_detected = all_subgroups_opposite
                    except:
                        paradox_detected = False
            else:
                bn_model = None
                paradox_detected = False
        else:
            bn_model = None
            paradox_detected = False

        # PHASE 2B: Fluid dynamics reasoning - compute "flow dominance"
        # Treat rates as velocities, compute momentum-like quantities
        entity_momentums = {}
        for ent_name, ent_data in entities.items():
            rates = ent_data.get("rates", [])
            if rates:
                # Convert to probabilities
                probs = [r/100 for r in rates if r <= 100]
                if probs:
                    # Use T1 primitive: entropy to measure uncertainty in rates
                    rate_entropy = entropy(probs) if len(probs) > 1 else 0
                    # Use T1 primitive: expected value of rates
                    ev = expected_value([(1/len(probs), p) for p in probs]) if probs else 0.5
                    # Fluid analogy: low entropy = laminar flow (consistent), high entropy = turbulent
                    # Momentum = expected rate * (1 - normalized entropy)
                    momentum = ev * (1 - rate_entropy / max(entropy([0.5, 0.5]), 0.001))
                    entity_momentums[ent_name] = momentum
        
        # Determine which entity has higher "effective flow" after accounting for subgroups
        if entity_momentums:
            # Use T1 primitive: confidence from agreement of multiple momentum estimates
            momentum_values = list(entity_momentums.values())
            confidence = confidence_from_agreement(momentum_values)
            
            # Find entity with highest momentum
            best_entity = max(entity_momentums.items(), key=lambda x: x[1])[0] if entity_momentums else ""
            
            # If paradox detected, the entity with better subgroup performance wins
            if paradox_detected and subgroup_data:
                # Re-evaluate based on subgroup consistency
                subgroup_scores = {}
                for ent_name in entity_momentums.keys():
                    # Count how many subgroups this entity wins in
                    wins = 0
                    for sg, rates in subgroup_data:
                        if len(rates) >= 2:
                            # Find which rate corresponds to this entity
                            # Simple heuristic: assume order matches entity_names
                            idx = list(entity_momentums.keys()).index(ent_name) if ent_name in entity_momentums else -1
                            if 0 <= idx < len(rates):
                                other_rates = [r for i, r in enumerate(rates) if i != idx]
                                if other_rates:
                                    # Check if this entity's rate is better than average of others
                                    if rates[idx] > sum(other_rates)/len(other_rates):
                                        wins += 1
                    subgroup_scores[ent_name] = wins
                
                if subgroup_scores:
                    best_entity = max(subgroup_scores.items(), key=lambda x: x[1])[0]
        else:
            best_entity = ""
            confidence = 0.5

        # PHASE 2C: Final answer determination
        # Extract what the question is asking for
        computed_answer = best_entity
        
        # If question asks "which is better", use best_entity
        # If question asks about paradox existence, answer is boolean
        if "paradox" in question.lower() or "reverse" in question.lower():
            computed_answer = "Yes" if paradox_detected else "No"
        elif "better" in question.lower() and best_entity:
            computed_answer = best_entity
        elif not computed_answer and entity_names:
            # Fallback: use first entity
            computed_answer = entity_names[0]

        # Use T1 primitive: Bayesian update on confidence
        prior_confidence = confidence if confidence > 0 else 0.5
        likelihood = 0.8 if paradox_detected else 0.6
        updated_confidence = bayesian_update(prior_confidence, likelihood)
        if updated_confidence is None:
            updated_confidence = prior_confidence

        return {
            "answer": str(computed_answer),
            "confidence": updated_confidence,
            "paradox_detected": paradox_detected,
            "reasoning": f"Fluid dynamics analysis: Entity momentum comparison with subgroup laminar flow analysis. {'Paradox detected: reverse flow in subgroups.' if paradox_detected else 'Consistent flow patterns.'}",
            "entity_momentums": entity_momentums
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or containment of computed answer
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
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        scores = [item["score"] for item in scored]
        if scores:
            max_score = max(scores)
            min_score = min(scores)
            if max_score > min_score:
                # Normalize to [0, 1] range
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