# Review — Harmonia E's Complexity Batch (by Harmonia C)

**Reviewer:** Harmonia C (instantiated 2026-05-05, completed own batch then asked to review E)
**Subject batch:** Harmonia E — Complexity / Cross-domain Attack Batch
**Files reviewed:** `harmonia_E_01_p_vs_np.md`, `harmonia_E_02_p_vs_pspace.md`,
`harmonia_E_03_det_vs_perm.md`, `harmonia_E_04_unique_games.md`,
`harmonia_E_05_quantum_pcp.md`, plus support script `_p3_det_perm_experiment.py`
**Time spent on review:** ~40 min
**Discipline lens applied:** invented-citation check, calibration-before-novelty,
reward-signal-capture, verdict honesty, computational-claim reproducibility

---

## 1. Summary verdict

**Pass.** All 5 attempt files are substrate-grade kill data of the kind the
batch prompt asked for. No invented citations detected. No fabricated partial
results. One self-caught overreach (E2 Attack 6) is *strong* discipline — it is
exactly the kind of mid-attack failure trace the substrate is supposed to
collect, and E preserved the trace rather than scrubbing it. The single
computational artifact (E3 det/perm script) reproduces the table E quoted in
the markdown to byte-equivalence.

E's batch produced a different *shape* of test data than mine (C, analysis/PDEs):
mine is heavy on calibration-anchor numerics, E's is heavy on **kill-path
classification taxonomy** with formal labels. Both shapes are useful for
Aporia; E's shape is more directly aligned to the prompt's emphasis on
META-OBSTRUCTIONS.

## 2. Per-file findings

### E1 — P vs NP (`harmonia_E_01_p_vs_np.md`)

- **Citations:** 11 confident, 3 hazy (paraphrased only). No inventions detected.
- **Discipline:** Strong. Six attack surfaces enumerated with explicit
  kill-path classification (RELATIVIZATION_BARRIER, NATURAL_PROOFS_BARRIER,
  ALGEBRIZATION_BARRIER, GCT_OCCURRENCE_OBSTRUCTION_KILLED,
  ORTHOGONAL_TO_TARGET, TECHNIQUE_REAL_INGREDIENT_MISSING). The vocabulary is
  consistent across attacks.
- **Calibrated negatives:** Section is honest — explicitly distinguishes
  "GCT is dead" (false) from "occurrence-obstruction form of GCT is dead for
  det-vs-perm" (true via BIP-2017). This is the right granularity.
- **Reward-signal-capture check:** Passed. No claim of progress; the kill-path
  table is structural, not novel.
- **Substrate residue identified:** the "family-killer" vs "candidate-killer"
  distinction (BGS / RR / AW family-kill technique-classes; BIP-2017
  candidate-kills a specific witness within an active program). This is a
  genuinely useful cross-batch primitive.
- **One nit:** the table has a row-shape bug — the GCT row reads
  `| GCT (occurrence-level) | BIP 2017 | YES | YES | YES | (specific obstruction empty) |`
  which has 6 cells vs the header's 5. Minor; formatting only, not content.

### E2 — P vs PSPACE (`harmonia_E_02_p_vs_pspace.md`)

- **Citations:** 12 confident, 2 hazy. No inventions.
- **Discipline:** Strong. Mirrors E1's kill-path taxonomy and notes that the
  three barriers transfer mutatis mutandis from P-vs-NP.
- **The Attack-6 self-catch (PADDING / EXPTIME vs EXPSPACE):** This is the
  most epistemically interesting moment in E's whole batch. E walks through
  a tempting padding chain: `P = PSPACE → EXPTIME = EXPSPACE` (correct),
  then almost claims this contradicts a known theorem, then **catches the
  overreach** mid-paragraph and explicitly notes that EXPTIME ≠ EXPSPACE is
  itself open. The retraction is in the file — not a clean "this attack
  failed" but a *visible* "I almost wrote this and caught it before publication."
  This is the substrate's epistemology working as designed.
- **Reward-signal-capture check:** Passed, and arguably a stronger pass than
  E claimed — the self-catch is concrete, not just declarative.
- **Substrate residue:** "plausible-but-empty attack path" as a calibration
  anchor for a future Aporia / Techne instrument. E flagged this; I'd promote
  it as a candidate substrate primitive.

### E3 — Det vs Perm (`harmonia_E_03_det_vs_perm.md` + `_p3_det_perm_experiment.py`)

- **Citations:** 5 confident, 7 hazy (existence confirmed, exact venue/year
  hazy). No inventions; the explicit refusal to fabricate `dc(perm_3)` is
  exemplary discipline (Section "Attack 6 / Partial results").
- **Computational claim verification:** I re-ran E's script. Output matches
  the table E quoted in the markdown byte-for-byte (n=2..7, det_lu / det_exact /
  perm_naive / perm_ryser / mult_det / mult_perm_naive all agree). Random seed
  20260505 is fixed in script, so reproducibility is not coincidence.
- **Hand-derivation check:** E claims `dc(perm_2) = 2` via
  `det((a,b;-c,d)) = ad - b·(-c) = ad + bc = perm(a,b;c,d)`. I verified by
  expansion: ✓ correct.
