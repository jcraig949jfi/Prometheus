# C-016-T042 -- Q3 re-check set against FREEZE_ENSORAIN v1.1.0 (committed BEFORE any outcome)

Pallas[harry1-7368c61b], claude-fable-5-1 (Q3; comms boot tier heavy), headless on harry1 (M4), 2026-10-11. Surface:
rso/ensorain at FREEZE_ENSORAIN v1.1.0 (FROZEN.json fcfe67ce, 34 files; code 6fff93af9; amendment 030f1746f; re-freeze
ebe4860c1), base 28b5c5e1c. `freeze check` OK before the claim (34/34). Authority: operator Continuous Observatory
directive 2026-10-11 s9 step 7 (re-check the repaired surface; no further repair); packet
ops/campaigns/C-016/tasks/C-016-T042/TASK.json. Rules: no production file is changed in any commit; a mutant is applied
to the working copy of THIS worktree only, tested, and restored byte-for-byte (sha256, `git diff --quiet`, then
`freeze check` OK); every lifetime uses an R2 seed (16_360_001..16_369_999, declared in subjects_r2.py, disjoint from
PREREGISTRATION s6, from every WTP-05 registered range and from the T040 challenge range; `conflicts() == []` is
checked before any case runs); no confirmatory seed, no `assay confirm`, no searched-subject lifetime (FS reads genome
structure only); one computing process at a time (the mutation runner's parent waits on its child: two at most);
ensorain/ and roles/Ensorain/ read-only; nothing on ubu006.

Scope (TASK.json `problem`): confirm the repair closes REPORT s4 without opening a new hole. Not an open-ended second
challenge. There is no repair round after this: a survivor becomes a recorded limitation the result must carry.

## 1. Scoring

    case    AS_EXPECTED       the repaired machinery does what PREREGISTRATION v1.1.0 says and the prediction held
            SURVIVOR          a demonstrated gap between what the registered inference / instrument / reading CLAIMS
                              and what the repaired machinery can SUPPORT
            NOT_AS_PREDICTED  the prediction failed; reported with the observed value
            RECORDED          a probe, with its prediction checked
    edit    RED               the named v1.1.0 test fails on the mutant (behaviour pinned)
            KILLED            no named test, but the suite fails (the E5 control)
            SURVIVES          both suites pass on the mutant
    surface CLOSED            no survivor whose bearing requires a narrowing or a limitation before the confirmatory
                              result is read; NOT CLOSED otherwise (with exactly what the result must state)

## 2. Exposure

The v1.1.0 code, tests, DEV_CHECK.json (all development verdicts, incl. my T040 subjects at N = 400) and red_rows.jsonl
were read before this set was written; this is an informed re-check, not first-sight. The searched genomes were read for
STRUCTURE (SUBJECTS.json: node lists, eta, sigma, plastic flags); no endpoint of any searched subject has been computed
in any form. The abstract random-walk model in s5 was computed before the predictions (it is a design calculation on a
model, not a run of the instrument on the genome).

## 3. Subjects (subjects_r2.py)

| Name | Definition | For |
|---|---|---|
| reference, jitter, innate_max, learns_pre, innate_zero | as T040 (subjects_c.py; innate_zero = ref_like(0, 1, .5)) | re-runs |
| walker | reference graph with type-2 = constant +1 (chance); theta0 +0.5 plastic, eta .024, sigma .01 | WK: law-blind random walk |
| ratchet | ref_like(+0.5, .024, .01): walker with type-2 = q (correct) | RT: search that halts on success |
| ref_tiny5 / ref_tiny4 | the reference rescaled by 1e-5 / 1e-4 (theta0 .2 s, sigma .5 s, eta s^2, readout x 1/s) | TN: the absolute ETA_NOISE floor |
| searched_dead | memoryless_plus + an unconnected plastic CONST, eta 1, sigma .5 | FS: family S from structure |

## 4. Cases and predictions (cases_r2.py; expected_r2.json is the answer key)

### Sound (the repair as frozen)

S1 FREEZE-HASHES-ORDER. All 34 pins recomputed without freeze.py (git blob and disk, LF); FROZEN.json's own LF sha256 =
fcfe67ce...; freeze.mismatches() and env_mismatches() empty; 030f1746f is an ancestor of ebe4860c1 and its committer
time is earlier; ebe4860c1 is an ancestor of HEAD. Also recorded, unscored: the files under rso/ensorain/ that
freeze.files() would pin at a RE-CUT but FROZEN.json does not list (my R2 files and T040's unpinned set; `check` reads
the manifest, so added files are invisible to it). PREDICTION: all hold.

S2 THRESHOLDS. From first principles (math.comb, Fractions): k_pos(400, .05, 1/2) = 217, k_pos(400, .05, 9/10) = 371,
k_pos(200, .05, 1/2) = 113, k_pos(200, .05, 9/10) = 188; the frozen ruler.thresholds and analysis._gate /
_competence agree at the edges (217 / 216, 371 / 370); analysis.power_revised at the recorded development rates
reproduces DEV_CHECK.json `power` P_n400 within .001. PREDICTION: all hold.

S3 NOISE-ARM-DRAWS. The reference on 5 R2 seeds: the world's episodes (obs, tgt, role) are identical block for block
between the full arm and the noise arm, the switch block is the same, the noise arm's theta moves <= 1e-6 over the
life, the full arm's moves >= 0.3. PREDICTION: all hold (noise_matched keeps sigma, so the perturbation draws are the
same count and the world's rng stream coincides; tape.py:320, :349).

S4 DEV-REPRODUCE. The v1.1.0 development check (8 controls + innate_zero, innate_max, clock_hybrid; seeds
16_300_001..400; 26,400 rows) re-executed; rows_sha256 must equal b54c751b... PREDICTION: equal.

GR5 BOUND. Synthetic six-arm rows at N = 400: 180 zero-role-5 lives -> G_R5 False, REVISION_WITHOUT_RETAINED_COMPETENCE
(B3 closed); 30 zero lives -> False; 29 -> True (371 of 400 kept); every life at 178/200 post role-5 (89%) -> 0 kept,
False; every life at 180/200 (90%) -> 400 kept, True. PREDICTION: as stated. Bearing: NONE; this is what s5.2 says; the
result must read "9 lives in 10 keep >= 90% of post-switch role-5 gates", not "keeps the competence".

B3 (re-run) the T040 input under the repaired rule -> REVISION_WITHOUT_RETAINED_COMPETENCE. PREDICTION: closed.

### Re-runs under the v1.1.0 rule (N = 200 R2 seeds, six arms)

B1 jitter. PREDICTION: REVISION_NOT_SHOWN; K1n EXACTLY 0:0:200 (its noise arm is itself); K1f alone p < .05 (the
frozen +s policy is never revised while jitter is revised in a few lives by variance); Holm K2 > .05; G_PRE and G_R5
hold. Endpoint sub-prediction (s4 attack on `revised`): jitter's full-arm revised lives come from lives with few late
gates: >= 55% of them have sw >= 7 (one or two late blocks); none of the frozen arm's.

S5 learns_pre. PREDICTION: REVISION_HISTORY_DEPENDENT; pre-competent >= 170; K1n wins >= 100, losses <= 3.
P3 innate_zero. PREDICTION: REVISION_HISTORY_DEPENDENT; Holm K2 <= .05.
B2 innate_max. PREDICTION: REVISION_HISTORY_DEPENDENT.
REF reference. Comparator: REVISION_HISTORY_DEPENDENT (RECORDED).

### Attacks on the new parts

WK WALKER (broken, inference; aimed at the intersection-union K1). A genome whose type-1 action is s * theta with
|theta| >> sigma (the perturbation never flips the decision, so the standardised ES gradient on theta is
reward-uncorrelated noise) and whose type-2 action is a constant (chance: the block's rewards always have spread, so
the gradient is never zero). theta is a law-blind clipped random walk, step ~ eta * 8 / (K sigma) = 0.3 per block, from
+0.5. Its frozen arm and its noise arm (eta 1e-9: step 1e-8) are the fixed +s policy and are never revised. Its full
arm is revised whenever the walk stays positive for most of the pre-switch blocks and sits negative for most of the
late blocks -- by the abstract model of s5, in about 20% of lives, with G_PRE held in about 88%. PREDICTION:
G_PRE holds (pre-competent >= 140 of 200); G_R5 fails (role-5 retained <= 5: type-2 is at chance); K1f and K1n each
>= 25 wins, <= 2 losses; Holm K2 > .05 (the shuffle arm is the same walk); verdict REVISION_WITHOUT_RETAINED_COMPETENCE;
noswitch late-majority lives <= 170 (it flips without a switch; the reference class gives 200); memory_ok and
recompute_ok on every row. SURVIVOR if the verdict is any REVISION_*. Bearing if so: a REVISION_* label whose K2 does not
hold is CONSISTENT WITH LAW-BLIND DRIFT; "revises within a life" is not licensed for such a subject; the discriminators
are K2 (fails for drift) and the descriptive noswitch count (drift flips without a switch). NARROWING of the s5
readings for REVISION_NOT_HISTORY_DEPENDENT and REVISION_WITHOUT_RETAINED_COMPETENCE, and a limitation the result
must carry for any family-S subject with either label. Not blocking: the reference's reading rests on K2.

RT RATCHET (probe, interpretation). The walker with type-2 correct: rewards have spread only while type-1 is wrong, so
theta is frozen while it is right and walks while it is wrong (a trial-and-error search that halts on success).
PREDICTION: REVISION_NOT_HISTORY_DEPENDENT; pre-competent >= 195; G_R5 holds; K1f and K1n >= 40 wins, 0 losses;
Holm K2 > .05; noswitch late-majority >= 195; theta never moves in 40 no-switch lives (max move <= 1e-6). RECORDED.
What it shows: NOT_HISTORY_DEPENDENT also covers a legitimate response to the switch that uses reward SPREAD and not
reward direction; the same label as the walker, separated from it only by the noswitch column. The s5 reading row
cannot distinguish the two; the result must print the noswitch count beside either label.

TN5 REF-TINY 1e-5 (semantic, instrument: "is eta -> 1e-9 really perturbation without update?"). The reference rescaled
by 1e-5 with its readout amplified by 1e5: decision for decision the reference on the same draws (theta/sigma = .4),
eta = 1e-10 <= ETA_NOISE, so noise_matched leaves eta unchanged and the noise arm IS the full arm. PREDICTION: the
full-arm and noise-arm rows are identical on all 200 seeds (every field but `arm`); K1n = 0:0:200; verdict
REVISION_NOT_SHOWN whatever the full arm does. SURVIVOR if so. Bearing: ETA_NOISE is an ABSOLUTE floor in a physics
whose update is in absolute units (tape.py:349: eta grad / (K sigma)); s11.4 states the consequence for "a subject
whose own eta <= 1e-9", and this case shows such a subject is the reference itself at another scale, i.e. the
comparator is not scale-invariant. A false NEGATIVE only. For this run: family S's smallest eta is .059 (SUBJECTS.json),
so no registered subject is affected; the result states the limitation and that it did not bite.

TN4 REF-TINY 1e-4 (probe). eta = 1e-8: the noise arm learns at 1/10 of the full arm's rate. PREDICTION: the noise arm
is revised in > 0 lives (it is a slow learner, not "perturbation without update"); the verdict stays REVISION_*.
RECORDED. Bearing: the graded form of TN5 (power loss on K1n for a small-eta subject), same limitation.

FS FAMILY-S-FROM-STRUCTURE (broken, interpretation). assay.family_s reads a non-empty declared plastic key set; it does
not ask whether the plastic node is LIVE (reachable from a sink: tape._live is the compiler's own liveness). From
SUBJECTS.json's node lists: searched_16310006's plastic CONST (node 1) reaches ACT (1 -> 3 -> 5 -> 6 -> 7 -> 9 -> 10);
searched_16310007's plastic LIN (node 12) is an input of NO node; searched_16310008's plastic BILIN (node 3) feeds
nodes 4, 5, 11, 12, 15, 17, none of which reaches ACT (node 8 <- 7 <- 1, 0) or WRITE (16 <- 7). PREDICTION:
family_s(SUBJECTS) = [006, 007, 008]; live_from_act = [True], [False], [False]; searched_dead is admitted. SURVIVOR if
so. Bearing: family S has ONE subject whose plastic parameter can affect its scored action; 007 and 008 are
parameter-free in effect (their declared plastic nodes are dead code), so (a) Holm over 6 tests spends power on 4 tests
that cannot win, (b) "search accessibility" must count them with the 5 parameter-free subjects (1 testable, 7 not),
(c) the result must say so. No lifetime of any searched subject was run to establish this. Not blocking: the rule is
conservative (power), and 007/008's labels will be REVISION_NOT_SHOWN by construction.

### Edits (run_edits_r2.py; red_rows_r2.jsonl)

Every edit of repair_v110/RED_EDITS.json re-applied by me (E1 E2 E3 E4 E6 verbatim from challenge/edits.json, R1-R6)
plus the E5 control, each in a fresh -B subprocess after a cache purge, with the hash guard recorded on the mutant and
the restore verified. PREDICTION: baseline GREEN (33 tests); E1 E2 E3 E4 E6 R1 R2 R3 R4 R5 R6 each RED on their named
test (the named test fails; the suite fails); E5 KILLED by test_assay (Endpoint / DeclaredMemory); hash guard fires on
every mutant; freeze check OK after every restore. Witnesses W1-W5 (witnesses_r2.py, six-arm schema; W4 re-designed
because under v1.1.0 jitter cannot distinguish E4: see witnesses_r2.W4) differ between original and mutant for
E1 E2 E3 E4 E6. PREDICTION: all five differ as their docstrings say.

## 5. Design calculation for the walker (abstract model; computed before the predictions)

A clipped Gaussian random walk theta_b (b = 0..11) from theta0 with step s per block; type-1 correct in block b iff
sign(theta_b) = law(b); pre-majority = majority of blocks 0..sw-1 positive; revised = pre-majority and majority of
blocks sw+3..11 negative; sw uniform in 4..8; 20,000 lives:

    theta0 .5  step .25   P(pre) .919  P(revised) .196  P(no-switch late +) .715
    theta0 .5  step .35   P(pre) .853  P(revised) .235  P(no-switch late +) .627

Chosen: theta0 .5, step ~.3 (eta .024, sigma .01, |grad| ~ 8). Expected at N = 200: ~175 pre-competent, ~42 revised,
~135 no-switch late-majority. The step: zr is standardised over 64 episodes (sum of squares 64), e are unit normals in
antithetic pairs, so grad = sum_k z_k e_k has standard deviation ~8 whatever the rewards are, as long as they are not
all equal; eta * 8 / (64 * .01) = .3.

Why no PURE walker keeps role 5: a stochastic type-2 needs a plastic parameter whose perturbation crosses the decision
threshold (band width sigma), whose gradient then has nonzero mean (it learns the type-2 law away to certainty, or at
the clip dips below and collapses); with eta and sigma shared by every parameter, a walker step >> sigma for theta is a
walker step >> sigma for that parameter too. Lanes and amplification do not change the band/range ratio
(sigma / sqrt(8) per summed lane). The walker therefore costs G_R5, and the attack lands on
REVISION_WITHOUT_RETAINED_COMPETENCE; the ratchet keeps G_R5 but IS switch-triggered.

Why no law-blind TIMER exists (T040 P2, restated for the v1.1.0 endpoint): the ES update is baseline-subtracted and
standardised (zero mean when the parameter does not affect reward), the perturbed value is unclipped, working state is
per episode, every gate has weight 1; a readout that flips at some parameter value has its maximal reward sensitivity
there, so a reward-driven drift stalls at the flip point before the switch and crosses only after it (clock_hybrid:
399/400 no-switch lives late-majority-correct, DEV_CHECK). The walker is the remaining class: drift that reads no law
at all, which the endpoint admits by variance and only K2 / noswitch expose.

## 6. Files

    subjects_r2.py      walker, ratchet, ref_tiny, searched_dead; R2 seed range; conflicts()
    cases_r2.py         S1 S2 S3 S4 FS GR5 B3 B1 S5 P3 B2 REF WK RT TN5 TN4 -> results_r2.jsonl
    witnesses_r2.py     W1-W5 (six-arm schema)
    run_edits_r2.py     the mutation re-run -> red_rows_r2.jsonl
    expected_r2.json    the answer key
    REPORT.md           written after the runs
