import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, expected_value
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, compare_conditional_marginal
from forge.amino_acids.nashpy_acids import find_equilibria, is_dominated


class ReasoningTool:
    """Game theory x Bayesian networks - Simpson's paradox detection"""

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
        
        # Find all percentage values
        percentages = []
        for line in lines:
            matches = re.findall(r'(\d+(?:\.\d+)?)%', line)
            percentages.extend([float(m) for m in matches])
        
        # Find entity names (capitalized multi-word phrases)
        entities = {}
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        
        for line in lines:
            matches = re.findall(entity_pattern, line)
            for match in matches:
                if match not in entities and len(match.split()) <= 3:  # Avoid long phrases
                    entities[match] = {"rates": [], "context": line}
        
        # Try to associate percentages with entities based on proximity
        for entity in entities:
            context = entities[entity]["context"]
            # Find percentages in the same sentence
            local_percents = re.findall(r'(\d+(?:\.\d+)?)%', context)
            entities[entity]["rates"] = [float(p) for p in local_percents]
        
        # If no rates found for entities, use all percentages in order
        if not any(entities[e]["rates"] for e in entities) and percentages:
            entity_list = list(entities.keys())
            for i, p in enumerate(percentages):
                if i < len(entity_list):
                    entities[entity_list[i]]["rates"].append(p)
        
        # Extract subgroup labels (like "men", "women", "young", "old")
        subgroups = []
        common_subgroups = ["men", "women", "male", "female", "young", "old", "severe", "mild", 
                           "treatment", "control", "group a", "group b", "category"]
        for line in lines:
            line_lower = line.lower()
            for sg in common_subgroups:
                if sg in line_lower and sg not in subgroups:
                    subgroups.append(sg)
        
        return {
            "entities": entities,
            "percentages": percentages,
            "subgroups": subgroups,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use game theory and Bayesian networks to detect Simpson's paradox and find the correct entity."""
        entities = structure["entities"]
        percentages = structure["percentages"]
        question = structure["question"]
        
        if not entities:
            return {"answer": "", "confidence": 0.0, "reasoning": "No entities found"}
        
        # GAME THEORY APPROACH: Treat entities as players in a coordination game
        # Each entity's "strategy" is its aggregated vs subgroup performance
        # We look for Nash equilibria where the paradox creates conflicting incentives
        
        # Step 1: Build payoff matrices based on extracted rates
        entity_names = list(entities.keys())
        
        if len(entity_names) >= 2 and len(percentages) >= 4:
            # Create a simple 2x2 game: Entity A vs Entity B
            # Strategy 0: Trust aggregated data
            # Strategy 1: Trust subgroup data
            
            # Extract rates for the game
            rates_a = entities[entity_names[0]]["rates"] if entities[entity_names[0]]["rates"] else [50.0]
            rates_b = entities[entity_names[1]]["rates"] if len(entity_names) > 1 and entities[entity_names[1]]["rates"] else [50.0]
            
            # Normalize rates to 0-1 scale
            norm_a = [r/100.0 for r in rates_a[:2]] if len(rates_a) >= 2 else [0.5, 0.5]
            norm_b = [r/100.0 for r in rates_b[:2]] if len(rates_b) >= 2 else [0.5, 0.5]
            
            # Payoff matrix A (row player = Entity A's perspective)
            # Rows: A's strategies (0=aggregated, 1=subgroup)
            # Columns: B's strategies (0=aggregated, 1=subgroup)
            payoff_a = [
                [norm_a[0] - norm_b[0], norm_a[0] - norm_b[1]],  # A uses aggregated
                [norm_a[1] - norm_b[0], norm_a[1] - norm_b[1]]   # A uses subgroup
            ]
            
            # Payoff matrix B (column player = Entity B's perspective)
            payoff_b = [
                [norm_b[0] - norm_a[0], norm_b[1] - norm_a[0]],
                [norm_b[0] - norm_a[1], norm_b[1] - norm_a[1]]
            ]
            
            # CRITICAL PRIMITIVE 1: Find Nash equilibria
            equilibria = find_equilibria(payoff_a, payoff_b)
            
            # CRITICAL PRIMITIVE 2: Check if strategies are dominated
            a_dominated_0 = is_dominated(payoff_a, 0, player_is_row=True)
            a_dominated_1 = is_dominated(payoff_a, 1, player_is_row=True)
            
            # Analyze the game theory results
            paradox_detected = False
            if equilibria:
                # Check if there are multiple equilibria (coordination problem)
                if len(equilibria) > 1:
                    paradox_detected = True
                # Check if aggregated strategy is dominated
                if a_dominated_0 and not a_dominated_1:
                    paradox_detected = True
            
            # Step 2: Bayesian network to model the causal structure
            # Build a simple BN: Subgroup -> Entity -> Outcome
            
            # CRITICAL AMINO ACID: Build Bayesian network
            edges = [("Subgroup", "Entity"), ("Entity", "Outcome")]
            
            # Use extracted percentages for CPDs
            if len(percentages) >= 4:
                # Convert percentages to probabilities
                probs = [p/100.0 for p in percentages[:4]]
                
                cpd_specs = {
                    "Subgroup": {"card": 2, "values": [[0.5, 0.5]]},
                    "Entity": {
                        "card": 2,
                        "values": [[probs[0] if probs[0] <= 1.0 else 0.5, 
                                  1 - (probs[0] if probs[0] <= 1.0 else 0.5)],
                                  [probs[1] if probs[1] <= 1.0 else 0.5, 
                                  1 - (probs[1] if probs[1] <= 1.0 else 0.5)]],
                        "evidence": ["Subgroup"],
                        "evidence_card": [2]
                    },
                    "Outcome": {
                        "card": 2,
                        "values": [[probs[2] if probs[2] <= 1.0 else 0.5, 
                                  1 - (probs[2] if probs[2] <= 1.0 else 0.5)],
                                  [probs[3] if probs[3] <= 1.0 else 0.5, 
                                  1 - (probs[3] if probs[3] <= 1.0 else 0.5)]],
                        "evidence": ["Entity"],
                        "evidence_card": [2]
                    }
                }
                
                model = build_bn(edges, cpd_specs)
                
                if model:
                    # CRITICAL AMINO ACID: Compare conditional vs marginal
                    comparison = compare_conditional_marginal(
                        model, "Outcome", "Entity", 0
                    )
                    
                    if comparison:
                        marginal_diff = abs(comparison.get("marginal", 0.5) - 
                                          comparison.get("conditional", 0.5))
                        if marginal_diff > 0.1:  # Significant difference
                            paradox_detected = True
                    
                    # Query the network
                    query_result = conditional_query(model, ["Outcome"], {"Entity": 0})
                    if query_result:
                        entity_0_prob = query_result.get(1, 0.5)
                    else:
                        entity_0_prob = 0.5
                else:
                    entity_0_prob = 0.5
            else:
                entity_0_prob = 0.5
            
            # Step 3: Use Bayesian update to combine evidence
            
            # CRITICAL PRIMITIVE 3: Bayesian update
            prior = 0.5  # Neutral prior
            likelihood = entity_0_prob
            
            # Adjust likelihood based on game theory results
            if paradox_detected:
                likelihood = 1.0 - likelihood  # Reverse due to paradox
            
            posterior = bayesian_update(prior, likelihood)
            
            # CRITICAL PRIMITIVE 4: Entropy of the decision
            probs_dist = [posterior, 1 - posterior]
            decision_entropy = entropy(probs_dist)
            
            # Determine which entity is better
            if len(entity_names) >= 2:
                # Use posterior probability to decide
                if posterior > 0.5:
                    computed_answer = entity_names[0]
                else:
                    computed_answer = entity_names[1]
            else:
                computed_answer = entity_names[0] if entity_names else ""
            
            # CRITICAL PRIMITIVE 5: Confidence from multiple signals
            signals = []
            if 'posterior' in locals():
                signals.append(posterior)
            if 'entity_0_prob' in locals():
                signals.append(entity_0_prob)
            if 'decision_entropy' in locals():
                signals.append(1.0 - decision_entropy)  # Convert entropy to confidence
            
            if signals:
                confidence = confidence_from_agreement(signals)
            else:
                confidence = 0.5
            
            reasoning_text = f"Game theory analysis: "
            if paradox_detected:
                reasoning_text += "Simpson's paradox detected. "
                if equilibria and len(equilibria) > 1:
                    reasoning_text += f"Multiple Nash equilibria found ({len(equilibria)}). "
                if a_dominated_0:
                    reasoning_text += "Aggregated strategy is dominated. "
            else:
                reasoning_text += "No strong paradox detected. "
            
            reasoning_text += f"Bayesian posterior: {posterior:.3f}. "
            reasoning_text += f"Selected entity: {computed_answer}"
            
            return {
                "answer": computed_answer,
                "confidence": confidence,
                "reasoning": reasoning_text,
                "paradox_detected": paradox_detected,
                "posterior": posterior
            }
        
        # Fallback: Simple comparison if not enough data
        # Still use primitives in fallback path
        entity_rates = {}
        for name, data in entities.items():
            rates = data["rates"]
            if rates:
                # CRITICAL PRIMITIVE in fallback: Expected value
                outcomes = [(r/100.0, 1.0) for r in rates]
                entity_rates[name] = expected_value(outcomes)
            else:
                entity_rates[name] = 0.5
        
        if entity_rates:
            best_entity = max(entity_rates.items(), key=lambda x: x[1])[0]
            
            # Still compute entropy for confidence
            rates_list = list(entity_rates.values())
            if rates_list:
                norm_rates = [r/sum(rates_list) for r in rates_list] if sum(rates_list) > 0 else [1/len(rates_list)]*len(rates_list)
                fallback_entropy = entropy(norm_rates)
                confidence = 1.0 - fallback_entropy
            else:
                confidence = 0.5
            
            return {
                "answer": best_entity,
                "confidence": confidence,
                "reasoning": f"Fallback: Max expected value {entity_rates[best_entity]:.3f}",
                "paradox_detected": False,
                "posterior": entity_rates[best_entity]
            }
        
        return {"answer": "", "confidence": 0.0, "reasoning": "Insufficient data"}

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result.get("answer", "")
        reasoning_text = reasoning_result.get("reasoning", "")
        confidence = reasoning_result.get("confidence", 0.5)
        
        if not computed_answer:
            return [{"candidate": c, "score": 0.0} for c in candidates]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match of computed answer
            score = 0.0
            
            # Check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                score = 1.0 * confidence
            else:
                # Fallback: NCD similarity with reasoning text
                ncd_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
                score = ncd_score * confidence
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Simple normalization to 0-1 range
        scores = [item["raw_score"] for item in scored]
        if scores:
            min_score = min(scores)
            max_score = max(scores)
            if max_score > min_score:
                for item in scored:
                    item["score"] = (item["raw_score"] - min_score) / (max_score - min_score)
            else:
                for item in scored:
                    item["score"] = 0.5
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance between two strings."""
        if not a and not b:
            return 0.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)