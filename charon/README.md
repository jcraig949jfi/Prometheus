# Charon: Geometric Embedding for Arithmetic Correspondences

> **DATA MIGRATION (2026-04-16):** `charon/data/charon.duckdb` has been fully migrated to Postgres (prometheus_fire) and Redis. The DuckDB file remains as a read-only archive. Scripts in `src/` and `tests/` still import duckdb — see `src/DUCKDB_NOTICE.md` for how to update them if re-running.

> **Charon** investigates whether geometric proximity in a mathematical embedding space can predict discrete Langlands-type correspondences in arithmetic. A rigorous, test-driven system for exploring whether continuous metrics can capture the discrete structure of the Langlands program.

## Mission

**Question**: Does any computable representation of arithmetic objects (elliptic curves, modular forms, L-functions) admit a metric under which continuous proximity predicts discrete correspondence?

**Approach**: Build a geometrically embedded database of ~133,000 arithmetic objects where the proximity structure reflects genuine arithmetic relationships. Test empirically whether this hypothesis is viable before scaling.

**Core Principle**: Test-driven discovery (TDD) with pre-set thresholds and binary kill conditions. Failures are classified and routed back to design stages—the system is built to fail fast and learn why.

---

## Architecture Overview

Charon implements a **closed-loop, 5-stage discovery system**:

```
Stage 1: The Crossing (Ingestion)
         LMFDB PostgreSQL → DuckDB with universal invariant vectors
                 ↓
Stage 2: Landscape Construction (Embedding)
         Vectors → k-NN similarity → Spectral embedding → 16D coordinates
                 ↓
Stage 3: Rigorous Testing (TDD Battery)
         4-layer test suite with pre-set thresholds and kill conditions
                 ↓
Stage 4: Failure Classification & Loop
         Route failures back to appropriate stage (data, encoding, embedding, or genuine negative)
                 ↓
Stage 5: Hypothesis Generation
         Extract top-N geometric proximity pairs without known bridges
         Queue for human-in-the-loop expert review
```

---

## Data & Scope

### **Objects**
- **Elliptic Curves**: ~31,073 curves from Cremona database (conductor ≤ 50,000)
- **Modular Forms**: ~102,150 weight-2 newforms (conductor ≤ 50,000)
- **L-functions**: Degree-2 L-functions from curve and form data
- **Known Bridges**: 17,314 modularity theorem pairs (EC isogeny class ↔ weight-2 newform)

### **Universal Invariant Representation**
All objects encoded as **Dirichlet coefficients a_p** for the first 50 primes (2, 3, 5, …, 229):
- Elliptic curves: 25 primes (Cremona completeness limit)
- Modular forms: 50 primes
- Represents the "discrete label" of the object's L-function
- Phase 1 uses shared 25 dimensions to handle dimension mismatch

### **Database Schema**
- `objects` — Central store: all objects + invariant vectors + completeness flags
- `elliptic_curves` — EC metadata: rank, torsion, j-invariant, isogeny class
- `modular_forms` — MF metadata: weight, level, Hecke eigenvalues, Sato-Tate group
- `l_functions` — L-function layer: conductor, root number, zeros, Dirichlet coefficients
- `known_bridges` — Ground truth correspondences (modularity, Langlands, Galois)
- `landscape` — Embedded coordinates, local curvature, cluster IDs, k-NN neighbors
- `hypothesis_queue` — Candidate discoveries (geometric proximity, no known bridge)
- `failure_log` — Closed-loop diagnostics: failures, classification, routing

---

## Phase 1 Results (2026-04-01)

### **Bridge Recovery**
✅ **100% (17,314/17,314)** — All known modularity theorem pairs recovered as nearest neighbors

### **TDD Battery**

