# RED-TEAM REVIEW: E3-KP + E2 pre-registration (PRE-FREEZE)

Target: `beta04/windows/E2_E3KP_PREREG.md` (commit c8e72bfaf, "under red-team before freeze").
Reviewer: independent red-team agent (C-015, W02), 2026-10-10. Read-only apart from this file. No searches or arm runs
were made. The only computation was small Python over existing artifacts: TFS-1 `Enumerator.cumulative` class
counts, `core.size` of the sealed witnesses, and tallies of foundry production JSON (well under 1 CPU-min).

Severity: **BLOCKER** = fix before the freeze; **MAJOR** = fix, or pre-register explicitly, before the first
production outcome; **MINOR** = record, or fix cheaply.

Line references are `E2_E3KP_PREREG.md:<line>` unless another file is named.

---

## 0. Verdict

**REVISE before freeze.** The prereg is honest in framing: it restricts claims to the motif-limited set, labels the
screen as a screen, and keeps the archive OFF at final evaluation. Five problems would make the frozen readouts
uninterpretable, or let them be read either way after the data arrive:

1. **The E2 representation is unspecified (B1).** There is no library choice. Under the natural reading (arm view,
   no library), every R3/R4 family is censored by construction.
2. **The prose does not match the code it names (B2, B4).**
   - "chain_neutral" is not credit-blind in the code.
   - "X1" in the prose is not the code's X1.
   - X1, X2 and X3 are all descriptor-guided, not only X2.
3. **FRONTIER_ARCHIVE_EFFECT maps an all-censored screen to NO (B3).** It also tests against a straw-man baseline.
4. **The freeze cannot cover code that does not exist or disagrees with the text (B5).**
   - There is no E2 driver.
   - The E3-KP runner applies a different scratch rule, and gives a per-world verdict where the prereg pools.
5. **The E3-KP outcome is largely predictable now (M1, M2), and not for the reason the gate is meant to test.**
   - About 10 of the 15 families depend on an R1 stepping stone that is an Int-output program of size 8. TFS-1's
     unpruned 1e6 enumeration covers only about 7% of that size class.
   - All 5 low-risk families depend on the foundry-derived readout fallback.

   A FAIL would mostly report that the base enumerator lacks observational-equivalence pruning, not that composition
   is out of reach. That is a legitimate result, but it has to be pre-registered as a decomposition so the
   first-failing link can be attributed.

Running E2 / E3-KP under E1 = NOT_QUALIFIED is legitimate, with explicit claim limits (s4). Compute is understated by
about 3-4x at the least (s5).

---

## 1. E3-KP (prereg A, lines 9-24)

### M1 -- MAJOR -- The likely FAIL is an R1-acquisition horizon caused by enumerator efficiency and by selection on the foundry's enumerator, not by composition search

**Evidence (pre-data; foundry E1 output plus TFS-1 class counts):**

- **TFS-1 base enumeration class brackets** (`Enumerator(None).cumulative`):
  - Int, size 7: ranks 63,501-627,412.
  - Int, size 8: ranks **627,413-6,007,202**.
  - List, size 8: ranks 90,619-916,438.

  At 1e6, TFS-1 is complete for List through size 8, but covers only about **6.9% of the Int size-8 class**.
- **The foundry's own R1 acquisitions** (`foundry/production/<W>/FINAL.jsonl`, field `chain_c`) show that the
  stepping stones for many constituent units are Int-output programs of size 8. Examples:
  - `(max (map (lam x (mod x (mul 3 3))) xs))`;
  - `(len (filter (lam x (lt x (pow 2 3))) xs))`;
  - `(sub 3 (div (last xs) (mul 3 3)))`.

  The foundry found these at charges of 309k-858k with its pruned enumerator: its level counts are about 4x smaller,
  e.g. 142,673 programs at size 7, against 563,912 for TFS-1 Int. The foundry's enumeration was complete through
  size 7, so no smaller solution exists for these families.

**Per (world, mechanism) unit, using the foundry's found R1 programs:**

| Risk | Units | Admitted R3/R4 families gated |
|---|---|---|
| Low (size-6 readout, List size 7/8, or scan List 8) | Wc025415a f1, p0; W2bdef02f f0 (via F007), s0; Wb49b6a5f p0; W0321d83c f0; W480ffd54 f1, p0; W6eb945cc s0 | -- |
| **High** (both R1 families need an Int size-8 program, or the first is UNDERDETERMINED and the second Int-8) | **Wb49b6a5f f1; W483b8c31 f0, f1, p0; W0321d83c p0; W480ffd54 f0; W6eb945cc f0; W2bdef02f p0** | **10 of 15:** W2bdef02f-F042; Wb49b6a5f-F052, F055; W483b8c31-F045, F046; W0321d83c-F040; W480ffd54-F039, F046; W6eb945cc-F033, F047 |

