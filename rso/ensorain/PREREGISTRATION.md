# C-016 Ensorain native assay -- preregistration v1.1.0 (C-016-T041 amendment of v1.0.0, C-016-T030)

Author of v1.0.0: Argus[harry1-293acef8]. Author of v1.1.0: Argus[harry1-b2f16d20], claude-opus-5-5 (Q2), headless on
harry1, 2026-10-11, branch argus/c016-t041 from base a387bbb5a. Authority: operator Continuous Observatory directive
2026-10-11 (roles/Palamedes/prompts/2026-10-11_continuous_observatory/01_OPERATOR_DIRECTIVE_verbatim.md) s4, s9
(at most ONE bounded repair round), s10, s13; ops/campaigns/C-016/tasks/C-016-T041/TASK.json `problem`; the Q3
challenge rso/ensorain/challenge/REPORT.md (Pallas, C-016-T040). Written BEFORE any confirmatory lifetime and before
any endpoint of a searched subject was computed. **No confirmatory run happens in C-016-T041.** v1.0.0 is the blob
of this file at 93623a03a (`git show 93623a03a:rso/ensorain/PREREGISTRATION.md`).

## 0. Amendment record (v1.0.0 -> v1.1.0): VERSIONED, not wording-only (arms and controls change)

| # | Change | Why (REPORT.md) | Where |
|---|---|---|---|
| A1 | s1 and the s5 "licensed reading" column narrowed | s4.1-4.3: K1/K2 readings depended on the innate value; "lifetime-learned" not supported (B2, S5, P4); "keeps the competence" (B3) | s1, s5 |
| A2 | Primary endpoint = the WHOLE-LIFE `revised` indicator (pre-switch AND late-window majority-correct), used by K1 and K2 | s4.1: the late-window contrast against the subject's own frozen arm is a statement about the innate start | s4, analysis.py:revised |
| A3 | New arm `noise` (noise-matched comparator: perturbation on, eta -> 1e-9); K1 must hold against frozen AND noise (intersection-union) | s4.1 B1 (jitter passes K1 vs frozen by noise alone), s5.2 | s3, s5, assay.py:noise_matched, analysis.py:subject_stats |
| A4 | New descriptive arm `noswitch` (same draws, the law never flips) | s4.2 P2 (timers) | s3, s5.6 |
| A5 | Controls jitter (Q-d, must not be REVISION_*) and learns_pre (Q-e, must be REVISION_*) registered | s4.2, s5.3 | s3, s5 |
| A6 | G_R5 gets a competence bound (9 lives in 10), not the chance-1/2 k_pos | s4.3 B3 | s5.2, analysis.py:_competence |
| A7 | Family S declared from genome structure: the searched subjects with an active plastic key set (3); the 5 parameter-free ones are reported, not tested | s4.3, s5.5 | s5.5, assay.py:family_s |
| A8 | np.isfinite in the declared-memory bound | s4.2 P1 | assay.py:memory_check |
| A9 | Behavioural tests for E1 E2 E3 E4 E6 (+P1 and every A-change), each RED on its mutant | s4.4 | tests/test_repair_v110.py, repair_v110/red_rows.jsonl |
| A10 | Per-subject per-arm revised lives and late accuracies printed beside every verdict | s4.1, s5.2 | assay.py:print_verdicts |
| A11 | N and power recomputed for the new endpoint (N stays 400) | task item (6) | s7 |

Unchanged: world, K, seeds and their partition, N = 400, alpha = 1/20, the sign test, Holm, G_PRE (full arm, k_pos 217),
the Smuggler analogues, the newlife arm, the instrument fields, the confirmatory command, one process on harry1.

**Coordinator suggestion: ACCEPTED, extended.** The coordinator proposed the whole-life joint endpoint compared full vs
frozen and full vs noise-matched. Accepted because (i) no fixed-sign policy (+s or -s, with or without perturbation)
can hold both halves in expectation, so the contrast stops depending on where theta starts: on 400 development lives
the reference (theta0 +.2), innate_zero (0), innate_max (+1) and learns_pre (-.1) have the SAME full-arm count of
revised lives (255) and the same verdict (s8); (ii) against the frozen arm ALONE the joint endpoint still passes jitter
(19:0, p = 1/524288; s8), so the noise-matched arm is necessary, and against the noise-matched arm jitter ties 0:0 by
construction (its full and noise arms are the same computation); (iii) Pallas's alternative "K1 against the
noise-matched arm on the late window" fails learns_pre's purpose (noise late .581 vs full .645 on development; weak),
while the joint endpoint separates it 254:1. Extension (my choice, recorded): K2 uses the same endpoint, so both
contrasts read one per-life outcome; the v1.0.0 late-window accuracies stay in the output as description.

