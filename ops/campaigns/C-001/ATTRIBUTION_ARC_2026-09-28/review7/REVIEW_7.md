# REVIEW 7 -- adversarial review of the v5 BEE dry run on r022153 (DRYRUN_BEE_r022153.md) and ANCESTRY_PREREG_v5.md

Reviewer: independent claude-opus-5-5 worker, 2026-09-28, checkout ~/Prometheus-worktrees/rev7 at 8262c32f2 (read-only).
Scripts: ~/wk/rev7/out/scripts/ (listed in s7). Scratch data (pickled pre-states, per-birth outputs): ~/wk/rev7/scratch/.

## 0. Summary verdicts

| claim | verdict |
|---|---|
| Replay of r022153 bit-exact (32,827 rows) | STANDS (reproduced, 86 s) |
| Every numeric entry in the dry-run tables | STANDS (all reproduced exactly by re-running the pipeline's own analyse_birth on my replay) |
| (a) singular-donor record adequate, Q8c = 0.0003 | STANDS WITH CORRECTION (the number is right; "adequate for 99.97% of the dependence" is not: the estimand excludes the performer and suppression by construction, and the R2-required Q8c-whether was never computed. For the Q1 class it is 0.88) |
| (b) 14% of transmission births are occupant-performed copies of writer material | STANDS WITH CORRECTION (the mechanism is real, not an artefact of the performer definition. But 18 of the 4,331 are performer "none", not occupant. The phenomenon is a heritable PARASITE, not a "K3 partner-performed copy") |
| (c) native "target" label wrong in 57% | STANDS WITH CORRECTION (191/333 reproduces, bootstrap [0.52, 0.63]. It is 46% without the identifiability filter. The stated mechanism "IBS read as IBD" is wrong for about 90% of these: 183/191 are frame-shifted copies whose native label is decided by chance positional coincidences) |
| (d) 85% of transmission children are isolated self-copiers; "material transmission and capacity transmission mostly coincide" | STANDS WITH CORRECTION (the number holds. The conclusion hides that the Q1 class is 0/120 capable against 117/120 for self-performed births, so the divergence is total and sits exactly in claim (b)'s class) |
| Verdict ALTERED via P2 | ALTERED is mechanically reachable, but WEAKLY WARRANTED: it rests only on P2. P2 as preregistered (R7) was a tautology, was rescued by a post-data amendment, is driven by shift-blindness rather than IBS, and names a BEE-native field rather than the v0 field that R3 demands |
| Amendment C3 "does not change the outcome" | STANDS (it is robust: every reading I tried holds, with lower bounds >= 0.43). The framing "both readings agree" understates that the preregistered reading was not a test at all |

## 1. What I executed

1. **Replay** (r7_replay.py). I reused bee_dryrun_v5.frozen_harness/replay: git show 16fc6c2a, sha256 prefixes checked, Bellerophon's
   traced_replay, and observation-only capture of the pre-state. Result: 32,827 / 32,827 rows identical, in 85.7 s.
2. **Independent labels** (r7_labels.py). I ran the REFERENCE tracer (reftracer/ref_tracer_bee.py, not bee_ref_tracer.py) on all
   32,827 births. It asserts value-equality with the frozen VM on every call, and every child reproduced.
   * Agreement with the pipeline's tracer on real data: per-birth data-entity counts are identical on 32,827/32,827 births.
   * Performer counts differ on 1 birth.
3. **Pipeline re-run** (r7_pipeline_rerun.py). I ran the dry run's own analyse_birth, with the same RNG seed and order, on my
   replay: 279 s, one core. This recovers the per-birth outputs the committed JSON lacks. Reproduced exactly:
   * NO_MATERIAL 183, TRANSMISSION 30,945, identifiable 0.9518;
   * classes self 28,091 / other 4,684 / none 52;
   * Q1 0.140, Q8c_tx 0.0003;
   * Q2: native writer 30,739, of which 52 are P-majority; native target 333, of which 191 are W-majority; overall 243/31,072.
4. **Concrete births** (r7_show.py: disassembly of both tapes, fetch path, per-locus labels). Births 11595, 5154, 16433 and 1757 are
   Q1; births 2356, 19836 and 10204 are native-"target" with W majority.
5. **Store-PC audit of Q1** (r7_perfpc.py). This is a patched copy of the reference tracer that also records the PC address of the
   store that last wrote each window byte.
6. Q4 split by class (r7_q4.py), Q8c-whether (r7_whether.py), per-class flip coverage of "other" (r7_flip_other.py), the Q2
   decomposition (r7_q2.py), and the draw check (inline): sha256(hex SHA string) mod 53 over the sorted eligible runs gives index 13
   = r022153. The draw reproduces.

## 2. Claim (b): "the occupant's code performs the copy" -- real, but misdescribed

**Is it an artefact of "performer = material label of the store opcode byte"? No.**
- r7_perfpc.py covers all 4,333 births whose data majority is w and whose performer-label majority is o.
- In each one, the majority of window loci were last written by a store instruction located at a WINDOW address (64..127) whose
  opcode byte carries an occupant label: 276,654 loci are (o-label, window PC). The exceptions are 473 (w-label, window PC),
  17 (w, own tape) and 168 (non-entity).
- So address and label agree. The occupant's bytes really are the instructions that copy.

**What actually happens (concrete births):**
- **Birth 11595:** the writer is 64 bytes of 0xC2 (an undefined opcode = NOP), with one 0x65, and no HALT. Its PC slides off byte 63
  into the occupant at 64. The occupant contains LD T,64 ... LDIR at +0x29, with S = 0 from reset and C = 0 (a wrap: LDIR sweeps
  until the budget). That copies bytes 0..63, the writer, over the occupant.
  * The child equals the writer's pre-tape exactly; the row shows by_own_code = 0.
- **Births 5154 and 1757:** the same pattern with an occupant COPYALL (LD T,64 ; ... COPYALL). Birth 16433: the same with an
  occupant LDIR.
- **Across the class:**
  * 3,592 of 4,333 Q1 writers (83%) contain NO LDI/LDIR/COPYALL byte anywhere in their tape. For self-performed births the
    figure is 0 of 27,728.
  * 365 Q1 writers are all-zero tapes.
  * The first PC in the window comes at step ~52-64 (median about 62): a straight fall-through.
- **Heritability:**
  * 3,793 of 4,313 Q1 writers (88%) were themselves born by a Q1 birth.
  * 1,549 Q1 births have >= 10 consecutive Q1 generations above them.
  * Self-performed writers were Q1-born in only 13 of 26,614 cases.
- **Capability:** Q1 children are 0/120 capable in the dry run's own isolated Q4 test (mean trial success 0.021). Self-performed
  children are 117/120 capable (0.973).
- **Existence dependence:** randomising the occupant group (K = 8) suppresses the birth in 0.882 of draws for Q1 births, and in
  0.000 for self-performed births.

**What this means:** this is a Tierra-style PARASITE lineage.
- Tapes with no copy code propagate by executing into a host replicator. The host's absolute-addressed copy loop (S = 0, T = 64)
  copies whatever sits at 0..63 over the host itself.
- "K3-type partner-performed copy" suggests a partner offering a copy service. In fact the partner is the victim, and the
  performer is the host's hijacked replication machinery.
- The dry run's point that v0 must separate performer from donor is correct, and if anything understated: in 14% of births the
  existence of the birth is conditioned on a second entity.

**Correction on the count:**
- Q1 in the transmission class = 4,331 births (0.140). Of these, 4,313 have performer P and **18 have performer "none"**.
- In those 18 the store opcode's label is INPUT or CONSTANT (e.g. birth 19836: the LDI opcode byte had earlier been written from
  an input byte), and bee_dryrun_v5 maps a non-entity performer to "none".
- So "All are performer = OCCUPANT" is false for 18 births. This is immaterial to the rate.

## 3. Claim (c): native "target" wrong in 57% -- real disagreement, wrong mechanism, selection-dependent size

**How BEE computes the native label:** traced_replay recomputes it the same way world.py does. The label is "target" iff the
positional Hamming fidelity to the pre-interaction occupant exceeds the positional fidelity to the writer's POST-execution tape.

**Reproduction and decomposition** (r7_q2.py, with reference-tracer labels): 191 of 333 identifiable target-labelled births are
W-majority.
- 183/191 are FRAME-SHIFTED copies (source locus != own index for more than half the loci). Examples:
  * birth 2356: child[i] = w[i+1];
  * birth 10204: the same shift. Its native fidelities are writer 0.000 and target 0.031, so the label was decided by 2 bytes
    that coincide with the mostly-zero occupant.
- In 169/191 BOTH native fidelities are < 0.2. The native label is then a coin-flip between two near-zero positional matches.
- Only 18/191 have target fidelity >= 0.5, the genuine "IBS read as IBD" case. Example: birth 19836, where the occupant is itself
  a shifted relative of the writer and target fidelity is 0.969.

**So the headline mechanism is mostly wrong.**
- The native label fails mainly because positional fidelity is blind to shifts: a shifted copy has about 0 positional identity
  with its true source.
- This is exactly P1's phenomenon (the "fidelity-by-position misreads descent" consequence), which P1 declares rare (3.6% of
  loci).
