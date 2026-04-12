import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, topological_sort
from forge.amino_acids.pgmpy_acids import compare_conditional_marginal, detect_confounders


class ReasoningTool:
    """Graph theory x pgmpy_acids - simpson_paradox"""

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
        """Extract entities, subgroups, rates, and question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find entity names (capitalized multi-word phrases that appear before numbers)
        entity_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        entities = {}
        subgroups = {}
        current_entity = None
        current_subgroup = None
        
        for line in lines:
            # Look for entity mentions
            entity_matches = re.findall(entity_pattern, line)
            for ent in entity_matches:
                if ent not in ["Hospital", "Drug", "Treatment", "Group"]:  # Filter generic terms
                    if ent not in entities:
                        entities[ent] = {"rates": [], "subgroups": {}}
                    current_entity = ent
            
            # Look for subgroup indicators
            if "subgroup" in line.lower() or "group" in line.lower():
                subgroup_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+subgroup', line, re.IGNORECASE)
                if subgroup_match:
                    current_subgroup = subgroup_match.group(1)
                    if current_subgroup not in subgroups:
                        subgroups[current_subgroup] = {"entities": {}}
            
            # Extract percentages
            percentages = re.findall(r'(\d+(?:\.\d+)?)%', line)
            if percentages and current_entity:
                rates = [float(p) / 100.0 for p in percentages]
                if current_subgroup:
                    if current_subgroup not in entities[current_entity]["subgroups"]:
                        entities[current_entity]["subgroups"][current_subgroup] = []
                    entities[current_entity]["subgroups"][current_subgroup].extend(rates)
                else:
                    entities[current_entity]["rates"].extend(rates)
        
        # Clean up: ensure each entity has aggregated and subgroup rates
        for entity, data in entities.items():
            if data["rates"] and len(data["rates"]) >= 2:
                # Assume first is overall, rest are subgroup aggregates
                data["overall_rate"] = data["rates"][0]
                if len(data["rates"]) > 1:
                    data["aggregated_subgroup_rate"] = sum(data["rates"][1:]) / len(data["rates"][1:])
            
            # Compute average for each subgroup
            for subgroup, rates in data["subgroups"].items():
                if rates:
                    data["subgroups"][subgroup] = sum(rates) / len(rates)
        
        return {
            "entities": entities,
            "subgroups": list(subgroups.keys()),
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use graph theory concepts to analyze Simpson's paradox."""
        entities = structure["entities"]
        subgroups = structure["subgroups"]
        
        if len(entities) < 2 or len(subgroups) < 2:
            # Fallback: simple comparison
            computed_answer = self._simple_fallback(entities)
            return {
                "answer": computed_answer,
                "confidence": 0.5,
                "reasoning": "Insufficient data for full Simpson's paradox analysis"
            }
        
        # Build a bipartite graph: entities ↔ subgroups
        # Nodes: all entities + all subgroups
        # Edges: entity-subgroup if subgroup data exists
        edges = []
        for entity in entities:
            for subgroup in entities[entity].get("subgroups", {}):
                edges.append((entity, subgroup))
        
        # Use topological_sort to find ordering (graph theory primitive)
        # This helps identify hierarchical structure
        try:
            sorted_nodes = topological_sort(edges)
            if sorted_nodes is None:
                # Graph has cycles, use entity order
                sorted_nodes = list(entities.keys()) + subgroups
        except Exception:
            sorted_nodes = list(entities.keys()) + subgroups
        
        # Build Bayesian network for causal analysis
        # Structure: Subgroup → Entity (subgroup influences entity's rate)
        bn_edges = []
        for subgroup in subgroups:
            for entity in entities:
                if subgroup in entities[entity].get("subgroups", {}):
                    bn_edges.append((subgroup, entity))
        
        # Create simple CPDs from extracted data
        cpd_specs = {}
        for entity in entities:
            if bn_edges:  # Only if we have edges
                # Get all parent subgroups
                parents = [sg for sg in subgroups if (sg, entity) in bn_edges]
                if parents:
                    # Create simple CPD based on extracted rates
                    parent_states = len(parents)
                    cpd_values = []
                    
                    # Use entropy to measure uncertainty in subgroup rates (primitive)
                    subgroup_rates = []
                    for sg in parents:
                        rate = entities[entity]["subgroups"].get(sg, 0.5)
                        subgroup_rates.append(rate)
                    
                    if subgroup_rates:
                        rate_entropy = entropy(subgroup_rates)
                        # Higher entropy → more uncertainty → flatter distribution
                        base_prob = 0.5
                        if rate_entropy > 0.5:
                            cpd_values = [[0.4, 0.6]]  # Favor entity
                        else:
                            cpd_values = [[0.6, 0.4]]  # Slightly favor entity
                        
                        cpd_specs[entity] = {
                            "variable": entity,
                            "variable_card": 2,
                            "evidence": parents,
                            "evidence_card": [2] * len(parents),
                            "values": cpd_values
                        }
        
        # Use amino acid to detect Simpson's paradox
        paradox_detected = False
        better_entity = None
        
        if bn_edges and cpd_specs:
            try:
                # Build the Bayesian network
                from forge.amino_acids.pgmpy_acids import build_bn
                model = build_bn(bn_edges, cpd_specs)
                
                # Compare conditional vs marginal for each entity
                for entity in entities:
                    if entity in cpd_specs:
                        # Use amino acid to check for paradox
                        result = compare_conditional_marginal(
                            model, 
                            target=entity,
                            condition_var=subgroups[0] if subgroups else None,
                            condition_val=1
                        )
                        
                        if result and isinstance(result, dict):
                            # Check if conditioning changes the distribution significantly
                            if "difference" in result and abs(result["difference"]) > 0.1:
                                paradox_detected = True
                                
                                # Use bayesian_update to refine confidence (primitive)
                                prior = 0.5
                                likelihood = abs(result["difference"])
                                posterior = bayesian_update(prior, likelihood)
                                
                                if posterior > 0.5:
                                    better_entity = entity
                                    break
            except Exception:
                # Fall through to simpler analysis
                pass
        
        # If amino acid failed or no paradox detected, use T1 primitives
        if better_entity is None:
            better_entity = self._analyze_with_primitives(entities, subgroups, sorted_nodes)
        
        # Compute confidence using multiple metrics
        confidence_scores = []
        
        # 1. Confidence from agreement between different analysis methods
        methods_results = []
        
        # Method A: Direct rate comparison
        if all("overall_rate" in entities[e] for e in entities):
            best_direct = max(entities.keys(), 
                            key=lambda e: entities[e].get("overall_rate", 0))
            methods_results.append(1.0 if best_direct == better_entity else 0.0)
        
        # Method B: Subgroup-weighted comparison
        subgroup_weighted = {}
        for entity in entities:
            if "subgroups" in entities[entity]:
                rates = list(entities[entity]["subgroups"].values())
                if rates:
                    subgroup_weighted[entity] = sum(rates) / len(rates)
        
        if subgroup_weighted:
            best_weighted = max(subgroup_weighted.keys(), 
                              key=lambda e: subgroup_weighted[e])
            methods_results.append(1.0 if best_weighted == better_entity else 0.0)
        
        # Use confidence_from_agreement primitive
        if methods_results:
            confidence = confidence_from_agreement(methods_results)
        else:
            confidence = 0.7 if paradox_detected else 0.5
        
        return {
            "answer": better_entity,
            "confidence": confidence,
            "paradox_detected": paradox_detected,
            "reasoning": f"Simpson's paradox {'detected' if paradox_detected else 'not detected'}. Better entity determined through graph analysis."
        }

    def _analyze_with_primitives(self, entities: Dict, subgroups: List[str], 
                                sorted_nodes: List[str]) -> str:
        """Analyze using T1 primitives when amino acids fail."""
        # Strategy: Compare entities based on subgroup consistency
        entity_scores = {}
        
        for entity in entities:
            score = 0.0
            
            # Check if entity has subgroup data
            if "subgroups" in entities[entity]:
                subgroup_rates = list(entities[entity]["subgroups"].values())
                
                if subgroup_rates:
                    # Use entropy to measure consistency (primitive)
                    consistency = 1.0 - entropy(subgroup_rates)
                    score += consistency * 0.5
                    
                    # Compare with overall rate if available
                    if "overall_rate" in entities[entity]:
                        avg_subgroup = sum(subgroup_rates) / len(subgroup_rates)
                        # Higher is better
                        if avg_subgroup > entities[entity]["overall_rate"]:
                            score += 0.3
                        elif avg_subgroup < entities[entity]["overall_rate"]:
                            score -= 0.3
            
            # Position in topological sort matters (graph theory)
            if entity in sorted_nodes:
                idx = sorted_nodes.index(entity)
                # Earlier in sort (more fundamental) gets bonus
                position_score = 1.0 - (idx / len(sorted_nodes))
                score += position_score * 0.2
            
            entity_scores[entity] = score
        
        # Return entity with highest score
        if entity_scores:
            return max(entity_scores.keys(), key=lambda e: entity_scores[e])
        else:
            # Last resort: first entity
            return list(entities.keys())[0] if entities else "Unknown"

    def _simple_fallback(self, entities: Dict) -> str:
        """Simple fallback when data is insufficient."""
        if not entities:
            return "Unknown"
        
        # Try to find entity with highest overall rate
        for entity in entities:
            if "overall_rate" in entities[entity]:
                return max(entities.keys(), 
                         key=lambda e: entities[e].get("overall_rate", 0))
        
        # Try to find entity with highest subgroup average
        entity_avgs = {}
        for entity in entities:
            if "subgroups" in entities[entity]:
                rates = list(entities[entity]["subgroups"].values())
                if rates:
                    entity_avgs[entity] = sum(rates) / len(rates)
        
        if entity_avgs:
            return max(entity_avgs.keys(), key=lambda e: entity_avgs[e])
        
        # Return first entity
        return list(entities.keys())[0]

    def _score(self, candidates: List[str], 
               reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or containment
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Use NCD as fallback
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
        """Normalized Compression Distance."""
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
        if not scores:
            return scored
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score - min_score > 0.001:
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        else:
            # All scores are similar, spread them slightly
            for i, item in enumerate(scored):
                item["score"] = 0.5 + (i * 0.01)
        
        return scored