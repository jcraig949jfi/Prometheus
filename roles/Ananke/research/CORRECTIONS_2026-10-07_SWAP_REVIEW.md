# Corrections 2026-10-07: independent review of the mirror-pair swap instrument

Context: the operator's 72h order (s2) asked for an adversarial pass on the swap instrument, after Hestia's audit noted
that lens_swap.py, swap_rel.py and campaign.py had never been read outside this seat.
- Reviewer: an independent subagent with no access to this seat's reasoning. It worked read-only at 8c48ebfdf.
- Tests run by the reviewer: test_lens_swap, test_swap_rel and test_lens_instruments, 42 passed.
- Known-answer script: hold_latch HOLD.

Overall verdict: no FATAL defect. The swap MECHANICS are correct:
- the named component is exchanged between twins (2k, 2k+1), not copied;
- it happens at the intended tick, between ticks;
- no RNG stream or counter is touched, and SITE + FLIGHT covers the full World state.

## Material findings (the verdict layer, not the mechanics)

- **M1. Empty swaps are scored as evidence.** The verdict functions never check that the swapped component differed
  between twins.
  - In sync physics with update_period 1, Acc_sum/Acc_cnt are zero between ticks, so the inbox arm is always empty.
  - w, r, Kp and E are empty whenever twins hold identical values.
  - **Reading:** an empty swap means the component carried no twin difference at that tick. That is a true statement
    about carriage at that tick. But it is NOT evidence that a differing component goes unused, and it is vacuous for
    the inbox under sync update_period 1.
- **M2. Offsets are not bounded by the readout.** run_arms and mixture_scan accept offsets ≥ ro_off (the swap lands
  after the scored readout) or below the trial onset (silently dropped). REL4 then certifies NO_EFFECT_REL. The frozen
  census catches this (IDENTITY-BROKEN); REL4 does not.
- **M3. The absolute rule has no competence precondition.** lens.swap_verdict calls FLIP on hi < .40, so an
  incompetent specimen reads FLIP from an empty swap. A weak specimen's randomized swap reads NO-EFFECT, not CHANCE.
- **M4. classify (SITE/CHANNEL) uses point estimates** (fS ≥ .80) with as few as 20 correlated pair-trials. A true fS
  of .65 reads SITE about 12% of the time.

Minor findings:
- m1: run_arms does not tile reset_state_mask, which raises an error rather than giving a wrong answer.
- m2: arm_identical compares readouts, not state.
- m3: REL4 silently returns NOT_ELIGIBLE outside its P/K table.
- m4: flip_state_transplant can never produce a result (already known and tested). It also builds Worlds from raw
  seeds rather than mirror-paired ones.

## What changes and what does not

- **C2A, C2B, C2BX and C2C used no swaps.** Their verdicts are unaffected.
- **Earlier ARC/C1b swap statements stay on record unchanged, with these readings attached:**
  - "Routing never carried the bit" and "r was never the memory carrier (18/18)" mean NO-EFFECT or EMPTY, not
    separated. Either way, w/r carried no usable cue difference at the tested ticks. The conclusion stands, but its
    evidence type is "no twin difference or no effect", not "a differing component that goes unused".
  - Inbox swap readings under sync update_period 1 are structural (EMPTY by construction), not empirical.
  - Any recorded REL4 NO_EFFECT_REL at an offset ≥ ro_off would be invalid. A full audit of past offsets is queued as
    T-SWAP-AUDIT2 and is not done in this window.
  - Absolute-rule verdicts on specimens with normal accuracy < .55 are not evidence (M3).
- **New campaigns (C3 onward) use roles/Ananke/pte/c3/swap_v2.py.** It has an applied-ness census (EMPTY_SWAP), an
  offset bound, a competence gate, and BOOTT intervals on a relative transfer statistic. It passes 5 known-answer
  tests (test_swap_v2.py), and lens.py and lens_swap.py are untouched.
