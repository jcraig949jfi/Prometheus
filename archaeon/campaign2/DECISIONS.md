# Campaign 2 -- local campaign decisions (no operator, no HITL)

Format: D2-### | when (UTC) | decision | evidence | alternative rejected |
revisit-if. Every decision also states whether it is SCIENTIFIC DISCRETION or
DETERMINISTIC (should be machinery; if so, where it went).

D2-001 | 2026-09-17 02:30 | Campaign 2 uses its OWN campaign seed 20260918 and
its own engine client cmp2-archaeon (cmp2-* sessions/worlds). | Campaign-1 rows
keyed on 20260917 are independent samples beside campaign-2 rows in the
reachability table only if the streams differ; the client separation keeps
campaign-1 worlds readable under their own principal (D-013). | Alternative:
reuse 20260917 (would make "replication" rows byte-identical to campaign 1 on
common cells: not a replication). | Revisit never. DETERMINISTIC (runner.py
constants).

D2-002 | 2026-09-17 02:30 | Common random numbers are the loop's DEFAULT: the RNG
is keyed on (campaign seed, world, regime, cell seed) and the provenance label
`branch` no longer enters the key; rng_label is the opt-out. Campaign-1
harnesses were patched to pass rng_label=<their branch> so their frozen rows
remain reproducible. | L-008 (rec 2) and L-030: two attempts lost to
label-keyed RNG. Regression snapshot archaeon/tests/data_evolve_snapshot_pre_c2.json
reproduces under rng_label=branch. | Alternative: keep the label in the key and
add a "crn" switch (the switch would have to be remembered, which is exactly
the failure). | Revisit if a harness needs distinct streams per arm by design
(pass rng_label explicitly). DETERMINISTIC (evolve.py).

D2-003 | 2026-09-17 02:30 | Reachability classes: COMMON = Wilson 95% lower
bound >= 0.5; REACHABLE = reached >= 1 and pooled frequency >= 0.25; RARE =
reached >= 1 and frequency < 0.25; OBSERVED_UNREACHABLE_AT_BUDGET = 0 reached
in >= 3 baseline runs; UNESTABLISHED otherwise. Only baseline runs (own
generation 0, no substitution, no intervention) pool into classes. | The bands
make 0/3 read as "< 0.56 at 95%", never as impossible; 4/9 on W2_K2 pools three
campaign-1 arms that separately read 1/3, 0/3 and 3/3. | Alternative: point
estimates without bands (that is what produced three assay-incapable
experiments). | Revisit when the table holds > 100 baseline rows per cell and
a finer scale pays. SCIENTIFIC thresholds, DETERMINISTIC application
(reachability.py).

D2-004 | 2026-09-17 02:30 | An artifact whose kind begins with cmp2.pop. (any
material that can enter a population) cannot be published without a maturity
block; publish() raises. | SFE-10: the one paying exchange came from the only
producer that had solved its own cell; L-010. | Alternative: a warning (would
be ignored under time pressure). | Revisit never. DETERMINISTIC (runner.py).

D2-005 | 2026-09-17 02:30 | Attempts are numbered by the runner (attempts/aNN),
the receipt is written after every step, the attempt of record is a copy at
the experiment root plus ATTEMPTS.json; resume replays a previous attempt's
steps whose results still verify (a world still alive, an artifact still
fetchable). | L-012 (rec 3), L-013 (rec 1). | Alternative: engine-side
Idempotency-Key only (the client can key observations/failures/artifacts but
not experiments or worlds, and the campaign needs local replay for the search
steps too). | Revisit if the engine gains keyed experiment/world creation.
DETERMINISTIC (runner.py).

D2-006 | 2026-09-17 02:57 | C2-SFE-01: pack maturity is recorded, not gating. | The
transported material is EPISODES; a source's failures are informative whether or
not it solved its own cell. | Alternative: fire IMMATURE_ARTIFACT on packs from
unsolved sources (would have voided 8 of 12 packs and the experiment). | Revisit
if a transport of ORGANISMS is designed. SCIENTIFIC.

D2-007 | 2026-09-17 03:10 | C2-SFE-02: representations differ ONLY in the opcode-field
neighbourhood under operand_perturbation; the twelve operator masses are the
grammar's own. | L-029: SFE-09's field grammar bundled geometry with operator
mix. | Alternative: a full field grammar with hand-matched masses (matching by
hand is what went wrong). | Revisit if a representation needs a different
STRUCTURAL operator set. SCIENTIFIC design, DETERMINISTIC implementation.

D2-008 | 2026-09-17 03:25 | C2-SFE-02 attempt a03 (campaign foundry, 1-16
instructions) failed its positive-control gate 1/6 against a 2/3 prior that
came from the v01 survey's 1-32 foundry; attempt a04 re-runs the SAME sealed
question under the v01 foundry (the regime the prior came from). The table now
keys on foundry (L2-017). | Table pooled two regimes; the gate did its job. |
Alternative: raise G until A reaches under the campaign foundry (a budget hunt
the directive forbids). | Revisit if a04's gate also fails: then W1_d1 8-bit at
G100 is RARE under both foundries and the representation question needs a
different control cell. DETERMINISTIC (the keying), SCIENTIFIC (the rerun).

D2-009 | 2026-09-17 03:35 | C2-SFE-02 a04 (v01 foundry) failed the gate too (1/6, first
solved 46): W1_d1 8-bit N200 G100 E24 is RARE in campaign 2's stream under both
foundries. The control cell moves to W2_K2 4-bit N200 G60 E16 (REACHABLE, 7/17
after dedupe, the most-evidenced budget in the table) and the stuck cell to
W1_d4 4-bit at the same budget (RARE 1/14); eight seeds; gate >= 2/8 (P(fail)
~0.11 at 0.41). | Table lookups under the campaign foundry. | Alternative: raise
G on the 8-bit cell until A reaches (a budget hunt). | Revisit never for this
campaign. SCIENTIFIC (the cell), DETERMINISTIC (the lookup).

D2-010 | 2026-09-17 03:45 | C2-SFE-02 a05 passed its gate (3/8) and produced the
rows of record, but its engine records for six rows were REPLAYED from a04 (a
different design) by the resume machinery; the keys now carry the design
digest and a06 re-runs the identical design so the engine record is clean.
a05 is preserved; its rows are identical to a06's by construction (common
random numbers). | L2-020. | Alternative: keep a05 as the row of record with a
note (the engine would then hold six observations attributed to the wrong
cell). | Revisit never. DETERMINISTIC (runner.py keys).
