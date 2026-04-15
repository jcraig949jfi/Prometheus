# Ergon Handoff — Start Here
## For the next Claude Code session
### 2026-04-15 (Session 2b — Executing real work)

---

## Current State

### What was done THIS session (2026-04-15, Sessions 2 + 2b)

Session 2 was a polling test run. Session 2b shifted to active execution after James's feedback ("execute, don't just poll").

#### 1. Agora Polling Loop (test run)
- Connected to Redis, announced Ergon@M1 back online
- Set up 5-minute cron polling across all 4 streams (agora:main, tasks, challenges, discoveries)
- Posted heartbeats every other cycle
- Ran ~40+ polling cycles over several hours

#### 2. Batch 01 Execution — COMPLETED (6/8 tests, executed by Aporia)
Ergon monitored and ACK'd results but did NOT execute tests directly. Aporia picked up execution while Ergon was in passive polling mode. **Lesson: next session, Ergon should execute, not just poll.**

**Kairos v3 execution order (LOCKED):**

| # | Test | Result | Executed by |
|---|------|--------|-------------|
| 1 | MATH-0332 Jones unknot | CALIBRATION PASS (0/249 counterexamples) | Aporia |
| 2 | MATH-0130 Langlands GL(2) | CALIBRATION PASS (100% match, 10880/10880) | Aporia |
| 3 | MATH-0136 abc Szpiro | STRONGLY SUPPORTED (monotone decrease) | Aporia |
| 4 | MATH-0063 BSD Phase 1 | PERFECT (3,824,372/3,824,372 rank agreement) | Aporia |
| 5 | MATH-0260 Artin entireness | FRONTIER MAPPED (359K open reps) | Aporia |
| 6 | MATH-0151 Chowla | SUPPORTED (N=10^7, indistinguishable from null) | Aporia |
| 7 | MATH-0145 Brumer-Stark | DEFERRED (nf_fields data gap) | — |
| 8 | MATH-0042 Lehmer | DEFERRED (NF polys data gap) | — |

**Gate: 2/2 calibrations PASSED. Open problems UNLOCKED.**
**Zero falsifications across all tests.**

#### 3. Major Findings from Agora (observed, not executed)

**NF Universal Mediator + Backbone Discovery (Kairos):**
- 77.3% of domain pairs show emergence when NF is third domain (34/44 pairs)
- Top-1 SV (~97% energy) = Megethos (log_disc_abs) — KILLED by battery every time
- Top-2 SV (~1-3% energy) = real mathematical backbone — PASSES battery every time
- NF PCA: Megethos is only PC3 (18.3%). PC1 = arithmetic (class number formula, 37.6%). PC2 = degree/regulator (22.6%)
- Backbone carries arithmetic or structural info, NOT size. Promoted to PROBABLE.

**Tensor Depth Hierarchy (Kairos):**
- Pure suppressors: dirichlet_zeros (31-0), modular_forms (25-0), elliptic_curves (19-0)
- Pure enhancers: number_fields (0-34), space_groups (0-24)
- Maps to analytic (suppressors) vs algebraic (enhancers) divide in mathematics

**Silent Islands Revised (Kairos + Aporia):**
- 3 islands, not 4: knots, Maass forms, fungrim
- Genus-2 RETRACTED as island (deep sweep rank 8-10 to most domains)
- Root cause: "computational bridges" — features need intermediate computation (Mahler measure, roots of unity evaluation)
- Aporia computed 2977 Mahler measures from Alexander polynomials (P1.1 partial)

**BSD Phase 2 (Kairos + Mnemosyne):**
- Sha circularity at rank >= 2: Sha computed ASSUMING BSD, so testing BSD with it is circular
- 2.89M rank 0-1 curves available for non-circular calibration
- Isogeny consistency: 99.93% (42 anomalies = 2-adic Sha computation, explained)
- Blocked on Omega (real period) + Tamagawa product
- Isogeny classes NEVER span rank boundaries (0 spanning in all LMFDB)

**abc Szpiro Transition:**
- Median Szpiro ratio: 4.41 (<1K conductor) -> 1.46 (100M-1B)
- Real transition at conductor ~1-2M (fine-grained bins confirmed)
- Convergence toward ~1.5, not 1.0

#### Session 2b Execution Results (Ergon)
1. **NF permutation null**: Confirmed Harmonia's kill. All 3 scorers see feature geometry only. z=0.08 (cosine), 0.07 (kurtosis), 0.00 (alignment after replication).
2. **AlignmentCoupling RETRACTED**: z=2.22 was seed artifact. 6/10 trials flat zero, max z=1.12. Scorer W matrix is unstable.
3. **P1.3 knot arithmetic re-encoding**: Computed Mahler measure + Alexander at roots of unity for 2977 knots. NULL result — cosine coupling insensitive to feature choice.
4. **GUE deviation**: Real but smaller than Harmonia reported. ~14% variance deficit (first-gap), not 40% (pooled was unfolding artifact). Needs proper smooth unfolding.
5. **abc Szpiro controlled test**: Decrease is REAL at fixed bad-prime count (all 5 strata monotone decrease). Selection effect amplifies but does not create. Strongest Batch 01 result.
6. **BSD Phase 2**: BLOCKED — no Omega/period or Tamagawa product in ec_curvedata. Mnemosyne confirmed.

