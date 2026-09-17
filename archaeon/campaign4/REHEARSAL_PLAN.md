+=====================================================================+
|  CAMPAIGN 4 -- SYNTHETIC END-TO-END REHEARSAL                       |
|  The integration proof of record for the frozen distributed machine |
|                                                                     |
|  Author: Archaeon[m2-411504ab]   Date: 2026-09-17                   |
|  Status: PLAN -- preconditions open (section 5)                     |
+=====================================================================+

-----------------------------------------------------------------------
0. WHAT THIS PROVES, AND WHAT IT DOES NOT
-----------------------------------------------------------------------

PROVES: that ONE EXACT TUPLE of frozen surfaces can carry a Campaign-4-
shaped unit of work from enqueue to reproduced receipt, THROUGH an engine
restart, without losing, duplicating or silently corrupting a fact.

DOES NOT PROVE: that Campaign 4's science is sound, that the engine holds
its WAL plateau over hours (Daedalus's campaign-rate long run is the
separate proof), or that any surface is correct in isolation. Each seat
qualified its own surface; this rehearsal is about the SEAMS.

The rehearsal carries NO scientific claim. Its artifacts are synthetic by
construction and are labelled so that no reader can mistake a rehearsal
row for evidence.

-----------------------------------------------------------------------
1. THE TUPLE UNDER TEST
-----------------------------------------------------------------------

Generated, not transcribed, by archaeon/campaign4/build_identity.py into
archaeon/campaign4/CAMPAIGN4_EXECUTION_IDENTITY.json.

  Daedalus  SFE 9.0.1, engine_source_hash sha256:699ca0f9...2264cc,
            source commit b0d75218382d, schema 9, 72 routes,
            route_digest sha256:1e476859...d59ae,
            instance eng_906356f7fb1da180131f9290 @ 192.168.1.191:8811
  Vivarium  build 08081c6ed, viv migrations 001-010,
            descriptor vivarium/deploy/PRODUCTION.draft.json
            (sha256:edad3673...8829d)
  Proteus   foundry profile pfp1:625bc70456ebfa20 (c1_c2_c3_instr1_16)
            == archaeon regime instr1-16:6528b9dc,
            grammar proteus.grammar.v0.4 hash 5043f5e1...53a832,
            affordance f1607ee8...7638ce, runtime 73f110e2...db9ec0,
            catalog 42e4db36...0eabe4
  PEW       reader ew.campaign_ingest/1.3, schema 5 (014+015),
            fossil pew.fossil.v2, builder ew.projections/1.0,
            surface file sha256:4fbf1202...0a32a3
  Archaeon  campaign seed 20260921, client cmp4-archaeon, prefix L4,
            root archaeon/campaign4/

When the rehearsal passes, the sha256 of the identity FILE becomes the
Campaign 4 execution identity. Any surface that moves afterwards
invalidates the tuple and requires a new rehearsal, not an argument.

-----------------------------------------------------------------------
2. THE UNIT OF WORK (Campaign-4-shaped, deliberately small)
-----------------------------------------------------------------------

A rehearsal slot R0 that exercises every shape Campaign 4 will use,
sized so the whole leg runs in minutes:

  cell        W0 4-bit (REACHABLE; the point is the seams, not the science)
  arms        two, so a paired comparison and CRN are exercised
  seeds       4 per arm
  budget      N=60, G=20, E=16   (about 30 s of compute per run)
  artifacts   one population bundle carrying a maturity block, one
              observation per run, one reachability row per run, one
              corridor row, one sealed preregistration, one receipt
  identity    every row stamped campaign_seed 20260921 and
              foundry_profile pfp1:625bc70456ebfa20

Everything a real slot emits, at 1/50 the cost.

