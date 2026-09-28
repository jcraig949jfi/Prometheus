# P2 synthesis -- endogenous heredity and reproductive machinery (Nestor, 2026-09-27)

Operator directive: `roles/Nestor/prompts/2026-09-27_endogenous_heredity_program/` (sha256 a0fa5c4d).
Theory-aware by date. Nothing here is offered as Selective-Irreversibility evidence.
Durable state: `roles/Nestor/EXPERIMENT_GRAPH.jsonl` (P2 nodes carry the prefix X-P2- or C-ZERO-).
Backlog: `BACKLOG.md`. Work packages: `work_packages/`. Delegate inputs: `delegates/`.

## 0. The headline

W1's two barriers survive, but both are re-described.

1. **Acquisition** is limited by the AVAILABILITY of usable copy-capable material, not by encoding length as such.
   - Donor competence runs entirely through the alias (372/372).
   - The alias's block-write density without a usable copier produces NO donors (SHAM 0/96).
   - The ordinary two-byte copy, simply made present in every initial genome, reproduces ~2/3 of the effect
     (PLANT 32/96 vs 0 plain, 49 dense).
   - The planted copy then disappears from the population (0.76 -> 0.16 of genomes). Donors arise while it is
     common.

2. **Establishment.** "Persistent register state poisons donors" is refuted as stated. Only the ZERO reset rescues
   establishment. A different clean state (0x5A) or a random state does WORSE than carried state, and even
   collapses the first copy.
   - The donors are specialists of the environment's zero initial condition. Most copy without any self-location
     instruction, taking their own address from never-written zero registers and the fixed tape layout.
   - Their own block copy advances HL/DE and consumes that environment-supplied addressing.
   - The establishment barrier is therefore better described as **dependence on environmental scaffolding that
     the reproducer's own action destroys**.
   - This is partly built in by construction: the competence ruler certifies from zeros.
   - **CONFIRMED (C-ZERO-SPECIFIC, fresh donor panel, fresh seeds):** ZERO 26/48 vs CONST 2/48, p = 2.4e-8; CARRY
     6/48; RANDOM 3/48.

3. **The "ffa6 but not 7ae3" split does not replicate.** It does not hold with a fixed implanted donor panel;
   there the state effect is largest in 7ae3. W1's 7ae3 null is best read as low power (8 donor runs per arm), not
   cell physics.

## 1. Adversarial review of W1 (Block A)

| W1 claim | Attack | Test | Outcome |
|---|---|---|---|
| Acquisition limited by encoding accessibility of block copy (C-DENSE-COPY) | Donors may succeed for reasons other than the alias | X-P2-ATTRIB: re-assay 372 dense donors on the stock VM | Competence runs through the alias: 0.93 -> 0.00 in 372/372. Negative control not exercised (no alias-free dense donors exist) |
| same | "Instruction density changes unrelated dynamics" | X-P2-SHAM: same 1-byte block-write density, random src/dst, no usable copier | KILLED: 0/96 donors (plain 0, dense 49) |
| same | "Presence, not encoding" | X-P2-PLANT: a 2-byte ED B0/B8 planted in every initial genome, stock VM, paired seeds | SUPPORTED: 32/96 donors (~2/3 of dense) with the 2-byte encoding; availability is the operative variable |
| same | Horizon probabilities overstate or understate effects (literature pitfall 6) | reanalysis | Open: T-ACQ-7 |
| same | Pair-tape soup vs random-walk search (Knierim 2026) | none yet | Open: T-ACQ-4, WP-5 |
| Establishment limited by register persistence in ffa6 (C-STATELESS-FFA6) | Cell-specific? | X-P2-BRIDGE: implanted fixed panel, 4 cells x 2 states | Split does NOT replicate; W1's 7ae3 null reinterpreted as low power |
| same | "Fresh" = zeros = the ruler's own state (circularity); clean vs useful values | X-P2-REGSTATE: CARRY / ZERO / CONST / RANDOM | ZERO_SPECIFIC: ZERO 0.53 > CARRY 0.28 > RANDOM 0.19 ~ CONST 0.16 (CF). "Persistence per se" REFUTED |
| same | Genome-specific / execution order / success-before-poisoning | X-P2-BRIDGE founder copy ages; corpus Q2-Q4 | "Success before poisoning" not supported (22/31 established founders first copy at age >= 1). Copiers are side-0-specific (1,052 of 1,154) |
| same | Register-subset effects | corpus Q3 | Resetting L/HL restores copying in 10/19 stalled donors; B, C, A and flags never do. No single register works for all |

