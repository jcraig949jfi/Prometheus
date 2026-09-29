# PREREG -- L4 recertification of the ENVGATE-01 founder "copier" label (coldstart_A-001)

Written 2026-09-28 BEFORE any committed founder tape is run through the L4 spec. This file is not edited after the run
(it stands in for the "own commit" of 00_READ_FIRST.md; this worker may not commit). Pure ASCII.

## What has already been done / seen (disclosed)
- Frozen fixture reproduced: test_known_answers.py (copy, REPO depth patched) 24/24; KNOWN_ANSWERS.json byte-identical.
- L4 spec (l4_envgate_copier.py) and its fixture (test_l4_known_answers.py) written; fixture run on HAND-BUILT tapes only:
  16/16 (8 verdicts + 8 frozen-ruler classes). The neighbour set reads 6 tapes from LINEAGES.json as environments.
- Seen before this prereg: LINEAGES.json summary (founder classes: EXACT_GATED 90, NEAR_COPIER 22, WRITER 58, INERT 290,
  TOUCH 15 lineages; 393 distinct founder tapes: 63 EXACT_GATED, 18 NEAR_COPIER, 47 WRITER, 251 INERT, 14 TOUCH); ONE
  lineage record (block 0 U arrival 320008: founder_exact_inputs [128], 99 birth inputs, world mean_fid 0.088, exact
  fraction 0.0067); the ENVGATE-01 review (copier-founded lineages: mean fidelity median 0.17, exact-birth fraction median
  1.6%); census stage 2 (vmcopy32: 95 of 176 hits kept an exact copy with ONE random occupied neighbour on their exact inputs).

## Question
Does a founder the frozen ENVGATE ruler labels a copier (EXACT_GATED / NEAR_COPIER / SPAN_COPIER; "copier-founded", "can
reproduce alone") actually write a self-copy, by copying, in the neighbour contexts the ecology presents, and not only in
the ruler's single empty-neighbour context? What does a "copier" founder's typical birth look like?

## Objects (eligible count)
All 393 distinct founder tapes of the 475 established lineages (archaeon/envgate/LINEAGES.json). Labelled = ruler class
in HIT_CLASSES: 81 (63 EXACT_GATED, 18 NEAR_COPIER, 0 SPAN_COPIER). Unlabelled controls (same test, UNLABELLED_ prefix):
312 (251 INERT, 47 WRITER, 14 TOUCH). No exclusions.

## Test (frozen here; code in l4_envgate_copier.py)
- Environments: 13 neighbour contents (zero; 6 uniform random tapes, seeded; 2 takeover residents; 2 EXACT_GATED founder
  tapes; 2 INERT founder tapes, chosen by sha256 order, never the object itself), each swept over all 256 input bytes
  (census input-skip), vm.execute, step_cap 256, copy primitive on.
- Behaviour pass (per environment): some input gives a copier-grade birth: coverage >= 0.9 and (fid >= 0.75 or same-offset
  span >= 0.75 G). min_rate 0.5 (>= 7 of 13 environments).
- Mechanism: template intervention (32 positions x 2 substitutions) at the best input of the zero environment (else the
  first passing one); carried iff child[p - k] == b; ok iff T >= 0.5.
- Structure: a COPY-primitive byte (byte & 31 == 20) present.
- Verdict: recert.verdict, frozen vocabulary, unchanged.

## Predictions and decision rules
P1 (ruler reproducibility) ruler_class_now == founder_class for 393/393, and the zero-neighbour exact-input set equals
   founder_exact_inputs for every labelled founder. Any mismatch is reported as a ruler/record defect.
P2 (label holds under occupancy) >= 70% of the 81 labelled founders are LABEL_OK. Reason: COPY writes the window from the
   tape; my copier-grade criterion tolerates unwritten bytes (the likely cause of the census's 54% exact retention).
   FALSIFIED if < 70%.
P3 (mechanism) BEHAVIOUR_WITHOUT_EXPECTED_MECHANISM <= 10% of labelled (random-tape founders are unlikely painters).
   FALSIFIED if > 10%.
P4 (heredity, the then/now column) median heredity_share_zero (copier-grade births / all births over 256 inputs, empty
   neighbour) among the 63 EXACT_GATED founders <= 0.25: most births of a "copier" founder at uniform inputs are NOT
   copies. FALSIFIED if the median > 0.25.
P5 (ruler false negatives) UNLABELLED_{LABEL_OK, LABEL_CONTEXT_DEPENDENT, BEHAVIOUR_WITHOUT_EXPECTED_MECHANISM} together
   <= 2% of the 312 controls. By construction the zero environment reproduces the ruler, so any such row must come from an
   OCCUPIED neighbour; that would be a real finding (copying enabled by the neighbour). FALSIFIED if > 2%.

## Controls
- Negative: blank tape (PROV), copy routine behind HALT (SWB). Positive: ungated replicator, input-gated copier (IN C),
  shifted k=1 copier (all LABEL_OK). Cheat: zero painter that the frozen ruler itself classes NEAR_COPIER (must be BWEM).
  Context: empty-neighbour-only copier (must be CTX). Unlabelled replicator (UNLABELLED_LABEL_OK). 16/16 required first.
- Population control: the 312 non-copier founders.
- Matched random-sampling / random-walk baselines: not applicable (no search or selection is claimed; a re-test of
  committed objects).

## Falsifiers
- Harness: any planted impostor passed or planted true instance rejected (24/24 + 16/16 must hold).
- Label: P2 falsified (the "copier" label does not survive the ecology's neighbours).

## Compute
One process (serial recertify_one loop), stdlib, Python 3.14.4, 4-core laptop shared with a background job. Estimate
<= 20 min. Abort and report partial if > 35 min.

## Known limits accepted in advance
- T >= 0.5 presumes the copy routine occupies < half the tape; a genuine copier with > 16 essential code bytes could read
  as BWEM. Rows keep T so the cut can be moved.
- Copy noise, overwrite, deaths and the world's case-0-only birth rule are not replayed (isolation, not world replay).
- The neighbour set is my choice; every row keeps the per-environment gate width.
