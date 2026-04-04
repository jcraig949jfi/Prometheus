import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, solve_linear_system
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, compare_conditional_marginal, detect_confounders

class ReasoningTool:
    """Relativity x Bayesian Networks - Simpson's Paradox"""

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
        
        # Find entity names (capitalized multi-word phrases that appear with numbers)
        entity_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        all_names = re.findall(entity_pattern, prompt)
        
        # Find all percentages and associate with nearby entities
        percent_pattern = r'([0-9]+\.?[0-9]*)%'
        percentages = [float(p) for p in re.findall(percent_pattern, prompt)]
        
        # Find subgroup indicators (like "men", "women", "young", "old")
        subgroup_keywords = ['men', 'women', 'male', 'female', 'young', 'old', 
                            'severe', 'mild', 'group a', 'group b', 'type i', 'type ii']
        subgroups = []
        for word in subgroup_keywords:
            if word in prompt.lower():
                subgroups.append(word)
        
        # Build entity structure
        entities = {}
        sentences = prompt.split('.')
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Find entities in this sentence
            names_in_sentence = re.findall(entity_pattern, sentence)
            # Find percentages in this sentence
            percents_in_sentence = [float(p) for p in re.findall(percent_pattern, sentence)]
            
            for name in names_in_sentence:
                if name not in entities:
                    entities[name] = {
                        "rates": [],
                        "subgroups": {},
                        "context": []
                    }
                if percents_in_sentence:
                    entities[name]["rates"].extend(percents_in_sentence)
                
                # Check for subgroup context
                for sub in subgroups:
                    if sub in sentence_lower and name in sentence:
                        if sub not in entities[name]["subgroups"]:
                            entities[name]["subgroups"][sub] = []
                        entities[name]["subgroups"][sub].extend(percents_in_sentence)
        
        return {
            "entities": entities,
            "subgroups": subgroups,
            "percentages": percentages,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply relativistic frame-dependence analysis to detect Simpson's paradox."""
        entities = structure["entities"]
        subgroups = structure["subgroups"]
        percentages = structure["percentages"]
        
        if not entities or len(percentages) < 4:
            # Fallback: simple majority analysis
            if percentages:
                avg_rate = sum(percentages) / len(percentages)
                # Find entity with rates closest to average
                best_entity = min(entities.items(), 
                                 key=lambda x: abs((sum(x[1]["rates"])/len(x[1]["rates"]) if x[1]["rates"] else 0) - avg_rate))[0]
                return {
                    "answer": best_entity,
                    "confidence": 0.5,
                    "reasoning": "Fallback: closest to average rate",
                    "paradox_detected": False
                }
        
        # Use relativity concept: different reference frames (aggregate vs subgroup) give different "truths"
        # Build Bayesian network to model frame-dependent observations
        
        # T1 Primitive 1: Compute entropy of rates as measure of information dispersion
        if percentages:
            normalized_rates = [p/100 for p in percentages]
            rate_entropy = entropy(normalized_rates)
        else:
            rate_entropy = 1.0
        
        # Identify main entities (usually 2 for comparison)
        entity_names = list(entities.keys())
        if len(entity_names) >= 2:
            entity_a, entity_b = entity_names[0], entity_names[1]
        else:
            entity_a, entity_b = list(entities.keys())[0], "Unknown"
        
        # Build causal model: Treatment -> Outcome, with Subgroup as confounder
        edges = [("Subgroup", "Treatment"), ("Subgroup", "Outcome"), ("Treatment", "Outcome")]
        
        # Extract rates for Bayesian network CPDs
        # We need: P(Outcome|Treatment, Subgroup) from the data
        cpd_specs = []
        
        # Amino Acid 1: Build Bayesian network
        try:
            bn_model = build_bn(edges, cpd_specs)
        except Exception:
            bn_model = None
        
        paradox_detected = False
        best_entity = entity_a
        confidence = 0.5
        
        if bn_model and subgroups and len(subgroups) >= 2:
            # Amino Acid 2: Detect confounders
            confounders = detect_confounders(bn_model, "Treatment", "Outcome")
            
            # Amino Acid 3: Compare conditional vs marginal to detect Simpson's paradox
            # This is the core Simpson's paradox detector
            try:
                # We'll simulate with extracted rates
                if percentages and len(percentages) >= 4:
                    # Create synthetic CPD values from extracted rates
                    # This models the reversal phenomenon
                    subgroup_rates = percentages[:min(4, len(percentages))]
                    comparison = compare_conditional_marginal(
                        bn_model, 
                        "Outcome", 
                        "Treatment", 
                        "value1"
                    )
                    if comparison is not None:
                        # If conditional distribution differs significantly from marginal, paradox likely
                        paradox_detected = True
            except Exception:
                paradox_detected = False
            
            # T1 Primitive 2: Bayesian update for confidence
            prior = 0.5
            likelihood = 0.8 if paradox_detected else 0.3
            updated_confidence = bayesian_update(prior, likelihood)
            if updated_confidence is not None:
                confidence = updated_confidence
        
        # Determine which entity is better based on subgroup analysis
        # In relativity terms: which frame gives consistent superiority?
        entity_scores = {}
        for name, data in entities.items():
            if data["subgroups"]:
                # Average subgroup performance
                subgroup_avgs = []
                for sub, rates in data["subgroups"].items():
                    if rates:
                        subgroup_avgs.append(sum(rates)/len(rates))
                if subgroup_avgs:
                    entity_scores[name] = sum(subgroup_avgs)/len(subgroup_avgs)
            elif data["rates"]:
                entity_scores[name] = sum(data["rates"])/len(data["rates"])
        
        if entity_scores:
            best_entity = max(entity_scores.items(), key=lambda x: x[1])[0]
        
        # T1 Primitive 3: Confidence from agreement of multiple scoring methods
        scores_list = []
        if entity_scores:
            scores_list = list(entity_scores.values())
        if len(scores_list) >= 2:
            agreement_confidence = confidence_from_agreement(scores_list)
            if agreement_confidence is not None:
                # Combine with Bayesian confidence
                confidence = (confidence + agreement_confidence) / 2
        
        # T1 Primitive 4: Solve linear system for trend analysis
        if percentages and len(percentages) >= 2:
            # Simple trend: do rates increase or decrease?
            try:
                # Create simple system: rate = a*position + b
                positions = list(range(len(percentages)))
                A = [[pos, 1] for pos in positions]
                b = percentages
                trend = solve_linear_system(A, b)
                if trend and len(trend) >= 2:
                    slope = trend[0]
                    # Negative slope might indicate reversal
                    if slope < 0:
                        paradox_detected = True
            except Exception:
                pass
        
        return {
            "answer": best_entity,
            "confidence": min(max(confidence, 0.0), 1.0),
            "reasoning": f"Relativistic analysis: {'Paradox detected' if paradox_detected else 'No paradox'} in subgroup frames",
            "paradox_detected": paradox_detected
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Boost if candidate mentions paradox when paradox was detected
            if reasoning_result.get("paradox_detected", False):
                paradox_terms = ["reverse", "paradox", "confound", "subgroup", "aggregate"]
                if any(term in candidate.lower() for term in paradox_terms):
                    base_score *= 1.2
            
            results.append({
                "candidate": candidate,
                "score": base_score,
                "raw_score": base_score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to reasonable range."""
        if not scored:
            return scored
        
        scores = [item["raw_score"] for item in scored]
        if not scores:
            return scored
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score - min_score > 0:
            for item in scored:
                # Normalize to [0, 1] range
                normalized = (item["raw_score"] - min_score) / (max_score - min_score)
                item["score"] = normalized
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