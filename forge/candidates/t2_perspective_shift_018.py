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
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, active_trails
from forge.amino_acids.pysat_acids import check_entailment, detect_paradox


class ReasoningTool:
    """Signal processing x Bayesian networks - perspective_shift"""

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
        if not lines:
            return {"agents": [], "facts": set(), "observations": [], "question": "", "raw": prompt}

        agents = []
        facts = set()
        observations = []
        question = lines[-1] if lines else ""

        # Extract agent names (capitalized proper nouns, often followed by 'knows', 'sees', etc.)
        agent_pattern = r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b'
        potential_agents = re.findall(agent_pattern, prompt)
        for agent in potential_agents:
            if agent.lower() not in ['the', 'a', 'an', 'and', 'but', 'or', 'if', 'then', 'that', 'this']:
                if any(keyword in prompt.lower() for keyword in [f'{agent.lower()} knows', f'{agent.lower()} sees', f'{agent.lower()} believes']):
                    agents.append(agent)

        # Extract facts (simple propositions, often in quotes or after 'that')
        fact_pattern = r'\"([^\"]+)\"|that ([^.,]+)'
        for match in re.finditer(fact_pattern, prompt):
            fact = match.group(1) or match.group(2)
            if fact and len(fact.split()) < 8:  # Avoid long sentences
                facts.add(fact.strip())

        # Extract observations (agent, fact, true/false)
        # Look for patterns like "Alice sees Bob leave" -> (Alice, "Bob leave", True)
        for line in lines:
            lower_line = line.lower()
            for agent in agents:
                agent_lower = agent.lower()
                if f'{agent_lower} sees' in lower_line or f'{agent_lower} observes' in lower_line:
                    # Find the fact being observed
                    fact_start = lower_line.find(agent_lower) + len(agent_lower)
                    rest = line[fact_start:].strip()
                    # Heuristic: fact is the next clause
                    fact_words = rest.split()
                    if len(fact_words) > 1:
                        fact = ' '.join(fact_words[1:4]) if len(fact_words) >= 4 else ' '.join(fact_words[1:])
                        observations.append((agent, fact, True))
                elif f'{agent_lower} knows' in lower_line:
                    fact_start = lower_line.find(agent_lower) + len(agent_lower)
                    rest = line[fact_start:].strip()
                    fact_words = rest.split()
                    if len(fact_words) > 1:
                        fact = ' '.join(fact_words[1:4]) if len(fact_words) >= 4 else ' '.join(fact_words[1:])
                        observations.append((agent, fact, True))

        # If no structured observations found, create simple ones from facts and agents
        if not observations and facts and agents:
            for fact in list(facts)[:3]:  # Limit to first few facts
                for agent in agents[:2]:  # Limit to first few agents
                    observations.append((agent, fact, True))

        return {
            "agents": list(set(agents)),
            "facts": facts,
            "observations": observations,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply signal processing concepts through Bayesian networks to compute perspective shifts."""
        agents = structure["agents"]
        observations = structure["observations"]
        question = structure["question"]
        facts = structure["facts"]

        # Signal processing metaphor: agents are receivers, facts are signals,
        # observations are received signals with possible noise/attenuation.
        # Knowledge states are filtered versions of the truth.

        # Use T1 primitive: track_beliefs to get initial belief states
        belief_states = track_beliefs(agents, observations)
        if belief_states is None:
            belief_states = {agent: set() for agent in agents}

        # Use T1 primitive: confidence_from_agreement on belief overlap
        agreement_scores = []
        for agent1 in agents:
            for agent2 in agents:
                if agent1 != agent2:
                    common = len(belief_states.get(agent1, set()) & belief_states.get(agent2, set()))
                    total = len(belief_states.get(agent1, set()) | belief_states.get(agent2, set()))
                    if total > 0:
                        agreement_scores.append(common / total)
        confidence = confidence_from_agreement(agreement_scores) if agreement_scores else 0.5

        # Use T1 primitive: entropy of belief distribution as uncertainty measure
        belief_entropy = 0.0
        if facts:
            # For each fact, compute proportion of agents who believe it
            fact_belief_probs = []
            for fact in facts:
                believers = sum(1 for agent in agents if fact in belief_states.get(agent, set()))
                prob = believers / len(agents) if agents else 0.0
                if 0 < prob < 1:
                    fact_belief_probs.append(prob)
            if fact_belief_probs:
                # Normalize to distribution
                total = sum(fact_belief_probs)
                if total > 0:
                    norm_probs = [p/total for p in fact_belief_probs]
                    belief_entropy = entropy(norm_probs)

        # Build Bayesian network for causal knowledge propagation
        # Nodes: Facts as sources, Agents as receivers with conditional probabilities
        edges = []
        cpd_specs = []

        # Add fact nodes
        fact_nodes = [f"Fact_{i}" for i, fact in enumerate(facts)]
        
        # Add agent nodes with edges from facts they observe
        for agent in agents:
            agent_node = f"Agent_{agent}"
            # Find facts this agent observes
            observed_facts = [fact for (obs_agent, fact, truth) in observations if obs_agent == agent and truth]
            for i, fact in enumerate(facts):
                if fact in observed_facts:
                    edges.append((f"Fact_{i}", agent_node))
        
        if edges:
            # Build simple CPDs: P(Agent_knows = True | Fact = True) = high
            for agent in agents:
                agent_node = f"Agent_{agent}"
                parent_facts = [parent for (parent, child) in edges if child == agent_node]
                if parent_facts:
                    # CPD: Agent knows if ANY parent fact is true (OR gate)
                    cpd_specs.append({
                        'variable': agent_node,
                        'variable_card': 2,
                        'evidence': parent_facts,
                        'evidence_card': [2] * len(parent_facts),
                        'values': [[0.0, 1.0] if any(ev) else [1.0, 0.0] for ev in self._truth_table(len(parent_facts))]
                    })
                else:
                    # No parents: prior probability based on observations
                    knows_count = sum(1 for (obs_agent, fact, truth) in observations if obs_agent == agent and truth)
                    prior = min(0.9, knows_count / max(1, len(facts)))
                    cpd_specs.append({
                        'variable': agent_node,
                        'variable_card': 2,
                        'values': [[1-prior, prior]]
                    })
            
            # Fact priors (uniform)
            for i, fact_node in enumerate(fact_nodes):
                cpd_specs.append({
                    'variable': fact_node,
                    'variable_card': 2,
                    'values': [[0.5, 0.5]]
                })

            # Use amino acid: build Bayesian network
            bn_model = build_bn(edges, cpd_specs)
            
            if bn_model is not None:
                # Use amino acid: active_trails to see knowledge propagation
                # Which agents' knowledge states are reachable from which facts?
                reachable_map = {}
                for fact_node in fact_nodes:
                    trails = active_trails(bn_model, [fact_node], observed=None)
                    if trails is not None:
                        reachable_map[fact_node] = set(trails.keys()) if isinstance(trails, dict) else set(trails)
                
                # Use amino acid: conditional_query to compute perspective differences
                # Query: What does Agent A believe about Fact X given Agent B's knowledge?
                perspective_diffs = []
                for agent1 in agents[:2]:  # Limit computation
                    for agent2 in agents[:2]:
                        if agent1 != agent2:
                            for i, fact in enumerate(list(facts)[:2]):  # Limit facts
                                # Evidence: Agent2 knows the fact
                                evidence = {f"Agent_{agent2}": 1}
                                query = conditional_query(bn_model, [f"Fact_{i}"], evidence)
                                if query is not None and isinstance(query, dict):
                                    # Get probability fact is true given Agent2 knows it
                                    prob_given_agent2 = query.get(1, 0.5)
                                    # Compare with Agent1's belief (from belief_states)
                                    agent1_beliefs = belief_states.get(agent1, set())
                                    agent1_knows = 1.0 if fact in agent1_beliefs else 0.0
                                    diff = abs(prob_given_agent2 - agent1_knows)
                                    perspective_diffs.append(diff)
                
                # Use perspective differences to identify most informative agent
                if perspective_diffs:
                    avg_diff = sum(perspective_diffs) / len(perspective_diffs)
                else:
                    avg_diff = 0.0
            else:
                avg_diff = 0.0
        else:
            avg_diff = 0.0

        # Determine which agent has the most complete/accurate perspective
        # Signal-to-noise ratio: agents with more beliefs (signal) and less uncertainty
        agent_scores = {}
        for agent in agents:
            beliefs = belief_states.get(agent, set())
            signal_strength = len(beliefs) / max(1, len(facts))
            # Uncertainty penalty (agents with contradictory beliefs)
            contradiction_penalty = 0.0
            # Use T1 primitive: modus_ponens to check consistency
            if beliefs:
                premises = [(b, "implies truth") for b in beliefs]  # Simplified
                deduced = modus_ponens(premises, beliefs)
                consistency = len(deduced) / max(1, len(beliefs))
                contradiction_penalty = 1 - consistency
            
            agent_scores[agent] = signal_strength * (1 - contradiction_penalty)

        # Answer is the agent with highest score, or a fact if question asks about knowledge content
        computed_answer = ""
        if "who knows" in question.lower() or "which agent" in question.lower():
            if agent_scores:
                computed_answer = max(agent_scores.items(), key=lambda x: x[1])[0]
            else:
                computed_answer = agents[0] if agents else "Unknown"
        elif "what does" in question.lower() and "know" in question.lower():
            # Extract agent from question
            question_agents = [agent for agent in agents if agent.lower() in question.lower()]
            if question_agents:
                target_agent = question_agents[0]
                agent_beliefs = belief_states.get(target_agent, set())
                computed_answer = list(agent_beliefs)[0] if agent_beliefs else "nothing"
            else:
                computed_answer = "unknown"
        else:
            # Default: agent with most complete knowledge
            computed_answer = max(agent_scores.items(), key=lambda x: x[1])[0] if agent_scores else ""

        return {
            "answer": computed_answer,
            "confidence": min(0.95, confidence * (1 - belief_entropy)),
            "reasoning": f"Knowledge states analyzed using signal propagation model. Perspective differences: {avg_diff:.2f}",
            "agent_scores": agent_scores,
            "belief_entropy": belief_entropy
        }

    def _truth_table(self, n: int) -> List[List[int]]:
        """Generate truth table for n variables."""
        if n <= 0:
            return [[]]
        table = []
        for i in range(2**n):
            bits = [(i >> j) & 1 for j in range(n)]
            table.append(bits)
        return table

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        def ncd(a: str, b: str) -> float:
            if not a or not b:
                return 1.0
            ca = len(zlib.compress(a.encode()))
            cb = len(zlib.compress(b.encode()))
            cab = len(zlib.compress((a + " " + b).encode()))
            return (cab - min(ca, cb)) / max(ca, cb) if max(ca, cb) > 0 else 1.0
        
        results = []
        for candidate in candidates:
            # Primary: exact match or containment of computed answer
            if computed_answer and computed_answer.lower() in candidate.lower():
                base_score = 1.0
            elif computed_answer:
                # Fallback 1: NCD with computed answer
                ncd_score = 1.0 / (1.0 + ncd(computed_answer, candidate))
                # Fallback 2: NCD with reasoning text (broader semantic match)
                ncd_reasoning = 1.0 / (1.0 + ncd(reasoning_text, candidate))
                base_score = max(ncd_score, ncd_reasoning * 0.7)
            else:
                base_score = 0.5
            
            # Adjust based on candidate characteristics
            # Candidates mentioning agents from reasoning get bonus
            agent_bonus = 0.0
            if "agent_scores" in reasoning_result:
                for agent in reasoning_result["agent_scores"]:
                    if agent.lower() in candidate.lower():
                        agent_bonus = 0.1
                        break
            
            final_score = min(1.0, base_score + agent_bonus)
            results.append({
                "candidate": candidate,
                "score": final_score,
                "base_score": base_score,
                "agent_bonus": agent_bonus
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence and entropy measures."""
        if not scored:
            return scored
        
        # Simple calibration: normalize to [0, 1] range
        scores = [item["score"] for item in scored]
        if scores:
            min_score = min(scores)
            max_score = max(scores)
            if max_score > min_score:
                for item in scored:
                    item["score"] = (item["score"] - min_score) / (max_score - min_score)
            else:
                for item in scored:
                    item["score"] = 0.5
        
        return scored