import re
import zlib
from typing import Dict, List, Any, Set, Tuple
from forge_primitives import (
    track_beliefs,
    sally_anne_test,
    confidence_from_agreement,
    modus_ponens,
    entropy
)
from forge.amino_acids.pysat_acids import check_entailment, detect_paradox
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Decision theory x SAT/Constraint reasoning - Perspective shift"""

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
        """Extract agents, their knowledge, facts, and the query from the prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        agents = set()
        facts = set()
        knowledge = {}
        query = ""
        
        # Extract agents (capitalized names, often followed by 'knows' or 'believes')
        agent_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        for line in lines:
            # Find potential agent names
            potential_agents = re.findall(agent_pattern, line)
            for agent in potential_agents:
                if agent.lower() in ['the', 'a', 'an', 'and', 'or', 'but', 'if', 'then']:
                    continue
                if any(keyword in line.lower() for keyword in ['knows', 'believes', 'thinks', 'sees', 'hears']):
                    agents.add(agent)
        
        # Extract facts and knowledge
        for line in lines:
            line_lower = line.lower()
            # Look for knowledge statements
            for agent in agents:
                if agent in line:
                    if 'knows that' in line_lower or 'believes that' in line_lower:
                        # Extract the proposition after 'that'
                        match = re.search(r'that\s+(.+?)(?:\.|$)', line_lower)
                        if match:
                            prop = match.group(1).strip()
                            if agent not in knowledge:
                                knowledge[agent] = set()
                            knowledge[agent].add(prop)
                            facts.add(prop)
                    elif 'knows' in line_lower or 'believes' in line_lower:
                        # Try to extract simple fact
                        parts = line.split(agent)
                        if len(parts) > 1:
                            fact_part = parts[1].split('.')[0].strip()
                            if fact_part and len(fact_part.split()) < 10:
                                if agent not in knowledge:
                                    knowledge[agent] = set()
                                knowledge[agent].add(fact_part.lower())
                                facts.add(fact_part.lower())
        
        # Last line is usually the query
        if lines:
            query = lines[-1]
        
        # Extract common facts (things stated as true without attribution)
        for line in lines:
            if not any(agent in line for agent in agents):
                # Simple fact statements
                if 'is true' in line.lower() or 'is the case' in line.lower():
                    fact = line.split('is')[0].strip()
                    if fact:
                        facts.add(fact.lower())
        
        return {
            "agents": list(agents),
            "knowledge": knowledge,
            "facts": list(facts),
            "query": query,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use decision theory to model agents as rational actors with information partitions."""
        agents = structure["agents"]
        knowledge = structure["knowledge"]
        facts = structure["facts"]
        query = structure["query"]
        
        # T1 Primitive 1: Track beliefs based on observations
        # Convert knowledge to observation format for track_beliefs
        observations = []
        for agent, known_facts in knowledge.items():
            for fact in known_facts:
                observations.append((agent, fact, True))
        
        belief_state = track_beliefs(agents, observations)
        
        # T1 Primitive 2: Use modus_ponens to derive new beliefs
        # Extract implication rules from facts
        premises = []
        derived_facts = set(facts)
        
        for fact in facts:
            if 'if' in fact and 'then' in fact:
                parts = fact.split('then')
                if len(parts) == 2:
                    antecedent = parts[0].replace('if', '').strip()
                    consequent = parts[1].strip()
                    premises.append((antecedent, consequent))
        
        # Apply modus ponens for each agent's knowledge
        agent_derivations = {}
        for agent in agents:
            agent_facts = set(knowledge.get(agent, []))
            new_facts = modus_ponens(premises, agent_facts)
            agent_derivations[agent] = new_facts
        
        # Amino Acid 1: Use SAT to check consistency of each agent's knowledge
        # Encode each agent's knowledge as CNF clauses
        agent_consistency = {}
        for agent in agents:
            clauses = []
            var_map = {}
            next_var = 1
            
            # Map facts to variables
            all_facts = set(knowledge.get(agent, [])) | agent_derivations.get(agent, set())
            for fact in all_facts:
                var_map[fact] = next_var
                next_var += 1
            
            # Each known fact is a unit clause
            for fact in knowledge.get(agent, []):
                if fact in var_map:
                    clauses.append([var_map[fact]])
            
            # Check consistency
            is_consistent = not detect_paradox(clauses) if clauses else True
            agent_consistency[agent] = is_consistent
        
        # Amino Acid 2: Use constraint solving to find possible worlds consistent with each agent's knowledge
        possible_worlds = {}
        for agent in agents:
            if not agent_consistency.get(agent, True):
                possible_worlds[agent] = []
                continue
            
            # Create CSP: each fact is a variable with domain {True, False}
            variables = list(set(knowledge.get(agent, [])) | agent_derivations.get(agent, set()))
            domains = {fact: [True, False] for fact in variables}
            
            # Constraints: known facts must be True
            constraints = []
            for fact in knowledge.get(agent, []):
                if fact in domains:
                    constraints.append(([fact], lambda x: x[fact] == True))
            
            # Find a possible world
            solution = solve_first(domains, constraints)
            possible_worlds[agent] = [solution] if solution else []
        
        # T1 Primitive 3: Compute entropy of each agent's belief state
        agent_entropy = {}
        for agent in agents:
            known_count = len(knowledge.get(agent, []))
            derived_count = len(agent_derivations.get(agent, set()))
            total_facts = known_count + derived_count
            
            if total_facts > 0:
                # Simple probability distribution: more facts = lower entropy
                p_known = known_count / total_facts
                p_derived = derived_count / total_facts
                agent_entropy[agent] = entropy([p_known, p_derived])
            else:
                agent_entropy[agent] = 1.0  # Maximum uncertainty
        
        # Determine which agent has the most complete/correct perspective
        # Decision theory: agents with consistent, derivable knowledge and low entropy have better perspective
        
        best_agent = None
        best_score = -1
        
        for agent in agents:
            consistency_score = 1.0 if agent_consistency.get(agent, False) else 0.0
            derivability_score = len(agent_derivations.get(agent, set())) / max(1, len(knowledge.get(agent, [])))
            entropy_score = 1.0 - agent_entropy.get(agent, 1.0)  # Convert to confidence
            
            # T1 Primitive 4: Aggregate scores using confidence_from_agreement
            agent_scores = [consistency_score, derivability_score, entropy_score]
            agent_confidence = confidence_from_agreement(agent_scores)
            
            if agent_confidence > best_score:
                best_score = agent_confidence
                best_agent = agent
        
        # Extract the actual answer from the query
        computed_answer = ""
        if best_agent:
            # If query asks about what an agent knows/believes
            if 'know' in query.lower() or 'believe' in query.lower():
                # Find which agent is mentioned in query
                for agent in agents:
                    if agent.lower() in query.lower():
                        # Return what that agent knows
                        known_facts = list(knowledge.get(agent, []))
                        if known_facts:
                            computed_answer = known_facts[0]
                        break
                if not computed_answer:
                    computed_answer = best_agent
            else:
                # Query is about which agent has correct perspective
                computed_answer = best_agent
        
        # Fallback if no agent found
        if not computed_answer and agents:
            computed_answer = agents[0]
        
        return {
            "answer": computed_answer,
            "confidence": best_score if best_score >= 0 else 0.5,
            "reasoning": f"Agent {best_agent} has most consistent knowledge with confidence {best_score:.2f}",
            "agent_scores": {agent: agent_consistency.get(agent, False) for agent in agents},
            "derivations": agent_derivations
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
            results.append({
                "candidate": candidate,
                "score": score,
                "computed_answer": computed_answer
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence from reasoning result."""
        if not scored:
            return scored
        
        # Simple calibration: normalize scores to [0, 1] range
        scores = [item["score"] for item in scored]
        if scores:
            min_score = min(scores)
            max_score = max(scores)
            if max_score > min_score:
                for item in scored:
                    item["score"] = (item["score"] - min_score) / (max_score - min_score)
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