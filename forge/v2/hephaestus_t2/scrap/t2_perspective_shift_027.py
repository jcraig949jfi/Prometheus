import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, track_beliefs
from forge.amino_acids.pysat_acids import check_entailment


class ReasoningTool:
    """Auction theory x SAT entailment - perspective_shift"""

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
        """Extract agents, their knowledge, and the query from the prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        
        agents = set()
        knowledge = {}
        query = ""
        
        # Find agents (capitalized names that appear as subjects)
        agent_pattern = r'\b([A-Z][a-z]+)\b'
        for line in lines:
            matches = re.findall(agent_pattern, line)
            for match in matches:
                if match not in ['The', 'What', 'Which', 'Does', 'Is', 'True', 'False']:
                    agents.add(match)
        
        # Extract knowledge statements
        for line in lines:
            if 'knows' in line.lower() or 'believes' in line.lower() or 'sees' in line.lower():
                # Find agent and fact
                agent_match = re.search(r'\b([A-Z][a-z]+)\b', line)
                if agent_match:
                    agent = agent_match.group(1)
                    fact = line.split('that')[-1].strip() if 'that' in line else line
                    fact = fact.rstrip('.')
                    if agent not in knowledge:
                        knowledge[agent] = []
                    knowledge[agent].append(fact)
        
        # Last line is usually the query
        if lines:
            query = lines[-1]
        
        return {
            "agents": list(agents),
            "knowledge": knowledge,
            "query": query,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use auction theory (common knowledge vs private information) to determine what each agent knows."""
        agents = structure["agents"]
        knowledge = structure["knowledge"]
        query = structure["query"]
        
        # Extract facts from query
        query_fact = query.lower().replace('what does', '').replace('know?', '').replace('believe?', '').strip()
        query_fact = query_fact.capitalize()
        
        # Build SAT clauses for each agent's knowledge
        all_clauses = []
        agent_clauses = {}
        
        for agent in agents:
            agent_facts = knowledge.get(agent, [])
            clauses = []
            
            # Convert each fact to a propositional variable
            for fact in agent_facts:
                # Create a unique variable ID for each fact
                var_id = abs(hash(fact)) % 1000 + 1
                clauses.append([var_id])  # Fact is true
            
            # Add clauses for knowledge relationships
            # If agent A knows fact X, then X must be true
            # This is encoded as: A_knows_X → X
            # In SAT: ¬A_knows_X ∨ X
            for fact in agent_facts:
                fact_var = abs(hash(fact)) % 1000 + 1
                knows_var = abs(hash(f"{agent}_knows_{fact}")) % 1000 + 1001
                clauses.append([-knows_var, fact_var])
            
            agent_clauses[agent] = clauses
            all_clauses.extend(clauses)
        
        # Use auction theory concept: common knowledge vs private information
        # In auctions, bidders have private valuations (private knowledge)
        # and common knowledge about auction rules
        
        # Compute entropy of each agent's knowledge base
        agent_entropies = {}
        for agent in agents:
            facts = knowledge.get(agent, [])
            if facts:
                # Create a simple probability distribution over facts
                # Each fact is equally likely to be known/not known
                probs = [0.5] * len(facts)  # Uniform uncertainty
                agent_entropy = entropy(probs)
                agent_entropies[agent] = agent_entropy
            else:
                agent_entropies[agent] = 0.0
        
        # Use track_beliefs to model belief propagation
        observations = []
        for agent in agents:
            facts = knowledge.get(agent, [])
            for fact in facts:
                # Agent observes the fact (True)
                observations.append((agent, fact, True))
        
        belief_state = track_beliefs(agents, observations)
        
        # Determine which agent knows the query fact
        # Higher entropy means more uncertainty, lower means more specific knowledge
        # In auction theory, bidders with more precise information (lower entropy)
        # have stronger beliefs
        
        query_agent = None
        max_confidence = 0.0
        
        for agent in agents:
            facts = knowledge.get(agent, [])
            if query_fact in facts or any(query_fact.lower() in f.lower() for f in facts):
                # Agent directly knows the fact
                # Use bayesian_update to compute confidence
                prior = 0.5  # Base uncertainty
                likelihood = 0.9  # High likelihood if mentioned
                confidence = bayesian_update(prior, likelihood)
                
                # Adjust confidence based on entropy
                # Lower entropy → higher confidence
                agent_entropy = agent_entropies.get(agent, 1.0)
                entropy_factor = 1.0 - min(agent_entropy, 1.0)
                confidence = confidence * (0.5 + 0.5 * entropy_factor)
                
                if confidence > max_confidence:
                    max_confidence = confidence
                    query_agent = agent
        
        # If no direct match, use SAT entailment to infer knowledge
        if query_agent is None:
            # Check which agent's knowledge base entails the query
            for agent in agents:
                clauses = agent_clauses.get(agent, [])
                if clauses:
                    # Create a variable for the query fact
                    query_var = abs(hash(query_fact)) % 1000 + 1
                    
                    # Check if agent's knowledge entails the query
                    # This means: knowledge → query
                    # In SAT: knowledge ∧ ¬query is UNSAT
                    test_clauses = clauses + [[-query_var]]
                    
                    result = check_entailment(clauses, [query_var])
                    
                    if result is not None and result.get("entails", False):
                        # Agent's knowledge entails the query
                        confidence = 0.8
                        
                        # Adjust with entropy
                        agent_entropy = agent_entropies.get(agent, 1.0)
                        entropy_factor = 1.0 - min(agent_entropy, 1.0)
                        confidence = confidence * (0.5 + 0.5 * entropy_factor)
                        
                        if confidence > max_confidence:
                            max_confidence = confidence
                            query_agent = agent
        
        # Fallback: agent with most specific knowledge (lowest entropy)
        if query_agent is None and agent_entropies:
            # Find agent with lowest entropy (most precise information)
            min_entropy = min(agent_entropies.values())
            for agent, ent in agent_entropies.items():
                if ent == min_entropy:
                    query_agent = agent
                    # Confidence based on how low entropy is
                    max_confidence = 0.7 * (1.0 - min_entropy)
                    break
        
        # Final confidence aggregation
        if query_agent:
            # Get confidence from agreement among different reasoning methods
            conf_scores = []
            
            # 1. Direct knowledge confidence
            facts = knowledge.get(query_agent, [])
            if query_fact in facts or any(query_fact.lower() in f.lower() for f in facts):
                conf_scores.append(0.9)
            
            # 2. Entropy-based confidence
            agent_entropy = agent_entropies.get(query_agent, 1.0)
            entropy_conf = 1.0 - min(agent_entropy, 1.0)
            conf_scores.append(entropy_conf)
            
            # 3. Belief state confidence
            if query_agent in belief_state:
                beliefs = belief_state[query_agent]
                if query_fact in beliefs or any(query_fact.lower() in b.lower() for b in beliefs):
                    conf_scores.append(0.8)
            
            if conf_scores:
                final_confidence = confidence_from_agreement(conf_scores)
            else:
                final_confidence = max_confidence
        else:
            query_agent = agents[0] if agents else "Unknown"
            final_confidence = 0.5
        
        computed_answer = query_agent
        
        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "reasoning": f"Agent {computed_answer} has the most relevant knowledge based on auction theory analysis of private information vs common knowledge.",
            "agent_entropies": agent_entropies,
            "belief_state": belief_state
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match of agent name
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust with confidence
            adjusted_score = base_score * (0.5 + 0.5 * confidence)
            
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
        if max(scores) > min(scores):
            normalized = [(s - min(scores)) / (max(scores) - min(scores)) for s in scores]
        else:
            normalized = [0.5] * len(scores)
        
        # Apply softmax for better differentiation
        exp_scores = [2.71828 ** s for s in normalized]
        sum_exp = sum(exp_scores)
        if sum_exp > 0:
            calibrated_scores = [e / sum_exp for e in exp_scores]
        else:
            calibrated_scores = normalized
        
        # Update results
        for i, item in enumerate(scored):
            item["score"] = calibrated_scores[i]
        
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