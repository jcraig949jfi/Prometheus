# C-016 Ensorain native assay -- preregistration v1.0.0 (C-016-T030)

Author: Argus[harry1-293acef8], claude-opus-5-5 (Q2), headless on harry1, 2026-10-11. Branch argus/c016-t030 from
base 8a5a3b572. Authority: operator Continuous Observatory directive 2026-10-11
(roles/Palamedes/prompts/2026-10-11_continuous_observatory/01_OPERATOR_DIRECTIVE_verbatim.md) s4, s9, s10, s13; the
coordinator's decision in ops/campaigns/C-016/tasks/C-016-T030/TASK.json `problem`; rso/ensorain/COMPATIBILITY.md
(Cadmus, C-016-T020). Written and frozen BEFORE any confirmatory lifetime and before any endpoint of a searched
subject was computed. **No confirmatory run happens in C-016-T030.** A Q3 challenge (Pallas) of the frozen surface
comes first (directive s9); the run is a later packet.

## 1. Question (reworded on evidence; directive s4 "candidate, not conclusion")

Can a bounded persistent learner REVISE a lifetime-learned parameter at an unannounced law switch while keeping the
unrelated competence, and does the revision depend on its own reward history?

Not asked, and not claimable from this assay: retention of information ACROSS a drift boundary. Family C does not
demand it: the never-switching type-2 law is solved by every memoryless policy (role 5 = 1.00 for N1-N4 in
COMPATIBILITY.md s4 and in DEV_QUALIFICATION.json `ladder`), and nothing the world asks after the switch needs a
carried observation. **Finding, recorded as such: no Ensorain world tested so far (WTP-05 A/B/N/C admission, E1, D1)
demands retention across a drift boundary.** If a later Ensorain world passes a demand gate on retention, a separate
preregistration is needed.

## 2. World and native semantics (pinned, read-only)

- Code: ensorain/ at 7b1d549c8 (last change to ensorain/ and roles/Ensorain/). Re-pinned at freeze time against
  origin/main 905702fe3: `git log 7b1d549c8..origin/main -- ensorain/ roles/Ensorain/` is empty and ensorain/wtp5/ is
  byte-identical. The eight ensorain/wtp5 sources the assay imports, plus ensorain/wtp3/collider.py (the N4 ladder),
  are in FROZEN.json; the confirmatory runner refuses if any byte differs.
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

## 3. Subjects, competitors and controls (defined before outcomes; rso/ensorain/subjects.py)