**The pilot agrees.**
- W0467897d f1: F006 was not found, and F007 (Int, size 8) was found at 763,421, inside the size-8 class.
- W0467897d p0: not found, then spurious.

**Rough expectation.** This is not a measurement. Equivalent spellings in the class, and dev-consistent alternatives,
can move it either way.
- About 3-5 of the 5 low-risk families succeed.
- Each high-risk unit has roughly 10-40% acquisition probability.
- So **chain success is of order 4-7 / 15, against the 12 needed.**

**Why this matters.**
- Admission rule 3(c) selected the 15 families precisely because the *foundry's* enumerator acquired their
  constituents. The foundry's own unconditional acquisition rate was 29/59 mechanisms, and 50/118 R1 attempts
  (`QUALIFICATION_REPORT.md:108-121`).
- Re-running with a weaker enumerator at the same nominal budget is a regression-to-the-mean design: the admitted set
  is the foundry's winners.
- The directive's question, at Exp 3, is "can the typed substrate reach the known-positive depth-2 mechanism". Link
  (iii) answers it; link (i) mostly measures base-enumerator throughput.

**Action (pre-data):**
- (a) Write this prediction into the prereg.
- (b) Pre-register a per-family first-failing-link table (R1 HORIZON / R1 UNDERDETERMINED / (iii) HORIZON / (iii)
  spurious / SOLVED). Add a per-unit acquisition table.
- (c) Add a diagnostic secondary, **(iii-F): TFS-1 chain enumeration using the FOUNDRY-acquired primitives**
  (`chain_c.primitive`). These are learner-found, not sealed. The secondary isolates TFS-1 composition search from
  TFS-1 R1 throughput. Cost is about 15 x 50 s. It is not the gate.
- (d) Declare NOW whether adding observational-equivalence pruning to the TFS-1 enumerator would be the single
  permitted "scientifically neutral repair/retest" (directive constraints) if the FAIL is R1-horizon. If it is not
  declared now, any later repair is outcome-driven.

### M2 -- MAJOR -- The readout fallback carries every plausible pass, comes from the foundry config, and is absent from the E3 organism

**Where it comes from.**
- `tfs1/e3/e3_known_positive.py:83-120` re-implements "abstract a single repeated readout s(xs)" from the foundry's
  QCONFIG `chain_c_mode` text.
- The prereg keeps it (lines 14-15).

**Why it is not neutral.**
- It is not per-family answer leakage. It is a generic abstraction.
- But it encodes the generator's R1 template, `m(readout(xs))`. The directive's falsification list names exactly this:
  "dependence on designed task motifs".

**What depends on it.**
- Every low-risk unit acquired through a size-6 program is a readout form needing the fallback: Wc025415a f1,
  W2bdef02f f0 (F007), W0321d83c f0, W480ffd54 f1.
- All 5 low-risk families (Wc025415a-F041, F044; W2bdef02f-F048, F051; W480ffd54-F055) depend on such a unit.
- **With the fallback OFF, the predicted chain success is about 0-3 / 15.**

**Why it does not transfer.** The E3 lifetime organism's promotion (`E3_RUNNER.md:97-109`) has no readout fallback:
only closed lambdas, plus compressor proposals needing 2 or more uses. So a KP pass obtained via the fallback does
not qualify the procedure that the 2x2 screen would actually use.

**Action:**
- Report a per-family `extraction` flag.
- Pre-register a fallback-OFF row. It needs no new search for (i) and re-runs (iii) only where the library changes.
- Either add the identical rule to organism promotion before the E3 2x2 freeze, or state that a fallback-dependent KP
  pass does not license the 2x2 organism's promotion route.

**Also fix the stale docstring.** `e3_known_positive.py:11` says "No f/p readout fallback (OPEN DECISION KP1)", but
`extract_mechanism` (line 112) applies it. The frozen hash must be of a self-consistent file.

### M3 -- MAJOR -- Within-class order lottery on 5 families under a single keyed seed

These brackets were computed with the production library types.

| Family | Promoted form and class | Bracket | P(witness rank <= 1e6), uniform in class |
|---|---|---|---|
| guard_p: Wc025415a-F041, Wb49b6a5f-F052, W483b8c31-F045 | `(map (lam x (if (q1 x) (q0 x) x)) xs)`; List, size 8, library f+p | 124,979-1,365,260 | about 0.70 |
| post_fold: W2bdef02f-F048, W6eb945cc-F047 | `(q0 (foldl ...))`; Int, size 7, library f+s | 131,402-1,427,485 | about 0.67 |

- The pilot's W1d5301d0-F077 (the guard_p form) was NOT FOUND at 1e6 with exactly this bracket.
- The other skeletons (map_of_filter, filter_of_map, scan_of_map) are size-7 List, at most 137,077, and safe.

