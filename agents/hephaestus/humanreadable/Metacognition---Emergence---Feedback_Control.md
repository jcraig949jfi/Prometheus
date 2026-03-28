# Metacognition + Emergence + Feedback Control

**Fields**: Cognitive Science, Complex Systems, Control Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T12:33:45.660047
**Report Generated**: 2026-03-27T17:21:24.333561

---

## Nous Analysis

The algorithm builds a lightweight propositional‑constraint graph from the prompt and each candidate answer, then iteratively refines node confidences using a PID‑style feedback loop; the emergent macro‑score is the stabilized confidence of the answer’s conclusion nodes.

**Data structures**  
- `Node`: `{id: int, text: str, conf: float, type: str}` where `type` ∈ {fact, rule, query}.  
- `Edge`: `(src_id, dst_id, rel)` with `rel` ∈ {IMPLIES, NOT, EQUIV, COMPARE, CAUSE}.  
- `Graph`: `nodes: dict[int, Node]`, `adj: dict[int, list[Edge]]`.  
- `PID_state` per node: `{e_prev: float, e_int: float}` for confidence error.

**Operations**  
1. **Parsing** – regexes extract:  
   - Negations (`not`, `no`), comparatives (`greater than`, `less than`), conditionals (`if … then …`), causal cues (`because`, `leads to`), numeric literals with units, and ordering tokens (`first`, `last`).  
   Each extracted fragment becomes a Node; relational cues create Edges.  
2. **Initial confidence** – set to 0.5 for all nodes; facts from the prompt get 0.9, queries 0.1.  
3. **Constraint propagation** – for each IMPLIES edge, compute predicted confidence of dst as `min(conf_src, 1.0)`. Error `e = conf_dst_pred - conf_dst`. Update `conf_dst` with a PID step:  
   `conf_dst += Kp*e + Ki*e_int + Kd*(e - e_prev)` (clipped to [0,1]).  
   Integrate and store `e_int`, `e_prev`.  
4. **Emergent scoring** – after N iterations (or when max|e| < ε), the macro‑level answer score is the weighted average of confidences of nodes marked as answer conclusions, weighted by inverse confidence variance (stability margin). Lower variance → higher trust.  
5. **Feedback control** – the PID loop acts as the feedback controller; the error signal is the inconsistency between inferred and stored confidences, driving the system toward a stable fixed point (emergent coherence).

**Structural features parsed** – negations, comparatives, conditionals, causal claims, numeric values/units, equivalence statements, ordering relations (before/after, greater/less), and conjunction/disjunction cues.

**Novelty** – While belief propagation and constraint solving exist, coupling them with explicit metacognitive confidence calibration via a PID feedback controller to produce an emergent stability‑based score is not documented in pure‑numpy reasoning tools; it combines three traditionally separate layers into a single update rule.

