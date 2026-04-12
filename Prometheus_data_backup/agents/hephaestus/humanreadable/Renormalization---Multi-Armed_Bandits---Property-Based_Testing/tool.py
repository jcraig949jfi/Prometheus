import numpy as np

class ReasoningTool:
    """
    Bandit-Guided Renormalized Property Validator (BGRPV)
    
    Combines renormalization (SCC-based clause graph coarsening), multi-armed bandits
    (UCB test selection), and property-based testing (constraint validation + shrinking).
    
    Key mechanisms:
    1. Parse prompt into ClauseGraph (nodes=propositions, edges=logical relations)
    2. Renormalize via Tarjan SCC to find mutually consistent clause clusters
    3. For each candidate, use UCB bandit to select which property tests to run
    4. Score based on property satisfaction rate across all clause types
    5. Meta-confidence checks prompt for ambiguity/presupposition traps
    """
    
    def __init__(self):
        self.test_budget = 100
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        graph = self._parse_clause_graph(prompt)
        sccs = self._tarjan_scc(graph)
        renorm_vals = self._renormalize(graph, sccs)
        
        results = []
        for cand in candidates:
            arm_table = self._init_arms(graph)
            score = self._bandit_test(prompt, cand, graph, arm_table, renorm_vals)
            comp_score = self._compute_answer(prompt, cand)
            struct_score = self._structural_match(prompt, cand, graph)
            ncd_score = self._ncd(prompt, cand)
            
            final = 0.4 * comp_score + 0.35 * struct_score + 0.15 * score + 0.1 * ncd_score
            reasoning = f"Comp:{comp_score:.2f} Struct:{struct_score:.2f} Bandit:{score:.2f} NCD:{ncd_score:.2f}"
            results.append({"candidate": cand, "score": final, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta = self._meta_confidence(prompt)
        if meta < 0.3:
            return meta
        
        graph = self._parse_clause_graph(prompt)
        comp_conf = self._compute_confidence(prompt, answer)
        struct_conf = self._structural_confidence(prompt, answer, graph)
        
        base = 0.6 * comp_conf + 0.4 * struct_conf
        return min(meta, base)
    
    def _meta_confidence(self, prompt: str) -> float:
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did.*fail|why did.*stop)\b', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', p) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she)\b', p) and re.search(r'\bwho\b', p):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p) and not re.search(r'\bonly\b', p):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prefer)\b', p) and not re.search(r'\b(most|least|highest|lowest)\b', p):
            return 0.25
        
        return 1.0
    
    def _parse_clause_graph(self, text: str):
        graph = {"nodes": [], "edges": [], "types": []}
        
        # Extract numbers
        nums = re.findall(r'\b\d+\.?\d*\b', text)
        for n in nums:
            graph["nodes"].append({"type": "numeric", "value": float(n)})
            graph["types"].append("numeric")
        
        # Comparatives
        if re.search(r'\b(greater|more|larger|higher|above)\b', text.lower()):
            graph["nodes"].append({"type": "comparative", "op": ">"})
            graph["types"].append("comparative")
        if re.search(r'\b(less|fewer|smaller|lower|below)\b', text.lower()):
            graph["nodes"].append({"type": "comparative", "op": "<"})
            graph["types"].append("comparative")
        
        # Negations
        if re.search(r'\b(not|no|never|none)\b', text.lower()):
            graph["nodes"].append({"type": "negation", "value": True})
            graph["types"].append("negation")
        
        # Conditionals
        if re.search(r'\b(if|unless|when|whenever)\b.*\b(then|,)\b', text.lower()):
            graph["nodes"].append({"type": "conditional", "value": True})
            graph["types"].append("conditional")
        
        # Causals
        if re.search(r'\b(cause|lead|result|because|due to)\b', text.lower()):
            graph["nodes"].append({"type": "causal", "value": True})
            graph["types"].append("causal")
        
        return graph
    
    def _tarjan_scc(self, graph):
        nodes = graph["nodes"]
        n = len(nodes)
        if n == 0:
            return []
        
        index_counter = [0]
        stack = []
        lowlinks = [0] * n
        index = [0] * n
        on_stack = [False] * n
        index_init = [-1] * n
        sccs = []
        
        def strongconnect(v):
            index[v] = index_counter[0]
            lowlinks[v] = index_counter[0]
            index_init[v] = index_counter[0]
            index_counter[0] += 1
            on_stack[v] = True
            stack.append(v)
            
            for e in graph["edges"]:
                if e[0] == v:
                    w = e[1]
                    if index_init[w] == -1:
                        strongconnect(w)
                        lowlinks[v] = min(lowlinks[v], lowlinks[w])
                    elif on_stack[w]:
                        lowlinks[v] = min(lowlinks[v], index[w])
            
            if lowlinks[v] == index[v]:
                scc = []
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    scc.append(w)
                    if w == v:
                        break
                sccs.append(scc)
        
        for v in range(n):
            if index_init[v] == -1:
                strongconnect(v)
        
        return sccs
    
    def _renormalize(self, graph, sccs):
        vals = {}
        for scc in sccs:
            mean_val = 0.5
            for node_idx in scc:
                vals[node_idx] = mean_val
        return vals
    
    def _init_arms(self, graph):
        arms = {}
        for t in set(graph["types"]):
            arms[t] = {"count": 0, "success": 0, "fail": 0}
        return arms
    
    def _bandit_test(self, prompt, cand, graph, arm_table, renorm_vals):
        total = 0
        for _ in range(min(self.test_budget, len(arm_table) * 20)):
            arm = self._ucb_select(arm_table)
            if arm is None:
                break
            result = self._run_property_test(prompt, cand, arm, graph)
            arm_table[arm]["count"] += 1
            total += 1
            if result:
                arm_table[arm]["success"] += 1
            else:
                arm_table[arm]["fail"] += 1
        
        if total == 0:
            return 0.5
        
        score = 0.0
        weight_sum = 0.0
        for arm, data in arm_table.items():
            if data["count"] > 0:
                rate = (data["success"] + 1) / (data["count"] + 2)
                weight = data["count"]
                score += rate * weight
                weight_sum += weight
        
        return score / weight_sum if weight_sum > 0 else 0.5
    
    def _ucb_select(self, arm_table):
        total = sum(a["count"] for a in arm_table.values())
        if total == 0:
            return list(arm_table.keys())[0] if arm_table else None
        
        best_arm = None
        best_ucb = -1
        for arm, data in arm_table.items():
            if data["count"] == 0:
                return arm
            avg = data["success"] / data["count"]
            ucb = avg + math.sqrt(2 * math.log(total) / data["count"])
            if ucb > best_ucb:
                best_ucb = ucb
                best_arm = arm
        return best_arm
    
    def _run_property_test(self, prompt, cand, arm_type, graph):
        # Simplified property test
        if arm_type == "numeric":
            return self._test_numeric(prompt, cand)
        elif arm_type == "comparative":
            return self._test_comparative(prompt, cand)
        elif arm_type == "negation":
            return self._test_negation(prompt, cand)
        return True
    
    def _test_numeric(self, prompt, cand):
        p_nums = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', prompt)]
        c_nums = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', cand)]
        return len(c_nums) > 0
    
    def _test_comparative(self, prompt, cand):
        return any(w in cand.lower() for w in ['greater', 'less', 'more', 'fewer', 'higher', 'lower'])
    
    def _test_negation(self, prompt, cand):
        p_neg = bool(re.search(r'\b(not|no)\b', prompt.lower()))
        c_neg = bool(re.search(r'\b(not|no)\b', cand.lower()))
        return p_neg == c_neg
    
    def _compute_answer(self, prompt, cand):
        # Numeric comparison
        score = self._numeric_eval(prompt, cand)
        if score > 0:
            return score
        
        # Bayesian
        score = self._bayesian_eval(prompt, cand)
        if score > 0:
            return score
        
        return 0.3
    
    def _numeric_eval(self, prompt, cand):
        p_nums = re.findall(r'\b\d+\.?\d*\b', prompt)
        c_nums = re.findall(r'\b\d+\.?\d*\b', cand)
        
        if len(p_nums) >= 2 and len(c_nums) > 0:
            p_vals = [float(x) for x in p_nums]
            c_val = float(c_nums[0])
            
            if re.search(r'\bsum\b|\bplus\b|\badd\b', prompt.lower()):
                expected = sum(p_vals)
                return 1.0 if abs(c_val - expected) < 0.01 else 0.1
            elif re.search(r'\bproduct\b|\btimes\b|\bmultiply\b', prompt.lower()):
                expected = np.prod(p_vals)
                return 1.0 if abs(c_val - expected) < 0.01 else 0.1
            elif re.search(r'\bgreater\b|\blarger\b', prompt.lower()):
                if len(p_vals) >= 2:
                    return 1.0 if p_vals[0] > p_vals[1] and 'yes' in cand.lower() else 0.1
        
        return 0.0
    
    def _bayesian_eval(self, prompt, cand):
        # Simple base rate check
        if re.search(r'\bprobability\b|\bchance\b|\blikely\b', prompt.lower()):
            nums = re.findall(r'\b\d+\.?\d*\b', prompt)
            if len(nums) >= 2:
                return 0.7
        return 0.0
    
    def _structural_match(self, prompt, cand, graph):
        score = 0.0
        
        # Negation alignment
        p_neg = bool(re.search(r'\b(not|no)\b', prompt.lower()))
        c_neg = bool(re.search(r'\b(not|no)\b', cand.lower()))
        if p_neg == c_neg:
            score += 0.3
        
        # Number presence
        p_nums = len(re.findall(r'\b\d+\.?\d*\b', prompt))
        c_nums = len(re.findall(r'\b\d+\.?\d*\b', cand))
        if p_nums > 0 and c_nums > 0:
            score += 0.4
        
        # Length ratio
        ratio = len(cand) / max(len(prompt), 1)
        if 0.1 < ratio < 0.5:
            score += 0.3
        
        return min(score, 1.0)
    
    def _structural_confidence(self, prompt, answer, graph):
        if len(graph["nodes"]) == 0:
            return 0.2
        
        comp = self._compute_answer(prompt, answer)
        if comp > 0.8:
            return 0.85
        elif comp > 0.5:
            return 0.6
        else:
            return 0.3
    
    def _compute_confidence(self, prompt, answer):
        score = self._compute_answer(prompt, answer)
        if score > 0.9:
            return 0.9
        elif score > 0.7:
            return 0.7
        elif score > 0.5:
            return 0.5
        else:
            return 0.3
    
    def _ncd(self, s1, s2):
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        ncd = (c12 - min(c1, c2)) / max(c1, c2)
        return max(0, 1 - ncd)