Seed 0 with slot = family_id is a single draw. That is fine for a deterministic gate. But a HORIZON on these five is
an enumeration-order outcome.

**Action:**
- Report the static bracket (already computed by `static_diag`), with order-free expected rank = class start + half
  the class. These are about 745k and 779k, both within 1e6.
- Pre-register 2-4 extra keyed seeds for (i) and (iii) as an order-sensitivity secondary, at about 1-2 core-h.
- The primary stays seed 0.

### M4 -- MAJOR -- Constituents-only and the R1-family map are an oracle decomposition; they also diverge from the foundry's chain_d

**What is supplied from sealed data.**
- `r1_families` and `constituents` read WORLD_SEALED `mechanisms_used` (`e3_known_positive.py:164-170`).
- So TFS-1 is told which R1 families teach which mechanism, and which mechanisms the R3 family needs.
- The foundry's chain_d instead used ALL acquired primitives of the world (QCONFIG `chain_d_mode`; KP2).

**Effect on difficulty.**
- Constituents-only is easier. With a 3-entry f+f+p library, the guard_p List size-8 bracket grows to
  164,609-1,916,505 (P about 0.48), and post_fold Int size 7 to 158,743-1,731,572 (P about 0.53).
- This is acceptable for a known-positive *instrument* test: the directive calls a planted solution "an instrument
  calibration".

**Action:**
- Label E3-KP explicitly as an oracle-decomposition instrument test, never as discovery evidence.
- Report the all-acquired library as a secondary, to match the foundry.
- Line 16 says "ONLY its constituent primitives". State that the base grammar is retained (MINOR wording).

### M5 -- MAJOR -- The R1 retry is certifier-guided and unbounded in the text

`run_r1` (lines 173-192) moves to the next R1 family when the first dev-consistent program fails test + tribunal. That
is certifier feedback used during acquisition. It is the same as the foundry, so it is fine for a KP, but:
- the prereg does not say it;
- the number of retries depends on how many R1 families the world has, which is a world property.

**Action:** state it. Report attempts per unit. Ledger the acquisition as CERTIFIER-assisted (cognitive accounting).

### Q: Is the 80% bar sensible on 15 families from 7 worlds?

As a deterministic rule frozen before the data (it is carried over from the draft), keep it. But:
- the 15 families are only **5 merged skeletons**: map_of_filter 6, guard_p 3, filter_of_map 2, post_fold 2,
  scan_of_map 2;
- they rest on **about 17 shared acquisition units**. One unit can remove 3 families: W480ffd54 p0 gates F039, F046
  and F055; W2bdef02f f0 gates F042, F048 and F051.

In practice, 80% means "almost every unit is acquired and at most one skeleton hits the horizon". Do not change the
number post hoc. Add the per-unit and per-skeleton readout (M1b) so the verdict is interpretable.

### Q: Is first-dev-consistent the right rule?

Yes, as the primary: it is learner-realistic and the same as Addendum D rule 2. But with a different enumeration order
than the one that defined admission, it turns order differences into outcome differences. Where the first
dev-consistent program fails, record the number of dev-consistent programs seen. Optionally (descriptive only), also
record "first qualified within budget", to separate under-determination from horizon.

### Other E3-KP items

- **B5 (see s6): the scratch rule mismatches the code.**
  - Line 19 says (iv) "fails on >= 80%".
  - The draft (`E3_DESIGN_DRAFT.md:13`) and the code (`verdict`, lines 263-275) say scratch fails ALL.
  - The code's verdict is per world, `TFS1_INSTRUMENT_QUALIFIED_world`, while the prereg pools 15 families. There is
    no pooled verdict function.
  - Recommendation: revert to "scratch fails all", the pre-production rule. Scratch is near-certain to fail anyway:
    expanded witnesses are sizes 13-19 and TFS-1 completes only about size 8. Add the pooled verdict function.
- **MINOR: R4 tasks have shifted test and tribunal (rule D4); 7 of the 15 families are R4.** An R1-acquired lambda
  that agrees with the sealed mechanism only on the base range fails R4. `agree_sealed` probes [-40, 40]. Report R3
  and R4 separately, and report agreement on the R4 tribunal range.
- **MINOR: 4 of the 15 families come from worlds that FAIL the per-world gate** (Wc025415a and Wb49b6a5f, 2 R4 each).
  Family-level use is fine, but say so.

---

## 2. E2 (prereg B, lines 26-80)

### B1 -- BLOCKER -- The representation and library for E2 are unspecified

Lines 35-45 name the arms but not the library. The arm view (`foundry/production/arm_view/*`) carries dev only, with
no library. There are three possible readings:

| Reading | What it means | Consequence |
|---|---|---|
| (a) `lib=None` | R3/R4 expanded witnesses are 13-19 nodes | Every admitted family already passed rule 3(b): base search from scratch fails at 1e6. Evidence so far: 0 hits on 6 foundry pilot tasks x 8 arms x 4 seeds at 5k (`ATLAS_DESIGN.md:331-342`); 0 R2+ solves in the 2e5 lifetime probe (`E3_RUNNER.md:218-244`). **Expect every cell censored**, so E2 measures only the desert that admission built in |
| (b) Sealed mechanisms promoted | Planted | Instrument calibration only |
| (c) TFS-1- or foundry-acquired primitives promoted | Promoted forms are size 7-9, within the arms' demonstrated range (GRADED toy hits at about 1.8k-25k) | Asks the directive's actual question: are depth-2 compositions reachable from depth-1 stepping stones, with or without an archive? |

**Action:**
- Freeze one reading. Recommended: (c) with the **foundry-acquired** primitives (public E1 artifacts, learner-found,
  target-blind with respect to the R3 family). Ledger them as supplied DEVELOPMENTAL context, not organism
  acquisition.
- Optionally add `lib=None` for chain_neutral only, as the desert reference.
- Specify that D-BEH qualification runs on the witness refactored under that library.
- If (a) is kept, pre-register the expected all-censored outcome and what it can and cannot license.

### B2 -- BLOCKER -- "chain_neutral" is not the credit-blind control; DESERT_VS_RARITY is computed on the wrong contrast

**Prose vs code.**
- Line 40 defines chain_neutral as "credit-BLIND ... acceptance ignores credit".
- In the code, `D1-chain_neutral` accepts iff f(child) >= f(parent) (`atlas/arms.py:28,70` and `:330-333`). That is
  the credit-using neutral chain, equal to A-CHAIN.
- The credit-blind control is `credit="none"` (`arms.py:178-179`; `ATLAS_DESIGN.md:153-156`).

**Why the label then fails.**
- With strict acceptance (`arms.py:66-69`, a single burst), the chain freezes at the first plateau, and permanently
  after any spurious dev-consistent program (key = n_dev; nothing is > n_dev).
- Calibration: chain_strict scored **0/8 on all four toys**, while chain_neutral scored 8/8 on GRADED and 4/8 on DESERT
  (`ATLAS_DESIGN.md:262-263`).
- So "strict > neutral by >= 3" (line 64, CREDIT_GRADIENT) is essentially unattainable. "RARITY" (line 68,
  "otherwise") becomes a catch-all. It even absorbs neutral >> strict, and both arms at 8/8 (REACHED).

**Action:**
- Run the credit-blind chain (`D1-chain_neutral` with `credit="none"`, i.e. A-CHAIN[none]).
- Define the label on **exact-credit neutral chain vs credit-blind chain**, which is the instrument the calibration
  validated (`ATLAS_DESIGN.md:289-291`).
- Replace the table:

| Result | Label |
|---|---|
| Both 0 | DESERT_OR_HORIZON |
| Credit chain minus blind chain >= 3 | CREDIT_GRADIENT |
| Blind chain minus credit chain >= 3 | CREDIT_MISLEADING |
| Both >= 6/8 | REACHED |
| Otherwise | UNRESOLVED |

- Do not use the word RARITY for an unresolved cell. The directive reserves RARITY_LIMIT for E5's higher-power test.

### B3 -- BLOCKER -- FRONTIER_ARCHIVE_EFFECT: an all-censored result reads as NO, and the baseline is a straw man

**(a) Censoring.**
- If every cell is 0, which is the expected outcome under B1(a), every difference is 0 and the sum is 0. Line 73 then
  returns **NO**.
- That turns a finite, censored null into a scientific negative, against the directive's "Do not infer impossibility
  from a finite null".
- More generally, NO fires on a sum <= 0 from a single non-tied family.

**(b) Baseline.**
- The comparator is chain_strict, the arm that freezes on plateaus.
- Archive arm minus chain_strict bundles neutral acceptance (D1 contrast C1) with retention, selection and admission.
- D1's own one-factor ladder compares X1 with **chain_neutral** (C2; `arms.py:27-32`).
- The first leg of the conjunction is therefore near-automatic, and the effective test is only X3 vs X3G.

**Action:**
- Comparator: chain_neutral (credit-using), which the atlas calls Aphrodite's ordinary operator. Keep strict as
  descriptive only.
- Add **INCONCLUSIVE_CENSORED** when fewer than 5 cluster units (s3) have a non-zero difference. With fewer than 5,
  p < 0.05 is unattainable: 2^-5 = 0.031.
- Define NO only as: sum <= 0 AND at least 5 informative units AND the reverse one-sided test is not significant
  (or another pre-stated futility rule).
- Carry D1's interpretive rule forward: "X3 > X3G does NOT mean the descriptor kept stepping stones"
  (`READING_DIGEST.md:150-151`).