- P2 "holds" because nearly every target-labelled writer copy is a shift.

**How big the 57% is depends on the selection:**
- Identifiability drops 111 P-majority, 23 W-majority and 88 NONE target-labelled births.
- Over all 467 target-labelled births with a W or P majority, W-majority is 46%, not 57%.
- Both readings are >= 10%.
- Bootstrap for the C3 reading (birth-level, 2,000 resamples): 0.574 [0.520, 0.628]. The dry run reports no interval, although R7
  requires one.

**Scope:** "target" births are 556/32,827 (1.7%). Overall, the native label disagrees with copy-descent in 0.78% of identifiable
births. The document gives both numbers, but the headline "wrong in 57% of the births it calls target" invites a much larger
reading.

## 4. Claims (a) and (d)

**(a) Q8c = 0.0003 is correct as computed, and nearly guaranteed by construction here.**
- For self-performed births the only groups outside {donor, performer} are the occupant, which is overwritten, and one input
  byte. The run's task is INC with NEUTRAL scoring, so inputs are behaviourally inert.
- For Q1 births the performer (P) is excluded, so the only outside group is INPUT.
- The dependence that matters in this run is excluded from Q8c by definition: the host's control of whether the parasite is
  copied at all (0.88 suppression).
- R2 says Q8c-whether "is reported separately". The pipeline never computes it: `supp` and `nd` are allocated and unused, although
  the docstring claims Q8c-whether.
