# Ecosystem Dynamics + Multi-Armed Bandits + Property-Based Testing

**Fields**: Biology, Game Theory, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T16:33:26.504869
**Report Generated**: 2026-04-02T04:20:10.100738

---

## Nous Analysis

**Algorithm – Constraint‑Driven Bandit‑Guided Property Testing (CDBG‑PT)**  

1. **Parsing & Constraint Graph**  
   - From the prompt extract atomic propositions (e.g., “species A preys on B”, “temperature > 20°C”) using regex patterns for negations, comparatives, conditionals, causal verbs (“leads to”, “results in”), and ordering relations (“more than”, “before”).  
   - Build a directed graph G = (V,E) where each node vᵢ∈V stores a proposition and its type (boolean, numeric, ordinal). Edge eᵢⱼ encodes a logical constraint extracted from the prompt (e.g., vᵢ → ¬vⱼ for “if A then not B”, vᵢ ≤ vⱼ + 5 for numeric bounds).  
   - Store adjacency lists as Python dicts of lists; edge weights are numpy arrays for numeric constraints.

2. **Candidate Representation**  
   - Each candidate answer aₖ is a vector xₖ∈ℝᵐ (m = |V|) where boolean entries are 0/1, numeric entries are the asserted values, and ordinal entries are encoded as ranks.  
   - Feasibility score sₖ = 1 − ‖C(xₖ)‖₂ / ‖C‖₂, where C(x) is the vector of constraint residuals (violation magnitude) computed by propagating constraints through G using numpy dot‑products and element‑wise max/min for logical ops.

3. **Multi‑Armed Bandit Selection**  
   - Treat each candidate as an arm. Maintain empirical mean μₖ and count nₖ of feasibility scores observed so far.  
   - At each iteration compute UCBₖ = μₖ + α·√(ln N / nₖ) (α tuned, N total pulls).  
   - Pull the arm with highest UCB: generate a set of property‑based mutants Mₖ by applying small random perturbations (bit‑flips for booleans, Gaussian noise for numerics, swap for ordinals) using numpy.random.  
   - Evaluate each mutant’s feasibility; keep the minimal‑violation mutant (shrinking step) to detect fragile claims.  
   - Update μₖ with the average feasibility of Mₖ (and the original candidate).  

4. **Final Score**  
   - After a fixed budget T of pulls, return the feasibility‑weighted UCB of the best arm: Score = μ_best + β·√(ln T / n_best). Higher scores indicate answers that satisfy more constraints and are robust to small perturbations.

**Structural Features Parsed**  
- Negations (“not”, “no”), comparatives (“greater than”, “less than”), conditionals (“if … then …”, “unless”), causal claims (“causes”, “leads to”), numeric thresholds, ordering relations (“before/after”, “more/less frequent”), and existential/universal quantifiers inferred from phrases like “some”, “all”.

**Novelty**  
- The combination is novel: property‑based testing supplies automatic mutation and shrinking; multi‑armed bandits allocate evaluation effort to uncertain answers; ecosystem‑dynamics‑inspired constraint graphs encode trophic‑like dependencies (energy flow → logical flow). No prior work couples UCB‑driven arm selection with constraint‑propagation‑based feasibility testing in a pure‑numpy evaluator.

**Rating**  
Reasoning: 8/10 — The algorithm directly evaluates logical and quantitative constraints, yielding a principled correctness measure.  
Metacognition: 6/10 — It monitors uncertainty via UCB counts but does not reflect on its own parsing errors.  
Hypothesis generation: 7/10 — Mutant generation creates hypotheses about answer robustness; shrinking isolates minimal counterexamples.  
Implementability: 9/10 — Uses only regex, numpy arrays, and basic Python data structures; no external libraries or APIs needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=24% cal=1% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-01T22:09:02.359094

---

## Code

**Source**: scrap

