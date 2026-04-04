import re
import zlib
from typing import Dict, List, Any, Set, Tuple
from forge_primitives import (
    sally_anne_test,
    track_beliefs,
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
    """quantum_mechanics x pgmpy_acids - perspective_shift"""

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
        """Parse prompt to extract agents, facts, observations, and question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        agents = set()
        facts = set()
        observations = []
        question = lines[-1] if lines else ""

        # Extract capitalized names as potential agents
        for line in lines:
            # Find multi-word capitalized names (likely agents)
            agent_matches = re.findall(r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b', line)
            for match in agent_matches:
                if len(match.split()) <= 3:  # Avoid long phrases
                    agents.add(match)

            # Extract simple facts (lowercase statements)
            if 'knows' in line.lower() or 'believes' in line.lower() or 'sees' in line.lower():
                # Try to parse observation tuples: (agent, fact, truth_value)
                words = line.split()
                for i, word in enumerate(words):
                    if word.lower() in ['knows', 'believes', 'sees', 'observed']:
                        if i > 0 and words[i-1] in agents:
                            agent = words[i-1]
                            # Extract fact (rest of sentence)
                            fact_start = i + 1
                            fact = ' '.join(words[fact_start:]).rstrip('.,')
                            if fact:
                                facts.add(fact)
                                # Determine truth value from context
                                truth = True
                                if 'not' in line.lower() or "doesn't" in line.lower():
                                    truth = False
                                observations.append((agent, fact, truth))

        # Clean up agents: remove those that appear in facts (likely not agents)
        agents = {a for a in agents if a not in ' '.join(facts)}

        return {
            "agents": list(agents),
            "facts": list(facts),
            "observations": observations,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use quantum superposition and entanglement analogies to model knowledge states."""
        agents = structure["agents"]
        facts = structure["facts"]
        observations = structure["observations"]
        question = structure["question"]

        # Initialize quantum-inspired knowledge representation
        # Each agent's knowledge is a superposition of possible belief states
        agent_beliefs = {agent: {} for agent in agents}

        # PHASE 2A: Use T1 primitives for basic theory of mind
        # 1. Track beliefs from observations
        if observations:
            belief_tracking = track_beliefs(agents, observations)
            if belief_tracking:
                for agent, believed_facts in belief_tracking.items():
                    for fact in believed_facts:
                        agent_beliefs[agent][fact] = 1.0  # Certain knowledge

        # 2. Apply Sally-Anne test for perspective shifts
        # Look for object movement scenarios in the prompt
        if "moved" in structure["raw"].lower() or "moves" in structure["raw"].lower():
            # Extract movement info
            moved_match = re.search(r'(\w+) moved (?:the )?(\w+) from (\w+) to (\w+)', structure["raw"], re.IGNORECASE)
            if moved_match:
                who_moved, obj, orig_loc, new_loc = moved_match.groups()
                # Find who saw the move
                saw_move = set()
                for agent in agents:
                    if f"{agent} saw" in structure["raw"] or f"{agent} observed" in structure["raw"]:
                        saw_move.add(agent)
                
                sally_result = sally_anne_test(who_moved, saw_move, orig_loc, new_loc)
                if sally_result:
                    for agent, believed_loc in sally_result.items():
                        fact = f"{obj} is at {believed_loc}"
                        agent_beliefs[agent][fact] = 1.0

        # PHASE 2B: Use amino acids for advanced reasoning
        # Build Bayesian network to model knowledge dependencies
        edges = []
        cpd_specs = []
        
        # Create nodes for each fact and agent's belief in that fact
        for fact in facts:
            fact_node = f"FACT_{hash(fact) % 1000}"
            for agent in agents:
                belief_node = f"{agent}_BELIEVES_{hash(fact) % 1000}"
                edges.append((fact_node, belief_node))  # Fact influences belief
                
                # Set CPD based on observations
                belief_value = 0.5  # Default superposition (uncertain)
                for obs_agent, obs_fact, truth in observations:
                    if obs_agent == agent and obs_fact == fact:
                        belief_value = 1.0 if truth else 0.0
                
                cpd_specs.append({
                    'variable': belief_node,
                    'variable_card': 2,
                    'values': [[1 - belief_value, belief_value]],  # [False, True]
                    'evidence': [fact_node],
                    'evidence_card': [2]
                })

        # Add edges between agents' beliefs (entanglement)
        for i, agent1 in enumerate(agents):
            for j, agent2 in enumerate(agents):
                if i < j:
                    # Entangle beliefs: if one agent knows, it may affect others
                    for fact in facts:
                        node1 = f"{agent1}_BELIEVES_{hash(fact) % 1000}"
                        node2 = f"{agent2}_BELIEVES_{hash(fact) % 1000}"
                        edges.append((node1, node2))

        # Build Bayesian network
        bn_model = build_bn(edges, cpd_specs)
        
        # Query the network for perspective differences
        perspective_differences = {}
        if bn_model is not None:
            for fact in facts[:3]:  # Limit to first 3 facts for efficiency
                fact_node = f"FACT_{hash(fact) % 1000}"
                for agent in agents:
                    belief_node = f"{agent}_BELIEVES_{hash(fact) % 1000}"
                    
                    # Query probability of belief given the fact
                    query_result = conditional_query(
                        bn_model, 
                        [belief_node], 
                        {fact_node: 1}  # Assume fact is true
                    )
                    
                    if query_result is not None and belief_node in query_result:
                        prob_belief = query_result[belief_node].get(1, 0.5)
                        if agent not in perspective_differences:
                            perspective_differences[agent] = {}
                        perspective_differences[agent][fact] = prob_belief

        # PHASE 2C: Use active trails to find knowledge propagation
        knowledge_paths = {}
        if bn_model is not None:
            for agent in agents[:2]:  # Limit for efficiency
                start_vars = [f"{agent}_BELIEVES_{hash(fact) % 1000}" for fact in facts[:2]]
                if start_vars:
                    trails = active_trails(bn_model, start_vars)
                    if trails:
                        knowledge_paths[agent] = list(trails)

        # PHASE 2D: Determine answer to the question
        computed_answer = ""
        confidence = 0.5
        
        # Extract what is being asked
        if "who" in question.lower():
            # Find agent with most certain knowledge
            agent_certainty = {}
            for agent in agents:
                if agent in agent_beliefs:
                    certainty = sum(agent_beliefs[agent].values()) / max(len(agent_beliefs[agent]), 1)
                    agent_certainty[agent] = certainty
            
            if agent_certainty:
                best_agent = max(agent_certainty.items(), key=lambda x: x[1])
                computed_answer = best_agent[0]
                confidence = best_agent[1]
        
        elif "what" in question.lower() and "knows" in question.lower():
            # Find what a specific agent knows
            for agent in agents:
                if agent.lower() in question.lower():
                    known_facts = [fact for fact, cert in agent_beliefs.get(agent, {}).items() if cert > 0.7]
                    if known_facts:
                        computed_answer = known_facts[0]
                        confidence = 0.8
                    break
        
        # Fallback: use topological sort of knowledge dependencies
        if not computed_answer and edges:
            try:
                sorted_nodes = topological_sort(edges)
                if sorted_nodes:
                    # Last node in topological order has most dependencies
                    last_node = sorted_nodes[-1]
                    # Extract agent name from node
                    agent_match = re.search(r'^(\w+)_BELIEVES', last_node)
                    if agent_match:
                        computed_answer = agent_match.group(1)
                        confidence = 0.6
            except:
                pass

        # Final fallback
        if not computed_answer and agents:
            computed_answer = agents[0]
            confidence = 0.5

        # Use confidence_from_agreement to refine confidence
        if perspective_differences:
            # Collect certainty scores for each agent
            certainty_scores = []
            for agent, beliefs in perspective_differences.items():
                if beliefs:
                    avg_certainty = sum(beliefs.values()) / len(beliefs)
                    certainty_scores.append(avg_certainty)
            
            if certainty_scores:
                agreement_confidence = confidence_from_agreement(certainty_scores)
                if agreement_confidence is not None:
                    # Combine with existing confidence
                    confidence = (confidence + agreement_confidence) / 2

        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Quantum-inspired belief superposition analysis. Agents: {agents}. Key facts: {facts[:3]}.",
            "agent_beliefs": agent_beliefs,
            "perspective_differences": perspective_differences
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact or substring match of computed answer
            if computed_answer and computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                base_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
            # Adjust based on confidence
            adjusted_score = base_score * reasoning_result["confidence"]
            
            results.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        scores = [item["score"] for item in scored]
        if not scores:
            return scored
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score - min_score > 0:
            # Normalize to [0, 1] range
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        else:
            # All scores equal, assign 0.5
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