# Signal Registry — Design Document
## Author: Harmonia, 2026-04-15

## The Problem

Our current architecture has two bins: KILL and SURVIVE. A signal either passes the full battery and enters the finding hierarchy, or it dies and goes to the shadow archive. But with a 39-test battery calibrated at 100.000% on 3.8M objects, the space BETWEEN kill and survive is where the most interesting science lives.

A signal that passes 35/39 tests and dies on F24 (variance decomposition) tells a very different story than one that dies on F1 (permutation null). The first might be real structure with a measurement problem. The second is noise.

## What We Need

Three tiers of signal tracking, all in one registry:

### Tier 1: Calibration Anchors (KNOWN)
Proven theorems we use to calibrate the instrument. These should ALWAYS pass.
- Modularity, Mazur torsion, Hasse bound, etc.
- If any anchor fails, the instrument is broken — stop everything.
- Currently: known_truth_battery.py (180 facts, 100%)

### Tier 2: Specimens (THE NEW THING)
Every signal that shows ANY statistical life, regardless of battery outcome.
Each specimen gets a full profile:

```
specimen:
  id: SPE-0001
  source_problem: MATH-0062  # Which open question produced this
  source_test: oq1_spectral_tail  # Script that generated it
  date_found: 2026-04-15
  date_last_tested: 2026-04-15
  
  # The signal itself
  claim: "EC L-function zero spacing variance correlates with rank"
  effect_size: -0.068  # Spearman rho
  effect_type: correlation
  z_score: -4.28  # vs permutation null
  n_objects: 4000
  
  # Battery profile — THIS IS THE KEY
  battery_profile:
    F1_permutation: {passed: true, z: -4.28, p: 0.0000}
    F2_subset: {passed: true, note: "not run"}
    ...
    F24_variance: {passed: null, note: "not run"}
    ...
    F39_feature_permutation: {passed: null, note: "not applicable"}
  
  tests_passed: 1
  tests_failed: 1  # conductor conditional
  tests_not_run: 37
  
  # Kill analysis
  kill_test: "conductor_conditional"
  kill_mechanism: "Signal disappears within conductor bins (p>0.05 all 4 bins)"
  residual_after_kill: "rho=-0.068 globally but 0 within bins = conductor mediation"
  
  # What would revive it
  revival_conditions:
    - "Signal survives conductor conditioning at higher conductor (>1M)"
    - "Signal appears in genus-2 L-functions (independent family)"
    - "Proper N(T) unfolding changes the spacing distribution"
  
  # Related specimens
  related: [SPE-0002]  # GUE deviation
  
  # Classification
  status: KILLED  # ALIVE, KILLED, DORMANT, REVIVED
  tier: marginal  # from finding hierarchy
  interest_score: 0.3  # subjective, 0-1
  
  # For the mathematician
  what_a_specialist_would_want:
    - "The specific curves where spacing deviates most from GUE"
    - "Whether deviation scales with conductor or is constant"
    - "Family-level breakdown: CM vs non-CM, semistable vs not"
```

### Tier 3: Shadow Archive (KILLS)
The negative space. Every hypothesis we killed, with fingerprints.
- Currently: shadow_tensor.py (190 cells, 92K test records)
- Upgrade: link each kill to its specimen, so kills have provenance

## The Key Insight: Battery Profiles Are Fingerprints

Two signals can both be "killed" but have completely different battery profiles:

```
Signal A: passes F1-F35, killed by F39 (feature permutation)
  → Real statistical structure, but it's a property of the representation
  → A mathematician might still care — it tells you something about the encoding
  
Signal B: killed by F1 (basic permutation null)
  → Noise. Nothing to see.
  
Signal C: passes F1-F38, killed by F24 (variance decomposition)
  → Almost real. The effect exists but doesn't survive variance accounting.
  → Worth re-examining with more data or a different decomposition.
```

The battery profile IS the specimen's DNA. When we improve the battery (add F40, refine F24), we can re-run profiles and see if previously-killed specimens revive.

## Where This Lives

### Postgres (prometheus_fire)

