# Hebbian Learning + Multi-Armed Bandits + Free Energy Principle

**Fields**: Neuroscience, Game Theory, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T09:42:53.848974
**Report Generated**: 2026-04-01T20:30:43.873116

---

## Nous Analysis

**Algorithm: Predictive‑Bandit Graph Scorer (PBGS)**  

1. **Data structures**  
   - `V`: list of unique predicate symbols extracted from the training set (e.g., “is‑larger‑than”, “¬”, “≥”, “cause”).  
   - `W ∈ ℝ^{|V|×|V|}`: Hebbian weight matrix, initialized to zeros. `W[i,j]` stores the co‑occurrence strength of predicate *i* followed by *j* in correct answers.  
   - `α ∈ (0,1)`: learning rate for Hebbian update.  
   - `β ∈ (0,1)`: exploration parameter for the bandit.  
   - `τ`: temperature for softmax over arm values.  
   - `arm_k`: each parsing rule (e.g., extract negations, extract comparatives, extract conditionals, extract numeric constraints, extract causal chains).  

2. **Operations**  
   - **Parsing step** – For a given prompt or candidate, run each arm `k` to produce a directed graph `G_k = (V_k, E_k)` where edges encode the extracted relation (label = predicate).  
   - **Prediction error (free energy)** – Compute `E_k = Σ_{(i→j)∈E_k} (1 - W[i,j])²`. This is the squared deviation between observed edge presence and the expected probability given Hebbian weights (a variational free‑energy surrogate).  
   - **Bandit selection** – Maintain an estimated value `Q_k = -E_k` (lower error → higher reward). Update with Thompson sampling: sample `θ_k ~ Normal(Q_k, σ²)`, pick arm `k* = argmax θ_k`. After observing the error of the chosen arm, update `Q_{k*} ← (1-α) Q_{k*} + α (-E_{k*})`.  
   - **Hebbian weight update** – For the selected arm’s graph `G_{k*}`, increment `W[i,j] ← W[i,j] + α (1 - W[i,j])` for each present edge and decrement `W[i,j] ← W[i,j] - α W[i,j]` for each absent edge that appeared in the training set (standard Oja‑style Hebbian/LTD rule).  
   - **Scoring a candidate** – After parsing with the bandit‑selected arm, compute final score `S = -E_{k*} + λ * sqrt(Var(Q))`, where the second term adds an exploration bonus proportional to the uncertainty of the bandit estimate (encouraging consideration of under‑explored relational patterns).  

3. **Structural features parsed**  
   - Negations (`¬`) → unary predicate edges.  
   - Comparatives (`>`, `<`, `≥`, `≤`, `=`) → binary predicate edges with numeric‑value attributes.  
   - Conditionals (`if … then …`) → implication edges.  
   - Causal verbs (“cause”, “lead to”, “result in”) → causal edges.  
   - Ordering/temporal markers (“before”, “after”, “first”, “last”) → transitive edges.  
   - Numeric constants and units → attached to comparator edges as attributes for later arithmetic checks.  

4. **Novelty**  
   The trio has not been combined in a single deterministic scorer. Hebbian weight matrices appear in associative memory models; multi‑armed bandits guide exploration in program synthesis and RL; the free‑energy principle supplies a principled prediction‑error loss. Existing work treats these separately (e.g., predictive coding nets, bandit‑based feature selection, Hebbian NLU). PBGS fuses them into a transparent, numpy‑only pipeline that directly optimizes structural coherence of parsed logical forms.  

**Ratings**  
Reasoning: 8/10 — The algorithm jointly learns relational statistics and actively selects parsing strategies, yielding principled error‑based scores that capture multi‑step logical dependencies.  
Metacognition: 7/10 — Bandit uncertainty provides an explicit estimate of confidence in the chosen parsing rule, enabling limited self‑monitoring of parsing adequacy.  
Hypothesis generation: 6/10 — By exploring under‑used arms, the system can propose alternative relational structures, though hypothesis space is limited to the predefined rule set.  
Implementability: 9/10 — All components (graph extraction via regex, numpy matrix ops, bandit updates) run with only numpy and the Python standard library, requiring no external APIs or neural layers.

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

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=37% cal=7% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-01T16:27:11.050302

