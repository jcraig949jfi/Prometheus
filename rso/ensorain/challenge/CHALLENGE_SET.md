# C-016-T040 -- Q3 challenge set against FREEZE_ENSORAIN v1.0.0 (committed BEFORE any outcome)

Pallas[harry1-855aa018], claude-fable-5-1 (Q3), 2026-10-11. Surface: rso/ensorain at freeze code commit 93623a03a
(FREEZE.md; FROZEN.json b198ab8f, 26/26 verified at base a5699de6e, EXPOSURE.md). Authority: operator Continuous
Observatory directive 2026-10-11 s9; packet ops/campaigns/C-016/tasks/C-016-T040/TASK.json. Rules of this set: no
production file is changed in any commit; a semantic edit is applied to the working copy of THIS worktree only, the
frozen suite is run against it, and the file is restored byte-for-byte (sha256, `git diff --quiet`, then
`freeze check` OK); every lifetime uses a CHALLENGE seed (16_350_001..16_359_999, disjoint from PREREGISTRATION s6 and
from every WTP-05 registered range; subjects_c.conflicts() == [] is checked before any case runs); no confirmatory
seed, no `assay confirm`, no searched-subject endpoint; one process; ensorain/ read-only; nothing on ubu006.

Three surfaces, as the packet names them: INFERENCE (PREREGISTRATION s5 decision rule, s7 power, s11.2 pairing;
analysis.py), INSTRUMENT (s4 memory_check / recompute_check, G_PRE as the Smuggler separator, the s3 four-policy
argument; assay.py, subjects.py), INTERPRETATION (s1 question, the s5 licensed readings, search accessibility).
Composition: 5 sound, 3 broken (one semantic), 2 probes, 1 comparator, 6 edits (5 predicted to survive the suite,
1 control predicted killed). Predictions are in expected.json and repeated here; they are the answer key.

## 1. Scoring

    case    AS_EXPECTED       the frozen machinery does what the preregistration says and the prediction held
            SURVIVOR          a demonstrated gap between what the registered inference / instrument / reading
                              CLAIMS and what the frozen machinery can SUPPORT
            NOT_AS_PREDICTED  the prediction failed; reported with the observed value (an honest miss)
            RECORDED          a probe, with its prediction checked
    edit    KILLED            the frozen unittest suite fails on the mutant (behaviour pinned)
            SURVIVES          the suite passes; a WITNESS then says whether a committed input distinguishes
                              original from mutant. The hash guard (`freeze check`, `assay confirm`) fires on every
                              edit by construction and is reported separately: it protects the run, it pins nothing.
    surface CLOSED            no survivor whose bearing requires an amendment or an explicit narrowing before the
                              confirmatory result is read; NOT CLOSED otherwise

Bearing per survivor: NONE (mechanical), NARROWING (a reading must be narrowed before use), AMENDMENT (a s2-s7 change
is needed before the run), BLOCKING (the run should not start).

## 2. Subjects (subjects_c.py; every one is the reference graph, planted.py:115-116, with its plastic CONST
re-initialised, except clock_hybrid)

| Name | theta0 | eta | sigma | What it is for |
|---|---|---|---|---|
| reference | +0.2 | 1.0 | 0.5 | the known answer at the challenge seeds (comparator) |
| jitter | +0.1 | 1e-9 | 0.5 | B1: fixed pre-switch prior + perturbation noise, no learning |
| innate_max | +1.0 | 1.0 | 0.5 | B2: nothing learnable before the switch |
| learns_pre | -0.1 | 1.0 | 0.5 | S5: the pre-switch law is learned in-life, then revised |
| nan_plastic | NaN | 1.0 | 0.5 | P1: the bound check |
| clock_hybrid | phi -1.0, c 1.0, d -0.25 | 0.5 | 0.5 | P2: the best law-blind timer TAPE allows, and why it is a reviser |

## 3. Cases (cases.py; results.jsonl)

### Sound

S1 FREEZE-HASHES (instrument). Every FROZEN.json entry recomputed without freeze.py: `git show HEAD:<path>`, CRLF to
LF, sha256, against the pin and against the working tree. PREDICTION: 26/26 equal; freeze.mismatches() empty; the
environment equal.

