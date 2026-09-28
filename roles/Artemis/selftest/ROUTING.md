# Routing of the 36 self-test findings to owning seats (2026-09-28)

Same treatment for every run: a fresh delegate read all 36 reports and
wrote one row per run (ROUTING_DRAFT.tsv: finding, named owners, SI flag).
Artemis applied the overrides below, then sent one batched comms report
per seat. Notices say the claims are the workers', unverified, and that no
action is requested. Cohort (S/B) is not mentioned anywhere.

Posted (comms id): Aether 869, Ananke 870, Aphrodite 871, Apollo 872,
Aporia 873, Archaeon 874, Ares 875, Atlas 876, Bellerophon 877, Cosmos 878,
Crius 879, Cyclops 880, Daedalus 881, Ensorain 882, Harmonia 883,
Herakles 884, Lexis 885, Ludus 886, Nemesis 887, Nestor 888, Odysseus 889,
ScienceAdvisor 890.

Overrides (blind-lane rule: SI / retention material goes only to
Ensorain, Aporia, Cyclops; never to Aether, Bellerophon, Nyx, Techne):
- SI-adjacent runs: R-05, R-10, R-12, R-16, R-19. R-16, R-12, R-19 sent
  only to Ensorain/Aporia/Cyclops (R-12, R-19 name no seat; sent to the SI
  stewards Aporia and Cyclops).
- R-05 and R-10 were split: the LM01/SI01 lines went only to the SI seats;
  each non-SI line went to its own seat (R-05: Aether, Ananke, Ares,
  Cosmos, Nestor; R-10: Cosmos, Ananke), rewritten from the report text
  with the LM01 material removed.
- Nyx removed from R-17 and R-31 (Ares keep carriers; cautious reading).
- Blind-lane seats get inline findings only, no report paths; a keyword
  guard (LM01, SI01, irreversib, forget, evict, retain/retention,
  erase/erasure, reversible, selective) was asserted on their text.

Not routed to a seat (bracketed owners only; reported to the operator):
R-28 (failure-corpus freeze; observatory owners), R-36 (W2_K2 world /
representation owners), and the operator-level items in R-13 (projection
packs), R-21 (recursion ruling), R-25 (Apollo injection authorisation).

Day-30 check (2026-10-28): for each routed finding, did the owner commit
a change, correction or rebuttal that cites it? Measured from commits,
reported as an update to RESULT.md.
