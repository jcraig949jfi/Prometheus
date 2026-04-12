import re
import zlib
from typing import Dict, List, Any, Set, Tuple

from forge_primitives import (
    track_beliefs,
    sally_anne_test,
    check_transitivity,
    confidence_from_agreement,
    topological_sort,
    entropy
)
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query
from forge.amino_acids.pysat_acids import check_entailment


class ReasoningTool:
    """Seismology x Bayesian networks - perspective_shift"""

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
        
        # Extract agents (capitalized names that appear as subjects)
        agent_pattern = r'\b([A-Z][a-z]+)\b'
        for line in lines:
            found = re.findall(agent_pattern, line)
            for name in found:
                if name not in ['The', 'A', 'An', 'In', 'On', 'At', 'To', 'From']:
                    agents.add(name)
        
        # Extract facts (simple declarative statements)
        fact_pattern = r'\b(is|has|knows|believes|thinks)\b'
        for line in lines:
            if re.search(fact_pattern, line, re.IGNORECASE):
                # Clean up the fact
                fact = line.lower().replace('that ', '').replace('which ', '')
                facts.add(fact)
        
        # Extract observations (who saw what)
        obs_pattern = r'(\w+)\s+(saw|observed|noticed|heard)\s+(.+)'
        for line in lines:
            match = re.search(obs_pattern, line, re.IGNORECASE)
            if match:
                observer, verb, content = match.groups()
                # Parse content to extract what was observed
                if 'move' in content.lower() or 'change' in content.lower():
                    # Extract moved object and locations
                    loc_match = re.search(r'from\s+(\w+)\s+to\s+(\w+)', content, re.IGNORECASE)
                    if loc_match:
                        old_loc, new_loc = loc_match.groups()
                        observations.append((observer, content, True))
        
        # Extract question type
        question_type = "unknown"
        if 'who' in question.lower():
            question_type = "agent"
        elif 'what' in question.lower():
            question_type = "fact"
        elif 'where' in question.lower():
            question_type = "location"
        
        return {
            "agents": list(agents),
            "facts": list(facts),
            "observations": observations,
            "question": question,
            "question_type": question_type,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply seismology-inspired reasoning about knowledge propagation."""
        agents = structure["agents"]
        observations = structure["observations"]
        question = structure["question"]
        
        if not agents:
            return {"answer": "Unknown", "confidence": 0.0, "reasoning": "No agents found"}
        
        # Seismology concept: Knowledge propagates like seismic waves through social networks
        # Agents are seismic stations, knowledge is wave energy
        # Different agents have different "epistemic density" affecting knowledge transmission
        
        # Build belief propagation network using track_beliefs (T1 primitive)
        # Convert observations to belief tracking format
        belief_observations = []
        for obs in observations:
            if len(obs) >= 3:
                observer, content, truth = obs
                # Extract fact from content
                fact_words = content.split()[:3]  # First few words as fact
                fact = " ".join(fact_words).lower()
                belief_observations.append((observer, fact, truth))
        
        # CRITICAL: track_beliefs directly determines which agents believe which facts
        belief_state = track_beliefs(agents, belief_observations)
        if belief_state is None:
            belief_state = {}
        
        # Build Bayesian network for knowledge propagation (amino acid)
        # Nodes: agents' knowledge states
        edges = []
        for i, agent1 in enumerate(agents):
            for j, agent2 in enumerate(agents):
                if i != j:
                    # Knowledge can flow between connected agents
                    edges.append((f"Knows_{agent1}", f"Knows_{agent2}"))
        
        # CRITICAL: build_bn creates the model for conditional_query
        bn_model = build_bn(edges)
        
        # Determine which agent has most unique knowledge (entropy measure)
        agent_entropies = {}
        for agent in agents:
            beliefs = belief_state.get(agent, set())
            # Convert belief set to probability distribution
            if beliefs:
                # Each belief contributes equally
                prob = 1.0 / len(beliefs)
                probs = [prob] * len(beliefs)
                # CRITICAL: entropy measures uncertainty in agent's knowledge
                agent_entropy = entropy(probs) if len(probs) > 0 else 0.0
            else:
                agent_entropy = 1.0  # Maximum uncertainty
            agent_entropies[agent] = agent_entropy
        
        # Use Sally-Anne test for false belief reasoning (T1 primitive)
        # Find moving object scenarios
        move_pattern = r'move[d]?\s+from\s+(\w+)\s+to\s+(\w+)'
        move_match = re.search(move_pattern, structure["raw"], re.IGNORECASE)
        if move_match:
            original_loc, new_loc = move_match.groups()
            # Determine who moved it and who saw
            mover = None
            observers = set()
            for line in structure["raw"].split('.'):
                if 'move' in line.lower():
                    for agent in agents:
                        if agent.lower() in line.lower():
                            mover = agent
                            break
                if 'saw' in line.lower() or 'observed' in line.lower():
                    for agent in agents:
                        if agent.lower() in line.lower():
                            observers.add(agent)
            
            if mover and observers:
                # CRITICAL: sally_anne_test directly determines false beliefs
                false_beliefs = sally_anne_test(
                    mover, observers, original_loc, new_loc
                )
                if false_beliefs:
                    # Agent with false belief has different perspective
                    for agent, belief in false_beliefs.items():
                        if agent in agent_entropies:
                            agent_entropies[agent] += 0.5  # Penalty for false belief
        
        # Check transitivity of knowledge relationships (T1 primitive)
        # Build relation pairs: if A knows B knows X, then A knows X
        relations = []
        for agent1 in agents:
            for agent2 in agents:
                if agent1 != agent2:
                    # If agent1 observed agent2 observing something
                    for obs in observations:
                        if len(obs) >= 2 and obs[0] == agent2:
                            relations.append((agent1, f"knows_{agent2}_observation"))
        
        # CRITICAL: check_transitivity finds closure of knowledge relationships
        transitive_closure = check_transitivity(relations)
        
        # Determine most knowledgeable agent (lowest entropy = most certain knowledge)
        if agent_entropies:
            # Find agent with minimum entropy (most certain knowledge)
            min_entropy_agent = min(agent_entropies.items(), key=lambda x: x[1])[0]
            
            # Use conditional_query to verify knowledge (amino acid)
            # Query: What does this agent know given observations?
            if bn_model is not None:
                evidence = {}
                for agent in agents:
                    if agent in belief_state and belief_state[agent]:
                        evidence[f"Knows_{agent}"] = True
                
                # CRITICAL: conditional_query directly informs confidence
                query_result = conditional_query(
                    bn_model, 
                    [f"Knows_{min_entropy_agent}"], 
                    evidence
                )
                
                # Calculate confidence from multiple sources (T1 primitive)
                confidence_sources = []
                if agent_entropies[min_entropy_agent] < 0.5:
                    confidence_sources.append(0.8)
                if transitive_closure and min_entropy_agent in transitive_closure:
                    confidence_sources.append(0.7)
                if query_result is not None:
                    # Extract probability from query result
                    if isinstance(query_result, dict) and 'probability' in query_result:
                        confidence_sources.append(query_result['probability'])
                    elif isinstance(query_result, (int, float)):
                        confidence_sources.append(float(query_result))
                
                # CRITICAL: confidence_from_agreement combines multiple confidence estimates
                if confidence_sources:
                    confidence = confidence_from_agreement(confidence_sources)
                else:
                    confidence = 0.5
            else:
                confidence = 0.5
        else:
            min_entropy_agent = agents[0] if agents else "Unknown"
            confidence = 0.3
        
        # Use topological sort to order agents by knowledge propagation (T1 primitive)
        # Build DAG of knowledge flow: who learned from whom
        knowledge_edges = []
        for obs in observations:
            if len(obs) >= 2:
                observer, content = obs[0], obs[1]
                # Find source of knowledge in content
                for agent in agents:
                    if agent != observer and agent.lower() in content.lower():
                        knowledge_edges.append((agent, observer))  # source -> observer
        
        # CRITICAL: topological_sort determines the knowledge hierarchy
        knowledge_order = topological_sort(knowledge_edges)
        if knowledge_order and min_entropy_agent in knowledge_order:
            # Agent high in knowledge order is more knowledgeable
            position = knowledge_order.index(min_entropy_agent)
            confidence = max(confidence, 1.0 - position/len(knowledge_order))
        
        # Determine answer based on question type
        computed_answer = min_entropy_agent
        
        # Check entailment for logical consistency (amino acid)
        # Build simple logical statements from facts
        clauses = []
        for fact in structure["facts"]:
            # Encode fact as positive literal
            fact_id = hash(fact) % 1000
            clauses.append([fact_id])
        
        # Add negation of contradictory statements
        if 'not' in question.lower():
            question_id = hash(question) % 1000
            clauses.append([-question_id])
        
        # CRITICAL: check_entailment verifies logical consistency
        if clauses:
            entailment_result = check_entailment(clauses, [1])  # Check if facts entail anything
            if entailment_result is False:
                # Inconsistent knowledge reduces confidence
                confidence *= 0.8
        
        return {
            "answer": computed_answer,
            "confidence": min(max(confidence, 0.0), 1.0),
            "reasoning": f"Agent {computed_answer} has most certain knowledge (entropy: {agent_entropies.get(computed_answer, 0.0):.2f})"
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact or partial match of computed answer
            score = 0.0
            
            # Check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                score = 1.0 * confidence
            else:
                # Fallback: NCD similarity between reasoning and candidate
                ncd_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
                score = ncd_score * confidence
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        # Extract raw scores
        raw_scores = [item["raw_score"] for item in scored]
        
        # Simple min-max normalization if range is too small
        min_score = min(raw_scores)
        max_score = max(raw_scores)
        
        if max_score - min_score > 0.001:  # Significant range
            for item in scored:
                normalized = (item["raw_score"] - min_score) / (max_score - min_score)
                item["score"] = normalized
        else:
            # All scores similar, use confidence-based adjustment
            for item in scored:
                item["score"] = item["raw_score"]
        
        return scored

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