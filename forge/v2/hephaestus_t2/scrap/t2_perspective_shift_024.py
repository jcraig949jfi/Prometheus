import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    track_beliefs,
    sally_anne_test,
    check_transitivity,
    confidence_from_agreement
)
from forge.amino_acids.constraint_acids import solve_first


class ReasoningTool:
    """social_choice_theory x constraint_acids - perspective_shift"""

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
        
        agents = set()
        facts = set()
        observations = []
        
        # Extract agent names (capitalized words that appear as subjects)
        agent_pattern = r'\b([A-Z][a-z]+)\b'
        for line in lines:
            potential_agents = re.findall(agent_pattern, line)
            for agent in potential_agents:
                if agent.lower() not in ['the', 'and', 'but', 'however', 'therefore', 'which', 'what', 'who']:
                    agents.add(agent)
        
        # Extract facts (statements about the world)
        fact_keywords = ['knows', 'believes', 'thinks', 'sees', 'hears', 'tells', 'says']
        for line in lines:
            line_lower = line.lower()
            for keyword in fact_keywords:
                if keyword in line_lower:
                    # Extract the fact content
                    fact_match = re.search(rf'{keyword}\s+(that\s+)?([^.,]+)', line_lower)
                    if fact_match:
                        fact = fact_match.group(2).strip()
                        if fact:
                            facts.add(fact)
        
        # Extract observations (who observed what)
        obs_pattern = r'([A-Z][a-z]+)\s+(saw|heard|observed|noticed)\s+([^.,]+)'
        for line in lines:
            matches = re.findall(obs_pattern, line, re.IGNORECASE)
            for agent, verb, content in matches:
                observations.append((agent, content.strip(), True))
        
        # Extract question type
        question_type = "unknown"
        if "who knows" in question.lower() or "who believes" in question.lower():
            question_type = "knowledge_query"
        elif "what does" in question.lower() and "think" in question.lower():
            question_type = "belief_query"
        elif "false belief" in prompt.lower():
            question_type = "false_belief"
        
        return {
            "agents": list(agents),
            "facts": list(facts),
            "observations": observations,
            "question": question,
            "question_type": question_type,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use social choice theory (voting over possible worlds) to determine perspectives."""
        agents = structure["agents"]
        observations = structure["observations"]
        question_type = structure["question_type"]
        
        if not agents:
            return {"answer": "No agents found", "confidence": 0.0, "reasoning": "No agents extracted"}
        
        # CRITICAL: Use track_beliefs primitive to model knowledge propagation
        # This directly determines which agents know which facts
        belief_state = track_beliefs(agents, observations)
        if belief_state is None:
            belief_state = {agent: set() for agent in agents}
        
        # CRITICAL: Use sally_anne_test for false belief scenarios
        # Extract object movement info if present
        object_info = self._extract_object_movement(structure["raw"])
        false_belief_result = None
        if object_info:
            false_belief_result = sally_anne_test(
                who_moved=object_info["mover"],
                who_saw_move=object_info["observers"],
                original_location=object_info["original_loc"],
                new_location=object_info["new_loc"]
            )
        
        # CRITICAL: Use constraint_acids to find consistent world states
        # Model as CSP: variables are facts, domains are {True, False}
        # Constraints come from observations and logical consistency
        csp_solution = self._build_csp_solution(structure, belief_state)
        
        # CRITICAL: Use check_transitivity to analyze knowledge hierarchies
        # Build knowledge relations: agent A knows more than B if A knows all B's facts
        knowledge_relations = []
        for i, agent_a in enumerate(agents):
            for j, agent_b in enumerate(agents):
                if i != j:
                    if belief_state.get(agent_a, set()).issuperset(belief_state.get(agent_b, set())):
                        knowledge_relations.append((agent_a, agent_b))
        
        transitivity_result = check_transitivity(knowledge_relations)
        if transitivity_result is None:
            transitivity_result = {}
        
        # Determine answer based on question type
        computed_answer = self._determine_answer(
            structure, belief_state, false_belief_result, 
            csp_solution, transitivity_result
        )
        
        # CRITICAL: Use confidence_from_agreement on multiple reasoning paths
        confidence_scores = []
        
        # Score from belief_state consistency
        if belief_state:
            avg_knowledge = sum(len(facts) for facts in belief_state.values()) / len(agents)
            confidence_scores.append(min(avg_knowledge / 10.0, 1.0))
        
        # Score from CSP solution
        if csp_solution:
            confidence_scores.append(0.7 if csp_solution else 0.3)
        
        # Score from transitivity analysis
        if transitivity_result:
            hierarchy_depth = max(len(chain) for chain in transitivity_result.values()) if transitivity_result else 1
            confidence_scores.append(min(hierarchy_depth / len(agents), 1.0))
        
        confidence = confidence_from_agreement(confidence_scores) if confidence_scores else 0.5
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Belief state: {belief_state}, CSP: {csp_solution}, Transitivity: {transitivity_result}",
            "belief_state": belief_state,
            "csp_solution": csp_solution,
            "transitivity": transitivity_result
        }

    def _extract_object_movement(self, text: str) -> Dict[str, Any] | None:
        """Extract object movement information for false belief scenarios."""
        movement_patterns = [
            r'([A-Z][a-z]+)\s+moved\s+the\s+(\w+)\s+from\s+(\w+)\s+to\s+(\w+)',
            r'the\s+(\w+)\s+was\s+moved\s+from\s+(\w+)\s+to\s+(\w+)\s+by\s+([A-Z][a-z]+)',
            r'([A-Z][a-z]+)\s+put\s+the\s+(\w+)\s+in\s+the\s+(\w+)'
        ]
        
        for pattern in movement_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 4:
                    mover = match.group(1)
                    object_name = match.group(2)
                    original = match.group(3)
                    new = match.group(4)
                elif len(match.groups()) == 3:
                    object_name = match.group(1)
                    original = match.group(2)
                    new = match.group(3)
                    mover = "unknown"
                else:
                    continue
                
                # Extract observers
                observer_pattern = rf'([A-Z][a-z]+)\s+(saw|watched|observed)\s+{mover}'
                observers = set(re.findall(observer_pattern, text, re.IGNORECASE))
                observer_names = {obs[0] for obs in observers}
                
                return {
                    "mover": mover,
                    "object": object_name,
                    "original_loc": original,
                    "new_loc": new,
                    "observers": observer_names
                }
        return None

    def _build_csp_solution(self, structure: Dict[str, Any], 
                           belief_state: Dict[str, set]) -> Dict[str, bool] | None:
        """Build and solve CSP for consistent world states."""
        facts = structure["facts"]
        agents = structure["agents"]
        observations = structure["observations"]
        
        if not facts:
            return None
        
        # Create variables for each fact
        variables = [f"fact_{i}" for i in range(len(facts))]
        domains = {var: [True, False] for var in variables}
        
        # Constraints: observations must be true
        constraints = []
        
        # Map facts to indices
        fact_to_idx = {fact: i for i, fact in enumerate(facts)}
        
        # Add observation constraints
        for agent, content, observed in observations:
            if observed and content in fact_to_idx:
                idx = fact_to_idx[content]
                
                def make_obs_constraint(fact_idx):
                    def constraint(assignment):
                        return assignment.get(f"fact_{fact_idx}", False)
                    return constraint
                
                constraints.append(([f"fact_{idx}"], make_obs_constraint(idx)))
        
        # Add knowledge constraints: if agent knows fact, it must be true
        for agent, known_facts in belief_state.items():
            for fact in known_facts:
                if fact in fact_to_idx:
                    idx = fact_to_idx[fact]
                    
                    def make_knowledge_constraint(fact_idx):
                        def constraint(assignment):
                            return assignment.get(f"fact_{fact_idx}", False)
                        return constraint
                    
                    constraints.append(([f"fact_{idx}"], make_knowledge_constraint(idx)))
        
        # CRITICAL: Use solve_first amino acid to find consistent world state
        # This directly determines which facts are true/false in consistent worlds
        if variables and constraints:
            solution = solve_first(variables_domains=domains, constraints=constraints)
            if solution:
                # Convert back to fact mapping
                fact_solution = {}
                for i, fact in enumerate(facts):
                    fact_solution[fact] = solution.get(f"fact_{i}", False)
                return fact_solution
        
        return None

    def _determine_answer(self, structure: Dict[str, Any],
                         belief_state: Dict[str, set],
                         false_belief_result: Dict[str, str] | None,
                         csp_solution: Dict[str, bool] | None,
                         transitivity_result: Dict[str, set]) -> str:
        """Determine the specific answer based on reasoning results."""
        question = structure["question"].lower()
        agents = structure["agents"]
        
        # Check for false belief question
        if "false belief" in structure["raw"].lower() and false_belief_result:
            # Find agent with false belief
            for agent, location in false_belief_result.items():
                if agent in agents and "original" in location.lower():
                    return agent
        
        # Check for "who knows X" questions
        if "who knows" in question:
            # Extract the fact being asked about
            fact_match = re.search(r'who knows (?:that )?([^?]+)', question)
            if fact_match:
                target_fact = fact_match.group(1).strip()
                # Find agents who know this fact
                knowing_agents = []
                for agent, facts in belief_state.items():
                    if any(target_fact in str(fact) for fact in facts):
                        knowing_agents.append(agent)
                
                if knowing_agents:
                    if len(knowing_agents) == 1:
                        return knowing_agents[0]
                    else:
                        # Use transitivity to find most knowledgeable
                        max_knowledge = max(knowing_agents, 
                                          key=lambda a: len(transitivity_result.get(a, set())))
                        return max_knowledge
        
        # Check for "what does X think" questions
        if "what does" in question and "think" in question:
            agent_match = re.search(r'what does ([A-Z][a-z]+) think', question)
            if agent_match:
                target_agent = agent_match.group(1)
                if target_agent in belief_state:
                    # Return a key fact this agent believes
                    if belief_state[target_agent]:
                        return list(belief_state[target_agent])[0]
        
        # Default: agent with most knowledge
        if agents:
            # Use transitivity hierarchy to find top agent
            if transitivity_result:
                # Find agent at top of hierarchy (knows about most others)
                top_agent = max(transitivity_result.items(), 
                              key=lambda x: len(x[1]))[0] if transitivity_result else agents[0]
                return top_agent
            else:
                # Fallback to agent with most facts
                return max(agents, key=lambda a: len(belief_state.get(a, set())))
        
        return "Unknown"

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust by confidence
            adjusted_score = base_score * (0.5 + 0.5 * confidence)
            
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
        
        # Simple normalization to [0, 1] range
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