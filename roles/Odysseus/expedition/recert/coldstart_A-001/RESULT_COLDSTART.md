# RESULT_COLDSTART -- recert packet cold-start trial + L4: the ENVGATE-01 founder "copier" label

Currency: 2026-09-28. Worker: coldstart_A-001, a fresh subagent with no oral context. Host ubu001, Python 3.14.4, stdlib
only, 1 process, on a laptop shared with a 3-process background job. Worktree
/home/jcraig/Prometheus-worktrees/odysseus-base-role. HEAD was 02800d2b5 at the start; the owner committed recert/ mid-trial
(d3941cb07), and HEAD is now 281eeed50 = origin/main. Nothing was committed or posted by this worker, and nothing outside
this directory was written, apart from a scratch snapshot in the session scratchpad. Pure ASCII.

## 1. Fixture (packet criterion d)

- `python3 test_known_answers.py` gives 24/24 in 3.3 s wall, peak RSS 26 MB. I ran it from a COPY in this directory, with
  REPO depth patched 4 -> 5 (PACKET_GAPS G2). KNOWN_ANSWERS.json came out byte-identical to the committed one.
- I repeated it UNPATCHED from a `git archive origin/main` snapshot (281eeed50): 24/24, byte-identical again.

## 2. New label: L4 = Archaeon ENVGATE-01 founder "copier"

What we called it then: the frozen census ruler (archaeon/envgate/ruler.py) classes each arriving tape ONCE, with an empty
neighbour and all 256 input bytes. EXACT_GATED, NEAR_COPIER and SPAN_COPIER make a founder "copier-founded". The ENVGATE-01
review reads this as "founders the frozen ruler says can reproduce alone", and the post-hoc copier-founded contrasts
(C1 46 vs 0, C3 37 vs 8) rest on it. Why this label:
- it is consequential;
- it comes from a different engine to L1-L3 (archaeon vmcopy32), so it tests the harness's portability;
- the world runs founders against OCCUPIED random neighbours, which the ruler never did;
- nobody had recertified it. Prior-work search log: prior_work_search.log. FF-1 recertified the LINEAGE label, not the
  founder class.

Spec (l4_envgate_copier.py; frozen in PREREG.md before any founder was run):
- 13 environments: neighbour contents. These are zero, 6 uniform random tapes, 2 takeover residents, 2 copier founders and
  2 INERT founders, never the object itself. Each environment is swept over all 256 inputs.
- Pass: some input gives a copier-grade birth, i.e. coverage >= 0.9 and (fid >= 0.75 or span >= 0.75 G). min_rate is 0.5.
- Mechanism: template intervention, offset-aware (child[p-k]). The mechanism counts as template copying if T >= 0.5.
- Structure: a COPY byte is present.
- Objects: all 393 distinct founder tapes of the 475 established lineages: 81 labelled copiers and 312 unlabelled
  non-copier founders as controls.

L4 fixture (test_l4_known_answers.py): 16/16 in 2.5 s. It covers:
- true instances: an ungated replicator, an input-gated copier (IN C), and a k=1 shifted copier;
- impostors: blank tape -> PROV; copy behind HALT -> SWB; a zero painter that the FROZEN RULER CLASSES NEAR_COPIER -> BWEM,
  T 0.00; an empty-neighbour-only copier -> CTX, rate 0.08;
- an unlabelled replicator -> UNLABELLED_LABEL_OK;
- the frozen ruler's class for each planted tape.

Run: `python3 l4_envgate_copier.py` took 270 s wall, peak RSS 31 MB. Rows are in L4_rows.json, tables in TABLES_L4.txt
(analyse_L4.py).

    L4 verdicts                    n    OK   CTX  BWEM  SWB  PROV
      EXACT_GATED (labelled)       63   63    0    0     0    0
      NEAR_COPIER (labelled)       18   18    0    0     0    0
      INERT   (unlabelled)        251    0    1    0   176   74     (UNLABELLED_*)
      WRITER  (unlabelled)         47    0    0    0    46    1
      TOUCH   (unlabelled)         14    0    0    0     9    5

Preregistered predictions:
- P1 HELD. The ruler class recomputed now equals the recorded founder_class for 393/393. The exact-input set equals
  founder_exact_inputs for 81/81.
- P2 HELD. 81/81 labelled copiers are LABEL_OK (the threshold was >= 70%). 79 pass in 13/13 neighbour environments; 2 (one
  per labelled class) pass in exactly 7/13, at the boundary. Exact-copy retention at the founder's exact input under the
  12 occupied neighbours is 748/756 (0.99). The census stage-2 figure of 95/176 counts a different population: NEAR/SPAN
  hits have no exact input.
- P3 HELD. 0 BWEM. T is 0.50-0.86 (median 0.75) and bits transmitted are 88-216 (median 184). T sits AT the cut for one
  founder (a47c4ffc, T = 0.500), and below 0.55 for 3 more. A T_MIN of 0.55 would turn 2 into BWEM. As in the planted
  copiers (T 0.72-0.78), the cause is that the copy routine takes up a large share of a 32-byte tape.
- P4 FALSIFIED. The median heredity share among the 63 EXACT_GATED founders is 0.316. My cut was <= 0.25. IQR 0.13-0.46,
  range 0.07-1.00. NEAR_COPIER median 0.24. The direction held and the magnitude did not.