### B4 -- BLOCKER -- Descriptor validity and arm definitions contradict the code and EXPERIMENT_PLAN s5.2

**All three archive arms use descriptor cells.**
- In the code, `D1-X1`, `D1-X2` and `D1-X3` all have `descriptor: True` (`arms.py:71-73`).
- X1 is *the elite of a best-scoring D-BEH cell* (`arms.py:310-316`).
- Line 41 describes X1 as "restore uniformly from retained programs". That is `B1-RETAIN` (`arms.py:58`), a different
  arm.

**The eligibility rule picks the unvalidated arm.**
- Line 42 conditions only X2 on D-BEH qualification.
- The per-family rule at line 70 ("X2 if eligible, else X3") therefore selects **X3, a D-BEH-guided arm, exactly on the
  families where D-BEH FAILED qualification**.
- EXPERIMENT_PLAN.md:102-106 makes such an arm INSTRUMENT_UNVALIDATED.
- Line 75 excludes INSTRUMENT_UNVALIDATED arms. The frozen text therefore lets a reader either include or exclude
  those families after seeing the data.

**X3G is matched only to X3.**
- X3G is matched in cell count and restore frequency to X3 (`calibrate_random_k`, `arms.py:472`).
- On X2-chosen families, "that arm minus its matched X3G" (line 71) is a mismatched contrast. X2's structure-free
  control would be X2 with RAND:K (a C2-RAND analogue).

**Action:**
- Use ONE pre-specified archive arm on every family, D1-X3 with its X3G.
- Compute FRONTIER only over families where D-BEH QUALIFIED.
- List all others as INSTRUMENT_UNVALIDATED.
- Report X1 and X2 descriptively, or drop them (s5).
- Fix the X1 prose to match the code, or run B1-RETAIN if retention-without-descriptor is what is meant.

### M6 -- MAJOR -- The E2 hit endpoint gets certifier assistance that E3-KP and the organism do not

`_post_eval` (`arms.py:185-213`) calls `Certifier.verify` on every dev-consistent child. A failed verdict lets the run
continue.

- The neutral chain and the archive arms then do certifier-filtered neutral drift on the dev-consistent plateau.
- X1 makes a spurious dev-consistent elite its permanent parent.
- chain_strict stops dead.

So hit counts partly measure dev under-determination plus evaluator filtering. This violates "a result cannot be
attributed to organism learning when the crucial operation was performed by the ... evaluator". It is also
inconsistent with the first-dev-consistent rule in E3-KP and in the organism (`E3_RUNNER.md:84-85`).

**Action:**
- Primary endpoint: the FIRST dev-consistent program of the run QUALIFIES.
- Secondary: "any qualified within B", with the number of certifier consultations, and hits after one or more rejected
  dev-consistent programs ledgered as CERTIFIER-assisted.
- Also define which tribunal counts. The search uses salt T0; `final_evaluation` uses a FRESH salt FINAL
  (`common.py:224-231`). Line 59 is ambiguous. Recommend: hit = search-qualified AND FINAL-qualified.

### M7 -- MAJOR -- The 4x escalation trigger contradicts the adopted escalation principle

- Line 77 escalates when "every family is DESERT_OR_HORIZON at 1x".
- EXPERIMENT_PLAN.md:117 (Hestia) and ATLAS_DESIGN.md:388 escalate "only when the certified-mechanism rate rises".
- Escalating an all-zero screen is the case Hestia's rule forbids, and it is the expected case under B1(a).

**Action:** escalate only the families and arms with at least one hit at 1x, or drop the all-zero trigger.

### M8 -- MAJOR -- No headroom proof or positive control for the E2 hit definition (EXPERIMENT_PLAN s5.3)

**The headroom proof is missing.**
- Nothing shows that any arm can register a hit at B = 2e5 on these families. The foundry's library-enumeration CRN
  ranks already exceed 2e5 for 3 guard_p families and several R2 families (`E1_ADDENDUM_D.md:46-98`).
- The R2 known-positive was certified on **test only**: QCONFIG `kp_mode`: "first dev-consistent with the SEALED
  mechanisms; SOLVED on test".
- E2 hits need test plus a generated widened-range tribunal with FAIL agreement plus the task tribunal
  (`ATLAS_DESIGN.md:65`). So the E2 standard is stricter than the known positive that admitted the family.

**Action (no search needed):**
- Judge all 53 sealed witnesses, and the foundry's route solutions (expanded), with the atlas `Certifier` at both
  salts.
- Port D1's controls:
  - an arm started AT the target must certify at evaluation 0 and NOT count as discovery;
  - a constant or lookup program must not certify (else VOID_CONTROLS).
- Run the existing target-blindness perturbation test on at least 2 production families per arm, at small B, before
  launch. The plan's E2 gate ("archive target-blind, verified by test") needs a production-side receipt.
