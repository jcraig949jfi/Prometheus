# T-EXT-1  Turn the prior-art raid into PTE tests

QUESTION. Which prior-art instruments sharpen PTE, and what do they say
about M2/M3?

EVIDENCE. ../PRIOR_ART_temporal_distributed_computation.md (s0, s12-14).

STEPS (each one small; write the plan, then run)
1 PING probe (Wolff et al. 2017). Inject a cue-neutral pulse at mid-gap
  into M2 and decode the cue from the response. Prediction: M2 does not
  need it, because its carrier is active. The point is to validate the
  probe for any future "silent" champion.
2 Simulator-state audit (the Thompson FPGA lesson). List every state or
  order dependence in engine._tick: queue order, index_add order,
  tie-breaks, RNG streams. Confirm a program can read none of them except
  the declared registers. Deliver a table.
3 JIDT local AIS / TE screening with CHANNEL variables. Validate on the
  JIDT CA example first, then on plants.echo_hold (known answer: storage
  at the loop level, transfer at the edge level), then run it on M2.
4 Carrier model (the Crutchfield-Mitchell standard). Write a reduced
  model of the M2 echo (a two-stage pipeline + the latency distribution)
  that predicts the S-M2b gap-tuning curve without running the champion.

DECISION. Step 4 is the strongest. If the model predicts the tuning curve
within its CI, M2 is explained.

STOP. 4 h total. The steps are independent.
