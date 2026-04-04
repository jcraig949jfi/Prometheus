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
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, active_trails
from forge.amino_acids.pysat_acids import check_entailment, detect_paradox


class ReasoningTool:
    """Control theory x Bayesian networks - perspective_shift"""

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
        """Extract agents, facts, observations, and the question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        agents = set()
        facts = set()
        observations = []
        question = lines[-1] if lines else ""
        
        # Extract capitalized names as potential agents
        agent_candidates = re.findall(r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b', prompt)
        for name in agent_candidates:
            if len(name.split()) <= 3:  # Avoid long phrases
                agents.add(name)
        
        # Extract facts (simple statements in present tense)
        fact_pattern = r'(\b[A-Z][a-z]+\b (?:is|has|knows|believes|sees) [^.!?]+)'
        for match in re.finditer(fact_pattern, prompt.lower()):
            fact = match.group(1)
            facts.add(fact)
        
        # Extract observations: (agent, fact, True/False)
        # Look for patterns like "Alice sees that X", "Bob knows that Y"
        see_pattern = r'([A-Z][a-z]+) (?:sees|observes|notices) that ([^.!?]+)'
        know_pattern = r'([A-Z][a-z]+) (?:knows|believes) that ([^.!?]+)'
        
        for match in re.finditer(see_pattern, prompt, re.IGNORECASE):
            agent, observation = match.groups()
            observations.append((agent, observation.strip(), True))
        
        for match in re.finditer(know_pattern, prompt, re.IGNORECASE):
            agent, observation = match.groups()
            observations.append((agent, observation.strip(), True))
        
        # Extract negations
        not_pattern = r'([A-Z][a-z]+) (?:does not know|does not believe|does not see) that ([^.!?]+)'
        for match in re.finditer(not_pattern, prompt, re.IGNORECASE):
            agent, observation = match.groups()
            observations.append((agent, observation.strip(), False))
        
        return {
            "agents": list(agents),
            "facts": list(facts),
            "observations": observations,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply control theory framework: agents as dynamical systems with information states."""
        agents = structure["agents"]
        observations = structure["observations"]
        question = structure["question"]
        
        # Control theory concept: Information states as system states
        # Each agent's knowledge is a state vector; observations are inputs that update the state
        
        # T1 Primitive 1: Track beliefs of all agents
        belief_tracking = track_beliefs(agents, observations)
        if belief_tracking is None:
            belief_tracking = {agent: set() for agent in agents}
        
        # Build a Bayesian network to model information flow (control theory: system dynamics)
        # Nodes: agents' knowledge states, facts
        edges = []
        cpd_specs = []
        
        # Create nodes for each agent's knowledge of each fact
        for agent in agents:
            for fact in structure["facts"]:
                fact_node = f"{agent}_knows_{hash(fact) % 1000}"
                # Connect observations to knowledge states
                for obs_agent, obs_fact, obs_value in observations:
                    if obs_agent == agent and obs_fact == fact:
                        # This is a direct observation edge
                        obs_node = f"obs_{hash(str((agent, fact))) % 1000}"
                        edges.append((obs_node, fact_node))
                        # CPD: P(knows_fact = True | obs = True) = 0.95, P(knows_fact = True | obs = False) = 0.05
                        cpd_specs.append({
                            "variable": fact_node,
                            "variable_card": 2,
                            "values": [[0.05, 0.95], [0.95, 0.05]],  # [obs=False, obs=True]
                            "evidence": [obs_node],
                            "evidence_card": [2]
                        })
        
        # Amino Acid 1: Build Bayesian network
        bn_model = build_bn(edges, cpd_specs)
        
        # Control theory: Compute reachable information states (active trails)
        reachable_states = {}
        if bn_model is not None:
            for agent in agents:
                # Amino Acid 2: Find what information is reachable from each agent's observations
                agent_obs_nodes = [f"obs_{hash(str((agent, fact))) % 1000}" 
                                  for fact in structure["facts"]]
                trails = active_trails(bn_model, agent_obs_nodes)
                if trails is not None:
                    reachable_states[agent] = trails
                else:
                    reachable_states[agent] = set()
        
        # T1 Primitive 2: Use Sally-Anne test for false belief reasoning
        # Extract object movement info from question
        movement_info = self._extract_movement(structure["raw"])
        if movement_info:
            who_moved, who_saw, orig_loc, new_loc = movement_info
            false_beliefs = sally_anne_test(who_moved, who_saw, orig_loc, new_loc)
            if false_beliefs is None:
                false_beliefs = {}
        else:
            false_beliefs = {}
        
        # T1 Primitive 3: Apply modus ponens to derive implicit knowledge
        # Extract implication rules from the prompt
        rules = self._extract_rules(structure["raw"])
        derived_beliefs = {}
        for agent in agents:
            agent_facts = belief_tracking.get(agent, set())
            if rules:
                new_facts = modus_ponens(rules, agent_facts)
                if new_facts is not None:
                    derived_beliefs[agent] = new_facts
                else:
                    derived_beliefs[agent] = set()
            else:
                derived_beliefs[agent] = set()
        
        # Amino Acid 3: Check for logical paradoxes in combined knowledge
        # Encode agent beliefs as logical clauses
        clauses = []
        for agent in agents:
            for fact in belief_tracking.get(agent, set()):
                # Encode as positive literal
                clauses.append([hash(fact) % 1000 + 1])
            # Add constraints: if agent knows fact, it's true for them
            # But different agents might have contradictory beliefs
        
        paradox_detected = False
        if clauses:
            paradox_result = detect_paradox(clauses)
            if paradox_result is not None:
                paradox_detected = paradox_result
        
        # Control theory: Determine which agent has most complete/consistent information state
        # Measure information completeness (entropy of belief state)
        agent_scores = {}
        for agent in agents:
            # T1 Primitive 4: Compute entropy of belief state
            beliefs = list(belief_tracking.get(agent, set()))
            # Convert to probability distribution over facts
            if beliefs and structure["facts"]:
                # Simple model: uniform over known facts
                known_count = len(beliefs)
                total_facts = len(structure["facts"])
                if total_facts > 0:
                    p_known = known_count / total_facts
                    p_unknown = 1 - p_known
                    if p_known > 0 and p_unknown > 0:
                        belief_entropy = entropy([p_known, p_unknown])
                    else:
                        belief_entropy = 0.0
                else:
                    belief_entropy = 0.0
            else:
                belief_entropy = 0.0
            
            # Control theory: Lower entropy = more certain/complete information state
            completeness = 1.0 / (1.0 + belief_entropy) if belief_entropy > 0 else 1.0
            
            # Consider derived knowledge
            derived_count = len(derived_beliefs.get(agent, set()))
            total_derivable = len(rules) * 2 if rules else 1
            derivation_score = derived_count / total_derivable if total_derivable > 0 else 0
            
            agent_scores[agent] = {
                "completeness": completeness,
                "derivation": derivation_score,
                "reachable": len(reachable_states.get(agent, set())),
                "has_false_belief": agent in false_beliefs and false_beliefs.get(agent) != new_loc if movement_info else False
            }
        
        # T1 Primitive 5: Compute confidence from agreement among scoring methods
        score_components = []
        for agent in agents:
            scores = [
                agent_scores[agent]["completeness"],
                agent_scores[agent]["derivation"],
                agent_scores[agent]["reachable"] / 100.0 if agent_scores[agent]["reachable"] > 0 else 0
            ]
            score_components.append(sum(scores) / len(scores))
        
        confidence = confidence_from_agreement(score_components)
        if confidence is None:
            confidence = 0.5
        
        # Determine which agent's perspective is asked about
        # Parse question to see if it asks about a specific agent
        target_agent = None
        for agent in agents:
            if agent.lower() in question.lower():
                target_agent = agent
                break
        
        # If no specific agent mentioned, find agent with most complete information
        if not target_agent and agents:
            target_agent = max(agents, key=lambda a: agent_scores[a]["completeness"])
        
        # Control theory output: The agent with optimal information state (minimal uncertainty)
        computed_answer = target_agent if target_agent else "Unknown"
        
        return {
            "answer": computed_answer,
            "confidence": float(confidence),
            "reasoning": f"Agent {computed_answer} has optimal information state with completeness {agent_scores.get(computed_answer, {}).get('completeness', 0):.2f}",
            "agent_scores": agent_scores,
            "paradox_detected": paradox_detected
        }

    def _extract_movement(self, text: str) -> Tuple[str, Set[str], str, str] | None:
        """Extract object movement information for false belief scenarios."""
        move_pattern = r'([A-Z][a-z]+) moves? (?:the|an?) ([^.!?]+) from ([^.!?]+) to ([^.!?]+)'
        match = re.search(move_pattern, text, re.IGNORECASE)
        if match:
            who_moved, obj, orig, new = match.groups()
            # Extract who saw the move
            see_pattern = rf'([A-Z][a-z]+) (?:sees|watches|observes) {who_moved} move'
            see_matches = re.findall(see_pattern, text, re.IGNORECASE)
            who_saw = set(see_matches)
            return who_moved.strip(), who_saw, orig.strip(), new.strip()
        return None

    def _extract_rules(self, text: str) -> List[Tuple[str, str]]:
        """Extract implication rules from text."""
        rules = []
        # Pattern: "If X then Y"
        if_then_pattern = r'if ([^.!?]+) then ([^.!?]+)'
        for match in re.finditer(if_then_pattern, text, re.IGNORECASE):
            antecedent, consequent = match.groups()
            rules.append((antecedent.strip(), consequent.strip()))
        
        # Pattern: "X implies Y"
        implies_pattern = r'([^.!?]+) implies ([^.!?]+)'
        for match in re.finditer(implies_pattern, text, re.IGNORECASE):
            antecedent, consequent = match.groups()
            rules.append((antecedent.strip(), consequent.strip()))
        
        return rules

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
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary: Check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
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
        if not scores:
            return scored
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score - min_score > 0:
            # Normalize to [0, 1] range
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        else:
            # All scores equal
            for item in scored:
                item["score"] = 0.5
        
        return scored