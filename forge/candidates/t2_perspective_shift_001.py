import re
import zlib
from typing import Dict, List, Any, Tuple, Set

from forge_primitives import (
    track_beliefs,
    sally_anne_test,
    confidence_from_agreement,
    entropy,
    modus_ponens,
    check_transitivity
)
from forge.amino_acids.pysat_acids import check_entailment, detect_paradox
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Relativity x SAT/Constraint Solving - Perspective Shift"""

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
        beliefs = {}  # agent -> set of known facts
        observations = []  # (agent, fact, True/False for knows)
        query = lines[-1] if lines else ""

        # Find agent names (capitalized words that appear as subjects)
        sentences = re.split(r'[.!?]', prompt)
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            # Simple heuristic: agents are often proper nouns before "knows", "believes", "sees"
            agent_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:knows|believes|sees|thinks|observes)', sent)
            if agent_match:
                agent = agent_match.group(1)
                agents.add(agent)
                # Extract the fact known
                fact_part = sent[agent_match.end():].strip()
                # Clean up fact (remove trailing punctuation)
                fact = re.sub(r'[,.!?;:]$', '', fact_part).strip()
                if fact:
                    if agent not in beliefs:
                        beliefs[agent] = set()
                    beliefs[agent].add(fact)
                    observations.append((agent, fact, True))

        # Also extract facts stated as general knowledge (no agent specified)
        general_facts = []
        for sent in sentences:
            if any(agent in sent for agent in agents):
                continue  # Skip sentences mentioning agents
            # Look for declarative statements
            if re.match(r'^[A-Z].* (?:is|are|has|have|can|cannot) .*', sent):
                # Remove question marks
                fact = re.sub(r'\?$', '', sent).strip()
                if fact:
                    general_facts.append(fact)

        return {
            "agents": list(agents),
            "beliefs": beliefs,
            "observations": observations,
            "general_facts": general_facts,
            "query": query,
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply relativistic reasoning: knowledge is frame-dependent, compute invariant truth."""
        agents = structure["agents"]
        observations = structure["observations"]
        general_facts = structure["general_facts"]
        query = structure["query"]

        # Use T1 primitive: track_beliefs to model each agent's knowledge state
        belief_state = track_beliefs(agents, observations)
        if belief_state is None:
            belief_state = {agent: set() for agent in agents}

        # Use T1 primitive: sally_anne_test to model false beliefs if movement is described
        # Look for object movement in prompt
        movement_pattern = r'moved from ([^,]+) to ([^,.!?]+)'
        movement_match = re.search(movement_pattern, structure["raw_prompt"], re.IGNORECASE)
        false_beliefs = {}
        if movement_match:
            original_loc = movement_match.group(1).strip()
            new_loc = movement_match.group(2).strip()
            # Determine who saw the move
            saw_move = set()
            for agent in agents:
                if agent.lower() in structure["raw_prompt"].lower() and 'saw' in structure["raw_prompt"].lower():
                    # Simple heuristic
                    saw_move.add(agent)
            if saw_move:
                false_belief_result = sally_anne_test(
                    who_moved="object",
                    who_saw_move=saw_move,
                    original_location=original_loc,
                    new_location=new_loc
                )
                if false_belief_result:
                    false_beliefs = false_belief_result

        # Use amino acid: encode knowledge as logical constraints and check entailment
        # Build SAT clauses for each agent's knowledge
        all_clauses = []
        variable_map = {}  # fact -> variable index
        next_var = 1

        # Assign variables to facts
        all_facts = set()
        for agent in agents:
            all_facts.update(belief_state.get(agent, set()))
        all_facts.update(general_facts)

        for fact in all_facts:
            variable_map[fact] = next_var
            next_var += 1

        # Encode each agent's knowledge as implications
        for agent in agents:
            agent_facts = belief_state.get(agent, set())
            for fact in agent_facts:
                var = variable_map[fact]
                # Agent knows fact -> fact is true in their frame
                all_clauses.append([var])  # fact must be true

        # Encode general facts as always true (background knowledge)
        for fact in general_facts:
            if fact in variable_map:
                all_clauses.append([variable_map[fact]])

        # Parse query to extract target fact
        query_fact = None
        # Look for "What does X know about Y?" or "Which agent knows Z?"
        query_lower = query.lower()
        for fact in all_facts:
            if fact.lower() in query_lower:
                query_fact = fact
                break

        # If no fact matches, try to extract the questioned fact from query
        if not query_fact:
            # Remove question words
            clean_query = re.sub(r'^(What|Which|Who|Where|When|How|Why)\s+', '', query_lower)
            clean_query = re.sub(r'\?$', '', clean_query).strip()
            # Last few words might be the fact
            words = clean_query.split()
            if len(words) >= 2:
                potential_fact = ' '.join(words[-2:]).capitalize()
                query_fact = potential_fact

        # Use amino acid: check_entailment to see if knowledge implies query
        query_entailed_by = []
        if query_fact and query_fact in variable_map:
            query_var = variable_map[query_fact]
            for agent in agents:
                # Build clauses for this agent's knowledge only
                agent_clauses = []
                agent_facts = belief_state.get(agent, set())
                for fact in agent_facts:
                    if fact in variable_map:
                        agent_clauses.append([variable_map[fact]])
                for fact in general_facts:
                    if fact in variable_map:
                        agent_clauses.append([variable_map[fact]])

                if agent_clauses:
                    # Check if agent's knowledge entails the query fact
                    entailment_result = check_entailment(agent_clauses, [query_var])
                    if entailment_result is True:
                        query_entailed_by.append(agent)

        # Use T1 primitive: confidence_from_agreement on multiple reasoning paths
        # Different "frames" = different subsets of agents
        frame_scores = []
        if query_entailed_by:
            # Score 1: proportion of agents whose knowledge entails the fact
            frame_scores.append(len(query_entailed_by) / max(len(agents), 1))

        # Use T1 primitive: entropy of belief distribution across agents
        belief_counts = {}
        for agent in agents:
            agent_facts = belief_state.get(agent, set())
            if query_fact:
                knows = 1 if query_fact in agent_facts else 0
                belief_counts[agent] = knows

        if belief_counts:
            probs = list(belief_counts.values())
            if len(set(probs)) > 1:
                # Normalize to distribution
                prob_sum = sum(probs)
                if prob_sum > 0:
                    dist = [p / prob_sum for p in probs]
                    belief_entropy = entropy(dist)
                    # Lower entropy = more agreement = higher confidence
                    frame_scores.append(1.0 - min(belief_entropy, 1.0))

        # Use amino acid: detect_paradox in combined knowledge
        combined_clauses = all_clauses.copy()
        paradox_detected = detect_paradox(combined_clauses)
        if paradox_detected is True:
            # Paradox reduces confidence
            confidence_adjustment = 0.5
        else:
            confidence_adjustment = 1.0

        # Compute final confidence
        if frame_scores:
            confidence = confidence_from_agreement(frame_scores)
            if confidence is None:
                confidence = 0.5
            confidence *= confidence_adjustment
        else:
            confidence = 0.5 * confidence_adjustment

        # Determine answer: which agent knows the queried fact?
        computed_answer = None
        if query_entailed_by:
            # If query asks "What does X know?", answer is the fact
            if re.search(r'what does [A-Z]', query_lower):
                computed_answer = query_fact if query_fact else "unknown"
            # If query asks "Which agent knows X?", answer is the agent
            elif re.search(r'which agent', query_lower) and query_entailed_by:
                computed_answer = query_entailed_by[0]
            else:
                # Default: list all agents who know
                computed_answer = ', '.join(query_entailed_by) if query_entailed_by else "none"
        else:
            computed_answer = "none"

        # Use T1 primitive: modus_ponens to derive additional knowledge
        # Extract implication rules from prompt
        implication_rules = []
        for sent in re.split(r'[.!?]', structure["raw_prompt"]):
            if 'if' in sent.lower() and 'then' in sent.lower():
                parts = sent.lower().split('then')
                if len(parts) == 2:
                    antecedent = parts[0].replace('if', '').strip()
                    consequent = parts[1].strip()
                    implication_rules.append((antecedent.capitalize(), consequent.capitalize()))

        if implication_rules and computed_answer not in ["none", "unknown"]:
            # Apply modus ponens starting from known facts
            known_facts = set()
            if computed_answer != "none" and computed_answer in agents:
                known_facts.update(belief_state.get(computed_answer, set()))
            known_facts.update(general_facts)

            derived_facts = modus_ponens(implication_rules, known_facts)
            if derived_facts:
                # Add derived facts to reasoning explanation
                pass  # For trace, not needed for answer

        return {
            "answer": computed_answer,
            "confidence": max(0.0, min(1.0, confidence)),
            "reasoning": f"Knowledge frame analysis: {len(query_entailed_by)} of {len(agents)} agents entail the query.",
            "query_fact": query_fact,
            "entailing_agents": query_entailed_by
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        results = []

        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })

        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence and distribution properties."""
        if not scored:
            return scored

        # Extract raw scores
        raw_scores = [item["raw_score"] for item in scored]
        if not raw_scores:
            return scored

        # Normalize to [0, 1] range
        min_score = min(raw_scores)
        max_score = max(raw_scores)
        if max_score > min_score:
            for item in scored:
                item["score"] = (item["raw_score"] - min_score) / (max_score - min_score)
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