import re
import zlib
from typing import Dict, List, Any, Set, Tuple

from forge_primitives import (
    track_beliefs,
    sally_anne_test,
    confidence_from_agreement,
    entropy,
    modus_ponens,
    topological_sort
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
    """fluid_dynamics x pgmpy_acids - perspective_shift"""

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
        """Extract agents, facts, observations, and the question from the prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        if not lines:
            return {"agents": [], "facts": set(), "observations": [], "question": "", "raw": prompt}

        # Extract agents (capitalized names, typically proper nouns)
        agent_pattern = r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b'
        potential_agents = re.findall(agent_pattern, prompt)
        # Filter: exclude common non-agent words and keep those appearing multiple times
        common_non_agents = {"The", "A", "An", "This", "That", "It", "He", "She", "They", "We", "You"}
        agent_counts = {}
        for agent in potential_agents:
            if agent not in common_non_agents:
                agent_counts[agent] = agent_counts.get(agent, 0) + 1
        agents = [agent for agent, count in agent_counts.items() if count > 1]

        # Extract facts (simple declarative statements in present tense)
        facts = set()
        observation_tuples = []
        for line in lines:
            lower_line = line.lower()
            if "knows that" in lower_line or "believes that" in lower_line:
                # Extract belief observation
                match = re.search(r'([A-Z][a-z]+(?: [A-Z][a-z]+)*) (?:knows|believes) that (.+)', line)
                if match:
                    agent, fact = match.groups()
                    observation_tuples.append((agent, fact.strip(), True))
                    facts.add(fact.strip())
            elif "sees" in lower_line or "observes" in lower_line:
                # Extract perceptual observation
                match = re.search(r'([A-Z][a-z]+(?: [A-Z][a-z]+)*) (?:sees|observes) (.+)', line)
                if match:
                    agent, event = match.groups()
                    observation_tuples.append((agent, event.strip(), True))
                    facts.add(event.strip())
            elif "does not know" in lower_line or "is unaware" in lower_line:
                # Extract lack of knowledge
                match = re.search(r'([A-Z][a-z]+(?: [A-Z][a-z]+)*) (?:does not know|is unaware of) (.+)', line)
                if match:
                    agent, fact = match.groups()
                    observation_tuples.append((agent, fact.strip(), False))
                    facts.add(fact.strip())
            elif line.endswith('?') or "which" in lower_line or "what" in lower_line:
                question = line
            else:
                # Simple fact statement
                if len(line.split()) < 10 and not line.startswith(('But', 'However', 'Therefore')):
                    facts.add(line)

        # Last line is usually the question if not already found
        question = lines[-1] if lines[-1].endswith('?') else ""
        for line in lines:
            if "which" in line.lower() or "what" in line.lower():
                question = line
                break

        return {
            "agents": agents,
            "facts": list(facts),
            "observations": observation_tuples,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply fluid dynamics concepts to model knowledge flow and perspective shifts."""
        agents = structure["agents"]
        facts = structure["facts"]
        observations = structure["observations"]
        question = structure["question"]

        if not agents or not observations:
            # Fallback: use simple belief tracking
            beliefs = track_beliefs(agents, observations) if agents else {}
            computed_answer = self._extract_answer_from_question(question, beliefs)
            return {
                "answer": computed_answer,
                "confidence": 0.5,
                "reasoning": "Simple belief tracking fallback",
                "belief_state": beliefs
            }

        # === FLUID DYNAMICS SCAFFOLD ===
        # Model knowledge as fluid flowing through a network of agents
        # Agents are nodes, communication/observation are pipes
        # Knowledge pressure gradients drive information flow
        # Viscosity (entropy of beliefs) resists rapid perspective shifts

        # Build Bayesian network edges: agent knowledge states influence each other
        edges = []
        for obs in observations:
            agent, fact, known = obs
            # Create edges from world state to agent belief
            edges.append(("World_" + fact.replace(" ", "_"), "Belief_" + agent + "_" + fact.replace(" ", "_")))
            # Connect agents who might communicate (simplified: all agents connected)
            for other_agent in agents:
                if other_agent != agent:
                    edges.append(("Belief_" + agent + "_" + fact.replace(" ", "_"), 
                                 "Belief_" + other_agent + "_" + fact.replace(" ", "_")))

        # Use T1 primitive: track_beliefs to get initial belief distribution
        initial_beliefs = track_beliefs(agents, observations)
        if initial_beliefs is None:
            initial_beliefs = {}

        # Compute entropy of belief states (viscosity analog)
        belief_entropies = []
        for agent, agent_facts in initial_beliefs.items():
            if agent_facts:
                # Simple probability model: P(belief=true) = 0.9 if in set, 0.1 otherwise
                probs = [0.9 if fact in agent_facts else 0.1 for fact in facts]
                ent = entropy(probs)
                belief_entropies.append(ent)
        
        avg_viscosity = sum(belief_entropies) / len(belief_entropies) if belief_entropies else 1.0

        # Use amino acid: build Bayesian network
        bn_model = build_bn(edges, cpd_specs=None)
        
        # Use amino acid: active_trails to find information flow paths
        info_paths = {}
        if bn_model is not None:
            for agent in agents:
                # Find what this agent can infer about others' knowledge
                start_vars = ["Belief_" + agent + "_" + fact.replace(" ", "_") for fact in facts[:2]]
                if start_vars:
                    trails = active_trails(bn_model, start_vars, observed=None)
                    if trails is not None:
                        info_paths[agent] = trails
        else:
            info_paths = {}

        # Use T1 primitive: sally_anne_test for specific perspective-taking
        perspective_results = {}
        # Look for object movement scenarios in observations
        object_moves = []
        for obs in observations:
            if "moves" in obs[1].lower() or "takes" in obs[1].lower():
                # Try to parse object movement
                parts = obs[1].split()
                if len(parts) >= 3:
                    object_moves.append((obs[0], obs[1], obs[2]))

        if len(object_moves) >= 2:
            # Use the first two moves for Sally-Anne test
            who_moved = object_moves[0][0]
            original_loc = object_moves[0][1].split()[-1] if object_moves[0][1].split() else "A"
            new_loc = object_moves[1][1].split()[-1] if object_moves[1][1].split() else "B"
            who_saw = {obs[0] for obs in observations if "sees" in obs[1].lower()}
            
            sat_result = sally_anne_test(who_moved, who_saw, original_loc, new_loc)
            if sat_result:
                perspective_results = sat_result

        # Use T1 primitive: modus_ponens for logical inference
        # Create implication rules from observations
        premises = []
        for obs in observations:
            agent, fact, known = obs
            if known:
                # If agent knows fact, they can potentially infer related facts
                for other_fact in facts:
                    if fact != other_fact and len(fact.split()) < 4:
                        premises.append((f"{agent}_knows_{fact.replace(' ', '_')}", 
                                        f"{agent}_can_infer_{other_fact.replace(' ', '_')}"))

        initial_facts = set()
        for obs in observations:
            if obs[2]:  # known is True
                initial_facts.add(f"{obs[0]}_knows_{obs[1].replace(' ', '_')}")

        inferred = modus_ponens(premises, initial_facts)
        if inferred is None:
            inferred = set()

        # Use amino acid: conditional_query to compute what an agent likely believes
        target_agent = None
        target_query = None
        if "what does" in question.lower() and "know" in question.lower():
            # Extract agent from question
            match = re.search(r'what does ([A-Z][a-z]+(?: [A-Z][a-z]+)*) know', question.lower())
            if match:
                target_agent = match.group(1).title()
                target_query = "knowledge_state"
        
        conditional_prob = None
        if bn_model is not None and target_agent and facts:
            # Query probability that agent knows first fact
            evidence = {}
            for obs in observations:
                if obs[0] == target_agent and obs[2]:
                    evidence["Belief_" + obs[0] + "_" + obs[1].replace(" ", "_")] = 1
            
            if evidence:
                try:
                    conditional_prob = conditional_query(
                        bn_model, 
                        ["Belief_" + target_agent + "_" + facts[0].replace(" ", "_")], 
                        evidence
                    )
                except:
                    conditional_prob = None

        # Use T1 primitive: confidence_from_agreement on multiple reasoning paths
        agreement_scores = []
        # Score 1: From initial beliefs
        if initial_beliefs:
            agreement_scores.append(0.7 if any(len(f) > 0 for f in initial_beliefs.values()) else 0.3)
        # Score 2: From perspective results
        if perspective_results:
            agreement_scores.append(0.8 if len(perspective_results) > 1 else 0.4)
        # Score 3: From inferred facts
        if inferred:
            agreement_scores.append(0.6)
        
        confidence = confidence_from_agreement(agreement_scores) if agreement_scores else 0.5

        # Determine answer based on question type
        computed_answer = self._extract_answer_from_question(question, initial_beliefs)
        
        # If no specific answer found, use most knowledgeable agent
        if not computed_answer and agents:
            # Find agent with most known facts
            agent_knowledge = {}
            for agent in agents:
                known_count = sum(1 for obs in observations if obs[0] == agent and obs[2])
                agent_knowledge[agent] = known_count
            
            if agent_knowledge:
                best_agent = max(agent_knowledge.items(), key=lambda x: x[1])[0]
                computed_answer = best_agent

        if not computed_answer:
            computed_answer = "Unknown"

        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Knowledge flow modeled with viscosity {avg_viscosity:.2f}, information paths: {len(info_paths)}",
            "belief_state": initial_beliefs,
            "conditional_prob": conditional_prob,
            "inferred_facts": inferred
        }

    def _extract_answer_from_question(self, question: str, beliefs: Dict[str, Set[str]]) -> str:
        """Extract likely answer from question text and belief states."""
        if not question:
            return ""
        
        lower_q = question.lower()
        
        # Check for "which agent" questions
        if "which" in lower_q and ("agent" in lower_q or "person" in lower_q):
            if "knows" in lower_q or "believes" in lower_q:
                # Find agent with specific belief
                for agent, agent_beliefs in beliefs.items():
                    if agent_beliefs:
                        return agent
            elif "does not know" in lower_q:
                # Find agent lacking knowledge
                for agent, agent_beliefs in beliefs.items():
                    if not agent_beliefs:
                        return agent
        
        # Check for "what does X know" questions
        match = re.search(r'what does ([A-Z][a-z]+(?: [A-Z][a-z]+)*) (?:know|believe)', question, re.IGNORECASE)
        if match:
            agent = match.group(1)
            if agent in beliefs and beliefs[agent]:
                # Return first fact they know
                return list(beliefs[agent])[0]
            else:
                return "Nothing"
        
        # Check for true/false questions
        if "true" in lower_q or "false" in lower_q:
            # Return the most common belief among agents
            all_beliefs = []
            for agent_beliefs in beliefs.values():
                all_beliefs.extend(list(agent_beliefs))
            
            if all_beliefs:
                from collections import Counter
                most_common = Counter(all_beliefs).most_common(1)[0][0]
                return most_common
        
        return ""

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact or substring match with computed answer
            if computed_answer and computed_answer.lower() in candidate.lower():
                base_score = 1.0
            elif computed_answer and candidate.lower() in computed_answer.lower():
                base_score = 0.9
            else:
                # Fallback: NCD similarity with reasoning text
                base_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
            # Adjust based on confidence
            confidence = reasoning_result.get("confidence", 0.5)
            adjusted_score = base_score * confidence
            
            results.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score,
                "confidence": confidence
            })
        
        return results

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

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        scores = [item["score"] for item in scored]
        if not scores:
            return scored
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score - min_score < 0.001:
            # All scores are essentially equal
            for item in scored:
                item["score"] = 0.5
            return scored
        
        # Normalize to [0, 1] range
        for item in scored:
            item["score"] = (item["score"] - min_score) / (max_score - min_score)
        
        return scored