[View code](./Ecosystem_Dynamics---Multi-Armed_Bandits---Property-Based_Testing/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    CDBG-PT: Constraint-Driven Bandit-Guided Property Testing.
    Combines ecosystem-style constraint graphs, UCB bandits for candidate selection,
    and property-based mutation testing to evaluate reasoning robustness.
    Includes Tier B metacognitive checks for epistemic honesty.
    """
    
    def __init__(self):
        self.alpha = 1.5  # UCB exploration parameter
        self.beta = 0.5   # Final score weighting
        self.t_mutate = 5 # Mutations per pull
        
    # --- TIER B: METACOGNITIVE ANALYSIS ---
    def _meta_confidence(self, prompt: str) -> float:
        """
        Detects ambiguity, presuppositions, and logical traps.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        score = 1.0
        
        # 1. Presupposition Traps ("Have you stopped...", "Why did X fail?")
        presup_patterns = [
            r"have you (stopped|quit|ceased)",
            r"why did .+ (fail|stop|break)",
            r"when did .+ (start|begin)",
            r"how much (better|worse)",
            r"who is the (king|leader|owner)" # Assumes existence
        ]
        for pat in presup_patterns:
            if re.search(pat, p_lower):
                score = min(score, 0.2) # Highly suspicious
        
        # 2. Scope/Pronoun Ambiguity
        if re.search(r"every .+ (a|an) .+\?", p_lower) and "same" not in p_lower:
            score = min(score, 0.4) # Potential scope ambiguity
        if re.search(r"(he|she|him|her|it) was", p_lower) and "who" in p_lower:
            score = min(score, 0.3) # Pronoun ambiguity trap

        # 3. False Dichotomy
        if re.search(r"either .+ or .+", p_lower) and "only" not in p_lower:
            score = min(score, 0.5)

        # 4. Subjectivity without criteria
        subj_words = ["best", "worst", "favorite", "beautiful", "ugly"]
        if any(w in p_lower for w in subj_words) and "measure" not in p_lower and "data" not in p_lower:
            score = min(score, 0.3)

        # 5. Unanswerability indicators (Heuristics)
        if "cannot be determined" in p_lower or "insufficient information" in p_lower:
            # If the prompt itself asks about insufficiency, we are confident in that logic
            return 0.9 
            
        return max(0.0, score)

    def _parse_constraints(self, prompt: str) -> Tuple[List[str], List[Tuple], Dict[str, any]]:
        """
        Extracts atomic propositions and constraints.
        Returns nodes, edges, and extracted numeric values.
        """
        nodes = []
        edges = [] # (src_idx, dst_idx, type, weight)
        data = {"nums": [], "bools": {}, "relations": []}
        
        # Extract Numbers
        nums = re.findall(r"[-]?\d+(?:\.\d+)?", prompt)
        data["nums"] = [float(n) for n in nums]
        
        # Simple SVO and Logic Parsing
        sentences = re.split(r'[.\n]', prompt)
        node_idx = 0
        
        for sent in sentences:
            sent = sent.strip()
            if not sent: continue
            
            # Negation
            is_neg = bool(re.search(r"\b(not|no|never|without)\b", sent.lower()))
            
            # Conditionals
            if "if" in sent.lower() and "then" in sent.lower():
                edges.append((0, 1, 'implies', 1.0)) # Abstract mapping for demo
            
            # Comparatives
            comp_match = re.search(r"(\w+)\s+(is|are)?\s*(greater|less|more|fewer)\s+than\s+(\w+)", sent.lower())
            if comp_match:
                # Create symbolic nodes for variables if not existing
                v1, v2 = comp_match.group(1), comp_match.group(4)
                if v1 not in data['bools']: nodes.append(v1); data['bools'][v1] = 0
                if v2 not in data['bools']: nodes.append(v2); data['bools'][v2] = 0
                
                direction = 1 if "greater" in comp_match.group(3) or "more" in comp_match.group(3) else -1
                if is_neg: direction *= -1
                edges.append((v1, v2, 'comp', direction))

            # Causal/Leads to
            if "leads to" in sent or "causes" in sent or "results in" in sent:
                parts = re.split(r'\s+(leads to|causes|results in)\s+', sent, flags=re.IGNORECASE)
                if len(parts) >= 2:
                    src, dst = parts[0].strip(), parts[1].strip()
                    edges.append((src, dst, 'causal', 1.0 if not is_neg else -1.0))

        # Deduplicate nodes list
        unique_nodes = list(dict.fromkeys(nodes))
        return unique_nodes, edges, data

    def _compute_feasibility(self, prompt: str, candidate: str) -> float:
        """
        Computes feasibility score based on constraint satisfaction.
        1.0 = Perfect match, 0.0 = Total violation.
        """
        p_nodes, p_edges, p_data = self._parse_constraints(prompt)
        c_lower = candidate.lower()
        p_lower = prompt.lower()
        
        score = 1.0
        violations = 0
        total_checks = 0
        
        # 1. Numeric Consistency Check
        c_nums = [float(n) for n in re.findall(r"[-]?\d+(?:\.\d+)?", candidate)]
        if p_data["nums"] and c_nums:
            # Check if candidate numbers respect simple orderings found in prompt
            # This is a heuristic proxy for "solving" the math
            if len(p_data["nums"]) == len(c_nums):
                for pn, cn in zip(p_data["nums"], c_nums):
                    total_checks += 1
                    if abs(pn - cn) > 1e-6: # Exact match expected for calc problems
                         # Allow small float errors, but penalize large deviations
                        if abs(pn - cn) > 0.1: 
                            violations += 1
            elif len(c_nums) > 0:
                # If candidate introduces new numbers not derivable, slight penalty unless it's a calculation result
                pass 

        # 2. Logical Constraint Check (Negation & Keywords)
        for src, dst, etype, weight in p_edges:
            total_checks += 1
            src_present = str(src).lower() in c_lower
            dst_present = str(dst).lower() in c_lower
            
            if etype == 'causal':
                # If A causes B, and candidate asserts A but denies B (or vice versa incorrectly)
                if weight > 0: # A -> B
                    if src_present and not dst_present:
                        # Check for explicit negation of B in candidate
                        if re.search(rf"\bnot\s+{dst}\b", c_lower) or (dst in ["yes", "no"] and (dst == "yes") != src_present):
                             violations += 1
                elif weight < 0: # A -> not B
                    if src_present and dst_present:
                        violations += 1
            
            elif etype == 'comp':
                # A > B. If candidate says B > A explicitly
                if weight > 0: # A > B
                    if str(dst).lower() in c_lower and str(src).lower() in c_lower:
                        # Check for reverse phrasing
                        if re.search(rf"{dst}.*(?:greater|more).*{src}", c_lower):
                            violations += 1

        if total_checks == 0:
            return 0.5 # Neutral if no constraints found
            
        raw_score = 1.0 - (violations / total_checks)
        return max(0.0, min(1.0, raw_score))

    def _generate_mutants(self, candidate: str, n: int = 3) -> List[str]:
        """Generate property-based mutants of the candidate."""
        mutants = [candidate]
        words = candidate.split()
        if not words:
            return mutants
            
        for _ in range(n):
            mutation_type = np.random.choice(['flip', 'noise', 'swap'])
            new_words = words.copy()
            
            if mutation_type == 'flip' and len(new_words) > 0:
                idx = np.random.randint(0, len(new_words))
                word = new_words[idx]
                if word.lower() in ['yes', 'true', 'correct']:
                    new_words[idx] = 'No'
                elif word.lower() in ['no', 'false', 'incorrect']:
                    new_words[idx] = 'Yes'
                elif word.lower() in ['increases', 'rises']:
                    new_words[idx] = 'decreases'
                elif word.lower() in ['decreases', 'falls']:
                    new_words[idx] = 'increases'
                    
            elif mutation_type == 'noise' and len(new_words) > 0:
                # Add slight numeric noise if numbers exist
                txt = " ".join(new_words)
                nums = re.findall(r"\d+(?:\.\d+)?", txt)
                if nums:
                    num_str = nums[0]
                    try:
                        val = float(num_str)
                        noise = np.random.normal(0, val * 0.1)
                        new_val = val + noise
                        txt = txt.replace(num_str, f"{new_val:.2f}")
                        mutants.append(txt)
                        continue
                    except: pass
            
            mutants.append(" ".join(new_words))
            
        return mutants

    def _ucb_select(self, arms: Dict[str, Dict], total_pulls: int) -> str:
        """Select arm with highest UCB."""
        best_ucb = -np.inf
        best_arm = None
        if total_pulls == 0: 
            return list(arms.keys())[0]
            
        for name, stats in arms.items():
            mu = stats['sum_score'] / stats['count'] if stats['count'] > 0 else 0.5
            exploration = self.alpha * np.sqrt(np.log(total_pulls + 1) / (stats['count'] + 1))
            ucb = mu + exploration
            if ucb > best_ucb:
                best_ucb = ucb
                best_arm = name
        return best_arm if best_arm else list(arms.keys())[0]

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # Initialize Arms
        arms = {c: {'count': 0, 'sum_score': 0.0} for c in candidates}
        total_pulls = 0
        budget = 10 # Fixed budget for speed
        
        # Initial Pull
        for c in candidates:
            score = self._compute_feasibility(prompt, c)
            arms[c]['count'] += 1
            arms[c]['sum_score'] += score
            total_pulls += 1
            
        # Bandit Loop
        for _ in range(budget):
            selected = self._ucb_select(arms, total_pulls)
            mutants = self._generate_mutants(selected, self.t_mutate)
            
            mutant_scores = []
            for m in mutants:
                s = self._compute_feasibility(prompt, m)
                mutant_scores.append(s)
            
            avg_score = np.mean(mutant_scores)
            
            arms[selected]['count'] += 1
            arms[selected]['sum_score'] += avg_score
            total_pulls += 1
            
        # Final Scoring
        results = []
        for c in candidates:
            stats = arms[c]
            mu = stats['sum_score'] / stats['count'] if stats['count'] > 0 else 0
            final_score = mu + self.beta * np.sqrt(np.log(total_pulls + 1) / (stats['count'] + 1))
            
            # NCD Tiebreaker (Max 15% influence)
            # We normalize NCD to [0,1] where 1 is similar. 
            # Actually, for reasoning, we want the candidate that fits the prompt constraints best.
            # NCD is weak here, so we use it only if scores are very close, or ignore if structural score is high.
            # Implementation: Blend slightly.
            p_comp = zlib.compress(prompt.encode())
            c_comp = zlib.compress(c.encode())
            pc_comp = zlib.compress((prompt + c).encode())
            ncd = 1.0 - (len(pc_comp) - len(p_comp)) / (len(c_comp) + 1) # Rough NCD approx
            ncd = max(0, min(1, ncd))
            
            # Weighted blend: 85% Structural/Bandit, 15% NCD (as fallback for semantic similarity)
            # Note: In strict reasoning, NCD is often noise, but required by prompt spec.
            blended_score = 0.85 * final_score + 0.15 * ncd
            
            results.append({
                "candidate": c,
                "score": float(blended_score),
                "reasoning": f"Feasibility: {mu:.3f}, Robustness: {stats['count']} pulls, NCD_bonus: {ncd:.3f}"
            })
            
        return sorted(results, key=lambda x: x['score'], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns calibrated confidence.
        Caps based on meta-analysis of the prompt.
        """
        # 1. Meta-confidence cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural Computation Confidence
        # If we can parse constraints and the answer satisfies them perfectly, confidence rises.
        # If parsing yields 0 constraints, confidence should be low (guessing).
        nodes, edges, data = self._parse_constraints(prompt)
        
        base_conf = 0.5 # Base uncertainty
        
        if len(edges) > 0:
            # We have logic to check
            feasibility = self._compute_feasibility(prompt, answer)
            if feasibility > 0.9:
                base_conf = 0.85
            elif feasibility < 0.5:
                base_conf = 0.2 # Likely wrong
            else:
                base_conf = 0.5
        else:
            # No structural constraints found. 
            # Check for pure numeric calculation (e.g. "What is 2+2?")
            if data["nums"] and re.search(r"=?", prompt):
                 # Heuristic: if numbers exist and answer is numeric, moderate confidence
                 if re.search(r"\d+", answer):
                     base_conf = 0.7
            else:
                # Purely semantic or ambiguous
                base_conf = 0.3

        # Apply Meta Cap
        final_conf = min(base_conf, meta_cap)
        
        # Never return > 0.9 unless it's a hard calculation (handled by high feasibility + low meta-cap override)
        # If meta_cap is low (ambiguity), final_conf is low.
        
        return float(np.clip(final_conf, 0.0, 0.95))
```

</details>
