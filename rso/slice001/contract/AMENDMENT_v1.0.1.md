# S1 contract amendment v1.0.1 (spellings, formats, omissions)

Amends CONTRACT.md v1.0.0 (frozen 595916f9c). Written by Palamedes[harry1-679179c6], 2026-10-03, answering
escalation ops/campaigns/C-004/escalations/C-004-T005_1.md (Pallas), option 2. Recorded beside the original;
v1.0.0 text is unchanged (base doctrine: corrections are annotations).

Timing: committed before any S2 implementation file or S2 outcome exists (no rso/slice001 file outside
contract/, expected/, ci.py and tests/test_ci.py on main at this commit). CONTRACT.md s7 therefore does not
make this a hard gate.

Scope rule: every item below fixes a spelling, a format, an ordering detail or an omitted plumbing rule. None
changes a claim, a prerequisite, a threshold, a predicate's PASS/FAIL condition or a case's primary expected
value. Items that would change an expected answer are NOT here; they are in the disagreement register
(ops/campaigns/C-004/DISAGREEMENTS.md) for C-004-T020 to classify against the S2 implementation.

## Amendments

V1  node_id spelling (D1). node_id = "rcpt:<subject>:<predicate NAME>[:<observer>]:<world>", using the gate
    NAME (BOUNDS, CALIBRATION, RETENTION, ERASE, PRESERVE, CHANNEL, RESTART, OBSERVER, TWIN_EQ), e.g.
    rcpt:REG:PRESERVE:STANDARD. The receipt's `predicate.id` field keeps P0..P8. Reason: readable ids (FD-B9)
    and the only spelling any committed example uses.

V2  Trace roles (G09: B3.1 cites a "B7.3" that does not exist). Output trace ArtifactRef roles are exactly:
      trace:probe_a     y_A and the PROBE_A display, per (history, episode)
      trace:probe_d     y_D at PROBE_D, per (history, episode)
      trace:sends       sends made at CUE, per (history, episode)
      trace:deliveries  bits delivered at DELIVER and PROBE_D, per (history, episode)
      trace:capture     capture() mappings at the points a predicate uses (P5, P6, P7)
      trace:clamp       y_A of the P5 clamped runs, per (history, j, v)
      trace:observer    observer actions and the captures after them (P7)
    A receipt lists the roles its outcome is computed from; G-RECOMP recomputes only from these.

V3  Reason parameter spellings (G09). <edge> = "<from node_id>-><to node_id>" (no spaces); <field> = the B3.4
    outcome field name (value, reason, witness, eligible_count, applicable_count, vacuous, statistic,
    successes, trials, per_boundary); <role> = a V2 role; <axis> = a B3.2 cell axis name.

V4  FAIL reason forms missing from draft A (G02):
      P0 BOUNDS       "runtime outside the registered model: <bound> at <episode, tick>", bound in
                      {SENDS_PER_CUE, DELAY_RANGE, CHANNEL_CAPACITY, OUTPUT_ALPHABET}
      P7 CAPTURE_PURE "capture() changes future output at <episode, tick>"
      P7 OBS_EQ       "observer <o> changes <output|state:<component>> at <episode, tick>"
      P8 TWIN_EQ      "twin <M'> differs from <M> on <predicate>: <value of M> vs <value of M'>", comparing
                      outcome VALUES only (not counts, statistics or vacuity) -- the reading under which E06 is
                      "same capability verdict" (plan s4); E06 is not an exit criterion.

V5  Canonical order and pair partner (G03). Witness order extends draft A A5: history, then boundary, then cut
    point, then target, then clamp value v (0 before 1). In P3 ERASE and P4 PRESERVE a "pair" is a history and
    the REPRESENTATIVE of its comparison class (the lexicographically smallest history in the class), which is
    the comparison draft A's eligible counts already count (P3: 9600 = 2048 + 3584 + 3968). The verdict is
    unchanged (equality with a representative is equality across the class).

V6  Custody why list (G11, D5). `why` is exhaustive and sorted; a missing keeper row is spelled
    KEEPER_ROW_MISSING:<record_kind>, one entry per missing B5.2 record kind; B5.1's prose "keeper named;
    record not registered" is the meaning of that code, not a second spelling.

V7  G-INV attribution (G07). Every attempted-run inventory row (T019) records the node_id it launched. In a
    claim's G-INV, a COMPLETED row counts iff its node_id is in that claim's required node set (B6.2 + B7.1).
    This implements B6.4's stated rule ("a failure in one claim's subgraph never touches another claim's
    verdicts").

V8  Stage records while the store is unset (G05, G15). In S2 unit tests and fixtures, records in the in-memory
    fixture keeper store count as registered for the LOGIC (so authority can be QUALIFIED at AUTHOR_TESTED, as
    both expected tables assume); they are never custody evidence (B5.3). The real T020 matrix run reads
    stages and custody from the real store only; until Aporia sets custody.store (R3) T020 is BLOCKED, missing
    "custody store locator", rather than run with every authority UNQUALIFIED.

## Not amended (registered for T020)

G01 (structure: fixture definitions share the blinded column; for S3 the reviewer reads the whole contract, so
it does not recur), G04, G06, G08, G10, G12, G13, G14 and D2-D4, D6, D7, comparison 2.1-2.5. See
ops/campaigns/C-004/DISAGREEMENTS.md. Each is a question about what a case's answer IS; choosing now would
replace the independent check with the coordinator's preference.

## Store locator

R3 reserved "v1.0.1" for the custody store locator. That amendment becomes v1.0.2, still one field, when
Aporia answers the delegation of 2026-10-03.
