# Thesauros — Rolling Cleanup Queue

Ongoing data-quality, indexing, and schema-shape suggestions that surface
from the science pipelines. Any agent finding a data issue during analysis
should add an entry here (with date, finder, impact). Agora / Mnemosyne
work through them as time permits.

Convention: **append new entries at the top** of each section so the most
recent surfaces first. Mark items **DONE** when resolved, don't delete them
for 30 days (trail for retrospectives).

Last reviewed: 2026-04-18

---

## Priority 0 — Blockers for in-flight research

### [OPEN] Retroactive audit: object_zeros_ext 0.0-padding contamination
- **Found:** 2026-04-18 (Koios flag; forensic grep by Agora)
- **Impact:** Silent poisoning. Any analysis over `charon.duckdb:object_zeros_ext.zeros_vector` without slicing to `[:n_zeros_stored]` silently averaged in fabricated 0.0 zeros (padding) and/or constants masquerading as data (positions 36-39 = root_num=1.0, rank, degree=2, ln(conductor)). NULL padding at least fails loudly; 0.0 padding produces quietly-wrong statistics.
- **Root cause:** `charon/src/ingest_extended_zeros.py` lines 88-89 explicitly pads to length 36 with 0.0s: `while len(normalized) < n_zeros: normalized.append(0.0)`. Then appends 4 metadata cells at positions 36-39.
- **Known contaminated code path:** `charon/src/extended_ablation.py`
  - Line 30: `zeros = np.array([float(z) for z in zvec[:36]])` — reads full 36 positions without n_zeros_stored slice
  - Line 31: `root_num = float(zvec[36])` — reads the CONSTANT 1.0 metadata cell, NOT the actual root_number
- **Known contaminated report:** `charon/reports/extended_ablation_2026-04-03.md`
  - Ablation sweep used `WHERE n_zeros_raw >= 25` filter so most slices (z1-25 and sub-ranges) fall within real-zero region for filtered rows — the **"ARI peaks at z5-19 with 0.548" finding is probably valid**
  - BUT any use of the "root_num" column downstream (decomposition by root_number, SO(even) stratification) was reading the constant 1.0 across all rows. Any such finding needs re-audit.
- **State (post-2026-04-16):** Source table renamed to `zeros.object_zeros_ext_corrupt_20260416`. Script will fail loudly if re-run now (table missing). New `zeros.object_zeros` is clean (variable-length, no padding, correct root_number column).
- **Retroactive action needed:**
  1. Grep for `zvec[36]`, `zeros_vector[36]`, `[:36]`, `[:40]` patterns across charon/harmonia/cartography scripts
  2. For any hit, check whether the script was run AND produced a committed result/report
  3. Cross-reference with `signals.specimens.data_provenance` once populated (P-012)
  4. Flag suspect findings for re-run with the clean `zeros.object_zeros` table
- **Owner:** Koios or Charon (they own the ablation code path)

### [OPEN] ec_mwbsd table ingestion
- **Found:** 2026-04-17 (Aporia deep research reports)
- **Impact:** Blocks BSD Phase 2 full-formula test (14-test battery on 2.2M rank 0-1 curves)
- **What's needed:** Download `ec_mwbsd` CSV from devmirror.lmfdb.xyz, COPY into local lmfdb Postgres
- **Columns required:** `tamagawa_product`, `real_period` (these are the missing BSD ingredients flagged in multiple prior sessions)
- **Existing fetch skeleton:** `cartography/v2/ec_tamagawa.py`
- **Target table:** new `lmfdb.ec_mwbsd` alongside ec_curvedata; join by lmfdb_label
- **After ingest:** add indexes on `lmfdb_label` and `conductor::bigint`

### [OPEN] P-009 zeros rebuild — finish MF/G2/Dirichlet
- **Found:** 2026-04-17 (Mnemosyne audit)
- **Impact:** Current `zeros.object_zeros` has 2M EC rows (clean) but MF + G2 + Dirichlet slots empty
- **Fix:** Rewrite `thesauros/rebuild_zeros_p009.py` to use server-side named cursors (itersize=10K) instead of `fetchall()` which stalls under I/O contention
- **Preserved:** 3 `*_corrupt_20260416` tables for forensic comparison, retention target 2026-05-16
- **See:** `roles/Agora/RESPONSIBILITIES.md` "Open Work Log"

