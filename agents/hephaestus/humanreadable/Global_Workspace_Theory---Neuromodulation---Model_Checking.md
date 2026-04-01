# Global Workspace Theory + Neuromodulation + Model Checking

**Fields**: Cognitive Science, Neuroscience, Formal Methods
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T22:41:12.346859
**Report Generated**: 2026-03-31T16:23:53.924778

---

## Nous Analysis

**Algorithm: Workspace‑Modulated Model Checker (WMMC)**  
The candidate answer is first parsed into a finite‑state transition system (FTS) whose states represent propositions extracted from the text (e.g., “X > Y”, “¬P”, “if A then B”). Each proposition becomes a Boolean variable; transitions encode elementary inference steps (modus ponens, transitivity, arithmetic substitution). The global workspace is a set W ⊆ {Vars} that holds the currently “ignited” propositions – those that have broadcast access to all other modules. Neuromodulation supplies a gain vector g ∈ ℝⁿ (n = |Vars|) that scales the probability of a variable entering W; gains are updated by simple Hebbian‑like rules: if a variable participates in a successful inference step, its gain increases Δg = η·reward, otherwise it decays g←γ·g (0 < γ < 1, η ∈ (0,1]).  

**Data structures**  
- `props: Dict[str, int]` maps each proposition to an index.  
- `transitions: List[Tuple[Tuple[int,...], int]]` where the left side is a tuple of source‑state indices (premises) and the right side is the consequent index.  
- `gain: np.ndarray` shape (n,).  
- `workspace: np.ndarray` Boolean mask (n,) indicating ignition.  

**Operations**  
1. **Parsing** – regex extracts atomic predicates, comparatives, negations, conditionals, and numeric constraints; each yields a proposition and possibly a transition (e.g., “A > B ∧ B > C → A > C”).  
2. **Ignition step** – compute activation a = gain · workspace (element‑wise). Select top‑k propositions with highest a to add to W (set workspace mask).  
3. **Model checking** – breadth‑first explore the FTS from initial states (given facts) using only propositions currently in W as allowed labels. If a transition’s premises are all in W, its consequent is added to W (for the next iteration). Continue until fixed point or depth limit D.  
4. **Scoring** – reward = |{goal propositions reached}| / |{goal propositions}|. Update gains per Hebbian rule; final score is the average reward over T = 5 ignition cycles.  

**Structural features parsed**  
- Negations (`not`, `no`) → ¬p.  
- Comparatives (`>`, `<`, `≥`, `≤`, `equal`) → arithmetic propositions.  
- Conditionals (`if … then …`) → implication transitions.  
- Causal verbs (`causes`, `leads to`) → treated as conditionals.  
- Numeric values and units → enable arithmetic substitution transitions.  
- Ordering relations (`first`, `before`, `after`) → temporal precedence transitions.  

**Novelty**  
The combination mirrors existing neuro‑cognitive architectures (Global Workspace + neuromodulatory gain) but couples them to an explicit model‑checking backend, which is uncommon in pure‑Python reasoning scorers. Prior work uses either symbolic theorem provers or similarity‑based metrics; WMMC adds a dynamic, resource‑limited broadcast mechanism that gates exploration, yielding a novel hybrid scorer implementable with only numpy and stdlib.  

**Ratings**  
Reasoning: 8/10 — captures logical inference and numeric constraints via exhaustive state search, outperforming bag‑of‑words baselines.  
Metacognition: 6/10 — gain modulation provides a rudimentary self‑monitoring of confidence but lacks higher‑order reflection on its own search strategy.  
Hypothesis generation: 7/10 — the ignition step proposes candidate propositions (hypotheses) based on current gains, enabling generation of intermediate lemmas.  
Implementability: 9/10 — relies only on regex, numpy arrays, and BFS; no external libraries or neural components required.

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
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T16:22:31.008203

---

## Code

*No code was produced for this combination.*
