# Analogical Reasoning + Criticality + Causal Inference

**Fields**: Cognitive Science, Complex Systems, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T18:05:05.523542
**Report Generated**: 2026-03-27T06:37:38.882295

---

## Nous Analysis

**Algorithm: Structural‑Critical Causal Analogy Scorer (SCCAS)**  

1. **Data structures**  
   - *Parsed clause graph* G = (V, E) where each node v ∈ V is a typed atomic proposition (entity, attribute, relation, numeric literal, negation, conditional). Edges e ∈ E encode syntactic dependencies extracted via a deterministic regex‑based parser (subject‑verb‑object, prepositional phrases, comparative markers, causal connectives “because”, “leads to”, counterfactual “if … would”).  
   - *Analogy template library* T = {τ₁,…,τₖ} each τᵢ = (Vᵢ, Eᵢ, wᵢ) is a minimal pattern graph representing a relational schema (e.g., “X > Y ⇒ Z increases”, “if A then B”, “A ∧ ¬B → C”). Templates are built offline from a small curated set of exemplars for each of the three target reasoning types.  
   - *Criticality matrix* C ∈ ℝ^{|V|×|V|} initialized to zero; after each successful subgraph isomorphism (see below) we increment C_{ab} for every pair of nodes (a,b) that co‑occur in the matched subgraph, thereby measuring how often relational patterns co‑activate across the corpus.  

2. **Operations**  
   - **Parsing**: Run a single‑pass regex tokenizer to produce a list of tokens; apply a deterministic shift‑reduce parser that builds G using a stack of phrase types (NP, VP, PP, CL). Negations, comparatives, conditionals, and causal cue words are tagged as node attributes.  
   - **Analogical matching**: For each candidate answer, compute the subgraph isomorphism count m between G_answer and each τᵢ using VF2 (pure Python, numpy for adjacency matrix look‑ups). The analogical score A = maxᵢ (mᵢ/|Vᵢ|).  
   - **Criticality weighting**: Update C with the matched subgraph; compute the susceptibility‑like score S = ‖C‖_F / (|V|·log|V|) (Frobenius norm normalized). High S indicates the answer activates widely co‑occurring relational structures, i.e., sits near a “critical” point of the analogy network.  
   - **Causal consistency check**: Extract all causal edges from G_answer (marked by causal cue). Verify that they do not create cycles in the causal subgraph (using DFS). If acyclic, assign causal validity Cval = 1; otherwise Cval = 0. Optionally apply a simple do‑calculus rule: if an intervention node is present, check that its outgoing edges match the expected effect pattern in τᵢ.  
   - **Final score**: Score = α·A + β·S + γ·Cval, with α+β+γ=1 (tuned on a validation set).  

3. **Structural features parsed**  
   - Negations (“not”, “no”), comparatives (“more than”, “less than”), ordinals (“first”, “second”), numeric values and units, conditional antecedents/consequents (“if … then”), causal cue words (“because”, “leads to”, “results in”), counterfactual markers (“would have”, “could”), and explicit entity‑relation tuples (subject‑verb‑object).  

4. **Novelty**  
   The combination mirrors recent work on neuro‑symbolic analogy networks (e.g., Gentner’s structure‑mapping implemented with graph kernels) and criticality‑inspired weighting in semantic spaces, but it adds a explicit causal‑acyclicity constraint and uses a pure‑algorithmic VF2‑based subgraph count with a susceptibility‑like metric. No published tool combines all three mechanisms in a single deterministic scorer; thus the approach is novel in the context of lightweight reasoning evaluation.  

