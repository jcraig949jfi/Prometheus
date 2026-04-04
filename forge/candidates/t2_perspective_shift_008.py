import re
import zlib
from typing import Dict, List, Any

from forge_primitives import (
    track_beliefs,
    sally_anne_test,
    entropy,
    confidence_from_agreement,
    modus_ponens
)
from forge.amino_acids.pgmpy_acids import (
    build_bn,
    conditional_query,
    active_trails
)


class ReasoningTool:
    """Information theory x Bayesian networks - perspective_shift"""

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
        """Extract agents, facts, observations, and question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""

        agents = set()
        facts = set()
        observations = []
        agent_knowledge = {}

        # Extract agent names (capitalized words that appear as subjects)
        words = re.findall(r'\b([A-Z][a-z]+)\b', prompt)
        for word in words:
            if word.lower() not in ['the', 'and', 'but', 'that', 'this', 'which']:
                agents.add(word)

        # Extract facts (simple declarative statements before "knows" or "sees")
        fact_pattern = r'([A-Z][^.!?]*?(?:is|are|has|have|was|were)[^.!?]*[.!?])'
        raw_facts = re.findall(fact_pattern, prompt)
        for fact in raw_facts:
            clean_fact = fact.strip().lower()
            if len(clean_fact.split()) < 10:  # Avoid long complex sentences
                facts.add(clean_fact)

        # Extract observations: "Agent sees/knows that..."
        know_pattern = r'([A-Z][a-z]+)\s+(?:knows|sees|observes|notices)\s+(?:that\s+)?([^.!?]+)'
        knows = re.findall(know_pattern, prompt, re.IGNORECASE)
        for agent, knowledge in knows:
            agents.add(agent)
            clean_knowledge = knowledge.strip().lower().rstrip('.')
            observations.append((agent, clean_knowledge, True))
            if agent not in agent_knowledge:
                agent_knowledge[agent] = set()
            agent_knowledge[agent].add(clean_knowledge)

        # Extract question focus (what is being asked about)
        question_focus = ""
        if "who" in question.lower():
            question_focus = "agent"
        elif "what" in question.lower():
            question_focus = "fact"
        elif "where" in question.lower():
            question_focus = "location"

        return {
            "agents": list(agents),
            "facts": list(facts),
            "observations": observations,
            "question": question,
            "question_focus": question_focus,
            "agent_knowledge": agent_knowledge,
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use information theory and Bayesian networks to model perspective shifts."""
        agents = structure["agents"]
        observations = structure["observations"]
        question = structure["question"]
        agent_knowledge = structure["agent_knowledge"]

        # T1 PRIMITIVE 1: Track beliefs of each agent
        belief_state = track_beliefs(agents, observations)
        if belief_state is None:
            belief_state = {agent: set() for agent in agents}

        # T1 PRIMITIVE 2: Compute entropy of belief distributions
        belief_entropies = {}
        for agent in agents:
            beliefs = list(belief_state.get(agent, set()))
            if beliefs:
                # Create a simple probability distribution over possible facts
                # Each fact believed is considered equally probable
                n = len(beliefs)
                probs = [1.0 / n] * n if n > 0 else []
                if probs:
                    ent = entropy(probs)
                    belief_entropies[agent] = ent
                else:
                    belief_entropies[agent] = 0.0
            else:
                belief_entropies[agent] = 0.0

        # AMINO ACID 1: Build Bayesian network for information flow
        bn_edges = []
        for agent in agents:
            # Connect agents to facts they know
            for fact in agent_knowledge.get(agent, set()):
                bn_edges.append((agent, fact))

        # Add edges between agents who might share information
        # (simplified: if one agent knows something another might learn)
        for i, agent1 in enumerate(agents):
            for j, agent2 in enumerate(agents):
                if i != j:
                    common = agent_knowledge.get(agent1, set()) & agent_knowledge.get(agent2, set())
                    if common:
                        bn_edges.append((agent1, agent2))

        bn_model = None
        information_paths = {}
        if bn_edges:
            bn_model = build_bn(bn_edges)
            if bn_model is not None:
                # AMINO ACID 2: Find active information trails
                for agent in agents:
                    trails = active_trails(bn_model, [agent], observed=None)
                    if trails is not None:
                        information_paths[agent] = trails.get(agent, set())
                    else:
                        information_paths[agent] = set()

        # T1 PRIMITIVE 3: Use modus ponens to infer new beliefs
        inferred_beliefs = {}
        for agent in agents:
            agent_facts = belief_state.get(agent, set())
            # Create simple implication rules from known facts
            premises = []
            for fact in agent_facts:
                # Simple rule: if fact contains "if...then" pattern
                if "if" in fact and "then" in fact:
                    parts = fact.split("then")
                    if len(parts) == 2:
                        antecedent = parts[0].replace("if", "").strip()
                        consequent = parts[1].strip()
                        premises.append((antecedent, consequent))

            if premises:
                new_facts = modus_ponens(premises, agent_facts)
                if new_facts is not None:
                    inferred_beliefs[agent] = new_facts
                else:
                    inferred_beliefs[agent] = set()
            else:
                inferred_beliefs[agent] = set()

        # AMINO ACID 3: Query conditional probabilities for perspective differences
        perspective_differences = {}
        if bn_model is not None:
            for agent in agents:
                # Query what this agent believes about key facts
                for fact in structure.get("facts", [])[:3]:  # Limit to first 3 facts
                    evidence = {agent: "knows"}
                    query_result = conditional_query(bn_model, [fact], evidence)
                    if query_result is not None:
                        perspective_differences[f"{agent}_{fact}"] = query_result

        # Determine which agent has the most/least information based on entropy
        if belief_entropies:
            max_entropy_agent = max(belief_entropies.items(), key=lambda x: x[1])[0]
            min_entropy_agent = min(belief_entropies.items(), key=lambda x: x[1])[0]
        else:
            max_entropy_agent = agents[0] if agents else ""
            min_entropy_agent = agents[0] if agents else ""

        # T1 PRIMITIVE 4: Compute confidence from agreement among agents
        agreement_scores = []
        for fact in structure.get("facts", [])[:3]:
            believing_agents = []
            for agent in agents:
                agent_beliefs = belief_state.get(agent, set())
                if fact in agent_beliefs:
                    believing_agents.append(1.0)
                else:
                    believing_agents.append(0.0)
            if believing_agents:
                conf = confidence_from_agreement(believing_agents)
                if conf is not None:
                    agreement_scores.append(conf)

        overall_confidence = sum(agreement_scores) / len(agreement_scores) if agreement_scores else 0.5

        # Determine answer based on question focus
        computed_answer = ""
        reasoning_text = ""

        if "who knows" in question.lower() or "who believes" in question.lower():
            # Find agent with most/least knowledge
            if "most" in question.lower():
                computed_answer = max_entropy_agent
                reasoning_text = f"{max_entropy_agent} has highest belief entropy ({belief_entropies.get(max_entropy_agent, 0):.2f})"
            elif "least" in question.lower():
                computed_answer = min_entropy_agent
                reasoning_text = f"{min_entropy_agent} has lowest belief entropy ({belief_entropies.get(min_entropy_agent, 0):.2f})"
            else:
                # Default: agent mentioned first in observations
                if observations:
                    computed_answer = observations[0][0]
                else:
                    computed_answer = agents[0] if agents else ""

        elif "what does" in question.lower() and "think" in question.lower():
            # Extract agent from question
            agent_match = re.search(r'what does ([A-Z][a-z]+) think', question.lower())
            if agent_match:
                target_agent = agent_match.group(1).capitalize()
                if target_agent in inferred_beliefs:
                    beliefs = inferred_beliefs[target_agent]
                    if beliefs:
                        computed_answer = list(beliefs)[0]
                    else:
                        computed_answer = "nothing specific"
                else:
                    computed_answer = "unknown"
            else:
                computed_answer = "cannot determine"

        else:
            # Fallback: use the agent with most inferred beliefs
            if inferred_beliefs:
                agent_with_most = max(inferred_beliefs.items(), key=lambda x: len(x[1]))[0]
                computed_answer = agent_with_most
            else:
                computed_answer = agents[0] if agents else ""

        return {
            "answer": computed_answer,
            "confidence": overall_confidence,
            "reasoning": reasoning_text,
            "belief_entropies": belief_entropies,
            "inferred_beliefs": inferred_beliefs,
            "information_paths": information_paths
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        confidence = reasoning_result["confidence"]

        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity with reasoning text
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
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored

        scores = [item["score"] for item in scored]
        min_score = min(scores)
        max_score = max(scores)

        if max_score - min_score > 0:
            # Normalize to [0, 1] range
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        else:
            # All scores equal, assign uniform scores
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