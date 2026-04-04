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
        """Parse prompt to extract agents, facts, observations, and question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        if not lines:
            return {"agents": [], "facts": [], "observations": [], "question": "", "raw": prompt}

        question = lines[-1] if lines else ""
        
        # Extract agent names (capitalized words that appear as subjects)
        agent_pattern = r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b'
        potential_agents = re.findall(agent_pattern, prompt)
        # Filter: agents are typically mentioned multiple times or with actions
        word_counts = {}
        for word in re.findall(r'\b[a-zA-Z]+\b', prompt.lower()):
            word_counts[word] = word_counts.get(word, 0) + 1
        
        agents = []
        for agent in potential_agents:
            # Check if agent appears with actions (knows, sees, believes, tells)
            agent_lower = agent.lower()
            context = prompt.lower()
            if (f"{agent_lower} knows" in context or 
                f"{agent_lower} sees" in context or 
                f"{agent_lower} believes" in context or
                f"{agent_lower} tells" in context):
                agents.append(agent)
        
        # Extract facts (simple propositions)
        fact_pattern = r'that ([^.,]+)'
        facts = []
        for match in re.finditer(fact_pattern, prompt.lower()):
            fact = match.group(1).strip()
            if fact and len(fact.split()) <= 8:  # Reasonable length for a fact
                facts.append(fact)
        
        # Extract observations (agent, fact, true/false)
        observations = []
        for line in lines:
            line_lower = line.lower()
            # Pattern: "Agent sees/knows/believes that..."
            for agent in agents:
                agent_lower = agent.lower()
                if f"{agent_lower} sees" in line_lower or f"{agent_lower} knows" in line_lower:
                    # Find the fact part
                    fact_match = re.search(r'that ([^.,]+)', line_lower)
                    if fact_match:
                        fact = fact_match.group(1).strip()
                        # Determine if observation is positive (sees/knows implies true)
                        observations.append((agent, fact, True))
                elif f"{agent_lower} believes" in line_lower:
                    fact_match = re.search(r'that ([^.,]+)', line_lower)
                    if fact_match:
                        fact = fact_match.group(1).strip()
                        # Belief might be false (false belief scenarios)
                        observations.append((agent, fact, True))  # Default to true
        
        # Extract implications (if-then rules)
        implications = []
        for line in lines:
            if "if" in line.lower() and "then" in line.lower():
                # Simple extraction
                parts = line.lower().split("then")
                if len(parts) == 2:
                    antecedent = parts[0].replace("if", "").strip()
                    consequent = parts[1].strip().rstrip('.')
                    implications.append((antecedent, consequent))
        
        return {
            "agents": list(set(agents)),
            "facts": list(set(facts)),
            "observations": observations,
            "implications": implications,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use information theory and Bayesian networks to compute perspective shifts."""
        agents = structure["agents"]
        observations = structure["observations"]
        implications = structure["implications"]
        question = structure["question"]
        
        if not agents:
            return {"answer": "", "confidence": 0.0, "reasoning": "No agents identified"}
        
        # T1 PRIMITIVE 1: Track beliefs of agents based on observations
        belief_state = track_beliefs(agents, observations)
        if belief_state is None:
            belief_state = {}
        
        # T1 PRIMITIVE 2: Apply modus ponens to derive new beliefs
        known_facts = set()
        for agent, facts in belief_state.items():
            known_facts.update(facts)
        
        derived_facts = modus_ponens(implications, known_facts)
        if derived_facts is None:
            derived_facts = set()
        
        # Information-theoretic reasoning: Compute mutual information between agents' knowledge states
        # Represent each agent's knowledge as a binary vector over facts
        all_facts = list(set(structure["facts"] + list(derived_facts)))
        if not all_facts:
            all_facts = ["dummy_fact"]  # Placeholder
        
        # Build a simple Bayesian network: Agents -> Facts (who knows what)
        edges = []
        for agent in agents:
            for fact in all_facts:
                edges.append((agent, fact))
        
        # Create CPDs: P(Fact = True | Agent knows) = high, else low
        cpd_specs = {}
        for fact in all_facts:
            # Find which agents know this fact
            knowing_agents = []
            for agent in agents:
                agent_facts = belief_state.get(agent, set())
                if fact in agent_facts or fact in derived_facts:
                    knowing_agents.append(agent)
            
            # CPD: If any knowing agent is observed, fact is likely true
            # This models information flow
            cpd_specs[fact] = {
                "variable": fact,
                "variable_card": 2,
                "evidence": agents,
                "evidence_card": [2] * len(agents),
                "values": []
            }
            
            # Generate values: fact is true with probability 0.9 if any agent knows it
            # Information theory: knowledge reduces entropy about the fact
            for i in range(2 ** len(agents)):
                bits = [(i >> j) & 1 for j in range(len(agents))]
                # Check if any agent with bit=1 (knows) is in knowing_agents
                knows = False
                for j, agent in enumerate(agents):
                    if bits[j] == 1 and agent in knowing_agents:
                        knows = True
                        break
                
                if knows:
                    # High probability if someone knows
                    cpd_specs[fact]["values"].append([0.1, 0.9])  # [False, True]
                else:
                    # Low probability otherwise
                    cpd_specs[fact]["values"].append([0.9, 0.1])
        
        # AMINO ACID 1: Build Bayesian network
        bn_model = build_bn(edges, cpd_specs)
        
        # AMINO ACID 2: Query conditional probabilities to find information gaps
        info_gaps = {}
        if bn_model is not None:
            for agent in agents:
                # What does this agent know that others might not?
                agent_knowledge = belief_state.get(agent, set())
                other_agents = [a for a in agents if a != agent]
                
                if other_agents and agent_knowledge:
                    # Sample fact known by this agent
                    sample_fact = list(agent_knowledge)[0] if agent_knowledge else all_facts[0]
                    
                    # Query: P(fact | agent knows, others don't know)
                    evidence = {agent: 1}  # Agent knows
                    for other in other_agents:
                        evidence[other] = 0  # Others don't know
                    
                    query_result = conditional_query(bn_model, [sample_fact], evidence)
                    if query_result is not None:
                        # Information value: how much this agent's knowledge changes belief
                        info_gaps[agent] = query_result.get(sample_fact, {}).get(1, 0.5)
        
        # T1 PRIMITIVE 3: Compute entropy of belief distribution
        belief_probs = []
        for agent in agents:
            agent_facts = belief_state.get(agent, set())
            # Probability agent knows a random fact
            if all_facts:
                p_knows = len(agent_facts) / len(all_facts)
                belief_probs.append(p_knows)
        
        if belief_probs:
            belief_entropy = entropy(belief_probs)
        else:
            belief_entropy = 1.0
        
        # T1 PRIMITIVE 4: Check information sufficiency
        n_unknowns = len(all_facts)
        n_constraints = len(observations) + len(implications)
        info_status = information_sufficiency(n_unknowns, n_constraints)
        
        # Determine answer based on question type
        computed_answer = ""
        reasoning_text = ""
        
        # Parse question to determine what's being asked
        question_lower = question.lower()
        
        if "who knows" in question_lower or "which agent" in question_lower:
            # Find agent with most unique knowledge (highest information gap)
            if info_gaps:
                best_agent = max(info_gaps.items(), key=lambda x: x[1])[0]
                computed_answer = best_agent
                reasoning_text = f"Agent {best_agent} has highest information value"
            else:
                # Fallback: agent with most facts
                if belief_state:
                    best_agent = max(belief_state.items(), key=lambda x: len(x[1]))[0]
                    computed_answer = best_agent
                    reasoning_text = f"Agent {best_agent} knows the most facts"
        
        elif "what does" in question_lower and "believe" in question_lower:
            # Extract agent from question
            for agent in agents:
                if agent.lower() in question_lower:
                    agent_facts = belief_state.get(agent, set())
                    if agent_facts:
                        computed_answer = list(agent_facts)[0]
                        reasoning_text = f"Agent {agent} believes {computed_answer}"
                    break
        
        elif "false belief" in question_lower:
            # Use Sally-Anne test primitive
            # Extract locations and movements from prompt
            location_matches = re.findall(r'\b([A-Z][a-z]+)\b location', prompt.lower())
            if location_matches and len(agents) >= 2:
                original_loc = location_matches[0] if location_matches else "original"
                new_loc = location_matches[1] if len(location_matches) > 1 else "new"
                
                # Determine who moved and who saw
                who_moved = agents[0] if agents else ""
                who_saw = set()
                for obs in observations:
                    if "sees" in obs[1].lower() or "move" in obs[1].lower():
                        who_saw.add(obs[0])
                
                false_belief_result = sally_anne_test(
                    who_moved, who_saw, original_loc, new_loc
                )
                if false_belief_result:
                    # Find agent with false belief
                    for agent, location in false_belief_result.items():
                        if location == original_loc and agent not in who_saw:
                            computed_answer = agent
                            reasoning_text = f"Agent {agent} has false belief"
                            break
        
        # If no specific answer found, use information theory result
        if not computed_answer and info_gaps:
            # Agent with highest information gap
            best_agent = max(info_gaps.items(), key=lambda x: x[1])[0]
            computed_answer = best_agent
            reasoning_text = f"Highest information asymmetry: {best_agent}"
        
        if not computed_answer and agents:
            computed_answer = agents[0]
            reasoning_text = "Default to first agent"
        
        # T1 PRIMITIVE 5: Compute confidence from agreement
        scores = []
        if info_gaps:
            scores = list(info_gaps.values())
        if belief_probs:
            scores.extend(belief_probs)
        
        if scores:
            confidence = confidence_from_agreement(scores)
        else:
            confidence = 0.5
        
        # Adjust confidence based on information sufficiency
        if info_status == "determined":
            confidence = min(1.0, confidence * 1.2)
        elif info_status == "underdetermined":
            confidence = confidence * 0.8
        
        return {
            "answer": computed_answer,
            "confidence": float(confidence),
            "reasoning": reasoning_text,
            "belief_state": belief_state,
            "info_gaps": info_gaps,
            "entropy": belief_entropy
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result.get("answer", "")
        reasoning_text = reasoning_result.get("reasoning", "")
        
        if not computed_answer:
            # Fallback to reasoning text
            target_text = reasoning_text
        else:
            target_text = computed_answer
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Secondary: NCD similarity to reasoning text
                ncd_score = self._ncd(target_text, candidate)
                score = 1.0 / (1.0 + ncd_score)
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence and entropy."""
        if not scored:
            return scored
        
        # Extract raw scores
        raw_scores = [item["raw_score"] for item in scored]
        if not raw_scores:
            return scored
        
        # Normalize to [0, 1] range
        min_score = min(raw_scores)
        max_score = max(raw_scores)
        
        if max_score > min_score:
            for item in scored:
                normalized = (item["raw_score"] - min_score) / (max_score - min_score)
                # Apply slight smoothing
                item["score"] = 0.9 * normalized + 0.1 * item["raw_score"]
        else:
            # All scores equal
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