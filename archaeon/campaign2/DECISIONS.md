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