**Verdict on W1 as a paper:**
- The measured effects are real. C-DENSE-COPY and C-STATELESS-FFA6 both stand as frozen results.
- Both mechanism readings needed revision.
- The establishment reading was wrong in its causal attribution: it was not persistence, it was loss of
  environment-supplied zero addressing.
- The cell-specificity reading was wrong: it was low power.

## 2. ffa6 versus 7ae3 (Block B)

**Resolved as a non-difference in establishment physics.**
- The cells differ in exactly two axes: representation (Z8_64 per-byte mutation with frame shifts, vs Z8_SLOTTED
  slot-aligned edits) and structure (WELL_MIXED vs 4 niches with migration 0.08). The pair epoch pairs across
  niches.
- With a fixed implanted donor panel, the fresh-state effect E is +0.25 in C7, +0.22 in C7S, +0.09 in C7N and
  +0.09 in CF.
- The axes DO raise baseline establishment under persistence: C7 0.13, C7S 0.28, C7N 0.31, CF 0.44.
- W1's split came from which donors arise and how many do. 7ae3 yields fewer spontaneous donors (C-STATELESS had 8
  donor runs per arm there).
- HL-dependence of first donors is similar in both cells (NO_COPY 5/6 vs 9/14; ESTABLISHED 1/9 vs 2/14).
- Open: why SLOTTED and NICHES each raise baseline establishment. Candidates are mutation topology (no frame shifts
  in the copy core) and niche migration (Thread T-WLD-3).

## 3. Self-poisoning (Block C)

"Self-poisoning" is a **symptom, not a causal class**.
- Stalled donors borrow HL (their self-address) from the never-written zero state (14/20 NO_COPY donors depend on a
  fresh HL; 2/22 established donors do).
- Their own LDIR/LDDR advances HL/DE by the copied length (z8.py: LDIR is charged per byte; BC = 0 copies until the
  budget runs out), so the next execution addresses the wrong region.
- It happens in one execution.
- It is reversible by restoring the zero registers (X-P2-REGSTATE ZERO), not by any clean state (CONST, RANDOM).
- Successful self-poisoners are not rescued by copying first: most established founders first copy at execution
  age >= 1.
- The copying machinery itself produces the poison, because the copy primitive's side effect is the address
  advance.
- What separates successful from stalled poisoned donors is still open. Candidates are side schedule (side-0-only
  copiers) and whether a child lands in a zero-state slot (WP-2).

## 4. Copiers that do not locate themselves (Block D)

Not one specimen but **the dominant architecture** (P2 corpus, 1,532-genome stratified sample):
- 95.7% of competent genomes stay competent with OP_SELF removed (7ae3 87.8%, ffa6 99.8%).
- The motif is an offset-64 block copy on the 128-byte wrapped tape: DE - HL = 64 (mod 128) in 98% of side-0
  copiers, and the count is 0 or >= 64 in 95%.
- HL is at the donor's own start or end, taken from never-written zero registers or from aligned immediates.
- The copiers work only at tape offset 0: side-0-only 1,052, side-1-only 102.
- They exploit the environment's zero reset plus the fixed tape geometry.
- Robustness: under the ZERO reset they establish at ~0.5. Under any other entry state they barely copy (S1 0.25).
- Descendants: in persistent-register runaway lineages, competent genomes are mostly state-robust (X-P2-ENDOSTATE:
  0.85 early, 0.88 late).
- This IS the literature's pattern: every published soup where copying emerges supplies self-location through its
  reset constants (EXTERNAL_RESEARCH.md s0.1).

The broader question ("can reproduction exploit inherited/environmental computational context?") is answered YES
for NPE. It is preserved as Threads T-CTX-1..5 and the cross-engine thread XE-ENV-1 (Archaeon: 265/265 random
copiers are environment-gated).

## 5. Descendant-competence decomposition (Block E)

X-P2-BRIDGE stage chain (implanted donors, 8 arms x 32 runs; shares):

    S1 accepted copy 0.72-0.88 -> S2 certified copy 0.56-0.78 -> S3 competent descendant 0.38-0.63
    -> S4 descendant's certified copy 0.38-0.66 -> S5 runaway by epoch 500 0.13-0.53

- The losses concentrate at S2 -> S3 (a certified copy that never yields a competent descendant) and at S4 -> S5.
- STATELESS mainly raises S4 and S5.
- X-P2-REGSTATE: non-zero clean states collapse S1 itself (0.25), so under them the failure moves to the very first
  copy.
- Localizing S2 -> S3 (STRUCTURAL vs STATE vs CONTEXT) is WP-2.

## 6. External research (Block G; delegates/EXTERNAL_RESEARCH.md)

