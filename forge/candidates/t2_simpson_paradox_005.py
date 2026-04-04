import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, expected_value
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, compare_conditional_marginal, detect_confounders

class ReasoningTool:
    """feedback_systems x pgmpy_acids - simpson_paradox"""

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
        entity_pattern = r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b'
        potential_entities = re.findall(entity_pattern, prompt)
        # Filter: entities that appear near numbers/percentages
        entities = {}
        for ent in set(potential_entities):
            # Look for lines containing this entity
            ent_lines = [line for line in lines if ent in line]
            if not ent_lines:
                continue
            # Extract all percentages from those lines
            rates = []
            for line in ent_lines:
                percents = re.findall(r'([0-9]+\.?[0-9]*)%', line)
                rates.extend([float(p) for p in percents])
            if rates:
                entities[ent] = {"rates": rates, "context": ent_lines[0][:100]}

        # Find subgroups (often indicated by colons, parentheses, or "for")
        subgroup_pattern = r'(?:for|among|in)\s+([^.,;:]+?)(?:\.|,|;)'
        subgroups = re.findall(subgroup_pattern, prompt.lower())
        subgroups = [sg.strip() for sg in subgroups if len(sg.split()) <= 5]

        # Find overall and subgroup rates
        rate_matches = re.findall(r'([0-9]+\.?[0-9]*)%', prompt)
        all_rates = [float(r) for r in rate_matches]

        return {
            "entities": entities,
            "subgroups": subgroups[:4],  # Limit to plausible number
            "rates": all_rates,
            "question": question,
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use feedback systems (stability analysis) to detect reversal trends."""
        entities = structure["entities"]
        rates = structure["rates"]
        question = structure["question"]

        # FEEDBACK SYSTEMS SCAFFOLD: Treat aggregated vs. subgroup trends as
        # competing feedback loops. A reversal indicates instability where
        # the aggregated loop dominates but subgroup loops have opposite sign.
        # We model each entity's rates as a dynamical system and check for
        # sign changes (positive vs. negative feedback).

        # T1 PRIMITIVE 1: entropy of rates as a measure of disorder in the system
        if rates:
            rate_probs = [r/100 for r in rates]
            # Normalize to distribution
            total = sum(rate_probs)
            if total > 0:
                norm_probs = [p/total for p in rate_probs]
                system_entropy = entropy(norm_probs)
            else:
                system_entropy = 1.0
        else:
            system_entropy = 1.0

        # Build a simple Bayesian network to model confounding
        # Nodes: Entity -> Outcome, with Subgroup as confounder
        edges = [("Subgroup", "Entity"), ("Subgroup", "Outcome"), ("Entity", "Outcome")]
        
        # Use extracted rates for CPDs if we have enough
        cpd_specs = None
        if len(rates) >= 4:
            # Assume first two rates are for entity A, next two for entity B
            # This is a simplification; real extraction would map better
            r1, r2, r3, r4 = rates[:4]
            cpd_specs = {
                "Subgroup": {"card": 2, "values": [[0.5, 0.5]]},
                "Entity": {
                    "card": 2,
                    "values": [[0.9, 0.1], [0.1, 0.9]],  # Entity depends on subgroup
                    "evidence": ["Subgroup"],
                    "evidence_card": [2]
                },
                "Outcome": {
                    "card": 2,
                    "values": [
                        [r1/100, 1 - r1/100],  # Entity=0, Subgroup=0
                        [r2/100, 1 - r2/100],  # Entity=0, Subgroup=1
                        [r3/100, 1 - r3/100],  # Entity=1, Subgroup=0
                        [r4/100, 1 - r4/100]   # Entity=1, Subgroup=1
                    ],
                    "evidence": ["Entity", "Subgroup"],
                    "evidence_card": [2, 2]
                }
            }

        # AMINO ACID 1: build Bayesian network
        bn_model = build_bn(edges, cpd_specs)

        paradox_detected = False
        confounders = []
        target_entity = None
        confidence = 0.5

        if bn_model is not None:
            # AMINO ACID 2: detect confounders
            confounders = detect_confounders(bn_model, "Entity", "Outcome")
            
            # AMINO ACID 3: compare conditional vs marginal for paradox detection
            if cpd_specs and "Entity" in bn_model.nodes():
                try:
                    # Compare P(Outcome=1 | Entity=0) vs P(Outcome=1 | Entity=1)
                    # and check if conditioning on Subgroup reverses trend
                    result_0 = conditional_query(bn_model, ["Outcome"], {"Entity": 0})
                    result_1 = conditional_query(bn_model, ["Outcome"], {"Entity": 1})
                    if result_0 and result_1:
                        prob_0 = result_0.get(1, 0.0)
                        prob_1 = result_1.get(1, 0.0)
                        # Check subgroup reversal
                        result_0_sub0 = conditional_query(bn_model, ["Outcome"], {"Entity": 0, "Subgroup": 0})
                        result_1_sub0 = conditional_query(bn_model, ["Outcome"], {"Entity": 1, "Subgroup": 0})
                        result_0_sub1 = conditional_query(bn_model, ["Outcome"], {"Entity": 0, "Subgroup": 1})
                        result_1_sub1 = conditional_query(bn_model, ["Outcome"], {"Entity": 1, "Subgroup": 1})
                        
                        if (result_0_sub0 and result_1_sub0 and result_0_sub1 and result_1_sub1):
                            prob_0_sub0 = result_0_sub0.get(1, 0.0)
                            prob_1_sub0 = result_1_sub0.get(1, 0.0)
                            prob_0_sub1 = result_0_sub1.get(1, 0.0)
                            prob_1_sub1 = result_1_sub1.get(1, 0.0)
                            
                            # FEEDBACK SYSTEMS: Check for sign reversal
                            # Overall trend: prob_1 vs prob_0
                            # Subgroup trends: prob_1_sub* vs prob_0_sub*
                            overall_better = prob_1 > prob_0
                            subgroup0_better = prob_1_sub0 > prob_0_sub0
                            subgroup1_better = prob_1_sub1 > prob_0_sub1
                            
                            # Paradox if overall trend differs from both subgroup trends
                            if (overall_better != subgroup0_better) and (overall_better != subgroup1_better):
                                paradox_detected = True
                                # The entity with higher subgroup rates is actually better
                                if prob_0_sub0 > prob_1_sub0 and prob_0_sub1 > prob_1_sub1:
                                    target_entity = "Entity0"  # Placeholder
                                else:
                                    target_entity = "Entity1"
                except Exception:
                    pass

        # If Bayesian network fails, fall back to simpler rate comparison
        if not target_entity and entities:
            # T1 PRIMITIVE 2: expected value of rates for each entity
            entity_scores = {}
            for ent, data in entities.items():
                rates_ent = data["rates"]
                if rates_ent:
                    # Create (probability, value) pairs assuming uniform probability
                    prob = 1.0 / len(rates_ent)
                    outcomes = [(prob, r) for r in rates_ent]
                    entity_scores[ent] = expected_value(outcomes)
                else:
                    entity_scores[ent] = 0.0
            
            # Find entity with highest average rate
            if entity_scores:
                target_entity = max(entity_scores.items(), key=lambda x: x[1])[0]
        
        # Determine answer from question
        computed_answer = ""
        if target_entity:
            computed_answer = target_entity
        elif paradox_detected:
            computed_answer = "paradox_detected"
        else:
            # Default: pick first entity
            computed_answer = list(entities.keys())[0] if entities else "unknown"

        # T1 PRIMITIVE 3: confidence from agreement of multiple signals
        signals = []
        if system_entropy < 0.7:  # Low entropy suggests clear pattern
            signals.append(0.8)
        if paradox_detected:
            signals.append(0.9)
        if confounders:
            signals.append(0.7)
        if len(signals) > 0:
            confidence = confidence_from_agreement(signals)
        else:
            confidence = 0.5

        return {
            "answer": computed_answer,
            "confidence": confidence,
            "paradox_detected": paradox_detected,
            "confounders": confounders,
            "reasoning": f"Feedback stability analysis: entropy={system_entropy:.2f}, paradox={paradox_detected}"
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
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
        """Simple calibration: ensure scores are in [0,1] and add small tie-breaking."""
        if not scored:
            return scored
        
        # Normalize to max score = 1.0
        max_score = max(item["score"] for item in scored)
        if max_score > 0:
            for item in scored:
                item["score"] = item["score"] / max_score
        
        # Add tiny tie-breaking based on candidate length (shorter preferred)
        for i, item in enumerate(scored):
            item["score"] += (len(item["candidate"]) * 1e-6)
        
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