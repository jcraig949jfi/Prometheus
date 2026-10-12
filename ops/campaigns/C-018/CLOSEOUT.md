# C-018 closeout -- Observatory generation 4 (Aether)

Palamedes[harry1-679179c6], 2026-10-12. Opened 09:01Z; closed ~20:00Z, about 11 h of the 72-hour window. The full
account is the self-contained review packet rso/scale/review/GEN4_REVIEW_PACKET.md.

## Completion condition (directive 2026-10-12 s16)

| # | Item | Status | Evidence |
|---|---|---|---|
| 1 | Gen 1-3 preserved and scoped | MET | roles/Palamedes/STATUS.md table; RESULT files untouched; C-017 frozen files unchanged (completeness wrapper is a new version) |
| 2 | Completeness check tested on the Z80 six-shard fixture | MET | rso/completeness/ (40 tests); complete = frozen verdict; 5 shards = INCOMPLETE |
| 3 | Falsifiability requirement in qualification | MET | rso/qualify/FALSIFIABILITY.md + falsifiable.py; applied in rso/aether/PREREGISTRATION s4 |
| 4 | Aether passed the selection / demand gate | MET (narrowed) | rso/aether/SELECTION.md: P1 as a guard, P2/P3 in scope, P4 unsupported |
| 5 | One bounded native spatial experiment | MET | rso/aether/RESULT.md: RX CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE_CONTENT; V1 ANCESTRY_UNEVALUABLE |
| 6 | Recorded independent challenge | MET | T040 + T042, both Pallas on claude-fable-5-1 for every message, 0 fallbacks (launch-log counts in the TASK notes) |
| 7 | Registry reflects new evidence and limits | MET | rso/registry/: 15 entries (experiment-completeness, control-falsifiability-checks, aether-ancestry-content-instrument added) |
| 8 | Four-generation cost comparison | MET | review packet s7; rso/aether/ONBOARDING.md s7.3 (cost of detecting a false interpretation) |
| 9 | Generation 5 candidate contract | MET (not opened) | rso/gen5/CANDIDATE_CONTRACT.md: Crius primary, Ananke runner-up |
| 10 | Final review packet | MET | rso/scale/review/GEN4_REVIEW_PACKET.md (ASCII, self-contained) |

No Q3 process requirement is unfulfilled in C-018. C-017's mixed-model re-check remains a stated limitation of Gen 3.

## Process record

- Seats (headless, harry1; models verified across every assistant message):
  - Eupalamus and Cadmus: Sonnet.
  - Argus: Opus for T030 and T041, Sonnet for T050.
  - Pallas: Fable 5.1 for T040 and T042.
- Incidents, all disclosed:
  - A pre-freeze run of 4 confirmatory units by a guard test; the block was burned.
  - A usage limit stopped T041 mid-work; the same seat was relaunched from its pushed commit.
  - Argus lost about 1 h to a wrapper path error in T050.
- Aether's lane was untouched: nothing run on M2; notice #2183, and a result notice follows.
- Cost:
  - About 5 core-h CPU, all local; 0 GPU; $0.
  - About 2.8 h of Q3 reviewer time.
  - Coordination waiting was 21% of packet time.

## Next (each needs its own authority)

- Generation 5 (Crius) needs an operator decision and a named engine steward.
- The Astra / Fable external reviews of C-013 are still pending.