What changed my reading:
1. Every published program soup resets state to useful values; NPE's carried registers remove machinery others get
   free. This predicted X-P2-REGSTATE's outcome.
2. The 2-byte LDIR is not prohibitive on Z80 when registers reset. NPE's ~1% plain acquisition has co-causes.
3. Pair interaction is not a better search operator than a random walk (Knierim 2026). NPE lacks that baseline.
4. Establishment failure is normal even with fresh state (BFF seeded takeover 22%).
5. Avida makes inherited state a switch (EPIGENETIC_METHOD); no published study of it was found. NPE could fill that
   gap.
6. Tierra: stale registers are a hijack channel.
7. Primitive accessibility changes which algorithms lock in (Avida mem-size), and so the downstream evolvability.

Fifteen missing experiments and thirteen pitfalls are entered in BACKLOG.md.

## 7. Cross-engine connections (Block H; delegates/CROSS_ENGINE.md)

- **ACCESSIBLE vs REPRESENTABLE.** Aphrodite slice 4 is the same experiment as the alias. Its attribution + sham
  design was adopted here (X-P2-ATTRIB done; X-P2-SHAM pending).
- **GENOME vs EXECUTION STATE.** Ananke's evolved state-reset bootstrap (T-M3-1) is the precedent for endogenous
  state normalization. Aether's hidden flag breaks a bytes-only causal predicate. Archaeon's MATERIAL-only
  heredity ruler is blind to execution state (XE-LENS-1).
- **ENVIRONMENT AS MACHINERY.** Archaeon: 265/265 random exact copiers are environment-gated (NPE: zero-state +
  layout). BEE: first self-replicators are built by others' copying (XE-ENV-2).
- **ACQUISITION vs ESTABLISHMENT.** An R0 branching decomposition shared with Archaeon and BEE (XE-EST-1).
  "The hard one is not acquisition" holds for NPE only with the dense aid present.
- **Limits.** Register persistence is not a general barrier: stateless engines still fail to establish most
  copiers. Copy-core conservation is not a law (Archaeon lineages keep 0.0 founder material).

## 8. Engine / lens implications (NPE)

1. **Certify from the life state.** Record, and sweep, the entry state in every competence certification (T-INS-ENTRY).
2. **List the environment's injected constants** (reset values, tape offsets, wrap) as machinery (pitfall 4). Zero
   state + offset 0 are self-location.
3. **Report hazards, not horizon probabilities** (T-INS-HAZARD).
4. **Add operand-provenance taint** for copy registers (WP-3). Add longitudinal lineage-tagged capture
   (T-INS-LINEAGE): Hamming distance cannot tell turnover from replacement.
5. **The reset policy is a first-class world axis.** Carried / zero / constant / random reset should be declared per
   world, as Avida does.

## 9. Durable backlog

`BACKLOG.md`: 40 Threads in 8 families, each with a question, why it matters, evidence, prior art, uncertainty,
cheapest discriminator, lens and resource class. The change log is at its foot.

## 10. Research-ready work packages

`work_packages/` WP-1..WP-6:
- WP-1 entry-state decomposition and circularity;
- WP-2 descendant-competence failure;
- WP-3 environment-borrowing copiers;
- WP-4 endogenous robustness and lineage identity;
- WP-5 acquisition rivals;
- WP-6 external synthesis and the minimal-donor landscape.

## 11. Bounded experiments executed (graph nodes)

| node | lane | verdict | one line |
|---|---|---|---|
| X-P2-BRIDGE | EXPLORE | CLEAN_NULL | ffa6/7ae3 split does not replicate with implanted donors; stage chain measured |
| X-P2-ENDOSTATE | EXPLORE | CLEAN_NULL | establishment under persistence sorts already-robust founders (0.85 -> 0.88) |
| X-P2-ATTRIB | EXPLORE | SIGNAL | 372/372 dense donors' competence runs through the alias |
| X-P2-REGSTATE | EXPLORE | SIGNAL (ZERO_SPECIFIC) | only the zero reset rescues; other clean states are worse than carried |
| X-P2-LINEAGE | EXPLORE | WEAK_SIGNAL | late robust genomes: replacement in 9/13 runs, within D0's lineage in 4/13 |
| X-P2-D0CHECK | EXPLORE | CLEAN_NULL | 3 of those 4 D0 sets were already robust; one candidate transition remains |
| X-P2-SHAM | EXPLORE | CLEAN_NULL | 1-byte block-write density without a usable copier: 0/96 donors |
| X-P2-PLANT | EXPLORE | SIGNAL | the planted 2-byte copy gives 32/96 donors; the planted instruction is lost over time |
| **C-ZERO-SPECIFIC** | CONFIRM | **CONFIRMED** | fresh panel: ZERO 26/48 vs CONST 2/48 (p = 2.4e-8); CARRY 6/48; RANDOM 3/48 |

