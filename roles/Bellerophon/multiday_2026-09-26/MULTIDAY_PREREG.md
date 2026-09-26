# MULTI-DAY CAMPAIGN PREREGISTRATION -- Bellerophon, physics v3: acquisition, protection, repair

Status: DRAFT (becomes FROZEN at the commit that fills the freeze record in s12; nothing above the amendments section
may change after the first scientific run). Authority: operator rulings 2026-09-26
(prompts/00_OPERATOR_RULINGS_verbatim.md), ruling 2: the coupling closeout issued READY_FOR_MULTIDAY, so the scoped
campaign proceeds autonomously. Scope source: roles/Bellerophon/coupling_2026-09-24/NEXT_MULTIDAY_CAMPAIGN.md.

## 0. Question

Once correct computation pays for reproduction (physics v3), does evolution go BEYOND keeping seeded code alive?
Specifically: do computing copiers acquire the NEXT computation on a task ladder (Q1), does their computation become
more robust to copy damage (Q2), and does repair of self-damaging copiers become common over a long horizon (Q3)?

## 1. Physics and code

Physics v3 unchanged (prometheus/z80atlas/coupling.py; COUPLING_CAMPAIGN_PREREG.md s1). Coupling modes ON, OFF,
SHUFFLED, YOKED as defined there. Driver prometheus/z80atlas/multiday_campaign.py. Measurement-only changes since the
coupling campaign, each proven output-identical: tasks.verify_exact + vm.execute(stop_at_first_out) for the
competence tracker (receipts/MEASUREMENT_SPEEDUP_2026-09-26.md: byte-identical 400-tick world vs the pinned coupling
code); World.events bounded in memory to exactly the records the runner writes; mid-run checkpoints (s6).

## 2. Parameterizations

K16 (BASE 16, BONUS 64) and K40 (BASE 40, BONUS 64), exactly as in the coupling campaign; both run in every lane as
separate strata of the same seed-pair family.

## 3. Lanes, arms, founders (plan sha256 in s12)

| lane | founders / start | task paid | arms | seeds per K | runs |
|---|---|---|---|---|---|
| LADDER1 | 4 ECHO acquirers (AUTO 2, 4, 5, 8), founder = k mod 4 | INC | ON OFF SHUFFLED YOKED | 80 | 640 |
| COPIER | pure copiers (SEEDED_REPLICATOR), no task code | ECHO | ON OFF SHUFFLED YOKED | 60 | 480 |
| REPAIR | REP + BAD (copier sweep wrecks its own INC code) | INC | ON OFF YOKED | 80 | 480 |
| LADDER2 | 3 INC repairs (AUTO 14, 15, 18), founder = k mod 3 | COND_ONE | ON OFF SHUFFLED YOKED | 60 | 480 |

Total 2,080 runs. Founders: receipts/md_inputs.json (tapes, source runs, AUTO per-arm successes). Each founder was
re-verified on 2026-09-26: ECHO founders are ECHO-exact and NOT INC-exact; INC founders are INC-exact and NOT
ECHO-exact; all self-copy alone. So any competent self-replicator on the PAID task at the end of a LADDER run is an
acquisition, not a founder. Ladder order follows the measured task family in tasks.py (ECHO -> INC -> COND_ONE); the
design note's SUM2 rung was replaced before freeze because SUM2 is a different family (two reads).

## 4. Common settings

Horizon TICKS = 10,000 (20x the coupling campaign). 256 cells, budget 256, GRID/LOCAL, Z80_64, SHARED,
ENDOGENOUS_COPY, IMPLICIT, NEUTRAL scoring, ABR, FIXED env, BYTE mutation MED; init RANDOM with the founder tape(s)
as init_tapes (COPIER: init SEEDED_REPLICATOR). Seeds: 12e12 + lane*1e9 + K_block*1e5 + k (disjoint from coupling
11e12, grounding 9e12, pilots 7e12..7.9e12); arms of one pair share the seed.

## 5. Execution

