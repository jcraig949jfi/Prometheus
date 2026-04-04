import re
import zlib
from typing import Dict, List, Any, Set, Tuple
from forge_primitives import (
    track_beliefs,
    sally_anne_test,
    confidence_from_agreement,
    entropy,
    modus_ponens,
    topological_sort
)
from forge.amino_acids.pgmpy_acids import (
    build_bn,
    conditional_query,
    active_trails,
    get_markov_blanket
)
from forge.amino_acids.pysat_acids import (
    check_entailment,
    detect_paradox
)


class ReasoningTool:
    """Thermodynamics x Bayesian Networks - Perspective Shift"""

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
        """Extract agents, their knowledge, and the query from the prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        agents = set()
        agent_knowledge = {}
        facts = set()
        implications = []
        query = lines[-1] if lines else ""

        # Find agent names (capitalized words that appear as subjects)
        words = re.findall(r'\b([A-Z][a-z]+)\b', prompt)
        for word in words:
            if word.lower() not in ['the', 'and', 'but', 'that', 'which', 'what', 'who']:
                agents.add(word)

        # Parse each sentence for knowledge attribution
        for line in lines:
            line_lower = line.lower()
            # Look for patterns like "Alice knows that X", "Bob believes Y"
            knows_match = re.search(r'([A-Z][a-z]+)\s+(?:knows|believes|thinks|sees)\s+(?:that\s+)?([^.,]+)', line)
            if knows_match:
                agent = knows_match.group(1)
                fact = knows_match.group(2).strip()
                agents.add(agent)
                if agent not in agent_knowledge:
                    agent_knowledge[agent] = set()
                agent_knowledge[agent].add(fact)
                facts.add(fact)

            # Look for implications "If X then Y"
            if_match = re.search(r'if\s+([^,]+),\s*then\s+([^.,]+)', line_lower)
            if if_match:
                premise = if_match.group(1).strip()
                conclusion = if_match.group(2).strip()
                implications.append((premise, conclusion))

            # Look for factual statements not attributed to agents
            elif not re.search(r'\b(?:knows|believes|thinks|sees)\b', line_lower):
                # Simple fact pattern: "The cat is on the mat"
                fact_match = re.search(r'^([^.,]+(?:is|are|was|were)[^.,]+)', line_lower)
                if fact_match:
                    fact = fact_match.group(1).strip()
                    facts.add(fact)

        # Clean up agents - remove common non-agent words
        common_non_agents = {'What', 'Which', 'Who', 'How', 'Why', 'When', 'Where'}
        agents = agents - common_non_agents

        return {
            "agents": list(agents),
            "agent_knowledge": agent_knowledge,
            "facts": list(facts),
            "implications": implications,
            "query": query,
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use thermodynamic concepts to model knowledge states and perspective shifts."""
        agents = structure["agents"]
        agent_knowledge = structure["agent_knowledge"]
        facts = structure["facts"]
        implications = structure["implications"]
        query = structure["query"]

        # THERMODYNAMIC ANALOGY:
        # Knowledge states as energy levels
        # Certainty as low entropy (ordered state)
        # Perspective shift as heat transfer between systems

        # Phase 1: Build belief tracking using T1 primitives
        observations = []
        for agent, known_facts in agent_knowledge.items():
            for fact in known_facts:
                observations.append((agent, fact, True))

        # T1 PRIMITIVE 1: Track beliefs of different agents
        belief_states = track_beliefs(agents, observations)
        if belief_states is None:
            belief_states = {agent: set() for agent in agents}
            for agent, known_facts in agent_knowledge.items():
                belief_states[agent] = set(known_facts)

        # T1 PRIMITIVE 2: Apply modus ponens to expand knowledge
        all_known_facts = set()
        for agent in agents:
            agent_facts = set(belief_states.get(agent, set()))
            # Apply logical inference
            new_facts = modus_ponens(implications, agent_facts)
            if new_facts:
                agent_facts.update(new_facts)
            belief_states[agent] = agent_facts
            all_known_facts.update(agent_facts)

        # Phase 2: Build Bayesian Network for knowledge propagation
        # Nodes: Agents' knowledge states
        # Edges: Communication/observation paths
        edges = []
        for i, agent1 in enumerate(agents):
            for j, agent2 in enumerate(agents):
                if i != j:
                    # Assume potential communication between all agents
                    edges.append((agent1, agent2))

        # Build simple BN with uniform priors
        cpd_specs = {}
        for agent in agents:
            # Knowledge probability based on what they know
            known_count = len(belief_states.get(agent, set()))
            total_facts = len(all_known_facts) if all_known_facts else 1
            knowledge_prob = known_count / total_facts if total_facts > 0 else 0.5

            # AMINO ACID 1: Build Bayesian Network
            cpd_specs[agent] = {
                'variable': agent,
                'variable_card': 2,  # 0: ignorant, 1: knowledgeable
                'evidence': [],
                'evidence_card': [],
                'values': [[1 - knowledge_prob, knowledge_prob]]
            }

        bn_model = build_bn(edges, cpd_specs)
        if bn_model is None:
            # Fallback to simpler reasoning
            bn_model = None

        # Phase 3: Analyze perspective differences using thermodynamic concepts
        # Compute "knowledge entropy" for each agent
        agent_entropies = {}
        for agent in agents:
            known_facts = belief_states.get(agent, set())
            unknown_facts = all_known_facts - known_facts

            # Create probability distribution over facts
            if all_known_facts:
                probs = []
                for fact in all_known_facts:
                    prob = 1.0 if fact in known_facts else 0.0
                    probs.append(prob)
                # T1 PRIMITIVE 3: Compute entropy of knowledge state
                agent_entropy = entropy(probs) if probs else 1.0
            else:
                agent_entropy = 1.0  # Maximum uncertainty

            agent_entropies[agent] = agent_entropy

        # Determine which agent has most complete perspective (lowest entropy)
        if agent_entropies:
            best_agent = min(agent_entropies.items(), key=lambda x: x[1])[0]
        else:
            best_agent = agents[0] if agents else "Unknown"

        # Phase 4: Answer the query
        computed_answer = self._answer_query(query, best_agent, belief_states, bn_model)

        # T1 PRIMITIVE 4: Compute confidence from agreement of multiple reasoning paths
        confidence_scores = []
        # Path 1: Entropy-based selection
        confidence_scores.append(1.0 - min(agent_entropies.values()) if agent_entropies else 0.5)

        # Path 2: Check if BN supports the answer
        if bn_model is not None:
            try:
                # AMINO ACID 2: Query Bayesian network
                query_result = conditional_query(bn_model, [best_agent], {})
                if query_result is not None and len(query_result) > 0:
                    # Get probability of being knowledgeable
                    prob_knowledgeable = query_result.get(1, 0.0)
                    confidence_scores.append(prob_knowledgeable)
            except:
                confidence_scores.append(0.5)

        # Path 3: Check logical consistency of answer
        if computed_answer in agents:
            agent_facts = belief_states.get(computed_answer, set())
            # Check if answer is consistent with known facts
            if agent_facts:
                confidence_scores.append(0.8)
            else:
                confidence_scores.append(0.3)

        final_confidence = confidence_from_agreement(confidence_scores) if confidence_scores else 0.5

        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "reasoning": f"Agent {computed_answer} has lowest knowledge entropy ({agent_entropies.get(computed_answer, 0):.3f}) indicating most complete perspective.",
            "agent_entropies": agent_entropies,
            "belief_states": belief_states
        }

    def _answer_query(self, query: str, best_agent: str, belief_states: Dict[str, Set[str]],
                      bn_model: Any) -> str:
        """Extract the answer to the specific query."""
        query_lower = query.lower()

        # Common query patterns in perspective shift problems
        if "who knows" in query_lower or "which agent knows" in query_lower:
            return best_agent

        if "what does" in query_lower and "think" in query_lower:
            # Extract agent name from query
            agent_match = re.search(r'what does\s+([A-Z][a-z]+)\s+think', query)
            if agent_match:
                return agent_match.group(1)
            return best_agent

        if "perspective" in query_lower or "view" in query_lower:
            return best_agent

        # Default: return the agent with most complete knowledge
        return best_agent

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        results = []

        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            candidate_lower = candidate.lower()
            computed_lower = computed_answer.lower()

            if computed_lower in candidate_lower:
                # Exact or partial match
                score = 1.0
            else:
                # Fallback: NCD similarity to reasoning
                score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))

            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })

        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored

        # Extract raw scores
        raw_scores = [item["raw_score"] for item in scored]

        # Simple calibration: normalize to [0, 1] range
        min_score = min(raw_scores)
        max_score = max(raw_scores)

        if max_score - min_score > 0.001:
            for item in scored:
                item["score"] = (item["raw_score"] - min_score) / (max_score - min_score)
        else:
            # All scores are similar, keep as is
            for item in scored:
                item["score"] = item["raw_score"]

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