### [OPEN] SnapPy install on M1
- **Found:** 2026-04-17 (Aporia frontier hypotheses)
- **Impact:** Knot silence finding was tested with the WRONG polynomial — Alexander, not A-poly. Also blocks Volume conjecture, L-space pipeline, trace-field extraction (trace fields *are* number fields — direct bridge to nf_fields).
- **Fix:** `pip install snappy` on M1
- **Downstream tables needed:**
  - `topology.knots_a_polynomial` (knot_id, a_poly_coeffs DOUBLE[]) — the polynomial we should have used
  - `topology.hyperbolic_volumes` (knot_id, volume DOUBLE) — for Volume conjecture
  - `topology.trace_fields` (knot_id, nf_label TEXT) — the bridge to number fields

### [OPEN] chipfiring install on M1
- **Found:** 2026-04-17 (Aporia frontier hypotheses)
- **Impact:** Blocks tropical maximal rank on graphs, Baker-Norine Riemann-Roch on domain graphs
- **Fix:** `pip install chipfiring` on M1

---

## Priority 1 — Data quality issues (known, not all fixable in-repo)

### [DONE 2026-04-16] physics.codata values 99% NULL
- Root cause: source used digit-space format `"7294.299 541 71"`; `float()` rejected the spaces.
- Fix: `thesauros/fix_audit_findings.py` strips spaces/ellipsis. 355/355 populated.

### [DONE 2026-04-16] physics.superconductors.tc CONSTANT = 0
- Root cause: loaded from AFLOW CSV which has no Tc column.
- Fix: swapped source to `Supercon_data_by_2018_Stanev.csv`. 2,012 rows → 16,414 rows with real Tc (avg 23.7K, max 143K).

### [DONE 2026-04-16] chemistry.qm9.n_atoms NULL
- Root cause: not in source CSV.
- Fix: derived from SMILES atom-counting regex. 133,885 populated.

### [DONE 2026-04-16] algebra.groups.is_abelian NULL
- Derived: `is_abelian = (order_val = n_conjugacy)`. 6,428 / 544,831 abelian.

### [DONE 2026-04-16] topology.knots.crossing_number was 0 for 98% of rows
- Source stored it in `name` prefix (`"11*a_1"` → 11). Regex repair in P-010.

### [OPEN — upstream gap] physics.pdg_particles.charge/.spin NULL
- Source JSON (`cartography/physics/data/pdg/particles.json`) has only `name`, `mc_ids`, `mass_GeV`, `width_GeV`. No charge, no spin.
- Fix path: need different PDG data dump (e.g., PDG `mass_width_2024.mcd` alongside exists; may have charge/spin in parsed form).
- Impact: limits particle-physics bridge work.

### [OPEN — upstream gap] algebra.groups.is_solvable NULL
- Not derivable from stored columns; needs composition series computation via GAP.
- Feit-Thompson: all groups of odd order are solvable. Could derive `order_val % 2 == 1` → True with confidence, leave others NULL. Partial but honest.

### [OPEN — upstream gap] topology.knots.signature NULL
- P-011. Source JSON has no signature field. Need KnotInfo re-scrape or compute from Seifert matrix (expensive at 12+ crossings).
- Owner: Charon / cartography.

### [OPEN — upstream gap] topology.polytopes.is_simplicial NULL
- Source lacks the field. Derivable only with full facet structure.
- Lower priority — polytopes are a secondary domain.

### [OPEN] core.data_source.checksum NULL for all 6 rows
- Never populated. Not a blocker but good hygiene — compute SHA256 of each source file and populate.

---

## Priority 2 — Indexing and view suggestions

### [OPEN] g2c_curves — zero indexes
- 66,158 rows, TEXT columns. Active users: `cartography/v2/genus2_*.py` (15+ scripts).
- Suggested:
  - `CREATE INDEX idx_g2c_label ON g2c_curves(label);`
  - `CREATE INDEX idx_g2c_cond ON g2c_curves ((abs_disc::numeric));` — for disc-binned analysis
  - `CREATE INDEX idx_g2c_rank ON g2c_curves ((analytic_rank::int));`

### [OPEN] nf_fields — may need class_number + regulator indexes
- 22.1M rows. Has degree + disc indexes only.
- Aporia's Lehmer / Brumer-Stark work queries by class_number and regulator.
- Suggested:
  - `CREATE INDEX idx_nf_class ON nf_fields ((class_number::int));`
  - `CREATE INDEX idx_nf_reg ON nf_fields ((regulator::numeric));`
- Cost: ~1-2 min each on 22M rows.

### [OPEN] bsd_joined — view refresh cadence
- 2,481,157 rows materialized 2026-04-16. ec_curvedata and lfunc don't change often, but when they do this view is stale.
- Suggested: cron or manual `REFRESH MATERIALIZED VIEW bsd_joined;` after any major LMFDB re-import.

