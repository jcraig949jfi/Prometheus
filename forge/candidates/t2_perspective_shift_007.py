import re
import zlib
from typing import Dict, List, Any, Set, Tuple

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
    active_trails,
    get_markov_blanket
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
        """Extract agents, facts, observations, and the question from the prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        agents: Set[str] = set()
        facts: Set[str] = set()
        observations: List[Tuple[str, str, bool]] = []
        question = lines[-1] if lines else ""

        # Extract agent names (capitalized words that appear as subjects)
        for line in lines:
            words = line.split()
            for i, word in enumerate(words):
                if word[0].isupper() and len(word) > 1:
                    # Check if it's likely an agent (followed by verbs like 'sees', 'knows', 'believes')
                    if i + 1 < len(words):
                        next_word = words[i + 1].lower()
                        if any(v in next_word for v in ['sees', 'knows', 'believes', 'thinks', 'hears']):
                            agents.add(word)

        # Extract facts (quoted phrases or noun phrases after 'that')
        for line in lines:
            if '"' in line:
                # Extract quoted facts
                quotes = re.findall(r'"([^"]*)"', line)
                facts.update(quotes)
            # Extract facts after 'that'
            if 'that' in line.lower():
                parts = line.split('that')
                if len(parts) > 1:
                    fact = parts[1].strip().rstrip('.')
                    if fact:
                        facts.add(fact)

        # Extract observations (agent, fact, True/False for belief)
        for line in lines:
            line_lower = line.lower()
            for agent in agents:
                if agent.lower() in line_lower:
                    # Check for belief indicators
                    if 'sees' in line_lower or 'observes' in line_lower:
                        # Agent sees something -> believes it
                        for fact in facts:
                            if fact.lower() in line_lower:
                                observations.append((agent, fact, True))
                    elif 'does not know' in line_lower or 'unaware' in line_lower:
                        # Agent doesn't know something -> doesn't believe it
                        for fact in facts:
                            if fact.lower() in line_lower:
                                observations.append((agent, fact, False))

        return {
            "agents": list(agents),
            "facts": list(facts),
            "observations": observations,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use information theory and Bayesian networks to compute perspective differences."""
        agents = structure["agents"]
        facts = structure["facts"]
        observations = structure["observations"]
        question = structure["question"]

        # Use T1 primitive: track_beliefs to get initial belief states
        belief_states = track_beliefs(agents, observations)
        if belief_states is None:
            belief_states = {}

        # Use T1 primitive: sally_anne_test for false belief reasoning
        # Extract movement info if present in prompt
        movement_info = self._extract_movement_info(structure["raw"])
        if movement_info:
            false_belief_result = sally_anne_test(
                who_moved=movement_info["who_moved"],
                who_saw_move=movement_info["who_saw_move"],
                original_location=movement_info["original_location"],
                new_location=movement_info["new_location"]
            )
        else:
            false_belief_result = {}

        # Build Bayesian network for information flow
        # Nodes: agents' knowledge states
        edges = []
        for agent in agents:
            # Each agent's knowledge depends on what they observed
            for obs in observations:
                if obs[0] == agent:
                    # Create edge from observation to agent's belief
                    fact_node = f"Fact_{obs[1].replace(' ', '_')}"
                    agent_node = f"{agent}_knows_{obs[1].replace(' ', '_')}"
                    edges.append((fact_node, agent_node))

        # Add edges for communication between agents
        # If prompt mentions communication, extract it
        if "tells" in structure["raw"].lower() or "informs" in structure["raw"].lower():
            for agent1 in agents:
                for agent2 in agents:
                    if agent1 != agent2:
                        if f"{agent1} tells {agent2}" in structure["raw"]:
                            edges.append((f"{agent1}_knowledge", f"{agent2}_knowledge"))

        # Use amino acid: build Bayesian network
        bn_model = build_bn(edges, cpd_specs=None)

        # Compute information entropy of each agent's belief state
        agent_entropies = {}
        for agent in agents:
            beliefs = belief_states.get(agent, set())
            if beliefs:
                # Convert to probability distribution over facts
                probs = []
                for fact in facts:
                    if fact in beliefs:
                        probs.append(0.9)  # High probability for believed facts
                    else:
                        probs.append(0.1)  # Low probability for disbelieved facts
                # Normalize
                total = sum(probs)
                if total > 0:
                    probs = [p/total for p in probs]
                    # Use T1 primitive: entropy
                    agent_entropy = entropy(probs)
                    agent_entropies[agent] = agent_entropy
                else:
                    agent_entropies[agent] = 1.0  # Maximum uncertainty
            else:
                agent_entropies[agent] = 1.0  # No beliefs -> maximum entropy

        # Use amino acid: active_trails to find information flow
        info_flow = {}
        if bn_model is not None:
            for agent in agents:
                agent_nodes = [node for node in bn_model.nodes() if agent in node]
                if agent_nodes:
                    trails = active_trails(bn_model, agent_nodes[:1], observed=None)
                    if trails is not None:
                        info_flow[agent] = len(trails.get(agent_nodes[0], []))

        # Determine which agent's perspective is asked about
        target_agent = None
        for agent in agents:
            if agent.lower() in question.lower():
                target_agent = agent
                break

        if not target_agent and agents:
            # Default to first agent mentioned in question
            for word in question.split():
                if word in agents:
                    target_agent = word
                    break

        # Use amino acid: conditional_query to compute what target agent believes
        target_belief = ""
        if target_agent and bn_model is not None:
            # Find a fact node to query
            fact_nodes = [node for node in bn_model.nodes() if node.startswith("Fact_")]
            if fact_nodes and target_agent:
                target_nodes = [node for node in bn_model.nodes() if target_agent in node]
                if target_nodes:
                    evidence = {}
                    # Set evidence based on observations
                    for obs in observations:
                        if obs[0] == target_agent:
                            node_name = f"{target_agent}_knows_{obs[1].replace(' ', '_')}"
                            evidence[node_name] = obs[2]
                    
                    if evidence:
                        query_result = conditional_query(bn_model, target_nodes[:1], evidence)
                        if query_result is not None:
                            # Extract the most probable belief
                            if hasattr(query_result, 'values'):
                                target_belief = str(list(query_result.values())[0])

        # Use T1 primitive: modus_ponens for logical inference
        implications = []
        for fact1 in facts:
            for fact2 in facts:
                if fact1 != fact2:
                    # Check if one fact implies another in the prompt
                    if f"if {fact1}" in structure["raw"].lower() and f"then {fact2}" in structure["raw"].lower():
                        implications.append((fact1, fact2))

        known_facts = set()
        for agent, beliefs in belief_states.items():
            known_facts.update(beliefs)

        inferred_facts = modus_ponens(implications, known_facts)
        if inferred_facts is None:
            inferred_facts = set()

        # Compute confidence using agreement between different reasoning methods
        scores = []
        # Score from belief tracking
        if target_agent and belief_states.get(target_agent):
            scores.append(0.8)
        # Score from Bayesian network
        if target_belief:
            scores.append(0.7)
        # Score from logical inference
        if inferred_facts:
            scores.append(0.6)

        # Use T1 primitive: confidence_from_agreement
        if scores:
            confidence = confidence_from_agreement(scores)
        else:
            confidence = 0.5

        # Determine the computed answer
        computed_answer = ""
        if target_agent:
            # Answer is what the target agent believes/knows
            if target_belief:
                computed_answer = target_belief
            elif target_agent in belief_states and belief_states[target_agent]:
                # Use the first fact the agent believes
                computed_answer = next(iter(belief_states[target_agent]), "")
            else:
                # Fallback: agent name with their information state
                computed_answer = f"{target_agent} has entropy {agent_entropies.get(target_agent, 1.0):.2f}"
        else:
            # Compare perspectives
            if agents:
                # Find agent with most/least information based on entropy
                if "most" in question.lower() or "best" in question.lower():
                    min_entropy_agent = min(agent_entropies.items(), key=lambda x: x[1])[0]
                    computed_answer = min_entropy_agent
                elif "least" in question.lower() or "worst" in question.lower():
                    max_entropy_agent = max(agent_entropies.items(), key=lambda x: x[1])[0]
                    computed_answer = max_entropy_agent
                else:
                    computed_answer = agents[0]

        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Agent perspectives analyzed using information theory. Target: {target_agent}, Beliefs: {belief_states.get(target_agent, set())}, Entropy: {agent_entropies.get(target_agent, 1.0):.2f}",
            "target_agent": target_agent,
            "agent_entropies": agent_entropies
        }

    def _extract_movement_info(self, prompt: str) -> Dict[str, Any]:
        """Extract movement information for false belief scenarios."""
        lines = prompt.lower().split('.')
        who_moved = ""
        who_saw_move = set()
        original_location = ""
        new_location = ""

        for line in lines:
            if 'moves' in line or 'moved' in line:
                words = line.split()
                for i, word in enumerate(words):
                    if word in ['moves', 'moved'] and i > 0:
                        who_moved = words[i-1].capitalize()
                        break
            
            if 'from' in line and 'to' in line:
                parts = line.split('from')
                if len(parts) > 1:
                    subparts = parts[1].split('to')
                    if len(subparts) > 1:
                        original_location = subparts[0].strip()
                        new_location = subparts[1].strip().rstrip('.')

            if 'sees' in line and 'move' in line:
                words = line.split()
                for i, word in enumerate(words):
                    if word == 'sees' and i > 0:
                        who_saw_move.add(words[i-1].capitalize())

        if who_moved and original_location and new_location:
            return {
                "who_moved": who_moved,
                "who_saw_move": who_saw_move,
                "original_location": original_location,
                "new_location": new_location
            }
        return {}

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

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        target_agent = reasoning_result.get("target_agent", "")
        agent_entropies = reasoning_result.get("agent_entropies", {})
        
        results = []
        for candidate in candidates:
            score = 0.0
            
            # Primary scoring: check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 0.9
            elif target_agent and target_agent.lower() in candidate.lower():
                # Candidate mentions the target agent
                score = 0.7
                
                # Check if candidate mentions entropy-related concepts
                entropy_terms = ['uncertain', 'certain', 'knows', 'doesn\'t know', 'unsure']
                if any(term in candidate.lower() for term in entropy_terms):
                    score += 0.1
            else:
                # Fallback: NCD similarity
                ncd_score = self._ncd(computed_answer, candidate)
                score = 1.0 / (1.0 + ncd_score)
            
            # Adjust based on confidence
            confidence = reasoning_result.get("confidence", 0.5)
            score *= confidence
            
            results.append({
                "candidate": candidate,
                "score": min(max(score, 0.0), 1.0),
                "raw_score": score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        # Extract raw scores
        raw_scores = [item["raw_score"] for item in scored]
        
        # Simple min-max normalization if there's variation
        min_score = min(raw_scores)
        max_score = max(raw_scores)
        
        if max_score > min_score:
            for item in scored:
                normalized = (item["raw_score"] - min_score) / (max_score - min_score)
                item["score"] = normalized
        else:
            # All scores equal, assign uniform scores
            for item in scored:
                item["score"] = 0.5
        
        return scored