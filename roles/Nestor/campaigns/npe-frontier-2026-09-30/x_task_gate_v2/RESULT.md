# X-TASK-GATE v2: result

**Verdict: INSTRUMENT_UNREACHABLE (Stage 0), descriptive subtype TRANSIENT_ONLY. Stage 1 was not run.**

This was decided under the frozen rule (`PREREG_V2.md`, freeze ef6d68cee) and is recorded in `STAGE0.json`.

| | |
|---|---|
| Host | BUCKKEEP, CPU only, 4 workers |
| Production window | 2026-10-05 07:17:58 -> 07:31:59 EDT (841 s wall; 3,064 run-s) |
| Peak memory | <= 88 MB per worker |
| Receipt | `results/stage0/RECEIPT_*.json` |

**Status, kept separate:**
- **Technical:** COMPLETE. 18 of 18 runs, no failures, rows and detail files present.
- **Scientific:** INSTRUMENT_UNREACHABLE. The planted positive's decisive quantity does not fire at the readout time.

## Stage 0 rows (seeds 43_000_000 + s)

| arm | established (depth >= 20) | final CD_TX >= 0.10 | final CD / CS >= 0.10 | CD_TX peak (descriptive) |
|---|---|---|---|---|
| PAIR_POS (CT_UA) | 4/6 | **0/6** | 0/6 / 0/6 | 0.54, 0.41, 0.40, 0.41 at epochs 20-30; CS = 0 from epochs 60-90 |
| PAIR_READ_NO_USE (CT_U) | 4/6 | 0/6 | **0/6 / 0/6** | 0 at every snapshot |
| PAIR_COPY_ONLY | 5/6 | 0/6 | **0/6 / 0/6** | 0 at every snapshot |

- **Every PAIR_POS run that established was the same:**
  - Planted CT_UA spread by P-11-certified copying.
  - Up to 54% of the population was task-competent P-11 descendants carrying competence transmitted from the planted
    competent founder (origin P11_TX).
  - The task routine was then lost from every copy within about 60-90 epochs.
  - The copier stayed at fixation to epoch 2000: P11-born share 0.77-0.97, causal depth 85-112.
- The two PAIR_POS runs that did not establish lost the single plant in the first epochs. The same thing happened at
  that seed in the paired negative arms (seed 43_000_002 in all three).

## The ten questions

1. **Could CT_UA cause task-competent P-11 descent on the pair path?**
   - Yes, transiently. CD_TX peaked at 0.40-0.54 in 4 of 4 established runs.
   - It did not persist to the final-state readout: 0 of 6.
2. **Did CT_U fail once actual cue use was required?** Yes.
   - Its use score is 0 statically. It still passes the old bridge+reader ruler (0.75 with 3 reads).
   - CD = CS = 0 in 6 of 6 runs, including 4 runaways.
3. **Did COPY_ONLY fail the task criterion?** Yes. CD = CS = 0 in 6 of 6 runs, including 5 runaways.
4. **Was Stage 0 therefore a reachable ruler?**
   - The ruler is correct and fires: it separates use from reading and from copying, and its static, cache and
     provenance tests pass.
   - It is NOT reachable at the readout time, because the world does not keep a planted competent copier competent for
     even 5% of the run.
   - By the frozen rule that is INSTRUMENT_UNREACHABLE, so Stage 1 cannot be interpreted and was not run.
5. **Did random TG populations establish a causal replicator regime?** Not tested. Stage 1 was not run, by rule.
6. **Did task competence arise?** Not tested in random populations. In Stage 0 a few creation events were logged in the
   planted arm: MUT 5, P11_CREATED 3. None persisted.
7. **Did it appear inside P-11-causal descendants?** In Stage 0, yes, transiently: CD_TX was almost all of CD at the
   peak.
8. **Was that competence transmitted through replication or created later by mutation?**
   - In Stage 0 it was transmitted: origin P11_TX, rooted at the planted founder.
   - Mutation-created competence was rare and short-lived.
   - The provenance split worked as designed.
9. **Did TG exceed SHUF?** Not tested.
10. **What does this say about endogenous functional heredity in NPE?**
    - In this world (ffa6 pair tape, ATOMIC write-back, LOW operand mutation, TG gate with floor 0.15), causal heredity
      CAN carry a useful functional property across many P-11 generations.
    - It cannot MAINTAIN that property. The copier is maintained because copying is self-propagating.
    - The task routine is ballast to the copier, and nothing selects for it on the pair tape:
      - the gate raises a competent organism's interaction rate, and every interaction both copies it and overwrites
        it, symmetrically;
      - every interaction also mutates both halves (ATOMIC).
    - So the routine decays to zero while the copier sweeps.
    - Functional heredity is reachable, but it is not maintained in this world, so a final-state test of task-coupled
      descent from random populations cannot qualify here.

## Strongest remaining alternative explanation

The TRANSIENT_ONLY failure is a property of the chosen readout time and of this world's parameters, not a general
impossibility. Specifically:

- One plant per run, at mutation rate LOW, with a 40-byte routine. The loss rate is about 0.09 per interaction against
  zero selective advantage.
- A design in which competence buys a replication ASYMMETRY would be a different experiment. Examples:
  - the gate decides which half executes first or copies;
  - the gate acts on being copied rather than on interacting.
- Such a design could still show maintained task-coupled descent. This result rules out the symmetric
  interaction-rate gate, not task coupling in general.
- **Not yet measured:** the counterfactual "TG vs no gate", to decide whether the gate is neutral or actively
  harmful to competence (competent organisms interact, and so mutate, more often). Under the frozen design no claim is
  made either way.

## Evidence

- `PREREG_V2.md`; `STAGE0.json` (verdict, code SHA).
- `results/stage0/*.json`: per-run rows with trajectory, provenance counts and root kinds.
- `results/stage0/*.detail.json.gz`: per-organism provenance, competent genomes, roots and P-11 birth edges.
- `MECHANISM_STAGE0.txt`: a descriptive read after the verdict, with no new runs.
- `flights/`: flight evidence disclosed before the freeze.
- `test_xtg2.py`: 5 of 5 tests. PV-3 fails on the pre-repair code.
