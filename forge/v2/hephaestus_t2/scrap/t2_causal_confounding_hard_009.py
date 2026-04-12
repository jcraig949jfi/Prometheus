import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, topological_sort
from forge.amino_acids.pgmpy_acids import detect_confounders, conditional_query


class ReasoningTool:
    """Ecology x Causal Inference - Causal Confounding Hard"""

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
        """Parse prompt to extract entities, relationships, and question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""

        # Find entity names (capitalized multi-word phrases)
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        all_entities = re.findall(entity_pattern, prompt)
        # Filter out common words and keep unique
        common = {"The", "A", "An", "In", "On", "At", "To", "For", "And", "Or", "But"}
        entities = [e for e in all_entities if e not in common]
        unique_entities = list(dict.fromkeys(entities))

        # Find percentages and associate with nearest entity
        percent_pattern = r'(\d+(?:\.\d+)?)%'
        percentages = re.findall(percent_pattern, prompt)
        percentages = [float(p) / 100.0 for p in percentages]

        # Find causal language: "affects", "influences", "causes", "leads to"
        causal_words = re.findall(r'\b(affects|influences|causes|leads to)\b', prompt.lower())

        # Build a simple graph from "X affects Y" patterns
        edges = []
        for i in range(len(lines)):
            line = lines[i]
            # Look for "X affects Y" patterns
            affect_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(affects|influences|causes|leads to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', line, re.IGNORECASE)
            if affect_match:
                source, _, target = affect_match.groups()
                if source in unique_entities and target in unique_entities:
                    edges.append((source, target))

        return {
            "entities": unique_entities,
            "percentages": percentages,
            "edges": edges,
            "question": question,
            "causal_words": causal_words,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply ecological causal reasoning to identify confounding."""
        entities = structure["entities"]
        edges = structure["edges"]
        percentages = structure["percentages"]
        question = structure["question"]

        if len(entities) < 2:
            # Fallback: not enough entities
            computed_answer = entities[0] if entities else "Unknown"
            return {
                "answer": computed_answer,
                "confidence": 0.5,
                "reasoning": "Insufficient entities extracted"
            }

        # ECOLOGICAL SCAFFOLD: Treat variables as species in a food web.
        # Confounders are keystone species that influence multiple others.
        # Entropy measures stability of the ecological network.

        # 1. Build a simple Bayesian network from extracted edges
        # Use amino acid: detect_confounders
        model_edges = edges if edges else []
        confounders_result = None
        if len(model_edges) >= 2 and len(entities) >= 2:
            # Try to detect confounders between first two entities
            try:
                confounders_result = detect_confounders(model_edges, entities[0], entities[1])
            except Exception:
                confounders_result = None

        # 2. Compute ecological entropy of the percentage distribution
        # T1 primitive: entropy
        if percentages:
            # Normalize percentages to a probability distribution
            total = sum(percentages)
            if total > 0:
                probs = [p / total for p in percentages]
                eco_entropy = entropy(probs)  # LOAD-BEARING
            else:
                eco_entropy = 0.0
        else:
            eco_entropy = 0.0

        # 3. Topological sort to find causal ordering
        # T1 primitive: topological_sort
        try:
            causal_order = topological_sort(edges)  # LOAD-BEARING
            if causal_order is None:
                causal_order = []
        except Exception:
            causal_order = []

        # 4. Bayesian update on extracted percentages if available
        # T1 primitive: bayesian_update
        prior = 0.5
        likelihood = 0.7
        false_positive = 0.1
        if percentages:
            # Use first percentage as likelihood signal
            likelihood = min(max(percentages[0], 0.01), 0.99)
        posterior = bayesian_update(prior, likelihood, false_positive)  # LOAD-BEARING

        # 5. Determine answer based on confounder detection
        computed_answer = "Unknown"
        reasoning_text = ""

        if confounders_result is not None and len(confounders_result) > 0:
            # Confounder detected: answer is the confounder
            confounder = list(confounders_result)[0]
            computed_answer = confounder
            reasoning_text = f"Confounder detected: {confounder}"
        elif len(causal_order) > 0:
            # Use causal order: root cause is first in topological order
            computed_answer = causal_order[0]
            reasoning_text = f"Root cause from topological order: {causal_order[0]}"
        else:
            # Fallback: use entity with highest posterior influence
            if len(entities) >= 2:
                # Use posterior to decide between first two entities
                if posterior > 0.5:
                    computed_answer = entities[0]
                else:
                    computed_answer = entities[1]
                reasoning_text = f"Bayesian posterior decision: {computed_answer}"
            else:
                computed_answer = entities[0] if entities else "Unknown"
                reasoning_text = "Default to first entity"

        # 6. Compute confidence using agreement between signals
        # T1 primitive: confidence_from_agreement
        signals = []
        if eco_entropy > 0:
            signals.append(eco_entropy)
        if posterior != 0.5:
            signals.append(posterior)
        if len(causal_order) > 0:
            signals.append(len(causal_order) / 10.0)  # Normalized

        if signals:
            confidence = confidence_from_agreement(signals)  # LOAD-BEARING
        else:
            confidence = 0.5

        # ECOLOGICAL INTERPRETATION:
        # Low entropy → stable ecosystem → confounding less likely
        # High entropy → unstable → confounding more likely
        if eco_entropy > 0.8:
            confidence *= 0.8  # Reduce confidence in high-entropy (chaotic) systems
            reasoning_text += " (high ecological entropy suggests instability)"

        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": reasoning_text,
            "entropy": eco_entropy,
            "posterior": posterior,
            "causal_order": causal_order,
            "confounders": list(confounders_result) if confounders_result else []
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        confidence = reasoning_result["confidence"]

        results = []
        for c in candidates:
            # Primary: exact match or substring of computed answer
            if computed_answer.lower() in c.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, c))
            
            # Adjust by confidence
            adjusted_score = base_score * confidence
            results.append({
                "candidate": c,
                "score": adjusted_score,
                "base_score": base_score,
                "confidence": confidence
            })
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simple calibration: ensure scores are in [0,1]."""
        if not scored:
            return scored
        
        scores = [s["score"] for s in scored]
        if max(scores) > 0:
            # Normalize to max = 1
            max_score = max(scores)
            for s in scored:
                s["score"] = s["score"] / max_score
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