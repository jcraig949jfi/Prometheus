import re
import zlib
from typing import Dict, List, Any, Set, Tuple
from forge_primitives import (
    track_beliefs,
    sally_anne_test,
    modus_ponens,
    confidence_from_agreement,
    entropy
)
from forge.amino_acids.pysat_acids import check_entailment, detect_paradox
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Immunology x SAT/Constraint Solving - Perspective Shift"""

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
        """Parse prompt to extract agents, their knowledge, and the query."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        agents = set()
        beliefs = {}  # agent -> set of known facts
        observations = []
        query = lines[-1] if lines else ""

        # Find agent names (capitalized words that appear as subjects)
        words = re.findall(r'\b([A-Z][a-z]+)\b', prompt)
        potential_agents = [w for w in words if w not in ['The', 'A', 'An', 'And', 'But', 'Or']]
        agents = set(potential_agents[:4])  # Limit to first 4 plausible agents

        # Extract belief statements
        belief_patterns = [
            r'([A-Z][a-z]+) knows? that ([^\.]+)',
            r'([A-Z][a-z]+) believes? that ([^\.]+)',
            r'([A-Z][a-z]+) (?:sees|observes|learns) that ([^\.]+)',
            r'([A-Z][a-z]+) (?:does not|doesn\'t) know that ([^\.]+)'
        ]

        for line in lines:
            for pattern in belief_patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                for agent, fact in matches:
                    if agent in agents:
                        fact_clean = fact.strip().lower()
                        if 'does not' in line.lower() or 'doesn\'t' in line.lower():
                            # Handle ignorance as a special fact
                            neg_fact = f"not_{fact_clean.replace(' ', '_')}"
                            if agent not in beliefs:
                                beliefs[agent] = set()
                            beliefs[agent].add(neg_fact)
                        else:
                            if agent not in beliefs:
                                beliefs[agent] = set()
                            beliefs[agent].add(fact_clean)
                            observations.append((agent, fact_clean, True))

        # Extract implications (if-then rules)
        implications = []
        implication_pattern = r'If ([^,]+), then ([^\.]+)'
        for line in lines:
            matches = re.findall(implication_pattern, line, re.IGNORECASE)
            for antecedent, consequent in matches:
                ant_clean = antecedent.strip().lower()
                cons_clean = consequent.strip().lower()
                implications.append((ant_clean, cons_clean))

        return {
            "agents": list(agents),
            "beliefs": beliefs,
            "observations": observations,
            "implications": implications,
            "query": query,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use immunological concepts (antigen presentation, immune memory) to model perspective shifts."""
        agents = structure["agents"]
        observations = structure["observations"]
        implications = structure["implications"]
        query = structure["query"]

        # T1 PRIMITIVE 1: Track beliefs over time (immune memory analogy)
        belief_tracking = track_beliefs(agents, observations)
        if belief_tracking is None:
            belief_tracking = {agent: set() for agent in agents}

        # T1 PRIMITIVE 2: Apply modus ponens to propagate knowledge (antigen processing)
        all_facts = set()
        for agent_beliefs in belief_tracking.values():
            all_facts.update(agent_beliefs)

        deduced_facts = modus_ponens(implications, all_facts)
        if deduced_facts is None:
            deduced_facts = set()

        # AMINO ACID 1: Check for logical paradoxes (autoimmune conflict detection)
        # Encode beliefs as SAT clauses
        clauses = []
        fact_to_var = {}
        var_counter = 1

        for fact in all_facts.union(deduced_facts):
            if fact not in fact_to_var:
                fact_to_var[fact] = var_counter
                var_counter += 1

        # Each agent's belief is a clause
        for agent, facts in belief_tracking.items():
            for fact in facts:
                if fact in fact_to_var:
                    clauses.append([fact_to_var[fact]])

        # Implications become clauses: (not A or B)
        for ant, cons in implications:
            if ant in fact_to_var and cons in fact_to_var:
                clauses.append([-fact_to_var[ant], fact_to_var[cons]])

        paradox_detected = detect_paradox(clauses)
        if paradox_detected is None:
            paradox_detected = False

        # AMINO ACID 2: Check entailment for the query (antigen recognition)
        # Extract query target from question
        query_target = None
        if "who knows" in query.lower():
            # Find agent mentioned in query
            query_agents = [a for a in agents if a.lower() in query.lower()]
            if query_agents:
                query_target = query_agents[0]
        elif "what does" in query.lower():
            # Extract fact being asked about
            fact_match = re.search(r'what does [A-Z][a-z]+ know\??', query.lower())
            if fact_match:
                # Try to find a fact from the prompt that fits
                for fact in all_facts:
                    if 'not_' not in fact and fact in query.lower():
                        query_target = fact
                        break

        # T1 PRIMITIVE 3: Compute entropy of belief states (immune diversity measure)
        belief_entropies = []
        for agent in agents:
            beliefs_list = list(belief_tracking.get(agent, set()))
            if beliefs_list:
                # Simple binary encoding: each fact is equally probable
                n_facts = len(beliefs_list)
                if n_facts > 0:
                    probs = [1.0 / n_facts] * n_facts
                    agent_entropy = entropy(probs)
                    if agent_entropy is not None:
                        belief_entropies.append(agent_entropy)

        avg_entropy = sum(belief_entropies) / len(belief_entropies) if belief_entropies else 0.5

        # T1 PRIMITIVE 4: Confidence from agreement (consensus immune response)
        # Score each agent's knowledge completeness
        agent_scores = []
        for agent in agents:
            agent_beliefs = belief_tracking.get(agent, set())
            # Score based on number of facts known
            score = len(agent_beliefs) / max(len(all_facts), 1)
            agent_scores.append(score)

        confidence = confidence_from_agreement(agent_scores)
        if confidence is None:
            confidence = 0.5

        # Immunological reasoning: Perspective shift as antigen presentation
        # The "correct" perspective is the one that survives logical consistency checks
        # and has the highest information integration (lowest entropy, highest confidence)

        # Determine answer based on query type
        computed_answer = ""
        reasoning_explanation = ""

        if query_target and isinstance(query_target, str):
            if query_target in agents:
                # Question about what an agent knows
                agent_beliefs = belief_tracking.get(query_target, set())
                if agent_beliefs:
                    # Select the most specific belief (longest fact)
                    computed_answer = max(agent_beliefs, key=len)
                else:
                    computed_answer = "nothing"
            else:
                # Question about a specific fact
                # Find which agents know this fact
                knowing_agents = []
                for agent in agents:
                    if query_target in belief_tracking.get(agent, set()):
                        knowing_agents.append(agent)

                if knowing_agents:
                    computed_answer = ", ".join(knowing_agents)
                else:
                    computed_answer = "nobody"
        else:
            # Fallback: answer with the agent having most comprehensive knowledge
            if agents:
                best_agent = max(agents, key=lambda a: len(belief_tracking.get(a, set())))
                computed_answer = best_agent
            else:
                computed_answer = "unknown"

        # Adjust confidence based on paradox detection and entropy
        if paradox_detected:
            confidence *= 0.7  # Reduce confidence if logical conflicts exist
        confidence = min(confidence * (1.0 - avg_entropy * 0.3), 1.0)

        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Immunological model: Belief states as immune memory, paradox detection as autoimmunity check. Entropy: {avg_entropy:.2f}, Confidence: {confidence:.2f}",
            "belief_tracking": belief_tracking,
            "paradox_detected": paradox_detected
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]

        results = []
        for candidate in candidates:
            # Primary scoring: exact or substring match of computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))

            # Boost if candidate contains reasoning keywords (from our reasoning text)
            reasoning_words = set(reasoning_text.lower().split())
            candidate_words = set(candidate.lower().split())
            overlap = len(reasoning_words.intersection(candidate_words))
            word_boost = min(overlap * 0.1, 0.3)

            final_score = min(base_score + word_boost, 1.0) * confidence

            results.append({
                "candidate": candidate,
                "score": final_score,
                "base_score": base_score,
                "confidence_weight": confidence
            })

        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored

        scores = [item["score"] for item in scored]
        max_score = max(scores) if scores else 1.0
        min_score = min(scores) if scores else 0.0

        if max_score - min_score < 0.01:  # All scores too close
            # Add small differentiation based on candidate length
            for item in scored:
                length_norm = len(item["candidate"]) / 100.0
                item["score"] = item["score"] * 0.9 + length_norm * 0.1
        else:
            # Normalize to [0, 1] range
            for item in scored:
                if max_score > min_score:
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