- E2 has no AccessLog equivalent to E3's (`E3_RUNNER.md:157`). Load the learner side through `worlds.ArmWorld`.

### M9 -- MAJOR -- REACHABILITY_ATLAS_COMPLETE is undefined, and the directive's atlas measurements are not registered

**The gap.**
- The directive's Exp 2 / Experiment B asks for: existence; density of viable intermediates; mutation robustness;
  observable feedback; revisitability; hitting times and candidate ranks.
- The prereg registers only hit counts.
- The plan's gate (EXPERIMENT_PLAN.md:71) is "Atlas complete on admitted R2/R3".
- Only 8 of the 38 R2 families enter.

**Action:**
- Define REACHABILITY_ATLAS_COMPLETE (YES / NO / INSTRUMENT_UNVALIDATED) as: every listed `M.atlas` quantity is
  recorded, or bracketed as censored, for every family in scope.
- Run `M.atlas` on all 53 admitted families. It costs about 12-18 CPU-s per family, roughly 15 CPU-min in total.
- Run arms only on the subset.
- Resolve the seeded R2 draw (`APHRODITE/B04/E2/R2/<idx>`) now, and list the 8 IDs in FREEZE_E2_E3KP.json.

### M10 -- MAJOR -- Frozen O-items are mis-numbered, and O2's premise is false

**Numbering.**
- Prereg O1-O7 (lines 48-55) do not correspond to ATLAS_DESIGN O1-O12 (`ATLAS_DESIGN.md:405-420`). For example,
  prereg O1 is atlas O4, prereg O2 is atlas O11, and prereg O3 is atlas O7.
- So "the other O-items are as defaulted" (line 56) does not identify which items are meant.

**O2's premise.** "max size = 20 (>= witness sizes)" is false. Measured with `tfs1.core.size`, which equals the foundry
esize, these R2 witnesses exceed 20:

| Family | Witness size |
|---|---|
| W09efdf93-F018-R2 | 21 |
| W6eb945cc-F025-R2 | 21 |
| Wd1490fbb-F021-R2 | 21 |
| W3a22e2ee-F025-R2 | 22 |
| W8f6a223e-F020-R2 | 27 |

R3/R4 witnesses reach at most 19.

**Action:**
- Map every O-item explicitly to the atlas numbering.
- For the 5 oversize R2 families: exclude them from the R2 draw, outcome-free; or raise the size cap; or pre-label
  them REPRESENTATION_LIMIT (witness), with shorter equivalents admissible.
- The issue disappears under B1(c), where promoted forms are 5-11 nodes.

### MINOR (E2)

- **ARCHIVE-ASSISTED vs autonomous is vacuous for genotype archives.** The calibration shows autonomous equals
  assisted on every hit (`ATLAS_DESIGN.md:302-304`). With L = 1, every X-arm step restores from the archive. Define
  the tag by lineage provenance (SEARCH_INFRASTRUCTURE), not by competence, and say that it cannot differ.
- **Restoration correctness on production.** The directive asks to "Test frontier restoration for correctness". Attach
  the `genotype_and_state_restoration` receipt on one production family.
- **Map YES_SCREEN explicitly** to the final field vocabulary (YES / NO / INCONCLUSIVE / INSTRUMENT_UNVALIDATED). The
  directive says "Do not infer statistical significance from screening runs". Recommend final field = INCONCLUSIVE
  (screen-positive; confirmation required).

---

## 3. Multiplicity and statistics at screening scale

### M11 -- MAJOR -- Pseudo-replication in the family-level sign-flip; the test population is unspecified

**Clustering.**
- The 15 R3/R4 families form 5 merged skeletons and about 17 shared acquisition units.
- R2 skeletons also repeat: `R2:p:base_post` 7, `R2:f:base_fold` 6, `R2:s:base_fold` 5.
- An exact sign-flip treats families as exchangeable independent units, so p-values over 15-23 near-duplicates are
  anti-conservative.

**Population.**
- Line 69 does not say whether the test runs over 23 families (R2 + R3/R4) or 15.

**Action:**
- Primary unit = merged skeleton x kind-pair, or world, averaged within the cluster.
- Population = R3/R4 only.
- Report R2 separately.
- Report family-level results as descriptive.

### Other statistical points

- **The conjunction of the two one-sided tests at 0.05 (line 72) is a valid intersection-union test.** It needs no
  correction.
- **All other contrasts are descriptive.** This covers C1-C5 and `empirical_flags`, which the atlas pipeline emits.
  Report them without p-values, or mark them "uncorrected, descriptive".
