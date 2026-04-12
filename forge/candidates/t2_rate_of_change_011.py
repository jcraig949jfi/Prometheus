import re
import zlib
from typing import Dict, List, Any

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    solve_linear_system,
    expected_value,
    information_sufficiency
)
from forge.amino_acids.pgmpy_acids import (
    build_bn,
    conditional_query,
    detect_confounders
)


class ReasoningTool:
    """Acoustics x Bayesian networks - rate_of_change"""

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
        """Extract entities, time points, values, and question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find all percentage values and numbers
        numbers = re.findall(r'([0-9]+\.?[0-9]*)%?', prompt)
        percentages = re.findall(r'([0-9]+\.?[0-9]*)%', prompt)
        
        # Find time references
        time_patterns = [
            r'(?:year|month|day|week|hour|minute|second)s?\s+(\d+)',
            r'(?:time|period)\s+(\d+)',
            r't=(\d+)',
            r'(\d+)\s*(?:st|nd|rd|th)\s+(?:year|month|day)'
        ]
        times = []
        for pattern in time_patterns:
            times.extend(re.findall(pattern, prompt.lower()))
        
        # Find entity names (capitalized phrases)
        entities = {}
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        potential_entities = re.findall(entity_pattern, prompt)
        
        # Filter out common words and associate with nearby numbers
        common_words = {'The', 'A', 'An', 'In', 'On', 'At', 'To', 'For', 'With', 'By'}
        for entity in potential_entities:
            if entity in common_words or len(entity.split()) > 3:
                continue
            
            # Find numbers near this entity
            entity_start = prompt.find(entity)
            if entity_start >= 0:
                context = prompt[max(0, entity_start-50):min(len(prompt), entity_start+50)]
                nearby_numbers = re.findall(r'([0-9]+\.?[0-9]*)%?', context)
                if nearby_numbers:
                    entities[entity] = {
                        "values": [float(n) for n in nearby_numbers[:3]],
                        "context": context
                    }
        
        return {
            "question": question,
            "entities": entities,
            "numbers": [float(n) for n in numbers if n],
            "percentages": [float(p) for p in percentages],
            "times": [int(t) for t in times if t.isdigit()],
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use acoustics concepts (wave propagation, frequency change) to model rate of change."""
        entities = structure["entities"]
        numbers = structure["numbers"]
        percentages = structure["percentages"]
        times = structure["times"]
        question = structure["question"]
        
        # Acoustics framework: treat rate of change as frequency shift (Doppler effect)
        # Higher rate = higher frequency = more compressed waveform
        
        # 1. Use entropy to measure uncertainty in the data (acoustic noise level)
        if numbers:
            # Normalize numbers for entropy calculation
            norm_numbers = [abs(n)/max(abs(n) for n in numbers) if numbers else 0.5 for n in numbers]
            data_entropy = entropy(norm_numbers[:min(5, len(norm_numbers))])
        else:
            data_entropy = 0.5
        
        # 2. Build Bayesian network for causal relationships (acoustic propagation model)
        # Nodes: Time -> Value -> Rate -> FinalAnswer
        edges = [("Time", "Value"), ("Value", "Rate"), ("Rate", "FinalAnswer")]
        
        # Use extracted percentages as conditional probabilities
        cpd_specs = None
        if percentages:
            # Convert percentages to probabilities
            probs = [p/100.0 for p in percentages[:4]]
            if len(probs) >= 2:
                cpd_specs = {
                    "Time": {"card": 2, "values": [[0.5, 0.5]]},
                    "Value": {
                        "card": 2,
                        "values": [[probs[0], 1-probs[0]], [probs[1] if len(probs)>1 else 0.5, 1-(probs[1] if len(probs)>1 else 0.5)]],
                        "parents": ["Time"]
                    },
                    "Rate": {
                        "card": 2,
                        "values": [[probs[2] if len(probs)>2 else 0.6, 1-(probs[2] if len(probs)>2 else 0.6)], 
                                  [probs[3] if len(probs)>3 else 0.4, 1-(probs[3] if len(probs)>3 else 0.4)]],
                        "parents": ["Value"]
                    }
                }
        
        # 3. Use amino acid: build Bayesian network
        model = build_bn(edges, cpd_specs)
        
        # 4. Use amino acid: detect confounders (acoustic interference sources)
        confounders = None
        if model is not None:
            confounders = detect_confounders(model, "Time", "FinalAnswer")
        
        # 5. Use amino acid: conditional query for rate prediction
        rate_prob = None
        if model is not None:
            rate_prob = conditional_query(model, ["Rate"], {})
        
        # 6. Use solve_linear_system to compute rate from time-value pairs (wave equation)
        # Extract time-value pairs if available
        time_vals = []
        if times and numbers:
            # Pair times with numbers (simple pairing)
            for i in range(min(len(times), len(numbers))):
                time_vals.append((float(times[i]), numbers[i]))
        
        slope = None
        if len(time_vals) >= 2:
            # Solve for slope in y = mx + b
            A = [[t, 1] for t, _ in time_vals[:2]]
            b = [v for _, v in time_vals[:2]]
            solution = solve_linear_system(A, b)
            if solution:
                slope = solution[0]  # Rate of change (m in y = mx + b)
        
        # 7. Use expected_value for weighted average rate (acoustic energy)
        outcomes = []
        if numbers and percentages:
            # Create probability-value pairs
            for i in range(min(len(numbers), len(percentages))):
                prob = percentages[i]/100.0
                outcomes.append((prob, numbers[i]))
        
        expected_val = None
        if outcomes:
            expected_val = expected_value(outcomes[:3])
        
        # 8. Use information_sufficiency to check if we have enough data
        n_unknowns = 1  # We're trying to find the rate
        n_constraints = len(time_vals) if time_vals else len(numbers)
        sufficiency = information_sufficiency(n_unknowns, n_constraints)
        
        # 9. Use bayesian_update to refine rate estimate (acoustic signal processing)
        prior = 0.5
        likelihood = 0.7 if slope and abs(slope) > 0 else 0.3
        posterior = bayesian_update(prior, likelihood)
        
        # 10. Determine answer based on reasoning
        computed_answer = ""
        confidence = 0.5
        
        # Decision logic using load-bearing primitives:
        # 1. If slope from solve_linear_system is significant, use that
        if slope is not None:
            # Acoustics: frequency shift proportional to rate
            if abs(slope) > 10:  # High rate
                computed_answer = "increasing rapidly"
                confidence = min(0.9, posterior * 1.2)
            elif slope > 0:
                computed_answer = "increasing"
                confidence = posterior
            elif slope < 0:
                computed_answer = "decreasing"
                confidence = posterior
            else:
                computed_answer = "constant"
                confidence = 0.6
        # 2. Else if expected_value gives clear direction
        elif expected_val is not None and numbers:
            avg_val = sum(numbers)/len(numbers)
            if expected_val > avg_val * 1.1:
                computed_answer = "increasing"
                confidence = 0.7
            elif expected_val < avg_val * 0.9:
                computed_answer = "decreasing"
                confidence = 0.7
            else:
                computed_answer = "stable"
                confidence = 0.6
        # 3. Else if Bayesian network gives high probability
        elif rate_prob is not None and isinstance(rate_prob, dict):
            if "Rate" in rate_prob and len(rate_prob["Rate"]) >= 2:
                if rate_prob["Rate"][0] > 0.6:  # High probability of positive rate
                    computed_answer = "increasing"
                    confidence = rate_prob["Rate"][0]
                elif rate_prob["Rate"][1] > 0.6:  # High probability of negative rate
                    computed_answer = "decreasing"
                    confidence = rate_prob["Rate"][1]
                else:
                    computed_answer = "uncertain"
                    confidence = 0.5
        # 4. Fallback using entropy and sufficiency
        else:
            if data_entropy > 0.8:
                computed_answer = "volatile"
                confidence = 0.4
            elif sufficiency == "determined":
                computed_answer = "calculable"
                confidence = 0.6
            else:
                computed_answer = "insufficient data"
                confidence = 0.3
        
        # 11. Use confidence_from_agreement to finalize confidence
        confidence_sources = []
        if slope is not None:
            confidence_sources.append(min(0.9, abs(slope)/100.0))
        if expected_val is not None:
            confidence_sources.append(0.7)
        if rate_prob is not None:
            confidence_sources.append(0.6)
        if confidence_sources:
            final_confidence = confidence_from_agreement(confidence_sources)
        else:
            final_confidence = confidence
        
        # Extract entity name from question if possible
        answer_entity = ""
        for entity in entities:
            if entity.lower() in question.lower():
                answer_entity = entity
                break
        
        if answer_entity and computed_answer:
            final_answer = f"{answer_entity} is {computed_answer}"
        else:
            final_answer = computed_answer if computed_answer else "No clear answer"
        
        return {
            "answer": final_answer,
            "confidence": final_confidence,
            "slope": slope,
            "expected_value": expected_val,
            "rate_probability": rate_prob,
            "confounders": confounders,
            "entropy": data_entropy,
            "sufficiency": sufficiency,
            "posterior": posterior
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Use NCD as fallback
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
        
        scores = [item["score"] for item in scored]
        if max(scores) - min(scores) < 0.01:
            # All scores too close, add small differentiation
            for i, item in enumerate(scored):
                item["score"] += (i * 0.001)
        
        # Ensure scores are between 0 and 1
        max_score = max(item["score"] for item in scored)
        if max_score > 0:
            for item in scored:
                item["score"] = item["score"] / max_score
        
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