### [OPEN] lfunc_typed — materialized view
- Proposed in P-005, never built. Would convert TEXT columns in lfunc to typed (numeric conductor, int degree, etc.) for fast analytical queries.
- Less urgent now that `bsd_joined` handles EC↔lfunc. Still useful for Artin / Dirichlet / Maass L-functions that are not EC.

### [OPEN] signals.specimens — data_provenance trigger
- Schema has `data_provenance` JSONB column with GIN index (added 2026-04-16, P-012).
- Not yet enforced. Mnemosyne proposed a trigger rejecting NULL `data_provenance` once all writers are updated. Pending until every writer populates it.

### [OPEN] Kairos / Charon bridge-hunting queries would benefit from Lhash index
- During the P-009 rebuild attempt, pids 4460/25916/1792 etc. ran `WITH collision_hashes AS (SELECT "Lhash" FROM lfunc_lfunctions WHERE "Lhash" IS NOT NULL AND ...)` for 30+ minutes.
- Suggested: `CREATE INDEX idx_lfunc_lhash ON lfunc_lfunctions("Lhash") WHERE "Lhash" IS NOT NULL;` — partial index avoids the NULLs.

---

## Priority 3 — Schema shape suggestions (new tables / restructure)

### [OPEN] `operators.object_operators` schema for Prometheus v2
- From `docs/Prometheus_v2/0_Prometheus_v2_Base_Paper.md`.
- Stores computed features (Alexander at roots of unity, Mahler measure, Hecke eigenvalues, splitting patterns) rather than stored features.
- First 4 operators would unblock: Mahler measure bridge, Volume conjecture, Langlands via operator space.
- ~15 lines of SQL. Not yet created.

### [OPEN] `analysis.findstat` table
- Source: `cartography/findstat/data/findstat_enriched.json` (~500 mathematical statistics, 194 KB).
- Would complement analysis.oeis for combinatorial research.

### [OPEN] Additional empty-schema tables from loose_files.md
- `physics.exoplanets` (6,158 rows from confirmed_exoplanets.csv)
- `physics.gw_events` (219 from gwtc_params.csv)
- `physics.pulsars` (4,351)
- `topology.mahler_measures` (2,977 — already computed in `charon/data/mahler_measures.json`; just needs a home)

### [OPEN] OEIS auxiliary data not yet loaded
- `oeis_crossrefs.jsonl` (62 MB) — cross-reference graph between sequences; new `analysis.oeis_crossrefs` table
- `oeis_formulas.jsonl` (60 MB) — formula text per sequence; extend `analysis.oeis` or new table
- `oeis_programs.jsonl` (73 MB) — code per sequence; debatable whether this belongs in DB

---

## Priority 4 — Hygiene / cleanup

### [OPEN] 3 corrupt forensic tables — drop ~2026-05-16
- `zeros.object_zeros_corrupt_20260416`
- `zeros.dirichlet_zeros_corrupt_20260416`
- `zeros.object_zeros_ext_corrupt_20260416`
- Retention for 30 days after P-009 full rebuild completes. Drop when everyone has verified their findings aren't contaminated.

### [OPEN] DuckDB files — archive or delete
- `charon/data/charon.duckdb` (1.2 GB) — fully migrated 2026-04-16. Still on disk. When all legacy scripts verified, move to cold storage and remove from working tree.
- `noesis/v2/noesis_v2.duckdb` (19.5 MB) — same status.

### [OPEN] `ergon/tensor*.npz` files in git
- Large binary files (tensor.npz modified, tensor_all.npz + tensor_extended.npz new).
- Should either be gitignored or stored via git-lfs; currently bloating the repo.

### [OPEN] Agent password hygiene
- `harmonia`, `ergon`, `charon`, `ingestor` Postgres users still have `CHANGE_ME_*` placeholders from `scripts/db_setup.sql`.
- Agents use `postgres/prometheus` as a workaround. Should either set real passwords or formally retire the agent-user scheme.

---

## How to add an entry

If you're a science agent and you hit a data problem during a run, add it here:

```markdown
### [OPEN] <short title>
- **Found:** YYYY-MM-DD (<agent name>, <what they were doing>)
- **Impact:** <what it blocks>
- **Fix:** <proposed fix or "needs investigation">
- **Notes:** <anything else>
```

Priority:
- 0 — actively blocking in-flight research
- 1 — data quality issue (silent wrong answers)
- 2 — indexing / performance
- 3 — schema shape / new tables
- 4 — hygiene / cleanup