- **The per-family DESERT_VS_RARITY threshold (>= 3 of 8) has a non-trivial false-label rate.** With mid-range hit
  rates, under exact computation for two independent Bin(8, 0.5) counts, P(d >= 3) = 0.105 one-sided and
  P(|d| >= 3) = 0.21. Across 23 families, expect 2-5 spurious directional labels.
  - Keep the labels descriptive.
  - Any pooled claim ("credit helps on R3/R4") should use the cluster-level sign-flip.
- **Power.** The atlas lead's own note says 8 seeds detect only all-or-nothing contrasts; confirmation needs 24 or more
  (`ATLAS_DESIGN.md:296, 394`). The prereg is consistent with this as long as it claims a screen only.

---

## 4. Legitimacy under E1 = WORLD_DEMAND_NOT_QUALIFIED (strict)

**Running E2 and E3-KP is legitimate.**
- They are instrument and atlas measurements, not the "expensive multi-generation work" that the directive defers.
- The EXPERIMENT_PLAN gate table (line 70) is met at the per-world level: 5/12 worlds.
- E1_V2_RULES says NOT_QUALIFIED "determines what E2-E4 can claim". It does not say "do not run".

### M12 -- MAJOR -- Claim limits and downstream gates must be explicit

1. WORLD_DEMAND_QUALIFIED = NO is carried into every final field.
2. TFS1_INSTRUMENT_QUALIFIED and FRONTIER_ARCHIVE_EFFECT are qualified as follows: "on 2 kind-pairings (fp, fs), 5
   merged skeletons, 7 worlds (4 families from gate-failing worlds)".
3. **The E3 2x2 gate (line 23) requires KP = YES only.** EXPERIMENT_PLAN.md:6 says E1 AND E2 gate everything else. Add:
   REACHABILITY_ATLAS_COMPLETE, the E2 target-blindness receipt, and an explicit coordinator acknowledgement of E1 =
   NOT_QUALIFIED.
4. **E4 does not begin in Beta-04 on these worlds** without a new prereg:
   - R5 = 0, so depth-2 inheritance cannot be demanded (Addendum D item 5);
   - E1 failed the strict reading.
5. No sentence may generalise to "the composition desert" or to "TFS-1" beyond this motif set.

---

## 5. Compute realism (cap: 48 core-h / 24 h, at most 4 workers; hard stop 2026-10-13 09:27Z)

### M13 -- MAJOR -- E2 1x is understated about 3-4x before archive overhead; 4x is not schedulable

**Where the 40 s figure comes from.** Line 84 uses about 40 s per run. That is the lifetime **A-FRESH** rate
(`E3_RUNNER.md:244-254`).

**Measured D1-ladder costs, foundry pilot task W1-F037-R3, B = 5,000, all censored**
(`atlas/calibration/PILOT_W1-F037-R3.json`):

| Arm | CPU-s per run |
|---|---|
| D1-X3 | 6.0-7.5 |
| D1-X3G | 4.3-5.4 |
| D1-X2 | 2.9-3.7 |
| D1-X1 | 2.6-3.3 |
| chain_neutral, chain_strict | 0.4-0.9 |

**Linear scaling to 2e5 (x40):**
- per run: X3 about 270 s; X3G about 190 s; X2 about 130 s; X1 about 120 s; chains about 20-35 s;
- **about 750 CPU-s per (family, seed) for the 6 arms**;
- 23 families x 8 seeds gives **about 38 core-h**.

**Added on top:**
- X3G K-calibration: 3 seeds x 23 families at full 2e5, with no stop on hit; 1-2 iterations; about 5-10 core-h.
  This is not in the estimate.
