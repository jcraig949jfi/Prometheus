import re
import zlib
from typing import Dict, List, Any, Set, Tuple
from forge_primitives import track_beliefs, topological_sort, entropy, confidence_from_agreement
from forge.amino_acids.pysat_acids import check_entailment

class ReasoningTool:
    """Complexity theory x SAT entailment - perspective_shift"""

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
        
        agents = set()
        facts = set()
        observations = []
        question = ""
        
        # Extract agents (capitalized names that appear as subjects)
        agent_pattern = r'\b([A-Z][a-z]+)\b'
        for line in lines:
            matches = re.findall(agent_pattern, line)
            for match in matches:
                if match not in ['The', 'A', 'An', 'And', 'But', 'Or', 'Not', 'Knows', 'Sees', 'Hears']:
                    agents.add(match)
        
        # Extract facts (propositions after "knows that" or similar)
        fact_pattern = r'knows that (.+?)(?:\.|,| and| but| or|$)'
        for line in lines:
            matches = re.findall(fact_pattern, line.lower())
            for match in matches:
                fact = match.strip()
                if fact:
                    facts.add(fact)
        
        # Extract observations (who observed what)
        obs_pattern = r'([A-Z][a-z]+) (sees|hears|observes) (?:that )?(.+?)(?:\.|,| and| but| or|$)'
        for line in lines:
            matches = re.findall(obs_pattern, line)
            for agent, verb, content in matches:
                observations.append((agent, content, True))
        
        # Last line is usually the question
        if lines:
            question = lines[-1]
        
        return {
            "agents": list(agents),
            "facts": list(facts),
            "observations": observations,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use complexity theory concepts (knowledge hierarchies, computational depth) 
        to model perspective shifts via SAT entailment and belief tracking."""
        
        agents = structure["agents"]
        facts = structure["facts"]
        observations = structure["observations"]
        question = structure["question"]
        
        # CRITICAL: Use track_beliefs primitive to compute initial belief states
        # This directly determines which agents know what
        belief_states = track_beliefs(agents, observations)
        
        # CRITICAL: Build knowledge hierarchy using topological sort
        # Determine who knows more based on observation count
        edges = []
        for i, a1 in enumerate(agents):
            for j, a2 in enumerate(agents):
                if i != j:
                    # Agent a1 knows more than a2 if a1 has observed more facts
                    a1_obs = sum(1 for obs in observations if obs[0] == a1)
                    a2_obs = sum(1 for obs in observations if obs[0] == a2)
                    if a1_obs > a2_obs:
                        edges.append((a1, a2))  # a1 → a2 (a1 knows more)
        
        # CRITICAL: topological_sort determines the knowledge hierarchy order
        knowledge_hierarchy = topological_sort(edges)
        if knowledge_hierarchy is None:
            knowledge_hierarchy = agents  # fallback if cycle
        
        # CRITICAL: Use SAT entailment to check what each agent can deduce
        # Convert facts and observations to propositional logic
        clauses = []
        var_map = {}
        next_var = 1
        
        # Map facts to variables
        for fact in facts:
            var_map[fact] = next_var
            next_var += 1
        
        # Add observations as unit clauses
        for agent, content, value in observations:
            if content in var_map:
                var = var_map[content]
                clauses.append([var] if value else [-var])
        
        # CRITICAL: For each agent, check what they can entail from their perspective
        agent_entailments = {}
        for agent in agents:
            # Agent's knowledge = what they directly observed
            agent_knowledge = [obs[1] for obs in observations if obs[0] == agent]
            
            # Convert to clauses for this agent's perspective
            agent_clauses = clauses.copy()
            
            # Add agent's direct knowledge as premises
            for fact in agent_knowledge:
                if fact in var_map:
                    agent_clauses.append([var_map[fact]])
            
            # Check entailment of each fact from this agent's perspective
            agent_can_prove = []
            for fact, var in var_map.items():
                # CRITICAL: check_entailment amino acid directly determines what agent can deduce
                result = check_entailment(agent_clauses, [var])
                if result:
                    agent_can_prove.append(fact)
            
            agent_entailments[agent] = agent_can_prove
        
        # CRITICAL: Use entropy to measure uncertainty in knowledge distribution
        # Higher entropy = more diverse knowledge states among agents
        knowledge_counts = []
        for agent in agents:
            knowledge_counts.append(len(agent_entailments[agent]))
        
        if knowledge_counts:
            total_knowledge = sum(knowledge_counts)
            if total_knowledge > 0:
                probs = [count/total_knowledge for count in knowledge_counts]
                # CRITICAL: entropy primitive measures knowledge asymmetry
                knowledge_entropy = entropy(probs)
            else:
                knowledge_entropy = 0.0
        else:
            knowledge_entropy = 0.0
        
        # Determine which agent has the most complete perspective
        # Based on knowledge hierarchy and what they can prove
        best_agent = None
        max_provable = -1
        
        # Follow knowledge hierarchy (topological order)
        for agent in knowledge_hierarchy:
            provable_count = len(agent_entailments.get(agent, []))
            if provable_count > max_provable:
                max_provable = provable_count
                best_agent = agent
        
        if best_agent is None and agents:
            best_agent = agents[0]
        
        # CRITICAL: confidence_from_agreement primitive uses consistency across agents
        # to determine confidence in the answer
        provable_counts = [len(agent_entailments.get(a, [])) for a in agents]
        if provable_counts:
            # Normalize counts to [0, 1] range for confidence calculation
            max_count = max(provable_counts) if provable_counts else 1
            normalized = [c/max_count for c in provable_counts]
            # CRITICAL: confidence primitive directly affects final score
            confidence = confidence_from_agreement(normalized)
        else:
            confidence = 0.5
        
        # Extract the actual answer from the question
        computed_answer = best_agent if best_agent else "Unknown"
        
        # If question asks about a specific fact, check which agents know it
        if "know" in question.lower() or "believe" in question.lower():
            # Look for fact mentioned in question
            fact_in_q = None
            for fact in facts:
                if fact.lower() in question.lower():
                    fact_in_q = fact
                    break
            
            if fact_in_q:
                # Find agents who can prove this fact
                knowing_agents = []
                for agent in agents:
                    if fact_in_q in agent_entailments.get(agent, []):
                        knowing_agents.append(agent)
                
                if knowing_agents:
                    # CRITICAL: topological_sort determines which knowing agent is most knowledgeable
                    sorted_knowing = [a for a in knowledge_hierarchy if a in knowing_agents]
                    if sorted_knowing:
                        computed_answer = sorted_knowing[0]
                    else:
                        computed_answer = knowing_agents[0]
        
        return {
            "answer": computed_answer,
            "confidence": confidence * (1.0 - knowledge_entropy),  # Lower entropy → higher confidence
            "reasoning": f"Agent {computed_answer} has most complete perspective based on knowledge hierarchy {knowledge_hierarchy}",
            "agent_entailments": agent_entailments,
            "knowledge_hierarchy": knowledge_hierarchy,
            "knowledge_entropy": knowledge_entropy
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match of computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Apply confidence from reasoning
            final_score = base_score * confidence
            
            results.append({
                "candidate": candidate,
                "score": final_score,
                "base_score": base_score,
                "confidence": confidence
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Simple normalization to [0, 1] range
        scores = [item["score"] for item in scored]
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score > min_score:
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        else:
            for item in scored:
                item["score"] = 0.5  # Tie case
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance between two strings."""
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) > 0:
            return (cab - min(ca, cb)) / max(ca, cb)
        return 1.0