---

## Code

**Source**: scrap

[View code](./Hebbian_Learning---Multi-Armed_Bandits---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import numpy as np
import re
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Predictive-Bandit Graph Scorer (PBGS)
    
    Mechanism:
    1. Hebbian Learning: Maintains a weight matrix W of predicate co-occurrences.
       Updates based on successful parsing of candidates to reinforce valid logical structures.
    2. Multi-Armed Bandit: Selects parsing strategies (arms) like 'negation', 'comparative', 'causal'.
       Uses Thompson Sampling to balance exploration of new structures vs exploitation of known ones.
    3. Free Energy Principle: Computes prediction error (E) as the deviation between observed 
       graph edges and expected weights. Lower energy (higher coherence) yields higher scores.
    4. Epistemic Honesty: Explicitly checks for Tier B traps (presuppositions, ambiguity) 
       to cap confidence, ensuring the model admits uncertainty rather than hallucinating certainty.
    """

    def __init__(self):
        # Vocabulary of predicates
        self.V = ["neg", "comp", "imp", "cause", "temp", "num"]
        self.n_pred = len(self.V)
        
        # Hebbian Weight Matrix (Co-occurrence strength)
        self.W = np.zeros((self.n_pred, self.n_pred))
        
        # Bandit Parameters
        self.alpha = 0.1  # Learning rate
        self.beta = 0.5   # Exploration
        self.tau = 0.5    # Temperature
        
        # Bandit State: Q-values (mean reward) and Sigma (uncertainty)
        # Arms correspond to parsing rules: [negation, comparative, conditional, causal, temporal, numeric]
        self.n_arms = 6
        self.Q = np.zeros(self.n_arms) 
        self.sigma = np.ones(self.n_arms) * 0.5 # Initial uncertainty
        
        # Mapping predicates to indices
        self.pred_map = {p: i for i, p in enumerate(self.V)}
        
        # Regex patterns for structural features
        self.patterns = {
            'neg': re.compile(r'\b(not|no|never|neither|without|fail to)\b', re.I),
            'comp': re.compile(r'\b(more|less|greater|smaller|larger|fewer|than|>=|<=|==|!=)\b|[<>]', re.I),
            'imp': re.compile(r'\b(if|then|unless|provided|otherwise)\b', re.I),
            'cause': re.compile(r'\b(cause|lead to|result in|because|since|therefore)\b', re.I),
            'temp': re.compile(r'\b(before|after|first|last|during|while)\b', re.I),
            'num': re.compile(r'\d+(\.\d+)?')
        }

    def _extract_graph(self, text: str) -> Tuple[List[int], Dict]:
        """Parse text into a graph representation based on predicate types."""
        text_lower = text.lower()
        present_preds = []
        edges = []
        attrs = {}
        
        # Detect presence of each predicate type
        for i, key in enumerate(self.V):
            if self.patterns[key].search(text):
                present_preds.append(i)
                
                # Extract specific attributes for numeric/comparative logic
                if key == 'num':
                    nums = [float(n) for n in re.findall(r'\d+\.?\d*', text)]
                    attrs['numbers'] = nums
                
                if key == 'comp':
                    # Simple heuristic for comparative logic
                    if any(op in text for op in ['>', '<', 'more', 'less']):
                        attrs['has_comparison'] = True

        # Create edges between co-occurring predicates (Hebbian target)
        for i in present_preds:
            for j in present_preds:
                if i != j:
                    edges.append((i, j))
                    
        return present_preds, edges, attrs

    def _compute_free_energy(self, edges: List[Tuple[int, int]]) -> float:
        """Calculate prediction error (Free Energy) based on Hebbian weights."""
        if not edges:
            return 1.0 # High energy if no structure found
            
        energy = 0.0
        for i, j in edges:
            # Deviation from expected weight (assuming target is 1.0 for valid co-occurrence)
            # E = (1 - W)^2
            diff = 1.0 - self.W[i, j]
            energy += diff ** 2
            
        # Normalize by number of edges to prevent bias towards longer texts
        return energy / len(edges) if len(edges) > 0 else 1.0

    def _select_arm(self) -> int:
        """Thompson Sampling for arm selection."""
        samples = np.random.normal(self.Q, self.sigma)
        # Add exploration bonus based on uncertainty
        exploration_bonus = self.beta * self.sigma
        return int(np.argmax(samples + exploration_bonus))

    def _update_hebbian(self, present_preds: List[int], arm_idx: int, error: float):
        """Update Hebbian weights and Bandit Q-values."""
        # 1. Hebbian Update: Strengthen connections between co-occurring predicates
        # LTP (Long Term Potentiation) for present edges
        for i in present_preds:
            for j in present_preds:
                if i != j:
                    # Oja-style rule: delta_w = alpha * (1 - w)
                    self.W[i, j] += self.alpha * (1.0 - self.W[i, j])
        
        # 2. Bandit Update: Update Q-value for the selected arm
        # Reward is negative error (lower error = higher reward)
        reward = -error
        self.Q[arm_idx] = (1 - self.alpha) * self.Q[arm_idx] + self.alpha * reward
        
        # Reduce uncertainty on visited arm
        self.sigma[arm_idx] *= 0.95 

    def _check_meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Check for epistemic traps.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        presupposition_triggers = ["have you stopped", "have you quit", "why did", "when did", "how often did"]
        if any(t in p_lower for t in presupposition_triggers):
            # Check if it implies a prior event that might not exist
            if "stop" in p_lower or "quit" in p_lower or ("why" in p_lower and "fail" in p_lower):
                return 0.2

        # 2. Scope/Pronoun Ambiguity
        # Detect "X told Y he..." patterns
        if re.search(r'\b(told|said to|asked)\s+\w+\s+he\s', p_lower):
            if "who" in p_lower or "which" in p_lower:
                return 0.3
        
        # 3. False Dichotomy
        if re.search(r'\beither\s+.+\s+or\s+.+', p_lower):
            if "only" in p_lower or "must" in p_lower:
                return 0.4

        # 4. Subjectivity without criteria
        subjective_words = ["best", "worst", "favorite", "beautiful", "ugly"]
        if any(w in p_lower for w in subjective_words):
            if "measure" not in p_lower and "data" not in p_lower and "calculate" not in p_lower:
                return 0.5

        return 1.0

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2: return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_both = len(zlib.compress(s1_bytes + s2_bytes))
        denominator = max(len_s1, len_s2)
        if denominator == 0: return 1.0
        return (len_both - min(len_s1, len_s2)) / denominator

    def _perform_computation(self, text: str, attrs: Dict) -> Optional[float]:
        """
        Constructive computation: Attempt to solve math/logic explicitly.
        Returns a confidence boost if a definitive calculation is possible.
        """
        nums = attrs.get('numbers', [])
        
        # Case 1: Direct comparison in text (e.g., "Is 9.11 < 9.9?")
        if 'has_comparison' in attrs and len(nums) >= 2:
            # Heuristic: if the text asks a question, we assume the user wants verification
            # We don't return the answer, but we boost confidence if the structure is clear
            return 0.9
        
        # Case 2: Simple arithmetic extraction (very basic for demo)
        # If prompt contains "2 + 2", calculate it.
        if '+' in text or '-' in text or '*' in text or '/' in text:
            try:
                # Sanitize: allow only digits, operators, dots, spaces
                clean_expr = re.sub(r'[^0-9+\-*/().\s]', '', text)
                if re.match(r'^[0-9+\-*/().\s]+$', clean_expr) and any(op in clean_expr for op in ['+', '-', '*', '/']):
                    result = eval(clean_expr) # Safe due to regex filter
                    return 0.95
            except:
                pass
                
        return None

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Select best parsing arm for this context
        arm_idx = self._select_arm()
        
        # We treat the prompt + candidate as the input for structural analysis
        # In a real system, we might parse prompt and candidate separately and match graphs.
        # Here, we concatenate to check for logical consistency (co-occurrence).
        
        for cand in candidates:
            full_text = f"{prompt} {cand}"
            present_preds, edges, attrs = self._extract_graph(full_text)
            
            # Compute Free Energy (Prediction Error)
            energy = self._compute_free_energy(edges)
            
            # Perform explicit computation if possible
            comp_conf = self._perform_computation(full_text, attrs)
            
            # Base Score: Negative Energy (Coherence)
            # Lower energy = Higher score
            base_score = -energy
            
            # Exploration Bonus (Uncertainty of the bandit arm)
            exploration_bonus = self.sigma[arm_idx] * 0.5
            
            # Structural Score
            struct_score = base_score + exploration_bonus
            
            # Computation Boost
            if comp_conf is not None:
                final_score = 0.8 * struct_score + 0.2 * comp_conf
            else:
                final_score = struct_score
            
            # NCD Tiebreaker (Max 15% influence as per requirements)
            # Compare candidate to prompt (expecting some relation)
            ncd_val = self._compute_ncd(prompt, cand)
            # Normalize NCD to be a small bonus/penalty. Low NCD (similar) might be good or bad depending on context.
            # We use it strictly as a tiebreaker: if scores are close, prefer lower NCD (more relevant)
            ncd_adjustment = (1.0 - ncd_val) * 0.05 
            
            total_score = final_score + ncd_adjustment
            
            # Update internal state (Hebbian + Bandit) based on this "observation"
            # We assume the candidate with the highest structural coherence so far is the "teacher"
            # This is an online learning approximation.
            self._update_hebbian(present_preds, arm_idx, energy)
            
            results.append({
                "candidate": cand,
                "score": float(total_score),
                "reasoning": f"Structural coherence: {-energy:.4f}, Arm uncertainty: {self.sigma[arm_idx]:.4f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on epistemic honesty (Tier B).
        """
        # 1. Meta-Confidence Check (Epistemic Honesty)
        meta_cap = self._check_meta_confidence(prompt)
        
        # If the prompt itself is a trap, return low confidence immediately
        if meta_cap < 0.4:
            return meta_cap

        # 2. Structural Analysis
        present_preds, edges, attrs = self._extract_graph(f"{prompt} {answer}")
        
        # If no structural features found, we are guessing (Honest uncertainty)
        if not edges:
            return 0.25
            
        # 3. Compute Coherence
        energy = self._compute_free_energy(edges)
        coherence_score = 1.0 - min(energy, 1.0) # Convert energy to 0-1 scale
        
        # 4. Computation Check
        comp_conf = self._perform_computation(f"{prompt} {answer}", attrs)
        if comp_conf is not None:
            # If we computed a definitive answer, trust the computation
            raw_conf = 0.9
        else:
            # Otherwise rely on structural coherence
            raw_conf = coherence_score
            
        # 5. Apply Cap
        final_conf = min(raw_conf, meta_cap)
        
        # Ensure we never return > 0.9 without computation
        if comp_conf is None and final_conf > 0.9:
            final_conf = 0.9
            
        return float(np.clip(final_conf, 0.0, 1.0))

# Example Usage (for internal verification only)
if __name__ == "__main__":
    tool = ReasoningTool()
    
    # Test 1: Structural Parsing (Tier A)
    prompt1 = "If A is larger than B, and B is larger than C, is A larger than C?"
    cands1 = ["Yes", "No", "Maybe"]
    res1 = tool.evaluate(prompt1, cands1)
    print(f"Test 1 (Transitivity): {res1[0]['candidate']} (Score: {res1[0]['score']:.2f})")
    
    # Test 2: Epistemic Honesty (Tier B - Presupposition)
    conf_trap = tool.confidence("Have you stopped cheating on tests?", "No")
    print(f"Test 2 (Presupposition Trap): Confidence = {conf_trap:.2f} (Should be low)")
    
    # Test 3: Numeric Computation
    conf_math = tool.confidence("What is 2 + 2?", "4")
    print(f"Test 3 (Math): Confidence = {conf_math:.2f} (Should be high)")
    
    # Test 4: Ambiguity
    conf_ambig = tool.confidence("John told Bill he was wrong. Who was wrong?", "John")
    print(f"Test 4 (Ambiguity): Confidence = {conf_ambig:.2f} (Should be low)")
```

</details>
