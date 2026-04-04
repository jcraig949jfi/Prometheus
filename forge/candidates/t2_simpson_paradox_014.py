import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, expected_value
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, compare_conditional_marginal, detect_confounders

class ReasoningTool:
    """auction_theory x pgmpy_acids - simpson_paradox"""

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

        # Find entity names (capitalized phrases, often hospital/drug names)
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        potential_entities = re.findall(entity_pattern, prompt)
        # Filter out common words and keep likely entities
        common_words = {'The', 'A', 'An', 'In', 'For', 'And', 'But', 'Or', 'When', 'Which', 'What', 'How'}
        entities = [e for e in potential_entities if e not in common_words and len(e.split()) <= 3]

        # Find all percentages and associate with nearest preceding entity
        percent_pattern = r'(\d+(?:\.\d+)?)%'
        percentages = re.findall(percent_pattern, prompt)
        percentages = [float(p) for p in percentages]

        # Find subgroup labels (e.g., 'Men', 'Women', 'Severe', 'Mild')
        subgroup_keywords = ['men', 'women', 'male', 'female', 'severe', 'mild', 'young', 'old', 'group']
        subgroups = []
        for line in lines:
            words = line.lower().split()
            for kw in subgroup_keywords:
                if kw in words:
                    # Get the capitalized version
                    idx = words.index(kw)
                    if idx < len(words):
                        subgroups.append(words[idx].title())

        # Structure data
        structure = {
            "entities": list(set(entities)),
            "subgroups": list(set(subgroups)),
            "percentages": percentages,
            "question": question,
            "raw_lines": lines
        }
        return structure

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use auction theory as scaffold: treat subgroups as bidders, aggregated outcome as auctioneer's revenue.
        Simpson's paradox occurs when the 'auction' (aggregation) selects a different winner than subgroup-wise bidding.
        Build Bayesian network to model confounding, compute which entity is truly better."""
        entities = structure["entities"]
        percentages = structure["percentages"]
        subgroups = structure["subgroups"]
        question = structure["question"]

        if len(entities) < 2 or len(percentages) < 4:
            # Fallback: simple majority if data insufficient
            if percentages:
                avg_percent = sum(percentages) / len(percentages)
                # Map loosely to entities (first entity gets first half of percentages)
                midpoint = len(percentages) // 2
                entity1_avg = sum(percentages[:midpoint]) / midpoint if midpoint > 0 else 0
                entity2_avg = sum(percentages[midpoint:]) / (len(percentages) - midpoint) if len(percentages) - midpoint > 0 else 0
                if entity1_avg > entity2_avg:
                    computed_answer = entities[0] if len(entities) > 0 else "Entity A"
                else:
                    computed_answer = entities[1] if len(entities) > 1 else "Entity B"
                return {"answer": computed_answer, "confidence": 0.5, "reasoning": "Fallback averaging"}

        # --- AUCTION THEORY SCAFFOLD ---
        # Subgroups are bidders, their success rates are bids.
        # The aggregated rate is the auctioneer's revenue when choosing the "winning" entity.
        # If the entity with higher aggregated rate is not the dominant bidder in all subgroups,
        # a Simpson reversal (paradox) is detected.
        # We'll model this as a Bayesian network: Subgroup -> Entity -> Success

        # Build simple BN: Subgroup (S) -> Entity (E) -> Success (Success)
        # CPDs: P(S) uniform, P(E|S) depends on subgroup distribution, P(Success|E,S) from extracted percentages
        edges = [("Subgroup", "Entity"), ("Entity", "Success"), ("Subgroup", "Success")]

        # Create CPDs from extracted data
        # We'll assume two entities and two subgroups for simplicity (common in Simpson cases)
        entity_names = entities[:2]
        subgroup_names = subgroups[:2] if subgroups else ["Group1", "Group2"]

        # Distribute percentages into a 2x2 table
        # We assume percentages are given in order: Entity1_Subgroup1, Entity1_Subgroup2, Entity2_Subgroup1, Entity2_Subgroup2
        if len(percentages) >= 4:
            rates = percentages[:4]
        else:
            # Pad with dummy values (should not happen due to earlier check)
            rates = [50.0, 50.0, 50.0, 50.0]

        # T1 PRIMITIVE 1: entropy of subgroup distribution
        subgroup_probs = [0.5, 0.5]  # assume equal
        subgroup_entropy = entropy(subgroup_probs)

        # T1 PRIMITIVE 2: expected value of success rates per entity
        # Entity1 expected success across subgroups
        ev_entity1 = expected_value([(0.5, rates[0]/100), (0.5, rates[1]/100)])
        ev_entity2 = expected_value([(0.5, rates[2]/100), (0.5, rates[3]/100)])

        # Determine which entity has higher aggregated (expected) success
        aggregated_better = entity_names[0] if ev_entity1 > ev_entity2 else entity_names[1]

        # Build Bayesian network to check for Simpson reversal
        cpd_specs = {
            "Subgroup": {
                "variable": "Subgroup",
                "variable_card": 2,
                "values": [[0.5], [0.5]],
                "evidence": [],
                "evidence_card": []
            },
            "Entity": {
                "variable": "Entity",
                "variable_card": 2,
                "values": [[0.5, 0.5], [0.5, 0.5]],  # P(Entity|Subgroup) - assume independent
                "evidence": ["Subgroup"],
                "evidence_card": [2]
            },
            "Success": {
                "variable": "Success",
                "variable_card": 2,
                "values": [
                    [rates[0]/100, rates[2]/100],  # Success given Subgroup=0, Entity=0 and Entity=1
                    [rates[1]/100, rates[3]/100]   # Success given Subgroup=1, Entity=0 and Entity=1
                ],
                "evidence": ["Subgroup", "Entity"],
                "evidence_card": [2, 2]
            }
        }

        # AMINO ACID 1: build Bayesian network
        model = build_bn(edges, cpd_specs)

        # AMINO ACID 2: compare conditional vs marginal to detect Simpson reversal
        simpson_detected = False
        if model is not None:
            # Compare P(Success | Entity=0) vs P(Success | Entity=1) in the aggregated data
            try:
                # Query marginal P(Success | Entity=0)
                prob_success_e0 = conditional_query(model, ["Success"], {"Entity": 0})
                prob_success_e1 = conditional_query(model, ["Success"], {"Entity": 1})
                if prob_success_e0 is not None and prob_success_e1 is not None:
                    # Check if subgroup trends reverse
                    # Entity0 better in subgroup0? rates[0] > rates[2]
                    # Entity0 better in subgroup1? rates[1] > rates[3]
                    subgroup0_better = rates[0] > rates[2]
                    subgroup1_better = rates[1] > rates[3]
                    aggregated_better_e0 = prob_success_e0[1] > prob_success_e1[1]  # index 1 = success=1
                    # Simpson reversal if aggregated preference differs from both subgroup preferences
                    if subgroup0_better == subgroup1_better and subgroup0_better != aggregated_better_e0:
                        simpson_detected = True
            except:
                pass

        # Determine which entity is truly better (accounting for Simpson)
        if simpson_detected:
            # When Simpson occurs, the entity better in ALL subgroups is the true winner
            if rates[0] > rates[2] and rates[1] > rates[3]:
                true_better = entity_names[0]
            elif rates[2] > rates[0] and rates[3] > rates[1]:
                true_better = entity_names[1]
            else:
                true_better = aggregated_better  # fallback
            reasoning = f"Simpson's paradox detected (aggregated vs subgroup reversal). True better entity is {true_better}."
        else:
            true_better = aggregated_better
            reasoning = f"No Simpson reversal. Aggregated better entity is {true_better}."

        # T1 PRIMITIVE 3: confidence from agreement between subgroup trends and aggregated
        agreement_scores = []
        if rates[0] > rates[2]:
            agreement_scores.append(1.0 if true_better == entity_names[0] else 0.0)
        if rates[1] > rates[3]:
            agreement_scores.append(1.0 if true_better == entity_names[0] else 0.0)
        if rates[2] > rates[0]:
            agreement_scores.append(1.0 if true_better == entity_names[1] else 0.0)
        if rates[3] > rates[1]:
            agreement_scores.append(1.0 if true_better == entity_names[1] else 0.0)
        confidence = confidence_from_agreement(agreement_scores) if agreement_scores else 0.5

        # AMINO ACID 3: detect confounders (Subgroup is the confounder here)
        confounders = []
        if model is not None:
            confounders = detect_confounders(model, "Entity", "Success")
            if confounders:
                reasoning += f" Confounder detected: {confounders}."

        return {
            "answer": true_better,
            "confidence": confidence,
            "reasoning": reasoning,
            "simpson_detected": simpson_detected,
            "aggregated_better": aggregated_better
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        scored = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate text
            if computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity between reasoning text and candidate
                score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            scored.append({
                "candidate": candidate,
                "raw_score": score,
                "confidence": reasoning_result["confidence"]
            })
        return scored

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores with confidence weighting."""
        calibrated = []
        for item in scored:
            # Adjust score by confidence (higher confidence strengthens score)
            adjusted = item["raw_score"] * (0.5 + 0.5 * item["confidence"])
            calibrated.append({
                "candidate": item["candidate"],
                "score": adjusted,
                "raw_score": item["raw_score"],
                "confidence": item["confidence"]
            })
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