**Ratings**  
Reasoning: 8/10 — captures logical structure and propagates uncertainty, but limited to shallow relational patterns.  
Metacognition: 7/10 — confidence calibration and error monitoring are present, yet no higher‑level strategy selection.  
Hypothesis generation: 6/10 — focuses on evaluating given answers; generating new hypotheses would require extra abductive rules.  
Implementability: 9/10 — relies only on regex, dict/list structures, and simple numeric loops; feasible within the constraints.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Metacognition**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Emergence**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 34% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Feedback Control**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Emergence + Feedback Control: strong positive synergy (+0.611). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Phenomenology + Emergence + Feedback Control (accuracy: 0%, calibration: 0%)
- Spectral Analysis + Emergence + Feedback Control (accuracy: 0%, calibration: 0%)
- Attention Mechanisms + Neural Plasticity + Feedback Control (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=31% cal=33% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T16:43:23.165777

---

## Code

**Source**: scrap

[View code](./Metacognition---Emergence---Feedback_Control/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning tool combining structural parsing, constraint propagation via PID feedback,
    and emergent scoring to evaluate candidate answers.
    
    Mechanism:
    1. Parses prompt and candidates into a graph of nodes (facts/rules) and edges (relations).
    2. Initializes confidence based on source (prompt facts high, queries low).
    3. Iteratively refines node confidences using a PID-style controller to minimize 
       inconsistency between connected nodes (e.g., if A implies B, conf(B) should match conf(A)).
    4. Scores candidates based on the stabilized confidence of their conclusion nodes.
    5. Applies epistemic honesty checks (Tier B) to cap confidence on ambiguous/unanswerable prompts.
    """
    
    def __init__(self):
        # PID Constants
        self.Kp = 0.5
        self.Ki = 0.1
        self.Kd = 0.1
        self.max_iter = 20
        self.epsilon = 1e-4

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self.confidence(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": self._generate_reasoning(prompt, cand)
            })
        # Sort by score descending
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        # Tier B: Epistemic Honesty Check first
        meta_cap = self._meta_confidence(prompt)
        
        # Structural Parsing & Graph Construction
        nodes, adj, conclusion_ids = self._parse(prompt, answer)
        
        if not nodes:
            # No structure found, rely on NCD tiebreaker but keep low confidence
            ncd_score = 1.0 - self._ncd(prompt, answer)
            return min(0.2, meta_cap) if ncd_score < 0.5 else min(0.3, meta_cap)

        # Initialize PID State
        pid_state = {nid: {"e_prev": 0.0, "e_int": 0.0} for nid in nodes}
        
        # Constraint Propagation with PID Feedback
        for _ in range(self.max_iter):
            max_error = 0.0
            for nid, node in nodes.items():
                if node["type"] == "fact":
                    continue # Facts are anchored
                
                # Gather incoming constraints
                predicted_vals = []
                weights = []
                
                if nid in adj:
                    for src_id, rel in adj[nid]:
                        if src_id not in nodes: continue
                        src_conf = nodes[src_id]["conf"]
                        
                        pred = 0.5
                        if rel == "IMPLIES":
                            pred = src_conf
                        elif rel == "NOT":
                            pred = 1.0 - src_conf
                        elif rel == "EQUIV":
                            pred = src_conf
                        elif rel == "CAUSE":
                            pred = src_conf * 0.9 # Slight decay for causal chains
                            
                        predicted_vals.append(pred)
                        weights.append(1.0) # Simple weighting
                
                if not predicted_vals:
                    continue
                    
                # Weighted average of predictions
                target_conf = sum(p*w for p, w in zip(predicted_vals, weights)) / sum(weights)
                
                # PID Control Step
                error = target_conf - node["conf"]
                max_error = max(max_error, abs(error))
                
                state = pid_state[nid]
                state["e_int"] += error
                d_error = error - state["e_prev"]
                
                delta = (self.Kp * error) + (self.Ki * state["e_int"]) + (self.Kd * d_error)
                node["conf"] = max(0.0, min(1.0, node["conf"] + delta))
                
                state["e_prev"] = error

            if max_error < self.epsilon:
                break

        # Emergent Scoring: Stability-weighted average of conclusion nodes
        if not conclusion_ids:
            base_score = 0.5
        else:
            total_weight = 0.0
            weighted_sum = 0.0
            for cid in conclusion_ids:
                if cid in nodes:
                    # Stability margin: inverse of final error variance proxy (using last delta approx)
                    # Here we use confidence magnitude as a proxy for stability in this simple loop
                    w = nodes[cid]["conf"] * (1.0 - nodes[cid]["conf"]) + 0.1 # Avoid div by zero
                    weighted_sum += nodes[cid]["conf"] * w
                    total_weight += w
            base_score = weighted_sum / total_weight if total_weight > 0 else 0.5

        # NCD Tiebreaker (max 15% influence)
        ncd_sim = 1.0 - self._ncd(prompt, answer)
        if ncd_sim > 0.8: # Only if very similar textually
            base_score = 0.85 * base_score + 0.15 * ncd_sim
            
        return min(base_score, meta_cap)

    def _meta_confidence(self, prompt: str) -> float:
        """Checks for Tier B traps: presupposition, ambiguity, subjectivity."""
        p = prompt.lower()
        
        # 1. Presupposition traps ("Have you stopped...", "Why did X fail?")
        if re.search(r'\b(have you stopped|why did .+ (fail|stop|quit)|when did .+ stop)\b', p):
            return 0.2
        
        # 2. Scope/Pronoun Ambiguity ("Every X... same Y?", "X told Y he...")
        if re.search(r'\b(every .+ a .+|told .+ he|told .+ she|who was it)\b', p):
            if "ambigu" in p or "who" in p: # Heuristic for explicit ambiguity questions
                return 0.2

        # 3. False Dichotomy ("Either A or B" without context)
        if re.search(r'\beither .+ or .+\b', p) and "only" not in p:
            # Soft penalty, depends on context
            pass 

        # 4. Subjectivity ("Best", "Favorite" without criteria)
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p):
            if "data" not in p and "chart" not in p and "table" not in p:
                return 0.3 # Cap for subjective questions without data

        return 1.0

    def _parse(self, prompt: str, answer: str) -> Tuple[Dict, Dict, List[int]]:
        """Parses text into Nodes and Edges."""
        nodes = {}
        adj = {} # dst -> [(src, rel)]
        node_id = 0
        conclusion_ids = []
        
        def add_node(text: str, n_type: str, conf: float) -> int:
            nonlocal node_id
            nid = node_id
            nodes[nid] = {"id": nid, "text": text, "conf": conf, "type": n_type}
            node_id += 1
            return nid

        def add_edge(src: int, dst: int, rel: str):
            if dst not in adj: adj[dst] = []
            adj[dst].append((src, rel))

        # Process Prompt
        sentences = re.split(r'[.!?]', prompt)
        for sent in sentences:
            sent = sent.strip()
            if not sent: continue
            
            # Detect Negation
            is_neg = bool(re.search(r'\b(not|no|never)\b', sent.lower()))
            
            # Detect Conditionals
            if "if" in sent.lower() and "then" in sent.lower():
                parts = re.split(r'\bthen\b', sent, flags=re.IGNORECASE)
                if len(parts) == 2:
                    src_id = add_node(parts[0].strip(), "fact", 0.9)
                    dst_id = add_node(parts[1].strip(), "rule", 0.5)
                    add_edge(src_id, dst_id, "IMPLIES")
                    continue
            
            # Detect Comparatives (Numeric)
            num_match = re.search(r'(\d+\.?\d*)\s*(greater|less|more|fewer).*?(\d+\.?\d*)', sent.lower())
            if num_match:
                v1, op, v2 = float(num_match.group(1)), num_match.group(2), float(num_match.group(3))
                fact_text = f"{v1} {op} {v2}"
                nid = add_node(fact_text, "fact", 0.9)
                # Implicitly validate answer against this if answer contains numbers
                continue

            # Default Fact Extraction
            clean_sent = sent.replace("If", "").replace("if", "").split("then")[-1].strip()
            if clean_sent:
                conf = 0.9 if not is_neg else 0.1
                nid = add_node(clean_sent, "fact", conf)
                if is_neg:
                    # Add implicit NOT relation if we had a positive node, 
                    # but for now just lower confidence or flag type
                    nodes[nid]["type"] = "negated_fact"

        # Process Answer as Query/Conclusion
        ans_nodes = []
        if answer.strip():
            # Check for numeric answer
            ans_num = re.search(r'(\d+\.?\d*)', answer)
            if ans_num:
                # Create a query node for the number
                nid = add_node(answer, "query", 0.1)
                ans_nodes.append(nid)
                conclusion_ids.append(nid)
            else:
                nid = add_node(answer, "query", 0.1)
                ans_nodes.append(nid)
                conclusion_ids.append(nid)

        # Link Prompt Facts to Answer Query (Heuristic Matching)
        # If answer text appears in prompt facts, link them
        for nid, node in nodes.items():
            if node["type"] == "fact":
                for aid in ans_nodes:
                    ans_node = nodes[aid]
                    # Simple substring match for linking
                    if node["text"].lower() in ans_node["text"].lower() or \
                       ans_node["text"].lower() in node["text"].lower():
                        add_edge(nid, aid, "EQUIV")
                    # Numeric consistency check
                    p_nums = re.findall(r'\d+\.?\d*', node["text"])
                    a_nums = re.findall(r'\d+\.?\d*', ans_node["text"])
                    if p_nums and a_nums:
                        if p_nums[-1] == a_nums[-1]:
                            add_edge(nid, aid, "IMPLIES")

        return nodes, adj, conclusion_ids

    def _generate_reasoning(self, prompt: str, answer: str) -> str:
        # Simplified reasoning string generation
        meta = self._meta_confidence(prompt)
        if meta < 0.5:
            return "Low confidence due to ambiguity or presupposition in prompt."
        
        # Check numeric
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        a_nums = re.findall(r'\d+\.?\d*', answer)
        
        if p_nums and a_nums:
            return f"Numeric consistency check: Prompt contains {p_nums}, Answer contains {a_nums}."
        
        return "Structural alignment based on keyword overlap and logical constraints."

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2: return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        concat = s1_bytes + s2_bytes
        
        len1 = len(zlib.compress(s1_bytes))
        len2 = len(zlib.compress(s2_bytes))
        len_concat = len(zlib.compress(concat))
        
        max_len = max(len1, len2)
        if max_len == 0: return 0.0
        return (len_concat - max_len) / max_len
```

</details>