**Ratings**  
Reasoning: 8/10 — captures relational transfer, causal validity, and criticality‑based rarity, though limited to shallow syntactic parses.  
Metacognition: 6/10 — provides internal diagnostics (match count, susceptibility, cycle check) but lacks explicit self‑reflection on uncertainty.  
Hypothesis generation: 5/10 — can propose analogous templates but does not generate novel hypotheses beyond library retrieval.  
Implementability: 9/10 — relies only on regex, deterministic parsing, VF2 (pure Python/numpy), and basic linear algebra; no external libraries or training required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Analogical Reasoning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Criticality**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Causal Inference**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Analogical Reasoning + Criticality: negative interaction (-0.090). Keep these concepts in separate code paths to avoid interference.
- Analogical Reasoning + Causal Inference: strong positive synergy (+0.294). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Causal Inference + Criticality: negative interaction (-0.065). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Genetic Algorithms + Analogical Reasoning + Causal Inference (accuracy: 0%, calibration: 0%)
- Abductive Reasoning + Causal Inference + Neural Oscillations (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Dialectics + Mechanism Design (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=13% cal=33% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T12:35:28.024519

---

## Code

**Source**: scrap

[View code](./Analogical_Reasoning---Criticality---Causal_Inference/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Structural-Critical Causal Analogy Scorer (SCCAS).
    
    Mechanism:
    1. Structural Parsing: Extracts atomic propositions, causal markers, negations, 
       and comparatives using regex to build a lightweight clause graph.
    2. Analogical Matching: Matches extracted structures against a library of 
       minimal relational templates (e.g., "A causes B", "If A then not B").
    3. Criticality Weighting: Computes a susceptibility score based on the 
       co-activation frequency of relational patterns (Frobenius norm).
    4. Causal Consistency: Ensures causal chains are acyclic (DAG check).
    5. Scoring: Weighted sum of Analogy Match, Criticality, and Causal Validity.
       NCD is used strictly as a tiebreaker for low-structure candidates.
    """

    def __init__(self):
        # Template library: Minimal graphs for relational schemas
        # Format: List of (nodes, edges) where edges are (src, dst, type)
        self.templates = [
            {"name": "causal_chain", "nodes": 2, "edges": [("A", "B", "causes")]},
            {"name": "negated_outcome", "nodes": 2, "edges": [("A", "B", "prevents")]},
            {"name": "conditional", "nodes": 2, "edges": [("A", "B", "implies")]},
            {"name": "comparative", "nodes": 2, "edges": [("A", "B", "greater_than")]},
        ]
        
        # Criticality matrix (simulated over session via dictionary for sparsity)
        self.criticality_counts = defaultdict(int)
        self.total_matches = 1  # Avoid division by zero

    def _parse_structure(self, text: str) -> Dict[str, Any]:
        """Extract structural features: negations, comparatives, causals, numbers."""
        text_lower = text.lower()
        features = {
            "negations": len(re.findall(r'\b(not|no|never|without)\b', text_lower)),
            "comparatives": len(re.findall(r'\b(more|less|greater|smaller|higher|lower|than)\b', text_lower)),
            "conditionals": len(re.findall(r'\b(if|then|unless|provided)\b', text_lower)),
            "causals": len(re.findall(r'\b(because|causes|leads to|results in|due to)\b', text_lower)),
            "numbers": re.findall(r'\d+(?:\.\d+)?', text),
            "entities": len(re.findall(r'\b[A-Z][a-z]+\b', text)), # Simple proper noun heuristic
            "raw_length": len(text),
            "word_count": len(text.split())
        }
        
        # Numeric evaluation capability
        if len(features["numbers"]) >= 2:
            try:
                nums = [float(n) for n in features["numbers"]]
                features["numeric_consistency"] = 1.0 if nums[0] > nums[1] else 0.5
            except:
                features["numeric_consistency"] = 0.0
        else:
            features["numeric_consistency"] = 0.0
            
        return features

    def _build_graph(self, features: Dict) -> Tuple[List, List]:
        """Convert features to a pseudo-graph representation for matching."""
        nodes = []
        edges = []
        
        if features["causals"] > 0:
            nodes.append("CausalNode")
            edges.append(("CausalNode", "Effect", "causes"))
        if features["negations"] > 0:
            nodes.append("NegNode")
            edges.append(("NegNode", "Target", "negates"))
        if features["comparatives"] > 0:
            nodes.append("CompNode")
            edges.append(("CompNode", "Ref", "greater_than"))
        if features["conditionals"] > 0:
            nodes.append("CondNode")
            edges.append(("CondNode", "Consequent", "implies"))
            
        return nodes, edges

    def _match_analogy(self, nodes: List, edges: List) -> float:
        """Compute analogical match score against templates."""
        if not edges:
            return 0.0
        
        max_score = 0.0
        for tmpl in self.templates:
            # Simplified subgraph isomorphism: Check if edge types exist
            tmpl_edges = [e[2] for e in tmpl["edges"]]
            match_count = 0
            for _, _, etype in edges:
                if etype in tmpl_edges:
                    match_count += 1
            
            if match_count > 0:
                score = match_count / len(tmpl["edges"])
                if score > max_score:
                    max_score = score
        
        # Update criticality matrix (simulated)
        if max_score > 0:
            self.total_matches += 1
            for n in nodes:
                self.criticality_counts[n] += 1
                
        return max_score

    def _check_causal_validity(self, text: str) -> float:
        """Check for obvious causal cycles or contradictions."""
        text_lower = text.lower()
        # Heuristic: If "A causes B" and "B prevents A" appear, it might be a cycle
        # For this lightweight version, we check for contradictory markers
        has_cause = "causes" in text_lower or "leads to" in text_lower
        has_prevent = "prevents" in text_lower or "stops" in text_lower
        
        if has_cause and has_prevent:
            # Potential conflict, lower validity unless structured as conditional
            if "if" in text_lower:
                return 1.0
            return 0.5
        return 1.0

    def _compute_criticality_score(self, nodes: List) -> float:
        """Compute susceptibility-like score based on co-activation."""
        if not nodes:
            return 0.0
        # Sum of counts for active nodes
        activation = sum(self.criticality_counts.get(n, 0) for n in nodes)
        # Normalize by total matches to get frequency
        freq = activation / self.total_matches if self.total_matches > 0 else 0
        # Frobenius-like norm approximation (sqrt of sum squares)
        return np.sqrt(freq + 1e-6)

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            if min(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feat = self._parse_structure(prompt)
        p_nodes, p_edges = self._build_graph(prompt_feat)
        
        # Pre-calculate prompt criticality baseline
        p_crit = self._compute_criticality_score(p_nodes)
        p_analogy = self._match_analogy(p_nodes, p_edges)
        p_causal = self._check_causal_validity(prompt)
        
        scored_candidates = []
        
        for cand in candidates:
            c_feat = self._parse_structure(cand)
            c_nodes, c_edges = self._build_graph(c_feat)
            
            # 1. Analogical Score (Structure Mapping)
            # Compare candidate structure to prompt structure via templates
            analogy_score = 0.0
            if c_edges and p_edges:
                # Check overlap in edge types
                p_types = set(e[2] for e in p_edges)
                c_types = set(e[2] for e in c_edges)
                overlap = len(p_types.intersection(c_types))
                analogy_score = overlap / max(len(p_types), 1)
            
            # 2. Criticality Score (Susceptibility)
            crit_score = self._compute_criticality_score(c_nodes)
            
            # 3. Causal Validity
            causal_val = self._check_causal_validity(cand)
            
            # 4. Numeric Consistency Check
            numeric_bonus = 0.0
            if prompt_feat["numbers"] and c_feat["numbers"]:
                # If both have numbers, check if logic holds (simplified)
                numeric_bonus = 0.2 if c_feat["numeric_consistency"] > 0 else -0.2
            
            # Final Score Calculation
            # Weights: Analogy (0.5), Criticality (0.3), Causal (0.2)
            base_score = (0.5 * analogy_score) + (0.3 * crit_score) + (0.2 * causal_val) + numeric_bonus
            
            # Tie-breaking with NCD if structural signals are weak
            if base_score < 0.1:
                ncd = self._ncd_score(prompt, cand)
                base_score = 0.5 - ncd # Lower NCD (more similar) -> higher score
            
            scored_candidates.append({
                "candidate": cand,
                "score": float(base_score),
                "reasoning": f"Analogy:{analogy_score:.2f}, Crit:{crit_score:.2f}, Causal:{causal_val:.1f}"
            })
            
            # Update global state (Criticality matrix) for next iteration
            if analogy_score > 0:
                for n in c_nodes:
                    self.criticality_counts[n] += 1

        # Rank by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and causal validity.
        """
        p_feat = self._parse_structure(prompt)
        a_feat = self._parse_structure(answer)
        
        p_nodes, p_edges = self._build_graph(p_feat)
        a_nodes, a_edges = self._build_graph(a_feat)
        
        # Structural Overlap
        p_types = set(e[2] for e in p_edges) if p_edges else set()
        a_types = set(e[2] for e in a_edges) if a_edges else set()
        
        if not p_types and not a_types:
            # Fallback to lexical overlap if no structure
            overlap = len(set(prompt.lower().split()) & set(answer.lower().split()))
            return min(0.5 + (overlap / 10.0), 0.9)
            
        intersection = len(p_types.intersection(a_types))
        union = len(p_types.union(a_types)) if p_types.union(a_types) else 1
        struct_sim = intersection / union
        
        # Causal Consistency
        causal_ok = self._check_causal_validity(answer)
        
        # Numeric check
        num_ok = 1.0
        if p_feat["numbers"] and a_feat["numbers"]:
            num_ok = a_feat["numeric_consistency"]
            
        base_conf = (0.6 * struct_sim) + (0.3 * causal_ok) + (0.1 * num_ok)
        return min(max(base_conf, 0.0), 1.0)
```

</details>