| Name | Definition | Role in the assay |
|---|---|---|
| reference | planted `switch_C(eta=1, sigma=.5)` (planted.py:113): act = theta * s on type 1, q on type 2, theta plastic (8 floats, 1 effective) | family P: the known-answer lawful reference (capacity, causal dependence) |
| searched_16310001..008 | the final elite `pop[0]` of eight NEW searches, ensorain/wtp5/search.py unchanged, arm L, C-R2-desert, 16,000 evaluations each (Ensorain's SCREEN budget), seeds 16_310_001..008, certify seeds 16_401_000 + 1000 i. Genomes and hashes in SUBJECTS.json. Selection rule fixed before the searches ran; no other selection | family S: search accessibility |
| smuggler | the reference with theta = -0.2 NON-plastic, eta = sigma = 0: reads the post-switch sign from a constant | forbidden channel; must be REFUSED |
| smuggler_decorative | declares a plastic parameter and eta, sigma as the reference, but acts on a NON-plastic -0.2 constant; the plastic node reaches the action only through a zero weight | forbidden channel dressed as a learner; must be REFUSED |
| memoryless_plus | the reference with theta = +0.2 non-plastic (= the frozen reference) | must NOT be read as a revision |
| constant_plus / constant_minus | act +1 / -1 at every gate | chance policies; must be REFUSED |

Arms, applied to every subject on every seed (assay.py:ARMS):

| Arm | Native call | Distinction it carries (directive s4) |
|---|---|---|
| full | plasticity on | the subject as it is |
| frozen | plasticity off (eta ignored; parameters never move) | the simpler competitor: WORLD DEMAND |
| shuffle | plasticity on, `history_shuffle=True` (tape.py:344: block rewards permuted across episodes before the update) | CAUSAL DEPENDENCE on the subject's own reward history |
| newlife | a full life on the seed, then a NEW life on the same seed starting from `out["learned"]` | the restart control Ensorain actually supports; descriptive (s5.5) |

The memoryless / short-window / register / menu competitors (N1-N4, nulls.py:120). At a type-1 gate a genome sees
only (s, tag = +1, fG = 1, bias) (worlds.py:263-266: the gate is written at t = 0 over the corridor noise); T = 2 with the gate at t = 0, so a window or register holds
nothing earlier in the episode. A deterministic policy without lifetime plasticity therefore maps a type-1 gate to
one of four answers: +s, -s, +1 or -1. These are memoryless_plus, smuggler, constant_plus and constant_minus, and all
four run as controls. N1-N4 are fitted in hindsight on lives mixing both laws, so their scalar role-1 accuracy
depends on that mixture (.542 on T020's ladder seed, N4 .608 on ours). The ladder is reported for the record on
development seed 16_320_001. It is not a decision input. Within the confirmatory design the best admissible
memoryless policy is memoryless_plus = the frozen arm, so contrast K1 covers it.

Stateful reference: the plastic reference IS the stateful reference (its state is theta). N6 (unbounded batch) is not
computed for family C (nulls.py:147) and no unbounded-memory reference exists natively.

## 4. Endpoint (per lifetime; integers only; assay.py:_counts)

Per (subject, arm, seed): sw; c_pre / n_pre = correct / total role-1 gates in blocks b < sw; c_early / n_early for
sw <= b < sw + 3; **c_late / n_late for b >= sw + 3 (the coordinator's primary endpoint)**; c5 / n5 role 5 over the
life and c5_post / n5_post role 5 in b >= sw. n_late >= 1 block always (sw <= 8, L = 12). Unit of analysis = the
lifetime; episodes inside a life share the plastic parameter and are never treated as independent. The certifier's
SWITCH_TRACKED fraction is NOT used: it does not separate the reference from the shuffle control at n = 40
(COMPATIBILITY.md s4).

Each row also carries two instrument fields, computed for every life:
- `recompute_ok`: the integer counts, rebuilt from the observed episodes and actions, reproduce the native float
  accuracies of every block and the role totals tape.lifetime itself reports (tape.py:329-341, 350-351).
- `memory_ok`, the EXTERNAL DECLARED-MEMORY CHECK (assay.py:memory_check). (a) After the life, the genome differs
  from the input only at the declared plastic keys (tape.plastic_keys, when plasticity is on and eta, sigma > 0,
  mirroring tape.py:305). (b) Those keys keep their shape and lie in [-1, 1]. (c) In a non-plastic arm nothing
  changes at all. (d) The working state is exactly zero at step 0 of every block, observed through run_block's
  native `record`. `n_carried` = the number of floats allowed across a block boundary.
  The check fires on a leak at a non-plastic field, on working state carried into a block, on any parameter drift in
  a frozen life, and on a plastic value outside the bound (tests/test_assay.py DeclaredMemory).

Rows are canonical JSON (registry receipt-canonical: no floats); the run records their sha256.

## 5. Decision rule (analysis.py; alpha = 1/20; all p-values exact)

Per subject, over its N lifetimes:

1. **G_PRE, the admissibility gate (refuses fixed priors).** A life is pre-competent iff 2 c_pre > n_pre in the
   full arm. G_PRE holds iff the count of pre-competent lives >= k_pos = 217 of N = 400, the integer threshold of
   the exact one-sided binomial test against 1/2 at alpha (rso/witness/ruler.py:thresholds). It separates the
   Smuggler class: a policy that knows the post-switch sign scores perfectly on the endpoint window and is never
   pre-competent.
2. **G_R5, unrelated competence kept.** A life keeps it iff 10 c5_post >= 9 n5_post. G_R5 holds iff that count is
   >= 217 of 400 (the same threshold).
3. **K1, world demand.** full vs frozen, paired by seed. Per pair, the sign of c_late/n_late (full) minus (frozen),
   compared by integer cross-multiplication. Exact one-sided sign test, ties dropped (analysis.py:sign_p, the
   ruler's exact binomial tail).
4. **K2, causal dependence.** full vs shuffle, the same test.
5. **Multiplicity.** Holm (rso/reach/stats.py:holm) over K1 and K2 within a family. Family P = {reference} (2
   tests). Family S = the 8 searched subjects (16 tests). Each instrument control is its own family.

Verdict per subject (analysis.py:verdict, in this order):

| Condition | Verdict | Licensed reading |
|---|---|---|
| any memory_ok or recompute_ok false | INSTRUMENT_FAULT | none |
| not G_PRE | REFUSED_FIXED_PRIOR | no revision claim (a fixed prior or chance) |
| K1 (Holm) and not G_R5 | REVISION_WITHOUT_RETAINED_COMPETENCE | revised, unrelated competence not kept |
| K1 and K2 (Holm) | REVISION_HISTORY_DEPENDENT | revises, and the revision depends on its own reward history |
| K1 only | REVISION_NOT_HISTORY_DEPENDENT | revises; dependence on own history not shown |
| otherwise | REVISION_NOT_SHOWN | no revision shown. This is NOT a demonstrated absence |

**Qualification of the confirmatory run.** The run is DETECTION_UNQUALIFIED as a whole, and no subject verdict is
read, if any of these fails on the confirmatory seeds: (Q-a) every row memory_ok and recompute_ok; (Q-b) smuggler,
smuggler_decorative, constant_plus and constant_minus are all REFUSED_FIXED_PRIOR; (Q-c) memoryless_plus is not a
REVISION_* verdict. The reference is the known-answer positive, and its verdict is the family-P result: capacity
(K1) and causal dependence (K2). If the reference is not REVISION_HISTORY_DEPENDENT, that is reported as the result.
The positive was detected on development seeds (s8).

**Search accessibility (descriptive).** The number of searched subjects per verdict, scoped to arm L, C-R2-desert,
16,000 evaluations, these 8 seeds. Not a rate claim beyond that budget.

**s5.5 newlife (descriptive, directional prediction registered).** The pooled pre-switch accuracy of the reference's
newlife arm is lower than its full arm's. The learned theta is negative after a life, so a new life starting from it
begins on the wrong sign. This shows the plastic parameter is the carried state. It is not a decision input and not
a resume.

## 6. Seeds (subjects.py; `seed_conflicts()` returns [] and is a test)

| Range | Use |
|---|---|
| 16_300_001..16_300_999 | development lives (DEV_QUALIFICATION.json used 16_300_001..400) |
| 16_310_001..16_310_008 | subject searches; certify 16_401_000 + 1000 i (+ generation < 1000) |
| 16_310_901..16_311_999 | the 2,000-evaluation timing search and its certify seeds (disclosed; produced no subject) |
| 16_320_001 | Ensorain null ladder, development |
| **16_330_001..16_330_400** | **confirmatory lives, N = 400; never executed in C-016-T030** |

These are disjoint from every WTP-05 registered seed and from the ranges those seeds generate. That includes a
pitfall found here: search.py:82 derives certify seeds as 7_000_000 + run seed, so Ensorain's PROBE seed 9_500_001
certifies at 16_500_001 + generation, and its assay seeds 9_700_000 and 9_710_000 certify at 16_700_000+ and
16_710_000+, all inside the 16_xxx_xxx space. Our seeds are also disjoint from T020's 16_020_xxx and 16_030_001.

## 7. N and power (computed before freezing; lifetime-level variance from development lives)

rso/ensorain/rerun_c_demand_result.json holds only arm MEANS, not lifetime-level variance. The variance was therefore
measured on 400 development lives of the reference (DEV_QUALIFICATION.json): late accuracy per life has mean .591 and
s.d. .333 (full arm), so the endpoint is broad and bimodal. Effect model (analysis.py:q_shift): the control's late
accuracy is the reference's lowered by d. q = P(reference beats control) is computed exactly over all pairs of
independent development lives with the same sw, with no clipping. Exact power of the one-sided sign test at the Holm
worst case (analysis.py:power):

| d | q | power N=200 | power N=400 | family S at alpha/16, N=400 |
|---|---|---|---|---|
| .05 | .570 | .475 | .778 | .523 |
| .10 | .624 | .933 | **.999** | .988 |

Sensitivity, at the true q: q = .58 gives .878 at N = 400 (S: .677). q = .60 gives .976 (S: .899). The observed
development shuffle contrast was 249 wins : 149 losses (q = .626). **N = 400 lifetimes per subject and arm.** Critical
win counts: 221 of 400 untied pairs (P), 228 (S, worst case).

## 8. Development evidence (DEV_QUALIFICATION.json; seeds 16_300_001..400; rows sha256 1d5ccf28...)

The verdicts obtained with the registered rule at N = 400 on development seeds:

| Subject | Verdict | Pre-competent lives | K1 W:L:T | K2 W:L:T | Late acc. full / frozen / shuffle / newlife |
|---|---|---|---|---|---|
| reference | REVISION_HISTORY_DEPENDENT | 400 | 396:0:4 | 249:149:2 (Holm p 3.1e-7) | .645 / 0 / .424 / .714 |
| smuggler | REFUSED_FIXED_PRIOR | 0 | ties | ties | 1.0 / 1.0 / 1.0 / 1.0 |
| smuggler_decorative | REFUSED_FIXED_PRIOR | 0 | ties | ties | 1.0 throughout |
| memoryless_plus | REVISION_NOT_SHOWN | 400 | ties | ties | 0 throughout |
| constant_plus / _minus | REFUSED_FIXED_PRIOR | 199 / 192 | ties | ties | .50 |

The known-answer positive is detected. Both forbidden channels are refused: on the coordinator's endpoint alone they
score PERFECTLY (1.0), and the instrument separates them only through G_PRE. That is why G_PRE is part of the rule.
memory_ok and recompute_ok held on all 9,600 rows. The reference's newlife pre-switch accuracy was .495 against
1.000 for memoryless_plus, consistent with s5.5. No searched subject's endpoint has been computed. Their only
contact with the assay is `assay.preflight` (2 development seeds), which returns memory_ok / recompute_ok and
discards the rows unread.

Structural facts about the searched subjects, read from the genomes before any assay: 5 of 8 set eta, sigma > 0 but
carry NO plastic parameter (tape.plastic_keys empty). Their full, frozen and shuffle arms are therefore the same
computation, and they cannot be classed as revisers. The other 3 carry 8, 64 and 16 plastic floats.

## 9. Resources (directive s13)

- Expected: 14 subjects x 400 seeds x 5 lives (newlife = 2) = 28,000 lives, about 5.5 ms each on harry1, so about
  155 CPU-seconds; a row file of about 6 MB. Peak working set about 50 MB (measured: 47 MB at N = 100).
- Parallelism: ONE process (all arms on one host and version set, by design). No ubu006, no Fabric, no paid compute.
- Stopping: none data-dependent. The run is complete at 28,000 lives. An external abort (crash, timeout) discards the
  partial output and reruns from the start: the run is deterministic, and the rerun must reproduce rows_sha256 of
  any completed earlier attempt if one exists.
- Reproducibility: rows_sha256 is recorded. A second run on harry1 with the frozen versions must give byte-identical
  rows. Another host or version set needs its own development baseline and is not comparable digit for digit.
- Checkpointing: not necessary (minutes).

## 10. How the confirmatory run is executed (a later packet, after the Q3 challenge)

    python -m rso.ensorain.freeze check                                   # must print OK
    python -m rso.ensorain.assay confirm rso/ensorain/runs/CONFIRM.json --n 400 \
        --subjects rso/ensorain/SUBJECTS.json --cleared-by <challenge/integration ref>

`confirm` refuses on any FROZEN.json mismatch, another Python/numpy version, or a missing --subjects/--cleared-by.
Read the result under s5 only. Commit the row file with the result.

## 11. Known limitations (declared before outcomes)

1. The sign test ignores magnitudes. It is exact and float-free, and powered at N = 400.
2. Pairing by seed matches sw. The rng streams of arms diverge after block 0 (frozen draws no perturbations; shuffle
   draws a permutation), so the pair shares its switch block and not its episodes.
3. The effect model for power uses the reference's development distribution, and the searched subjects' variance is
   unknown. Family S power is therefore indicative.
4. K1 is nearly automatic for any genome whose frozen arm keeps the pre-switch sign, since frozen late accuracy is 0.
   The demand claim it carries is exactly "a non-learning version of this genome cannot do the post-switch task".
   The comparison against the whole memoryless class rests on the four-policy argument in s3, plus G_PRE.
5. Smuggler analogues are constructed (no TAPE-native Smuggler exists; the E0/E1 Smuggler at ensorain/e0/memories.py:325
   is a pattern, not reusable code). A forbidden channel outside the genome, for example the block index, is not
   reachable by a TAPE genome (observations carry no global address: worlds.py header). That is a property of the
   world, not something this instrument tests.
6. The searched subjects were produced on harry1 with world K = 32 (search.py evaluates at world.K). The assay runs
   at K = 64. This is the same convention certify.py uses.