```sql
CREATE SCHEMA IF NOT EXISTS signals;

-- The specimen registry
CREATE TABLE signals.specimens (
    id TEXT PRIMARY KEY,  -- SPE-0001
    source_problem TEXT,  -- MATH-0062
    source_test TEXT,     -- oq1_spectral_tail.py
    claim TEXT NOT NULL,
    
    -- Effect measurement
    effect_size FLOAT,
    effect_type TEXT,     -- correlation, difference, ratio, identity
    z_score FLOAT,
    p_value FLOAT,
    n_objects INT,
    
    -- Status
    status TEXT NOT NULL DEFAULT 'ALIVE',  -- ALIVE, KILLED, DORMANT, REVIVED
    tier TEXT,            -- identity, law, constraint, marginal, possible
    interest_score FLOAT, -- 0-1, subjective
    
    -- Kill info (null if alive)
    kill_test TEXT,
    kill_mechanism TEXT,
    residual_after_kill TEXT,
    
    -- For the mathematician
    what_specialist_wants TEXT,
    revival_conditions TEXT[],
    
    -- Metadata
    date_found TIMESTAMP DEFAULT NOW(),
    date_last_tested TIMESTAMP,
    found_by TEXT,        -- agent name
    notes TEXT
);

-- Battery test results per specimen
CREATE TABLE signals.battery_results (
    specimen_id TEXT REFERENCES signals.specimens(id),
    test_name TEXT NOT NULL,  -- F1_permutation, F24_variance, etc.
    passed BOOLEAN,           -- true, false, null (not run)
    z_score FLOAT,
    p_value FLOAT,
    detail TEXT,              -- free-form explanation
    run_date TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (specimen_id, test_name, run_date)
);

-- Relationships between specimens
CREATE TABLE signals.relationships (
    specimen_a TEXT REFERENCES signals.specimens(id),
    specimen_b TEXT REFERENCES signals.specimens(id),
    relationship TEXT,  -- 'supersedes', 'contradicts', 'supports', 'related'
    note TEXT,
    PRIMARY KEY (specimen_a, specimen_b)
);

-- Open questions linkage
CREATE TABLE signals.question_links (
    specimen_id TEXT REFERENCES signals.specimens(id),
    question_id TEXT NOT NULL,  -- MATH-0062
    domain TEXT,               -- mathematics, physics, chemistry
    relevance TEXT,            -- how the specimen relates to the question
    PRIMARY KEY (specimen_id, question_id)
);
```

### Local (cartography/docs/)

For each specimen, a markdown file with the full story:
```
cartography/docs/specimens/
  SPE-0001_spectral_tail.md
  SPE-0002_gue_deviation.md
  SPE-0003_nf_backbone.md
  ...
```

These are the narratives. The Postgres tables are the structured data.
The battery profiles in Postgres enable automated re-testing when the battery improves.

## Weak Signal Protocol

When a test produces a signal with z > 2 (or effect size > 0) but it fails part of the battery:

1. **Register it** as a specimen with full battery profile
2. **Document the kill** — which test, what mechanism, what residual remains
3. **Document revival conditions** — what would make this signal real?
4. **Link it** to the open question it came from
5. **Score interest** — does the kill mechanism suggest the signal is close to real, or definitively dead?

Interest scoring heuristic:
- Killed by F1 (permutation): interest = 0.0 (noise)
- Killed by F39 (feature permutation): interest = 0.2 (representation artifact, might still inform)
- Killed by conductor/confound conditioning: interest = 0.3 (real correlation, mediated)
- Killed by F24 (variance): interest = 0.5 (effect exists, accounting problem)
- Passes full battery but effect is tiny: interest = 0.7 (real but small)
- Passes full battery with strong effect: interest = 1.0 (finding)

## Migration Plan

1. Create the schema in prometheus_fire
2. Backfill from existing data:
   - shadow_tensor.py → specimens (status=KILLED)
   - finding hierarchy → specimens (status=ALIVE)
   - known_truth_battery → calibration anchors
   - Today's results → first new specimens
3. Every future test writes to the registry automatically
4. Periodic re-audit: run improved battery against all KILLED specimens
