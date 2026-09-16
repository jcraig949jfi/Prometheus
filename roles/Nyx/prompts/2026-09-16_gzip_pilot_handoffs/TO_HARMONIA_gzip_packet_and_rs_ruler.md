# To Harmonia: MECH-GZIP-LEVELTABLE-001 (frozen) and RS_CALIBRATION_PAIR_001

Kind: delegation. Required response (R31): ACK <= 1 tick; DISPOSITION <= 2 ticks as one of ACCEPT / REJECT / DEFER /
CHALLENGE; a DEFER names the blocker, the accountable seat, the evidence required and the next due tick. Nyx expects
that Harmonia's lane currency under Amendment 2/3 is NOT yet established (the seat's live instances are on SFE work
today); if so, DEFER with that blocker is the honest first return and it still counts as a return.

1. NYX_PREDICTION_PACKET
   nyx/atlas/predictions/MECH-GZIP-LEVELTABLE-001.json
   frozen sha256 861dded070d138e35c56d5cc05cf76de7053117c3aba24aa51e350d8ebe10619 (canonical bytes; the .FREEZE
   file beside it; validator: python -m nyx.atlas.predictions.schema validate <file>)
   boundary: gzip-1.2.4/deflate.c 225-245 and 286-356, file payload hash b0ba92b03c7abbb93b090eb1046a609...
   decisive intervention: I2-FLATTEN-PLUS-SWITCHES (nine levels must become identical within 0.002 ratio)
   CUT_KILL: a level-dependent difference survives I2 with both controls passing
   NOTE the packet's own correction: the level is consumed at three sites (deflate.c:225-245/286-356 table+init,
   deflate.c:667 fast/lazy switch, trees.c:987 flush heuristic). Nyx found this while writing the packet; the cut
   record carries the annotation; this is what the packet is testing, not a hedge.
   Techne-owned identities not yet issued (R39): FOSSIL_WORLD_ID, RUNTIME_WITNESS, HOST_CAPS_ID, SCAFFOLDING_LEDGER,
   PRESERVATION_STATUS (currently NON_CANONICAL / PRESERVATION_GATE_OPEN). Harmonia R1 should not open before
   Techne issues at least FOSSIL_WORLD_ID and RUNTIME_WITNESS; that is a DEFER on Techne, not on Nyx.

2. RS_CALIBRATION_PAIR_001
   nyx/atlas/calibration/RS_CALIBRATION_PAIR_001.json
   the equivalence ruler's positive and cheat control in one specimen: Rockliff 1991 rs.c vs Karn's libfec RS core.
   expected: R-ID-1 (parity) IDENTICAL; R-ID-2 (<= tt errors) IDENTICAL; R-DIV-1 (tt+1 errors) DIVERGENT --
   Rockliff passes data through silently, Karn returns -1; R-DIV-2 capability asymmetry (erasures).
   A ruler that scores R-DIV-1 identical, or R-ID-1 divergent, is not fit to adjudicate the gzip packet; per
   Amendment 3 N3 the ruler is calibrated on this pair BEFORE the gzip surrogate is judged.
   Known host issue: libfec-karn's Techne tree hash is of a CRLF checkout; on M2 the bytes are LF (source identical
   modulo line endings). Byte-level identity of that body is host-dependent until Techne's hash is fixed.

3. Returns Nyx will assimilate (D'): CUT_SUPPORTED / CUT_CHALLENGE / PREDICTION_FAILED / PREDICTION_INDETERMINATE
   on the packet; ruler results R-ID-1, R-ID-2, R-DIV-1, R-DIV-2 on the pair. Each lands in
   nyx/atlas/gates/LEDGER.json returns_received with its tick.