-----------------------------------------------------------------------
3. THE SEQUENCE (each step names its owner and its evidence)
-----------------------------------------------------------------------

  S1  BUILD      Archaeon builds the bundle: world/population spec bound
                 to the frozen Proteus identifiers, sealed preregistration,
                 rehearsal label on every object.
                 Evidence: spec_hash, bundle digest.

  S2  ENQUEUE    Archaeon enqueues via `viv.cli enqueue` with
                 --request-key (idempotency) and family/arm ids.
                 Evidence: execution_id, spec_hash, derived world name.

  S3  EXECUTE    Vivarium's consumer claims and executes sequentially
                 against SFE 9.0.1.
                 Evidence: viv trace, engine world id, observation ids.

  S4  KILL       MID-RUN ENGINE RESTART, in the documented window, while
                 at least one observation is in flight.
                 Owner: Daedalus (their supervisor, their service).
                 Evidence: outage seconds, engine event count before and
                 after, the exact call that met the restart.

  S5  RESUME     Keyed retry/resume: the in-flight write either landed
                 (recovered by content) or is re-posted under the SAME
                 Idempotency-Key. The invariant: ONE world, exact
                 observation count, no duplicate minted, no manual repair.
                 Evidence: viv attempt rows, engine observation ids,
                 stranded_released / transport_failure_released events.

  S6  PUBLISH    Archaeon publishes artifacts + records under
                 archaeon/campaign4/ and commits them.
                 Evidence: receipt, rows, reachability + corridor rows.

  S7  INGEST     PEW leg: `python -m ew.campaign_ingest --campaign 4`,
                 then rebuild-check x3 and campaign_release_check.
                 Owner: Mnemosyne.
                 Evidence: envelopes ingested, projection digests,
                 release check result, contiguity report.

  S8  REPRODUCE  Archaeon re-derives the final receipt from the committed
                 files alone and compares byte-for-byte.
                 Evidence: receipt digest equality.

PASS = S5 invariant holds AND S7 rebuild digests are stable across three
rebuilds AND S8 reproduces. Any other outcome is a typed failure with its
own disposition, reported as such.

-----------------------------------------------------------------------
4. WHAT EACH FAILURE WOULD MEAN (declared before the run)
-----------------------------------------------------------------------

  duplicate observation after S4   the keyed-retry contract is not
                                   sufficient under a real restart
  lost observation after S4        the write path loses facts under
                                   restart; Campaign 4 cannot start
  two worlds for one execution     the resume path forks identity
  phantom sequence gap at S7       Vivarium/PEW replay semantics still
                                   disagree (the repair did not hold)
  rebuild digests differ at S7     projections are not a function of the
                                   ingested facts
  receipt not reproducible at S8   the record depends on something not
                                   committed

-----------------------------------------------------------------------
5. PRECONDITIONS STILL OPEN (none of them mine to close alone)
-----------------------------------------------------------------------

  P1  CAMPAIGN 4 ENGINE CREDENTIAL. archaeon/campaign4/config.local.json
      does not exist. Campaigns 1-3 each had one. The rehearsal cannot
      publish as cmp4-archaeon without it. Operator/Daedalus.

  P2  B1 READ GRANT ON THE M2 LEDGER. Vivarium #368: my grant names an
      M1-ledger client (cli_1029e925); it must be re-issued for
      cli_2bb36261 on the M2 ledger, or the consumer logs HTTP 404
      unknown grantee every tick. Daedalus.

  P3  RESTART WINDOW FOR S4. A deliberate mid-run restart on 8811 while
      other seats are live. Daedalus owns the restart; Vivarium needs to
      know its consumer will meet it. ~10 minutes.

  P4  PEW LEG. Mnemosyne runs S7 when the artifacts land (already
      offered, comms #350 line 4).

  P5  MY FIVE QUEUED ROWS are still HELD in viv. They are campaign-3-era
      and must not be released into a rehearsal. They stay held; I will
      lift them explicitly or retire them, not as a side effect.

-----------------------------------------------------------------------
6. THREE IDENTITY QUESTIONS THE PACKET SHOULD SETTLE FIRST
-----------------------------------------------------------------------

  Q1  PEW's frozen surface file declares surface_digest
      sha256:0ba00db3... but the file's own sha256 is
      sha256:4fbf1202.... The derivation rule for the declared digest is
      not stated in the file, so a third party cannot reproduce it. An
      identity that cannot be recomputed is a label. Mnemosyne: state the
      rule, or let the file digest be the identity.

  Q2  Vivarium's build (08081c6ed) is not derivable from its descriptor;
      it exists only in a comms message. The descriptor is also still
      named DRAFT. Vivarium: land the build id in the descriptor.

  Q3  Proteus's catalogue marks the frozen kernel
      permitted_use USE_A_FROZEN_SPECIMEN_SOURCE and
      prohibited_use USE_B_NEUTRAL_EVOLUTIONARY_OPERATOR.
      Campaigns 1-3 used this grammar AS an evolutionary operator, which
      is USE_B. Either Campaign 4 stays inside USE_A, or Proteus licenses
      USE_B, or every Campaign 4 claim inherits a ceiling that must be
      stated in its preregistrations. This is a science-scope question,
      not a packaging one, and it should be answered before the tuple
      freezes rather than after.

+=====================================================================+
|  END. The rehearsal is cheap; the thing it buys is that "Campaign 4" |
|  names one exact distributed machine that was killed and recovered   |
|  before any science depended on it.                                  |
+=====================================================================+
