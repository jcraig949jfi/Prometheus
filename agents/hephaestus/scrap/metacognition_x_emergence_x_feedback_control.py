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