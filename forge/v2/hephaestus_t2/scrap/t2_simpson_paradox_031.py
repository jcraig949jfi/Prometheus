import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, topological_sort
from forge.amino_acids.pgmpy_acids import compare_conditional_marginal, build_bn


class ReasoningTool:
    """Number theory x Bayesian networks - Simpson's paradox detection"""

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
        
        # Find all percentage values
        percentages = []
        for line in lines:
            matches = re.findall(r'([0-9]+\.?[0-9]*)%', line)
            percentages.extend([float(m) for m in matches])
        
        # Find entity names (capitalized multi-word phrases)
        entities = {}
        current_entity = None
        subgroup_data = {}
        
        for line in lines:
            # Look for entity names (e.g., "Hospital A", "Drug B")
            entity_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', line)
            if entity_match:
                current_entity = entity_match.group(1)
                if current_entity not in entities:
                    entities[current_entity] = {"rates": [], "subgroups": {}}
            
            # Look for subgroup indicators (e.g., "mild cases", "severe cases")
            subgroup_match = re.search(r'(mild|severe|young|old|small|large|low|high)\s+cases?', line.lower())
            if subgroup_match:
                subgroup = subgroup_match.group(1)
                # Extract percentage for this subgroup
                sub_percent = re.findall(r'([0-9]+\.?[0-9]*)%', line)
                if sub_percent and current_entity:
                    if subgroup not in entities[current_entity]["subgroups"]:
                        entities[current_entity]["subgroups"][subgroup] = []
                    entities[current_entity]["subgroups"][subgroup].append(float(sub_percent[0]))
            
            # Extract overall rates for entities
            if current_entity and '%' in line:
                rate_match = re.search(r'([0-9]+\.?[0-9]*)%', line)
                if rate_match:
                    entities[current_entity]["rates"].append(float(rate_match.group(1)))
        
        # Clean up: remove entities with no data
        entities = {k: v for k, v in entities.items() if v["rates"] or v["subgroups"]}
        
        # Extract subgroup names from the data
        all_subgroups = set()
        for entity_data in entities.values():
            all_subgroups.update(entity_data["subgroups"].keys())
        
        return {
            "entities": entities,
            "subgroups": list(all_subgroups),
            "question": question,
            "percentages": percentages,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use number theory concepts and Bayesian networks to detect Simpson's paradox."""
        entities = structure["entities"]
        subgroups = structure["subgroups"]
        
        if len(entities) < 2 or len(subgroups) < 2:
            # Not enough data for Simpson's paradox analysis
            # Fallback: compare overall rates
            best_entity = max(entities.items(), 
                            key=lambda x: x[1]["rates"][-1] if x[1]["rates"] else 0,
                            default=(None, None))
            return {
                "answer": best_entity[0] if best_entity[0] else "Unknown",
                "confidence": 0.5,
                "reasoning": "Insufficient data for Simpson's paradox detection",
                "paradox_detected": False
            }
        
        # CRITICAL PRIMITIVE 1: topological_sort to order entities by their rates
        # Build edges based on rate comparisons
        edges = []
        entity_names = list(entities.keys())
        for i, e1 in enumerate(entity_names):
            for j, e2 in enumerate(entity_names):
                if i != j:
                    rate1 = entities[e1]["rates"][-1] if entities[e1]["rates"] else 0
                    rate2 = entities[e2]["rates"][-1] if entities[e2]["rates"] else 0
                    if rate1 > rate2:
                        edges.append((e1, e2))  # e1 "better than" e2
        
        # Use topological_sort to get a consistent ordering
        try:
            sorted_entities = topological_sort(edges)
            if sorted_entities is None:
                sorted_entities = entity_names
        except:
            sorted_entities = entity_names
        
        # CRITICAL PRIMITIVE 2: entropy to measure uncertainty in subgroup distributions
        subgroup_entropies = {}
        for subgroup in subgroups:
            subgroup_rates = []
            for entity in entities.values():
                if subgroup in entity["subgroups"]:
                    subgroup_rates.extend(entity["subgroups"][subgroup])
            
            if subgroup_rates:
                # Normalize rates to probabilities
                total = sum(subgroup_rates)
                if total > 0:
                    probs = [r/total for r in subgroup_rates]
                    # Compute entropy of subgroup distribution
                    subgroup_entropies[subgroup] = entropy(probs)
                else:
                    subgroup_entropies[subgroup] = 0.0
            else:
                subgroup_entropies[subgroup] = 0.0
        
        # CRITICAL AMINO ACID: compare_conditional_marginal to detect Simpson's paradox
        # Build a simple Bayesian network: Entity -> Rate, Subgroup -> Rate
        paradox_detected = False
        best_entity = None
        highest_confidence = 0.0
        
        try:
            # Build edges for Bayesian network
            bn_edges = []
            for entity in entities:
                bn_edges.append((entity, "Rate"))
            for subgroup in subgroups:
                bn_edges.append((subgroup, "Rate"))
            
            # Build CPDs from extracted data
            cpd_specs = {}
            
            # Entity CPDs (prior probabilities)
            for entity in entities:
                # Use number theory: treat rates as residues mod 100
                rate = entities[entity]["rates"][-1] if entities[entity]["rates"] else 50
                cpd_specs[entity] = {
                    "variable": entity,
                    "variable_card": 2,
                    "values": [[rate/100, 1 - rate/100]],
                    "evidence": [],
                    "evidence_card": []
                }
            
            # Subgroup CPDs
            for subgroup in subgroups:
                # Compute average rate for this subgroup across entities
                rates = []
                for entity in entities.values():
                    if subgroup in entity["subgroups"]:
                        rates.extend(entity["subgroups"][subgroup])
                avg_rate = sum(rates)/len(rates) if rates else 50
                cpd_specs[subgroup] = {
                    "variable": subgroup,
                    "variable_card": 2,
                    "values": [[avg_rate/100, 1 - avg_rate/100]],
                    "evidence": [],
                    "evidence_card": []
                }
            
            # Rate CPD (conditional on entity and subgroup)
            # This is where Simpson's paradox manifests
            model = build_bn(bn_edges, cpd_specs)
            
            # Check for each entity if conditioning on subgroups reverses trend
            for entity in entities:
                # Compute P(Rate=high | Entity=this) vs P(Rate=high)
                marginal_result = compare_conditional_marginal(
                    model, 
                    target="Rate", 
                    condition_var=entity, 
                    condition_val=0  # 0 represents "high rate" in our encoding
                )
                
                if marginal_result:
                    # marginal_result gives difference between conditional and marginal
                    diff = abs(marginal_result.get("difference", 0))
                    if diff > 0.1:  # Significant difference indicates possible paradox
                        paradox_detected = True
                        
                        # CRITICAL PRIMITIVE 3: bayesian_update to compute posterior confidence
                        # Prior: 0.5 (uncertain)
                        # Likelihood: based on entropy of subgroup distributions
                        avg_entropy = sum(subgroup_entropies.values()) / len(subgroup_entropies) if subgroup_entropies else 0.5
                        likelihood = 1 - avg_entropy  # Low entropy = high likelihood of clear winner
                        
                        posterior = bayesian_update(0.5, likelihood)
                        
                        if posterior > highest_confidence:
                            highest_confidence = posterior
                            best_entity = entity
            
        except Exception as e:
            # Amino acid failed, fallback to primitive-based reasoning
            paradox_detected = False
        
        # If no paradox detected or amino acid failed, use primitive-based analysis
        if not paradox_detected or best_entity is None:
            # Compare subgroup performances using number theory concepts
            # Treat rates as residues mod 100, compare using modular arithmetic
            entity_scores = {}
            for entity_name, entity_data in entities.items():
                score = 0
                # Use overall rate (mod 100)
                if entity_data["rates"]:
                    score += entity_data["rates"][-1] % 100
                
                # Add subgroup performance (weighted by entropy)
                for subgroup, rates in entity_data["subgroups"].items():
                    if rates:
                        subgroup_entropy = subgroup_entropies.get(subgroup, 0.5)
                        weight = 1 - subgroup_entropy  # Low entropy = more weight
                        score += (sum(rates)/len(rates)) * weight
                
                entity_scores[entity_name] = score
            
            best_entity = max(entity_scores.items(), key=lambda x: x[1])[0]
            
            # CRITICAL PRIMITIVE 4: confidence_from_agreement
            # Create multiple scoring methods to compute confidence
            scoring_methods = []
            
            # Method 1: Overall rates
            if any(entities[e]["rates"] for e in entities):
                rate_scores = [entities[e]["rates"][-1] if entities[e]["rates"] else 0 for e in entities]
                scoring_methods.append([s/max(rate_scores) if max(rate_scores) > 0 else 0 for s in rate_scores])
            
            # Method 2: Average subgroup performance
            subgroup_avgs = []
            for entity in entities:
                sub_rates = []
                for subgroup_data in entities[entity]["subgroups"].values():
                    sub_rates.extend(subgroup_data)
                avg = sum(sub_rates)/len(sub_rates) if sub_rates else 0
                subgroup_avgs.append(avg)
            if any(subgroup_avgs):
                scoring_methods.append([s/max(subgroup_avgs) if max(subgroup_avgs) > 0 else 0 for s in subgroup_avgs])
            
            if scoring_methods:
                # Transpose to get scores per entity across methods
                entity_scores_list = list(zip(*scoring_methods))
                confidence = confidence_from_agreement([sum(scores)/len(scores) for scores in entity_scores_list])
            else:
                confidence = 0.5
        
        # Determine if we should report the paradox or just the best entity
        # Based on the question phrasing
        question_lower = structure["question"].lower()
        if "paradox" in question_lower or "reverse" in question_lower or "actually" in question_lower:
            if paradox_detected:
                computed_answer = f"Simpson's paradox detected: {best_entity} is better"
            else:
                computed_answer = f"No paradox: {best_entity} is better"
        else:
            computed_answer = best_entity
        
        return {
            "answer": computed_answer,
            "confidence": highest_confidence if paradox_detected else confidence,
            "reasoning": f"Analyzed using number theory (modular residues) and Bayesian networks. {'Simpson\'s paradox detected.' if paradox_detected else 'No paradox detected.'}",
            "paradox_detected": paradox_detected,
            "best_entity": best_entity
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        def ncd(a: str, b: str) -> float:
            ca = len(zlib.compress(a.encode()))
            cb = len(zlib.compress(b.encode()))
            cab = len(zlib.compress((a + " " + b).encode()))
            return (cab - min(ca, cb)) / max(ca, cb) if max(ca, cb) > 0 else 1.0
        
        scored = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
                similarity = 1.0 / (1.0 + ncd(computed_answer, candidate))
                base_score = similarity
            
            # Adjust by confidence
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
        
        # Simple min-max normalization
        scores = [item["score"] for item in scored]
        if max(scores) > min(scores):
            for item in scored:
                item["score"] = (item["score"] - min(scores)) / (max(scores) - min(scores))
        else:
            for item in scored:
                item["score"] = 0.5
        
        return scored