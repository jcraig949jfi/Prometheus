import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    track_beliefs,
    solve_sat,
    topological_sort
)
from forge.amino_acids.pysat_acids import check_entailment
from forge.amino_acids.nashpy_acids import find_equilibria


class ReasoningTool:
    """complexity_theory x pysat_acids - strategic_deception"""

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
        """Extract agents, statements, and relationships from the prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find agent names (capitalized words that appear multiple times)
        words = re.findall(r'\b[A-Z][a-z]+\b', prompt)
        from collections import Counter
        word_counts = Counter(words)
        agents = [word for word, count in word_counts.items() if count > 1 and word not in ['The', 'A', 'An', 'In', 'At', 'On']]
        
        # Extract statements and their truth values
        statements = []
        truth_pattern = r'(says|claims|states|asserts|tells) (that )?(.*?)(?=\.|,| but| however|$)'
        for line in lines:
            matches = re.findall(truth_pattern, line, re.IGNORECASE)
            for match in matches:
                statement_text = match[2].strip()
                if statement_text:
                    # Determine if statement contains negation
                    is_negative = any(word in statement_text.lower() for word in ['not', 'never', 'false', 'no ', "doesn't", "isn't"])
                    statements.append({
                        'text': statement_text,
                        'negative': is_negative,
                        'source': self._find_source_agent(line, agents)
                    })
        
        # Extract relationships (who knows what about whom)
        relationships = []
        know_pattern = r'(\w+) (knows|believes|thinks) (that )?(.*?)(?=\.|,|$)'
        for line in lines:
            matches = re.findall(know_pattern, line, re.IGNORECASE)
            for match in matches:
                knower = match[0]
                known_content = match[3]
                if knower in agents:
                    relationships.append((knower, known_content))
        
        return {
            'agents': agents,
            'statements': statements,
            'relationships': relationships,
            'question': question,
            'raw': prompt
        }

    def _find_source_agent(self, line: str, agents: List[str]) -> str:
        """Find which agent made a statement in a line."""
        for agent in agents:
            if agent in line:
                return agent
        return ""

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use complexity theory concepts (NP-hardness, strategic equilibria) to model deception."""
        agents = structure['agents']
        statements = structure['statements']
        relationships = structure['relationships']
        question = structure['question']
        
        # Complexity theory scaffold: Model strategic deception as a SAT game
        # where each agent's statements create constraints, and we find equilibria
        
        # 1. Build logical constraints from statements
        clauses = []
        var_map = {}
        var_counter = 1
        
        for stmt in statements:
            # Create variable for each statement
            if stmt['text'] not in var_map:
                var_map[stmt['text']] = var_counter
                var_counter += 1
            
            var = var_map[stmt['text']]
            # If statement is negative, use negative literal
            if stmt['negative']:
                clauses.append([-var])
            else:
                clauses.append([var])
        
        # 2. Use SAT solving to check consistency (NP-complete problem - complexity theory)
        sat_result = solve_sat(clauses, len(var_map))
        
        # 3. Model agent beliefs using track_beliefs primitive
        observations = []
        for stmt in statements:
            if stmt['source']:
                agent = stmt['source']
                fact = stmt['text']
                # Agent believes their own statement
                observations.append((agent, fact, True))
        
        belief_state = track_beliefs(agents, observations)
        
        # 4. Compute entropy of belief distributions (complexity theory: information entropy)
        belief_entropies = {}
        for agent in agents:
            if agent in belief_state:
                beliefs = list(belief_state[agent])
                # Create probability distribution over possible belief states
                if beliefs:
                    # Simple uniform distribution for demonstration
                    probs = [1.0/len(beliefs)] * len(beliefs)
                    belief_entropies[agent] = entropy(probs)
                else:
                    belief_entropies[agent] = 0.0
        
        # 5. Use topological sort to find deception hierarchy
        deception_edges = []
        for stmt1 in statements:
            for stmt2 in statements:
                if stmt1['source'] and stmt2['source'] and stmt1['source'] != stmt2['source']:
                    # If agent1's statement contradicts agent2's statement
                    if self._statements_contradict(stmt1, stmt2):
                        deception_edges.append((stmt1['source'], stmt2['source']))
        
        hierarchy = topological_sort(deception_edges)
        
        # 6. Model as game theory: find Nash equilibria in deception game
        # Create payoff matrix based on statement consistency
        payoff_a = []
        payoff_b = []
        
        if len(agents) >= 2:
            # Simplified 2-agent game for demonstration
            agent1, agent2 = agents[0], agents[1] if len(agents) > 1 else agents[0]
            
            # Count consistent vs inconsistent statements for each agent
            agent1_consistent = sum(1 for stmt in statements 
                                  if stmt['source'] == agent1 and sat_result and 
                                  ((stmt['negative'] and sat_result.get(var_map[stmt['text']], False) == False) or
                                   (not stmt['negative'] and sat_result.get(var_map[stmt['text']], False) == True)))
            agent2_consistent = sum(1 for stmt in statements 
                                  if stmt['source'] == agent2 and sat_result and 
                                  ((stmt['negative'] and sat_result.get(var_map[stmt['text']], False) == False) or
                                   (not stmt['negative'] and sat_result.get(var_map[stmt['text']], False) == True)))
            
            # Payoffs based on consistency (higher is better)
            payoff_a = [[agent1_consistent, -agent1_consistent], 
                       [-agent1_consistent, agent1_consistent]]
            payoff_b = [[agent2_consistent, -agent2_consistent], 
                       [-agent2_consistent, agent2_consistent]]
            
            equilibria = find_equilibria(payoff_a, payoff_b) if payoff_a and payoff_b else []
        else:
            equilibria = []
        
        # 7. Use check_entailment to find logical consequences
        # Create premise clauses from all statements
        premise_clauses = []
        for stmt in statements:
            if stmt['text'] in var_map:
                var = var_map[stmt['text']]
                if stmt['negative']:
                    premise_clauses.append([-var])
                else:
                    premise_clauses.append([var])
        
        # Check if deception is entailed (simplified: check if "someone is lying" is entailed)
        deception_var = var_counter
        conclusion_clause = [deception_var]  # Variable representing "deception exists"
        
        # Add relationship between inconsistency and deception
        if sat_result is None:  # Inconsistent statements imply deception
            premise_clauses.append([-deception_var])  # ¬deception → contradiction
        else:
            premise_clauses.append([deception_var])   # deception → consistent
        
        entailment_result = check_entailment(premise_clauses, conclusion_clause)
        
        # 8. Bayesian update on deception probability
        prior_deception = 0.3  # Base rate assumption
        evidence_strength = 0.7 if entailment_result else 0.3
        deception_prob = bayesian_update(prior_deception, evidence_strength)
        
        # 9. Determine which agent is most deceptive
        deceptive_agent = None
        if hierarchy:
            # In deception hierarchy, earlier nodes deceive later ones
            deceptive_agent = hierarchy[0] if hierarchy else None
        elif belief_entropies:
            # Agent with highest entropy of beliefs might be deceptive
            deceptive_agent = max(belief_entropies.items(), key=lambda x: x[1])[0]
        elif agents:
            deceptive_agent = agents[0]
        
        # 10. Compute confidence from multiple reasoning paths
        confidence_scores = []
        if deceptive_agent:
            confidence_scores.append(deception_prob)
        if belief_entropies and deceptive_agent in belief_entropies:
            confidence_scores.append(belief_entropies[deceptive_agent])
        if sat_result is not None:
            consistency_score = 1.0 if sat_result else 0.0
            confidence_scores.append(consistency_score)
        
        confidence = confidence_from_agreement(confidence_scores) if confidence_scores else 0.5
        
        # Determine answer based on question
        computed_answer = ""
        if "who" in question.lower() and deceptive_agent:
            computed_answer = deceptive_agent
        elif "deceptive" in question.lower() or "lying" in question.lower():
            computed_answer = "Yes" if deception_prob > 0.5 else "No"
        elif deceptive_agent:
            computed_answer = deceptive_agent
        else:
            computed_answer = "Unknown"
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "deception_prob": deception_prob,
            "deceptive_agent": deceptive_agent,
            "hierarchy": hierarchy,
            "entropies": belief_entropies,
            "equilibria": equilibria,
            "entailment": entailment_result
        }

    def _statements_contradict(self, stmt1: Dict, stmt2: Dict) -> bool:
        """Check if two statements logically contradict."""
        text1 = stmt1['text'].lower()
        text2 = stmt2['text'].lower()
        
        # Simple contradiction detection
        negations = ['not', 'never', 'false', 'no ']
        for neg in negations:
            if neg in text1 and neg not in text2:
                # Check if they're about the same subject
                words1 = set(text1.split())
                words2 = set(text2.split())
                common = words1.intersection(words2)
                if len(common) > 2:  # Enough common words to be about same topic
                    return True
        return False

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
        
        # Simple min-max normalization
        scores = [item["score"] for item in scored]
        if max(scores) > min(scores):
            for item in scored:
                item["score"] = (item["score"] - min(scores)) / (max(scores) - min(scores))
        else:
            for item in scored:
                item["score"] = 0.5
        
        return scored