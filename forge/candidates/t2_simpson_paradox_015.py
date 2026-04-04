import re
import zlib
from typing import Dict, List, Any

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, expected_value
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, compare_conditional_marginal

class ReasoningTool:
    """Thermodynamics x Bayesian Networks - Simpson's Paradox Detection"""

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

        # Find entity names (capitalized multi-word phrases that appear with rates)
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        potential_entities = re.findall(entity_pattern, prompt)

        # Find all percentages
        rate_pattern = r'(\d+(?:\.\d+)?)%'
        all_rates = [float(r) for r in re.findall(rate_pattern, prompt)]

        # Build structure: assume first entity is overall, then subgroups
        entities = {}
        if len(potential_entities) >= 2:
            main_entity = potential_entities[0]
            subgroup_entity = potential_entities[1]
            entities["overall"] = {"name": main_entity, "rates": []}
            entities["subgroup"] = {"name": subgroup_entity, "rates": []}

            # Simple heuristic: first rates are overall, later rates are subgroups
            if len(all_rates) >= 4:
                entities["overall"]["rates"] = all_rates[:2]
                entities["subgroup"]["rates"] = all_rates[2:4]
            elif len(all_rates) >= 2:
                entities["overall"]["rates"] = all_rates[:2]
                entities["subgroup"]["rates"] = []

        # Extract subgroup labels (like "men", "women", "severe", "mild")
        subgroup_labels = []
        label_keywords = ["men", "women", "male", "female", "severe", "mild", "young", "old"]
        for word in prompt.lower().split():
            if word in label_keywords and word not in subgroup_labels:
                subgroup_labels.append(word)

        return {
            "entities": entities,
            "question": question,
            "raw_rates": all_rates,
            "subgroup_labels": subgroup_labels,
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Thermodynamic reasoning: treat aggregated vs subgroup data as different energy states.
        Overall rates are high-temperature (mixed) states, subgroups are low-temperature (ordered) states.
        Simpson's paradox occurs when the 'free energy' (expected success) reverses between states.
        """
        entities = structure["entities"]
        raw_rates = structure["raw_rates"]
        question = structure["question"]

        # Use T1 primitives
        # 1. Compute entropy of overall vs subgroup distributions
        overall_rates = entities.get("overall", {}).get("rates", [])
        subgroup_rates = entities.get("subgroup", {}).get("rates", [])

        if overall_rates and subgroup_rates:
            # Normalize rates to probabilities
            overall_probs = [r/100 for r in overall_rates]
            subgroup_probs = [r/100 for r in subgroup_rates]

            # Thermodynamic concept: entropy measures disorder
            entropy_overall = entropy(overall_probs) if len(overall_probs) >= 2 else 0.0
            entropy_subgroup = entropy(subgroup_probs) if len(subgroup_probs) >= 2 else 0.0

            # 2. Bayesian update: treat overall rate as prior, subgroup as likelihood
            prior = overall_probs[0] if overall_probs else 0.5
            likelihood = subgroup_probs[0] if subgroup_probs else 0.5
            posterior = bayesian_update(prior, likelihood)
            if posterior is None:
                posterior = prior

            # 3. Expected value comparison
            # Assume binary outcomes: success (1) vs failure (0)
            if len(overall_rates) >= 2 and len(subgroup_rates) >= 2:
                # Overall expected success
                ev_overall = expected_value([(overall_rates[0]/100, 1), (1 - overall_rates[0]/100, 0)])
                # Subgroup expected success (average across subgroups)
                ev_subgroup = expected_value([(subgroup_rates[0]/100, 1), (subgroup_rates[1]/100, 1)])

                # Thermodynamic analogy: compare free energies
                free_energy_overall = -ev_overall if ev_overall is not None else 0
                free_energy_subgroup = -ev_subgroup if ev_subgroup is not None else 0

                # Detect reversal: which entity has higher success rate?
                overall_success = overall_rates[0] if overall_rates else 0
                subgroup_success_avg = sum(subgroup_rates[:2])/2 if len(subgroup_rates) >= 2 else 0

                if overall_success > subgroup_success_avg:
                    better_entity = entities.get("overall", {}).get("name", "Overall")
                else:
                    better_entity = entities.get("subgroup", {}).get("name", "Subgroup")

                # 4. Use amino acid: Bayesian network to check conditional vs marginal
                paradox_detected = False
                if len(raw_rates) >= 4:
                    try:
                        # Build simple BN: Treatment -> Outcome, with Subgroup as confounder
                        edges = [("Subgroup", "Outcome"), ("Treatment", "Outcome")]
                        # CPD: P(Outcome | Treatment, Subgroup) using extracted rates
                        # Assume rates correspond to P(success | treatment, subgroup)
                        cpd_specs = {
                            "Outcome": {
                                "variables": ["Treatment", "Subgroup"],
                                "values": [
                                    [raw_rates[2]/100, 1 - raw_rates[2]/100],  # Treatment A, Subgroup 1
                                    [raw_rates[3]/100, 1 - raw_rates[3]/100],  # Treatment A, Subgroup 2
                                    [raw_rates[0]/100, 1 - raw_rates[0]/100],  # Treatment B, Subgroup 1
                                    [raw_rates[1]/100, 1 - raw_rates[1]/100],  # Treatment B, Subgroup 2
                                ]
                            }
                        }
                        bn = build_bn(edges, cpd_specs)
                        if bn is not None:
                            # Compare P(Outcome | Treatment=A) vs P(Outcome | Treatment=B)
                            # This is a simplified check for reversal
                            result = compare_conditional_marginal(bn, "Outcome", "Treatment", "A")
                            if result is not None and "reversal" in str(result).lower():
                                paradox_detected = True
                    except Exception:
                        paradox_detected = False

                # 5. Confidence from agreement of multiple indicators
                indicators = []
                if entropy_overall > entropy_subgroup:
                    indicators.append(0.8)  # Higher disorder in aggregated data
                if posterior != prior:
                    indicators.append(0.7)  # Bayesian update shifted belief
                if abs(free_energy_overall - free_energy_subgroup) > 0.1:
                    indicators.append(0.9)  # Significant free energy difference
                if paradox_detected:
                    indicators.append(1.0)

                confidence = confidence_from_agreement(indicators) if indicators else 0.5

                # Determine answer: which entity is actually better?
                # Look for question cues
                if "better" in question.lower():
                    computed_answer = better_entity
                elif "paradox" in question.lower():
                    computed_answer = "Yes" if paradox_detected else "No"
                else:
                    # Default: return the entity with higher success
                    computed_answer = better_entity

                reasoning_text = f"Thermodynamic analysis: overall entropy={entropy_overall:.3f}, subgroup entropy={entropy_subgroup:.3f}. "
                reasoning_text += f"Free energy overall={free_energy_overall:.3f}, subgroup={free_energy_subgroup:.3f}. "
                reasoning_text += f"Paradox detected: {paradox_detected}. Better entity: {better_entity}"

                return {
                    "answer": computed_answer,
                    "confidence": confidence,
                    "reasoning": reasoning_text,
                    "better_entity": better_entity,
                    "paradox_detected": paradox_detected
                }

        # Fallback if extraction failed
        return {
            "answer": "Unknown",
            "confidence": 0.0,
            "reasoning": "Insufficient data extracted from prompt",
            "better_entity": "Unknown",
            "paradox_detected": False
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        better_entity = reasoning_result.get("better_entity", "")
        paradox_detected = reasoning_result.get("paradox_detected", False)

        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                score = 1.0
            # Secondary: check for better entity match
            elif better_entity and better_entity.lower() in candidate.lower():
                score = 0.8
            # Tertiary: check for paradox indication
            elif paradox_detected and ("yes" in candidate.lower() or "paradox" in candidate.lower()):
                score = 0.7
            elif not paradox_detected and ("no" in candidate.lower() or "not" in candidate.lower()):
                score = 0.7
            else:
                # Fallback: NCD similarity to reasoning text
                score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            results.append({"candidate": candidate, "raw_score": score})

        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence from reasoning result."""
        if not scored:
            return []

        # Normalize scores to [0, 1]
        raw_scores = [item["raw_score"] for item in scored]
        max_score = max(raw_scores) if raw_scores else 1.0
        min_score = min(raw_scores) if raw_scores else 0.0
        range_score = max_score - min_score if max_score > min_score else 1.0

        calibrated = []
        for item in scored:
            normalized = (item["raw_score"] - min_score) / range_score if range_score > 0 else 0.5
            # Apply slight smoothing
            calibrated_score = min(1.0, max(0.0, normalized))
            calibrated.append({
                "candidate": item["candidate"],
                "score": calibrated_score
            })

        return calibrated

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance between two strings."""
        if not a or not b:
            return 1.0
        try:
            ca = len(zlib.compress(a.encode()))
            cb = len(zlib.compress(b.encode()))
            cab = len(zlib.compress((a + " " + b).encode()))
            return (cab - min(ca, cb)) / max(ca, cb) if max(ca, cb) > 0 else 1.0
        except Exception:
            return 1.0