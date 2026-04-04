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
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, active_trails


class ReasoningTool:
    """Climate modeling x Bayesian networks - Perspective shift"""

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
        
        # Find agent names (capitalized words that appear as subjects)
        agent_pattern = r'\b([A-Z][a-z]+)\b(?= (?:knows|sees|observes|believes|thinks|says))'
        agents = list(set(re.findall(agent_pattern, prompt)))
        
        # Extract facts/statements (quoted or following "that")
        fact_pattern = r'"(.*?)"|that ([^.,]+)'
        raw_facts = []
        for match in re.finditer(fact_pattern, prompt):
            if match.group(1):
                raw_facts.append(match.group(1))
            elif match.group(2):
                raw_facts.append(match.group(2).strip())
        
        # Extract observations: who observed what
        observations = []
        obs_pattern = r'([A-Z][a-z]+) (?:sees|observes|knows) (?:that )?"?([^".]+)'
        for match in re.finditer(obs_pattern, prompt, re.IGNORECASE):
            agent = match.group(1)
            observation = match.group(2).strip().rstrip('"')
            if agent in agents:
                observations.append((agent, observation, True))
        
        # Extract implications (if-then statements)
        implications = []
        imp_pattern = r'If ([^,]+), then ([^.,]+)'
        for match in re.finditer(imp_pattern, prompt, re.IGNORECASE):
            premise = match.group(1).strip()
            conclusion = match.group(2).strip()
            implications.append((premise, conclusion))
        
        return {
            "agents": agents,
            "raw_facts": raw_facts,
            "observations": observations,
            "implications": implications,
            "question": question,
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use climate modeling concepts to model knowledge diffusion."""
        agents = structure["agents"]
        observations = structure["observations"]
        implications = structure["implications"]
        question = structure["question"]
        
        if not agents:
            return {"answer": "", "confidence": 0.0, "reasoning": "No agents found"}
        
        # === CLIMATE MODELING SCAFFOLD ===
        # Model knowledge as heat in a climate system
        # Agents are grid cells, observations are heat sources
        # Knowledge diffuses through implication pathways
        # Uncertainty is modeled as entropy in the system
        
        # Phase 1: Track initial beliefs (like initial temperature field)
        # Use T1 primitive: track_beliefs
        belief_state = track_beliefs(agents, observations)
        if belief_state is None:
            belief_state = {agent: set() for agent in agents}
            for agent, obs, _ in observations:
                if agent in belief_state:
                    belief_state[agent].add(obs)
        
        # Phase 2: Apply logical propagation (like heat diffusion)
        # Use T1 primitive: modus_ponens
        all_facts = set()
        for agent_beliefs in belief_state.values():
            all_facts.update(agent_beliefs)
        
        if implications:
            # Create premises for modus_ponens
            premises = []
            for prem, conc in implications:
                premises.append((prem, conc))
            
            # Apply modus_ponens to each agent's beliefs
            for agent in agents:
                agent_facts = belief_state[agent]
                new_facts = modus_ponens(premises, agent_facts)
                if new_facts:
                    belief_state[agent].update(new_facts)
        
        # Phase 3: Build Bayesian network for knowledge uncertainty
        # Model agents as nodes, edges represent communication/observation
        # Use amino acid: build_bn
        edges = []
        for agent1 in agents:
            for agent2 in agents:
                if agent1 != agent2:
                    # Add edges based on shared observations
                    obs1 = {obs for a, obs, _ in observations if a == agent1}
                    obs2 = {obs for a, obs, _ in observations if a == agent2}
                    if obs1.intersection(obs2):
                        edges.append((agent1, agent2))
        
        bn_model = None
        if edges:
            bn_model = build_bn(edges, cpd_specs=None)
        
        # Phase 4: Analyze knowledge accessibility (like atmospheric circulation)
        # Use amino acid: active_trails to see what knowledge can reach whom
        knowledge_access = {}
        if bn_model and agents:
            for agent in agents:
                trails = active_trails(bn_model, [agent], observed=None)
                if trails:
                    # Convert to set of accessible agents
                    accessible = set(trails.keys()) if isinstance(trails, dict) else set(trails)
                    knowledge_access[agent] = accessible
        
        # Phase 5: Compute perspective differences (like temperature gradients)
        # Use T1 primitive: entropy to measure uncertainty in belief distribution
        belief_entropies = {}
        for agent in agents:
            beliefs = belief_state.get(agent, set())
            if beliefs:
                # Convert to probability distribution over possible facts
                all_unique_facts = list(set().union(*belief_state.values()))
                if all_unique_facts:
                    # Simple distribution: agent knows fact or not
                    probs = []
                    for fact in all_unique_facts:
                        known = 1.0 if fact in beliefs else 0.0
                        probs.append(known)
                    # Normalize
                    total = sum(probs)
                    if total > 0:
                        probs = [p/total for p in probs]
                        agent_entropy = entropy(probs)
                        belief_entropies[agent] = agent_entropy
        
        # Phase 6: Determine answer based on question
        computed_answer = ""
        reasoning_desc = ""
        
        # Parse question to determine what's being asked
        if "who knows" in question.lower() or "which agent" in question.lower():
            # Find agent with most/least knowledge
            if belief_entropies:
                # Lower entropy = more certain knowledge
                least_uncertain = min(belief_entropies.items(), key=lambda x: x[1])
                computed_answer = least_uncertain[0]
                reasoning_desc = f"Agent with lowest knowledge entropy ({least_uncertain[1]:.3f})"
            else:
                # Fallback: agent with most beliefs
                most_beliefs = max(belief_state.items(), key=lambda x: len(x[1]))
                computed_answer = most_beliefs[0]
                reasoning_desc = f"Agent with most beliefs ({len(most_beliefs[1])})"
        
        elif "what does" in question.lower() and "think" in question.lower():
            # Extract agent from question
            agent_match = re.search(r'what does ([A-Z][a-z]+) think', question.lower())
            if agent_match:
                target_agent = agent_match.group(1).capitalize()
                if target_agent in belief_state:
                    # Use Sally-Anne test for false belief if applicable
                    # Find if there's a location change mentioned
                    location_pattern = r'([A-Z][a-z]+) moves? (?:the )?([^ ]+) from ([^ ]+) to ([^ ]+)'
                    location_match = re.search(location_pattern, structure["raw_prompt"])
                    if location_match:
                        who_moved = location_match.group(1)
                        object_name = location_match.group(2)
                        old_loc = location_match.group(3)
                        new_loc = location_match.group(4)
                        
                        # Determine who saw the move
                        saw_move = set()
                        for agent, obs, _ in observations:
                            if "move" in obs.lower() or object_name in obs:
                                saw_move.add(agent)
                        
                        # Use T1 primitive: sally_anne_test
                        belief_locations = sally_anne_test(
                            who_moved, saw_move, old_loc, new_loc
                        )
                        if belief_locations and target_agent in belief_locations:
                            computed_answer = belief_locations[target_agent]
                            reasoning_desc = f"False belief test result"
                    
                    if not computed_answer:
                        # Return a key belief
                        beliefs = belief_state[target_agent]
                        if beliefs:
                            computed_answer = next(iter(beliefs))
                            reasoning_desc = f"Key belief of {target_agent}"
        
        # Fallback: if no specific pattern matched, use first agent
        if not computed_answer and agents:
            computed_answer = agents[0]
            reasoning_desc = "First agent (fallback)"
        
        # Phase 7: Compute confidence using agreement among reasoning methods
        # Use T1 primitive: confidence_from_agreement
        confidence_sources = []
        
        # Confidence from belief entropy analysis
        if belief_entropies and computed_answer in belief_entropies:
            # Lower entropy = higher confidence
            max_entropy = max(belief_entropies.values()) if belief_entropies else 1.0
            if max_entropy > 0:
                conf1 = 1.0 - (belief_entropies[computed_answer] / max_entropy)
                confidence_sources.append(conf1)
        
        # Confidence from knowledge access analysis
        if knowledge_access and computed_answer in knowledge_access:
            # Agent with access to most other agents is more reliable
            max_access = max(len(acc) for acc in knowledge_access.values()) if knowledge_access else 1
            if max_access > 0:
                conf2 = len(knowledge_access[computed_answer]) / max_access
                confidence_sources.append(conf2)
        
        # Confidence from number of beliefs
        if belief_state and computed_answer in belief_state:
            max_beliefs = max(len(b) for b in belief_state.values()) if belief_state else 1
            if max_beliefs > 0:
                conf3 = len(belief_state[computed_answer]) / max_beliefs
                confidence_sources.append(conf3)
        
        # Compute final confidence
        if confidence_sources:
            confidence = confidence_from_agreement(confidence_sources)
            if confidence is None:
                confidence = sum(confidence_sources) / len(confidence_sources)
        else:
            confidence = 0.5
        
        return {
            "answer": computed_answer,
            "confidence": float(confidence),
            "reasoning": reasoning_desc,
            "belief_state": belief_state,
            "knowledge_access": knowledge_access
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                score = 1.0 / (1.0 + self._ncd(computed_answer + " " + reasoning_text, candidate))
            
            results.append({
                "candidate": candidate,
                "raw_score": score,
                "reasoning_match": computed_answer.lower() in candidate.lower() if computed_answer else False
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using climate modeling uncertainty concepts."""
        if not scored:
            return []
        
        # Extract raw scores
        raw_scores = [item["raw_score"] for item in scored]
        
        # Apply uncertainty calibration (like climate model ensemble adjustment)
        # Higher variance in scores = lower confidence = compress toward mean
        if len(raw_scores) > 1:
            mean_score = sum(raw_scores) / len(raw_scores)
            variance = sum((s - mean_score) ** 2 for s in raw_scores) / len(raw_scores)
            
            # Climate-inspired: uncertainty grows with variance
            # Calibrate by pulling toward mean based on variance
            calibrated = []
            for item in scored:
                raw = item["raw_score"]
                if variance > 0.1:  # High uncertainty
                    # Blend with mean (like ensemble averaging)
                    calibrated_score = 0.7 * raw + 0.3 * mean_score
                else:
                    calibrated_score = raw
                
                calibrated.append({
                    "candidate": item["candidate"],
                    "score": calibrated_score,
                    "raw_score": item["raw_score"],
                    "reasoning_match": item.get("reasoning_match", False)
                })
            
            return calibrated
        
        return [{"candidate": item["candidate"], "score": item["raw_score"]} for item in scored]

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance."""
        if not a or not b:
            return 1.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)