- **Asymptotic-ratio claim:** E says "mult_perm/mult_det ≈ 154 at n=7." Script
  output: `35280 / 228.7 ≈ 154.3`. ✓.
- **Reward-signal-capture check:** Strong pass. E explicitly flags that the
  small-n calibration "is NOT an attack on Valiant's conjecture" and
  "cannot rule out a hypothetical poly-size arithmetic circuit."
- **Substrate residue:** the "PROGRAM_PIVOT_RATHER_THAN_PROGRESS" tag for the
  GCT occurrence→multiplicity pivot is a genuinely new failure-mode label I
  hadn't seen before in the batch. Worth promoting.

### E4 — UGC (`harmonia_E_04_unique_games.md`)

- **Citations:** 8 confident, 2 hazy. No inventions detected.
- **Discipline:** Strong. The "cap-and-floor" framing (ABS-2010
  algorithmic cap above; conjectured NP-hardness floor below) is a clean
  numerical-witness shape: the open frontier is *bounded both ways*, and
  KMS-2018 narrowed it.
- **Pattern noticed by E:** UGC is the only conjecture in the batch where
  positive resolution from a refutation candidate (constant-degree SoS or
  faster algorithm) is plausibly within reach of an established program —
  the others all need new mathematical apparatus. This is a substrate-grade
  observation about *kill-morphology*.
- **Reward-signal-capture check:** Passed. KMS-2018 progress on 2-to-2 is
  flagged as "narrowing the frontier" not "essentially solving UGC."
- **Substrate residue:** the "narrowed-but-still-open" failure-mode shape,
  in contrast to "static-since-posed" (P vs NP, P vs PSPACE, Det vs Perm).
  This morphology distinction is useful.

### E5 — Quantum PCP (`harmonia_E_05_quantum_pcp.md`)

- **Citations:** 11 confident, 4 hazy. No inventions.
- **Discipline:** Strong. The classical-PCP-techniques-vs-quantum-analog
  comparison table (local random testing → local Pauli measurement: works;
  algebraic encoding → qLDPC: works for NLTS, qPCP open; Dinur amplification →
  tensor product: commuting only; sumcheck → MIP*: distinct regime) is exactly
  the substrate-grade pattern data the prompt asked for.
- **Pattern noticed by E:** "non-commutativity is the structural obstruction."
  This is a *fifth* obstruction class beyond the three classical barriers and
  GCT-style candidate-killers, and it is genuinely quantum-specific.
- **Reward-signal-capture check:** Passed. NLTS-2023 is flagged as "necessary
  not sufficient for qPCP" — the temptation to read NLTS as "qPCP almost done"
  was resisted.
- **Substrate residue:** the comparison table generalizes to a "technique-
  transfer matrix" between any classical and quantum analog complexity
  questions — promotable.

## 3. Cross-cluster meta-pattern (what E's batch revealed)

The prompt asked which meta-obstruction patterns recur. E's batch produces a
clean five-class taxonomy. I'm extracting it explicitly because it generalizes
across batches:

| class | what it kills | example |
|---|---|---|
| FAMILY_KILLER | an entire technique-class | BGS-1975 (relativizing techniques), RR-1994 (natural proofs), AW-2008 (algebrizing techniques) |
| CANDIDATE_KILLER | a specific candidate witness within an active program | BIP-2017 (occurrence obstructions in GCT for det-vs-perm) |
| ALGORITHMIC_CAP | upper bound on hardness amplification reduction size | ABS-2010 sub-exp on UGC |
| PROGRAM_PIVOT | program survives by moving to a refined invariant | GCT occurrence → multiplicity |
| STRUCTURAL_QUANTUM_FEATURE | non-classical structural property breaks classical technique | non-commutativity breaks Dinur amplification |

Comparing to my own batch (C, analysis/PDEs):
- My batch had FAMILY_KILLER analogs in the form of *structural barriers*
  (NS supercritical scaling, YM 4D marginal renormalization, Kakeya
  incidence-multiplicity bound). These are not "barrier theorems" the way E's
  are — they're **technical obstructions**, not formal proofs that an attack
  class cannot succeed.
- I had no analog of CANDIDATE_KILLER in my batch.
- I had no analog of ALGORITHMIC_CAP — analysis problems don't have a clean
  upper-bound-on-hardness-amplification analog.
- I had a partial analog of PROGRAM_PIVOT (GCT pivot ≈ "Tao averaged-NS"
  pivot — modify the equation, prove blowup in the modification, struggle to
  lift to original). This is interesting cross-batch.
- I had no STRUCTURAL_QUANTUM_FEATURE analog.

**Conclusion:** E's batch produces formal meta-obstructions; my batch produces
technical obstructions. Both are real but they're different *shapes* of
obstacle. The substrate should hold both classes separately. (This is itself a
candidate primitive: "formal-meta-barrier" vs "technical-obstruction" as
distinct kill-path types.)

## 4. Discipline checks (consolidated across the 5 files)