- **Superlinear archive cost.**
  - With burst = 1, every step calls `_restore`. That calls `live_entries()` and rebuilds the weight list over all
    cells (`arms.py:283-285, 296-327`), so the cost is O(#cells) per step.
  - X3 realised about 1,800 cells by 5,000 charges on the pilot task (`X3G_calibration.ref_realised_cells`).
  - If cells grow even sublinearly to 2e5, the per-step overhead could add of order 10^3 s per X2/X3/X3G run.
    **This is unmeasured.**

**The 4x condition.**
- Line 86 gives 15 x 3 x 8 x 160 s = 16 core-h.
- At measured rates (chain_strict + X3 + X3G at 4x linear), the figure is **about 50+ core-h**.

**Total demand.** E3-KP (2-3 core-h) + E2 1x (at least 43) + E3 2x2 (about 31, per `E3_RUNNER.md:262`) + any 4x
(50 or more). That is more than the rolling cap allows before the 2026-10-13 09:27Z stop, alongside the plan's
120 core-h ceiling.

**Action (pre-data):**
- (a) Time X3 and X3G at 2e5 on an **exposed pilot_v2** family, not a production one, to avoid outcome exposure. Do
  this before freezing B.
- (b) Cut to the arms that carry frozen readouts: credit-chain, blind-chain, X3, X3G, with strict and X1/X2 optional.
  This saves about 35%.
- (c) Pre-register a truncation order to use if the cap binds, e.g. R2 subset first, then seeds 7-8, then 4x. This
  stops compute truncation from becoming an outcome-dependent stopping rule.
- (d) If the archive's O(#cells) cost is confirmed, a neutral performance fix (an incremental weight structure) is an
  instrument repair. Make it before the freeze and re-run the determinism test.

**E3-KP's estimate is realistic.** It is about 1.5-3 core-h. The recommended (iii-F), fallback-OFF, extra-seed and
all-acquired secondaries add about 2-3 core-h.

---

## 6. Freeze completeness

### B5 -- BLOCKER -- The freeze cannot cover what the prereg names

- **The freeze file does not exist yet.** Line 7 says "Hashes are in beta04/FREEZE_E2_E3KP.json"; the file does not
  exist. That is expected pre-freeze.
- **There is no E2 production driver** in `atlas/`. `pilot.py` is explicitly "NOT the E2 production run". So
  family selection, the library, the arm list, seeds, B, K-calibration and label computation are not yet code.
- **The E3-KP runner disagrees with the prereg:**
  - scratch rule: all vs >= 80%;
  - verdict level: per world vs pooled;
  - docstring vs fallback behaviour.

**Action:** write the E2 driver and the pooled KP verdict. Hash both, with the resolved R2 ID list, before any
production outcome.

---

## 7. Recommended pre-data amendments (ordered)

1. **E2 library (B1).** Freeze it: recommended, foundry-acquired primitives promoted (ledgered as supplied
   developmental context). Add an optional `lib=None` chain_neutral desert reference. Refactor the witness under the
   library for D-BEH qualification.
2. **Desert label (B2).** Add the credit-blind chain (`credit="none"`). Define the per-family label on credit-neutral vs
   blind with REACHED / CREDIT_GRADIENT / CREDIT_MISLEADING / DESERT_OR_HORIZON / UNRESOLVED. Make strict descriptive.
3. **FRONTIER (B3, B4).**
   - One archive arm (D1-X3) and its X3G on every family.
   - Comparator = chain_neutral.
   - Population = R3/R4 families where D-BEH QUALIFIED; others INSTRUMENT_UNVALIDATED and listed.
   - Unit = skeleton x kind-pair cluster (M11).
   - Fewer than 5 informative units gives INCONCLUSIVE_CENSORED.
   - NO needs at least 5 informative units and a stated futility rule.
   - Fix the X1 prose to match the code.
4. **Endpoint (M6).** The first dev-consistent program qualifies, on both the search tribunal and the FRESH tribunal.
   "Any qualified within B" is secondary, with the certifier-consultation count and a CERTIFIER-assisted ledger tag.
5. **Escalation (M7).** 4x only for families and arms with at least one 1x hit.
6. **Controls and receipts before launch (M8).**
   - Certifier check of all 53 witnesses and foundry route solutions.
   - Start-at-target and constant/lookup controls.
   - Production target-blindness perturbation per arm.
   - ArmWorld loading with an access log.
   - Restoration receipt.
7. **Atlas completeness (M9).** Define REACHABILITY_ATLAS_COMPLETE. Run `M.atlas` on all 53 admitted families. List the
   8 resolved R2 IDs.
8. **O-items (M10).** Map them to the ATLAS_DESIGN numbering. Handle the 5 R2 witnesses larger than 20.
9. **E3-KP decomposition (M1-M5).**
   - Pre-state the prediction (about 4-7 / 15).
   - Per-family first-failing link, and per-unit acquisition table.
   - Secondaries: (iii-F) with foundry-acquired primitives; fallback-OFF; 2-4 extra keyed seeds plus order-free
     brackets; all-acquired library.
   - State whether observational-equivalence pruning is the single permitted neutral repair.
   - Label E3-KP an oracle-decomposition instrument test.
   - Bring the organism's promotion into line with the readout fallback, or limit what a KP pass licenses.
10. **KP verdict code (B5).** Scratch fails ALL, matching the draft and the code. Add the pooled verdict function. Fix
    the docstring.
11. **Claims and gates (M12).** Restriction text. The E3 2x2 gate also requires E2 completion and acknowledgement of
    E1 = NOT_QUALIFIED. No E4 on these worlds in Beta-04 without a new prereg.
12. **Compute (M13).** Scout timing on pilot_v2 at 2e5. Trim the arm set. Pre-register a truncation order. Make any
    archive-performance repair before the freeze.

## 8. Disagreements preserved

- **Is the readout fallback acceptable at all in an "independent" replication?** This review says it is acceptable,
  *if* it is labelled and paired with a fallback-OFF row.
- A stricter reading would be: the fallback imports foundry design knowledge into the substrate, so E3-KP should be
  primary fallback-OFF.

The coordinator should choose before the freeze and record the choice. This review does not resolve it.
