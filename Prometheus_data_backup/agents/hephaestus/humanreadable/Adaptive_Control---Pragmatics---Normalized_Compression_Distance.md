# Adaptive Control + Pragmatics + Normalized Compression Distance

**Fields**: Control Theory, Linguistics, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T13:21:57.870308
**Report Generated**: 2026-03-31T14:34:56.052003

---

## Nous Analysis

**Algorithm**  
The tool builds a lightweight logical‑form representation of each text using only regex‑based extraction. Each extracted pattern becomes a *proposition* object:  
`{type: str, vars: tuple, polarity: bool}` where `type` ∈ {`neg`, `comp`, `cond`, `caus`, `num`, `order`}. All propositions from a prompt and a candidate answer are stored in two lists, `P_ref` and `P_cand`.  

A weight vector `w` (same length as the set of types) modulates the influence of each proposition class. Initially `w = [1,1,1,1,1,1]`. After each scoring batch, an adaptive‑control update treats the weight as a controller parameter:  

```
error = score_target – score_current   # score_target can be a heuristic like length of justification
for i, t in enumerate(types):
    w[i] += η * error * (count_t_in_cand – count_t_in_ref)
    w[i] = clip(w[i], 0.1, 5.0)       # keep weights bounded
```

`η` is a small fixed step (e.g., 0.05). This is a model‑free, gradient‑free self‑tuning regulator.  

To compare the two proposition sets we compute a **Normalized Compression Distance** (NCD) on their serialized forms. Serialization concatenates propositions sorted by type, each encoded as `"type:var1,var2:polarity;"`. The NCD uses the standard library’s `zlib.compress` as the compressor `C(x)`.  

```
NCD(A,B) = (C(AB) – min(C(A),C(B))) / max(C(A),C(B))
```

We compute a weighted NCD:  

```
score = 1 – Σ_t w[t] * NCD(C_t(A), C_t(B)) / Σ_t w[t]
```

where `C_t` extracts only propositions of type `t` before compression. The final score lies in `[0,1]`; higher means the candidate aligns better with the reference under the current pragmatic‑adaptive weighting.

**Structural features parsed**  
- Negations (`not`, `no`, `-`)  
- Comparatives (`greater than`, `<`, `>`, `equal`)  
- Conditionals (`if … then …`, `unless`)  
- Causal claims (`because`, `leads to`, `results in`)  
- Numeric values and units (`3 km`, `20%`)  
- Ordering relations (`before`, `after`, `first`, `last`)  
- Quantifiers (`all`, `some`, `none`) – treated as a subtype of `comp`.

**Novelty**  
Pure NCD‑based similarity exists (e.g., Li et al., 2004) and logic‑guided scoring appears in semantic‑parsers, but the tight loop where an adaptive‑control regulator continuously re‑weights proposition types based on scoring error, while pragmatic enrichment adds implicit propositions via Grice‑style rules, has not been combined in a purely algorithmic, numpy‑only tool. Hence the combination is novel.

**Ratings**  
Reasoning: 7/10 — captures logical structure and adapts weights, but relies on hand‑crafted regex and simple error signal.  
Metacognition: 5/10 — the controller offers basic self‑adjustment, yet lacks higher‑order monitoring of its own assumptions.  
Hypothesis generation: 4/10 — implicit propositions are generated via fixed pragmatic rules, not open‑ended hypothesis search.  
Implementability: 9/10 — uses only regex, numpy (for vector ops), and zlib; no external libraries or training needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 4/10 |
| Implementability | 9/10 |
| **Composite** | **5.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