- P5 HELD. 1/312 (0.3%) unlabelled founders show the behaviour. See s3.

Then vs now: the world versus isolation.
- A "copier" founder's typical birth is not a copy. Under an empty neighbour and uniform inputs, EXACT_GATED founders have
  a median of 38 birth inputs, of which 12 are copier-grade and 1 is exact.
- The mean fidelity of all births in isolation is 0.030 (median; max 0.10).
- The world's records for the same lineages give a births-weighted mean fidelity of 0.164 and an exact share of 0.018
  (medians). Those figures include descendants.
- So the label says "can reproduce alone", and that is true (P2). But roughly two thirds of what such a founder places in
  the ecology, and about 95% (1 - 12/256) of its executions at uniform inputs, are non-self births or no birth.

The gate is an address. 70/81 labelled founders have copier-grade inputs ONLY within 120..131, and 53 have exactly 120..131.
The input byte is the copy destination: 128 is the neighbour base, and x near 128 gives a shifted copy with span >= 24.
Exact gates: 128 x54, 127 x7, 129 x1, 255 x1. This confirms, per founder in isolation, the ENVGATE-01 review's
"reproductive-input window" reading. ENVGATE-02 later found that restoring parts of the window does not rescue
establishment, so the window is where copies happen but was not shown sufficient for lineages.

## 3. The one unlabelled behaviour: host-mediated transmission of the HOST's genome

Founder 5334b0df25513416:
- Ruler class INERT. Block 15, RESCUE_128. The world credited it with 16,873 births (14,766 exact) and max generation 327,
  under parent-chain identity.
- It copies in none of 12 neighbour contexts.
- Next to eco1, a block-15 takeover resident (EXACT_UNGATED; source lineage 15/BAND_BLOCK/2097035), it produces a
  copier-grade birth at ALL 256 inputs.
- It runs 150 steps of foreign code, i.e. the resident's code. The window ends up holding the HOST's own bytes 0..27 at
  window offsets 4..31 (span 28, k = -4). Positional fidelity is 0.0.
- Template intervention: T = 0.58, 128 bits. The host's genome, not the resident's, is carried.
- The child is ruler-class INERT, so this is not stable heredity on its own. Every hosted round shifts it again.

Contrast with the adjudicated reading (ENVGATE-01 s8, ruling R2):
- That reading is that host-mediated reproduction "amplifies residents but does not originate genomes", and that hosts
  emit the resident's genome (23/26 exact copies of the resident; host first-birth fidelity 0.008).
- This row shows the same channel can also transmit the host's own bytes.
- Positional fidelity (0.0 here, 0.008 there) cannot see it; a same-offset span can. This is an FF-15 instance ("fidelity
  is resemblance") in the ENVGATE measurement.
- It is a single row in isolation. I have NOT shown that it happened in the world. It is a candidate for the
  causal_lens / genetic-lineage (taint VM) tools, not a claim.

## 4. What changed in the packet's framing

- The harness ported to a third engine in one spec file (l4_envgate_copier.py, ~230 lines with documentation), and its verdict logic needed no change.
- The finding that carries over is that the environment set has to be chosen against the label's own qualifiers (G6).
- The ENVGATE copier label is sound as a CAPABILITY in 81/81 cases, and it survives neighbour occupancy. So "copier-founded"
  is not a provenance-only label, unlike P-11's L2 genomes.
- What the label hides is HEREDITY RATE. "Copier" means a gated capability at about 12/256 inputs, next to about 26 other
  birth inputs that write non-self children.
- The frozen ruler admits painters: the planted zero painter is NEAR_COPIER. None was found among the real founders, but
  the ruler has no mechanism column.

## 5. Next questions

- Replay host 5334b0df with the genetic-lineage VM in its block-15 world. Does host-genome transmission occur in situ, and
  does any shifted descendant regain copier class?
- Re-cut copier-founded establishment by heredity share (for example >= 0.3 vs < 0.3). Do high-share founders explain
  establishment better than the class does?
- Reconcile L2 (packet) with Artemis P-11 challenge 2af325f7b (PACKET_GAPS G12).

## 6. Limits

- Isolation, not world replay: no copy noise, overwrite, death, or the case-0-only birth rule.
- The neighbour set (13) and the thresholds (min_rate 0.5, T_MIN 0.5, NEAR 0.75) are my choices. Every row keeps the pass
  rate, the per-environment gate width and T, so any of them can be re-cut.
- One founder has T exactly at the cut and two have rates exactly at the cut.
- Heredity share weights inputs uniformly (the U arm), not per arm.
- PREREG.md was written and hashed (PREREG.sha256) before the data run, but it is not committed. Its timestamp rests on
  this worker's word and the hash file.

## Commands (from this directory, PYTHONDONTWRITEBYTECODE=1)

    python3 test_known_answers.py            # 24/24 (copy; REPO depth patched)
    python3 test_l4_known_answers.py         # 16/16
    python3 l4_envgate_copier.py             # 393 rows, 270 s
    python3 analyse_L4.py > TABLES_L4.txt    # (the exact-retention block was appended by an inline script; see TABLES_L4.txt)

Total compute: about 5 min wall, well under the 40 min cap.
