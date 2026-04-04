import re
import zlib
from typing import Dict, List, Any, Set, Tuple
from forge_primitives import track_beliefs, sally_anne_test, confidence_from_agreement, entropy, modus_ponens
from forge.amino_acids.pysat_acids import check_entailment, detect_paradox

class ReasoningTool:
    """evolutionary_biology x pysat_acids - perspective_shift"""

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

        # Extract agent names (capitalized words that appear as subjects)
        # Simple heuristic: words that appear before "knows", "sees", "believes", "thinks"
        agent_keywords = ["knows", "sees", "believes", "thinks", "hears", "tells"]
        for line in lines:
            words = line.split()
            for i, word in enumerate(words):
                if word.lower() in agent_keywords and i > 0:
                    # Previous word(s) likely the agent
                    agent_candidate = words[i-1]
                    if agent_candidate[0].isupper():
                        agents.add(agent_candidate)
                # Also look for "Alice and Bob" patterns
                if " and " in line.lower():
                    parts = line.split(" and ")
                    for part in parts:
                        name = part.strip().split()[0] if part.strip() else ""
                        if name and name[0].isupper():
                            agents.add(name)

        # Extract facts (simple propositions in quotes or following "that")
        fact_pattern = r'\"([^\"]+)\"|that ([^.,]+)'
        for line in lines:
            matches = re.findall(fact_pattern, line)
            for match in matches:
                fact = match[0] if match[0] else match[1]
                if fact and len(fact.split()) <= 8:  # Avoid overly long fragments
                    facts.add(fact.strip())

        # Extract observations: (agent, fact, True/False for belief)
        # Look for patterns like "Alice sees Bob leave" -> (Alice, "Bob leave", True)
        belief_verbs = ["knows", "believes", "thinks"]
        perception_verbs = ["sees", "hears", "observes"]
        for line in lines:
            for verb in belief_verbs + perception_verbs:
                if f" {verb} " in line.lower():
                    parts = line.lower().split(f" {verb} ")
                    if len(parts) >= 2:
                        agent_part = parts[0]
                        fact_part = parts[1]
                        # Extract agent name
                        agent_words = agent_part.split()
                        if agent_words:
                            agent = agent_words[-1]
                            if agent[0].isupper():
                                # Extract fact from fact_part
                                fact = fact_part.split(',')[0].split(';')[0].strip()
                                if fact:
                                    observations.append((agent, fact, True))

        # Clean up agents and facts
        agents = {a for a in agents if len(a) > 1}
        facts = {f for f in facts if len(f) > 2}

        return {
            "agents": list(agents),
            "facts": list(facts),
            "observations": observations,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply evolutionary biology framework: agents as species, beliefs as traits,
        knowledge propagation as horizontal gene transfer, logical consistency as fitness."""
        agents = structure["agents"]
        facts = structure["facts"]
        observations = structure["observations"]
        question = structure["question"]

        # Use T1 primitive: track_beliefs to establish initial belief state
        belief_state = track_beliefs(agents, observations)
        if not belief_state:
            belief_state = {agent: set() for agent in agents}

        # Evolutionary biology concept: Horizontal Gene Transfer (HGT)
        # Agents share beliefs through communication, like bacteria sharing plasmids
        # Simulate HGT rounds: beliefs spread to agents who don't contradict them
        hgt_rounds = 2
        for _ in range(hgt_rounds):
            new_beliefs = belief_state.copy()
            for agent in agents:
                for other_agent in agents:
                    if agent == other_agent:
                        continue
                    # Transfer beliefs that are logically compatible
                    for belief in belief_state[other_agent]:
                        # Check if belief contradicts agent's existing beliefs
                        # Use amino acid: detect_paradox to check consistency
                        clauses = []
                        # Encode existing beliefs as positive literals
                        for b in list(belief_state[agent]) + [belief]:
                            # Simple encoding: each fact gets a variable index
                            fact_id = abs(hash(b)) % 1000 + 1
                            clauses.append([fact_id])
                        # Check for paradox
                        paradox_info = detect_paradox(clauses)
                        if not paradox_info or not paradox_info.get("is_paradox", True):
                            # No paradox -> belief can be transferred
                            new_beliefs[agent].add(belief)
            belief_state = new_beliefs

        # Evolutionary biology concept: Fitness = Logical Consistency
        # Agents with more consistent belief sets have higher fitness
        agent_fitness = {}
        for agent in agents:
            beliefs = list(belief_state[agent])
            if not beliefs:
                agent_fitness[agent] = 0.0
                continue
            
            # Encode beliefs as CNF clauses
            clauses = []
            for belief in beliefs:
                fact_id = abs(hash(belief)) % 1000 + 1
                clauses.append([fact_id])
            
            # Use amino acid: check_entailment to test if beliefs entail key facts
            # Fitness increases with number of non-paradoxical entailments
            fitness = 0.0
            for fact in facts:
                fact_id = abs(hash(fact)) % 1000 + 1
                entailment_result = check_entailment(clauses, [fact_id])
                if entailment_result and entailment_result.get("entails", False):
                    fitness += 1.0
            
            # Normalize fitness
            agent_fitness[agent] = fitness / max(len(facts), 1)

        # Use T1 primitive: sally_anne_test for perspective comparison
        # Extract potential object movement from observations
        moved_objects = []
        for obs in observations:
            if "move" in obs[1].lower() or "take" in obs[1].lower():
                moved_objects.append(obs)
        
        perspective_differences = {}
        if len(moved_objects) >= 1:
            # Use first movement observation
            agent_who_moved = moved_objects[0][0]
            # Find who saw the move
            who_saw = set()
            for obs in observations:
                if "see" in obs[1].lower() and agent_who_moved in obs[1]:
                    who_saw.add(obs[0])
            
            # Simple location extraction
            locations = ["box", "drawer", "room", "table", "desk"]
            original_loc = "box"
            new_loc = "drawer"
            for loc in locations:
                if loc in structure["raw"].lower():
                    original_loc = loc
                    break
            
            # Use sally_anne_test
            perspective_result = sally_anne_test(
                agent_who_moved, 
                who_saw, 
                original_loc, 
                new_loc
            )
            if perspective_result:
                for agent, loc in perspective_result.items():
                    if agent in agents:
                        perspective_differences[agent] = loc

        # Use T1 primitive: confidence_from_agreement
        # Agents' confidence based on agreement with others (evolutionary pressure)
        fitness_values = list(agent_fitness.values())
        confidence = confidence_from_agreement(fitness_values)
        if confidence is None:
            confidence = 0.5

        # Use T1 primitive: entropy to measure belief diversity
        # High entropy = many different beliefs across population
        belief_counts = {}
        for agent in agents:
            for belief in belief_state[agent]:
                belief_counts[belief] = belief_counts.get(belief, 0) + 1
        
        if belief_counts:
            probs = [count / len(agents) for count in belief_counts.values()]
            belief_entropy = entropy(probs)
        else:
            belief_entropy = 0.0

        # Determine which agent knows most based on evolutionary fitness
        if agent_fitness:
            best_agent = max(agent_fitness.items(), key=lambda x: x[1])[0]
            computed_answer = best_agent
        else:
            # Fallback: agent mentioned most in question
            question_words = question.split()
            for agent in agents:
                if agent in question_words:
                    computed_answer = agent
                    break
            else:
                computed_answer = agents[0] if agents else "Unknown"

        return {
            "answer": computed_answer,
            "confidence": min(confidence + (1 - belief_entropy) * 0.3, 1.0),
            "reasoning": f"Evolutionary fitness analysis: {computed_answer} has highest logical consistency fitness ({agent_fitness.get(computed_answer, 0):.2f}). Belief entropy: {belief_entropy:.2f}. Perspective differences: {perspective_differences}",
            "agent_fitness": agent_fitness,
            "belief_state": {k: list(v) for k, v in belief_state.items()}
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        def ncd(a: str, b: str) -> float:
            ca = len(zlib.compress(a.encode()))
            cb = len(zlib.compress(b.encode()))
            cab = len(zlib.compress((a + " " + b).encode()))
            if max(ca, cb) == 0:
                return 1.0
            return (cab - min(ca, cb)) / max(ca, cb)
        
        scored = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                similarity = 1.0 / (1.0 + ncd(computed_answer, candidate))
                base_score = similarity
            
            scored.append({
                "candidate": candidate,
                "score": base_score,
                "computed_answer": computed_answer
            })
        
        return scored

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence and consistency checks."""
        if not scored:
            return scored
        
        # Use T1 primitive: modus_ponens to check if scoring is logically consistent
        # Build simple rules: if answer contains computed_answer -> high score
        premises = []
        for item in scored:
            candidate = item["candidate"]
            computed = item["computed_answer"]
            # Rule: If candidate contains computed answer, then score should be high
            if computed.lower() in candidate.lower():
                premises.append(("contains", "high_score"))
        
        facts = {"contains"}
        deduced = modus_ponens(premises, facts)
        
        # Adjust scores based on logical consistency
        if "high_score" in deduced:
            # Boost scores that follow the rule
            for item in scored:
                candidate = item["candidate"]
                computed = item["computed_answer"]
                if computed.lower() in candidate.lower():
                    item["score"] = min(item["score"] * 1.2, 1.0)
        
        # Normalize scores to [0, 1] range
        max_score = max(item["score"] for item in scored) if scored else 1.0
        if max_score > 0:
            for item in scored:
                item["score"] = item["score"] / max_score
        
        return scored