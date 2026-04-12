import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    track_beliefs,
    topological_sort,
    check_transitivity,
    bayesian_update,
    entropy,
    confidence_from_agreement
)
from forge.amino_acids.pysat_acids import check_entailment, detect_paradox


class ReasoningTool:
    """Topology x SAT entailment - perspective_shift"""

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
        
        agents = []
        facts = set()
        observations = []
        question = ""
        
        # Extract agents (capitalized names that appear as subjects)
        agent_pattern = r'\b([A-Z][a-z]+)\b'
        potential_agents = re.findall(agent_pattern, prompt)
        
        # Filter to likely agents (appear multiple times or in specific contexts)
        word_counts = {}
        for word in re.findall(r'\b[a-zA-Z]+\b', prompt.lower()):
            word_counts[word] = word_counts.get(word, 0) + 1
        
        for agent in potential_agents:
            if agent.lower() in ['i', 'you', 'he', 'she', 'it', 'they', 'we']:
                continue
            if word_counts.get(agent.lower(), 0) >= 2:
                agents.append(agent)
        
        # Extract observations: "Agent sees/knows/believes that..."
        observation_pattern = r'([A-Z][a-z]+)\s+(sees|knows|believes|thinks|observes|notices)\s+(that\s+)?([^\.]+)'
        for match in re.finditer(observation_pattern, prompt, re.IGNORECASE):
            agent, verb, _, content = match.groups()
            if agent not in agents:
                agents.append(agent)
            
            # Parse the content to extract facts
            fact_match = re.search(r'(\w+)\s+(is|are|has|have|was|were)\s+(\w+)', content)
            if fact_match:
                fact = f"{fact_match.group(1)} {fact_match.group(2)} {fact_match.group(3)}"
                facts.add(fact)
                observations.append((agent, fact, True))
        
        # Extract direct statements as facts
        statement_pattern = r'([A-Z][a-z]+)\s+(is|are|has|have|was|were)\s+([^\.]+)'
        for match in re.finditer(statement_pattern, prompt):
            subject, verb, predicate = match.groups()
            fact = f"{subject} {verb} {predicate.split(',')[0].split(' and')[0]}"
            facts.add(fact)
        
        # Last sentence is usually the question
        if lines:
            question = lines[-1]
        
        return {
            "agents": list(set(agents)),
            "facts": list(facts),
            "observations": observations,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use topological reasoning about knowledge spaces to determine perspective differences."""
        agents = structure["agents"]
        observations = structure["observations"]
        question = structure["question"]
        
        if not agents or not observations:
            # Fallback: use simple belief tracking
            computed_answer = "Unknown"
            confidence = 0.5
            reasoning = "Insufficient data"
            return {"answer": computed_answer, "confidence": confidence, "reasoning": reasoning}
        
        # 1. Use track_beliefs primitive to get initial belief sets
        belief_sets = track_beliefs(agents, observations)
        
        # 2. Build knowledge dependency graph: agent A knows what agent B knows
        edges = []
        for agent1 in agents:
            for agent2 in agents:
                if agent1 != agent2:
                    # Check if agent1 observes agent2's knowledge
                    for obs_agent, fact, _ in observations:
                        if obs_agent == agent1 and any(agent2 in fact for agent2 in agents):
                            edges.append((agent1, agent2))
        
        # 3. Use topological_sort to find knowledge propagation order
        if edges:
            knowledge_order = topological_sort(edges)
            if knowledge_order is None:
                knowledge_order = agents  # fallback if cycle
        else:
            knowledge_order = agents
        
        # 4. Use check_transitivity to find closure of knowledge relationships
        if len(agents) >= 2:
            transitivity_result = check_transitivity(edges)
            # Extract reachable sets
            reachable = {}
            for agent in agents:
                reachable[agent] = transitivity_result.get(agent, set())
        else:
            reachable = {agent: set() for agent in agents}
        
        # 5. Use SAT entailment to check perspective consistency
        clauses = []
        var_map = {}
        var_counter = 1
        
        # Map facts to propositional variables
        for fact in structure["facts"]:
            var_map[fact] = var_counter
            var_counter += 1
        
        # Map agent beliefs to variables: "Agent_knows_Fact"
        for agent in agents:
            for fact in structure["facts"]:
                var_map[f"{agent}_knows_{fact}"] = var_counter
                var_counter += 1
        
        # Encode observations as clauses
        for agent, fact, value in observations:
            if fact in var_map and f"{agent}_knows_{fact}" in var_map:
                fact_var = var_map[fact]
                knows_var = var_map[f"{agent}_knows_{fact}"]
                # If agent knows fact, then fact must be true
                clauses.append([-knows_var, fact_var])
                # If observation is True, agent knows it
                if value:
                    clauses.append([knows_var])
        
        # Encode knowledge propagation: if A knows B knows X, then A knows X
        for agent1 in agents:
            for agent2 in agents:
                if agent1 != agent2:
                    for fact in structure["facts"]:
                        if (f"{agent1}_knows_{agent2}_knows_{fact}" in var_map and 
                            f"{agent1}_knows_{fact}" in var_map and
                            f"{agent2}_knows_{fact}" in var_map):
                            knows1_var = var_map[f"{agent1}_knows_{agent2}_knows_{fact}"]
                            knows2_var = var_map[f"{agent1}_knows_{fact}"]
                            knows3_var = var_map[f"{agent2}_knows_{fact}"]
                            clauses.append([-knows1_var, knows2_var])
                            clauses.append([-knows1_var, knows3_var])
        
        # 6. Use check_entailment to see what perspectives entail
        perspective_differences = []
        for agent in agents:
            # What does this agent know that others might not?
            agent_knows = []
            for fact in structure["facts"]:
                if f"{agent}_knows_{fact}" in var_map:
                    agent_knows.append(var_map[f"{agent}_knows_{fact}"])
            
            if agent_knows:
                # Check if this knowledge entails contradictions with others
                for other_agent in agents:
                    if other_agent != agent:
                        other_ignorant = []
                        for fact in structure["facts"]:
                            if f"{other_agent}_knows_{fact}" in var_map:
                                other_ignorant.append(-var_map[f"{other_agent}_knows_{fact}"])
                        
                        if other_ignorant:
                            entailment_result = check_entailment(clauses, other_ignorant[0])
                            if entailment_result is not None:
                                if not entailment_result:  # Not entailed = perspective difference
                                    perspective_differences.append((agent, other_agent))
        
        # 7. Use detect_paradox to check for logical inconsistencies in perspectives
        paradox_result = detect_paradox(clauses)
        
        # 8. Use bayesian_update to compute confidence in perspective differences
        prior = 0.5
        likelihood = len(perspective_differences) / max(1, len(agents) * (len(agents) - 1))
        confidence = bayesian_update(prior, likelihood)
        
        # 9. Use entropy to measure uncertainty in belief distribution
        belief_probs = []
        for agent in agents:
            agent_beliefs = belief_sets.get(agent, set())
            belief_probs.append(len(agent_beliefs) / max(1, len(structure["facts"])))
        
        if belief_probs:
            uncertainty = entropy(belief_probs)
        else:
            uncertainty = 1.0
        
        # 10. Determine which agent has the most unique perspective
        unique_counts = {}
        for agent in agents:
            unique_count = 0
            agent_beliefs = belief_sets.get(agent, set())
            for other_agent in agents:
                if other_agent != agent:
                    other_beliefs = belief_sets.get(other_agent, set())
                    unique_count += len(agent_beliefs - other_beliefs)
            unique_counts[agent] = unique_count
        
        # 11. Use confidence_from_agreement to get final confidence
        if unique_counts:
            scores = list(unique_counts.values())
            agreement_confidence = confidence_from_agreement(scores)
        else:
            agreement_confidence = 0.5
        
        # Determine answer based on topological order and perspective differences
        if perspective_differences:
            # Find agent with most perspective differences (most unique viewpoint)
            diff_counts = {}
            for agent in agents:
                diff_counts[agent] = sum(1 for a, b in perspective_differences if a == agent)
            
            if diff_counts:
                max_agent = max(diff_counts.items(), key=lambda x: x[1])[0]
                computed_answer = max_agent
            else:
                # Use topological order: first in knowledge propagation
                computed_answer = knowledge_order[0] if knowledge_order else agents[0]
        else:
            # No perspective differences, use topological order
            computed_answer = knowledge_order[0] if knowledge_order else agents[0]
        
        # Adjust confidence based on paradox detection
        if paradox_result is not None and paradox_result:
            confidence *= 0.7  # Reduce confidence if paradox detected
        
        # Combine confidence sources
        final_confidence = (confidence + agreement_confidence + (1 - uncertainty)) / 3
        
        reasoning = f"Topological order: {knowledge_order}. Perspective differences: {perspective_differences}. Uncertainty: {uncertainty:.2f}"
        
        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "reasoning": reasoning
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        
        for candidate in candidates:
            # Primary: exact match of agent name
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Check if any agent from reasoning appears
                agent_found = False
                for word in candidate.split():
                    if word[0].isupper() and word.lower() != computed_answer.lower():
                        # Might be another agent
                        agent_found = True
                        break
                
                if agent_found:
                    base_score = 0.3  # Partial match - different agent
                else:
                    # Use NCD similarity to reasoning text
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
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Normalize scores to [0, 1] range
        scores = [item["score"] for item in scored]
        if max(scores) > 0:
            for item in scored:
                item["score"] = item["score"] / max(scores)
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance between two strings."""
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) > 0:
            return (cab - min(ca, cb)) / max(ca, cb)
        return 1.0