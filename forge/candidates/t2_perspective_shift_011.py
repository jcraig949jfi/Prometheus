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
from forge.amino_acids.pysat_acids import check_entailment


class ReasoningTool:
    """Electromagnetism x Bayesian Networks - Perspective Shift"""

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

    # ========== PHASE 1: EXTRACT ==========
    def _extract(self, prompt: str) -> Dict[str, Any]:
        """Parse prompt to extract agents, facts, observations, and question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        agents = set()
        facts = set()
        observations = []
        question = lines[-1] if lines else ""

        # Extract agent names (capitalized words that appear as subjects)
        words = re.findall(r'\b([A-Z][a-z]+)\b', prompt)
        potential_agents = [w for w in words if len(w) > 2]
        # Filter: agents are typically mentioned with "knows", "sees", "believes"
        agent_keywords = ['knows', 'sees', 'believes', 'thinks', 'tells', 'asks']
        for i, word in enumerate(potential_agents):
            context = prompt.lower()
            if any(kw in context for kw in agent_keywords):
                agents.add(word)

        # Extract facts (quoted phrases or simple propositions)
        quoted = re.findall(r'"([^"]*)"', prompt)
        facts.update(quoted)
        # Also extract simple factual statements
        fact_patterns = re.findall(r'that ([^.,]+)', prompt.lower())
        for fp in fact_patterns:
            clean = fp.strip()
            if len(clean.split()) <= 8:  # Avoid long clauses
                facts.add(clean.capitalize())

        # Extract observations: (agent, fact, True/False)
        # Look for patterns like "Alice sees Bob leave"
        for line in lines:
            line_lower = line.lower()
            for agent in agents:
                if agent.lower() in line_lower:
                    # Check for perception verbs
                    if 'sees' in line_lower or 'observes' in line_lower:
                        # Extract the object of observation
                        parts = line.split()
                        try:
                            agent_idx = parts.index(agent)
                            # Simple heuristic: fact is rest of sentence after verb
                            verb_idx = next(i for i, w in enumerate(parts) if w in ['sees', 'observes'])
                            fact = ' '.join(parts[verb_idx+1:])
                            if fact:
                                observations.append((agent, fact, True))
                        except (ValueError, StopIteration):
                            pass
                    # Check for knowledge statements
                    elif 'knows' in line_lower or 'believes' in line_lower:
                        # Extract the known fact
                        match = re.search(r'knows that ([^.,]+)', line_lower)
                        if match:
                            fact = match.group(1).capitalize()
                            observations.append((agent, fact, True))

        return {
            "agents": list(agents),
            "facts": list(facts),
            "observations": observations,
            "question": question,
            "raw_prompt": prompt
        }

    # ========== PHASE 2: REASON ==========
    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use electromagnetic field theory as scaffold: agents as charged particles,
        knowledge as electric potential, observations as field interactions."""
        agents = structure["agents"]
        facts = structure["facts"]
        observations = structure["observations"]
        question = structure["question"]

        # T1 PRIMITIVE 1: Track beliefs based on observations
        belief_state = track_beliefs(agents, observations)
        if belief_state is None:
            belief_state = {agent: set() for agent in agents}

        # T1 PRIMITIVE 2: Use Sally-Anne test for perspective shifts
        # Extract object movement info if present
        movement_info = self._extract_movement(structure["raw_prompt"])
        if movement_info:
            who_moved, who_saw, orig_loc, new_loc = movement_info
            perspective_map = sally_anne_test(who_moved, who_saw, orig_loc, new_loc)
        else:
            perspective_map = {}

        # Build Bayesian Network representing knowledge propagation
        # Nodes: agents' knowledge states, edges: communication/observation paths
        bn_edges = []
        for obs in observations:
            agent, fact, _ = obs
            # Connect fact node to agent's knowledge node
            fact_node = f"FACT_{hash(fact) % 1000}"
            agent_node = f"KNOW_{agent}"
            bn_edges.append((fact_node, agent_node))

        # Add communication edges between agents (inferred from prompt)
        comm_edges = self._infer_communication(structure["raw_prompt"], agents)
        bn_edges.extend(comm_edges)

        # AMINO ACID 1: Build Bayesian Network
        bn_model = build_bn(bn_edges)
        
        # AMINO ACID 2: Query conditional probabilities for perspective differences
        conditional_probs = {}
        if bn_model is not None:
            for agent in agents:
                # Query what agent knows given evidence
                evidence = {}
                for obs_agent, fact, value in observations:
                    if obs_agent == agent:
                        fact_node = f"FACT_{hash(fact) % 1000}"
                        evidence[fact_node] = value
                
                if evidence:
                    # Query probability agent knows a specific fact
                    for fact in facts[:3]:  # Limit to first few facts
                        fact_node = f"FACT_{hash(fact) % 1000}"
                        prob = conditional_query(bn_model, [fact_node], evidence)
                        if prob is not None:
                            conditional_probs[(agent, fact)] = prob.get(fact_node, 0.5)

        # AMINO ACID 3: Find active trails to see information flow
        info_paths = {}
        if bn_model is not None:
            for agent1 in agents:
                for agent2 in agents:
                    if agent1 != agent2:
                        trails = active_trails(bn_model, [f"KNOW_{agent1}"], observed=None)
                        if trails is not None:
                            info_paths[(agent1, agent2)] = f"KNOW_{agent2}" in trails

        # T1 PRIMITIVE 3: Compute confidence from agreement among agents
        agreement_scores = []
        for fact in facts[:3]:
            agent_beliefs = []
            for agent in agents:
                knows = fact in belief_state.get(agent, set())
                agent_beliefs.append(1.0 if knows else 0.0)
            if agent_beliefs:
                conf = confidence_from_agreement(agent_beliefs)
                if conf is not None:
                    agreement_scores.append(conf)

        avg_confidence = sum(agreement_scores) / len(agreement_scores) if agreement_scores else 0.5

        # T1 PRIMITIVE 4: Compute entropy of knowledge distribution
        knowledge_vectors = []
        for agent in agents:
            vec = [1 if fact in belief_state.get(agent, set()) else 0 for fact in facts[:5]]
            knowledge_vectors.append(vec)
        
        # Flatten and compute distribution entropy
        if knowledge_vectors:
            flat = [bit for vec in knowledge_vectors for bit in vec]
            if flat:
                prob_1 = sum(flat) / len(flat)
                prob_0 = 1 - prob_1
                if prob_0 > 0 and prob_1 > 0:
                    knowledge_entropy = entropy([prob_0, prob_1])
                else:
                    knowledge_entropy = 0.0
            else:
                knowledge_entropy = 0.0
        else:
            knowledge_entropy = 0.0

        # T1 PRIMITIVE 5: Apply modus ponens to derive implicit knowledge
        premises = []
        # Extract implication rules from prompt
        implication_patterns = re.findall(r'if ([^,]+), then ([^.,]+)', structure["raw_prompt"].lower())
        for antecedent, consequent in implication_patterns:
            premises.append((antecedent.capitalize(), consequent.capitalize()))
        
        derived_facts = set()
        if premises:
            # Start with explicitly known facts
            initial_facts = set()
            for agent, fact, _ in observations:
                initial_facts.add(fact)
            
            derived = modus_ponens(premises, initial_facts)
            if derived is not None:
                derived_facts.update(derived)

        # Determine answer based on electromagnetic analogy:
        # Knowledge potential = confidence * (1 - entropy)
        # Higher potential = more certain, less dispersed knowledge
        agent_potentials = {}
        for agent in agents:
            # Agent's personal confidence
            agent_facts = belief_state.get(agent, set())
            agent_vec = [1 if fact in agent_facts else 0 for fact in facts[:5]]
            if agent_vec:
                agent_agreement = confidence_from_agreement(agent_vec) or 0.5
            else:
                agent_agreement = 0.5
            
            # Information access from active trails
            info_access = sum(1 for a2 in agents if info_paths.get((agent, a2), False))
            info_factor = info_access / max(len(agents) - 1, 1)
            
            # Electromagnetic potential formula: V = Q/(4πεr)
            # Analog: potential = (knowledge_charge) / (dispersion + 1)
            knowledge_charge = len(agent_facts) + len(derived_facts.intersection(agent_facts))
            dispersion = knowledge_entropy + 1e-6
            potential = (agent_agreement * knowledge_charge) / (dispersion * (1 + info_factor))
            
            agent_potentials[agent] = potential

        # Identify which agent's perspective is asked about
        target_agent = None
        for agent in agents:
            if agent.lower() in question.lower():
                target_agent = agent
                break
        
        if not target_agent and agents:
            # Default to agent with highest potential
            target_agent = max(agent_potentials.items(), key=lambda x: x[1])[0]

        # Compute answer: what does target agent know/believe?
        target_knowledge = belief_state.get(target_agent, set())
        if target_knowledge:
            # Select most distinctive fact known by target
            other_knowledge = set()
            for agent in agents:
                if agent != target_agent:
                    other_knowledge.update(belief_state.get(agent, set()))
            
            distinctive = target_knowledge - other_knowledge
            if distinctive:
                computed_answer = next(iter(distinctive))
            else:
                # No distinctive knowledge, use fact with highest conditional probability
                relevant_probs = [(fact, prob) for (a, fact), prob in conditional_probs.items() 
                                 if a == target_agent]
                if relevant_probs:
                    computed_answer = max(relevant_probs, key=lambda x: x[1])[0]
                else:
                    computed_answer = target_agent  # Fallback to agent name
        else:
            computed_answer = target_agent or "Unknown"

        return {
            "answer": str(computed_answer),
            "confidence": min(avg_confidence * (1 - knowledge_entropy), 0.95),
            "reasoning": f"Agent {target_agent} has knowledge potential {agent_potentials.get(target_agent, 0):.3f}. " +
                        f"Knows {len(target_knowledge)} facts. " +
                        f"Information entropy: {knowledge_entropy:.3f}.",
            "agent_potentials": agent_potentials,
            "target_agent": target_agent
        }

    def _extract_movement(self, prompt: str) -> Tuple[str, Set[str], str, str] | None:
        """Extract object movement information for Sally-Anne test."""
        # Look for patterns like "X moves Y from A to B"
        move_pattern = r'([A-Z][a-z]+) moves? ([^ ]+) from ([^ ]+) to ([^ .]+)'
        match = re.search(move_pattern, prompt)
        if match:
            who_moved, obj, orig, new = match.groups()
            # Who saw the move? Look for "sees" references
            who_saw = set()
            sees_pattern = r'([A-Z][a-z]+) sees? [^.]* move'
            for m in re.finditer(sees_pattern, prompt):
                who_saw.add(m.group(1))
            return who_moved, who_saw, orig, new
        return None

    def _infer_communication(self, prompt: str, agents: List[str]) -> List[Tuple[str, str]]:
        """Infer communication edges between agents from prompt text."""
        edges = []
        prompt_lower = prompt.lower()
        
        # Direct communication verbs
        comm_verbs = ['tells', 'says to', 'informs', 'asks', 'communicates with']
        
        for agent1 in agents:
            for agent2 in agents:
                if agent1 != agent2:
                    pattern1 = f'{agent1.lower()} ({ "|".join(comm_verbs) }) {agent2.lower()}'
                    pattern2 = f'{agent2.lower()} ({ "|".join(comm_verbs) }) {agent1.lower()}'
                    
                    if (re.search(pattern1, prompt_lower) or 
                        re.search(pattern2, prompt_lower)):
                        edges.append((f"KNOW_{agent1}", f"KNOW_{agent2}"))
        
        return edges

    # ========== PHASE 3: SCORE ==========
    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback 1: check if target agent appears
                target_agent = reasoning_result.get("target_agent")
                if target_agent and target_agent.lower() in candidate.lower():
                    base_score = 0.7
                else:
                    # Fallback 2: NCD similarity to reasoning text
                    base_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
            # Adjust by confidence
            confidence = reasoning_result.get("confidence", 0.5)
            adjusted_score = base_score * confidence
            
            results.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score,
                "confidence": confidence
            })
        
        return results

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

    # ========== PHASE 4: CALIBRATE ==========
    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        scores = [item["score"] for item in scored]
        if max(scores) - min(scores) < 0.01:
            # All scores too close, differentiate by base_score
            for item in scored:
                item["score"] = item["base_score"]
        
        # Softmax normalization
        exp_scores = [2.71828 ** (s * 3) for s in scores]  # Scaled exponential
        total = sum(exp_scores)
        
        for i, item in enumerate(scored):
            item["score"] = exp_scores[i] / total if total > 0 else 0.0
        
        return scored