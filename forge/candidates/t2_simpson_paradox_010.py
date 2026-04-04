import re
import zlib
from typing import Dict, List, Any

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, solve_linear_system
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, compare_conditional_marginal, detect_confounders


class ReasoningTool:
    """social_choice_theory x pgmpy_acids - simpson_paradox"""

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
        """Parse prompt to find entities, subgroups, rates, and the question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""

        # Find entity names (capitalized multi-word phrases that appear as categories)
        # These are typically hospital names, drug names, treatment options, etc.
        entity_pattern = r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b'
        all_names = re.findall(entity_pattern, prompt)
        # Filter: names that appear multiple times or near numbers are likely entities
        entity_counts = {}
        for name in all_names:
            entity_counts[name] = entity_counts.get(name, 0) + 1
        entities = [name for name, count in entity_counts.items() 
                   if count > 1 and len(name.split()) <= 3]  # Avoid long phrases

        # Find subgroups (often demographic categories like "Men", "Women", "Young", "Old")
        subgroup_keywords = ["men", "women", "male", "female", "young", "old", 
                            "group a", "group b", "category", "subgroup"]
        subgroups = []
        for line in lines:
            lower_line = line.lower()
            for kw in subgroup_keywords:
                if kw in lower_line:
                    # Extract the actual subgroup name from context
                    words = line.split()
                    for i, w in enumerate(words):
                        if kw in w.lower():
                            if i < len(words) - 1 and words[i+1].istitle():
                                subgroups.append(words[i] + " " + words[i+1])
                            else:
                                subgroups.append(words[i])
                            break

        # Find all percentage values and associate with nearby entities/subgroups
        percentage_pattern = r'(\d+(?:\.\d+)?)%'
        percentages = re.findall(percentage_pattern, prompt)
        rates = [float(p) / 100.0 for p in percentages]

        # Parse lines to build a structured representation
        data_table = []
        current_entity = None
        current_subgroup = None

        for line in lines:
            lower_line = line.lower()
            # Check if this line introduces an entity
            for entity in entities:
                if entity in line:
                    current_entity = entity
                    break
            
            # Check for subgroup mentions
            for sg in subgroups:
                if sg.lower() in lower_line:
                    current_subgroup = sg
                    break

            # Extract percentages from this line
            line_percentages = re.findall(percentage_pattern, line)
            if line_percentages:
                values = [float(p) / 100.0 for p in line_percentages]
                data_table.append({
                    "entity": current_entity,
                    "subgroup": current_subgroup,
                    "values": values,
                    "raw_line": line
                })

        return {
            "entities": entities,
            "subgroups": subgroups,
            "rates": rates,
            "data_table": data_table,
            "question": question,
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply social choice theory: treat subgroups as voters with preferences."""
        entities = structure["entities"]
        subgroups = structure["subgroups"]
        data_table = structure["data_table"]
        rates = structure["rates"]

        if len(entities) < 2 or len(rates) < 4:
            # Not enough data for Simpson's paradox analysis
            return {"answer": "Insufficient data", "confidence": 0.0, "reasoning": "Not enough entities or rates"}

        # PHASE 2A: Build preference profiles using social choice theory
        # Each subgroup's "vote" is based on which entity has higher rate for that subgroup
        subgroup_preferences = {}
        
        for sg in subgroups:
            sg_data = [d for d in data_table if d["subgroup"] and sg.lower() in d["subgroup"].lower()]
            if len(sg_data) >= 2:  # Need at least two entities for comparison
                entity_rates = {}
                for d in sg_data:
                    if d["entity"] and d["values"]:
                        entity_rates[d["entity"]] = d["values"][0] if d["values"] else 0.0
                
                if len(entity_rates) >= 2:
                    # Rank entities by rate for this subgroup (higher is better)
                    ranked = sorted(entity_rates.items(), key=lambda x: x[1], reverse=True)
                    subgroup_preferences[sg] = [e[0] for e in ranked]

        # PHASE 2B: Check for Simpson's paradox using Bayesian network
        # Build a simple BN: Subgroup -> Entity -> SuccessRate
        edges = []
        for sg in subgroups:
            for e in entities:
                edges.append((sg, e))  # Subgroup influences entity choice
                edges.append((e, "SuccessRate"))  # Entity influences success

        # Create CPDs based on extracted rates
        cpd_specs = {}
        
        # For each entity, compute average success rate across subgroups
        entity_success = {}
        for e in entities:
            e_data = [d for d in data_table if d["entity"] == e and d["values"]]
            if e_data:
                avg_rate = sum([d["values"][0] for d in e_data if d["values"]]) / len(e_data)
                entity_success[e] = avg_rate

        # Build CPD for SuccessRate given Entity
        if entity_success:
            # Normalize to create a probability distribution
            total = sum(entity_success.values())
            if total > 0:
                for e, rate in entity_success.items():
                    cpd_specs[e] = {"SuccessRate": [rate/total, 1 - rate/total]}

        # Use T1 primitive: entropy of entity success rates
        success_rates = list(entity_success.values())
        if success_rates:
            entropy_val = entropy([r/sum(success_rates) for r in success_rates] if sum(success_rates) > 0 else [1/len(success_rates)]*len(success_rates))
        else:
            entropy_val = 1.0

        # Build Bayesian network
        bn_model = None
        paradox_detected = False
        confounder_info = None
        
        try:
            bn_model = build_bn(edges, cpd_specs if cpd_specs else None)
        except Exception:
            bn_model = None

        # Use amino acid: detect confounders
        if bn_model and len(entities) >= 2:
            try:
                confounders = detect_confounders(bn_model, entities[0], entities[1])
                confounder_info = list(confounders) if confounders else []
            except Exception:
                confounder_info = []

        # Use amino acid: compare conditional vs marginal for Simpson's paradox check
        reversal_evidence = []
        if bn_model and subgroups and len(entities) >= 2:
            for sg in subgroups[:2]:  # Check first two subgroups
                try:
                    # Compare P(Success|Entity=E1, Subgroup=SG) vs P(Success|Entity=E2, Subgroup=SG)
                    for i, e1 in enumerate(entities):
                        for e2 in entities[i+1:]:
                            comp1 = compare_conditional_marginal(bn_model, "SuccessRate", e1, "high")
                            comp2 = compare_conditional_marginal(bn_model, "SuccessRate", e2, "high")
                            if comp1 and comp2:
                                # Check if ordering reverses between subgroups
                                sg1_pref = subgroup_preferences.get(sg, [])
                                if len(sg1_pref) >= 2:
                                    e1_pos = sg1_pref.index(e1) if e1 in sg1_pref else -1
                                    e2_pos = sg1_pref.index(e2) if e2 in sg1_pref else -1
                                    if e1_pos >= 0 and e2_pos >= 0 and e1_pos != e2_pos:
                                        # This subgroup has a preference ordering
                                        reversal_evidence.append({
                                            "subgroup": sg,
                                            "preference": sg1_pref,
                                            "entities": [e1, e2]
                                        })
                except Exception:
                    continue

        # PHASE 2C: Aggregate preferences using social choice (Borda count)
        borda_scores = {e: 0 for e in entities}
        for sg, prefs in subgroup_preferences.items():
            for i, entity in enumerate(prefs):
                borda_scores[entity] = borda_scores.get(entity, 0) + (len(prefs) - i - 1)

        # Use T1 primitive: confidence from agreement (variance in subgroup preferences)
        if subgroup_preferences:
            # Create score vectors for each entity across subgroups
            entity_scores = []
            for e in entities:
                scores = []
                for sg, prefs in subgroup_preferences.items():
                    if e in prefs:
                        scores.append(len(prefs) - prefs.index(e) - 1)
                    else:
                        scores.append(0)
                if scores:
                    entity_scores.append(scores)
            
            if entity_scores:
                # Flatten scores for confidence calculation
                flat_scores = [score for sublist in entity_scores for score in sublist]
                if flat_scores:
                    confidence = confidence_from_agreement(flat_scores)
                else:
                    confidence = 0.5
            else:
                confidence = 0.5
        else:
            confidence = 0.3

        # PHASE 2D: Determine if Simpson's paradox occurs
        # Paradox occurs if aggregated ranking differs from all subgroup rankings
        aggregated_ranking = sorted(entities, key=lambda e: borda_scores.get(e, 0), reverse=True)
        
        paradox = False
        if subgroup_preferences and len(aggregated_ranking) >= 2:
            # Check if any subgroup has opposite top preference
            top_aggregated = aggregated_ranking[0]
            for sg, prefs in subgroup_preferences.items():
                if prefs and prefs[0] != top_aggregated:
                    paradox = True
                    break

        # Use T1 primitive: Bayesian update on paradox confidence
        prior_paradox = 0.3
        likelihood_paradox = 0.8 if paradox else 0.2
        paradox_posterior = bayesian_update(prior_paradox, likelihood_paradox)
        
        # Use T1 primitive: solve linear system for final scores
        # Create a simple system: entity_score = base + subgroup_effect
        if entities and subgroups:
            try:
                # Build matrix: each equation is entity_score = sum of subgroup contributions
                A = []
                b = []
                for e in entities[:3]:  # Use first 3 entities for stability
                    row = [1 if sg in subgroup_preferences and e in subgroup_preferences.get(sg, []) else 0 
                          for sg in subgroups[:3]]  # Use first 3 subgroups
                    if len(row) > 0:
                        A.append(row + [1])  # Add intercept
                        b.append(borda_scores.get(e, 0))
                
                if A and len(A) >= 2:
                    solution = solve_linear_system(A, b)
                    if solution:
                        # Solution gives weights for subgroups
                        linear_weights = solution
                    else:
                        linear_weights = []
                else:
                    linear_weights = []
            except Exception:
                linear_weights = []
        else:
            linear_weights = []

        # Determine final answer
        if paradox and aggregated_ranking:
            # When paradox detected, the "actually better" entity is the one that wins
            # in subgroup analysis but loses in aggregate (or vice versa)
            # We return the entity that is top in aggregated ranking (post-paradox correction)
            computed_answer = aggregated_ranking[0]
            reasoning_text = f"Simpson's paradox detected (p={paradox_posterior:.2f}). Social choice aggregation via Borda count selects {computed_answer} after accounting for subgroup preferences. Confounders: {confounder_info}. Entropy of rates: {entropy_val:.3f}."
        elif aggregated_ranking:
            computed_answer = aggregated_ranking[0]
            reasoning_text = f"No strong Simpson's paradox. Social choice aggregation selects {computed_answer} based on subgroup preferences. Confidence: {confidence:.2f}. Linear weights: {linear_weights}."
        else:
            computed_answer = "Cannot determine"
            reasoning_text = "Insufficient data for social choice analysis."

        return {
            "answer": computed_answer,
            "confidence": min(0.95, confidence * (1 + paradox_posterior if paradox else 1)),
            "reasoning": reasoning_text,
            "paradox_detected": paradox,
            "paradox_confidence": paradox_posterior,
            "aggregated_ranking": aggregated_ranking,
            "subgroup_preferences": subgroup_preferences
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate text
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity between reasoning text and candidate
                base_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
            # Adjust based on paradox detection confidence
            if reasoning_result.get("paradox_detected", False):
                paradox_boost = reasoning_result.get("paradox_confidence", 0.5)
                # Candidates that mention paradox-related terms get bonus
                paradox_terms = ["reverse", "paradox", "confound", "aggregat", "subgroup"]
                if any(term in candidate.lower() for term in paradox_terms):
                    base_score = min(1.0, base_score * (1 + 0.2 * paradox_boost))
            
            results.append({
                "candidate": candidate,
                "score": base_score,
                "computed_answer": computed_answer
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        scores = [item["score"] for item in scored]
        if max(scores) - min(scores) < 0.01:
            # All scores too similar, add small differentiation
            for i, item in enumerate(scored):
                item["score"] = item["score"] + (i * 0.001)
        
        # Ensure scores are in [0, 1]
        for item in scored:
            item["score"] = max(0.0, min(1.0, item["score"]))
        
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