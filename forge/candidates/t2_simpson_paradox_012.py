import re
import zlib
from typing import Dict, List, Any

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, solve_linear_system
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, compare_conditional_marginal, detect_confounders

class ReasoningTool:
    """quantum_mechanics x pgmpy_acids - simpson_paradox"""

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

    # ========== PHASE 1: EXTRACT ==========
    def _extract(self, prompt: str) -> Dict[str, Any]:
        """Parse prompt to find entities, subgroups, rates, and the question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""

        # Find entity names (capitalized multi-word phrases)
        entity_pattern = r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b'
        all_entities = re.findall(entity_pattern, prompt)
        # Filter out common words and keep unique
        common_words = {'The', 'A', 'An', 'In', 'For', 'And', 'But', 'Or', 'With', 'Which', 'What', 'When', 'Where', 'Why', 'How'}
        entities = [e for e in all_entities if e not in common_words and len(e.split()) <= 3]
        entities = list(set(entities))

        # Find all percentages and associate with nearby entities
        rate_pattern = r'(\d+(?:\.\d+)?)%'
        percentages = re.findall(rate_pattern, prompt)
        rates = [float(p) / 100.0 for p in percentages]

        # Try to detect subgroups (often demographic categories like "Men", "Women", "Young", "Old")
        subgroup_keywords = ['men', 'women', 'male', 'female', 'young', 'old', 'group a', 'group b', 'subgroup', 'category']
        subgroups = []
        for line in lines:
            lower_line = line.lower()
            for kw in subgroup_keywords:
                if kw in lower_line:
                    # Extract the capitalized version if present
                    words = line.split()
                    for w in words:
                        if w.lower() == kw and w not in subgroups:
                            subgroups.append(w)
                            break

        # If no subgroups found via keywords, assume first two entities might be subgroups
        if not subgroups and len(entities) >= 2:
            subgroups = entities[:2]

        # Determine which entity is the "treatment" or "choice" (often appears in question)
        treatment = None
        if 'better' in question.lower() or 'higher' in question.lower() or 'recommend' in question.lower():
            for e in entities:
                if e.lower() in question.lower():
                    treatment = e
                    break

        return {
            "entities": entities,
            "subgroups": subgroups[:2] if len(subgroups) >= 2 else subgroups,
            "rates": rates,
            "question": question,
            "treatment": treatment,
            "raw_prompt": prompt
        }

    # ========== PHASE 2: REASON ==========
    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use quantum-mechanics-inspired superposition of subgroup states to detect reversal."""
        entities = structure["entities"]
        subgroups = structure["subgroups"]
        rates = structure["rates"]
        treatment = structure["treatment"]

        # If we don't have enough data, fall back to simple comparison
        if len(rates) < 4 or len(subgroups) < 2:
            # Use T1 primitive: entropy of rates as uncertainty measure
            if rates:
                rate_entropy = entropy([r/100.0 if r>1 else r for r in rates])
            else:
                rate_entropy = 1.0
            # Use T1 primitive: confidence from agreement (simulate multiple "observers")
            if len(rates) >= 2:
                conf = confidence_from_agreement(rates[:2])
            else:
                conf = 0.5
            return {
                "answer": entities[0] if entities else "Unknown",
                "confidence": max(0.1, 1.0 - rate_entropy) * conf,
                "reasoning": "Insufficient data for quantum superposition analysis",
                "reversal_detected": False
            }

        # ===== QUANTUM MECHANICS SCAFFOLD =====
        # Model each subgroup as a quantum state |ψ_i⟩
        # The aggregated rate is like measuring the system in a "mixed state"
        # Simpson's paradox occurs when the phase interference between subgroup amplitudes
        # causes destructive interference in the aggregate measurement.

        # We'll use the rates to compute "amplitudes" (sqrt of probabilities)
        # For two subgroups A and B with rates r_A1, r_A2 (treatment vs control in subgroup A)
        # and r_B1, r_B2 (treatment vs control in subgroup B)

        # Reorder rates: assume first two rates are for subgroup1, next two for subgroup2
        if len(rates) >= 4:
            r1_t, r1_c = rates[0], rates[1]  # treatment, control in subgroup1
            r2_t, r2_c = rates[2], rates[3]  # treatment, control in subgroup2
        else:
            # Not enough rates, use what we have
            r1_t, r1_c, r2_t, r2_c = rates[0], rates[1] if len(rates)>1 else 0.5, rates[2] if len(rates)>2 else 0.5, rates[3] if len(rates)>3 else 0.5

        # Compute amplitudes (quantum probability amplitudes)
        amp1_t = r1_t ** 0.5
        amp1_c = r1_c ** 0.5
        amp2_t = r2_t ** 0.5
        amp2_c = r2_c ** 0.5

        # Compute "interference term" - difference in phase between subgroups
        # Phase difference = arccos(correlation between treatment effects)
        # Simplified: use difference in treatment advantage between subgroups
        advantage1 = r1_t - r1_c
        advantage2 = r2_t - r2_c
        phase_diff = abs(advantage1 - advantage2)  # Larger difference → more potential for paradox

        # Aggregate amplitudes (weighted by subgroup sizes - assume equal for simplicity)
        # This simulates quantum superposition
        agg_amp_t = (amp1_t + amp2_t) / 2.0
        agg_amp_c = (amp1_c + amp2_c) / 2.0

        # Convert back to probabilities (Born rule)
        agg_prob_t = agg_amp_t ** 2
        agg_prob_c = agg_amp_c ** 2

        # Check for reversal: treatment better in each subgroup but worse in aggregate
        subgroup_t_better = (r1_t > r1_c) and (r2_t > r2_c)
        aggregate_t_better = agg_prob_t > agg_prob_c
        reversal_detected = subgroup_t_better != aggregate_t_better

        # ===== USE AMINO ACIDS: Bayesian Network to model confounding =====
        # Build a simple BN: Treatment → Outcome ← Confounder (Subgroup)
        edges = [("Subgroup", "Outcome"), ("Treatment", "Outcome")]
        
        # Create CPDs using extracted rates
        # P(Outcome | Subgroup, Treatment)
        # Values: [P(Outcome=1 | Subgroup=0, Treatment=0), P(Outcome=1 | Subgroup=0, Treatment=1),
        #          P(Outcome=1 | Subgroup=1, Treatment=0), P(Outcome=1 | Subgroup=1, Treatment=1)]
        cpd_values = [[r1_c, r1_t, r2_c, r2_t]]
        
        cpd_specs = {
            "Outcome": {"variables": ["Subgroup", "Treatment"], "values": cpd_values}
        }
        
        bn_model = build_bn(edges, cpd_specs)
        
        # Use amino acid: compare conditional vs marginal to detect Simpson's
        simpson_check = None
        if bn_model is not None:
            try:
                # Compare P(Outcome=1 | Treatment=1) vs P(Outcome=1)
                cond_query = conditional_query(bn_model, ["Outcome"], {"Treatment": 1})
                # For simplicity, get a numerical value
                if cond_query and isinstance(cond_query, dict) and "Outcome" in cond_query:
                    cond_prob = cond_query["Outcome"].get(1, 0.5)
                else:
                    cond_prob = agg_prob_t
                
                # Use amino acid: compare_conditional_marginal
                simpson_result = compare_conditional_marginal(bn_model, "Outcome", "Treatment", 1)
                if simpson_result is not None:
                    simpson_check = simpson_result
            except:
                simpson_check = None

        # Use T1 primitive: Bayesian update to refine confidence
        prior_conf = 0.7
        likelihood = phase_diff if phase_diff <= 1.0 else 1.0
        updated_conf = bayesian_update(prior_conf, likelihood)
        if updated_conf is None:
            updated_conf = prior_conf

        # Use T1 primitive: solve linear system to check consistency
        # Equations: r1_t = a + b*X1, r1_c = a + b*X2, etc.
        # Simple check: can we find weights that make aggregated rate consistent?
        if len(rates) >= 4:
            A = [[0.5, 0.5], [0.5, 0.5]]  # Equal weights for subgroups
            b = [agg_prob_t, agg_prob_c]
            weights = solve_linear_system(A, b)
            if weights is not None:
                consistency = 1.0 - abs(weights[0] - weights[1])
                updated_conf = updated_conf * consistency

        # Determine answer based on quantum analysis
        if reversal_detected:
            # When reversal occurs, the "better" choice flips
            if subgroup_t_better:
                # Treatment better in subgroups but worse overall → control is actually better
                answer = "Control" if treatment else entities[1] if len(entities) > 1 else "Option B"
            else:
                # Treatment worse in subgroups but better overall → treatment is actually better
                answer = treatment if treatment else entities[0] if entities else "Option A"
            reasoning = f"Quantum superposition analysis detected Simpson's paradox (phase difference={phase_diff:.3f}). Subgroup advantage reverses in aggregate due to destructive interference."
        else:
            # No reversal, treatment better if aggregate probability higher
            if agg_prob_t > agg_prob_c:
                answer = treatment if treatment else entities[0] if entities else "Option A"
            else:
                answer = "Control" if treatment else entities[1] if len(entities) > 1 else "Option B"
            reasoning = f"No reversal detected. Aggregate treatment probability={agg_prob_t:.3f}, control={agg_prob_c:.3f}."

        # Incorporate amino acid result if available
        if simpson_check is not None:
            if isinstance(simpson_check, bool) and simpson_check:
                reversal_detected = True
                reasoning += " Bayesian network analysis confirms Simpson's paradox."
            elif isinstance(simpson_check, dict) and "reversal" in simpson_check:
                if simpson_check["reversal"]:
                    reversal_detected = True
                    reasoning += " Bayesian network analysis confirms Simpson's paradox."

        # Final confidence
        final_confidence = min(0.99, max(0.1, updated_conf))
        if reversal_detected:
            final_confidence = final_confidence * 0.9  # Slightly less confident when paradox detected

        return {
            "answer": answer,
            "confidence": final_confidence,
            "reasoning": reasoning,
            "reversal_detected": reversal_detected,
            "quantum_phase_diff": phase_diff,
            "aggregate_treatment_prob": agg_prob_t,
            "aggregate_control_prob": agg_prob_c
        }

    # ========== PHASE 3: SCORE ==========
    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        def ncd(a: str, b: str) -> float:
            """Normalized Compression Distance between two strings."""
            if not a or not b:
                return 1.0
            ca = len(zlib.compress(a.encode()))
            cb = len(zlib.compress(b.encode()))
            cab = len(zlib.compress((a + " " + b).encode()))
            if max(ca, cb) == 0:
                return 1.0
            return (cab - min(ca, cb)) / max(ca, cb)
        
        scored = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate (case-insensitive)
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback 1: NCD with computed answer
                ncd1 = ncd(computed_answer, candidate)
                # Fallback 2: NCD with reasoning (longer text, more robust)
                ncd2 = ncd(reasoning_text, candidate)
                base_score = 1.0 / (1.0 + min(ncd1, ncd2))
            
            # Adjust based on reversal detection
            if reasoning_result.get("reversal_detected", False):
                # Candidates mentioning "paradox", "reverse", or "confounding" get bonus
                paradox_terms = ["paradox", "reverse", "confound", "simpson"]
                if any(term in candidate.lower() for term in paradox_terms):
                    base_score = min(1.0, base_score * 1.2)
            
            scored.append({
                "candidate": candidate,
                "score": base_score,
                "computed_answer": computed_answer
            })
        
        return scored

    # ========== PHASE 4: CALIBRATE ==========
    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence and normalization."""
        if not scored:
            return []
        
        # Extract scores
        scores = [item["score"] for item in scored]
        
        # Use T1 primitive: confidence from agreement to adjust
        conf = confidence_from_agreement(scores)
        if conf is None:
            conf = 0.5
        
        # Calibrate: scale scores toward confidence
        calibrated = []
        for item in scored:
            original = item["score"]
            # Bayesian-style calibration: weighted average with confidence
            calibrated_score = original * conf + (1 - conf) * 0.5
            # Ensure in [0, 1]
            calibrated_score = max(0.0, min(1.0, calibrated_score))
            
            calibrated.append({
                "candidate": item["candidate"],
                "score": calibrated_score,
                "computed_answer": item.get("computed_answer", "")
            })
        
        return calibrated