| Test | Layer | Outcome | Finding |
|------|-------|---------|---------|
| **0.2: Isogeny Coherence** | Sanity | ✅ PASS | Data clean, ingest infrastructure works |
| **0.3: Trivial Dominance** | Sanity | ❌ FAIL | Coefficient AUC 1.0 vs. metadata AUC 0.84 (ratio exceeds 0.80 threshold) |
| **1.1: Separability** | Metric | ✅ PASS | True pairs at distance ~0, non-pairs at ~47, perfect separation (Cohen's d=11.54) |
| **1.3: Conductor Conditioning** | Metric | ❌ FAIL | ARI = 0.008 against rank/torsion/CM (random noise) |

### **Critical Diagnosis**

**The coefficient vectors encode a single bit of information**: "same L-function or not."
- Matching pairs: distance ≈ 0
- Non-matching pairs: distance ≈ 47 (regardless of arithmetic similarity)
- **No continuous geometric structure** exists in coefficient space

**Implication**: This is a **LOOKUP INDEX**, not a **COORDINATE SYSTEM**.
- The 100 candidates in hypothesis_queue are conductor neighbors (false positives)
- Scaling to conductor 50K would only enlarge a lookup index
- The closed loop worked as designed: caught fundamental flaw before wasting weeks on scaling

---

## Three Directions Forward

### **Direction 1: Enrich the Coefficient Vector** (Incremental)
*Estimated effort: 2–3 days*

Improve coefficient representation without changing the representation paradigm:
- Ramanujan normalize: a_p → a_p / p^{(k-1)/2}
- Include prime-power terms: a_{p²}, a_{p³}
- Append root number (±1), analytic rank, degree
- **Status**: Achievable from LMFDB data
- **Risk**: Doesn't solve metric continuity problem; less lossy but still fundamentally discrete

### **Direction 2: Low-lying Zeros as Coordinates** (Significant Upgrade)
*Estimated effort: 1–2 weeks*

Use first 20 zeros of L-function instead of truncated Dirichlet coefficients:
- **Mathematical grounding**: Zeros are global invariants; Katz-Sarnak connects zero distributions to symmetry type
- **Should exhibit continuous variation** between non-corresponding objects (unlike coefficients)
- **Test immediately**: Run Test 1.3 (conductor conditioning) on zeros; expect ARI > 0.3 if viable
- **Risk**: Zeros still truncated; conductor-dependent; requires L-function computation

### **Direction 3: Embed the Known Relationship Graph** (Fundamental Reframing)
*Estimated effort: 3–4 weeks*

Embed LMFDB's explicit relationship structure, not coefficient similarity:
- Use isogenies, Hecke correspondences, Galois orbits, base change
- Apply spectral graph embedding to the *known* relationship graph
- Resulting coordinates guaranteed to respect known arithmetic structure by construction
- **Advantage**: Mathematical provenance; addresses continuous-discrete tension directly
- **Challenge**: Extracting the relationship graph cleanly from LMFDB is non-trivial

---

## Design Principles

1. **Test-Driven Design**
   - Write tests before seeing results
   - Pre-set thresholds; no post-hoc tuning
   - Binary pass/fail outcomes only

2. **Forcing Principle**
   - Every test has explicit kill conditions
   - No "promising" or "marginal" results
   - Prevents motivated reasoning and scope creep

3. **Representation is Research**
   - Embedding method (PCA, spectral, UMAP) is tuning
   - Representation (which features) is the real question
   - Test the representation before debugging the embedding

4. **Closed-Loop Diagnostics**
   - Every failure classified and routed back to appropriate stage
   - Failure log drives iteration
   - System designed to fail *informatively*

5. **Brutally Honest Framing**
   - Explicitly states what it does NOT do (discovery, navigation)
   - Tests falsifiable hypotheses
   - Reports negative results as scientific progress

---

## Project Structure

```
charon/
├── README.md                          (this file)
├── data/
│   └── charon.duckdb                 (queryable local database)
├── src/
│   ├── ingest.py                     (LMFDB → DuckDB pipeline)
│   ├── embed.py                      (Vectors → landscape transformation)
│   ├── schema.py                     (DuckDB initialization)
│   └── config.py                     (Configuration management)
├── tests/
│   ├── test_03_trivial_dominance.py  (Kill test for coefficient representation)
│   ├── test_11_separability.py       (Metric validity)
│   ├── test_13_conductor_conditioning.py (Continuous structure detection)
│   └── zero_battery.py               (Tests for Direction 2)
├── scripts/
│   ├── run_phase1.sh                 (Complete Phase 1 pipeline)
│   └── status.sh                     (Pipeline status check)
├── reports/
│   ├── first_crossing_2026-04-01.md  (Ingestion + embedding results)
│   ├── battery_results_2026-04-01.md (TDD test outcomes)
│   └── phase1_analysis.md            (Detailed findings and next steps)
└── docs/
    ├── DESIGN.md                     (Detailed design documentation)
    ├── MATHEMATICS.md                (Mathematical foundations)
    └── TESTING.md                    (TDD battery and kill conditions)
```

---

## Configuration

**File**: `src/config.py`

Key parameters:
- **LMFDB Connection**: PostgreSQL at `devmirror.lmfdb.xyz:5432`
- **Phase 1 Conductor Cap**: 50,000
- **Batch Size**: 5,000 rows per LMFDB fetch
- **Embedding Dimension**: 16
- **k-NN**: k=30 nearest neighbors
- **Quality Gate**: 80% bridge recovery target

---

## Running the System

### **Complete Phase 1**
```bash
cd charon
bash scripts/run_phase1.sh
```

Executes all 5 stages end-to-end. Outputs reports to `reports/`.

### **Check Status**
```bash
bash scripts/status.sh
```

Shows pipeline progress, database stats, and test results.

### **Run Individual Stages**

```bash
# Stage 1: Ingest from LMFDB
python src/ingest.py

# Stage 2: Build landscape
python src/embed.py

# Stage 3: Run tests
python -m pytest tests/

# Stage 5: Generate hypothesis queue
python scripts/generate_queue.py
```

### **Query the Database**
```bash
# Directly via DuckDB
duckdb data/charon.duckdb

# Example: Find objects nearest to a given elliptic curve
SELECT * FROM landscape 
WHERE object_id = 'EC_123456'
ORDER BY nearest_distance
LIMIT 10;
```

---

## Key Findings & Insights

### **What Went Right**
✅ Ingest infrastructure is robust — cleanly loaded 133K+ objects from LMFDB  
✅ Bridge recovery is perfect — all 17K known correspondences recovered as NN  
✅ System design works — TDD caught fundamental problem before expensive scaling  

### **What Failed**
❌ Coefficient vectors are fundamentally discrete — no continuous geometric structure  
❌ False positive rate is 100% — hypothesis queue is all conductor neighbors  
❌ Current representation cannot support the hypothesis

### **What We Learned**
- **Representation is the bottleneck**, not embedding or similarity method
- **A discrete "same/different" bit cannot support continuous proximity search**
- **The forcing principle works**: kill conditions prevented wasted effort on scaling
- **Directed failures are progress**: knowing what doesn't work narrows possibilities

---

## Next Steps

### **Immediate (This Week)**
1. Run Direction 2 (zeros) with Test 1.3
2. Define passing threshold BEFORE seeing results
3. Decide: Continue with zeros or pivot to Direction 1 enrichment?

### **Short-term (Next 2 Weeks)**
- Implement Direction 1 as fallback strategy
- If Direction 2 shows promise (ARI > 0.3), scale zero computation

### **Medium-term (Next 4 Weeks)**
- Extract LMFDB relationship graph for Direction 3
- Begin spectral graph embedding infrastructure

### **If Representation Improves**
- Scale to conductor 50,000
- Re-run full TDD battery
- Proceed to HITL expert review of hypothesis queue

---

## Important Design Constraints

1. **Isogeny Class Deduplication**: One representative per class to avoid crowding out cross-type neighbors

2. **Dimension Mismatch**: EC aplist = 25 primes; MF hecke_nf = 50 primes. Phase 1 uses shared 25 dimensions; full deployment will need careful handling

3. **Tie-Breaking in k-NN**: When vectors have distance exactly 0 (true matches), check all k positions, not just position 0

4. **Conductor as Null Hypothesis**: Conductor explains clustering structure; if representation success rate is <90% vs. conductor alone, return to design stage

5. **Forced Binary Outcomes**: Tests must decisively reject or accept, never "marginal"

---

## Mathematical Background

### **The Langlands Program**
A fundamental conjecture relating:
- **Arithmetic objects**: Elliptic curves, modular forms, Galois representations
- **Discrete correspondences**: Modularity theorem, base change, functoriality
- **Open question**: Can continuous geometry capture discrete correspondence?

### **Why Coefficient Vectors?**
The Dirichlet coefficients a_p of an L-function encode its "analytic signature":
- For elliptic curves: Coefficients determined by Frobenius traces
- For modular forms: Coefficients are Hecke eigenvalues
- Universal coordinate system: Works across object types (EC, MF, L-function)

### **Why It Failed**
- Coefficients are **integer-valued** (or rational) — discrete by nature
- Matching objects have a_p = b_p exactly (distance 0)
- Non-matching objects differ at some prime p (distance > 1)
- No gradient; no continuous variation between near-misses

### **Why Zeros Might Work**
- L-function zeros are **real numbers** — continuous by nature
- Non-matching objects have *similar* (not identical) zero distributions (Katz-Sarnak)
- Expected: Continuous gradual variation, not discrete jump

---

## References & Resources

- **LMFDB**: L-functions and Modular Forms Database (https://www.lmfdb.org/)
- **Cremona Database**: Elliptic curves by conductor (https://johncremona.github.io/ecdata/)
- **Katz-Sarnak Conjecture**: Zero distribution statistics and random matrix theory
- **Modularity Theorem**: Wiles et al., foundational for modern arithmetic geometry

---

## Contact & Attribution

**System Design**: Charon (Prometheus pipeline)  
**Test Suite**: Rigorous TDD methodology inspired by software engineering best practices applied to mathematical empiricism

---

## License

Part of the Prometheus system. Subject to project licensing.

---

## Disclaimer

**Charon is NOT:**
- ✗ A "discovery engine" claiming new Langlands correspondences
- ✗ A "Langlands landscape navigator"
- ✗ A replacement for rigorous mathematical proof
- ✗ A tool for generating unvetted conjectures

**Charon IS:**
- ✓ A hypothesis testing system for representation viability
- ✓ An empirical investigation of a mathematical question
- ✓ A closed-loop failure detection system
- ✓ A foundation for human-expert-in-the-loop review (HITL)

Results require expert mathematical interpretation and rigorous proof before publication.
