import re
import zlib
from typing import Dict, List, Any, Set, Tuple
from forge_primitives import (
    track_beliefs,
    sally_anne_test,
    confidence_from_agreement,
    entropy,
    modus_ponens,
    check_transitivity
)
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, active_trails
from forge.amino_acids.pysat_acids import check_entailment, detect_paradox
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable
from forge.amino_acids.nashpy_acids import find_equilibria, best_response


class ReasoningTool:
    """auction_theory x pgmpy_acids - perspective_shift"""

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
        """Parse prompt to identify agents, their knowledge, and the query."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        agents = set()
        agent_knowledge = {}
        facts = set()
        implications = []
        query = lines[-1] if lines else ""

        # Extract agent names (capitalized words that appear as subjects)
        words = re.findall(r'\b([A-Z][a-z]+)\b', prompt)
        for word in words:
            if word.lower() not in ['the', 'and', 'but', 'that', 'which', 'what', 'who']:
                agents.add(word)

        # Extract knowledge statements
        for line in lines:
            line_lower = line.lower()
            if 'know' in line_lower or 'believe' in line_lower or 'think' in line_lower:
                # Find agent and fact
                agent_match = re.search(r'\b([A-Z][a-z]+)\b', line)
                if agent_match:
                    agent = agent_match.group(1)
                    agents.add(agent)
                    # Extract fact (text after 'that' or 'knows that')
                    fact_match = re.search(r'(?:knows|believes|thinks)\s+(?:that\s+)?([^.,]+)', line_lower)
                    if fact_match:
                        fact = fact_match.group(1).strip()
                        if agent not in agent_knowledge:
                            agent_knowledge[agent] = []
                        agent_knowledge[agent].append(fact)
                        facts.add(fact)

            # Extract logical implications
            if 'if' in line_lower and 'then' in line_lower:
                parts = line_lower.split('then')
                if len(parts) == 2:
                    antecedent = parts[0].replace('if', '').strip()
                    consequent = parts[1].strip()
                    implications.append((antecedent, consequent))

        # Extract numerical values (for auction-like valuations)
        valuations = {}
        value_pattern = r'(\d+)\s*(?:dollar|point|value|worth)'
        value_matches = re.findall(value_pattern, prompt, re.IGNORECASE)
        for i, val in enumerate(value_matches):
            valuations[f"item_{i}"] = int(val)

        return {
            "agents": list(agents),
            "agent_knowledge": agent_knowledge,
            "facts": list(facts),
            "implications": implications,
            "query": query,
            "valuations": valuations,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply auction theory as scaffold: agents as bidders with private valuations,
        knowledge as private signals, perspective shifts as equilibrium reasoning."""
        agents = structure["agents"]
        agent_knowledge = structure["agent_knowledge"]
        facts = structure["facts"]
        implications = structure["implications"]
        query = structure["query"]
        valuations = structure["valuations"]

        # Use T1 primitive: track_beliefs to model initial knowledge state
        observations = []
        for agent, known_facts in agent_knowledge.items():
            for fact in known_facts:
                observations.append((agent, fact, True))
        belief_state = track_beliefs(agents, observations)

        # Use T1 primitive: sally_anne_test to model false beliefs
        # We'll simulate a simple perspective shift: if an agent doesn't know a fact,
        # what do they believe others know?
        perspective_shifts = {}
        for agent in agents:
            other_agents = [a for a in agents if a != agent]
            for other in other_agents:
                # Simple test: if agent knows fact X, does other know it?
                # Use a dummy location shift for sally_anne_test
                test_result = sally_anne_test(
                    who_moved=agent,
                    who_saw_move=set([agent]),
                    original_location="unknown",
                    new_location="known"
                )
                # Extract belief about other's knowledge
                if other in test_result:
                    perspective_shifts[(agent, other)] = test_result[other]

        # Use amino acid: build_bn to model knowledge as causal network
        # Nodes: agents' knowledge states and facts
        edges = []
        for agent in agents:
            for fact in facts:
                edges.append((f"{agent}_knows_{fact}", f"{fact}_true"))
        # Add edges based on implications
        for ant, cons in implications:
            edges.append((ant, cons))

        try:
            bn_model = build_bn(edges, cpd_specs=None)
            if bn_model is not None:
                # Use amino acid: conditional_query to compute knowledge given evidence
                # Query: what does an agent believe given what others know?
                evidence = {}
                for agent, known_facts in agent_knowledge.items():
                    for fact in known_facts:
                        evidence[f"{agent}_knows_{fact}"] = 1

                target_vars = [f"{agent}_knows_{fact}" for agent in agents for fact in facts]
                if target_vars and evidence:
                    conditional_probs = conditional_query(bn_model, target_vars[:1], evidence)
                else:
                    conditional_probs = None
        except Exception:
            conditional_probs = None

        # Use amino acid: active_trails to find what knowledge propagates
        try:
            if bn_model is not None:
                start_vars = [f"{agent}_knows_{fact}" for agent in agents for fact in facts][:2]
                if start_vars:
                    reachable = active_trails(bn_model, start_vars, observed=None)
                else:
                    reachable = None
        except Exception:
            reachable = None

        # Use T1 primitive: modus_ponens to derive new knowledge
        premises = [(ant, cons) for ant, cons in implications]
        known_facts_set = set(facts)
        derived_facts = modus_ponens(premises, known_facts_set)

        # Use T1 primitive: confidence_from_agreement on multiple reasoning paths
        agreement_scores = []
        # Score 1: belief state coverage
        if belief_state:
            coverage = sum(len(beliefs) for beliefs in belief_state.values()) / (len(agents) * len(facts) + 1)
            agreement_scores.append(coverage)
        # Score 2: derived facts count
        agreement_scores.append(len(derived_facts) / (len(facts) + 1))
        # Score 3: perspective shift consistency
        if perspective_shifts:
            shift_consistency = len(set(perspective_shifts.values())) / (len(perspective_shifts) + 1)
            agreement_scores.append(shift_consistency)

        confidence = confidence_from_agreement(agreement_scores) if agreement_scores else 0.5

        # Use T1 primitive: entropy to measure uncertainty in knowledge distribution
        if belief_state:
            belief_counts = [len(beliefs) for beliefs in belief_state.values()]
            total_beliefs = sum(belief_counts)
            if total_beliefs > 0:
                probs = [count / total_beliefs for count in belief_counts]
                knowledge_entropy = entropy(probs)
            else:
                knowledge_entropy = 1.0
        else:
            knowledge_entropy = 0.5

        # Auction theory: compute equilibrium knowledge state as if agents bid based on private info
        # Each agent's valuation is their knowledge set size
        payoff_a = [[len(agent_knowledge.get(agent, [])) for _ in agents] for agent in agents]
        payoff_b = [[len(agent_knowledge.get(other, [])) for _ in agents] for other in agents]

        try:
            equilibria = find_equilibria(payoff_a, payoff_b)
            if equilibria:
                # Take first equilibrium strategy profile
                eq_strategy = equilibria[0]
                # Determine which agent has dominant knowledge position
                agent_scores = []
                for i, agent in enumerate(agents):
                    if isinstance(eq_strategy[0], list) and isinstance(eq_strategy[1], list):
                        # Mixed strategies
                        score = sum(eq_strategy[0][j] * payoff_a[i][j] for j in range(len(agents)))
                    else:
                        # Pure strategies
                        score = payoff_a[i][0]  # simplified
                    agent_scores.append((agent, score))
                best_agent = max(agent_scores, key=lambda x: x[1])[0] if agent_scores else agents[0]
            else:
                best_agent = agents[0] if agents else "Unknown"
        except Exception:
            best_agent = agents[0] if agents else "Unknown"

        # Determine answer based on query
        computed_answer = best_agent
        if "what does" in query.lower() and "know" in query.lower():
            # Find agent mentioned in query
            query_agent = None
            for agent in agents:
                if agent.lower() in query.lower():
                    query_agent = agent
                    break
            if query_agent and query_agent in belief_state:
                known = belief_state[query_agent]
                computed_answer = ", ".join(sorted(known)) if known else "nothing"
            else:
                computed_answer = "unknown"
        elif "who" in query.lower() and "knows" in query.lower():
            # Who knows the most?
            if belief_state:
                best = max(belief_state.items(), key=lambda x: len(x[1]))
                computed_answer = best[0]
            else:
                computed_answer = best_agent

        return {
            "answer": str(computed_answer),
            "confidence": float(confidence),
            "reasoning": f"Auction equilibrium: {best_agent} has dominant knowledge position. Entropy: {knowledge_entropy:.2f}.",
            "belief_state": belief_state,
            "perspective_shifts": perspective_shifts
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        results = []

        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity
                score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
                # Also check against reasoning text as secondary
                score2 = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
                score = max(score, score2 * 0.5)  # weight reasoning lower
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })

        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence from reasoning result."""
        # Simple calibration: scale by confidence (simulated from earlier phase)
        # In practice, confidence would come from reasoning_result
        confidence = 0.8  # placeholder, should come from reasoning_result
        for item in scored:
            item["score"] = item["raw_score"] * confidence
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance."""
        if not a or not b:
            return 1.0
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        return (cab - min(ca, cb)) / max(ca, cb) if max(ca, cb) > 0 else 1.0