S2 THRESHOLDS-POWER (inference). From first principles (math.comb, Fractions): k_pos(400, .05); the Holm worst-case
critical count; q(.05), q(.10) from the 400 development reference lives by an independent pair loop; the four power
entries of s7. PREDICTION: 217 (P(X >= 217) = .0494), 221, q .570 / .624, power .778 / .999 (P) and .523 / .988 (S)
within .005. Also recorded: what family S's power would be at alpha/6. Ten of its sixteen tests are p = 1 by
construction: a genome with no plastic key draws nothing from the rng in tape.lifetime (tape.py:305, :313-324, :344),
so its full, frozen and shuffle arms are the same computation and every pair ties (DEV_QUALIFICATION shows the
pattern for memoryless_plus and the constants: 400 ties). Holm over 16 with 10 forced ones is conservative, not
invalid; the registered worst case already says alpha/16.

S3 GATE-SPACE (instrument; the s3 four-policy argument). 200 blocks of C-R2-desert at K = 64: the distinct observation
vectors at the scored step per role, whether the corridor step is ever scored, whether the type-1 target is s * law.
PREDICTION: 2 and 2 (s = +1 / -1; tag, fG, bias fixed; payload channels other than the role's are 0), 0, yes. With z
= 0 at step 0 (tape.py:171) a deterministic genome's scored action is a function of s alone, so the deterministic
memoryless class on type-1 gates is exactly {+s, -s, +1, -1}: memoryless_plus, smuggler, constant_plus,
constant_minus. The N1-N4 collapse is a theorem of the world, not a fitted observation.

S4 DEV-REPRODUCE (instrument). The 400-seed development run re-executed: rows_sha256 must equal 1d5ccf28... (FREEZE.md
says a second run already reproduced it; this is a third, from a different worktree). PREDICTION: equal.

S5 LEARNS-PRE (interpretation; the honest positive). theta0 = -0.1: in block 0 the subject acts +s only ~42% of the
time (P(-0.1 + 0.5 e > 0)), the ES gradient (correct episodes have e > 0.2) pushes theta up, and within 1-2 blocks it
is on the pre-switch law; at the switch it revises. This is what "revise a lifetime-LEARNED parameter" (s1) actually
looks like, and the frozen instrument should accept it. PREDICTION: pre-competent lives >= 170 of 200 (sw >= 4, so
blocks 1..sw-1 carry the majority), REVISION_HISTORY_DEPENDENT.

### Broken

B1 JITTER (inference -> instrument; the claim-critical one). A fixed pre-switch prior (+0.1) plus the perturbation
noise the ES machinery adds whenever eta, sigma > 0, and NO learning (eta = 1e-9: tape.py:305 keeps the perturbation
on; the update, tape.py:349, moves theta by ~1e-8 per block). On every type-1 gate it acts +s with probability .58,
before and after the switch. Its frozen arm (plasticity off: no perturbation) is the deterministic +s policy with late
accuracy 0. PREDICTION: G_PRE holds (>= 180 of 200 lives have a pre majority: p = .58 over >= 128 gates); K1 full
beats frozen on the late window in >= 190 of 200 pairs (.42 against 0); K2 is a fair coin (wins in [86, 114], p >
.05; this doubles as S6, the empirical null of the s11.2 pairing with diverged rng streams); G_R5 holds (type 2 is
q = s, untouched); verdict REVISION_NOT_HISTORY_DEPENDENT, whose licensed reading (s5 table) is "revises; dependence
on own history not shown". Nothing was revised. s11.4 says K1 "is nearly automatic for any genome whose frozen arm
keeps the pre-switch sign"; the sharper statement is that the frozen arm removes the PERTURBATION together with the
learning, so K1 is passed by noise alone, and the four-policy argument (deterministic policies) does not reach the
noise class. Bearing if SURVIVOR: NARROWING of the K1-only row before any result is read; AMENDMENT candidate for the
repair round (a noise-matched control with plasticity on and eta -> 0, or a registered qualification control Q-d:
jitter must not be REVISION_*). Three searched subjects carry a plastic parameter with eta .059 / .33 / 1.0 and
sigma .13 / .14 / .02; for them REVISION_NOT_HISTORY_DEPENDENT would be uninterpretable.

B2 INNATE-MAX (interpretation). theta0 = +1.0 = PLASTIC_BOUND: before the switch the gradient points into the clip and
nothing is learned; the pre-switch competence is entirely innate. PREDICTION: REVISION_HISTORY_DEPENDENT (the
post-switch gradient pulls theta down from 1.0: the flipped episodes, e < -2, are the correct ones; as theta falls
the pull grows and the sign flips within ~4 blocks), with a K2 win fraction below the reference's at the same seeds
(the shuffle arm's clipped random walk also leaves the boundary, toward the interior). Bearing if SURVIVOR:
NARROWING of s1: "revise a genome-initialised plastic parameter". For the reference itself the law SIGN is innate
(theta0 = +0.2) and only the magnitude is learned pre-switch; S5 is the learned case.

B3 G_R5-SEMANTICS (interpretation; synthetic rows, no lifetime). N = 400, every life pre-competent, K1 400 wins, K2 300
wins; 180 lives have ZERO role-5 accuracy after the switch. PREDICTION: G_R5 holds (220 >= 217 = k_pos of a chance-1/2
binomial) and the verdict is REVISION_HISTORY_DEPENDENT, read as "keeps the unrelated competence"; at 184 it is
REVISION_WITHOUT_RETAINED_COMPETENCE. Bearing if SURVIVOR: NARROWING: the threshold borrowed from a chance test has no
justification for a retention-of-competence statement; the licensed reading is "in significantly more than half of
the lives". Not blocking (the reference: 400/400 on development seeds).

### Probes

P1 NAN-PLASTIC (instrument). assay.memory_check bounds a plastic value with `np.any(np.abs(ya) > PLASTIC_BOUND)`,
False for NaN. PREDICTION: memory_check(g, g, True) == (True, 8); in a non-plastic arm np.array_equal(NaN, NaN) is
False so memory_ok is False there; the N = 40 verdict is INSTRUMENT_FAULT. It fails closed by the accident of the
comparison, not by the bound. Bearing NONE; one `np.isfinite` for the repair round if wanted.

P2 TIMER-HYBRID (instrument + interpretation; the wake note's "Smuggler that learns the first sign then flips on a
block counter"). Could a plastic genome pass G_PRE and the late window by flipping at a TIME rather than by reading
the law? The only cross-block channel is the ES update of a plastic parameter theta: eta * sum_k z(r_k) e_k / (K
sigma) (tape.py:342-349), whose expectation is non-zero only if the block's rewards depend on theta's own
perturbation e. Two reward channels exist. (i) Type-2 (role 5, never switches): a law-INDEPENDENT drive of strength
n2 * phi(t2) / (K sigma sd(r)) per block, with t2 the distance of theta from its type-2 flip point in sigma units and
phi the standard normal density. (ii) Type-1: whatever parameter the type-1 action reads receives a law-DEPENDENT
gradient n1 * phi(t1) / (K sigma sd(r)), pointing toward the pre-switch side before the switch and toward the
post-switch side after it. A timer needs the drive (i) to carry the parameter across its type-1 flip point before
the switch; at that point t1 = 0 and phi(0) is the maximum of phi, so with n1 ~ n2 the pull is at least as strong as
any drive: in expectation the parameter stalls below the flip point before the switch (for clock_hybrid at (d - c)/2
= -0.625) and crosses only after it. Re-weighting the 8 components linearly cannot change the ratio (the readout and
the drive see the same information about theta; Cauchy-Schwarz), and a second parameter cannot relay the drive (its
gradient depends on its own perturbation only; cross terms vanish). The discrete regime (sigma small, eta / sigma
large: one update jumps over the coupling window) escapes the pull, but the ES estimate's per-block signal-to-noise is
bounded by n_c phi(0) / (sqrt(K) sd(r)) <= ~3.7 (n_c = 32 coupled episodes, K = 64), every waiting stage of a cascade
random-walks with step eta / (sqrt(K) sigma), and G_PRE at sw = 8 needs the flip at block >= 5: a 5-stage one-shot
timer cannot fire reliably. CONCLUSION (analytic): no TAPE genome implements a law-blind timer that passes G_PRE in
expectation; the four-policy argument extends to plastic genomes, EXCEPT the noise class of B1, which needs no timer.
PREDICTION (a): the assay reads clock_hybrid as a reviser, REVISION_HISTORY_DEPENDENT or (G_R5 marginal: type-2
accuracy ~.77 at the equilibrium) REVISION_WITHOUT_RETAINED_COMPETENCE, K1 >= 190, K2 >= 150 wins, late accuracy
above the reference's (it is poised 0.4 below its flip point, the reference 1.0 above). PREDICTION (b), the control
the assay lacks, run outside it: with the law never switching (w.sw = 99) clock_hybrid's type-1 accuracy in blocks
7-11 stays above 1/2 in >= 90 of 100 lives (no timed flip); the reference >= 95; innate_max 100; jitter ~.58 mean.
If (b) fails (<= 50), the hybrid IS a timer and the finding is BLOCKING. Either way the no-switch arm is the cheap
control that would make the timer question empirical for any searched subject; recommended for the repair round
(descriptive, like newlife).

### Comparator

REF200: the reference at the 200 challenge seeds (REVISION_HISTORY_DEPENDENT; K1 ~198:0; K2 ~125:75).

## 4. Edits (edits.json; run_edits.py; mutation_rows.jsonl)

    E1  analysis.py:70   verdict reads the raw p, not the Holm-adjusted      SURVIVES   W1 synthetic family
    E2  analysis.py:50   G_PRE counts the frozen arm's lives                  SURVIVES   W2 learns_pre refused
    E3  assay.py:119     late window starts at sw + 2                         SURVIVES   W3 window counts differ
    E4  analysis.py:55   K1 <-> K2 controls swapped                           SURVIVES   W4 jitter NOT_SHOWN
    E5  assay.py:131     frozen arm runs plastic (control)                    KILLED     --
    E6  analysis.py:45   gates pass on a simple majority                      SURVIVES   W5 205/400 admitted

Why these: the frozen suite pins the instrument (DeclaredMemory: four leak classes; Endpoint: integer counts, frozen
late = 0; Subjects: both Smugglers refused) but the DECISION RULE only through the development verdicts of the
smuggler and the reference, which are insensitive to the Holm step, the window start, which arm a gate reads, which
control a contrast uses, and the exact threshold. Every suite kill is behavioural: no test hashes the tree
(test_confirm_refuses_on_changed_bytes mocks file_sha; the CLI test refuses before the hash). The hash guard is
`freeze check` / `assay confirm`, recorded with each mutant in place.

## 5. Predicted state of the three surfaces (to be confirmed or corrected in REPORT.md)

    INFERENCE        NOT CLOSED: K1 is passed by noise (B1); Holm, the window and the threshold are unpinned
                     behaviourally (E1, E3, E6). The sign test, its pairing and the power table are sound (S2, S6).
    INSTRUMENT       NOT CLOSED on the control set: memory_check / recompute_check sound on every input tried (S1,
                     S4, P1 fails closed); G_PRE separates every deterministic forbidden policy (S3) and, by P2, every
                     plastic timer; the registered controls lack the noise class (B1) and a no-switch arm (P2).
    INTERPRETATION   NOT CLOSED: "lifetime-learned" (B2, S5), "unrelated competence kept" (B3), the K1-only
                     "revises" (B1) and "search accessibility" over 8 subjects of which 5 cannot be revisers by
                     construction (S2 note) need NARROWING before any result is read.

## 6. Ordering

This file, expected.json, subjects_c.py, cases.py, witnesses.py, edits.json, run_edits.py and EXPOSURE.md are
committed in one commit before any case or edit is run; results.jsonl, mutation_rows.jsonl and REPORT.md follow in a
later commit; `git diff <set commit> HEAD -- <the set files>` must be empty at the end.
