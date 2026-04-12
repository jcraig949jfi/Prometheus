# Thermodynamics + Neuromodulation + Counterfactual Reasoning

**Fields**: Physics, Neuroscience, Philosophy
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T13:27:13.331095
**Report Generated**: 2026-04-01T20:30:42.918633

---

## Nous Analysis

**Algorithm**  
We parse each prompt and candidate answer into a set of *propositional nodes* \(P_i\). Each node stores: polarity (True/False/Unknown), modality (conditional, negation, comparative, causal, numeric), a numeric value if present, and a list of incoming edges representing logical dependencies (modus ponens, transitivity, causal do‑calculus). All nodes are placed in a NumPy array \(X\in\{0,1,‑1\}^{N}\) where 1 = True, ‑1 = False, 0 = Unknown.  

An *energy* vector \(E\) is initialized as the sum of local penalties:  
- \(E_i = 0\) if the node’s assignment satisfies its internal constraints (e.g., a comparative “5 > 3” is true),  
- \(E_i = 1\) otherwise (violation).  

Constraint propagation updates energies via a weighted adjacency matrix \(W\) (derived from edge types):  
\[
E^{(t+1)} = \sigma\bigl(g \odot (W^\top E^{(t)}) + b\bigr)
\]  
where \(\sigma\) is a piecewise‑linear clamp to \([0,1]\), \(b\) a bias term, and \(g\) a *neuromodulatory gain* vector. \(g\) assigns higher step‑size to nodes tagged with dopaminergic‑like reward signals (e.g., assertions that improve answer coherence) and lower step‑size to serotonergic‑like stability nodes (e.g., background facts). Iteration continues until \(\|E^{(t+1)}-E^{(t)}\|_1<\epsilon\).  

For *counterfactual reasoning*, we generate a bounded set of worlds \(\mathcal{W}\) by applying Pearl‑style \(do()\) interventions: for each world we flip the truth value of a randomly selected subset of nodes (size ≤ k) and recompute the relaxed energy using the same propagation step. The probability of a world is given by a softmax over negative energies, modulated by the gain vector:  
\[
P(w)=\frac{\exp(-\gamma\, g^\top E_w)}{\sum_{w'}\exp(-\gamma\, g^\top E_{w'})}
\]  
with temperature \(\gamma\).  

A candidate answer \(A\) is scored by its expected energy across worlds:  
\[
\text{Score}(A)=-\sum_{w\in\mathcal{W}} P(w)\, \bigl\|X_A\odot (1-X_w)\bigr\|_1
\]  
Lower expected energy (higher score) indicates the answer is consistent with the most probable counterfactual scenarios.

**Structural features parsed**  
Negations (“not”, “never”), comparatives (“greater than”, “less than”), conditionals (“if … then …”, “unless”), causal verbs (“because”, “leads to”, “results in”), numeric values and units, ordering relations (“more … than”, “first … then”), and temporal markers (“before”, “after”). These are extracted via regex‑based patterns that populate the proposition fields.

**Novelty**  
Pure‑algorithm scorers typically use hash similarity, bag‑of‑words, or simple rule‑based matching. Energy‑based constraint propagation appears in Probabilistic Soft Logic, but the addition of a neuromodulatory gain‑controlled update rule and explicit generation of counterfactual worlds via do‑calculus is not present in existing open‑source QA evaluation tools. Thus the combination is novel.

