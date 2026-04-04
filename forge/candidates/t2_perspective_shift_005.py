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
from forge.amino_acids.pgmpy_acids import (
    build_bn,
    conditional_query,
    active_trails,
    get_markov_blanket
)


class ReasoningTool:
    """feedback_systems x pgmpy_acids - perspective_shift"""

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

    def _extract(self, prompt: str) -> Dict[str, Any]:
        """Extract agents, facts, observations, and question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""

        agents = set()
        facts = set()
        observations = []
        agent_knowledge = {}

        current_agent = None
        for line in lines:
            line_lower = line.lower()

            # Extract agent names (capitalized words at sentence start)
            agent_match = re.match(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', line)
            if agent_match:
                agent_name = agent_match.group(1)
                agents.add(agent_name)
                current_agent = agent_name

            # Extract facts (statements with "is", "has", "are", "were")
            fact_patterns = [
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(is|has|are|were)\s+([^\.]+)',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(knows|believes|thinks)\s+that\s+([^\.]+)'
            ]
            for pattern in fact_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    if len(match) == 3:
                        subject, verb, predicate = match
                        fact = f"{subject} {verb} {predicate}".strip()
                        facts.add(fact)

            # Extract observations (Agent sees/hears/learns something)
            obs_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(sees|hears|learns|observes)\s+that\s+([^\.]+)'
            obs_matches = re.findall(obs_pattern, line)
            for agent, verb, content in obs_matches:
                observations.append((agent, content, True))
                if agent not in agent_knowledge:
                    agent_knowledge[agent] = set()
                agent_knowledge[agent].add(content)

            # Extract knowledge statements
            know_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(knows|does not know)\s+that\s+([^\.]+)'
            know_matches = re.findall(know_pattern, line)
            for agent, verb, content in know_matches:
                knows = verb == "knows"
                if agent not in agent_knowledge:
                    agent_knowledge[agent] = set()
                if knows:
                    agent_knowledge[agent].add(content)
                else:
                    # Mark as unknown for this agent
                    pass

        # Use T1 primitive: track_beliefs to initialize belief states
        belief_states = track_beliefs(list(agents), observations)

        return {
            "agents": list(agents),
            "facts": list(facts),
            "observations": observations,
            "question": question,
            "belief_states": belief_states,
            "agent_knowledge": agent_knowledge,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Reason about perspective shifts using feedback systems framework."""
        agents = structure["agents"]
        observations = structure["observations"]
        question = structure["question"]
        belief_states = structure["belief_states"]
        agent_knowledge = structure["agent_knowledge"]

        # Phase 1: Build feedback model of knowledge propagation
        # In feedback systems, knowledge states are nodes with feedback loops
        # through observation and communication channels

        # Create Bayesian network edges: agent -> knowledge -> other agents
        edges = []
        for agent in agents:
            # Self-loop representing internal belief maintenance (feedback)
            edges.append((f"{agent}_belief", f"{agent}_knowledge"))
            # Influence from observations
            for obs_agent, content, _ in observations:
                if obs_agent == agent:
                    edges.append((f"obs_{agent}", f"{agent}_knowledge"))

        # Build simple Bayesian network
        bn_model = build_bn(edges, cpd_specs=None)

        # Use amino acid: active_trails to find knowledge propagation paths
        propagation_paths = {}
        for agent in agents:
            if bn_model is not None:
                trails = active_trails(
                    bn_model,
                    start_vars=[f"{agent}_knowledge"],
                    observed=None
                )
                if trails is not None:
                    propagation_paths[agent] = trails
            else:
                propagation_paths[agent] = set()

        # Use T1 primitive: sally_anne_test for false belief reasoning
        false_belief_results = {}
        for agent in agents:
            # Find if there's a location change in the prompt
            if "moved" in structure["raw"].lower() or "moves" in structure["raw"].lower():
                location_matches = re.findall(
                    r'from\s+([^\.]+)\s+to\s+([^\.]+)',
                    structure["raw"]
                )
                if location_matches:
                    orig_loc, new_loc = location_matches[0]
                    # Find who saw the move
                    saw_move = set()
                    for obs_agent, content, _ in observations:
                        if "move" in content.lower() or "moved" in content.lower():
                            saw_move.add(obs_agent)

                    result = sally_anne_test(
                        who_moved=agent,
                        who_saw_move=saw_move,
                        original_location=orig_loc,
                        new_location=new_loc
                    )
                    false_belief_results[agent] = result

        # Use T1 primitive: modus_ponens for logical inference
        # Convert facts to implication rules
        premises = []
        for fact in structure["facts"]:
            if "if" in fact.lower() and "then" in fact.lower():
                parts = fact.lower().split("then")
                if len(parts) == 2:
                    antecedent = parts[0].replace("if", "").strip()
                    consequent = parts[1].strip()
                    premises.append((antecedent, consequent))

        # Apply modus ponens for each agent's known facts
        agent_inferences = {}
        for agent in agents:
            agent_facts = set()
            if agent in agent_knowledge:
                agent_facts.update(agent_knowledge[agent])
            if agent in belief_states:
                agent_facts.update(belief_states[agent])

            inferred = modus_ponens(premises, agent_facts)
            agent_inferences[agent] = inferred

        # Use amino acid: get_markov_blanket to find what influences each agent's knowledge
        knowledge_dependencies = {}
        if bn_model is not None:
            for agent in agents:
                blanket = get_markov_blanket(bn_model, f"{agent}_knowledge")
                if blanket is not None:
                    knowledge_dependencies[agent] = blanket
                else:
                    knowledge_dependencies[agent] = set()

        # Use T1 primitive: entropy to measure uncertainty in knowledge states
        uncertainty_scores = {}
        for agent in agents:
            # Create probability distribution over possible knowledge states
            known_count = len(agent_inferences.get(agent, set()))
            total_facts = len(structure["facts"]) + len(observations)
            if total_facts > 0:
                p_known = known_count / total_facts
                p_unknown = 1 - p_known
                if p_known > 0 and p_unknown > 0:
                    uncertainty = entropy([p_known, p_unknown])
                    uncertainty_scores[agent] = uncertainty
                else:
                    uncertainty_scores[agent] = 0.0
            else:
                uncertainty_scores[agent] = 1.0

        # Determine answer based on question
        computed_answer = ""
        reasoning_text = ""

        # Parse question to determine what's being asked
        question_lower = question.lower()
        if "who knows" in question_lower or "which agent knows" in question_lower:
            # Find agent with most knowledge/least uncertainty
            if uncertainty_scores:
                best_agent = min(uncertainty_scores.items(), key=lambda x: x[1])[0]
                computed_answer = best_agent
                reasoning_text = f"{best_agent} has lowest uncertainty ({uncertainty_scores[best_agent]:.3f})"
        elif "false belief" in question_lower or "wrong" in question_lower:
            # Find agent with false belief
            if false_belief_results:
                for agent, result in false_belief_results.items():
                    if agent in result and "wrong" in str(result[agent]).lower():
                        computed_answer = agent
                        reasoning_text = f"{agent} has false belief about location"
                        break
        elif "what does" in question_lower and "think" in question_lower:
            # Extract agent name from question
            agent_match = re.search(r'what does\s+([A-Z][a-z]+)', question, re.IGNORECASE)
            if agent_match:
                agent = agent_match.group(1)
                if agent in agent_inferences:
                    # Summarize what this agent thinks
                    inferences = list(agent_inferences[agent])
                    if inferences:
                        computed_answer = inferences[0]  # Take first inference
                        reasoning_text = f"{agent} believes {computed_answer}"
        else:
            # Default: agent with most comprehensive knowledge
            if agent_inferences:
                best_agent = max(agent_inferences.items(),
                               key=lambda x: len(x[1]))[0]
                computed_answer = best_agent
                reasoning_text = f"{best_agent} has most inferences ({len(agent_inferences[best_agent])})"

        # Use T1 primitive: confidence_from_agreement to compute confidence
        # Create multiple scoring perspectives
        scores = []
        if uncertainty_scores:
            # Convert uncertainty to confidence (lower uncertainty = higher confidence)
            for agent in agents:
                if agent in uncertainty_scores:
                    confidence = 1.0 - uncertainty_scores[agent]
                    scores.append(confidence)

        if scores:
            confidence = confidence_from_agreement(scores)
        else:
            confidence = 0.5

        # Use amino acid: conditional_query for probabilistic reasoning about knowledge
        prob_knowledge = 0.5  # Default
        if bn_model is not None and computed_answer and computed_answer in agents:
            try:
                # Query probability that agent knows something relevant
                evidence = {}
                for obs_agent, content, _ in observations:
                    if obs_agent == computed_answer:
                        evidence[f"obs_{obs_agent}"] = 1

                if evidence:
                    query_result = conditional_query(
                        bn_model,
                        target_vars=[f"{computed_answer}_knowledge"],
                        evidence=evidence
                    )
                    if query_result is not None:
                        # Extract probability value
                        if isinstance(query_result, dict):
                            prob_values = list(query_result.values())
                            if prob_values:
                                prob_knowledge = float(prob_values[0])
            except:
                prob_knowledge = 0.5

        # Adjust confidence based on probabilistic query
        final_confidence = (confidence + prob_knowledge) / 2

        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "reasoning": reasoning_text,
            "uncertainty_scores": uncertainty_scores,
            "agent_inferences": agent_inferences,
            "false_belief_results": false_belief_results
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates against computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]

        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback 1: check if reasoning text matches
                if reasoning_text and reasoning_text.lower() in candidate.lower():
                    score = 0.8
                else:
                    # Fallback 2: NCD similarity
                    if computed_answer:
                        similarity = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
                    else:
                        similarity = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
                    score = similarity * 0.6  # Scale down for indirect match

            results.append({
                "candidate": candidate,
                "score": score,
                "computed_answer": computed_answer
            })

        return results

    def _calibrate(self, scored_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using feedback systems principle: adjust based on consistency."""
        if not scored_candidates:
            return scored_candidates

        # Extract scores for normalization
        scores = [item["score"] for item in scored_candidates]
        if not scores:
            return scored_candidates

        max_score = max(scores)
        min_score = min(scores)

        # Apply feedback: if scores are too close, amplify differences
        score_range = max_score - min_score
        if score_range < 0.3 and max_score > 0:
            # Amplify differences (positive feedback)
            for item in scored_candidates:
                normalized = (item["score"] - min_score) / score_range if score_range > 0 else 0.5
                item["score"] = normalized ** 0.7  # Non-linear amplification
        elif score_range > 0.7:
            # Dampen extreme differences (negative feedback)
            for item in scored_candidates:
                normalized = (item["score"] - min_score) / score_range
                item["score"] = 0.3 + 0.4 * normalized  # Compress range

        return scored_candidates

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        """Main evaluation method following four-phase architecture."""
        # Phase 1: EXTRACT
        structure = self._extract(prompt)

        # Phase 2: REASON
        reasoning_result = self._reason(structure)

        # Phase 3: SCORE
        scored = self._score(candidates, reasoning_result)

        # Phase 4: CALIBRATE
        calibrated = self._calibrate(scored)

        return sorted(calibrated, key=lambda x: x["score"], reverse=True)