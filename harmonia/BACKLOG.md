# Harmonia BACKLOG — Cross-Domain Bridge Mining

**Author:** Harmonia_M2_sessionB
**Date:** 2026-05-15
**Authorizing docs:**
- `D:\Prometheus\pivot\atlas_continuous_attack_roadmap_2026-05-15.md` (commit `701a0241`) — 4-phase roadmap, my role + cron slot
- `D:\Prometheus\pivot\arena_problem_atlas_sandbox_vision_2026-05-14.md` (commit `f4093dc6`) — Sandbox firewall, asymmetric promotion gate, `RepresentationShiftWitness` primitive
- User prompt 2026-05-15 — revival commitments, output schema, hard stops

**Status:** Phase 0 (weeks 1–4) revival. Operating in **manual-quarantine mode** until the Sandbox firewall lands (Phase 0 prerequisite, owned by Aporia + Techne + Ergon + Substrate-tester; ETA week 2–3).

---

## Operating envelope (binding)

- **All exploration outputs land in `D:\Prometheus\harmonia\sandbox_drafts\<date>\<exploration_id>\` during manual-quarantine mode.** Aporia is expected to add this path to `.gitignore` this week so accidental commits don't leak to canonical paths.
- **All bridge IDs carry `sandbox::HBR-NNN` namespacing pre-emptively** (HBR = Harmonia Bridge Reframing). Post-firewall migration into the canonical sandbox tree is no-rename.
- **Per-exploration artifact shape (JSON):** `{source_problem_id, target_problem_id, hypothesized_transport_mechanism, evidence_for, evidence_against, falsification_attempts, current_verdict}`. `current_verdict ∈ {open, candidate_RSW, sandbox_dormant, killed}`.
- **Asymmetric promotion gate (six conjunctive criteria) per `arena_vision §5 Part 5`:** primary-literature citation; falsification anchor; three independent verification paths; two-week sandbox dormancy; Aporia + Techne dual sign-off; explicit `sandbox::X → X` mapping in promotion ledger. Default verdict: REJECT. Expected ratio ~30:1 sandbox candidates per canonical promotion.
- **Hard stops:** no canonical writes during manual-quarantine; no kernel contract changes; no `--writeable` promotions; no LoRA-related work.

## Item schema

Each item below carries:
- **id** — `BL-H-NNN`
- **phase** — 0 / 1 / 2 / 3
- **type** — `bridge_candidate` / `domain_inventory` / `methodology`
- **title** — for bridges: `<source> ↔ <target>` + one-line hypothesized transport
- **deps** — load-bearing prerequisites
- **effort** — per-exploration token/time estimate
- **emission** — substrate-block(s) the exploration is expected to produce

---

## Phase 0 — Revival (weeks 1–4, mid-May → mid-June 2026)

Goal: first 10 bridge explorations under manual quarantine; falsification methodology re-established; per-domain bridge inventory seeded. Cadence: ~5 explorations/week target. Phase 0 success = ≥5 sandbox_drafts/ artifacts landed/week + Sandbox firewall live by end of phase.

### BL-H-001 — Lehmer's conjecture ↔ knot polynomial coefficient growth

- **phase:** 0  **type:** bridge_candidate
- **transport hypothesis:** Mahler measure of integer Laurent polynomials carries to Alexander/Jones polynomial coefficient growth via the Silver–Williams correspondence between knot complements and integer polynomial roots near the unit circle. If Lehmer's number is the infimum of Mahler measures > 1, the same infimum should govern knot-polynomial coefficient envelopes for hyperbolic knots.
- **deps:** Aporia files `aporia/meta/problem_queue/harmonia.jsonl` with this seed; LMFDB EC Mahler measure access; knot polynomial DB (sage / SnapPy).
- **effort:** 4–6 hours per first-pass exploration.
- **emission:** 1 sandbox::HBR-001 artifact; one falsification attempt under permutation-null on coefficient sequences; either `candidate_RSW` or `killed` verdict.

### BL-H-002 — BSD rank distribution ↔ isogeny class size distribution

- **phase:** 0  **type:** bridge_candidate
- **transport hypothesis:** Both distributions are conductor-stratified functionals of the same underlying L-function; if rank correlates with isogeny class size beyond what conductor alone predicts, this is evidence for a shared arithmetic substrate beyond the BSD identity. Carry the Attack-4 permutation-null methodology (NF backbone kill from 2026-04-15) over to this pairing.
- **deps:** LMFDB EC tables (3.8M curves, already mirrored at 192.168.1.176:5432); F011 rank-0 residual methodology as anchor.
- **effort:** 6–8 hours.
- **emission:** 1 sandbox::HBR-002 artifact; Pattern 30 lineage check (rank↔isogeny may be algebraically coupled); permutation-null verdict.

### BL-H-003 — modular form coefficient bounds ↔ tensor decomposition rank bounds

- **phase:** 0  **type:** bridge_candidate
- **transport hypothesis:** Deligne's `√p` Hecke eigenvalue bound and Strassen-style tensor rank lower bounds both reduce to representation-theoretic dimension counting. If the bounds share an underlying group-theoretic exponent, a transport identifies which.
- **deps:** Read MEMORY pointer `project_tensor_decomp_qd.md`; LMFDB modular forms access; flag this as HIGH FALSIFICATION RISK — bound-comparisons are notorious for spurious-coupling Pattern 30 hits.
- **effort:** 8–10 hours including Pattern 30 diagnostic before any correlation work.
- **emission:** 1 sandbox::HBR-003 artifact; Pattern 30 severity report (expected Level ≥ 1; required Level 0 to claim correlational evidence).

### BL-H-004 — Sato–Tate ↔ random matrix theory eigenvalue spacing

- **phase:** 0  **type:** bridge_candidate
- **transport hypothesis:** Katz–Sarnak philosophy already names this bridge for L-function families; the substrate's job is to test whether the existing F011/EPS011 rank-0 residual signal (22.90 ± 0.78%) survives transport to non-EC L-functions (Maass forms, GL_3, function-field zeta). Calibration anchor.
- **deps:** EPS011@v2 symbol resolved; UF_CAT unfolding pipeline; LMFDB Maass / higher-rank L-function tables.
- **effort:** 6 hours per L-function family.
- **emission:** 1 sandbox::HBR-004 artifact per family; this is the closest candidate to canonical promotion given prior calibration weight.

### BL-H-005 — Goldbach gap distribution ↔ prime k-tuples conjecture

- **phase:** 0  **type:** bridge_candidate
- **transport hypothesis:** Both are sieve/circle-method targets governed by singular-series products; Maynard–Tao bounded-gap machinery may transport directly to Goldbach gap moments under a Bonferroni-corrected paired audit.
- **deps:** Aporia seed queue; primes DB; needs the BL-H-008 Bonferroni template live before promotion claims.
- **effort:** 6–8 hours.
- **emission:** 1 sandbox::HBR-005 artifact; explicit Bonferroni-correction record in the falsification trail.

### BL-H-006 — Hodge conjecture ↔ motive realization

- **phase:** 0  **type:** bridge_candidate
- **transport hypothesis:** Hodge cycles in singular cohomology that fail to be algebraic should be detectable by their motivic Galois group orbit structure. The conjectural transport: `Hodge ⇒ algebraic` factors through `Hodge ⇒ motivic ⇒ algebraic`, and the substrate's task is to find computable obstructions to the first arrow.
- **deps:** This is the LEAST tractable seed; treat as long-arc Phase 0 reading-only first pass with no correlational claims attempted. Likely produces `sandbox_dormant` rather than `candidate_RSW`.
- **effort:** 10–12 hours for literature inventory; no numerical attack until Phase 1.
- **emission:** 1 sandbox::HBR-006 artifact in `sandbox_dormant` verdict by default.

### BL-H-007 — Permutation-null variants library (per-domain)

- **phase:** 0  **type:** methodology
- **content:** Catalog the permutation-null protocols that have killed candidate findings before, generalized per domain:
  - NF backbone permutation (Attack 4, 2026-04-15) — number theory baseline.
  - Block-shuffle within conductor decile (NULL_BSWCD@v2) — analytic structure preservation.
  - Frame-based resample (NULL_FRAME@v1) — construction-biased samples.
  - Boot resample (NULL_BOOT@v1) — quick first-pass falsifier.
  - Plain shuffle (NULL_PLAIN@v1) — pedagogical baseline.
  - **NEW (Phase 0 deliverable):** isogeny-class permutation null (proposed for BL-H-002 as a stronger control than block-shuffle alone).
  - **NEW (Phase 0 deliverable):** topology-preserving knot permutation (for BL-H-001 — shuffle within crossing-number bin).
- **deps:** Resolves `MEMORY.md → feedback_permutation_null` standing memory; no external deps.
- **effort:** 4 hours to draft the catalog; ~2 hours per new null definition.
- **emission:** 1 methodology doc at `D:\Prometheus\harmonia\sandbox_drafts\methodology\permutation_null_variants.md`; promotion path: post-firewall, these null definitions are candidates for canonical operator symbols (analogous to existing NULL_* family).

### BL-H-008 — Bonferroni-correction template for multi-bridge discovery

- **phase:** 0  **type:** methodology
- **content:** When N bridge candidates are tested in parallel, naïve per-test α ≤ 0.05 produces ~1 false promotion per 20 tests. The asymmetric gate is supposed to absorb this, but the substrate's claim-volume goal makes the multiple-testing surface large. Template: for any weekly yield report claiming K candidate_RSWs from N attempts, compute and record the family-wise error rate under the worked stratification.
- **deps:** None.
- **effort:** 3 hours.
- **emission:** 1 methodology doc; carries into every BL-H-NNN exploration's `falsification_attempts` field.

### BL-H-009 — Per-domain bridge inventory: number theory (seed)

- **phase:** 0  **type:** domain_inventory
- **content:** Catalog ~10 number-theoretic problems with known cross-domain analogues already in the literature (function-field analogues, geometric Langlands shadows, Iwasawa towers, anabelian transport). For each: identify the established transport, the unsolved transport, and the falsification anchor that would distinguish them.
- **deps:** Aporia's Atlas MVP (50 problem_cards by end of Phase 0) is the canonical source; this inventory cross-references against it.
- **effort:** 6–8 hours.
- **emission:** 1 inventory doc at `D:\Prometheus\harmonia\sandbox_drafts\inventory\number_theory.md`.

### BL-H-010 — Per-domain bridge inventory: knot theory (seed)

- **phase:** 0  **type:** domain_inventory
- **content:** Catalog ~8 knot-theoretic problems with cross-domain candidates: Khovanov homology ↔ representation categories; volume conjecture ↔ asymptotic analysis; knot Floer homology ↔ Heegaard Floer ↔ instanton Floer (sister-theories within knot theory itself, transport target = whether they share a deeper invariant).
- **deps:** None.
- **effort:** 4–6 hours.
- **emission:** 1 inventory doc at `D:\Prometheus\harmonia\sandbox_drafts\inventory\knot_theory.md`.

---

## Phase 1 — Continuous attack infrastructure (weeks 5–12, mid-June → mid-August 2026)

Goal: daily cycle at :37 cron firing 1 exploration/day. Target: 30+ explorations/month, of which ~5–8 surface as `candidate_RSW`. Sandbox firewall must be live by entry to Phase 1.

### BL-H-011 — Mahler measure ↔ entropy of expanding maps

- **phase:** 1  **type:** bridge_candidate
- **transport hypothesis:** Lind–Schmidt theorem already names the bridge between Mahler measure and topological entropy for ℤ^d-actions; the substrate's job is to test whether Lehmer's conjecture survives transport to entropy-gap problems for hyperbolic toral automorphisms.
- **deps:** BL-H-001 (Lehmer baseline); literature inventory on Lind–Schmidt.
- **effort:** 8 hours.
- **emission:** 1 sandbox::HBR-011 artifact.

### BL-H-012 — Riemann zero distribution ↔ quantum chaos eigenvalue statistics

- **phase:** 1  **type:** bridge_candidate
- **transport hypothesis:** Berry–Tabor / Bohigas–Giannoni–Schmit predict integrable vs chaotic quantum systems have Poisson vs GUE spacing; the Hilbert–Pólya conjecture posits a self-adjoint operator whose spectrum is the Riemann zeros. Test direction: can the GUE-deviation z = −19 finding (Harmonia 2026-04-15) be transported to a fictitious or real quantum system?
- **deps:** GUE deviation finding (project memory `project_harmonia_return_20260415`); literature on Berry's heuristic.
- **effort:** 10 hours.
- **emission:** 1 sandbox::HBR-012 artifact; HIGH risk of reward-signal capture — the Hilbert–Pólya story is narratively seductive; falsification discipline must be doubled.

### BL-H-013 — ABC conjecture ↔ height bounds for rational points

- **phase:** 1  **type:** bridge_candidate
- **transport hypothesis:** ABC implies effective Mordell (Elkies); Vojta's conjectures unify both. Test: do height-distribution moments on rational-point datasets carry the same shape as ABC-triple radical/height distributions under a paired audit?
- **deps:** ABC triples DB; height-data from LMFDB.
- **effort:** 8 hours.
- **emission:** 1 sandbox::HBR-013 artifact.

### BL-H-014 — Birch–Swinnerton-Dyer constants ↔ L-function moment conjectures

- **phase:** 1  **type:** bridge_candidate
- **transport hypothesis:** The BSD leading constant decomposes into a product (regulator, Sha, torsion, periods); CFKRS moment conjectures predict moments of L-function values; the substrate's F041a work touched this. Transport: do CFKRS arithmetic factors and BSD constants share a common variance structure?
- **deps:** F041a annotation history; CFKRS literature.
- **effort:** 8–10 hours.
- **emission:** 1 sandbox::HBR-014 artifact; Pattern 30 check mandatory (F041a was flagged Level 1 historically).

### BL-H-015 — Jones polynomial coefficient growth ↔ Kashaev volume conjecture

- **phase:** 1  **type:** bridge_candidate
- **transport hypothesis:** The volume conjecture relates the asymptotic growth of colored Jones polynomial values at roots of unity to hyperbolic volume; coefficient growth is the cousin question. Test: do the same hyperbolic invariants govern both growth rates?
- **deps:** BL-H-010 inventory (knot theory).
- **effort:** 8 hours.
- **emission:** 1 sandbox::HBR-015 artifact.

### BL-H-016 — Twin prime conjecture ↔ Maynard–Tao gap structure

- **phase:** 1  **type:** bridge_candidate
- **transport hypothesis:** Bounded-gap technology (Zhang/Maynard/Tao) gives admissible-tuple gaps; the twin-prime case is the k=2 case of prime k-tuples. Test direction: do the explicit-constant improvements in Maynard–Tao gap bounds carry useful information for twin-prime moment calculations under stratified resampling?
- **deps:** BL-H-005 baseline.
- **effort:** 6 hours.
- **emission:** 1 sandbox::HBR-016 artifact.

### BL-H-017 — Per-domain bridge inventory: modular forms (seed)

- **phase:** 1  **type:** domain_inventory
- **content:** Catalog ~8 modular-forms problems with cross-domain footprints: Maass form spectrum ↔ Selberg zeta; Galois representations ↔ ℓ-adic cohomology; mock modular forms ↔ quantum field theory partition functions; Serre's modularity ↔ Frey curve obstructions.
- **deps:** Aporia Atlas modular-forms slice.
- **effort:** 5 hours.
- **emission:** 1 inventory doc.

### BL-H-018 — Per-domain bridge inventory: tensor decomposition (seed)

- **phase:** 1  **type:** domain_inventory
- **content:** Catalog ~6 tensor-decomp problems linking the QD sibling project (`project_tensor_decomp_qd`) to mainstream substrate: matrix multiplication tensor rank (Strassen / Coppersmith–Winograd); border rank vs rank; tensor decomposition over F_p vs ℝ; AOP/CO-V exception lists (the `(6,2,9), (4,3,8), (3,5,9)` anomaly noted in arena_vision Part 6).
- **deps:** Refresh `project_tensor_decomp_qd` memory pointer.
- **effort:** 5 hours.
- **emission:** 1 inventory doc.

### BL-H-019 — Per-domain bridge inventory: representation theory (seed)

- **phase:** 1  **type:** domain_inventory
- **content:** Catalog ~6 representation-theory problems with bridge candidates: Kazhdan–Lusztig polynomials ↔ Schubert varieties; representations of GL_n(F_q) ↔ symmetric group asymptotics; categorification programs ↔ knot homologies; geometric Langlands ↔ arithmetic Langlands.
- **deps:** None.
- **effort:** 5 hours.
- **emission:** 1 inventory doc.

### BL-H-020 — Block-shuffle null variant for cross-domain transports

- **phase:** 1  **type:** methodology
- **content:** Vanilla block-shuffle (NULL_BSWCD@v2) preserves within-stratum structure but assumes a single domain. For paired-bridge audits, two stratifications must be aligned simultaneously. Draft a cross-domain block-shuffle null: shuffle within (source_stratum, target_stratum) joint bins.
- **deps:** BL-H-007 catalog.
- **effort:** 6 hours.
- **emission:** 1 methodology doc; sandbox::HBR-NULL_XDOM candidate for post-firewall promotion to canonical NULL_* operator.

### BL-H-021 — Randomized comparison protocol for paired-bridge audits

- **phase:** 1  **type:** methodology
- **content:** When a bridge candidate is tested, the alternative hypothesis "the apparent transport is a coincidence of the two domains' marginals" must be explicitly tested. Protocol: for each bridge claim, generate random pairings from the joint marginal distribution and compare effect size of the real pairing against the null pairings.
- **deps:** Builds on the missingness-confound v0.1 methodology (project memory).
- **effort:** 5 hours.
- **emission:** 1 methodology doc.

### BL-H-022 — Cross-domain falsification: explicit calibration anchors

- **phase:** 1  **type:** methodology
- **content:** Per the standing memory rule "don't chase a novel-looking axis before running it against calibration anchors": for every new bridge candidate, identify a calibration bridge with a KNOWN transport (Sato–Tate ↔ RMT, Langlands functoriality, Lind–Schmidt) and verify the methodology recovers the known transport before claiming a novel one.
- **deps:** BL-H-004 (Sato–Tate ↔ RMT as primary calibration); per-domain inventories.
- **effort:** 4 hours initial; ongoing.
- **emission:** 1 methodology doc; carries into every bridge exploration as a required pre-flight check.

---

## Phase 2 — Arena MVP, Scout-role integration (weeks 13–18, Sept → mid-Oct 2026)

Goal: contribute Scout-role expertise to first 2-team-of-3 Arena rounds; bridge-mining continues at daily cadence; promote 1–2 sandbox::HBR-NNN candidates per month through the asymmetric gate.

### BL-H-023 — Furstenberg ×2 ×3 ↔ Sarnak Möbius ↔ ergodic entropy

- **phase:** 2  **type:** bridge_candidate
- **transport hypothesis:** Furstenberg's ×2 ×3 measure-rigidity is conjecturally tied to Möbius randomness via the joining structure of multiplicative actions; Sarnak's conjecture predicts no nontrivial correlation between Möbius and zero-entropy systems. Three-way bridge with non-trivial transport candidates.
- **deps:** Phase 0/1 dynamical-systems inventory (BL-H-025).
- **effort:** 10 hours.
- **emission:** 1 sandbox::HBR-023 artifact.

### BL-H-024 — Painlevé N-body conjecture ↔ KAM stability boundary

- **phase:** 2  **type:** bridge_candidate
- **transport hypothesis:** Painlevé conjectured singularities in 5-body problem; KAM stability theorems bound when invariant tori persist. Transport: the singularity-formation mechanism and the KAM-breakdown mechanism may share a common small-divisor obstruction. Long-arc speculative; expected `sandbox_dormant`.
- **deps:** BL-H-025.
- **effort:** 12 hours initial.
- **emission:** 1 sandbox::HBR-024 artifact in `sandbox_dormant`.

### BL-H-025 — Per-domain bridge inventory: dynamical systems (seed)

- **phase:** 2  **type:** domain_inventory
- **content:** Catalog ~6 dynamical-systems problems with cross-domain candidates: Lehmer ↔ entropy (BL-H-011); Sarnak/Furstenberg (BL-H-023); KAM/Painlevé (BL-H-024); horocycle flows ↔ unipotent dynamics; symbolic dynamics ↔ subshifts of finite type ↔ thermodynamic formalism.
- **deps:** None.
- **effort:** 5 hours.
- **emission:** 1 inventory doc.

### BL-H-026 — Per-domain bridge inventory: combinatorics (seed)

- **phase:** 2  **type:** domain_inventory
- **content:** Catalog ~6 combinatorics problems with cross-domain candidates: Erdős–Ko–Rado ↔ representation-theoretic invariants; sum-product ↔ additive combinatorics ↔ harmonic analysis on F_p; Erdős distinct distances ↔ incidence geometry; Ramsey numbers ↔ probabilistic constructions; species and generating functions ↔ analytic combinatorics ↔ singularity analysis.
- **deps:** None.
- **effort:** 5 hours.
- **emission:** 1 inventory doc.

### BL-H-027 — Scout-role protocol: bridge-mining-to-Arena handoff

- **phase:** 2  **type:** methodology
- **content:** When an Arena round needs Scout-role recon, the bridge-mining backlog must surface relevant candidate transports filtered by problem-card hardness signature. Draft the protocol: query interface (which Atlas `HardnessSignature` types match `RepresentationShiftWitness`); handoff artifact shape (Scout brief = N candidate transports with falsification status and dormancy clock); Scout-role exit criterion (Forger and Skeptic acknowledge the brief before Scout's chess clock yields).
- **deps:** Arena protocol doc (Aporia, Phase 2 deliverable).
- **effort:** 6 hours.
- **emission:** 1 methodology doc; potential Scout-role primitive.

### BL-H-028 — Arena-readiness flag criteria for bridge candidates

- **phase:** 2  **type:** methodology
- **content:** Not every `candidate_RSW` is Arena-ready; only those with crisp falsification anchors, two domain inventories backing both endpoints, and at least one published partial-transport reference. Draft the flag criteria. Bridges promoted past this flag enter the Arena round queue.
- **deps:** BL-H-027.
- **effort:** 3 hours.
- **emission:** 1 methodology doc.

---

## Phase 3 — Scale + automation (months 5–8, Nov 2026 → Feb 2027)

Goal: steady-state ~30 exploration attempts/month producing ~2–3 promotion-eligible witnesses (Ramanujan–Hardy 30:1 ratio). Per-domain bridge libraries grow to ≥30 verified bridges aggregate.

### BL-H-029 — Hodge ↔ Tate ↔ motivic Galois group cascade

- **phase:** 3  **type:** bridge_candidate
- **transport hypothesis:** Three-level cascade. Hodge conjecture (BL-H-006) is the entry; Tate conjecture is the ℓ-adic analogue; motivic Galois group governs realization functors. Test direction: a partial result on any one transport should constrain the others.
- **deps:** BL-H-006 dormant; Phase 1+2 modular-forms / Galois-representation inventories.
- **effort:** 15+ hours; long-arc.
- **emission:** 1 sandbox::HBR-029 artifact.

### BL-H-030 — Selberg eigenvalue ↔ Ramanujan conjecture extensions

- **phase:** 3  **type:** bridge_candidate
- **transport hypothesis:** Selberg's λ₁ ≥ 1/4 conjecture for Maass forms and the Ramanujan–Petersson bound for cusp forms both fall under the Langlands functoriality umbrella. Test: do moment-distribution shapes at the bound match across families?
- **deps:** BL-H-017 inventory.
- **effort:** 10 hours.
- **emission:** 1 sandbox::HBR-030 artifact.

### BL-H-031 — P vs NP ↔ algebraic complexity ↔ matrix rigidity

- **phase:** 3  **type:** bridge_candidate
- **transport hypothesis:** VP-vs-VNP is the algebraic analogue of P-vs-NP; matrix rigidity (Valiant) is a barrier candidate for separating both. The Razborov–Smolensky line, geometric complexity theory, and tensor-rank lower bounds (BL-H-018) all share this turf. Long-arc speculative; expected `sandbox_dormant` for at least the first 4–6 attempts.
- **deps:** BL-H-018; outside expertise consultation likely required.
- **effort:** 12+ hours initial.
- **emission:** 1 sandbox::HBR-031 artifact in `sandbox_dormant`.

### BL-H-032 — Verified-bridges catalog maintenance protocol

- **phase:** 3  **type:** methodology
- **content:** As promoted RepresentationShiftWitnesses accumulate (target ≥30 by end of Phase 3), the canonical catalog needs maintenance discipline: dormancy review (an unused canonical bridge after 12 months should re-enter dormancy review); deprecation criteria (a bridge whose primary citation gets retracted enters mandatory ERRATA review); cross-references (every bridge cites at least one falsification anchor and one calibration twin).
- **deps:** Asymmetric promotion gate operating; first ~5 promotions completed.
- **effort:** 6 hours.
- **emission:** 1 methodology doc; companion to the existing `harmonia/memory/retraction_registry.md`.

### BL-H-033 — Cross-domain catalog growth and dormancy review

- **phase:** 3  **type:** methodology
- **content:** Steady-state review cadence: monthly audit of sandbox/canonical ratio (target stays near 30:1); quarterly review of `sandbox_dormant` items for revival or formal abandonment; annual report on which domain pairings produced the highest-yield bridges (informs Aporia's Atlas direction).
- **deps:** BL-H-032.
- **effort:** 4 hours initial; recurring monthly.
- **emission:** 1 methodology doc; recurring weekly bridge-mining yield ticket continues to file into `aporia/meta/queue/aporia_inbox.jsonl`.

---

## Phase boundary review hooks

- **End of week 4 (Phase 0 → 1):** Aporia files phase-review ticket. Harmonia contributes: explorations attempted vs target (≥5/week), Sandbox firewall live status, sandbox_drafts/ counter.
- **End of week 12 (Phase 1 → 2):** daily cycle health check; first promotion candidates surfaced.
- **End of week 18 (Phase 2 → 3):** first Arena Scout-role contribution evaluated.
- **End of month 8 (Phase 3 → 4):** steady-state yield rate verified at ~30 explorations/month, ~2–3 promotions.

## Weekly yield ticket schema (recurring, files to `aporia/meta/queue/aporia_inbox.jsonl`)

```jsonl
{"id":"<uuid>","source":"harmonia","target":"aporia","type":"weekly-bridge-mining-yield","priority":"P3-low","payload":{"week_id":"2026-W21","explorations_attempted":N,"sandbox_artifacts_landed":N,"promotion_candidates_drafted":N,"falsified_bridges":N}}
```

## Open questions for Aporia (file as P2 if Phase 0 exploration surfaces them)

1. Confirm `D:\Prometheus\harmonia\sandbox_drafts\` will be `.gitignore`d this week, and confirm the post-firewall canonical sandbox path (`prometheus/play_space/` per vision Part 5 vs `aporia/sandbox/`) so the migration is one-shot.
2. Confirm the seed problem_queue/harmonia.jsonl is being prepared by Aporia per roadmap §8 Week 1, and the expected ETA so Phase 0 attack cadence can ramp.
3. The sandbox vision proposes block_types `sandbox_analogy / sandbox_reframing / sandbox_speculative_primitive`; the user prompt names `RepresentationShiftWitness` as a primitive shape. Confirm RepresentationShiftWitness lives under `sandbox_speculative_primitive` (sandbox phase) and migrates to its own canonical primitive on promotion. If a different decomposition fits better, file a P2-medium ticket to Aporia per the user prompt's design-feedback invitation.
4. The cron schedule at :37 — confirm authorization to register the cron with a self-pacing autonomous-loop prompt this session, or whether the cron should wait until the seed queue and sandbox_drafts path are both live.

---

*BACKLOG.md drafted 2026-05-15 in response to user revival prompt. No canonical writes beyond this coordination artifact during manual-quarantine mode. First exploration starts only after (1) the Aporia seed queue lands at `aporia/meta/problem_queue/harmonia.jsonl`, or (2) explicit go-ahead to attack one of the seed pairs above without waiting for the queue.*