**Rating**  
Reasoning: 8/10 — The algorithm captures logical consistency, uncertainty, and alternative scenarios via principled energy minimization and gain‑modulated belief propagation.  
Metacognition: 6/10 — It can self‑adjust update strengths via the gain vector, but lacks explicit monitoring of its own convergence or uncertainty estimation.  
Hypothesis generation: 7/10 — Counterfactual world generation provides a mechanism for hypothesizing alternative conditions, though limited to bounded intervention sets.  
Implementability: 9/10 — All components rely solely on NumPy operations and standard‑library regex; no external models or APIs are required.

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
**Reason**: trap_battery_failed (acc=39% cal=47% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-01T19:22:45.230230

---

## Code

**Source**: scrap

[View code](./Thermodynamics---Neuromodulation---Counterfactual_Reasoning/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A computational reasoning tool combining thermodynamic energy minimization,
    neuromodulatory gain control, and counterfactual world simulation with
    dynamical systems stability analysis.
    
    Mechanism:
    1. Parses prompts into propositional nodes (True/False/Unknown) with modalities.
    2. Constructs an energy landscape where violations of logic/constraints add energy.
    3. Applies neuromodulatory gains (Dopamine=high update for coherence, Serotonin=stability).
    4. Simulates counterfactual worlds via do-calculus interventions.
    5. Evaluates dynamical stability (Lyapunov-like) of the solution trajectory.
    6. Scores candidates based on expected energy across worlds and trajectory stability.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|only if|provided)\b', re.I),
            'causal': re.compile(r'\b(because|causes|leads to|results in|due to)\b', re.I),
            'numeric': re.compile(r'-?\d+(?:\.\d+)?'),
            'presupposition': re.compile(r'\b(have you stopped|why did|when did|quit)\b', re.I),
            'scope_ambiguity': re.compile(r'\b(every|all|each).*\b(a|an|the)\b', re.I),
            'pronoun_ambiguity': re.compile(r'\b(he|she|him|her|they)\b.*\b(who|whom)\b', re.I),
            'false_dichotomy': re.compile(r'\b(either|or|but not|must be)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|beautiful|ugly)\b', re.I)
        }
        
        # Neuromodulatory gains (Dopamine for coherence, Serotonin for facts)
        self.g_dopamine = 1.5  # High gain for logical consistency updates
        self.g_serotonin = 0.5 # Low gain for static fact retention
        self.gamma = 0.5       # Temperature for softmax
        self.epsilon = 1e-4    # Convergence threshold

    def _extract_nodes(self, text: str) -> List[Dict]:
        """Parse text into propositional nodes with modality and polarity."""
        nodes = []
        text_lower = text.lower()
        
        # Check modalities
        has_neg = bool(self.patterns['negation'].search(text))
        has_comp = bool(self.patterns['comparative'].search(text))
        has_cond = bool(self.patterns['conditional'].search(text))
        has_causal = bool(self.patterns['causal'].search(text))
        
        # Extract numbers
        nums = [float(n) for n in self.patterns['numeric'].findall(text)]
        
        # Determine base polarity and modality
        modality = 'assertion'
        if has_neg: modality = 'negation'
        elif has_comp: modality = 'comparative'
        elif has_cond: modality = 'conditional'
        elif has_causal: modality = 'causal'
        
        # Simple heuristic for polarity based on keywords
        polarity = 1 # True
        if has_neg:
            # Crude check: if "not" is near start or dominates, flip
            if text_lower.count('not') % 2 == 1:
                polarity = -1
        
        nodes.append({
            'text': text[:50], # Truncate for storage
            'polarity': polarity,
            'modality': modality,
            'values': nums,
            'energy': 0.0,
            'gain': self.g_dopamine if (has_cond or has_causal) else self.g_serotonin
        })
        
        # Add implicit constraint nodes for numbers if present
        if len(nums) >= 2:
            nodes.append({
                'text': f"numeric_constraint_{nums[0]}_vs_{nums[1]}",
                'polarity': 1 if nums[0] > nums[1] else -1, # Placeholder logic
                'modality': 'numeric',
                'values': nums,
                'energy': 0.0,
                'gain': self.g_serotonin
            })
            
        return nodes if nodes else [{'text': 'empty', 'polarity': 0, 'modality': 'unknown', 'values': [], 'energy': 0.0, 'gain': 1.0}]

    def _compute_energy(self, nodes: List[Dict], candidate: str) -> float:
        """Compute local energy penalties based on candidate consistency."""
        total_energy = 0.0
        candidate_lower = candidate.lower()
        
        for i, node in enumerate(nodes):
            penalty = 0.0
            val = node['polarity']
            
            # Check consistency with candidate
            if node['modality'] == 'negation':
                # If node is negated, candidate should reflect opposition or absence
                if 'not' in candidate_lower or 'no' in candidate_lower:
                    penalty = 0.0 # Consistent
                else:
                    penalty = 0.5 # Potential conflict depending on context
                    
            elif node['modality'] == 'numeric' and len(node['values']) >= 2:
                # Evaluate numeric constraint
                v1, v2 = node['values'][0], node['values'][1]
                expected_true = v1 > v2
                
                # Check if candidate affirms the truth
                cand_affirms = any(k in candidate_lower for k in ['true', 'yes', 'correct', 'greater', 'higher'])
                cand_denies = any(k in candidate_lower for k in ['false', 'no', 'incorrect', 'less', 'lower'])
                
                if expected_true:
                    if cand_denies: penalty = 1.0
                    elif cand_affirms: penalty = 0.0
                    else: penalty = 0.5 # Unknown
                else:
                    if cand_affirms: penalty = 1.0
                    elif cand_denies: penalty = 0.0
                    else: penalty = 0.5

            elif node['modality'] in ['assertion', 'causal']:
                # Simple keyword overlap penalty reduction (weak coupling)
                words = set(re.findall(r'\w+', node['text'].lower()))
                cand_words = set(re.findall(r'\w+', candidate_lower))
                overlap = len(words & cand_words)
                if overlap == 0 and len(words) > 2:
                    penalty = 0.2 # Slight penalty for irrelevance
            
            total_energy += penalty * node['gain']
            
        return total_energy

    def _propagate_energy(self, nodes: List[Dict], candidate: str, iterations: int = 5) -> float:
        """Simulate energy propagation with neuromodulatory gains."""
        if not nodes:
            return 1.0
            
        E = np.array([self._compute_energy([n], candidate) for n in nodes])
        G = np.array([n['gain'] for n in nodes])
        
        # Construct simple adjacency (fully connected for small N, or sequential)
        N = len(nodes)
        W = np.ones((N, N)) * 0.1
        np.fill_diagonal(W, 0)
        
        for _ in range(iterations):
            # E_new = sigma(g * (W^T E) + bias)
            # Bias is local energy, W^T E is neighbor influence
            local_E = np.array([self._compute_energy([nodes[i]], candidate) for i in range(N)])
            neighbor_E = W.T @ E
            update = G * (neighbor_E + local_E)
            
            # Clamp [0, 1]
            E = np.clip(update, 0, 1)
            
            if np.linalg.norm(E - local_E, 1) < self.epsilon:
                break
                
        return float(np.sum(E))

    def _generate_counterfactuals(self, nodes: List[Dict], candidate: str, k: int = 2) -> List[List[Dict]]:
        """Generate bounded set of counterfactual worlds by flipping node polarities."""
        worlds = [nodes] # Base world
        
        if len(nodes) == 0:
            return worlds
            
        # Generate k interventions
        for i in range(min(k, len(nodes))):
            world_copy = []
            for j, n in enumerate(nodes):
                new_n = n.copy()
                # Flip polarity for the i-th node in this world
                if j == i:
                    new_n['polarity'] = -n['polarity'] if n['polarity'] != 0 else 1
                world_copy.append(new_n)
            worlds.append(world_copy)
            
        return worlds

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        denom = max(len_s1, len_s2)
        if denom == 0:
            return 0.0
        return (len_both - min(len_s1, len_s2)) / denom

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns low confidence if prompt exhibits ambiguity, presupposition, or unanswerability.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        
        # 2. Scope Ambiguity (simplified heuristic)
        if self.patterns['scope_ambiguity'].search(p_lower) and 'same' in p_lower:
            return 0.3
            
        # 3. Pronoun Ambiguity
        if self.patterns['pronoun_ambiguity'].search(p_lower):
            return 0.25
            
        # 4. False Dichotomy indicators without clear options
        if self.patterns['false_dichotomy'].search(p_lower) and 'or' in p_lower:
            # If it looks like a forced choice without data
            if not any(c.isdigit() for c in p_lower):
                return 0.3
                
        # 5. Subjectivity
        if self.patterns['subjectivity'].search(p_lower):
            return 0.4 # Subjective questions are hard to be "definitive" on
            
        # 6. Unanswerability (No verbs, no numbers, very short)
        words = re.findall(r'\w+', p_lower)
        if len(words) < 3:
            return 0.2
            
        return 1.0 # Default to high potential confidence if structure is sound

    def _dynamics_tracker(self, prompt: str, candidate: str) -> Tuple[float, float]:
        """
        Frame C: Dynamics Tracker.
        Models reasoning as a state evolution.
        Returns (stability_score, convergence_rate).
        """
        # Discretize prompt into premises (split by period or conjunction)
        segments = re.split(r'[.;]', prompt)
        segments = [s.strip() for s in segments if s.strip()]
        
        if len(segments) < 2:
            return 0.9, 1.0 # Trivially stable
            
        state_history = []
        current_state = 0.0
        
        # Simulate sequential processing
        for i, seg in enumerate(segments):
            # State update: simple accumulation of semantic weight
            # In a real system, this would be vector rotation. Here we use energy delta.
            local_energy = self._compute_energy(self._extract_nodes(seg), candidate)
            # Update state (inverse of energy)
            current_state += (1.0 - local_energy) * 0.1
            
            # Add noise sensitivity check (Lyapunov exponent approximation)
            perturbed_state = current_state + np.random.normal(0, 0.01)
            divergence = abs(current_state - perturbed_state)
            
            state_history.append({
                'step': i,
                'state': current_state,
                'divergence': divergence
            })
            
        if len(state_history) < 2:
            return 0.5, 0.5
            
        # Calculate stability (inverse of average divergence)
        avg_div = np.mean([s['divergence'] for s in state_history])
        stability = 1.0 / (1.0 + avg_div * 10)
        
        # Calculate convergence (variance of state changes)
        changes = [abs(state_history[i]['state'] - state_history[i-1]['state']) 
                   for i in range(1, len(state_history))]
        convergence_rate = 1.0 / (1.0 + np.var(changes)) if len(changes) > 1 else 1.0
        
        return stability, convergence_rate

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-check meta-confidence for the whole prompt
        # If the prompt itself is garbage/ambiguous, all candidates get low scores
        prompt_meta_conf = self._meta_confidence(prompt)
        
        # Extract global nodes
        global_nodes = self._extract_nodes(prompt)
        worlds = self._generate_counterfactuals(global_nodes, "", k=2)
        
        for cand in candidates:
            # 1. Structural & Energy Scoring
            total_expected_energy = 0.0
            world_probs = []
            
            # Calculate probabilities for each world (softmax of negative energy)
            energies = []
            for w in worlds:
                e = self._propagate_energy(w, cand, iterations=3)
                energies.append(e)
            
            # Softmax
            exp_energies = np.exp(-np.array(energies) * self.gamma)
            probs = exp_energies / np.sum(exp_energies)
            
            # Expected Energy
            score_energy = -np.sum(probs * np.array(energies))
            
            # 2. Dynamics Scoring (Stability)
            stability, conv_rate = self._dynamics_tracker(prompt, cand)
            
            # 3. NCD Tiebreaker (Max 15% influence)
            ncd_score = 1.0 - self._calculate_ncd(prompt, cand)
            
            # Combine Scores
            # Weighting: Energy (40%), Dynamics (45%), NCD (15%)
            # Note: Energy is negative (lower is better), so we invert for scoring
            raw_score = (0.40 * (1.0 - min(1.0, max(0, score_energy / 5.0)))) + \
                        (0.45 * stability * conv_rate) + \
                        (0.15 * ncd_score)
            
            # Apply Meta-Confidence Cap (Epistemic Honesty)
            # If the prompt is ambiguous, the max possible score is capped
            raw_score = min(raw_score, prompt_meta_conf)
            
            results.append({
                "candidate": cand,
                "score": float(raw_score),
                "reasoning": f"Energy: {score_energy:.2f}, Stability: {stability:.2f}, Meta-Conf: {prompt_meta_conf:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at meta-confidence limit.
        """
        # 1. Meta-Confidence Check (Tier B)
        meta_conf = self._meta_confidence(prompt)
        
        # 2. Compute internal score components
        nodes = self._extract_nodes(prompt + " " + answer)
        energy = self._propagate_energy(nodes, answer, iterations=5)
        stability, _ = self._dynamics_tracker(prompt, answer)
        
        # Base confidence from energy and stability
        # Low energy + High stability = High confidence
        base_conf = (1.0 - min(1.0, energy / 5.0)) * 0.6 + (stability * 0.4)
        
        # 3. Apply Cap
        final_conf = min(base_conf, meta_conf)
        
        # Ensure strict bounds
        return float(np.clip(final_conf, 0.0, 0.99))
```

</details>