- The pipeline also counts suppressed writes as value changes. R2 says "among draws in which the write occurs". This errs
  conservative and is negligible here.
- "ADEQUATE for 99.97% of the dependence" should read: "0.03% of transmission loci change value when entities other than the
  donor and the performer are randomised; existence dependence on the performer (0.88 in the Q1 class) is not measured by Q8c".

**(d) The 85% [79, 90] figure is consistent with my split:** 0.86 x 0.975 + 0.14 x 0 = about 0.84.
- "Material transmission and capacity transmission mostly coincide" is true only as an average of two classes that are 97.5% and
  0%.
- Q4 is literally "material without capability", and the answer is: all of the Q1 class.
- The isolated test also cannot see the parasite's contextual capability. It persists for >= 10 generations with 0% isolated
  capability.
- capable() does not check v4's "by its own stores" clause (it compares only the window with the child). That makes no
  difference for these tapes.

## 5. Does the pipeline implement v5 as written?

| item | finding |
|---|---|
| R1 identification | provenance + K = 8 interventions: implemented. The flip clause is applied only to the 201-birth sample, not per birth (identifiability share 0.95 ignores flips). Acceptable given 0 FAILED, but not "as written" |
| R2 Q8c | value-change share over outside groups: implemented. Suppression is not separated (conservative). Q8c-whether: NOT computed. Estimand: mean of per-birth means rather than the mean over loci (equal in practice here) |
| Bootstrap | boot() resamples births (valid birth clustering for per-birth statistics). The `clusters` argument is unused. No interval for P2 |
| Classes | as R1. "none" absorbs INPUT/CONSTANT performers |
| Flip coverage floor | v4 s2.1 says ">= 50% PER CLASS". The pipeline computes a pooled 0.79. From the dry run's own JSON, class "other" = 910/(910 + 786) = **0.537**. My fresh sample of 60 "other" births: 0.578, 95% CI [0.497, 0.651], with 22/60 births below 0.5. The class that carries claim (b) passes the gate only by its point estimate |
| Sample stratification | v4 s4: by class AND Q4 capability. The pipeline stratifies by (class, transmission) |
| Per-byte precision | 0.17, below R5's original 0.20 gate (INSTRUMENT_FAILED). Amendment C1, committed with the draw (9cd6bb4ed) but before the r022153 dry run, made it non-gating. The C1 reasoning (r025144: 0.096) is sound, but the verdict depends on it and the dry-run document does not say so |
| Verdict | The script outputs "VALIDATED (pending ...)". ALTERED was set by hand in the markdown: no prediction logic exists in code |
| Traceability | The Q2 numbers in the document (30,739/52, 333/191, 243/31,072) are not in dry_r022153.json. They come from the uncommitted .births.json.gz on C:/. I could reproduce them only by re-running |
| "C2 does not affect verdict inputs" | Essentially true. C2 only enlarges addr/ctrl sets, which can only lower the completeness leak; identification is interventional |

