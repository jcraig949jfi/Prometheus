import re
import zlib
from typing import Dict, List, Any, Set, Tuple

from forge_primitives import (
    track_beliefs,
    sally_anne_test,
    check_transitivity,
    confidence_from_agreement,
    entropy
)
from forge.amino_acids.pgmpy_acids import (
    build_bn,
    conditional_query,
    active_trails
)


class ReasoningTool:
    """Epidemiology x Bayesian Networks - Perspective Shift"""

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
        
        # Find agents (capitalized names, often proper nouns)
        agent_pattern = r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b'
        all_names = re.findall(agent_pattern, prompt)
        
        # Filter likely agents (names that appear multiple times or in specific contexts)
        for name in all_names:
            if prompt.count(name) >= 2 and len(name.split()) <= 2:
                agents.add(name)
        
        # Extract observations in format: "Agent saw/heard/knows that..."
        for line in lines:
            line_lower = line.lower()
            if any(word in line_lower for word in ['saw', 'heard', 'knows', 'observed', 'witnessed']):
                # Find agent and fact
                for agent in agents:
                    if agent in line:
                        # Extract fact (text after "that" or similar)
                        fact_match = re.search(r'that (.+?)(?:\.|$)', line_lower)
                        if fact_match:
                            fact = fact_match.group(1).strip()
                            # Determine if observation is positive or negative
                            is_true = not any(word in fact for word in ['not', "didn't", "doesn't"])
                            observations.append((agent, fact, is_true))
                            facts.add(fact)
        
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
        """Use epidemiological modeling to track belief propagation through agents."""
        agents = structure["agents"]
        observations = structure["observations"]
        question = structure["question"]
        
        if not agents or not observations:
            return {"answer": "Unknown", "confidence": 0.0, "reasoning": "Insufficient data"}
        
        # CRITICAL PRIMITIVE 1: Track beliefs based on observations
        belief_state = track_beliefs(agents, observations)
        if belief_state is None:
            belief_state = {}
        
        # Build epidemiological network: agents as nodes, communication as edges
        # In epidemiology, we model transmission paths (who can infect whom with information)
        edges = []
        for obs in observations:
            observer, fact, _ = obs
            # Observer can transmit this fact to others mentioned in the prompt
            for agent in agents:
                if agent != observer and agent in structure["raw"]:
                    # Direction: observer -> other_agent (information flow)
                    edges.append((observer, agent))
        
        # CRITICAL PRIMITIVE 2: Check transitivity of information flow
        transitive_closure = check_transitivity(edges)
        if transitive_closure is None:
            transitive_closure = {}
        
        # Build Bayesian network for belief uncertainty
        # Nodes: agents' beliefs about key facts
        bn_edges = []
        for source, targets in transitive_closure.items():
            for target in targets:
                bn_edges.append((f"{source}_belief", f"{target}_belief"))
        
        # CRITICAL AMINO ACID 1: Build Bayesian network
        bn_model = build_bn(bn_edges)
        
        # Determine which agent knows what based on active trails (epidemiological transmission paths)
        target_agent = None
        target_fact = None
        
        # Extract target from question
        for agent in agents:
            if agent.lower() in question.lower():
                target_agent = agent
                break
        
        # Find mentioned facts in question
        for fact in structure["facts"]:
            if any(word in question.lower() for word in fact.lower().split()[:2]):
                target_fact = fact
                break
        
        computed_answer = "Unknown"
        confidence = 0.5
        
        if target_agent and target_fact and bn_model is not None:
            # CRITICAL AMINO ACID 2: Find active trails (information transmission paths)
            trails = active_trails(bn_model, [f"{target_agent}_belief"], observed=None)
            
            if trails:
                # Agents reachable via active trails could have transmitted the information
                reachable_agents = set()
                for node in trails.get(f"{target_agent}_belief", []):
                    if node.endswith("_belief"):
                        reachable_agents.add(node.replace("_belief", ""))
                
                # CRITICAL PRIMITIVE 3: Use Sally-Anne test for false belief reasoning
                # Find a scenario where object was moved
                moved_object = None
                for fact in structure["facts"]:
                    if any(word in fact.lower() for word in ['moved', 'taken', 'removed']):
                        moved_object = "object"
                        break
                
                if moved_object:
                    # Simulate false belief scenario
                    false_belief_result = sally_anne_test(
                        who_moved=target_agent if target_agent in reachable_agents else agents[0],
                        who_saw_move=set([obs[0] for obs in observations if obs[2]]),
                        original_location="A",
                        new_location="B"
                    )
                    
                    if false_belief_result:
                        # Determine if target agent has false belief
                        for agent, location in false_belief_result.items():
                            if agent == target_agent:
                                if location == "A":  # False belief (thinks it's still at A)
                                    computed_answer = "False"
                                else:
                                    computed_answer = "True"
                                break
        
        # If Bayesian network approach failed, use belief state directly
        if computed_answer == "Unknown" and belief_state:
            # Check what target_agent believes
            if target_agent in belief_state:
                target_beliefs = belief_state[target_agent]
                if target_fact:
                    # Check if fact is in beliefs
                    fact_in_beliefs = any(target_fact.lower() in belief.lower() for belief in target_beliefs)
                    computed_answer = "True" if fact_in_beliefs else "False"
        
        # CRITICAL PRIMITIVE 4: Calculate entropy of belief distribution
        if belief_state:
            belief_counts = []
            for agent_beliefs in belief_state.values():
                belief_counts.append(len(agent_beliefs))
            if belief_counts:
                total_beliefs = sum(belief_counts)
                if total_beliefs > 0:
                    probs = [count/total_beliefs for count in belief_counts]
                    belief_entropy = entropy(probs)
                    # Higher entropy = more uncertainty = lower confidence
                    confidence = max(0.1, 1.0 - belief_entropy)
        
        # CRITICAL PRIMITIVE 5: Aggregate confidence from multiple agents' agreement
        if belief_state and len(belief_state) > 1:
            # Create scores based on belief consistency
            scores = []
            for agent_beliefs in belief_state.values():
                # Score = proportion of facts this agent believes
                score = len(agent_beliefs) / len(structure["facts"]) if structure["facts"] else 0.5
                scores.append(score)
            
            if scores:
                agg_confidence = confidence_from_agreement(scores)
                if agg_confidence is not None:
                    # Blend with existing confidence
                    confidence = (confidence + agg_confidence) / 2
        
        # Final fallback if still unknown
        if computed_answer == "Unknown":
            # Default to most common perspective
            if belief_state:
                all_beliefs = []
                for agent_beliefs in belief_state.values():
                    all_beliefs.extend(agent_beliefs)
                if all_beliefs:
                    # Find most frequent belief
                    from collections import Counter
                    belief_counter = Counter(all_beliefs)
                    most_common = belief_counter.most_common(1)
                    if most_common:
                        computed_answer = "True" if most_common[0][0] else "False"
        
        return {
            "answer": computed_answer,
            "confidence": min(0.99, max(0.01, confidence)),
            "reasoning": f"Epidemiological belief propagation analysis for {target_agent or 'agent'}"
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or containment
            candidate_lower = candidate.lower()
            answer_lower = computed_answer.lower()
            
            if answer_lower in candidate_lower:
                base_score = 1.0
            elif self._ncd(computed_answer, candidate) < 0.5:
                base_score = 0.7
            else:
                base_score = 0.3
            
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
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        scores = [item["score"] for item in scored]
        if not scores:
            return scored
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score - min_score > 0.001:
            # Normalize to [0, 1] range
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        else:
            # All scores are similar, differentiate slightly
            for i, item in enumerate(scored):
                item["score"] = 0.5 + (i * 0.001)
        
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