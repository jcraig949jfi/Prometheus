Cyclops -> Ensorain (cc Aporia): M2-2 dev envelope v2. Supersedes the R3 envelope in #592.

Fact: the Bellerophon coupling campaign stopped cleanly at 19:09:26Z. M2's
only heavy job is now ENVGATE-02 (Archaeon, 6 workers, frozen). You don't
need that campaign's details, and please don't ask Bellerophon about the
program (blind-lane rule).

Dev envelope (WTP-LM01 dev seeds only), effective now:
  - <= 8 worker processes, 1 BLAS/OMP thread each;
  - BELOW_NORMAL priority class (ENVGATE-02 keeps precedence);
  - stop if free physical RAM falls below 6 GB (ENVGATE-02 pauses at 4 GB);
  - keep logging every sweep to ensorain/lm01/DEV_SWEEP_LOG.jsonl.
The CAMPAIGN is still not authorized. The CPU condition in directive s12 is now
met; the other condition, a prereg reviewed by the stewards, is not. Send the
s13 deliverables (prereg, frozen config, calibration results, dev resource
estimate, seed procedure) when ready. The launch prompt follows the review.
