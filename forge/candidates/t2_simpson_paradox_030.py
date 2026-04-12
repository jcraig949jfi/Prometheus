import re
import zlib
from typing import Dict, List, Any, Optional

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, topological_sort
from forge.amino_acids.pgmpy_acids import compare_conditional_marginal, build_bn


class ReasoningTool:
    """Auction theory x Bayesian networks - Simpson's paradox detection"""

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
        lines = [line.strip() for line in prompt.split('\n') if line.strip()]
        
        # Find all percentages
        percentages = []
        for line in lines:
            matches = re.findall(r'([0-9]+\.?[0-9]*)%', line)
            percentages.extend([float(m) for m in matches])
        
        # Find entity names (capitalized multi-word phrases)
        entities = {}
        entity_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        
        # Look for hospital/drug/entity names
        for line in lines:
            matches = re.findall(entity_pattern, line)
            for match in matches:
                if len(match.split()) <= 3 and match not in ['Simpson', 'Paradox', 'Which', 'What']:
                    if match not in entities:
                        entities[match] = {"rates": [], "subgroups": []}
        
        # Extract subgroup structure
        subgroups = []
        subgroup_data = {}
        current_subgroup = None
        
        for line in lines:
            line_lower = line.lower()
            if any(word in line_lower for word in ['subgroup', 'group', 'category', 'type']):
                # Try to extract subgroup name
                sub_match = re.search(r'([A-Za-z]+\s+[A-Za-z]+)', line)
                if sub_match:
                    current_subgroup = sub_match.group(1)
                    subgroups.append(current_subgroup)
                    subgroup_data[current_subgroup] = {"entities": {}, "rates": []}
            elif current_subgroup and '%' in line:
                # Extract rates for this subgroup
                rates = re.findall(r'([0-9]+\.?[0-9]*)%', line)
                if rates:
                    subgroup_data[current_subgroup]["rates"] = [float(r) for r in rates]
        
        # Find the question
        question = ""
        for line in reversed(lines):
            if '?' in line:
                question = line.strip()
                break
        
        return {
            "entities": list(entities.keys()),
            "percentages": percentages,
            "subgroups": subgroups,
            "subgroup_data": subgroup_data,
            "question": question,
            "raw_lines": lines
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use auction theory framework to analyze Simpson's paradox.
        
        Auction theory concepts:
        - Entities are bidders competing for the "truth" resource
        - Subgroup rates are private valuations
        - Aggregated rates are public bids
        - The paradox occurs when the winner changes based on aggregation level
        - We use Bayesian networks to model the causal structure
        """
        
        entities = structure["entities"]
        subgroups = structure["subgroups"]
        subgroup_data = structure["subgroup_data"]
        percentages = structure["percentages"]
        
        if len(entities) < 2 or len(subgroups) < 2 or len(percentages) < 4:
            # Not enough data for proper analysis
            return {
                "answer": "Insufficient data",
                "confidence": 0.0,
                "reasoning": "Could not extract sufficient data for analysis"
            }
        
        # Build Bayesian network for causal analysis
        # Nodes: Subgroup -> Entity -> Outcome
        edges = []
        for subgroup in subgroups:
            for entity in entities[:2]:  # Use first two entities
                edges.append((subgroup, entity))
                edges.append((entity, "Outcome"))
        
        # Create CPDs using extracted percentages
        # We'll use the percentages as conditional probabilities
        cpd_specs = {}
        
        # For each entity, create CPD based on subgroup rates
        entity_rates = {}
        for i, entity in enumerate(entities[:2]):
            rates = []
            for subgroup in subgroups:
                if subgroup in subgroup_data and "rates" in subgroup_data[subgroup]:
                    sub_rates = subgroup_data[subgroup]["rates"]
                    if i < len(sub_rates):
                        rates.append(sub_rates[i] / 100.0)
            
            if rates:
                # Use entropy to measure uncertainty in subgroup rates
                # Higher entropy = more uniform rates across subgroups
                rate_entropy = entropy(rates) if len(rates) > 1 else 0.0
                entity_rates[entity] = {
                    "rates": rates,
                    "entropy": rate_entropy,
                    "avg_rate": sum(rates) / len(rates) if rates else 0.0
                }
        
        # Build the Bayesian network
        model = build_bn(edges, cpd_specs)
        
        # Use auction theory: entities bid with their rates
        # The "auction" has two stages: subgroup and aggregated
        subgroup_winners = []
        aggregated_winner = None
        
        # Stage 1: Subgroup auctions
        for subgroup in subgroups:
            if subgroup in subgroup_data and "rates" in subgroup_data[subgroup]:
                rates = subgroup_data[subgroup]["rates"]
                if len(rates) >= 2:
                    # Each entity's bid is their rate
                    bids = {entities[i]: rates[i] for i in range(min(2, len(rates)))}
                    # Winner is highest bidder
                    winner = max(bids.items(), key=lambda x: x[1])[0]
                    subgroup_winners.append(winner)
        
        # Stage 2: Aggregated auction
        if entity_rates:
            # Use Bayesian update to combine subgroup information
            prior = 0.5  # Neutral prior
            aggregated_scores = {}
            
            for entity in entities[:2]:
                if entity in entity_rates:
                    avg_rate = entity_rates[entity]["avg_rate"]
                    # Use entropy as uncertainty measure (lower entropy = more confident)
                    uncertainty = entity_rates[entity]["entropy"]
                    # Bayesian update: treat avg_rate as likelihood
                    # Higher uncertainty reduces effective likelihood
                    effective_likelihood = avg_rate * (1 - uncertainty)
                    posterior = bayesian_update(prior, effective_likelihood)
                    aggregated_scores[entity] = posterior
            
            if aggregated_scores:
                aggregated_winner = max(aggregated_scores.items(), key=lambda x: x[1])[0]
        
        # Check for Simpson's paradox using compare_conditional_marginal
        paradox_detected = False
        if model is not None and len(entities) >= 2:
            try:
                # Compare conditional vs marginal probabilities
                for entity in entities[:2]:
                    result = compare_conditional_marginal(
                        model, 
                        target="Outcome", 
                        condition_var=entity,
                        condition_val=1
                    )
                    if result and "difference" in result:
                        # Large difference indicates conditioning matters
                        if abs(result["difference"]) > 0.1:
                            paradox_detected = True
                            break
            except:
                pass
        
        # Determine final answer using topological sort of decision hierarchy
        decision_nodes = []
        if subgroup_winners:
            decision_nodes.extend(subgroup_winners)
        if aggregated_winner:
            decision_nodes.append(aggregated_winner)
        
        # Create edges for topological sort: subgroup -> aggregated
        decision_edges = []
        for i in range(len(subgroup_winners) - 1):
            decision_edges.append((subgroup_winners[i], subgroup_winners[i + 1]))
        if subgroup_winners and aggregated_winner:
            decision_edges.append((subgroup_winners[-1], aggregated_winner))
        
        # Use topological sort to find the ultimate decision
        final_decision = None
        if decision_edges:
            sorted_nodes = topological_sort(decision_edges)
            if sorted_nodes:
                final_decision = sorted_nodes[-1]  # Last node in topological order
        
        # If topological sort fails or gives no answer, use aggregated winner
        if not final_decision and aggregated_winner:
            final_decision = aggregated_winner
        
        # Calculate confidence using agreement between different methods
        confidence_scores = []
        
        # 1. Agreement between subgroup winners
        if subgroup_winners:
            unique_winners = len(set(subgroup_winners))
            agreement_score = 1.0 - (unique_winners - 1) / len(subgroups) if len(subgroups) > 0 else 0.0
            confidence_scores.append(agreement_score)
        
        # 2. Bayesian posterior strength
        if aggregated_scores and aggregated_winner in aggregated_scores:
            posterior_strength = abs(aggregated_scores[aggregated_winner] - 0.5) * 2
            confidence_scores.append(posterior_strength)
        
        # 3. Paradox detection confidence
        paradox_confidence = 1.0 if paradox_detected else 0.5
        confidence_scores.append(paradox_confidence)
        
        # Final confidence from agreement of different methods
        confidence = 0.0
        if confidence_scores:
            confidence = confidence_from_agreement(confidence_scores)
        
        # Prepare reasoning explanation
        reasoning_parts = []
        if paradox_detected:
            reasoning_parts.append("Simpson's paradox detected: subgroup trends reverse in aggregate.")
        if subgroup_winners:
            reasoning_parts.append(f"Subgroup winners: {', '.join(set(subgroup_winners))}.")
        if aggregated_winner:
            reasoning_parts.append(f"Aggregated analysis favors {aggregated_winner}.")
        
        reasoning = " ".join(reasoning_parts) if reasoning_parts else "No clear pattern detected."
        
        return {
            "answer": final_decision if final_decision else "Cannot determine",
            "confidence": confidence,
            "reasoning": reasoning,
            "paradox_detected": paradox_detected,
            "subgroup_winners": list(set(subgroup_winners)) if subgroup_winners else [],
            "aggregated_winner": aggregated_winner
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on match with computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        scored = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match of computed answer
            if computed_answer and computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity between reasoning and candidate
                base_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
            # Adjust by confidence
            adjusted_score = base_score * (0.5 + 0.5 * confidence)
            
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
            min_score = min(scores)
            max_score = max(scores)
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        
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