## 1. Question (narrowed in v1.1.0, A1)

Can a bounded persistent learner REVISE a plastic parameter at an unannounced law switch -- hold the pre-switch law and
then the post-switch law within one life -- where neither a non-learning (frozen) nor a noise-matched non-learning
version of the same genome does so, while keeping the unrelated competence in at least 9 lives in 10; and does the
revision depend on its own reward history?

Not claimed: that the pre-switch value was LEARNED in the life. The assay cannot tell an innate pre-switch value from
a learned one: innate_max (theta0 = +1, nothing learnable before the switch) and learns_pre (theta0 = -0.1, learns the
law first) both read REVISION_HISTORY_DEPENDENT (s8). "Revises a genome-initialised or lifetime-learned plastic
parameter" is the scope (REPORT s4.3 B2, S5).

Not asked, and not claimable from this assay: retention of information ACROSS a drift boundary. Family C does not
demand it: the never-switching type-2 law is solved by every memoryless policy (role 5 = 1.00 for N1-N4 in
COMPATIBILITY.md s4 and in DEV_QUALIFICATION.json `ladder`), and nothing the world asks after the switch needs a
carried observation. **Finding, recorded as such: no Ensorain world tested so far (WTP-05 A/B/N/C admission, E1, D1)
demands retention across a drift boundary.** If a later Ensorain world passes a demand gate on retention, a separate
preregistration is needed.

## 2. World and native semantics (pinned, read-only)

- Code: ensorain/ at 7b1d549c8 (last change to ensorain/ and roles/Ensorain/). Re-pinned at the v1.1.0 freeze against
  origin/main a387bbb5a: `git log 7b1d549c8..a387bbb5a -- ensorain/ roles/Ensorain/` is empty. The eight ensorain/wtp5
  sources the assay imports, plus ensorain/wtp3/collider.py (the N4 ladder), are in FROZEN.json; the confirmatory
  runner refuses if any byte differs.
- World `C-R2-desert` (ensorain/wtp5/worlds.py:239 FamilyC, :275 make): L = 12 blocks per life, T = 2, the switch
  block sw drawn uniformly in [4, 8] by `new_life` (:245-246), law(b) = -1 for b >= sw else +1 (:248-252). Role 1 =
  the switching law (type-1 gates, tag +1, payload P0 = s, target s * law); role 5 = the never-switching law (tag -1,
  payload P1, target s). K = 64 episodes per block (as certify.py:72 and T020).
- One life = `ensorain.wtp5.tape.lifetime(g, world, rng, plasticity, K=64, history_shuffle)` (tape.py:298) with
  rng = numpy default_rng(seed), after `world.new_life(rng)`, exactly as certify.py:69-72 and T020. Working state is
  zeroed at every block start (tape.py:171); plastic parameters move only between blocks (tape.py:342-349) and are
  clipped to [-1, 1] (tape.py:49). A life starts from a deep copy of the genome (tape.py:304).
- `ws_reset` is vacuous for family C (COMPATIBILITY.md s5) and is NOT used. No mid-life resume exists natively
  (COMPATIBILITY.md s6); the restart control is a NEW LIFE from learned parameters and is named so.
- Host and version set: all arms of a run execute in ONE process on ONE host (harry1; Python 3.12.10, numpy 2.4.3,
  recorded in FROZEN.json `environment`); the runner refuses another Python/numpy version. Ensorain's results are
  bitwise host-bound (worlds header; COMPATIBILITY.md s7): no number here is compared to a ubu006 row.

## 3. Subjects, competitors and controls (defined before outcomes; rso/ensorain/subjects.py, assay.py:controls)

