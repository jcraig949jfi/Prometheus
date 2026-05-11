# Layer 3 — Patterns (failure modes)

Patterns are **reified failure modes**: characteristic ways attacks fail or produce mis-calibrated outputs. Each entry has a detection signature (what to look for in agent output), a calibration anchor (a canonical example the substrate-tester probes against), and a mitigation protocol (the substrate-side response when the pattern fires). The five MANDATED patterns are required citations on every deep-research report (≥2 per report); all 18 in the seed batch cleared the gate. The three additional CANDIDATE patterns surfaced by this batch are proposed for promotion to mandated status in the next contract-change window — they are documented here in candidate state pending ratification.

---

## Mandated patterns (required citations on every report)

### `PATTERN_PRIME_GRAVITATIONAL_OVERFIT`

- **Tier / status:** mandated.
- **Detection signature:** an analysis attributes 96%+ of cross-domain structure to primes (or to whatever canonical narrative dominates the corpus) without first applying domain-specific detrending. In tensor space, the analogue surfaces as agents anchoring on a single canonical paradigm (e.g. "GCT is the path") and weighting non-canonical routes near zero.
- **Calibration anchor:** Charon prime-detrending finding (`feedback_prime_atmosphere.md`); cross-domain analyses kept finding "primes are 96% of the structure" until prime-detrending became mandatory. Tensor analogue: BIP 2019 forces honest re-rank of GCT vs non-GCT routes (LST/Forbes 2024, Bhattacharjee 2024, Kumar–Volk 2021).
- **Mitigation protocol:** apply explicit detrending — re-rank candidate paradigms with non-canonical routes weighted equal-or-higher; require any "X is the path" framing to enumerate at least three non-X alternatives with comparable seriousness.
- **Seed-batch occurrences:** T#1 (AlphaEvolve narrative pull); T#92 (GCT-as-only-viable-program pull, instantiated as candidate `PATTERN_GCT_GRAVITATIONAL_OVERFIT`).
- **Source:** mandated by doctrine; instantiated in this batch via T#1, T#92.

### `PATTERN_CONDUCTOR_CONFOUND`

- **Tier / status:** mandated.
- **Detection signature:** stabilizer / regime / normalization confound — a numerical claim is reported without specifying the conductor / stabilizer / normalization regime under which it holds. In tensor space: a complexity bound reported without specifying which model (unrestricted vs equivariant vs set-multilinear); an identifiability claim without specifying the reshaping.
- **Calibration anchor:** Landsberg–Ressayre 2017's exponential lower bound on `dc(perm)` is **restricted to equivariant model**; reporting it as a bound on `dc(perm)` unrestricted is a textbook PATTERN_CONDUCTOR_CONFOUND (anti-anchor 8).
- **Mitigation protocol:** require explicit `model_restriction` / `stabilizer` / `regime` field on every numerical-bound primitive; substrate-tester probes any unannotated bound as a fail.
- **Seed-batch occurrences:** T#22, T#34, T#40, T#72, T#85, T#92.
- **Source:** mandated by doctrine.

### `PATTERN_BASE_RATE_NEGLECT`