Priority LADDER1, COPIER, REPAIR, LADDER2; within a lane, plan order. Continuous submission; YOKED released when its
ON partner's result exists (a YOKED whose ON partner voided or never ran gets an empty yoke, recorded).
Workers: TBD-PILOT, recycled every 2 runs. Active-runtime cap: TBD-PILOT h (sum of execution segments;
suspensions do not count; a crashed segment closes at its last heartbeat). Runs not completed at the cap are
NOT_RUN by lane and K. A restart re-executes only runs without a result line. Voids are recorded, never re-seeded.
Detached supervisor with standing recovery authority (as in the coupling campaign's Amendment 1).

## 6. Per-run measurements (frozen)

End of run: everything the coupling campaign recorded (competence summary, ledger, births, dominant tapes, frozen
architecture descriptor of the dominant competent SR tape). Checkpoints after ticks 499, 999, 2,499, 4,999, 7,499,
9,999 (0-based tick index): alive, competent (paid task), competent self-replicators, SR alive, dominant competent SR
tape, dominant SR tape, previous-rung competent count (LADDER1: ECHO; LADDER2: INC), robust_comp =
robustness(dominant competent SR tape, n = 128, seed = run seed mod 2^31) and robust_sr_copy = copy-only robustness
of the dominant SR tape. Robustness (prometheus/z80atlas/robustness.py): the fraction of n sampled single-byte
substitutions of the tape that stay exactly competent (task), still self-copy (copy), or both (joint); eligibility
requires task competence (copy-only mode: self-copying).

## 7. Primary hypotheses (confirmatory; exact two-sided sign tests on seed pairs, ties dropped; Holm across 5)

acquired(run) := at least one competent self-replicator on the PAID task alive at the end (competence
final_competent_sr >= 1).

Q1_LADDER1  acquisition of INC from ECHO copiers: ON > OFF, ON > SHUFFLED and ON > YOKED (pairs pooled over K).
Q1_COPIER   acquisition of ECHO from pure copiers: same three contrasts.
Q1_LADDER2  acquisition of COND_ONE from INC copiers: same three contrasts.
            For each Q1 the test p-value is the LARGEST of its three sign-test p-values (ON must beat every control),
            and Q1 holds only if also (kill margin) rate(ON) > max(rate(OFF), rate(SHUFFLED), rate(YOKED)) + 0.02.
Q2          protection of computation: over all ON runs with >= 2 checkpoints carrying an eligible robust_comp, the
            change in task robustness (last eligible checkpoint minus first) is > 0 (sign test over runs).
            Reported beside it (not a test): the same change in copy-only robustness in OFF runs.
Q3          repair becomes common: REPAIR acquisition ON > OFF and ON > YOKED (largest p), AND rate(ON) > 4/60
            (the coupling campaign's E2 K16 ON rate at 500 ticks).
A hypothesis HOLDS iff Holm-adjusted p < 0.05, the direction is as predicted in every contrast, and its extra clause
(Q1 margin, Q3 baseline) is met.

## 8. Secondary and descriptive (labelled; never promoted to primary)

Per-K rates for every Q1/Q3 lane; previous-rung retention at the end (does acquiring INC lose ECHO?); tick of the
first checkpoint with a competent SR (time to acquisition); non-competent-earner share by lane (exploit channel);
frozen architecture descriptors of acquired dominants; copy-only robustness drift in OFF runs.

## 9. Instrument checks

instrument_ok := no VOID runs, no ledger imbalance, and a seeded 3% replay (random.Random(20260926)) of completed runs
byte-identical (every field except wall_s). Pre-freeze evidence: 30/30 smoke runs (300 ticks, all lanes and arms,
off-plan seeds) replayed identically; z80atlas tests TBD-PILOT/TBD-PILOT.
If instrument_ok fails, no hypothesis is interpreted; the report is INSTRUMENT_REPAIR_REQUIRED.

## 10. Disposition (frozen)

Report each of Q1_LADDER1, Q1_COPIER, Q1_LADDER2, Q2, Q3 as HOLDS / FAILS with its failure shape (which contrast,
which clause, effect size and CI). Overall:
  LADDER_CLIMBED        Q1_LADDER1 holds (evolution acquires a computation it did not have, because computation pays)
  PROTECTION_EVOLVED    Q2 holds
  REPAIR_COMMON         Q3 holds
  NO_ESCALATION         none of Q1_LADDER1, Q1_LADDER2, Q2, Q3 holds (a clean negative: the coupling maintains and
                        barely creates; the next step is rephysics, not a longer run)
Several tags may apply. No tag is tuned after launch.

## 11. Exclusions

None except VOID runs (listed). Extinct runs are data (acquired 0; robustness undefined).

## 12. Freeze record

TBD at freeze: plan sha256; sha256 of multiday_campaign.py, robustness.py, coupling.py, world.py, vm.py, tasks.py,
adjudication.py, md_analysis.py, md_inputs.json; pilot receipts; pinned code copy path.
