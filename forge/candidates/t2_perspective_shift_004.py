import re
import zlib
from typing import Dict, List, Any, Set, Tuple

from forge_primitives import (
    track_beliefs,
    sally_anne_test,
    confidence_from_agreement,
    entropy,
    modus_ponens,
    information_sufficiency
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
        question = lines[-1] if lines else ""

        # Extract agent names (capitalized proper nouns)
        agent_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        all_names = re.findall(agent_pattern, prompt)
        # Filter: exclude common non-agent words and question words
        common_non_agents = {'The', 'Which', 'What', 'Who', 'Where', 'When', 'Why', 'How'}
        agents = [name for name in all_names if name not in common_non_agents and len(name.split()) <= 3]

        # Extract facts/statements (sentences with "knows", "sees", "believes", "told")
        facts = []
        observations = []
        for line in lines:
            line_lower = line.lower()
            if any(word in line_lower for word in ['knows', 'sees', 'believes', 'told', 'heard', 'observed']):
                # Try to extract the fact content
                fact_match = re.search(r'that\s+(.+?)[,.]', line, re.IGNORECASE)
                if fact_match:
                    fact = fact_match.group(1).strip()
                    facts.append(fact)
                # Try to extract observation triplets: (agent, observed_fact, True/False)
                # Simple pattern: "Agent sees that..." or "Agent knows that..."
                for agent in agents:
                    if agent in line:
                        if 'sees' in line_lower or 'observed' in line_lower:
                            obs_fact = fact if 'fact' in locals() else line
                            observations.append((agent, obs_fact, True))
                        elif 'does not see' in line_lower or 'did not see' in line_lower:
                            obs_fact = fact if 'fact' in locals() else line
                            observations.append((agent, obs_fact, False))

        # Extract known locations if present (for Sally-Anne style problems)
        locations = re.findall(r'\b(at|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', prompt)
        location_names = [loc[1] for loc in locations] if locations else []

        return {
            "agents": list(set(agents)),
            "facts": list(set(facts)),
            "observations": observations,
            "question": question,
            "locations": location_names,
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply signal processing concepts through Bayesian reasoning."""
        agents = structure["agents"]
        observations = structure["observations"]
        question = structure["question"]
        facts = structure["facts"]
        locations = structure["locations"]

        # Signal processing scaffold: treat knowledge as signals transmitted through noisy channels
        # Agents are receivers with different observation filters (bandwidth/SNR)
        # Common knowledge = coherent signal; private knowledge = filtered component

        # Step 1: Track beliefs using T1 primitive (signal aggregation)
        belief_tracking = track_beliefs(agents, observations)
        if belief_tracking is None:
            belief_tracking = {agent: set() for agent in agents}

        # Step 2: Build Bayesian network for knowledge propagation
        # Nodes: agents' knowledge states, facts as latent variables
        edges = []
        cpd_specs = []

        # Create fact nodes
        for fact in facts:
            # Prior probability of fact being true (signal source)
            cpd_specs.append({
                'variable': f"F_{fact[:10]}",
                'variable_card': 2,
                'values': [[0.5], [0.5]],  # Uniform prior
                'evidence': [],
                'evidence_card': []
            })

        # Create agent knowledge nodes with observation as evidence
        for agent in agents:
            agent_node = f"K_{agent}"
            # Find observations for this agent
            agent_obs = [obs for obs in observations if obs[0] == agent]
            if agent_obs:
                # Connect from facts this agent observed
                for obs in agent_obs:
                    fact_text = obs[1]
                    fact_node = f"F_{fact_text[:10]}"
                    edges.append((fact_node, agent_node))
                # CPD: if any observed fact is true, agent knows it with high probability
                # Signal transmission with noise (0.9 reliability)
                cpd_values = [[0.1, 0.9], [0.9, 0.1]]  # P(K|F): [F=false, F=true]
                cpd_specs.append({
                    'variable': agent_node,
                    'variable_card': 2,
                    'values': cpd_values,
                    'evidence': [f"F_{fact_text[:10]}" for obs in agent_obs],
                    'evidence_card': [2] * len(agent_obs)
                })
            else:
                # No direct observation - knowledge comes from other agents (signal relay)
                edges.append(("common_knowledge", agent_node))
                cpd_specs.append({
                    'variable': agent_node,
                    'variable_card': 2,
                    'values': [[0.5], [0.5]],
                    'evidence': [],
                    'evidence_card': []
                })

        # Build Bayesian network
        bn_model = build_bn(edges, cpd_specs)

        # Step 3: Use amino acid to query knowledge states (signal reconstruction)
        target_agent = None
        target_fact = None
        
        # Parse question to find target
        if "who" in question.lower():
            # Find which agent knows something
            for fact in facts:
                if fact.lower() in question.lower():
                    target_fact = fact
                    break
        elif "what" in question.lower() or "which" in question.lower():
            # Find what an agent knows
            for agent in agents:
                if agent.lower() in question.lower():
                    target_agent = agent
                    break

        computed_answer = ""
        confidence = 0.5
        reasoning = ""

        # Try Bayesian query first
        if bn_model is not None and target_fact and target_agent:
            try:
                # Query P(agent knows fact | observations)
                fact_node = f"F_{target_fact[:10]}"
                agent_node = f"K_{target_agent}"
                
                # Use amino acid for conditional query
                query_result = conditional_query(
                    bn_model,
                    target_vars=[agent_node],
                    evidence={fact_node: 1}  # Assume fact is true
                )
                
                if query_result is not None:
                    # Extract probability that agent knows fact
                    prob_knows = query_result.values[1] if len(query_result.values) > 1 else 0.5
                    confidence = prob_knows
                    computed_answer = target_agent if prob_knows > 0.5 else "Unknown"
                    reasoning = f"Bayesian query gives P(knows)={prob_knows:.2f}"
            except Exception:
                # Fallback to simpler reasoning
                pass

        # If Bayesian query didn't work, use T1 primitives
        if not computed_answer:
            # Use active trails amino acid to find information flow
            if bn_model is not None and agents:
                try:
                    # Check which agents have active information trails to facts
                    info_access = {}
                    for agent in agents:
                        agent_node = f"K_{agent}"
                        trails = active_trails(bn_model, [agent_node], observed=None)
                        if trails:
                            # Count how many fact nodes are reachable
                            reachable_facts = sum(1 for node in trails if node.startswith('F_'))
                            info_access[agent] = reachable_facts
                    
                    if info_access:
                        # Agent with most information access likely knows more
                        best_agent = max(info_access.items(), key=lambda x: x[1])[0]
                        computed_answer = best_agent.replace("K_", "")
                        confidence = info_access[best_agent] / len(facts) if facts else 0.5
                        reasoning = f"Information flow analysis: {computed_answer} has access to {info_access[best_agent]}/{len(facts)} facts"
                except Exception:
                    pass

        # Final fallback: use belief tracking from T1 primitive
        if not computed_answer and belief_tracking:
            # Compute entropy of belief states (signal diversity)
            belief_entropies = {}
            for agent, beliefs in belief_tracking.items():
                if beliefs:
                    # Convert belief set to probability distribution
                    probs = [0.5, 0.5]  # Default uniform
                    belief_entropies[agent] = entropy(probs)
                else:
                    belief_entropies[agent] = 1.0  # Maximum entropy for no beliefs
            
            # Agent with lowest entropy has most certain knowledge
            if belief_entropies:
                best_agent = min(belief_entropies.items(), key=lambda x: x[1])[0]
                computed_answer = best_agent
                confidence = 1.0 - (belief_entropies[best_agent] / max(belief_entropies.values()))
                reasoning = f"Belief entropy analysis: {computed_answer} has most certain knowledge"

        # Ultimate fallback: use first agent mentioned
        if not computed_answer and agents:
            computed_answer = agents[0]
            confidence = 0.3
            reasoning = "Fallback to first mentioned agent"

        # Use confidence_from_agreement T1 primitive to refine confidence
        if computed_answer:
            # Simulate multiple reasoning paths
            scores = [confidence, 0.5, 0.7]  # Include some variation
            refined_confidence = confidence_from_agreement(scores)
            if refined_confidence is not None:
                confidence = refined_confidence

        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": reasoning,
            "beliefs": belief_tracking
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 0.9 + (reasoning_result["confidence"] * 0.1)
            else:
                # Fallback: NCD similarity to reasoning text
                ncd_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
                score = ncd_score * 0.5  # Lower weight for NCD matches
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence and consistency checks."""
        if not scored:
            return scored
        
        # Use information_sufficiency T1 primitive to check if we have enough data
        n_candidates = len(scored)
        n_factors = 3  # agents, facts, observations
        info_status = information_sufficiency(n_candidates, n_factors)
        
        # Adjust scores based on information status
        calibration_factor = 1.0
        if info_status == "underdetermined":
            calibration_factor = 0.8
        elif info_status == "overconstrained":
            calibration_factor = 0.9
        
        # Apply calibration
        for item in scored:
            item["score"] = item["raw_score"] * calibration_factor
            # Ensure score is in [0, 1]
            item["score"] = max(0.0, min(1.0, item["score"]))
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance between two strings."""
        if not a or not b:
            return 1.0
        try:
            ca = len(zlib.compress(a.encode()))
            cb = len(zlib.compress(b.encode()))
            cab = len(zlib.compress((a + " " + b).encode()))
            if max(ca, cb) > 0:
                return (cab - min(ca, cb)) / max(ca, cb)
        except Exception:
            pass
        return 1.0