### What needs doing (in priority order)

#### 1. Proper GUE unfolding
The ~14% variance deficit needs calibrated N(T) formula for EC L-functions, not per-curve mean normalization. A number theorist would know the right formula.

#### 2. Silent Islands execution (P1-P8, Kairos-approved)
Priority tests that Ergon should run:
- P1.3: Knot feature re-encoding (fast, approved)
- P2.1: Maass Dirichlet coefficients (approved)
- P4.1: Fungrim numerical evaluation (approved)
- P5: NF Langlands check (must-work calibration)
- P1: Alexander poly at roots of unity (fast)

#### 3. NF PCA definitional test
Load NF features from domain_index.py, compute PCA, project tensor bond vectors onto NF PCA basis. Answers: is the backbone degree or class_number?

#### 4. OQ1 Spectral tail decisive test
6 equal-N conductor bins, spectral tail coupling per bin. Needs Postgres (EC + L-function zeros at high conductor). Mnemosyne assigned preflight.

#### 5. BSD Phase 2 (when Omega + Tamagawa available)
Run Kairos's revised protocol on rank 0-1 calibration set (2.89M curves).

#### 6. Wire explore_ungated() through GradientTracker
Kairos's gradient_tracker.py is on main. Integrate with explore_ungated().

#### 7. CSV fallback for Harmonia loaders (carried over)
Still needed: load_ec_rich and load_artin CSV fallbacks.

---

## Agora State Summary (as of 2026-04-15, end of session 2)

### Stream message counts (approximate)
- agora:main: ~60+ messages
- agora:tasks: ~7 messages
- agora:challenges: ~15+ messages
- agora:discoveries: ~25+ messages

### Key Decisions This Session
- [PASSED] Jones unknot calibration
- [PASSED] Langlands GL(2) calibration (100% match)
- [SUPPORTED] abc Szpiro (monotone decrease, no falsification)
- [PERFECT] BSD Phase 1 (3.8M/3.8M rank agreement)
- [MAPPED] Artin entireness frontier (359K open reps)
- [KILLED] Megethos as NF hub mechanism (97% energy, battery kills it)
- [PROBABLE] NF arithmetic backbone (component-2, 1-3% energy)
- [CONFIRMED] Tensor depth hierarchy (suppressors vs enhancers)
- [RETRACTED] Genus-2 as silent island
- [IDENTIFIED] Sha circularity at rank >= 2
- [CLOSED] Silent islands challenge loop ("computational bridge" thesis)

### Open Questions
- [OPEN] What is NF component-2? Degree vs class_number (needs PCA projection)
- [OPEN] Spectral tail asymptote: H1 vs H2 (needs high-conductor data)
- [OPEN] BSD Phase 2: full formula test (needs Omega + Tamagawa)
- [OPEN] Artin linkage: Mnemosyne investigating lfunc origin field
- [OPEN] Suppression mechanism: why do zeros absorb shared variance?

### Infrastructure (all live)
- Redis: localhost:6379, password=prometheus
- Postgres on M1: lmfdb (30M+ rows)
- Postgres connection: host=192.168.1.176 port=5432

### Team Status (end of session)
- Kairos (M2): ACTIVE — ran emergence test, NF PCA, BSD isogeny, depth hierarchy
- Mnemosyne (M2): ACTIVE — BSD data audit, Artin linkage investigation
- Aporia (M1): ACTIVE — executed all 6 Batch 01 tests, P1.1 Mahler measures
- Ergon (M1): POLLING ONLY this session — should EXECUTE next session
- Claude_M1 (M1): OFFLINE

---

## WARNINGS

### Phoneme framework is UNVALIDATED
Same as before — do NOT extend DOMAIN_PHONEME_MAP, use distributional scorer only.

### Don't break Harmonia
Changes to harmonia/src/ must not change scoring behavior, must pass calibration.

### tntorch ZeroDivisionError on Windows
`tn.cross()` crashes with ZeroDivisionError when convergence is very fast. Fixed by passing `verbose=False`.

### Sha circularity
Do NOT use LMFDB sha values to "verify" BSD at rank >= 2. They are computed by assuming BSD. Only rank 0-1 sha is independent.

### Gate condition
Calibration gate (2/2) is PASSED. Open-problem tests are unlocked. But maintain execution order discipline.

---

## Key files (no code changes this session)
- `ergon/HANDOFF.md` — This file (updated)
- No code was modified by Ergon this session. All test execution was by Aporia.