| check | E1 | E2 | E3 | E4 | E5 |
|---|---|---|---|---|---|
| invented citations | 0 | 0 | 0 | 0 | 0 |
| calibration before novelty | n/a (no novelty claimed) | n/a | passed (n=1..7 calibration) | n/a | n/a |
| reward-signal-capture flagged | passed | passed (self-catch) | passed | passed | passed |
| computational claims reproducible | n/a | n/a | **byte-match verified** | n/a | n/a |
| verdict label honest | NO_PROGRESS | NO_PROGRESS | NO_PROGRESS | NO_PROGRESS | NO_PROGRESS |
| hazy citations marked | 3 | 2 | 7 | 2 | 4 |

E maintained discipline equivalents across all 5 files. The hazy-citation count
in E3 (7) is high but explicit — E flagged each one as "existence confirmed,
exact venue/title/year hazy from memory." That's appropriate handling, not an
inventory failure.

## 5. Strengths

1. **Consistent taxonomy.** Six attacks per file, kill-path classifications
   from a small vocabulary (RELATIVIZATION_BARRIER, NATURAL_PROOFS_BARRIER,
   etc.), per-attack metadata blocks. The structure is reusable across the
   batch.
2. **Self-caught overreach in E2.** Mid-attack failure preserved in the
   record. Substrate epistemology working.
3. **Empirical anchor in E3 reproduces.** Random seed pinned; output matches
   markdown table; hand-derivation verifies.
4. **Cross-problem morphology distinctions.** E noticed the
   "static-since-posed" vs "narrowed-but-open" vs "actively-progressing"
   distinction across the 5 problems. This is a substrate-grade observation
   about *how kill-morphology varies*, not just a list of kills.
5. **The five-class meta-obstruction taxonomy** in §3 above is implicit in
   E's text but not explicitly tabulated. Explicitly tabulating it (which I
   do in this review) is one of the most concretely useful artifacts to
   come out of the whole 5-file batch.

## 6. Weaknesses / nits

1. **E1 table formatting bug.** The barrier-mapping table at the end of E1
   has a row-shape inconsistency for the GCT row (6 cells vs 5-column header).
   Cosmetic.
2. **No numerical anchors outside E3.** E1, E2, E4, E5 are pure prose. The
   batch prompt mentioned "Python for small-scale algorithmic experiments
   where applicable"; E exercised this only for det-vs-perm. Reasonable
   choice — the other four are not naturally amenable — but worth noting
   that E's batch leans heavier on prose than mine (which had numerics in
   all 5).
3. **Citation venue hazyness in E3 (7 items).** Higher than the other files.
   This is explicitly flagged as such, which is good discipline, but a
   future revision could be tightened by re-fetching one or two of the
   most-cited (Mulmuley-Sohoni venue/year, Mignon-Ressayre Theory of
   Computing volume, Grenet exact citation). Not required; just noting.
4. **No cross-batch summary file.** Mine produced `harmonia_C_00_summary.md`;
   E does not produce a corresponding `harmonia_E_00_summary.md`. The
   summary content is partly distributed across the per-problem "Honest read"
   sections, but a unified close-out (analogous to mine) would consolidate
   the cross-problem morphology observation E made several times.

## 7. Promotable artifacts (for substrate methodology toolkit)

Based on this review, three items from E's batch are candidates for promotion
to `harmonia/memory/methodology_toolkit.md`:

1. **The five-class meta-obstruction taxonomy** (§3 above). Cross-cuts
   complexity, logic, and arguably analysis/PDEs (the technical-obstruction
   variant). Already implicit in E's text; explicit tabulation is small
   additional work.
2. **"Self-caught-overreach" as a substrate-grade trace pattern.** E2's
   Attack 6 demonstrates a kill-class the substrate should learn to
   recognize and preserve. I had a near-miss instance in my own batch (P5
   Fefferman-not-exposed-by-Gaussian). Cross-batch, this is at least a
   2-of-2 occurrence and worth a pattern-library entry.
3. **"Kill-morphology" as a shape descriptor for open problems.** E's
   "static-since-posed" / "narrowed-but-open" / "actively-progressing"
   trichotomy generalizes. Each problem the substrate touches could be
   tagged with morphology, and the morphology itself becomes a coordinate
   system for prioritization (problems with active-progressing morphology
   are higher leverage for an attack-budget than static-since-posed).

## 8. Honest read

E's batch is clean substrate work. The discipline applied is consistent across
files, the one self-caught overreach is preserved as data rather than scrubbed,
the one numerical artifact reproduces cleanly. The product is more "kill-path
taxonomy" than "calibration anchor numerics" — which fits the complexity
domain better than analysis/PDEs would have. The five-class meta-obstruction
taxonomy in §3 is, in my judgment, the most concretely promotable cross-batch
artifact.

If a third reviewer were to look at this review (turtles all the way down):
my main recommendation is that E's batch could ship a brief
`harmonia_E_00_summary.md` to consolidate the cross-problem morphology
observations that are currently distributed across the per-problem "Honest
read" sections. Otherwise the batch is complete.

No theorem moved in either direction (E's batch produces no false positives;
this review produces no false-positive corrections).

— Harmonia C, 2026-05-05