| Name | Definition | Role in the assay |
|---|---|---|
| reference | planted `switch_C(eta=1, sigma=.5)` (planted.py:113): act = theta * s on type 1, q on type 2, theta plastic (8 floats, 1 effective), theta0 = +0.2 | family P: the known-answer lawful reference (capacity, causal dependence) |
| searched_16310001..008 | the final elite `pop[0]` of eight NEW searches, ensorain/wtp5/search.py unchanged, arm L, C-R2-desert, 16,000 evaluations each (Ensorain's SCREEN budget), seeds 16_310_001..008, certify seeds 16_401_000 + 1000 i. Genomes and hashes in SUBJECTS.json. Selection rule fixed before the searches ran; no other selection | family S (the 3 with an active plastic key set, s5.5): search accessibility; the other 5 reported, not tested |
| smuggler | the reference with theta = -0.2 NON-plastic, eta = sigma = 0: reads the post-switch sign from a constant | forbidden channel; must be REFUSED (Q-b) |
| smuggler_decorative | declares a plastic parameter and eta, sigma as the reference, but acts on a NON-plastic -0.2 constant; the plastic node reaches the action only through a zero weight | forbidden channel dressed as a learner; must be REFUSED (Q-b) |
| memoryless_plus | the reference with theta = +0.2 non-plastic (= the frozen reference) | must NOT be read as a revision (Q-c) |
| constant_plus / constant_minus | act +1 / -1 at every gate | chance policies; must be REFUSED (Q-b) |
| **jitter** (v1.1.0) | challenge/subjects_c.py:40: the reference graph, theta0 = +0.1, eta = 1e-9, sigma = .5: a fixed PRE-switch prior with perturbation noise and no learning | the noise class; must NOT be REVISION_* (Q-d) |
| **learns_pre** (v1.1.0) | challenge/subjects_c.py:54: the reference graph, theta0 = -0.1, eta = 1, sigma = .5: starts on the post-switch side, learns the pre-switch law in-life, then revises | the lifetime-learned positive; MUST be REVISION_* (Q-e) |

Arms, applied to every subject on every seed (analysis.py:ARMS; assay.py:life):

| Arm | Native call | Distinction it carries (directive s4) |
|---|---|---|
| full | plasticity on | the subject as it is |
| frozen | plasticity off (eta ignored; parameters never move) | the non-learning competitor: WORLD DEMAND (with noise) |
| **noise** (v1.1.0) | plasticity on with eta lowered to 1e-9 (assay.py:noise_matched; never raised). tape.py:305 keeps the perturbation on while eta > 0; the update moves a parameter by ~1e-8 over a life. The rng draws are those of the full arm on the same seed, so the pair differs only in the update | the noise-matched non-learning competitor: WORLD DEMAND without removing the perturbation (REPORT s4.1) |
| shuffle | plasticity on, `history_shuffle=True` (tape.py:344: block rewards permuted across episodes before the update) | CAUSAL DEPENDENCE on the subject's own reward history |
| newlife | a full life on the seed, then a NEW life on the same seed starting from `out["learned"]` | the restart control Ensorain actually supports; descriptive (s5.6) |
| **noswitch** (v1.1.0) | plasticity on, the same draws, the switch block overridden to L after `new_life` (worlds.py:248-252 then never flips the law); windows are those of the drawn sw | descriptive: does the subject flip WITHOUT a switch (a timer)? (REPORT s4.2 P2) |

The memoryless / short-window / register / menu competitors (N1-N4, nulls.py:120). At a type-1 gate a genome sees
only (s, tag = +1, fG = 1, bias) (worlds.py:263-266: the gate is written at t = 0 over the corridor noise); T = 2 with the gate at t = 0, so a window or register holds
nothing earlier in the episode. A deterministic policy without lifetime plasticity therefore maps a type-1 gate to
one of four answers: +s, -s, +1 or -1. These are memoryless_plus, smuggler, constant_plus and constant_minus, and all
four run as controls. N1-N4 are fitted in hindsight on lives mixing both laws, so their scalar role-1 accuracy
depends on that mixture (.542 on T020's ladder seed, N4 .608 on ours). The ladder is reported for the record on
development seed 16_320_001. It is not a decision input. The noise class (a fixed sign plus perturbation) is covered
by the noise arm and by jitter (Q-d), not by the four-policy argument (REPORT s4.1).

Stateful reference: the plastic reference IS the stateful reference (its state is theta). N6 (unbounded batch) is not
computed for family C (nulls.py:147) and no unbounded-memory reference exists natively.

## 4. Endpoint (per lifetime; integers only; assay.py:_counts, analysis.py:revised)

Per (subject, arm, seed): sw; c_pre / n_pre = correct / total role-1 gates in blocks b < sw; c_early / n_early for
sw <= b < sw + 3; c_late / n_late for b >= sw + 3; c5 / n5 role 5 over the life and c5_post / n5_post role 5 in
b >= sw. n_late >= 1 block always (sw <= 8, L = 12). Unit of analysis = the lifetime; episodes inside a life share
the plastic parameter and are never treated as independent.

**Primary endpoint (v1.1.0, A2): `revised` = (2 c_pre > n_pre) AND (2 c_late > n_late)**, a binary per-life outcome.
A policy that acts a fixed sign (+s or -s) with per-gate correctness p before the switch has 1 - p after it, so in
expectation it cannot be majority-correct on both sides; perturbation noise does not change that. The late-window
accuracy c_late / n_late (v1.0.0's endpoint) is reported per arm as description. The certifier's SWITCH_TRACKED
fraction is NOT used (COMPATIBILITY.md s4).

Each row also carries two instrument fields, computed for every life:
- `recompute_ok`: the integer counts, rebuilt from the observed episodes and actions, reproduce the native float
  accuracies of every block and the role totals tape.lifetime itself reports (tape.py:329-341, 350-351).
- `memory_ok`, the EXTERNAL DECLARED-MEMORY CHECK (assay.py:memory_check). (a) After the life, the genome differs
  from the input only at the declared plastic keys (tape.plastic_keys, when plasticity is on and eta, sigma > 0,
  mirroring tape.py:305). (b) Those keys keep their shape, are FINITE (v1.1.0, A8) and lie in [-1, 1]. (c) In a
  non-plastic arm nothing changes at all. (d) The working state is exactly zero at step 0 of every block, observed
  through run_block's native `record`. `n_carried` = the number of floats allowed across a block boundary.

Rows are canonical JSON (registry receipt-canonical: no floats); the run records their sha256.

## 5. Decision rule (analysis.py; alpha = 1/20; all p-values exact)

Per subject, over its N lifetimes:

1. **G_PRE, the admissibility gate (refuses fixed priors).** A life is pre-competent iff 2 c_pre > n_pre in the
   FULL arm (tests/test_repair_v110.py Gates.test_gpre_counts_the_full_arm). G_PRE holds iff the count of
   pre-competent lives >= k_pos = 217 of N = 400, the integer threshold of the exact one-sided binomial test against
   1/2 at alpha (rso/witness/ruler.py:thresholds). It separates the Smuggler class.
2. **G_R5, unrelated competence kept (v1.1.0, A6).** A life keeps it iff 10 c5_post >= 9 n5_post. G_R5 holds iff that
   count is >= k_pos(N, alpha, bound 9/10) = **371 of 400**: the share of lives keeping the competence is
   significantly above 9 in 10. (At N = 40 every life must keep it; at N < 29 no count passes.)
3. **K1, world demand (v1.1.0, A3).** Two paired sign tests on `revised`, ties dropped: full vs frozen (K1f) and full
   vs noise (K1n). A win is a life revised in the full arm and not in the control. K1's p = max(p_K1f, p_K1n), the
   intersection-union test: K1 holds only if BOTH contrasts hold.
4. **K2, causal dependence.** full vs shuffle on `revised`, the same test.
5. **Multiplicity.** Holm (rso/reach/stats.py:holm) over K1 and K2 within a family. Family P = {reference} (2 tests).
   **Family S = assay.family_s(SUBJECTS): the searched subjects whose declared plastic key set is non-empty, read
   from genome structure before the run = searched_16310006, 16310007, 16310008 (6 tests).** The other 5 searched
   subjects (no plastic parameter: their full, frozen, noise and shuffle arms are the same computation) are reported
   with every statistic and the verdict NOT_TESTED_PARAMETER_FREE. Each instrument control is its own family.
6. **Descriptive, printed beside every verdict (A10):** per arm, revised lives and late-window accuracy; newlife
   pre-switch accuracy; noswitch lives that are late-window majority-correct under the unchanged law.

Verdict per subject (analysis.py:verdict, in this order):

| Condition | Verdict | Licensed reading (v1.1.0, narrowed) |
|---|---|---|
| any memory_ok or recompute_ok false | INSTRUMENT_FAULT | none |
| parameter-free searched subject | NOT_TESTED_PARAMETER_FREE | none (reported, not tested) |
| not G_PRE | REFUSED_FIXED_PRIOR | no revision claim (a fixed prior or chance) |
| K1 (Holm) and not G_R5 | REVISION_WITHOUT_RETAINED_COMPETENCE | revises within a life, beyond its frozen and noise-matched versions; the unrelated competence is not shown kept in 9 lives in 10 |
| K1 and K2 (Holm) | REVISION_HISTORY_DEPENDENT | revises within a life, beyond its frozen and noise-matched versions, keeping role 5 in 9 lives in 10; and its revised lives exceed those of a history-shuffled configuration STARTED AT THE SAME INNATE VALUE (K2's sensitivity is a property of the pair (learner, innate start): REPORT s4.1) |
| K1 only | REVISION_NOT_HISTORY_DEPENDENT | revises as above; dependence on own reward history not shown (not a demonstrated independence) |
| otherwise | REVISION_NOT_SHOWN | no revision shown. This is NOT a demonstrated absence |

No verdict says the pre-switch value was learned in the life (s1). A searched subject's label is read only together
with its per-arm numbers (s5.6).

**Qualification of the confirmatory run (analysis.py:qualification).** The run is DETECTION_UNQUALIFIED as a whole,
and no subject verdict is read, if any of these fails on the confirmatory seeds: (Q-a) every row memory_ok and
recompute_ok; (Q-b) smuggler, smuggler_decorative, constant_plus and constant_minus are all REFUSED_FIXED_PRIOR; (Q-c)
memoryless_plus is not a REVISION_* verdict; **(Q-d) jitter is not a REVISION_* verdict; (Q-e) learns_pre IS a
REVISION_* verdict** (REVISION_* = HISTORY_DEPENDENT, NOT_HISTORY_DEPENDENT or WITHOUT_RETAINED_COMPETENCE). The
reference is the known-answer positive, and its verdict is the family-P result. If the reference is not
REVISION_HISTORY_DEPENDENT, that is reported as the result. Q-a..Q-e held on development seeds (s8).

**Search accessibility (descriptive).** The number of family-S subjects per verdict, plus the count reported
NOT_TESTED_PARAMETER_FREE, scoped to arm L, C-R2-desert, 16,000 evaluations, these 8 seeds. Not a rate claim beyond
that budget. clock_hybrid (challenge/subjects_c.py:67, a learner poised near its flip point) revises in 400 of 400
development lives against the reference's 255 (s8): a searched elite that out-revises the reference shows the world
rewards such poise, nothing beyond that (REPORT s4.3).

**s5.6 newlife and noswitch (descriptive).** Registered directional prediction (v1.0.0, kept): the pooled pre-switch
accuracy of the reference's newlife arm is lower than its full arm's (the learned theta is negative after a life).
Not a decision input and not a resume. noswitch: a subject that is late-window majority-correct in few no-switch
lives flips without a switch (a timer); reported, not tested.

## 6. Seeds (subjects.py; `seed_conflicts()` returns [] and is a test)

| Range | Use |
|---|---|
| 16_300_001..16_300_999 | development lives (DEV_QUALIFICATION.json used 001..400; v1.1.0 DEV_CHECK.json used 001..400; tests/test_repair_v110.py uses 401..440) |
| 16_310_001..16_310_008 | subject searches; certify 16_401_000 + 1000 i (+ generation < 1000) |
| 16_310_901..16_311_999 | the 2,000-evaluation timing search and its certify seeds (disclosed; produced no subject) |
| 16_320_001 | Ensorain null ladder, development |
| 16_350_001..16_359_999 | the C-016-T040 challenge (Pallas; challenge/subjects_c.py CH_RANGE) |
| **16_330_001..16_330_400** | **confirmatory lives, N = 400; never executed in C-016-T030 or C-016-T041** |

These are disjoint from every WTP-05 registered seed and from the ranges those seeds generate. That includes a
pitfall found here: search.py:82 derives certify seeds as 7_000_000 + run seed, so Ensorain's PROBE seed 9_500_001
certifies at 16_500_001 + generation, and its assay seeds 9_700_000 and 9_710_000 certify at 16_700_000+ and
16_710_000+, all inside the 16_xxx_xxx space. Our seeds are also disjoint from T020's 16_020_xxx and 16_030_001.

## 7. N and power (recomputed for the v1.1.0 endpoint; repair_v110/DEV_CHECK.json `power`)

Effect model (analysis.py:power_revised): a life is revised with probability p_full in the full arm and p_ctrl in the
control, independently given the seed; discordant pairs D ~ Bin(N, w + l) with w = p_full (1 - p_ctrl), l = p_ctrl
(1 - p_full); wins | D ~ Bin(D, w / (w + l)); power = P(wins >= the exact critical count at D), summed over D, at the
Holm worst case (alpha/2 for P, alpha/6 for family S of 3 subjects). The pairs within a seed share sw and, for the
noise arm, every random draw; independence given the seed is an approximation, and the observed development
contrasts (s8) are the check on it.

Development rates of the reference (400 lives): revised full 255, frozen 0, noise 2, shuffle 79 (p = .6375, 0, .005,
.1975). Power at N = 400 against each control: 1.000 (P and S). Sensitivity (P at N = 200 / P at N = 400 / S at 400):

| p_full | p_ctrl | P N=200 | P N=400 | S N=400 |
|---|---|---|---|---|
| .60 | .45 | .829 | .987 | .964 |
| .60 | .40 | .975 | 1.000 | .999 |
| .40 | .25 | .874 | .994 | .982 |
| .30 | .15 | .940 | .999 | .996 |

Observed development contrasts (s8): reference K2 204:28 (v1.0.0 late-window K2 was 249:149). **N = 400 lifetimes per
subject and arm, unchanged.** Family S power is indicative: the searched subjects' rates are unknown.

## 8. Development evidence (repair_v110/DEV_CHECK.json; seeds 16_300_001..400; N = 400; rows sha256 b54c751b...)

The verdicts obtained with the v1.1.0 rule on development seeds, with Pallas's challenge subjects (imported unchanged
from challenge/subjects_c.py; innate_zero = ref_like(0.0, 1.0, 0.5), P3). Revised lives per arm
full / frozen / noise / shuffle / newlife / noswitch-late-majority:

| Subject | theta0 | Verdict | K1f W:L:T | K1n W:L:T | K2 W:L:T | Revised lives (f/fz/n/sh/nl) | noswitch |
|---|---|---|---|---|---|---|---|
| reference | +.2 | REVISION_HISTORY_DEPENDENT | 255:0:145 | 255:2:143 | 204:28:168 | 255/0/2/79/59 | 400 |
| innate_zero | 0 | REVISION_HISTORY_DEPENDENT | 191:34:175 | 197:37:166 | 222:24:154 | 255/98/95/57/59 | 400 |
| innate_max | +1 | REVISION_HISTORY_DEPENDENT | 255:0:145 | 255:0:145 | 230:22:148 | 255/0/0/47/59 | 400 |
| learns_pre (Q-e) | -.1 | REVISION_HISTORY_DEPENDENT | 255:0:145 | 254:1:145 | 231:17:152 | 255/0/2/41/59 | 400 |
| jitter (Q-d) | +.1, eta 1e-9 | REVISION_NOT_SHOWN | 19:0:381 | 0:0:400 | 18:15:367 | 19/0/19/16/19 | 372 |
| clock_hybrid | phi -1 | REVISION_HISTORY_DEPENDENT | 400:0:0 | 400:0:0 | 389:0:11 | 400/0/0/11/1 | 399 |
| smuggler, smuggler_decorative | | REFUSED_FIXED_PRIOR (pre-competent 0) | ties | ties | ties | 0 throughout | 0 |
| constant_plus / _minus | | REFUSED_FIXED_PRIOR (199 / 192) | ties | ties | ties | 98 / 83 in every arm | |
| memoryless_plus (Q-c) | | REVISION_NOT_SHOWN | ties | ties | ties | 0 throughout | 400 |

Q-a..Q-e all hold; qualified. What the table shows against REPORT s4.1: the four reference-graph learners differ only
in theta0 and now share one verdict and one full-arm count (255); the v1.0.0 rule gave them three verdicts. jitter's
K1 against the frozen arm ALONE is 19:0 (p = 1/524288): the noise arm is what refuses it. Late-window accuracy
full / frozen / noise / shuffle for the reference .645 / 0 / .348 / .424 (full table: DEV_CHECK.json `verdicts`).
G_R5: every reference-graph learner 400/400; clock_hybrid 376 (>= 371). The 8 searched subjects received
`assay.preflight` only (2 development seeds; memory_ok and recompute_ok True; rows discarded unread); no searched
subject's endpoint has been computed in any form. memory_ok and recompute_ok held on all 26,400 development rows.

v1.0.0's development evidence (DEV_QUALIFICATION.json, 9,600 rows, sha256 1d5ccf28...) stays as the record of the
v1.0.0 rule; it lacks the noise and noswitch arms and is not re-read under v1.1.0.

## 9. Resources (directive s13)

- Expected: 16 subjects (8 controls, 8 searched) x 400 seeds x 7 lives (newlife = 2) = 44,800 lives, about 8.3 ms
  each on harry1 (DEV_CHECK: 30,800 lives in 255 s), so about 370 CPU-seconds; a row file of about 11 MB.
- Parallelism: ONE process (all arms on one host and version set, by design). No ubu006, no Fabric, no paid compute.
- Stopping: none data-dependent. The run is complete at 44,800 lives. An external abort (crash, timeout) discards
  the partial output and reruns from the start: the run is deterministic, and the rerun must reproduce rows_sha256 of
  any completed earlier attempt if one exists.
- Reproducibility: rows_sha256 is recorded. A second run on harry1 with the frozen versions must give byte-identical
  rows. Another host or version set needs its own development baseline and is not comparable digit for digit.
- Checkpointing: not necessary (minutes). A shell timeout below 600 s is too tight: run it with >= 900 s.

## 10. How the confirmatory run is executed (a later packet, after the T042 re-check)

    python -m rso.ensorain.freeze check                                   # must print OK
    python -m rso.ensorain.assay confirm rso/ensorain/runs/CONFIRM.json --n 400 \
        --subjects rso/ensorain/SUBJECTS.json --cleared-by <re-check/integration ref>

`confirm` refuses on any FROZEN.json mismatch, another Python/numpy version, or a missing --subjects/--cleared-by.
It prints every verdict with its per-arm numbers and the qualification line. Read the result under s5 only. Commit
the row file with the result.

## 11. Known limitations (declared before outcomes)

1. The sign test ignores magnitudes. It is exact and float-free, and powered at N = 400.
2. Pairing by seed matches sw. The rng streams of frozen and shuffle diverge from full after block 0 (frozen draws no
   perturbations; shuffle draws a permutation), so those pairs share the switch block and not their episodes. The
   noise pair shares every draw.
3. The searched subjects' revised-life rates are unknown. Family S power is indicative.
4. The noise arm is eta = 1e-9, not eta = 0 (tape.py:305 turns the perturbation off at eta = 0). A parameter moves
   ~1e-8 over a life; jitter (eta = 1e-9) is its own noise arm exactly. A subject whose OWN eta is <= 1e-9 is its
   own noise arm and cannot pass K1.
5. **Innate vs learned pre-switch value is not distinguished (s1).** The verdict reads the pair of halves of a life,
   not where the pre-switch value came from.
6. **K2 is relative to the innate start.** The shuffle arm is a history-scrambled walk from the subject's own theta0;
   its revised-life rate depends on that start (development: 79, 57, 47, 41 of 400 for theta0 = +.2, 0, +1, -.1).
   K2 holds for all four, but "depends on its own reward history" means "beyond a scrambled-history walk from the
   same start".
7. The intersection-union K1 is conservative (size <= alpha without correction; power is the smaller of two).
8. G_R5 needs N >= 29 to be passable at all; at N = 40 it demands every life. Development tests use N = 40 or 400.
9. The `revised` majority is per half: a life with few late gates (sw = 8: one late block, ~32 gates) reads its late
   half on fewer gates. Pairing by seed equalises this within a pair.
10. Smuggler analogues are constructed (no TAPE-native Smuggler exists; the E0/E1 Smuggler at
    ensorain/e0/memories.py:325 is a pattern, not reusable code). A forbidden channel outside the genome, for example
    the block index, is not reachable by a TAPE genome (observations carry no global address: worlds.py header). The
    noswitch arm makes timer behaviour visible for any subject; it is descriptive.
11. The searched subjects were produced on harry1 with world K = 32 (search.py evaluates at world.K). The assay runs
    at K = 64. This is the same convention certify.py uses.
12. One repair round only (directive s9). A defect found after this freeze is narrowed and recorded as a limitation,
    not repaired.