## 12. Resource leases

- **Lease #6** in `agora.gpu_reservations` (slot CPU-POOL-NESTOR, M1, 10 workers, <= 8 GB): acquired 17:01,
  renewed 17:40.
- **Collision.** Ananke W-A held `cpu8` through the host-lease-file convention (`~/ananke_runs/leases/`), and the
  host reached 100% CPU.
- **Yield.** Nestor stopped X-P2-PLANT at 36/96 (resumable) and released #6 at 19:23, announced on comms (#761 and
  #762).
- **Re-acquire.** Ananke released `cpu8` at 19:23:31 (comms #763). Nestor acquired it through the host lease file at
  19:23:47, ran PLANT (resume), SHAM and C-ZERO-SPECIFIC, and released it at 21:31, all announced on comms. The
  record is in `LEASES.jsonl`.
- **Compute.** ~4.5 h of 10-worker pool time, <= ~45 worker-hours, 17:01-21:31. Plus light in-process analyses and
  three delegates (no NPE compute). No GPU, no external spend.
- **The finding.** The program has two lease conventions that do not see each other. One operator ruling would fix
  it (see s15).

## 13. Important nulls and withdrawn interpretations

- **WITHDRAWN:** "persistent register state is the establishment barrier" (refuted by X-P2-REGSTATE; confirmed
  re-description C-ZERO-SPECIFIC: it is loss of zero-state scaffolding).
- **KILLED:** "the alias acts through block-write density" (X-P2-SHAM 0/96).
- **NARROWED:** "acquisition limited by encoding accessibility" -> "by availability of copy-capable material"
  (X-P2-PLANT).
- **WITHDRAWN:** "register persistence is an ffa6-specific barrier" (X-P2-BRIDGE; 7ae3 null read as low power).
- **NOT SUPPORTED:** "successful donors copy before poisoning" (X-P2-BRIDGE founder ages).
- **NULL:** establishment in persistent lineages does not produce robustness afterwards; it selects robust
  founders (X-P2-ENDOSTATE).
- **NULL:** 3 of 4 apparent within-lineage transitions were sorting (X-P2-D0CHECK).
- **CAVEAT:** Hamming distance cannot distinguish replacement from within-lineage turnover in NPE.

## 14. Candidate endogenous transitions (Block N)

- **Candidate:** one lineage (7ae3 seed 16000006; all 5 first donors self-poisoning; every late robust genome in
  their lineage) may have modified its own reproductive machinery to copy from its own post-execution state. It
  is n = 1 and a hypothesis. WP-4 step 1 localizes the change: knock-in/out against the ancestor, classified
  BOOTSTRAP / INSENSITIVE.
- **No evidence yet** of endogenous accessibility (T-END-2) or of decaying environment dependence (T-END-4). Both
  need new instruments (WP-3, T-INS-LINEAGE).
- The honest summary: in NPE so far, crossing the establishment barrier happens mainly by **founder sorting and
  lineage replacement**, not by lineages re-engineering their machinery. The one candidate is the thread to pull.

## 15. What proceeds without the operator, and what needs HITL

**Proceeds without the operator:**
- WP-1..WP-6.
- The re-acquired chain: X-P2-PLANT, X-P2-SHAM, C-ZERO-SPECIFIC.
- Every EXPLORE/CONFIRM follow-up inside the existing charter.

**Needs HITL:**
1. **Lease convention (resource policy).** Declare ONE mechanism for CPU/GPU bursts on M1. Candidates: Ananke's
   host lease file + comms record; the `agora.gpu_reservations` table; or the bus once Redis is back. Seats
   currently cannot see each other's leases.
2. **Engine-level choice (program values).** Should NPE's reset policy be changed to a zero-reset world (as in every
   comparable soup), making the environment-supplied self-location explicit? Or kept as carried state, making "can
   lineages internalize self-location?" the core North-Star problem? This is a direction choice between "study
   heredity where the environment scaffolds it" and "study the endogenization of scaffolding". Recommendation:
   keep carried state as the default, and add the reset policy as a declared world axis. The endogenization
   question is the North Star.

Nothing else needs the operator.

---
**ERRATUM (added 2026-09-28, ARC3):** s2 describes representation as 'Z8_64 per-byte mutation with frame shifts'. For
these cells (OPERAND operator) there are no indels; 7ae3 opcode bytes never mutate. See FINDINGS 'ARC3 -- corrections'.