## 6. Amendment C3, and whether ALTERED is warranted

**Does the outcome depend on C3? Formally, no.**
- The literal R7 gives 100% ("holds" by construction). C3 gives 57% [52, 63].
- The no-identifiability reading gives 46%.
- With target-labelled births under 2% of the total, any reading lands far above 10%.
- C3 is honestly flagged.

**But the honest description is sharper than "both readings agree".**
- As preregistered, P2 could not fail on any run with at least one target-labelled transmission birth. It was not a test.
- The engine verdict ALTERED rests ONLY on P2, since Q8c alone gives VALIDATED. So the verdict's only discriminating input is a
  post-data evaluation set.
- The mechanism behind that input is shift-blindness, not IBS/IBD confusion.

**R3 also says each ALTERED route must "name the v0 field required".**
- P2's consequence names a correction field for BEE's NATIVE label, which is not a v0 field.
- If ALTERED is meant to be a statement about attribution v0, P2 is the wrong route to it.
- The v0-relevant findings are two, and neither is an ALTERED route under v5:
  * the performer role is load-bearing (claim b);
  * existence dependence on the performer is large and unmeasured by Q8c.

**My ruling:** "P2 holds" is correct, and the correction the dry run proposes should read "use copy-descent / alignment-aware
resemblance, not positional fidelity". Calling this an ALTERED verdict on v0 overstates it. A defensible reading is:
- VALIDATED on Q8c (pending);
- P2 holds, as a BEE-native-label finding;
- plus an undeclared finding: a heritable parasite class, 14% of births, 0% isolated capability, 88% host-dependent existence.

## 7. What v5 still gets wrong

1. **Q8c excludes the performer entirely, and Q8c-whether never gates.** In a world with parasites, the second party that
   decides whether descent happens is invisible to the only gating estimand. v5 would call a run VALIDATED with 100% parasitic
   births.
2. **R5 defines the transmission class by the same quantity** (writer-majority copy-descent) that label-vs-descent predictions
   compare against. C3 fixed P2 only. Any future prediction of the form "label X vs descent" on this class has the same defect.
3. **Q4 isolated capability cannot distinguish "incapable" from "capable only with a host".** v4 s7 acknowledges only the survival
   confound.
4. **Per-class gates** (flip coverage, completeness) are specified per class but have no interval rule. The pipeline pools them.
   The Q1 class sits at the 50% floor.
5. **The ALTERED route via predictions** has no requirement that the consequence be a v0 field. P2's consequence is a BEE-native
   field.
6. **Painting still passes as transmission.** Example: birth 4 is an LDIR self-overlap fill, with all 64 child bytes labelled
   (w, 0). Source diversity averages it away (0.997), but P1 and Q8c count its 64 loci as copying.

## 8. Scripts (~/wk/rev7/out/scripts/)
- r7_replay.py: frozen-harness replay; pickles the pre-states.
- r7_labels.py: reference-tracer labels for all births.
- r7_show.py: disassembly and paths of chosen births.
- r7_perfpc.py: store-PC audit of Q1.
- r7_pipeline_rerun.py: the dry run's analyse_birth on all births.
- r7_q2.py: all Q2/Q1 recomputations, the decomposition and the bootstrap.
- r7_q4.py: Q4 by class.
- r7_whether.py: Q8c-whether.
- r7_flip_other.py: per-class flip coverage with CI.

Run order: replay, then labels, then pipeline_rerun, then the rest. Run from any directory; the scripts cd into the checkout.

## 9. Single strongest objection

The headline "producer != donor in 14%" is a heritable parasite lineage, not a partner-performed copy: code-less writers (83% have
no copy opcode) run off their tape into a host's replicator, their children are 0/120 capable, and randomising the host suppresses
88% of those births. Q8c excludes that dependence by definition, so "singular-donor record adequate for 99.97%" and "material and
capacity mostly coincide" come from the choice of estimand; and the only route to ALTERED, P2, was a tautology as preregistered, was
rescued after the data, and is driven by frame-shifted copies whose native label turns on 1-3 coincidental bytes, not by IBS read
as IBD.