- **Tier / status:** mandated.
- **Detection signature:** an analysis spot-checks at the generic / full-measure stratum and reports "no phenomenon detected," missing the lower-dimensional defective stratum where the interesting math lives.
- **Calibration anchor:** Bernardi–Ranestad cubic-form bound — for *general* forms, `R = R̄ = sr = cr` (rank-zoo collapses on the generic full-measure stratum). Strict inequalities live entirely on the lower-dimensional defective stratum (T#26). A generic-point spot-check would falsely report no gap (`report_T19_cactus_rank.md` Flagged finding 5). Five-application convergence in tensor type-2 constant (anti-anchor 10) is another instance.
- **Mitigation protocol:** require non-generic / wild-form / minimal-border-rank witnesses for any gap claim; pair every Tier-D `GenericityAlmostEverywhereCert` with `MeasureZeroExceptionAnnotation` when explicit exceptions known.
- **Seed-batch occurrences:** T#19, T#22, T#26, T#40, T#56, T#73, T#85, T#92.
- **Source:** mandated by doctrine.

### `PATTERN_VRAM_TRUNCATION_ARTIFACT`

- **Tier / status:** mandated.
- **Detection signature:** an enumeration / Monte-Carlo / Macaulay2 computation reports a negative / null result without recording its truncation depth — the substrate cannot distinguish a genuine NO from a truncation-induced silent NO.
- **Calibration anchor:** Macaulay2 B-invariant-ideal enumeration in border apolarity (Buczyńska–Buczyński Algorithm 5.1) blows up combinatorially with multigraded Hilbert function; implementations truncate to small `r` and small format. `report_T19_cactus_rank.md` Flagged finding 6 mandates truncation-depth recording on every `apolar_witness`.
- **Mitigation protocol:** require `truncation_depth`, `compute_budget_consumed`, `was_budget_exhausted` fields on every enumeration / search-based primitive; substrate-tester probes any null result without these fields as a fail.
- **Seed-batch occurrences:** T#19, T#26, T#40, T#72, T#73, T#84.
- **Source:** mandated by doctrine.

### `PATTERN_RANK_PARITY_LEAK`

- **Tier / status:** mandated. **Most-cited pattern in seed batch.** Reflects the substrate's most active failure mode: rank-zoo / coordinate-collapse confusion across the entire frontier.
- **Detection signature:** an analysis reports "rank decreased from X to Y" or "complexity is Z" without specifying *which* rank coordinate or *which* complexity coordinate. In tensor space this manifests as collapsing `(R, R̄, sr, cr, cr̄)` into a single "rank" field, or collapsing `(dc, \underline{dc}, L, B, dc_{equiv})` into "determinantal complexity."
- **Calibration anchor:** five rank coordinates `(R, R̄, sr, cr, cr̄)` from T#19 (cactus chain); four complexity coordinates `(dc, \underline{dc}, L, B, dc_{equiv})` from T#92 (GCT cluster). Lampert–Moshkovitz Sept 2025 separation of partition-rank from analytic-rank is a direct test.
- **Mitigation protocol:** any chart asserting "rank decreased from X to Y" without specifying WHICH rank is HARD-5-noncompliant; `RankZooSignature` registration with all coordinates filled or explicitly `null` is required; substrate-tester probes for the parity violation by submitting deliberately-collapsed claims and verifying rejection.
- **Seed-batch occurrences:** T#13, T#19, T#22, T#34, T#40, T#56, T#58, T#72, T#73, T#79, T#85, T#92, T#95 — **13 of 18 reports**.
- **Source:** mandated by doctrine.

---

## Candidate patterns (proposed for promotion in next contract-change window)

The seed batch surfaced three patterns of sufficient frequency and sharpness to warrant promotion to mandated status. They are documented in candidate state pending Aporia ratification.

### `PATTERN_GCT_OCCURRENCE_DEAD` (candidate)

- **Tier / status:** candidate; counterpart to `PATTERN_BSD_TAUTOLOGY` in number-theory space.
- **Detection signature:** an agent attempts to construct an `OccurrenceObstruction` for `(det_m, padded_perm_{n,m}, m=poly(n))` — the canonical GCT regime. The attempt is **provably impossible** by BIP 2019 (J.AMS).
- **Calibration anchor:** Bürgisser–Ikenmeyer–Panova, *No occurrence obstructions in geometric complexity theory*, J.AMS 32 (2019) 163–193, arXiv:1604.06431. For all sufficiently large `n` and `m = poly(n)`, every irreducible `GL_{m^2}`-representation occurring in `\mathbb{C}[\overline{GL_{m^2}\cdot\det_m}]_d` also occurs in `\mathbb{C}[\overline{GL_{m^2}\cdot \widetilde{perm}_{n,m}}]_d`. The original Mulmuley–Sohoni roadmap (separate via *occurrence* obstructions) is impossible.
- **Mitigation protocol:** substrate-tester rejects any `GCTObstructionCertificate.OccurrenceObstruction` for the canonical regime as a sentinel-violation; agents are routed to `MultiplicityObstruction` / `VanishingIdealObstruction` / `OutsideOrbitObstruction` as alternatives. `anti_anchors.md` entry 1 pins the false form.
- **Seed-batch occurrences:** T#92 (canonical instance).
- **Source:** T#92; synthesis §4 entry 1.

### `PATTERN_GCT_GRAVITATIONAL_OVERFIT` (candidate)

- **Tier / status:** candidate; analogue / specialization of `PATTERN_PRIME_GRAVITATIONAL_OVERFIT` in tensor / complexity space.
- **Detection signature:** agent prompt invokes "GCT is the path to P vs NP" or weights GCT routes substantially above non-GCT routes for `dc(perm)` lower-bound work. Identical *shape* to the prime-detrending phenomenon: an LLM trained on widely-circulating commentary will gravitate to the canonical narrative.
- **Calibration anchor:** by 2026 the actual progress on algebraic-circuit lower bounds has migrated to non-GCT routes — Limaye–Srinivasan–Tavenas (FOCS 2021, arXiv:2101.01340) + Forbes 2024 (CCC 2024) for set-multilinear constant-depth; Bhattacharjee–Bläser–Dutta–Mukherjee ICALP 2024 (exponential sums); Kumar–Volk 2021 (`Θ(n)` for `Σx_i^n`). Mulmuley's CACM 2012 ~100-year estimate is the program's chief proponent's own calibration anchor.
- **Mitigation protocol:** when an agent prompt contains "GCT" + "P vs NP" + "the only viable program," apply detrending — re-rank with LST / Forbes / Bhattacharjee / Kumar–Volk / equivariant routes weighted equal-or-higher.
- **Seed-batch occurrences:** T#92 (canonical instance, proposed for registration alongside parent pattern).
- **Source:** T#92; synthesis §4 (PATTERN_GCT_GRAVITATIONAL_OVERFIT proposed alongside PATTERN_PRIME_GRAVITATIONAL_OVERFIT).

### `PATTERN_ZAUNER_FALSE_ANCHOR` (candidate)

- **Tier / status:** candidate; specialization of conditional-vs-unconditional confusion.
- **Detection signature:** an agent reports "Zauner's SIC-POVM conjecture proved in 2025" (or any unconditional framing of AFK 2025). The true status is **conditional on Stark conjectures + Shintani–Faddeev modularity**.
- **Calibration anchor:** AFK 2025, arXiv:2501.03970. The construction is conditional; substrate must reject "Zauner proved" without conditional annotation. Anti-anchor 2 in `anti_anchors.md`.
- **Mitigation protocol:** any `RayClassFieldFiducial` or `StarkUnitWitness` primitive must carry mandatory `conditional_on: [stark_conjectures, shintani_faddeev_modularity]` annotation; substrate-tester probes for the missing-annotation form.
- **Seed-batch occurrences:** T#85 (canonical instance).
- **Source:** T#85; synthesis §4 entry 2.

---

## TODO for future batches

- **Promote three candidates.** `PATTERN_GCT_OCCURRENCE_DEAD`, `PATTERN_GCT_GRAVITATIONAL_OVERFIT`, `PATTERN_ZAUNER_FALSE_ANCHOR` are candidate-state in v0.1.0; promotion to mandated requires Aporia ratification + ≥1 cross-batch confirmation (i.e. another batch where a non-T#85, non-T#92 report independently fires the pattern).
- **Distribution table.** Synthesis §9 documents the per-report citation distribution. Future versions should track running per-pattern count to surface drift / over-fitting of any single pattern.
- **Adjacent-corner patterns.** Number-theory and knot-theory batches will likely surface new mandated patterns — e.g. PATTERN_BSD_TAUTOLOGY is referenced as counterpart but not yet a Layer-3 entry here (number-theory not seeded yet).
